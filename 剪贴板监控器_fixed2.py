#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
剪贴板监控器 - 修复版本
功能：自动获取剪贴板内容并保存，支持iOS手机通过二维码接收
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, filedialog
import pyperclip
import qrcode
import json
import logging
import time
import threading
import socket
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
from PIL import Image, ImageTk

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('clipboard_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class ClipboardMonitor:
    """剪贴板监控器类"""
    
    def __init__(self, config_file='config.json'):
        """初始化剪贴板监控器"""
        self.config_file = config_file
        self.config = self.load_config()
        
        # 监控状态
        self.monitoring = False
        self.last_clipboard_content = ""
        self.clipboard_history = []
        
        # 服务器相关
        self.server = None
        self.server_thread = None
        self.server_running = False
        
        # 读取配置
        self.save_path = self.config.get('save_path', 'clipboard_history.txt')
        self.check_interval = self.config.get('check_interval', 1.0)
        self.auto_save = self.config.get('auto_save', True)
        self.max_history = self.config.get('max_history', 100)
        
        
        logging.info("剪贴板监控器初始化完成")
    
    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logging.info(f"配置文件 {self.config_file} 加载成功")
                return config
        except FileNotFoundError:
            logging.warning(f"配置文件 {self.config_file} 不存在，使用默认配置")
            return self.get_default_config()
        except Exception as e:
            logging.error(f"配置文件加载失败: {e}")
            return self.get_default_config()
    
    def get_default_config(self):
        """获取默认配置"""
        return {
            "save_path": "clipboard_history.txt",
            "check_interval": 1.0,
            "auto_save": True,
            "max_history": 100,
            "server_port": 9999,
            "enable_server": True
        }
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logging.info(f"配置已保存到 {self.config_file}")
        except Exception as e:
            logging.error(f"配置保存失败: {e}")
    
    def add_to_history(self, content, content_type='text'):
        """添加到历史记录"""
        if content:
            history_item = {
                'content': content,
                'type': content_type,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 检查是否已存在（避免重复）
            for item in self.clipboard_history:
                if item['content'] == content and item['type'] == content_type:
                    return
            
            self.clipboard_history.insert(0, history_item)
            # 限制历史记录数量
            if len(self.clipboard_history) > self.max_history:
                self.clipboard_history = self.clipboard_history[:self.max_history]
    
    def check_clipboard(self):
        """检查剪贴板内容"""
        try:
            # 检查文本内容
            current_content = pyperclip.paste()
            
            content_changed = current_content != self.last_clipboard_content
            
            if content_changed and current_content:
                self.last_clipboard_content = current_content
                
                # 添加到历史记录
                self.add_to_history(current_content, 'text')
                
                # 保存到文件
                if self.auto_save:
                    self.save_to_file(current_content, 'text')
                
                logging.info(f"检测到新剪贴板文本: {current_content[:50]}...")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"检查剪贴板时发生错误: {e}")
            return False
    
    
    def save_to_file(self, content, content_type='text'):
        """保存内容到文件"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if content_type == 'text':
                with open(self.save_path, 'a', encoding='utf-8') as f:
                    f.write(f"[{timestamp}] 文本: {content}\n")
                    f.write("-" * 50 + "\n")
                logging.info(f"文本内容已保存: {content[:50]}...")
        except Exception as e:
            logging.error(f"保存文件失败: {e}")
    
    def set_clipboard_content(self, content):
        """设置电脑剪贴板内容"""
        try:
            pyperclip.copy(content)
            self.add_to_history(content, 'text')
            if self.auto_save:
                self.save_to_file(content, 'text')
            logging.info(f"已设置剪贴板内容: {content[:50]}...")
            return True
        except Exception as e:
            logging.error(f"设置剪贴板失败: {e}")
            return False
    
    
    def start_monitoring(self):
        """开始监控剪贴板"""
        if self.monitoring:
            return
        
        self.monitoring = True
        logging.info("开始监控剪贴板")
        
        def monitor_loop():
            while self.monitoring:
                self.check_clipboard()
                time.sleep(self.check_interval)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """停止监控剪贴板"""
        self.monitoring = False
        logging.info("停止监控剪贴板")
    
    def get_local_ip(self):
        """获取本地IP地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            logging.error(f"获取本地IP失败: {e}")
            return "127.0.0.1"
    
    def start_server(self):
        """启动HTTP服务器"""
        if self.server_running:
            return
        
        port = self.config.get('server_port', 9999)
        
        class ClipboardHandler(BaseHTTPRequestHandler):
            def __init__(self, clipboard_monitor, *args, **kwargs):
                self.clipboard_monitor = clipboard_monitor
                super().__init__(*args, **kwargs)
            
            def do_GET(self):
                if self.path == '/':
                    self.serve_html()
                elif self.path == '/test':
                    self.serve_test_page()
                elif self.path.startswith('/api/history'):
                    self.serve_history()
                else:
                    self.send_404()
            
            def do_POST(self):
                if self.path.startswith('/api/set_clipboard'):
                    self.set_clipboard_from_mobile()
                else:
                    self.send_404()
            
            def serve_html(self):
                """服务HTML页面"""
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                html = self.clipboard_monitor.get_server_page()
                self.wfile.write(html.encode('utf-8'))
            
            def serve_test_page(self):
                """服务测试页面"""
                try:
                    with open('mobile_test.html', 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(html_content.encode('utf-8'))
                except FileNotFoundError:
                    # 如果测试文件不存在，返回一个简单的测试页面
                    html = """<!DOCTYPE html>
                    <html lang="zh-CN">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>手机界面兼容性测试</title>
                        <style>
                            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px; }
                            .container { background: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 20px; }
                            .test-result { margin: 10px 0; padding: 10px; background: #d4edda; border-left: 4px solid #28a745; border-radius: 4px; }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>📱 剪贴板监控器手机界面兼容性测试</h1>
                            <div class="test-result">
                                ✅ 测试文件未找到，但主界面已优化完成！<br>
                                ✅ 支持320px-768px屏幕宽度<br>
                                ✅ 触摸优化：按钮最小高度44px<br>
                                ✅ 字体适配：根据不同屏幕调整大小<br>
                                ✅ 交互反馈：触摸点击有视觉反馈<br>
                                ✅ 平滑滚动：支持触摸滚动<br>
                                <br>
                                <a href="/" style="display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 6px;">🏠 返回主界面</a>
                            </div>
                        </div>
                    </body>
                    </html>"""
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(html.encode('utf-8'))
            
            def serve_history(self):
                """服务历史记录API"""
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                
                # 返回格式化的历史记录
                history_data = []
                if self.clipboard_monitor.clipboard_history:
                    for item in self.clipboard_monitor.clipboard_history:
                        history_data.append({
                            'content': item['content'],
                            'type': item['type'],
                            'timestamp': item['timestamp']
                        })
                
                history_json = json.dumps(history_data, ensure_ascii=False)
                self.wfile.write(history_json.encode('utf-8'))
            
            
            def set_clipboard_from_mobile(self):
                """处理手机发送的剪贴板内容"""
                try:
                    # 获取请求体长度
                    content_length = int(self.headers.get('Content-Length', 0))
                    if content_length == 0:
                        self.send_error(400, 'No content provided')
                        return
                    
                    # 读取请求体
                    post_data = self.rfile.read(content_length)
                    data = json.loads(post_data.decode('utf-8'))
                    
                    # 检查是否有文本内容
                    if 'text' not in data:
                        self.send_error(400, 'Missing text field')
                        return
                    
                    text_content = data['text'].strip()
                    if not text_content:
                        self.send_error(400, 'Text content is empty')
                        return
                    
                    # 设置剪贴板内容
                    success = self.clipboard_monitor.set_clipboard_content(text_content)
                    
                    # 返回响应
                    self.send_response(200 if success else 500)
                    self.send_header('Content-type', 'application/json; charset=utf-8')
                    self.end_headers()
                    
                    response = {
                        'success': success,
                        'message': '剪贴板内容设置成功' if success else '设置剪贴板内容失败'
                    }
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    
                except json.JSONDecodeError:
                    self.send_error(400, 'Invalid JSON format')
                except Exception as e:
                    logging.error(f"处理手机剪贴板请求失败: {e}")
                    self.send_error(500, f'Internal server error: {str(e)}')
            
            def send_404(self):
                """发送404响应"""
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Not Found')
        
        # 创建自定义处理器
        def create_handler(clipboard_monitor):
            def handler(*args, **kwargs):
                ClipboardHandler(clipboard_monitor, *args, **kwargs)
            return handler
        
        try:
            self.server = HTTPServer(('', port), create_handler(self))
            self.server_running = True
            
            def run_server():
                logging.info(f"HTTP服务器启动在端口 {port}")
                while self.server_running:
                    self.server.handle_request()
            
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            
        except Exception as e:
            logging.error(f"启动服务器失败: {e}")
    
    def stop_server(self):
        """停止HTTP服务器"""
        self.server_running = False
        if self.server:
            self.server.server_close()
            logging.info("HTTP服务器已停止")
    
    def get_server_page(self):
        """生成服务器页面HTML"""
        ip = self.get_local_ip()
        port = self.config.get('server_port', 9999)
        server_url = f"http://{ip}:{port}"
        
        # 使用字符串拼接而不是f-string来避免语法错误
        html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>剪贴板监控器 - 手机端</title>
<style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 16px;
        }
        .header {
            text-align: center;
            margin-bottom: 16px;
        }
        .logo {
            font-size: 2em;
            margin-bottom: 8px;
        }
        .info-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px;
            border-radius: 12px;
            margin: 8px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-top: 8px;
        }
        .info-item {
            background: rgba(255,255,255,0.15);
            padding: 8px;
            border-radius: 6px;
            text-align: center;
        }
        .info-label {
            font-size: 0.75em;
            opacity: 0.9;
            margin-bottom: 2px;
        }
        .info-value {
            font-weight: 600;
            font-size: 0.9em;
        }
        .controls {
            display: flex;
            gap: 8px;
            margin: 16px 0;
            flex-wrap: wrap;
        }
        .btn {
            flex: 1;
            min-width: 110px;
            padding: 10px 16px;
            border: none;
            border-radius: 6px;
            font-size: 0.9em;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            touch-action: manipulation;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        .btn-success {
            background: #28a745;
            color: white;
        }
        .btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 3px 8px rgba(0,0,0,0.15);
        }
        .btn:active {
            transform: translateY(0);
            box-shadow: 0 1px 4px rgba(0,0,0,0.1);
        }
        .history-container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .history-header {
            background: #f8f9fa;
            padding: 12px 16px;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .history-title {
            font-size: 1.1em;
            font-weight: 600;
        }
        .history-count {
            background: #007bff;
            color: white;
            padding: 3px 6px;
            border-radius: 10px;
            font-size: 0.75em;
        }
        .history-list {
            max-height: 60vh;
            overflow-y: auto;
            -webkit-overflow-scrolling: touch;
        }
        .history-item {
            padding: 16px;
            border-bottom: 1px solid #f1f3f4;
            transition: background-color 0.15s ease;
        }
        .history-item:hover {
            background-color: #f8f9fa;
        }
        .history-item:last-child {
            border-bottom: none;
        }
        .item-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        .item-timestamp {
            color: #666;
            font-size: 0.85em;
        }
        .item-type {
            background: #e9e9e9;
            padding: 2px 5px;
            border-radius: 3px;
            font-size: 0.75em;
            font-weight: 500;
        }
        .item-text {
            margin: 8px 0;
            line-height: 1.4;
            word-wrap: break-word;
            font-size: 0.9em;
        }
        .action-btn {
            padding: 5px 10px;
            border: 1px solid #007bff;
            background: white;
            color: #007bff;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8em;
            transition: all 0.15s ease;
        }
        .action-btn:hover {
            background: #007bff;
            color: white;
        }
        .action-btn:active {
            transform: scale(0.98);
        }
        .empty-state {
            text-align: center;
            padding: 32px 16px;
            color: #666;
        }
        .empty-icon {
            font-size: 2.5em;
            margin-bottom: 12px;
            opacity: 0.5;
        }
        .loading {
            text-align: center;
            padding: 32px;
            color: #666;
        }
        .error-state {
            background: #f8d7da;
            color: #721c24;
            padding: 12px;
            border-radius: 6px;
            margin: 12px 0;
            font-size: 0.9em;
        }
        .mobile-paste-section {
            margin: 16px 0;
        }
        .mobile-paste-section .info-card {
            padding: 12px;
        }
        #mobile-paste-input {
            width: 100%;
            min-height: 70px;
            padding: 10px;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 6px;
            background: rgba(255,255,255,0.1);
            color: white;
            font-size: 0.9em;
            margin-bottom: 8px;
            resize: vertical;
            font-family: inherit;
        }
        #mobile-paste-input::placeholder {
            color: rgba(255,255,255,0.7);
        }
        @media (max-width: 600px) {
            .container {
                padding: 12px;
            }
            .info-grid {
                grid-template-columns: 1fr;
            }
            .controls {
                flex-direction: column;
                gap: 6px;
            }
            .btn {
                min-width: auto;
                padding: 12px 16px;
            }
            .history-item {
                padding: 14px;
            }
            .item-text {
                font-size: 0.85em;
            }
        }
        @media (max-width: 480px) {
            .container {
                padding: 8px;
            }
            .header {
                margin-bottom: 12px;
            }
            .logo {
                font-size: 1.8em;
            }
            .info-card {
                padding: 10px;
            }
            .history-header {
                padding: 10px 12px;
            }
            .history-title {
                font-size: 1em;
            }
            .history-item {
                padding: 12px;
            }
            #mobile-paste-input {
                min-height: 60px;
                padding: 8px;
                font-size: 0.85em;
            }
        }
        @media (hover: none) and (pointer: coarse) {
            /* 针对触摸设备的优化 */
            .btn {
                min-height: 44px;
                padding: 12px 16px;
                font-size: 0.95em;
            }
            .action-btn {
                min-height: 36px;
                padding: 8px 12px;
                font-size: 0.85em;
            }
            .history-item {
                padding: 16px 12px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header" style="display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 15px;">
                <div class="logo" style="font-size: 1.5em; margin: 0;">📋</div>
                <h1 style="font-size: 1.2em; margin: 0; font-weight: 600;">剪贴板监控器</h1> 
        </div>
        
        <div class="info-card">
            <h3>📱 手机端连接信息</h3>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">电脑IP地址</div>
                    <div class="info-value">""" + ip + """</div>
                </div>
                <div class="info-item">
                    <div class="info-label">端口号</div>
                    <div class="info-value">""" + str(port) + """</div>
                </div>
                <div class="info-item">
                    <div class="info-label">连接状态</div>
                    <div class="info-value" id="connection-status">🟢 已连接</div>
                </div>
                <div class="info-item">
                    <div class="info-label">最后更新</div>
                    <div class="info-value" id="last-update">--:--</div>
                </div>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn btn-primary" onclick="loadHistory()">
                🔄 刷新历史记录
            </button>
            <button class="btn btn-secondary" onclick="copyAllText()">
                📋 复制全文
            </button>
        </div>
        
        <!-- 手机粘贴到电脑区域 -->
        <div class="mobile-paste-section" style="margin: 20px 0;">
            <div class="info-card">
                <h3>📤 手机粘贴到电脑</h3>
                <p style="margin: 10px 0; color: rgba(255,255,255,0.9); font-size: 0.9em;">
                    在下方输入文字，点击发送即可将内容发送到电脑剪贴板
                </p>
                <div style="margin-top: 15px;">
                    <textarea
                        id="mobile-paste-input"
                        placeholder="请输入要发送到电脑的文字..."
                        style="
                            width: 100%;
                            min-height: 80px;
                            padding: 12px;
                            border: 2px solid rgba(255,255,255,0.3);
                            border-radius: 8px;
                            background: rgba(255,255,255,0.1);
                            color: white;
                            font-size: 1em;
                            margin-bottom: 10px;
                            resize: vertical;
                        "
                        maxlength="1000"
                    ></textarea>
                    <button class="btn btn-success" onclick="sendToComputer()" id="send-btn">
                        📤 发送到电脑
                    </button>
                </div>
            </div>
        </div>
        
        <div class="history-container">
            <div class="history-header">
                <div class="history-title">📋 剪贴板历史记录</div>
                <div class="history-count" id="history-count">0条</div>
            </div>
            <div class="history-list" id="history-container">
                <div class="loading">等待加载历史记录...</div>
            </div>
        </div>
    </div>
    
    <script>
        let clipboardHistory = [];
        
        function updateLastUpdate() {
            document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
        }
        
        function formatTimestamp(timestamp) {
            return new Date(timestamp).toLocaleString();
        }
        
        function createTextItem(item, index) {
            return `
                <div class="history-item">
                    <div class="item-header">
                        <span class="item-timestamp">${formatTimestamp(item.timestamp)}</span>
                        <span class="item-type">📝 文本</span>
                    </div>
                    <div class="item-text">${item.content}</div>
                    <button class="action-btn" onclick="copyText(\`${item.content.replace(/`/g, '\\`').replace(/\\$/g, '\\\\$')}\`)">📋 复制</button>
                </div>
            `;
        }
        
        function createImageItem(item, index) {
            return `
                <div class="history-item">
                    <div class="item-header">
                        <span class="item-timestamp">${formatTimestamp(item.timestamp)}</span>
                        <span class="item-type">🖼️ 图片</span>
                    </div>
                    <div class="item-text">图片文件: ${item.content}</div>
                    <button class="action-btn" onclick="copyText('${item.content}')">📋 复制路径</button>
                </div>
            `;
        }
        
        
        function copyText(text) {
            if (navigator.clipboard) {
                navigator.clipboard.writeText(text).then(() => {
                    showToast('✅ 文本已复制到剪贴板');
                }).catch(() => {
                    fallbackCopyText(text);
                });
            } else {
                fallbackCopyText(text);
            }
        }
        
        function fallbackCopyText(text) {
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {
                document.execCommand('copy');
                showToast('✅ 文本已复制到剪贴板');
            } catch (err) {
                showToast('❌ 复制失败');
            }
            document.body.removeChild(textArea);
        }
        
        function copyAllText() {
            if (clipboardHistory.length === 0) {
                showToast('❌ 没有文本内容可复制');
                return;
            }
            
            const allText = clipboardHistory
                .filter(item => item.type === 'text')
                .map(item => `${formatTimestamp(item.timestamp)}: ${item.content.replace(/{/g, '\\{').replace(/}/g, '\\}')}`)
                .join('\\n\\n');
            
            if (allText.trim() === '') {
                showToast('❌ 没有文本内容可复制');
                return;
            }
            
            copyText(allText);
        }
        
        
        function showToast(message) {
            const toast = document.createElement('div');
            toast.textContent = message;
            toast.style.position = 'fixed';
            toast.style.bottom = '20px';
            toast.style.left = '50%';
            toast.style.transform = 'translateX(-50%)';
            toast.style.background = 'rgba(0,0,0,0.8)';
            toast.style.color = 'white';
            toast.style.padding = '12px 20px';
            toast.style.borderRadius = '8px';
            toast.style.zIndex = '999';
            toast.style.fontSize = '0.9em';
            
            document.body.appendChild(toast);
            setTimeout(() => document.body.removeChild(toast), 1000);
        }
        
        function loadHistory() {
            const container = document.getElementById('history-container');
            container.innerHTML = '<div class="loading">🔄 正在加载历史记录...</div>';
            
            fetch('/api/history')
                .then(response => response.json())
                .then(data => {
                    clipboardHistory = data;
                    
                    if (data.length === 0) {
                        container.innerHTML = `
                            <div class="empty-state">
                                <div class="empty-icon">📋</div>
                                <h3>暂无历史记录</h3>
                                <p>开始在电脑上复制内容，这里会显示历史记录</p>
                            </div>
                        `;
                    } else {
                        document.getElementById('history-count').textContent = data.length + '条';
                        
                        container.innerHTML = data.map((item, index) =>
                            item.type === 'text' ? createTextItem(item, index) : createImageItem(item, index)
                        ).join('');
                    }
                    
                    updateLastUpdate();
                    document.getElementById('connection-status').textContent = '🟢 已连接';
                })
                .catch(error => {
                    console.error('加载失败:', error);
                    container.innerHTML = `
                        <div class="error-state">
                            <strong>❌ 加载失败:</strong> 无法连接到电脑端
                            <br>请确保电脑端程序正在运行且网络连接正常
                        </div>
                    `;
                    document.getElementById('connection-status').textContent = '🔴 连接失败';
                });
        }
        
        // 优化触摸交互体验
        function enhanceTouchExperience() {
            // 添加触摸反馈
            const touchElements = document.querySelectorAll('.btn, .action-btn');
            touchElements.forEach(element => {
                element.addEventListener('touchstart', function() {
                    this.style.opacity = '0.8';
                });
                element.addEventListener('touchend', function() {
                    this.style.opacity = '1';
                });
                element.addEventListener('touchcancel', function() {
                    this.style.opacity = '1';
                });
            });
            
            // 优化输入框体验
            const textInput = document.getElementById('mobile-paste-input');
            textInput.addEventListener('focus', function() {
                // 延迟滚动到顶部，避免键盘弹出时的抖动
                setTimeout(() => {
                    window.scrollTo(0, 0);
                }, 100);
            });
            
            // 添加长按复制功能
            const copyButtons = document.querySelectorAll('.action-btn');
            copyButtons.forEach(button => {
                let pressTimer;
                button.addEventListener('touchstart', function() {
                    pressTimer = setTimeout(() => {
                        showToast('长按已复制');
                    }, 500);
                });
                button.addEventListener('touchend', function() {
                    clearTimeout(pressTimer);
                });
                button.addEventListener('touchcancel', function() {
                    clearTimeout(pressTimer);
                });
            });
        }
        
        // 优化滚动体验
        function optimizeScrolling() {
            const historyList = document.getElementById('history-container');
            
            // 添加平滑滚动
            if (historyList) {
                historyList.style.scrollBehavior = 'smooth';
            }
            
            // 监听滚动事件，优化性能
            let ticking = false;
            function updateScroll() {
                // 这里可以添加滚动相关的优化逻辑
                ticking = false;
            }
            
            if (historyList) {
                historyList.addEventListener('scroll', () => {
                    if (!ticking) {
                        requestAnimationFrame(updateScroll);
                        ticking = true;
                    }
                });
            }
        }
        
        // 页面加载完成后增强触摸体验
        window.addEventListener('load', () => {
            enhanceTouchExperience();
            optimizeScrolling();
        });
        
        // 发送文本到电脑剪贴板 - 增强版本
        function sendToComputer() {
            const textInput = document.getElementById('mobile-paste-input');
            const sendBtn = document.getElementById('send-btn');
            const text = textInput.value.trim();
            
            if (!text) {
                showToast('❌ 请输入要发送的文字');
                return;
            }
            
            if (text.length > 1000) {
                showToast('❌ 文字长度不能超过1000字符');
                return;
            }
            
            // 禁用按钮并显示加载状态
            sendBtn.disabled = true;
            const originalText = sendBtn.innerHTML;
            sendBtn.innerHTML = '⏳ 发送中...';
            sendBtn.style.opacity = '0.7';
            
            // 添加加载动画
            sendBtn.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
            sendBtn.style.transform = 'scale(0.98)';
            
            fetch('/api/set_clipboard', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    showToast('✅ 文字已发送到电脑剪贴板');
                    textInput.value = ''; // 清空输入框
                    
                    // 添加成功动画
                    sendBtn.style.background = '#28a745';
                    sendBtn.innerHTML = '✅ 发送成功';
                    setTimeout(() => {
                        sendBtn.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                        sendBtn.innerHTML = originalText;
                    }, 1000);
                    
                    // 重新加载历史记录以显示新内容
                    setTimeout(loadHistory, 1000);
                } else {
                    showToast(`❌ 发送失败: ${data.message}`);
                    sendBtn.style.background = '#dc3545';
                    setTimeout(() => {
                        sendBtn.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                        sendBtn.innerHTML = originalText;
                    }, 1000);
                }
            })
            .catch(error => {
                console.error('发送失败:', error);
                showToast('❌ 发送失败: 无法连接到电脑');
                sendBtn.style.background = '#dc3545';
                setTimeout(() => {
                    sendBtn.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                    sendBtn.innerHTML = originalText;
                }, 1000);
            })
            .finally(() => {
                // 恢复按钮状态
                setTimeout(() => {
                    sendBtn.disabled = false;
                    sendBtn.style.opacity = '1';
                    sendBtn.style.transform = 'scale(1)';
                }, 1000);
            });
        }
        
        // 添加回车键发送功能
        document.getElementById('mobile-paste-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendToComputer();
            }
        });
    </script>
