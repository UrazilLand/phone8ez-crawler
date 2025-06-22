from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from datetime import datetime, timedelta
import time
import config
import utils
import json
import pandas as pd
from selenium.webdriver.common.keys import Keys
import os

# 브라우저 설정
BROWSER_OPTIONS = {
    "headless": False,  # 브라우저가 보이도록 False로 변경
    "no_sandbox": True,
    "disable_dev_shm_usage": True,
    "disable_gpu": True,
    "window_size": "1920,1080",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

class SmartChoiceCrawler:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Chrome WebDriver 설정"""
        utils.log_message("Chrome WebDriver 설정 중...")
        
        chrome_options = Options()
        
        # 브라우저 옵션 설정
        for option, value in BROWSER_OPTIONS.items():
            if option == "headless" and value:
                chrome_options.add_argument("--headless")
            elif option == "no_sandbox" and value:
                chrome_options.add_argument("--no-sandbox")
            elif option == "disable_dev_shm_usage" and value:
                chrome_options.add_argument("--disable-dev-shm-usage")
            elif option == "disable_gpu" and value:
                chrome_options.add_argument("--disable-gpu")
            elif option == "window_size":
                chrome_options.add_argument(f"--window-size={value}")
            elif option == "user_agent":
                chrome_options.add_argument(f"--user-agent={value}")
        
        # 추가 옵션
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--remote-debugging-port=9222")
        
        try:
            driver_path = ChromeDriverManager().install()
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            utils.log_message("Chrome WebDriver 설정 완료")
        except Exception as e:
            utils.log_message(f"WebDriver 설정 실패: {e}")
            utils.log_message("시스템 기본 Chrome WebDriver로 재시도...")
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                utils.log_message("시스템 Chrome WebDriver 설정 완료")
            except Exception as e2:
                utils.log_message(f"시스템 WebDriver도 실패: {e2}")
                raise
    
    def open_smartchoice_page(self):
        """스마트초이스 페이지 열기"""
        utils.log_message(f"스마트초이스 페이지 접속 중: {config.BASE_URL}")
        
        try:
            self.driver.get(config.BASE_URL)
            time.sleep(3)  # 페이지 로딩 대기
            
            # 페이지 제목 확인
            page_title = self.driver.title
            utils.log_message(f"페이지 제목: {page_title}")
            
            # 현재 URL 확인
            current_url = self.driver.current_url
            utils.log_message(f"현재 URL: {current_url}")
            
            return True
            
        except Exception as e:
            utils.log_message(f"페이지 접속 실패: {e}")
            return False
    
    def select_manufacturer(self, manufacturer):
        """제조사 선택"""
        try:
            utils.log_message(f"제조사 '{manufacturer}' 선택 중...")
            
            # 제조사 드롭다운 찾기
            manufacturer_select = self.driver.find_element(By.ID, "dan_Mau")
            
            # 드롭다운의 모든 옵션 확인
            select = Select(manufacturer_select)
            options = select.options
            utils.log_message(f"드롭다운 옵션들: {[opt.text for opt in options]}")
            
            # 현재 선택된 제조사 확인 (텍스트로)
            current_text = select.first_selected_option.text
            utils.log_message(f"현재 선택된 제조사: '{current_text}'")
            
            # 이미 선택된 제조사라면 변경하지 않음
            if current_text == manufacturer:
                utils.log_message(f"제조사 '{manufacturer}'가 이미 선택되어 있습니다.")
                return True
            
            # 제조사 변경 시 이전 모달 닫기
            try:
                # 정확한 모달 닫기 버튼 셀렉터 사용
                modal_close_btn = self.driver.find_element(By.CSS_SELECTOR, "#contentsarea > div.devicesupport > div.contentsbox > div.modalpop > div.popupwrap.selectProductPopup > button")
                if modal_close_btn.is_displayed():
                    modal_close_btn.click()
                    time.sleep(2)  # 모달이 완전히 닫힐 때까지 대기
                    
            except Exception as e:
                utils.log_message(f"모달 닫기 실패: {e}")
                # 백업 방법으로 ESC 키 시도
                try:
                    self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                    time.sleep(1)
                except:
                    pass
            
            # 제조사 선택
            select.select_by_visible_text(manufacturer)
            time.sleep(2)  # 선택 후 대기
            
            # 선택 확인
            new_text = select.first_selected_option.text
            utils.log_message(f"선택 후 제조사: '{new_text}'")
            
            if new_text == manufacturer:
                utils.log_message(f"제조사 '{manufacturer}' 선택 완료")
                return True
            else:
                utils.log_message(f"제조사 선택 실패: 예상 '{manufacturer}', 실제 '{new_text}'")
                return False
            
        except Exception as e:
            utils.log_message(f"제조사 선택 실패: {e}")
            return False
    
    def click_phone_select_button(self):
        """휴대폰 선택 버튼 클릭"""
        utils.log_message("휴대폰 선택 버튼 클릭 중...")
        
        try:
            phone_select_btn = self.driver.find_element(By.ID, "product_btn")
            phone_select_btn.click()
            utils.log_message("휴대폰 선택 버튼 클릭 완료")
            time.sleep(2)  # 모달 로딩 대기
            return True
        except Exception as e:
            utils.log_message(f"휴대폰 선택 버튼 클릭 실패: {e}")
            return False
    
    def extract_phone_list(self):
        """휴대폰 선택 모달에서 휴대폰 목록 추출 (출시일 2년 이내만)"""
        try:
            utils.log_message("휴대폰 목록 추출 시작 (출시일 2년 이내 필터링 적용)...")
            
            # 모달이 로드될 때까지 대기
            time.sleep(2)
            
            # 홀수 인덱스 div > label 요소에서 휴대폰 목록 추출
            phone_labels = self.driver.find_elements(By.CSS_SELECTOR, "div.modalpop div.popupwrap.selectProductPopup div:nth-child(odd) label")
            
            if not phone_labels:
                utils.log_message("모달에서 휴대폰 목록을 찾을 수 없습니다.")
                return []
            
            phones = []
            current_date = datetime.now()
            cutoff_date = current_date - timedelta(days=730)  # 2년 전 날짜
            
            utils.log_message(f"현재 날짜: {current_date.strftime('%Y-%m-%d')}")
            utils.log_message(f"필터링 기준 날짜 (2년 전): {cutoff_date.strftime('%Y-%m-%d')}")
            utils.log_message(f"포함 조건: 출시일 >= {cutoff_date.strftime('%Y-%m-%d')} (2년 이내)")
            
            total_phones = len(phone_labels)
            filtered_count = 0
            excluded_no_date_count = 0
            excluded_old_count = 0
            
            for i, label in enumerate(phone_labels):
                try:
                    phone_text = label.text.strip()
                    if not phone_text:
                        continue
                    
                    # 출시일 추출 (모델명 뒤의 날짜)
                    release_date = None
                    model_name = phone_text
                    
                    if "\n" in phone_text:
                        parts = phone_text.split("\n")
                        model_name = parts[0].strip()
                        
                        if len(parts) >= 2:
                            date_text = parts[1].strip()
                            try:
                                # "2025년 06월" 형식을 파싱
                                if "년" in date_text and "월" in date_text:
                                    year = int(date_text.split("년")[0])
                                    month = int(date_text.split("년")[1].split("월")[0])
                                    release_date = datetime(year, month, 1)
                                    utils.log_message(f"  모델: {model_name} | 출시일: {release_date.strftime('%Y-%m')}")
                            except Exception as date_error:
                                utils.log_message(f"  모델: {model_name} | 출시일 파싱 실패: {date_text} - {date_error}")
                    
                    # 출시일이 있는 모델만 처리
                    if release_date:
                        # 2년 이내 출시된 모델만 포함 (cutoff_date 이후 출시)
                        # release_date >= cutoff_date: 출시일이 2년 전 이후인 모델
                        if release_date >= cutoff_date:
                            phones.append({
                                "index": i,
                                "name": model_name,
                                "release_date": release_date.strftime("%Y-%m"),
                                "full_text": phone_text
                            })
                            filtered_count += 1
                            utils.log_message(f"  ✅ 포함 (2년 이내): {model_name} ({release_date.strftime('%Y-%m')})")
                        else:
                            excluded_old_count += 1
                            utils.log_message(f"  ❌ 제외 (2년 초과): {model_name} ({release_date.strftime('%Y-%m')})")
                    else:
                        # 출시일을 파싱할 수 없는 경우 제외
                        excluded_no_date_count += 1
                        utils.log_message(f"  ❌ 제외 (출시일 없음): {model_name}")
                        
                except Exception as e:
                    utils.log_message(f"휴대폰 {i} 정보 추출 실패: {e}")
                    continue
            
            utils.log_message(f"=== 필터링 결과 ===")
            utils.log_message(f"전체 휴대폰: {total_phones}개")
            utils.log_message(f"2년 이내 휴대폰: {filtered_count}개")
            utils.log_message(f"제외된 휴대폰 (2년 초과): {excluded_old_count}개")
            utils.log_message(f"제외된 휴대폰 (출시일 없음): {excluded_no_date_count}개")
            utils.log_message(f"총 제외된 휴대폰: {excluded_old_count + excluded_no_date_count}개")
            utils.log_message(f"2년 내 휴대폰 {len(phones)}개 추출 완료")
            
            return phones
            
        except Exception as e:
            utils.log_message(f"휴대폰 목록 추출 실패: {e}")
            return []
    
    def analyze_page_structure(self):
        """페이지 구조 분석 및 주요 셀렉터 정보 출력"""
        utils.log_message("페이지 구조 분석 중...")
        try:
            # 주요 테이블, 드롭다운, 버튼 등 주요 요소 탐색
            elements_info = []
            elements_to_find = [
                ("select", "드롭다운"),
                ("input", "입력 필드"),
                ("button", "버튼"),
                ("table", "테이블"),
                ("div", "DIV"),
                ("form", "폼")
            ]
            for tag, desc in elements_to_find:
                elements = self.driver.find_elements(By.TAG_NAME, tag)
                utils.log_message(f"[{desc}] {tag} 요소 개수: {len(elements)}")
                for i, element in enumerate(elements[:5]):
                    try:
                        element_id = element.get_attribute("id") or "-"
                        element_class = element.get_attribute("class") or "-"
                        element_name = element.get_attribute("name") or "-"
                        element_text = element.text.strip().replace("\n", " ")[:60] or "-"
                        selector = f"{tag}#{element_id}" if element_id != "-" else f"{tag}.{element_class}" if element_class != "-" else tag
                        utils.log_message(f"  {desc}[{i}]: selector={selector}, id={element_id}, class={element_class}, name={element_name}, text={element_text}")
                    except Exception as e:
                        utils.log_message(f"    요소 정보 추출 실패: {e}")
            # 주요 테이블의 첫 1~2줄 데이터 샘플 출력
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            for t_idx, table in enumerate(tables[:2]):
                try:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    utils.log_message(f"  [테이블 {t_idx}] 행 개수: {len(rows)}")
                    for r_idx, row in enumerate(rows[:2]):
                        cols = row.find_elements(By.TAG_NAME, "td")
                        col_texts = [col.text.strip() for col in cols]
                        utils.log_message(f"    [테이블 {t_idx}][행 {r_idx}] 데이터: {col_texts}")
                except Exception as e:
                    utils.log_message(f"    테이블 샘플 추출 실패: {e}")
            return True
        except Exception as e:
            utils.log_message(f"페이지 구조 분석 실패: {e}")
            return False
    
    def select_phone_by_index(self, index):
        """모달에서 인덱스로 휴대폰 모델 선택"""
        try:
            utils.log_message(f"모달에서 인덱스 {index}로 휴대폰 모델 선택 중...")
            
            # 모달이 로드될 때까지 대기
            time.sleep(2)
            
            # 모달 내 휴대폰 목록 찾기 (홀수 인덱스 div > label)
            phone_labels = self.driver.find_elements(By.CSS_SELECTOR, "div.modalpop div.popupwrap.selectProductPopup div:nth-child(odd) label")
            
            if not phone_labels:
                utils.log_message("모달에서 휴대폰 목록을 찾을 수 없습니다.")
                return False
            
            utils.log_message(f"모달에서 총 {len(phone_labels)}개의 휴대폰을 찾았습니다.")
            
            # 인덱스 범위 확인
            if index >= len(phone_labels):
                utils.log_message(f"인덱스 {index}가 범위를 벗어났습니다. (0~{len(phone_labels)-1})")
                return False
            
            # 해당 인덱스의 라벨 선택
            target_label = phone_labels[index]
            label_text = target_label.text.strip()
            utils.log_message(f"선택할 모델: [{index}] {label_text}")
            
            # 라벨 클릭
            target_label.click()
            time.sleep(2)
            
            utils.log_message(f"인덱스 {index} 모델 선택 완료: {label_text}")
            return True
            
        except Exception as e:
            utils.log_message(f"인덱스 {index} 모델 선택 실패: {e}")
            return False
    
    def analyze_detail_page(self):
        """상세 페이지 구조 분석"""
        try:
            utils.log_message("상세 페이지 구조 분석 중...")
            
            # 현재 URL 확인
            current_url = self.driver.current_url
            utils.log_message(f"현재 URL: {current_url}")
            
            # 페이지 제목 확인
            page_title = self.driver.title
            utils.log_message(f"페이지 제목: {page_title}")
            
            # 주요 요소들 찾기
            elements = {
                "테이블": self.driver.find_elements(By.TAG_NAME, "table"),
                "폼": self.driver.find_elements(By.TAG_NAME, "form"),
                "버튼": self.driver.find_elements(By.TAG_NAME, "button"),
                "입력필드": self.driver.find_elements(By.TAG_NAME, "input"),
                "드롭다운": self.driver.find_elements(By.TAG_NAME, "select"),
                "링크": self.driver.find_elements(By.TAG_NAME, "a")
            }
            
            # 요소 개수 출력
            for element_type, element_list in elements.items():
                utils.log_message(f"[{element_type}] {len(element_list)}개")
                
                # 처음 5개 요소의 정보 출력
                for i, element in enumerate(element_list[:5]):
                    try:
                        element_info = f"  {element_type}[{i}]: "
                        if element.get_attribute("id"):
                            element_info += f"id={element.get_attribute('id')}, "
                        if element.get_attribute("class"):
                            element_info += f"class={element.get_attribute('class')}, "
                        if element.get_attribute("name"):
                            element_info += f"name={element.get_attribute('name')}, "
                        if element.text.strip():
                            element_info += f"text={element.text.strip()[:50]}"
                        
                        utils.log_message(element_info)
                    except:
                        pass
            
            # 지원금 관련 정보 찾기
            utils.log_message("=== 지원금 관련 정보 검색 ===")
            
            # "지원금", "할인", "가격" 등의 키워드가 포함된 텍스트 찾기
            page_text = self.driver.page_source
            keywords = ["지원금", "할인", "가격", "원", "만원", "천원"]
            
            for keyword in keywords:
                if keyword in page_text:
                    utils.log_message(f"'{keyword}' 키워드 발견")
            
            # 테이블 데이터 확인
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            for i, table in enumerate(tables):
                try:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    utils.log_message(f"테이블 {i}: {len(rows)}행")
                    
                    for j, row in enumerate(rows[:3]):  # 처음 3행만 확인
                        cells = row.find_elements(By.TAG_NAME, "td")
                        cell_data = [cell.text.strip() for cell in cells if cell.text.strip()]
                        if cell_data:
                            utils.log_message(f"  행 {j}: {cell_data}")
                except:
                    pass
            
            utils.log_message("상세 페이지 분석 완료")
            
        except Exception as e:
            utils.log_message(f"상세 페이지 분석 중 오류: {e}")
    
    def close_driver(self):
        """브라우저 종료"""
        if self.driver:
            self.driver.quit()
            utils.log_message("브라우저 종료")

    def click_search_button(self):
        """검색 버튼 클릭"""
        try:
            utils.log_message("검색 버튼 클릭 중...")
            
            # 검색 버튼 찾기
            search_btn = self.driver.find_element(By.CSS_SELECTOR, "#dantongForm > fieldset > div > a.h_btn.fill.size_l")
            
            # 버튼 클릭
            search_btn.click()
            time.sleep(3)  # 검색 결과 로드 대기
            
            utils.log_message("검색 버튼 클릭 완료")
            return True
            
        except Exception as e:
            utils.log_message(f"검색 버튼 클릭 실패: {e}")
            return False

    def click_select_phone_button(self):
        """모달에서 선택하기 버튼 클릭"""
        try:
            utils.log_message("모달에서 선택하기 버튼 클릭 중...")
            
            # 선택하기 버튼 찾기
            select_btn = self.driver.find_element(By.ID, "selectPhone")
            
            # 버튼 클릭
            select_btn.click()
            time.sleep(2)  # 모달이 닫힐 때까지 대기
            
            utils.log_message("선택하기 버튼 클릭 완료")
            return True
            
        except Exception as e:
            utils.log_message(f"선택하기 버튼 클릭 실패: {e}")
            return False

    def extract_model_info(self, index):
        """특정 인덱스의 모델 정보 추출"""
        try:
            # 모달에서 해당 인덱스의 모델 정보 추출
            model_name = ""
            model_number = ""
            
            try:
                # 홀수 인덱스 div > label 요소에서 해당 인덱스 모델 찾기
                phone_labels = self.driver.find_elements(By.CSS_SELECTOR, "div.modalpop div.popupwrap.selectProductPopup div:nth-child(odd) label")
                
                if index < len(phone_labels):
                    selected_label = phone_labels[index]
                    full_text = selected_label.text.strip()
                    model_number = selected_label.get_attribute("for")
                    
                    # 모델명에서 출고일 부분 제거 (\n 뒤의 텍스트)
                    if "\n" in full_text:
                        model_name = full_text.split("\n")[0].strip()
                    else:
                        model_name = full_text
                    
                    utils.log_message(f"모델 정보 추출: {model_name} ({model_number})")
                else:
                    utils.log_message(f"인덱스 {index}가 범위를 벗어났습니다.")
                    return None
                    
            except Exception as e:
                utils.log_message(f"모델 정보 추출 중 오류: {e}")
                return None
            
            return {
                "model_name": model_name,
                "model_number": model_number
            }
            
        except Exception as e:
            utils.log_message(f"모델 정보 추출 실패: {e}")
            return None

    def extract_support_info(self):
        """검색 결과 페이지에서 통신사별 지원금 정보 추출"""
        try:
            utils.log_message("검색 결과 페이지에서 지원금 정보 추출 시작...")
            
            # 페이지 로드 대기
            time.sleep(3)
            
            support_data = {
                "carriers": {},  # 통신사별 데이터
                "sections": []   # 섹션별 데이터
            }
            
            # 1. 통신사명 추출 (SK, KT, LG)
            carriers = []
            for i in range(2, 5):  # 2, 3, 4 (SK, KT, LG)
                try:
                    carrier_selector = f"#contentsarea > div.devicesupport > div.contentsbox > div.tab_contents > div.dantong_result_top > div > div > table > thead > tr:nth-child(1) > td:nth-child({i})"
                    carrier_element = self.driver.find_element(By.CSS_SELECTOR, carrier_selector)
                    carrier_name = carrier_element.text.strip()
                    
                    # 통신사명 변경
                    if carrier_name == "SKT":
                        carrier_name = "SK"
                    elif carrier_name == "LGU+":
                        carrier_name = "LG"
                    
                    carriers.append(carrier_name)
                    utils.log_message(f"통신사 {i-1}: {carrier_name}")
                except Exception as e:
                    carriers.append(f"통신사{i-1}")
                    utils.log_message(f"통신사 {i-1} 추출 실패: {e}")
            
            # 2. 출고가 추출
            prices = []
            for i in range(1, 4):  # 1, 2, 3 (출고가)
                try:
                    price_selector = f"#contentsarea > div.devicesupport > div.contentsbox > div.tab_contents > div.dantong_result_top > div > div > table > thead > tr:nth-child(2) > td:nth-child({i})"
                    price_element = self.driver.find_element(By.CSS_SELECTOR, price_selector)
                    price = price_element.text.strip()
                    prices.append(price)
                    utils.log_message(f"출고가 {i}: {price}")
                except Exception as e:
                    prices.append("")
                    utils.log_message(f"출고가 {i} 추출 실패: {e}")
            
            # 3. 섹션별 요금제 정보 추출 (A01, B01, C01... 최대 10개)
            section_names = ["A01", "B01", "C01", "D01", "E01", "F01", "G01", "H01", "I01", "J01"]
            
            for section_idx, section_name in enumerate(section_names):
                try:
                    # 섹션이 존재하는지 확인
                    section_selector = f"#{section_name}"
                    section_element = self.driver.find_element(By.CSS_SELECTOR, section_selector)
                    
                    if not section_element.is_displayed():
                        continue
                    
                    utils.log_message(f"=== 섹션 {section_name} 분석 중 ===")
                    
                    section_data = {
                        "section": section_name,
                        "carriers": {}
                    }
                    
                    # 각 통신사별 데이터 추출
                    for carrier_idx, carrier_name in enumerate(carriers):
                        carrier_data = {
                            "carrier_name": carrier_name,
                            "price": prices[carrier_idx] if carrier_idx < len(prices) else "",
                            "plan_name": "",
                            "device_support": "",
                            "number_port_support": "",
                            "announcement_date": "",
                            "monthly_fee": ""
                        }
                        
                        # 요금제명 추출
                        try:
                            plan_selector = f"#{section_name} > div > table > tbody > tr.choice > td:nth-child({carrier_idx + 2}) > span.name"
                            plan_element = self.driver.find_element(By.CSS_SELECTOR, plan_selector)
                            carrier_data["plan_name"] = plan_element.text.strip()
                        except:
                            pass
                        
                        # 월 요금제 금액 추출
                        try:
                            price_selector = f"#{section_name} > div > table > tbody > tr.choice > td:nth-child({carrier_idx + 2}) > span.price"
                            price_element = self.driver.find_element(By.CSS_SELECTOR, price_selector)
                            price_text = price_element.text.strip()
                            # 쉼표, '원', '월' 제거 후 숫자로 변환
                            if price_text and price_text != "":
                                price_text = price_text.replace(",", "").replace("원", "").replace("월", "").strip()
                                try:
                                    carrier_data["monthly_fee"] = int(price_text)
                                except:
                                    carrier_data["monthly_fee"] = price_text
                        except:
                            pass
                        
                        # 기기변경 지원금 추출
                        try:
                            device_selector = f"#{section_name} > div > table > tbody > tr.grey_bg.fs9 > td:nth-child({carrier_idx + 3}) > a > span > em"
                            device_element = self.driver.find_element(By.CSS_SELECTOR, device_selector)
                            device_text = device_element.text.strip()
                            # 쉼표와 '원' 제거 후 숫자로 변환
                            if device_text and device_text != "":
                                device_text = device_text.replace(",", "").replace("원", "").strip()
                                try:
                                    carrier_data["device_support"] = int(device_text)
                                except:
                                    carrier_data["device_support"] = device_text
                        except:
                            pass
                        
                        # 번호이동 지원금 추출
                        try:
                            number_selector = f"#{section_name} > div > table > tbody > tr:nth-child(5) > td:nth-child({carrier_idx + 2}) > a > span > em"
                            number_element = self.driver.find_element(By.CSS_SELECTOR, number_selector)
                            number_text = number_element.text.strip()
                            # 쉼표와 '원' 제거 후 숫자로 변환
                            if number_text and number_text != "":
                                number_text = number_text.replace(",", "").replace("원", "").strip()
                                try:
                                    carrier_data["number_port_support"] = int(number_text)
                                except:
                                    carrier_data["number_port_support"] = number_text
                        except:
                            pass
                        
                        # 공시일 추출
                        try:
                            date_selector = f"#{section_name} > div > table > tbody > tr:nth-child(6) > td:nth-child({carrier_idx + 2}) > a"
                            date_element = self.driver.find_element(By.CSS_SELECTOR, date_selector)
                            carrier_data["announcement_date"] = date_element.text.strip()
                        except:
                            pass
                        
                        section_data["carriers"][carrier_name] = carrier_data
                        
                        # 로그 출력
                        utils.log_message(f"  {carrier_name}: {carrier_data['plan_name']} | 기기변경: {carrier_data['device_support']} | 번호이동: {carrier_data['number_port_support']} | 공시일: {carrier_data['announcement_date']}")
                    
                    support_data["sections"].append(section_data)
                    
                except Exception as e:
                    utils.log_message(f"섹션 {section_name} 처리 중 오류: {e}")
                    break  # 더 이상 섹션이 없으면 중단
            
            utils.log_message(f"지원금 정보 추출 완료: {len(support_data['sections'])}개 섹션")
            return support_data
            
        except Exception as e:
            utils.log_message(f"지원금 정보 추출 중 오류: {e}")
            return None

def main():
    """메인 실행 함수"""
    utils.log_message("스마트초이스 크롤링 시작")
    
    # 데이터 디렉토리 생성
    utils.create_data_directory()
    
    # 오래된 파일 정리
    utils.cleanup_old_files()
    
    crawler = None
    file_created = False  # 파일 생성 여부 추적
    
    try:
        # 크롤러 초기화
        crawler = SmartChoiceCrawler()
        
        # 1단계: 페이지 접속
        if not crawler.open_smartchoice_page():
            utils.log_message("페이지 접속 실패. 프로그램을 종료합니다.")
            return
        
        # 2단계: 페이지 구조 분석
        if not crawler.analyze_page_structure():
            utils.log_message("페이지 구조 분석 실패.")
            return
        
        utils.log_message("1단계 완료: 브라우저 오픈 및 페이지 접속 성공")
        
        # 제조사 리스트 순회하며 자동 진행
        manufacturers = ["삼성전자", "애플", "기타"]
        all_phone_data = {}
        for manufacturer in manufacturers:
            utils.log_message(f"=== {manufacturer} 제조사 수집 시작 ===")
            
            # 제조사 선택
            if not crawler.select_manufacturer(manufacturer):
                utils.log_message(f"{manufacturer} 제조사 선택 실패. 다음 제조사로 진행합니다.")
                continue
            
            # 휴대폰 선택 버튼 클릭
            if not crawler.click_phone_select_button():
                utils.log_message(f"{manufacturer} 휴대폰 선택 버튼 클릭 실패. 다음 제조사로 진행합니다.")
                continue
            
            # 휴대폰 목록 추출
            phones = crawler.extract_phone_list()
            all_phone_data[manufacturer] = phones
            
            utils.log_message(f"{manufacturer} 제조사 수집 완료: {len(phones)}개 휴대폰")
            
            # 제조사별 추출된 목록 출력
            utils.log_message(f"=== {manufacturer} 추출된 휴대폰 목록 ===")
            for i, phone in enumerate(phones, 1):
                utils.log_message(f"{i}. {phone['name']} - {phone['release_date']}")
            utils.log_message(f"=== {manufacturer} 제조사 수집 완료 ===")
            
            # 제조사 수집 완료 후 모달 닫기
            try:
                # 정확한 모달 닫기 버튼 셀렉터 사용
                modal_close_btn = crawler.driver.find_element(By.CSS_SELECTOR, "#contentsarea > div.devicesupport > div.contentsbox > div.modalpop > div.popupwrap.selectProductPopup > button")
                if modal_close_btn.is_displayed():
                    modal_close_btn.click()
                    time.sleep(2)  # 모달이 완전히 닫힐 때까지 대기
                    utils.log_message(f"{manufacturer} 제조사 수집 후 모달 닫기 완료")
                    
            except Exception as e:
                utils.log_message(f"{manufacturer} 제조사 수집 후 모달 닫기 실패: {e}")
                # 백업 방법으로 ESC 키 시도
                try:
                    crawler.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                    time.sleep(1)
                    utils.log_message(f"{manufacturer} 제조사 수집 후 ESC 키로 모달 닫기 완료")
                except:
                    utils.log_message(f"{manufacturer} 제조사 수집 후 모달 닫기 모든 방법 실패")
        # 전체 결과 요약
        total_phones = sum(len(phones) for phones in all_phone_data.values())
        utils.log_message(f"=== 전체 수집 결과 ===")
        utils.log_message(f"총 수집된 휴대폰: {total_phones}개")
        for manufacturer, phones in all_phone_data.items():
            utils.log_message(f"{manufacturer}: {len(phones)}개")
        
        # 5단계: 전체 모델 지원금 정보 수집 및 저장
        utils.log_message("=== 정식 버전: 전체 모델 지원금 정보 수집 및 저장 ===")
        
        # 수집할 데이터를 저장할 딕셔너리
        collected_data = {
            "collection_date": utils.get_current_datetime(),
            "total_models": 0,
            "manufacturers": {}
        }
        
        # 각 제조사별로 필터링된 모델만 선택
        for manufacturer in manufacturers:
            utils.log_message(f"=== {manufacturer} 제조사 필터링된 모델 수집 시작 (정식 버전) ===")
            
            # 해당 제조사의 필터링된 모델 목록 가져오기
            filtered_phones = all_phone_data.get(manufacturer, [])
            if not filtered_phones:
                utils.log_message(f"{manufacturer} 제조사의 필터링된 모델이 없습니다. 다음 제조사로 진행합니다.")
                continue
            
            utils.log_message(f"{manufacturer} 제조사 필터링된 모델 {len(filtered_phones)}개 수집 시작")
            
            manufacturer_data = {
                "name": manufacturer,
                "models": []
            }
            
            # 해당 제조사 선택
            if not crawler.select_manufacturer(manufacturer):
                utils.log_message(f"{manufacturer} 제조사 선택 실패. 다음 제조사로 진행합니다.")
                continue
            
            # 휴대폰 선택 버튼 클릭
            if not crawler.click_phone_select_button():
                utils.log_message(f"{manufacturer} 휴대폰 선택 버튼 클릭 실패. 다음 제조사로 진행합니다.")
                continue
            
            # 필터링된 모델들의 인덱스만 사용하여 크롤링
            for phone_info in filtered_phones:
                index = phone_info["index"]
                model_name = phone_info["name"]
                release_date = phone_info["release_date"]
                
                utils.log_message(f"=== {manufacturer} - 인덱스 {index} 모델 수집 ({model_name}, {release_date}) ===")
                
                # 모델 선택
                if not crawler.select_phone_by_index(index):
                    utils.log_message(f"{manufacturer} 인덱스 {index} 모델 선택 실패. 다음 모델로 진행합니다.")
                    continue
                
                # 모델 정보 추출 (모델 선택 직후, 선택하기 버튼 누르기 전)
                model_info = crawler.extract_model_info(index)
                
                # 선택하기 버튼 클릭
                if not crawler.click_select_phone_button():
                    utils.log_message(f"{manufacturer} 인덱스 {index} 선택하기 버튼 클릭 실패. 다음 모델로 진행합니다.")
                    continue
                
                # 검색 버튼 클릭
                if not crawler.click_search_button():
                    utils.log_message(f"{manufacturer} 인덱스 {index} 검색 버튼 클릭 실패. 다음 모델로 진행합니다.")
                    continue
                
                # 지원금 정보 추출
                support_info = crawler.extract_support_info()
                if support_info:
                    # 모델 정보 구성
                    model_data = {
                        "index": index,
                        "model_name": model_info["model_name"] if model_info else model_name,
                        "model_number": model_info["model_number"] if model_info else f"INDEX_{index}",
                        "release_date": release_date,
                        "support_info": support_info
                    }
                    manufacturer_data["models"].append(model_data)
                    collected_data["total_models"] += 1
                    
                    utils.log_message(f"{manufacturer} 인덱스 {index} 모델 지원금 정보 수집 완료")
                else:
                    utils.log_message(f"{manufacturer} 인덱스 {index} 모델 지원금 정보 추출 실패")

                # 다음 모델을 위해 스크롤을 맨 위로 올리고 휴대폰 선택 버튼을 다시 누름
                crawler.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
                
                if not crawler.click_phone_select_button():
                    utils.log_message(f"{manufacturer} 휴대폰 선택 버튼 재클릭 실패. 다음 제조사로 진행합니다.")
                    break
            
            collected_data["manufacturers"][manufacturer] = manufacturer_data
            utils.log_message(f"{manufacturer} 제조사 수집 완료: {len(manufacturer_data['models'])}개 모델")
        
        # 데이터 구조 개선: 통신사별 요금제 중복 제거 및 모델 정보 상단 추가
        utils.log_message("=== 데이터 구조 개선 및 정리 ===")
        
        # 모든 통신사별 월 요금제 금액 수집
        all_monthly_fees = {"SK": set(), "KT": set(), "LG": set()}
        all_prices = []
        all_model_info = []  # 모델 정보를 저장할 리스트
        
        for manufacturer, manufacturer_data in collected_data["manufacturers"].items():
            for model in manufacturer_data["models"]:
                # 모델 정보 수집 (모델번호, 모델명, 출고가)
                model_info = {
                    "manufacturer": manufacturer,
                    "model_number": model["model_number"],
                    "model_name": model["model_name"],
                    "max_price": 0
                }
                
                support_info = model["support_info"]
                if support_info and "sections" in support_info:
                    for section in support_info["sections"]:
                        for carrier_name, carrier_data in section["carriers"].items():
                            # 월 요금제 금액 수집
                            if carrier_data.get("monthly_fee") and carrier_data["monthly_fee"] != "":
                                if isinstance(carrier_data["monthly_fee"], int):
                                    all_monthly_fees[carrier_name].add(carrier_data["monthly_fee"])
                                
                            # 출고가 수집 (숫자로 변환)
                            if carrier_data["price"] and carrier_data["price"] != "해당사항 없음":
                                try:
                                    price_text = carrier_data["price"].replace(",", "").replace("원", "").strip()
                                    price_num = int(price_text)
                                    all_prices.append(price_num)
                                    # 해당 모델의 최대 출고가 업데이트
                                    if price_num > model_info["max_price"]:
                                        model_info["max_price"] = price_num
                                except:
                                    pass
                
                all_model_info.append(model_info)
        
        # 개선된 데이터 구조 생성
        improved_data = {
            "collection_date": collected_data["collection_date"],
            "total_models": collected_data["total_models"],
            "model_info": all_model_info,  # 모든 모델 정보 (모델번호, 모델명, 출고가)
            "carrier_monthly_fees": {
                carrier: sorted(list(fees)) for carrier, fees in all_monthly_fees.items()
            },
            "manufacturers": collected_data["manufacturers"]
        }
        
        # 데이터가 있는지 확인
        if improved_data["total_models"] == 0:
            utils.log_message("수집된 모델이 없습니다. 파일을 저장하지 않습니다.")
            return
        
        # 파일 저장 (성공 시에만)
        file_created = False  # 파일 생성 여부 초기화
        try:
            # JSON 파일 저장
            utils.log_message("=== 수집된 데이터 JSON 파일 저장 ===")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_filename = f"data/phone_support_data_{timestamp}.json"
            
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(improved_data, f, ensure_ascii=False, indent=2)
            
            utils.log_message(f"데이터 저장 완료: {json_filename}")
            
            # CSV 파일 생성
            utils.log_message("=== CSV 파일 생성 ===")
            csv_filename = f"data/phone_support_data_{timestamp}.csv"
            
            csv_data = []
            for manufacturer, manufacturer_data in improved_data["manufacturers"].items():
                for model in manufacturer_data["models"]:
                    support_info = model["support_info"]
                    if support_info and "sections" in support_info:
                        for section in support_info["sections"]:
                            for carrier_name, carrier_data in section["carriers"].items():
                                row = {
                                    "제조사": manufacturer,
                                    "모델명": model["model_name"],
                                    "모델번호": model["model_number"],
                                    "통신사": carrier_name,
                                    "요금제": carrier_data["plan_name"],
                                    "월요금제": carrier_data.get("monthly_fee", ""),
                                    "기기변경지원금": carrier_data["device_support"],
                                    "번호이동지원금": carrier_data["number_port_support"],
                                    "공시일": carrier_data["announcement_date"],
                                    "섹션": section["section"]
                                }
                                csv_data.append(row)
            
            if csv_data:
                import pandas as pd
                df = pd.DataFrame(csv_data)
                df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
                utils.log_message(f"CSV 파일 저장 완료: {csv_filename}")
                file_created = True  # 파일 생성 성공 표시
            else:
                utils.log_message("CSV 데이터가 없습니다. CSV 파일을 저장하지 않습니다.")
                # JSON 파일도 삭제
                if os.path.exists(json_filename):
                    os.remove(json_filename)
                    utils.log_message(f"빈 JSON 파일 삭제: {json_filename}")
                file_created = False
                return
        except Exception as file_error:
            utils.log_message(f"파일 저장 중 오류 발생: {file_error}")
            file_created = False
        
        utils.log_message(f"총 수집된 모델 수: {improved_data['total_models']}개")
        utils.log_message("=== 수집 결과 요약 ===")
        for manufacturer, manufacturer_data in improved_data["manufacturers"].items():
            utils.log_message(f"{manufacturer}: {len(manufacturer_data['models'])}개 모델")
        
        # Telegram 알림 전송 (파일 생성 성공 시에만)
        if file_created:
            try:
                # 환경변수에서 Telegram 설정 가져오기
                telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN') or config.TELEGRAM_BOT_TOKEN
                telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID') or config.TELEGRAM_CHAT_ID
                
                # 각 제조사별 지원금 정보 항목 수 계산
                manufacturer_details = {}
                total_support_items = 0
                
                for manufacturer, manufacturer_data in improved_data["manufacturers"].items():
                    support_items = 0
                    for model in manufacturer_data["models"]:
                        support_info = model["support_info"]
                        if support_info and "sections" in support_info:
                            for section in support_info["sections"]:
                                for carrier_name, carrier_data in section["carriers"].items():
                                    if carrier_data.get("device_support") or carrier_data.get("number_port_support"):
                                        support_items += 1
                
                    manufacturer_details[manufacturer] = {
                        "models": len(manufacturer_data["models"]),
                        "support_items": support_items
                    }
                    total_support_items += support_items
                
                # 결과 요약 메시지 생성
                summary_message = f"""📱 <b>스마트초이스 크롤링 완료</b>

📊 <b>수집 결과</b>
• 총 모델 수: {improved_data['total_models']}개
• 총 지원금 정보: {total_support_items}개 항목
• 수집 시간: {improved_data['collection_date']}

🏭 <b>제조사별 수집 현황</b>"""
                
                for manufacturer, details in manufacturer_details.items():
                    summary_message += f"\n• {manufacturer}: {details['models']}개 모델, {details['support_items']}개 지원금 정보"
                
                summary_message += f"""

📁 <b>저장 파일</b>
• JSON: {json_filename}
• CSV: {csv_filename}

✅ 크롤링이 성공적으로 완료되었습니다!"""
                
                # Telegram 메시지 전송
                utils.send_telegram_message(summary_message, telegram_bot_token, telegram_chat_id)
                
            except Exception as e:
                utils.log_message(f"Telegram 알림 전송 실패: {e}")
        else:
            utils.log_message("파일 생성 실패로 인해 Telegram 알림을 전송하지 않습니다.")
            
    except Exception as e:
        error_message = f"❌ <b>스마트초이스 크롤링 오류</b>\n\n오류 내용: {str(e)}\n\n시간: {utils.get_current_datetime()}"
        
        # 섹션 관련 오류는 제외하고 실제 크롤링 실패만 알림
        error_str = str(e).lower()
        is_section_error = any(keyword in error_str for keyword in [
            "no such element: unable to locate element", 
            "섹션", 
            "section"
        ]) and any(section in error_str for section in ["a01", "b01", "c01", "d01", "e01", "f01", "g01", "h01", "i01", "j01"])
        
        # Telegram 오류 알림 전송 (섹션 오류 제외)
        if not is_section_error:
            try:
                telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN') or config.TELEGRAM_BOT_TOKEN
                telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID') or config.TELEGRAM_CHAT_ID
                utils.send_telegram_message(error_message, telegram_bot_token, telegram_chat_id)
            except:
                pass
        
        utils.log_message(f"크롤링 중 오류 발생: {e}")
    finally:
        if crawler:
            crawler.close_driver()
        utils.log_message("크롤링 종료")

if __name__ == "__main__":
    main() 