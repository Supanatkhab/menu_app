import streamlit as st
import json
import sqlite3
import pandas as pd
import uuid
from io import BytesIO
import base64
from PIL import Image

# --- Initializing the database on app start ---
def init_db():
    """สร้างฐานข้อมูลและตารางถ้ายังไม่มี"""
    conn = sqlite3.connect("menu.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            image_data TEXT
        )
    """)
    conn.commit()
    conn.close()

# Ensure the database and table are created on every app start
init_db()

# --- Functions for Database Management ---
def load_menu_data_from_db():
    """โหลดข้อมูลทั้งหมดจากฐานข้อมูล"""
    conn = sqlite3.connect("menu.db")
    df = pd.read_sql_query("SELECT * FROM menu", conn)
    conn.close()
    return df

def add_menu_item_to_db(name, price, image_data):
    """เพิ่มรายการใหม่ลงในฐานข้อมูล"""
    conn = sqlite3.connect("menu.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO menu (name, price, image_data) VALUES (?, ?, ?)", (name, price, image_data))
    conn.commit()
    conn.close()

def update_menu_item_in_db(id, name, price, image_data):
    """แก้ไขรายการในฐานข้อมูล"""
    conn = sqlite3.connect("menu.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE menu SET name=?, price=?, image_data=? WHERE id=?", (name, price, image_data, id))
    conn.commit()
    conn.close()

def delete_menu_item_from_db(id):
    """ลบรายการออกจากฐานข้อมูล"""
    conn = sqlite3.connect("menu.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM menu WHERE id=?", (id,))
    conn.commit()
    conn.close()

# --- Functions for App Pages ---
def show_login_page():
    """แสดงหน้าฟอร์มล็อกอินสำหรับผู้ดูแลระบบ"""
    st.sidebar.markdown("### เข้าสู่ระบบผู้ดูแล")
    with st.sidebar.form("login_form"):
        username = st.text_input("ชื่อผู้ใช้")
        password = st.text_input("รหัสผ่าน", type="password")
        submitted = st.form_submit_button("เข้าสู่ระบบ")

        if submitted:
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

def show_admin_page():
    """แสดงหน้าจัดการรายการอาหารสำหรับผู้ดูแลระบบ"""
    st.markdown("<h1 style='text-align: center;'>หน้าจัดการรายการอาหาร (หลังบ้าน)</h1>", unsafe_allow_html=True)
    st.markdown("---")

    if st.sidebar.button("ออกจากระบบ", key="logout_button"):
        st.session_state.logged_in = False
        st.rerun()

    menu_options = ["เพิ่มรายการใหม่", "แก้ไข/ลบรายการ"]
    choice = st.selectbox("เลือกการจัดการ:", menu_options)

    if choice == "เพิ่มรายการใหม่":
        st.subheader("เพิ่มรายการอาหารใหม่")
        with st.form("add_form"):
            food_name = st.text_input("ชื่ออาหาร (ไทย/อังกฤษ)")
            price = st.number_input("ราคา (บาท)", min_value=0, step=1)
            uploaded_file = st.file_uploader("อัปโหลดรูปภาพ", type=["jpg", "jpeg", "png"])
            submitted = st.form_submit_button("บันทึกรายการ")

            if submitted:
                if food_name and price and uploaded_file:
                    buffered = BytesIO()
                    image = Image.open(uploaded_file)
                    image.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    image_data = f"data:image/png;base64,{img_str}"
                    add_menu_item_to_db(food_name, price, image_data)
                    st.success("เพิ่มรายการอาหารใหม่สำเร็จแล้ว!")
                    st.rerun()
                else:
                    st.error("กรุณากรอกข้อมูลให้ครบถ้วนและอัปโหลดรูปภาพ")

    elif choice == "แก้ไข/ลบรายการ":
        st.subheader("แก้ไข/ลบรายการอาหาร")
        df_menu = load_menu_data_from_db()

        if df_menu.empty:
            st.info("ไม่พบรายการอาหารในฐานข้อมูล")
            return
        
        # Select item from dropdown
        item_names = df_menu['name'].tolist()
        selected_name = st.selectbox("เลือกรหัส/ชื่ออาหารที่ต้องการแก้ไข", item_names)
        
        # Get data for the selected item
        selected_item = df_menu[df_menu['name'] == selected_name].iloc[0]

        # Display form for editing
        with st.form("edit_delete_form"):
            st.text_input("ชื่ออาหาร", value=selected_item['name'], key="edit_name")
            st.number_input("ราคา", value=selected_item['price'], key="edit_price")
            uploaded_file = st.file_uploader("อัปโหลดรูปภาพใหม่", type=["jpg", "jpeg", "png"])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("บันทึกการแก้ไข"):
                    updated_name = st.session_state.edit_name
                    updated_price = st.session_state.edit_price
                    image_data = selected_item['image_data']
                    if uploaded_file:
                        buffered = BytesIO()
                        image = Image.open(uploaded_file)
                        image.save(buffered, format="PNG")
                        img_str = base64.b64encode(buffered.getvalue()).decode()
                        image_data = f"data:image/png;base64,{img_str}"

                    update_menu_item_in_db(selected_item['id'], updated_name, updated_price, image_data)
                    st.success("บันทึกการแก้ไขสำเร็จแล้ว!")
                    st.rerun()
            with col2:
                if st.form_submit_button("ลบรายการนี้"):
                    delete_menu_item_from_db(selected_item['id'])
                    st.success("ลบรายการสำเร็จแล้ว!")
                    st.rerun()
        
        # Display current image
        st.markdown("---")
        st.subheader("รูปภาพปัจจุบัน")
        st.image(selected_item['image_data'], width=200)


def show_menu_page():
    """แสดงหน้าเมนูอาหารสำหรับลูกค้า"""
    st.markdown("""
    <style>
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
        font-size: 24px !important;
        font-weight: bold;
        color: #F8F9FA;
        margin-bottom: 5px;
    }
    @media (max-width: 600px) {
        .menu-card {
            padding: 10px;
            gap: 10px;
        }
        .menu-card img {
            width: 150px;
            height: 100px;
        }
        .menu-card-text {
            padding: 0 5px;
        }
        .food-name {
            font-size: 16px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    df_menu = load_menu_data_from_db()

    if df_menu.empty:
        st.info("ยังไม่มีรายการอาหารในเมนู")
        return

    st.markdown("<h1 style='text-align: center;'>🍽️ เมนูอาหาร / Menu</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>ร้าน Midwinter Khaoyai</h3>", unsafe_allow_html=True)
    
    for i, row in df_menu.iterrows():
        card_class = "menu-card"
        if i % 2 != 0:
            card_class += " menu-card-reverse"

        html_content = f"""
        <div class="{card_class}">
            <img src="{row['image_data']}" />
            <div class="menu-card-text">
                <p class="food-name">{row['name']}</p>
                <p><i>price:</i> {row['price']} ฿</p>
            </div>
        </div>
        """
        st.markdown(html_content, unsafe_allow_html=True)
    st.markdown("---")

# --- Main App Logic ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

st.sidebar.title("ควบคุมระบบ")
page_options = {
    "หน้าเมนู": show_menu_page,
    "หน้าผู้ดูแล": show_admin_page
}

page = st.sidebar.radio("เลือกหน้า", list(page_options.keys()), index=0)

if page == "หน้าผู้ดูแล" and not st.session_state.logged_in:
    show_login_page()
elif page == "หน้าผู้ดูแล" and st.session_state.logged_in:
    show_admin_page()
else:
    show_menu_page()