"""
author: Alexey Aleshchenok
date: 2024-01-05
HTTP SERVER
"""
import socket

QUEUE_SIZE = 10
IP = '0.0.0.0'
PORT = 80
SOCKET_TIMEOUT = 2
DEFAULT_URL = '/html/index.html'
MOVED_LOCATION = '/index.html'
ROOT_WEB = 'C:/Users/User/PycharmProjects/HTTP_server/ROOT-WEB'
BAD_REQUEST = b'HTTP/1.1 400 Bad Request\n\n<h1>400 Bad Request</h1>'
NOT_FOUND = b'HTTP/1.1 404 Not Found\n\n<h1>404 Not Found</h1>'
OK = 'HTTP/1.1 200 OK\r\nContent-Type: '


def get_file_data(file_name):
    """
    Get data from file
    :param file_name: the name of the file
    :return: data from file in a string
    """
    try:
        with open(file_name, 'rb') as file:
            return file.read()
    except FileNotFoundError:
        return b''


def handle_client_request(resource, client_socket):
    """
    Check the required resource, generate proper HTTP response and send
    to client
    :param resource: the required resource
    :param client_socket: a socket for the communication with the client
    :return: None
    """
    """ """
    if resource == b'/':
        url = DEFAULT_URL
    else:
        url = resource.decode()

    if url == '/moved':
        http_response = f'HTTP/1.1 302 Moved Temporarily\n\nLocation: {MOVED_LOCATION}\r\n'.encode()
        client_socket.send(http_response)
        return
    if url == '/forbidden':
        http_response = b'HTTP/1.1 403 Forbidden\n\n<h1>403 Forbidden</h1>'
        client_socket.send(http_response)
        return
    if url == '/error':
        http_response = b"HTTP/1.1 500 Internal Server Error\n\n<h1>500 Internal Server Error</h1>"
        client_socket.send(http_response)
        return

    file_type = url.split('/')[1]
    if file_type == 'html':
        http_header = OK + 'text/html;charset=utf-8\r\nContent-Length: '
        url = '/' + url.split('/')[2]
    elif file_type == 'css':
        http_header = OK + 'text/css\r\nContent-Length: '
    elif file_type == 'js':
        http_header = OK + 'text/javascript; charset=UTF-8\r\nContent-Length: '
    elif file_type == 'txt':
        http_header = OK + 'text/plain\r\nContent-Length: '
    elif file_type == 'imgs':
        img_type = url.split('/')[2].split('.')[1]
        if img_type == 'ico':
            http_header = OK + 'image/x-icon\r\nContent-Length: '
        elif img_type == 'gif':
            http_header = OK + 'image/jpeg\r\nContent-Length: '
        elif img_type == 'png':
            http_header = OK + 'image/png\r\nContent-Length: '
        elif img_type == 'jpg':
            http_header = OK + 'image/jpeg\r\nContent-Length: '
        else:
            client_socket.sendall(NOT_FOUND)
            return
    else:
        client_socket.send(NOT_FOUND)
        return

    filename = ROOT_WEB + url
    data = get_file_data(filename)
    if data == b'':
        client_socket.sendall(NOT_FOUND)
    else:
        http_header += str(len(data))
        client_socket.sendall(http_header.encode() + b'\n\n' + data)


def validate_http_request(request):
    """
    Check if request is a valid HTTP request and returns TRUE / FALSE and
    the requested URL
    :param request: the request which was received from the client
    :return: a tuple of (True/False - the request validation, the requested resource)
    """
    validation = True
    resource = ''
    sorted_request = request.split(b'\r\n')
    if not sorted_request or not sorted_request[0].startswith(b'GET') or not sorted_request[0].endswith(b'HTTP/1.1'):
        validation = False
    else:
        resource = sorted_request[0].split(b' ')[1]

    return validation, resource


def handle_client(client_socket):
    """
    Handles client requests: verifies client's requests are legal HTTP, calls
    function to handle the requests
    :param client_socket: the socket for the communication with the client
    :return: None
    """
    print('Client connected')
    while True:
        try:
            client_request = client_socket.recv(4096)
            if not client_request:
                break
            valid_http, resource = validate_http_request(client_request)
            if valid_http:
                print('Got a valid HTTP request')
                handle_client_request(resource, client_socket)
            else:
                client_socket.sendall(BAD_REQUEST)
                print('Error: Not a valid HTTP request')
                break
        except socket.timeout:
            break
    print('Closing connection')


def main():
    """Main function"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_SIZE)
        print("Listening for connections on port %d" % PORT)
        while True:
            client_socket, client_address = server_socket.accept()
            print(f'New connection with {client_address}')
            try:
                client_socket.settimeout(SOCKET_TIMEOUT)
                handle_client(client_socket)
            except socket.error as err:
                print('Received socket exception - ' + str(err))
            finally:
                client_socket.close()
    except socket.error as err:
        print('Received socket exception - ' + str(err))
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
