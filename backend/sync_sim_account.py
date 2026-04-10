#!/usr/bin/env python3
"""
同步 sim_account 表数据（从 sim_daily_snapshots）
使用方法：python3 sync_sim_account.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
from sqlalchemy import text

def sync_sim_account():
    """从 sim_daily_snapshots 同步最新数据到 sim_account"""
    
    with app.app_context():
        # 获取 sim_daily_snapshots 最新一条记录
        latest = db.session.execute(text("""
            SELECT snapshot_date, total_asset, cash, position_value, total_return
            FROM sim_daily_snapshots
            ORDER BY snapshot_date DESC
            LIMIT 1
        """)).fetchone()
        
        if not latest:
            print("❌ sim_daily_snapshots 表为空")
            return False
        
        snapshot_date, total_asset, cash, position_value, total_return = latest
        total_asset = float(total_asset)
        cash = float(cash)
        position_value = float(position_value)
        total_return = float(total_return) if total_return else 0
        
        # 计算初始资金 = 总值 / (1 + 总收益率)
        initial_capital = total_asset / (1 + total_return) if total_return != 0 else total_asset
        
        # 已投入成本 = 总值 - 现金 - 未实现盈亏
        # 简化：已投入成本 = 持仓市值
        cost_paid = position_value
        
        # 获取或创建 sim_account 记录
        account = db.session.execute(text("SELECT * FROM sim_account WHERE id = 1")).fetchone()
        
        if account:
            # 更新现有记录
            db.session.execute(text("""
                UPDATE sim_account
                SET cash = :cash,
                    total_value = :total_value,
                    total_cost_paid = :cost_paid,
                    updated_at = NOW()
                WHERE id = 1
            """), {
                'cash': cash,
                'total_value': total_asset,
                'cost_paid': cost_paid
            })
            print(f"✅ 已更新 sim_account (日期：{snapshot_date})")
        else:
            # 创建新记录
            db.session.execute(text("""
                INSERT INTO sim_account (id, total_capital, cash, total_value, total_cost_paid, created_at, updated_at)
                VALUES (1, :capital, :cash, :total_value, :cost_paid, NOW(), NOW())
            """), {
                'capital': initial_capital,
                'cash': cash,
                'total_value': total_asset,
                'cost_paid': cost_paid
            })
            print(f"✅ 已创建 sim_account (日期：{snapshot_date})")
        
        db.session.commit()
        
        # 打印结果
        result = db.session.execute(text("SELECT id, total_capital, cash, total_value, total_cost_paid FROM sim_account WHERE id = 1")).fetchone()
        print(f"\n📊 sim_account 当前数据:")
        print(f"   初始资金：¥{result[1]:,.2f}")
        print(f"   现金：¥{result[2]:,.2f}")
        print(f"   总值：¥{result[3]:,.2f}")
        print(f"   已投入成本：¥{result[4]:,.2f}")
        print(f"   持仓市值：¥{position_value:,.2f}")
        print(f"   总收益率：{total_return*100:.2f}%")
        
        return True

if __name__ == '__main__':
    if sync_sim_account():
        print("\n✅ 同步完成！")
    else:
        print("\n❌ 同步失败！")
        sys.exit(1)
