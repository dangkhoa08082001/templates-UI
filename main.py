import sys
from PyQt5.QtWidgets import QApplication
from sidebar import MySideBar


app = QApplication(sys.argv)
window = MySideBar()
window.show()
sys.exit(app.exec())
