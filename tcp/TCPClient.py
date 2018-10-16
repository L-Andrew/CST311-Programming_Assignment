from socket import *
import random, string

dest = ("localhost", 12000)

try:
	c_socket = socket(AF_INET, SOCK_STREAM)
	c_socket.connect(dest)
except:
	print(f"[!] Failed to connect to server {dest[0]}:{dest[1]}")
	exit()

clientID = ''.join(random.choice(string.ascii_uppercase) for i in range(8))

print(f"[!] Connected to {dest[0]}:{dest[1]}")
print(f"[.] Using ID: {clientID}")

sentence = input("[?] Input message: ")
message = f"Client ID {clientID}: {sentence}"
print(f"[.] Sending \"{message}\"")
c_socket.send(message.encode())

modifiedSentence = c_socket.recv(1024)
print(f"[!] Received from server: \n\t{modifiedSentence.decode()}")
c_socket.close()
