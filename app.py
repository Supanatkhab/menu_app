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
CATEGORIES = ["อาหาร/Food", "เครื่องดื่ม/Drink", "ขนมหวาน/Dessrets", "พิซซ่า/Pizza",]

# --- Multi-language Support (Thai & English) ---
# Dictionary สำหรับข้อความที่ต้องแปล
# Key: 'th' (Thai), 'en' (English)
# *** ควรเพิ่มคำแปลสำหรับชื่ออาหารใน Database ด้วย แต่ในโค้ดจะเน้นที่ UI ก่อน ***

TRANSLATIONS = {
    'title_menu': {'th': "🍽️ เมนูอาหาร ", 'en': "🍽️ Food Menu "},
    'subtitle_restaurant': {'th': "ร้าน Midwinter Khaoyai", 'en': "Midwinter Khaoyai Restaurant"},
    'title_cart': {'th': "🛒 สรุปรายการสั่งซื้อ", 'en': "🛒 Shopping Cart Summary"},
    'cart_empty': {'th': "ตะกร้าสินค้าว่างเปล่า! 🧐", 'en': "Your shopping cart is empty! 🧐"},
    'back_to_menu': {'th': "<< กลับไปหน้าเมนู", 'en': "<< Back to Menu"},
    'items_ordered': {'th': "รายการที่สั่งซื้อ", 'en': "Items Ordered"},
    'item': {'th': "รายการ", 'en': "Item"},
    'quantity': {'th': "จำนวน", 'en': "Qty"},
    'subtotal': {'th': "ราคารวมย่อย", 'en': "Subtotal"},
    'remove': {'th': "ลบ", 'en': "Remove"},
    'total': {'th': "รวมทั้งสิ้น:", 'en': "Total:"},
    'checkout_info': {'th': "ข้อมูลการสั่งซื้อ (ยืนยัน)", 'en': "Order Information (Checkout)"},
    'table_number': {'th': "หมายเลขโต๊ะ 🔢 (บังคับกรอก)", 'en': "Table Number 🔢 (Required)"},
    'customer_name': {'th': "ชื่อลูกค้า 👤 (ไม่บังคับ)", 'en': "Customer Name 👤 (Optional)"},
    'confirm_order': {'th': "✅ ยืนยันการสั่งซื้อ", 'en': "✅ Confirm Order"},
    'order_success': {'th': "🎉 สั่งซื้อสำเร็จ! กรุณารอรับอาหาร", 'en': "🎉 Order Placed Successfully! Please wait for your food."},
    'required_table': {'th': "กรุณากรอกหมายเลขโต๊ะ", 'en': "Please enter the table number."},
    'cart_empty_checkout': {'th': "ตะกร้าสินค้าว่างเปล่า ไม่สามารถสั่งซื้อได้", 'en': "Cart is empty. Cannot place order."},
    'admin_title': {'th': "หน้าจัดการรายการอาหาร (หลังบ้าน)", 'en': "Menu Management (Admin Backend)"},
    'service_title': {'th': "👩‍🍳 หน้าบริการ (KDS)", 'en': "👩‍🍳 Service Display (KDS)"},
    'admin_login_label': {'th': "เข้าสู่ระบบผู้ดูแล", 'en': "Admin Login"},
    'service_login_label': {'th': "เข้าสู่ระบบบริการ", 'en': "Service Login"},
    'logout_all': {'th': "🚪 ออกจากระบบทั้งหมด", 'en': "🚪 Log out All"},
    'page_menu': {'th': "หน้าเมนู (ลูกค้า)", 'en': "Menu Page (Customer)"},
    'page_admin': {'th': "หน้าผู้ดูแล (Admin)", 'en': "Admin Page (Admin)"},
    'page_service': {'th': "หน้าบริการ (Service)", 'en': "Service Page (Service)"},
    'select_category': {'th': "เลือกหมวดหมู่:", 'en': "Select Category:"},
    'item_not_found': {'th': "ไม่พบรายการอาหารในหมวดหมู่", 'en': "No items found in this category"},
    'cart_button': {'th': "🛒 ตะกร้าสินค้า", 'en': "🛒 Shopping Cart"},
}

