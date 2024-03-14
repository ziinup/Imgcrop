#카페24 상품 크롤링

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import os
import time
from selenium.common.exceptions import NoSuchElementException
import re

# 사용자로부터 URL 입력 받기
url = input("상품 목록이 있는 웹 페이지 URL을 입력하세요: ")
user_folder_name = input("저장할 폴더 이름을 입력하세요: ")

# DataFrame 초기화
productdf = pd.DataFrame(columns=['상품명', '상품이미지', '상품URL', '판매가', '할인판매가', '옵션1', '옵션2', '옵션3', '옵션4'])

# 새 User-Agent 문자열을 설정합니다. 이 예에서는 Windows 10에서 Chrome 88을 사용하는 것처럼 보이게 설정했습니다.
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"

# WebDriver 설정
s = Service('D:\\chromedriver-win64\\chromedriver.exe')
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36")
driver = webdriver.Chrome(service=s, options=chrome_options)

driver.get(url)
time.sleep(5)

try:
    product_list_wrapper = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'prdList'))
    )
    shop_product_wrappers = product_list_wrapper.find_elements(By.CLASS_NAME, 'item')

    for product_wrapper in shop_product_wrappers:
        # 상품명 추출
        try:
            product_name = product_wrapper.find_element(By.CLASS_NAME, 'name').text
        except NoSuchElementException:
            product_name = ''  # 요소가 없는 경우 빈 문자열
        
        print(product_name)

        # 상품 이미지 URL 추출 (첫 번째 요소만)
        image_element = product_wrapper.find_element(By.CSS_SELECTOR, '.thumb-box .thumb')
        if image_element:  # 이미지가 존재하는지 확인
            image_urls = image_element.get_attribute('src')  # 첫 번째 이미지의 URL 추출
        else:
            image_urls = ""  # 이미지가 없는 경우 빈 문자열 할당
        
        print(image_urls)
        
       # 상품 URL 추출
        try:
            product_url = product_wrapper.find_element(By.TAG_NAME, 'a').get_attribute('href')
        except NoSuchElementException:
            product_url = ''  # 요소가 없는 경우 빈 문자열
        
        prices_list = product_wrapper.find_elements(By.CSS_SELECTOR, '.xans-product-listitem li')

        # 판매가 추출
        original_price = ''  # 초기값 설정
        if len(prices_list) > 0:
            original_price_text = prices_list[0].text
            original_price = re.sub(r'\D', '', original_price_text)
        
        # 할인판매가 추출
        discount_price = ''  # 초기값 설정
        if len(prices_list) > 1:
            discount_price_text = prices_list[1].text
            discount_price = re.sub(r'\D', '', discount_price_text)
        
        # DataFrame에 데이터 추가
        productdf = productdf._append({
            '상품명': product_name,
            '상품이미지': image_urls, 
            '상품URL': product_url, 
            '할인판매가': discount_price, 
            '판매가': original_price
        }, ignore_index=True)

except Exception as e:
    print(f"Error: {e}")

finally:
    driver.quit()

# 상품별 옵션 정보 추출을 위한 별도의 WebDriver 인스턴스 생성
for index, row in productdf.iterrows():
    s = Service('D:\\chromedriver-win64\\chromedriver.exe')
    driver = webdriver.Chrome(service=s)
    
    driver.get(row['상품URL'])
    time.sleep(3)  # 상품 페이지 로딩 대기
    
    # 'ul.ec-product-button' 요소 내의 모든 'li' 요소를 찾아서 각각의 텍스트를 추출
    try:
        options_list = driver.find_element(By.CSS_SELECTOR, 'ul.ec-product-button')
        options_items = options_list.find_elements(By.TAG_NAME, 'li')
        
        options_texts = []
        for item in options_items:
            option_text = item.get_attribute('innerText').strip()
            options_texts.append(option_text)
        
        # 옵션 텍스트를 쉼표로 구분하여 하나의 문자열로 결합
        options_str = ', '.join(options_texts)
        
        # 결합된 옵션 문자열을 DataFrame에 저장
        productdf.at[index, '옵션1'] = options_str
        
    except NoSuchElementException:
        # 옵션이 없는 경우 빈 문자열 저장
        productdf.at[index, '옵션1'] = ''

driver.quit()

# 기본 저장 경로 설정
base_dir = 'D:\\extract'
folder_path = os.path.join(base_dir, user_folder_name)

# 입력받은 폴더 이름으로 새로운 폴더 생성
os.makedirs(folder_path, exist_ok=True)

# 엑셀 파일 기본 이름 설정 (폴더명 + "crawling")
base_file_name = f"{user_folder_name}crawling"

# 파일명에 추가할 숫자 초기화
file_number = 0

# 최종 파일 경로 설정 (동일한 이름이 있을 경우 숫자 추가)
while True:
    if file_number == 0:
        final_file_name = f"{base_file_name}.xlsx"
    else:
        final_file_name = f"{base_file_name}_{file_number}.xlsx"
    
    final_file_path = os.path.join(folder_path, final_file_name)
    
    # 파일이 존재하는지 확인
    if not os.path.exists(final_file_path):
        break  # 해당 파일명이 존재하지 않으면 루프 탈출
    file_number += 1  # 파일명이 존재하면 숫자를 1 증가

# DataFrame을 엑셀 파일로 저장
productdf.to_excel(final_file_path, index=False)

print(f"파일이 저장되었습니다: {final_file_path}")

# 이미지 저장 폴더 생성
image_folder_path = os.path.join(folder_path, 'images')
os.makedirs(image_folder_path, exist_ok=True)

# 이미지 다운로드 및 저장
for i, urls_string in enumerate(productdf['상품이미지']):
    urls = urls_string.split(', ')
    print(urls)
    for img_url in urls:
        # URL이 유효한지 확인
        if not img_url.startswith(('http://', 'https://')):
            print(f"잘못된 URL 형식을 감지: {img_url}")
            continue  # 잘못된 URL 형식인 경우 다음 URL로 넘어감

        # URL의 마지막 슬래시("/") 이후 모든 부분을 파일 이름으로 사용
        file_name = img_url.split('/')[-1]

        print(file_name)

        # 이미지 파일 경로 생성
        image_file_path = os.path.join(image_folder_path, file_name)

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
            response = requests.get(img_url, headers=headers)
            if response.status_code == 200:
                with open(image_file_path, 'wb') as file:
                    file.write(response.content)
            time.sleep(2)

        except PermissionError:
            print(f"권한 오류: {image_file_path} 파일에 쓸 수 없습니다.")

        except requests.exceptions.RequestException as e:
            print(f"URL 요청 중 오류 발생: {img_url} -> {e}")