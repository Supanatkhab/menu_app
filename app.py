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
    """Initializes and caches the Supabase connection using Environment Variables (Render) or st.secrets (Streamlit Cloud)."""
    try:
        # 1. Try reading from Environment Variables (Recommended for Render)
        url = os.getenv("SUPABASE_URL") 
        key = os.getenv("SUPABASE_KEY")
        
        # 2. Fallback to st.secrets (for Streamlit Cloud or local testing with secrets.toml)
        if not url or not key:
            url = st.secrets["supabase"]["SUPABASE_URL"]
            key = st.secrets["supabase"]["SUPABASE_KEY"]

        if not url or not key:
             st.error("Error: Missing SUPABASE_URL or SUPABASE_KEY. Please set Environment Variables on Render or in secrets.toml.")
             st.stop()

        return create_client(url, key)
    except KeyError as e:
        st.error(f"Error: Missing Supabase secrets. Details: {e}")
        st.stop()

# เชื่อมต่อฐานข้อมูล
supabase = init_connection()

# --- Session State Initialization ---
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
    
if "service_logged_in" not in st.session_state:
    st.session_state.service_logged_in = False
    
if "show_cart_modal" not in st.session_state:
    st.session_state.show_cart_modal = False
    
if 'cart' not in st.session_state:
    st.session_state.cart = {}
    
# --- Navigation/State Functions ---
def open_cart_modal():
    st.session_state.show_cart_modal = True
    
def close_cart_modal():
    st.session_state.show_cart_modal = False
    
def clear_cart():
    st.session_state.cart = {}

# --- Database and Storage Functions (ย่อไว้, ใช้โค้ดเดิม) ---

def load_menu_data_from_db():
    @st.cache_data(ttl=10)
    def fetch_data():
        response = supabase.from_('menu').select('*').order('id', desc=False).execute()
        return pd.DataFrame(response.data)
    return fetch_data()

def upload_image_to_storage(uploaded_file):
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
    try:
        file_name = image_url.split(f"/{BUCKET_NAME}/")[1]
        supabase.storage.from_(BUCKET_NAME).remove([file_name])
    except Exception as e:
        st.error(f"ไม่สามารถลบไฟล์รูปภาพได้: {e}")

def add_menu_item_to_db(name, price, category, image_url):
    data = {'name': name, 'price': price, 'category': category, 'image_url': image_url}
    supabase.from_('menu').insert(data).execute()

def update_menu_item_in_db(id, name, price, category, new_image_url, old_image_url):
    data = {'name': name, 'price': price, 'category': category, 'image_url': new_image_url}
    if new_image_url and old_image_url and new_image_url != old_image_url:
        remove_image_from_storage(old_image_url)
    supabase.from_('menu').update(data).eq('id', id).execute()

def delete_menu_item_from_db(id, image_url):
    remove_image_from_storage(image_url)
    supabase.from_('menu').delete().eq('id', id).execute()

def place_order_to_db(table_number, customer_name, cart):
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
    data['items'] = json.dumps(data['items']) 
    supabase.from_('orders').insert(data).execute()

def load_active_orders():
    response = supabase.from_('orders').select('*').in_('status', ['New Order', 'In Service']).order('created_at', desc=False).execute()
    return response.data

def update_order_status(order_id, new_status):
    supabase.from_('orders').update({'status': new_status}).eq('id', order_id).execute()

def delete_order_from_db(order_id):
    supabase.from_('orders').delete().eq('id', order_id).execute()


# --- Functions for Admin/Service Login ---
def show_login_page():
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


# --- NEW: Cart Modal/Popup Function (Native Streamlit Container) ---

