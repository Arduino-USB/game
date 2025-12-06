import socket
import threading
import server_functions
import sys
import ast
import traceback
import time

HOST = "127.0.0.1"
PORT_CMD = 6742       # Commands + SEND replies
PORT_BCAST = 6741     # Broadcast updates only

connected_cmd = {}    # addr -> {"conn": socket, "data": {}, "id": int}
connected_bcast = {}  # addr -> conn only
index = 0


def get_data():
	return {"server_data": {addr: info["data"] for addr, info in connected_cmd.items()}}


# ----------------------------------------
# COMMAND HANDLER (port 6742)
# ----------------------------------------
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
					continue

				if not isinstance(data, dict):
					print("Received non-dict data:", data)
					continue

				func_name = list(data.keys())[0]
				func = getattr(server_functions, func_name, None)

				if not callable(func):
					print(f"{func_name} not callable")
					continue
				
				print(f"Got from client: {data}")
				output = func(data[func_name], server_data=get_data(), from_id=data.get("from"))
				

				# Update local state
				if "SET" in output:
					for k in output["SET"]:
						connected_cmd[addr]["data"][k] = output["SET"][k]

				
				if "SEND" in output:
					try:
						sending = str(output["SEND"]).encode() + b'\n'
						print(f"Server is sending {sending}")
						conn.sendall(sending)
					except:
						print(f"Failed to SEND to {addr}")

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


def broadcast_loop():
	"""Broadcast server_data to ALL broadcast clients"""
	while True:
		if connected_cmd and connected_bcast:
			data_to_send = str(get_data()).encode() + b'\n'

			for addr in list(connected_bcast.keys()):
				try:
					connected_bcast[addr].sendall(data_to_send)
				except:
					connected_bcast[addr].close()
					del connected_bcast[addr]

		time.sleep(0.1)


# ----------------------------------------
# SERVER MAIN (one file, two ports)
# ----------------------------------------
def main():
	print("Server ready")

	# Start broadcast thread
	threading.Thread(target=broadcast_loop, daemon=True).start()

	# Listener for CMD socket
	cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	cmd_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	cmd_socket.bind((HOST, PORT_CMD))
	cmd_socket.listen()

	# Listener for BCAST socket
	bcast_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	bcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	bcast_socket.bind((HOST, PORT_BCAST))
	bcast_socket.listen()

	print(f"CMD server on port {PORT_CMD}")
	print(f"BCAST server on port {PORT_BCAST}")

	try:
		while True:
			# Accept from BOTH sockets
			r1, addr1 = cmd_socket.accept()
			threading.Thread(target=handle_cmd_client, args=(r1, addr1), daemon=True).start()

			r2, addr2 = bcast_socket.accept()
			threading.Thread(target=handle_bcast_client, args=(r2, addr2), daemon=True).start()

	except KeyboardInterrupt:
		print("\nCtrl-C: shutting down")

	finally:
		cmd_socket.close()
		bcast_socket.close()


if __name__ == "__main__":
	main()

