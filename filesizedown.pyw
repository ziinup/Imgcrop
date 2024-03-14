#폴더 내에 모든 이미지를 순회하며, 1MB가 넘는 이미지의 퀄리티를 85로 줄입니다.

import os
from tkinter import Tk, filedialog
from PIL import Image

def resize_images_in_folder(folder_path, quality=85, size_limit=1048576):
    # folder_path 내의 모든 파일에 대해 반복
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            try:
                # 파일 경로 결합
                file_path = os.path.join(root, file)
                # 파일이 이미지인지 확인
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    # 이미지 열기
                    with Image.open(file_path) as img:
                        # 파일 크기가 1MB 이상인지 확인
                        if os.path.getsize(file_path) > size_limit:
                            # 이미지 품질을 줄임
                            img.save(file_path, quality=quality, optimize=True)
                            print(f'Resized {file_path}')
            except Exception as e:
                print(f'Error processing {file}: {e}')

def select_folder():
    root = Tk()
    root.withdraw()  # Tk 창 숨김
    folder_selected = filedialog.askdirectory()  # 폴더 선택 대화상자
    return folder_selected

if __name__ == "__main__":
    folder = select_folder()
    if folder:
        resize_images_in_folder(folder)
        print("Image resizing complete.")
    else:
        print("No folder selected.")