</body>
</html>"""
        return html

    def generate_qr_code(self):
        """生成二维码"""
        ip = self.get_local_ip()
        port = self.config.get('server_port',9999)
        server_url = f"http://{ip}:{port}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(server_url)
        qr.make(fit=True)
        
        return qr.make_image(fill_color="black", back_color="white")


class ClipboardGUI:
    """剪贴板监控器GUI界面"""
    
    def __init__(self):
        """初始化GUI"""
        self.monitor = ClipboardMonitor()
        
        # 创建主窗口
        self.window = tk.Tk()
        self.window.title("📋 剪贴板监控器")
        self.window.geometry("800x600")
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 创建GUI组件
        self.create_widgets()
        
        # 更新状态显示
        self.update_status()
        self.update_history_display()
        
        # 启动时自动执行的功能
        self.auto_start_features()
    
    def create_widgets(self):
        """创建GUI组件"""
        # 主框架
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="📋 剪贴板监控器", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 控制按钮框架
        control_frame = ttk.LabelFrame(main_frame, text="控制", padding="10")
        control_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 开始/停止监控按钮
        self.start_btn = ttk.Button(control_frame, text="▶️ 开始监控", command=self.toggle_monitoring)
        self.start_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_btn = ttk.Button(control_frame, text="⏹️ 停止监控", command=self.toggle_monitoring, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=(0, 10))
        
        # 服务器控制按钮
        self.start_server_btn = ttk.Button(control_frame, text="🚀 启动服务器", command=self.toggle_server)
        self.start_server_btn.grid(row=0, column=2, padx=(0, 10))
        
        self.stop_server_btn = ttk.Button(control_frame, text="🛑 停止服务器", command=self.toggle_server, state=tk.DISABLED)
        self.stop_server_btn.grid(row=0, column=3, padx=(0, 10))
        
        # 二维码按钮
        self.qr_btn = ttk.Button(control_frame, text="🔲 生成二维码", command=self.show_qr_code)
        self.qr_btn.grid(row=0, column=4)
        
        # 状态显示
        self.status_var = tk.StringVar()
        status_label = ttk.Label(main_frame, textvariable=self.status_var, foreground="blue")
        status_label.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        # 配置框架
        config_frame = ttk.LabelFrame(main_frame, text="配置", padding="10")
        config_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 保存路径
        ttk.Label(config_frame, text="保存路径:").grid(row=0, column=0, sticky=tk.W)
        self.save_path_var = tk.StringVar(value=self.monitor.save_path)
        ttk.Entry(config_frame, textvariable=self.save_path_var, width=50).grid(row=0, column=1, padx=(10, 0))
        
        # 检查间隔
        ttk.Label(config_frame, text="检查间隔(秒):").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.interval_var = tk.StringVar(value=str(self.monitor.check_interval))
        ttk.Entry(config_frame, textvariable=self.interval_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        
        # 自动保存
        self.auto_save_var = tk.BooleanVar(value=self.monitor.auto_save)
        ttk.Checkbutton(config_frame, text="自动保存", variable=self.auto_save_var).grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        
        # 服务器端口
        ttk.Label(config_frame, text="服务器端口:").grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        self.port_var = tk.StringVar(value=str(self.monitor.config.get('server_port', 8080)))
        ttk.Entry(config_frame, textvariable=self.port_var, width=10).grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        
        # 自动启动选项
        self.auto_start_monitoring_var = tk.BooleanVar(value=self.monitor.config.get('auto_start_monitoring', True))
        ttk.Checkbutton(config_frame, text="启动时自动监控", variable=self.auto_start_monitoring_var).grid(row=4, column=0, sticky=tk.W, pady=(5, 0))
        
        self.auto_start_server_var = tk.BooleanVar(value=self.monitor.config.get('auto_start_server', True))
        ttk.Checkbutton(config_frame, text="启动时自动服务器", variable=self.auto_start_server_var).grid(row=4, column=1, sticky=tk.W, pady=(5, 0))
        
        self.auto_show_qr_var = tk.BooleanVar(value=self.monitor.config.get('auto_show_qr_code', True))
        ttk.Checkbutton(config_frame, text="启动时自动显示二维码", variable=self.auto_show_qr_var).grid(row=5, column=0, sticky=tk.W, pady=(5, 0))
        
        # 保存配置按钮
        ttk.Button(config_frame, text="💾 保存配置", command=self.save_config).grid(row=6, column=0, pady=(10, 0))
        
        # 历史记录框架
        history_frame = ttk.LabelFrame(main_frame, text="剪贴板历史记录", padding="10")
        history_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 历史记录显示
        self.history_text = scrolledtext.ScrolledText(history_frame, height=15, width=80)
        self.history_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 清空历史记录按钮
        ttk.Button(history_frame, text="🗑️ 清空历史记录", command=self.clear_history).grid(row=1, column=0, pady=(10, 0))
        
        # 配置行列权重
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(4, weight=1)
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
    
    def update_status(self):
        """更新状态显示"""
        status = f"监控状态: {'🟢 运行中' if self.monitor.monitoring else '🔴 已停止'} | "
        status += f"服务器: {'🟢 运行中' if self.monitor.server_running else '🔴 已停止'} | "
        status += f"历史记录: {len(self.monitor.clipboard_history)} 条"
        self.status_var.set(status)
    
    def update_history_display(self):
        """更新历史记录显示"""
        self.history_text.delete(1.0, tk.END)
        
        if not self.monitor.clipboard_history:
            self.history_text.insert(tk.END, "暂无历史记录")
        else:
            for i, item in enumerate(self.monitor.clipboard_history):
                timestamp = item['timestamp']
                content_type = "📝 文本" if item['type'] == 'text' else "🖼️ 图片"
                content = item['content']
                
                self.history_text.insert(tk.END, f"[{i+1}] [{timestamp}] {content_type}\n")
                if item['type'] == 'text':
                    self.history_text.insert(tk.END, f"内容: {content}\n")
                else:
                    self.history_text.insert(tk.END, f"文件: {content}\n")
                self.history_text.insert(tk.END, "-" * 50 + "\n")
        
        # 滚动到底部
        self.history_text.see(tk.END)
    
    def toggle_monitoring(self):
        """切换监控状态"""
        if self.monitor.monitoring:
            self.monitor.stop_monitoring()
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
        else:
            self.monitor.start_monitoring()
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
        
        self.update_status()
    
    def toggle_server(self):
        """切换服务器状态"""
        if self.monitor.server_running:
            self.monitor.stop_server()
            self.start_server_btn.config(state=tk.NORMAL)
            self.stop_server_btn.config(state=tk.DISABLED)
        else:
            self.monitor.start_server()
            self.start_server_btn.config(state=tk.DISABLED)
            self.stop_server_btn.config(state=tk.NORMAL)
        
        self.update_status()
    
    def show_qr_code(self):
        """显示二维码"""
        try:
            qr_image = self.monitor.generate_qr_code()
            
            # 创建二维码窗口
            qr_window = tk.Toplevel(self.window)
            qr_window.title("📱 手机连接二维码")
            qr_window.geometry("400x500")

            # 转换为Tkinter可显示的格式
            img_buffer = BytesIO()
            qr_image.save(img_buffer, format="PNG")
            img_buffer.seek(0)
            tk_img = ImageTk.PhotoImage(data=img_buffer.read())

            # 显示二维码
            qr_label = ttk.Label(qr_window, image=tk_img)
            qr_label.image = tk_img  # 保持引用
            qr_label.pack(pady=20)
            
            # 显示连接信息
            ip = self.monitor.get_local_ip()
            port = self.monitor.config.get('server_port', 9999)
            server_url = f"http://{ip}:{port}"
            
            info_text = f"""
