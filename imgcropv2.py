import os
from PIL import Image
import glob
from tkinter import Tk, messagebox
from tkinter.filedialog import askdirectory

def process_image(image_path, output_directory, background_color=(0, 0, 0)):
     with Image.open(image_path) as img:
        original_width, original_height = img.size
        base_filename = os.path.splitext(os.path.basename(image_path))[0]

        # 원본 이미지의 가로 대 세로 비율을 계산
        img_ratio = original_width / original_height

        # 세로형 이미지 처리
        if original_height > original_width:
            target_width = 1000
            resized_height = int(target_width / img_ratio)
            
            img_resized = img.resize((target_width, resized_height), Image.Resampling.LANCZOS)

            # 세로 길이에 따라 처리
            if resized_height <= 1310:
                # 이미지 전체를 확대하여 세로 길이를 1310px에 맞추기
                # 여기서 img_ratio 재정의가 필요 없으므로, 해당 라인을 제거하고 진행합니다.
                scale_factor = 1310 / resized_height
                new_width = int(target_width * scale_factor)
                new_height = 1310

                img_scaled = img_resized.resize((new_width, new_height), Image.Resampling.LANCZOS)
                # 가로 길이가 1000px 초과 시 중앙에서 잘라내기
                if new_width > 1000:
                    crop_start_x = (new_width - 1000) // 2
                    img_final = img_scaled.crop((crop_start_x, 0, crop_start_x + 1000, new_height))
                else:
                    img_final = img_scaled
                
                img_final.save(os.path.join(output_directory, f"{base_filename}_resized.jpg"), quality=95)
            else:
                # 세로 길이가 1310px 이상인 경우, 상단/중앙/하단 정렬로 이미지 저장
                alignments = ['top', 'center', 'bottom']
                for alignment in alignments:
                    crop_start_y = 0
                    if alignment == 'center':
                        crop_start_y = (resized_height - 1310) // 2
                    elif alignment == 'bottom':
                        crop_start_y = resized_height - 1310

                    img_cropped = img_resized.crop((0, crop_start_y, target_width, crop_start_y + 1310))
                    img_cropped.save(os.path.join(output_directory, f"{base_filename}_{alignment}.jpg"), quality=95)
                    
        # 가로형 이미지 처리
        else:
            new_width = 2000
            new_height = int(new_width / img_ratio)
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            if new_height > 1310:
                top = (new_height - 1310) // 2
                bottom = top + 1310
                img_cropped = img_resized.crop((0, top, new_width, bottom))
            else:
                img_cropped = Image.new("RGB", (new_width, 1310), background_color)
                y1 = (1310 - new_height) // 2
                img_cropped.paste(img_resized, (0, y1))

            # 가로 2000px 이미지를 1000px 기준으로 두 부분으로 나누어 각각 저장
            left_part = img_cropped.crop((0, 0, 1000, 1310))
            right_part = img_cropped.crop((1000, 0, 2000, 1310))

            left_part.save(os.path.join(output_directory, f"{base_filename}_left.jpg"), quality=95)
            right_part.save(os.path.join(output_directory, f"{base_filename}_right.jpg"), quality=95)

def main():
    root = Tk()
    root.withdraw()  # 메인 윈도우 숨기기

    # 사용자 정렬 선택 과정 생략 - 모든 정렬 옵션을 자동으로 적용

    image_directory = askdirectory(title='Select Image Directory', parent=root)
    if not image_directory:
        messagebox.showinfo("Information", "No directory selected, exiting...", parent=root)
        root.destroy()
        return

    output_directory = os.path.join(image_directory, "output")
    os.makedirs(output_directory, exist_ok=True)

    processed_files = 0
    for image_path in glob.glob(os.path.join(image_directory, '*.jpg')):
        process_image(image_path, output_directory)
        processed_files += 3  # 각 이미지당 세 가지 정렬 옵션 적용

    messagebox.showinfo("Complete", f"Image processing complete. Total: {processed_files} images processed with top, center, and bottom alignments.", parent=root)
    root.destroy()

if __name__ == "__main__":
    main()