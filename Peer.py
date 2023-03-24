from socket import *
import os
import threading
import sys
import time
import platform



class ActivePeer:
    def __init__(self, hostname='None', upload_port='None'):
        self.hostname = hostname
        self.upload_port = upload_port

    def __str__(self):
        return 'Hostname is ' + str(self.hostname) + ' upload port is :' + str(self.upload_port)

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.hostname == other.hostname and self.upload_port == other.upload_port
        return False


class RFC:
    def __init__(self, rfc_number='None', rfc_title='None'):
        self.rfc_number = rfc_number
        self.rfc_title = rfc_title
        self.rfc_active_peer = ActivePeer()

    def __str__(self):
        return 'RFC ' + str(self.rfc_number) + ' ' + str(self.rfc_title) + ' ' + str(
            self.rfc_active_peer.hostname) + ' ' + str(self.rfc_active_peer.upload_port)

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.rfc_number == other.rfc_number and self.rfc_title == other.rfc_title and self.rfc_active_peer == other.rfc_active_peer
        return False


def peer_download(peer_socket, rfc_number, hostname):
    if rfc_number is not None:
        message = 'GET RFC ' + rfc_number + ' P2P-CI/1.0\nHost: ' + str(
            hostname) + '\nOS: ' + platform.system() + ' ' + platform.release()
    message=message.encode()
    peer_socket.send(message)
    data = peer_socket.recv(1024)
    print(data.decode())
    data = peer_socket.recv(1024)
    file = "RFC" + rfc_number + ".txt"
    f = open(file, "w+")
    while data:
        f.write(data.decode())
        data = peer_socket.recv(1024)
    f.close()
    peer_socket.close()
    print('Enter your choice')

    return 0


def peer_server():
    peer_socket = socket(AF_INET, SOCK_STREAM)
    peer_ip = ''
    peer_port = int(upload_port)
    try:
        peer_socket.bind((peer_ip, peer_port))
    except error as message:
        print()
        'Binding of socket to given ip, port failed. Error Code: ' + str(message[0]) + ' Message ' + str(message[1])
        sys.exit()
    try:
        while True:
            peer_socket.listen(3)
            (conn, socket_info) = peer_socket.accept()
            print('\nConnection initialized on port : ', socket_info[1])
            peer_thread = threading.Thread(target=peer_thread_fact, args=(conn,))
            peer_thread.start()
        peer_socket.close()
    except KeyboardInterrupt:
        peer_socket.close()
        sys.exit(0)


def peer_thread_fact(peer_socket):
    resp = peer_socket.recv(1024)
    resp = resp.decode()
    arr = resp.split(' ')
    file = 'RFC' + arr[2] + '.txt'
    cwd = os.getcwd()
    files = os.listdir(cwd)
    if file in files:
        print('file found')
        last_modified = time.strftime("%a, %d %b %Y %H:%M:%S ", time.gmtime(os.path.getmtime(file))) + 'GMT\n'
        OS = platform.system() + ' ' + platform.release()
        curr_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime()) + 'GMT\n'
        file_size = os.path.getsize(file)
        message = 'P2P-CI/1.0 200 OK\nDate: ' + str(curr_time) + 'OS: ' + str(OS) + '\nLast-Modified: ' + str(
            last_modified) + 'Content-Length: ' + str(file_size) + '\nContent-Type: text/text\n'
        print(message)
        message = message.encode()
        peer_socket.send(message)
        file_handler = open(file, "r")
        data = file_handler.read(1024)
        while data:
            peer_socket.send(data.encode())
            data = file_handler.read(1024)
        file_handler.close()
    peer_socket.close()
    print("Peer connection closed")
    sys.exit(0)


def ADD_RFC(clientsoc, rfc_number=None, rfc_title=None):
    global hostname
    hostname = gethostname()
    hostname = (gethostbyname(hostname))
    if rfc_title is None:
        rfc_number = input('Enter the RFC number: ')
        rfc_title = input('Enter the RFC title : ')
    message = 'ADD RFC ' + str(rfc_number) + ' P2P-CI/1.0\nHOST: ' + str(hostname) + '\nPort: ' + str(
        upload_port) + '\nTitle: ' + str(rfc_title)
    transmit(message, clientsoc)


def LIST_RFC(clientsoc):
    global hostname
    hostname = gethostname()
    hostname = (gethostbyname(hostname))
    message = 'LIST ALL P2P-CI/1.0\nHOST: ' + str(hostname) + '\nPort: ' + str(upload_port) + '\n'
    transmit(message, clientsoc)


def LOOKUP_RFC(clientsoc):
    global hostname
    hostname = gethostname()
    hostname = (gethostbyname(hostname))
    rfc_number = input('Enter the RFC number: ')
    rfc_title = input('Enter the RFC title: ')
    message = 'LOOKUP RFC ' + str(rfc_number) + ' P2P-CI/1.0\nHost: ' + str(hostname) + '\nPort: ' + str(
        upload_port) + '\nTitle: ' + str(rfc_title)
    transmit(message, clientsoc)


def PEER_DELETE(clientsoc):
    global hostname
    hostname = gethostname()
    hostname = (gethostbyname(hostname))
    message = 'DEL PEER P2P-CI/1.0\nHOST: ' + str(hostname) + '\nPort: ' + str(upload_port)
    transmit(message, clientsoc)


def transmit(message, clientsoc):
    clientsoc.send(message.encode())
    resp = clientsoc.recv(1024)
    resp = resp.decode()
    i = 0
    print('\nResponse is\n' + str(resp))


def MENU():
    print('*_*_*_*_*Enter number of respective option below*_*_*_*_*')
    print('1. Add RFC')
    print('2. List RFCs')
    print('3. Lookup RFC')
    print('4. Download RFC')
    print('5. Exit')
    return input('Enter your option:')


def connect_server():
    global serverip
    serverport = 7734
    serverip = input('Enter the server IP: ')
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((serverip, serverport))
    while True:
        inp = MENU()
        if inp == '1':
            ADD_RFC(client_socket)
        elif inp == '2':
            LIST_RFC(client_socket)
        elif inp == '3':
            LOOKUP_RFC(client_socket)
        elif inp == '4':
            peer_IP = input('Enter IP of peer server: ')
            peer_port = input('Enter upload port of peer: ')
            rfc_num = input('Enter RFC Number: ')
            peer_socket = socket(AF_INET, SOCK_STREAM)
            peer_socket.connect((peer_IP, int(peer_port)))
            peer_download(peer_socket, rfc_num, peer_IP)
        elif inp == '5':
            PEER_DELETE(client_socket)
            break
        else:
            print('Invalid Input')



def main():
    global upload_port
    upload_port = input('Enter the upload port on which we will be listening as peer: ')
    try:
        thread_peer_server = threading.Thread(name='thread_peer_server', target=peer_server)
        thread_peer_server.Daemon = True
        thread_peer_server.start()
        thread_connect_server = threading.Thread(name='thread_connect_server', target=connect_server)
        thread_connect_server.Daemon = True
        thread_connect_server.start()
        thread_connect_server.join()
        thread_peer_server.join()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    main()
