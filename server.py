import socket
import threading
import json
import os
from datetime import datetime
import time

class ChatServer:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(10)
        self.clients = {}  # {username: {'socket': socket, 'address': address, 'avatar': avatar_path}}
        self.lock = threading.Lock()
        
        # 创建历史记录目录
        self.history_dir = "server_history"
        if not os.path.exists(self.history_dir):
            os.makedirs(self.history_dir)
        
        # 创建文件存储目录
        self.files_dir = "server_files"
        if not os.path.exists(self.files_dir):
            os.makedirs(self.files_dir)
        
        # 加载历史记录
        self.chat_history = self.load_chat_history()
        
        # 文件列表
        self.file_list = self.load_file_list()
        
        print(f"服务器启动成功，监听地址：{self.host}:{self.port}")

    def load_chat_history(self):
        """加载历史聊天记录"""
        history = []
        try:
            history_file = os.path.join(self.history_dir, "chat_history.json")
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
        except Exception as e:
            print(f"加载历史记录失败: {e}")
        return history

    def save_chat_history(self):
        """保存聊天历史记录到文件"""
        try:
            history_file = os.path.join(self.history_dir, "chat_history.json")
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.chat_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")

    def add_to_history(self, message):
        """添加消息到历史记录"""
        if message.get('type') in ['message', 'system']:
            self.chat_history.append({
                'type': message['type'],
                'sender': message['sender'],
                'content': message['content'],
                'timestamp': message.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                'is_private': message.get('is_private', False)
            })
            # 限制历史记录数量，只保留最近的1000条消息
            if len(self.chat_history) > 1000:
                self.chat_history = self.chat_history[-1000:]
            self.save_chat_history()

    def send_chat_history(self, client_socket):
        """发送聊天历史记录给新用户"""
        try:
            # 只发送非私聊的历史消息
            public_history = [msg for msg in self.chat_history if not msg.get('is_private', False)]
            history_message = {
                'type': 'chat_history',
                'history': public_history
            }
            print(f"发送历史记录: {len(public_history)} 条消息")
            client_socket.send(json.dumps(history_message).encode('utf-8'))
            # 添加延迟确保历史记录被完整接收
            time.sleep(0.1)
        except Exception as e:
            print(f"发送历史记录失败: {e}")

    def load_file_list(self):
        """加载文件列表"""
        file_list = []
        try:
            file_list_path = os.path.join(self.files_dir, "file_list.json")
            if os.path.exists(file_list_path):
                with open(file_list_path, 'r', encoding='utf-8') as f:
                    file_list = json.load(f)
        except Exception as e:
            print(f"加载文件列表失败: {e}")
        return file_list

    def save_file_list(self):
        """保存文件列表"""
        try:
            file_list_path = os.path.join(self.files_dir, "file_list.json")
            with open(file_list_path, 'w', encoding='utf-8') as f:
                json.dump(self.file_list, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存文件列表失败: {e}")

    def handle_file_upload(self, username, file_info, file_data):
        """处理文件上传"""
        try:
            # 生成唯一文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{file_info['name']}"
            file_path = os.path.join(self.files_dir, unique_filename)
            
            # 保存文件
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # 添加到文件列表
            file_record = {
                'filename': file_info['name'],
                'stored_name': unique_filename,
                'size': file_info['size'],
                'uploader': username,
                'upload_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self.file_list.append(file_record)
            self.save_file_list()
            
            # 广播文件列表更新消息
            self.broadcast_file_list()
            
            return True
        except Exception as e:
            print(f"保存文件失败: {e}")
            return False

    def broadcast_file_list(self):
        """广播文件列表给所有客户端"""
        self.send_file_list()

    def handle_file_download(self, client_socket, filename):
        """处理文件下载请求"""
        try:
            # 查找文件记录
            file_record = next((f for f in self.file_list if f['stored_name'] == filename), None)
            if not file_record:
                return False
            
            file_path = os.path.join(self.files_dir, filename)
            if not os.path.exists(file_path):
                return False
            
            # 读取文件数据
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # 发送文件信息
            file_info = {
                "type": "file_download",
                "file_info": {
                    "name": file_record['filename'],
                    "size": len(file_data)
                }
            }
            client_socket.send(json.dumps(file_info).encode())
            time.sleep(0.1)  # 等待客户端准备接收
            
            # 发送文件数据
            client_socket.sendall(file_data)
            return True
            
        except Exception as e:
            print(f"处理文件下载失败: {e}")
            return False

    def broadcast(self, message, sender=None, target=None):
        """广播消息给所有客户端或指定客户端"""
        with self.lock:
            disconnected_clients = []
            
            if target:  # 私聊消息
                if target in self.clients:
                    try:
                        self.clients[target]['socket'].send(json.dumps(message).encode('utf-8'))
                    except:
                        disconnected_clients.append(target)
            else:  # 群聊消息
                for username, client_info in self.clients.items():
                    if username != sender:
                        try:
                            client_info['socket'].send(json.dumps(message).encode('utf-8'))
                        except:
                            disconnected_clients.append(username)
            
            # 添加到历史记录
            self.add_to_history(message)
            
            # 清理断开连接的客户端
            for username in disconnected_clients:
                self.remove_client(username)

    def send_user_list(self):
        """发送在线用户列表（包含头像信息）"""
        user_list = []
        for username, client_info in self.clients.items():
            user_list.append({
                'username': username,
                'avatar': client_info.get('avatar', '')
            })
        
        message = {
            "type": "user_list",
            "users": user_list
        }
        self.broadcast(message)

    def handle_client(self, client_socket, address):
        """处理单个客户端连接"""
        username = None
        try:
            # 接收登录信息
            login_data = json.loads(client_socket.recv(1024).decode('utf-8'))
            username = login_data.get('username')
            password = login_data.get('password')
            avatar_path = login_data.get('avatar', '')
            
            # 检查用户名是否已存在
            with self.lock:
                if username in self.clients:
                    client_socket.send(json.dumps({
                        "type": "login", 
                        "status": "error",
                        "message": "用户名已存在"
                    }).encode('utf-8'))
                    return
                
                self.clients[username] = {
                    'socket': client_socket,
                    'address': address,
                    'avatar': avatar_path
                }
            
            # 发送登录成功消息
            client_socket.send(json.dumps({
                "type": "login", 
                "status": "success",
                "message": "登录成功"
            }).encode('utf-8'))
            
            # 确保登录响应被接收后再发送历史记录
            time.sleep(0.1)
            
            # 发送历史记录
            self.send_chat_history(client_socket)
            
            # 发送文件列表
            self.send_file_list(client_socket)
            
            # 广播新用户加入
            self.broadcast({
                "type": "system",
                "content": f"{username} 加入了聊天室",
                "sender": "系统",
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }, username)
            
            # 发送用户列表
            self.send_user_list()
            
            print(f"用户 {username} 连接成功")

            while True:
                try:
                    data = client_socket.recv(4096)
                    if not data:
                        break
                    
                    message = json.loads(data.decode('utf-8'))
                    message_type = message.get('type', 'message')
                    print(f"收到消息类型: {message_type}, 发送者: {username}")
                    
                    if message_type == 'message':
                        # 构建消息
                        broadcast_message = {
                            "type": "message",
                            "sender": username,
                            "content": message['content'],
                            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        # 发送消息
                        self.broadcast(broadcast_message, username)
                        print(f"群聊消息：{username}: {message['content']}")
                    
                    elif message_type == 'private_message':
                        target = message.get('target')
                        content = message.get('content')
                        
                        if target and target in self.clients:
                            # 构建私聊消息
                            private_message = {
                                "type": "private_message",
                                "sender": username,
                                "content": content,
                                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                            
                            try:
                                # 发送给目标用户
                                print(f"发送私聊消息：{username} -> {target}: {content}")
                                self.clients[target]['socket'].send(json.dumps(private_message).encode('utf-8'))
                                
                                # 发送确认消息给发送者
                                confirm_message = {
                                    "type": "private_message",
                                    "sender": username,
                                    "target": target,
                                    "content": content,
                                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                }
                                client_socket.send(json.dumps(confirm_message).encode('utf-8'))
                                
                                # 保存到历史记录
                                self.add_to_history({
                                    "type": "message",
                                    "sender": username,
                                    "content": content,
                                    "is_private": True,
                                    "target": target,
                                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                })
                                
                            except Exception as e:
                                print(f"发送私聊消息失败: {e}")
                                error_message = {
                                    "type": "system",
                                    "content": f"发送私聊消息失败：{target} 可能已离线",
                                    "sender": "系统"
                                }
                                client_socket.send(json.dumps(error_message).encode('utf-8'))
                        else:
                            # 目标用户不存在
                            error_message = {
                                "type": "system",
                                "content": f"用户 {target} 不存在或已离线",
                                "sender": "系统"
                            }
                            client_socket.send(json.dumps(error_message).encode('utf-8'))
                    
                    elif message_type == 'file_upload':
                        # 处理文件上传
                        file_info = message['file_info']
                        file_size = file_info['size']
                        
                        file_data = b''
                        received_size = 0
                        
                        while received_size < file_size:
                            chunk = client_socket.recv(min(4096, file_size - received_size))
                            if not chunk:
                                break
                            file_data += chunk
                            received_size += len(chunk)
                        
                        # 处理文件上传
                        if self.handle_file_upload(username, file_info, file_data):
                            # 发送成功消息
                            success_msg = {
                                "type": "system",
                                "content": f"{username} 上传了文件：{file_info['name']}",
                                "sender": "系统",
                                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                            self.broadcast(success_msg)
                    
                    elif message_type == 'file_download_request':
                        # 处理文件下载请求
                        filename = message.get('filename')
                        if filename:
                            self.handle_file_download(client_socket, filename)
                    
                    elif message_type == 'file_list_request':
                        # 处理文件列表请求
                        self.send_file_list(client_socket)

                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"处理客户端 {username} 消息时出错: {e}")
                    break

        except Exception as e:
            print(f"处理客户端连接时出错: {e}")
        finally:
            if username:
                self.remove_client(username)

    def remove_client(self, username):
        """移除客户端连接"""
        with self.lock:
            if username in self.clients:
                try:
                    self.clients[username]['socket'].close()
                except:
                    pass
                del self.clients[username]
                
                # 广播用户离开消息
                self.broadcast({
                    "type": "system",
                    "content": f"{username} 离开了聊天室",
                    "sender": "系统",
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                
                # 更新用户列表
                self.send_user_list()
                
                print(f"用户 {username} 断开连接")

    def start(self):
        """启动服务器"""
        try:
            while True:
                client_socket, address = self.server_socket.accept()
                thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
                thread.daemon = True
                thread.start()
        except KeyboardInterrupt:
            print("\n服务器正在关闭...")
            self.save_chat_history()  # 保存历史记录
        finally:
            self.server_socket.close()

    def send_file_list(self, client_socket=None):
        """发送文件列表给指定客户端或所有客户端"""
        try:
            message = {
                "type": "file_list",
                "files": self.file_list
            }
            if client_socket:
                client_socket.send(json.dumps(message).encode())
            else:
                self.broadcast(message)
        except Exception as e:
            print(f"发送文件列表失败: {e}")

if __name__ == "__main__":
    server = ChatServer()
    server.start()