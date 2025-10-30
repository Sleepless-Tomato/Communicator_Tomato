#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""创建剪贴板监控器的图标文件"""

from PIL import Image, ImageDraw

def create_clipboard_icon():
    """创建一个简单的剪贴板图标"""
    # 创建一个256x256的图像
    img = Image.new('RGBA', (256, 256), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制剪贴板的底座（矩形）
    base_color = (70, 130, 180)  # 钢蓝色
    draw.rectangle([64, 160, 192, 224], fill=base_color)
    
    # 绘制剪贴板的夹子部分
    clip_color = (100, 100, 100)  # 灰色
    draw.rectangle([112, 80, 144, 160], fill=clip_color)
    
    # 绘制夹子的圆形部分
    draw.ellipse([104, 70, 152, 118], fill=clip_color)
    
    # 绘制纸张
    paper_color = (255, 255, 255)  # 白色
    draw.rectangle([96, 96, 160, 152], fill=paper_color, outline=(0, 0, 0), width=2)
    
    # 在纸上添加一些线条表示文字
    line_color = (100, 100, 100)
    for i in range(5):
        y = 108 + i * 8
        draw.line([104, y, 152, y], fill=line_color, width=1)
    
    # 保存为ICO格式
    img.save('clipboard.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
    print("图标文件 clipboard.ico 已创建成功！")

if __name__ == "__main__":
    create_clipboard_icon()