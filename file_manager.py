import os
import json
import shutil
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                           QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

class FileManagerWindow(QWidget):
    # 定义信号
    file_uploaded = pyqtSignal(str)  # 发送文件路径
    file_download_requested = pyqtSignal(str)  # 发送文件名

    def __init__(self, socket_client=None):
        super().__init__()
        self.socket_client = socket_client
        
        # 创建文件存储目录
        self.files_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")
        if not os.path.exists(self.files_dir):
            os.makedirs(self.files_dir)
            
        # 创建下载目录
        self.download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        
        # 远程文件列表
        self.remote_files = []
        # 本地文件列表
        self.local_files = []
        
        self.init_ui()
        self.load_local_files()
        
    def init_ui(self):
        """初始化文件管理器界面"""
        self.setWindowTitle('文件管理')
        self.setGeometry(300, 300, 900, 600)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 标题和说明
        title_layout = QHBoxLayout()
        
        title_label = QLabel("文件管理")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #1976D2;
                padding: 5px;
            }
        """)
        title_layout.addWidget(title_label)
        
        # 添加文件存储路径显示
        path_label = QLabel(f"文件存储路径：{self.files_dir}")
        path_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 12px;
                padding: 5px;
            }
        """)
        title_layout.addWidget(path_label)
        title_layout.addStretch()
        
        # 刷新按钮
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.refresh_files)
        refresh_btn.setStyleSheet(self.get_button_style('normal'))
        title_layout.addWidget(refresh_btn)
        
        # 打开文件夹按钮
        open_folder_btn = QPushButton("打开文件夹")
        open_folder_btn.clicked.connect(self.open_files_folder)
        open_folder_btn.setStyleSheet(self.get_button_style('success'))
        title_layout.addWidget(open_folder_btn)
        
        layout.addLayout(title_layout)
        
        # 远程文件列表
        remote_label = QLabel("远程文件")
        remote_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
                padding: 5px;
            }
        """)
        layout.addWidget(remote_label)
        
        self.remote_file_list = QTableWidget()
        self.remote_file_list.setColumnCount(6)
        self.remote_file_list.setHorizontalHeaderLabels(['文件名', '大小', '上传者', '上传时间', '本地状态', '操作'])
        self.remote_file_list.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.remote_file_list.setStyleSheet(self.get_table_style())
        layout.addWidget(self.remote_file_list)
        
        # 本地文件列表
        local_label = QLabel("本地文件")
        local_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
                padding: 5px;
            }
        """)
        layout.addWidget(local_label)
        
        self.local_file_list = QTableWidget()
        self.local_file_list.setColumnCount(4)
        self.local_file_list.setHorizontalHeaderLabels(['文件名', '大小', '修改时间', '操作'])
        self.local_file_list.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.local_file_list.setStyleSheet(self.get_table_style())
        layout.addWidget(self.local_file_list)
        
        # 上传按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        upload_btn = QPushButton('上传文件')
        upload_btn.clicked.connect(self.upload_file)
        upload_btn.setStyleSheet(self.get_button_style('primary'))
        button_layout.addWidget(upload_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def get_button_style(self, style_type='normal'):
        """获取按钮样式"""
        colors = {
            'normal': ('#2196F3', '#1976D2'),
            'primary': ('#2196F3', '#1976D2'),
            'success': ('#4CAF50', '#388E3C'),
            'warning': ('#FF9800', '#F57C00'),
            'danger': ('#F44336', '#D32F2F')
        }
        base_color, hover_color = colors.get(style_type, colors['normal'])
        
        return f"""
            QPushButton {{
                background-color: {base_color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """
    
    def get_table_style(self):
        """获取表格样式"""
        return """
            QTableWidget {
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """
    
    def load_local_files(self):
        """加载本地文件列表"""
        try:
            self.local_files = []
            for filename in os.listdir(self.files_dir):
                file_path = os.path.join(self.files_dir, filename)
                if os.path.isfile(file_path):
                    file_stat = os.stat(file_path)
                    self.local_files.append({
                        'filename': filename,
                        'size': file_stat.st_size,
                        'mtime': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                        'path': file_path
                    })
            self.update_local_file_list()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载本地文件失败: {e}")
    
    def update_remote_file_list(self):
        """更新远程文件列表显示"""
        self.remote_file_list.setRowCount(0)
        for file in self.remote_files:
            row = self.remote_file_list.rowCount()
            self.remote_file_list.insertRow(row)
            
            # 文件名
            self.remote_file_list.setItem(row, 0, QTableWidgetItem(file['filename']))
            
            # 文件大小
            size_str = self.format_size(file['size'])
            self.remote_file_list.setItem(row, 1, QTableWidgetItem(size_str))
            
            # 上传者
            self.remote_file_list.setItem(row, 2, QTableWidgetItem(file['uploader']))
            
            # 上传时间
            self.remote_file_list.setItem(row, 3, QTableWidgetItem(file['upload_time']))
            
            # 本地状态
            local_file_path = os.path.join(self.files_dir, file['filename'])
            status = "已保存" if os.path.exists(local_file_path) else "未下载"
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor("#4CAF50" if status == "已保存" else "#F44336"))
            self.remote_file_list.setItem(row, 4, status_item)
            
            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            btn_layout.setSpacing(5)
            
            if status == "未下载":
                # 下载按钮
                download_btn = QPushButton('下载')
                download_btn.setStyleSheet(self.get_button_style('primary'))
                download_btn.clicked.connect(lambda checked, f=file: self.download_file(f))
                btn_layout.addWidget(download_btn)
            else:
                # 打开按钮
                open_btn = QPushButton('打开')
                open_btn.setStyleSheet(self.get_button_style('success'))
                open_btn.clicked.connect(lambda checked, f=file: self.open_file(f['filename']))
                btn_layout.addWidget(open_btn)
            
            btn_layout.addStretch()
            self.remote_file_list.setCellWidget(row, 5, btn_widget)
    
    def update_local_file_list(self):
        """更新本地文件列表显示"""
        self.local_file_list.setRowCount(0)
        for file in self.local_files:
            row = self.local_file_list.rowCount()
            self.local_file_list.insertRow(row)
            
            # 文件名
            self.local_file_list.setItem(row, 0, QTableWidgetItem(file['filename']))
            
            # 文件大小
            size_str = self.format_size(file['size'])
            self.local_file_list.setItem(row, 1, QTableWidgetItem(size_str))
            
            # 修改时间
            self.local_file_list.setItem(row, 2, QTableWidgetItem(file['mtime']))
            
            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            btn_layout.setSpacing(5)
            
            # 打开按钮
            open_btn = QPushButton('打开')
            open_btn.setStyleSheet(self.get_button_style('success'))
            open_btn.clicked.connect(lambda checked, f=file: self.open_file(f['filename']))
            btn_layout.addWidget(open_btn)
            
            # 下载按钮
            download_btn = QPushButton('下载')
            download_btn.setStyleSheet(self.get_button_style('primary'))
            download_btn.clicked.connect(lambda checked, f=file: self.download_local_file(f))
            btn_layout.addWidget(download_btn)
            
            btn_layout.addStretch()
            self.local_file_list.setCellWidget(row, 3, btn_widget)
    
    def refresh_files(self):
        """刷新文件列表"""
        self.load_local_files()
        if self.socket_client:
            try:
                request = {
                    "type": "file_list_request"
                }
                self.socket_client.send(json.dumps(request).encode())
            except Exception as e:
                QMessageBox.warning(self, "错误", f"请求文件列表失败: {e}")
    
    def update_remote_files(self, files):
        """更新远程文件列表"""
        self.remote_files = files
        self.update_remote_file_list()
    
    def format_size(self, size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"
    
    def open_file(self, filename):
        """打开文件"""
        try:
            file_path = os.path.join(self.files_dir, filename)
            if os.path.exists(file_path):
                os.startfile(file_path)
            else:
                QMessageBox.warning(self, "错误", "文件不存在")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"打开文件失败: {e}")
    
    def open_files_folder(self):
        """打开文件存储文件夹"""
        try:
            os.startfile(self.files_dir)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"打开文件夹失败: {e}")
    
    def upload_file(self):
        """选择并上传新文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if file_path:
            self.file_uploaded.emit(file_path)
    
    def upload_existing_file(self, file):
        """上传已存在的文件"""
        self.file_uploaded.emit(file['path'])
    
    def download_file(self, file):
        """下载文件"""
        self.file_download_requested.emit(file['stored_name'])
    
    def download_local_file(self, file):
        """下载本地文件到下载目录"""
        try:
            source_path = file['path']
            download_path = os.path.join(self.download_dir, file['filename'])
            
            # 复制文件到下载目录
            shutil.copy2(source_path, download_path)
            QMessageBox.information(self, "成功", f"文件已下载到：{download_path}")
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"下载文件失败: {e}")
    
    def handle_file_saved(self, filename):
        """处理文件保存成功的回调"""
        self.load_local_files()
        self.update_remote_file_list() 