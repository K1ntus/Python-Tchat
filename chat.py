import socket
import select
import threading

print("Creating socket")
s = socket.socket(family=socket.AF_INET6, type=socket.SOCK_STREAM, proto=0, fileno=None)

port_to_use = 7777
print("Binding socket to port: "+str(port_to_use))
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
s.bind(('',port_to_use))

print("Put the socket on listening mode")
s.listen(1)

print("Creation of variables to manage the chat")
socket_list = dict()
socket_list={'server':s}
socket_nickname={'server':s}
channel_list=[]
member_list=[]
print("\n...\n")

def convert_dico_to_array(dico):
    res=[]
    for i in dico:
        res.append(dico[i])
    return res
def remove_socket_from_dict(dico,value_to_remove):
    dico = {key: value for key, value in dico.items() 
        if value is not value_to_remove}
    return dico
    

def cast_msg_to_everyone(l,data):
    tab=convert_dico_to_array(l)
    for j in range(1,len(tab),1):   #On parcours toutes les sockets SAUF la socket d'écoute
        #print(tab[j])
        #res = str(s)+">"+data.decode()
        if not tab[j] == s:
            res = ">"+" "+data.decode()
            tab[j].send(res.encode())

def cast_to_everyone(l,data):
    tab=convert_dico_to_array(l)
    for j in range(1,len(tab),1):   #On parcours toutes les sockets SAUF la socket d'écoute
        try:
            if not tab[j] == s:
                tab[j].send(data)
        except BrokenPipeError:
            print("broken pipe error! ")
            print(tab[j])
            return


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
        #input_nickname(data,l,sock)
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
    

def list_users(l,sock):#list of socket except listen, and socket asking for the list of members
    tab = convert_dico_to_array(l)
    for j in range(1,len(tab),1):   #On parcours toutes les sockets SAUF la socket d'écoute
        (ip,port,a,b)=tab[j].getsockname()
        res = "LIST:  "+str(ip)+"\n"
        bytes(res, "UTF-8")
        sock.send(res.encode())

def command_kill(ip_to_kill, socket_list):
    print("command kill asked")
    
    tab=convert_dico_to_array(socket_list)
    bytes(ip_to_kill, "UTF-8")
    for i in range(0,len(tab),1):   #On parcours toutes les sockets SAUF la socket d'écoute
        

        print(tab[i].getsockname())
        (sockaddr,port,a,b) = tab[i].getsockname()
        print(sockaddr)
        #print("i:",tab)
        #print("i[0]:",tab[i])
        #print("ip to kill:",ip_to_kill)
        if(sockaddr == ip_to_kill):
            print("j'ai trouve l'ip")
            print("socket:",tab[i],"get killed")
            remove_socket_from_dict(socket_list,tab[i])
            tab[i].close()
            #notify_on_leave(socket_list,tab[i])

def input_nickname(data,l,sock):
    tab = convert_dico_to_array(l)
    new_name = get_suffix_from_data(data)
    print(new_name)
    print(l[1])
    print(sock)

print("Socket is ready to use\n")
while(1):
    (readable_socket, a,b) = select.select(convert_dico_to_array(socket_list), [],[])
    for i in readable_socket:
        if i == s:
            (con,addr)=i.accept()
            socket_list[str(addr)]=con
            notify_on_join(socket_list,addr)
        else:
            data = i.recv(1500)
            #print("socket:",i,"xxxx")
            print(readable_socket)

            if not data or data == '\n' or data == b'':
                remove_socket_from_dict(socket_list,i)
                i.close()
                notify_on_leave(socket_list,addr)
                
            if not decode_and_compare(data, socket_list, i):
                print(data.decode())
                cast_msg_to_everyone(socket_list,data)
                #cast_msg_to_everyone(socket_list,data,i)
 
