# 📱 스마트초이스 단말기 지원금 크롤러

스마트초이스(https://m.smartchoice.or.kr)에서 휴대폰 단말기 지원금 정보를 자동으로 수집하는 크롤러입니다.

## 🚀 주요 기능

- **제조사별 단말기 지원금 조회**: 삼성전자, 애플, 기타 제조사 지원
- **모델별 상세 정보 추출**: 요금제, 월 요금, 기기변경/번호이동 지원금
- **다중 통신사 비교**: SKT, KT, LG U+ 지원금 비교
- **모델 정보 요약**: 모델번호:모델명:출고가(최대값) 형태로 요약
- **자동화된 데이터 수집**: 사용자 친화적인 인터페이스로 간편한 크롤링
- **다양한 형식 저장**: JSON, CSV 형식으로 데이터 저장

## 📋 시스템 요구사항

- Python 3.7 이상
- Chrome 브라우저
- ChromeDriver (자동 설치됨)

## 🛠️ 설치 방법

### 1. 저장소 클론
```bash
git clone https://github.com/your-username/phone8ez-crawler.git
cd phone8ez-crawler
```

### 2. 가상환경 생성 (권장)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. lxml 설치 (Windows 사용자)
Windows 환경에서는 lxml 설치 시 컴파일 오류가 발생할 수 있습니다:
```bash
pip install lxml
```
만약 설치가 실패하면, 미리 컴파일된 wheel 파일을 사용하세요:
```bash
pip install lxml --only-binary=all
```

## 🎯 사용 방법

### 기본 사용법
```bash
python smartchoice_runner.py
```

### 실행 과정
1. **제조사 선택**: 삼성전자, 애플, 기타 중 선택
2. **모델명 입력**: 갤럭시 S24, iPhone 15 등 정확한 모델명 입력
3. **브라우저 모드 선택**: 백그라운드 실행 또는 브라우저 창 표시
4. **자동 크롤링**: 설정에 따라 자동으로 데이터 수집
5. **결과 확인**: `data/` 폴더에 결과 파일 저장

### 예시 모델명
- **삼성전자**: 갤럭시 S24, 갤럭시 A55, 갤럭시 Z Fold6
- **애플**: iPhone 15, iPhone 15 Pro, iPhone 14
- **기타**: 기타 제조사 모델명

## 📁 출력 파일

크롤링 결과는 `data/YYYYMMDD_HHMMSS/` 폴더에 저장됩니다:

- `{모델명}_detailed.json`: 상세 크롤링 결과 (모든 정보 포함)
- `{모델명}_summary.json`: 요약 정보 (모델 정보 + 통계)
- `{모델명}_plans.csv`: 요금제 정보 (Excel에서 열기 가능)

### 데이터 구조

#### 상세 데이터 (JSON)
```json
{
  "model_info": {
    "model_code": "갤럭시 S24",
    "model_name": "갤럭시 S24",
    "max_price": "1,350,000원"
  },
  "carrier_plans": {
    "SKT": [
      {
        "plan_name": "5G 프리미엄 플랜",
        "monthly_fee": "110,000원",
        "device_change_support": "495,000원",
        "number_port_support": "330,000원"
      }
    ]
  }
}
```

#### 요금제 데이터 (CSV)
| carrier | model_name | manufacturer | plan_name | monthly_fee | device_change_support | number_port_support |
|---------|------------|--------------|-----------|-------------|---------------------|-------------------|
| SKT | 갤럭시 S24 | 삼성전자 | 5G 프리미엄 플랜 | 110,000원 | 495,000원 | 330,000원 |

## 🔧 고급 사용법

### 프로그래밍 방식 사용
```python
from smartchoice_crawler import SmartChoiceCrawler

# 크롤러 인스턴스 생성
with SmartChoiceCrawler(headless=True) as crawler:
    # 페이지 접속
    crawler.navigate_to_page()
    
    # 제조사 선택
    crawler.select_manufacturer("삼성전자")
    
    # 모델 선택
    crawler.select_model("갤럭시 S24")
    
    # 검색 실행
    crawler.search_support_info()
    
    # 데이터 추출
    result = crawler.crawl_model_with_summary("삼성전자", "갤럭시 S24")
    
    # 데이터 저장
    crawler.save_summary_data([result], "result.json")
```

### 배치 처리
여러 모델을 연속으로 크롤링하려면:
```python
models = ["갤럭시 S24", "갤럭시 A55", "iPhone 15"]
results = []

with SmartChoiceCrawler(headless=True) as crawler:
    crawler.navigate_to_page()
    
    for model in models:
        try:
            crawler.select_manufacturer("삼성전자")
            crawler.select_model(model)
            crawler.search_support_info()
            result = crawler.crawl_model_with_summary("삼성전자", model)
            if result:
                results.append(result)
            crawler.reset_search()
        except Exception as e:
            print(f"모델 {model} 크롤링 실패: {e}")
    
    # 모든 결과 저장
    crawler.save_summary_data(results, "batch_results.json")
```

## ⚠️ 주의사항

1. **모델명 정확성**: 정확한 모델명을 입력해야 합니다 (예: "갤럭시 S24" vs "S24")
2. **네트워크 안정성**: 안정적인 인터넷 연결이 필요합니다
3. **브라우저 업데이트**: Chrome 브라우저가 최신 버전이어야 합니다
4. **사용량 제한**: 과도한 크롤링은 서버에 부하를 줄 수 있으니 적절한 간격을 두세요
5. **법적 고려사항**: 웹사이트 이용약관을 준수하고 상업적 목적으로 사용하지 마세요

## 🐛 문제 해결

### 일반적인 오류

#### 1. ChromeDriver 오류
```
Message: unknown error: cannot find Chrome binary
```
**해결방법**: Chrome 브라우저가 설치되어 있는지 확인하고, 최신 버전으로 업데이트하세요.

#### 2. 모델을 찾을 수 없음
```
❌ 모델 '갤럭시 S24'을 찾을 수 없습니다.
```
**해결방법**: 
- 모델명을 정확히 입력했는지 확인
- 제조사를 올바르게 선택했는지 확인
- 해당 모델이 스마트초이스에 등록되어 있는지 확인

#### 3. 검색 결과 없음
```
❌ '갤럭시 S24'에 대한 지원금 정보가 없습니다.
```
**해결방법**: 해당 모델에 대한 지원금 정보가 아직 등록되지 않았을 수 있습니다.

#### 4. lxml 설치 오류 (Windows)
```
Microsoft Visual C++ 14.0 is required
```
**해결방법**: 
```bash
pip install lxml --only-binary=all
```

### 로그 확인
크롤링 중 발생하는 문제는 콘솔에 상세한 로그가 출력됩니다. 오류 발생 시 로그를 확인하여 문제를 파악하세요.

## 📈 성능 최적화

1. **헤드리스 모드 사용**: 백그라운드 실행으로 성능 향상
2. **적절한 대기 시간**: 네트워크 상태에 따라 대기 시간 조정
3. **배치 처리**: 여러 모델을 연속으로 처리할 때는 초기화 후 다음 모델 처리

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 지원

문제가 발생하거나 개선 사항이 있으면 이슈를 등록해주세요.

---

**버전**: 1.0.0  
**최종 업데이트**: 2025-06-21  
**작성자**: AI Assistant