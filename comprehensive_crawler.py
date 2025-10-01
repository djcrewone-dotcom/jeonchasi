import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import re
from datetime import datetime
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

class ComprehensiveElectricVehicleCrawler:
    def __init__(self):
        self.driver = None
        self.all_data = []
        
    def setup_driver(self):
        """Chrome 드라이버 설정"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')
        
        try:
            # GitHub Actions 환경에서 ChromeDriver 경로 설정
            if os.environ.get('GITHUB_ACTIONS'):
                # GitHub Actions 환경에서는 시스템에 설치된 ChromeDriver 사용
                service = Service('/usr/local/bin/chromedriver')
            else:
                # 로컬 환경에서는 자동 다운로드
                service = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            return True
        except Exception as e:
            print(f"Chrome 드라이버 설정 실패: {e}")
            return False

    def click_button(self, button_text):
        """지정된 버튼 클릭"""
        print(f"{button_text} 버튼 클릭 시도...")
        
        # 여러 방법으로 버튼 찾기
        selectors = [
            f"//input[@value='{button_text}']",
            f"//button[contains(text(), '{button_text}')]",
            f"//a[contains(text(), '{button_text}')]",
            f"//span[contains(text(), '{button_text}')]",
            f"//div[contains(text(), '{button_text}')]",
            f"//*[contains(text(), '{button_text}')]"
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        self.driver.execute_script("arguments[0].click();", element)
                        print(f"{button_text} 버튼 클릭 성공: {selector}")
                        time.sleep(3)
                        return True
            except Exception as e:
                continue
        
        # JavaScript로 시도
        try:
            js_code = f"""
            var elements = document.querySelectorAll('*');
            for (var i = 0; i < elements.length; i++) {{
                var element = elements[i];
                if (element.textContent && element.textContent.includes('{button_text}')) {{
                    element.click();
                    return true;
                }}
            }}
            return false;
            """
            
            result = self.driver.execute_script(js_code)
            if result:
                print(f"JavaScript로 {button_text} 버튼 클릭 성공")
                time.sleep(3)
                return True
        except Exception as e:
            print(f"JavaScript 클릭 실패: {e}")
        
        return False

    def convert_region_name(self, region_name):
        """지역명 변환 규칙 적용"""
        if not region_name:
            return None
            
        # 잘못된 지역명 필터링 (더 엄격하게)
        invalid_regions = ["클릭", "초과", "차량구", "합계", "소계", "총계", "기타", "시도"]
        if region_name in invalid_regions:
            return None
            
        # 특별 규칙들
        if region_name == "한국환경공단":
            return "한국환경공단"
        
        # 의정부시, 남양주시, 동두천시는 첫 세글자
        if region_name in ["의정부시", "남양주시", "동두천시"]:
            return region_name[:3]
        
        # 화성 다음의 광주는 광주(경기)
        if region_name == "광주시" and hasattr(self, '_last_region') and self._last_region == "화성시":
            return "광주(경기)"
        
        # 창녕 다음의 고성은 고성(경남)
        if region_name == "고성군" and hasattr(self, '_last_region') and self._last_region == "창녕군":
            return "고성(경남)"
        
        # 일반적으로는 첫 두글자
        if len(region_name) >= 2:
            converted = region_name[:2]
            self._last_region = region_name  # 다음 지역명 변환을 위해 저장
            return converted
        
        return None

    def extract_data_from_page(self, vehicle_type):
        """페이지에서 데이터 추출"""
        print(f"{vehicle_type} 데이터 추출 시작...")
        
        try:
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 테이블 찾기
            tables = soup.find_all('table')
            if not tables:
                return []
            
            extracted_data = []
            current_region = None
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) < 5:
                        continue
                    
                    row_text = ' '.join([cell.get_text(strip=True) for cell in cells])
                    
                    # 지역명 추출 (더 정확한 패턴 - 특별자치도 포함)
                    region_match = re.search(r'([가-힣]+(?:시|도|구|군|특별시|광역시|특별자치시|특별자치도|환경공단))', row_text)
                    if region_match:
                        converted_region = self.convert_region_name(region_match.group(1))
                        if converted_region:  # None이 아닌 경우만 사용
                            current_region = converted_region
                    
                    # 각 차종별 데이터 추출
                    if vehicle_type == "승용":
                        data = self.extract_passenger_data(row_text, current_region)
                    elif vehicle_type == "화물":
                        data = self.extract_cargo_data(row_text, current_region)
                    elif vehicle_type == "승합":
                        # 승합 데이터에서 '초과' 관련 행만 제외하고 모든 행 처리
                        if "초과" in row_text:
                            continue
                        # 지역이 없어도 데이터 추출 시도 (extract_bus_data에서 지역 재추출)
                        data = self.extract_bus_data(row_text, current_region)
                    
                    if data:
                        extracted_data.extend(data)
            
            print(f"{vehicle_type} 데이터 {len(extracted_data)}개 추출 성공")
            return extracted_data
            
        except Exception as e:
            print(f"{vehicle_type} 데이터 추출 실패: {e}")
            return []

    def extract_passenger_data(self, row_text, region):
        """전기승용 데이터 추출"""
        if not region or '전기승용' not in row_text:
            return []
        
        # 괄호 안의 모든 숫자 추출
        all_numbers = re.findall(r'\((\d+)\)', row_text)
        
        if len(all_numbers) >= 16:  # 최소 16개 숫자 필요
            data = []
            
            # 실제 구조: 공고대수(우선,법인,택시,일반), 접수대수(우선,법인,택시,일반), 출고대수(우선,법인,택시,일반), 잔여대수(우선,법인,택시,일반)
            
            # 우선순위 데이터
            data.append({
                '구분': '승용',
                '지역': region,
                '유형': '우선',
                '공고대수': all_numbers[0] if len(all_numbers) > 0 else '0',
                '접수대수': all_numbers[4] if len(all_numbers) > 4 else '0',
                '출고대수': all_numbers[8] if len(all_numbers) > 8 else '0',
                '잔여대수': all_numbers[12] if len(all_numbers) > 12 else '0',
                '날짜': datetime.now().strftime('%Y-%m-%d')
            })
            
            # 법인 데이터
            data.append({
                '구분': '승용',
                '지역': region,
                '유형': '법인',
                '공고대수': all_numbers[1] if len(all_numbers) > 1 else '0',
                '접수대수': all_numbers[5] if len(all_numbers) > 5 else '0',
                '출고대수': all_numbers[9] if len(all_numbers) > 9 else '0',
                '잔여대수': all_numbers[13] if len(all_numbers) > 13 else '0',
                '날짜': datetime.now().strftime('%Y-%m-%d')
            })
            
            # 택시 데이터
            data.append({
                '구분': '승용',
                '지역': region,
                '유형': '택시',
                '공고대수': all_numbers[2] if len(all_numbers) > 2 else '0',
                '접수대수': all_numbers[6] if len(all_numbers) > 6 else '0',
                '출고대수': all_numbers[10] if len(all_numbers) > 10 else '0',
                '잔여대수': all_numbers[14] if len(all_numbers) > 14 else '0',
                '날짜': datetime.now().strftime('%Y-%m-%d')
            })
            
            # 일반 데이터
            data.append({
                '구분': '승용',
                '지역': region,
                '유형': '일반',
                '공고대수': all_numbers[3] if len(all_numbers) > 3 else '0',
                '접수대수': all_numbers[7] if len(all_numbers) > 7 else '0',
                '출고대수': all_numbers[11] if len(all_numbers) > 11 else '0',
                '잔여대수': all_numbers[15] if len(all_numbers) > 15 else '0',
                '날짜': datetime.now().strftime('%Y-%m-%d')
            })
        
        return data

    def extract_cargo_data(self, row_text, region):
        """전기화물 데이터 추출"""
        if not region or '전기화물' not in row_text:
            return []
        
        # 괄호 안의 모든 숫자 추출
        all_numbers = re.findall(r'\((\d+)\)', row_text)
        
        if len(all_numbers) >= 20:  # 최소 20개 숫자 필요
            data = []
            
            # 실제 구조: 공고대수(우선,중소,법인,택배,일반), 접수대수(우선,중소,법인,택배,일반), 출고대수(우선,중소,법인,택배,일반), 잔여대수(우선,중소,법인,택배,일반)
            
            # 우선순위 데이터
            data.append({
                '구분': '화물',
                '지역': region,
                '유형': '우선',
                '공고대수': all_numbers[0] if len(all_numbers) > 0 else '0',
                '접수대수': all_numbers[5] if len(all_numbers) > 5 else '0',
                '출고대수': all_numbers[10] if len(all_numbers) > 10 else '0',
                '잔여대수': all_numbers[15] if len(all_numbers) > 15 else '0',
                '날짜': datetime.now().strftime('%Y-%m-%d')
            })
            
            # 중소 데이터
            data.append({
                '구분': '화물',
                '지역': region,
                '유형': '중소',
                '공고대수': all_numbers[1] if len(all_numbers) > 1 else '0',
                '접수대수': all_numbers[6] if len(all_numbers) > 6 else '0',
                '출고대수': all_numbers[11] if len(all_numbers) > 11 else '0',
                '잔여대수': all_numbers[16] if len(all_numbers) > 16 else '0',
                '날짜': datetime.now().strftime('%Y-%m-%d')
            })
            
            # 법인 데이터
            data.append({
                '구분': '화물',
                '지역': region,
                '유형': '법인',
                '공고대수': all_numbers[2] if len(all_numbers) > 2 else '0',
                '접수대수': all_numbers[7] if len(all_numbers) > 7 else '0',
                '출고대수': all_numbers[12] if len(all_numbers) > 12 else '0',
                '잔여대수': all_numbers[17] if len(all_numbers) > 17 else '0',
                '날짜': datetime.now().strftime('%Y-%m-%d')
            })
            
            # 택배 데이터
            data.append({
                '구분': '화물',
                '지역': region,
                '유형': '택배',
                '공고대수': all_numbers[3] if len(all_numbers) > 3 else '0',
                '접수대수': all_numbers[8] if len(all_numbers) > 8 else '0',
                '출고대수': all_numbers[13] if len(all_numbers) > 13 else '0',
                '잔여대수': all_numbers[18] if len(all_numbers) > 18 else '0',
                '날짜': datetime.now().strftime('%Y-%m-%d')
            })
            
            # 일반 데이터
            data.append({
                '구분': '화물',
                '지역': region,
                '유형': '일반',
                '공고대수': all_numbers[4] if len(all_numbers) > 4 else '0',
                '접수대수': all_numbers[9] if len(all_numbers) > 9 else '0',
                '출고대수': all_numbers[14] if len(all_numbers) > 14 else '0',
                '잔여대수': all_numbers[19] if len(all_numbers) > 19 else '0',
                '날짜': datetime.now().strftime('%Y-%m-%d')
            })
        
        return data

    def extract_bus_data(self, row_text, region):
        """전기승합 데이터 추출 - 중복 방지하면서 누락된 지역들 포함"""
        # 지역이 없어도 데이터 추출 시도 (누락 방지)
        if not region:
            # 지역명을 다시 추출 시도 (특별자치도 포함, 더 정확한 패턴)
            region_match = re.search(r'([가-힣]+(?:시|도|구|군|특별시|광역시|특별자치시|특별자치도|환경공단))', row_text)
            if region_match:
                region = self.convert_region_name(region_match.group(1))
        
        # 지역이 여전히 없어도 데이터 추출 시도 (누락 방지)
        if not region:
            # 모든 가능한 지역명 패턴으로 재시도
            region_patterns = [
                r'([가-힣]+(?:시|도|구|군|특별시|광역시|특별자치시|특별자치도))',
                r'([가-힣]+(?:시|도|구|군))',
                r'([가-힣]+(?:시|도))',
                r'([가-힣]+)'
            ]
            
            for pattern in region_patterns:
                region_match = re.search(pattern, row_text)
                if region_match:
                    potential_region = region_match.group(1)
                    if len(potential_region) >= 2 and potential_region not in ["클릭", "초과", "차량구", "합계", "소계", "총계", "기타", "시도"]:
                        region = self.convert_region_name(potential_region)
                        if region:
                            break
        
        # 지역이 여전히 없으면 빈 문자열로 처리하지 않고 계속 진행
        # (미분류로 처리하면 데이터가 생성되지 않음)
        
        # 괄호 안의 모든 숫자 추출
        all_numbers = re.findall(r'\((\d+)\)', row_text)
        
        data = []
        
        # 제주특별자치도 특별 처리 (중복 방지)
        if ('제주' in row_text or '특별자치도' in row_text) and len(all_numbers) >= 4:
            # 제주 지역이면 무조건 데이터 생성
            region = '제주'  # 제주특별자치도 -> 제주로 변환
            
            # 전기버스 데이터 (우선, 일반)
            data.append({
                '구분': '승합',
                '지역': region,
                '유형': '전기버스 우선',
                '공고대수': all_numbers[0] if len(all_numbers) > 0 else '0',
                '접수대수': all_numbers[2] if len(all_numbers) > 2 else '0',
                '출고대수': all_numbers[4] if len(all_numbers) > 4 else '0',
                '잔여대수': all_numbers[6] if len(all_numbers) > 6 else '0',
                '날짜': datetime.now().strftime('%Y-%m-%d')
            })
            
            data.append({
                '구분': '승합',
                '지역': region,
                '유형': '전기버스 일반',
                '공고대수': all_numbers[1] if len(all_numbers) > 1 else '0',
                '접수대수': all_numbers[3] if len(all_numbers) > 3 else '0',
                '출고대수': all_numbers[5] if len(all_numbers) > 5 else '0',
                '잔여대수': all_numbers[7] if len(all_numbers) > 7 else '0',
                '날짜': datetime.now().strftime('%Y-%m-%d')
            })
            
            # 어린이버스 데이터 (우선, 일반)
            data.append({
                '구분': '승합',
                '지역': region,
                '유형': '어린이버스 우선',
                '공고대수': all_numbers[0] if len(all_numbers) > 0 else '0',
                '접수대수': all_numbers[2] if len(all_numbers) > 2 else '0',
                '출고대수': all_numbers[4] if len(all_numbers) > 4 else '0',
                '잔여대수': all_numbers[6] if len(all_numbers) > 6 else '0',
                '날짜': datetime.now().strftime('%Y-%m-%d')
            })
            
            data.append({
                '구분': '승합',
                '지역': region,
                '유형': '어린이버스 일반',
                '공고대수': all_numbers[1] if len(all_numbers) > 1 else '0',
                '접수대수': all_numbers[3] if len(all_numbers) > 3 else '0',
                '출고대수': all_numbers[5] if len(all_numbers) > 5 else '0',
                '잔여대수': all_numbers[7] if len(all_numbers) > 7 else '0',
                '날짜': datetime.now().strftime('%Y-%m-%d')
            })
            
            return data
        
        # 일반적인 전기버스 데이터 추출 (지역이 있고 중복 방지를 위해 엄격한 조건)
        if region and '전기버스' in row_text and len(all_numbers) >= 4:
            # 전기버스 우선
            data.append({
                '구분': '승합',
                '지역': region,
                '유형': '전기버스 우선',
                '공고대수': all_numbers[0] if len(all_numbers) > 0 else '0',
                '접수대수': all_numbers[2] if len(all_numbers) > 2 else '0',
                '출고대수': all_numbers[4] if len(all_numbers) > 4 else '0',
                '잔여대수': all_numbers[6] if len(all_numbers) > 6 else '0',
                '날짜': datetime.now().strftime('%Y-%m-%d')
            })
            
            # 전기버스 일반
            data.append({
                '구분': '승합',
                '지역': region,
                '유형': '전기버스 일반',
                '공고대수': all_numbers[1] if len(all_numbers) > 1 else '0',
                '접수대수': all_numbers[3] if len(all_numbers) > 3 else '0',
                '출고대수': all_numbers[5] if len(all_numbers) > 5 else '0',
                '잔여대수': all_numbers[7] if len(all_numbers) > 7 else '0',
                '날짜': datetime.now().strftime('%Y-%m-%d')
            })
        
        # 어린이버스 데이터 추출 (지역이 있고 중복 방지를 위해 엄격한 조건)
        if region and '어린이버스' in row_text and len(all_numbers) >= 4:
            # 어린이버스 우선
            data.append({
                '구분': '승합',
                '지역': region,
                '유형': '어린이버스 우선',
                '공고대수': all_numbers[0] if len(all_numbers) > 0 else '0',
                '접수대수': all_numbers[2] if len(all_numbers) > 2 else '0',
                '출고대수': all_numbers[4] if len(all_numbers) > 4 else '0',
                '잔여대수': all_numbers[6] if len(all_numbers) > 6 else '0',
                '날짜': datetime.now().strftime('%Y-%m-%d')
            })
            
            # 어린이버스 일반
            data.append({
                '구분': '승합',
                '지역': region,
                '유형': '어린이버스 일반',
                '공고대수': all_numbers[1] if len(all_numbers) > 1 else '0',
                '접수대수': all_numbers[3] if len(all_numbers) > 3 else '0',
                '출고대수': all_numbers[5] if len(all_numbers) > 5 else '0',
                '잔여대수': all_numbers[7] if len(all_numbers) > 7 else '0',
                '날짜': datetime.now().strftime('%Y-%m-%d')
            })
        
        return data

    def crawl_all_data(self):
        """모든 차종 데이터 크롤링"""
        if not self.setup_driver():
            return False
        
        try:
            url = "https://ev.or.kr/nportal/buySupprt/initSubsidyPaymentCheckAction.do"
            print(f"페이지 접속: {url}")
            self.driver.get(url)
            time.sleep(5)
            
            # 전기승용 데이터 크롤링
            print("\n=== 전기승용 데이터 크롤링 ===")
            if self.click_button("전기승용"):
                passenger_data = self.extract_data_from_page("승용")
                self.all_data.extend(passenger_data)
                print(f"전기승용 데이터 {len(passenger_data)}개 추출 완료")
            else:
                print("전기승용 버튼 클릭 실패")
            
            # 전기화물 데이터 크롤링
            print("\n=== 전기화물 데이터 크롤링 ===")
            if self.click_button("전기화물"):
                cargo_data = self.extract_data_from_page("화물")
                self.all_data.extend(cargo_data)
                print(f"전기화물 데이터 {len(cargo_data)}개 추출 완료")
            else:
                print("전기화물 버튼 클릭 실패")
            
            # 전기승합 데이터 크롤링
            print("\n=== 전기승합 데이터 크롤링 ===")
            if self.click_button("전기승합"):
                bus_data = self.extract_data_from_page("승합")
                self.all_data.extend(bus_data)
                print(f"전기승합 데이터 {len(bus_data)}개 추출 완료")
            else:
                print("전기승합 버튼 클릭 실패")
            
            print(f"\n총 {len(self.all_data)}개의 데이터 추출 완료")
            return True
                
        except Exception as e:
            print(f"크롤링 실패: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()

    def save_to_csv(self, filename=None):
        """데이터를 CSV 파일로 저장"""
        if not self.all_data:
            print("저장할 데이터가 없습니다.")
            return False
        
        try:
            # 파일명이 지정되지 않으면 현재 날짜로 생성
            if filename is None:
                current_date = datetime.now().strftime('%Y%m%d')
                filename = f"data/{current_date} remaining car.csv"
            
            # data 디렉토리 생성
            os.makedirs('data', exist_ok=True)
            
            # 기존 파일들 삭제 (최신 파일만 유지)
            self.cleanup_old_files()
            
            # 데이터를 요청된 형식으로 변환
            df = pd.DataFrame(self.all_data)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"데이터가 {filename} 파일로 저장되었습니다.")
            print(f"총 {len(self.all_data)}개의 레코드가 저장되었습니다.")
            
            # 데이터 요약 출력
            if self.all_data:
                regions = df['지역'].unique()
                print(f"추출된 지역: {', '.join(regions[:10])}{'...' if len(regions) > 10 else ''}")
                print(f"차종별 데이터 수: {df.groupby('구분').size().to_dict()}")
            
            return True
            
        except Exception as e:
            print(f"CSV 저장 실패: {e}")
            return False

    def cleanup_old_files(self):
        """이전 파일들을 정리하여 최신 파일만 유지"""
        try:
            data_dir = 'data'
            if not os.path.exists(data_dir):
                return
            
            # remaining car 관련 파일들 찾기
            remaining_files = [f for f in os.listdir(data_dir) if 'remaining car' in f and f.endswith('.csv')]
            
            if len(remaining_files) > 0:
                # 가장 최신 파일을 제외하고 삭제
                remaining_files.sort(reverse=True)  # 최신 파일이 앞에 오도록 정렬
                files_to_delete = remaining_files[1:]  # 첫 번째(최신) 파일을 제외한 나머지
                
                for file_to_delete in files_to_delete:
                    file_path = os.path.join(data_dir, file_to_delete)
                    try:
                        os.remove(file_path)
                        print(f"이전 파일 삭제: {file_path}")
                    except Exception as e:
                        print(f"파일 삭제 실패 {file_path}: {e}")
                        
        except Exception as e:
            print(f"파일 정리 중 오류: {e}")

def main():
    """메인 실행 함수"""
    print("전기차 전체 데이터 크롤링 시작...")
    print("승용 → 화물 → 승합 순으로 데이터를 추출합니다.")
    
    crawler = ComprehensiveElectricVehicleCrawler()
    success = crawler.crawl_all_data()
    
    if success:
        crawler.save_to_csv()
        print("크롤링 완료!")
    else:
        print("크롤링 실패!")

if __name__ == "__main__":
    main()


