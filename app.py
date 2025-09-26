# import streamlit as st
# import pandas as pd
# from supabase import create_client, Client
# from io import BytesIO
# import base64
# from PIL import Image
# import uuid
# import os

# # --- Configuration ---
# ADMIN_USERNAME = "admin"
# ADMIN_PASSWORD = "password123"
# # ตั้งชื่อ bucket ที่คุณสร้างใน Supabase Storage
# BUCKET_NAME = "menu_images" 

# # --- Supabase Client ---
# @st.cache_resource
# def init_connection():
#     try:
#         url = st.secrets["supabase"]["SUPABASE_URL"]
#         key = st.secrets["supabase"]["SUPABASE_KEY"]
#         return create_client(url, key)
#     except KeyError as e:
#         st.error(f"Error: Missing Supabase secrets. Please check your secrets.toml file or Streamlit Cloud settings. Details: {e}")
#         st.stop()

# supabase = init_connection()

# # --- Functions for Database and Storage Management ---
# def load_menu_data_from_db():
#     """Load all data from Supabase"""
#     response = supabase.from_('menu').select('*').order('id', desc=False).execute()
#     df = pd.DataFrame(response.data)
#     return df

# def upload_image_to_storage(uploaded_file):
#     """Uploads an image file to Supabase Storage and returns its URL"""
#     try:
#         # สร้างชื่อไฟล์ที่ไม่ซ้ำกันด้วย UUID
#         file_extension = os.path.splitext(uploaded_file.name)[1]
#         file_name = f"{uuid.uuid4()}{file_extension}"
        
#         # อ่านข้อมูลดิบ (bytes) ของไฟล์
#         file_bytes = uploaded_file.getvalue()

#         # อัปโหลดไฟล์โดยใช้ข้อมูลดิบ
#         # แก้ไขการตรวจสอบ status_code ตามคำแนะนำล่าสุด
#         supabase.storage.from_(BUCKET_NAME).upload(file_name, file_bytes)

#         # ถ้ารันมาถึงตรงนี้ได้ แปลว่าอัปโหลดสำเร็จแล้ว
#         return supabase.storage.from_(BUCKET_NAME).get_public_url(file_name)
#     except Exception as e:
#         # ถ้าเกิดข้อผิดพลาดในการอัปโหลด จะถูกจับโดย except block นี้
#         st.error(f"เกิดข้อผิดพลาดในการอัปโหลดรูปภาพ: {e}")
#         return None

# def remove_image_from_storage(image_url):
#     """Removes an image from Supabase Storage using its URL"""
#     try:
#         # ดึงชื่อไฟล์จาก URL
#         file_name = image_url.split(f"/{BUCKET_NAME}/")[1]
#         supabase.storage.from_(BUCKET_NAME).remove([file_name])
#     except Exception as e:
#         st.error(f"ไม่สามารถลบไฟล์รูปภาพได้: {e}")

# def add_menu_item_to_db(name, price, image_url):
#     """Add a new item to Supabase"""
#     data = {'name': name, 'price': price, 'image_url': image_url}
#     supabase.from_('menu').insert(data).execute()

# def update_menu_item_in_db(id, name, price, new_image_url, old_image_url):
#     """Update an item in Supabase"""
#     data = {'name': name, 'price': price, 'image_url': new_image_url}
    
#     # ลบรูปภาพเก่าถ้ามีการอัปโหลดรูปภาพใหม่
#     if new_image_url and old_image_url and new_image_url != old_image_url:
#         remove_image_from_storage(old_image_url)

#     supabase.from_('menu').update(data).eq('id', id).execute()

# def delete_menu_item_from_db(id, image_url):
#     """Delete an item from Supabase and its corresponding image"""
#     # ลบรูปภาพจาก storage ก่อน
#     remove_image_from_storage(image_url)
#     # แล้วจึงลบข้อมูลในฐานข้อมูล
#     supabase.from_('menu').delete().eq('id', id).execute()

# # --- App Pages ---
# def show_login_page():
#     """Display login form for admin"""
#     st.sidebar.markdown("### เข้าสู่ระบบผู้ดูแล")
#     with st.sidebar.form("login_form"):
#         username = st.text_input("ชื่อผู้ใช้")
#         password = st.text_input("รหัสผ่าน", type="password")
#         submitted = st.form_submit_button("เข้าสู่ระบบ")

