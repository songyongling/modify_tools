from PIL import Image, ImageDraw

# 创建一个300x300的图像，设置为透明背景
img = Image.new('RGBA', (300, 300), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# 设置颜色
body_color = (169, 103, 78)  # 棕色
ear_color = (130, 70, 60)    # 深棕色
face_color = (225, 175, 145) # 浅棕色
eye_color = (50, 50, 50)     # 黑色

# 绘制身体（圆形）
draw.ellipse((50, 50, 250, 250), fill=body_color)

# 绘制左耳
draw.ellipse((40, 30, 120, 110), fill=ear_color)

# 绘制右耳
draw.ellipse((180, 30, 260, 110), fill=ear_color)

# 绘制面部（圆形）
draw.ellipse((75, 75, 225, 225), fill=face_color)

# 绘制左眼
draw.ellipse((105, 125, 135, 155), fill=eye_color)

# 绘制右眼
draw.ellipse((165, 125, 195, 155), fill=eye_color)

# 绘制鼻子
draw.ellipse((140, 160, 160, 180), fill=(80, 50, 50))

# 绘制嘴巴
draw.arc((120, 160, 180, 200), 0, 180, fill=(80, 50, 50), width=3)

# 保存为ICO格式
img.save("icon.ico", format="ICO")

print("小熊图标已成功创建！") 