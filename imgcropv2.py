import os
from PIL import Image
import glob
from tkinter import Tk, messagebox, simpledialog
from tkinter.filedialog import askdirectory

def get_image_alignment(root):
    """
    사용자에게 이미지 정렬 방식을 입력받습니다.
    """
    alignment = simpledialog.askstring("Image Alignment", 
                                       "Enter alignment for vertical images (top, center, bottom):",
                                       parent=root)
    # 입력 검증
    if alignment not in ['top', 'center', 'bottom']:
        messagebox.showwarning("Warning", "Invalid alignment selected. Defaulting to 'center'.")
        alignment = 'center'
    return alignment

def process_image(image_path, output_directory, alignment, background_color=(0, 0, 0)):
    with Image.open(image_path) as img:
        width, height = img.size
        img_ratio = width / height
        base_filename = os.path.splitext(os.path.basename(image_path))[0]

        # 세로형 이미지 처리
        if height > width:
            target_width = 1000
            target_height = 1310
            
            # 1-a 및 1-b 조건에 따른 처리 로직
            if img_ratio > 1/1.31:  # 1-a 조건
                new_height = 1310
            else:  # 1-b 조건
                new_height = int(target_width / img_ratio)
                
            new_width = int(new_height * img_ratio)
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            if new_width > target_width:
                # 가로 길이 조정 필요
                if alignment == 'center':
                    left = (new_width - target_width) // 2
                elif alignment == 'bottom':
                    left = new_width - target_width
                else:  # top or default
                    left = 0
                right = left + target_width
                img_final = img_resized.crop((left, 0, right, new_height))
            elif new_height > target_height:
                # 세로 길이 조정 필요
                if alignment == 'center':
                    top = (new_height - target_height) // 2
                elif alignment == 'bottom':
                    top = new_height - target_height
                else:  # top or default
                    top = 0
                bottom = top + target_height
                img_final = img_resized.crop((0, top, new_width, bottom))
            else:
                img_final = img_resized

            img_final.save(os.path.join(output_directory, f"{base_filename}.jpg"), quality=95)
        
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

    alignment = get_image_alignment(root)  # 정렬 방식 선택

    image_directory = askdirectory(title='Select Image Directory', parent=root)
    if not image_directory:
        messagebox.showinfo("Information", "No directory selected, exiting...", parent=root)
        root.destroy()
        return

    output_directory = os.path.join(image_directory, "output")
    os.makedirs(output_directory, exist_ok=True)

    processed_files = 0  # 처리된 파일 수를 세는 변수
    for image_path in glob.glob(os.path.join(image_directory, '*.jpg')):
        process_image(image_path, output_directory, alignment)
        processed_files += 1  # 이미지를 처리할 때마다 카운트 증가

    # 처리된 이미지 파일의 총 수를 사용자에게 알림
    messagebox.showinfo("Complete", f"Image processing complete. Total: {processed_files} files.", parent=root)
    root.destroy()

if __name__ == "__main__":
    main()