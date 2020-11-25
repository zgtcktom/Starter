import collections
import threading
import socket
import time
import datetime

class SocketThread(threading.Thread):
    def __init__(self, host, port, ptype):
        super().__init__()
        assert ptype == 'udp' or ptype == 'tcp'
        
        self.ptype = ptype
        self.addr = (host, port)
        
        self._stop_event = threading.Event()
        
    def print(self, *args, **kwargs):
        print(*args, **kwargs)
        
    def stop_wait(self):
        self._stop_event.set()
        self.join()
    
    def connect(self):
        pass
    
    def receive(self):
        pass
    
    def close(self):
        pass
    
    def respond(self):
        pass

def udp_server(self):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setblocking(False)
        s.bind(self.addr)
        self.connect()
        while not self._stop_event.is_set():
            try:
                data, addr = s.recvfrom(1024)
                self.print('[UDP server]', '[Receiving]', 'from', addr, 'to', self.addr, ':', '\n', data)
                self.receive()
                
                data, addr = ('msg received: ' + str(data)).encode(), addr
                s.sendto(data, addr)
                self.print('[UDP server]', '[Sending]', 'from', self.addr, 'to', addr, ':', '\n', data)
                self.respond()
            except:
                pass
    self.close()
    
def tcp_conn(self, conn, addr, stop_event):
    with conn as s:
        self.connect()
        #s.setblocking(False)
        while not stop_event.is_set():
            try:
                data, addr = s.recv(1024), addr
                if not data:
                    stop_event.set()
                    break
                self.print('[TCP server]', '[Receiving]', 'from', addr, 'to', self.addr, ':', '\n', data)
                self.receive()
                
                data, addr = ('msg received: ' + str(data)).encode(), addr
                s.send(data)
                self.print('[TCP server]', '[Sending]', 'from', self.addr, 'to', addr, ':', '\n', data)
                self.respond()
            except:
                pass
    self.print('[TCP server]', '[Disconnected]', 'from', addr, 'to', self.addr)
    
def tcp_server(self):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(self.addr)
        s.listen(5)
        conns = []
        s.setblocking(False)
        while not self._stop_event.is_set():
            try:
                conn, addr = s.accept()
                self.print('[TCP server]', '[Connected]', 'from', addr, 'to', self.addr)
                stop_event = threading.Event()
                conn_thread = threading.Thread(target=tcp_conn, args=(self, conn, addr, stop_event))
                conns.append((conn_thread, stop_event))
                conn_thread.start()
            except Exception as e:
                pass
    for _, stop_event in conns:
        stop_event.set()
    for conn_thread, _ in conns:
        conn_thread.join()
    self.close()
        
class ServerThread(SocketThread):
    def __init__(self, host='0.0.0.0', port=80, ptype='udp'):
        super().__init__(host, port, ptype)
        
        self.history = collections.defaultdict(lambda: [])
        
    def run(self):
        if self.ptype == 'udp':
            udp_server(self)
        elif self.ptype == 'tcp':
            tcp_server(self)

def udp_client(self):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setblocking(False)
        self.connect()
        while not self._stop_event.is_set():
            try:
                data, addr = str(datetime.datetime.now()).encode(), self.addr
                s.sendto(data, addr)
                self.print('[UDP client]', '[Sending]', 'to', addr, ':', '\n', data)
                self.respond()

                data, addr = s.recvfrom(1024)
                self.print('[UDP client]', '[Receiving]', 'from', addr, ':', '\n', data)
                self.receive()
            except:
                pass
            time.sleep(1)
    self.close()
    
def tcp_client(self):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(self.addr)
        #s.setblocking(False)
        self.connect()
        self.print('[TCP client]', '[Connected]', 'to', self.addr)
        while not self._stop_event.is_set():
            try:
                data, addr = str(datetime.datetime.now()).encode(), self.addr
                s.send(data)
                self.print('[TCP client]', '[Sending]', 'to', addr, ':', '\n', data)
                self.respond()

                data, addr = s.recv(1024), addr
                self.print('[TCP client]', '[Receiving]', 'from', addr, ':', '\n', data)
                self.receive()
            except:
                pass
            time.sleep(1)
    self.print('[TCP client]', '[Disconnected]', 'to', self.addr)
    pass
        
class ClientThread(SocketThread):
    def __init__(self, host='127.0.0.1', port=80, ptype='udp'):
        super().__init__(host, port, ptype)
        
        self._buffer = []
        
    def run(self):
        if self.ptype == 'udp':
            udp_client(self)
        elif self.ptype == 'tcp':
            tcp_client(self)
            
    def write(self, msg):
        msg = str(msg)
        self._buffer.append(msg)
            
        
if __name__ == '__main__':
    type = input('(0) server, (1) client\n')
    ptype='tcp'
    if type == '0':
        th = ServerThread(ptype=ptype)
    elif type == '1':
        th = ClientThread(ptype=ptype)
    th.start()

    try:
        input('enter to stop\n')
    except KeyboardInterrupt:
        pass
    th.stop_wait()