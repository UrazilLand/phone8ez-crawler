#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
스마트초이스 단말기 지원금 크롤러 실행 파일
실제 크롤링 작업을 수행하는 메인 스크립트입니다.
"""

import os
import sys
import time
from datetime import datetime
from smartchoice_crawler import SmartChoiceCrawler, logger

def print_banner():
    """배너 출력"""
    print("=" * 60)
    print("📱 스마트초이스 단말기 지원금 크롤러 v1.0.0")
    print("=" * 60)
    print("스마트초이스에서 휴대폰 단말기 지원금 정보를 수집합니다.")
    print("=" * 60)

def get_user_input():
    """사용자 입력 받기"""
    print("\n🔧 크롤링 설정")
    print("-" * 30)
    
    # 제조사 선택
    print("제조사 선택:")
    print("1. 삼성전자")
    print("2. 애플")
    print("3. 기타")
    
    while True:
        try:
            choice = input("제조사를 선택하세요 (1-3): ").strip()
            if choice == "1":
                manufacturer = "삼성전자"
                break
            elif choice == "2":
                manufacturer = "애플"
                break
            elif choice == "3":
                manufacturer = "기타"
                break
            else:
                print("❌ 잘못된 선택입니다. 1-3 중에서 선택하세요.")
        except KeyboardInterrupt:
            print("\n\n👋 프로그램을 종료합니다.")
            sys.exit(0)
    
    # 모델명 입력
    print(f"\n📱 {manufacturer} 모델명을 입력하세요.")
    print("예시: 갤럭시 S24, iPhone 15, 갤럭시 A55 등")
    
    while True:
        try:
            model_name = input("모델명: ").strip()
            if model_name:
                break
            else:
                print("❌ 모델명을 입력해주세요.")
        except KeyboardInterrupt:
            print("\n\n👋 프로그램을 종료합니다.")
            sys.exit(0)
    
    # 헤드리스 모드 선택
    print("\n🖥️ 브라우저 모드 선택:")
    print("1. 백그라운드 실행 (권장)")
    print("2. 브라우저 창 표시")
    
    while True:
        try:
            choice = input("모드를 선택하세요 (1-2): ").strip()
            if choice == "1":
                headless = True
                break
            elif choice == "2":
                headless = False
                break
            else:
                print("❌ 잘못된 선택입니다. 1-2 중에서 선택하세요.")
        except KeyboardInterrupt:
            print("\n\n👋 프로그램을 종료합니다.")
            sys.exit(0)
    
    return manufacturer, model_name, headless

def create_output_directory():
    """출력 디렉토리 생성"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"data/{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def main():
    """메인 함수"""
    try:
        # 배너 출력
        print_banner()
        
        # 사용자 입력 받기
        manufacturer, model_name, headless = get_user_input()
        
        # 출력 디렉토리 생성
        output_dir = create_output_directory()
        
        print(f"\n🚀 크롤링 시작...")
        print(f"제조사: {manufacturer}")
        print(f"모델명: {model_name}")
        print(f"출력 디렉토리: {output_dir}")
        print("-" * 40)
        
        # 크롤러 실행
        with SmartChoiceCrawler(headless=headless) as crawler:
            try:
                # 1. 페이지 접속
                print("📡 페이지 접속 중...")
                crawler.navigate_to_page()
                
                # 2. 제조사 선택
                print(f"🏭 {manufacturer} 선택 중...")
                crawler.select_manufacturer(manufacturer)
                
                # 3. 모델 선택
                print(f"📱 {model_name} 모델 선택 중...")
                if not crawler.select_model(model_name):
                    print(f"❌ 모델 '{model_name}'을 찾을 수 없습니다.")
                    print("💡 모델명을 정확히 입력했는지 확인해주세요.")
                    return
                
                # 4. 검색 실행
                print("🔍 지원금 정보 검색 중...")
                search_success = crawler.search_support_info()
                if not search_success:
                    print(f"❌ '{model_name}'에 대한 지원금 정보가 없습니다.")
                    return
                
                # 5. 데이터 추출
                print("📊 데이터 추출 중...")
                result = crawler.crawl_model_with_summary(manufacturer, model_name)
                
                if result:
                    # 6. 데이터 저장
                    print("💾 데이터 저장 중...")
                    
                    # 상세 데이터 저장
                    detailed_filename = os.path.join(output_dir, f"{model_name}_detailed.json")
                    with open(detailed_filename, 'w', encoding='utf-8') as f:
                        import json
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    
                    # 요약 데이터 저장
                    summary_filename = os.path.join(output_dir, f"{model_name}_summary.json")
                    crawler.save_summary_data([result], summary_filename)
                    
                    # CSV 저장
                    if result.get("carrier_plans"):
                        import pandas as pd
                        all_plans = []
                        for carrier, plans in result["carrier_plans"].items():
                            for plan in plans:
                                plan["carrier"] = carrier
                                plan["model_name"] = model_name
                                plan["manufacturer"] = manufacturer
                                all_plans.append(plan)
                        
                        if all_plans:
                            df = pd.DataFrame(all_plans)
                            csv_filename = os.path.join(output_dir, f"{model_name}_plans.csv")
                            df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
                    
                    print("✅ 크롤링 완료!")
                    print(f"📁 결과 파일 위치: {output_dir}")
                    
                    # 결과 요약 출력
                    if result.get("model_info"):
                        model_info = result["model_info"]
                        print(f"\n📋 모델 정보:")
                        print(f"   모델명: {model_info.get('model_name', 'N/A')}")
                        print(f"   최대 출고가: {model_info.get('max_price', 'N/A')}")
                    
                    if result.get("carrier_plans"):
                        print(f"\n📊 통신사별 요금제:")
                        for carrier, plans in result["carrier_plans"].items():
                            print(f"   {carrier}: {len(plans)}개 요금제")
                
                else:
                    print("❌ 데이터 추출에 실패했습니다.")
                
            except Exception as e:
                logger.error(f"크롤링 중 오류 발생: {e}")
                print(f"❌ 오류가 발생했습니다: {e}")
        
    except KeyboardInterrupt:
        print("\n\n👋 사용자가 프로그램을 중단했습니다.")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류가 발생했습니다: {e}")
        logger.error(f"예상치 못한 오류: {e}")

if __name__ == "__main__":
    main() 