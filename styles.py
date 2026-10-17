"""
全局样式定义文件
"""

# 全局字体设置
GLOBAL_FONT = '"Microsoft YaHei", Arial'

# 主题颜色
COLORS = {
    'primary': '#2196F3',
    'primary_dark': '#1976D2',
    'primary_darker': '#0D47A1',
    'success': '#4CAF50',
    'success_dark': '#388E3C',
    'warning': '#FFC107',
    'danger': '#FF5252',
    'gray': '#9E9E9E',
    'gray_light': '#E0E0E0',
    'gray_lighter': '#F5F5F5',
    'text': '#424242',
    'text_light': '#666666',
    'white': '#FFFFFF',
}

# 全局样式表
GLOBAL_STYLE = f"""
* {{
    font-family: {GLOBAL_FONT};
}}

QWidget {{
    font-family: {GLOBAL_FONT};
}}

QPushButton {{
    font-family: {GLOBAL_FONT};
    background-color: {COLORS['primary']};
    color: {COLORS['white']};
    border: none;
    border-radius: 5px;
    padding: 8px 15px;
    font-size: 13px;
    min-width: 80px;
}}

QPushButton:hover {{
    background-color: {COLORS['primary_dark']};
}}

QPushButton:pressed {{
    background-color: {COLORS['primary_darker']};
    padding: 9px 15px 7px 15px;
}}

QLineEdit {{
    font-family: {GLOBAL_FONT};
    border: 1px solid {COLORS['gray_light']};
    border-radius: 5px;
    padding: 8px;
    background-color: {COLORS['white']};
}}

QLineEdit:focus {{
    border: 2px solid {COLORS['primary']};
}}

QLabel {{
    font-family: {GLOBAL_FONT};
    color: {COLORS['text']};
}}

QTextEdit {{
    font-family: {GLOBAL_FONT};
    border: 1px solid {COLORS['gray_light']};
    border-radius: 5px;
    padding: 8px;
    background-color: {COLORS['white']};
    font-size: 13px;
}}

QScrollArea {{
    border: none;
    background-color: {COLORS['white']};
}}

QScrollBar:vertical {{
    border: none;
    background-color: {COLORS['gray_lighter']};
    width: 10px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['gray']};
    border-radius: 5px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['gray_light']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QComboBox {{
    font-family: {GLOBAL_FONT};
    border: 1px solid {COLORS['gray_light']};
    border-radius: 5px;
    padding: 5px;
    background-color: {COLORS['white']};
    min-width: 150px;
}}

QComboBox:hover {{
    border: 1px solid {COLORS['primary']};
}}

QComboBox QAbstractItemView {{
    font-family: {GLOBAL_FONT};
    background-color: {COLORS['white']};
    border: 1px solid {COLORS['gray_light']};
    selection-background-color: {COLORS['primary']};
    selection-color: {COLORS['white']};
}}

QMessageBox {{
    font-family: {GLOBAL_FONT};
}}

QMessageBox QPushButton {{
    font-family: {GLOBAL_FONT};
    min-width: 80px;
    padding: 8px 16px;
}}

QDialog {{
    font-family: {GLOBAL_FONT};
    background-color: {COLORS['white']};
    border-radius: 10px;
}}
"""

# 登录窗口样式
LOGIN_STYLE = f"""
QWidget {{
    font-family: {GLOBAL_FONT};
    background-color: {COLORS['white']};
}}

QLabel#title {{
    font-size: 24px;
    font-weight: bold;
    color: {COLORS['primary']};
    margin-bottom: 20px;
}}

QLabel#avatar_label {{
    font-size: 14px;
    color: {COLORS['text_light']};
}}

QLineEdit {{
    font-size: 14px;
    padding: 10px;
    margin: 5px 0;
}}

QPushButton#login_btn {{
    font-size: 14px;
    font-weight: bold;
    padding: 10px 20px;
    margin-top: 15px;
}}

QPushButton#avatar_btn {{
    background-color: {COLORS['gray']};
}}

QLabel#avatar_display {{
    border: 2px solid {COLORS['gray_light']};
    border-radius: 50px;
    background-color: {COLORS['gray_lighter']};
    font-family: {GLOBAL_FONT};
    font-size: 13px;
    color: {COLORS['text_light']};
}}
"""

# 聊天气泡样式
CHAT_BUBBLE_STYLE = f"""
QLabel#username {{
    color: {COLORS['text_light']};
    font-size: 12px;
    font-weight: bold;
    margin-left: 5px;
    font-family: {GLOBAL_FONT};
}}

QLabel#private_username {{
    color: {COLORS['danger']};
    font-size: 12px;
    font-weight: bold;
    margin-left: 5px;
    font-family: {GLOBAL_FONT};
}}

QLabel#message {{
    font-family: {GLOBAL_FONT};
    font-size: 14px;
    padding: 10px;
    background-color: {COLORS['primary']};
    color: {COLORS['white']};
    border-radius: 10px;
}}

QLabel#message_received {{
    background-color: {COLORS['gray_lighter']};
    color: {COLORS['text']};
}}
""" 