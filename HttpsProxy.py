from BaseProxy import AsyncMitmProxy
from queue import Queue


class HttpsProxy(AsyncMitmProxy):
    def __init__(self, queue, file_path, callback, host='0.0.0.0', port=8080):
        self.request_queue = Queue(maxsize=0)
        self.response_queue = Queue(maxsize=0)
        super().__init__(self.request_queue,self.response_queue,(host,port))
        #备份路径
        self.file_path = file_path
        #代理地址
        self.host = host
        #代理端口
        self.port = port
        #接收到的套接字及数据队列
        self.queue = queue
        #接收到数据后的回调函数
        self.callback = callback

    def send(self,data:str):
        #向自己发请求
        sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = 'localhost' if self.host == '0.0.0.0' else self.host
        sender.connect((host, self.port))
        sender.sendto(data.encode(), (host, self.port))
        sender.close()