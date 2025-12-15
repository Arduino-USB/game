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

	player_images = client_data["player_images"]
	player_uuids = list(player_images.keys())
	for i in range(len(player_images)):
		current_image = player_images[player_uuids[i]]
		current_image = pygame.transform.scale(current_image, (client_data["CURRENT_W"] / 15, client_data["CURRENT_H"] / 15))
		client_data.update({"player_images" : {player_uuids[i] : current_image}})

	client_data["computer_locked"] = pygame.transform.scale(client_data["computer_locked"], (client_data["CURRENT_W"] / 10, client_data["CURRENT_H"] / 10))
	client_data["computer_hacked"] = pygame.transform.scale(client_data["computer_hacked"], (client_data["CURRENT_W"] / 10, client_data["CURRENT_H"] / 10))
	client_data["locker"] = pygame.transform.scale(client_data["locker"], (client_data["CURRENT_W"] / 10, client_data["CURRENT_H"]  / 10))
	client_data["exit"] = pygame.transform.scale(client_data["exit"], (client_data["CURRENT_W"] / 10, client_data["CURRENT_H"] / 10))

	font = pygame.font.Font(None, int(32 / scale))

	client_data.update({"LAST_KNOWN_WH": LAST_KNOWN_WH})
	return client_data, True

