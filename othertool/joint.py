
import os
import PIL.Image as Image


IMAGES_PATH = r"E:\map\14\\"  # 图片集地址

IMAGES_FORMAT = ['.png', '.PNG']  # 图片格式

IMAGE_SIZE = 256  # 每张小图片的大小

IMAGE_ROW = 87  # 图片间隔，也就是合并成一张图后，一共有几行

IMAGE_COLUMN = 54  # 图片间隔，也就是合并成一张图后，一共有几列

IMAGE_SAVE_PATH = r'E:\map\final.png'  # 图片转换后的地址

# 获取图片集地址下的所有图片名称

image_names = [name for name in os.listdir(IMAGES_PATH) for item in IMAGES_FORMAT if

               os.path.splitext(name)[1] == item]
print(image_names)
num =1
row_list = []
image_namess = []
for i in range(0, IMAGE_ROW*IMAGE_COLUMN):
    row_list.append(image_names[i])
    if num == IMAGE_COLUMN:
        print(row_list)
        print(len(row_list))
        image_namess=row_list+image_namess
        row_list=[]
        num=0
    num = num+1

# 简单的对于参数的设定和实际图片集的大小进行数量判断

if len(image_names) != IMAGE_ROW * IMAGE_COLUMN:
    raise ValueError("合成图片的参数和要求的数量不能匹配！")


# 定义图像拼接函数

def image_compose():

    to_image = Image.new('RGB', (IMAGE_COLUMN * IMAGE_SIZE, IMAGE_ROW * IMAGE_SIZE))  # 创建一个新图
    print("创建新图完毕")
    # 循环遍历，把每张图片按顺序粘贴到对应位置上
    print(image_namess)
    for y in range(1, IMAGE_ROW + 1):

        for x in range(1, IMAGE_COLUMN + 1):
            from_image = Image.open(IMAGES_PATH + image_namess[IMAGE_COLUMN * (y - 1) + x - 1]).resize(
                (IMAGE_SIZE, IMAGE_SIZE), Image.ANTIALIAS)

            to_image.paste(from_image, ((x - 1) * IMAGE_SIZE, (y - 1) * IMAGE_SIZE))
    print("创建完毕")

    return to_image.save(IMAGE_SAVE_PATH)  # 保存新图


image_compose()  # 调用函数
print("图片已生成")

# 左上角10722  5893

#右下角 10824  5795