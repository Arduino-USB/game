import random
import os
from helper_functions import load_map_init, norm_path, list_to_dict, get_region_coords

# Edited by Grok

def set_location(data, server_data=None, from_id=None, connected_cmd=None):
	return {"SET": {"location": {"x": data['x'], "y": data['y']}}}

def set_username(data, server_data=None, from_id=None, connected_cmd=None):
	s_data = server_data
	s_keys = list(s_data.keys())
	# Check if username already exists
	for i in range(len(s_keys)):
		client_info = s_data[s_keys[i]]
		if client_info.get("username") == data:
			return {"SEND": {"uuid" : from_id, "message": "USER_EXISTS"}}
	# If not, set the username for this client
	return {"SET": {"username": data}, "SEND" : {"uuid" : from_id, "message" : "SUCCESS"}}

def set_uuid(data, server_data=None, from_id=None, connected_cmd=None):
	s_data = server_data
	s_keys = list(s_data.keys())
	for i in range(len(s_keys)):
		client_info = s_data[s_keys[i]]
		if client_info.get("uuid") == data:
			{"SEND": {"message": "UUID_EXISTS"}}
	return {"SET": {"uuid": data}, "SEND" : {"uuid" : data, "message" : "SUCCESS"}}

def set_player_image(data, server_data=None, from_id=None, connected_cmd=None):
	return {"SET" : {"player_image" : data}}

def kill_player(data, server_data=None, from_id=None, connected_cmd=None):
	target_uuid = data["target_uuid"]
	users = server_data["users"]

	for addr, info in users.items():
		if info.get("uuid") == target_uuid:
			if info.get("role") == "survivor":
				# Mark player as dead
				ret = {
					"SR_SET_USERS": {target_uuid: {"alive": False}},
					"SEND": {"uuid": "*", "func": "player_killed", "target_uuid": target_uuid}
				}

				# Check for game end conditions
				hunters = [u for u in users.values() if u.get("role") == "hunter"]
				survivors_alive = [u for u in users.values() if u.get("role") == "survivor" and u.get("alive", True)]

				if not survivors_alive:
					# All survivors dead → hunter loses? Or maybe everyone loses?
					for u in hunters:
						ret["SEND"] = {"uuid": u.get("uuid"), "func": "game_end", "set_vars": {"current_scene": "end_scene", "won": False}}
					# All survivors lose anyway
					for u in users.values():
						if u.get("role") == "survivor":
							ret.setdefault("SR_SET_USERS", {})[u["uuid"]] = {"alive": False}
					return ret
				elif len(hunters) == 1 and not survivors_alive:
					# Only hunter left alive → hunter wins
					hunter_uuid = hunters[0]["uuid"]
					ret["SEND"] = {"uuid": hunter_uuid, "func": "game_end", "set_vars": {"current_scene": "end_scene", "won": True}}
					for u in users.values():
						if u.get("uuid") != hunter_uuid:
							ret.setdefault("SR_SET_USERS", {})[u["uuid"]] = {"alive": False}
					return ret

				return ret
	return {}


# Edited by Grok - new function for hacking computer
def hack_computer(data, server_data=None, from_id=None, connected_cmd=None):
	obj_uuid = data["obj_uuid"]
	objects = server_data["objects"]
	if obj_uuid in objects and objects[obj_uuid]["type"] == "computer" and objects[obj_uuid]["status"] is None:
		objects[obj_uuid]["status"] = "hacked"
		
		# Check if all computers are hacked
		all_hacked = all(
			obj["status"] == "hacked" 
			for obj in objects.values() 
			if obj["type"] == "computer"
		)
		
		ret = {
			"SR_SET_OBJ": {
				obj_uuid: {"status": "hacked"}
			}
		}
		
		if all_hacked:
			# Open all exits
			exit_updates = {}
			for uuid, obj in objects.items():
				if obj["type"] == "exit":
				    exit_updates[uuid] = {"status": "open"}
			ret["SR_SET_OBJ"] = exit_updates
			ret["SEND"] = {
				"uuid": "*",
				"func": "exits_opened"
			}
		
		return ret
	return {}
def player_exit(data, server_data=None, from_id=None, connected_cmd=None):
	player_uuid = from_id

	if connected_cmd is None:
		print("Error: connected_cmd not provided")
		return {}

	# Find the connection for this player
	player_info = None
	for addr, info in connected_cmd.items():
		if info.get("data", {}).get("uuid") == player_uuid:
			player_info = info
			break

	if not player_info:
		return {}

	output = {
		"SR_DEL_USERS": {},
		"SR_SET_USERS": {},
		"SEND": []
	}

	# Send exit message to the player first
	output["SEND"].append({
		"uuid": player_uuid,
		"set_vars": {"current_scene": "end_scene", "won" : True},
	})

	# Remaining players
	remaining_users = [u for u in connected_cmd.values() if u["data"].get("uuid") != player_uuid]
	hunters = [u for u in remaining_users if u["data"].get("role") == "hunter"]
	survivors_alive = [u for u in remaining_users if u["data"].get("role") == "survivor" and u["data"].get("alive", True)]

	if not survivors_alive:
		for h in hunters:
			output["SEND"].append({
				"uuid": h["data"].get("uuid"),
				"set_vars": {"current_scene": "end_scene", "won" : False},
			})

	output["SR_DEL_USERS"][player_uuid] = "*"

	return output

def __send_init_data(data, server_data=None, from_id=None, connected_cmd=None):
	server_data_keys = list(server_data["users"].keys())
	print(server_data_keys)
	hunter = random.choice(list(server_data_keys))
	maps = os.listdir("maps")
	#load the map so we can send spawn data and obj data
	current_map = random.choice(maps)
	map_path, MAP_CONF = load_map_init(current_map)
	master_dih = {}
	for i in range(len(server_data_keys)):
		conn_addr = server_data_keys[i]
		player_dict = server_data["users"][conn_addr]
		print(player_dict.keys())
		if conn_addr == hunter:
			hunter_spawn = random.choice(get_region_coords(MAP_CONF, "hunter_spawn"))
			master_dih[player_dict["uuid"]] = {"role" : "hunter", "player_image" : player_dict["player_image"], "location" : {"x": hunter_spawn[0], "y" : hunter_spawn[1]}, "alive": True}
		else:
			player_spawn = random.choice(get_region_coords(MAP_CONF, "player_spawn"))
			master_dih[player_dict["uuid"]] = {"role" : "survivor", "player_image": player_dict["player_image"] , "location" : {"x": player_spawn[0], "y" : player_spawn[1]}, "alive": True}
	computer_spawns = list_to_dict("computer", get_region_coords(MAP_CONF, "computer_spawn"))
	locker_spawns = list_to_dict("locker", get_region_coords(MAP_CONF, "locker_spawn"))
	exit_spawn = list_to_dict("exit", get_region_coords(MAP_CONF, "exit_spawn"))
	obj_dict = {}
	obj_dict.update(computer_spawns)
	obj_dict.update(locker_spawns)
	obj_dict.update(exit_spawn)
	ret_val = {
		"SR_SET_USERS": master_dih,
		"SR_SET_OBJ" : obj_dict,
		"SEND" : {"player_data" : master_dih, "map" : current_map, "obj" : obj_dict, "uuid" : "*", "func": "__send_init_data"}
	}
	print(ret_val)
	return ret_val
