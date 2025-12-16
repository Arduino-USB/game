import random
import os
from helper_functions import load_map_init, norm_path, list_to_dict, get_region_coords

# Edited by Grok

def set_location(data, server_data=None, from_id=None):
	return {"SET": {"location": {"x": data['x'], "y": data['y']}}}

def set_username(data, server_data=None, from_id=None):
	s_data = server_data
	s_keys = list(s_data.keys())
	# Check if username already exists
	for i in range(len(s_keys)):
		client_info = s_data[s_keys[i]]
		if client_info.get("username") == data:
			return {"SEND": {"uuid" : from_id, "message": "USER_EXISTS"}}
	# If not, set the username for this client
	return {"SET": {"username": data}, "SEND" : {"uuid" : from_id, "message" : "SUCCESS"}}

def set_uuid(data, server_data=None, from_id=None):
	s_data = server_data
	s_keys = list(s_data.keys())
	for i in range(len(s_keys)):
		client_info = s_data[s_keys[i]]
		if client_info.get("uuid") == data:
			{"SEND": {"message": "UUID_EXISTS"}}
	return {"SET": {"uuid": data}, "SEND" : {"uuid" : data, "message" : "SUCCESS"}}

def set_player_image(data, server_data=None, from_id=None):
	return {"SET" : {"player_image" : data}}

# Edited by Grok - new function for killing
def kill_player(data, server_data=None, from_id=None):
	target_uuid = data["target_uuid"]
	users = server_data["users"]
	for addr, info in users.items():
		if info.get("uuid") == target_uuid:
			if info.get("role") == "survivor":
				return {
				    "SR_SET_USERS": {
				        target_uuid: {"alive": False}
				    },
				    "SEND": {
				        "uuid": "*",
				        "func": "player_killed",
				        "target_uuid": target_uuid
				    }
				}
	return {}

# Edited by Grok - new function for hacking computer
def hack_computer(data, server_data=None, from_id=None):
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

# Edited by Grok - new function for exiting
def player_exit(data, server_data=None, from_id=None):
	player_uuid = from_id
	users = server_data["users"]
	for addr, info in users.items():
		if info.get("uuid") == player_uuid:
			if info.get("alive", True) == False:
				# Dead players can't win
				return {
				    "SEND": {
				        "uuid": player_uuid,
				        "func": "game_end",
						"set_vars": {"current_scene" : "end_scene", "end_scene_message" : "You Lost!"}
				    },
					"SR_DEL_USERS" : {player_uuid : "*"}
			
				}
			else:
				return {
				    "SEND": {
						"uuid" : player_uuid,
				        "func": "game_end",
				        "set_vars": {"current_scene" : "end_scene", "end_scene_message" : "You Won!"}
				    },
					"SR_DEL_USERS" : {player_uuid : "*"}
				}
	return {}

def __send_init_data(data, server_data=None, from_id=None):
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
