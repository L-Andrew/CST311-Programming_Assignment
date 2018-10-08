# Name: UDPPingerClient.py
# Authors: Andrew Lin, Evan Gonzales
# Abstract: A simple UDP client that pings a given server and calculates
#			the average, max, and minimum ping.

import time
from socket import *

# declare our target server and the amount of packets to send
UDP_IP = '127.0.0.1'
UDP_PORT = 12000
NUM_PACKETS_TO_SEND = 10

# declare ping statistics
avg_ping = 0
# min_ping is set to 1000 as timeout is 1000ms (or 1s)
min_ping = 1000
max_ping = 0

# initialize client_sock as UDP and set its timeout to 1s
client_sock = socket(AF_INET, SOCK_DGRAM)
client_sock.settimeout(1)

# declare sequence number and packet loss count
curr_seq = 0
pkt_lost_count = 0

for i in range(NUM_PACKETS_TO_SEND):
	# get current time and convert it to ms
	time_ms = int(round(time.time() * 1000))
	# prepare our message with the current seq. num. and time
	message = 'Ping {} {}'.format(curr_seq, time_ms)
	past = time.time()
	# fire off UDP packet to our server
	client_sock.sendto(message.encode(), (UDP_IP, UDP_PORT))
	try:
		# recv maximum of 1024 bytes and decode data
		data = client_sock.recv(1024).decode()
		time_taken = (time.time() - past) * 1000
		# increment avg_ping by time_taken and set min/max_ping to the new highest or lowest (if any)
		avg_ping += time_taken
		min_ping = min(min_ping, time_taken)
		max_ping = max(max_ping, time_taken)
		
		# if time_taken was under 1ms, display as <1
		if time_taken < 1:
			time_taken = '<1'
		else:
			# round and trim off any decimal places 
			time_taken = int(round(time_taken))
		# print data sent with our RTT
		print(data + " (RTT: {}ms)".format(time_taken))
		curr_seq += 1
	except timeout:
		# if a timeout occured, increment pkt_lost_count
		pkt_lost_count += 1
		print('Request timed out.')

# calculate percentage of packets lost during transit (or on server)
num_pkt_lost_percent = int(round((pkt_lost_count / NUM_PACKETS_TO_SEND) * 100.0))

# for ever packet lost, assume it was 1000ms
avg_ping_t = int(round((avg_ping + (pkt_lost_count * 1000)) / NUM_PACKETS_TO_SEND))
# curr_seq would have the amount of successive pings, so we can use it in averaging
avg_ping = int(round(avg_ping / curr_seq))
min_ping = int(round(min_ping))
max_ping = int(round(max_ping))

# display statistics
print("")
print("Avg. Ping:\t\t{}ms".format(avg_ping))
print("Avg. Ping w/ loss:\t{}ms".format(avg_ping_t))
print("Min. Ping:\t\t{}ms".format(min_ping))
print("Max. Ping:\t\t{}ms".format(max_ping))
print("Packets lost:\t\t{} ({}%)".format(pkt_lost_count, num_pkt_lost_percent))