import random

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
	server_data_keys = list(server_data.keys())
	hunter = random.choice(list(server_data_keys))
	
	master_dih = {}
	for i in range(len(server_data_keys)):
		
		conn_addr = server_data_keys[i]
		player_dict = server_data[conn_addr]
		
		if conn_addr == hunter:
			master_dih.update({player_dict["uuid"] : {"role" : "hunter", "player_image" : player_dict["player_image"]}})	
		else:
			master_dih.update({player_dict["uuid"] : {"role" : "survivor"}})
	
	return {"SR_SET": master_dih, "SEND" : master_dih}	
