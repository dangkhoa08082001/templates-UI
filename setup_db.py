import sqlite3

# Kết nối đến cơ sở dữ liệu
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Mã SQL để tạo lại bảng với tên cột 'phone' thay cho 'phone_number'
create_table_query = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    address TEXT,
    confirmation_code TEXT
)
"""

# Thực thi mã SQL để tạo lại bảng
cursor.execute(create_table_query)

# Lưu thay đổi và đóng kết nối
conn.commit()
conn.close()

print("Successfully updated the users table structure.")
