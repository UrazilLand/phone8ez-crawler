#통신사
#contentsarea > div.devicesupport > div.contentsbox > div.tab_contents > div.dantong_result_top > div > div > table > thead > tr:nth-child(1) > td:nth-child(2)
#contentsarea > div.devicesupport > div.contentsbox > div.tab_contents > div.dantong_result_top > div > div > table > thead > tr:nth-child(1) > td:nth-child(3)
#contentsarea > div.devicesupport > div.contentsbox > div.tab_contents > div.dantong_result_top > div > div > table > thead > tr:nth-child(1) > td:nth-child(4)

#출고가(쉼표 제거, '원'제거, 숫자로 변환)
#contentsarea > div.devicesupport > div.contentsbox > div.tab_contents > div.dantong_result_top > div > div > table > thead > tr:nth-child(2) > td:nth-child(1)
#contentsarea > div.devicesupport > div.contentsbox > div.tab_contents > div.dantong_result_top > div > div > table > thead > tr:nth-child(3) > td:nth-child(2)
#contentsarea > div.devicesupport > div.contentsbox > div.tab_contents > div.dantong_result_top > div > div > table > thead > tr:nth-child(4) > td:nth-child(3)

#요금제명
#A01 > div > table > tbody > tr.choice > td:nth-child(2) > span.name
#A01 > div > table > tbody > tr.choice > td:nth-child(3) > span.name
#A01 > div > table > tbody > tr.choice > td:nth-child(4) > span.name

#월 요금제
#A01 > div > table > tbody > tr.choice > td:nth-child(2) > span.price > em
#A01 > div > table > tbody > tr.choice > td:nth-child(3) > span.price > em
#A01 > div > table > tbody > tr.choice > td:nth-child(4) > span.price > em

#기기변경 지원금 (쉼표 제거 숫자로 변환 )
#A01 > div > table > tbody > tr.grey_bg.fs9 > td:nth-child(3) > a > span > em
#A01 > div > table > tbody > tr.grey_bg.fs9 > td:nth-child(4) > a > span > em
#A01 > div > table > tbody > tr.grey_bg.fs9 > td:nth-child(5) > a > span > em

#번호이동 지원금 (쉼표 제거 숫자로 변환)
#A01 > div > table > tbody > tr:nth-child(5) > td:nth-child(2) > a > span > em
#A01 > div > table > tbody > tr:nth-child(5) > td:nth-child(3) > a > span > em
#A01 > div > table > tbody > tr:nth-child(5) > td:nth-child(4) > a > span > em

#공시일
#A01 > div > table > tbody > tr:nth-child(6) > td:nth-child(2) > a
#A01 > div > table > tbody > tr:nth-child(6) > td:nth-child(3) > a
#A01 > div > table > tbody > tr:nth-child(6) > td:nth-child(4) > a


from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
import json
import os
import shutil
from pathlib import Path

# 📌 셀렉터 모음
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
    "plan_name": "#A01 > div > table > tbody > tr.choice > td:nth-child(2) > span.name",  # 요금제명
    "plan_price": "#A01 > div > table > tbody > tr.choice > td:nth-child(2) > span.price > em",  # 월 요금제
    "release_date": ".date",  # 출시일
    "carrier": "#contentsarea > div.devicesupport > div.contentsbox > div.tab_contents > div.dantong_result_top > div > div > table > thead > tr:nth-child(1) > td:nth-child(2)",  # 통신사
    "release_price": "#contentsarea > div.devicesupport > div.contentsbox > div.tab_contents > div.dantong_result_top > div > div > table > thead > tr:nth-child(2) > td:nth-child(1)",  # 출고가
    "device_change_support": "#A01 > div > table > tbody > tr.grey_bg.fs9 > td:nth-child(3) > a > span > em",  # 기기변경 지원금
    "number_port_support": "#A01 > div > table > tbody > tr:nth-child(5) > td:nth-child(2) > a > span > em",  # 번호이동 지원금
    "notice_date": "#A01 > div > table > tbody > tr:nth-child(6) > td:nth-child(2) > a"  # 공시일
}

def print_model_data(model_name, sheet_id, carrier_data):
    """모델별 통신사 데이터를 보기 좋게 출력"""
    print(f"\n{'='*50}")
    print(f"📱 모델: {model_name} (시트: {sheet_id})")
    print(f"{'='*50}")
    
    for carrier, data in carrier_data.items():
        if not data:  # 데이터가 없는 경우
            print(f"\n❌ {carrier}: 데이터 없음")
            continue
            
        print(f"\n📡 {carrier}")
        print(f"  ├─ 출고가: {data['출고가']:,}원")
        print(f"  ├─ 요금제: {data['요금제명']}")
        print(f"  ├─ 월요금: {data['월요금']:,}원")
        print(f"  ├─ 기기변경지원금: {data['기기변경지원금']:,}원")
        print(f"  ├─ 번호이동지원금: {data['번호이동지원금']:,}원")
        print(f"  └─ 공시일: {data['공시일']}")
    print(f"\n{'='*50}\n")

