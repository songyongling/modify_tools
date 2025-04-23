import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import importlib.util
import subprocess

class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件重命名工具集")
        self.root.geometry("400x350")
        self.root.resizable(True, True)
        
        # 设置窗口图标
        try:
            if os.path.exists("icon.ico"):
                self.root.iconbitmap("icon.ico")
        except Exception:
            pass
        
        self.create_widgets()
    
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题标签
        title_label = ttk.Label(main_frame, text="文件重命名工具集", font=("Microsoft YaHei", 16, "bold"))
        title_label.pack(pady=20)
        
        # 说明标签
        desc_label = ttk.Label(main_frame, text="请选择要使用的工具：", font=("Microsoft YaHei", 10))
        desc_label.pack(pady=10)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        # 文件夹重命名按钮 - 减小按钮间距
        folder_rename_btn = ttk.Button(
            button_frame, 
            text="文件夹重命名", 
            command=self.launch_folder_rename,
            width=20
        )
        folder_rename_btn.pack(pady=5)  # 减小间距
        
        # Eagle重命名按钮
        eagle_rename_btn = ttk.Button(
            button_frame, 
            text="Eagle文件重命名", 
            command=self.launch_eagle_rename,
            width=20
        )
        eagle_rename_btn.pack(pady=5)  # 减小间距
        
        # 底部版权信息
        version_label = ttk.Label(main_frame, text="版本 1.0.0", font=("Microsoft YaHei", 8))
        version_label.pack(side=tk.BOTTOM, pady=5)
        
        # 设置样式 - 减小按钮内部填充
        style = ttk.Style()
        style.configure("TButton", font=("Microsoft YaHei", 10), padding=8)  # 减少内边距
        style.configure("TLabel", font=("Microsoft YaHei", 10))
    
    def launch_folder_rename(self):
        """启动文件夹重命名工具"""
        # 获取当前执行文件的路径
        try:
            if getattr(sys, 'frozen', False):
                # 如果是打包后的环境
                application_path = os.path.dirname(sys.executable)
                module_path = os.path.join(application_path, "folder_rename_gui_app.exe")
                if not os.path.exists(module_path):
                    # 查找同级目录下的可执行文件
                    parent_dir = os.path.dirname(application_path)
                    module_path = os.path.join(parent_dir, "folder_rename_gui_app.exe")
                    if not os.path.exists(module_path):
                        # 尝试在其他可能的位置查找
                        module_path = os.path.join(os.path.dirname(parent_dir), "folder_rename_gui_app.exe")
                        if not os.path.exists(module_path):
                            # 最后尝试在当前目录查找
                            module_path = "folder_rename_gui.py"
            else:
                # 开发环境
                module_path = "folder_rename_gui.py"
            
            print(f"尝试启动: {module_path}")
            
            self.root.withdraw()  # 隐藏主窗口
            
            if os.path.exists(module_path):
                if module_path.endswith('.exe'):
                    # 启动可执行文件
                    subprocess.Popen([module_path])
                else:
                    # 启动Python脚本
                    subprocess.Popen([sys.executable, module_path])
                
                # 稍后恢复主窗口可见
                self.root.after(500, self.check_subprocess_and_return)
            else:
                messagebox.showerror("错误", f"找不到文件夹重命名工具！\n{module_path}")
                self.root.deiconify()
        except Exception as e:
            self.root.deiconify()  # 确保主窗口重新显示
            messagebox.showerror("错误", f"启动文件夹重命名工具失败：\n{str(e)}")
    
    def check_subprocess_and_return(self):
        """检查子进程并在适当时机返回主窗口"""
        # 这里只是简单延迟返回，实际可能需要更复杂的逻辑
        self.root.deiconify()
    
    def launch_eagle_rename(self):
        """启动Eagle重命名工具"""
        # 获取当前执行文件的路径
        try:
            if getattr(sys, 'frozen', False):
                # 如果是打包后的环境
                application_path = os.path.dirname(sys.executable)
                module_path = os.path.join(application_path, "eagle_rename_gui_app.exe")
                if not os.path.exists(module_path):
                    # 查找同级目录下的可执行文件
                    parent_dir = os.path.dirname(application_path)
                    module_path = os.path.join(parent_dir, "eagle_rename_gui_app.exe")
                    if not os.path.exists(module_path):
                        # 尝试在其他可能的位置查找
                        module_path = os.path.join(os.path.dirname(parent_dir), "eagle_rename_gui_app.exe")
                        if not os.path.exists(module_path):
                            # 最后尝试在当前目录查找
                            module_path = "eagle_rename_gui.py"
            else:
                # 开发环境
                module_path = "eagle_rename_gui.py"
            
            print(f"尝试启动: {module_path}")
            
            self.root.withdraw()  # 隐藏主窗口
            
            if os.path.exists(module_path):
                if module_path.endswith('.exe'):
                    # 启动可执行文件
                    subprocess.Popen([module_path])
                else:
                    # 启动Python脚本
                    subprocess.Popen([sys.executable, module_path])
                
                # 稍后恢复主窗口可见
                self.root.after(500, self.check_subprocess_and_return)
            else:
                messagebox.showerror("错误", f"找不到Eagle文件重命名工具！\n{module_path}")
                self.root.deiconify()
        except Exception as e:
            self.root.deiconify()  # 确保主窗口重新显示
            messagebox.showerror("错误", f"启动Eagle文件重命名工具失败：\n{str(e)}")
    
    def launch_tool(self, module_file, tool_name):
        """通用工具启动方法"""
        # 首先检查文件是否存在
        if not os.path.exists(module_file):
            messagebox.showerror("错误", f"找不到{tool_name}工具！\n缺少文件: {module_file}")
            return
        
        try:
            # 方法1：通过importlib动态导入并运行模块
            self.root.withdraw()  # 隐藏主窗口
            
            try:
                # 尝试导入并运行模块
                spec = importlib.util.spec_from_file_location("module.name", module_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 调用模块的main函数
                if hasattr(module, 'main'):
                    module.main()
                else:
                    raise AttributeError(f"{module_file} 中未找到main函数")
                
            except Exception as e:
                # 如果importlib方法失败，尝试使用subprocess启动
                print(f"通过importlib启动失败: {e}，尝试使用subprocess")
                subprocess.Popen([sys.executable, module_file])
            
            # 启动后，显示主窗口
            self.root.deiconify()
            
        except Exception as e:
            self.root.deiconify()  # 确保主窗口重新显示
            messagebox.showerror("错误", f"启动{tool_name}工具失败：\n{str(e)}")

def main():
    root = tk.Tk()
    app = LauncherApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 