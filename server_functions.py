

def set_location(data, server_data=None):
	return {"SET": {"location": {"x": data['x'], "y": data['y']}}}


def set_username(data, server_data=None):
	s_data = server_data
	s_keys = list(s_data.keys())
	
	# Check if username already exists
	for i in range(len(s_keys)):
		client_info = s_data[s_keys[i]]
		if client_info.get("username") == data:
			return {"SEND": {"error": "USER_EXISTS"}}
	
	# If not, set the username for this client
	return {"SET": {"username": data, "message": "SUCCESS"}}


def set_uuid(data, server_data=None):
	s_data = server_data
	s_keys = list(s_data.keys())
	
	for i in range(len(s_keys)):
		client_info = s_data[s_keys[i]]
		if client_info.get("uuid") == data:
			return {"SEND": {"error": "UUID_EXISTS"}}
	
	return {"SET": {"uuid": data}, "SEND" : {"uuid" : data, "message" : "SUCCESS"}}

