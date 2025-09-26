import schedule
import time
import subprocess
import sys
import os
from datetime import datetime

def run_crawler():
    """크롤러 실행"""
    print(f"[{datetime.now()}] 크롤링 작업 시작...")
    
    try:
        # 크롤러 실행
        result = subprocess.run([sys.executable, "crawler.py"], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print(f"[{datetime.now()}] 크롤링 작업 완료")
            print("출력:", result.stdout)
        else:
            print(f"[{datetime.now()}] 크롤링 작업 실패")
            print("오류:", result.stderr)
            
    except Exception as e:
        print(f"[{datetime.now()}] 크롤링 실행 중 오류: {e}")

def main():
    """스케줄러 메인 함수"""
    print("환경부 무공해차 보조금 데이터 크롤링 스케줄러 시작")
    print("매일 오전 9시에 크롤링을 실행합니다.")
    
    # 매일 오전 9시에 크롤링 실행
    schedule.every().day.at("09:00").do(run_crawler)
    
    # 시작 시 한 번 실행 (선택사항)
    # run_crawler()
    
    # 스케줄러 실행
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 체크

if __name__ == "__main__":
    main()
