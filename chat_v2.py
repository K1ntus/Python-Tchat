import socket
import select
import threading

#JOIN, PART, NICK, LIST, KILL fonctionnels
#les channels presque bons

s = socket.socket(family=socket.AF_INET6, type=socket.SOCK_STREAM, proto=0, fileno=None)    #define the socket, putting it IPv6, TCP, etc

s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)  #bypass some -security- like port already used
s.bind(('',7777))   #bind the socket to the port 7777

s.listen(1)         #put the socket on listen mode

socket_list=[s]     #init the socket list with the listening one
(ip,a,b,c) = s.getsockname()


nick_dictionnary={ip:"server"}
channel_list = ["world"]
channel_dictionnary = {ip:["world"]}

#print(nick_dictionnary)

def get_nick_for_socket(nick_dico, socket):
    try:
        (ip,a,b,c) = socket.getsockname()
        res = nick_dictionnary[ip]
    except KeyError:    #if user doesnt have any nick
        res = ip
    return res

def set_nick_for_socket(nick_dico, socket, nick):
    (ip,a,b,c) = socket.getsockname()
    nick_dico[ip]=nick
    return True
    
    

def cast_msg_to_everyone(l,data,socket):
    nick = get_nick_for_socket(nick_dictionnary,socket) #we get the nick to print as msg
    for j in l:   #On parcours toutes les sockets SAUF la socket d'écoute
        if not j == s:
            res = nick+"/ "+data.decode()
            j.send(res.encode())

def cast_to_everyone(l,data):   #like system msg, so no real users but we could use cast_msg_to_everyone with the nick of the listen socket (which his nick equals to "server")
    for j in l:   #On parcours toutes les sockets SAUF la socket d'écoute
        try:
            if not j == s:
                j.send(data)
        except BrokenPipeError:
            print("broken pipe error! ")


def notify_on_join(l,name):         #notify every current user when someone connect
    (ip,a,b,c) = name               #get the data from the socket, but only the first parameters, the ip is interesting us
    res = "JOIN:"+" "+str(ip)+"\n"  #We arrange the string to display  
    bytes(res, "UTF-8")             #We convert the string to bytes
    cast_to_everyone(l,res.encode())#we encode it


def notify_on_leave(l,name):        #same but on leave
    (ip,a,b,c) = name               #get the data from the socket, but only the first parameters, the ip is interesting us
    res = "PART:"+" "+str(ip)+"\n"
    bytes(res, "UTF-8")
    cast_to_everyone(l,res.encode())



def get_prefix_from_data(data): #get the prefix (ie the first word) when a client send a message
    res = ""
    i=0
    while not (data[i] == " " or data[i] == "\n"or data == b''):
        res=res+data[i]
        i=i+1
    return res

def get_suffix_from_data(data): #get the suffix (ie the second word) when a client send a message
    i=0
    data = data.decode()
    res = ""
    prefix =""
    
    while not (data[i] == " " or data[i] == "\n"or data == b''):
        prefix=prefix+data[i]
        i=i+1

    i=i+1
    while not (data[i] == " " or data[i] == "\n"or data == b''):
        res = res+data[i]
        i=i+1
    return res


def leave_channel(socket,channel_to_leave):
    (ip,a,b,c) = socket.getsockname()
    print(ip + "left the channel " + channel_to_leave)
    try:
        channel_dictionnary[ip].remove(channel_to_leave)
        res = "vous avez quitté le channel " + str(channel_to_leave) +"\n"
        socket.send(res.encode())
    except ValueError:
        print("you are not on this channel")

def join_channel(socket, channel_to_join):
    (ip,a,b,c) = socket.getsockname()
    nick = get_nick_for_socket(nick_dictionnary,socket) #we get the nick to print as msg
    #print(ip + "joined the channel " + channel_to_join)

    #print("before:",channel_dictionnary)
    try:
        for i in channel_dictionnary[ip]:#not allow to join multiple time the same channel
            if str(channel_to_join) == i:
                return False
        channel_dictionnary[ip].append(str(channel_to_join))
        res = "vous avez rejoins le channel " + str(channel_to_join) +"\n"
        socket.send(res.encode())
    except KeyError:
        channel_dictionnary.update({ip:["world"]})
        channel_dictionnary[ip].append(str(channel_to_join))
        res = "vous avez rejoins le channel " + str(channel_to_join) +"\n"
        socket.send(res.encode())
            

    
def remove_suffix(data):
    i=0
    while not (data[i] == " " or data[i] == "\n"or data == b''):
        data.replace(data[i], "",1)
        i=i+1
    if data[i] == " ":
        data.replace(" ", "",1)
    return data