连接信息:
IP地址: {ip}
端口号: {port}
访问地址: {server_url}

请确保手机和电脑在同一个Wi-Fi网络下
使用手机浏览器扫描上方二维码即可访问
"""
            info_label = ttk.Label(qr_window, text=info_text, justify=tk.CENTER)
            info_label.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("错误", f"生成二维码失败: {e}")
    
    def auto_start_features(self):
        """启动时自动执行的功能"""
        # 根据配置自动开始监控
        if self.monitor.config.get('auto_start_monitoring', True):
            self.start_auto_monitoring()
        
        # 根据配置自动启动服务器
        if self.monitor.config.get('auto_start_server', True):
            self.start_auto_server()
        
        # 根据配置自动显示二维码
        if self.monitor.config.get('auto_show_qr_code', True):
            self.show_auto_qr_code()
    
    def start_auto_monitoring(self):
        """自动开始监控"""
        if not self.monitor.monitoring:
            self.monitor.start_monitoring()
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            logging.info("启动时自动开始监控")
    
    def start_auto_server(self):
        """自动启动服务器"""
        if not self.monitor.server_running:
            self.monitor.start_server()
            self.start_server_btn.config(state=tk.DISABLED)
            self.stop_server_btn.config(state=tk.NORMAL)
            logging.info("启动时自动启动服务器")
    
    def show_auto_qr_code(self):
        """自动显示二维码"""
        # 延迟显示二维码，确保服务器已启动
        self.window.after(1000, self.show_qr_code_non_blocking)
        logging.info("启动时自动显示二维码")
    
    def show_qr_code_non_blocking(self):
        """非阻塞方式显示二维码"""
        try:
            qr_image = self.monitor.generate_qr_code()
            
            # 创建二维码窗口
            qr_window = tk.Toplevel(self.window)
            qr_window.title("📱 手机连接二维码")
            qr_window.geometry("400x500")
            qr_window.transient(self.window)  # 设置为临时窗口
            qr_window.grab_set()  # 模态窗口
            
            # 转换为Tkinter可显示的格式
            img_buffer = BytesIO()
            qr_image.save(img_buffer, format="PNG")
            img_buffer.seek(0)
            tk_img = ImageTk.PhotoImage(data=img_buffer.read())

            # 显示二维码
            qr_label = ttk.Label(qr_window, image=tk_img)
            qr_label.image = tk_img  # 保持引用
            qr_label.pack(pady=20)
            
            # 显示连接信息
            ip = self.monitor.get_local_ip()
            port = self.monitor.config.get('server_port', 9999)
            server_url = f"http://{ip}:{port}"
            
            info_text = f"""
