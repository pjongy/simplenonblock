
# Pythonasyncserver
Python 2.7.x, 3.6.x non-block TCP server

```
Non-block TCP servers commonly use kernel defined functions
(ex. select, poll, epoll ...) for performance
But in Windows, should uses IOCP that is replacement of epoll in linux.
When using select in Windows, only defined FD (Handle) count can acceptable.
(default 512 in python)
It can't control C10k problem (Concurrent 10,000 connection)
So in this case, this code not uses select but also iterates all connected FD.
```

 So it can control c10k problem but causes CPU's resource waste

## Using with arbitrary client limitation
```python
import asyncserver

class MyHandler(asyncserver.Handler):
    def __init__(self):
        asyncserver.Handler.__init__(self)

    def send_handler(self):
        data = self.get_recv_buffer()
        if(len(data) > 1):
            self.flush()
            self.add_send_buffer(data)

def main():
    host, port = "", 31337
    server = asyncserver.NonblockServer(
        host,
        port,
        max_fd=1000
    )
    server.run(MyHandler)
    
if(__name__ == "__main__"):
    main()
```


## Control backlog
```python
import asyncserver

class MyHandler(asyncserver.Handler):
    def __init__(self):
        asyncserver.Handler.__init__(self)

    def send_handler(self):
        data = self.get_recv_buffer()
        if(len(data) > 1):
            self.flush()
            self.add_send_buffer(data)

def main():
    host, port = "", 31337
    server = asyncserver.NonblockServer(
        host,
        port,
        backlog=1000
    )
    server.run(MyHandler)
    
if(__name__ == "__main__"):
    main()
```

## Debug mode
```python
import asyncserver

class MyHandler(asyncserver.Handler):
    def __init__(self):
        asyncserver.Handler.__init__(self)

    def send_handler(self):
        data = self.get_recv_buffer()
        if(len(data) > 1):
            self.flush()
            self.add_send_buffer(data)

def main():
    host, port = "", 31337
    server = asyncserver.NonblockServer(
        host,
        port,
        debug=1
    )
    server.run(MyHandler)
    
if(__name__ == "__main__"):
    main()
```

SOURCECODE:
[asyncserver.py](./asyncserver.py)
