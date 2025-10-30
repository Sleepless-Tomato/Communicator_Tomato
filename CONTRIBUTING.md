# 🤝 贡献指南

感谢您对剪贴板监控器项目的关注！我们欢迎任何形式的贡献，包括代码改进、文档完善、问题报告和功能建议。

## 🚀 开始贡献

### 1. 环境设置

```bash
# 克隆仓库
git clone https://github.com/yourusername/clipboard-monitor.git
cd clipboard-monitor

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 代码规范

#### Python代码规范
- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 代码风格指南
- 使用4个空格进行缩进
- 行长度不超过79个字符
- 使用有意义的变量和函数名

#### 代码示例
```python
# ✅ 正确示例
def check_clipboard_content(self):
    """检查剪贴板内容是否有变化"""
    try:
        current_content = pyperclip.paste()
        content_changed = current_content != self.last_clipboard_content
        
        if content_changed and current_content:
            self.last_clipboard_content = current_content
            self.add_to_history(current_content, 'text')
            return True
        return False
        
    except Exception as e:
        logging.error(f"检查剪贴板时发生错误: {e}")
        return False

# ❌ 错误示例
def check(self):
    try:
        c=pyperclip.paste()
        if c!=self.last:
            self.last=c
            self.add(c,'text')
            return True
        return False
    except:
        return False
```

#### 文档规范
- 使用中文编写文档
- 添加适当的emoji图标增加可读性
- 代码示例使用markdown格式
- 重要信息使用粗体或高亮标记

### 3. 开发流程

1. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **编写代码**
   - 添加适当的注释
   - 确保代码功能完整
   - 进行基本测试

3. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   ```

4. **推送分支**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **创建Pull Request**
   - 详细描述更改内容
   - 说明解决的问题
   - 添加相关截图（如适用）

### 4. 提交信息规范

使用以下格式编写提交信息：

```
类型: 简要描述

详细描述（可选）

相关链接或Issue编号（可选）
```

#### 提交类型
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建工具或依赖更新

#### 示例
```
feat: 添加手机端触摸优化功能

- 优化按钮点击体验
- 添加触摸反馈动画
- 改进移动端布局

Closes #123
```

## 🐛 问题报告

### 报告Bug

1. **搜索现有Issue**：确保问题尚未被报告
2. **提供详细信息**：
   - 操作系统版本
   - Python版本
   - 完整的错误日志
   - 复现步骤
   - 期望行为和实际行为

3. **使用模板**：
   ```markdown
   ## 描述问题
   简要描述遇到的问题

   ## 复现步骤
   1. 启动程序
   2. 进行操作
   3. 出现错误

   ## 环境信息
   - 操作系统: Windows 10
   - Python版本: 3.9.0
   - 程序版本: 1.0.0

   ## 错误日志
   ```
   粘贴完整的错误日志
   ```

   ## 期望行为
   描述期望的结果

   ## 实际行为
   描述实际发生的情况
   ```

### 功能建议

1. **描述需求**：详细说明希望添加的功能
2. **使用场景**：描述功能的使用场景
3. **实现建议**：如果有实现思路可以一并提供
4. **优先级**：说明功能的重要程度

## 📋 代码审查

### 审查清单

- [ ] 代码是否遵循项目规范？
- [ ] 是否有适当的错误处理？
- [ ] 是否添加了必要的注释？
- [ ] 是否影响现有功能？
- [ ] 是否需要更新文档？
- [ ] 是否通过了基本测试？

### 审查标准

1. **功能性**：代码是否正确实现了功能？
2. **可读性**：代码是否易于理解和维护？
3. **性能**：是否有性能优化的空间？
4. **安全性**：是否存在安全风险？
5. **兼容性**：是否兼容不同操作系统？

## 🎯 贡献类型

### 代码贡献
- 修复bug
- 添加新功能
- 优化性能
- 改进用户体验

### 文档贡献
- 完善使用说明
- 添加教程文档
- 翻译文档
- 更新API文档

### 其他贡献
- 测试和反馈
- 设计建议
- 推广宣传
- 用户支持

## 📞 联系方式

- **问题讨论**：
- **代码审查**：通过Pull Request进行
- **一般咨询**：ewrz55555@qq.com

## 🙏 感谢

我们感谢每一位贡献者的时间和努力。您的贡献让这个项目变得更好！

---

**注意**：在开始贡献之前，请确保您已经阅读并理解了项目的[许可证](LICENSE)和[使用条款](README.md)。