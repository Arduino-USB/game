import socket
import threading
import queue
import json
import ast

HOST = "127.0.0.1"
PORT_BCAST = 6741  # Broadcast updates
PORT_CMD = 6742    # Commands + SEND replies

USER_UUID = None


# Sockets
_broadcast_socket = None
_cmd_socket = None

# Data storage
server_data = {}          # latest broadcast data
_reply_queue = queue.Queue()  # queued SEND replies

_socket_lock = threading.Lock()


# -------------------------------
# CONNECTION SETUP
# -------------------------------
def get_host():
	global HOST
	return HOST

def set_host(host):
	global HOST
	HOST = host

def set_uuid(u_id):
	global USER_UUID
	USER_UUID = u_id

def connect(host=get_host()):
	global HOST, _broadcast_socket, _cmd_socket
	HOST = host

	# Broadcast socket
	try:
		_broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		_broadcast_socket.connect((HOST, PORT_BCAST))
		threading.Thread(target=_recv_broadcast_thread, daemon=True).start()

		# Command/Reply socket
		_cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		_cmd_socket.connect((HOST, PORT_CMD))
		threading.Thread(target=_recv_reply_thread, daemon=True).start()
		return True
	except:
		return False

# -------------------------------
# BROADCAST READER
# -------------------------------
def _recv_broadcast_thread():
	"""Continuously read broadcast updates"""
	buffer = ""
	global server_data
	while True:
		try:
			data = _broadcast_socket.recv(1024)
			if not data:
				break
			buffer += data.decode()
			while "\n" in buffer:
				line, buffer = buffer.split("\n", 1)
				if not line.strip():
					continue
				try:
					msg = ast.literal_eval(line)
					server_data.clear()
					server_data.update(msg.get("server_data", {}))
				except Exception as e:
					print("Broadcast parse error:", e)
		except Exception as e:
			print("Broadcast receive error:", e)
			break


def read_broadcast():
	"""Return a copy of latest server_data"""
	global server_data
	return server_data.copy()


# -------------------------------
# COMMAND/REPLY READER
# -------------------------------
def _recv_reply_thread():
	"""Continuously read replies (SEND)"""
	buffer = ""
	while True:
		try:
			data = _cmd_socket.recv(1024)
			if not data:
				break
			buffer += data.decode()
			while "\n" in buffer:
				line, buffer = buffer.split("\n", 1)
				if not line.strip():
					continue
				try:
					msg = ast.literal_eval(line)
					_reply_queue.put(msg)
				except Exception as e:
					print("Reply parse error:", e)
		except Exception as e:
			print("Reply receive error:", e)
			break


def read_reply():
	"""Non-blocking read for next SEND reply"""
	if not _reply_queue.empty():
		try:
			reply_from_server = _reply_queue.get_nowait()
			if USER_UUID == None:
				print("UUID not set up yet")		
				return reply_from_server	
			elif reply_from_server["uuid"] == USER_UUID:
				print("Message is for me")
				return reply_from_server
			else:
				print("Message isnt for me")
				return None
		except queue.Empty:
			return None
	return None


# -------------------------------
# SEND COMMANDS
# -------------------------------
def send_to_server(msg_dict):
	"""Send a dict command to server"""
	global _cmd_socket
	
	if USER_UUID != None:
		#print(f"USER_UUID is not None, it's {USER_UUID}")
		msg_dict["from"] = USER_UUID
	try:
		msg_str = json.dumps(msg_dict) + "\n"
		with _socket_lock:
			_cmd_socket.sendall(msg_str.encode())
	except Exception as e:
		print("send_to_server error:", e)

