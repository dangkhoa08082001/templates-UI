import sys
import requests
from PyQt5.QtWidgets import QCheckBox
import concurrent.futures
import base64
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLineEdit, QLabel, QPushButton, 
                             QVBoxLayout, QWidget, QMessageBox, QFileDialog, QStackedWidget, 
                             QTableWidget, QTableWidgetItem, QListWidget, QAbstractItemView,QTextEdit)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from ui_sidebar import Ui_BaseWindow
from PyQt5.QtGui import QColor


class MainWindow(QMainWindow):
    def __init__(self, identifier):
        super(MainWindow, self).__init__()
        self.ui = Ui_BaseWindow()
        self.ui.setupUi(self)
        self.selected_images = []
        self.identifier = identifier
        self.avatar_path = None
        self.current_post_id = None
        self.ui.groupBox_3.setVisible(True)
        self.ui.stackedWidget.setCurrentWidget(self.ui.notifications_page)
        self.ui.notifications_1.clicked.connect(self.load_platforms)
        self.ui.notifications_2.clicked.connect(self.load_platforms)
        # Kết nối các nút điều hướng
        self.ui.dashboard_1.clicked.connect(self.show_dashboard_page)
        self.ui.dashboard_2.clicked.connect(self.show_dashboard_page)
        self.ui.profile_1.clicked.connect(self.show_profile_page)
        self.ui.profile_2.clicked.connect(self.show_profile_page)
        self.ui.messages_1.clicked.connect(self.show_messages_page)
        self.ui.messages_2.clicked.connect(self.show_messages_page)
        self.ui.notifications_1.clicked.connect(self.show_notifications_page)
        self.ui.notifications_2.clicked.connect(self.show_notifications_page)
        self.ui.settings_1.clicked.connect(self.show_settings_page)
        self.ui.settings_2.clicked.connect(self.show_settings_page)

        # Kết nối các nút trong dashboard_page
        self.ui.loadButton.clicked.connect(self.load_data)
        self.ui.addButton.clicked.connect(self.add_post)
        self.ui.editButton.clicked.connect(self.edit_post)
        self.ui.deleteButton.clicked.connect(self.delete_post)
        self.ui.addImageButton.clicked.connect(self.add_images)
        self.ui.uploadButton.clicked.connect(self.upload_images)
        self.ui.postWidget.itemSelectionChanged.connect(self.on_post_selected)
        
        self.ui.loadDataButton.clicked.connect(self.load_post_schedules)  # Thay đổi phương thức theo nhu cầu
        self.ui.saveButton_2.clicked.connect(self.save_selected_platforms)
        self.selected_row_id = None  # Biến để lưu ID của dòng được chọn trong tableWidget_2
        self.ui.tableWidget_2.itemChanged.connect(self.on_tableWidget_checkbox_changed)  # Kết nối sự kiện thay đổi checkbox
        for checkbox in self.get_platform_checkboxes():
            checkbox.stateChanged.connect(self.on_platformsWidget_checkbox_changed)
        self.titleLineEdit = QLineEdit(self)
        self.contentTextEdit = QTextEdit(self)
        self.urlLineEdit = QLineEdit(self)
        self.imageListWidget = QListWidget(self)
        # Cập nhật giao diện và đọc dữ liệu profile
        self.update_menu_display()
        self.read_profile_data()
        self.show_dashboard_page()

    def update_menu_display(self):
        self.ui.icon_name_widget.setVisible(True)
        self.ui.icon_only_widget.setVisible(False)

    def show_dashboard_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.dashboard_page)
        print("Navigating to Dashboard")

    def show_profile_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.profile_page)
        print("Navigating to Profile")

    def show_messages_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.messages_page)
        print("Navigating to Messages")

    def show_notifications_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.notifications_page)
        print("Navigating to Notifications")

    def show_settings_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.settings_page)
        print("Navigating to Settings")

    def toggle_edit_mode(self):
        is_editing = self.ui.editProfileButton.text() == 'Edit'
        self.ui.emailLineEdit.setReadOnly(not is_editing)
        self.ui.phoneLineEdit.setReadOnly(not is_editing)
        self.ui.addressLineEdit.setReadOnly(not is_editing)
        self.ui.addAvatarButton.setEnabled(is_editing)
        self.ui.saveButton.setEnabled(is_editing)

        if is_editing:
            self.ui.editProfileButton.setText('Cancel')
        else:
            self.ui.editProfileButton.setText('Edit')

    def add_button_clicked(self):
        # Code đẩy dữ liệu lên API...
        response = self.push_data_to_api()

        if response.status_code == 200:
            # Xóa dữ liệu sau khi đẩy thành công
            self.clear_input_fields()
        else:
            # Xử lý lỗi nếu cần
            print("Có lỗi xảy ra khi đẩy dữ liệu lên API.")



    def load_post_schedules(self):
        """Tải dữ liệu từ bảng post_schedules và hiển thị trong tableWidget_2."""
        try:
            # Gọi API để lấy dữ liệu post_schedules
            response = requests.get('http://localhost:8000/load_post_schedules', params={'identifier': self.identifier})
            if response.status_code == 200:
                # Nhận dữ liệu từ API
                post_schedules = response.json()
                # Cập nhật tableWidget_2 với dữ liệu nhận được
                self.update_post_schedules_widget(post_schedules)
            else:
                # Hiển thị thông báo lỗi nếu API trả về lỗi
                QMessageBox.warning(self, 'Error', f'Error: {response.status_code} - {response.json().get("message", "")}')
        except Exception as e:
            # Hiển thị thông báo lỗi nếu xảy ra lỗi trong quá trình gọi API
            QMessageBox.warning(self, 'Error', f'An error occurred while loading post schedules: {str(e)}')

    def update_post_schedules_widget(self, post_schedules):
        """Cập nhật tableWidget_2 với dữ liệu từ bảng post_schedules."""
        self.ui.tableWidget_2.setRowCount(len(post_schedules))
        self.ui.tableWidget_2.setColumnCount(7)  # Số cột: Checkbox, ID, Platform, Title, Content, Image URLs, Status
        self.ui.tableWidget_2.setHorizontalHeaderLabels(["Select", "ID", "Platform", "Title", "Content", "Image URLs", "Status"])

        for row, schedule in enumerate(post_schedules):
            checkbox = QCheckBox()
            checkbox.setObjectName(f"checkbox_{schedule['id']}")
            checkbox.stateChanged.connect(self.on_checkbox_state_changed)
            
            self.ui.tableWidget_2.setCellWidget(row, 0, checkbox)
            self.ui.tableWidget_2.setItem(row, 1, QTableWidgetItem(str(schedule['id'])))
            self.ui.tableWidget_2.setItem(row, 2, QTableWidgetItem(schedule['platforms']))
            self.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(schedule['post']['title']))
            self.ui.tableWidget_2.setItem(row, 4, QTableWidgetItem(schedule['post']['content']))
            self.ui.tableWidget_2.setItem(row, 5, QTableWidgetItem(schedule['post']['image_urls']))
            self.ui.tableWidget_2.setItem(row, 6, QTableWidgetItem(schedule['status']))
    def on_tableWidget_checkbox_changed(self, item):
        if item.column() == 0 and item.checkState() == Qt.Checked:  # Kiểm tra checkbox tại cột 0
            self.selected_row_id = self.ui.tableWidget_2.item(item.row(), 1).text()  # Lấy ID từ cột 1
            print(f"Selected row ID: {self.selected_row_id}")

    def on_platformsWidget_checkbox_changed(self, state):
        if self.selected_row_id:
            selected_platforms = [checkbox.text() for checkbox in self.get_platform_checkboxes() if checkbox.isChecked()]
            self.save_platforms_to_db(self.selected_row_id, selected_platforms)
        else:
            print("Vui lòng chọn một dòng trong tableWidget_2 trước khi chọn nền tảng.")
    def get_platform_checkboxes(self):
        # Trả về danh sách các checkbox trong platformsWidget
        return self.ui.platformsWidget.findChildren(QCheckBox)
    def save_platforms_to_db(self, row_id, platforms):
        print(f"Lưu các nền tảng {platforms} cho dòng ID {row_id}")
        # Gửi request API hoặc thực hiện lưu vào DB ở đây

    def on_checkbox_state_changed(self, state):
        """Xử lý sự kiện khi checkbox thay đổi trạng thái."""
        current_row = -1

        # Xác định dòng của checkbox được chọn
        for row in range(self.ui.tableWidget_2.rowCount()):
            checkbox = self.ui.tableWidget_2.cellWidget(row, 0)
            if checkbox.isChecked():
                current_row = row
                break

        # Nếu có checkbox được chọn
        if current_row != -1:
            # Bỏ chọn tất cả các checkbox khác và làm nổi bật dòng được chọn
            for row in range(self.ui.tableWidget_2.rowCount()):
                checkbox = self.ui.tableWidget_2.cellWidget(row, 0)
                if row == current_row:
                    self.highlight_row(row)
                else:
                    checkbox.setChecked(False)
                    self.remove_highlight(row)
        else:
            # Nếu không có checkbox nào được chọn, bỏ nổi bật tất cả các dòng
            for row in range(self.ui.tableWidget_2.rowCount()):
                self.remove_highlight(row)




    def highlight_row(self, row):
        """Làm nổi bật dòng."""
        for column in range(self.ui.tableWidget_2.columnCount()):
            item = self.ui.tableWidget_2.item(row, column)
            if item:
                item.setBackground(QColor('lightblue'))  # Màu nền nổi bật

    def remove_highlight(self, row):
        """Xóa nổi bật khỏi dòng."""
        for column in range(self.ui.tableWidget_2.columnCount()):
            item = self.ui.tableWidget_2.item(row, column)
            if item:
                item.setBackground(QColor('white'))  # Màu nền mặc định

    def create_checkboxes(self):
        """Tạo checkbox cho bảng và kết nối sự kiện."""
        for row in range(self.ui.tableWidget_2.rowCount()):
            checkbox = QCheckBox(self)
            checkbox.stateChanged.connect(self.on_checkbox_state_changed)
            self.ui.tableWidget_2.setCellWidget(row, 0, checkbox)

    def save_selected_platforms(self):
    # Bước 1: Lấy danh sách các nền tảng đã chọn
        selected_platforms = []
        for i in range(self.ui.platformsWidget.layout().count()):
            widget = self.ui.platformsWidget.layout().itemAt(i).widget()
            if isinstance(widget, QCheckBox) and widget.isChecked():
                selected_platforms.append(widget.text())

        # Bước 2: Cập nhật danh sách nền tảng vào tableWidget_2
        selected_row = None
        for row in range(self.ui.tableWidget_2.rowCount()):
            checkbox_item = self.ui.tableWidget_2.cellWidget(row, 0)  # Cột checkbox
            if checkbox_item and isinstance(checkbox_item, QCheckBox) and checkbox_item.isChecked():
                selected_row = row
                break

        if selected_row is not None:
            # Truy cập vào cột ID để lấy giá trị
            item = self.ui.tableWidget_2.item(selected_row, 1)  # Thay đổi từ cột 0 thành cột 1
            if item and item.text():
                post_schedule_id = item.text()
            else:
                QMessageBox.warning(self, 'Error', 'No data item found in the selected row')
                return

            # Cập nhật cột nền tảng với các nền tảng đã chọn
            self.ui.tableWidget_2.setItem(selected_row, 4, QTableWidgetItem(", ".join(selected_platforms)))

            # Bước 3: Lưu dữ liệu vào cơ sở dữ liệu thông qua API
            data = {
                'post_schedule_id': post_schedule_id,
                'platforms': selected_platforms
            }

            try:
                response = requests.post('http://localhost:8000/save_post_schedules', json=data)
                if response.status_code == 200:
                    QMessageBox.information(self, 'Success', 'Data saved successfully')
                else:
                    QMessageBox.warning(self, 'Error', f'Error: {response.status_code} - {response.json().get("message", "")}')
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'An error occurred while saving data: {str(e)}')
        else:
            QMessageBox.warning(self, 'Error', 'No row selected')



    def load_platforms(self):
    # Kiểm tra nếu platformsWidget chưa có layout, tạo một QVBoxLayout mới
        if self.ui.platformsWidget.layout() is None:
            layout = QVBoxLayout(self.ui.platformsWidget)
            self.ui.platformsWidget.setLayout(layout)
        else:
            layout = self.ui.platformsWidget.layout()

        # Clear any existing widgets in platformsWidget
        for i in reversed(range(layout.count())): 
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        try:
            response = requests.get('http://localhost:8000/platforms')
            if response.status_code == 200:
                platforms = response.json()

                for platform in platforms:
                    checkbox = QCheckBox(platform["name"], self.ui.platformsWidget)
                    checkbox.setObjectName(f"platform_{platform['id']}")
                    layout.addWidget(checkbox)

            else:
                QMessageBox.warning(self, 'Error', 'Failed to load platforms')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'An error occurred: {str(e)}')
    def display_platforms(self, platforms):
        """Hiển thị danh sách nền tảng với checkbox vào platformsWidget."""
        # Xóa tất cả các widget hiện có trong platformsWidget
        for i in reversed(range(self.ui.platformsWidget.layout().count())):
            widget = self.ui.platformsWidget.layout().itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        # Tạo layout mới cho platformsWidget nếu chưa có
        if not self.ui.platformsWidget.layout():
            layout = QVBoxLayout()
            self.ui.platformsWidget.setLayout(layout)
        else:
            layout = self.ui.platformsWidget.layout()

        # Thêm checkbox cho từng nền tảng
        for platform in platforms:
            checkbox = QCheckBox(platform["name"])
            checkbox.setObjectName(f"platform_{platform['id']}")
            layout.addWidget(checkbox)

    def save_profile_data(self):
        email = self.ui.emailLineEdit.text()
        phone = self.ui.phoneLineEdit.text()
        address = self.ui.addressLineEdit.text()

        if not email:
            QMessageBox.warning(self, 'Error', 'Email is required')
            return

        if not any([phone, address, self.avatar_path]):
            QMessageBox.warning(self, 'Error', 'At least one field (phone, address, avatar) must be provided')
            return

        url = 'http://localhost:8000/update_profile'
        files = {'avatar': open(self.avatar_path, 'rb')} if self.avatar_path else None
        data = {'email': email, 'phone': phone, 'address': address}

        try:
            response = requests.post(url, files=files, data=data)
            if response.status_code == 200:
                QMessageBox.information(self, 'Success', 'Profile updated successfully')
            else:
                QMessageBox.warning(self, 'Error', f'Error: {response.json().get("error", "Unknown error")}')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'An error occurred: {str(e)}')

    def select_avatar(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Select Avatar', '', 'Images (*.png *.jpg *.bmp)')
        if file_name:
            self.avatar_path = file_name
            pixmap = QPixmap(file_name)
            self.ui.avatarLabel.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))

    def read_profile_data(self):
        url = f'http://localhost:8000/get_user_profile/{self.identifier}'
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                self.ui.emailLineEdit.setText(data.get('email', ''))
                self.ui.phoneLineEdit.setText(data.get('phone', ''))
                self.ui.addressLineEdit.setText(data.get('address', ''))

                if 'avatar' in data:
                    avatar_data = base64.b64decode(data['avatar'])
                    pixmap = QPixmap()
                    pixmap.loadFromData(avatar_data)
                    self.ui.avatarLabel.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))
            else:
                QMessageBox.warning(self, 'Error', 'Failed to load profile data')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'An error occurred: {str(e)}')

    def load_data(self):
        try:
            response = requests.get('http://localhost:8000/load_posts', params={'identifier': self.identifier})
            if response.status_code == 200:
                data = response.json()
                self.update_post_widget(data)
            else:
                QMessageBox.warning(self, 'Error', f'Error: {response.status_code} - {response.json().get("message", "")}')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'An error occurred while loading data: {str(e)}')

    def update_post_widget(self, posts):
        self.ui.postWidget.setRowCount(len(posts))
        self.ui.postWidget.setColumnCount(4)  # Số cột: ID, Title, Content, Image URLs
        self.ui.postWidget.setHorizontalHeaderLabels(["ID", "Title", "Content", "Image URLs"])

        for row, post in enumerate(posts):
            self.ui.postWidget.setItem(row, 0, QTableWidgetItem(str(post['id'])))
            self.ui.postWidget.setItem(row, 1, QTableWidgetItem(post['title']))
            self.ui.postWidget.setItem(row, 2, QTableWidgetItem(post['content']))
            self.ui.postWidget.setItem(row, 3, QTableWidgetItem(post['image_urls']))

    def add_post(self):
        title = self.ui.titleLineEdit.text().strip()
        content = self.ui.contentTextEdit.toPlainText().strip()
        image_urls = self.ui.urlLineEdit.text().strip()
        identifier = self.identifier  # Đây là username hoặc email

        if not title or not content:
            QMessageBox.warning(self, 'Error', 'Title and content are required')
            return

        try:
            response = requests.post('http://localhost:8000/get_user_id', json={'identifier': identifier})
            if response.status_code == 200:
                user_id = response.json().get('user_id')
            else:
                QMessageBox.warning(self, 'Error', 'Unable to retrieve user ID')
                return

            url = 'http://localhost:8000/add_post'
            data = {
                'title': title,
                'content': content,
                'image_urls': image_urls,
                'user_id': user_id
            }

            response = requests.post(url, json=data)
            if response.status_code == 200:
                QMessageBox.information(self, 'Success', 'Post added successfully')
                self.load_data()
                self.clear_input_fields()  # Gọi hàm xóa dữ liệu sau khi thành công
            else:
                QMessageBox.warning(self, 'Error', f'Error: {response.status_code} - {response.json().get("message", "")}')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'An error occurred while adding the post: {str(e)}')

    def clear_input_fields(self):
        self.ui.titleLineEdit.clear()
        self.ui.contentTextEdit.clear()
        self.ui.urlLineEdit.clear()
        self.ui.imageListWidget.clear()



    def on_post_selected(self):
        selected_row = self.ui.postWidget.currentRow()
        if selected_row < 0:
            return

        # Lưu lại post_id để sử dụng trong việc chỉnh sửa
        self.current_post_id = self.ui.postWidget.item(selected_row, 0).text()
        # Tự động điền thông tin vào các trường để chỉnh sửa
        self.ui.titleLineEdit.setText(self.ui.postWidget.item(selected_row, 1).text())
        self.ui.contentTextEdit.setPlainText(self.ui.postWidget.item(selected_row, 2).text())
        self.ui.urlLineEdit.setText(self.ui.postWidget.item(selected_row, 3).text())

    def edit_post(self):
        if not self.current_post_id:
            QMessageBox.warning(self, 'Error', 'No post selected')
            return

        title = self.ui.titleLineEdit.text().strip()
        content = self.ui.contentTextEdit.toPlainText().strip()
        image_urls = self.ui.urlLineEdit.text().strip()
        identifier = self.identifier

        if not title or not content:
            QMessageBox.warning(self, 'Error', 'Title and content are required')
            return

        try:
            response = requests.post('http://localhost:8000/get_user_id', json={'identifier': identifier})
            if response.status_code == 200:
                user_id = response.json().get('user_id')
            else:
                QMessageBox.warning(self, 'Error', 'Unable to retrieve user ID')
                return

            url = 'http://localhost:8000/update_post'
            data = {
                'id': self.current_post_id,
                'title': title,
                'content': content,
                'image_urls': image_urls,
                'user_id': user_id
            }

            response = requests.post(url, json=data)
            if response.status_code == 200:
                QMessageBox.information(self, 'Success', 'Post updated successfully')
                self.load_data()
            else:
                QMessageBox.warning(self, 'Error', f'Error: {response.status_code} - {response.text}')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'An error occurred: {str(e)}')

    def delete_post(self):
        selected_row = self.ui.postWidget.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, 'Error', 'No post selected')
            return

        post_id = self.ui.postWidget.item(selected_row, 0).text()

        # Xác nhận người dùng trước khi xóa
        reply = QMessageBox.question(self, 'Confirm Delete', 'Are you sure you want to delete this post?', 
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        try:
            url = f'http://localhost:8000/delete_post/{post_id}'
            response = requests.delete(url)

            if response.status_code == 200:
                QMessageBox.information(self, 'Success', 'Post deleted successfully')
                self.load_data()
            else:
                error_message = response.json().get("message", "Unknown error")
                QMessageBox.warning(self, 'Error', f'Error: {error_message}')
        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, 'Error', f'An error occurred: {str(e)}')

    
    def add_images(self):
        file_names, _ = QFileDialog.getOpenFileNames(self, 'Select Images', '', 'Images (*.png *.jpg *.bmp)')
        if file_names:
            # Thêm các ảnh mới vào danh sách
            self.selected_images.extend(file_names)
            # Cập nhật QListWidget
            self.ui.imageListWidget.clear()
            self.ui.imageListWidget.addItems(self.selected_images)

    def upload_images(self):
        image_urls = []
        failed_images = []
    
    # Lấy tất cả các mục từ QListWidget
        file_names = [self.ui.imageListWidget.item(i).text() for i in range(self.ui.imageListWidget.count())]


        def upload_image(file_name):
            try:
                with open(file_name, 'rb') as img_file:
                    img_data = img_file.read()
                    img_base64 = base64.b64encode(img_data).decode()
                    response = requests.post('https://api.imgur.com/3/image', 
                                            headers={'Authorization': 'Client-ID daddc9d927e5acc'},
                                            data={'image': img_base64})
                    if response.status_code == 200:
                        img_url = response.json().get('data', {}).get('link', '')
                        return img_url
                    else:
                        print(f"Failed to upload image {file_name}: {response.json()}")
                        return None
            except Exception as e:
                print(f"An error occurred while uploading image {file_name}: {str(e)}")
                return None

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_file = {executor.submit(upload_image, file_name): file_name for file_name in file_names}
            for future in concurrent.futures.as_completed(future_to_file):
                file_name = future_to_file[future]
                img_url = future.result()
                if img_url:
                    image_urls.append(img_url)
                else:
                    failed_images.append(file_name)

        if image_urls:
            self.ui.urlLineEdit.setText(', '.join(image_urls))

        if failed_images:
            QMessageBox.warning(self, 'Upload Error', f"Failed to upload the following images: {', '.join(failed_images)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(identifier='1')  # Thay đổi identifier nếu cần
    window.show()
    sys.exit(app.exec_())
