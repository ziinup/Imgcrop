import tkinter as tk
from tkinter import filedialog
import json
import pandas as pd

def select_json_file():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        process_json(file_path)

def process_json(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Specify the columns to exclude
    columns_to_exclude = set([
        "cgbi_id", "cgbi_order", "total_qty", "is_delete", "cgbig_id",
        "cgb_id", "cde_id", "ins_dtm", "upd_dtm", "ins_user", "upd_user",
        "cmall_item_detail"
    ])

    combined_data = []
    for item in data:
        product_name = item.get('product_name', '')
        cgbi_detail = item.get('cgbi_detail', '')
        product_color = item.get('product_color', '')
        for sub_item in item.get('cmall_group_buying_item', []):
            # Exclude specified columns
            filtered_sub_item = {k: v for k, v in sub_item.items() if k not in columns_to_exclude}
            filtered_sub_item['product_name'] = product_name
            filtered_sub_item['cgbi_detail'] = cgbi_detail
            filtered_sub_item['product_color'] = product_color
            combined_data.append(filtered_sub_item)

    df_combined = pd.DataFrame(combined_data)
    excel_file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if excel_file_path:
        df_combined.to_excel(excel_file_path, index=False)
        tk.messagebox.showinfo("Success", "The Excel file has been created successfully.")

root = tk.Tk()
root.title("JSON to Excel Converter")

tk.Label(root, text="Select a JSON file to convert to Excel", padx=20, pady=20).pack()

select_button = tk.Button(root, text="Select JSON File", command=select_json_file, padx=10, pady=5)
select_button.pack(pady=20)

root.mainloop()
