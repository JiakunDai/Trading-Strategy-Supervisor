@echo off
echo ========================================
echo    交易纪律检查工具 - 启动脚本
echo ========================================
echo.

echo [1/3] 检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

echo.
echo [2/3] 安装依赖包...
pip install -r requirements.txt

echo.
echo [3/3] 启动Flask服务器...
echo.
echo ========================================
echo    服务器启动中...
echo    前端地址: http://localhost:5000 或直接打开 frontend/index.html
echo    后端API: http://localhost:5000/api
echo.
echo    按 Ctrl+C 停止服务器
echo ========================================
echo.

cd backend
python app.py
