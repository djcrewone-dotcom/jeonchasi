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

def download_chromedriver(chrome_version):
    """Chrome 버전에 맞는 ChromeDriver 다운로드 - Chrome for Testing API 사용"""
    try:
        print(f'Chrome for Testing API를 사용하여 ChromeDriver 다운로드 시도...')
        
        # Chrome for Testing API에서 사용 가능한 ChromeDriver 목록 가져오기
        api_url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
        
        print(f'Chrome for Testing API 호출: {api_url}')
        response = requests.get(api_url, timeout=30)
        if response.status_code != 200:
            print(f'Chrome for Testing API 호출 실패: {response.status_code}')
            return None
        
        data = response.json()
        versions = data.get('versions', [])
        
        # Chrome 버전과 호환되는 ChromeDriver 찾기
        chrome_major = chrome_version.split('.')[0]
        compatible_versions = []
        
        # 메이저 버전이 일치하는 ChromeDriver 찾기
        for version_info in versions:
            version = version_info.get('version', '')
            downloads = version_info.get('downloads', {})
            chromedriver_downloads = downloads.get('chromedriver', [])
            
            if version.startswith(chrome_major + '.') and chromedriver_downloads:
                # Linux 64비트 ChromeDriver 다운로드 링크 찾기
                for download in chromedriver_downloads:
                    if download.get('platform') == 'linux64':
                        compatible_versions.append({
                            'version': version,
                            'url': download.get('url')
                        })
                        break
        
        # 호환 버전을 버전 순으로 정렬 (최신부터)
        compatible_versions.sort(key=lambda x: [int(v) for v in x['version'].split('.')], reverse=True)
        
        if not compatible_versions:
            print(f'Chrome {chrome_major}과 호환되는 ChromeDriver를 찾을 수 없습니다')
            return None
        
        print(f'발견된 호환 ChromeDriver 버전: {len(compatible_versions)}개')
        
        # 첫 번째 호환 버전 시도
        for i, version_info in enumerate(compatible_versions[:3]):  # 최대 3개 버전 시도
            try:
                version = version_info['version']
                download_url = version_info['url']
                
                print(f'ChromeDriver {version} 시도 중... ({i+1}/3)')
                print(f'다운로드 URL: {download_url}')
                
                # ChromeDriver 다운로드
                response = requests.get(download_url, timeout=60)
                if response.status_code != 200:
                    print(f'ChromeDriver {version} 다운로드 실패: {response.status_code}')
                    continue
                
                # 임시 파일로 저장
                temp_zip = '/tmp/chromedriver.zip'
                with open(temp_zip, 'wb') as f:
                    f.write(response.content)
                
                # 압축 해제
                with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                    zip_ref.extractall('/tmp/')
                
                # ChromeDriver 실행 파일 찾기 (새로운 구조에서는 chromedriver-linux64/chromedriver)
                possible_paths = [
                    '/tmp/chromedriver',
                    '/tmp/chromedriver-linux64/chromedriver',
                    '/tmp/chromedriver_linux64/chromedriver'
                ]
                
                chromedriver_path = None
                for path in possible_paths:
                    if os.path.exists(path):
                        chromedriver_path = path
                        break
                
                if chromedriver_path:
                    # 실행 권한 부여
                    os.chmod(chromedriver_path, 0o755)
                    print(f'ChromeDriver {version} 설치 완료: {chromedriver_path}')
                    return chromedriver_path
                else:
                    print(f'ChromeDriver {version} 실행 파일을 찾을 수 없습니다')
                    print(f'시도한 경로: {possible_paths}')
                    continue
                    
            except Exception as e:
                print(f'ChromeDriver {version} 시도 실패: {e}')
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
    
    # ChromeDriver 다운로드 (전체 버전 전달)
    driver_path = download_chromedriver(chrome_version)
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
