from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from data_fetcher import fetch_stock_data, get_fetcher_manager

app = Flask(__name__)
CORS(app)

Base = declarative_base()
DATABASE_URL = 'sqlite:///./finance.db'
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Holding(Base):
    __tablename__ = "holdings"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    name = Column(String, default="")
    holding_type = Column(String, index=True)
    quantity = Column(Float)
    cost_price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class CheckReport(Base):
    __tablename__ = "check_reports"
    id = Column(Integer, primary_key=True, index=True)
    report_date = Column(DateTime, default=datetime.utcnow)
    report_content = Column(Text)

class APIKeyConfig(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String, unique=True, index=True)
    api_key = Column(String)
    updated_at = Column(DateTime, default=datetime.utcnow)

class PriceHistory(Base):
    __tablename__ = "price_history"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    check_date = Column(DateTime, index=True)
    price = Column(Float)
    data_source = Column(String)

Base.metadata.create_all(bind=engine)

def load_api_keys():
    """从数据库加载 API Keys 到数据获取器"""
    db = get_db()
    manager = get_fetcher_manager()
    keys = db.query(APIKeyConfig).all()
    for key in keys:
        manager.set_api_key(key.source_name, key.api_key)
    db.close()

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()



@app.route('/')
def index():
    return jsonify({"message": "交易纪律检查工具 API 运行中"})

@app.route('/api/holdings', methods=['GET'])
def get_holdings():
    db = get_db()
    holdings = db.query(Holding).all()
    
    holdings_data = []
    for h in holdings:
        last_price = db.query(PriceHistory).filter(
            PriceHistory.symbol == h.symbol
        ).order_by(PriceHistory.check_date.desc()).first()
        
        holdings_data.append({
            'id': h.id,
            'symbol': h.symbol,
            'name': h.name,
            'type': h.holding_type,
            'quantity': h.quantity,
            'costPrice': h.cost_price,
            'lastCheckPrice': last_price.price if last_price else None,
            'lastCheckDate': last_price.check_date.strftime('%Y-%m-%d') if last_price else None
        })
    
    db.close()
    return jsonify(holdings_data)

@app.route('/api/holdings', methods=['POST'])
def add_holding():
    data = request.json
    db = get_db()
    holding = Holding(
        symbol=data['symbol'].upper(),
        name=data.get('name', ''),
        holding_type=data['type'],
        quantity=data['quantity'],
        cost_price=data['costPrice']
    )
    db.add(holding)
    db.commit()
    db.refresh(holding)
    return jsonify({
        'id': holding.id,
        'symbol': holding.symbol,
        'name': holding.name,
        'type': holding.holding_type,
        'quantity': holding.quantity,
        'costPrice': holding.cost_price
    })

@app.route('/api/holdings/<int:holding_id>', methods=['PUT'])
def update_holding(holding_id):
    data = request.json
    db = get_db()
    holding = db.query(Holding).filter(Holding.id == holding_id).first()
    if not holding:
        return jsonify({'error': 'Holding not found'}), 404
    holding.symbol = data['symbol'].upper()
    holding.name = data.get('name', '')
    holding.holding_type = data['type']
    holding.quantity = data['quantity']
    holding.cost_price = data['costPrice']
    db.commit()
    return jsonify({'success': True})

@app.route('/api/holdings/<int:holding_id>', methods=['DELETE'])
def delete_holding(holding_id):
    db = get_db()
    holding = db.query(Holding).filter(Holding.id == holding_id).first()
    if not holding:
        return jsonify({'error': 'Holding not found'}), 404
    db.delete(holding)
    db.commit()
    return jsonify({'success': True})

@app.route('/api/sources', methods=['GET'])
def get_sources():
    manager = get_fetcher_manager()
    return jsonify({
        'available': manager.get_available_sources()
    })

@app.route('/api/api-keys', methods=['GET'])
def get_api_keys():
    db = get_db()
    keys = db.query(APIKeyConfig).all()
    result = {}
    for key in keys:
        result[key.source_name] = key.api_key
    db.close()
    return jsonify(result)

