import gevent
from gevent import monkey
monkey.patch_all()
from gevent.pool import Pool
import time
import os
import urllib3
import math
import psycopg2 as ps2
import random
import requests
import threading

from config import *





def save_to_psql(choice, name,level, num, path):
    """
    将瓦片的相关元数据存储到数据库中
    :param choice:地图商以及相应的服务
    :param name:瓦片的名称：由生成时间，瓦片xy坐标三个信息构成
    :param level:瓦片隶属等级
    :param num:该瓦片是第几张存入的
    :param path:瓦片在nas上的存储路径
    :return:None
    """
    conn = ps2.connect(dbname='map_MD', user='postgres', password='您的密码', host="127.0.0.1", port="5432")
    cur = conn.cursor()
    cur.execute(
        """insert into {}(name,level,create_time,id,path)values('{}',{},'{}',{},'{}')""".format(map_name[choice], name, level, time.strftime('%Y-%m-%d', time.localtime()) , num, path)
    )
    conn.commit()
    conn.close()

def mkdir_for_map(path, name):
    """
    创建以标题命令的目录
    :param name: 目录名称
    :return: 返回创建的目录路径
    """
    path = os.path.join(path, name)
    if not os.path.exists(path):
        os.mkdir(path)
    return path

def save_map(path, title_x, title_y, content,choice,level):
    """
        保存图片到本地指定文件夹
        :param path: 保存图片的文件夹，由mkdir_for_map返回
        :param title_x: 获得瓦片地图的横坐标
        :param title_y: 获得瓦片地图的纵坐标
        :param pic_url: 获得瓦片地图的链接
        :return: 如果已经存在该照片，返回0
    """
    try:
        global nums
        pic_name = str(title_y) + '_' + str(title_x) + '.png'
        file_name = os.path.join(path, pic_name)
        # 如果存在该图片则不保存
        if os.path.exists(file_name):
            with open(file_name, 'rb') as pic:
                details = pic.read()
                if details != content:
                    path_new = mkdir_for_map(path, time.strftime('%Y-%m-%d', time.localtime()))
                    save_map(path_new, title_x, title_y, content, choice, level)

                else:
                    nums += 1
                    print('该照片已存在', pic_name)
            return 0
        with open(file_name, 'wb+') as file:
            file.write(content)
        print('save the map successfully', pic_name)
        # 将瓦片的元数据存储到本地的数据库
        # save_to_psql(choice=choice,
        #          name=time.strftime('%Y-%m-%d', time.localtime()) + '_' + str(title_x) + '_' + str(title_y),
        #          level=str(level), num=str(nums), path=file_name)
        nums += 1
    except Exception as e:
        save_map(path, title_x, title_y, content, choice, level)



