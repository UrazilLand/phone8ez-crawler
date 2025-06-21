import traceback
import sys
import os

try:
    print("1. 모듈 import 테스트 시작...")
    import config
    print("   config 모듈 import 성공")
    
    import utils
    print("   utils 모듈 import 성공")
    
    from selenium import webdriver
    print("   selenium import 성공")
    
    print("\n2. 기본 설정 테스트...")
    print(f"   BASE_URL: {config.BASE_URL}")
    print(f"   DATA_DIR: {config.DATA_DIR}")
    
    print("\n3. 유틸리티 함수 테스트...")
    utils.create_data_directory()
    print("   데이터 디렉토리 생성 완료")
    
    print("\n4. WebDriver 설정 테스트...")
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    # ChromeDriver 경로 확인
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        driver_path = ChromeDriverManager().install()
        print(f"   ChromeDriver 경로: {driver_path}")
        
        # 파일 존재 확인
        if os.path.exists(driver_path):
            print(f"   ChromeDriver 파일 존재: {os.path.getsize(driver_path)} bytes")
        else:
            print("   ChromeDriver 파일이 존재하지 않습니다!")
            
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("   WebDriver 생성 성공")
        
    except Exception as e:
        print(f"   ChromeDriverManager 오류: {e}")
        print("   시스템 Chrome 사용 시도...")
        
        # 시스템 Chrome 사용
        driver = webdriver.Chrome(options=chrome_options)
        print("   시스템 Chrome WebDriver 생성 성공")
    
    print("\n5. 페이지 접속 테스트...")
    driver.get(config.BASE_URL)
    print(f"   페이지 제목: {driver.title}")
    print(f"   현재 URL: {driver.current_url}")
    
    # 페이지 소스 일부 확인
    page_source = driver.page_source[:200]
    print(f"   페이지 소스 일부: {page_source}")
    
    driver.quit()
    print("   WebDriver 종료 완료")
    
    print("\n✅ 모든 테스트 통과!")
    
except Exception as e:
    print(f"\n❌ 오류 발생: {e}")
    print(f"오류 타입: {type(e).__name__}")
    print("상세 오류 정보:")
    traceback.print_exc()
    sys.exit(1) 