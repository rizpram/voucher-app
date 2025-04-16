from flask import Flask, render_template, request
import sqlite3
import uuid
import qrcode
import os

app = Flask(__name__)

# Setup DB
def get_db():
    conn = sqlite3.connect('vouchers.db')
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS vouchers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            amount INTEGER DEFAULT 80000,
            is_used INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

# Generate vouchers
def generate_vouchers(n):
    os.makedirs('static/qrcodes', exist_ok=True)
    conn = get_db()
    c = conn.cursor()
    for _ in range(n):
        code = str(uuid.uuid4())[:8].upper()
        c.execute("INSERT INTO vouchers (code) VALUES (?)", (code,))
        img = qrcode.make(f"https://your-app-name.onrender.com/redeem/{code}")
        img.save(f"static/qrcodes/{code}.png")
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT code, is_used FROM vouchers")
    vouchers = c.fetchall()
    return render_template('index.html', vouchers=vouchers)

@app.route('/redeem/<code>')
def redeem(code):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT is_used FROM vouchers WHERE code = ?", (code,))
    result = c.fetchone()
    if not result:
        return "❌ Voucher tidak ditemukan"
    elif result[0] == 1:
        return "⚠️ Voucher sudah digunakan"
    else:
        c.execute("UPDATE vouchers SET is_used = 1 WHERE code = ?", (code,))
        conn.commit()
        return "✅ Voucher berhasil digunakan. Senilai Rp80.000"

if __name__ == '__main__':
    init_db()
    # generate_vouchers(150)  # Uncomment sekali untuk buat voucher
    app.run(host="0.0.0.0", port=10000)
