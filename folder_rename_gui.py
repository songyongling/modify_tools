import os
import sys
import re
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tkinter.scrolledtext import ScrolledText

class RedirectText:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = ""

    def write(self, string):
        self.buffer += string
        self.text_widget.configure(state=tk.NORMAL)
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.configure(state=tk.DISABLED)
    
    def flush(self):
        pass

class FileRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件夹重命名工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.folder_path = tk.StringVar()
        self.start_file = tk.StringVar()
        self.mode = tk.StringVar(value="increment")
        self.files = []
        
        self.create_widgets()
        
        # 配置样式
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#3498db")
        style.configure("TLabel", font=("Microsoft YaHei", 10))
        style.configure("TRadiobutton", font=("Microsoft YaHei", 10))
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文件夹选择部分
        folder_frame = ttk.LabelFrame(main_frame, text="文件夹选择", padding="10")
        folder_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(folder_frame, text="文件夹路径:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(folder_frame, textvariable=self.folder_path, width=50).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        ttk.Button(folder_frame, text="浏览...", command=self.browse_folder).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(folder_frame, text="加载文件", command=self.load_files).grid(row=0, column=3, padx=5, pady=5)
        
        # 文件列表部分
        files_frame = ttk.LabelFrame(main_frame, text="文件列表", padding="10")
        files_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建带滚动条的列表框
        list_frame = ttk.Frame(files_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Microsoft YaHei", 10))
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        
        scrollbar.config(command=self.file_listbox.yview)
        
        # 操作设置部分
        options_frame = ttk.LabelFrame(main_frame, text="重命名选项", padding="10")
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(options_frame, text="起始文件:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.start_file_entry = ttk.Entry(options_frame, textvariable=self.start_file, width=50, state="readonly")
        self.start_file_entry.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky=tk.W+tk.E)
        
        ttk.Label(options_frame, text="前缀变化方式:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(options_frame, text="递增", variable=self.mode, value="increment").grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Radiobutton(options_frame, text="递减", variable=self.mode, value="decrement").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        
        # 执行按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Button(button_frame, text="执行重命名", command=self.rename_files).pack(side=tk.RIGHT, padx=5)
        
        # 日志输出区域
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = ScrolledText(log_frame, state=tk.DISABLED, wrap=tk.WORD, font=("Microsoft YaHei", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 重定向stdout到文本框
        self.old_stdout = sys.stdout
        sys.stdout = RedirectText(self.log_text)
    
    def browse_folder(self):
        folder_path = filedialog.askdirectory(title="选择文件夹")
        if folder_path:
            self.folder_path.set(folder_path)
            self.load_files()
    
    def load_files(self):
        folder_path = self.folder_path.get()
        if not folder_path:
            messagebox.showerror("错误", "请先选择一个文件夹！")
            return
        
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            messagebox.showerror("错误", "无效的文件夹路径！")
            return
        
        try:
            # 获取文件列表
            self.files = sorted(os.listdir(folder_path))
            
            # 清空并重新填充列表框
            self.file_listbox.delete(0, tk.END)
            for i, item in enumerate(self.files):
                item_path = os.path.join(folder_path, item)
                item_type = "文件夹" if os.path.isdir(item_path) else "文件"
                self.file_listbox.insert(tk.END, f"{i+1}. {item} ({item_type})")
            
            print(f"已加载文件夹 '{folder_path}' 中的 {len(self.files)} 个项目")
            
            # 清空选定的起始文件
            self.start_file.set("")
            self.start_file_entry.config(state="readonly")
        except Exception as e:
            messagebox.showerror("错误", f"读取文件夹内容失败: {e}")
    
    def on_file_select(self, event):
        # 获取选择的项目索引
        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            return
        
        index = int(selected_indices[0])
        if 0 <= index < len(self.files):
            selected_file = self.files[index]
            self.start_file.set(selected_file)
            
            # 获取文件前缀和组信息
            prefix, _ = self.extract_number_prefix(selected_file)
            group = self.get_file_group(selected_file)
            
            info_text = selected_file
            if prefix is not None:
                info_text += f" (前缀: {prefix:02d}"
                if group:
                    info_text += f", 组: {group}"
                info_text += ")"
            
            self.start_file_entry.config(state="normal")
            self.start_file.set(info_text)
            self.start_file_entry.config(state="readonly")
    
    def rename_files(self):
        folder_path = self.folder_path.get()
        start_file = self.start_file.get()
        mode = self.mode.get()
        
        if not folder_path:
            messagebox.showerror("错误", "请先选择一个文件夹！")
            return
        
        if not start_file:
            messagebox.showerror("错误", "请先选择一个起始文件！")
            return
        
        # 从显示文本中提取实际文件名
        start_file_match = re.search(r'^\d+\.\s+([^\s]+)', start_file)
        if start_file_match:
            actual_start_file = start_file_match.group(1)
        else:
            actual_start_file = start_file.split(' ')[0]
        
        # 查找起始文件索引
        try:
            start_index = self.files.index(actual_start_file)
        except ValueError:
            messagebox.showerror("错误", f"找不到文件: {actual_start_file}")
            return
        
        # 执行重命名操作
        self.rename_files_with_new_prefix(folder_path, self.files, start_index, mode)
        
        # 重新加载文件列表以显示修改后的结果
        self.load_files()
    
    def extract_number_prefix(self, filename):
        """从文件名中提取前缀数字（两位数字格式）"""
        match = re.match(r'^(\d{2})(.*)$', filename)
        if match:
            number = int(match.group(1))
            rest = match.group(2)
            return number, rest
        return None, filename
    
    def get_file_group(self, filename):
        """从文件名中提取文件组信息"""
        prefix, rest = self.extract_number_prefix(filename)
        
        if rest == filename:
            return None
        
        group_match = re.match(r'^([^0-9]+)', rest)
        if group_match:
            group_name = group_match.group(1).strip()
            if group_name:
                return group_name
        
        return None
    
    def rename_files_with_new_prefix(self, folder_path, files, start_index, mode="increment"):
        """从指定索引开始重命名文件，修改前缀数字"""
        # 筛选出从开始索引到最后的文件
        files_to_rename = files[start_index:]
        
        if not files_to_rename:
            print("没有找到需要重命名的文件。")
            return
        
        # 获取起始文件的组名和前缀
        start_file = files_to_rename[0]
        start_prefix, _ = self.extract_number_prefix(start_file)
        current_group = self.get_file_group(start_file)
        
        if start_prefix is None:
            print(f"无法识别起始文件 '{start_file}' 的前缀，无法继续。")
            return
        
        if current_group is None:
            print(f"无法识别起始文件 '{start_file}' 的组名，无法继续。")
            return
        
        # 计算第一个组的新前缀
        if mode == "increment":
            # 递增模式：在原有前缀上加1
            new_prefix = min(99, start_prefix + 1)  # 限制最大为99
        else:
            # 递减模式：将前缀减1
            new_prefix = max(0, start_prefix - 1)  # 允许最小为00
        
        # 对这些文件进行重命名
        current_prefix = new_prefix
        renamed_count = 0
        last_group = None
        
        # 显示前缀变化信息
        change_text = "递增" if mode == "increment" else "递减"
        print(f"\n开始重命名文件，起始前缀从 {start_prefix:02d} {change_text}为 {current_prefix:02d}")
        
        for filename in files_to_rename:
            file_path = os.path.join(folder_path, filename)
            
            # 跳过文件夹
            if os.path.isdir(file_path):
                continue
                
            # 提取当前文件的组名
            file_group = self.get_file_group(filename)
            
            # 如果无法识别文件组，跳过此文件
            if file_group is None:
                print(f"跳过 {filename}（无法识别文件组）")
                continue
            
            # 提取当前文件名的数字前缀和剩余部分
            _, rest = self.extract_number_prefix(filename)
            
            # 如果是新的文件组（和前一个文件组不同），根据递增/递减选项调整前缀数字
            if last_group is not None and file_group != last_group:
                if mode == "increment":
                    current_prefix = min(99, current_prefix + 1)  # 限制最大为99
                    print(f"\n检测到新文件组 '{file_group}'，前缀递增至 {current_prefix:02d}")
                else:
                    # 递减模式下，新文件组的前缀反而递增
                    current_prefix = min(99, current_prefix + 1)  # 限制最大为99
                    print(f"\n检测到新文件组 '{file_group}'，前缀递增至 {current_prefix:02d}")
            
            last_group = file_group
            
            # 创建新文件名（保持两位数字前缀格式）
            new_filename = f"{current_prefix:02d}{rest}"
            new_file_path = os.path.join(folder_path, new_filename)
            
            # 如果新文件名与原文件名相同，则跳过
            if new_filename == filename:
                print(f"跳过 {filename}（文件名未改变）")
                continue
            
            # 检查目标文件是否已存在
            if os.path.exists(new_file_path):
                print(f"跳过 {filename}（目标文件 {new_filename} 已存在）")
                continue
            
            # 执行重命名
            try:
                os.rename(file_path, new_file_path)
                print(f"已重命名: {filename} -> {new_filename}")
                renamed_count += 1
            except Exception as e:
                print(f"重命名 {filename} 失败: {e}")
        
        print(f"\n重命名完成！共重命名 {renamed_count} 个文件。")
        
        # 操作完成后弹出提示
        messagebox.showinfo("完成", f"重命名完成！共重命名 {renamed_count} 个文件。")

def main():
    root = tk.Tk()
    app = FileRenamerApp(root)
    
    # 设置窗口图标
    try:
        root.iconbitmap("icon.ico")  # 如果有图标文件的话
    except:
        pass
    
    root.mainloop()
    
    # 恢复stdout
    sys.stdout = app.old_stdout

if __name__ == "__main__":
    main() 