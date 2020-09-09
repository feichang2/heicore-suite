from HttpProxy import HttpProxy, GetData
from queue import Queue
from types import FunctionType
import eel,re
import socket
import gevent.monkey
gevent.monkey.patch_all()
#eel初始化前端
eel.init('web')
#代理对象未初始化
proxy = None
#正在被处理的客户端套接字对象
client = None
#正在被处理的客户端套接字对象发送的数据
client_data = None
#没有被处理的客户端套接字对象的队列
session_queue = None
#历史套接字数据及其响应数据
history={}
alive_client = []
repeater = []

def data_coming():
    print("set data comming")
    eel.setDataComming()

@eel.expose
def beginListening():
    #开启一个代理
    global proxy, session_queue
    session_queue = Queue(maxsize=0)
    proxy = HttpProxy(session_queue, './record', data_coming, port=6666)
    proxy.start()


@eel.expose
def endListening():
    global proxy
    print('close proxy')
    proxy.stop()
    proxy = None


@eel.expose
def queryData(filter):  
    # 前端主动查询是否捕获到了请求(考虑增加一个代理主动通知前端的函数)
    global proxy, client, session_queue, client_data
    if not client:
        try:
            session = session_queue.get()
        except:  # proxy==None or session_queue is empty
            return ''
        (client, client_data) = session
        print('query once')
        client_data=client_data.decode('utf-8')
        if client_data:
            l=filter.split('||')#根据过滤规则检查,不符合的直接pass
            for i in l:
                if re.search(i,client_data):
                    return (client_data,True)
        return (client_data,False)
    else:
        return ''


@eel.expose
def sendToRepeater(data):
    repeater.append(data)


@eel.expose
def deleteRepeater(index):
    del repeater[index]


@eel.expose
def sendDataToServer(data, flag=1):  
    # 将代理捕获的数据发送给服务器,然后接收数据作为返回,考虑调整为单开一个线程,以及将数据缓存而不是返回
    print('begin send data to server')
    global client_data
    #修改当前正在处理套接字的数据
    client_data=data
    #获取服务器的地址和端口号
    buf=proxy.set_data_to_server(data)
    if flag:
        sendDataToClient(buf)
    return buf.decode('utf-8')

@eel.expose
def processData(data,script):
    #动态创建函数用来执行data
    code=compile(script,"<string>","exec")
    func=FunctionType(code.co_consts[0],globals(),"process")
    return func(data)

@eel.expose
def sendDataToClient(data):  
    # 将对应的响应交给当前正在处理的客户端套接字
    print('send to client')
    global client,client_data
    try:
        #向当前正在处理的客户端发送数据
        proxy.send_data_to_client(client,data)
        #向历史套接字记录里添加接收到的客户端数据和服务器数据
        history[len(history)]=(client_data,data)
    except:  # 套接字已经被客户端关闭了
        pass
    client = None


@eel.expose
def drop():#丢掉当前请求
    try:
        client.close()
        client=None
    except:
        pass


@eel.expose
def test():
    # data_coming()
    proxy.send('test')
    

eel.start('index.html', mode='chrome-app', host='127.0.0.1',
          port=8000, cmdline_args=['--start-fullscreen'])
