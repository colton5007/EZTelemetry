import socket
import random
import threading

channels = list()
types = list()

host = '192.168.4.199'
port = 4001
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port))
server.listen(10)
tcp_clients = list()


def load_channels():
	file = open("channels").readlines()
	for line in file:
		split = line.replace('\n', '').replace(' ', '_').split(',')
		channels.append(split[0])
		types.append(split[1])


def get_test_data():
	payload = ""
	for i in range(len(channels)):
		if types[i] == "String":
			d = "Test" + i + str(random.random())
		else:
			d = random.random()
		payload = payload + f"{d}, "
	return payload + '\n'


def send_test_data():
	while True:
		for c in tcp_clients:
			data = get_test_data()
			try:
				print(f"Sending data {data}")
				c.send(bytearray(data, encoding="UTF-8"))
			except Exception as e:
				print(e)
				tcp_clients.remove(c)


def handle_tcp():
	global tcp_clients
	while True:
		conn, addr = server.accept()
		tcp_clients.append(conn)
		print(addr)


load_channels()
tcp_thread = threading.Thread(target=handle_tcp)
tcp_thread.start()
# Start streaming data
send_test_data()
