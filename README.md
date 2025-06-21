# 스마트초이스 휴대폰 지원금 크롤러

스마트초이스 사이트에서 휴대폰 지원금 정보를 자동으로 수집하는 크롤러입니다.

## 주요 기능

- 🏭 **제조사별 수집**: 삼성전자, 애플, 기타 제조사
- 📅 **최신 모델 필터링**: 출시일 기준 2년 내 모델만 수집
- 💰 **지원금 정보**: SK, KT, LG 통신사별 기기변경/번호이동 지원금
- 📊 **데이터 정리**: JSON, CSV 형태로 저장
- 🤖 **자동화**: GitHub Actions로 매일 23시 자동 실행
- 📱 **Telegram 알림**: 크롤링 결과 및 오류 알림

## 설정 방법

### 1. 로컬 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 크롤러 실행
python main.py
```

### 2. GitHub Actions 설정

#### 2.1 Telegram Bot 설정

1. [@BotFather](https://t.me/botfather)에서 봇 생성
2. 봇 토큰 받기
3. 채팅방에 봇 초대 후 채팅 ID 확인

#### 2.2 GitHub Secrets 설정

Repository Settings → Secrets and variables → Actions에서 다음 설정:

- `TELEGRAM_BOT_TOKEN`: Telegram 봇 토큰
- `TELEGRAM_CHAT_ID`: 채팅방 ID

#### 2.3 자동 실행

- **스케줄**: 매일 한국시간 23시 자동 실행
- **수동 실행**: GitHub Actions 탭에서 "Run workflow" 버튼으로 수동 실행 가능

## 데이터 구조

### JSON 파일 구조
```json
{
  "collection_date": "2025-01-22 23:00:00",
  "total_models": 150,
  "model_info": [
    {
      "manufacturer": "삼성전자",
      "model_number": "SM-A366N",
      "model_name": "[5G] 갤럭시 A36 5G",
      "max_price": 499400
    }
  ],
  "carrier_monthly_fees": {
    "SK": [28000, 35000, 42000],
    "KT": [28000, 35000, 42000],
    "LG": [28000, 35000, 42000]
  },
  "manufacturers": {
    "삼성전자": {
      "name": "삼성전자",
      "models": [...]
    }
  }
}
```

### CSV 파일 구조
- 제조사, 모델명, 모델번호
- 통신사, 요금제, 월요금제
- 기기변경지원금, 번호이동지원금, 공시일

## 파일 구조

```
phone8ez-crawler/
├── main.py              # 메인 크롤러
├── utils.py             # 유틸리티 함수
├── config.py            # 설정 파일
├── requirements.txt     # 의존성 목록
├── .github/workflows/   # GitHub Actions
│   └── crawler.yml
├── data/                # 수집된 데이터
│   ├── *.json
│   └── *.csv
└── README.md
```

## 알림 메시지

### 성공 시
```
📱 스마트초이스 크롤링 완료

📊 수집 결과
• 총 모델 수: 150개
• 수집 시간: 2025-01-22 23:00:00

🏭 제조사별 수집 현황
• 삼성전자: 50개
• 애플: 30개
• 기타: 70개

📁 저장 파일
• JSON: data/phone_support_data_20250122_230000.json
• CSV: data/phone_support_data_20250122_230000.csv

✅ 크롤링이 성공적으로 완료되었습니다!
```

### 오류 시
```
❌ 스마트초이스 크롤링 오류

오류 내용: [오류 상세 내용]

시간: 2025-01-22 23:00:00
```

## 주의사항

- 크롤링은 사이트 구조 변경 시 오류가 발생할 수 있습니다
- 과도한 요청으로 인한 차단을 방지하기 위해 적절한 대기 시간을 설정했습니다
- 수집된 데이터는 개인적인 용도로만 사용해주세요

## 라이선스

이 프로젝트는 교육 및 개인 사용 목적으로 제작되었습니다. 