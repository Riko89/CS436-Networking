import socket
import select
import errno
import sys

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 12000
while True:
    my_username = input("Username: ")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    username = my_username.encode()
    username_header = f"{len(username):<{HEADER_LENGTH}}".encode()
    client_socket.send(username_header + username)

    receive = client_socket.recv(1024).decode()
    if receive != ('Welcome to the server ' + username.decode()):
        print(receive)
    else:
        print(receive)
        break
client_socket.setblocking(False)
await_response = False
choice2 = False
chatting = False

while True:
    if await_response is False and choice2 is False and chatting is False:
        print("Enter a choice:\n1. List users\n2. Chat\n3. Exit\n")
        choice = input("Enter your choice: ")
        if choice:
            if len(choice) > 1:
                print("incorrect value")
                continue
            if int(choice) < 1 or int(choice) > 3:
                print("incorrect value ")
                continue
            if int(choice) == 3:
                sys.exit()
            choice = choice.encode()
            choice_header = f"{len(choice):<{HEADER_LENGTH}}".encode()
            client_socket.send(choice_header + choice)
            await_response = True
    elif choice2 is True and await_response is False:
        who = input("Who: ")
        if who:
            who = who.encode()
            who_header = f"{len(who):<{HEADER_LENGTH}}".encode()
            client_socket.send(who_header + who)
            await_response = True

    elif chatting is True:
        message = input(f"{my_username} > ")
        if message == "quit" or message == "Quit":
            await_response = True
            chatting = False
        if message:
            message = message.encode()
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode()
            client_socket.send(message_header + message)

    try:
        while True:
            #receive things
            username_header = client_socket.recv(HEADER_LENGTH)
            if not len(username_header):
                print("connection closed by the server")
                sys.exit()

            username_length = int(username_header.decode())
            username = client_socket.recv(username_length).decode()

            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode())
            message = client_socket.recv(message_length).decode()
            if "Quitting chat" in message:
                chatting = False
            elif "yes/no" in message:
                print(f"{username}: {message}\n")
                yes_no = input("yes/no: ")
                yes_no = yes_no.encode()
                yes_no_header = f"{len(yes_no):<{HEADER_LENGTH}}".encode()
                client_socket.send(yes_no_header + yes_no)
                await_response = True
                yes_no = yes_no.decode()
                if yes_no == 'no' or yes_no == 'No':
                    await_response = False
                    print("no no no")
                    break
                continue
            elif message == 'Please select user to chat with: ':
                print(f"{username} : {message}")
                choice2 = True
                continue
            elif 'Awaiting response from' in message:
                print(f"{username} : {message}")
                choice2 = False
                await_response = True
                continue
            elif message == 'You are now chatting':
                chatting = True
                choice2 = False

            print(f"{username}: {message}")
            await_response = False

    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('read error', str(e))
            sys.exit()
        continue

    except Exception as e:
        print('Error', str(e))
        sys.exit()
