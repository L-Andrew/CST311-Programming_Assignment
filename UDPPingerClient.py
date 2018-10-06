import time
from socket import *

UDP_IP = '127.0.0.1'
UDP_PORT = 12000
NUM_PACKETS_TO_SEND = 1000
avg_ping = 0
avg_ping_t = 0

client_sock = socket(AF_INET, SOCK_DGRAM)
client_sock.settimeout(1)

curr_seq = 0
for i in range(NUM_PACKETS_TO_SEND):
	time_ms = int(round(time.time() * 1000))
	message = 'Ping {} {}'.format(curr_seq, time_ms)
	past = time.time()
	client_sock.sendto(message.encode(), (UDP_IP, UDP_PORT))
	try:
		data = client_sock.recv(1024).decode()
		time_taken = (time.time() - past) * 1000
		avg_ping += time_taken
		
		if time_taken < 1:
			time_taken = '<1'
		else:
			time_taken = int(time_taken)
		print(data + " (RTT: {}ms)".format(time_taken))
		curr_seq += 1
	except timeout:
		time_taken = (time.time() - past) * 1000
		print('Request timed out.')
	avg_ping_t += time_taken
avg_ping /= curr_seq
avg_ping_t /= NUM_PACKETS_TO_SEND
num_pkt_lost = NUM_PACKETS_TO_SEND - curr_seq
num_pkt_lost_percent = int(round(100 - (curr_seq / NUM_PACKETS_TO_SEND) * 100.0))
avg_ping = int(round(avg_ping))
avg_ping_t = int(round(avg_ping_t))
print("")
print("Avg. Ping:\t{}ms".format(avg_ping))
print("Avg. Ping(incl. timeouts):\t{}ms".format(avg_ping_t))
print("Packets lost:\t{} ({}%)".format(num_pkt_lost, num_pkt_lost_percent))