import os
import pygame

def norm_path(unix_path):
	parts = unix_path.strip("/").split("/")  
	return os.path.join(*parts)

def load_assets(w, h, client_data=None):
	display = pygame.display.Info()
	client_data["CURRENT_W"] = display.current_w
	client_data["CURRENT_H"] = display.current_h
	
	if client_data["LAST_KNOWN_WH"] == (w, h):
		return client_data, None

	if w != client_data["CURRENT_W"] and h != client_data["CURRENT_H"]:
		return client_data, None
	
	
	#print("load_assets is not returning None this time")
	scale = client_data["CURRENT_W"] / 1000 
	
	LAST_KNOWN_WH = w, h

	player_image = pygame.transform.scale(client_data["player_image"], (client_data["CURRENT_W"] / 10, client_data["CURRENT_H"] / 10))
	font = pygame.font.Font(None, int(32 / scale))

	return client_data.update({"player_image" : player_image, "font" : font, "scale" : scale, "player_width" : player_image.get_width(), "player_height" : player_image.get_height, "LAST_KNOWN_WH": LAST_KNOWN_WH })

