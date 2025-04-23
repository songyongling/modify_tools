import os
import shutil
import sys

def copy_file(src, dst):
    """复制文件，并创建目标目录（如果不存在）"""
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print(f"复制: {src} -> {dst}")

def main():
    # 设置路径
    dist_dir = "dist"
    release_dir = os.path.join(dist_dir, "文件重命名工具集")
    
    # 确保发布目录存在
    os.makedirs(release_dir, exist_ok=True)
    
    # 复制主程序
    launcher_exe = os.path.join(dist_dir, "文件重命名工具_v2", "文件重命名工具_v2.exe")
    if os.path.exists(launcher_exe):
        copy_file(launcher_exe, os.path.join(release_dir, "文件重命名工具.exe"))
    else:
        print(f"错误: 找不到主程序 '{launcher_exe}'")
        return
    
    # 复制内部模块文件夹
    internal_dir = os.path.join(dist_dir, "文件重命名工具_v2", "_internal")
    if os.path.exists(internal_dir):
        for item in os.listdir(internal_dir):
            src = os.path.join(internal_dir, item)
            dst = os.path.join(release_dir, "_internal", item)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
                print(f"复制目录: {src} -> {dst}")
            else:
                copy_file(src, dst)
    else:
        print(f"错误: 找不到内部模块文件夹 '{internal_dir}'")
        return
    
    # 复制子模块可执行文件
    folder_rename_exe = os.path.join(dist_dir, "folder_rename_gui_app.exe")
    eagle_rename_exe = os.path.join(dist_dir, "eagle_rename_gui_app.exe")
    
    if os.path.exists(folder_rename_exe):
        copy_file(folder_rename_exe, os.path.join(release_dir, "folder_rename_gui_app.exe"))
    else:
        print(f"警告: 找不到文件夹重命名工具 '{folder_rename_exe}'")
    
    if os.path.exists(eagle_rename_exe):
        copy_file(eagle_rename_exe, os.path.join(release_dir, "eagle_rename_gui_app.exe"))
    else:
        print(f"警告: 找不到Eagle重命名工具 '{eagle_rename_exe}'")
    
    # 复制图标文件
    icon_file = "icon.ico"
    if os.path.exists(icon_file):
        copy_file(icon_file, os.path.join(release_dir, "icon.ico"))
    else:
        print(f"警告: 找不到图标文件 '{icon_file}'")
    
    print(f"\n发布包已准备完成，位于: {release_dir}")
    print("请将此文件夹压缩后分发给用户。")

if __name__ == "__main__":
    main() 