from HttpProxy import HttpProxy, GetData
from queue import Queue
from types import FunctionType
import eel,re,binascii
import socket
import gevent.monkey
gevent.monkey.patch_all()
#eel初始化前端
eel.init('web')
#代理对象未初始化
proxy = None
#正在被处理的数据
processing_data = None
processing_data_timestamp = None
processing_socket = None
processing_finished = True
#当前页号,默认是第一页,也就是proxy界面
tab=1

#前一个被处理的数据
# last_processing_data = None
# last_processing_data_timestamp = None


@eel.expose
def begin_listening():
    #开启一个代理
    global proxy
    proxy = HttpProxy(Queue(100), './record', port=6666,callback=_get_data_callback,secure=True)
    proxy.start()


@eel.expose
def end_listening():
    global proxy
    # print('close proxy')
    proxy.stop()
    proxy = None

@eel.expose
def set_blocking(blocking=False):
    global proxy
    proxy.is_forward=not blocking
    print('blocking:',blocking)

# @eel.expose
# def queryData(filter):  
#     # 前端主动查询是否捕获到了请求(考虑增加一个代理主动通知前端的函数)
#     global proxy
#     if not handler:
#         try:
#             handler = proxy.queue.get()
#         except:  # proxy==None or queue is empty
#             return ''
#         print('query once')
#         handler_data=handler.to_data()
#         if handler_data:
#             l=filter.split('||')#根据过滤规则检查,不符合的直接pass
#             for i in l:
#                 if re.search(i,handler_data):
#                     return (handler_data,True)
#         return (handler_data,False)
#     else:
#         return ''

@eel.expose
def get_processing_data(to_hex=False):
    global processing_data
    #print(processing_data)
    if to_hex:
        return binascii.b2a_hex(processing_data.encode('ascii')).decode('ascii')
    else:
        return processing_data

@eel.expose
def update_processing_data(new_data,is_hex=False):
    global processing_data
    if is_hex:
        processing_data = binascii.a2b_hex(new_data.encode('ascii')).decode('ascii')
    else:
        processing_data = new_data


@eel.expose
def send_to_repeater(data):
    proxy.send_to_repeater(data)


@eel.expose
def delete_repeater(index):
    proxy.delete_a_repeater(index)

@eel.expose
def get_repeater():
    print("repeater:",proxy.repeater)
    return proxy.repeater

@eel.expose
def get_history():
    print("history:",proxy.history)
    return proxy.history

@eel.expose
def send_data_to_server():
    global processing_finished
    # 将代理捕获的数据发送给服务器,调整为单开一个线程,以及将数据缓存而不是返回
    proxy.send_data_to_server(processing_data,processing_data_timestamp,processing_socket)
    processing_finished=True
    # return

@eel.expose
def run_data(args_data,script):
    #动态创建函数用来执行args_data
    code=compile(script,"<string>","exec")
    func=FunctionType(code.co_consts[0],globals(),"process")
    return func(args_data)

# @eel.expose
# def sendDataToClient(data):  
#     # 将对应的响应交给当前正在处理的客户端套接字
#     print('send to client')
#     global client,client_data
#     try:
#         #向当前正在处理的客户端发送数据
#         proxy.send_data_to_client(client,data)
#         #向历史套接字记录里添加接收到的客户端数据和服务器数据
#         history[len(history)]=(client_data,data)
#     except:  # 套接字已经被客户端关闭了
#         pass
#     client = None

@eel.expose
def add_filter_to_response(script):
    code=compile(script,"<string>","exec")
    func=FunctionType(code.co_consts[0],globals(),"process")
    proxy.add_filter_to_response(func)
    # return

# @eel.expose
# def drop():#丢掉当前请求
#     try:
#         processing_socket.close()
#         processing_socket=None
#     except:
#         pass
#完全没有必要嘛,这个功能


@eel.expose
def test():
    # data_coming()
    proxy.send('test')
    
def _get_data_callback():
    global processing_data,processing_data_timestamp,processing_socket,processing_finished
    print("new data comming")
    if processing_finished:
        processing_socket,processing_data,processing_data_timestamp = proxy.queue.get()
        eel.new_data_comming()()
        #print("new data comming")
        processing_finished=False

eel.start('index.html', mode='edge', host='127.0.0.1',
          port=8000, cmdline_args=['--start-fullscreen'])
