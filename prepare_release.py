"""
打包脚本 - 用于构建可执行文件
"""
import os
import sys
import shutil
import subprocess
import time

def clean_previous_build():
    """清理之前的构建文件"""
    print("正在清理之前的构建文件...")
    
    # 删除dist和build目录
    for directory in ["dist", "build", "__pycache__"]:
        if os.path.exists(directory):
            try:
                shutil.rmtree(directory)
                print(f"已删除 {directory} 目录")
            except PermissionError as e:
                print(f"警告: 无法完全删除 {directory} 目录")
                print(f"原因: {str(e)}")
                print("这可能是因为某些文件正在被使用。程序将继续执行，但可能会重用一些旧文件。")
    
    print("清理完成!")

def build_executable():
    """使用PyInstaller构建可执行文件"""
    print("正在构建可执行文件...")
    
    # 使用现有的spec文件构建
    result = subprocess.run(["pyinstaller", "文件重命名工具.spec"], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("构建失败!")
        print("错误信息:")
        print(result.stderr)
        return False
    
    print("构建成功!")
    return True

def create_release_zip():
    """创建发布的ZIP文件"""
    print("正在创建发布包...")
    
    # 创建release目录
    if not os.path.exists("release"):
        os.makedirs("release")
    
    # 准备发布的时间戳
    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
    
    # 创建ZIP文件
    zip_filename = f"release/文件重命名工具_v1.0_{timestamp}.zip"
    
    # 压缩dist目录中的文件
    dist_path = os.path.join("dist", "文件重命名工具")
    if os.path.exists(dist_path):
        shutil.make_archive(zip_filename[:-4], 'zip', "dist", "文件重命名工具")
        print(f"发布包已创建: {zip_filename}")
        return True
    else:
        print("错误: 找不到构建的可执行文件目录")
        return False

def main():
    """主入口函数"""
    print("===== 文件重命名工具打包脚本 =====")
    
    # 检查PyInstaller是否安装
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, capture_output=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("错误: 找不到PyInstaller。请先安装PyInstaller: pip install pyinstaller")
        return
    
    # 清理之前的构建
    clean_previous_build()
    
    # 构建可执行文件
    if build_executable():
        # 创建发布包
        create_release_zip()
    
    print("===== 打包流程完成 =====")

if __name__ == "__main__":
    main() 