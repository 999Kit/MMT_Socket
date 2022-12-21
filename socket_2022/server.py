import socket
import _thread
import server_config

content_type_dict = {
    "html": "text/html",
    "htm": "text/html",
    "txt": "text/plain",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "png": "image/png",
    "css": "text/css",
    "ico": "image/x-icon"
}

def get_filename_content_type(headers):
    filename = headers[0].split()[1]
    if filename == '/':
        filename = '/index.html'

    if '.' in filename:
        file_type = filename.split('.')[1]
    else:
        file_type = ""
    if file_type not in content_type_dict:
        content_type = "application/octet-stream"
    else:
        content_type = content_type_dict[file_type]
    return filename, content_type


def check_login(request, client_socket):
    if "uname=admin&psw=123456" not in request:
        response = "HTTP/1.1 401 Unauthorized\r\nConnection: close\r\n\r\n" \
                   "<!DOCTYPE html><h1>401 Unauthorized</h1><p>This is a private area.</p>"
        client_socket.send(response.encode())
        return False
    return True

def handle_client(client_socket, client_address):
    print(f"\n[NEW CONNECTION] {client_address} connected.")

    while True:
        request = ""
        client_socket.settimeout(5)
        try:
            request = client_socket.recv(server_config.BUFFERSIZE).decode()
        except socket.timeout:
            print("\n[REQUEST TIMEOUT]")
            header = "HTTP/1.1 408 Request Time-out\r\nConnection: close\r\n\r\n"
            client_socket.send(header.encode())
            break

        if not request:
            break

        if "POST" in request:
            if not check_login(request, client_socket):
                break

        headers = request.split('\n')
        # print(f"[HTTP REQUEST]\n{headers[0]}")
        print(f"{client_address} {headers[0]}")

        filename, content_type = get_filename_content_type(headers)
        # Return 404 when file does not exist

        try:
            with open("." + filename, 'rb') as f:
                content = f.read()
            header = """HTTP/1.1 200 OK\r\nContent-Type: %s\r\nContent-Length: %s\r\n\r\n""" % \
                     (content_type, len(content))
            client_socket.sendall(header.encode() + content)
        except FileNotFoundError:
            response = "HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\nFile Not Found"
            client_socket.sendall(response.encode())
            break

    client_socket.close()
    print(f"\n{client_address} closed.")


def accept_incoming_connections(server_socket):
    """Sets up handling for incoming clients."""

    while True:
        client_socket, client_address = server_socket.accept()
        _thread.start_new_thread(handle_client, (client_socket, client_address))

def start(server_socket):
    print(f"[LISTENING] {socket.gethostbyname(socket.gethostname()), server_config.PORT} is listening")
    server_socket.listen(50)
    accept_incoming_connections(server_socket)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(server_config.ADDR)

start(server_socket)