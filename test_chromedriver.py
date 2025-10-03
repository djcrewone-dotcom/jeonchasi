#!/usr/bin/env python3
"""
ChromeDriver 설치 및 테스트 스크립트
"""
import os
import sys

# webdriver-manager 환경 변수 설정
os.environ['WDM_LOG_LEVEL'] = '0'
os.environ['WDM_LOCAL'] = '1'
os.environ['WDM_SILENT'] = 'true'

try:
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    
    print('webdriver-manager로 ChromeDriver 설치 중...')
    driver_path = ChromeDriverManager().install()
    print(f'ChromeDriver 설치 완료: {driver_path}')
    
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
    
except Exception as e:
    print(f'ChromeDriver 설치 실패: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
