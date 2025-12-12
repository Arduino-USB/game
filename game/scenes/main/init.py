import pygame
from scenes.main.map import load_map_init
from io import BytesIO
import base64


def init(client_data=None):
	print("INIT MAIN")
	client_data = load_map_init(client_data=client_data)
	client_data.update({"player_image" : pygame.image.load(client_data["PLAYER_IMAGE_PATH"]).convert_alpha()})
	
	
	client_data["player_images"] = {}
	
		
	player_data = client_data["init_player_data"]	
	all_uuids = list(player_data.keys()) 
	
	for i in range(len(player_data)):
	    b64_str = player_data[all_uuids[i]]["player_image"]  # <-- access dict first
	    player_image = BytesIO(base64.b64decode(b64_str))
	    client_data["player_images"][all_uuids[i]] = pygame.image.load(player_image)	
	
	print(f"Loaded player images:\n{client_data["player_images"]}")
	
	del[client_data["init_player_data"]]	
	
	
	return client_data