#         if submitted:
#             if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
#                 st.session_state.logged_in = True
#                 st.rerun()
#             else:
#                 st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

# def show_admin_page():
#     """Display admin management page"""
#     st.markdown("<h1 style='text-align: center;'>หน้าจัดการรายการอาหาร (หลังบ้าน)</h1>", unsafe_allow_html=True)
#     st.markdown("---")

#     if st.sidebar.button("ออกจากระบบ", key="logout_button"):
#         st.session_state.logged_in = False
#         st.rerun()

#     menu_options = ["เพิ่มรายการใหม่", "แก้ไข/ลบรายการ"]
#     choice = st.selectbox("เลือกการจัดการ:", menu_options)

#     if choice == "เพิ่มรายการใหม่":
#         st.subheader("เพิ่มรายการอาหารใหม่")
#         with st.form("add_form"):
#             food_name = st.text_input("ชื่ออาหาร (ไทย/อังกฤษ)")
#             price = st.number_input("ราคา (บาท)", min_value=0, step=1)
#             uploaded_file = st.file_uploader("อัปโหลดรูปภาพ", type=["jpg", "jpeg", "png"])
#             submitted = st.form_submit_button("บันทึกรายการ")

#             if submitted:
#                 if food_name and price and uploaded_file:
#                     image_url = upload_image_to_storage(uploaded_file)
#                     if image_url:
#                         add_menu_item_to_db(food_name, price, image_url)
#                         st.success("เพิ่มรายการอาหารใหม่สำเร็จแล้ว!")
#                         st.rerun()
#                 else:
#                     st.error("กรุณากรอกข้อมูลให้ครบถ้วนและอัปโหลดรูปภาพ")

#     elif choice == "แก้ไข/ลบรายการ":
#         st.subheader("แก้ไข/ลบรายการอาหาร")
#         df_menu = load_menu_data_from_db()

#         if df_menu.empty:
#             st.info("ไม่พบรายการอาหารในฐานข้อมูล")
#             return
        
#         item_names = df_menu['name'].tolist()
#         selected_name = st.selectbox("เลือกรหัส/ชื่ออาหารที่ต้องการแก้ไข", item_names)
        
#         selected_item = df_menu[df_menu['name'] == selected_name].iloc[0]

#         with st.form("edit_delete_form"):
#             st.text_input("ชื่ออาหาร", value=selected_item['name'], key="edit_name")
#             st.number_input("ราคา", value=selected_item['price'], key="edit_price")
#             uploaded_file = st.file_uploader("อัปโหลดรูปภาพใหม่", type=["jpg", "jpeg", "png"])
            
#             col1, col2 = st.columns(2)
#             with col1:
#                 if st.form_submit_button("บันทึกการแก้ไข"):
#                     updated_name = st.session_state.edit_name
#                     updated_price = st.session_state.edit_price
#                     image_url = selected_item['image_url']
                    
#                     if uploaded_file:
#                         image_url = upload_image_to_storage(uploaded_file)
                        
#                     update_menu_item_in_db(selected_item['id'], updated_name, updated_price, image_url, selected_item['image_url'])
#                     st.success("บันทึกการแก้ไขสำเร็จแล้ว!")
#                     st.rerun()
#             with col2:
#                 if st.form_submit_button("ลบรายการนี้"):
#                     delete_menu_item_from_db(selected_item['id'], selected_item['image_url'])
#                     st.success("ลบรายการสำเร็จแล้ว!")
#                     st.rerun()
        
#         st.markdown("---")
#         st.subheader("รูปภาพปัจจุบัน")
#         st.image(selected_item['image_url'], width=200)

