import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QLabel, QMessageBox, QFileDialog)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPainterPath
import os
import shutil
from styles import GLOBAL_STYLE, LOGIN_STYLE, GLOBAL_FONT

class LoginWindow(QWidget):
    login_success = pyqtSignal(str, str, str)  # 登录成功信号：用户名，密码，头像路径

    def __init__(self):
        super().__init__()
        self.avatar_path = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('登录')
        self.setGeometry(300, 300, 400, 500)
        self.setStyleSheet(GLOBAL_STYLE + LOGIN_STYLE)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # 标题
        title = QLabel('聊天室登录')
        title.setObjectName('title')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 头像区域
        avatar_layout = QVBoxLayout()
        avatar_layout.setSpacing(10)
        
        avatar_label = QLabel('选择头像')
        avatar_label.setObjectName('avatar_label')
        avatar_label.setAlignment(Qt.AlignCenter)
        avatar_layout.addWidget(avatar_label)
        
        # 头像显示
        self.avatar_display = QLabel()
        self.avatar_display.setObjectName('avatar_display')
        self.avatar_display.setFixedSize(120, 120)
        self.avatar_display.setAlignment(Qt.AlignCenter)
        self.avatar_display.setText('点击选择\n头像')
        self.avatar_display.mousePressEvent = self.select_avatar
        
        avatar_container = QHBoxLayout()
        avatar_container.addStretch()
        avatar_container.addWidget(self.avatar_display)
        avatar_container.addStretch()
        avatar_layout.addLayout(avatar_container)
        
        layout.addLayout(avatar_layout)
        layout.addSpacing(20)
        
        # 用户名输入
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('请输入用户名')
        self.username_input.setFont(QFont(GLOBAL_FONT.split(',')[0], 12))
        self.username_input.textChanged.connect(self.load_user_avatar)
        layout.addWidget(self.username_input)
        
        # 密码输入
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('请输入密码')
        self.password_input.setFont(QFont(GLOBAL_FONT.split(',')[0], 12))
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        
        layout.addSpacing(30)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # 选择头像按钮
        avatar_btn = QPushButton('选择头像')
        avatar_btn.setObjectName('avatar_btn')
        avatar_btn.clicked.connect(self.select_avatar)
        button_layout.addWidget(avatar_btn)
        
        # 登录按钮
        login_btn = QPushButton('登录')
        login_btn.setObjectName('login_btn')
        login_btn.clicked.connect(self.handle_login)
        button_layout.addWidget(login_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 创建头像存储目录
        self.avatar_dir = 'user_avatars'
        if not os.path.exists(self.avatar_dir):
            os.makedirs(self.avatar_dir)

    def select_avatar(self, event=None):
        """选择头像"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, '选择头像', '', 
            'Image Files (*.png *.jpg *.jpeg *.bmp *.gif)'
        )
        
        if file_path:
            self.avatar_path = file_path
            self.display_avatar(file_path)

    def display_avatar(self, image_path):
        """显示头像"""
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            # 创建圆形头像
            scaled_pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            
            # 创建圆形遮罩
            rounded_pixmap = QPixmap(120, 120)
            rounded_pixmap.fill(Qt.transparent)
            
            painter = QPainter(rounded_pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            path = QPainterPath()
            path.addEllipse(0, 0, 120, 120)
            painter.setClipPath(path)
            
            # 居中绘制图片
            x = (120 - scaled_pixmap.width()) // 2
            y = (120 - scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, scaled_pixmap)
            painter.end()
            
            self.avatar_display.setPixmap(rounded_pixmap)

    def load_user_avatar(self):
        """根据用户名加载已保存的头像"""
        username = self.username_input.text().strip()
        if username:
            avatar_file = os.path.join(self.avatar_dir, f'{username}.png')
            if os.path.exists(avatar_file):
                self.avatar_path = avatar_file
                self.display_avatar(avatar_file)
            else:
                # 重置头像显示
                self.avatar_display.clear()
                self.avatar_display.setText('点击选择\n头像')
                self.avatar_path = None

    def save_user_avatar(self, username):
        """保存用户头像"""
        if self.avatar_path and username:
            avatar_file = os.path.join(self.avatar_dir, f'{username}.png')
            try:
                # 如果是新选择的头像，复制到用户目录
                if self.avatar_path != avatar_file:
                    shutil.copy2(self.avatar_path, avatar_file)
                return avatar_file
            except Exception as e:
                print(f"保存头像失败: {e}")
        return None

    def handle_login(self):
        """处理登录"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, '提示', '用户名和密码不能为空！', QMessageBox.Ok)
            return
        
        # 保存用户头像
        avatar_path = self.save_user_avatar(username)
        
        # 发送登录成功信号
        self.login_success.emit(username, password, avatar_path or '')
        self.hide()