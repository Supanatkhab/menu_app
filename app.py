import streamlit as st
import json
from PIL import Image
import base64
from io import BytesIO

# โหลดข้อมูลจาก JSON
with open("menu.json", "r", encoding="utf-8") as f:
    menu = json.load(f)

# ฟังก์ชันสำหรับแปลงรูปภาพเป็น base64
def img_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

# หัวข้อหลัก
st.markdown("<h1 style='text-align: center;'>🍽️ เมนูอาหาร / Menu</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>ร้าน Midwinter Khaoyai</h3>", unsafe_allow_html=True)

# CSS สำหรับ Responsive Design
st.markdown("""
<style>
/* Style สำหรับหน้าจอทั่วไป (Desktop) */
.menu-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: #262730;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
}
.menu-card-reverse {
    flex-direction: row-reverse;
}
.menu-card img {
    width: 300px;
    height: 200px;
    object-fit: cover;
    border-radius: 8px;
}
.menu-card-text {
    flex: 1;
    padding: 0 20px;
    text-align: center;
}
.menu-card-text p {
    margin: 0;
    line-height: 1.5;
}
.food-name {
    font-size: 28px !important; /* เพิ่ม !important ตรงนี้ */
    font-weight: bold;
    color: #F8F9FA;
    margin-bottom: 5px;
}
.price {
    font-size: 20px !important; /* เพิ่ม !important ตรงนี้ */
    color: #F8F9FA;
    margin-bottom: 5px;
}

/* --- Media Queries สำหรับหน้าจอมือถือ --- */
@media (max-width: 600px) {
    .menu-card, .menu-card-reverse {
        flex-direction: column; /* เปลี่ยนเป็นแนวตั้ง */
        text-align: center; /* จัดข้อความกึ่งกลาง */
    }
    .menu-card img {
        width: 100%; /* ทำให้รูปภาพเต็มความกว้างของหน้าจอ */
        height: auto; /* รักษาอัตราส่วน */
        margin-bottom: 15px; /* เพิ่มระยะห่างด้านล่างรูปภาพ */
    }
    .menu-card-text {
        padding: 0;
    }
}
</style>
""", unsafe_allow_html=True)

# แสดงเมนูอาหาร
for i, item in enumerate(menu):
    img = Image.open(item["image"])
    img_base64 = img_to_base64(img)

    card_class = "menu-card"
    if i % 2 != 0:
        card_class += " menu-card-reverse"

    html_content = f"""
    <div class="{card_class}">
        <img src="data:image/jpeg;base64,{img_base64}" />
        <div class="menu-card-text">
            <p class="food-name">{item['name']}</p>
            <p class="price "><i>price:</i> {item['price']} ฿</p>
        </div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)

st.markdown("---")