# def show_menu_page():
#     """Display menu page for customers"""
#     st.markdown("""
#     <style>
#     .menu-card {
#         display: flex;
#         align-items: center;
#         justify-content: space-between;
#         background-color: #262730;
#         border-radius: 10px;
#         padding: 20px;
#         margin-bottom: 20px;
#         box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
#     }
#     .menu-card-reverse {
#         flex-direction: row-reverse;
#     }
#     .menu-card img {
#         width: 300px;
#         height: 200px;
#         object-fit: cover;
#         border-radius: 8px;
#     }
#     .menu-card-text {
#         flex: 1;
#         padding: 0 20px;
#         text-align: center;
#     }
#     .menu-card-text p {
#         margin: 0;
#         line-height: 1.5;
#     }
#     .food-name {
#         font-size: 24px !important;
#         font-weight: bold;
#         color: #F8F9FA;
#         margin-bottom: 5px;
#     }
#     @media (max-width: 600px) {
#         .menu-card {
#             padding: 10px;
#             gap: 10px;
#         }
#         .menu-card img {
#             width: 150px;
#             height: 100px;
#         }
#         .menu-card-text {
#             padding: 0 5px;
#         }
#         .food-name {
#             font-size: 16px !important;
#         }
#     }
#     </style>
#     """, unsafe_allow_html=True)
    
#     df_menu = load_menu_data_from_db()

#     if df_menu.empty:
#         st.info("ยังไม่มีรายการอาหารในเมนู")
#         return

#     st.markdown("<h1 style='text-align: center;'>🍽️ เมนูอาหาร / Menu</h1>", unsafe_allow_html=True)
#     st.markdown("<h3 style='text-align: center;'>ร้าน Midwinter Khaoyai</h3>", unsafe_allow_html=True)
    
#     for i, row in df_menu.iterrows():
#         card_class = "menu-card"
#         if i % 2 != 0:
#             card_class += " menu-card-reverse"

#         html_content = f"""
#         <div class="{card_class}">
#             <img src="{row['image_url']}" />
#             <div class="menu-card-text">
#                 <p class="food-name">{row['name']}</p>
#                 <p><i>price:</i> {row['price']} ฿</p>
#             </div>
#         </div>
#         """
#         st.markdown(html_content, unsafe_allow_html=True)
#     st.markdown("---")

# # --- Main App Logic ---
# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False

# st.sidebar.title("ควบคุมระบบ")
# page_options = {
#     "หน้าเมนู": show_menu_page,
#     "หน้าผู้ดูแล": show_admin_page
# }

# page = st.sidebar.radio("เลือกหน้า", list(page_options.keys()), index=0)

# if page == "หน้าผู้ดูแล" and not st.session_state.logged_in:
#     show_login_page()
# elif page == "หน้าผู้ดูแล" and st.session_state.logged_in:
#     show_admin_page()
# else:
#     show_menu_page()
import streamlit as st
import pandas as pd
from supabase import create_client, Client
import uuid
import os
import json 
import time

# --- Configuration ---
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"
SERVICE_USERNAME = "service" 
SERVICE_PASSWORD = "service123" 
BUCKET_NAME = "menu_images" 

# กำหนดหมวดหมู่รายการอาหาร
CATEGORIES = ["อาหาร", "เครื่องดื่ม", "ขนมหวาน", "พิซซ่า", "อื่นๆ"] 

# --- Supabase Client ---
@st.cache_resource
def init_connection():
    """Initializes and caches the Supabase connection."""
    try:
        url = st.secrets["supabase"]["SUPABASE_URL"]
        key = st.secrets["supabase"]["SUPABASE_KEY"]
        return create_client(url, key)
    except KeyError as e:
        st.error(f"Error: Missing Supabase secrets. Please check your secrets.toml file or Streamlit Cloud settings. Details: {e}")
        st.stop()

supabase = init_connection()

# --- Functions for Database and Storage Management ---

def load_menu_data_from_db():
    """Load all data from Supabase"""
    response = supabase.from_('menu').select('*').order('id', desc=False).execute()
    df = pd.DataFrame(response.data)
    return df

def upload_image_to_storage(uploaded_file):
    """Uploads an image file to Supabase Storage and returns its URL"""
    try:
        file_extension = os.path.splitext(uploaded_file.name)[1]
        file_name = f"{uuid.uuid4()}{file_extension}"
        file_bytes = uploaded_file.getvalue()
        supabase.storage.from_(BUCKET_NAME).upload(file_name, file_bytes)
        return supabase.storage.from_(BUCKET_NAME).get_public_url(file_name)
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการอัปโหลดรูปภาพ: {e}")
        return None

def remove_image_from_storage(image_url):
    """Removes an image from Supabase Storage using its URL"""
    try:
        file_name = image_url.split(f"/{BUCKET_NAME}/")[1]
        supabase.storage.from_(BUCKET_NAME).remove([file_name])
    except Exception as e:
        st.error(f"ไม่สามารถลบไฟล์รูปภาพได้: {e}")

