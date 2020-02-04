using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Linq;
using System.ServiceProcess;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.Net;
using Npgsql;

namespace server
{
    public partial class Service1 : ServiceBase
    {
        static HttpListener httpobj;
        public Service1()
        {
            InitializeComponent();
        }

        string filePath = @":\map\MyServiceLog.txt";  //创建一个日志记录每次服务的启动与关闭
        protected override void OnStart(string[] args)
        {
            using (FileStream stream = new FileStream(filePath, FileMode.Append))
            using (StreamWriter writer = new StreamWriter(stream))
            {
                writer.WriteLine($"{DateTime.Now},服务启动！");
            }
            //提供一个简单的的HTTP协议侦听器。此类不能被继承。
            httpobj = new HttpListener();
            //定义简单的url，ip地址和端口号。
            httpobj.Prefixes.Add("http://+:9001/");
            //启动监听
            httpobj.Start();
            //异步监听客户端的请求，当客户端的网络请求到来时会自动执行result委托
            httpobj.BeginGetContext(Result, null);
            Console.WriteLine("服务端初始化完毕，正在等待客户端请求,时间为：");
            Console.Read();
        }
        private static void Result(IAsyncResult ar) 
        {
            //当接受到请求之后，程序流会运行到这里

            //继续异步监听
            httpobj.BeginGetContext(Result, null);
            var guid = Guid.NewGuid().ToString();
            Console.ForegroundColor = ConsoleColor.White;
            Console.WriteLine("接到新的请求");
            //获得context对象
            var context = httpobj.EndGetContext(ar);
            var request = context.Request;
            var response = context.Response;
            context.Response.ContentType = "image/png";//告诉客户端返回的ContentType类型为纯文本格式，编码为UTF-8
            context.Response.AddHeader("Content-type", "image/png");//添加响应头信息
            //context.Response.ContentEncoding = Encoding.UTF8;
            string returnObj = null;//定义返回客户端的信息
            byte[] returnByteArr;
            try
            {
                //Console.WriteLine("sdasd");
                if (request.HttpMethod == "POST" && request.InputStream != null)
                {
                    //处理客户端发送的请求并返回处理信息
                    HandleRequest(request, response);
                    returnObj = "不是post/get请求或者传过来的数据为空";
                    returnByteArr = Encoding.UTF8.GetBytes(returnObj);
                    using (var stream = response.OutputStream)
                    {
                        //把处理信息返回到客户端
                        stream.Write(returnByteArr, 0, returnByteArr.Length);
                    }
                }
                else
                {
                    returnByteArr = Handleget(request, response);
                    if (returnByteArr == null)
                    {
                        returnObj = "不存在该数据，url输入有误";
                        response.StatusDescription = "404";
                        response.StatusCode = 404;
                        returnByteArr = Encoding.UTF8.GetBytes(returnObj);
                        using (var stream = response.OutputStream)
                        {
                            //把处理信息返回到客户端
                            stream.Write(returnByteArr, 0, returnByteArr.Length);
                        }
                    }
                    else
                    {
                        using (var stream = response.OutputStream)
                        {
                            //把处理信息返回到客户端
                            stream.Write(returnByteArr, 0, returnByteArr.Length);
                        }
                    }
                }

            }
            catch (Exception ex)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine("网络崩了了：{0}", ex.ToString());
            }
            Console.ForegroundColor = ConsoleColor.Yellow;
            Console.WriteLine("请求处理完成：{1},时间：{0}\r\n", DateTime.Now.ToString(), guid);

        }

