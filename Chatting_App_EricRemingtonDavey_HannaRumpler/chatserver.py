import socket
import select

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 12000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind(('', PORT))

server_socket.listen()

sockets_list = [server_socket]

clients = {}

choice2 = False
server_message = "Server"  # use this to indicate the message is from the server


def receive_message(client_socket):
    try:
        msg_header = client_socket.recv(HEADER_LENGTH)
        if not len(msg_header):
            return False
        msg_length = int(msg_header.decode())
        return {"header": msg_header, "data": client_socket.recv(msg_length)}
    except:
        return False


def check_user_name(user_msg, client, socket_list):
    count = 0
    found = False
    for check in socket_list:
        if count == 0:
            count = 1
            continue
        if user['data'] in client[check]['data']:
            found = True
    return found


def get_users(clients, sockets_list):
    count = 0
    get_list = ''
    for sockets in sockets_list:
        if count == 0:
            count = 1
            continue
        if clients[sockets]['available'] is True:
            available = 'available'
            chatting_with = ''
        else:
            available = 'Unavailable'
            chatting_with = f"Chatting with {clients[sockets]['chatting_with']}"
        get_list += f"\n{clients[sockets]['data'].decode()}, {available}, {chatting_with}"
    return get_list


#takes in notified socket, the socket it wants to chat with and the client list changes their status to busy
def connect_users(notified_socket, found_user, clients):
    clients[notified_socket]['available'] = False
    clients[found_user]['available'] = False
    clients[notified_socket]['chatting_with'] = clients[found_user]['data'].decode()
    clients[found_user]['chatting_with'] = clients[notified_socket]['data'].decode()


#takes in decoded string of sender and string to turn into dict
def send_message(sender, message, sock):
    global HEADER_LENGTH
    sender_header = f"{len(sender):<{HEADER_LENGTH}}".encode()
    sender = sender.encode()
    from_who = {"header": sender_header, "data": sender}
    message_header = f"{len(message):<{HEADER_LENGTH}}".encode()
    message = message.encode()
    msg = {"header": message_header, "data": message}
    sock.send(from_who['header'] + from_who['data'] + msg['header'] + msg['data'])


print("Server is ready to receive connections.")
while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            user = receive_message(client_socket)
            if user is False:
                continue
            if check_user_name(user, clients, sockets_list) is True:
                errMsg = 'Username already in use'
                print("Rejecting Username, already being used")
                client_socket.send(errMsg.encode())
                continue
            welcome_msg = f"Welcome to the server {user['data'].decode()}".encode()
            client_socket.send(welcome_msg)

            sockets_list.append(client_socket)

            clients[client_socket] = user
            clients[client_socket]['available'] = True
            clients[client_socket]['chatting_with'] = False
            print(f"Accepted new connection from {client_address[0]}:{client_address[1]} username:{user['data'].decode()}")
        else:
            message = receive_message(notified_socket)
            if message is False:
                print(f"Closed connection from {clients[notified_socket]['data'].decode()}")
                sockets_list.remove(notified_socket)
                if clients[notified_socket]['available'] is False:
                    # clients[clients[notified_socket]['chatting_with']]['available'] = True
                    skip = 0
                    for client_sockets in sockets_list:
                        if skip == 0:
                            skip = 1
                            continue
                        if clients[client_sockets]['data'].decode() == clients[notified_socket]['chatting_with']:
                            found_socket = client_sockets
                            clients[found_socket]['available'] = True# set the person whom you're chatting with to True
                del clients[notified_socket]
                continue

            user = clients[notified_socket]

            print(f"Received message from {user['data'].decode()}: {message['data'].decode()}")
            if user['available'] is False:
                if message['data'].decode() == 'quit' or message['data'].decode() == 'Quit':
                    #if user enters quit
                    user['available'] = True
                    quit_message = "Quitting chat"
                    skip = 0
                    for client_sockets in sockets_list:
                        if skip == 0:
                            skip = 1
                            continue
                        if clients[client_sockets]['data'].decode() == user['chatting_with']:
                            found_socket = client_sockets
                            clients[found_socket]['available'] = True
                            send_message(server_message, quit_message, found_socket)
                    send_message(server_message, quit_message, notified_socket)
                for client_socket in clients:
                    if client_socket != notified_socket:
                        if clients[client_socket]['chatting_with'] == clients[notified_socket]['data'].decode():
                            client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
            #if choice is 1
            elif int(message['data'].decode()) == 1:
                get_list = get_users(clients, sockets_list)
                send_message(server_message, get_list, notified_socket)
            #if choice is 2
            elif int(message['data'].decode()) == 2:
                server_response = "Please select user to chat with: "
                send_message(server_message, server_response, notified_socket)
                ##now send list of current users
                get_list = get_users(clients, sockets_list)
                send_message(server_message, get_list, notified_socket)
                choice2 = True
                found_user = False
                while choice2 is True:
                    if found_user is False:
                        response = receive_message(notified_socket)
                    else:
                        response = receive_message(found_user)
                    if response is False:
                        print(f"Closed connection from {clients[notified_socket]['data'].decode()}")
                        sockets_list.remove(notified_socket)
                        del clients[notified_socket]
                        choice2 = False
                        found_user = False
                        break
                    else:
                        if found_user:
                            user = clients[found_user]
                            print(f"Asking {user['data'].decode()} if they want to chat with {clients[notified_socket]['data'].decode()}")
                            print(f"Received message from {user['data'].decode()}: {response['data'].decode()}")
                            if response['data'].decode() == 'yes' or response['data'].decode() == 'Yes':
                                message = "You are now chatting"
                                print(f"connecting {user['data'].decode()} with {clients[notified_socket]['data'].decode()}")
                                send_message(server_message, message, notified_socket)
                                send_message(server_message, message, found_user)
                                connect_users(notified_socket, found_user, clients)
                                choice2 = False
                                found_user = False
                                break
                            else:
                                message = f"{clients[found_user]['data'].decode()}, refused your request to chat"
                                send_message(server_message, message, notified_socket)
                                choice2 = False
                                found_user = False
                                break
                        user = clients[notified_socket]
                        print(f"Received message from {user['data'].decode()}: {response['data'].decode()}")
                        skip = 0
                        for users in sockets_list:
                            if skip == 0:
                                skip = 1
                                continue
                            if clients[users] == clients[notified_socket]:
                                continue
                            if response['data'].decode() == clients[users]['data'].decode():
                                found_user = users
                                if clients[users]['available'] is False:
                                    found_user = False
                                break
                        if found_user:
                            query_message = f"{clients[notified_socket]['data'].decode()} would like to chat, accept? yes/no"
                            response_message = f"Awaiting response from {clients[found_user]['data'].decode()}"
                            send_message(server_message, query_message, found_user)
                            send_message(server_message, response_message, notified_socket)
                        else:
                            message = "This person is unavailable to chat with."
                            send_message(server_message, message, notified_socket)

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