def add_menu_item_to_db(name, price, category, image_url):
    """Add a new item to Supabase (includes category)"""
    data = {'name': name, 'price': price, 'category': category, 'image_url': image_url}
    supabase.from_('menu').insert(data).execute()

def update_menu_item_in_db(id, name, price, category, new_image_url, old_image_url):
    """Update an item in Supabase (includes category)"""
    data = {'name': name, 'price': price, 'category': category, 'image_url': new_image_url}
    
    if new_image_url and old_image_url and new_image_url != old_image_url:
        remove_image_from_storage(old_image_url)

    supabase.from_('menu').update(data).eq('id', id).execute()

def delete_menu_item_from_db(id, image_url):
    """Delete an item from Supabase and its corresponding image"""
    remove_image_from_storage(image_url)
    supabase.from_('menu').delete().eq('id', id).execute()

# --- Functions for Order Management ---

def place_order_to_db(table_number, customer_name, cart):
    """Inserts a new order into the 'orders' table."""
    order_items = [
        {'name': item['name'], 'quantity': item['quantity'], 'price': item['price']}
        for item in cart.values()
    ]
    
    data = {
        'table_number': table_number,
        'customer_name': customer_name,
        'items': order_items,
        'status': 'New Order' 
    }
    # Supabase (PostgREST) ต้องการ JSON string หาก column เป็น jsonb/json
    data['items'] = json.dumps(data['items']) 
    
    supabase.from_('orders').insert(data).execute()

def load_active_orders():
    """Load active orders (New Order and In Service) for the Service page."""
    response = supabase.from_('orders').select('*').in_('status', ['New Order', 'In Service']).order('created_at', desc=False).execute()
    return response.data

def update_order_status(order_id, new_status):
    """Updates the status of a specific order."""
    supabase.from_('orders').update({'status': new_status}).eq('id', order_id).execute()


# --- Function for Sidebar Cart (MODAL) ---

def show_sidebar_cart():
    """Display the cart contents and order form in the sidebar (acting as a modal)."""
    st.sidebar.markdown("## 🛒 ตะกร้าสินค้า")
    
    if 'cart' not in st.session_state:
        st.session_state.cart = {}
    
    total_items = sum(item['quantity'] for item in st.session_state.cart.values())
    total_price = sum(item['price'] * item['quantity'] for item in st.session_state.cart.values())

    if total_items > 0:
        with st.sidebar.form("place_order_form"):
            st.write("### รายการที่สั่ง")
            for menu_id, item in st.session_state.cart.items():
                st.write(f"- {item['name']} (x{item['quantity']}) : {item['price'] * item['quantity']} ฿")
                
            st.markdown(f"**รวมทั้งสิ้น:** **{total_price} ฿**")
            st.markdown("---")
            
            table_number = st.text_input("เลขที่โต๊ะ", key="table_number_input_side")
            customer_name = st.text_input("ชื่อผู้สั่ง (ไม่บังคับ)", key="customer_name_input_side")
            
            # ใช้ st.columns ภายใน st.form
            col_submit, col_clear = st.columns(2)
            
            with col_submit:
                if st.form_submit_button("✅ ยืนยันการสั่งอาหาร"):
                    if table_number.strip():
                        try:
                            place_order_to_db(table_number, customer_name, st.session_state.cart)
                            st.success(f"ส่งออเดอร์เรียบร้อยแล้ว! โต๊ะ {table_number}")
                            st.session_state.cart = {} # Clear cart
                            st.session_state.show_cart_sidebar = False # ปิด Sidebar Modal
                            time.sleep(1) # หน่วงเวลาให้ข้อความแสดงผลก่อน rerund
                            st.rerun() 
                        except Exception as e:
                            st.error(f"เกิดข้อผิดพลาดในการส่งออเดอร์: โปรดตรวจสอบ RLS Policy ของตาราง 'orders' ด้วยครับ. ข้อผิดพลาด: {e}")
                    else:
                        st.error("กรุณาระบุเลขที่โต๊ะ")
            
            with col_clear:
                if st.form_submit_button("🗑️ ล้างตะกร้า"):
                    st.session_state.cart = {}
                    st.rerun()

    else:
        st.sidebar.info("ตะกร้าสินค้าว่างเปล่า")
    
    # ปุ่มปิด Modal (Popup)
    if st.sidebar.button("✖️ ปิดตะกร้า", key="close_cart_sidebar"):
        st.session_state.show_cart_sidebar = False
        st.rerun()

