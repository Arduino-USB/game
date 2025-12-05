import socket
import threading
import server_functions
import sys
import ast
import traceback
import time

HOST = "127.0.0.1"
PORT = 6741

# Keep track of all connected clients and their state
connected = {}  # addr -> {"conn": socket, "data": {}}

index = 0 

def get_data():
	return {"server_data" : {addr: info["data"] for addr, info in connected.items()}}

def handle_client(conn, addr):
	global index
	connected[addr] = {"conn": conn, "data": {}, "id" : index }
	index += 1
	print(f"Connected: {addr}")
	buffer = ""
	while True:
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
				except Exception as e:
					print("Invalid data:", e, line)
					continue

				if not isinstance(data, dict):
					print("Received non-dict data:", data)
					continue

				func_name = list(data.keys())[0]
				func = getattr(server_functions, func_name, None)
				if not callable(func):
					print(f"server_functions.{func_name} is not callable")
					continue

				output = func(data[func_name], server_data=get_data())
				

				# Update client-specific state
				if "SET" in output:
					for key_name in output["SET"]:
						connected[addr]["data"][key_name] = output["SET"][key_name]

				# Send response specifically to this client if requested
				if "SEND" in output:
					try:
						###add id system
						sending = str(output["SEND"]).encode() + b'\n'
						connected[addr]["conn"].sendall(sending)
					except Exception as e:
						print(f"Failed to send specific response to {addr}: {e}")



		except Exception as e:
			print("Error:", e)
			traceback.print_exc()
			break

	conn.close()
	print(f"Disconnected: {addr}")
	if addr in connected:
		del connected[addr]

def broadcast_server_data():
	"""Constantly send current server_data to all clients"""
	while True:
		if connected:
			data_to_send = str({"server_data": get_data()["server_data"]}).encode() + b'\n'
			for addr in list(connected.keys()):
				try:
					connected[addr]["conn"].sendall(data_to_send)
				except Exception as e:
					print(f"Failed to broadcast to {addr}: {e}")
					connected[addr]["conn"].close()
					del connected[addr]
		time.sleep(0.1)  # 10 times per second


def main():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((HOST, PORT))
	s.listen()
	print("Server ready")

	# Start broadcast thread
	threading.Thread(target=broadcast_server_data, daemon=True).start()

	try:
		while True:
			conn, addr = s.accept()
			thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
			thread.start()

	except KeyboardInterrupt:
		print("\nCtrl-C pressed, shutting down server...")

	finally:
		s.close()
		print("Server socket closed.")

if __name__ == "__main__":
	main()