def T(key):
    """Simple translation function based on session state language."""
    lang = st.session_state.get('language', 'th')
    return TRANSLATIONS.get(key, {}).get(lang, key) # fallback to key if not found

# --- Supabase Client ---
@st.cache_resource
def init_connection():
    """Initializes and caches the Supabase connection."""
    try:
        url = os.getenv("SUPABASE_URL") 
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            url = st.secrets["supabase"]["SUPABASE_URL"]
            key = st.secrets["supabase"]["SUPABASE_KEY"]

        return create_client(url, key)
    except KeyError as e:
        st.error(f"Error: Missing Supabase secrets. Please check your secrets.toml file or Environment Variables. Details: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Error: Failed to initialize Supabase connection. Details: {e}")
        st.stop()

# เชื่อมต่อฐานข้อมูล
supabase = init_connection()

# --- Session State Initialization ---
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
    
if "service_logged_in" not in st.session_state:
    st.session_state.service_logged_in = False
    
if 'cart' not in st.session_state:
    st.session_state.cart = {}

if 'page' not in st.session_state:
    st.session_state.page = "Menu" # Page: Menu, Cart, Admin, Service

# *** เพิ่ม: สถานะภาษาเริ่มต้น (สามารถเปลี่ยนเป็น 'en' ได้ถ้าต้องการให้ default เป็นอังกฤษ) ***
if 'language' not in st.session_state:
    st.session_state.language = 'th'
    
# --- Navigation/State Functions ---
def set_page(new_page):
    """Function to change the current displayed page."""
    st.session_state.page = new_page
    st.rerun()
    
def clear_cart():
    st.session_state.cart = {}
    
def set_language(lang):
    """Function to change the language."""
    st.session_state.language = lang
    st.rerun()

# --- Database and Storage Functions (No Change) ---

@st.cache_data(ttl=10)
def load_menu_data_from_db():
    response = supabase.from_('menu').select('*').order('id', desc=False).execute()
    return pd.DataFrame(response.data)

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
        path_segments = image_url.split(f"/{BUCKET_NAME}/")
        if len(path_segments) < 2:
            st.warning("URL รูปภาพไม่ถูกต้อง ไม่สามารถลบได้")
            return
        file_name = path_segments[1].split('?')[0]
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
def show_login_page(role):
    # ใช้ T() เพื่อแปลชื่อหน้า Login
    login_key = 'admin_login_label' if role == "ผู้ดูแล" else 'service_login_label'
    st.sidebar.markdown(f"### {T(login_key)}")
    with st.sidebar.form(f"{role}_login_form"):
        username = st.text_input(f"ชื่อผู้ใช้ ({role})")
        password = st.text_input(f"รหัสผ่าน ({role})", type="password")
        submitted = st.form_submit_button(T('admin_login_label').replace("ผู้ดูแล", "").replace("Login", "").strip()) # ใช้ปุ่มสั้นๆ
        if submitted:
            if role == "ผู้ดูแล" and username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                set_page("Admin")
            elif role == "บริการ" and username == SERVICE_USERNAME and password == SERVICE_PASSWORD:
                st.session_state.service_logged_in = True
                set_page("Service")
            else:
                st.error(T('required_table').replace('หมายเลขโต๊ะ', 'Username/Password')) # ใช้ข้อความที่ใกล้เคียงไปก่อน


