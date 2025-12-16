import socket
import threading
import server_functions
import sys
import ast
import traceback
import time
import random

HOST = "127.0.0.1"
PORT_CMD = 6742
PORT_BCAST = 6741

connected_cmd = {}		# addr -> {"conn": socket, "data": {}, "id": int}
connected_bcast = {}	# addr -> conn only

objects = {}			# uuid -> object dict
index = 0


# ----------------------------------------
# SERVER DATA STRUCTURE
# ----------------------------------------
def get_data():
	# Only include users whose data dict is not empty
	return {
		"users": {addr: info["data"] for addr, info in connected_cmd.items() if info["data"]},
		"objects": objects
	}

def remove_key_from_all_users(key):
	for info in connected_cmd.values():
		info["data"].pop(key, None)


def all_players_ready():
	users = get_data()["users"]
	if len(users) < 2:
		return False
	for info in users.values():
		if not all(key in info for key in ("uuid", "username", "player_image")):
			return False
	return True

# ----------------------------------------
# SERVER FUNCTION CALL HELPER
# ----------------------------------------
def call_helper(data, conn=None, addr=None, from_server=False):

	# ensure client entry exists
	if addr is not None:
		if addr not in connected_cmd:
			connected_cmd[addr] = {"conn": conn, "data": {}, "id": -1}
		else:
			connected_cmd[addr]["conn"] = conn

	func_name = list(data.keys())[0]

	# block internal names
	if func_name.startswith("__") and from_server == False:
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
	# SR_SET_USERS (server-wide user update by UUID)
	# -----------------------------------------------------
	if "SR_SET_USERS" in output:
		payload = output["SR_SET_USERS"]	# {uuid: {vars}}

		users = get_data()["users"]

		for target_uuid, vars_to_set in payload.items():
			found = False
			for a in users:
				if users[a].get("uuid") == target_uuid:
					for k, v in vars_to_set.items():
						users[a][k] = v
					print(f"SR_SET_USERS applied to uuid={target_uuid} at {a}")
					found = True
					break

			if not found:
				print(f"SR_SET_USERS uuid={target_uuid} not found")

	# -----------------------------------------------------
	# SR_SET_OBJ (update or create object by UUID)
	# -----------------------------------------------------
	if "SR_SET_OBJ" in output:
		payload = output["SR_SET_OBJ"]		# {uuid: {vars}}

		for target_uuid, vars_to_set in payload.items():

			# Auto-create entry if missing
			if target_uuid not in objects:
				objects[target_uuid] = {"uuid": target_uuid}
				print(f"SR_SET_OBJ created new object uuid={target_uuid}")

			# Apply updates
			for k, v in vars_to_set.items():
				objects[target_uuid][k] = v

			print(f"SR_SET_OBJ applied to object uuid={target_uuid}")


	if "SR_DEL_USERS" in output:
		payload = output["SR_DEL_USERS"]  # {uuid: [keys]} or {uuid: "*"}

		users = get_data()["users"]

		for target_uuid, keys_to_delete in payload.items():
			found_addr = None

			for a in users:
				if users[a].get("uuid") == target_uuid:
					found_addr = a
					break

			if found_addr is None:
				print(f"SR_DEL_USERS uuid={target_uuid} not found")
				continue

			if keys_to_delete == "*":
				# Remove entire user data dict (keep connection alive)
				connected_cmd[found_addr]["data"].clear()
				print(f"SR_DEL_USERS cleared entire data for uuid={target_uuid}")
			else:
				# Remove only listed keys
				for k in keys_to_delete:
					if k in connected_cmd[found_addr]["data"]:
						del connected_cmd[found_addr]["data"][k]
						print(f"SR_DEL_USERS deleted key '{k}' from uuid={target_uuid}")

	# -----------------------------------------------------
	# Normal per-client SET
	# -----------------------------------------------------
	if addr is not None and "SET" in output:
		for k in output["SET"]:
			connected_cmd[addr]["data"][k] = output["SET"][k]

	# -----------------------------------------------------
	# SEND back to client
	# -----------------------------------------------------

	if "SEND" in output:
		output["SEND"]["func"] = func_name
		if conn is not None:
			sending = str(output["SEND"]).encode() + b'\n'
			conn.sendall(sending)
		else:
			# broadcast to all connected clients
			for a, info in connected_cmd.items():
				try:
					sending = str(output["SEND"]).encode() + b'\n'
					info["conn"].sendall(sending)
				except:
					print(f"Failed to send to {a}")
	
	return output


# ----------------------------------------
# COMMAND HANDLER
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
# BROADCAST HANDLER
# ----------------------------------------
def handle_bcast_client(conn, addr):
	connected_bcast[addr] = conn
	print(f"[BCAST] Connected: {addr}")

	try:
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
	while True:
		if connected_cmd and connected_bcast:
			data_to_send = str({"server_data": get_data()}).encode() + b'\n'

			for addr in list(connected_bcast.keys()):
				try:
					connected_bcast[addr].sendall(data_to_send)
				except:
					connected_bcast[addr].close()
					del connected_bcast[addr]

		time.sleep(0.1)


# ----------------------------------------
# INTERMISSION
# ----------------------------------------
def intermission(debug=False):
	print("Waiting for at least 2 players with username and player image...")
	countdown_started = False
	seconds_left = 10	# Change this number if you want a longer/shorter countdown

	while True:
		if not debug:
			ready = all_players_ready()
		else:
			ready = True

		if ready:
			if not countdown_started:
				print("Conditions met! Starting intermission countdown...")
				countdown_started = True
				seconds_left = 10	# Reset when starting fresh

			print(f"{seconds_left} seconds left till game start")
			seconds_left -= 1

			if seconds_left < 0:
				print("Game starting now!")
				call_helper({"__send_init_data": None}, from_server=True)
				time.sleep(0.1)
				remove_key_from_all_users("player_image")
				return	# Exit intermission, game begins

		else:
			if countdown_started:
				print("Player left or became incomplete. Pausing countdown and waiting again...")
				countdown_started = False
				seconds_left = 10	# Reset for next valid start
			else:
				print(f"Waiting for players... Currently {len(get_data()['users'])} connected, need at least 2 ready.")

		time.sleep(1)
	
		
			
# ----------------------------------------
# SERVER MAIN
# ----------------------------------------
def main():
	print("Server ready")

	cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	cmd_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	cmd_socket.bind((HOST, PORT_CMD))
	cmd_socket.listen()

	bcast_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	bcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	bcast_socket.bind((HOST, PORT_BCAST))
	bcast_socket.listen()

	threading.Thread(target=cmd_accept_loop, args=(cmd_socket,), daemon=True).start()
	threading.Thread(target=bcast_accept_loop, args=(bcast_socket,), daemon=True).start()

	print(f"CMD server on port {PORT_CMD}")
	print(f"BCAST server on port {PORT_BCAST}")

	print("Starting intermission stage")
	intermission(debug=False)
	print("Intermission stage is over, game is starting")

	threading.Thread(target=broadcast_loop, daemon=True).start()

	while True:
		time.sleep(1)


if __name__ == "__main__":
	main()

