import os
import sys
import re

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

def extract_number_prefix(filename):
    """
    从文件名中提取前缀数字（两位数字格式）
    
    Args:
        filename: 文件名
        
    Returns:
        tuple: (前缀数字, 剩余部分) 如果没有前缀数字则返回 (None, 原文件名)
    """
    # 匹配文件名前面的两位数字
    match = re.match(r'^(\d{2})(.*)$', filename)
    if match:
        number = int(match.group(1))
        rest = match.group(2)
        return number, rest
    return None, filename

def get_file_group(filename):
    """
    从文件名中提取文件组信息
    
    Args:
        filename: 文件名
    
    Returns:
        str: 文件组名称，如果无法提取则返回None
    """
    # 先提取前缀数字后的部分
    prefix, rest = extract_number_prefix(filename)
    
    # 如果没有数字前缀或提取失败，返回None
    if rest == filename:
        return None
    
    # 尝试从剩余部分提取主要部分（在第一个数字之前的非数字字符）
    # 例如从"薛芳菲沈玉容旧家00.mp4"提取"薛芳菲沈玉容旧家"
    group_match = re.match(r'^([^0-9]+)', rest)
    if group_match:
        # 去除前后空格
        group_name = group_match.group(1).strip()
        if group_name:
            return group_name
    
    return None

def rename_files_with_new_prefix(folder_path, files, start_index, mode="increment"):
    """
    从指定索引开始重命名文件，修改前缀数字
    
    Args:
        folder_path: 文件夹路径
        files: 文件列表
        start_index: 从哪个文件开始修改
        mode: 前缀变化模式，"increment"为递增，"decrement"为递减
    """
    # 筛选出从开始索引到最后的文件
    files_to_rename = files[start_index:]
    
    if not files_to_rename:
        print("没有找到需要重命名的文件。")
        return
    
    # 获取起始文件的组名和前缀
    start_file = files_to_rename[0]
    start_prefix, _ = extract_number_prefix(start_file)
    current_group = get_file_group(start_file)
    
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
        file_group = get_file_group(filename)
        
        # 如果无法识别文件组，跳过此文件
        if file_group is None:
            print(f"跳过 {filename}（无法识别文件组）")
            continue
        
        # 提取当前文件名的数字前缀和剩余部分
        _, rest = extract_number_prefix(filename)
        
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
        
        # 执行重命名
        try:
            os.rename(file_path, new_file_path)
            print(f"已重命名: {filename} -> {new_filename}")
            renamed_count += 1
        except Exception as e:
            print(f"重命名 {filename} 失败: {e}")
    
    print(f"\n重命名完成！共重命名 {renamed_count} 个文件。")

def main():
    """
    程序主入口函数
    """
    print("文件夹重命名工具已启动")
    
    # 获取用户输入的文件夹路径
    folder_path = get_folder_path()
    print(f"您选择的文件夹路径：{folder_path}")
    
    # 获取并显示文件夹内容
    try:
        # 先获取原始文件列表
        files = os.listdir(folder_path)
        
        # 根据文件名排序（确保数字顺序正确）
        files = sorted(files)
        
        print(f"\n文件夹内容（共{len(files)}项）：")
        for i, item in enumerate(files):
            item_path = os.path.join(folder_path, item)
            item_type = "文件夹" if os.path.isdir(item_path) else "文件"
            print(f"  {i+1}. {item} ({item_type})")
    except Exception as e:
        print(f"无法读取文件夹内容：{e}")
        return

    # 如果文件夹为空，提示并退出
    if not files:
        print("文件夹为空，没有文件可以重命名。")
        return
    
    # 获取用户输入：从哪个文件开始修改
    start_file_index = None
    while start_file_index is None:
        start_input = input("\n请输入从哪个文件开始修改(输入对应的序号或文件前缀，如'7'或'01'): ")
        
        # 尝试按序号查找
        if start_input.isdigit() and not start_input.startswith('0'):
            index = int(start_input) - 1
            if 0 <= index < len(files):
                start_file_index = index
                print(f"选择了第 {start_input} 个文件: {files[index]}")
            else:
                print(f"错误：序号必须在 1 到 {len(files)} 之间。")
        # 尝试按前缀查找
        elif re.match(r'^\d{2}$', start_input):
            target_prefix = start_input
            found = False
            
            print(f"正在查找前缀为 '{target_prefix}' 的文件...")
            
            # 存储所有匹配的文件
            matching_files = []
            for i, filename in enumerate(files):
                if filename.startswith(target_prefix):
                    matching_files.append((i, filename))
            
            # 如果找到匹配的文件
            if matching_files:
                # 使用第一个匹配的文件
                start_file_index = matching_files[0][0]
                found_file = matching_files[0][1]
                print(f"找到 {len(matching_files)} 个匹配的文件，选择第一个: {found_file}")
                found = True
            
            if not found:
                print(f"错误：找不到前缀为 '{target_prefix}' 的文件。")
        else:
            print("错误：无法识别输入。请输入有效的序号或两位数字前缀。")
    
    # 确认选择的文件
    selected_file = files[start_file_index]
    selected_prefix, _ = extract_number_prefix(selected_file)
    selected_group = get_file_group(selected_file)
    
    print(f"\n您选择从文件 \"{selected_file}\" 开始修改。")
    if selected_prefix is not None:
        print(f"文件前缀: {selected_prefix:02d}")
    if selected_group:
        print(f"文件组: {selected_group}")
    
    # 获取用户选择：递增还是递减
    while True:
        mode_choice = input("\n请选择前缀数字变化方式 (1: 递增, 2: 递减): ")
        if mode_choice in ['1', '2']:
            mode = "increment" if mode_choice == '1' else "decrement"
            break
        else:
            print("错误：请输入 1 (递增) 或 2 (递减)")
    
    # 计算新的起始前缀
    if mode == "increment":
        new_start_prefix = min(99, selected_prefix + 1)
    else:
        # 递减模式下，前缀减1，最小为00
        new_start_prefix = max(0, selected_prefix - 1)
    
    # 显示操作信息，然后直接执行（不需要确认）
    if mode == "increment":
        print(f"\n将从文件 \"{selected_file}\" 开始，将前缀 {selected_prefix:02d} 递增为 {new_start_prefix:02d}，且在不同组之间递增前缀。")
    else:
        print(f"\n将从文件 \"{selected_file}\" 开始，将前缀递减为 {new_start_prefix:02d}，且在不同组之间递增前缀（{new_start_prefix:02d}→{min(99, new_start_prefix+1):02d}→{min(99, new_start_prefix+2):02d}→...）。")
    
    # 直接执行重命名操作
    rename_files_with_new_prefix(folder_path, files, start_file_index, mode)

if __name__ == "__main__":
    main()