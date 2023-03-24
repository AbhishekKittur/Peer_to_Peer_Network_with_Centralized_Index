from socket import *
import sys
import threading

active_peers = []
active_RFCs = []
hostname = '192.168.1.196'
port = 7734


def main():

    server_socket = socket(AF_INET, SOCK_STREAM)
    try:
        server_socket.bind((hostname, port))
    except error as message:
        print('Binding to local address unsuccessful. Error Code: ' + str(message[0]) + ' Message ' + str(message[1]))
        sys.exit()
    try:
        while True:
            server_socket.listen(50)
            (conn, socket_info) = server_socket.accept()
            print("Connection formed with " + str(socket_info) )
            # Spawning thread for each connection
            server_thread = threading.Thread(target=peer_thread_fact, args=(conn,))
            server_thread.start()
    except KeyboardInterrupt:
        server_socket.close()
        sys.exit(0)


class ACTIVEPEER:
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
    def __init__(self, rfc_number='None', rfc_title='None', active_peer=ACTIVEPEER()):
        self.rfc_number = rfc_number
        self.rfc_title = rfc_title
        self.rfc_active_peer = active_peer

    def __str__(self):
        return 'RFC ' + str(self.rfc_number) + ' ' + str(self.rfc_title) + ' ' + str(
            self.rfc_active_peer.hostname) + ' ' + str(self.rfc_active_peer.upload_port)

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.rfc_number == other.rfc_number and self.rfc_title == other.rfc_title and self.rfc_active_peer == other.rfc_active_peer
        return False


def peer_thread_fact(peer_socket):
    try:
        while True:
            response = peer_socket.recv(1024)
            response = response.decode()
            print(response)
            if len(response) == 0:
                peer_socket.close()
                return
            i = 0

            arr = response.split(' ')
            action = arr[0]
            if action == 'ADD':
                ADD_RFC(response, peer_socket)
            elif action == 'LOOKUP':
                LOOKUP_RFC(response, peer_socket)
            elif action == 'LIST':
                LIST_RFC(peer_socket)
            elif action == 'DEL':
                Delete_Peer(response, peer_socket)
    except KeyboardInterrupt:
        peer_socket.close()
        sys.exit(0)


def ADD_RFC(response, peer_socket):
    arr = response.split(' ');
    rfc_number = arr[2]
    hostname = arr[4]
    hostname_str = hostname.split('\n')
    hostname = hostname_str[0]
    upload_port = arr[5]
    upload_port_str = upload_port.split('\n')
    upload_port = upload_port_str[0];
    title = arr[6]

    peer = ACTIVEPEER(hostname, upload_port)
    if peer not in active_peers:
        active_peers.append(peer)
    rfc = RFC(rfc_number, title, peer)
    if rfc not in active_RFCs:
        active_RFCs.append(rfc)
    message = 'P2P-CI/1.0 200 OK\n' + 'RFC ' + str(rfc_number) + ' ' + str(title) + ' ' + str(hostname) + ' ' + str(
        upload_port)

    message=message.encode()
    peer_socket.send(message)


def LOOKUP_RFC(response, peer_socket):
    arr = response.split(' ');
    rfc_number = arr[2]
    title = arr[6]
    count = 0
    message = 'P2P-CI/1.0 404 NOT FOUND'
    if len(active_RFCs) > 0:

        for active_RFC in active_RFCs:
            if active_RFC.rfc_number == rfc_number and active_RFC.rfc_title == title:
                message = 'P2P-CI/1.0 200 OK\n'
                message += 'RFC ' + str(active_RFC.rfc_number) + ' ' + str(active_RFC.rfc_title) + ' ' + str(
                    active_RFC.rfc_active_peer.hostname) + ' ' + str(active_RFC.rfc_active_peer.upload_port)
                count += 1

    message=message.encode()
    peer_socket.send(message)


def LIST_RFC(peer_socket):
    message = 'P2P-CI/1.0 404 NOT FOUND'
    if len(active_RFCs) > 0:
        count = 0
        message = 'P2P-CI/1.0 200 OK \n'
        for active_RFC in active_RFCs:
            message += str(active_RFC) + '\n'
            count += 1

    message=message.encode()
    peer_socket.send(message)


def Delete_Peer(response, peer_socket):
    arr = response.split(' ');
    hostname = arr[3]
    hostname_str = hostname.split('\n')
    hostname= hostname_str[0]
    upload_port = arr[4]
    global active_peers
    global active_RFCs
    copy_active_RFCS = []
    hostnameStr = hostname.split('/n')
    for active_RFC in active_RFCs:
        if active_RFC.rfc_active_peer.hostname == hostnameStr[0] and active_RFC.rfc_active_peer.upload_port == upload_port:
            continue
        else:
            copy_active_RFCS.append(active_RFC)
    active_RFCs[:] = copy_active_RFCS
    copy_active_peers = []
    for active_peer in active_peers:
        if active_peer.hostname == hostnameStr[0] and active_peer.upload_port == upload_port:
            continue
        else:
            copy_active_peers.append(active_peer)
    active_peers[:] = copy_active_peers

    message = 'P2P-CI/1.0 200 OK \n'
    message = message.encode()
    peer_socket.send(message)
    print(active_peers)


if __name__ == '__main__':
    main()
