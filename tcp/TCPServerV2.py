from socket import *
from select import select
from threading import Thread
import sys, threading, time

# CONFIG: Change these to whatever necessary
BINDING_ADDRESS = '0.0.0.0'
BINDING_PORT = 12000
MSG_BUFFER_SIZE = 1024
NAME_BUFFER_SIZE = 32

# MESSAGE FORMATS: Change these to suit a flavor of console.
# Technically speaking, these also effect clients.
# (Clients do not print their own message - they wait for the server to respond with it)
NEW_CONNECTION_STR_FMT = "[.] Accepted new connection from {}."
NEW_USER_STR_FMT = "[!] {} has joined"
NEW_MSG_STR_FMT = "[.] {}: {}"
DISCONNECTED_STR_FMT = "[!] {} has disconnected."
CLOSING_STR_FMT = "[!] Server is closing."

class ChatServer:
	def __init__(self):
		'''
		Constructs a new ChatServer instance.
		Note: The server is _not_ listening. You must call startHosting(hostname, port).
		'''
		self.host_socket = None
		self.connected = {}
	
	def startHosting(self, hostname, port):
		'''
		Creates a TCP socket and binds it to the given hostname and port.
		'''
		self.host_socket = socket(AF_INET, SOCK_STREAM)
		self.host_socket.bind((BINDING_ADDRESS, BINDING_PORT))
		self.host_socket.listen(1)
		
	def acceptNewUser(self):
		'''
		Accepts and stores any new connections, waiting for their names.
		'''
		new_client, addr = self.host_socket.accept()
		self.connected[new_client] = None
		print(NEW_CONNECTION_STR_FMT.format(addr))
		
	def removeDeadSocket(self, socket):
		'''
		Removes any socket from the name mapping.
		Assumes the socket is dead and will notify users of their disconnection.
		'''
		name = self.connected[socket]
		self.connected.pop(socket)
		if name != None:
			self.broadcastMessage(DISCONNECTED_STR_FMT, name)
		
	def writeData(self, socket, data):
		'''
		Attempts to write data to the socket, removing it if dead
		'''
		try:
			socket.send(data)
		except ConnectionResetError:
			self.removeDeadSocket(socket)
			
	def readData(self, socket, buffer_size):
		'''
		Attempts to read string data from a socket, removing it if dead.
		'''
		try:
			data = socket.recv(buffer_size)
			
			if len(data) == 0:
				self.removeDeadSocket(socket)
				return None
				
			return data.decode()
		except ConnectionResetError:
			self.removeDeadSocket(socket)
			return None
		
	def broadcastMessage(self, fmt, *args):
		'''
		Broadcasts a message to all clients and prints to console.
		'''
		msg = fmt.format(*args)
		print(msg)
		for socket in self.connected.keys():
			self.writeData(socket, msg.encode())
		
	def tick(self):
		'''
		Main server ticking method.
		Would have been single threaded, but alas, Windows select() does _not_ handle sys.stdin.
		Therefore, it is necessary to spin this in a different thread, as select() _will_ lock
		the process up until some socket event happens.
		'''
		active_sockets, _, _ = select([self.host_socket] + list(self.connected.keys()), [], [])
		
		for socket in active_sockets:
			if socket == self.host_socket:
				self.acceptNewUser()
			else:
				if socket not in self.connected:
					print("[?] Unknown socket")
					print(socket)
				if self.connected[socket] == None:
					name = self.readData(socket, NAME_BUFFER_SIZE)
					if name is not None:
						self.connected[socket] = name
						self.broadcastMessage(NEW_USER_STR_FMT, name)
				else:
					message = self.readData(socket, MSG_BUFFER_SIZE)
					if message is not None:
						self.broadcastMessage(NEW_MSG_STR_FMT, self.connected[socket], message)
	
	def close(self):
		'''
		Does what it says on the tin - closes the server.
		'''
		self.broadcastMessage(CLOSING_STR_FMT)
		self.host_socket.close()

# dummy method because python doesn't support
# multi-line lambdas
def thread_loop(server):
	while True:
		server.tick()

if __name__ == "__main__":
	# start server and begin listening
	server = ChatServer()
	server.startHosting(BINDING_ADDRESS, BINDING_PORT)
	
	# spin server ticks on a seperate thread to let main thread process ctrl+c
	# and user input
	server_thread = Thread(target=thread_loop, args=(server,))
	server_thread.daemon = True
	server_thread.start()
	
	while True:
		try:
			server_input = input()
			if server_input.lower() == "bye":
				# bad hack, but don't want to repeat self
				# tl;dr just interpret "bye" as ctrl+c
				raise KeyboardInterrupt
		except KeyboardInterrupt:
			server.close()
			sys.exit(0)