# 📌 제조사 목록
BRANDS = ["삼성전자", "애플", "기타"]

# 📌 시트별 셀렉터 템플릿
SHEET_SELECTORS = {
    "carrier": "#contentsarea > div.devicesupport > div.contentsbox > div.tab_contents > div.dantong_result_top > div > div > table > thead > tr:nth-child(1) > td:nth-child({idx})",  # 통신사 (2,3,4)
    "release_price": "#contentsarea > div.devicesupport > div.contentsbox > div.tab_contents > div.dantong_result_top > div > div > table > thead > tr:nth-child(2) > td:nth-child({idx})",  # 출고가 (1,2,3)
    "plan_name": "#A01 > div > table > tbody > tr.choice > td:nth-child({idx}) > span.name",  # 요금제명 (2,3,4)
    "monthly_fee": "#A01 > div > table > tbody > tr.choice > td:nth-child({idx}) > span.price > em",  # 월 요금제 (2,3,4)
    "device_change_support": "#A01 > div > table > tbody > tr.grey_bg.fs9 > td:nth-child({idx}) > a > span > em",  # 기기변경 지원금 (3,4,5)
    "number_port_support": "#A01 > div > table > tbody > tr:nth-child(5) > td:nth-child({idx}) > a > span > em",  # 번호이동 지원금 (2,3,4)
    "notice_date": "#A01 > div > table > tbody > tr:nth-child(6) > td:nth-child({idx}) > a"  # 공시일 (2,3,4)
}

# 📌 데이터 항목별 인덱스 매핑
DATA_INDICES = {
    "carrier": [2, 3, 4],  # 통신사
    "release_price": [1, 2, 3],  # 출고가
    "plan_name": [2, 3, 4],  # 요금제명
    "monthly_fee": [2, 3, 4],  # 월 요금제
    "device_change_support": [3, 4, 5],  # 기기변경 지원금
    "number_port_support": [2, 3, 4],  # 번호이동 지원금
    "notice_date": [2, 3, 4]  # 공시일
}

# 📌 시트 ID 목록
SHEET_IDS = ["A01", "B01", "C01", "D01", "E01", "F01", "G01"]

# 📌 통신사 목록
CARRIERS = ["SKT", "KT", "LGU+"]

# 📌 시트별 통신사 컬럼 인덱스 매핑
SHEET_CARRIER_INDICES = {
    "A01": [2, 3, 4],  # SKT: 2, KT: 3, LGU+: 4
    "B01": [2, 3, 4],
    "C01": [2, 3, 4],
    "D01": [2, 3, 4],
    "E01": [2, 3, 4],
    "F01": [2, 3, 4],
    "G01": [2, 3, 4]
}

# 📌 WebDriver 실행
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 헤드리스 모드
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)
driver.get("https://m.smartchoice.or.kr/smc/mobile/dantongList.do?type=m")
WebDriverWait(driver, 10).until(EC.presence_of_element_located(SELECTORS["manufacturer_dropdown"]))
time.sleep(1)  # 페이지 완전 로딩 대기

# 📌 오늘 날짜 기준 2년 이내 출시 모델만 필터링
results = []
today = datetime.today()
cutoff_year = today.year - 2

# 📌 결과 파일명 생성
def get_output_filename():
    """연월별 폴더에 날짜가 포함된 파일명 생성"""
    today = datetime.today()
    year_month = today.strftime('%Y%m')
    
    # 연월별 폴더 생성
    output_dir = Path(f"data/{year_month}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 파일명 생성
    base_name = f"smartchoice_results_{today.strftime('%Y%m%d')}.json"
    counter = 1
    
    while (output_dir / base_name).exists():
        base_name = f"smartchoice_results_{today.strftime('%Y%m%d')}_{counter}.json"
        counter += 1
    
    return output_dir / base_name

def cleanup_old_data():
    """한 달이 지난 데이터 폴더 삭제"""
    today = datetime.today()
    data_dir = Path("data")
    
    if not data_dir.exists():
        return
        
    for folder in data_dir.iterdir():
        if not folder.is_dir():
            continue
            
        try:
            folder_date = datetime.strptime(folder.name, '%Y%m')
            # 한 달이 지난 폴더 삭제
            if (today.year - folder_date.year) * 12 + (today.month - folder_date.month) > 1:
                shutil.rmtree(folder)
                print(f"🗑️ 오래된 데이터 폴더 삭제: {folder}")
        except ValueError:
            continue

# 메인 실행 부분 시작 전에 오래된 데이터 정리
cleanup_old_data()

output_file = get_output_filename()
print(f"📁 결과 파일: {output_file}")

def save_results():
    """현재까지의 결과를 파일에 저장"""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"💾 현재까지 {len(results)}개 데이터 저장 완료")

