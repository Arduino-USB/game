import random
import os
from helper_functions import load_map_init, norm_path, list_to_dict, get_region_coords


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
			master_dih[player_dict["uuid"]] = {"role" : "hunter", "player_image" : player_dict["player_image"], "location" : {"x": hunter_spawn[0], "y" : hunter_spawn[1]}}	
		else:
			player_spawn = random.choice(get_region_coords(MAP_CONF, "player_spawn"))
			master_dih[player_dict["uuid"]] = {"role" : "survivor", "player_image": player_dict["player_image"] , "location" : {"x": player_spawn[0], "y" : player_spawn[1]}}
			
		
		
	computer_spawns = list_to_dict("computer", get_region_coords(MAP_CONF, "computer_spawn"))
	locker_spawns = list_to_dict("locker", get_region_coords(MAP_CONF, "locker_spawn"))
	exit_spawn = list_to_dict("exit", get_region_coords(MAP_CONF, "exit_spawn"))			
	
	obj_dict = {}
	obj_dict.update(computer_spawns)	
	obj_dict.update(locker_spawns)
	obj_dict.update(exit_spawn)	
		
				
	
	ret_val =  {
		"SR_SET_OBJ" : obj_dict, 
		"SR_SET_USERS": master_dih, 
		"SEND" : {"player_data" : master_dih, "map" : current_map, "obj" : obj_dict, "uuid" : "*"}
	}
		
	print(ret_val)	
		
	return ret_val

