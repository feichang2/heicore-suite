from threading import Thread
from queue import Queue
import socket
import sys
import time
import os
import eel


# 直接HttpProxy().start()就可以开始一个线程作为代理
class HttpProxy(Thread):
    __listening = 1

    def __init__(self, queue, file_path, callback, host='0.0.0.0', port=8080):
        super().__init__()
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

    def run(self):
        proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            proxy.bind((self.host, self.port))
        except:
            sys.exit("bind error!!Is the port free of use?")
        print("proxy start")
        proxy.listen(1024)
        while self.__listening == 1:
            #处于监听状态时,对于每一个连接到代理的socket,开启一个线程用于接收它的数据,然后代理继续监听,等待下一个连接
            client, _ = proxy.accept()
            GetData(self.queue, self.file_path, client, self.callback).start()
            # time.sleep(0.1)
    
    def send(self,data:str):
        #向自己发请求
        sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = 'localhost' if self.host == '0.0.0.0' else self.host
        sender.connect((host, self.port))
        sender.sendto(data.encode(), (host, self.port))
        sender.close()

    def stop(self):
        #用来关闭代理
        #首先是关闭监听
        self.__listening = 0
        #然后向该代理发一个空请求,因为accept是阻塞等待的,这样才会发现监听状态已关闭
        self.send('')
        #对于每一个之前连接到的,还没有处理的套接字,逐个关闭
        while not self.queue.empty:
            (client, _) = self.queue.get()
            client.close()

    def set_data_to_server(self, data):
        try:
            host = data.split('\r\n')[1].split(':')
        except:
            host = data.split('\n')[1].split(':')
        # print(data)
        if len(host) == 2:
            host.append('80')
        (_, host, port) = host
        host = host.strip()
        if host == 'localhost':
            host = "127.0.0.1"
        else:
            host = (socket.getaddrinfo(host, int(port))[0][4][0])
        print(host)
        print('finish print')
        sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("host"+host)
        print('port%d' % int(port))
        sender.connect((host, int(port)))
        print(data.encode('utf-8'))
        sender.send(data.encode('utf-8'))
        buf = b''
        sender.settimeout(3)
        try:
            response = sender.recv(1024)
            buf = response
            while response:
                response = sender.recv(1024)
                buf += response
        except:
            pass
        print(buf)
        return buf

    def send_data_to_client(self,client,data):
        client.send(data)
        client.close()


class GetData(Thread):
    #对于每一个连接到代理的套接字,一个单独的线程用来获取数据
    def __init__(self, queue, file_path, client, callback):
        super().__init__()
        self.queue = queue
        self.path = file_path
        self.client = client
        self.callback = callback

    def run(self):
        header = ''.encode()
        print(self.name)
        self.client.settimeout(1)
        while True:
            try:
                response = self.client.recv(2048)
                if not response:
                    break
                else:
                    header += response
            except:
                break
        print(header)
        #数据放入队列
        self.queue.put((self.client, header))
        #执行回调函数
        self.callback()
        #备份一下数据,为了调试
        with open(self.path, 'a') as f:
            f.write(header.decode('utf-8'))


if __name__ == "__main__":
    with open('./test.record', 'w') as f:
        f.write('')
        f.close()
    session_queue = Queue(maxsize=0)
    proxy = HttpProxy(session_queue, './test.record')
    proxy.start()
    history=[]
    print('try to send sth')
    '''for i in range(32):
        sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sender.connect(('192.168.0.103', 8080))
        sender.sendto('junk data ,test the theading'.encode(),
                      ('192.168.0.103', 8080))
        history.append(sender)'''
    time.sleep(32)
    proxy.stop()
