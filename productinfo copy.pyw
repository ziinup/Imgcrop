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
from selenium.common.exceptions import StaleElementReferenceException

# 사용자로부터 URL 입력 받기
url = input("상품 목록이 있는 웹 페이지 URL을 입력하세요: ")
user_folder_name = input("저장할 폴더 이름을 입력하세요: ")

# DataFrame 초기화
productdf = pd.DataFrame(columns=['상품이미지', '상품URL', '상품명', '할인판매가', '판매가', '옵션1', '옵션2', '옵션3', '옵션4'])

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
            discount_price = product_wrapper.find_element(By.CLASS_NAME, 'productDiscountPriceSpan').text
        except NoSuchElementException:
            discount_price = ''  # 요소가 없는 경우 빈 문자열
        
        # 판매가 추출
        try:
            original_price = product_wrapper.find_element(By.CLASS_NAME, 'productPriceWithDiscountSpan').text
        except NoSuchElementException:
            original_price = ''  # 요소가 없는 경우 빈 문자열

        # 추출한 정보를 기반으로 DataFrame에 데이터 추가
        productdf = productdf._append({
            '상품이미지': image_urls, 
            '상품URL': product_url, 
            '상품명': product_name,
            '할인판매가': discount_price, 
            '판매가': original_price,
        }, ignore_index=True)

except Exception as e:
    print(f"Error: {e}")

finally:
    driver.quit()

def get_product_options(url):

    print('시작됨')

    driver.get(url)
    options = ['', '', '', '']
    try:
        # 모든 옵션 요소를 기다림
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'custom-select-wrapper'))
        )
        option_elements = driver.find_elements(By.CLASS_NAME, 'custom-select-wrapper')
        
        for i, option_element in enumerate(option_elements[:4]): # 최대 4개의 옵션만 처리
            try:
                option_name = option_element.find_element(By.CLASS_NAME, 'custom-select-option-name').text

                print(option_name)

                option_value = option_element.find_element(By.CLASS_NAME, 'custom-select-option-info').text
                print(option_value)

                options[i] = f'{option_name}: {option_value}'
            except StaleElementReferenceException:
                # 요소가 stale 되었을 경우, 재시도
                option_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'custom-select-wrapper'))
                )
                option_name = option_element.find_element(By.CLASS_NAME, 'custom-select-option-name').text
                option_value = option_element.find_element(By.CLASS_NAME, 'custom-select-option-info').text
                options[i] = f'{option_name}: {option_value}'
    except Exception as e:
        print(f"Error while processing options: {e}")
    return options

# 상품 URL에 대해 옵션 추출
for index, row in productdf.iterrows():
    if pd.notna(row['상품URL']):
        options = get_product_options(row['상품URL'])
        productdf.at[index, '옵션1'] = options[0]
        productdf.at[index, '옵션2'] = options[1]
        productdf.at[index, '옵션3'] = options[2]
        productdf.at[index, '옵션4'] = options[3]

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

# NaN 값이 포함된 행을 제외하고, 이미지 URL을 가진 행만 처리
for i, urls in enumerate(productdf['상품이미지'].dropna().str.split(', ')):
    # 여기서 urls는 이미지 URL 리스트입니다.
    for j, img_url in enumerate(urls):
        try:
            response = requests.get(img_url, timeout=10)  # timeout을 추가하여 요청 시간을 제한
            if response.status_code == 200:
                image_file_path = os.path.join(image_folder_path, f'product_{i}_{j}.jpg')
                with open(image_file_path, 'wb') as file:
                    file.write(response.content)
        except requests.RequestException as e:
            print(f"Error downloading {img_url}: {e}")