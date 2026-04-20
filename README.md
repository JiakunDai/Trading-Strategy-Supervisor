# 📊 交易纪律检查工具

一个简洁、强大的交易纪律执行器，帮助你每周机械化执行交易策略。

## ✨ 功能特点

- **自定义持仓管理** - 自由添加、编辑、删除任意股票/ETF
- **灵活的仓位分类** - 支持保守型、核心型、现金型仓位标签
- **自动数据获取** - Yahoo Finance API，失败时自动切换模拟数据
- **6项周度纪律检查**
  - 现金分配检查
  - 20周均线检查
  - 止损检查（-12%）
  - 止盈检查（+30%）
  - 再平衡检查
- **自动定时任务** - 每周一早上9点自动检查
- **SQLite数据库** - 数据持久化，支持跨设备（需部署到服务器）

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务器

Windows用户双击 `start.bat`

或者手动启动：
```bash
cd backend
python app.py
```

### 3. 打开前端

直接用浏览器打开 `frontend/index.html`

### 4. （可选）启动定时任务

在另一个终端窗口运行：
```bash
cd backend
python scheduler.py
```

## 📁 项目结构

```
finnance/
├── requirements.txt       # Python依赖
├── start.bat         # Windows启动脚本
├── README.md         # 本文件
├── backend/
│   ├── app.py        # Flask后端服务器
│   ├── scheduler.py  # 定时任务
│   └── finance.db   # SQLite数据库（自动生成）
└── frontend/
    └── index.html   # 前端页面
```

## 🔧 使用说明

### 添加持仓
1. 点击「持仓管理」标签页
2. 点击「+ 添加持仓」
3. 填写：
   - 股票代码（如 AAPL, MSFT, VOO）
   - 名称（可选）
   - 仓位类型
   - 持有数量
   - 成本价
   - 目标权重（可选）

### 运行纪律检查
1. 点击「纪律检查」标签页
2. 点击「🔍 运行周度纪律检查」
3. 查看生成的报告

### 自动周度检查
运行 `scheduler.py` 后，每周一早上9点会自动执行检查

## 💡 技术方案

### 前端
- 纯 HTML/CSS/JavaScript
- 响应式设计

### 后端
- Flask 框架
- SQLAlchemy ORM
- SQLite 数据库
- yfinance 获取股票数据
- schedule 定时任务

### 跨设备解决方案
当前使用本地 SQLite 数据库。如需跨设备：
1. 将后端部署到云服务器（如阿里云、腾讯云）
2. 或将 SQLite 换成 MySQL/PostgreSQL
3. 或使用云数据库服务

## 📝 注意事项

- 确保后端服务在运行时使用前端
- 股票数据来自 Yahoo Finance，可能有延迟
- 如遇 API 问题，系统会自动使用模拟数据
