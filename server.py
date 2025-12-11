import socket
import threading
import server_functions
import sys
import ast
import traceback
import time
import random

HOST = "127.0.0.1"
PORT_CMD = 6742       # Commands + SEND replies
PORT_BCAST = 6741     # Broadcast updates only

connected_cmd = {}    # addr -> {"conn": socket, "data": {}, "id": int}
connected_bcast = {}  # addr -> conn only
index = 0


def get_data():
	return {addr: info["data"] for addr, info in connected_cmd.items()}


# ----------------------------------------
# COMMAND HANDLER (port 6742)
# ----------------------------------------


# ----------------------------------------
# SERVER FUNCTION CALL HELPER
# ----------------------------------------
def call_helper(data, conn=None, addr=None):
	"""
	data: dict in the form {"func_name": payload}
	conn, addr: optional, only used if sending to a client
	"""
	# ensure client entry exists
	if addr is not None:
		if addr not in connected_cmd:
			connected_cmd[addr] = {"conn": conn, "data": {}, "id": -1}
		else:
			connected_cmd[addr]["conn"] = conn

	func_name = list(data.keys())[0]

	# block internal names
	if func_name.startswith("__"):
		print(f"Function {func_name} not allowed")
		return {"ERROR": "Function not allowed"}

	func = getattr(server_functions, func_name, None)
	if not callable(func):
		print(f"{func_name} not callable")
		return {"ERROR": "Function not callable"}

	# run the server function
	output = func(
		data[func_name],
		server_data=get_data(),
		from_id=data.get("from")
	)

	# -----------------------------------------------------
	# NEW: SR_SET (server-wide SET by UUID)
	# -----------------------------------------------------
	if "SR_SET" in output:
		payload = output["SR_SET"]

		# payload should be: { uuid1: {k:v, k:v}, uuid2: {...} }
		for target_uuid, vars_to_set in payload.items():

			sd = get_data()  # dict of all players

			found = False
			for a in sd:
				if sd[a].get("uuid") == target_uuid:
					for k, v in vars_to_set.items():
						sd[a][k] = v
					print(f"SR_SET applied to uuid={target_uuid} at {a}")
					found = True
					break

			if not found:
				print(f"SR_SET uuid={target_uuid} not found")

	# -----------------------------------------------------
	# Normal per-client SET
	# -----------------------------------------------------
	if addr is not None and "SET" in output:
		for k in output["SET"]:
			connected_cmd[addr]["data"][k] = output["SET"][k]

	# -----------------------------------------------------
	# SEND back to client
	# -----------------------------------------------------
	if conn is not None and "SEND" in output:
		try:
			output["SEND"]["func"] = func_name
			sending = str(output["SEND"]).encode() + b'\n'
			print(f"SENDING {sending}")
			conn.sendall(sending)
		except:
			print(f"Failed to SEND to {addr}")

	return output





def handle_cmd_client(conn, addr):
	
	global index
	connected_cmd[addr] = {"conn": conn, "data": {}, "id": index}
	index += 1
	print(f"[CMD] Connected: {addr}")

	buffer = ""
	while True:
		print(get_data())
		try:
			data_raw = conn.recv(1024)
			if not data_raw:
				break

			buffer += data_raw.decode()

			while "\n" in buffer:
				line, buffer = buffer.split("\n", 1)
				line = line.strip()
				if not line:
					continue

				try:
					data = ast.literal_eval(line)
				except:
					print("Invalid data:", line)
					

				if not isinstance(data, dict):
					print("Received non-dict data:", data)
					continue
				call_helper(data, conn, addr)
		except Exception as e:
			print("CMD Error:", e)
			traceback.print_exc()
			break

	conn.close()
	print(f"[CMD] Disconnected: {addr}")
	if addr in connected_cmd:
		del connected_cmd[addr]


# ----------------------------------------
# BROADCAST HANDLER (port 6741)
# ----------------------------------------
def handle_bcast_client(conn, addr):
	connected_bcast[addr] = conn
	print(f"[BCAST] Connected: {addr}")

	try:
		# Broadcast clients don't send us anything
		while conn.recv(1):
			pass
	except:
		pass

	conn.close()
	print(f"[BCAST] Disconnected: {addr}")
	if addr in connected_bcast:
		del connected_bcast[addr]

def cmd_accept_loop(cmd_socket):
	while True:
		r, addr = cmd_socket.accept()
		threading.Thread(target=handle_cmd_client, args=(r, addr), daemon=True).start()

def bcast_accept_loop(bcast_socket):
	while True:
		r, addr = bcast_socket.accept()
		threading.Thread(target=handle_bcast_client, args=(r, addr), daemon=True).start()

def broadcast_loop():
	"""Broadcast server_data to ALL broadcast clients"""
	while True:
		if connected_cmd and connected_bcast:
			data_to_send = str({"server_data" : get_data()}).encode() + b'\n'

			for addr in list(connected_bcast.keys()):
				try:
					connected_bcast[addr].sendall(data_to_send)
				except:
					connected_bcast[addr].close()
					del connected_bcast[addr]

		time.sleep(0.1)


def intermission():
	for i in reversed(range(1, 10)):
		print(f"{i} seconds left till game start")
		time.sleep(1)
		print(get_data())
		
	call_helper({"__send_init_data": ""}, conn=conn, addr=addr)
# ----------------------------------------
# SERVER MAIN (one file, two ports)
def main():
	print("Server ready")

	# Set up sockets
	cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	cmd_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	cmd_socket.bind((HOST, PORT_CMD))
	cmd_socket.listen()

	bcast_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	bcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	bcast_socket.bind((HOST, PORT_BCAST))
	bcast_socket.listen()

	# Start accept loops in background threads
	threading.Thread(target=cmd_accept_loop, args=(cmd_socket,), daemon=True).start()
	threading.Thread(target=bcast_accept_loop, args=(bcast_socket,), daemon=True).start()

	print(f"CMD server on port {PORT_CMD}")
	print(f"BCAST server on port {PORT_BCAST}")

	print("Starting intermission stage")
	intermission()
	print("Intermission stage is over, game is starting")

	# Start broadcast loop
	threading.Thread(target=broadcast_loop, daemon=True).start()

	# Keep main thread alive so program doesn't exit
	while True:
		time.sleep(1)

if __name__ == "__main__":
	main()
