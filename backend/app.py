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

class SimTrade(db.Model):
    """模拟交易记录表 (映射到 sim_trades 表)"""
    __tablename__ = 'sim_trades'
    id = db.Column(db.Integer, primary_key=True)
    stock_code = db.Column(db.String(20), nullable=False)
    stock_name = db.Column(db.String(100), nullable=False)
    action = db.Column(db.Enum('BUY', 'SELL'), nullable=False)  # 数据库中是 action
    price = db.Column(db.Numeric(10,2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Numeric(12,2), nullable=False)
    trade_date = db.Column(db.DateTime, nullable=False)
    cost = db.Column(db.Numeric(12,2))  # 交易成本/持仓成本
    reason = db.Column(db.String(200))  # 数据库中是 reason
    created_at = db.Column(db.DateTime)

    # 别名属性，方便代码使用
    @property
    def direction(self):
        return self.action

    @property
    def strategy(self):
        return self.reason

    @property
    def remark(self):
        return None

    @property
    def profit_loss(self):
        """计算盈亏：卖出时 = 成交金额 - 成本"""
        if self.action == 'SELL' and self.cost:
            return float(self.amount) - float(self.cost)
        return 0

    @property
    def profit_loss_pct(self):
        """计算盈亏比例"""
        if self.action == 'SELL' and self.cost and float(self.cost) > 0:
            return (float(self.amount) - float(self.cost)) / float(self.cost) * 100
        return 0

    @property
    def fee(self):
        return 0

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
    sh_index_return = db.Column(db.Numeric(10,4))  # 上证指数收益率
    sh_index_close = db.Column(db.Numeric(10,4))   # 上证指数收盘价
    created_at = db.Column(db.DateTime)

class SimDailySnapshot(db.Model):
    """模拟盘每日收盘快照"""
    __tablename__ = 'sim_daily_snapshots'
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

@app.route('/api/sim-trades', methods=['GET'])
@jwt_required()
def get_sim_trades():
    """获取模拟交易记录（支持搜索和分页）"""
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    keyword = request.args.get('keyword', '')
    direction = request.args.get('direction', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    # 构建查询 - 使用数据库实际字段名
    query = db.session.query(
        SimTrade.id,
        SimTrade.stock_code,
        SimTrade.stock_name,
        SimTrade.action,
        SimTrade.price,
        SimTrade.quantity,
        SimTrade.amount,
        SimTrade.trade_date,
        SimTrade.reason,
        SimTrade.created_at
    )

    # 条件过滤
    if keyword:
        query = query.filter(
            db.or_(
                SimTrade.stock_code.like(f'%{keyword}%'),
                SimTrade.stock_name.like(f'%{keyword}%')
            )
        )
    if direction:
        query = query.filter(SimTrade.action == direction)
    if start_date:
        query = query.filter(SimTrade.trade_date >= start_date)
    if end_date:
        query = query.filter(SimTrade.trade_date <= end_date)

    # 总数
    total = query.count()

    # 分页排序
    trades = query.order_by(SimTrade.trade_date.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    result = []
    for t in trades:
        result.append({
            'id': t.id,
            'stock_code': t.stock_code,
            'stock_name': t.stock_name or '',
            'direction': t.action,
            'price': float(t.price),
            'quantity': t.quantity,
            'amount': float(t.amount) if t.amount else 0,
            'trade_date': t.trade_date.strftime('%Y-%m-%d %H:%M') if t.trade_date else None,
            'strategy': t.reason,
            'remark': '',
            'profit_loss': 0,
            'profit_loss_pct': 0,
            'fee': 0
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

    # 日收益率数据（最近 60 天，倒序）
    daily_returns = []
    for s in snapshots[:60]:
        daily_returns.append({
            'date': s.snapshot_date.strftime('%Y-%m-%d') if s.snapshot_date else '',
            'daily_return': float(s.daily_return) if s.daily_return else 0,
            'total_return': float(s.total_return) if s.total_return else 0,
            'total_asset': float(s.total_asset) if s.total_asset else 0,
            'sh_index_return': float(s.sh_index_return) if s.sh_index_return else 0
        })
    # 按日期倒序（最新的在前）
    daily_returns.sort(key=lambda x: x['date'], reverse=True)

    # 周收益率统计（按周分组）
    from collections import defaultdict
    from datetime import datetime, timedelta

    weekly_data = defaultdict(lambda: {'returns': [], 'sh_returns': [], 'dates': []})
    for s in snapshots:
        if s.snapshot_date:
            # ISO calendar: (year, week, weekday)
            iso_cal = s.snapshot_date.isocalendar()
            week_key = f"{iso_cal[0]}-W{iso_cal[1]:02d}"
            weekly_data[week_key]['returns'].append(float(s.daily_return) if s.daily_return else 0)
            weekly_data[week_key]['sh_returns'].append(float(s.sh_index_return) if s.sh_index_return else 0)
            weekly_data[week_key]['dates'].append(s.snapshot_date)

    weekly_returns = []
    for week, data in sorted(weekly_data.items(), key=lambda x: x[0], reverse=True)[:30]:
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

        # 上证指数周收益率
        sh_compounded = 1.0
        for r in data['sh_returns']:
            sh_compounded *= (1 + r / 100)
        sh_weekly_ret = (sh_compounded - 1) * 100

        weekly_returns.append({
            'week': f"{monday.strftime('%m-%d')} ~ {sunday.strftime('%m-%d')}",
            'week_start': monday,
            'weekly_return': round(weekly_ret, 4),
            'sh_index_return': round(sh_weekly_ret, 4),
            'trading_days': len(data['returns'])
        })

    # 按日期倒序排序（最新的在前）
    weekly_returns.sort(key=lambda x: x['week_start'], reverse=True)

    # 移除辅助字段
    for w in weekly_returns:
        del w['week_start']

    # 月收益率统计（最近 15 个月，倒序）
    monthly_data = defaultdict(lambda: {'returns': [], 'sh_returns': []})
    for s in snapshots:
        if s.snapshot_date:
            month_key = s.snapshot_date.strftime('%Y-%m')
            monthly_data[month_key]['returns'].append(float(s.daily_return) if s.daily_return else 0)
            monthly_data[month_key]['sh_returns'].append(float(s.sh_index_return) if s.sh_index_return else 0)

    monthly_returns = []
    for month, data in sorted(monthly_data.items(), key=lambda x: x[0], reverse=True)[:15]:
        compounded = 1.0
        for r in data['returns']:
            compounded *= (1 + r / 100)
        monthly_ret = (compounded - 1) * 100

        # 上证指数月收益率
        sh_compounded = 1.0
        for r in data['sh_returns']:
            sh_compounded *= (1 + r / 100)
        sh_monthly_ret = (sh_compounded - 1) * 100

        monthly_returns.append({
            'month': month,
            'monthly_return': round(monthly_ret, 4),
            'sh_index_return': round(sh_monthly_ret, 4),
            'trading_days': len(data['returns']),
            'positive_days': sum(1 for r in data['returns'] if r > 0),
            'negative_days': sum(1 for r in data['returns'] if r < 0)
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
        for r in data['returns']:
            compounded *= (1 + r / 100)
        monthly_ret = (compounded - 1) * 100

        # 上证指数月收益率
        sh_compounded = 1.0
        for r in data['sh_returns']:
            sh_compounded *= (1 + r / 100)
        sh_monthly_ret = (sh_compounded - 1) * 100

        positive_days = sum(1 for r in data['returns'] if r > 0)
        negative_days = sum(1 for r in data['returns'] if r < 0)
        max_daily = max(data['returns']) if data['returns'] else 0
        min_daily = min(data['returns']) if data['returns'] else 0

        monthly_summary.append({
            'month': month,
            'return': round(monthly_ret, 4),
            'sh_index_return': round(sh_monthly_ret, 4),
            'trading_days': len(data['returns']),
            'positive_days': positive_days,
            'negative_days': negative_days,
            'win_rate': round(positive_days / len(data['returns']) * 100, 2) if data['returns'] else 0,
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

@app.route('/api/sim-stats', methods=['GET'])
@jwt_required()
def get_sim_stats():
    """获取模拟盘统计数据"""
    # 持仓数量
    position_count = SimPosition.query.filter(SimPosition.quantity > 0).count()

    # 交易记录数量
    trade_count = SimTrade.query.count()

    # 计算总持仓市值和总成本
    positions = SimPosition.query.filter(SimPosition.quantity > 0).all()
    total_market_value = sum(
        0  # 模拟盘暂不计算实时市值
        for p in positions
    )
    total_cost = sum(
        (float(p.cost_price) if p.cost_price else 0) * p.quantity
        for p in positions
    )

    # 计算总盈亏 = 已实现盈亏（卖出交易）+ 未实现盈亏（当前持仓）
    realized_profit = db.session.query(db.func.sum(SimTrade.amount - SimTrade.cost)).filter(
        SimTrade.action == 'SELL'
    ).scalar() or 0

    # 未实现盈亏 = 当前持仓市值 - 持仓成本（模拟盘暂不计算实时市值，所以为 0）
    unrealized_profit = 0  # 持仓浮动盈亏

    total_profit = realized_profit + unrealized_profit

    # 账户信息
    account = SimAccount.query.filter_by(id=1).first()

    # 如果有账户，计算收益率
    if account and account.total_capital:
        profit_pct = ((float(account.total_value) - float(account.total_capital)) / float(account.total_capital) * 100)
    else:
        profit_pct = 0

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

@app.route('/api/sim-analysis', methods=['GET'])
@jwt_required()
def get_sim_analysis():
    """获取模拟盘收益分析数据（日/周/月收益率 + 日历热力图）"""
    # 获取所有快照数据
    snapshots = SimDailySnapshot.query.order_by(SimDailySnapshot.snapshot_date.desc()).all()

    if not snapshots:
        return jsonify({
            'success': True,
            'data': {
                'daily_returns': [],
                'weekly_returns': [],
                'monthly_returns': [],
                'calendar_data': [],
                'monthly_summary': [],
                'daily_positions': [],
                'weekly_positions': [],
                'monthly_positions': []
            }
        })

    # 日收益率数据（最近 60 天，倒序）
    daily_returns = []
    daily_positions = []
    for s in snapshots[:60]:
        daily_returns.append({
            'date': s.snapshot_date.strftime('%Y-%m-%d') if s.snapshot_date else '',
            'daily_return': float(s.daily_return) if s.daily_return else 0,
            'total_return': float(s.total_return) if s.total_return else 0,
            'total_asset': float(s.total_asset) if s.total_asset else 0
        })
        # 仓位数据：由于旧数据 position_value 为 0，我们用 total_asset 作为参考
        # 仓位比例 = 持仓市值 / 总资产，如果 position_value 为 0 则用 total_asset 推断
        pos_value = float(s.position_value) if s.position_value else 0
        total_asset = float(s.total_asset) if s.total_asset else 0
        # 如果 position_value 为 0，尝试用总资产变化推断（简化的处理）
        pos_ratio = (pos_value / total_asset * 100) if total_asset > 0 else 0
        daily_positions.append({
            'date': s.snapshot_date.strftime('%Y-%m-%d') if s.snapshot_date else '',
            'position_value': pos_value,
            'position_ratio': round(pos_ratio, 2),
            'total_asset': total_asset
        })
    # 按日期倒序（最新的在前）
    daily_returns.sort(key=lambda x: x['date'], reverse=True)
    daily_positions.sort(key=lambda x: x['date'], reverse=True)

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
    for week, data in sorted(weekly_data.items(), key=lambda x: x[0], reverse=True)[:30]:
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

    # 周仓位数据
    weekly_positions = []
    for w in weekly_returns:
        # 计算这周的平均仓位
        week_str = w['week']
        # 从 week_str 提取日期范围，如 "04-01 ~ 04-07"
        try:
            start_date_str, end_date_str = week_str.split(' ~ ')
            # 使用 2026 年作为基准年份（因为快照数据是 2026 年的）
            year = 2026
            monday = datetime.strptime(f"{year}-{start_date_str}", "%Y-%m-%d").date()
            sunday = datetime.strptime(f"{year}-{end_date_str}", "%Y-%m-%d").date()

            # 计算这周的平均仓位比例
            week_snapshots = [s for s in snapshots if s.snapshot_date and monday <= s.snapshot_date <= sunday]
            avg_pos_ratio = 0
            avg_position_value = 0
            if week_snapshots:
                total_assets = []
                position_values = []
                for ws in week_snapshots:
                    if ws.total_asset and ws.position_value:
                        total_assets.append(float(ws.total_asset))
                        position_values.append(float(ws.position_value))
                if total_assets and sum(total_assets) > 0:
                    avg_position_value = sum(position_values) / len(position_values) if position_values else 0
                    avg_pos_ratio = (sum(position_values) / sum(total_assets) * 100) if total_assets else 0

            weekly_positions.append({
                'week': week_str,
                'position_ratio': round(avg_pos_ratio, 2),
                'position_value': round(avg_position_value, 2)
            })
        except Exception as e:
            # 如果解析失败，使用简化的方式
            weekly_positions.append({
                'week': w['week'],
                'position_ratio': 0,
                'position_value': 0
            })

        del w['week_start']

    # 月收益率统计（最近 15 个月，倒序）— 模拟盘
    # 先找到最早的月份，然后填充所有月份（包括空仓月份）
    from dateutil.relativedelta import relativedelta

    monthly_data = defaultdict(list)
    for s in snapshots:
        if s.snapshot_date:
            month_key = s.snapshot_date.strftime('%Y-%m')
            monthly_data[month_key].append(float(s.daily_return) if s.daily_return else 0)

    # 获取所有存在的月份
    existing_months = set(monthly_data.keys())

    # 找到最近和有数据的月份
    sorted_months = sorted(existing_months)
    if sorted_months:
        earliest_month = sorted_months[0]
        latest_month = sorted_months[-1]

        # 从最早月份往前推，确保有 15 个月的数据
        earliest_dt = datetime.strptime(earliest_month, '%Y-%m')
        latest_dt = datetime.strptime(latest_month, '%Y-%m')

        # 计算需要往前推多少个月才能凑够 15 个月
        months_diff = (latest_dt.year - earliest_dt.year) * 12 + (latest_dt.month - earliest_dt.month)
        if months_diff < 14:
            months_to_add = 14 - months_diff
            earliest_dt = earliest_dt - relativedelta(months=months_to_add)

        # 生成连续的月份列表
        all_months = []
        current_dt = earliest_dt
        while current_dt <= latest_dt:
            all_months.append(current_dt.strftime('%Y-%m'))
            current_dt = current_dt + relativedelta(months=1)
    else:
        all_months = []

    monthly_returns = []
    monthly_positions = []
    for month in all_months[-15:]:  # 取最近 15 个月
        daily_rets = monthly_data.get(month, [])

        if daily_rets:
            compounded = 1.0
            for r in daily_rets:
                compounded *= (1 + r / 100)
            monthly_ret = (compounded - 1) * 100
        else:
            monthly_ret = 0

        monthly_returns.append({
            'month': month,
            'monthly_return': round(monthly_ret, 4),
            'trading_days': len(daily_rets),
            'positive_days': sum(1 for r in daily_rets if r > 0),
            'negative_days': sum(1 for r in daily_rets if r < 0)
        })

        # 计算月平均仓位
        month_snapshots = [s for s in snapshots if s.snapshot_date and s.snapshot_date.strftime('%Y-%m') == month]
        avg_pos_ratio = 0
        avg_position_value = 0
        if month_snapshots:
            total_assets = []
            position_values = []
            for ms in month_snapshots:
                if ms.total_asset and ms.position_value:
                    total_assets.append(float(ms.total_asset))
                    position_values.append(float(ms.position_value))
            if total_assets and sum(total_assets) > 0:
                avg_position_value = sum(position_values) / len(position_values) if position_values else 0
                avg_pos_ratio = (sum(position_values) / sum(total_assets) * 100) if total_assets else 0

        monthly_positions.append({
            'month': month,
            'position_ratio': round(avg_pos_ratio, 2),
            'position_value': round(avg_position_value, 2)
        })
    # 按月份倒序（最新的在前）— 模拟盘
    monthly_returns.sort(key=lambda x: x['month'], reverse=True)
    monthly_positions.sort(key=lambda x: x['month'], reverse=True)

    # 日历热力图数据（最近 6 个月）— 模拟盘
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
    # 按月份倒序（最新的在前）— 模拟盘
    monthly_summary.sort(key=lambda x: x['month'], reverse=True)

    return jsonify({
        'success': True,
        'data': {
            'daily_returns': daily_returns,
            'weekly_returns': weekly_returns,
            'monthly_returns': monthly_returns,
            'calendar_data': calendar_data,
            'monthly_summary': monthly_summary,
            'daily_positions': daily_positions,
            'weekly_positions': weekly_positions,
            'monthly_positions': monthly_positions
        }
    })

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
