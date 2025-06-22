import os
from datetime import datetime

# 기본 설정
BASE_URL = "https://m.smartchoice.or.kr/smc/mobile/dantongList.do?type=m"
DATA_DIR = "data"

# 스마트초이스 크롤러 설정

# 웹사이트 URL
SMARTCHOICE_URL = "https://www.smartchoice.or.kr"

# 브라우저 설정
HEADLESS = True  # True로 설정하면 브라우저 창이 보이지 않음
BROWSER_WIDTH = 1920
BROWSER_HEIGHT = 1080

# 대기 시간 설정 (초)
PAGE_LOAD_WAIT = 10
ELEMENT_WAIT = 5

# 제조사 목록
MANUFACTURERS = ["삼성전자", "애플", "기타"]

# Telegram 설정 (GitHub Actions에서 환경변수로 설정)
TELEGRAM_BOT_TOKEN = None  # GitHub Secrets에서 설정
TELEGRAM_CHAT_ID = None    # GitHub Secrets에서 설정

# 데이터 저장 설정
RETENTION_DAYS = 30  # 30일 이전 데이터 삭제

# 셀렉터 설정 (실제 사이트 분석 후 업데이트 예정)
SELECTORS = {
    "manufacturer_dropdown": "",  # 제조사 드롭다운
    "phone_dropdown": "",        # 휴대폰 선택 드롭다운
    "search_button": "",         # 검색 버튼
    "result_table": "",          # 결과 테이블
    "phone_name": "",            # 단말기명
    "model_number": "",          # 모델번호
    "carrier_price": "",         # 통신사별 출고가
    "plan_name": "",             # 요금제명
    "monthly_fee": "",           # 월 요금제 금액
    "number_portability": "",    # 번호이동 지원금
    "device_change": "",         # 기기변경 지원금
    "announcement_date": ""      # 공시일
}

def get_today_str():
    """오늘 날짜를 YYYY-MM-DD 형식으로 반환"""
    return datetime.now().strftime("%Y-%m-%d")

def get_file_paths():
    """오늘 날짜의 파일 경로들을 반환"""
    today = get_today_str()
    return {
        "json": f"{DATA_DIR}/{today}_smartchoice_data.json",
        "csv": f"{DATA_DIR}/{today}_smartchoice_data.csv"
    } 