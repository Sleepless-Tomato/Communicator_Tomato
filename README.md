# 📋 剪贴板监控器 - 跨设备剪贴板同步工具

https://github.com/Sleepless-Tomato/Communicator_Tomato
一个强大的跨设备剪贴板同步工具，支持电脑与手机之间的双向剪贴板内容传输。通过本地Web服务器和二维码连接，实现无缝的剪贴板同步体验。

## 🌟 功能特性

### 🔧 核心功能
- **双向同步**：电脑 ↔ 手机剪贴板内容双向同步
- **实时监控**：自动监控电脑剪贴板变化
- **Web界面**：手机浏览器直接访问，无需安装APP
- **二维码连接**：快速扫码连接，简化配置过程
- **历史记录**：保存剪贴板历史，支持查看和管理

### 📱 手机端功能
- **发送文字**：手机输入文字发送到电脑剪贴板
- **查看历史**：实时查看电脑剪贴板历史记录
- **触摸优化**：专为移动设备优化的UI界面
- **自动刷新**：定时刷新历史记录
- **复制功能**：一键复制历史记录中的内容

### 💻 电脑端功能
- **GUI界面**：直观的图形化操作界面
- **服务器管理**：启动/停止本地Web服务器
- **配置管理**：灵活的参数配置和保存
- **日志记录**：详细的运行日志和错误追踪
- **自动启动**：支持开机自动启动和连接

## 🚀 快速开始

### 系统要求
- Python 3.7 或更高版本
- Windows 10/11、macOS 或 Linux
- 同一Wi-Fi网络下的手机设备

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

#### GUI版本（推荐）
```bash
python 剪贴板监控器_fixed2.py
```

#### 测试版本（稳定运行）
```bash
python clipboard_test_server.py
```

### 连接手机

1. 确保手机和电脑连接在同一Wi-Fi网络
2. 在手机浏览器中访问电脑的IP地址和端口（默认 `http://电脑IP:9999`）
3. 或使用GUI版本生成的二维码扫描连接

## 📋 使用说明

### 电脑 → 手机同步
1. 启动电脑端程序
2. 开始监控剪贴板
3. 在电脑上复制任何文字
4. 手机访问Web页面即可查看历史记录

### 手机 → 电脑同步
1. 在手机Web页面的"手机粘贴到电脑"区域输入文字
2. 点击"📤 发送到电脑"按钮
3. 文字将自动设置为电脑剪贴板内容
4. 在电脑上粘贴即可使用

### GUI界面操作
- **▶️ 开始监控**：启动剪贴板监控
- **⏹️ 停止监控**：停止剪贴板监控
- **🚀 启动服务器**：启动Web服务器
- **🛑 停止服务器**：停止Web服务器
- **🔲 生成二维码**：显示连接二维码
- **🗑️ 清空历史**：清空剪贴板历史记录

## ⚙️ 配置说明

### 配置文件 (config.json)
```json
{
  "save_path": "clipboard_history.txt",
  "check_interval": 1.0,
  "auto_save": true,
  "max_history": 100,
  "server_port": 9999,
  "enable_server": true,
  "auto_start_monitoring": true,
  "auto_start_server": true,
  "auto_show_qr_code": false
}
```

### 配置参数说明
- **save_path**: 剪贴板历史保存文件路径
- **check_interval**: 剪贴板检查间隔（秒）
- **auto_save**: 是否自动保存剪贴板内容
- **max_history**: 最大历史记录条数
- **server_port**: Web服务器端口号
- **auto_start_monitoring**: 启动时是否自动开始监控
- **auto_start_server**: 启动时是否自动启动服务器
- **auto_show_qr_code**: 启动时是否自动显示二维码

## 📱 手机端界面

### 界面特色
- **响应式设计**：适配各种屏幕尺寸
- **触摸优化**：按钮大小适合手指点击
- **视觉反馈**：操作时有明确的视觉反馈
- **平滑滚动**：支持流畅的触摸滚动

### 主要功能区域
1. **连接信息**：显示电脑IP、端口和连接状态
2. **控制按钮**：刷新历史、复制全文等功能
3. **手机粘贴区**：输入文字发送到电脑
4. **历史记录**：显示电脑剪贴板历史

## 🔧 技术架构

### 核心组件
- **pyperclip**: 跨平台剪贴板操作
- **qrcode**: 二维码生成
- **tkinter**: GUI界面
- **http.server**: 本地Web服务器
- **PIL**: 图像处理

### API接口
- `GET /` - 手机Web界面
- `GET /api/history` - 获取剪贴板历史
- `POST /api/set_clipboard` - 设置电脑剪贴板

### 数据流
```
电脑剪贴板 → 监控器 → 历史记录 → Web API → 手机界面
手机输入 → Web API → 电脑剪贴板 ← pyperclip
```

## 📊 日志和监控

### 日志文件
- **clipboard_monitor.log**: GUI版本运行日志
- **clipboard_test.log**: 测试版本运行日志
- **clipboard_history.txt**: 剪贴板历史记录

### 日志级别
- INFO: 正常操作日志
- ERROR: 错误信息
- WARNING: 警告信息

## 🛠️ 故障排除

### 常见问题

#### Q: 手机无法连接电脑
**A:** 
1. 检查是否在同一Wi-Fi网络
2. 确认防火墙未阻止端口9999
3. 验证电脑IP地址是否正确

#### Q: 发送文字失败
**A:**
1. 检查文字长度（≤1000字符）
2. 确认服务器正在运行
3. 查看日志文件获取错误信息

#### Q: 历史记录不更新
**A:**
1. 确认监控功能已启动
2. 检查剪贴板是否有新内容
3. 重启监控服务

### 调试技巧
```bash
# 查看实时日志
tail -f clipboard_monitor.log

# 测试本地连接
curl http://localhost:9999/api/history

# 检查端口占用
netstat -an | grep 9999
```

## 📦 打包发布

### 使用PyInstaller打包
```bash
pyinstaller 剪贴板监控器_fixed2.py --onefile --windowed --icon=clipboard.ico
```

### 打包配置
- 单文件模式：便于分发
- 窗口模式：无控制台窗口
- 自定义图标：专业外观

## 🤝 贡献指南

### 开发环境设置
```bash
# 克隆仓库
git clone https://github.com/yourusername/clipboard-monitor.git

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 安装开发依赖
pip install -r requirements.txt
```

### 代码规范
- 使用PEP 8代码风格
- 添加适当的注释和文档
- 编写单元测试
- 提交前运行代码检查

### 提交流程
1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证，详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- 感谢所有贡献者和用户
- 特别感谢测试团队的反馈
- 开源社区的支持

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 发送邮件至: ewrz55555@qq.com

---


**注意**：使用前请确保已安装所有依赖项，并仔细阅读使用说明。