def display_cart_modal():
    """Renders the shopping cart content in a simulated modal container."""
    
    total_items = sum(item['quantity'] for item in st.session_state.cart.values())
    total_price = sum(item['price'] * item['quantity'] for item in st.session_state.cart.values())
    
    # --- Modal Header and Close Button ---
    col_title, col_close = st.columns([5, 1])
    with col_title:
        st.subheader("🛒 ตะกร้าสินค้าของคุณ")
    with col_close:
        # ใช้ปุ่ม Close (x) เพื่อปิด Modal
        if st.button("✖️ ปิด", on_click=close_cart_modal, key="close_modal_btn"):
            pass
            
    st.markdown("---")

    if not st.session_state.cart:
        st.info("ตะกร้าสินค้าว่างเปล่า!")
        return

    # --- Display and Manage Items in the Cart ---
    st.markdown("### รายการที่สั่งซื้อ")
    for menu_id, item in list(st.session_state.cart.items()): # Use list() for safe modification
        col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 1])
        
        with col1:
            st.write(f"**{item['name']}**")
        
        with col2:
            # Quantity control
            new_qty = st.number_input(
                "จำนวน", 
                min_value=0, 
                value=item['quantity'], 
                step=1,
                key=f"modal_qty_{menu_id}",
                label_visibility="collapsed",
            )
        
        # Update cart immediately on change 
        if new_qty != item['quantity']:
            if new_qty <= 0:
                del st.session_state.cart[menu_id]
                st.rerun() 
            else:
                st.session_state.cart[menu_id]['quantity'] = new_qty
                st.rerun()
                
        with col3:
            st.write(f"{item['price'] * item['quantity']:,.0f} ฿")
        
        with col4:
            # Remove button
            if st.button("🗑️", key=f"modal_remove_{menu_id}", help="ลบรายการ"):
                del st.session_state.cart[menu_id]
                st.rerun() 
            
    st.markdown("---")
    st.markdown(f"**รวมทั้งสิ้น:** **{total_price:,.0f} ฿**")

    # --- Order Submission Form ---
    st.markdown("### ข้อมูลการสั่งซื้อ")
    
    with st.form("order_form"):
        table_number = st.text_input("หมายเลขโต๊ะ 🔢", key="modal_table_number")
        customer_name = st.text_input("ชื่อลูกค้า 👤 (ไม่บังคับ)", key="modal_customer_name")
        
        col_submit, col_clear = st.columns([3, 1])
        
        with col_submit:
            submitted = st.form_submit_button("✅ ยืนยันการสั่งซื้อ")
        
        with col_clear:
            if st.form_submit_button("🗑️ ล้างตะกร้า"):
                clear_cart()
                close_cart_modal()
                st.rerun()
                
        if submitted:
            if not table_number.strip():
                st.error("กรุณากรอกหมายเลขโต๊ะ")
            elif not st.session_state.cart:
                st.error("ตะกร้าสินค้าว่างเปล่า ไม่สามารถสั่งซื้อได้")
            else:
                try:
                    place_order_to_db(table_number, customer_name, st.session_state.cart)
                    st.success("🎉 สั่งซื้อสำเร็จ! กรุณารอรับอาหาร")
                    clear_cart()
                    close_cart_modal()
                    st.rerun() 
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการบันทึกคำสั่งซื้อ: {e}")

# --- App Pages ---

def show_admin_page():
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
            image_url = selected_item['image_url']
            st.markdown(
                f"""
                <img src="{image_url}" style="width: 200px; height: 150px; object-fit: cover; border-radius: 5px;">
                """,
                unsafe_allow_html=True
            )

def show_service_page():
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
    
    with col_new:
        st.subheader("🔔 ออเดอร์ใหม่ (New Order)")
        new_orders = df_orders[df_orders['status'] == 'New Order']
        
        if new_orders.empty:
            st.info("ไม่มีออเดอร์ใหม่")
            
        for i, order in new_orders.iterrows():
            order_id = order['id']
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
            
            if st.button("▶️ กำลังบริการ (Start Service)", key=f"start_{order_id}"):
                update_order_status(order_id, 'In Service')
                st.rerun() 
            st.markdown("---")
            
    with col_in_service:
        st.subheader("⏳ กำลังบริการ (In Service)")
        in_service_orders = df_orders[df_orders['status'] == 'In Service']
        
        if in_service_orders.empty:
            st.info("ไม่มีออเดอร์ที่กำลังบริการ")

        for i, order in in_service_orders.iterrows():
            order_id = order['id']
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
            
            if st.button("✅ เสร็จสิ้น (Complete & Delete)", key=f"complete_{order_id}"):
                delete_order_from_db(order_id)
                st.rerun() 
            st.markdown("---")

