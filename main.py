import sys
from PyQt5.QtWidgets import QApplication
from main_app import LoginWindow  # Import LoginWindow từ main_app.py

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
