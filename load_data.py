from dotenv import load_dotenv
from pathlib import Path
import os
import pyodbc
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
env_file = BASE_DIR / ".env"
load_dotenv(env_file)

def get_data(DB,query):
    conn = pyodbc.connect(
        'DRIVER={SQL Server};'
        f'SERVER={os.getenv("SERVER")};'
        f'DATABASE={DB};'
        f'UID={os.getenv("UID")};'
        f'PWD={os.getenv("PASSWORD")}'
    )
    df = pd.read_sql(query, conn)
    conn.close()
    return df
#######
# import streamlit as st
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# import time

# # Hàm tự động đăng nhập
# def auto_login(url, username, password):
#     # Cấu hình trình duyệt
#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless')  # Nếu muốn chạy nền (không hiển thị trình duyệt), bỏ dòng này nếu cần debug
#     options.add_argument('--disable-gpu')
#     options.add_argument('--no-sandbox')

#     # Tạo đối tượng driver
#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

#     try:
#         # Mở trang web
#         driver.get(url)
#         time.sleep(2)  # Đợi trang tải xong

#         # Điền thông tin đăng nhập
#         driver.find_element(By.NAME, 'loginUsername-inputEl').send_keys(username)  # Thay 'username' bằng ID/NAME của trường input
#         driver.find_element(By.NAME, 'loginPassword-inputEl').send_keys(password)  # Thay 'password' bằng ID/NAME của trường input

#         # Bấm nút đăng nhập
#         driver.find_element(By.ID, 'loginButton-btnIconEl').click()  # Thay 'login-button' bằng ID của nút
#         time.sleep(3)

#         # Trả về URL sau khi đăng nhập thành công
#         return driver.current_url

#     except Exception as e:
#         return str(e)

#     finally:
#         driver.quit()
