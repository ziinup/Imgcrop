import cv2
import numpy as np
import os
from tkinter import filedialog
from tkinter import Tk

def apply_horizontal_gradient(image, width=1000):
    height, original_width = image.shape[:2]
    new_image = np.zeros((height, width, 3), dtype=np.uint8)  # 새 이미지 초기화

    # 중앙에 이미지를 배치할 시작점 계산
    center_start = (width - original_width) // 2

    if center_start >= 0:
        # 원본 이미지가 새 이미지보다 작거나 같은 경우, 원본 이미지를 중앙에 배치
        new_image[:, center_start:center_start+original_width] = image
    else:
        # 원본 이미지가 새 이미지보다 큰 경우, 원본 이미지의 중앙 부분을 잘라서 새 이미지에 맞춤
        crop_start = -center_start
        new_image = image[:, crop_start:crop_start + width]

    return new_image

def process_folder(folder_path, output_folder):
    processed_count = 0

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            img_path = os.path.join(folder_path, filename).replace('\\', '/')
            print(f"Attempting to load: {img_path}")  # 디버깅을 위해 경로 출력
            if not os.path.exists(img_path):
                print(f"File does not exist: {img_path}")
                continue

            image = cv2.imread(img_path)
            if image is None:
                print(f"Failed to load: {img_path}")
            else:
                if image is not None:
                    processed_image = apply_horizontal_gradient(image)
                    cv2.imwrite(os.path.join(output_folder, filename), processed_image)
                    processed_count += 1

    return processed_count

def main():
    root = Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory()

    if folder_selected:
        output_folder = os.path.join(folder_selected, "output")
        processed_count = process_folder(folder_selected, output_folder)
        print(f"{processed_count} images have been processed.")
    else:
        print("No folder selected.")

if __name__ == "__main__":
    main()