def show_menu_page():
    """Display menu page for customers (with ordering and categories)"""
    
    # --- ปุ่มตะกร้าสินค้า (ด้านบนซ้าย) ---
    total_items = sum(item['quantity'] for item in st.session_state.cart.values())
    total_price = sum(item['price'] * item['quantity'] for item in st.session_state.cart.values())
    
    button_label = f"🛒 ตะกร้าสินค้า ({total_items} รายการ, {total_price} ฿)"
    
    col_cart_button, col_title = st.columns([1, 4])
    
    with col_cart_button:
        # *** ใช้ on_click เพื่อเปิด Modal ***
        if st.button(button_label, key="open_cart_modal", on_click=open_cart_modal):
            pass

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
        
        # *** โครงสร้าง Layout ใหม่สำหรับมือถือ: [รูปภาพ (1)] | [ชื่อ/ราคา (2.5)] | [จำนวน/ปุ่ม (1.5)] ***
        col_img, col_text, col_order = st.columns([1, 2.5, 1.5])
        
        with col_img:
            image_url = row['image_url']
            # ใช้ HTML/Markdown เพื่อควบคุมขนาดรูปภาพให้พอดี
            st.markdown(
                f"""
                <img src="{image_url}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 5px; margin-top: 10px;">
                """,
                unsafe_allow_html=True
            )
        
        with col_text:
            # ใช้ Markdown เพื่อจัดให้ชิดด้านบน
            st.markdown(f"**{row['name']}**")
            st.write(f"ราคา: **{row['price']}** ฿")
            
        with col_order:
            current_quantity = st.session_state.cart.get(menu_id, {}).get('quantity', 0)
            quantity_key = f"qty_{menu_id}_{selected_category}"
            
            # Number Input (จำนวน)
            quantity = st.number_input(
                "จำนวน:", 
                min_value=0, 
                value=current_quantity, 
                step=1, 
                key=quantity_key, 
                label_visibility="collapsed" # ซ่อน Label
            )
            
            # จัดการ Session State เมื่อจำนวนเปลี่ยน
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
        
        st.divider() 


# --- Main App Logic ---

# 1. Sidebar Control
st.sidebar.title("ควบคุมระบบ")
st.sidebar.markdown("---")

page = st.sidebar.radio("เลือกหน้า", ["หน้าเมนู (ลูกค้า)", "หน้าผู้ดูแล (Admin)", "หน้าบริการ (Service)"], index=0) 

# 2. Main Content Placeholder
# *สร้าง Placeholder สำหรับ Modal ที่จะซ้อนทับเนื้อหาหลัก*
modal_placeholder = st.empty()
app_content = st.container()

# 3. Logic การแสดงผลหน้าหลัก
with app_content:
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

    else: # หน้าเมนู (ลูกค้า)
        show_menu_page()


# 4. Logic การแสดง Modal
# ถ้า show_cart_modal เป็น True ให้วาด Modal ทับเนื้อหา app_content
if st.session_state.show_cart_modal:
    # เพิ่ม CSS เพื่อทำให้ Container มีลักษณะเป็น Modal
    st.markdown("""
    <style>
    /* ซ่อนเนื้อหาหลักเมื่อ Modal เปิด เพื่อให้ Modal ดูโดดเด่น */
    /* การซ่อนทำได้ยากใน Streamlit โดยไม่ใช้ Component ภายนอก เราจึงใช้ Container */
    
    .modal-container {
        position: fixed; 
        top: 50%; 
        left: 50%; 
        transform: translate(-50%, -50%); 
        max-width: 600px;
        min-width: 80%; /* สำหรับมือถือ */
        padding: 20px;
        border-radius: 10px;
        background-color: white; 
        box-shadow: 0 4px 8px rgba(0,0,0,0.5);
        z-index: 9999; 
        max-height: 90vh; /* จำกัดความสูงของ Modal */
        overflow-y: auto;
    }
    
    /* สไตล์สำหรับพื้นหลังทึบ (Overlay) */
    .st-emotion-cache-18ni7ap { /* target the main app container for overlay */
        pointer-events: none; /* Disable interaction with background */
    }
    </style>
    """, unsafe_allow_html=True)
    
    # วาด Modal ใน Placeholder โดยใช้ Container
    with modal_placeholder.container():
        # ใช้มาร์คดาวน์เพื่อสร้าง Container ที่มีสไตล์ Modal
        st.markdown('<div class="modal-container">', unsafe_allow_html=True)
        display_cart_modal()
        st.markdown('</div>', unsafe_allow_html=True)