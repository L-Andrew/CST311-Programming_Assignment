# UDPPingerServer.py
# We will need the following module to generate randomized lost packets
from socket import *
serverSocket = socket(AF_INET, SOCK_STREAM)
# Assign IP address and port number to socket
serverSocket.bind(('', 12000))
serverSocket.listen(1)
print('Server ready')
while True:
	# Receive the client packet along with the address it is coming from
	connectionSocketA, addressA = serverSocket.accept()
	messageA = connectionSocketA.recv(1024).decode()
	print(messageA)
	connectionSocketB, addressB = serverSocket.accept()
	messageB = connectionSocketB.recv(1024).decode()
	print(messageB)
	# Capitalize the message from the client
	messageA += ' received before ' + messageB
	# Otherwise, the server responds
	connectionSocketA.send(messageA.encode())
	connectionSocketA.close()
	connectionSocketB.send(messageA.encode())
	connectionSocketB.close()