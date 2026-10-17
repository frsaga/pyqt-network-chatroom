from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QScrollArea, QGridLayout, QLabel)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from styles import GLOBAL_STYLE, COLORS, GLOBAL_FONT

class EmojiPicker(QWidget):
    emoji_selected = pyqtSignal(str)  # 表情被选中的信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        self.setWindowFlags(Qt.Popup)  # 设置为弹出窗口
        self.setStyleSheet(GLOBAL_STYLE)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # 常用表情列表
        self.emojis = [
            "😊", "😂", "🤣", "😍", "😒", "😘", "🥰", "😅",
            "😁", "😉", "😌", "😔", "😢", "😭", "😩", "😤",
            "😠", "😡", "🤔", "🤨", "😐", "😑", "😶", "🙄",
            "😏", "😣", "😥", "😮", "😯", "😪", "😫", "😴",
            "😌", "😛", "😜", "😝", "😋", "😚", "😙", "😗",
            "👍", "👎", "👌", "✌️", "🤞", "🤝", "👊", "✊",
            "❤️", "💔", "💖", "💗", "💓", "💙", "💚", "💛",
            "🌹", "🌺", "🌸", "🌼", "🌻", "🍀", "✨", "⭐",
        ]
        
        # 创建表情网格
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {COLORS['gray_light']};
                border-radius: 5px;
                background-color: white;
            }}
        """)
        
        container = QWidget()
        grid = QGridLayout()
        grid.setSpacing(5)
        
        # 添加表情按钮
        row = 0
        col = 0
        max_cols = 8
        
        for emoji in self.emojis:
            btn = QPushButton(emoji)
            btn.setFixedSize(40, 40)
            btn.setFont(QFont(GLOBAL_FONT.split(',')[0], 16))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: 1px solid transparent;
                    border-radius: 5px;
                    padding: 5px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['gray_lighter']};
                    border: 1px solid {COLORS['gray_light']};
                }}
            """)
            btn.clicked.connect(lambda checked, e=emoji: self.emoji_selected.emit(e))
            grid.addWidget(btn, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        container.setLayout(grid)
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        # 添加分类标签（预留功能）
        categories = QHBoxLayout()
        categories.setSpacing(10)
        
        category_labels = ["常用", "表情", "手势", "符号", "自然"]
        for category in category_labels:
            label = QLabel(category)
            label.setStyleSheet(f"""
                QLabel {{
                    color: {COLORS['text_light']};
                    padding: 5px 10px;
                    border-radius: 10px;
                }}
                QLabel:hover {{
                    background-color: {COLORS['gray_lighter']};
                    color: {COLORS['primary']};
                }}
            """)
            categories.addWidget(label)
        
        layout.addLayout(categories)
        self.setLayout(layout)
        
    def showEvent(self, event):
        """显示时调整位置"""
        super().showEvent(event)
        if self.parent():
            # 获取父组件（表情按钮）的位置
            parent_pos = self.parent().mapToGlobal(self.parent().rect().bottomLeft())
            # 设置选择器位置
            self.move(parent_pos.x(), parent_pos.y() + 5)
    
    def leaveEvent(self, event):
        """鼠标离开时隐藏"""
        self.hide() 