# 📌 각 제조사 반복
for brand in BRANDS:
    print(f"\n🚩 제조사: {brand}")
    model_data = []

    try:
        # 알림창이 있다면 처리
        try:
            alert = driver.switch_to.alert
            alert.accept()
            time.sleep(1)
        except:
            pass

        # 페이지 초기화
        print("🔄 페이지 초기화 중...")
        try:
            # JavaScript로 초기화 버튼 클릭
            reset_button = driver.find_element(*SELECTORS["reset_button"])
            driver.execute_script("arguments[0].click();", reset_button)
            time.sleep(3)  # 초기화 후 대기 시간 증가
            print("✅ 페이지 초기화 완료")
        except Exception as e:
            print(f"❌ 초기화 실패: {e}")
            # 페이지 새로고침으로 대체
            print("🔄 페이지 새로고침으로 대체...")
            driver.refresh()
            time.sleep(3)
            print("✅ 페이지 새로고침 완료")

        # 제조사 선택
        manufacturer_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(SELECTORS["manufacturer_dropdown"])
        )
        Select(manufacturer_dropdown).select_by_visible_text(brand)
        time.sleep(2)  # 선택 후 대기

        # 모델 모달 버튼이 다시 활성화되기를 기다림
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(SELECTORS["model_modal_button"]))
        time.sleep(2)  # 대기 시간 증가
        
        try:
            # 모델 모달 버튼 클릭
            driver.find_element(*SELECTORS["model_modal_button"]).click()
        except Exception as e:
            print(f"❌ 모델 모달 버튼 클릭 실패: {e}")
            continue

        # 모델 리스트가 로딩될 때까지 대기
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(SELECTORS["model_list"]))
            time.sleep(1)
        except TimeoutException:
            print("❌ 모델 리스트 로딩 실패 - 다음 제조사로 넘어갑니다.")
            continue

        model_elements = driver.find_elements(*SELECTORS["model_list"])
        print(f"모델 요소 수: {len(model_elements)}개")

        # 모델 정보 수집 (1년 이내만)
        for el in model_elements:
            try:
                name = el.find_element(By.ID, "spanPhone_name").text.strip()
                release = el.find_element(By.CLASS_NAME, "release_date").text.strip()
                release_year = int(re.findall(r"\d{4}", release)[0]) if re.findall(r"\d{4}", release) else 0

                if release_year >= cutoff_year:
                    model_code = el.get_attribute("for")
                    model_data.append({"모델명": name, "출시일": release, "모델코드": model_code})
            except Exception as e:
                print("❌ 모델 파싱 실패:", e)

        print(f"✅ 출시일 2년 이내 모델 수: {len(model_data)}개")

        # 모달 닫기
        driver.find_element(*SELECTORS["modal_close_button"]).click()

        # 모델별 검색 시작
        for i, model in enumerate(model_data):
            print(f"\n🔍 {i + 1}번째 모델 선택 시작: {model['모델명']} ({model['출시일']})")

            try:
                # 모델 선택 모달 다시 열기
                time.sleep(3)
                model_modal_button = driver.find_element(*SELECTORS["model_modal_button"])
                driver.execute_script("arguments[0].scrollIntoView(true);", model_modal_button)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", model_modal_button)
                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(SELECTORS["model_list"]))
                time.sleep(1)

                # 해당 모델 클릭
                model_elements = driver.find_elements(*SELECTORS["model_list"])
                target_model = next((el for el in model_elements if el.get_attribute("for") == model["모델코드"]), None)
                if not target_model:
                    print(f"❌ 모델코드 {model['모델코드']} 찾기 실패")
                    continue

                target_model.click()
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(SELECTORS["select_model_button"]))
                time.sleep(1)
                driver.find_element(*SELECTORS["select_model_button"]).click()

                # 검색 버튼 클릭
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(SELECTORS["search_button"]))
                time.sleep(1)
                driver.find_element(*SELECTORS["search_button"]).click()

                # 결과 페이지 로딩 대기 (여러 요소 확인)
                try:
                    WebDriverWait(driver, 20).until(
                        EC.any_of(
                            EC.presence_of_element_located(SELECTORS["result_notice"]),
                            EC.presence_of_element_located(SELECTORS["result_table"])
                        )
                    )
                except TimeoutException:
                    print(f"❌ 결과 페이지 로딩 실패 - 모델: {model['모델명']}")
                    continue

                # BeautifulSoup 파싱
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # 디버깅을 위해 HTML 저장
                if i == 0:  # 첫 번째 모델인 경우
                    with open("debug_first_model.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                    print("✅ 디버깅용 HTML 저장 완료")
                    
                    # 첫 번째 모델의 경우 셀렉터 테스트
                    print("\n🔍 셀렉터 테스트:")
                    for key, selector in SHEET_SELECTORS.items():
                        test_selector = selector.format(sheet_id="A01", idx=2)
                        element = soup.select_one(test_selector)
                        print(f"  - {key}: {'✅' if element else '❌'} ({test_selector})")
                
                # 각 시트별로 데이터 수집
                for sheet_id in SHEET_IDS:
                    carrier_data = {carrier: None for carrier in CARRIERS}  # 통신사별 데이터 저장
                    
                    # 각 통신사별로 데이터 수집
                    for carrier_idx, carrier in enumerate(CARRIERS):
                        try:
                            # 셀렉터 생성 (각 데이터 항목별로 다른 인덱스 사용)
                            selectors = {
                                key: selector.format(
                                    sheet_id=sheet_id,
                                    idx=DATA_INDICES[key][carrier_idx]  # 각 데이터 항목별 인덱스 사용
                                )
                                for key, selector in SHEET_SELECTORS.items()
                            }
                            
                            # 데이터 추출
                            carrier_name = soup.select_one(selectors["carrier"])
                            if not carrier_name:  # 해당 통신사 데이터가 없는 경우
                                print(f"⚠️ {sheet_id} 시트의 {carrier} 통신사 데이터 없음 (셀렉터: {selectors['carrier']})")
                                continue
                                
                            carrier_name = carrier_name.text.strip()
                            release_price = soup.select_one(selectors["release_price"])
                            plan_name = soup.select_one(selectors["plan_name"])
                            monthly_fee = soup.select_one(selectors["monthly_fee"])
                            device_change_support = soup.select_one(selectors["device_change_support"])
                            number_port_support = soup.select_one(selectors["number_port_support"])
                            notice_date = soup.select_one(selectors["notice_date"])
                            
                            # 디버깅 정보 출력
                            print(f"\n🔍 {sheet_id} 시트의 {carrier} 데이터:")
                            print(f"  - 통신사: {carrier_name} (인덱스: {DATA_INDICES['carrier'][carrier_idx]})")
                            print(f"  - 출고가: {release_price.text.strip() if release_price else '없음'} (인덱스: {DATA_INDICES['release_price'][carrier_idx]})")
                            print(f"  - 요금제: {plan_name.text.strip() if plan_name else '없음'} (인덱스: {DATA_INDICES['plan_name'][carrier_idx]})")
                            
                            # 통신사별 데이터 저장
                            carrier_data[carrier] = {
                                "출고가": int(re.sub(r"[^0-9]", "", release_price.text.strip())) if release_price else 0,
                                "요금제명": plan_name.text.strip() if plan_name else "",
                                "월요금": int(re.sub(r"[^0-9]", "", monthly_fee.text.strip())) if monthly_fee else 0,
                                "기기변경지원금": int(re.sub(r"[^0-9]", "", device_change_support.text.strip())) if device_change_support else 0,
                                "번호이동지원금": int(re.sub(r"[^0-9]", "", number_port_support.text.strip())) if number_port_support else 0,
                                "공시일": notice_date.text.strip() if notice_date else ""
                            }
                            
                            # 결과 저장
                            results.append({
                                "제조사": brand,
                                "모델명": model["모델명"],
                                "모델코드": model["모델코드"],
                                "출시일": model["출시일"],
                                "시트ID": sheet_id,
                                "통신사": carrier_name,
                                **carrier_data[carrier]  # 통신사 데이터 추가
                            })
                            
                            # 실시간 저장
                            save_results()
                            
                        except Exception as e:
                            print(f"❌ 데이터 추출 실패 - 시트: {sheet_id}, 통신사: {carrier}, 에러: {e}")
                            continue
                    
                    # 시트별 데이터 출력
                    print_model_data(model["모델명"], sheet_id, carrier_data)
                    
            except Exception as e:
                print(f"❌ 모델 처리 중 오류 발생: {e}")
                continue

    except Exception as e:
        print(f"❌ 제조사 처리 중 오류 발생: {e}")
        continue

print(f"\n✅ 총 {len(results)}개 항목 저장 완료")
driver.quit()