def cal(choice,first, second, level):
    """
    通过输入经纬度范围，返回osm、gmap和amap的范围
    :param first: 左上角的经纬度
    :param second: 左下角的经纬度
    :param level: 爬取的等级
    :return: 返回爬取的瓦片坐标范围
    """
    first_lon = float(first.split(',')[0])
    first_lat = float(first.split(',')[1])
    second_lon = float(second.split(',')[0])
    second_lat = float(second.split(',')[1])
    if choice =='1' or choice =='2' or choice=='3' or choice =='6' or choice =='7' or choice == '8'or choice == '10':
        title1_x = int(math.pow(2, level - 1) * ((first_lon / 180) + 1))
        title1_y = int(math.pow(2, level - 1) * (
            1 - (math.log((math.tan(math.pi * first_lat / 180) + 1 / math.cos(math.pi * first_lat / 180)),
                          math.e)) / math.pi))
        title2_x = int(math.pow(2, level - 1) * ((second_lon / 180) + 1))
        title2_y = int(math.pow(2, level - 1) * (1 - (
            math.log((math.tan(math.pi * second_lat / 180) + 1 / math.cos(math.pi * second_lat / 180)),
                     math.e)) / math.pi))
        return [title1_x, title1_y, title2_x, title2_y]
    elif choice =='4'or choice =='9'or choice =='11':
        # print(1123456)
        R = 6378137
        title1_x = int(math.pow(2, level - 26) * (math.pi * first_lon * R / 180))
        title1_y = int(math.pow(2, level - 26) * R * (
            math.log((math.tan(math.pi * first_lat / 180) + 1 / math.cos(math.pi * first_lat / 180)), math.e)))
        title2_x = int(math.pow(2, level - 26) * (math.pi * second_lon * R / 180))
        title2_y = int(math.pow(2, level - 26) * R * (
            math.log((math.tan(math.pi * second_lat / 180) + 1 / math.cos(math.pi * second_lat / 180)), math.e)))
        return [title1_x, title1_y, title2_x, title2_y]
        # 在对极小范围的区域进行爬取时，会发现百度地图的结算公式不是很准确，会出现一定量的偏移，但是具体的偏移量尚不清楚，只能做大概的估计
        # bmap 19级
        # return [title1_x+10, title2_y-173, title2_x+14, title1_y-173]
        # bmap 17级
        #return [title1_x, title2_y-42, title2_x+4, title1_y-42]
        # bmap 15级
       # return [title1_x, title2_y-11, title2_x+1, title1_y-11]
    elif choice =='5':
        title1_x = int(math.pow(2, level - 1) * ((first_lon / 180) + 1))
        title1_y = int((math.pow(2, level) - 1) - math.pow(2, level - 1) * (
            1 - (
                math.log((math.tan(math.pi * first_lat / 180) + 1 / math.cos(math.pi * first_lat / 180)),
                         math.e)) / math.pi))
        title2_x = int(math.pow(2, level - 1) * ((second_lon / 180) + 1))
        title2_y = int((math.pow(2, level) - 1) - math.pow(2, level - 1) * (
            1 - (
                math.log((math.tan(math.pi * second_lat / 180) + 1 / math.cos(math.pi * second_lat / 180)),
                         math.e)) / math.pi))
        return [title1_x, title2_y, title2_x, title1_y]



def arccal(path,title_x,title_y,level,choice ):
    # 1    2
    # 3    4
    """
        获得每一个瓦片的四个角的地理坐标（osm,gmap,amap),即进行反算坐标
        :param path: 保存坐标的文件夹，由mkdir_for_map返回
        :param title_x: 获得瓦片地图的横坐标
        :param title_y: 获得瓦片地图的纵坐标
        :param level: 获得瓦片地图的等级
        :return: 如果已经存在该文档，返回0
    """
    global left_lat,left_lon,right_lat,right_lon
    if choice == '1' or choice == '2' or choice == '3' or choice == '6' or choice == '7'or choice == '8'or choice == '10':
        left_lon = (math.pow(2,1-level)*(title_x+0/256)-1)*180
        left_lat = ((360*math.atan(math.pow(math.e,(1-math.pow(2,1-level)*(title_y+0/256))*math.pi)))/math.pi)-90
        right_lon = (math.pow(2,1-level)*(title_x+255/256)-1)*180
        right_lat = ((360*math.atan(math.pow(math.e,(1-math.pow(2,1-level)*(title_y+255/256))*math.pi)))/math.pi)-90
    elif choice == '4':
        R = 6378137
        left_lon = (math.pow(2, 1 - level) * (title_x + 0 / 256) - 1) * 180
        left_lat = ((360 * math.atan(
            math.pow(math.e, (1 - math.pow(2, 1 - level) * (title_y + 0 / 256)) * math.pi))) / math.pi) - 90
        right_lon = (math.pow(2, 1 - level) * (title_x + 255 / 256) - 1) * 180
        right_lat = ((360 * math.atan(
            math.pow(math.e, (1 - math.pow(2, 1 - level) * (title_y + 255 / 256)) * math.pi))) / math.pi) - 90
    elif choice=='5':
        title_y = (math.pow(2, level) - 1) - title_y
        left_lon = (math.pow(2, 1 - level) * (title_x + 0 / 256) - 1) * 180
        left_lat = ((360 * math.atan(
            math.pow(math.e, (1 - math.pow(2, 1 - level) * (title_y + 0 / 256)) * math.pi))) / math.pi) - 90
        right_lon = (math.pow(2, 1 - level) * (title_x + 255 / 256) - 1) * 180
        right_lat = ((360 * math.atan(
            math.pow(math.e, (1 - math.pow(2, 1 - level) * (title_y + 255 / 256)) * math.pi))) / math.pi) - 90
    first_lon = left_lon ;first_lat = left_lat
    first_info = '左上角：'+str(first_lon)+','+str(first_lat)+'\n'
    second_lon = right_lon ; second_lat = left_lat
    second_info = '右上角：' + str(second_lon) + ',' + str(second_lat) + '\n'
    level_lon = left_lon ; level_lat = right_lat
    level_info = '左下角：' + str(level_lon) + ',' + str(level_lat) + '\n'
    fourth_lon = right_lon ;fourth_lat =right_lat
    fourth_info = '右下角：' + str(fourth_lon) + ',' + str(fourth_lat) + '\n'
    txt_name = str(title_x) + '_' + str(title_y) + '.txt'
    file_name = os.path.join(path, txt_name)
    # 如果存在该图片则不保存
    if os.path.exists(file_name):
        print('该文档已存在')
        return 0
    with open(file_name, 'w+') as file:
        file.writelines([first_info,second_info,level_info,fourth_info])
    print('save the text successfully')



