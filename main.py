import eel,socket
import gevent.monkey
gevent.monkey.patch_all()
from HttpProxy import HttpProxy
eel.init('web')
proxy = None
client = None
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
    global proxy, client
    client = []
    proxy = HttpProxy('./record')
    eel.spawn(proxy.run)


@eel.expose
def endListening():
    global proxy
    print('close proxy')
    proxy.stop()
    proxy = None


@eel.expose
def queryData():  #浏览器查询是否捕获到了请求
    global proxy, client
    try:
        session = proxy.session_queue.get()
    except:  #proxy==None or session_queue is empty
        return ''
    (client, data) = session
    print('query once')
    return data.decode('utf-8')


@eel.expose
def sendToRepeater(data):
    repeater.append(data)


@eel.expose
def deleteRepeater(index):
    del repeater[index]


@eel.expose
def sendDataToServer(data):  #发送http请求获得返回的http响应
    print('begin send data to server')
    host = data.split('\r\n')[1].split(':')
    #print(data)
    if len(host) == 2:
        host.append('80')
    (_, host, port) = host
    host=host.strip()
    #print(host+':'+port)
    print(socket.getaddrinfo(host,80))
    host=(socket.getaddrinfo(host,int(port))[0][4][0])
    print(host)
    #print('finish print')
    sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("host"+host)
    print('port%d'%int(port))
    sender.connect((host, int(port)))
    #print(data.encode('utf-8'))
    sender.send(data.encode('utf-8'))
    buf = ''
    sender.settimeout(1)
    while True:
        try:
            response = sender.recv(2048)
            if not response:
                break
            else:
                buf += response.decode('utf-8')
        except:
            break
    return buf


@eel.expose
def sendDataToClient(data):  #将对应的响应交给对应的会话
    client.send(data.encode('utf-8'))


eel.start('index.html',mode=None,host='0.0.0.0',port=8000)
