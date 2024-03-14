#특정 폴더에 오늘 날짜에 이름을 입력하여 폴더 생성후, 폴더 열기

import os
import datetime
import tkinter as tk
from tkinter import simpledialog, filedialog
import configparser

# 설정 파일 로드 및 저장 함수
def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config.get('Settings', 'folder_path', fallback=os.path.expanduser("~"))

def save_config(folder_path):
    config = configparser.ConfigParser()
    config['Settings'] = {'folder_path': folder_path}
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

# 사용자 정의 대화 상자 클래스
class CustomDialog(simpledialog.Dialog):
    def body(self, master):
        self.title("폴더 이름과 경로 설정")
        tk.Label(master, text="폴더 이름:").grid(row=0)
        self.entry = tk.Entry(master)
        self.entry.grid(row=0, column=1)
        self.folder_path = load_config()
        tk.Button(master, text="경로 변경", command=self.change_folder_path).grid(row=1, columnspan=2)
        return self.entry

    def change_folder_path(self):
        new_path = filedialog.askdirectory(initialdir=self.folder_path, title="폴더 생성 경로 선택")
        if new_path:
            self.folder_path = new_path

    def apply(self):
        self.result = self.entry.get(), self.folder_path

# 폴더 생성 및 경로 변경 기능
def create_folder_with_custom_dialog():
    root = tk.Tk()
    root.withdraw()  # 메인 창을 숨김
    dialog = CustomDialog(root)
    if dialog.result:
        folder_name, folder_path = dialog.result
        if folder_name:
            date_str = datetime.datetime.now().strftime("%y%m%d_")
            full_path = os.path.join(folder_path, date_str + folder_name)
            if not os.path.exists(full_path):
                os.makedirs(full_path)
                print(f"폴더 '{full_path}'가 생성되었습니다.")
                os.startfile(full_path)
                save_config(folder_path)  # 새 경로 저장
            else:
                print(f"폴더 '{full_path}'는 이미 존재합니다.")
                os.startfile(full_path)

if __name__ == "__main__":
    create_folder_with_custom_dialog()
