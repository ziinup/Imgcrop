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
productdf = pd.DataFrame(columns=['상품이미지', '상품URL', '상품명', '할인판매가', '판매가', '옵션1', '옵션2', '옵션3', '옵션4'])

# 새 User-Agent 문자열을 설정합니다. 이 예에서는 Windows 10에서 Chrome 88을 사용하는 것처럼 보이게 설정했습니다.
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"

# WebDriver 설정
s = Service('D:\\chromedriver-win64\\chromedriver.exe')
driver = webdriver.Chrome(service=s)
driver.get(url)
time.sleep(5)

try:
    product_list_wrapper = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'productListWrapper'))
    )
    shop_product_wrappers = product_list_wrapper.find_elements(By.CLASS_NAME, 'shopProductWrapper')

    for product_wrapper in shop_product_wrappers:
        # 상품 이미지 URL 추출 (첫 번째 요소만)
        images = product_wrapper.find_elements(By.CSS_SELECTOR, '.thumbDiv .thumb.img')
        if images:  # 이미지가 존재하는지 확인
            first_image_url = images[0].get_attribute('imgsrc')  # 첫 번째 이미지의 URL 추출
            image_urls = [first_image_url]  # 리스트로 변환하여 처리
        else:
            image_urls = []  # 이미지가 없는 경우 빈 리스트 할당
        
        print(image_urls)
        
       # 상품 URL 추출
        try:
            product_url = product_wrapper.find_element(By.TAG_NAME, 'a').get_attribute('href')
        except NoSuchElementException:
            product_url = ''  # 요소가 없는 경우 빈 문자열
        
        # 상품명 추출
        try:
            product_name = product_wrapper.find_element(By.CLASS_NAME, 'productName').text
        except NoSuchElementException:
            product_name = ''  # 요소가 없는 경우 빈 문자열
        
        print(product_name)
        
        # 할인판매가 추출
        try:
            discount_price_text = product_wrapper.find_element(By.CLASS_NAME, 'productDiscountPriceSpan').text
            # 숫자만 추출
            discount_price = re.sub(r'\D', '', discount_price_text)
        except NoSuchElementException:
            discount_price = ''  # 요소가 없는 경우 빈 문자열

        # 판매가 추출
        try:
            original_price_text = product_wrapper.find_element(By.CLASS_NAME, 'productPriceWithDiscountSpan').text
            # 숫자만 추출
            original_price = re.sub(r'\D', '', original_price_text)
        except NoSuchElementException:
            original_price = ''  # 요소가 없는 경우 빈 문자열
        
        # DataFrame에 데이터 추가
        productdf = productdf._append({
            '상품이미지': ', '.join(image_urls), 
            '상품URL': product_url, 
            '상품명': product_name,
            '할인판매가': discount_price, 
            '판매가': original_price
        }, ignore_index=True)

except Exception as e:
    print(f"Error: {e}")

finally:
    driver.quit()

# 상품별 옵션 정보 추출
for index, row in productdf.iterrows():
    # WebDriver 설정
    s = Service('D:\\chromedriver-win64\\chromedriver.exe')
    driver = webdriver.Chrome(service=s)
    driver.get(row['상품URL'])
    time.sleep(5)  # 상품 페이지 로딩 대기
    
    options = []
    for i in range(1, 5):  # 최대 4개의 옵션
        try:

            option_wrapper = driver.find_element(By.CLASS_NAME,'shopProductOptionListDiv')

            # 옵션 이름 추출
            option_name = option_wrapper.find_element(By.CSS_SELECTOR, f'.productOption.custom-select-wrapper:nth-of-type({i}) .custom-select-option-name').text

            # 해당 옵션에 대한 모든 'custom-select-option-info' 요소 추출
            option_values_elements = option_wrapper.find_elements(By.CSS_SELECTOR, f'.productOption.custom-select-wrapper:nth-of-type({i}) .custom-select-option-info')

            # 각 요소의 텍스트 추출 후 리스트에 저장
            option_values = [element.get_attribute('innerText').strip() for element in option_values_elements]

            # 모든 옵션 값들을 쉼표로 구분하여 하나의 문자열로 결합
            option_values_str = ', '.join(option_values)

            # 옵션 이름과 결합된 옵션 값들을 저장
            options.append(f"{option_name}: {option_values_str}")
            
            print(option_values_str)
            
        except NoSuchElementException:
            options.append('')
    
    # 옵션 데이터를 DataFrame에 추가
    for j, option in enumerate(options):
        print(j)
        productdf.at[index, f'옵션{j+1}'] = option

driver.quit()

# 기본 저장 경로 설정
base_dir = 'D:\\extract'
folder_path = os.path.join(base_dir, user_folder_name)

# 입력받은 폴더 이름으로 새로운 폴더 생성
os.makedirs(folder_path, exist_ok=True)

# 엑셀 파일 경로 설정
excel_file_path = os.path.join(folder_path, 'output.xlsx')

# DataFrame을 엑셀 파일로 저장
productdf.to_excel(excel_file_path, index=False)

# 이미지 저장 폴더 생성
image_folder_path = os.path.join(folder_path, 'images')
os.makedirs(image_folder_path, exist_ok=True)

# 이미지 다운로드 및 저장
for i, url in enumerate(productdf['상품이미지'].str.split(', ')):
    for j, img_url in enumerate(url):
        response = requests.get(img_url)
        if response.status_code == 200:
            image_file_path = os.path.join(image_folder_path, f'product_{i}_{j}.jpg')
            with open(image_file_path, 'wb') as file:
                file.write(response.content)
