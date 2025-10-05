#!/usr/bin/env python3
"""
ChromeDriver 수동 설치 및 테스트 스크립트
"""
import os
import sys
import subprocess
import requests
import zipfile
import shutil
from pathlib import Path

def get_chrome_version():
    """Chrome 버전 확인"""
    try:
        result = subprocess.run(['google-chrome', '--version'], capture_output=True, text=True)
        version = result.stdout.strip().split()[-1]
        major_version = version.split('.')[0]
        print(f'Chrome 버전: {version} (메이저: {major_version})')
        return version, major_version
    except Exception as e:
        print(f'Chrome 버전 확인 실패: {e}')
        return None, None

def download_chromedriver(chrome_major):
    """Chrome 메이저 버전에 맞는 ChromeDriver 다운로드 - 여러 버전 시도"""
    try:
        # Chrome 141+ 버전에 대한 ChromeDriver 버전 목록 (최신부터 순서대로)
        if int(chrome_major) >= 141:
            chrome_major_list = [140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130]
            print(f'Chrome {chrome_major} 버전 감지 - 여러 ChromeDriver 버전 시도')
        else:
            chrome_major_list = [chrome_major]
        
        for chrome_major_to_try in chrome_major_list:
            try:
                print(f'ChromeDriver {chrome_major_to_try} 시도 중...')
                
                # ChromeDriver 다운로드 URL
                chromedriver_url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{chrome_major_to_try}"
                
                # 최신 ChromeDriver 버전 가져오기
                response = requests.get(chromedriver_url, timeout=10)
                if response.status_code != 200:
                    print(f'ChromeDriver {chrome_major_to_try} 버전 확인 실패: {response.status_code}')
                    continue
                
                chromedriver_version = response.text.strip()
                print(f'ChromeDriver {chrome_major_to_try} 버전: {chromedriver_version}')
                
                # ChromeDriver 다운로드
                download_url = f"https://chromedriver.storage.googleapis.com/{chromedriver_version}/chromedriver_linux64.zip"
                print(f'ChromeDriver 다운로드 중: {download_url}')
                
                response = requests.get(download_url, timeout=30)
                if response.status_code != 200:
                    print(f'ChromeDriver {chrome_major_to_try} 다운로드 실패: {response.status_code}')
                    continue
                
                # 임시 파일로 저장
                temp_zip = '/tmp/chromedriver.zip'
                with open(temp_zip, 'wb') as f:
                    f.write(response.content)
                
                # 압축 해제
                with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                    zip_ref.extractall('/tmp/')
                
                # ChromeDriver 실행 파일 찾기
                chromedriver_path = '/tmp/chromedriver'
                if os.path.exists(chromedriver_path):
                    # 실행 권한 부여
                    os.chmod(chromedriver_path, 0o755)
                    print(f'ChromeDriver {chrome_major_to_try} 설치 완료: {chromedriver_path}')
                    return chromedriver_path
                else:
                    print(f'ChromeDriver {chrome_major_to_try} 실행 파일을 찾을 수 없습니다')
                    continue
                    
            except Exception as e:
                print(f'ChromeDriver {chrome_major_to_try} 시도 실패: {e}')
                continue
        
        print('사용 가능한 ChromeDriver 버전을 찾을 수 없습니다')
        return None
            
    except Exception as e:
        print(f'ChromeDriver 다운로드 실패: {e}')
        import traceback
        traceback.print_exc()
        return None

def test_chromedriver(driver_path):
    """ChromeDriver 테스트"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        
        # Chrome 옵션 설정
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # ChromeDriver 테스트
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.get('https://www.google.com')
        title = driver.title
        print(f'ChromeDriver 테스트 성공: {title}')
        
        driver.quit()
        print('ChromeDriver 설치 및 테스트 완료')
        return True
        
    except Exception as e:
        print(f'ChromeDriver 테스트 실패: {e}')
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 함수"""
    print('ChromeDriver 수동 설치 시작...')
    
    # Chrome 버전 확인
    chrome_version, chrome_major = get_chrome_version()
    if not chrome_version:
        print('Chrome 버전을 확인할 수 없습니다')
        sys.exit(1)
    
    # ChromeDriver 다운로드
    driver_path = download_chromedriver(chrome_major)
    if not driver_path:
        print('ChromeDriver 다운로드 실패')
        sys.exit(1)
    
    # ChromeDriver 테스트
    if test_chromedriver(driver_path):
        print('ChromeDriver 설치 및 테스트 성공')
        sys.exit(0)
    else:
        print('ChromeDriver 테스트 실패')
        sys.exit(1)

if __name__ == '__main__':
    main()
