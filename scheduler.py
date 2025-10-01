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
        # 새로운 종합 크롤러 실행
        result = subprocess.run([sys.executable, "comprehensive_crawler.py"], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print(f"[{datetime.now()}] 크롤링 작업 완료")
            print("출력:", result.stdout)
            
            # Git에 자동 커밋 및 푸시
            git_commit_and_push()
        else:
            print(f"[{datetime.now()}] 크롤링 작업 실패")
            print("오류:", result.stderr)
            
    except Exception as e:
        print(f"[{datetime.now()}] 크롤링 실행 중 오류: {e}")

def git_commit_and_push():
    """Git에 자동으로 커밋하고 푸시"""
    try:
        print(f"[{datetime.now()}] Git 커밋 및 푸시 시작...")
        
        # Git 상태 확인
        status_result = subprocess.run(['git', 'status', '--porcelain'], 
                                     capture_output=True, text=True, cwd=os.getcwd())
        
        if status_result.returncode == 0 and status_result.stdout.strip():
            # 변경된 파일이 있으면 커밋
            subprocess.run(['git', 'add', '.'], cwd=os.getcwd())
            
            current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            commit_message = f"자동 업데이트: {current_date}"
            
            commit_result = subprocess.run(['git', 'commit', '-m', commit_message], 
                                         cwd=os.getcwd())
            
            if commit_result.returncode == 0:
                # 푸시 실행
                push_result = subprocess.run(['git', 'push', 'origin', 'main'], 
                                           cwd=os.getcwd())
                
                if push_result.returncode == 0:
                    print(f"[{datetime.now()}] Git 푸시 완료")
                else:
                    print(f"[{datetime.now()}] Git 푸시 실패")
            else:
                print(f"[{datetime.now()}] Git 커밋 실패")
        else:
            print(f"[{datetime.now()}] 변경된 파일이 없어 Git 작업을 건너뜁니다.")
            
    except Exception as e:
        print(f"[{datetime.now()}] Git 작업 중 오류: {e}")

def main():
    """스케줄러 메인 함수 (GitHub Actions 사용으로 비활성화)"""
    print("전기차 데이터 크롤링 스케줄러")
    print("현재 GitHub Actions를 사용하여 서버에서 자동 크롤링을 실행합니다.")
    print("로컬 스케줄러는 비활성화되었습니다.")
    
    # GitHub Actions를 사용하므로 로컬 스케줄러는 비활성화
    # 매일 오전 9시에 크롤링 실행
    # schedule.every().day.at("09:00").do(run_crawler)
    
    # 수동 테스트를 위한 옵션
    print("\n수동 테스트를 원하시면 아래 주석을 해제하세요:")
    print("# run_crawler()")
    
    # 스케줄러 실행 (비활성화됨)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(60)  # 1분마다 체크

if __name__ == "__main__":
    main()
