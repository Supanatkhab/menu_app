import streamlit as st
import json
from PIL import Image

# โหลดข้อมูลเมนู
with open("menu.json", "r", encoding="utf-8") as f:
    menu = json.load(f)

st.set_page_config(page_title="เมนูอาหาร", layout="wide")

# หัวข้ออยู่ตรงกลาง
st.markdown("<h1 style='text-align: center;'>🍽️ เมนูอาหาร</h1>", unsafe_allow_html=True)

# ฟังก์ชันปรับขนาดภาพ
def resize_image(image_path, size=(300, 200)):
    img = Image.open(image_path)
    img = img.resize(size)
    return img

# แสดงเมนูแบบ Grid Responsive
cols = st.columns(3)

for i, item in enumerate(menu):
    with cols[i % 3]:
        img = resize_image(item["image"])
        st.image(img, use_container_width=False)
        st.markdown(f"**ชื่ออาหาร:** {item['name']}")
        st.markdown(f"**ราคา:** {item['price']} บาท")
        st.markdown(f"foodname: {item['foodname']}")
        st.markdown(f"price: {item['price']} ฿")
