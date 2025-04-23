import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import json
import shutil

class RedirectText:
    """将输出重定向到Tkinter文本小部件"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = ""

    def write(self, string):
        self.buffer += string
        self.text_widget.configure(state="normal")
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.configure(state="disabled")
    
    def flush(self):
        self.buffer = ""

class EagleRenamerApp:
    def __init__(self, root=None):
        if root is None:
            self.root = tk.Tk()
            self.root.title("Eagle文件重命名工具")
            self.root.geometry("900x600")
            self.should_destroy_root = True
        else:
            self.root = root
            self.root.title("Eagle文件重命名工具")
            self.should_destroy_root = False
        
        # 设置窗口图标
        try:
            if os.path.exists("icon.ico"):
                self.root.iconbitmap("icon.ico")
        except Exception:
            pass
        
        # 初始化变量
        self.eagle_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.prefix_format = tk.StringVar(value="{:02d}")
        self.start_index = tk.IntVar(value=1)
        self.folders_data = []
        self.selected_folders = []
        
        # 创建GUI界面
        self.create_widgets()
    
    def create_widgets(self):
        """创建GUI组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 上方区域 - Eagle文件夹选择
        folder_frame = ttk.LabelFrame(main_frame, text="Eagle数据选择", padding="10")
        folder_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(folder_frame, text="Eagle数据文件夹:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(folder_frame, textvariable=self.eagle_folder, width=60).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(folder_frame, text="浏览", command=self.browse_eagle_folder).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(folder_frame, text="输出文件夹:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(folder_frame, textvariable=self.output_folder, width=60).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(folder_frame, text="浏览", command=self.browse_output_folder).grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Button(folder_frame, text="加载Eagle数据", command=self.load_eagle_data).grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky=tk.EW)
        
        # 中间区域 - 文件夹列表和选项
        middle_frame = ttk.Frame(main_frame)
        middle_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 文件夹列表框架
        folder_list_frame = ttk.LabelFrame(middle_frame, text="Eagle文件夹列表", padding="10")
        folder_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建文件夹列表
        folder_scroll = ttk.Scrollbar(folder_list_frame)
        folder_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.folder_listbox = tk.Listbox(
            folder_list_frame,
            selectmode=tk.EXTENDED,
            yscrollcommand=folder_scroll.set,
            font=("Courier New", 10)
        )
        self.folder_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        folder_scroll.config(command=self.folder_listbox.yview)
        
        self.folder_listbox.bind('<<ListboxSelect>>', self.on_folder_select)
        
        # 重命名选项框架
        options_frame = ttk.LabelFrame(middle_frame, text="重命名选项", padding="10", width=300)
        options_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)
        
        # 前缀格式
        ttk.Label(options_frame, text="前缀格式:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(options_frame, textvariable=self.prefix_format, width=10).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(options_frame, text="例如: {:02d}").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        
        # 起始索引
        ttk.Label(options_frame, text="起始索引:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(options_frame, from_=1, to=99, textvariable=self.start_index, width=5).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 预览按钮
        ttk.Button(options_frame, text="预览结果", command=self.preview_process).grid(row=2, column=0, columnspan=3, padx=5, pady=10, sticky=tk.EW)
        
        # 执行按钮
        ttk.Button(options_frame, text="执行处理", command=self.execute_process).grid(row=3, column=0, columnspan=3, padx=5, pady=10, sticky=tk.EW)
        
        # 选择操作按钮
        select_frame = ttk.Frame(options_frame)
        select_frame.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Button(select_frame, text="全选", command=self.select_all).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Button(select_frame, text="取消全选", command=self.deselect_all).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Button(select_frame, text="反选", command=self.invert_selection).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # 帮助信息
        help_text = "使用说明:\n" \
                   "1. 选择Eagle数据文件夹\n" \
                   "2. 选择输出文件夹\n" \
                   "3. 加载Eagle数据后选择需要处理的文件夹\n" \
                   "4. 设置前缀格式和起始索引\n" \
                   "5. 预览处理效果\n" \
                   "6. 确认无误后执行处理"
        
        help_label = ttk.Label(options_frame, text=help_text, justify=tk.LEFT, wraplength=280)
        help_label.grid(row=5, column=0, columnspan=3, padx=5, pady=10, sticky=tk.NW)
        
        # 下方区域 - 日志输出
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="10")
        log_frame.pack(fill=tk.X, padx=5, pady=5)
        
        log_scroll = ttk.Scrollbar(log_frame)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(log_frame, height=8, yscrollcommand=log_scroll.set, state="disabled")
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll.config(command=self.log_text.yview)
        
        # 重定向标准输出到日志文本框
        self.stdout_redirect = RedirectText(self.log_text)
    
    def browse_eagle_folder(self):
        """浏览并选择Eagle数据文件夹"""
        folder_selected = filedialog.askdirectory(title="选择Eagle数据文件夹")
        if folder_selected:
            self.eagle_folder.set(folder_selected)
            print(f"已选择Eagle数据文件夹: {folder_selected}")
    
    def browse_output_folder(self):
        """浏览并选择输出文件夹"""
        folder_selected = filedialog.askdirectory(title="选择输出文件夹")
        if folder_selected:
            self.output_folder.set(folder_selected)
            print(f"已选择输出文件夹: {folder_selected}")
    
    def load_eagle_data(self):
        """加载Eagle数据"""
        eagle_folder = self.eagle_folder.get()
        if not eagle_folder or not os.path.isdir(eagle_folder):
            messagebox.showerror("错误", "请选择有效的Eagle数据文件夹")
            return
        
        # 检查是否为有效的Eagle数据文件夹
        if not os.path.exists(os.path.join(eagle_folder, "metadata.json")):
            messagebox.showerror("错误", "所选文件夹不是有效的Eagle数据文件夹")
            return
        
        try:
            # 读取元数据文件
            with open(os.path.join(eagle_folder, "metadata.json"), 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # 检查是否有文件夹数据
            if "folders" not in metadata:
                messagebox.showerror("错误", "未找到Eagle文件夹数据")
                return
            
            # 获取文件夹数据
            self.folders_data = metadata["folders"]
            
            # 清空并填充列表框
            self.folder_listbox.delete(0, tk.END)
            
            # 按文件夹名称排序
            sorted_folders = sorted(self.folders_data, key=lambda x: x.get("name", "").lower())
            
            for folder in sorted_folders:
                folder_name = folder.get("name", "未命名文件夹")
                folder_id = folder.get("id", "")
                self.folder_listbox.insert(tk.END, f"{folder_name} (ID: {folder_id})")
            
            print(f"已加载 {len(self.folders_data)} 个Eagle文件夹")
        
        except Exception as e:
            messagebox.showerror("错误", f"加载Eagle数据时出错: {str(e)}")
    
    def on_folder_select(self, event):
        """处理文件夹选择事件"""
        selection = self.folder_listbox.curselection()
        if selection:
            self.selected_folders = [self.folders_data[i] for i in selection]
            print(f"已选择 {len(self.selected_folders)} 个文件夹")
    
    def select_all(self):
        """选择所有文件夹"""
        self.folder_listbox.select_set(0, tk.END)
        self.on_folder_select(None)
    
    def deselect_all(self):
        """取消选择所有文件夹"""
        self.folder_listbox.selection_clear(0, tk.END)
        self.selected_folders = []
        print("已取消所有选择")
    
    def invert_selection(self):
        """反转选择"""
        selected = set(self.folder_listbox.curselection())
        all_indices = set(range(len(self.folders_data)))
        
        # 清除当前选择
        self.folder_listbox.selection_clear(0, tk.END)
        
        # 选择未选择的项目
        for i in all_indices - selected:
            self.folder_listbox.selection_set(i)
        
        self.on_folder_select(None)
    
    def preview_process(self):
        """预览处理结果"""
        if not self.selected_folders:
            messagebox.showinfo("提示", "请选择要处理的Eagle文件夹")
            return
        
        if not self.output_folder.get():
            messagebox.showinfo("提示", "请选择输出文件夹")
            return
        
        try:
            eagle_folder = self.eagle_folder.get()
            output_folder = self.output_folder.get()
            prefix_format = self.prefix_format.get()
            start_idx = self.start_index.get()
            
            # 生成预览信息
            preview_info = "处理预览:\n\n"
            for i, folder in enumerate(self.selected_folders):
                folder_name = folder.get("name", "未命名文件夹")
                folder_id = folder.get("id", "")
                
                # 构建新的文件夹名称
                new_prefix = prefix_format.format(start_idx + i)
                new_folder_name = f"{new_prefix}_{folder_name}"
                
                preview_info += f"{folder_name} -> {new_folder_name}\n"
                
                # 检查该文件夹下有多少图片
                folder_path = os.path.join(eagle_folder, "images", folder_id)
                if os.path.exists(folder_path):
                    image_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and not f.endswith('.info')]
                    preview_info += f"  - 包含 {len(image_files)} 个文件\n"
                else:
                    preview_info += "  - 文件夹不存在或为空\n"
            
            # 显示预览对话框
            preview_window = tk.Toplevel(self.root)
            preview_window.title("处理预览")
            preview_window.geometry("600x400")
            
            # 预览文本框
            preview_scroll = ttk.Scrollbar(preview_window)
            preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            preview_text = tk.Text(
                preview_window,
                yscrollcommand=preview_scroll.set,
                font=("Courier New", 10)
            )
            preview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            preview_scroll.config(command=preview_text.yview)
            
            # 添加预览内容
            preview_text.insert(tk.END, preview_info)
            
            # 添加按钮
            button_frame = ttk.Frame(preview_window)
            button_frame.pack(fill=tk.X, padx=10, pady=10)
            
            ttk.Button(
                button_frame, 
                text="关闭", 
                command=preview_window.destroy
            ).pack(side=tk.RIGHT, padx=5)
            
            ttk.Button(
                button_frame, 
                text="执行处理", 
                command=lambda: [self.execute_process(), preview_window.destroy()]
            ).pack(side=tk.RIGHT, padx=5)
            
            print("已生成处理预览")
        
        except Exception as e:
            messagebox.showerror("错误", f"生成预览时出错: {str(e)}")
    
    def execute_process(self):
        """执行处理操作"""
        if not self.selected_folders:
            messagebox.showinfo("提示", "请选择要处理的Eagle文件夹")
            return
        
        if not self.output_folder.get():
            messagebox.showinfo("提示", "请选择输出文件夹")
            return
        
        try:
            # 创建一个线程来执行处理操作
            process_thread = threading.Thread(target=self._process_folders_thread)
            process_thread.start()
            
        except Exception as e:
            messagebox.showerror("错误", f"执行处理时出错: {str(e)}")
    
    def _process_folders_thread(self):
        """在单独的线程中执行处理操作"""
        eagle_folder = self.eagle_folder.get()
        output_folder = self.output_folder.get()
        prefix_format = self.prefix_format.get()
        start_idx = self.start_index.get()
        
        success_count = 0
        error_count = 0
        
        try:
            # 确保输出文件夹存在
            os.makedirs(output_folder, exist_ok=True)
            
            # 处理每个选定的文件夹
            for i, folder in enumerate(self.selected_folders):
                folder_name = folder.get("name", "未命名文件夹")
                folder_id = folder.get("id", "")
                
                # 构建新的文件夹名称
                new_prefix = prefix_format.format(start_idx + i)
                new_folder_name = f"{new_prefix}_{folder_name}"
                
                # 创建输出子文件夹
                new_folder_path = os.path.join(output_folder, new_folder_name)
                os.makedirs(new_folder_path, exist_ok=True)
                
                # 复制该文件夹下的所有图片
                folder_path = os.path.join(eagle_folder, "images", folder_id)
                
                if os.path.exists(folder_path):
                    # 获取所有文件（排除.info文件）
                    image_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and not f.endswith('.info')]
                    
                    # 复制每个文件
                    for j, filename in enumerate(image_files):
                        src_file = os.path.join(folder_path, filename)
                        
                        # 获取文件扩展名
                        _, ext = os.path.splitext(filename)
                        
                        # 创建新的文件名
                        new_filename = f"{j+1:03d}{ext}"
                        dst_file = os.path.join(new_folder_path, new_filename)
                        
                        try:
                            shutil.copy2(src_file, dst_file)
                            print(f"已复制: {filename} -> {new_folder_name}/{new_filename}")
                        except Exception as e:
                            print(f"复制文件失败: {filename} -> {new_filename}")
                            print(f"错误: {str(e)}")
                            error_count += 1
                    
                    print(f"已处理文件夹: {folder_name} -> {new_folder_name} (共 {len(image_files)} 个文件)")
                    success_count += 1
                else:
                    print(f"文件夹不存在或为空: {folder_name}")
                    error_count += 1
            
            # 显示完成消息
            self.root.after(0, lambda: messagebox.showinfo(
                "完成", 
                f"处理操作完成\n成功: {success_count} 个文件夹\n失败: {error_count} 个文件夹"
            ))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"处理过程中出错: {str(e)}"))

def main():
    root = tk.Tk()
    root.title("Eagle文件重命名工具")
    root.geometry("900x600")
    
    # 设置窗口图标
    try:
        if os.path.exists("icon.ico"):
            root.iconbitmap("icon.ico")
    except Exception:
        pass
    
    app = EagleRenamerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 