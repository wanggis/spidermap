from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
import time
import cgi
import sys
import psycopg2 as ps2



# 暂时还没有解决如何使得python文件以win服务的形式在后台运行，只能采取折中方式。将后缀名改为pyw后，python文件会自动在后台运行，而不会跳出cmd窗口
if sys.executable.endswith("pythonw.exe"):
  sys.stdout = open(os.devnull, "w")
  sys.stderr = open(os.path.join(os.getenv("TEMP"), "stderr-"+os.path.basename(sys.argv[0])), "w")



def save_to_psql(mapname, title_x, title_y, path,level):
    """
    将每一个瓦片地图的元数据存入到数据中
    :param mapname: 数据地图名称
    :param title_x: 瓦片x坐标
    :param title_y: 瓦片y坐标
    :param path:每一块瓦片的url连接
    :param level: 瓦片等级
    :return:None
    """
    conn = ps2.connect(dbname='map_MD', user='postgres', password='ws260819', host="127.0.0.1", port="5432")
    cur = conn.cursor()
    cur.execute(
        """insert into {}(title_x,title_y,create_time,rank,path)values('{}','{}',CURRENT_TIMESTAMP,{},'{}')""".format(mapname, str(title_x), str(title_y), level, path)
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

def save_map(mapname,path, title_x, title_y, content,level,url):
    """
        保存图片到本地指定文件夹
        :param path: 保存图片的文件夹，由mkdir_for_map返回
        :param title_x: 获得瓦片地图的横坐标
        :param title_y: 获得瓦片地图的纵坐标
        :param pic_url: 获得瓦片地图的链接
        :return: 如果已经存在该照片，返回0
    """
    try:
        pic_name = str(title_x) + '_' + str(title_y) + '.png'
        file_name = os.path.join(path, pic_name)
        # 如果存在该图片则不保存
        if os.path.exists(file_name):
            with open(file_name , 'rb') as pic:
                details = pic.read()
                if details != content:
                    path_new = mkdir_for_map(path, time.strftime('%Y-%m-%d', time.localtime()))
                    save_map(mapname, path_new, title_x, title_y, content, level,url)

                else:
                    return('该照片已存在', pic_name)
            return 0
        with open(file_name, 'wb+') as file:
            file.write(content)
        global nums
        save_to_psql(mapname=mapname,
                 title_x = title_x,
                 title_y=title_y,
                 level=level, path=url)
        nums+=1
        return ('save the map successfully',pic_name)
    except Exception as e:
        save_map(mapname,path, title_x, title_y, content,level,url)


class PostHandler(BaseHTTPRequestHandler):
    """
    处理get和post请求
    """
    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     }
        )
        self.send_response(200)
        self.end_headers()

        # self.wfile.write('Client: %sn ' % str(self.client_address) )
        # self.wfile.write('User-agent: %sn' % str(self.headers['user-agent']))
        # self.wfile.write('Path: %sn'%self.path)
        # self.wfile.write('Form data:n')
        for field in form.keys():
            field_item = form[field]
            filevalue = field_item.value
            # filesize = len(filevalue)#文件大小(字节)
            list_path = self.path.split("/")
            path1 = mkdir_for_map("E:\\map", list_path[1])   #创建存储文件夹的地址
            path2 = mkdir_for_map(path1, list_path[2])
            save_map(mapname=list_path[1], path=path2, title_x=list_path[3], title_y=list_path[4], content=filevalue, level=list_path[2],url=self.path)
        self.close_connection = True
        return


    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'image/png')
        self.end_headers()
        # Send the html message
        list_path = self.path.split("/")
        source_path = "E:\\map\\"+list_path[1]+"\\"+list_path[2]+"\\"+list_path[3]+'_'+list_path[4]+".png"
        try:
            with open(source_path, 'rb') as f:
                content = f.read()
            self.wfile.write(content)
        except FileNotFoundError  as e:
            self.send_error(404, "file is not exist", "参数超出了该等级的瓦片坐标范围")
        return



def StartServer():
    """
    return:启动服务器
    """
    sever = ThreadingHTTPServer(("", 9001), PostHandler)   #如果要改成局域网互传，只需要填入0.0.0.0
    print('Started httpserver on port ')
    sever.serve_forever()




if __name__=='__main__':
    nums = 0
    StartServer()