def get_link( choice, title_x, title_y, level):
    """
    获取每一个瓦片的url链接
    :param link: 最基础的url链接
    :param title_x: 瓦片坐标x
    :param title_y: 瓦片坐标y
    :param level: 瓦片坐标等级
    :return: 返回瓦片的url
    """
    link = map_dict[choice]
    if choice == '1':
        url = link + '//{}//{}//{}.png'.format(str(level), str(title_x), str(title_y))
        return url
    elif choice == '2' or choice == '3' or choice == '4'or choice == '9':
        url = link + '&x={}&y={}&z={}'.format(str(title_x), str(title_y), str(level))
        return url
    elif choice == '5':
        url = link + '{}//{}//{}//{}_{}.png?'.format(str(level), str(int(title_x / 16)),
                                                      str(int(title_y / 16)), str(title_x), str(title_y))
        return url
    elif choice == '6':
        url = link + '//{}//{}//{}.png'.format(str(level), str(title_y), str(title_x))
        return url
    elif choice == '7' or choice == '8'or choice == '10':
        url = link + '&x={}&y={}&l={}'.format(str(title_x), str(title_y), str(level))
        return url
    elif choice == '11':
        url = link + '&u=x={};y={};z={};v=009;type=sate'.format(str(title_x), str(title_y), str(level))
        print(url)
        return url




def getThesis(path,choice,title_x,title_y,level,length):
    headers = {
        "User_Agent":random.choice(MY_USER_AGENT),
        'Connection': 'close'
    }
    # proxy = {"http" : 'http://'+random.choice(ip_pool)}
    url=get_link(choice,title_x,title_y,level)
    path1=mkdir_for_map(path, map_name[choice])
    path2 = mkdir_for_map(path1, str(level))  # 创建一个关于等级的文件夹
    # path3 = mkdir_for_map(path2, 'pic')  # 创建一个存储图片的文件夹
    # path4 = mkdir_for_map(path2, 'txt')  # 创建一个存储坐标的文件夹
    try:
        response = requests.get(url, headers=headers, timeout=5)
        # 将瓦片存储到本机
        save_map(path2, title_x, title_y, content=response.content, choice=choice, level=level)
        response.keep_alive = False

        # arccal(path4,title_x,title_y,level,choice)
        # 构建post_url，向服务器发送图片
        url_post = "http://*.*.*.*:9001/" + map_name[choice] + "/" + str(level) + "/" + str(title_x) + "_" + str(
            title_y)
        # print('已经完成%f' % ((nums / length) * 100))

        requests.adapters.DEFAULT_RETRIES = 5
        print(time.time(), url_post)
        r = requests.post(url_post, data=response.content, timeout=20, headers=headers)
        print(time.time(), url_post)
        r.keep_alive = False
        print('已经完成%f' % ((nums / length) * 100))

    except:
        getThesis(path,choice,title_x,title_y,level,length)

