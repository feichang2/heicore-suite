from BaseProxy import AsyncMitmProxy
from queue import Queue
import socket


class HttpsProxy(AsyncMitmProxy):
    def __init__(self, file_path,  host='0.0.0.0', port=8080):
        # self.request_queue = Queue(maxsize=0)
        # self.response_queue = Queue(maxsize=0)
        # super().__init__(self.request_queue,self.response_queue,(host,port))
        super().__init__(Queue(maxsize=0),Queue(maxsize=0),(host,port))
        #备份路径
        self.file_path = file_path
        #代理地址
        self.host = host
        #代理端口
        self.port = port
        #接收到的套接字及数据队列
        # self.queue = queue
        #接收到数据后的回调函数
        self.callback = callback

    def send(self,data:str):
        #向自己发请求
        sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = 'localhost' if self.host == '0.0.0.0' else self.host
        sender.connect((host, self.port))
        sender.sendto(data.encode(), (host, self.port))
        sender.close()

    def stop(self):
        #关掉所有连接后,关闭请求
        while not self.request_queue.empty:
            handler = self.request_queue.get()
            handler.send_error(500,"proxy stopped")
        while not self.response_queue.empty:
            handler = self.response_queue.get()
            handler.send_error(500,"proxy stopped")
        self.server_close()