"""
author: Alexey Aleshchenok
date: 2024-01-23
HTTP SERVER
"""
import socket

QUEUE_SIZE = 10
IP = '0.0.0.0'
PORT = 80
SOCKET_TIMEOUT = 2
DEFAULT_URL = '/index.html'
ROOT_WEB = 'C:/Users/User/PycharmProjects/HTTP_server/ROOT-WEB'
HEADER_END = '\r\n\r\n'
REQUEST_TYPE = {b'GET ': 'get', b'POST': 'post'}
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
GET_INTERFACES = ('/calculate-next', '/calculate-area', '/image')
POST_INTERFACE = '/upload'
UPLOAD_FOLDER = '/uploads'


def receive(client_socket):
    """
    Receive client's requests
    :param client_socket: a socket for the communication with the client
    :return: data received from client socket
    """
    data = b''
    while True:
        chunk = client_socket.recv(1024)
        if not chunk:
            break
        data += chunk
        if len(chunk) < 1024:
            break
    return data


def get_file_data(file_name):
    """
    Get data from file
    :param file_name: the name of the file
    :return: data from file
    """
    try:
        with open(file_name, 'rb') as file:
            return file.read()
    except FileNotFoundError:
        return b''


def upload_file(file_name, file_data):
    """
    Upload client's image to 'uploads' folder
    :param file_name: name of client's file
    :param file_data: image's data in bytes
    :return: None
    """
    file_path = ROOT_WEB + UPLOAD_FOLDER + '/' + file_name
    with open(file_path, 'wb') as file:
        file.write(file_data)


def calculate_next(num):
    """
    Return next number in row
    :param num: number received from client
    :return: next number in row
    """
    try:
        num = str(int(num) + 1)
    except ValueError:
        num = ''
    return num


def calculate_area(height, width):
    """
    Calculate triangle's area
    :param height: value received from client
    :param width: value received from client
    :return: area of triangle with given height and width
    """
    try:
        area = str(int(height) * int(width) / 2)
    except ValueError:
        area = ''
    return area


def handle_client_get_request(resource, client_socket):
    """
    Check the required GET request, generate proper HTTP response and send
    to client
    :param resource: the required resource
    :param client_socket: a socket for the communication with the client
    :return: None
    """
    folder = '/'
    if resource == '/' or '':
        url = DEFAULT_URL
    elif '?' in resource:
        gets_interfaces(resource, client_socket)
        return
    elif resource == '/index.html':
        url = resource.split('/')[-1]
    else:
        folder += resource.split('/')[1] + '/'
        url = resource.split('/')[-1]

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
        client_socket.sendall(http_header.encode() + HEADER_END.encode() + data)


def post_interface(resource, file_data, client_socket):
    """
    Check the required POST request ,generate proper HTTP response and send to client
    Use upload_file function
    :param resource: request url
    :param file_data: image's data in bytes
    :param client_socket: a socket for the communication with the client
    :return: None
    """
    if resource == '':
        client_socket.sendall(BAD_REQUEST)
        return

    function = resource.split('?')[0]
    parameters = resource.split('?')[1]
    if function not in POST_INTERFACE:
        client_socket.sendall(NOT_FOUND)
        return

    if function == POST_INTERFACE:
        if not parameters.startswith('file-name='):
            client_socket.sendall(BAD_REQUEST)
            return
        if file_data == '':
            client_socket.sendall(BAD_REQUEST)
            return
        file_name = parameters.split('=')[1]
        if file_name == '':
            client_socket.sendall(BAD_REQUEST)
            return
        upload_file(file_name, file_data)

    response = OK[:15] + HEADER_END
    client_socket.sendall(response.encode())


def gets_interfaces(resource, client_socket):
    """
    Check the required GET request with parameters,generate proper HTTP response and send to client
    Use calculate_next, calculate_area and get_file_data functions
    :param resource: request url
    :param client_socket: a socket for the communication with the client
    :return:
    """
    function = resource.split('?')[0]
    parameters = resource.split('?')[1]
    data = ''
    if function not in GET_INTERFACES:
        client_socket.sendall(NOT_FOUND)
        return

    if function == GET_INTERFACES[0]:
        if not parameters.startswith('num='):
            client_socket.sendall(BAD_REQUEST)
            return
        data = calculate_next(parameters.split('=')[1]).encode()
        if data == '':
            client_socket.sendall(BAD_REQUEST)
            return

    if function == GET_INTERFACES[1]:
        parameters = parameters.split('&')
        try:
            if not parameters[0].startswith('height=') and not parameters[1].startswith('width='):
                client_socket.sendall(BAD_REQUEST)
                return
            data = calculate_area(parameters[0].split('=')[1], parameters[1].split('=')[1]).encode()
            if data == '':
                client_socket.sendall(BAD_REQUEST)
                return
        except IndexError:
            client_socket.sendall(BAD_REQUEST)

    if function == GET_INTERFACES[2]:
        if not parameters.startswith('image-name='):
            client_socket.sendall(BAD_REQUEST)
            return
        image_name = parameters.split('=')[1]
        if image_name == '':
            client_socket.sendall(BAD_REQUEST)
            return
        image_path = ROOT_WEB + UPLOAD_FOLDER + '/' + image_name
        data = get_file_data(image_path)
        if data == b'':
            client_socket.sendall(NOT_FOUND)
            return

    response = OK + FILE_TYPE['txt'] + str(len(data)) + HEADER_END
    client_socket.sendall(response.encode() + data)


def validate_http_request(request):
    """
    Check if request is a valid HTTP request and returns its type and
    the requested URL
    :param request: the request which was received from the client
    :return: the request validation (type of request) and the requested resource
    """
    resource = ''
    sorted_request = request.split(b'\r\n')
    if not sorted_request or not sorted_request[0][:4] in REQUEST_TYPE or not sorted_request[0].endswith(b'HTTP/1.1'):
        validation = ''
    else:
        validation = REQUEST_TYPE[sorted_request[0][:4]]
        try:
            resource = sorted_request[0].split(b' ')[1].decode()
        except IndexError:
            resource = ''

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
            client_request = receive(client_socket)
            if client_request != b'':
                valid_http, resource = validate_http_request(client_request)
                if valid_http == 'get':
                    print('Got a valid HTTP GET request')
                    handle_client_get_request(resource, client_socket)
                elif valid_http == 'post':
                    print('Got a valid HTTP POST request')
                    file_data = receive(client_socket)
                    post_interface(resource, file_data, client_socket)
                else:
                    client_socket.sendall(BAD_REQUEST)
                    print('Error: Not a valid HTTP request')
                    break
            else:
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
