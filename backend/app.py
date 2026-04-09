#!/usr/bin/env python3
"""
stockMonitor - 股票监控 Web 系统后端
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config.from_object('config.Config')

CORS(app, supports_credentials=True)
db = SQLAlchemy(app)
jwt = JWTManager(app)

# ============== 数据模型 ==============

class User(db.Model):
    __tablename__ = 'sm_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class SimAccount(db.Model):
    __tablename__ = 'sim_account'
    id = db.Column(db.Integer, primary_key=True)
    total_capital = db.Column(db.Numeric(12,2))
    cash = db.Column(db.Numeric(12,2))
    total_value = db.Column(db.Numeric(12,2))
    total_cost_paid = db.Column(db.Numeric(12,2))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

class SimPosition(db.Model):
    __tablename__ = 'sim_positions'
    id = db.Column(db.Integer, primary_key=True)
    stock_code = db.Column(db.String(20), nullable=False)
    stock_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    cost_price = db.Column(db.Numeric(10,2))
    highest_price = db.Column(db.Numeric(10,2))
    buy_date = db.Column(db.DateTime)
    sell_date = db.Column(db.DateTime)
    sell_price = db.Column(db.Numeric(10,2))

class Watchlist(db.Model):
    __tablename__ = 'watchlist'
    id = db.Column(db.Integer, primary_key=True)
    stock_code = db.Column(db.String(20), nullable=False)
    stock_name = db.Column(db.String(100), nullable=False)
    target_price = db.Column(db.Numeric(10,2))
    target_type = db.Column(db.String(20))
    current_price = db.Column(db.Numeric(10,2))
    status = db.Column(db.String(20), default='active')
    remark = db.Column(db.String(200))

# ============== 实盘数据模型 (复用 stockProject 数据库) ==============

class Position(db.Model):
    """实盘持仓表 - 复用 stockProject.positions"""
    __tablename__ = 'positions'
    id = db.Column(db.Integer, primary_key=True)
    stock_code = db.Column(db.String(20), nullable=False)
    stock_name = db.Column(db.String(50))
    industry = db.Column(db.String(50))
    quantity = db.Column(db.Integer, nullable=False)
    cost_price = db.Column(db.Numeric(10,4), nullable=False)
    current_price = db.Column(db.Numeric(10,4))
    stop_loss_price = db.Column(db.Numeric(10,4))
    stop_loss_pct = db.Column(db.Numeric(5,2))
    stop_loss_type = db.Column(db.String(20))
    highest_price = db.Column(db.Numeric(10,4))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

class Trade(db.Model):
    """实盘交易记录表 - 复用 stockProject.trades"""
    __tablename__ = 'trades'
    id = db.Column(db.Integer, primary_key=True)
    stock_code = db.Column(db.String(20), nullable=False)
    stock_name = db.Column(db.String(50))
    direction = db.Column(db.String(10), nullable=False)  # BUY/SELL
    price = db.Column(db.Numeric(10,4), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Numeric(20,4))
    trade_date = db.Column(db.DateTime, nullable=False)
    strategy = db.Column(db.String(50))
    remark = db.Column(db.String(200))
    decision_note = db.Column(db.Text)
    trade_type = db.Column(db.String(20), default='manual')
    profit_loss = db.Column(db.Numeric(20,4), default=0)
    profit_loss_pct = db.Column(db.Numeric(10,4), default=0)
    fee = db.Column(db.Numeric(10,4), default=0)
    created_at = db.Column(db.DateTime)

class DailySnapshot(db.Model):
    """每日收盘快照 - 复用 stockProject.daily_snapshots"""
    __tablename__ = 'daily_snapshots'
    id = db.Column(db.Integer, primary_key=True)
    snapshot_date = db.Column(db.Date)
    total_asset = db.Column(db.Numeric(15,2))
    cash = db.Column(db.Numeric(20,4))
    position_value = db.Column(db.Numeric(20,4))
    daily_return = db.Column(db.Numeric(10,4))
    total_return = db.Column(db.Numeric(10,4))
    created_at = db.Column(db.DateTime)

# ============== API 路由 ==============

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=username)
        return jsonify({
            'success': True,
            'token': access_token,
            'username': username
        })
    
    return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': '用户名已存在'}), 400
    
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '注册成功'})

@app.route('/api/sim-account', methods=['GET'])
@jwt_required()
def get_sim_account():
    account = SimAccount.query.filter_by(id=1).first()
    if not account:
        return jsonify({'success': False, 'message': '账户不存在'}), 404
    
    return jsonify({
        'success': True,
        'data': {
            'total_capital': float(account.total_capital),
            'cash': float(account.cash),
            'total_value': float(account.total_value),
            'total_cost_paid': float(account.total_cost_paid),
            'position_value': float(account.total_value) - float(account.cash)
        }
    })

@app.route('/api/sim-positions', methods=['GET'])
@jwt_required()
def get_sim_positions():
    """获取模拟持仓列表（支持搜索和分页）"""
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    keyword = request.args.get('keyword', '')

    # 构建查询
    query = SimPosition.query.filter(SimPosition.quantity > 0)

    # 条件过滤
    if keyword:
        query = query.filter(
            db.or_(
                SimPosition.stock_code.like(f'%{keyword}%'),
                SimPosition.stock_name.like(f'%{keyword}%')
            )
        )

    # 总数
    total = query.count()

    # 分页排序
    positions = query.order_by(SimPosition.buy_date.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    result = []
    for p in positions:
        result.append({
            'stock_code': p.stock_code,
            'stock_name': p.stock_name,
            'quantity': p.quantity,
            'cost_price': float(p.cost_price),
            'current_price': 0,  # 需要实时获取
            'highest_price': float(p.highest_price),
            'buy_date': p.buy_date.strftime('%Y-%m-%d') if p.buy_date else None,
            'profit_pct': 0
        })

    return jsonify({
        'success': True,
        'data': result,
        'total': total,
        'page': page,
        'page_size': page_size
    })

@app.route('/api/watchlist', methods=['GET'])
@jwt_required()
def get_watchlist():
    watchlist = Watchlist.query.filter_by(status='active').all()

    result = []
    for w in watchlist:
        result.append({
            'stock_code': w.stock_code,
            'stock_name': w.stock_name,
            'target_price': float(w.target_price) if w.target_price else 0,
            'current_price': float(w.current_price) if w.current_price else 0,
            'status': w.status,
            'remark': w.remark
        })

    return jsonify({'success': True, 'data': result})

# ============== 实盘 API 路由 ==============

@app.route('/api/actual-positions', methods=['GET'])
@jwt_required()
def get_actual_positions():
    """获取实盘持仓列表（支持搜索和分页）"""
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    keyword = request.args.get('keyword', '')
    industry = request.args.get('industry', '')

    # 构建查询
    query = Position.query.filter(Position.quantity > 0)

    # 条件过滤
    if keyword:
        query = query.filter(
            db.or_(
                Position.stock_code.like(f'%{keyword}%'),
                Position.stock_name.like(f'%{keyword}%')
            )
        )
    if industry:
        query = query.filter(Position.industry == industry)

    # 总数
    total = query.count()

    # 获取所有行业列表（用于下拉筛选）
    industries = db.session.query(Position.industry).filter(
        Position.quantity > 0,
        Position.industry != None,
        Position.industry != ''
    ).distinct().order_by(Position.industry).all()
    industry_list = [i[0] for i in industries if i[0]]

    # 分页排序
    positions = query.order_by(Position.updated_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    result = []
    for p in positions:
        cost = float(p.cost_price) if p.cost_price else 0
        current = float(p.current_price) if p.current_price else 0
        profit_pct = ((current - cost) / cost * 100) if cost > 0 else 0

        result.append({
            'id': p.id,
            'stock_code': p.stock_code,
            'stock_name': p.stock_name,
            'industry': p.industry,
            'quantity': p.quantity,
            'cost_price': cost,
            'current_price': current,
            'stop_loss_price': float(p.stop_loss_price) if p.stop_loss_price else 0,
            'stop_loss_pct': float(p.stop_loss_pct) if p.stop_loss_pct else 0,
            'stop_loss_type': p.stop_loss_type,
            'highest_price': float(p.highest_price) if p.highest_price else 0,
            'profit_pct': round(profit_pct, 2),
            'created_at': p.created_at.strftime('%Y-%m-%d %H:%M') if p.created_at else None,
            'updated_at': p.updated_at.strftime('%Y-%m-%d %H:%M') if p.updated_at else None
        })

    return jsonify({
        'success': True,
        'data': result,
        'total': total,
        'page': page,
        'page_size': page_size,
        'industries': industry_list
    })

@app.route('/api/actual-trades', methods=['GET'])
@jwt_required()
def get_actual_trades():
    """获取实盘交易记录（支持搜索和分页）"""
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    keyword = request.args.get('keyword', '')
    direction = request.args.get('direction', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    # 构建查询
    query = db.session.query(
        Trade.id,
        Trade.stock_code,
        Trade.stock_name,
        Trade.direction,
        Trade.price,
        Trade.quantity,
        Trade.amount,
        Trade.trade_date,
        Trade.strategy,
        Trade.remark,
        Trade.trade_type,
        Trade.profit_loss,
        Trade.profit_loss_pct,
        Trade.fee,
        Trade.created_at
    )

    # 条件过滤
    if keyword:
        query = query.filter(
            db.or_(
                Trade.stock_code.like(f'%{keyword}%'),
                Trade.stock_name.like(f'%{keyword}%'),
                Trade.remark.like(f'%{keyword}%')
            )
        )
    if direction:
        query = query.filter(Trade.direction == direction)
    if start_date:
        query = query.filter(Trade.trade_date >= start_date)
    if end_date:
        query = query.filter(Trade.trade_date <= end_date)

    # 总数
    total = query.count()

    # 分页排序
    trades = query.order_by(Trade.trade_date.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    result = []
    for t in trades:
        result.append({
            'id': t.id,
            'stock_code': t.stock_code,
            'stock_name': t.stock_name or '',
            'direction': t.direction,
            'price': float(t.price),
            'quantity': t.quantity,
            'amount': float(t.amount) if t.amount else 0,
            'trade_date': t.trade_date.strftime('%Y-%m-%d %H:%M') if t.trade_date else None,
            'strategy': t.strategy,
            'remark': t.remark,
            'trade_type': t.trade_type,
            'profit_loss': float(t.profit_loss) if t.profit_loss else 0,
            'profit_loss_pct': float(t.profit_loss_pct) if t.profit_loss_pct else 0,
            'fee': float(t.fee) if t.fee else 0
        })

    return jsonify({
        'success': True,
        'data': result,
        'total': total,
        'page': page,
        'page_size': page_size
    })

@app.route('/api/actual-stats', methods=['GET'])
@jwt_required()
def get_actual_stats():
    """获取实盘统计数据"""
    # 持仓数量
    position_count = Position.query.filter(Position.quantity > 0).count()

    # 交易记录数量
    trade_count = Trade.query.count()

    # 计算总持仓市值和总成本
    positions = Position.query.filter(Position.quantity > 0).all()
    total_market_value = sum(
        (float(p.current_price) if p.current_price else 0) * p.quantity
        for p in positions
    )
    total_cost = sum(
        (float(p.cost_price) if p.cost_price else 0) * p.quantity
        for p in positions
    )

    # 计算总盈亏（从 trades 表累计卖出盈亏）
    total_profit = db.session.query(db.func.sum(Trade.profit_loss)).filter(
        Trade.direction == 'SELL',
        Trade.profit_loss != 0
    ).scalar() or 0

    # 收益率
    profit_pct = ((total_market_value - total_cost) / total_cost * 100) if total_cost > 0 else 0

    return jsonify({
        'success': True,
        'data': {
            'position_count': position_count,
            'trade_count': trade_count,
            'total_market_value': round(total_market_value, 2),
            'total_cost': round(total_cost, 2),
            'total_profit': round(float(total_profit), 2),
            'profit_pct': round(profit_pct, 2)
        }
    })

@app.route('/api/actual-analysis', methods=['GET'])
@jwt_required()
def get_actual_analysis():
    """获取实盘收益分析数据（日/周/月收益率 + 日历热力图）"""
    # 获取所有快照数据
    snapshots = DailySnapshot.query.order_by(DailySnapshot.snapshot_date.desc()).all()

    if not snapshots:
        return jsonify({
            'success': True,
            'data': {
                'daily_returns': [],
                'weekly_returns': [],
                'monthly_returns': [],
                'calendar_data': [],
                'monthly_summary': []
            }
        })

    # 日收益率数据（最近 30 天，倒序）
    daily_returns = []
    for s in snapshots[:30]:
        daily_returns.append({
            'date': s.snapshot_date.strftime('%Y-%m-%d') if s.snapshot_date else '',
            'daily_return': float(s.daily_return) if s.daily_return else 0,
            'total_return': float(s.total_return) if s.total_return else 0,
            'total_asset': float(s.total_asset) if s.total_asset else 0
        })
    # 按日期倒序（最新的在前）
    daily_returns.sort(key=lambda x: x['date'], reverse=True)

    # 周收益率统计（按周分组）
    from collections import defaultdict
    from datetime import datetime, timedelta

    weekly_data = defaultdict(lambda: {'returns': [], 'dates': []})
    for s in snapshots:
        if s.snapshot_date:
            # ISO calendar: (year, week, weekday)
            iso_cal = s.snapshot_date.isocalendar()
            week_key = f"{iso_cal[0]}-W{iso_cal[1]:02d}"
            weekly_data[week_key]['returns'].append(float(s.daily_return) if s.daily_return else 0)
            weekly_data[week_key]['dates'].append(s.snapshot_date)

    weekly_returns = []
    for week, data in sorted(weekly_data.items(), key=lambda x: x[0], reverse=True)[:12]:
        # 计算这周的日期范围（周一到周日）
        dates = sorted(data['dates'])
        first_date = min(dates)
        # 找到第一个日期所在周的周一
        monday = first_date - timedelta(days=first_date.weekday())
        # 周日
        sunday = monday + timedelta(days=6)

        # 周收益率 = (1 + r1) * (1 + r2) * ... - 1
        compounded = 1.0
        for r in data['returns']:
            compounded *= (1 + r / 100)
        weekly_ret = (compounded - 1) * 100
        weekly_returns.append({
            'week': f"{monday.strftime('%m-%d')} ~ {sunday.strftime('%m-%d')}",
            'week_start': monday,
            'weekly_return': round(weekly_ret, 4),
            'trading_days': len(data['returns'])
        })

    # 按日期倒序排序（最新的在前）
    weekly_returns.sort(key=lambda x: x['week_start'], reverse=True)

    # 移除辅助字段
    for w in weekly_returns:
        del w['week_start']

    # 月收益率统计（最近 6 个月，倒序）
    monthly_data = defaultdict(list)
    for s in snapshots:
        if s.snapshot_date:
            month_key = s.snapshot_date.strftime('%Y-%m')
            monthly_data[month_key].append(float(s.daily_return) if s.daily_return else 0)

    monthly_returns = []
    for month, daily_rets in sorted(monthly_data.items(), key=lambda x: x[0], reverse=True)[:6]:
        compounded = 1.0
        for r in daily_rets:
            compounded *= (1 + r / 100)
        monthly_ret = (compounded - 1) * 100
        monthly_returns.append({
            'month': month,
            'monthly_return': round(monthly_ret, 4),
            'trading_days': len(daily_rets),
            'positive_days': sum(1 for r in daily_rets if r > 0),
            'negative_days': sum(1 for r in daily_rets if r < 0)
        })
    # 按月份倒序（最新的在前）
    monthly_returns.sort(key=lambda x: x['month'], reverse=True)

    # 日历热力图数据（最近 6 个月）
    calendar_data = []
    for s in snapshots:
        if s.snapshot_date:
            calendar_data.append({
                'date': s.snapshot_date.strftime('%Y-%m-%d'),
                'return': float(s.daily_return) if s.daily_return else 0,
                'total_asset': float(s.total_asset) if s.total_asset else 0
            })

    # 月度汇总统计（最近 6 个月，倒序）
    monthly_summary = []
    for month, data in sorted(monthly_data.items(), key=lambda x: x[0], reverse=True)[:6]:
        compounded = 1.0
        for r in data:
            compounded *= (1 + r / 100)
        monthly_ret = (compounded - 1) * 100
        positive_days = sum(1 for r in data if r > 0)
        negative_days = sum(1 for r in data if r < 0)
        max_daily = max(data) if data else 0
        min_daily = min(data) if data else 0

        monthly_summary.append({
            'month': month,
            'return': round(monthly_ret, 4),
            'trading_days': len(data),
            'positive_days': positive_days,
            'negative_days': negative_days,
            'win_rate': round(positive_days / len(data) * 100, 2) if data else 0,
            'max_daily': round(max_daily, 4),
            'min_daily': round(min_daily, 4)
        })
    # 按月份倒序（最新的在前）
    monthly_summary.sort(key=lambda x: x['month'], reverse=True)

    return jsonify({
        'success': True,
        'data': {
            'daily_returns': daily_returns,
            'weekly_returns': weekly_returns,
            'monthly_returns': monthly_returns,
            'calendar_data': calendar_data,
            'monthly_summary': monthly_summary
        }
    })

@app.route('/api/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """获取统计数据"""
    # 持仓数量
    position_count = SimPosition.query.filter(SimPosition.quantity > 0).count()
    
    # 自选表数量
    watchlist_count = Watchlist.query.filter_by(status='active').count()
    
    # 账户信息
    account = SimAccount.query.filter_by(id=1).first()
    
    stats = {
        'position_count': position_count,
        'watchlist_count': watchlist_count,
        'total_capital': float(account.total_capital) if account else 0,
        'total_value': float(account.total_value) if account else 0,
        'cash': float(account.cash) if account else 0
    }
    
    return jsonify({'success': True, 'data': stats})

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'time': datetime.now().isoformat()})

# ============== 初始化 ==============

def init_db():
    with app.app_context():
        db.create_all()
        
        # 创建默认管理员账户
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@stockmonitor.local')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ 默认管理员账户已创建：admin / admin123")

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
