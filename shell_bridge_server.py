import socket
import threading
import time

global bridge_list_index
global bridge_list
bridge_list_index = 0
bridge_list = []

# Function to handle receiving data from the client
def receive_data(client_socket, target_socket):
    try:
        while True:
            client_data = client_socket.recv(4096)
            if not client_data:        
                break    
            # Only foward if selected bridge port
            if bridge_list[bridge_list_index] == client_socket.getpeername():
                target_socket.send(client_data)
    except: 
        pass
    print("[*] receive_data socket closed")

# Function to handle transmitting data to the client
def transmit_data(client_socket, target_socket):
    try: 
        while True:
            target_response = target_socket.recv(4096)
            if not target_response:
                break
            # Only foward if selected bridge port
            if bridge_list[bridge_list_index] == client_socket.getpeername():    
                client_socket.send(target_response)
    except:
        pass
    print("[*] transmit_data socket closed")



# Function to handle incoming client connections
def handle_client(client_socket, target_host, target_port):

    bridge_list.append(client_socket.getpeername())
    
    while True:
        # Connect only when the client is selected    
        while bridge_list[bridge_list_index] != client_socket.getpeername():
                time.sleep(1)

        try:
            # Connect to the target host
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.connect((target_host, target_port))

            # Threads for receiving and transmitting data
            receive_thread = threading.Thread(target=receive_data, args=(client_socket, target_socket))
            transmit_thread = threading.Thread(target=transmit_data, args=(client_socket, target_socket))

            receive_thread.start()
            transmit_thread.start()

            # Control socket detected off
            transmit_thread.join()
            print("[*] Control socket closed")

            # Force receive thread to stopped before timeout
            receive_thread._stop.set()

            # Do not close the sockets for persistance
            #client_socket.close()
            #target_socket.close()
        except:
            time.sleep(1)



# Set up the server
def start_server(bind_host, bind_port, target_host, target_port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((bind_host, bind_port))
    server.listen(5)
    print(f"[*] Listening on {bind_host}:{bind_port}")

    while True:
        client_socket, addr = server.accept()
        print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")


        # Create a thread to handle each client connection
        client_handler = threading.Thread(
            target=handle_client,
            args=(client_socket, target_host, target_port)
        )
        client_handler.start()


# Function to take input from keyboard
def keyboard_input():
    global bridge_list_index
    time.sleep(1)
    while True:
        cmd = input("bridge> ")
        if cmd == "list":
            print("[*] Ports list:", bridge_list)
        elif cmd == "n": 
            if bridge_list_index >= len(bridge_list) - 1:
                bridge_list_index = 0
            else:
                bridge_list_index = bridge_list_index + 1
        elif cmd == "all":
            bridge_list_index = 0
        else:
            try:
                bridge_list_index = int(cmd)
            except:
                pass
        try:
            print("[*] Forwarding the traffic to port", bridge_list[bridge_list_index])
        except:
            print("[x] No connections available to foward")

# Start the keyboard input thread
input_thread = threading.Thread(target=keyboard_input)
input_thread.start()

# Define the server and target details
server_host = 'localhost'  # Change this to your server's IP address
server_port = 2222  # Change this to your desired port

target_host = 'localhost'  # Change this to your target's IP address
target_port = 10001  # Change this to your target's port

# Start the server
start_server(server_host, server_port, target_host, target_port)


