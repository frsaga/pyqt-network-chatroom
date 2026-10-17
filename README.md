# 基于TCP的聊天程序

这是一个基于TCP套接字编程实现的聊天程序，使用PyQt5构建图形界面，支持以下功能：

- 用户登录
- 群聊消息
- 文件传输
- 聊天气泡界面
- 集成AI助手功能

## 功能特点

1. 登录系统
   - 用户名和密码验证
   - 登录状态维护

2. 聊天功能
   - 群聊消息发送和接收
   - 美观的聊天气泡界面
   - 实时消息更新

3. 文件传输
   - 支持发送任意类型文件
   - 自动保存接收的文件
   - 文件传输进度提示

4. AI助手
   - 集成通义千问AI助手
   - 随时调用AI帮助

## 安装说明

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置AI助手：
   - 在 `ai1.py` 中配置你的通义千问API密钥

## 使用说明

1. 启动服务器：
```bash
python server.py
```

2. 启动客户端：
```bash
python client.py
```

3. 使用流程：
   - 输入用户名和密码登录
   - 在输入框输入消息并发送
   - 点击"发送文件"按钮选择要发送的文件
   - 点击"AI助手"按钮打开/关闭AI助手窗口

## 注意事项

1. 服务器默认监听地址为 127.0.0.1:5000
2. 接收的文件将保存在 received_files 目录下
3. 确保通义千问API密钥配置正确

## 系统要求

- Python 3.6+
- PyQt5
- 网络连接 
## Public source edition

This repository contains a source snapshot of an educational project. Personal reports, real user records, private credentials, build outputs and original Git history are excluded. No production security or performance certification is claimed.

The optional assistant reads QWEN_API_KEY from the environment. Configure your own key locally; never commit it.