def speak_on_channel(socket, channel_name_and_data,socket_list):
    channel_name_and_data=channel_name_and_data.decode()
    channel_name_and_data = remove_suffix(channel_name_and_data)
    print("chan name+data: "+channel_name_and_data)
    channel_name = get_prefix_from_data(channel_name_and_data)
    channel_name_and_data = remove_suffix(channel_name_and_data)
    channel_name = get_prefix_from_data(channel_name_and_data)
    print("channel_name: "+channel_name)
    msg_data = remove_suffix(channel_name_and_data)
    print("message data: "+msg_data)
    print("channel_name > "+msg_data)
    broadcast_on_channel(msg_data, channel_name, socket_list)

def get_channel_from_name(channel_name):
    print("a")

#channel_dictionnary
def broadcast_on_channel(msg, channel, socket_list):
    for i in channel_dictionnary:                           #all the ip of connected sockets to the server (directly connected to a 'main' channel on first join
        for j in channel_dictionnary[i]:                    #Every channels used by this ip
            if j == channel:                                #if the ip is connected to this channel
                for h in socket_list:                       #we search the socket of this ip
                    (sockaddr,port,a,b) = h.getsockname()   #we get information from the h socket
                    if sockaddr == i:                       #if the socket ip is the same than the one find
                        h.send(msg.encode())                #then we send the msg
                

    
def decode_and_compare(data,l,sock):
    string = get_prefix_from_data(data.decode())    #We get the first word

    
    if string == "NICK":         #if its equal to NICK, redirect to the good function
        set_nick_for_socket(nick_dictionnary, sock, get_suffix_from_data(data))
        return True
    
    if string == "LIST":        #if the first word is LIST then print a list of all users and the ip
        list_users(l,sock)
        return True
    
    if string == "KILL":        #if the first word is kill, we close the connection linked to the ip in parameters
        command_kill(get_suffix_from_data(data),l)
        return True
    
    if string == "KICK":        #no channel has been made so actually useless and TODO
        print("kick")
        return True
    
    if string == "MSG":         #Same
        print("sending msg")
        speak_on_channel(sock, data,l)
        return True

    if string == "JOIN":
        print("join")
        join_channel(sock, get_suffix_from_data(data))
        return True
    if string == "PART":
        print("part")
        leave_channel(sock, get_suffix_from_data(data))
        return True
    
    #print("no special cmd, just sending usual msg")
    return False


def command_kill(ip_to_kill, socket_list):
    print("command kill asked")
    
    bytes(ip_to_kill, "UTF-8")
    for i in socket_list:   #On parcours toutes les sockets SAUF la socket d'écoute
        (sockaddr,port,a,b) = i.getsockname()   #we get information from the i socket
        if(sockaddr == ip_to_kill):             #we compare the ip from the i socket with the one to kill
            print("ip:",sockaddr,"get killed")
            delete_nick(nick_dictionnary, i)
            socket_list.remove(i)   #remove the socket from the list
            i.close()
            notify_on_leave(socket_list,addr)
            return
    print("No socket linked with this ip")  #if no socket has been found with this ip

        
        

            
def list_users(l,sock):#list of socket except listen, and socket asking for the list of members
    for j in range(1,len(l),1):             #On parcours toutes les sockets SAUF la socket d'écoute
        (ip,port,a,b)=l[j].getsockname()    #we get information about the socket at position j
        res = ("LIST:  "+str(ip)+" -> "+str(get_nick_for_socket(nick_dictionnary, l[j]))+" \n")#formatting
        bytes(res, "UTF-8")                 #convert it to bytes
        sock.send(res.encode())             #send the encoded string to the socket
        


def delete_nick(nick_dico,socket):
    try:
        (ip,a,b,c) = socket.getsockname()
        nick_dico[ip] = "Guest"
    except:
        print("got an error while deleting a nick")
        pass

def remove_socket(socket_list,socket):
    delete_nick(nick_dictionnary, socket)
    socket_list.remove(socket)          #remove the socket from the list
    socket.close()                      #close the socket
    notify_on_leave(socket_list,addr)   #notify each user on the IRC



while(1):
    (readable_socket, a,b) = select.select(socket_list, [],[])  #Work like a crossroad
    for i in readable_socket:   #for each socket on the list
        
        if i == s:  #if the socket is the listening one
            (con,addr)=i.accept()               #we get the information (ie. socket and address) and accept his connection request
            socket_list.append(con)             #we had the socket to the socket list
            notify_on_join(socket_list,addr)    #message to cast to every user when someone connect to the chat
            (socket_ip,a,b,c)=i.getsockname()

                
        else:   #else we get the data
            data = i.recv(1500) #We receive the data of a length of 1500B
            
            if not data or data == '\n' or data == b'':    #if the data formatting is like nothing, or user closed the service
                j = remove_socket(socket_list,i)
            try:
                if not decode_and_compare(data, socket_list, i):        #if the function return false, then there s no 'cmd'
                    print(data.decode())     
                    cast_msg_to_everyone(socket_list,data,i)  #send the message to everyone                    
            except IndexError:
                eof=True
 
