import socket
import errno
import sys
import time
import abc

VERSION = sys.version_info.major
if(VERSION == 3):
    import queue
else:
    import Queue as queue


BLOCK_CONDITION = lambda e:(
    e.errno == errno.EWOULDBLOCK
)
ABORT_CONDITION = lambda e:(
    e.errno == errno.ECONNABORTED
)
RESET_CONDITION = lambda e:(
    e.errno == errno.ECONNRESET
)

class Handler(abc.ABCMeta('ABC', (object,), {'__slots__': ()})):
    def __init__(self):
        self.__recv_buffer = []
        self.__send_buffer = queue.Queue()
        self.__start_time = time.time()

    def add_recv_buffer(self, data):
        self.__recv_buffer.append(data)

    def get_recv_buffer(self, size=-1):
        buffer = b"".join(self.__recv_buffer)
        if(size == -1):
            return buffer
        return buffer[:size]

    def add_send_buffer(self, data):
        self.__send_buffer.put(data)

    def get_send_buffer(self):
        return self.__send_buffer
    
    def flush(self, data = None):
        if(data == None):
            self.__recv_buffer = []
        else:
            self.__recv_buffer = [data]

    def is_timeouted(self, current_time, timeout):
        if(current_time - self.__start_time > timeout):
            return 1
        else:
            return 0

    @abc.abstractmethod
    def send_handler(self):
        pass


class Error(socket.error):
    def __init__(self):
        self.errno = errno.ECONNABORTED
        
class NonblockServer(object):
    def __init__(
        self,
        host,
        port,
        max_fd=1000,
        timeout=300,
        debug=0,
        backlog=5
    ):
        self.host = host
        self.port = int(port)
        self.debug = debug
        
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #reuse socket addr
        self.__socket.bind((self.host, self.port))
        self.__socket.setblocking(0)
        #non-block
        
        self.timeout = timeout
        self.backlog = backlog
        self.max_fd = max_fd
        self.peers = {}

        self.destruct_queue = []
        print(
            "HOST: %s / PORT: %d / TIMEOUT: %d / BACKLOG: %d / MAX_FD: %d"
            %(host, port, timeout, backlog, max_fd)
        )

        if(self.debug):
            self.debug_time = time.time()

    def put_destruct_socket(self, peer):
        if(peer not in self.destruct_queue):
            self.destruct_queue.append(peer)

    def run(self, ArbitraryHandler = Handler):
        self.__socket.listen(self.backlog)
        while(1):
            if(self.debug and self.debug_time+1 < time.time()):
                print("Peers: "+str(len(self.peers.keys())))
                print("DestructQueue: "+str(len(self.destruct_queue)))
                self.debug_time = time.time()
            try:
                conn, addr = self.__socket.accept()
                conn.setblocking(0)
                if(self.max_fd > len(self.peers.keys())):
                    if(self.debug):
                        print("Connected")
                    self.peers[conn] = ArbitraryHandler()
                else: #if can't accept more connection (rely on max_fd)
                    if(self.debug):
                        print("No more connect")
                    conn.close()
            except socket.error as e:
                if(BLOCK_CONDITION(e)):
                    pass
                else:
                    raise e

            current_time = time.time()
            for peer in self.peers.keys():
                peer_instance = self.peers[peer]
                try: #recv
                    recv = peer.recv(1024)
                    if(not recv):
                        raise Error()
                    peer_instance.add_recv_buffer(recv)
                except socket.error as e:
                    if(BLOCK_CONDITION(e)):
                        pass
                    elif(ABORT_CONDITION(e) or RESET_CONDITION(e)):
                        if(self.debug):
                            print("Shutdowned")
                        self.put_destruct_socket(peer)
                    else:
                        raise e
                if(peer_instance.is_timeouted(current_time, self.timeout)):
                    if(self.debug):
                        print("Timeouted")
                    self.put_destruct_socket(peer)

                try: #send
                    peer_instance.send_handler()
                    data = peer_instance.get_send_buffer().get_nowait()
                    peer.send(data)
                except queue.Empty as e:
                    pass

            while(1):
                try:
                    conn = self.destruct_queue.pop(0)
                    self.peers.pop(conn)
                    if(self.debug):
                        print("Destruct Socket")
                except IndexError as e:
                    break
                except KeyError as e:
                    break
