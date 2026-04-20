import schedule
import time
import requests
from datetime import datetime

def run_weekly_check():
    print(f"[{datetime.now()}] 执行周度纪律检查...")
    try:
        response = requests.post('http://localhost:5000/api/check')
        if response.status_code == 200:
            print(f"[{datetime.now()}] 周度检查完成！")
        else:
            print(f"[{datetime.now()}] 检查失败: {response.status_code}")
    except Exception as e:
        print(f"[{datetime.now()}] 错误: {e}")

def main():
    print("交易纪律检查定时任务已启动...")
    print("每周一早上9点自动执行检查")
    
    # 每周一 09:00 执行
    schedule.every().monday.at("09:00").do(run_weekly_check)
    
    # 测试：每分钟执行一次（方便测试）
    # schedule.every(1).minutes.do(run_weekly_check)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