@app.route('/api/api-keys', methods=['POST'])
def save_api_key():
    data = request.json
    source_name = data.get('sourceName')
    api_key = data.get('apiKey', '')
    
    db = get_db()
    existing = db.query(APIKeyConfig).filter(APIKeyConfig.source_name == source_name).first()
    
    if existing:
        existing.api_key = api_key
        existing.updated_at = datetime.utcnow()
    else:
        new_key = APIKeyConfig(
            source_name=source_name,
            api_key=api_key
        )
        db.add(new_key)
    
    db.commit()
    
    manager = get_fetcher_manager()
    manager.set_api_key(source_name, api_key)
    
    db.close()
    return jsonify({'success': True})

@app.route('/api/check', methods=['POST'])
def run_check():
    db = get_db()
    holdings = db.query(Holding).all()
    
    total_value = 0
    total_cost = 0
    holding_data = []
    
    now = datetime.now()
    
    for h in holdings:
        stock_info, current_price, source = fetch_stock_data(h.symbol)
        value = current_price * h.quantity
        cost = h.cost_price * h.quantity
        
        total_value += value
        total_cost += cost
        
        holding_data.append({
            'id': h.id,
            'symbol': h.symbol,
            'name': h.name,
            'type': h.holding_type,
            'quantity': h.quantity,
            'costPrice': h.cost_price,
            'currentPrice': current_price,
            'ma20': stock_info['ma20'] if stock_info else None,
            'dataSource': source,
            'value': value,
            'cost': cost,
            'returnPct': ((current_price - h.cost_price) / h.cost_price) * 100,
            'returnValue': value - cost
        })
        
        price_history = PriceHistory(
            symbol=h.symbol,
            check_date=now,
            price=current_price,
            data_source=source
        )
        db.add(price_history)
    
    week_number = now.isocalendar()[1]
    is_quarter_start = (now.month - 1) % 3 == 0 and now.weekday() <= 6 and now.day <= 7
    
    must_do = []
    forbidden = []
    no_action = []
    
    for h in holding_data:
        if h['type'] == 'cash':
            continue
            
        if h['returnPct'] <= -12:
            must_do.append(f"🔴 {h['symbol']} 触发止损 ({h['returnPct']:.1f}%) → 立即清仓")
        elif h['returnPct'] > 30:
            must_do.append(f"🟡 {h['symbol']} 触发止盈 (+{h['returnPct']:.1f}%) → 卖出1/3")
        
        if h['ma20'] and h['currentPrice'] < h['ma20']:
            forbidden.append(f"⛔ {h['symbol']} 低于20周均线 → 禁止新资金买入")
    
    if not must_do and not forbidden:
        no_action.append("✓ 所有持仓正常，无操作需求")
    
    if is_quarter_start:
        must_do.append("📅 新季度首周 → 检查现金分配")
    else:
        no_action.append("✓ 非季度首周，现金保持不变")
    
    total_return = total_value - total_cost
    total_return_pct = (total_return / total_cost) * 100 if total_cost > 0 else 0
    
    type_distribution = {}
    stock_distribution = {}
    
    for h in holding_data:
        if h['type'] not in type_distribution:
            type_distribution[h['type']] = 0
        type_distribution[h['type']] += h['value']
        
        key = h['symbol']
        if key not in stock_distribution:
            stock_distribution[key] = 0
        stock_distribution[key] += h['value']
    
    report = {
        'date': now.strftime('%Y年%m月%d日'),
        'week': week_number,
        'mustDo': must_do,
        'forbidden': forbidden,
        'noAction': no_action,
        'holdings': holding_data,
        'totalValue': total_value,
        'totalCost': total_cost,
        'totalReturn': total_return,
        'totalReturnPct': total_return_pct,
        'typeDistribution': type_distribution,
        'stockDistribution': stock_distribution
    }
    
    report_record = CheckReport(
        report_content=str(report)
    )
    db.add(report_record)
    db.commit()
    
    return jsonify(report)

@app.route('/api/reports', methods=['GET'])
def get_reports():
    db = get_db()
    reports = db.query(CheckReport).order_by(CheckReport.report_date.desc()).limit(10).all()
    return jsonify([{
        'id': r.id,
        'date': r.report_date.strftime('%Y-%m-%d %H:%M'),
        'content': r.report_content
    } for r in reports])

if __name__ == '__main__':
    load_api_keys()
    app.run(debug=True, port=5000)
