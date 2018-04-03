import socket
import select
import threading

s = socket.socket(family=socket.AF_INET6, type=socket.SOCK_STREAM, proto=0, fileno=None)

s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
s.bind(('',7777))

s.listen(1)

socket_list=[s]
nick_list=["server"]


def nick_for_this_socket(socket, nick_list):
    print("nickname is: abc")

def nick_input(socket, nick):
    print(nick)

    

def cast_msg_to_everyone(l,data):
    for j in l:   #On parcours toutes les sockets SAUF la socket d'écoute
        if not j == s:
            res = ">"+" "+data.decode()
            j.send(res.encode())

def cast_to_everyone(l,data):
    for j in l:   #On parcours toutes les sockets SAUF la socket d'écoute
        try:
            if not j == s:
                j.send(data)
        except BrokenPipeError:
            print("broken pipe error! ")
            print(j)


def notify_on_join(l,name):
    (ip,a,b,c) = name
    res = "JOIN:"+" "+str(ip)+"\n"
    bytes(res, "UTF-8")
    cast_to_everyone(l,res.encode())

def notify_on_leave(l,name):
    (ip,a,b,c) = name
    res = "PART:"+" "+str(ip)+"\n"
    bytes(res, "UTF-8")
    cast_to_everyone(l,res.encode())



def get_prefix_from_data(data):
    res = ""
    i=0
    while not (data[i] == " " or data[i] == "\n"):
        res=res+data[i]
        i=i+1
    return res

def get_suffix_from_data(data):
    i=0
    data = data.decode()
    res = ""
    prefix =""
    
    while not (data[i] == " " or data[i] == "\n"):
        prefix=prefix+data[i]
        i=i+1
    print("prefix:"+prefix)

    i=i+1
    while not (data[i] == " " or data[i] == "\n"):
        res = res+data[i]
        i=i+1
    print("suffix:"+res)
    return res




    
def decode_and_compare(data,l,sock):
    string = get_prefix_from_data(data.decode())
    if string == "NICK":
        nick_input(sock,get_suffix_from_data(data))
        return True
    if string == "LIST":
        list_users(l,sock)
        return True
    if string == "KILL":
        command_kill(get_suffix_from_data(data),l)
        return True
    if string == "KICK":
        print("kick")
        return True
    if string == "MSG":
        print("msg")
        return True
    print("no special cmd, just sending usual msg")
    return False

def command_kill(ip_to_kill, socket_list):
    print("command kill asked")
    
    bytes(ip_to_kill, "UTF-8")
    for i in socket_list:   #On parcours toutes les sockets SAUF la socket d'écoute
        

        print(i.getsockname())
        (sockaddr,port,a,b) = i.getsockname()
        print(sockaddr)
        #print("i:",tab)
        #print("i[0]:",tab[i])
        #print("ip to kill:",ip_to_kill)
        if(sockaddr == ip_to_kill):
            print("ip:",sockaddr,"get killed")
            socket_list.remove(i)   #remove the socket from the list
            i.close()
            notify_on_leave(socket_list,addr)
            return
    print("No socket linked with this ip")

            
def list_users(l,sock):#list of socket except listen, and socket asking for the list of members
    for j in range(1,len(l),1):   #On parcours toutes les sockets SAUF la socket d'écoute
        (ip,port,a,b)=l[j].getsockname()#we get information about the socket at position j
        res = "LIST:  "+str(ip)+"\n"#formatting
        bytes(res, "UTF-8")#convert it
        sock.send(res.encode())#and encode its
        

def input_nickname(l,s):#TODO
    print("a")


while(1):
    (readable_socket, a,b) = select.select(socket_list, [],[])  #Work like a crossroad
    for i in readable_socket:   #for each socket on the list
        if i == s:  #if the socket is the listening one
            (con,addr)=i.accept()
            socket_list.append(con)
            notify_on_join(socket_list,addr)
        else:   #else we get the data
            data = i.recv(1500)
            #print("socket:",i,"xxxx")
            if not data or data == '\n':    #if the data formatting is like nothing, or user closed the service
                socket_list.remove(i)   #remove the socket from the list
                i.close()   #close the socket
                notify_on_leave(socket_list,addr)   #notify each user on the IRC
                
            if not decode_and_compare(data, socket_list, i):    #if the function return false, then there s no 'cmd'
                print(data.decode())    #just debug to see the message on the interpreter
                cast_msg_to_everyone(socket_list,data)  #send the message to everyone
 
