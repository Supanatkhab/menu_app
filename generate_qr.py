import qrcode

# เปลี่ยนเป็นลิงก์เว็บของคุณหลัง deploy
url = "https://your-streamlit-app-url.com"

qr = qrcode.make(url)
qr.save("qr.png")
print("สร้าง QR Code สำเร็จ: qr.png")
