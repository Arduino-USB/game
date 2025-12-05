# network.py
from client import send_to_server, read_from_server

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
	server_reply = read_from_server()
	if server_reply is None:
		server_reply = last_server_data
	if "server_data" in server_reply:
		last_server_data = server_reply
		return server_reply["server_data"]
	return {}

