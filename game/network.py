# network.py
from client import send_to_server, read_broadcast

last_server_data = {}

def update_server_location(player_pos, last_send_time, send_interval):
	import time
	now = time.time()
	if now - last_send_time >= send_interval:
		send_to_server({"set_location": {"x": player_pos["x"], "y": player_pos["y"]}})
		return now
	return last_send_time

def get_server_data():
	global last_server_data
	server_reply = read_broadcast()
	

	if server_reply is None:
		server_reply = last_server_data
	else:
		last_server_data = server_reply
		return server_reply

