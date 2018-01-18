import asyncserver
import time

class MyHandler(asyncserver.Handler):
    def __init__(self):
        asyncserver.Handler.__init__(self)

    def send_handler(self): #override
        data = self.get_recv_buffer()
        if(len(data) > 1):
            self.flush()
            self.add_send_buffer(data)

def main():
    host, port = "", 31337
    server = asyncserver.NonblockServer(
        host,
        port,
        max_fd=100000,
        debug=1,
        backlog=10000,
        timeout=10*60
    )
    server.run(MyHandler)
    
if(__name__ == "__main__"):
    main()