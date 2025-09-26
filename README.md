# jeonchasi
전기차 살 시점 전치시 : 전기차 보조금 조회 사이트

환경부 무공해차 보조금 데이터를 자동으로 크롤링하고 시각화하는 웹 애플리케이션입니다.

## 기능

### 1. 보조금 조회 페이지
- 차종, 지역, 제조사, 모델별 보조금 정보 조회
- 실시간 데이터 필터링 및 검색

### 2. 잔여대수 조회 페이지
- 환경부 무공해차 보조금 페이지에서 자동 크롤링
- 지역별, 차량구분별 잔여대수 현황
- 시각적 통계 및 진행률 표시

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. Chrome 드라이버 설치
- Chrome 브라우저가 설치되어 있어야 합니다
- ChromeDriver는 자동으로 다운로드됩니다

### 3. 웹 애플리케이션 실행
```bash
# 브라우저에서 index.html 파일을 열기
start index.html
```

### 4. 데이터 크롤링 실행
```bash
# 수동으로 크롤링 실행
python crawler.py

# 또는 배치 파일 실행
run_crawler.bat
```

## 자동화 설정

### Windows 작업 스케줄러 설정
1. PowerShell을 관리자 권한으로 실행
2. 다음 명령어 실행:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup_scheduler.ps1
```

### 수동 스케줄러 실행
```bash
# 백그라운드에서 스케줄러 실행
python scheduler.py
```

## 파일 구조

```
gonggongcar13/
├── index.html              # 메인 웹 애플리케이션
├── style.css               # 스타일시트
├── crawler.py              # 크롤링 스크립트
├── scheduler.py            # 스케줄러 스크립트
├── requirements.txt        # Python 의존성
├── run_crawler.bat         # Windows 배치 파일
├── setup_scheduler.ps1     # 작업 스케줄러 설정
├── data/
│   └── subsidy_remain.csv  # 크롤링된 데이터
└── README.md               # 이 파일
```

## 데이터 형식

### CSV 파일 구조 (subsidy_remain.csv)
```csv
지역,차량구분,총공고대수,접수가능대수,출고잔여대수,날짜
서울,일반,1322,854,728,2025-09-14
부산,일반,1057,718,465,2025-09-14
...
```

## 사용법

### 1. 보조금 조회
1. "보조금" 탭 클릭
2. 차종 선택 (승용, 화물, 승합)
3. 지역 선택
4. 제조사 선택
5. 모델 선택
6. 보조금 정보 확인

### 2. 잔여대수 조회
1. "잔여대수" 탭 클릭
2. 지역 선택 (드롭다운)
3. 차량구분 선택 (일반, 우선, 법인, 택시)
4. 잔여대수 현황 확인

## 문제 해결

### 크롤링 실패 시
- Chrome 브라우저가 설치되어 있는지 확인
- 인터넷 연결 상태 확인
- 방화벽 설정 확인

### 데이터가 표시되지 않을 때
- `data/subsidy_remain.csv` 파일이 존재하는지 확인
- 브라우저 개발자 도구에서 콘솔 오류 확인
- CORS 정책 확인 (로컬 파일 서버 사용 권장)

## 라이선스

이 프로젝트는 교육 및 개인 사용 목적으로 제작되었습니다.
