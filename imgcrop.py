import os
from PIL import Image

def resize_and_crop(image_path, output_path, target_size=(1000, 1310), background_color=(0, 0, 0)):
    with Image.open(image_path) as img:
        # 원본 이미지의 가로 사이즈를 target_size[0]에 맞추고 비율에 따라 세로 사이즈 조정
        ratio = target_size[0] / img.width
        new_height = int(img.height * ratio)
        img_resized = img.resize((target_size[0], new_height), Image.Resampling.LANCZOS)

        if new_height > target_size[1]:
            # 세로 크기가 1310픽셀을 넘으면 중앙 부분을 유지하면서 잘라냄
            top = (new_height - target_size[1]) // 2
            bottom = top + target_size[1]
            img_cropped = img_resized.crop((0, top, target_size[0], bottom))
        else:
            # 세로 사이즈가 1310픽셀 이하인 경우, 상하에 검정색 배경 추가
            img_cropped = Image.new("RGB", target_size, background_color)
            y1 = (target_size[1] - new_height) // 2
            img_cropped.paste(img_resized, (0, y1))

        # 출력 디렉토리가 존재하는지 확인하고, 없으면 생성
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # 결과 이미지 저장
        img_cropped.save(output_path, quality=95)

# 예제 사용
image_directory = 'D:\\작업\\240216_PLZPROJECT 룩북 등록\\plz24ss'
output_directory = image_directory + '\\output'
import glob

# 해당 디렉토리의 모든 JPG 파일에 대해 처리
for image_path in glob.glob(image_directory + '\\*.jpg'):
    # 출력 파일 경로 생성
    filename = os.path.basename(image_path)
    output_path = os.path.join(output_directory, filename)
    
    # 리사이즈 및 필요에 따라 이미지 크롭 함수 호출
    resize_and_crop(image_path, output_path)

print("모든 이미지 처리가 완료되었습니다.")
