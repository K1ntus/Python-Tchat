import socket
import select
import threading



#partie2
s = socket.socket(family=socket.AF_INET6, type=socket.SOCK_STREAM, proto=0, fileno=None)

s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
s.bind(('',7777))
s.listen(1) 


def read_and_write(n1):
    while(1):
        data = n1.recv(1500)
        print("data=",data.decode(),"xxxx" )
        if not data or data.decode() == '\n':
            n1.close()
            return
        n1.send(data)
    return

    
    

while (1):
    (n1,addr) = s.accept()
    Thread = threading.Thread(None, read_and_write, None, (n1,)).start()
s.close()
    
