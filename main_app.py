# main_app.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.uic import loadUi
import requests
import bcrypt
import sqlite3
from sidebar import MainWindow  # Import MainWindow từ sidebar.py

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

class LoginWindow(QMainWindow):
    def __init__(self):
        super(LoginWindow, self).__init__()
        loadUi("login.ui", self)
        self.loginButton.clicked.connect(self.login)
        self.forgotPasswordLink.linkActivated.connect(self.go_to_forgot_password)
        self.registerButton.clicked.connect(self.go_to_register)

    def login(self):
        username_or_email = self.usernameInput.text()
        password = self.passwordInput.text()
        response = requests.post('http://127.0.0.1:8000/login', json={
            'username_or_email': username_or_email,
            'password': password
        })

        if response.status_code == 200:
            user_data = response.json()
            identifier = user_data.get("username") or user_data.get("email")  # Lấy username hoặc email từ phản hồi
            self.open_sidebar(identifier)  # Truyền identifier vào MainWindow
        else:
            self.show_message_box("Error", "Invalid username or password")

    def open_sidebar(self, user_email):
        self.sidebar = MainWindow(user_email)  # Truyền user_email vào MainWindow
        self.sidebar.show()
        self.close()

    def go_to_register(self):
        self.register = RegisterWindow()
        self.register.show()
        self.close()

    def go_to_forgot_password(self):
        self.forgot_password = ForgotPasswordWindow()
        self.forgot_password.show()
        self.close()

    def show_message_box(self, title, message):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

class RegisterWindow(QMainWindow):
    def __init__(self):
        super(RegisterWindow, self).__init__()
        loadUi("register.ui", self)
        self.registerButton.clicked.connect(self.register)

    def register(self):
        username = self.usernameInput.text()
        password = self.passwordInput.text()
        email = self.emailInput.text()
        phone = self.phoneInput.text()
        address = self.addressInput.text()

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        data = {
            'username': username,
            'password': hashed_password.decode('utf-8'),
            'email': email,
            'phone': phone,
            'address': address
        }

        try:
            response = requests.post('http://127.0.0.1:8000/register', json=data)

            if response.status_code == 201:
                self.show_message_box("Success", "Registration successful. Please login.")
            else:
                self.show_message_box("Error", f"Failed to register. {response.json()['message']}")
        except Exception as e:
            print(f"Error during registration: {e}")
            self.show_message_box("Error", "Failed to register. Please try again later.")

    def show_message_box(self, title, message):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()
    def show_message_box(self, title, message):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

class ForgotPasswordWindow(QMainWindow):
    def __init__(self):
        super(ForgotPasswordWindow, self).__init__()
        loadUi("forgot-password-initial.ui", self)
        self.sendRequestButton.clicked.connect(self.send_request)

    def send_request(self):
        email = self.emailInput.text()

        try:
            response = requests.post('http://127.0.0.1:8000/forgot_password', json={'email': email})
            
            if response.status_code == 200:
                self.show_message_box("Success", "Confirmation code sent to email.")
                self.go_to_reset_password(email)
            else:
                self.show_message_box("Error", "Email not found in the database.")
        except Exception as e:
            print(f"Error sending request: {e}")
            self.show_message_box("Error", "Failed to send request. Please try again later.")

    def go_to_reset_password(self, user_email):
        self.reset_password = ResetPasswordWindow(user_email)
        self.reset_password.show()
        self.close()

    def show_message_box(self, title, message):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

class ResetPasswordWindow(QMainWindow):
    def __init__(self, user_email):
        super(ResetPasswordWindow, self).__init__()
        loadUi("reset-password.ui", self)

        self.user_email = user_email

        self.resetPasswordButton.clicked.connect(self.on_reset_password_clicked)

    def on_reset_password_clicked(self):
        new_password = self.newPasswordInput.text()
        re_entered_password = self.reEnterNewPasswordInput.text()
        entered_code = self.confirmationCodeInput.text()

        if not entered_code:
            self.show_message_box("Error", "Please enter confirmation code.")
            return

        try:
            entered_code = int(entered_code)
        except ValueError:
            self.show_message_box("Error", "Invalid confirmation code format.")
            return

        if new_password != re_entered_password:
            self.show_message_box("Error", "Passwords do not match.")
            return

        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

        try:
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute('UPDATE users SET password=? WHERE email=?', (hashed_password.decode('utf-8'), self.user_email))
            conn.commit()
            conn.close()
            self.show_message_box("Success", "Password updated successfully. Please login.")
            self.go_to_login()
        except Exception as e:
            print(f"Error updating password: {e}")
            self.show_message_box("Error", "Failed to update password. Please try again later.")

    def go_to_login(self):
        self.login = LoginWindow()
        self.login.show()
        self.close()

    def show_message_box(self, title, message):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()
