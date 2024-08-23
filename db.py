import sqlite3

def create_facebook_table():
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Xóa bảng cũ nếu cần
        cursor.execute('DROP TABLE IF EXISTS facebook_data')

        # Tạo bảng mới với khóa ngoại
        cursor.execute('''
            CREATE TABLE facebook_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                facebook_name TEXT NOT NULL,
                uid TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()
        conn.close()
        print("Table 'facebook_data' created successfully with foreign key.")
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")

if __name__ == '__main__':
    create_facebook_table()