# --- CART CHECKOUT PAGE (หน้าใหม่) ---
def show_cart_page():
    """Renders the shopping cart content and checkout form as a dedicated page."""
    
    st.markdown(f"<h1 style='text-align: center;'>{T('title_cart')}</h1>", unsafe_allow_html=True)
    st.markdown("---")

    total_items = sum(item['quantity'] for item in st.session_state.cart.values())
    total_price = sum(item['price'] * item['quantity'] for item in st.session_state.cart.values())
    
    if not st.session_state.cart:
        st.info(T('cart_empty'))
        if st.button(T('back_to_menu'), key="back_from_empty_cart", use_container_width=True):
            set_page("Menu")
        return
        
    st.markdown(f"#### {T('items_ordered')} ({total_items} {T('item')})")
    st.markdown("---")

    # --- Display and Manage Items in the Cart (ในหน้าหลัก) ---
    col_header_name, col_header_qty, col_header_subtotal, col_header_remove = st.columns([3, 1.5, 2, 1])
    with col_header_name: st.markdown(f"**{T('item')}**")
    with col_header_qty: st.markdown(f"**{T('quantity')}**")
    with col_header_subtotal: st.markdown(f"**{T('subtotal')}**")
    with col_header_remove: st.markdown(f"**{T('remove')}**")
    st.divider()

    for menu_id, item in list(st.session_state.cart.items()): 
        
        col_name, col_qty, col_subtotal, col_remove = st.columns([3, 1.5, 2, 1])
        
        with col_name:
            st.markdown(f"**{item['name']}**")
        
        with col_qty:
            new_qty = st.number_input(
                T('quantity'), 
                min_value=0, 
                value=item['quantity'], 
                step=1,
                key=f"cart_qty_{menu_id}",
                label_visibility="collapsed",
            )
            
            if new_qty != item['quantity']:
                if new_qty <= 0:
                    del st.session_state.cart[menu_id]
                    st.rerun() 
                else:
                    st.session_state.cart[menu_id]['quantity'] = new_qty
                    st.rerun()
            
        with col_subtotal:
            # ใช้ T() สำหรับสกุลเงินได้
            currency_symbol = "฿" if st.session_state.language == 'th' else "THB"
            st.markdown(f"**{item['price'] * item['quantity']:,.0f} {currency_symbol}**")
            st.caption(f"({item['price']} {currency_symbol}/{T('quantity')})")
            
        with col_remove:
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            if st.button("🗑️", key=f"cart_remove_{menu_id}", help=T('remove')):
                del st.session_state.cart[menu_id]
                st.rerun() 
        
        st.markdown("---") 
            
    st.markdown(f"### **{T('total')}** **{total_price:,.0f} {currency_symbol}**")

    # --- Order Submission Form ---
    st.markdown("---")
    st.markdown(f"## {T('checkout_info')}")
    
    with st.form("order_form_cart_page"):
        table_number = st.text_input(T('table_number'), key="checkout_table")
        customer_name = st.text_input(T('customer_name'), key="checkout_name")
        
        col_back, col_submit = st.columns(2)
        
        with col_back:
            if st.form_submit_button(T('back_to_menu'), type="secondary"):
                set_page("Menu")
                
        with col_submit:
            submitted = st.form_submit_button(T('confirm_order'), type="primary")
        
        if submitted:
            if not table_number.strip():
                st.error(T('required_table'))
            elif not st.session_state.cart:
                st.error(T('cart_empty_checkout'))
            else:
                try:
                    place_order_to_db(table_number, customer_name, st.session_state.cart)
                    st.success(T('order_success'))
                    time.sleep(1) 
                    clear_cart()
                    set_page("Menu") 
                    st.rerun() 
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการบันทึกคำสั่งซื้อ: {e}")
                    

# --- App Pages (Admin, Service) ---

