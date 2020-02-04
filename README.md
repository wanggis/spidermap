# spidermap
This is a spider about online map based on python and C#  <br>
  只需要输入爬取的地图商，爬取区域（经纬度，level），存储路径，程序就会自动爬取该区域的瓦片地图，存储至本地或者发送至服务器，同时支持将瓦片的元数据存储至数据库（postgresql）. <br> 
 目前支持的地图如下:
    1.osm : https://www.openstreetmap.org  <br>
    2.谷歌地图 ：https://ditu.google.cn  （目前暂时被ban了）  <br>
    3.百度地图(包括无标注纯底图，影像地图) ：https://map.baidu.com/  <br>
    4.高德地图 ：https://www.amap.com/  <br>
    5.arcgis online ：http://www.arcgisonline.cn/arcgis/home/webmap/viewer.html?useExisting=1  <br>
    6.天地图（包括标记地图，无标记底图，影像地图） ： https://map.tianditu.gov.cn/   <br>

## 程序结构
程序分为爬虫端（spider ）和 服务器端（sever）
### 爬虫端
本部分程序由python完成，采用了多线程+协程的方法来进行爬取。
### 服务端
服务端一共有两个版本：C#版本和python版本 <br>
C#版本将http服务编写为windows服务进程，后台运行。<br>
python版本暂时还未解决后台运行的问题。
