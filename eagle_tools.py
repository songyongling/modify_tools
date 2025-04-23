#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
import sys
import os
from eagle_rename_gui import EagleRenamerApp

class EagleToolsApp:
    """Eagle工具集主界面"""
    def __init__(self, root=None):
        if root is None:
            self.root = tk.Tk()
            self.should_destroy_root = True
        else:
            self.root = root
            self.should_destroy_root = False
            
        self.root.title("Eagle工具集")
        self.root.geometry("500x400")
        self.root.minsize(500, 400)
        
        # 设置窗口图标
        try:
            if os.path.exists("icon.ico"):
                self.root.iconbitmap("icon.ico")
        except Exception:
            pass
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="Eagle工具集", 
            font=("Microsoft YaHei", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # 工具按钮区域
        tools_frame = ttk.LabelFrame(main_frame, text="可用工具", padding="10")
        tools_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Eagle文件重命名工具按钮
        eagle_rename_btn = ttk.Button(
            tools_frame,
            text="Eagle文件重命名工具",
            command=self.open_eagle_rename,
            width=30
        )
        eagle_rename_btn.pack(pady=10)
        
        # 创建底部框架
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(20, 0))
        
        # 退出按钮
        exit_btn = ttk.Button(bottom_frame, text="退出", command=self.root.destroy)
        exit_btn.pack(side=tk.RIGHT)
        
    def open_eagle_rename(self):
        """打开Eagle文件重命名工具"""
        # 隐藏主窗口
        self.root.withdraw()
        
        # 创建Eagle文件重命名应用
        eagle_rename_app = EagleRenamerApp()
        
        # 当Eagle文件重命名窗口关闭时，重新显示主窗口
        def on_rename_close():
            self.root.deiconify()
        
        eagle_rename_app.root.protocol("WM_DELETE_WINDOW", on_rename_close)

def main():
    """主程序入口"""
    app = EagleToolsApp()
    app.root.mainloop()

if __name__ == "__main__":
    main() 