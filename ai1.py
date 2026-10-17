import sys
import os
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QTextEdit, 
                            QLineEdit, QPushButton, QLabel, QScrollArea,
                            QHBoxLayout, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor

# 替换为你的 Qwen API Key（Token）
API_KEY = os.environ.get("QWEN_API_KEY", "")
QWEN_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

class MessageWidget(QFrame):
    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent)
        self.init_ui(text, is_user)
    
    def init_ui(self, text, is_user):
        layout = QHBoxLayout()
        
        if is_user:
            layout.addStretch()
        
        # 消息气泡
        message = QLabel(text)
        message.setWordWrap(True)
        message.setMaximumWidth(400)
        message.setStyleSheet(f"""
            QLabel {{
                background-color: {'#2196F3' if is_user else '#f0f0f0'};
                color: {'white' if is_user else 'black'};
                border-radius: 15px;
                padding: 10px 15px;
                font-size: 14px;
            }}
        """)
        layout.addWidget(message)
        
        if not is_user:
            layout.addStretch()
        
        self.setLayout(layout)

class QwenAssistant(QWidget):
    def __init__(self):
        super().__init__()
        self.chat_history_list = []  # 用于存储对话上下文
        self.initUI()

    def initUI(self):
        self.setWindowTitle("通义千问助手")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                font-family: "Microsoft YaHei", Arial;
            }
            QScrollArea {
                border: none;
                background-color: white;
            }
            QTextEdit {
                border: none;
                background-color: white;
                font-size: 14px;
            }
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 20px;
                padding: 10px 15px;
                font-size: 14px;
                background-color: #f5f5f5;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
                background-color: white;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)

        # 主布局
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_layout = QHBoxLayout()
        title_label = QLabel("通义千问 AI 助手")
        title_label.setStyleSheet("""
            QLabel {
                color: #1976D2;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        # 聊天区域
        chat_container = QWidget()
        self.chat_layout = QVBoxLayout(chat_container)
        self.chat_layout.setSpacing(15)
        self.chat_layout.addStretch()

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidget(chat_container)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #bdbdbd;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #757575;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        layout.addWidget(scroll)

        # 底部输入区域
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("输入你的问题...")
        self.input_field.returnPressed.connect(self.send_message)
        bottom_layout.addWidget(self.input_field)

        self.send_button = QPushButton("发送")
        self.send_button.setFixedWidth(100)
        self.send_button.clicked.connect(self.send_message)
        bottom_layout.addWidget(self.send_button)

        layout.addLayout(bottom_layout)
        self.setLayout(layout)

        # 添加欢迎消息
        self.add_message("你好！我是通义千问AI助手，请问有什么我可以帮你的吗？", False)

    def add_message(self, text, is_user=True):
        message_widget = MessageWidget(text, is_user)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, message_widget)
        
        # 滚动到底部
        QApplication.processEvents()
        scroll_area = self.findChild(QScrollArea)
        vsb = scroll_area.verticalScrollBar()
        vsb.setValue(vsb.maximum())

    def send_message(self):
        user_input = self.input_field.text().strip()
        if not user_input:
            return

        # 显示用户消息
        self.add_message(user_input, True)
        self.input_field.clear()

        # 添加到上下文中
        self.chat_history_list.append({"role": "user", "content": user_input})

        try:
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            body = {
                "model": "qwen-turbo",
                "input": {
                    "messages": self.chat_history_list
                },
                "parameters": {
                    "temperature": 0.7
                }
            }

            response = requests.post(QWEN_API_URL, headers=headers, json=body)
            result = response.json()

            ai_reply = result["output"]["text"].strip()
            self.add_message(ai_reply, False)

            # 添加 AI 回复到上下文中
            self.chat_history_list.append({"role": "assistant", "content": ai_reply})

        except Exception as e:
            error_message = f"获取回复失败：{str(e)}"
            self.add_message(error_message, False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    assistant = QwenAssistant()
    assistant.show()
    sys.exit(app.exec_())
