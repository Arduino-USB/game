import socket
import threading
import json
import ast
import queue

_client_socket = None
_socket_lock = threading.Lock()
_reply_queue = queue.Queue()
server_data = {}  # shared data from server

HOST = "127.0.0.1"
PORT = 6741

def set_host(host):
	global HOST
	HOST = host
	


def _ensure_connection():
	global _client_socket
	if _client_socket is None:
		_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		_client_socket.connect((HOST, PORT))
		thread = threading.Thread(target=_recv_thread, daemon=True)
		thread.start()

def _recv_thread():
	"""Continuously read from socket and update server_data"""
	buffer = ""
	global server_data
	while True:
		try:
			data = _client_socket.recv(1024)
			if not data:
				break
			buffer += data.decode()
			while "\n" in buffer:
				line, buffer = buffer.split("\n", 1)
				line = line.strip()
				if not line:
					continue
				try:
					msg = ast.literal_eval(line)
					_reply_queue.put(msg)
				except Exception as e:
					print("Failed to parse server message:", e, "Raw:", line)
		except Exception as e:
			print("Receive thread error:", e)
			break

def send_to_server(msg_dict):
	"""Send dict to server without blocking"""
	global _client_socket
	_ensure_connection()

	try:
		msg_str = json.dumps(msg_dict) + "\n"
		with _socket_lock:
			_client_socket.sendall(msg_str.encode())
	except Exception as e:
		print("send_to_server error:", e)

def get_server_data():
	"""Return a copy of latest server data (push-based)"""
	global server_data
	return server_data.copy()

def read_from_server():
	"""Non-blocking read for the next reply (if any)"""
	if not _reply_queue.empty():
		try:
			return _reply_queue.get_nowait()
		except queue.Empty:
			return None
	return None

