from HttpProxy import HttpProxy, GetData
from queue import Queue
from types import FunctionType
import eel,re
import socket
import gevent.monkey
gevent.monkey.patch_all()
eel.init('web')
proxy = None
client = None
session_queue = None
alive_client = []
repeater = []


@eel.expose
def hello_world():
    return "Hello world from python"


@eel.expose
def print_string(string):
    if len(string) > 20:
        print(string)
        return "Success!"
    else:
        return "Please type more than 20 characters."


@eel.expose
def beginListening():
    global proxy, client, session_queue
    session_queue = Queue(maxsize=0)
    proxy = HttpProxy(session_queue, './record', port=6666)
    proxy.start()


@eel.expose
def endListening():
    global proxy
    print('close proxy')
    proxy.stop()
    proxy = None


@eel.expose
def queryData(filter):  # 浏览器查询是否捕获到了请求
    global proxy, client, session_queue
    if not client:
        try:
            session = session_queue.get()
        except:  # proxy==None or session_queue is empty
            return ''
        (client, data) = session
        print('query once')
        data=data.decode('utf-8')
        if data:
            l=filter.split('||')#根据过滤规则检查,不符合的直接pass
            for i in l:
                if re.search(i,data):
                    return (data,True)
        return (data,False)
    else:
        return ''


@eel.expose
def sendToRepeater(data):
    repeater.append(data)


@eel.expose
def deleteRepeater(index):
    del repeater[index]


@eel.expose
def sendDataToServer(data, flag=1):  # 发送http请求获得返回的http响应
    print('begin send data to server')
    try:
        host = data.split('\r\n')[1].split(':')
    except:
        host = data.split('\n')[1].split(':')
    # print(data)
    if len(host) == 2:
        host.append('80')
    (_, host, port) = host
    host = host.strip()
    # print(host+':'+port)
    # print(socket.getaddrinfo(host,80))
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
    if flag:
        sendDataToClient(buf)
    return buf.decode('utf-8')

@eel.expose
def processData(data,script):
    code=compile(script,"<string>","exec")
    func=FunctionType(code.co_consts[0],globals(),"process")
    return func(data)

@eel.expose
def sendDataToClient(data):  # 将对应的响应交给对应的会话
    print('send to client')
    global client
    try:
        client.send(data)
        client.close()
    except:  # 套接字被关闭了,自说自话的错误
        pass
    client = None


@eel.expose
def drop():#丢掉当前请求
    try:
        client.close()
    except:
        pass

eel.start('index.html', mode='chrome-app', host='127.0.0.1',
          port=8000, cmdline_args=['--start-fullscreen'])
