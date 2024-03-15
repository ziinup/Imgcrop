import os
from PIL import Image
from collections import Counter
from tkinter import messagebox, Tk
import tkinter.filedialog as filedialog

def get_border_color(img):
    pixels = []
    width, height = img.size
    pixels.extend(img.getpixel((x, 0)) for x in range(width))
    pixels.extend(img.getpixel((x, height-1)) for x in range(width))
    pixels.extend(img.getpixel((0, y)) for y in range(height))
    pixels.extend(img.getpixel((width-1, y)) for y in range(height))
    most_common_color = Counter(pixels).most_common(1)[0][0]
    return most_common_color

def resize_image_with_padding(img_path, output_path, scale_factor=0.9, final_size=(960, 1280)):
    try:
        img = Image.open(img_path)
        border_color = get_border_color(img)
        
        # 원본 이미지를 80%로 축소
        new_width = int(img.size[0] * scale_factor)
        new_height = int(img.size[1] * scale_factor)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 축소된 이미지의 크기를 기반으로 최종 사이즈의 캔버스 생성
        final_img = Image.new("RGB", final_size, border_color)
        x_left = (final_size[0] - new_width) // 2
        y_top = (final_size[1] - new_height) // 2
        final_img.paste(img, (x_left, y_top))
        
        final_img.save(output_path)
    except Exception as e:
        messagebox.showerror("Error", f"Error processing {img_path}: {e}")


def process_images_in_folder(folder_path):
    print(f"Processing folder: {folder_path}")
    output_folder = os.path.join(folder_path, "output")
    print(f"Output folder: {output_folder}")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print("Output folder created.")
    
    for item in os.listdir(folder_path):
        print(f"Found file: {item}")
        if item.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            img_path = os.path.join(folder_path, item)
            output_path = os.path.join(output_folder, item)
            print(f"Processing image: {img_path}")
            resize_image_with_padding(img_path, output_path)
            print(f"Image processed: {output_path}")

    return len(os.listdir(output_folder))

def main():
    root = Tk()
    root.withdraw()  # Hide the main window
    folder_path = filedialog.askdirectory(title="Select Folder Containing Images")
    if not folder_path:
        messagebox.showinfo("Info", "No folder selected. Exiting.")
        return
    processed_count = process_images_in_folder(folder_path)
    messagebox.showinfo("Complete", f"Processed {processed_count} images and saved to 'output' folder.")

if __name__ == "__main__":
    main()
