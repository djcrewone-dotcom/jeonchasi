# 전기차 데이터 크롤러

환경부 무공해차 보조금 페이지에서 전기차 잔여대수 데이터를 자동으로 크롤링하는 프로젝트입니다.

## 🚀 주요 기능

- **자동 크롤링**: 매일 한국시간 오전 9시에 자동 실행
- **전체 차종 지원**: 승용, 화물, 승합 모든 전기차 데이터 수집
- **최신 파일 유지**: data 폴더에 최신 파일만 자동 저장
- **GitHub Actions**: 서버에서 자동 실행 및 Git 커밋

## 📁 프로젝트 구조

```
jeonchasi/
├── .github/
│   └── workflows/
│       └── daily-crawler.yml    # GitHub Actions 워크플로우
├── comprehensive_crawler.py     # 메인 크롤러
├── scheduler.py                # 로컬 스케줄러 (비활성화됨)
├── data/                       # 크롤링 데이터 저장 폴더
│   └── YYYYMMDD remaining car.csv
└── requirements.txt            # Python 의존성
```

## ⚙️ GitHub Actions 설정

### 1. 자동 스케줄 실행
- **실행 시간**: 매일 한국시간 오전 9시 (UTC 00:00)
- **실행 환경**: Ubuntu Latest
- **자동 커밋**: 크롤링 완료 후 자동으로 Git에 커밋 및 푸시

### 2. 수동 실행
GitHub 저장소의 Actions 탭에서 "Daily Electric Vehicle Data Crawler" 워크플로우를 수동으로 실행할 수 있습니다.

## 📊 데이터 형식

크롤링된 데이터는 다음과 같은 형식으로 저장됩니다:

```csv
구분,지역,유형,공고대수,접수대수,출고대수,잔여대수,날짜
승용,서울,우선,0,3381,3314,0,2025-10-01
승용,서울,법인,0,395,383,0,2025-10-01
승용,서울,택시,1200,1099,1031,169,2025-10-01
승용,서울,일반,9174,6125,5917,3257,2025-10-01
```

## 🛠️ 로컬 테스트

### 환경 설정
```bash
pip install -r requirements.txt
```

### 크롤러 실행
```bash
python comprehensive_crawler.py
```

### 스케줄러 실행 (로컬)
```bash
python scheduler.py
```

## 📋 의존성

- Python 3.9+
- Selenium
- BeautifulSoup4
- Pandas
- WebDriver Manager

## 🔧 설정 변경

### 크롤링 시간 변경
`.github/workflows/daily-crawler.yml` 파일의 cron 스케줄을 수정하세요:

```yaml
schedule:
  - cron: '0 0 * * *'  # UTC 00:00 (한국시간 오전 9시)
```

### 크롤링 대상 변경
`comprehensive_crawler.py` 파일에서 크롤링할 차종을 수정할 수 있습니다.

## 📈 모니터링

GitHub Actions 탭에서 크롤링 실행 상태와 로그를 확인할 수 있습니다.

## 🚨 주의사항

- 크롤링 대상 사이트의 정책 변경 시 코드 수정이 필요할 수 있습니다
- GitHub Actions는 월 2,000분의 무료 실행 시간이 제공됩니다
- 크롤링 실패 시 자동으로 재시도하지 않으므로 수동 확인이 필요합니다