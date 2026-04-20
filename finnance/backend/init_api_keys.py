#!/usr/bin/env python3
"""
API Key 初始化脚本
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app import Base, APIKeyConfig

DATABASE_URL = 'sqlite:///./finance.db'
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 你提供的 API Keys
API_KEYS = {
    'Alpha Vantage': '82707WR01RKFMIK9',
    'Polygon.io': 'vSHres4HQI6PUeZ26NY7aSip0em7XwnX',
    'Finnhub': 'd5icoghr01qmmfjg3se0d5icoghr01qmmfjg3seg'
}

def init_api_keys():
    db = SessionLocal()
    
    print("=" * 60)
    print("  初始化 API Keys")
    print("=" * 60)
    print()
    
    for source_name, api_key in API_KEYS.items():
        existing = db.query(APIKeyConfig).filter(APIKeyConfig.source_name == source_name).first()
        
        if existing:
            existing.api_key = api_key
            existing.updated_at = datetime.utcnow()
            print(f"[更新] {source_name}")
        else:
            new_key = APIKeyConfig(
                source_name=source_name,
                api_key=api_key
            )
            db.add(new_key)
            print(f"[新增] {source_name}")
    
    db.commit()
    db.close()
    
    print()
    print("=" * 60)
    print("  API Keys 保存成功！")
    print("=" * 60)
    print()
    print("已配置的数据源：")
    for name in API_KEYS.keys():
        print(f"  ✓ {name}")

if __name__ == "__main__":
    init_api_keys()
