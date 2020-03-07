from threading import Thread
from queue import Queue
import socket, sys, time, os,eel


#直接HttpProxy().start()就可以开始一个线程
class HttpProxy(Thread):
    __listening = 1

    def __init__(self, file_path, host='0.0.0.0', port=8080):
        super().__init__()
        self.file_path = file_path
        self.host = host
        self.port = port
        self.session_queue = Queue(maxsize=0)

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
            Thread(target=self.record, args=(self.file_path, client)).start()
            time.sleep(1)

    def stop(self):
        self.__listening = 0
        sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = 'localhost' if self.host == '0.0.0.0' else self.host
        sender.connect((host, self.port))
        sender.sendto(''.encode(), (host, self.port))
        sender.close()
        while not self.session_queue.empty:
            (client, _) = self.session_queue.get()
            client.close()

    def record(self, path, client):
        client.settimeout(2)
        header = client.recv(4096)
        print(header)
        self.session_queue.put((client, header))
        with open(path, 'a') as f:
            f.write(header.decode('utf-8'))
            f.close()


if __name__ == "__main__":
    with open('./test.record', 'w') as f:
        f.write('')
        f.close()
    proxy = HttpProxy('./test.record')
    proxy.start()
    print('try to send sth')
    sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sender.connect(('192.168.0.103', 8080))
    sender.sendto('just test can i end the threading'.encode(),
                  ('192.168.0.103', 8080))
    sender.close()
    time.sleep(32)
    proxy.stop()
    sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sender.connect(('192.168.0.103', 8080))
    sender.sendto('try to end again'.encode(), ('192.168.0.103', 8080))
    sender.close()