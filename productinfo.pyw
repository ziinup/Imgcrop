import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import os
import time

# DataFrame 초기화
productdf = pd.DataFrame(columns=['상품이미지', '상품URL', '상품명', '할인판매가', '판매가'])

# WebDriver 설정
s = Service('D:\\chromedriver-win64\\chromedriver.exe')
driver = webdriver.Chrome(service=s)
driver.get('https://www.320sroom.com/new_arrivals?productListFilter=965862&productSortFilter=PRODUCT_ORDER_NO')
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
        product_url = product_wrapper.find_element(By.TAG_NAME, 'a').get_attribute('href')
        print(product_url)

        # 상품명 추출
        product_name = product_wrapper.find_element(By.CLASS_NAME, 'productName').text
        print(product_name)
        
        # 할인판매가 추출
        discount_price = product_wrapper.find_element(By.CLASS_NAME, 'productDiscountPriceSpan').text
        print(discount_price)
        
        # 판매가 추출
        original_price = product_wrapper.find_element(By.CLASS_NAME, 'productPriceWithDiscountSpan').text
        print(original_price)
        
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

# DataFrame을 엑셀 파일로 저장
excel_path = 'D:\\extract\\'
productdf.to_excel(excel_path+'output.xlsx', index=False)

# 이미지를 저장할 폴더 경로 수정
image_folder_base = os.path.dirname(excel_path)  # 엑셀 파일이 위치한 폴더의 경로를 가져옵니다.
image_folder = os.path.join(image_folder_base, 'images')  # 'images' 폴더의 전체 경로를 구성합니다.

# 폴더가 없으면 만들어줍니다.
os.makedirs(image_folder, exist_ok=True)

# 이미지 다운로드 및 저장
for i, url in enumerate(productdf['상품이미지'].str.split(', ')):
    for j, img_url in enumerate(url):
        response = requests.get(img_url)
        if response.status_code == 200:
            with open(os.path.join(image_folder, f'product_{i}_{j}.jpg'), 'wb') as file:
                file.write(response.content)
