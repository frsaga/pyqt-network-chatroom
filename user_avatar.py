from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPainterPath, QFont
import os

class UserAvatarWidget(QWidget):
    user_clicked = pyqtSignal(str)  # 用户被点击信号
    
    def __init__(self, username, avatar_path=None, is_online=True, parent=None):
        super().__init__(parent)
        self.username = username
        self.avatar_path = avatar_path
        self.is_online = is_online
        self.initUI()
        
    def initUI(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 头像
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(40, 40)
        self.load_avatar()
        layout.addWidget(self.avatar_label)
        
        # 用户信息
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        # 用户名
        self.username_label = QLabel(self.username)
        self.username_label.setFont(QFont('Arial', 10, QFont.Bold))
        info_layout.addWidget(self.username_label)
        
        # 在线状态
        self.status_label = QLabel('在线' if self.is_online else '离线')
        self.status_label.setFont(QFont('Arial', 8))
        self.status_label.setStyleSheet(
            f"color: {'#4CAF50' if self.is_online else '#999'};"
        )
        info_layout.addWidget(self.status_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # 设置样式
        self.setStyleSheet("""
            UserAvatarWidget {
                border-radius: 5px;
                padding: 5px;
            }
            UserAvatarWidget:hover {
                background-color: #e3f2fd;
            }
        """)
        
    def load_avatar(self):
        """加载头像"""
        if self.avatar_path and os.path.exists(self.avatar_path):
            pixmap = QPixmap(self.avatar_path)
            if not pixmap.isNull():
                self.set_rounded_avatar(pixmap)
                return
        
        # 默认头像
        self.set_default_avatar()
    
    def set_rounded_avatar(self, pixmap):
        """设置圆形头像"""
        scaled_pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        
        rounded_pixmap = QPixmap(40, 40)
        rounded_pixmap.fill(Qt.transparent)
        
        painter = QPainter(rounded_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        path = QPainterPath()
        path.addEllipse(0, 0, 40, 40)
        painter.setClipPath(path)
        
        x = (40 - scaled_pixmap.width()) // 2
        y = (40 - scaled_pixmap.height()) // 2
        painter.drawPixmap(x, y, scaled_pixmap)
        painter.end()
        
        self.avatar_label.setPixmap(rounded_pixmap)
    
    def set_default_avatar(self):
        """设置默认头像"""
        self.avatar_label.setStyleSheet("""
            QLabel {
                border: 2px solid #ddd;
                border-radius: 20px;
                background-color: #f0f0f0;
                color: #666;
                font-weight: bold;
            }
        """)
        self.avatar_label.setText(self.username[0].upper())
        self.avatar_label.setAlignment(Qt.AlignCenter)
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            self.user_clicked.emit(self.username)
        super().mousePressEvent(event)
    
    def update_status(self, is_online):
        """更新在线状态"""
        self.is_online = is_online
        self.status_label.setText('在线' if is_online else '离线')
        self.status_label.setStyleSheet(
            f"color: {'#4CAF50' if is_online else '#999'};"
        )