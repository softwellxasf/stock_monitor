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
    positions = SimPosition.query.filter(SimPosition.quantity > 0).all()
    
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
    
    return jsonify({'success': True, 'data': result})

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