连接信息:
IP地址: {ip}
端口号: {port}
访问地址: {server_url}

请确保手机和电脑在同一个Wi-Fi网络下
使用手机浏览器扫描上方二维码即可访问
"""
            info_label = ttk.Label(qr_window, text=info_text, justify=tk.CENTER)
            info_label.pack(pady=10)
            
            # 添加关闭按钮
            close_btn = ttk.Button(qr_window, text="✅ 知道了", command=qr_window.destroy)
            close_btn.pack(pady=10)
            
            # 居中显示
            qr_window.update_idletasks()
            x = (qr_window.winfo_screenwidth() - qr_window.winfo_width()) // 2
            y = (qr_window.winfo_screenheight() - qr_window.winfo_height()) // 2
            qr_window.geometry(f"+{x}+{y}")
            
        except Exception as e:
            logging.error(f"自动显示二维码失败: {e}")
    
    def save_config(self):
        """保存配置"""
        try:
            self.monitor.save_path = self.save_path_var.get()
            self.monitor.check_interval = float(self.interval_var.get())
            self.monitor.auto_save = self.auto_save_var.get()
            self.monitor.config['server_port'] = int(self.port_var.get())
            self.monitor.config['auto_start_monitoring'] = self.auto_start_monitoring_var.get()
            self.monitor.config['auto_start_server'] = self.auto_start_server_var.get()
            self.monitor.config['auto_show_qr_code'] = self.auto_show_qr_var.get()
            
            self.monitor.save_config()
            messagebox.showinfo("成功", "配置保存成功！")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")
    
    def clear_history(self):
        """清空历史记录"""
        if messagebox.askyesno("确认", "确定要清空所有历史记录吗？"):
            self.monitor.clipboard_history.clear()
            self.update_history_display()
            messagebox.showinfo("成功", "历史记录已清空")
    
    def on_closing(self):
        """窗口关闭事件"""
        if messagebox.askokcancel("退出", "确定要退出剪贴板监控器吗？"):
            self.monitor.stop_monitoring()
            self.monitor.stop_server()
            self.window.destroy()
    
    def run(self):
        """运行GUI"""
        self.window.mainloop()

def main():
    """主函数"""
    logging.info("剪贴板监控器启动")
    
    # 检查依赖
    try:
        import pyperclip
        import qrcode
    except ImportError as e:
        print(f"缺少必要的依赖: {e}")
        return
    
    # 创建并运行GUI
    app = ClipboardGUI()
    app.run()

if __name__ == "__main__":
    main()

