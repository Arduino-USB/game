# network.py
from client import send_to_server, read_broadcast
import time
last_server_data = {}

def update_server_location(client_data=None):
	
	now = time.time()
	if now - client_data["last_send_time"] >= client_data["SEND_INTERVAL"]:
		send_to_server({"set_location": {"x": client_data["player_pos"]["x"], "y": client_data["player_pos"]["y"]}})
		#print("location updated")
		return now
	return client_data["last_send_time"]

def get_server_data():
	global last_server_data
	server_reply = read_broadcast()
	

	if server_reply is None:
		server_reply = last_server_data
	else:
		last_server_data = server_reply
		return server_reply

