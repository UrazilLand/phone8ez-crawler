#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
스마트초이스 단말기 지원금 크롤러 (정식 버전)
스마트초이스(https://m.smartchoice.or.kr)에서 휴대폰 단말기 지원금 정보를 자동으로 수집합니다.

주요 기능:
- 제조사별 단말기 지원금 조회
- 모델별 상세 정보 추출 (요금제, 월 요금, 기기변경/번호이동 지원금)
- 다중 통신사 비교 (SKT, KT, LG U+)
- 모델 정보 요약 (모델번호:모델명:출고가)
- 자동화된 데이터 수집 및 저장

버전: 1.0.0
작성일: 2025-06-21
"""

import time
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 📌 셀렉터 모음 (개선된 버전)
SELECTORS = {
    "manufacturer_dropdown": (By.ID, "dan_Mau"),  # 제조사 선택 드롭다운
    "model_modal_button": (By.ID, "productName_Show"),  # 모델 선택 모달 열기 버튼
    "model_list": (By.CSS_SELECTOR, "label.monthlyValue"),  # 모달 내부 모델 리스트
    "modal_close_button": (By.CSS_SELECTOR, "#contentsarea > div.devicesupport > div.contentsbox > div.modalpop > div.popupwrap.selectProductPopup > button"),
    "select_model_button": (By.ID, "selectPhone"),  # 모델 확정 버튼
    "search_button": (By.CSS_SELECTOR, "#dantongForm > fieldset > div > a.h_btn.fill.size_l"),  # 검색 버튼
    "result_notice": (By.CSS_SELECTOR, ".result_notice"),  # 공시일 안내 문구
    "result_table": (By.CSS_SELECTOR, "#A01 > div > table"),  # 결과 테이블
    "reset_button": (By.CSS_SELECTOR, "#dantongForm > fieldset > div > a.h_btn.noHover.blank.size_l.icon_refresh"),  # 초기화 버튼
    # 추가된 셀렉터들
    "loading_spinner": (By.CSS_SELECTOR, ".loading, .spinner"),  # 로딩 스피너
    "error_message": (By.CSS_SELECTOR, ".error, .alert"),  # 에러 메시지
    "no_result_message": (By.CSS_SELECTOR, ".no_result, .empty_result"),  # 결과 없음 메시지
}

# 📌 제조사 목록
BRANDS = ["삼성전자", "애플", "기타"]
SHEET_IDS = ["A01", "B01", "C01", "D01", "E01", "F01", "G01", "H01", "I01", "J01"]

# 📌 시트별 셀렉터 템플릿 (동적 시트 ID 지원)
SHEET_SELECTORS = {
    "carrier": "#contentsarea > div.devicesupport > div.contentsbox > div.tab_contents > div.dantong_result_top > div > div > table > thead > tr:nth-child(1) > td:nth-child({idx})",  # 통신사 (2,3,4)
    "release_price": "#contentsarea > div.devicesupport > div.contentsbox > div.tab_contents > div.dantong_result_top > div > div > table > thead > tr:nth-child(2) > td:nth-child({idx})",  # 출고가 (1,2,3)
    "plan_name": "#{sheet_id} > div > table > tbody > tr.choice > td:nth-child({idx}) > span.name",  # 요금제명 (2,3,4)
    "monthly_fee": "#{sheet_id} > div > table > tbody > tr.choice > td:nth-child({idx}) > span.price > em",  # 월 요금제 (2,3,4)
    "device_change_support": "#{sheet_id} > div > table > tbody > tr.grey_bg.fs9 > td:nth-child({idx}) > a > span > em",  # 기기변경 지원금 (3,4,5) 
    "number_port_support": "#{sheet_id} > div > table > tbody > tr:nth-child(5) > td:nth-child({idx}) > a > span > em",  # 번호이동 지원금 (2,3,4)
    "notice_date": "#{sheet_id} > div > table > tbody > tr:nth-child(6) > td:nth-child({idx}) > a"  # 공시일 (2,3,4)
}

class SmartChoiceCrawler:
    def __init__(self, headless=True):
        """
        스마트초이스 크롤러 초기화
        """
        self.url = "https://m.smartchoice.or.kr/smc/mobile/dantongList.do?type=m"
        self.driver = None
        self.wait = None
        self.headless = headless
        self.setup_driver()
    
    def setup_driver(self):
        """
        1단계: 웹드라이버 설정 (개선된 버전)
        """
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,3000")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            # 추가된 옵션들
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            # 자동화 감지 방지
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 20)  # 대기 시간을 20초로 증가
            logger.info("웹드라이버 설정 완료")
            
        except Exception as e:
            logger.error(f"웹드라이버 설정 실패: {e}")
            raise
    
    def navigate_to_page(self):
        """
        2단계: 페이지 접속 (개선된 버전)
        """
        try:
            self.driver.get(self.url)
            logger.info(f"페이지 접속 완료: {self.url}")
            
            # 페이지 로딩 대기
            self.wait.until(EC.presence_of_element_located(SELECTORS["manufacturer_dropdown"]))
            logger.info("페이지 로딩 완료")
            
            # 추가 대기 시간
            time.sleep(3)
            
        except TimeoutException:
            logger.error("페이지 로딩 시간 초과")
            raise
        except Exception as e:
            logger.error(f"페이지 접속 실패: {e}")
            raise
    
    def select_manufacturer(self, manufacturer):
        """
        3단계: 제조사 선택 (개선된 버전)
        """
        try:
            # 제조사 드롭다운 찾기
            dropdown = self.wait.until(EC.element_to_be_clickable(SELECTORS["manufacturer_dropdown"]))
            select = Select(dropdown)
            
            # 제조사 선택
            select.select_by_visible_text(manufacturer)
            logger.info(f"제조사 선택 완료: {manufacturer}")
            
            # 선택 후 잠시 대기
            time.sleep(3)
            
        except Exception as e:
            logger.error(f"제조사 선택 실패: {e}")
            raise
    
    def safe_click(self, element):
        """
        안전한 클릭 메서드 (요소 클릭 차단 문제 해결)
        """
        try:
            # 요소가 보이도록 스크롤 (중앙에 위치하도록)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", element)
            time.sleep(0.5)  # 스크롤 후 잠시 대기
            
            # JavaScript로 클릭 시도
            self.driver.execute_script("arguments[0].click();", element)
            return True
        except Exception as e1:
            logger.warning(f"JavaScript 클릭 실패: {e1}")
            try:
                # ActionChains로 클릭 시도 (요소로 이동 후 클릭)
                ActionChains(self.driver).move_to_element(element).pause(0.3).click().perform()
                return True
            except Exception as e2:
                logger.warning(f"ActionChains 클릭 실패: {e2}")
                try:
                    # 일반 클릭 시도
                    element.click()
                    return True
                except Exception as e3:
                    logger.error(f"모든 클릭 방법 실패: {e3}")
                    return False
    
    def select_model(self, model_name):
        """
        4단계: 모델 선택 (모달 처리) - 개선된 버전
        """
        try:
            # 페이지 스크롤
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # 모델 선택 모달 열기
            modal_button = self.wait.until(EC.element_to_be_clickable(SELECTORS["model_modal_button"]))
            
            # 안전한 클릭 사용
            if not self.safe_click(modal_button):
                logger.error("모달 버튼 클릭 실패")
                return False
                
            logger.info("모델 선택 모달 열기")
            
            # 모달 내부 모델 리스트 대기
            time.sleep(3)
            
            # 모델 검색 및 선택
            model_elements = self.driver.find_elements(*SELECTORS["model_list"])
            
            # 모델명 매칭 개선
            for element in model_elements:
                element_text = element.text.strip()
                logger.info(f"찾은 모델: {element_text}")
                
                # 부분 매칭으로 변경
                if model_name.lower() in element_text.lower() or element_text.lower() in model_name.lower():
                    # 요소가 보이도록 스크롤
                    try:
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", element)
                        time.sleep(0.5)
                    except Exception as e:
                        logger.warning(f"모델 요소 스크롤 실패: {e}")
                    
                    if self.safe_click(element):
                        logger.info(f"모델 선택 완료: {model_name} (매칭: {element_text})")
                        break
                    else:
                        logger.warning(f"모델 클릭 실패: {element_text}")
                        continue
            else:
                logger.warning(f"모델을 찾을 수 없음: {model_name}")
                # 모달 닫기
                try:
                    close_button = self.driver.find_element(*SELECTORS["modal_close_button"])
                    self.safe_click(close_button)
                except:
                    pass
                return False
            
            # 모델 확정 버튼 클릭
            select_button = self.wait.until(EC.element_to_be_clickable(SELECTORS["select_model_button"]))
            if self.safe_click(select_button):
                logger.info("모델 확정 완료")
                time.sleep(2)
                return True
            else:
                logger.error("모델 확정 버튼 클릭 실패")
                return False
            
        except Exception as e:
            logger.error(f"모델 선택 실패: {e}")
            return False
    
    def search_support_info(self):
        """
        5단계: 검색 실행 (개선된 버전)
        """
        try:
            # 페이지 스크롤
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # 검색 버튼 클릭
            search_button = self.wait.until(EC.element_to_be_clickable(SELECTORS["search_button"]))
            if not self.safe_click(search_button):
                logger.error("검색 버튼 클릭 실패")
                raise Exception("검색 버튼 클릭 실패")
                
            logger.info("검색 실행")
            
            # 로딩 스피너 대기
            try:
                self.wait.until(EC.presence_of_element_located(SELECTORS["loading_spinner"]))
                logger.info("로딩 스피너 감지됨")
            except TimeoutException:
                logger.info("로딩 스피너 없음, 직접 대기")
            
            # 결과 로딩 대기 (시간 증가)
            try:
                self.wait.until(EC.presence_of_element_located(SELECTORS["result_notice"]))
                logger.info("검색 결과 로딩 완료")
                return True
            except TimeoutException:
                # 결과 테이블이 있는지 확인
                try:
                    self.driver.find_element(*SELECTORS["result_table"])
                    logger.info("결과 테이블이 존재함 (결과 있음)")
                    return True
                except NoSuchElementException:
                    logger.warning("결과 테이블 없음, 결과 없음 처리")
                    return False
        except Exception as e:
            logger.error(f"검색 실행 실패: {e}")
            raise
    
    def extract_support_data(self):
        """
        6단계: 지원금 데이터 추출 (개선된 버전)
        """
        try:
            data = []
            
            # 각 시트별로 데이터 추출
            for sheet_id in SHEET_IDS:
                try:
                    # 시트 존재 여부 확인
                    sheet_selector = f"#{sheet_id}"
                    sheet_element = self.driver.find_element(By.CSS_SELECTOR, sheet_selector)
                    
                    # 통신사 정보 추출
                    carriers = []
                    for idx in [2, 3, 4]:
                        try:
                            carrier_selector = SHEET_SELECTORS["carrier"].format(idx=idx)
                            carrier_element = self.driver.find_element(By.CSS_SELECTOR, carrier_selector)
                            carriers.append(carrier_element.text.strip())
                        except NoSuchElementException:
                            carriers.append("")
                    
                    # 출고가 정보 추출
                    release_prices = []
                    for idx in [1, 2, 3]:
                        try:
                            price_selector = SHEET_SELECTORS["release_price"].format(idx=idx)
                            price_element = self.driver.find_element(By.CSS_SELECTOR, price_selector)
                            price_text = price_element.text.strip().replace(",", "").replace("원", "").strip()
                            release_prices.append(price_text)
                        except NoSuchElementException:
                            release_prices.append("")
                    
                    # 요금제별 정보 추출
                    for carrier_idx, carrier in enumerate(carriers, 1):
                        if not carrier:
                            continue
                            
                        try:
                            # 요금제명
                            plan_selector = SHEET_SELECTORS["plan_name"].format(sheet_id=sheet_id, idx=carrier_idx+1)
                            plan_element = self.driver.find_element(By.CSS_SELECTOR, plan_selector)
                            plan_name = plan_element.text.strip()
                            
                            # 월 요금
                            fee_selector = SHEET_SELECTORS["monthly_fee"].format(sheet_id=sheet_id, idx=carrier_idx+1)
                            fee_element = self.driver.find_element(By.CSS_SELECTOR, fee_selector)
                            monthly_fee = fee_element.text.strip().replace(",", "").replace("원", "").strip()
                            
                            # 기기변경 지원금
                            device_selector = SHEET_SELECTORS["device_change_support"].format(sheet_id=sheet_id, idx=carrier_idx+2)
                            device_element = self.driver.find_element(By.CSS_SELECTOR, device_selector)
                            device_support = device_element.text.strip().replace(",", "").replace("원", "").strip()
                            
                            # 번호이동 지원금
                            port_selector = SHEET_SELECTORS["number_port_support"].format(sheet_id=sheet_id, idx=carrier_idx+1)
                            port_element = self.driver.find_element(By.CSS_SELECTOR, port_selector)
                            port_support = port_element.text.strip().replace(",", "").replace("원", "").strip()
                            
                            # 공시일
                            notice_selector = SHEET_SELECTORS["notice_date"].format(sheet_id=sheet_id, idx=carrier_idx+1)
                            notice_element = self.driver.find_element(By.CSS_SELECTOR, notice_selector)
                            notice_date = notice_element.text.strip()
                            
                            data.append({
                                "sheet_id": sheet_id,
                                "carrier": carrier,
                                "release_price": release_prices[carrier_idx-1] if carrier_idx <= len(release_prices) else "",
                                "plan_name": plan_name,
                                "monthly_fee": monthly_fee,
                                "device_change_support": device_support,
                                "number_port_support": port_support,
                                "notice_date": notice_date
                            })
                            
                        except NoSuchElementException as e:
                            logger.warning(f"데이터 추출 실패 (시트: {sheet_id}, 통신사: {carrier}): {e}")
                            continue
                            
                except NoSuchElementException:
                    logger.info(f"시트 {sheet_id} 없음, 다음 시트로 진행")
                    continue
            
            logger.info(f"데이터 추출 완료: {len(data)}개 항목")
            return data
            
        except Exception as e:
            logger.error(f"데이터 추출 실패: {e}")
            return []
    
    def reset_search(self):
        """
        7단계: 검색 초기화 (개선된 버전)
        """
        try:
            reset_button = self.wait.until(EC.element_to_be_clickable(SELECTORS["reset_button"]))
            if self.safe_click(reset_button):
                logger.info("검색 초기화 완료")
                # 초기화 후 대기
                time.sleep(3)
            else:
                logger.error("검색 초기화 버튼 클릭 실패")
            
        except Exception as e:
            logger.error(f"검색 초기화 실패: {e}")
    
    def save_data(self, data, filename="smartchoice_data.json"):
        """
        8단계: 데이터 저장
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"데이터 저장 완료: {filename}")
            
            # CSV로도 저장
            df = pd.DataFrame(data)
            csv_filename = filename.replace('.json', '.csv')
            df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
            logger.info(f"CSV 저장 완료: {csv_filename}")
            
        except Exception as e:
            logger.error(f"데이터 저장 실패: {e}")
    
    def close(self):
        """
        브라우저 종료
        """
        if self.driver:
            self.driver.quit()
            logger.info("브라우저 종료")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def extract_model_info(self):
        """
        모델 기본 정보 추출 (모델번호:모델명:출고가)
        """
        try:
            model_info = {}
            
            # 모델명 추출 (이미 선택된 모델)
            selected_model_element = self.driver.find_element(By.ID, "productName_Show")
            model_name = selected_model_element.get_attribute("value")
            
            # 출고가 정보 추출 (최대값 찾기)
            max_price = ""
            try:
                # 출고가 테이블에서 최대값 찾기
                price_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    "#contentsarea > div.devicesupport > div.contentsbox > div.tab_contents > div.dantong_result_top > div > div > table > thead > tr:nth-child(2) > td")
                
                prices = []
                for element in price_elements:
                    price_text = element.text.strip().replace(",", "").replace("원", "").strip()
                    if price_text and "원" in price_text:
                        # 숫자만 추출
                        price_num = ''.join(filter(str.isdigit, price_text))
                        if price_num:
                            prices.append(int(price_num))
                
                if prices:
                    max_price = str(max(prices))
                    logger.info(f"최대 출고가: {max_price}")
                
            except Exception as e:
                logger.warning(f"출고가 추출 실패: {e}")
            
            # 모델번호는 추후 필요시 추가 (현재는 모델명으로 대체)
            model_code = model_name  # 실제 모델번호가 있다면 여기서 추출
            
            model_info = {
                "model_code": model_code,
                "model_name": model_name,
                "max_price": max_price
            }
            
            logger.info(f"모델 정보 추출 완료: {model_code}:{model_name}:{max_price}")
            return model_info
            
        except Exception as e:
            logger.error(f"모델 정보 추출 실패: {e}")
            return {}
    
    def extract_carrier_plans(self):
        """
        통신사별 요금제 정보 추출
        """
        try:
            carrier_plans = {}
            
            # 각 시트별로 데이터 추출
            for sheet_id in SHEET_IDS:
                try:
                    # 시트 존재 여부 확인
                    sheet_selector = f"#{sheet_id}"
                    sheet_element = self.driver.find_element(By.CSS_SELECTOR, sheet_selector)
                    
                    # 통신사 정보 추출
                    carriers = []
                    for idx in [2, 3, 4]:
                        try:
                            carrier_selector = SHEET_SELECTORS["carrier"].format(idx=idx)
                            carrier_element = self.driver.find_element(By.CSS_SELECTOR, carrier_selector)
                            carrier_name = carrier_element.text.strip()
                            if carrier_name:
                                carriers.append(carrier_name)
                        except NoSuchElementException:
                            continue
                    
                    # 각 통신사별 요금제 추출
                    for carrier_idx, carrier in enumerate(carriers, 1):
                        if carrier not in carrier_plans:
                            carrier_plans[carrier] = []
                        
                        try:
                            # 요금제명
                            plan_selector = SHEET_SELECTORS["plan_name"].format(sheet_id=sheet_id, idx=carrier_idx+1)
                            plan_element = self.driver.find_element(By.CSS_SELECTOR, plan_selector)
                            plan_name = plan_element.text.strip()
                            
                            # 월 요금
                            fee_selector = SHEET_SELECTORS["monthly_fee"].format(sheet_id=sheet_id, idx=carrier_idx+1)
                            fee_element = self.driver.find_element(By.CSS_SELECTOR, fee_selector)
                            monthly_fee = fee_element.text.strip().replace(",", "").replace("원", "").strip()
                            
                            # 기기변경 지원금
                            device_selector = SHEET_SELECTORS["device_change_support"].format(sheet_id=sheet_id, idx=carrier_idx+2)
                            device_element = self.driver.find_element(By.CSS_SELECTOR, device_selector)
                            device_support = device_element.text.strip().replace(",", "").replace("원", "").strip()
                            
                            # 번호이동 지원금
                            port_selector = SHEET_SELECTORS["number_port_support"].format(sheet_id=sheet_id, idx=carrier_idx+1)
                            port_element = self.driver.find_element(By.CSS_SELECTOR, port_selector)
                            port_support = port_element.text.strip().replace(",", "").replace("원", "").strip()
                            
                            plan_info = {
                                "plan_name": plan_name,
                                "monthly_fee": monthly_fee,
                                "device_change_support": device_support,
                                "number_port_support": port_support,
                                "sheet_id": sheet_id
                            }
                            
                            carrier_plans[carrier].append(plan_info)
                            
                        except NoSuchElementException as e:
                            logger.warning(f"요금제 정보 추출 실패 (시트: {sheet_id}, 통신사: {carrier}): {e}")
                            continue
                            
                except NoSuchElementException:
                    logger.info(f"시트 {sheet_id} 없음, 다음 시트로 진행")
                    continue
            
            logger.info(f"통신사별 요금제 추출 완료: {len(carrier_plans)}개 통신사")
            return carrier_plans
            
        except Exception as e:
            logger.error(f"통신사별 요금제 추출 실패: {e}")
            return {}
    
    def crawl_model_with_summary(self, manufacturer, model_name):
        """
        모델 크롤링 + 요약 정보 생성
        """
        try:
            # 1. 제조사 선택
            self.select_manufacturer(manufacturer)
            time.sleep(3)
            
            # 2. 모델 선택
            if not self.select_model(model_name):
                logger.error(f"모델 선택 실패: {model_name}")
                return None
            
            time.sleep(3)
            
            # 3. 검색 실행
            search_success = self.search_support_info()
            if not search_success:
                logger.warning(f"검색 결과 없음: {model_name}")
                return None
            
            time.sleep(5)
            
            # 4. 모델 정보 추출
            model_info = self.extract_model_info()
            
            # 5. 통신사별 요금제 추출
            carrier_plans = self.extract_carrier_plans()
            
            # 6. 결과 정리
            result = {
                "model_info": model_info,
                "carrier_plans": carrier_plans,
                "manufacturer": manufacturer,
                "model_name": model_name,
                "crawled_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            logger.info(f"크롤링 완료: {manufacturer} - {model_name}")
            return result
            
        except Exception as e:
            logger.error(f"크롤링 실패: {manufacturer} - {model_name}: {e}")
            return None
    
    def save_summary_data(self, all_results, filename="smartchoice_summary.json"):
        """
        모든 크롤링 결과를 요약하여 저장
        """
        try:
            # 모델 요약 정보 생성
            model_summaries = []
            detailed_results = []
            
            for result in all_results:
                if result and result.get("model_info"):
                    model_info = result["model_info"]
                    carrier_plans = result.get("carrier_plans", {})
                    
                    # 모델 요약 (모델번호:모델명:출고가)
                    model_summary = {
                        "model_code": model_info.get("model_code", ""),
                        "model_name": model_info.get("model_name", ""),
                        "max_price": model_info.get("max_price", ""),
                        "manufacturer": result.get("manufacturer", ""),
                        "summary_line": f"{model_info.get('model_code', '')}:{model_info.get('model_name', '')}:{model_info.get('max_price', '')}"
                    }
                    model_summaries.append(model_summary)
                    
                    # 상세 결과
                    detailed_results.append(result)
            
            # 최종 결과 구조
            final_result = {
                "summary": {
                    "total_models": len(model_summaries),
                    "crawled_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "model_summaries": model_summaries
                },
                "detailed_results": detailed_results
            }
            
            # JSON 저장
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(final_result, f, ensure_ascii=False, indent=2)
            logger.info(f"요약 데이터 저장 완료: {filename}")
            
            # CSV 요약 저장
            if model_summaries:
                import pandas as pd
                df_summary = pd.DataFrame(model_summaries)
                csv_filename = filename.replace('.json', '_summary.csv')
                df_summary.to_csv(csv_filename, index=False, encoding='utf-8-sig')
                logger.info(f"요약 CSV 저장 완료: {csv_filename}")
            
            return final_result
            
        except Exception as e:
            logger.error(f"요약 데이터 저장 실패: {e}")
            return None

# 정식 사용 예시
if __name__ == "__main__":
    print("📱 스마트초이스 단말기 지원금 크롤러 v1.0.0")
    print("=" * 50)
    print("이 파일은 크롤러 클래스 정의용입니다.")
    print("실제 크롤링은 'smartchoice_runner.py'를 실행하세요.")
    print("\n사용법:")
    print("python smartchoice_runner.py")