# --- Functions for Admin/Service Login ---

def show_login_page():
    """Display login form for admin"""
    st.sidebar.markdown("### เข้าสู่ระบบผู้ดูแล")
    with st.sidebar.form("admin_login_form"):
        username = st.text_input("ชื่อผู้ใช้ (Admin)")
        password = st.text_input("รหัสผ่าน (Admin)", type="password")
        submitted = st.form_submit_button("เข้าสู่ระบบ")
        if submitted:
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

def show_service_login():
    """Display login form for service staff"""
    st.sidebar.markdown("### เข้าสู่ระบบบริการ")
    with st.sidebar.form("service_login_form"):
        username = st.text_input("ชื่อผู้ใช้ (Service)")
        password = st.text_input("รหัสผ่าน (Service)", type="password")
        submitted = st.form_submit_button("เข้าสู่ระบบบริการ")
        if submitted:
            if username == SERVICE_USERNAME and password == SERVICE_PASSWORD:
                st.session_state.service_logged_in = True
                st.rerun()
            else:
                st.error("ชื่อผู้ใช้หรือรหัสผ่านบริการไม่ถูกต้อง")

# --- App Pages ---

def show_admin_page():
    """Display admin management page"""
    st.markdown("<h1 style='text-align: center;'>หน้าจัดการรายการอาหาร (หลังบ้าน)</h1>", unsafe_allow_html=True)
    st.markdown("---")

    if st.sidebar.button("ออกจากระบบผู้ดูแล", key="admin_logout_button"):
        st.session_state.admin_logged_in = False
        st.rerun()

    menu_options = ["เพิ่มรายการใหม่", "แก้ไข/ลบรายการ"]
    choice = st.selectbox("เลือกการจัดการ:", menu_options)

    if choice == "เพิ่มรายการใหม่":
        st.subheader("เพิ่มรายการอาหารใหม่")
        with st.form("add_form"):
            food_name = st.text_input("ชื่ออาหาร (ไทย/อังกฤษ)")
            price = st.number_input("ราคา (บาท)", min_value=0, step=1)
            category = st.selectbox("หมวดหมู่", CATEGORIES) 
            uploaded_file = st.file_uploader("อัปโหลดรูปภาพ", type=["jpg", "jpeg", "png"])
            submitted = st.form_submit_button("บันทึกรายการ")

            if submitted:
                if food_name and price and category and uploaded_file:
                    image_url = upload_image_to_storage(uploaded_file)
                    if image_url:
                        add_menu_item_to_db(food_name, price, category, image_url) 
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
        
        if 'category' not in df_menu.columns:
            st.warning("กรุณาเพิ่มคอลัมน์ 'category' ในตาราง 'menu' ด้วย Type 'text' ก่อน")
            return

        item_names = df_menu['name'].tolist()
        selected_name = st.selectbox("เลือกรหัส/ชื่ออาหารที่ต้องการแก้ไข", item_names)
        
        selected_item = df_menu[df_menu['name'] == selected_name].iloc[0]

        try:
            current_category_index = CATEGORIES.index(selected_item['category'])
        except ValueError:
            current_category_index = 0

        with st.form("edit_delete_form"):
            st.text_input("ชื่ออาหาร", value=selected_item['name'], key="edit_name")
            st.number_input("ราคา", value=selected_item['price'], key="edit_price")
            st.selectbox("หมวดหมู่", CATEGORIES, index=current_category_index, key="edit_category") 
            uploaded_file = st.file_uploader("อัปโหลดรูปภาพใหม่", type=["jpg", "jpeg", "png"])
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("บันทึกการแก้ไข"):
                    updated_name = st.session_state.edit_name
                    updated_price = st.session_state.edit_price
                    updated_category = st.session_state.edit_category
                    image_url = selected_item['image_url']
                    
                    if uploaded_file:
                        image_url = upload_image_to_storage(uploaded_file)
                        
                    update_menu_item_in_db(selected_item['id'], updated_name, updated_price, updated_category, image_url, selected_item['image_url'])
                    st.success("บันทึกการแก้ไขสำเร็จแล้ว!")
                    st.rerun()
            with col2:
                if st.form_submit_button("ลบรายการนี้"):
                    delete_menu_item_from_db(selected_item['id'], selected_item['image_url'])
                    st.success("ลบรายการสำเร็จแล้ว!")
                    st.rerun()
        
        st.markdown("---")
        st.subheader("รูปภาพปัจจุบัน")
        st.image(selected_item['image_url'], width=200)

