# 📁 项目结构说明

## 📋 项目概览

剪贴板监控器是一个跨平台的剪贴板同步工具，支持电脑与手机之间的双向内容传输。项目采用模块化设计，包含GUI界面、Web服务器和剪贴板监控核心功能。

## 🏗️ 项目结构

```
clipboard-monitor/
├── 📝 核心代码
│   ├── 剪贴板监控器_fixed2.py    # 主程序 - GUI版本
│   ├── clipboard_test_server.py  # 测试版本 - 稳定运行
│   └── create_icon.py           # 图标生成工具
│
├── ⚙️ 配置文件
│   ├── config.json              # 程序配置文件
│   ├── requirements.txt         # Python依赖列表
│   └── 剪贴板监控器.spec        # PyInstaller打包配置
│
├── 📱 Web界面
│   ├── mobile_test.html         # 手机端测试页面
│   └── clipboard.ico            # 程序图标
│
├── 📋 文档文件
│   ├── README.md                # 项目说明文档
│   ├── CONTRIBUTING.md          # 贡献指南
│   ├── LICENSE                  # MIT许可证
│   ├── PROJECT_STRUCTURE.md     # 项目结构说明
│   ├── 使用说明.md              # 详细使用指南
│   └── 打包说明.md              # 打包发布说明
│
├── 📊 数据文件
│   ├── clipboard_history.txt    # 剪贴板历史记录
│   ├── clipboard_monitor.log    # GUI版本日志
│   └── clipboard_test.log       # 测试版本日志
│
├── 🚀 启动脚本
│   └── 启动剪贴板监控器.bat     # Windows启动脚本
│
└── 📦 打包输出
    └── build/                   # PyInstaller打包输出目录
        └── 剪贴板监控器/
            ├── 剪贴板监控器.exe # 可执行文件
            ├── *.manifest        # 清单文件
            ├── *.toc            # 打包表文件
            └── warn-*.txt       # 警告信息
```

## 🔍 核心模块说明

### 1. 剪贴板监控器_fixed2.py

**主要功能**：完整的GUI应用程序，包含所有功能模块

**核心类**：
- `ClipboardMonitor` - 剪贴板监控核心类
- `ClipboardGUI` - 图形用户界面类

**主要功能**：
- 剪贴板实时监控
- 本地Web服务器
- GUI界面管理
- 配置文件管理
- 二维码生成
- 历史记录管理

### 2. clipboard_test_server.py

**主要功能**：简化版本，专注于稳定运行

**特点**：
- 自动启动监控和服务器
- 无GUI界面，适合后台运行
- 简化的错误处理
- 持续运行模式

### 3. create_icon.py

**主要功能**：生成程序图标

**使用方法**：
```python
python create_icon.py
```

## ⚙️ 配置文件详解

### config.json

```json
{
  "save_path": "clipboard_history.txt",    // 历史记录保存路径
  "check_interval": 1.0,                  // 监控检查间隔（秒）
  "auto_save": true,                      // 是否自动保存
  "max_history": 100,                     // 最大历史记录条数
  "server_port": 9999,                     // Web服务器端口
  "enable_server": true,                  // 是否启用服务器
  "auto_start_monitoring": true,          // 启动时自动监控
  "auto_start_server": true,              // 启动时自动启动服务器
  "auto_show_qr_code": false              // 启动时自动显示二维码
}
```

### requirements.txt

```txt
pyperclip>=1.8.0     # 跨平台剪贴板操作
qrcode>=7.0          # 二维码生成
Pillow>=9.0.0        # 图像处理
```

## 🌐 Web界面结构

### 主要页面
- **/ (根页面)** - 手机端主界面
- **/test** - 兼容性测试页面
- **/api/history** - 历史记录API
- **/api/set_clipboard** - 设置剪贴板API

### 界面特性
- 响应式设计，适配移动设备
- 触摸优化的用户界面
- 实时历史记录更新
- 双向剪贴板同步

## 📊 数据流说明

### 电脑 → 手机流程
```
电脑剪贴板 → ClipboardMonitor.check_clipboard() → add_to_history() → 保存到文件 → Web API → 手机界面显示
```

### 手机 → 电脑流程
```
手机输入 → POST /api/set_clipboard → set_clipboard_content() → pyperclip.copy() → 电脑剪贴板
```

### 监控循环
```
启动监控 → 定时检查 → 检测变化 → 保存记录 → 更新界面
```

## 🔧 开发环境

### 系统要求
- Python 3.7+
- Windows 10/11, macOS, Linux
- 网络连接（用于手机同步）

### 开发工具
- VS Code / PyCharm
- Git
- Python虚拟环境

### 测试环境
- 多浏览器兼容性测试
- 多设备触摸测试
- 网络连接稳定性测试

## 📦 打包发布

### PyInstaller配置
```bash
pyinstaller 剪贴板监控器_fixed2.py --onefile --windowed --icon=clipboard.ico
```

### 打包输出
- 单文件可执行程序
- 无控制台窗口
- 包含所有依赖
- 自定义图标

## 📈 项目演进

### 当前版本特性
- 完整的GUI界面
- 稳定的Web服务器
- 双向剪贴板同步
- 响应式手机界面
- 详细的日志记录

### 未来规划
- 支持图片剪贴板
- 多设备同步
- 云同步功能
- 更多平台支持

## 🙋‍♂️ 获取帮助

- **问题反馈**：[创建Issue](https://github.com/yourusername/clipboard-monitor/issues)
- **使用咨询**：查看[使用说明.md](使用说明.md)
- **技术讨论**：通过Pull Request交流

---

**注意**：项目结构可能会随着版本更新而调整，请以实际代码库为准。