class threasDownload(threading.Thread):
    """
    使用threading.Thread初始化自定义类
    """
    def __init__(self, que, length1):
        threading.Thread.__init__(self)
        self.que = que
        self.len = length1


    def run(self):
        length = len(self.que)
        coroutineNum = 1000         # 协程数量
        for i in range(coroutineNum):
            jobs = []
            left = i *(length//coroutineNum)
            if (i+1)*(length//coroutineNum)<length:
                right = (i+1) *(length//coroutineNum)
            else:
                right=length
            for j in self.que[left:right]:
                jobs.append(gevent.spawn(getThesis, path=j[0], choice=j[1], title_x=j[2], title_y=j[3], level=j[4], length=self.len))
            if i == (coroutineNum-1):
                for j in self.que[(i+1) * (length // coroutineNum):]:
                    jobs.append(gevent.spawn(getThesis, path=j[0], choice=j[1], title_x=j[2], title_y=j[3], level=j[4], length=self.len))
            gevent.joinall(jobs)


def main(first1, second1, i, path1, choice1):
    """
    将任务进行切割，开启多线程。
    """



    first = first1
    second = second1
    level = i
    path = path1
    print(map_name)
    choice = choice1
    start = time.time()
    date = time.strftime('%Y-%m-%d', time.localtime())   #计数器
    threadNum = 5  #线程的数量


    quelist=[]
    urllist=[]
    path1=mkdir_for_map(path, map_name[choice])
    path2 = mkdir_for_map(path1, str(level))  # 创建一个关于等级的文件夹
    for title_x in range(cal(choice, first, second, level)[0], cal(choice,first, second, level)[2] + 1):
        for title_y in range(cal(choice,first, second, level)[1], cal(choice,first, second, level)[3] + 1):
            pic_name = str(title_x) + '_' + str(title_y) + '.png'
            file_name = os.path.join(path2, pic_name)
            if os.path.exists(file_name):
               print("This pic has existed")
            else:
                urllist.append([path,choice,title_x,title_y,level])
    # 将urllist按照线程数目进行分割
    length1 = len(urllist)
    print(length1)

    pathhhh="E:\\map\\"+map_name[choice]+"\\瓦片数量.txt"
    if os.path.exists(pathhhh):
        with open(pathhhh, "a") as file:
            file.writelines("第"+str(level)+"级别的数量是"+str(length1)+"/n")
    else:
        with open(pathhhh, 'w') as file:
            file.writelines("第"+str(level)+"级别的数量是"+str(length1)+"/n")
    for i in range(threadNum):
        que = []
        left = i * (length1//threadNum)
        if (i+1)*(length1//threadNum)<length1:
            right = (i+1) * (length1//threadNum)
        else:
            right = length1
        for url in urllist[left:right]:
            que.append(url)
        if i== (threadNum-1):
            for j in urllist[(i+1)*(length1//threadNum):]:
                que.append(j)
        print(len(que))
        quelist.append(que)
    threadlist = []
    for i in range(threadNum):
        threadlist.append(threasDownload(que=quelist[i], length1=length1))
    for thread in threadlist:
        thread.start()  #启动线程

    for thread in threadlist:
        thread.join()    #这句是必须写的，否则线程还没运行就结束了


    print(time.time()-start)

if __name__ == '__main__':
    first = input('请输入经纬度范围（左上角，请用半角逗号将经纬度隔开）：')
    second = input('请输入经纬度范围（右下角，请用半角逗号将经纬度隔开）：')
    path = input('请输入存储的文件夹路径：')
    print(map_name)
    choice = input('请选择你要获取的地图：')
    paaa=mkdir_for_map(path, map_name[choice])

    for i in range(19, 20):
        nums=1
        main(first, second, i, path, choice)
        with open(paaa+"爬虫情况.txt", 'a') as f:   # 建立相应的日志文件，记录爬取的瓦片级别。便于出现报错，闪退等问题时的追溯
            f.writelines("第"+str(i)+"级已经爬完")


