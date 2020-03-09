from threading import Thread
from queue import Queue
import socket
import sys
import time
import os
import eel


# 直接HttpProxy().start()就可以开始一个线程
class HttpProxy(Thread):
    __listening = 1

    def __init__(self, queue, file_path, host='0.0.0.0', port=8080):
        super().__init__()
        self.file_path = file_path
        self.host = host
        self.port = port
        self.queue = queue

    def run(self):
        proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            proxy.bind((self.host, self.port))
        except:
            sys.exit("bind error!!Is the port free of use?")
        print("proxy start")
        proxy.listen(1024)
        while self.__listening == 1:
            client, _ = proxy.accept()
            GetData(self.queue, self.file_path, client).start()
            time.sleep(0.1)

    def stop(self):
        self.__listening = 0
        sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = 'localhost' if self.host == '0.0.0.0' else self.host
        sender.connect((host, self.port))
        sender.sendto(''.encode(), (host, self.port))
        sender.close()
        while not self.queue.empty:
            (client, _) = self.queue.get()
            client.close()


class GetData(Thread):
    def __init__(self, queue, file_path, client):
        super().__init__()
        self.queue = queue
        self.path = file_path
        self.client = client

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
        self.queue.put((self.client, header))
        with open(self.path, 'a') as f:
            f.write(header.decode('utf-8'))
            f.close()


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
