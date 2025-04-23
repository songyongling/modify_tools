import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import json
import shutil
import sys

class RedirectText:
    """用于将控制台输出重定向到Tkinter文本控件"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = ""
        
    def write(self, string):
        self.buffer += string
        self.update_text_widget()
    
    def flush(self):
        self.update_text_widget()
        self.buffer = ""
    
    def update_text_widget(self):
        self.text_widget.configure(state=tk.NORMAL)
        self.text_widget.insert(tk.END, self.buffer)
        self.text_widget.see(tk.END)
        self.text_widget.configure(state=tk.DISABLED)
        self.buffer = ""

class EagleRenamerApp:
    def __init__(self, root=None):
        if root is None:
            self.root = tk.Tk()
            self.should_destroy_root = True
        else:
            self.root = root
            self.should_destroy_root = False
            
        self.root.title("Eagle文件重命名")
        self.root.geometry("900x700")
        self.root.minsize(900, 700)
        
        # 设置窗口图标
        try:
            if os.path.exists("icon.ico"):
                self.root.iconbitmap("icon.ico")
        except Exception:
            pass
        
        # 初始化变量
        self.eagle_folder = None
        self.eagle_files = []  # 存储Eagle文件信息
        self.selected_files = []  # 存储选中的文件
        self.start_index = tk.IntVar(value=1)
        self.prefix_mode = tk.StringVar(value="increment")
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建顶部框架 - 文件夹路径输入
        path_frame = ttk.LabelFrame(main_frame, text="Eagle文件夹路径", padding="10")
        path_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 文件夹路径输入框和浏览按钮
        path_input_frame = ttk.Frame(path_frame)
        path_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(path_input_frame, text="Eagle文件夹:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.eagle_path_var = tk.StringVar()
        self.eagle_path_entry = ttk.Entry(path_input_frame, textvariable=self.eagle_path_var, width=60)
        self.eagle_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_btn = ttk.Button(path_input_frame, text="浏览...", command=self.browse_eagle_folder)
        browse_btn.pack(side=tk.LEFT)
        
        # 描述标签
        description_frame = ttk.Frame(path_frame)
        description_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(
            description_frame, 
            text="请选择Eagle软件的数据文件夹，通常位于'文档/Eagle/Library'目录下。", 
            wraplength=800
        ).pack(fill=tk.X)
        
        # 功能按钮框架
        buttons_frame = ttk.Frame(path_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        load_btn = ttk.Button(buttons_frame, text="加载Eagle文件", command=self.load_eagle_files)
        load_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 创建中间部分 - 左侧文件列表、右侧选项
        middle_frame = ttk.Frame(main_frame)
        middle_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧 - 文件列表
        files_frame = ttk.LabelFrame(middle_frame, text="Eagle文件列表", padding="10")
        files_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 创建表格
        columns = ("序号", "文件ID", "文件名", "类型")
        self.file_tree = ttk.Treeview(files_frame, columns=columns, show="headings", selectmode="extended")
        
        # 定义列
        self.file_tree.heading("序号", text="序号")
        self.file_tree.heading("文件ID", text="文件ID")
        self.file_tree.heading("文件名", text="文件名")
        self.file_tree.heading("类型", text="类型")
        
        self.file_tree.column("序号", width=50, anchor="center")
        self.file_tree.column("文件ID", width=150)
        self.file_tree.column("文件名", width=400)
        self.file_tree.column("类型", width=80, anchor="center")
        
        # 添加滚动条
        tree_scroll = ttk.Scrollbar(files_frame, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=tree_scroll.set)
        
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 绑定选择事件
        self.file_tree.bind("<<TreeviewSelect>>", self.on_file_select)
        
        # 右侧 - 操作选项
        options_frame = ttk.LabelFrame(middle_frame, text="重命名选项", padding="10", width=300)
        options_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        options_frame.pack_propagate(False)  # 防止框架被内容压缩
        
        # 选择和操作按钮
        select_frame = ttk.Frame(options_frame)
        select_frame.pack(fill=tk.X, pady=10)
        
        select_all_btn = ttk.Button(select_frame, text="全选", command=self.select_all)
        select_all_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        deselect_all_btn = ttk.Button(select_frame, text="取消全选", command=self.deselect_all)
        deselect_all_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        invert_btn = ttk.Button(select_frame, text="反选", command=self.invert_selection)
        invert_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # 起始索引设置
        index_frame = ttk.Frame(options_frame)
        index_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(index_frame, text="起始索引:").pack(side=tk.LEFT)
        
        index_spinbox = ttk.Spinbox(
            index_frame, 
            from_=1, 
            to=99, 
            textvariable=self.start_index, 
            width=5
        )
        index_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        # 前缀模式选择
        mode_frame = ttk.LabelFrame(options_frame, text="前缀变化方式", padding="10")
        mode_frame.pack(fill=tk.X, pady=10)
        
        ttk.Radiobutton(
            mode_frame, 
            text="递增", 
            value="increment", 
            variable=self.prefix_mode
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(
            mode_frame, 
            text="递减", 
            value="decrement", 
            variable=self.prefix_mode
        ).pack(anchor=tk.W, pady=2)
        
        # 预览和执行按钮
        preview_btn = ttk.Button(options_frame, text="预览重命名", command=self.preview_rename)
        preview_btn.pack(fill=tk.X, pady=(20, 5))
        
        execute_btn = ttk.Button(options_frame, text="执行重命名", command=self.execute_rename)
        execute_btn.pack(fill=tk.X, pady=5)
        
        # 创建操作日志框架（底部）
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="10")
        log_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 添加滚动条
        log_scroll = ttk.Scrollbar(log_frame, orient="vertical")
        self.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD, state=tk.DISABLED, yscrollcommand=log_scroll.set)
        log_scroll.config(command=self.log_text.yview)
        
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 重定向标准输出到日志窗口
        self.redirect = RedirectText(self.log_text)
        sys.stdout = self.redirect
        
        # 设置样式
        style = ttk.Style()
        style.configure("TButton", font=("Microsoft YaHei", 10))
        style.configure("TLabel", font=("Microsoft YaHei", 10))
        style.configure("TLabelframe.Label", font=("Microsoft YaHei", 10, "bold"))
    
    def browse_eagle_folder(self):
        """浏览并选择Eagle文件夹"""
        # 默认打开用户文档目录下的Eagle文件夹
        default_dir = os.path.join(os.path.expanduser("~"), "Documents", "Eagle", "Library")
        if not os.path.exists(default_dir):
            default_dir = os.path.expanduser("~")
            
        folder_path = filedialog.askdirectory(
            title="选择Eagle文件夹",
            initialdir=default_dir
        )
        
        if folder_path:
            self.eagle_path_var.set(folder_path)
            print(f"已选择Eagle文件夹: {folder_path}")
    
    def load_eagle_files(self):
        """加载Eagle文件夹中的文件"""
        eagle_folder = self.eagle_path_var.get().strip()
        
        if not eagle_folder:
            messagebox.showwarning("警告", "请先选择Eagle文件夹!")
            return
            
        if not os.path.isdir(eagle_folder):
            messagebox.showerror("错误", f"文件夹不存在: {eagle_folder}")
            return
        
        # 保存Eagle文件夹路径
        self.eagle_folder = eagle_folder
        
        # 清空文件树和数据
        self.file_tree.delete(*self.file_tree.get_children())
        self.eagle_files = []
        
        # 检查images文件夹
        images_folder = os.path.join(eagle_folder, "images")
        if not os.path.exists(images_folder):
            messagebox.showerror("错误", f"未找到images文件夹: {images_folder}\n这可能不是一个有效的Eagle库文件夹。")
            return
        
        print(f"开始扫描Eagle文件夹: {eagle_folder}")
        
        try:
            # 扫描images文件夹中所有的子文件夹
            folder_count = 0
            for folder_name in os.listdir(images_folder):
                folder_path = os.path.join(images_folder, folder_name)
                
                # 只处理文件夹，而且是以.info结尾的
                if os.path.isdir(folder_path) and folder_name.endswith(".info"):
                    folder_count += 1
                    
                    # 文件ID (去掉.info后缀)
                    file_id = folder_name[:-5] if folder_name.endswith(".info") else folder_name
                    
                    # 查找metadata.json文件
                    metadata_file = os.path.join(folder_path, "metadata.json")
                    if os.path.exists(metadata_file):
                        try:
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                                
                                # 获取文件名和类型
                                file_name = metadata.get("name", "未知")
                                file_ext = metadata.get("ext", "").lower()
                                
                                # 找到对应的实际文件
                                actual_files = [f for f in os.listdir(folder_path) 
                                              if os.path.isfile(os.path.join(folder_path, f)) 
                                              and not f.endswith('.json') 
                                              and not f.endswith('.png')]
                                
                                actual_file = actual_files[0] if actual_files else None
                                
                                # 保存文件信息
                                file_info = {
                                    "id": file_id,
                                    "folder": folder_path,
                                    "metadata_file": metadata_file,
                                    "name": file_name,
                                    "type": file_ext,
                                    "actual_file": actual_file,
                                    "metadata": metadata
                                }
                                
                                self.eagle_files.append(file_info)
                                
                                # 添加到界面
                                self.file_tree.insert("", "end", values=(
                                    folder_count,
                                    file_id,
                                    file_name,
                                    file_ext.upper()
                                ))
                        except Exception as e:
                            print(f"处理文件{metadata_file}时发生错误: {str(e)}")
            
            print(f"扫描完成，共找到 {folder_count} 个Eagle文件，有效文件 {len(self.eagle_files)} 个")
            
            if not self.eagle_files:
                messagebox.showinfo("提示", "未找到Eagle文件，请确认选择了正确的Eagle库文件夹。")
            
        except Exception as e:
            messagebox.showerror("错误", f"扫描Eagle文件夹时发生错误: {str(e)}")
    
    def on_file_select(self, event):
        """处理文件选择事件"""
        self.selected_files = []
        for item_id in self.file_tree.selection():
            item_index = self.file_tree.index(item_id)
            if 0 <= item_index < len(self.eagle_files):
                self.selected_files.append(self.eagle_files[item_index])
        
        print(f"已选择 {len(self.selected_files)} 个文件")
    
    def select_all(self):
        """选择所有文件"""
        self.file_tree.selection_set(self.file_tree.get_children())
        self.on_file_select(None)
    
    def deselect_all(self):
        """取消选择所有文件"""
        self.file_tree.selection_remove(self.file_tree.get_children())
        self.selected_files = []
        print("已取消所有选择")
    
    def invert_selection(self):
        """反选"""
        all_items = self.file_tree.get_children()
        selected_items = self.file_tree.selection()
        
        # 取消当前选择
        self.file_tree.selection_remove(selected_items)
        
        # 选择未选择的项目
        for item in all_items:
            if item not in selected_items:
                self.file_tree.selection_add(item)
        
        self.on_file_select(None)
    
    def preview_rename(self):
        """预览重命名结果"""
        if not self.selected_files:
            messagebox.showwarning("警告", "请先选择要重命名的文件!")
            return
        
        start_idx = self.start_index.get()
        mode = self.prefix_mode.get()
        
        # 创建预览窗口
        preview_window = tk.Toplevel(self.root)
        preview_window.title("重命名预览")
        preview_window.geometry("800x500")
        preview_window.minsize(800, 500)
        
        # 添加预览表格
        preview_frame = ttk.Frame(preview_window, padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        preview_columns = ("序号", "原文件名", "新文件名")
        preview_tree = ttk.Treeview(preview_frame, columns=preview_columns, show="headings")
        
        preview_tree.heading("序号", text="序号")
        preview_tree.heading("原文件名", text="原文件名")
        preview_tree.heading("新文件名", text="新文件名")
        
        preview_tree.column("序号", width=50, anchor="center")
        preview_tree.column("原文件名", width=350)
        preview_tree.column("新文件名", width=350)
        
        # 添加滚动条
        preview_scroll = ttk.Scrollbar(preview_frame, orient="vertical", command=preview_tree.yview)
        preview_tree.configure(yscrollcommand=preview_scroll.set)
        
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        preview_tree.pack(fill=tk.BOTH, expand=True)
        
        # 生成预览数据
        original_names = []
        new_names = []
        
        for i, file_info in enumerate(self.selected_files):
            original_name = file_info["name"]
            original_names.append(original_name)
            
            # 提取前缀和后缀
            match = re.match(r'^(\d+)(.+?)(\d+)$', original_name)
            if match:
                prefix, main_part, suffix = match.groups()
                
                # 根据模式递增或递减前缀
                if mode == "increment":
                    new_prefix = str(min(99, start_idx + i)).zfill(len(prefix))
                else:  # decrement
                    new_prefix = str(max(1, start_idx - i)).zfill(len(prefix))
                
                new_name = f"{new_prefix}{main_part}{suffix}"
            else:
                # 如果不符合预期格式，则添加新前缀
                if mode == "increment":
                    new_prefix = str(min(99, start_idx + i)).zfill(2)
                else:  # decrement
                    new_prefix = str(max(1, start_idx - i)).zfill(2)
                
                new_name = f"{new_prefix}_{original_name}"
            
            new_names.append(new_name)
            
            # 添加到预览表格
            preview_tree.insert("", "end", values=(i+1, original_name, new_name))
        
        # 添加按钮
        button_frame = ttk.Frame(preview_window, padding="10")
        button_frame.pack(fill=tk.X)
        
        close_btn = ttk.Button(button_frame, text="关闭", command=preview_window.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        execute_btn = ttk.Button(
            button_frame, 
            text="执行重命名", 
            command=lambda: [self.execute_rename_with_data(original_names, new_names), preview_window.destroy()]
        )
        execute_btn.pack(side=tk.RIGHT, padx=5)
    
    def execute_rename(self):
        """执行重命名"""
        if not self.selected_files:
            messagebox.showwarning("警告", "请先选择要重命名的文件!")
            return
            
        # 询问确认
        if not messagebox.askyesno("确认", "确定要执行重命名操作吗？此操作不可撤销！"):
            return
            
        start_idx = self.start_index.get()
        mode = self.prefix_mode.get()
        
        # 生成重命名数据
        original_names = []
        new_names = []
        
        for i, file_info in enumerate(self.selected_files):
            original_name = file_info["name"]
            original_names.append(original_name)
            
            # 提取前缀和后缀
            match = re.match(r'^(\d+)(.+?)(\d+)$', original_name)
            if match:
                prefix, main_part, suffix = match.groups()
                
                # 根据模式递增或递减前缀
                if mode == "increment":
                    new_prefix = str(min(99, start_idx + i)).zfill(len(prefix))
                else:  # decrement
                    new_prefix = str(max(1, start_idx - i)).zfill(len(prefix))
                
                new_name = f"{new_prefix}{main_part}{suffix}"
            else:
                # 如果不符合预期格式，则添加新前缀
                if mode == "increment":
                    new_prefix = str(min(99, start_idx + i)).zfill(2)
                else:  # decrement
                    new_prefix = str(max(1, start_idx - i)).zfill(2)
                
                new_name = f"{new_prefix}_{original_name}"
            
            new_names.append(new_name)
        
        # 执行重命名
        self.execute_rename_with_data(original_names, new_names)
    
    def execute_rename_with_data(self, original_names, new_names):
        """使用预生成的数据执行重命名"""
        if len(original_names) != len(new_names) or len(original_names) != len(self.selected_files):
            messagebox.showerror("错误", "重命名数据不匹配，操作取消。")
            return
        
        # 创建进度条
        progress_window = tk.Toplevel(self.root)
        progress_window.title("重命名进行中")
        progress_window.geometry("400x100")
        progress_window.resizable(False, False)
        progress_window.transient(self.root)
        
        progress_frame = ttk.Frame(progress_window, padding="20")
        progress_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(progress_frame, text="正在重命名文件，请稍候...").pack()
        
        progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=350, mode="determinate")
        progress_bar.pack(pady=10)
        
        # 在单独的线程中执行重命名
        def rename_thread():
            success_count = 0
            error_count = 0
            
            try:
                total = len(self.selected_files)
                
                for i, (file_info, new_name) in enumerate(zip(self.selected_files, new_names)):
                    try:
                        # 更新进度条
                        progress = int((i / total) * 100)
                        progress_bar["value"] = progress
                        progress_window.update()
                        
                        # 获取文件信息
                        folder_path = file_info["folder"]
                        metadata_file = file_info["metadata_file"]
                        actual_file = file_info["actual_file"]
                        old_name = file_info["name"]
                        metadata = file_info["metadata"]
                        
                        # 1. 修改metadata.json中的name字段
                        if os.path.exists(metadata_file):
                            metadata["name"] = new_name
                            
                            # 备份原文件
                            backup_file = f"{metadata_file}.bak"
                            if os.path.exists(backup_file):
                                os.remove(backup_file)
                            shutil.copy2(metadata_file, backup_file)
                            
                            # 写入新内容
                            with open(metadata_file, 'w', encoding='utf-8') as f:
                                json.dump(metadata, f)
                        
                        # 2. 如果有实际文件，重命名实际文件
                        if actual_file and os.path.exists(os.path.join(folder_path, actual_file)):
                            # 获取文件扩展名
                            _, ext = os.path.splitext(actual_file)
                            
                            # 创建新文件名
                            new_actual_file = f"{new_name}{ext}"
                            
                            # 重命名文件
                            os.rename(
                                os.path.join(folder_path, actual_file),
                                os.path.join(folder_path, new_actual_file)
                            )
                            
                            # 更新文件信息
                            file_info["actual_file"] = new_actual_file
                        
                        # 更新文件信息
                        file_info["name"] = new_name
                        
                        print(f"重命名成功: {old_name} -> {new_name}")
                        success_count += 1
                        
                    except Exception as e:
                        print(f"重命名失败: {file_info['name']} -> {new_name}")
                        print(f"错误: {str(e)}")
                        error_count += 1
                
                # 更新UI
                progress_bar["value"] = 100
                progress_window.update()
                
                # 重新加载文件列表
                self.root.after(500, self.refresh_file_list)
                
                # 显示完成消息
                messagebox.showinfo(
                    "完成", 
                    f"重命名操作完成\n成功: {success_count} 个文件\n失败: {error_count} 个文件"
                )
                
                # 关闭进度窗口
                progress_window.destroy()
                
            except Exception as e:
                messagebox.showerror("错误", f"重命名过程中发生错误: {str(e)}")
                progress_window.destroy()
        
        # 启动线程
        threading.Thread(target=rename_thread).start()
    
    def refresh_file_list(self):
        """刷新文件列表"""
        if self.eagle_folder:
            # 保存当前选择
            selected_ids = [file_info["id"] for file_info in self.selected_files]
            
            # 重新加载文件
            self.load_eagle_files()
            
            # 恢复选择
            children = self.file_tree.get_children()
            for i, item_id in enumerate(children):
                if i < len(self.eagle_files) and self.eagle_files[i]["id"] in selected_ids:
                    self.file_tree.selection_add(item_id)
            
            # 更新选择状态
            self.on_file_select(None)

def main():
    root = tk.Tk()
    app = EagleRenamerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 