def show_service_page():
    """Display the Kitchen Display System (KDS) for staff."""
    st.markdown("<h1 style='text-align: center;'>👩‍🍳 หน้าบริการ (KDS)</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    if st.sidebar.button("ออกจากระบบบริการ", key="service_logout_button"):
        st.session_state.service_logged_in = False
        st.rerun()

    st.header("รายการออเดอร์ที่ใช้งานอยู่")
    
    if st.button("🔄 อัปเดตรายการ (Refresh)", key="refresh_orders"):
        st.rerun() 
    
    active_orders = load_active_orders()

    if not active_orders:
        st.info("ไม่มีรายการออเดอร์ใหม่ หรือออเดอร์ที่กำลังบริการอยู่")
        return

    df_orders = pd.DataFrame(active_orders)

    col_new, col_in_service = st.columns(2)
    
    # --- New Orders Column ---
    with col_new:
        st.subheader("🔔 ออเดอร์ใหม่ (New Order)")
        new_orders = df_orders[df_orders['status'] == 'New Order']
        
        if new_orders.empty:
            st.info("ไม่มีออเดอร์ใหม่")
            
        for i, order in new_orders.iterrows():
            order_id = order['id']
            # Display Card
            st.markdown(f"**โต๊ะ:** **{order['table_number']}** | **ชื่อผู้สั่ง:** {order['customer_name'] or 'ลูกค้า'}")
            st.caption(f"เวลาสั่ง: {pd.to_datetime(order['created_at']).strftime('%H:%M:%S')}")
            st.markdown("---")
            
            items_data = order['items']
            if isinstance(items_data, str):
                 items_data = json.loads(items_data)

            item_list = ""
            for item in items_data:
                item_list += f"- {item['name']} (x{item['quantity']}) \n"
            st.text(item_list)
            
            # Action Button: กำลังบริการ
            if st.button("▶️ กำลังบริการ (Start Service)", key=f"start_{order_id}"):
                update_order_status(order_id, 'In Service')
                st.rerun() 
            st.markdown("---")
            
    # --- In Service Column ---
    with col_in_service:
        st.subheader("⏳ กำลังบริการ (In Service)")
        in_service_orders = df_orders[df_orders['status'] == 'In Service']
        
        if in_service_orders.empty:
            st.info("ไม่มีออเดอร์ที่กำลังบริการ")

        for i, order in in_service_orders.iterrows():
            order_id = order['id']
            # Display Card
            st.markdown(f"**โต๊ะ:** **{order['table_number']}** | **ชื่อผู้สั่ง:** {order['customer_name'] or 'ลูกค้า'}")
            st.caption(f"เวลาสั่ง: {pd.to_datetime(order['created_at']).strftime('%H:%M:%S')}")
            st.markdown("---")
            
            items_data = order['items']
            if isinstance(items_data, str):
                 items_data = json.loads(items_data)

            item_list = ""
            for item in items_data:
                item_list += f"- {item['name']} (x{item['quantity']}) \n"
            st.text(item_list)
            
            # Action Button: เสร็จสิ้น
            if st.button("✅ เสร็จสิ้น (Mark as Completed)", key=f"complete_{order_id}"):
                update_order_status(order_id, 'Completed')
                st.rerun() 
            st.markdown("---")

def show_menu_page():
    """Display menu page for customers (with ordering and categories)"""
    
    if 'cart' not in st.session_state:
        st.session_state.cart = {}
        
    # --- ปุ่มตะกร้าสินค้า (ด้านบนซ้าย) ---
    total_items = sum(item['quantity'] for item in st.session_state.cart.values())
    total_price = sum(item['price'] * item['quantity'] for item in st.session_state.cart.values())
    
    button_label = f"🛒 ตะกร้าสินค้า ({total_items} รายการ, {total_price} ฿)"
    
    col_cart_button, col_title = st.columns([1, 4])
    
    with col_cart_button:
        # ปุ่มกดเพื่อเปิด Sidebar Modal/Popup
        if st.button(button_label, key="open_cart_modal"):
            st.session_state.show_cart_sidebar = True
            st.rerun()

    # --- Menu Display Logic ---
    with col_title:
        st.markdown("<h1 style='text-align: center;'>🍽️ เมนูอาหาร / Menu</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>ร้าน Midwinter Khaoyai</h3>", unsafe_allow_html=True)
        
    st.markdown("---")

    df_menu = load_menu_data_from_db()

    if df_menu.empty or 'category' not in df_menu.columns:
        st.info("ไม่พบรายการอาหาร หรือตาราง 'menu' ขาดคอลัมน์ 'category'")
        return

    # Category Filter
    selected_category = st.radio("เลือกหมวดหมู่:", CATEGORIES, horizontal=True)
    st.markdown("---")

    df_filtered = df_menu[df_menu['category'] == selected_category]
    if df_filtered.empty:
        st.info(f"ไม่พบรายการอาหารในหมวดหมู่ **'{selected_category}'**")
        return

    # Display filtered items
    for i, row in df_filtered.iterrows():
        menu_id = row['id']
        
        col_img, col_text, col_order = st.columns([1, 2, 1])
        
        with col_img:
            st.image(row['image_url'], width=150)
        
        with col_text:
            st.markdown(f"<p class='food-name'>{row['name']}</p>", unsafe_allow_html=True)
            st.write(f"ราคา: **{row['price']}** ฿")
            
        with col_order:
            # ใช้ st.number_input สำหรับเลือกจำนวนสินค้า
            current_quantity = st.session_state.cart.get(menu_id, {}).get('quantity', 0)
            quantity_key = f"qty_{menu_id}_{selected_category}"
            
            quantity = st.number_input("จำนวน:", min_value=0, value=current_quantity, step=1, key=quantity_key, label_visibility="collapsed")
            
            # Logic to update cart on change
            if quantity != current_quantity:
                if quantity > 0:
                    st.session_state.cart[menu_id] = {
                        'id': menu_id,
                        'name': row['name'], 
                        'price': row['price'], 
                        'quantity': quantity
                    }
                elif quantity == 0 and menu_id in st.session_state.cart:
                    del st.session_state.cart[menu_id]
                st.rerun() 


# --- Main App Logic ---

# Initialize Session State
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
    
if "service_logged_in" not in st.session_state:
    st.session_state.service_logged_in = False
    
if "show_cart_sidebar" not in st.session_state:
    st.session_state.show_cart_sidebar = False


# 1. กำหนดตัวเลือกหน้า
page_options = {
    "หน้าเมนู (ลูกค้า)": show_menu_page,
    "หน้าผู้ดูแล (Admin)": show_admin_page,
    "หน้าบริการ (Service)": show_service_page
}

# 2. แสดงผลใน Sidebar: เลือกแสดง 'ตะกร้าสินค้า' หรือ 'เมนูนำทาง'
if st.session_state.show_cart_sidebar:
    # หากตะกร้าสินค้าแสดงอยู่
    show_sidebar_cart()
    # กำหนดให้หน้าหลักเป็น หน้าเมนู เสมอ
    page = "หน้าเมนู (ลูกค้า)"
else:
    # หากแสดงเมนูนำทางปกติ
    st.sidebar.title("ควบคุมระบบ")
    st.sidebar.markdown("---")
    # ตัวแปร 'page' จะถูกกำหนดค่าที่นี่
    page = st.sidebar.radio("เลือกหน้า", list(page_options.keys()), index=0) 


# 3. แสดงผลหน้าหลัก (ใช้ตัวแปร page ที่ถูกกำหนดแล้ว)
if page == "หน้าผู้ดูแล (Admin)":
    if not st.session_state.admin_logged_in:
        show_login_page()
    else:
        show_admin_page()
        
elif page == "หน้าบริการ (Service)":
    if not st.session_state.service_logged_in:
        show_service_login()
    else:
        show_service_page()

else:
    # สำหรับ "หน้าเมนู (ลูกค้า)" (รวมถึงกรณีที่เปิด Sidebar Cart)
    show_menu_page()