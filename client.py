import sys
import socket
import json
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QTextEdit, QLineEdit, QPushButton,
                            QFileDialog, QScrollArea, QMessageBox, QListWidget,
                            QSplitter, QLabel, QComboBox, QDialog, QTableWidget,
                            QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QTimer
from login import LoginWindow
from chat_bubble import ChatBubble
from user_avatar import UserAvatarWidget
from private_chat import PrivateChatWindow
from file_manager import FileManagerWindow
from styles import GLOBAL_STYLE, COLORS, GLOBAL_FONT
import os
from datetime import datetime
import shutil
from PyQt5.QtGui import QColor, QFont

# 导入AI助手
from ai1 import QwenAssistant
from emoji_picker import EmojiPicker

class SignalBus(QObject):
    message_received = pyqtSignal(str, str, bool)  # 消息内容，发送者，是否私聊
    file_received = pyqtSignal(str, str, bytes)  # 文件名，发送者，文件数据
    user_list_updated = pyqtSignal(list)  # 在线用户列表更新
    chat_history_received = pyqtSignal(list)  # 聊天历史记录

class ChatClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.socket = None
        self.username = None
        self.user_avatar = None
        self.signal_bus = SignalBus()
        self.ai_assistant = QwenAssistant()
        self.current_chat_target = "所有人"  # 当前聊天对象
        self.private_chat_windows = {}  # 私聊窗口字典
        self.user_avatars = {}  # 用户头像路径字典
        self.emoji_picker = None  # 表情选择器
        
        # 创建必要的目录
        self.setup_directories()
        
        # 设置全局样式表
        self.setStyleSheet(GLOBAL_STYLE)
        
        self.initUI()
        self.show_login()

        # 连接信号
        self.setup_signals()

    def setup_directories(self):
        """创建必要的目录"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 创建聊天记录目录
        self.chat_log_dir = os.path.join(base_dir, "chat_logs")
        if not os.path.exists(self.chat_log_dir):
            os.makedirs(self.chat_log_dir)
            
        # 创建下载目录
        self.download_dir = os.path.join(base_dir, "downloads")
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        
        # 创建文件存储目录
        self.files_dir = os.path.join(base_dir, "files")
        if not os.path.exists(self.files_dir):
            os.makedirs(self.files_dir)
        
        # 文件列表初始化
        self.file_list = []

    def setup_signals(self):
        """设置信号连接"""
        self.signal_bus.message_received.connect(self.display_message)
        self.signal_bus.file_received.connect(self.handle_file_received)
        self.signal_bus.user_list_updated.connect(self.update_user_list)
        self.signal_bus.chat_history_received.connect(self.display_chat_history)

    def initUI(self):
        """初始化用户界面"""
        self.setWindowTitle('聊天室')
        self.setGeometry(100, 100, 1200, 800)

        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建垂直布局作为主布局
        main_vertical_layout = QVBoxLayout(central_widget)
        main_vertical_layout.setContentsMargins(20, 20, 20, 20)
        main_vertical_layout.setSpacing(15)
        
        # 创建工具栏
        self.setup_toolbar(main_vertical_layout)
        
        # 创建聊天区域
        self.setup_chat_area(main_vertical_layout)

    def setup_toolbar(self, parent_layout):
        """设置工具栏"""
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(10)
        
        # 工具栏标题
        title_label = QLabel('聊天室')
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['primary']};
                font-size: 20px;
                font-weight: bold;
                font-family: {GLOBAL_FONT};
            }}
        """)
        toolbar_layout.addWidget(title_label)
        
        toolbar_layout.addStretch()
        
        # 历史记录按钮
        history_btn = QPushButton("历史记录")
        history_btn.clicked.connect(self.show_history_dialog)
        toolbar_layout.addWidget(history_btn)
        
        # 文件管理按钮
        file_manager_btn = QPushButton("文件管理")
        file_manager_btn.clicked.connect(self.show_file_manager)
        toolbar_layout.addWidget(file_manager_btn)
        
        # AI助手按钮
        ai_btn = QPushButton("AI助手")
        ai_btn.clicked.connect(self.toggle_ai_assistant)
        toolbar_layout.addWidget(ai_btn)
        
        parent_layout.addLayout(toolbar_layout)

    def setup_chat_area(self, parent_layout):
        """设置聊天区域"""
        chat_layout = QHBoxLayout()
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {COLORS['gray_light']};
                width: 2px;
            }}
        """)
        
        # 左侧：在线用户列表
        left_widget = self.setup_user_list()
        left_widget.setMaximumWidth(250)
        splitter.addWidget(left_widget)
        
        # 右侧：聊天区域
        right_widget = self.setup_chat_widget()
        splitter.addWidget(right_widget)
        
        # 设置分割器初始位置
        splitter.setSizes([250, 950])
        
        chat_layout.addWidget(splitter)
        parent_layout.addLayout(chat_layout)

    def setup_user_list(self):
        """设置用户列表"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 在线用户标题
        users_label = QLabel("在线用户")
        users_label.setStyleSheet(f"""
            QLabel {{
                font-family: {GLOBAL_FONT};
                font-size: 16px;
                font-weight: bold;
                color: {COLORS['text']};
                padding: 10px;
                background-color: {COLORS['gray_lighter']};
                border-radius: 5px;
                margin-bottom: 10px;
            }}
        """)
        left_layout.addWidget(users_label)
        
        # 在线用户列表容器
        self.users_scroll = QScrollArea()
        self.users_scroll.setWidgetResizable(True)
        self.users_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.users_widget = QWidget()
        self.users_layout = QVBoxLayout(self.users_widget)
        self.users_layout.setSpacing(5)
        self.users_layout.addStretch()
        
        self.users_scroll.setWidget(self.users_widget)
        left_layout.addWidget(self.users_scroll)
        
        return left_widget

    def setup_chat_widget(self):
        """设置聊天窗口"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        # 聊天对象选择
        chat_target_layout = QHBoxLayout()
        chat_target_label = QLabel("聊天对象:")
        chat_target_label.setFont(QFont(GLOBAL_FONT.split(',')[0], 12))
        
        self.chat_target_combo = QComboBox()
        self.chat_target_combo.setFont(QFont(GLOBAL_FONT.split(',')[0], 12))
        self.chat_target_combo.addItem("所有人")
        self.chat_target_combo.currentTextChanged.connect(self.change_chat_target)
        
        chat_target_layout.addWidget(chat_target_label)
        chat_target_layout.addWidget(self.chat_target_combo)
        chat_target_layout.addStretch()
        right_layout.addLayout(chat_target_layout)

        # 聊天区域
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setSpacing(10)
        self.chat_layout.addStretch()
        
        self.chat_scroll.setWidget(self.chat_widget)
        right_layout.addWidget(self.chat_scroll)

        # 底部输入区域
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)
        
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
        bottom_layout.addWidget(self.emoji_btn)
        
        # 文件选择按钮
        self.file_btn = QPushButton('发送文件')
        self.file_btn.setIcon(self.style().standardIcon(self.style().SP_FileIcon))
        self.file_btn.clicked.connect(self.select_file)
        bottom_layout.addWidget(self.file_btn)
        
        # 输入框
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText('输入消息...')
        self.input_field.setFont(QFont(GLOBAL_FONT.split(',')[0], 12))
        self.input_field.returnPressed.connect(self.send_message)
        bottom_layout.addWidget(self.input_field)
        
        # 发送按钮
        send_btn = QPushButton('发送')
        send_btn.setIcon(self.style().standardIcon(self.style().SP_CommandLink))
        send_btn.clicked.connect(self.send_message)
        bottom_layout.addWidget(send_btn)
        
        right_layout.addLayout(bottom_layout)
        
        # 创建表情选择器
        self.setup_emoji_picker()
        
        return right_widget

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

    def show_login(self):
        self.login_window = LoginWindow()
        self.login_window.login_success.connect(self.handle_login)
        self.login_window.show()

    def connect_to_server(self, username, password, avatar_path):
        """连接到服务器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(('127.0.0.1', 5000))
            
            # 发送登录信息（包含头像路径）
            login_data = {
                'username': username,
                'password': password,
                'avatar': avatar_path
            }
            self.socket.send(json.dumps(login_data).encode())
            
            # 接收登录响应
            response = json.loads(self.socket.recv(1024).decode())
            if response.get('status') == 'success':
                # 启动接收消息的线程
                thread = threading.Thread(target=self.receive_messages)
                thread.daemon = True
                thread.start()
                
                # 加载历史记录
                self.load_chat_history()
                return True
            else:
                QMessageBox.warning(self, '错误', '登录失败！')
                self.login_window.show()
                return False
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'连接服务器失败: {str(e)}')
            self.login_window.show()
            return False

    def handle_login(self, username, password, avatar_path):
        """处理登录成功"""
        self.username = username
        self.user_avatar = avatar_path
        if self.connect_to_server(username, password, avatar_path):
            self.show()

    def handle_disconnect(self):
        """处理断开连接"""
        try:
            # 关闭socket
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
                self.socket = None
            
            # 显示重连按钮或消息
            self.display_message("与服务器的连接已断开", "系统")
            
            # 禁用发送按钮和输入框
            self.input_field.setEnabled(False)
            self.send_button.setEnabled(False)
            
            # 显示重连对话框
            reply = QMessageBox.question(self, '连接断开',
                                       "与服务器的连接已断开，是否重新连接？",
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.Yes)
            
            if reply == QMessageBox.Yes:
                # 重新连接
                if self.connect_to_server(self.username, "", self.user_avatar):
                    # 恢复输入框和按钮
                    self.input_field.setEnabled(True)
                    self.send_button.setEnabled(True)
                    self.display_message("重新连接成功", "系统")
                else:
                    self.show_login()
            else:
                self.close()
                
        except Exception as e:
            print(f"处理断开连接失败: {e}")
            self.show_login()

    def closeEvent(self, event):
        """窗口关闭事件"""
        try:
            reply = QMessageBox.question(self, '确认退出',
                                       "确定要退出聊天室吗？",
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)

            if reply == QMessageBox.Yes:
                # 关闭所有私聊窗口
                for window in self.private_chat_windows.values():
                    window.close()
                
                # 关闭表情选择器
                if self.emoji_picker:
                    self.emoji_picker.hide()
                    self.emoji_picker.deleteLater()
                
                # 关闭socket连接
                if self.socket:
                    try:
                        self.socket.close()
                    except:
                        pass
                
                event.accept()
            else:
                event.ignore()
        except Exception as e:
            print(f"关闭窗口失败: {e}")
            event.accept()

    def receive_messages(self):
        """接收消息的线程函数"""
        buffer = ""  # 用于处理粘包问题
        while True:
            try:
                if not self.socket:
                    print("Socket已关闭")
                    break
                    
                data = self.socket.recv(1024).decode()
                if not data:
                    print("接收到空数据，连接可能已断开")
                    break
                
                buffer += data
                
                try:
                    # 尝试解析JSON
                    message = json.loads(buffer)
                    buffer = ""  # 清空缓冲区
                    
                    message_type = message.get('type', 'message')
                    print(f"收到消息类型: {message_type}")
                    
                    if message_type == 'message':
                        sender = message['sender']
                        content = message['content']
                        timestamp = message.get('timestamp', '')
                        is_private = message.get('is_private', False)
                        target = message.get('target', None)
                        
                        # 如果是私聊消息且目标是当前用户
                        if is_private and target == self.username:
                            # 如果私聊窗口已经打开，就发送到私聊窗口
                            if sender in self.private_chat_windows:
                                self.private_chat_windows[sender].receive_message(content, sender)
                            else:
                                # 在主窗口显示私聊消息
                                self.signal_bus.message_received.emit(content, sender, True)
                        else:
                            # 普通消息直接显示
                            self.signal_bus.message_received.emit(content, sender, False)
                    
                    elif message_type == 'private_message':
                        sender = message['sender']
                        content = message['content']
                        timestamp = message.get('timestamp', '')
                        target = message.get('target', '')
                        
                        print(f"收到私聊消息 - 发送者: {sender}, 内容: {content}")
                        
                        # 如果这是发送确认消息（发给自己的），不显示
                        if target and sender == self.username:
                            continue
                        
                        # 如果私聊窗口已经打开，就发送到私聊窗口
                        if sender in self.private_chat_windows:
                            print(f"转发消息到私聊窗口: {sender}")
                            self.private_chat_windows[sender].receive_message(content, sender)
                        else:
                            # 在主窗口显示私聊消息
                            print(f"在主窗口显示私聊消息: {sender}")
                            self.signal_bus.message_received.emit(content, sender, True)
                    
                    elif message_type == 'chat_history':
                        print("接收到历史记录")
                        self.signal_bus.chat_history_received.emit(message['history'])
                    
                    elif message_type == 'user_list':
                        self.signal_bus.user_list_updated.emit(message['users'])
                    
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"处理消息错误: {str(e)}")
                    buffer = ""
                
            except ConnectionError as e:
                print(f"连接错误: {e}")
                break
            except Exception as e:
                print(f"接收消息错误: {str(e)}")
                break
        
        print("消息接收线程结束，准备处理断开连接")
        # 使用QTimer确保在主线程中调用handle_disconnect
        QTimer.singleShot(0, self.handle_disconnect)

    def open_private_chat(self, target_user):
        """打开私聊窗口"""
        if target_user == self.username:
            return
        
        if target_user not in self.private_chat_windows:
            # 创建新的私聊窗口
            private_chat = PrivateChatWindow(
                self.username,
                target_user,
                self.user_avatars.get(target_user),
                self
            )
            
            # 连接私聊窗口的消息发送信号
            private_chat.message_sent.connect(self.send_private_message)
            
            # 保存私聊窗口引用
            self.private_chat_windows[target_user] = private_chat
        
        # 显示私聊窗口
        self.private_chat_windows[target_user].show()
        self.private_chat_windows[target_user].activateWindow()

    def send_private_message(self, content, target):
        """发送私聊消息"""
        try:
            message = {
                'type': 'private_message',
                'target': target,
                'content': content
            }
            print(f"发送私聊消息到: {target}, 内容: {content}")
            self.socket.send(json.dumps(message).encode())
        except Exception as e:
            print(f"发送私聊消息失败: {str(e)}")
            QMessageBox.warning(self, '错误', f'发送私聊消息失败: {str(e)}')

    def update_user_list(self, users_data):
        """更新在线用户列表"""
        # 清空现有用户列表
        for i in reversed(range(self.users_layout.count() - 1)):
            child = self.users_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 更新下拉框
        self.chat_target_combo.clear()
        self.chat_target_combo.addItem("所有人")
        
        # 添加用户到列表
        for user_data in users_data:
            if isinstance(user_data, dict):
                username = user_data.get('username')
                avatar_path = user_data.get('avatar')
            else:
                username = user_data
                avatar_path = None
            
            if username != self.username:
                # 创建用户头像组件
                user_widget = UserAvatarWidget(username, avatar_path)
                user_widget.user_clicked.connect(self.open_private_chat)
                self.users_layout.insertWidget(self.users_layout.count() - 1, user_widget)
                
                # 添加到下拉框
                self.chat_target_combo.addItem(username)
                
                # 保存用户头像路径
                if avatar_path:
                    self.user_avatars[username] = avatar_path

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '选择文件')
        if file_path:
            try:
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                
                # 发送文件信息
                message = {
                    'type': 'file_start',
                    'file_info': {
                        'name': file_name,
                        'size': file_size
                    }
                }
                self.socket.send(json.dumps(message).encode())
                
                # 发送文件数据
                with open(file_path, 'rb') as f:
                    self.socket.sendall(f.read())
                
                self.display_message(f"发送文件：{file_name}", self.username)
                
            except Exception as e:
                QMessageBox.warning(self, '错误', f'发送文件失败：{str(e)}')

    def send_message(self):
        """发送消息"""
        try:
            text = self.input_field.text().strip()
            if not text:
                return
            
            # 如果是私聊
            if self.current_chat_target != "所有人":
                # 构建私聊消息
                message = {
                    'type': 'private_message',
                    'target': self.current_chat_target,
                    'content': text
                }
                print(f"发送私聊消息到: {self.current_chat_target}")
                # 发送到服务器
                self.socket.send(json.dumps(message).encode())
                # 在本地显示消息
                self.display_message(text, self.username, True)
            else:
                # 构建普通消息
                message = {
                    'type': 'message',
                    'content': text
                }
                # 发送到服务器
                self.socket.send(json.dumps(message).encode())
                # 在本地显示消息
                self.display_message(text, self.username)
            
            # 清空输入框并设置焦点
            self.input_field.clear()
            self.input_field.setFocus()
            
        except Exception as e:
            print(f"发送消息失败: {str(e)}")
            QMessageBox.warning(self, '错误', '发送消息失败')

    def display_chat_history(self, history):
        """显示聊天历史记录"""
        try:
            print(f"收到历史记录: {len(history)} 条消息")
            
            # 清空现有消息
            for i in reversed(range(self.chat_layout.count() - 1)):
                widget = self.chat_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            
            # 添加历史记录分隔线
            separator_label = QLabel("=== 历史消息 ===")
            separator_label.setStyleSheet("""
                QLabel {
                    color: #999999;
                    font-size: 12px;
                    padding: 10px;
                    qproperty-alignment: AlignCenter;
                }
            """)
            self.chat_layout.insertWidget(0, separator_label)
            
            # 显示历史消息
            for message in history:
                if message['type'] in ['message', 'system']:
                    print(f"显示历史消息: {message['sender']}: {message['content']}")
                    self.display_message(
                        message['content'],
                        message['sender'],
                        message.get('is_private', False),
                        message.get('timestamp', '')
                    )
            
            # 添加当前消息分隔线
            current_separator = QLabel("=== 当前消息 ===")
            current_separator.setStyleSheet("""
                QLabel {
                    color: #999999;
                    font-size: 12px;
                    padding: 10px;
                    qproperty-alignment: AlignCenter;
                }
            """)
            self.chat_layout.insertWidget(self.chat_layout.count() - 1, current_separator)
            
            # 滚动到底部
            self.scroll_to_bottom()
            
        except Exception as e:
            print(f"显示历史记录错误: {str(e)}")
            import traceback
            traceback.print_exc()

    def display_message(self, content, sender, is_private=False, timestamp=None):
        """显示消息"""
        # 判断是否是系统消息
        is_system = sender == "系统" or sender == "System"
        
        # 如果没有提供时间戳，使用当前时间
        if not timestamp:
            timestamp = datetime.now().strftime('%H:%M:%S')
        
        # 创建消息气泡
        bubble = ChatBubble(
            text=content,
            sender=sender,
            is_self=sender == self.username,
            is_private=is_private,
            is_system=is_system,
            timestamp=timestamp
        )
        
        # 将消息气泡添加到聊天区域
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        
        # 确保新消息可见
        self.scroll_to_bottom()
        
        # 保存聊天记录（不保存系统消息）
        if not is_system:
            self.save_chat_log(content, sender, is_private)

    def scroll_to_bottom(self):
        """滚动到底部"""
        try:
            if self.chat_widget and self.chat_scroll:
                # 使用QTimer确保在UI更新后滚动
                def do_scroll():
                    self.chat_scroll.verticalScrollBar().setValue(
                        self.chat_scroll.verticalScrollBar().maximum()
                    )
                QTimer.singleShot(50, do_scroll)
        except Exception as e:
            print(f"滚动到底部失败: {e}")
    
    def handle_system_message(self, message):
        """处理系统消息"""
        self.display_message(message, "系统")

    def show_history_dialog(self):
        """显示历史记录对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("聊天记录")
        dialog.setGeometry(200, 200, 800, 600)
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: white;
                border-radius: 10px;
            }}
            QLabel {{
                font-family: {GLOBAL_FONT};
                font-size: 14px;
                color: {COLORS['text']};
                font-weight: bold;
            }}
            QTextEdit {{
                border: 1px solid {COLORS['gray_light']};
                border-radius: 5px;
                padding: 10px;
                font-family: {GLOBAL_FONT};
                font-size: 13px;
                line-height: 1.5;
            }}
            QComboBox {{
                min-width: 200px;
                font-family: {GLOBAL_FONT};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("聊天历史记录")
        title_label.setStyleSheet(f"""
            font-size: 18px;
            color: {COLORS['primary']};
            padding: 10px 0;
        """)
        layout.addWidget(title_label)
        
        # 日期选择区域
        date_layout = QHBoxLayout()
        date_label = QLabel("选择日期：")
        date_combo = QComboBox()
        
        # 获取所有可用的日期
        available_dates = []
        for filename in os.listdir(self.chat_log_dir):
            if filename.startswith("chat_log_") and filename.endswith(".txt"):
                date_str = filename[9:-4]  # 提取日期部分
                available_dates.append(date_str)
        
        date_combo.addItems(sorted(available_dates, reverse=True))
        date_layout.addWidget(date_label)
        date_layout.addWidget(date_combo)
        date_layout.addStretch()
        layout.addLayout(date_layout)
        
        # 聊天记录显示区域
        history_text = QTextEdit()
        history_text.setReadOnly(True)
        layout.addWidget(history_text)
        
        def load_history(date):
            """加载指定日期的聊天记录"""
            try:
                log_file = os.path.join(self.chat_log_dir, f'chat_log_{date}.txt')
                if not os.path.exists(log_file):
                    history_text.setHtml('<div style="color: #666;">没有找到聊天记录</div>')
                    return
                
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # 格式化聊天记录
                formatted_text = ""
                for line in lines:
                    try:
                        # 解析日志行
                        parts = line.strip().split('] ')
                        if len(parts) >= 3:
                            time_str = parts[0][1:]
                            chat_type = parts[1][1:]
                            sender_content = parts[2]
                            sender, content = sender_content.split(': ', 1)
                            
                            # 根据消息类型设置不同的样式
                            if sender == "系统":
                                formatted_text += f'<div style="text-align: center; color: {COLORS["text_light"]}; margin: 5px 0;">{content}</div>'
                            elif sender == self.username:
                                formatted_text += f'''
                                    <div style="text-align: right; margin: 5px 0;">
                                        <span style="font-size: 12px; color: {COLORS["text_light"]};">{time_str}</span>
                                        <div style="background-color: {COLORS["primary"]}; color: white; display: inline-block; padding: 8px 12px; border-radius: 10px; max-width: 80%; text-align: left;">
                                            {content}
                                        </div>
                                    </div>
                                '''
                            else:
                                formatted_text += f'''
                                    <div style="text-align: left; margin: 5px 0;">
                                        <span style="font-size: 12px; color: {COLORS["text_light"]};">{sender} {time_str}</span>
                                        <div style="background-color: {COLORS["gray_lighter"]}; color: {COLORS["text"]}; display: inline-block; padding: 8px 12px; border-radius: 10px; max-width: 80%;">
                                            {content}
                                        </div>
                                    </div>
                                '''
                    except Exception as e:
                        print(f"格式化聊天记录行失败: {e}")
                        continue
                
                history_text.setHtml(formatted_text)
                # 滚动到底部
                history_text.verticalScrollBar().setValue(
                    history_text.verticalScrollBar().maximum()
                )
                
            except Exception as e:
                error_msg = f'<div style="color: red;">加载聊天记录失败: {str(e)}</div>'
                history_text.setHtml(error_msg)
        
        # 连接信号
        date_combo.currentTextChanged.connect(load_history)
        
        # 加载初始记录
        if available_dates:
            load_history(date_combo.currentText())
        
        # 添加底部按钮
        button_layout = QHBoxLayout()
        export_btn = QPushButton("导出记录")
        close_btn = QPushButton("关闭")
        
        export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['success_dark']};
            }}
        """)
        
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['gray']};
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['danger']};
            }}
        """)
        
        def export_history():
            """导出聊天记录"""
            try:
                if not available_dates:
                    QMessageBox.warning(dialog, "提示", "没有可导出的聊天记录")
                    return
                
                # 选择保存路径
                file_path, _ = QFileDialog.getSaveFileName(
                    dialog,
                    "导出聊天记录",
                    os.path.expanduser("~/chat_history.txt"),
                    "Text Files (*.txt)"
                )
                
                if file_path:
                    # 复制当前查看的聊天记录文件
                    current_date = date_combo.currentText()
                    source_file = os.path.join(self.chat_log_dir, f'chat_log_{current_date}.txt')
                    shutil.copy2(source_file, file_path)
                    QMessageBox.information(dialog, "成功", "聊天记录导出成功！")
            except Exception as e:
                QMessageBox.warning(dialog, "错误", f"导出失败: {str(e)}")
        
        export_btn.clicked.connect(export_history)
        close_btn.clicked.connect(dialog.close)
        
        button_layout.addWidget(export_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def save_chat_log(self, content, sender, is_private=False):
        """保存聊天记录"""
        try:
            # 获取当前日期和时间
            now = datetime.now()
            date_str = now.strftime('%Y-%m-%d')
            time_str = now.strftime('%H:%M:%S')
            
            # 创建日志文件路径
            log_file = os.path.join(self.chat_log_dir, f'chat_log_{date_str}.txt')
            
            # 构建日志行
            chat_type = '私聊' if is_private else '消息'
            log_line = f'[{time_str}] [{chat_type}] {sender}: {content}\n'
            
            # 写入日志文件
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_line)
                
        except Exception as e:
            print(f"保存聊天记录失败: {e}")

    def load_chat_history(self):
        """加载今日聊天记录"""
        try:
            # 获取当前日期
            today = datetime.now().strftime('%Y-%m-%d')
            log_file = os.path.join(self.chat_log_dir, f'chat_log_{today}.txt')
            
            if not os.path.exists(log_file):
                # 如果今天还没有聊天记录，显示欢迎消息
                welcome_msg = "欢迎来到聊天室！"
                QTimer.singleShot(100, lambda: self.display_message(welcome_msg, "系统"))
                return
            
            # 读取聊天记录
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 显示最近的聊天记录（最多显示50条）
            start_idx = max(0, len(lines) - 50)
            
            # 使用QTimer延迟加载消息，确保UI已经准备好
            def load_messages():
                for line in lines[start_idx:]:
                    try:
                        # 解析日志行
                        # 格式：[时间] [类型] 发送者: 内容
                        parts = line.strip().split('] ')
                        if len(parts) >= 3:
                            time_str = parts[0][1:]  # 去掉开头的 '['
                            chat_type = parts[1][1:]  # 去掉开头的 '['
                            sender_content = parts[2]
                            
                            # 分离发送者和内容
                            sender, content = sender_content.split(': ', 1)
                            
                            # 显示消息
                            is_private = (chat_type == '私聊')
                            self.display_message(content, sender, is_private, time_str)
                    except Exception as e:
                        print(f"解析聊天记录行失败: {e}")
                        continue
                
                # 添加分隔线
                self.display_message("以上是历史消息", "系统")
                
                # 确保滚动到最新消息
                QTimer.singleShot(150, self.scroll_to_bottom)
            
            # 延迟100ms加载消息，确保UI已经准备好
            QTimer.singleShot(100, load_messages)
            
        except Exception as e:
            print(f"加载聊天记录失败: {e}")
            QTimer.singleShot(100, lambda: self.display_message("加载历史消息失败", "系统"))

    def change_chat_target(self, target):
        """改变聊天对象"""
        self.current_chat_target = target

    def handle_file_received(self, filename, sender, file_data):
        """处理接收到的文件"""
        try:
            # 保存到文件存储目录
            file_path = os.path.join(self.files_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # 显示系统消息
            self.display_message(f"收到来自 {sender} 的文件：{filename}", "系统")
            
            # 显示通知
            QMessageBox.information(self, "文件接收", f"文件已保存到：{file_path}")
            
        except Exception as e:
            print(f"保存文件失败: {e}")
            QMessageBox.warning(self, "错误", f"保存文件失败: {e}")

    def toggle_ai_assistant(self):
        if self.ai_assistant.isVisible():
            self.ai_assistant.hide()
        else:
            self.ai_assistant.show()

    def show_file_manager(self):
        """显示文件管理器窗口"""
        self.file_manager = FileManagerWindow(self.socket)
        # 连接文件管理器的信号
        self.file_manager.file_uploaded.connect(self.upload_file)
        self.file_manager.file_download_requested.connect(self.download_file)
        self.file_manager.show()
        # 请求最新的文件列表
        try:
            request = {
                "type": "file_list_request"
            }
            self.socket.send(json.dumps(request).encode())
        except Exception as e:
            print(f"请求文件列表失败: {e}")

    def handle_message(self, data):
        """处理接收到的消息"""
        try:
            message = json.loads(data.decode('utf-8'))
            message_type = message.get('type', 'message')
            
            if message_type == 'message':
                content = message.get('content', '')
                sender = message.get('sender', '')
                is_private = message.get('is_private', False)
                timestamp = message.get('timestamp', '')
                
                # 处理私聊消息
                if is_private:
                    target = message.get('target', '')
                    if target == self.username:
                        # 如果是发给自己的私聊消息
                        if sender in self.private_chat_windows:
                            self.private_chat_windows[sender].receive_message(content, sender)
                        else:
                            # 创建新的私聊窗口
                            self.open_private_chat(sender)
                            self.private_chat_windows[sender].receive_message(content, sender)
                else:
                    # 显示群聊消息
                    self.display_message(content, sender, is_private, timestamp)
                    
            elif message_type == 'system':
                content = message.get('content', '')
                sender = message.get('sender', '系统')
                timestamp = message.get('timestamp', '')
                self.display_message(content, sender, False, timestamp)
                
            elif message_type == 'file_list':
                # 更新文件列表
                files = message.get('files', [])
                if hasattr(self, 'file_manager') and self.file_manager.isVisible():
                    self.file_manager.update_remote_files(files)
                
            elif message_type == 'file_download':
                # 处理文件下载
                self.handle_file_download(message)
                
        except json.JSONDecodeError:
            print("解析消息失败")
        except Exception as e:
            print(f"处理消息时出错: {e}")
            import traceback
            traceback.print_exc()

    def upload_file(self, file_path):
        """上传文件"""
        try:
            if not os.path.exists(file_path):
                QMessageBox.warning(self, "错误", "文件不存在")
                return
            
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            
            # 发送文件信息
            file_info = {
                "type": "file_upload",
                "file_info": {
                    "name": file_name,
                    "size": file_size
                }
            }
            self.socket.send(json.dumps(file_info).encode())
            
            # 发送文件数据
            with open(file_path, 'rb') as f:
                self.socket.sendall(f.read())
            
            print(f"文件 {file_name} 上传成功")
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"上传文件失败: {e}")

    def download_file(self, filename):
        """请求下载文件"""
        try:
            request = {
                "type": "file_download_request",
                "filename": filename
            }
            self.socket.send(json.dumps(request).encode())
        except Exception as e:
            QMessageBox.warning(self, "错误", f"请求下载文件失败: {e}")

    def handle_file_download(self, message):
        """处理文件下载响应"""
        try:
            file_info = message['file_info']
            file_name = file_info['name']
            file_size = file_info['size']
            
            # 接收文件数据
            received_data = b''
            received_size = 0
            
            while received_size < file_size:
                chunk = self.socket.recv(min(4096, file_size - received_size))
                if not chunk:
                    break
                received_data += chunk
                received_size += len(chunk)
            
            # 通知文件管理器保存文件
            if hasattr(self, 'file_manager'):
                self.file_manager.handle_file_saved(file_name)
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"下载文件失败: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = ChatClient()
    sys.exit(app.exec_())