def show_admin_page():
    st.markdown(f"<h1 style='text-align: center;'>{T('admin_title')}</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # ... (ส่วน Admin Form ยังใช้ภาษาไทยหลัก) ...
    # หากต้องการแปล UI ส่วนนี้ด้วย ต้องเพิ่ม key ใน TRANSLATIONS

    if st.sidebar.button(T('logout_all').replace("ทั้งหมด", "ผู้ดูแล"), key="admin_logout_button", on_click=lambda: set_page("Menu")):
        st.session_state.admin_logged_in = False
        st.session_state.service_logged_in = False
        st.rerun()
        
    # --- UI Elements ใน Admin Page (แปลเฉพาะส่วนหลัก) ---
    menu_options_th = ["เพิ่มรายการใหม่", "แก้ไข/ลบรายการ"]
    menu_options_en = ["Add New Item", "Edit/Delete Item"]
    menu_options = menu_options_th if st.session_state.language == 'th' else menu_options_en
    choice = st.selectbox(T('select_category').replace("หมวดหมู่", "จัดการ:"), menu_options)

    if choice == menu_options[0]: # "เพิ่มรายการใหม่" / "Add New Item"
        st.subheader(menu_options[0])
        with st.form("add_form"):
            food_name = st.text_input("ชื่ออาหาร (ไทย/อังกฤษ)")
            price = st.number_input("ราคา (บาท)", min_value=0, step=1)
            category = st.selectbox("หมวดหมู่", CATEGORIES) 
            uploaded_file = st.file_uploader("อัปโหลดรูปภาพ", type=["jpg", "jpeg", "png"])
            submitted = st.form_submit_button(T('confirm_order').replace("ยืนยันการสั่งซื้อ", "บันทึกรายการ"))

            # ... (Logic การเพิ่มรายการ) ...
            if submitted:
                if food_name and price and category and uploaded_file:
                    image_url = upload_image_to_storage(uploaded_file)
                    if image_url:
                        add_menu_item_to_db(food_name, price, category, image_url) 
                        st.success("เพิ่มรายการอาหารใหม่สำเร็จแล้ว!")
                        st.rerun()
                else:
                    st.error("กรุณากรอกข้อมูลให้ครบถ้วนและอัปโหลดรูปภาพ")

    elif choice == menu_options[1]: # "แก้ไข/ลบรายการ" / "Edit/Delete Item"
        st.subheader(menu_options[1])
        load_menu_data_from_db.clear() 
        df_menu = load_menu_data_from_db()

        # ... (Logic การแก้ไข/ลบรายการ) ...
        if df_menu.empty:
            st.info("ไม่พบรายการอาหารในฐานข้อมูล")
            return
        
        if 'category' not in df_menu.columns:
            st.warning("กรุณาเพิ่มคอลัมน์ 'category' ในตาราง 'menu' ด้วย Type 'text' ก่อน")
            return

        item_names = df_menu['name'].tolist()
        selected_name = st.selectbox("เลือกรหัส/ชื่ออาหารที่ต้องการแก้ไข", item_names, key="select_item_to_edit")
        
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
                if st.form_submit_button(T('confirm_order').replace("ยืนยันการสั่งซื้อ", "บันทึกการแก้ไข")):
                    # ... (Logic การบันทึก) ...
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
                if st.form_submit_button(T('remove').replace("ลบ", "ลบรายการนี้")):
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
    st.markdown(f"<h1 style='text-align: center;'>{T('service_title')}</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # ... (ส่วน Service Page ยังใช้ภาษาไทยหลัก) ...
    if st.sidebar.button(T('logout_all').replace("ทั้งหมด", "บริการ"), key="service_logout_button", on_click=lambda: set_page("Menu")):
        st.session_state.service_logged_in = False
        st.session_state.admin_logged_in = False
        st.rerun()
    
    st.header(T('items_ordered').replace("ที่สั่งซื้อ", "ที่ใช้งานอยู่")) 
    
    if st.button("🔄 " + ("อัปเดตรายการ (Refresh)" if st.session_state.language == 'th' else "Update List (Refresh)"), key="refresh_orders"):
        st.rerun() 
    
    active_orders = load_active_orders()

    if not active_orders:
        st.info("ไม่มีรายการออเดอร์ใหม่ หรือออเดอร์ที่กำลังบริการอยู่")
        return

    df_orders = pd.DataFrame(active_orders)

    col_new, col_in_service = st.columns(2)
    
    with col_new:
        st.subheader("🔔 " + ("ออเดอร์ใหม่ (New Order)" if st.session_state.language == 'th' else "New Orders"))
        new_orders = df_orders[df_orders['status'] == 'New Order']
        
        if new_orders.empty:
            st.info("ไม่มีออเดอร์ใหม่")
            
        for i, order in new_orders.iterrows():
            order_id = order['id']
            st.markdown(f"**{T('table_number').split('(')[0].strip()}:** **{order['table_number']}** | **{T('customer_name').split('(')[0].strip()}:** {order['customer_name'] or 'Customer'}")
            st.caption(f"{('เวลาสั่ง' if st.session_state.language == 'th' else 'Time Ordered')}: {pd.to_datetime(order['created_at']).strftime('%H:%M:%S')}")
            st.markdown("---")
            
            items_data = order['items']
            if isinstance(items_data, str):
                 items_data = json.loads(items_data)

            item_list = ""
            for item in items_data:
                item_list += f"- {item['name']} (x{item['quantity']}) \n"
            st.text(item_list)
            
            if st.button("▶️ " + ("กำลังบริการ (Start Service)" if st.session_state.language == 'th' else "Start Service"), key=f"start_{order_id}"):
                update_order_status(order_id, 'In Service')
                st.rerun() 
            st.markdown("---")
            
    with col_in_service:
        st.subheader("⏳ " + ("กำลังบริการ (In Service)" if st.session_state.language == 'th' else "In Service"))
        in_service_orders = df_orders[df_orders['status'] == 'In Service']
        
        if in_service_orders.empty:
            st.info("ไม่มีออเดอร์ที่กำลังบริการ")

        for i, order in in_service_orders.iterrows():
            order_id = order['id']
            st.markdown(f"**{T('table_number').split('(')[0].strip()}:** **{order['table_number']}** | **{T('customer_name').split('(')[0].strip()}:** {order['customer_name'] or 'Customer'}")
            st.caption(f"{('เวลาสั่ง' if st.session_state.language == 'th' else 'Time Ordered')}: {pd.to_datetime(order['created_at']).strftime('%H:%M:%S')}")
            st.markdown("---")
            
            items_data = order['items']
            if isinstance(items_data, str):
                 items_data = json.loads(items_data)

            item_list = ""
            for item in items_data:
                item_list += f"- {item['name']} (x{item['quantity']}) \n"
            st.text(item_list)
            
            if st.button("✅ " + ("เสร็จสิ้น (Complete & Delete)" if st.session_state.language == 'th' else "Complete & Delete"), key=f"complete_{order_id}"):
                delete_order_from_db(order_id)
                st.rerun() 
            st.markdown("---")


# --- CUSTOMER MENU PAGE ---
def show_menu_page():
    """Display menu page for customers (with ordering and categories)."""
    
    # --- ปุ่มตะกร้าสินค้า (ด้านบนซ้าย) ---
    total_items = sum(item['quantity'] for item in st.session_state.cart.values())
    total_price = sum(item['price'] * item['quantity'] for item in st.session_state.cart.values())
    
    button_label = f"{T('cart_button')} ({total_items} {T('item')}, {total_price:,.0f} {'฿' if st.session_state.language == 'th' else 'THB'})"
    
    col_cart_button, col_title = st.columns([1, 4])
    
    with col_cart_button:
        if st.button(button_label, key="go_to_cart_page"):
             set_page("Cart")

    # --- Menu Display Logic ---
    with col_title:
        st.markdown(f"<h1 style='text-align: center;'>{T('title_menu')}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center;'>{T('subtitle_restaurant')}</h3>", unsafe_allow_html=True)
        
    st.markdown("---")

    load_menu_data_from_db.clear() 
    df_menu = load_menu_data_from_db()

    if df_menu.empty or 'category' not in df_menu.columns:
        st.info("ไม่พบรายการอาหาร หรือตาราง 'menu' ขาดคอลัมน์ 'category'")
        return

    # Category Filter
    st.markdown(f"**{T('select_category')}**", unsafe_allow_html=True)
    selected_category = st.radio("", CATEGORIES, horizontal=True, key="category_filter", label_visibility="collapsed")
    st.markdown("---")

    df_filtered = df_menu[df_menu['category'] == selected_category]
    if df_filtered.empty:
        st.info(f"{T('item_not_found')} **'{selected_category}'**")
        return

    # Display filtered items
    for i, row in df_filtered.iterrows():
        menu_id = row['id']
        
        col_img, col_data, col_order = st.columns([1.2, 2.8, 1]) 
        
        with col_img:
            image_url = row['image_url']
            st.markdown(
                f"""
                <img src="{image_url}" 
                     style="width: 150px; 
                            height: 150px; 
                            object-fit: cover; 
                            border-radius: 5px; 
                            margin-top: 5px; 
                            display: block; 
                            margin-left: auto; 
                            margin-right: auto;"> 
                """,
                unsafe_allow_html=True
            )
        
        with col_data:
            price_label = "Price" if st.session_state.language == 'en' else "ราคา"
            currency_symbol = "THB" if st.session_state.language == 'en' else "฿"
            st.markdown(f"""
                <div style='
                    display: flex; 
                    justify-content: space-between; 
                    align-items: center; 
                    margin-top: 65px; 
                    padding-right: 20px; 
                '>
                    <p style='margin: 0; font-size: 1.1em;'><b>{row['name']}</b></p>
                    <p style='margin: 0; color: #4CAF50;'>{price_label}: <b>{row['price']}</b> {currency_symbol}</p>
                </div>
            """, unsafe_allow_html=True)


        with col_order:
            current_quantity = st.session_state.cart.get(menu_id, {}).get('quantity', 0)
            quantity_key = f"qty_{menu_id}_{selected_category}"
            
            st.markdown("<div style='margin-top: 55px;'></div>", unsafe_allow_html=True)

            # Number Input (จำนวน)
            quantity = st.number_input(
                T('quantity'), 
                min_value=0, 
                value=current_quantity, 
                step=1, 
                key=quantity_key, 
                label_visibility="collapsed"
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


# --- Main App Logic (Navigation) ---

# 0. Language Switcher (Always at the top for customers)
col_lang_th, col_lang_en, col_spacer = st.columns([1, 1, 4])
with col_lang_th:
    if st.button("🇹🇭 Thai", key="lang_th_btn", disabled=(st.session_state.language == 'th')):
        set_language('th')
with col_lang_en:
    if st.button("🇬🇧 English", key="lang_en_btn", disabled=(st.session_state.language == 'en')):
        set_language('en')
st.markdown("---")

# 1. Sidebar Control
with st.sidebar:
    st.title(T('page_admin').replace("หน้าผู้ดูแล", "").strip())
    
    # แสดงเมนูเลือกหน้าสำหรับพนักงานที่เข้าสู่ระบบแล้ว
    if st.session_state.admin_logged_in or st.session_state.service_logged_in:
        
        # Logout button
        if st.button(T('logout_all'), key="global_logout_button"):
            st.session_state.admin_logged_in = False
            st.session_state.service_logged_in = False
            set_page("Menu")

        st.markdown("---")
        
        # Navigation สำหรับผู้ที่เข้าสู่ระบบแล้ว
        page_options = ["Menu", "Admin", "Service"]
        page_format = lambda x: {"Menu": T('page_menu'), "Admin": T('page_admin'), "Service": T('page_service')}[x]
        current_page_index = page_options.index(st.session_state.page) if st.session_state.page in page_options else 0
        
        selected_page = st.radio(T('select_category').replace("หมวดหมู่", "หน้าปฏิบัติงาน:"), 
                                 page_options, 
                                 format_func=page_format,
                                 index=current_page_index,
                                 key="employee_navigation")
        
        if selected_page != st.session_state.page:
            set_page(selected_page)
        
        st.markdown("---")

    # แสดง Login forms สำหรับผู้ที่ยังไม่ได้เข้าสู่ระบบ
    if not st.session_state.admin_logged_in and not st.session_state.service_logged_in:
        show_login_page("ผู้ดูแล")
        st.markdown("---")
        show_login_page("บริการ")


# 2. Main Content Rendering
if st.session_state.page == "Admin":
    if st.session_state.admin_logged_in:
        show_admin_page()
    else:
        set_page("Menu") 
        st.warning(T('admin_login_label'))

elif st.session_state.page == "Service":
    if st.session_state.service_logged_in:
        show_service_page()
    else:
        set_page("Menu")
        st.warning(T('service_login_label'))

elif st.session_state.page == "Cart":
    show_cart_page()
    
else: # Menu (หน้าเริ่มต้น)
    show_menu_page()