import sys
import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                            QLineEdit, QPushButton, QScrollArea, QLabel)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from chat_bubble import ChatBubble
from user_avatar import UserAvatarWidget
from emoji_picker import EmojiPicker
from styles import GLOBAL_STYLE, COLORS, GLOBAL_FONT

class PrivateChatWindow(QWidget):
    message_sent = pyqtSignal(str, str)  # 消息内容，目标用户
    
    def __init__(self, current_user, target_user, target_avatar=None, parent=None):
        super().__init__()
        self.current_user = current_user
        self.target_user = target_user
        self.target_avatar = target_avatar
        self.parent = parent
        self.emoji_picker = None
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(f'与 {self.target_user} 的私聊')
        self.setGeometry(200, 200, 800, 600)
        self.setStyleSheet(GLOBAL_STYLE)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 顶部用户信息
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        # 目标用户头像和信息
        target_avatar_widget = UserAvatarWidget(self.target_user, self.target_avatar)
        header_layout.addWidget(target_avatar_widget)
        
        # 添加用户状态标签
        status_label = QLabel("在线")
        status_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['success']};
                font-family: {GLOBAL_FONT};
                font-size: 14px;
                padding: 5px 10px;
                background-color: {COLORS['gray_lighter']};
                border-radius: 10px;
            }}
        """)
        header_layout.addWidget(status_label)
        
        header_layout.addStretch()
        
        # 关闭按钮
        close_btn = QPushButton('关闭')
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['gray']};
                padding: 8px 20px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['danger']};
            }}
        """)
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)
        
        layout.addLayout(header_layout)
        
        # 分隔线
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"""
            background-color: {COLORS['gray_light']};
            margin: 5px 0px;
        """)
        layout.addWidget(separator)
        
        # 聊天区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: white;
            }}
        """)
        
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setSpacing(10)
        self.chat_layout.addStretch()
        
        scroll.setWidget(self.chat_widget)
        layout.addWidget(scroll)
        
        # 输入区域
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        
        # 表情按钮
        self.emoji_btn = QPushButton('😊')
        self.emoji_btn.setFixedSize(40, 40)
        self.emoji_btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 20px;
                background-color: transparent;
                border: 1px solid {COLORS['gray_light']};
                border-radius: 20px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['gray_lighter']};
            }}
        """)
        self.emoji_btn.clicked.connect(self.show_emoji_picker)
        input_layout.addWidget(self.emoji_btn)
        
        # 输入框
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(f'给 {self.target_user} 发送消息...')
        self.input_field.setFont(QFont(GLOBAL_FONT.split(',')[0], 12))
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {COLORS['gray_light']};
                border-radius: 20px;
                padding: 10px 20px;
                background-color: {COLORS['gray_lighter']};
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['primary']};
                background-color: white;
            }}
        """)
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        
        # 发送按钮
        send_btn = QPushButton('发送')
        send_btn.setIcon(self.style().standardIcon(self.style().SP_CommandLink))
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)
        
        layout.addLayout(input_layout)
        self.setLayout(layout)
        
        # 创建表情选择器
        self.setup_emoji_picker()
    
    def setup_emoji_picker(self):
        """设置表情选择器"""
        self.emoji_picker = EmojiPicker(self.emoji_btn)
        self.emoji_picker.emoji_selected.connect(self.insert_emoji)
        self.emoji_picker.hide()  # 初始隐藏
    
    def show_emoji_picker(self):
        """显示表情选择器"""
        if self.emoji_picker and not self.emoji_picker.isVisible():
            self.emoji_picker.show()
    
    def insert_emoji(self, emoji):
        """插入表情到输入框"""
        current_text = self.input_field.text()
        cursor_pos = self.input_field.cursorPosition()
        new_text = current_text[:cursor_pos] + emoji + current_text[cursor_pos:]
        self.input_field.setText(new_text)
        self.input_field.setCursorPosition(cursor_pos + len(emoji))
        self.emoji_picker.hide()
        self.input_field.setFocus()
    
    def send_message(self):
        """发送消息"""
        text = self.input_field.text().strip()
        if text:
            self.message_sent.emit(text, self.target_user)
            self.input_field.clear()
            
            # 添加消息气泡到聊天区域
            bubble = ChatBubble(text, self.current_user, is_self=True, is_private=True)
            self.chat_layout.addWidget(bubble)
            self.scroll_to_bottom()
    
    def receive_message(self, text, sender):
        """接收消息"""
        bubble = ChatBubble(text, sender, is_self=False, is_private=True)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        self.scroll_to_bottom()
        
        # 如果窗口不是活动窗口，闪烁提醒
        if not self.isActiveWindow():
            self.flash_window()
    
    def scroll_to_bottom(self):
        """滚动到底部"""
        try:
            if self.chat_widget:
                QTimer.singleShot(50, lambda: self.chat_widget.parent().verticalScrollBar().setValue(
                    self.chat_widget.parent().verticalScrollBar().maximum()
                ))
        except Exception as e:
            print(f"滚动到底部失败: {e}")
    
    def flash_window(self):
        """闪烁窗口提醒"""
        try:
            # 设置窗口标题提醒
            self.setWindowTitle(f'【新消息】与 {self.target_user} 的私聊')
            # 激活窗口
            self.activateWindow()
            self.raise_()
        except Exception as e:
            print(f"闪烁窗口失败: {e}")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        if self.emoji_picker:
            self.emoji_picker.hide()
            self.emoji_picker.deleteLater()
        
        # 从父窗口的私聊窗口字典中移除
        if self.parent and hasattr(self.parent, 'private_chat_windows'):
            if self.target_user in self.parent.private_chat_windows:
                del self.parent.private_chat_windows[self.target_user]
        
        super().closeEvent(event)