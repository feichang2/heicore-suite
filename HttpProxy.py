from threading import Thread
from queue import Queue
import sys,re,gevent,time,os,eel,socket,ssl,pprint


# 直接HttpProxy().start()就可以开始一个线程作为代理
class HttpProxy(Thread):
    __listening = 1

    def __init__(self, queue, file_path, callback=None, host='0.0.0.0', port=8080,secure=False):
        super().__init__()
        #是否启用https
        self.secure=secure
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
        #是否阻塞
        self.is_forward = True
        #重放数据
        self.repeater = []
        #历史数据
        self.history = []
        #请求过滤器
        self.response_filters = []
        if self.secure:
            self.context=ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            self.context.load_cert_chain(certfile="cert.pem",keyfile="key.pem")

    def run(self):
        proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            proxy.bind((self.host, self.port))
            print(f"Binding @{self.host}:{self.port}")
        except:
            sys.exit("bind error!!Is the port free of use?")
        print("proxy start")
        proxy.listen(1024)
        while self.__listening == 1:
            #处于监听状态时,对于每一个连接到代理的socket,开启一个线程用于接收它的数据,然后代理继续监听,等待下一个连接
            client, _ = proxy.accept()
            #if self.secure:
                #client=self.context.wrap_socket(client,server_side=True)
            if self.is_forward:
                ForwardRequest(self.file_path,client,self.history,self.response_filters,self.secure,self.context).start()
            else:
                GetData(self.queue, self.file_path, client, self.callback,self.secure,self.context).start()
            # time.sleep(0.1)
    
    def send(self,data:str):
        #向自己发请求
        sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.secure:
            sender=ssl.wrap_socket(sender)
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
    def send_data_to_server(self, data, time_stamp,socket):
        gevent.spawn(_send_data_to_server,self.history,data, time_stamp,socket,self.response_filters,self.secure)
    
    
    def send_to_repeater(self,data):
        self.repeater.append({'data':data})
    def delete_a_repeater(self,index):
        del self.repeater[index]
    def add_filter_to_response(self,func):
        self.response_filters.append(func)

def _send_data_to_server(history, data, time_stamp,client,response_filters,secure):
    pprint.pprint(data)
    host,port=re.findall(r"Host: ([a-z\.]*)(:\d+)*",data)[0]
    if port=='':
        port=':443'if secure else ':80'
    port=port[1:]
    if(data==''):
        client.close()
        return
    
    host = host.strip()
    if host == 'localhost':
        host = "127.0.0.1"
    # else:
    #     host = (socket.getaddrinfo(host, int(port))[0][4][0])
    # print(host)
    # print('finish print')
    sender = socket.socket(socket.AF_INET)
    if secure:
        context=ssl.create_default_context()
        sender=context.wrap_socket(sender,server_hostname=host)
    print("host:"+host)
    print('port:%d' % int(port))
    sender.connect((host, int(port)))
    # print(data.encode('utf-8'))
    sender.send(data.encode('ascii'))
    buf = b''
    sender.settimeout(2)
    while True:
        try:
            response = sender.recv(512)
            if not response:
                break
            else:
                buf += response
        except:
            break
    sender.close()
    print(buf)
    for func in response_filters:
        func(buf)
    history.append((time_stamp,data,buf))#stamp,request,response
    _send_data_to_client(client,buf)

def _send_data_to_client(client,data):
    client.send(data)
    client.close()

def _get_data(client):
    header = b''
    client.settimeout(1)
    while True:
        try:
            response = client.recv(512)
            if not response:
                break
            else:
                header += response
        except:
            break
    #print(header)
    return header
class GetData(Thread):
    #对于每一个连接到代理的套接字,一个单独的线程用来获取数据
    def __init__(self, queue, file_path, client, callback, secure, context):
        super().__init__()
        self.queue = queue
        self.path = file_path
        self.client = client
        self.callback = callback
        self.secure = secure
        self.context = context

    def run(self):
        header=_get_data(self.client)
        if header[:7]==b"CONNECT":
            self.client.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
            self.client=self.context.wrap_socket(self.client,server_side=True)
            header=_get_data(self.client)
        header=header.replace(b"Connection: keep-alive",b"Connection: close")
        #数据放入队列
        self.queue.put((self.client, header.decode('ascii'), time.time()))
        #执行回调函数
        self.callback()
        #备份一下数据,为了调试
        with open(self.path, 'a') as f:
            f.write(header.decode('ascii'))

class ForwardRequest(Thread):
    def __init__(self,file_path,client,history,response_filters,secure,context):
        super().__init__()
        self.path = file_path
        self.client=client
        self.history=history
        self.response_filters=response_filters
        self.secure=secure
        self.context=context
    def run(self):
        header=_get_data(self.client)
        if header[:7]==b"CONNECT":
            self.client.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
            self.client=self.context.wrap_socket(self.client,server_side=True)
            header=_get_data(self.client)
        #备份一下数据,为了调试
        with open(self.path, 'a') as f:
            f.write(header.decode('ascii'))
        _send_data_to_server(self.history, header.decode('ascii'), time.time() ,self.client,self.response_filters,self.secure)
        

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
