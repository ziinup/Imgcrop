#MAC에서 받은 파일명이 인코딩으로 인해 깨졌을때, 다시 인코딩 하여 제대로 표시해주는 프로그램

import os
import unicodedata
import tkinter as tk
from tkinter import filedialog
import logging
from datetime import datetime

def setup_logging(folder_path):
    # 현재 시간을 가져와서 문자열 형태로 포맷합니다.
    current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
    # 선택한 폴더명을 추출합니다.
    folder_name = os.path.basename(os.path.normpath(folder_path))
    # 로그 파일 이름을 설정합니다.
    log_filename = f"{current_time}_{folder_name}.log"
    # 로그 설정
    logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    # 로그 파일 경로를 반환하여 나중에 사용할 수 있도록 합니다.
    return os.path.abspath(log_filename)

def normalize_string(s):
    return unicodedata.normalize('NFC', s)

def rename_files_in_directory(directory):
    for root, dirs, files in os.walk(directory, topdown=False):
        for items in [files, dirs]:
            for name in items:
                normalized_name = normalize_string(name)
                if name != normalized_name:
                    original_path = os.path.join(root, name)
                    new_path = os.path.join(root, normalized_name)
                    os.rename(original_path, new_path)
                    logging.info(f'Renamed: {original_path} -> {new_path}')

def select_folder():
    root = tk.Tk()
    root.withdraw()  # Tkinter 창을 숨김
    folder_selected = filedialog.askdirectory()  # 폴더 선택 대화상자를 열고 사용자가 선택한 폴더의 경로를 반환
    return folder_selected

if __name__ == "__main__":
    base_directory = select_folder()
    if base_directory:  # 사용자가 폴더를 선택한 경우
        log_file_path = setup_logging(base_directory)
        rename_files_in_directory(base_directory)
        logging.info(f"Completed renaming files and directories. Log file: {log_file_path}")
    else:
        print("No folder selected. Exiting.")
