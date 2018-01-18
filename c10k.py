import socket
import threading
import queue as queue
import time
import multiprocessing
import sys

def r(q, fq):
    fq.put(1)
    while(1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(("127.0.0.1", 31337))
            send_size = 24000
            s.sendall(b"A"*send_size)
            data = b""
            while(len(data) < send_size):
                #print(send_size)
                if(len(data) == send_size):
                    break
                tmp_data = s.recv(1024)
                data += tmp_data
            if(len(data) == send_size):
                q.put(1)
            s.close()
            break
        except:
            s.close()

def t():
    first = time.time()
    q = queue.Queue()
    fq = queue.Queue()
    ts = []
    for _ in range(500):
        t = threading.Thread(target=r, args=(q,fq,))
        t.start()
        ts.append(t)
    while(1):
        time.sleep(1)
        print("Total: %d/%d"%(q.qsize(), fq.qsize()))
        last = time.time()
        print("Time: %d secs"%(last - first))
 
if(__name__ == "__main__"):
    concurrent = 10000
    for x in range(int(concurrent / 500)+1):
        print("Process %d Start"%x)
        p = multiprocessing.Process(target = t)
        p.start()
    sys.exit()
