#!/usr/bin/env python3
"""
同步 watchlist_history 表的股息率数据
从 akshare 获取分红数据，从数据库获取季度末股价，计算股息率
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import akshare as ak
from sqlalchemy import text
from app import app, db
from datetime import datetime
import time
import re

def get_stock_list():
    """获取 watchlist_history 表中的股票列表"""
    with app.app_context():
        results = db.session.execute(text("""
            SELECT DISTINCT stock_code, stock_name
            FROM watchlist_history
            ORDER BY stock_code
        """)).fetchall()
    return [{'code': r[0], 'name': r[1]} for r in results]

def convert_code_for_akshare(stock_code):
    """转换股票代码格式（去掉 .SH/.SZ 后缀）"""
    return stock_code.split('.')[0]

def fetch_dividend_history(stock_code):
    """获取分红历史数据"""
    try:
        pure_code = convert_code_for_akshare(stock_code)
        df = ak.stock_dividend_cninfo(symbol=pure_code)

        if df is None or len(df) == 0:
            return []

        # 解析每股分红
        def parse_dividend(desc):
            if desc is None or (isinstance(desc, float) and pd.isna(desc)):
                return 0.0
            desc_str = str(desc)
            # 找到"派"和"元"的位置
            pai_idx = desc_str.find('派')
            yuan_idx = desc_str.find('元')

            if pai_idx >= 0 and yuan_idx > pai_idx:
                # 提取中间的数字
                between = desc_str[pai_idx+1:yuan_idx]
                nums = re.findall(r'[\d.]+', between)
                if nums:
                    return float(nums[0]) / 10.0
            return 0.0

        df['每股分红'] = df['实施方案分红说明'].apply(parse_dividend)
        df['年份'] = pd.to_datetime(df['实施方案公告日期']).dt.year

        annual_div = df.groupby('年份')['每股分红'].sum().reset_index()
        annual_div['年份'] = annual_div['年份'].astype(int)

        return annual_div.to_dict('records')

    except Exception as e:
        print(f"  获取分红数据失败：{e}")
        return []

def get_quarterly_prices(stock_code, years):
    """从 daily_prices 表获取季度末股价"""
    prices = {}

    # 先获取 stock_id
    with app.app_context():
        result = db.session.execute(text("""
            SELECT id FROM stocks WHERE code = :code
        """), {'code': stock_code}).fetchone()
        stock_id = result[0] if result else None

        if not stock_id:
            return prices

        # 季度末日期
        quarter_ends = {
            1: "{0}-03-31",
            2: "{0}-06-30",
            3: "{0}-09-30",
            4: "{0}-12-31",
        }

        for year in years:
            for quarter in range(1, 5):
                quarter_end = quarter_ends[quarter].format(year)
                result = db.session.execute(text("""
                    SELECT close FROM daily_prices
                    WHERE stock_id = :sid AND date <= :qend
                    ORDER BY date DESC
                    LIMIT 1
                """), {
                    'sid': stock_id,
                    'qend': quarter_end
                }).fetchone()

                if result and result[0]:
                    prices[(year, quarter)] = float(result[0])

    return prices

def calculate_and_save_dividend_yield(stock_code, stock_name, dividend_data, prices):
    """计算并保存股息率到 watchlist_history 表"""
    saved_count = 0

    with app.app_context():
        for div_record in dividend_data:
            year = div_record['年份']
            annual_dividend = div_record['每股分红']

            for quarter in range(1, 5):
                quarter_start = f"{year}-{(quarter-1)*3+1:02d}-01"

                # 跳过未来季度
                if quarter_start > datetime.now().strftime('%Y-%m-%d'):
                    continue

                price = prices.get((year, quarter))

                # 计算股息率 = 年度分红 / 季度末股价 * 100（得到百分比数值）
                dividend_yield = None
                if price and price > 0 and annual_dividend and annual_dividend > 0:
                    dividend_yield = (annual_dividend / price) * 100

                try:
                    result = db.session.execute(text("""
                        UPDATE watchlist_history
                        SET dividend_yield = :dy, updated_at = NOW()
                        WHERE stock_code = :code AND quarter_start = :qstart
                    """), {
                        'dy': dividend_yield,
                        'code': stock_code,
                        'qstart': quarter_start
                    })

                    if result.rowcount > 0:
                        saved_count += 1

                except Exception as e:
                    continue

        db.session.commit()

    return saved_count

def main():
    print("=" * 80)
    print("同步 watchlist_history 股息率数据")
    print("=" * 80)

    stock_list = get_stock_list()
    print(f"\n自选股票数量：{len(stock_list)} 只")

    current_year = datetime.now().year
    years = [current_year - 3, current_year - 2, current_year - 1, current_year]

    total_saved = 0
    success_count = 0

    for i, stock in enumerate(stock_list, 1):
        print(f"\n[{i}/{len(stock_list)}] 处理 {stock['code']} {stock['name']}")

        # 获取分红数据
        dividend_data = fetch_dividend_history(stock['code'])

        if not dividend_data:
            print(f"  ⚠️ 无分红数据")
            continue

        dividend_data = [d for d in dividend_data if d['年份'] in years]

        if not dividend_data:
            print(f"  ⚠️ 无近三年分红数据")
            continue

        print(f"  获取到 {len(dividend_data)} 年分红数据")

        # 获取季度末股价
        prices = get_quarterly_prices(stock['code'], years)

        if not prices:
            print(f"  ⚠️ 无股价数据")
            continue

        print(f"  获取到 {len(prices)} 个季度股价")

        # 计算并保存股息率
        saved_count = calculate_and_save_dividend_yield(
            stock['code'], stock['name'], dividend_data, prices)
        total_saved += saved_count

        if saved_count > 0:
            success_count += 1
            print(f"  ✅ 更新 {saved_count} 条股息率记录")

        time.sleep(0.1)

    print("\n" + "=" * 80)
    print(f"完成！成功处理 {success_count}/{len(stock_list)} 只股票，共更新 {total_saved} 条记录")
    print("=" * 80)

    with app.app_context():
        result = db.session.execute(text("""
            SELECT
                COUNT(*) as total,
                COUNT(DISTINCT stock_code) as stocks,
                AVG(dividend_yield) as avg_yield,
                MAX(dividend_yield) as max_yield,
                MIN(dividend_yield) as min_yield
            FROM watchlist_history
            WHERE dividend_yield IS NOT NULL
        """)).fetchone()

        print(f"\n股息率统计:")
        print(f"  有股息率记录数：{result[0]}")
        print(f"  股票数：{result[1]}")
        if result[2]:
            print(f"  平均股息率：{result[2]:.2f}%")
            print(f"  最高股息率：{result[3]:.2f}%")
            print(f"  最低股息率：{result[4]:.2f}%")

if __name__ == '__main__':
    main()
