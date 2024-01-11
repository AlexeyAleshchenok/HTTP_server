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
DEFAULT_URL = '/index.html'
ROOT_WEB = 'C:/Users/User/PycharmProjects/HTTP_server/ROOT-WEB'
BAD_REQUEST = b'HTTP/1.1 400 Bad Request\n\n<h1>400 Bad Request</h1>\r\n\r\n'
NOT_FOUND = b'HTTP/1.1 404 Not Found\n\n<h1>404 Not Found</h1>\r\n\r\n'
OK = 'HTTP/1.1 200 OK\r\nContent-Type: '
SPECIAL_STATUS = {'moved': b'HTTP/1.1 302 Moved Temporarily\r\nLocation: /index.html\r\n\r\n',
                  'forbidden': b'HTTP/1.1 403 Forbidden\r\n\r\n<h1>403 Forbidden</h1>',
                  'error': b'HTTP/1.1 500 Internal Server Error\r\n\r\n<h1>500 Internal Server Error</h1>'}
FILE_TYPE = {'html': 'text/html;charset=utf-8\r\nContent-Length: ',
             'css': 'text/css\r\nContent-Length: ',
             'js': 'text/javascript; charset=UTF-8\r\nContent-Length: ',
             'txt': 'text/plain\r\nContent-Length: '}
IMAGE_TYPE = {'ico': 'image/x-icon\r\nContent-Length: ',
              'gif': 'image/jpeg\r\nContent-Length: ',
              'png': 'image/png\r\nContent-Length: ',
              'jpg': 'image/jpeg\r\nContent-Length: '}


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
    folder = '/'
    if resource == b'/' or b'':
        url = DEFAULT_URL
    elif resource == b'/index.html':
        url = resource.decode().split('/')[-1]
    else:
        folder += resource.decode().split('/')[1] + '/'
        url = resource.decode().split('/')[-1]

    if url in SPECIAL_STATUS:
        client_socket.send(SPECIAL_STATUS[url])
        return

    file_type = url.split('.')[-1]
    if folder == '/imgs/':
        http_header = OK + IMAGE_TYPE[file_type]
    elif file_type in FILE_TYPE:
        http_header = OK + FILE_TYPE[file_type]
    else:
        client_socket.send(NOT_FOUND)
        return

    filename = ROOT_WEB + folder + url
    data = get_file_data(filename)
    if data == b'':
        client_socket.sendall(NOT_FOUND)
    else:
        http_header += str(len(data))
        client_socket.sendall(http_header.encode() + b'\r\n\r\n' + data)


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
        try:
            resource = sorted_request[0].split(b' ')[1]
        except IndexError:
            resource = b''

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
            client_request = b''
            while True:
                client_request += client_socket.recv(1024)
                if client_request.endswith(b'\r\n\r\n') or client_request == b'':
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
