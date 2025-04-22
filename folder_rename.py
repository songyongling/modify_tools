import os
import sys

def get_folder_path():
    """
    获取用户输入的文件夹路径并验证其有效性
    
    Returns:
        str: 有效的文件夹路径
    """
    while True:
        folder_path = input("请输入文件夹路径：")
        
        # 去除可能的引号（用户可能从文件资源管理器复制路径）
        folder_path = folder_path.strip('"\'')
        
        # 检查路径是否存在
        if os.path.exists(folder_path):
            # 检查是否是文件夹
            if os.path.isdir(folder_path):
                return folder_path
            else:
                print("错误：输入的路径不是文件夹！请重新输入。")
        else:
            print("错误：文件夹路径不存在！请重新输入。")

def main():
    """
    程序主入口函数
    """
    print("文件夹重命名工具已启动")
    
    # 获取用户输入的文件夹路径
    folder_path = get_folder_path()
    print(f"您选择的文件夹路径：{folder_path}")
    
    # 显示文件夹内容
    try:
        files = os.listdir(folder_path)
        print(f"\n文件夹内容（共{len(files)}项）：")
        for item in files:
            item_path = os.path.join(folder_path, item)
            item_type = "文件夹" if os.path.isdir(item_path) else "文件"
            print(f"  - {item} ({item_type})")
    except Exception as e:
        print(f"无法读取文件夹内容：{e}")
    
    print("\n等待添加重命名功能...")
    
    # 示例：打印当前工作目录
    current_dir = os.getcwd()
    print(f"当前工作目录: {current_dir}")

if __name__ == "__main__":
    main()