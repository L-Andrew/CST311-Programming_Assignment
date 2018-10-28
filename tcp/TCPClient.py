from socket import *
from select import select
from threading import Thread
import random, string, sys

# change to whatever necessary
HOST_ADDRESS = "localhost"
HOST_PORT = 12000

# recv buffer size
MSG_BUFFER_SIZE = 1024

# MESSAGE FORMATS: These are not used for chat messages; they're purely status messages.
CONNECTING_STR_FMT = "[.] Generating ID and connecting to {}:{}..."
FAILED_TO_CONNECT_STR_FMT = "[!] Failed to connect to server {}:{}"
SUCCESS_CONNECT_STR_FMT = "[.] Connected, sending name..."
FAILED_TO_SEND_NAME_STR_FMT = "[!] Failed to send our name ({})!"
UNKNOWN_ERROR_STR_FMT = "[!] Unknown error!"

def listen(client_socket, name):
	'''
	Main loop for receving and outputting data from the server.
	Automatically closes if error occurs.
	'''
	while True:
		try:
			message = client_socket.recv(MSG_BUFFER_SIZE)
			print(message.decode().replace(name, name + " (You)"))
			break
		except:
			print("[!] Connection closed.")
			break
			
def generateClientID():
	'''
	Generates a random 8 character long ID.
	'''
	return ''.join(random.choice(string.ascii_uppercase) for i in range(8))

def connect(hostname, port):
	'''
	Creates a socket and connects to the server.
	Returns the socket or None if it failed.
	'''
	try:
		client_socket = socket(AF_INET, SOCK_STREAM)
		client_socket.connect((hostname, port))
		return client_socket
	except:
		return None
	
if __name__ == "__main__":
	# connect to server
	print(CONNECTING_STR_FMT.format(HOST_ADDRESS, HOST_PORT))
	
	client_socket = connect(HOST_ADDRESS, HOST_PORT)
	name = generateClientID()
	
	# check for client_socket being None, indicating failure
	if client_socket is None:
		print(FAILED_TO_CONNECT_STR_FMT.format(HOST_ADDRESS, HOST_PORT))
		sys.exit(1)
		
	print(SUCCESS_CONNECT_STR_FMT)
	
	try:
		# send our client name
		client_socket
		client_socket.send(name.encode())
	except Exception as exc:
		print(exc)
		print(FAILED_TO_SEND_NAME_STR_FMT.format(name))
		sys.exit(1)

	# unfortunately, due Windows's lack of file descriptors, 
	# we must spawn a seperate thread to read stdin
	# otherwise, on *nix systems, we would use select()
	recv_and_print_thread = Thread(target=listen, args=(client_socket,name))
	recv_and_print_thread.daemon = True
	recv_and_print_thread.start()
	
	while True:
		try:
			# grab user input
			message = input()
			if not recv_and_print_thread.isAlive():
				# interpret isAlive() being false as connection being closed
				sys.exit(0)
			# send the data over to the server
			client_socket.send(message.encode())
			# after sent, check if message is "bye", and if it is, then interpret as ctrl+c
			if message.lower() == "bye":
				raise KeyboardInterrupt
		except KeyboardInterrupt:
			client_socket.close()
			sys.exit(0)
		except Exception as exc:
			print(UNKNOWN_ERROR_STR_FMT)
			print(exc)
			sys.exit(1)