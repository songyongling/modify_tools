import base64
from PIL import Image
import io

# 创建一个简单的图标
img = Image.new('RGB', (128, 128), color=(52, 152, 219))

# 保存为ICO文件
img.save("icon.ico", format="ICO")

print("图标文件已成功创建！") 