        private static void HandleRequest(HttpListenerRequest request, HttpListenerResponse response)
        {
            //获取完整的url
            string url = request.Url.AbsolutePath;
            Console.WriteLine(url);
            string base_Path = @"Z:\map\";// + @url.Replace(@"/", @"\") + @".png";
            string[] lists = url.Split(new char[1] { '/' });
            //string data = null;
            try
            {
                var byteList = new List<byte>();
                var byteArr = new byte[2048];
                int readLen = 0;
                int len = 0;
                //接收客户端传过来的数据并转成字符串类型
                do
                {
                    readLen = request.InputStream.Read(byteArr, 0, byteArr.Length);
                    len += readLen;
                    byteList.AddRange(byteArr);
                } while (readLen != 0);
                string path1 = Make_dic(base_Path, lists[1]);
                string path2 = Make_dic(path1, lists[2]);
                string[] listss = url.Split(new char[2] { '/', '_' });
                Exists(path2 + @"\" + lists[3] + @".png", path2, lists[3], listss, byteList.ToArray());

            }
            catch (Exception ex)
            {
                response.StatusDescription = "404";
                response.StatusCode = 404;
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine("在接收数据时发生错误:{0}", ex.ToString());
                //return $"在接收数据时发生错误:{ex.ToString()}";//把服务端错误信息直接返回可能会导致信息不安全，此处仅供参考
            }
            response.StatusDescription = "200";//获取或设置返回给客户端的 HTTP 状态代码的文本说明。
            response.StatusCode = 200;// 获取或设置返回给客户端的 HTTP 状态代码。
            Console.ForegroundColor = ConsoleColor.Green;
            Console.WriteLine("接收数据完成:{data.Trim()},时间：{DateTime.Now.ToString()}");
            //return @"接收数据完成";

        }



        private static string Make_dic(string path, string canshu)
        {
            if (false == Directory.Exists(path + @"\" + canshu))
            {
                Directory.CreateDirectory(path + @"\" + canshu);
                return path + @"\" + canshu;
            }
            else
            {
                Console.WriteLine("已经存在该文件夹");
                return path + @"\" + canshu;
            }
        }



        //<summary>

        // 将byte[]输出为图片

        // </summary>

        // <param name="path">输出图片的路径及名称</param>

        // <param name="picByte">byte[]数组存放的图片数据</param>

        private static void Writeimg(string path, byte[] picByte)
        {

            FileStream fs = new FileStream(path, FileMode.Create);

            BinaryWriter bw = new BinaryWriter(fs);

            //开始写入

            bw.Write(picByte, 0, picByte.Length);

            //关闭流

            bw.Close();

            fs.Close();

        }


        private static void Exists(string path1, string path2, string name, string[] listss, byte[] picByte)
        {
            if (File.Exists(@path1))
            {
                string new_path = select_to_pg(listss);//查找出来目前存储的该瓦片的最新的数据
                FileStream files = new FileStream(@new_path, FileMode.Open);
                byte[] imgByte = new byte[files.Length];
                files.Read(imgByte, 0, imgByte.Length);
                files.Close();
                if (imgByte == picByte) //对比刚刚获取的瓦片与存储的最新瓦片的区别
                {
                    Console.WriteLine("存在该照片");
                }
                else
                {
                    //如果照片不同的话，创建新的文件夹；
                    //string[] liss = path1.Split('\\');
                    string[] date = DateTime.Now.Date.ToString().Replace(@"/", @"-").Split(' ');
                    string path_new = path2 + @"\" + date[0];
                    if (false == Directory.Exists(path_new))
                    {
                        Console.WriteLine(path_new);
                        Directory.CreateDirectory(path_new);
                        path1 = path_new + @"\" + name + @".png";
                        Writeimg(path1, picByte);
                        //liss = path.Split('\\');
                        //string[] liss1 = { liss[2], liss[1] }
                        //Save_to_pg(listss, path1);
                        Xiugai(listss, path1);
                    }
                    else
                    {
                        path1 = path_new + @"\" + name + @".png";
                        Writeimg(path1, picByte);
                        //liss = path.Split('\\');
                        //string[] liss1 = { liss[2], liss[1] }
                        Save_to_pg(listss, path1);
                        Xiugai(listss, path1);
                    }
                }
            }
            else
            {
                Writeimg(path1, picByte);
                Save_to_pg(listss, path1);
                Save_to_pg_new(listss, path1);
            }
        }

        private static void Save_to_pg(string[] lists, string paths)
        {
            //用于向最原始的数据库插入数据

            string mysql;//,table;   //sql语句和表名
            NpgsqlConnection c = new NpgsqlConnection();   //新建数据库连接
            NpgsqlCommand cmd = new NpgsqlCommand();
            //NpgsqlDataAdapter da = new NpgsqlDataAdapter();  //数据适配器
            //DataSet ds = new DataSet();
            string s;
            s = "Server=*.*.*.*;Port=5432;User Id=postgres;Password=*****;Database=map;";
            c.ConnectionString = s;    //连接postgresql
            c.Open();   //打开数据库
            mysql = string.Format("insert into {0}(title_x,title_y,create_time,rank,path)values('{1}','{2}',CURRENT_DATE,{3},'{4}')", lists[1], lists[3], lists[4], lists[2], paths);
            Console.WriteLine(mysql);
            cmd.CommandText = mysql;
            cmd.Connection = c;
            NewMethod(cmd);
            Console.WriteLine("数据插入数据库");
            c.Close();
        }

        private static void Save_to_pg_new(string[] lists, string paths)
        {
            //用于向最新表的数据库插入数据
            string mysql;//,table;   //sql语句和表名
            NpgsqlConnection c = new NpgsqlConnection();   //新建数据库连接
            NpgsqlCommand cmd = new NpgsqlCommand();
            //NpgsqlDataAdapter da = new NpgsqlDataAdapter();  //数据适配器
            //DataSet ds = new DataSet();
            string s;
            s = "Server=*.*.*.*;Port=5432;User Id=postgres;Password=*****;Database=map;";
            c.ConnectionString = s;    //连接postgresql
            c.Open();   //打开数据库
            mysql = string.Format("insert into {0}(title_x,title_y,create_time,rank,path)values('{1}','{2}',CURRENT_DATE,{3},'{4}')", lists[1], lists[3], lists[4], lists[2], paths);
            Console.WriteLine(mysql);
            cmd.CommandText = mysql;
            cmd.Connection = c;
            NewMethod(cmd);
            Console.WriteLine("数据插入数据库");
            c.Close();
        }

        private static string select_to_pg(string[] lists)
        {
            //用于向最新的数据库查询最新瓦片的存储地址
            string mysql;//,table;   //sql语句和表名
            NpgsqlConnection c = new NpgsqlConnection();   //新建数据库连接
            NpgsqlCommand cmd = new NpgsqlCommand();
            //NpgsqlDataAdapter da = new NpgsqlDataAdapter();  //数据适配器
            //DataSet ds = new DataSet();
            string s;
            s = "Server=*.*.*.*;Port=5432;User Id=postgres;Password=*****;Database=map;";
            c.ConnectionString = s;    //连接postgresql
            c.Open();   //打开数据库
            mysql = string.Format("select path from {0} where title_x='{1}' and title_y ='{2}' ", lists[1], lists[3], lists[4]);
            //Console.WriteLine(mysql);
            cmd.CommandText = mysql;
            cmd.Connection = c;
            //NewMethod(cmd);
            //string path=cmd.ExecuteReader().ToString();
            Console.WriteLine(mysql);
            IDataReader dr = cmd.ExecuteReader();
            string path = string.Empty;
            while (dr.Read())
            {
                path = dr[0].ToString();
            }
            Console.WriteLine("数据查询成功");
            c.Close();
            return path;
        }


        private static void Xiugai(string[] lists, string paths)
        {
            //更改最新数据中最新的数据，即new数据库始终保持更新最新的地图瓦片。
            string mysql;//,table;   //sql语句和表名
            NpgsqlConnection c = new NpgsqlConnection();   //新建数据库连接
            NpgsqlCommand cmd = new NpgsqlCommand();
            //NpgsqlDataAdapter da = new NpgsqlDataAdapter();  //数据适配器
            //DataSet ds = new DataSet();
            string s;
            s = "Server=*.*.*.*;Port=5432;User Id=postgres;Password=*****;Database=map;";
            c.ConnectionString = s;    //连接postgresql
            c.Open();   //打开数据库
            mysql = string.Format("UPDATE {0} SET create_time=current_date,path='{1}' where title_x='{2}' and title_y ='{3}' ", lists[1], paths, lists[3], lists[4]);
            //Console.WriteLine(mysql);
            cmd.CommandText = mysql;
            cmd.Connection = c;
            NewMethod(cmd);
            Console.WriteLine("数据修改成功");
            c.Close();
        }

        private static void NewMethod(NpgsqlCommand cmd)
        {
            cmd.ExecuteNonQuery();
        }

        private static byte[] Handleget(HttpListenerRequest request, HttpListenerResponse response)
        {
            string url = request.Url.AbsolutePath;
            Console.WriteLine(url);
            string img_Path = @"Z:\map" + @url.Replace("/", @"\") + @".png";
            string filePath = @"Z:\map\MyServiceLog2.txt"; 
            using (FileStream stream = new FileStream(filePath, FileMode.Append))
            using (StreamWriter writer = new StreamWriter(stream))
            {
                    
                writer.WriteLine("照片为空zas");
            }
            byte[] imgByte=null;
            if (File.Exists(img_Path))
            {   
                using (FileStream stream = new FileStream(filePath, FileMode.Append))
                using (StreamWriter writer = new StreamWriter(stream))
                {
                    
                    writer.WriteLine("照片为空zasss");
                }
                FileStream files = new FileStream(img_Path, FileMode.Open);
                imgByte = new byte[files.Length];
                files.Read(imgByte, 0, imgByte.Length);
                files.Close();
            }
            return imgByte;

        }
        protected override void OnStop()
        {
                using (FileStream stream = new FileStream(filePath, FileMode.Append))
                using (StreamWriter writer = new StreamWriter(stream))
                {
                    writer.WriteLine($"{DateTime.Now},服务停止！");
                }
        }
    }
}
 