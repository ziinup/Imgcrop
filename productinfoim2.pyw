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
productdf = pd.DataFrame(columns=['상품이미지', '상품URL', '상품명', '할인판매가', '판매가'])

# WebDriver 설정
s = Service('D:\\chromedriver-win64\\chromedriver.exe')  # 크롬 드라이버 경로 수정 필요
driver = webdriver.Chrome(service=s)
driver.get(url)
time.sleep(5)  # 페이지 로드 대기

try:
    product_list_wrapper = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, '_item_wrap'))
    )
    shop_product_wrappers = product_list_wrapper.find_elements(By.CLASS_NAME, 'shop-item')
    for product_wrapper in shop_product_wrappers:
        try:
            image_url = product_wrapper.find_element(By.TAG_NAME, 'img').get_attribute('src')
        except NoSuchElementException:
            image_url = ''  # 이미지 URL이 없는 경우

        print(image_url)

        try:
            product_url = product_wrapper.find_element(By.TAG_NAME, 'a').get_attribute('href')
        except NoSuchElementException:
            product_url = ''  # 상품 URL이 없는 경우

        sec_target = product_wrapper.find_element(By.CLASS_NAME, 'item-detail')

        try:
            product_name = sec_target.find_element(By.TAG_NAME, 'h2').text
        except NoSuchElementException:
            product_name = ''  # 상품명이 없는 경우

        print(product_name)

        # 할인판매가와 판매가 추출
        try:
            pay_text = sec_target.find_element(By.CLASS_NAME, 'pay').text
            pay_price = re.sub(r'\D', '', pay_text)
        except NoSuchElementException:
            pay_price = ''  # pay 가격이 없는 경우

        try:
            original_price_text = sec_target.find_element(By.CLASS_NAME, 'sale_price').text
            original_price = re.sub(r'\D', '', original_price_text)
        except NoSuchElementException:
            original_price = pay_price  # sale_price가 없는 경우, pay 값을 판매가로 사용

        # 할인판매가와 판매가 결정
        discount_price = pay_price if original_price != pay_price else ''  # 판매가와 pay 가격이 다를 경우에만 할인판매가에 pay 값을 할당

        # DataFrame에 데이터 추가
        productdf = productdf._append({
            '상품이미지': image_url, 
            '상품URL': product_url, 
            '상품명': product_name,
            '할인판매가': discount_price, 
            '판매가': original_price
        }, ignore_index=True)

except Exception as e:
    print(f"Error: {e}")
finally:
    driver.quit()

# 기본 저장 경로 설정 및 폴더 생성
base_dir = 'D:\\extract'  # 기본 저장 경로 수정 필요
folder_path = os.path.join(base_dir, user_folder_name)
os.makedirs(folder_path, exist_ok=True)

# 엑셀 파일 경로 설정 및 저장
excel_file_path = os.path.join(folder_path, 'output.xlsx')
productdf.to_excel(excel_file_path, index=False)

# 이미지 저장 폴더 생성 및 이미지 다운로드
image_folder_path = os.path.join(folder_path, 'images')
os.makedirs(image_folder_path, exist_ok=True)

for i, img_url in enumerate(productdf['상품이미지']):
    if img_url:  # 이미지 URL이 존재하는 경우에만 다운로드
        response = requests.get(img_url)
        if response.status_code == 200:
            image_file_path = os.path.join(image_folder_path, f'product_{i}.jpg')
            with open(image_file_path, 'wb') as file:
                file.write(response.content)
