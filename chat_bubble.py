from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPainterPath, QColor, QPen, QBrush, QFont
from styles import CHAT_BUBBLE_STYLE, COLORS, GLOBAL_FONT

class ChatBubble(QWidget):
    def __init__(self, text, sender, is_self=True, is_private=False, is_system=False, timestamp=None, parent=None):
        super().__init__(parent)
        self.text = text
        self.sender = sender
        self.is_self = is_self
        self.is_private = is_private
        self.is_system = is_system
        self.timestamp = timestamp
        self.msg_label = None
        self.initUI()

    def initUI(self):
        self.setStyleSheet(CHAT_BUBBLE_STYLE)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.setSpacing(2)
        
        # 用户名标签
        if not self.is_self and not self.is_system:
            header_layout = QHBoxLayout()
            header_layout.setSpacing(5)
            
            self.username_label = QLabel(self.sender)
            self.username_label.setFont(QFont(GLOBAL_FONT.split(',')[0], 10))
            if self.is_private:
                self.username_label.setStyleSheet(f"""
                    QLabel {{
                        color: {COLORS['danger']};
                        font-weight: bold;
                        margin-left: 5px;
                    }}
                """)
                self.username_label.setText(f"{self.sender} (私聊)")
            else:
                self.username_label.setStyleSheet(f"""
                    QLabel {{
                        color: {COLORS['text_light']};
                        font-weight: bold;
                        margin-left: 5px;
                    }}
                """)
            header_layout.addWidget(self.username_label)
            
            # 添加时间戳（如果有）
            if self.timestamp:
                time_label = QLabel(self.timestamp)
                time_label.setFont(QFont(GLOBAL_FONT.split(',')[0], 9))
                time_label.setStyleSheet(f"""
                    QLabel {{
                        color: {COLORS['text_light']};
                        margin-left: 10px;
                    }}
                """)
                header_layout.addWidget(time_label)
            
            header_layout.addStretch()
            main_layout.addLayout(header_layout)
        
        # 消息气泡布局
        bubble_layout = QHBoxLayout()
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加弹性空间（根据是否是自己发送的消息决定位置）
        if self.is_self:
            bubble_layout.addStretch()
        
        # 创建消息内容标签
        self.msg_label = QLabel(self.text)
        self.msg_label.setFont(QFont(GLOBAL_FONT.split(',')[0], 12))
        self.msg_label.setWordWrap(True)
        self.msg_label.setMaximumWidth(400)
        
        # 设置不同类型消息的样式
        if self.is_system:
            # 系统消息样式
            self.msg_label.setStyleSheet(f"""
                QLabel {{
                    color: {COLORS['text_light']};
                    background-color: {COLORS['gray_lighter']};
                    border: 1px solid {COLORS['gray_light']};
                    border-radius: 10px;
                    padding: 8px 12px;
                    font-size: 12px;
                }}
            """)
            # 系统消息居中显示
            bubble_layout.addStretch()
        elif self.is_self:
            # 自己发送的消息样式
            if self.is_private:
                # 私聊消息样式
                self.msg_label.setStyleSheet(f"""
                    QLabel {{
                        color: white;
                        background-color: {COLORS['danger']};
                        border-radius: 10px;
                        padding: 8px 12px;
                    }}
                """)
            else:
                # 普通消息样式
                self.msg_label.setStyleSheet(f"""
                    QLabel {{
                        color: white;
                        background-color: {COLORS['primary']};
                        border-radius: 10px;
                        padding: 8px 12px;
                    }}
                """)
        else:
            # 他人发送的消息样式
            if self.is_private:
                # 私聊消息样式
                self.msg_label.setStyleSheet(f"""
                    QLabel {{
                        color: {COLORS['text']};
                        background-color: {COLORS['gray_lighter']};
                        border: 1px solid {COLORS['danger']};
                        border-radius: 10px;
                        padding: 8px 12px;
                    }}
                """)
            else:
                # 普通消息样式
                self.msg_label.setStyleSheet(f"""
                    QLabel {{
                        color: {COLORS['text']};
                        background-color: {COLORS['gray_lighter']};
                        border: 1px solid {COLORS['gray_light']};
                        border-radius: 10px;
                        padding: 8px 12px;
                    }}
                """)
        
        bubble_layout.addWidget(self.msg_label)
        
        if not self.is_self and not self.is_system:
            bubble_layout.addStretch()
        
        main_layout.addLayout(bubble_layout)
        self.setLayout(main_layout)
    
    def paintEvent(self, event):
        """自定义绘制事件，添加气泡尾巴"""
        super().paintEvent(event)
        
        if self.msg_label is None or self.is_system:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 获取消息标签的位置和大小
        rect = self.msg_label.geometry()
        
        # 创建气泡尾巴路径
        path = QPainterPath()
        if self.is_self:
            # 右侧尾巴
            path.moveTo(rect.right() - 5, rect.top() + 10)
            path.lineTo(rect.right() + 5, rect.top() + 15)
            path.lineTo(rect.right() - 5, rect.top() + 20)
        else:
            # 左侧尾巴
            path.moveTo(rect.left() + 5, rect.top() + 10)
            path.lineTo(rect.left() - 5, rect.top() + 15)
            path.lineTo(rect.left() + 5, rect.top() + 20)
        
        # 设置画笔和画刷颜色
        if self.is_self:
            if self.is_private:
                color = QColor(COLORS['danger'])
            else:
                color = QColor(COLORS['primary'])
        else:
            color = QColor(COLORS['gray_lighter'])
        
        # 设置画笔和画刷
        painter.setPen(QPen(color, 1))
        painter.setBrush(QBrush(color))