import os
import json
import pandas as pd
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import config
import requests

def create_data_directory():
    """데이터 디렉토리 생성"""
    if not os.path.exists(config.DATA_DIR):
        os.makedirs(config.DATA_DIR)
        print(f"데이터 디렉토리 생성: {config.DATA_DIR}")

def save_data(data, file_paths):
    """데이터를 JSON과 CSV로 저장"""
    # JSON 저장
    with open(file_paths["json"], 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # CSV 저장
    if data:
        df = pd.DataFrame(data)
        df.to_csv(file_paths["csv"], index=False, encoding='utf-8-sig')
    
    print(f"데이터 저장 완료: {file_paths['json']}, {file_paths['csv']}")

def cleanup_old_files():
    """30일 이전 파일들 삭제"""
    cutoff_date = datetime.now() - timedelta(days=config.RETENTION_DAYS)
    
    if not os.path.exists(config.DATA_DIR):
        return
    
    for filename in os.listdir(config.DATA_DIR):
        file_path = os.path.join(config.DATA_DIR, filename)
        
        # 파일 생성 시간 확인
        file_time = datetime.fromtimestamp(os.path.getctime(file_path))
        
        if file_time < cutoff_date:
            os.remove(file_path)
            print(f"오래된 파일 삭제: {filename}")

def wait_for_element(driver, selector, timeout=10):
    """요소가 로드될 때까지 대기"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        return element
    except TimeoutException:
        print(f"요소를 찾을 수 없습니다: {selector}")
        return None

def safe_get_text(element, selector):
    """안전하게 텍스트 추출"""
    try:
        if element:
            target = element.find_element(By.CSS_SELECTOR, selector)
            return target.text.strip()
        return ""
    except NoSuchElementException:
        return ""

def safe_get_attribute(element, selector, attribute):
    """안전하게 속성값 추출"""
    try:
        if element:
            target = element.find_element(By.CSS_SELECTOR, selector)
            return target.get_attribute(attribute)
        return ""
    except NoSuchElementException:
        return ""

def send_telegram_message(message, bot_token=None, chat_id=None):
    """Telegram으로 메시지 전송"""
    if not bot_token or not chat_id:
        print("Telegram 설정이 없습니다. 메시지를 전송하지 않습니다.")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            print(f"Telegram 메시지 전송 성공: {message[:50]}...")
            return True
        else:
            print(f"Telegram 메시지 전송 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Telegram 메시지 전송 중 오류: {e}")
        return False

def log_message(message):
    """로그 메시지 출력"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def get_current_datetime():
    """현재 날짜와 시간을 문자열로 반환"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") 