import pygame
from scenes.main.map import load_map_init
from io import BytesIO
import base64

# Edited by Grok

def init(client_data=None):
	print("INIT MAIN")
	client_data = load_map_init(client_data=client_data)
	client_data.update({"player_image" : pygame.image.load(client_data["PLAYER_IMAGE_PATH"]).convert_alpha()})
	client_data["player_images"] = {}
	client_data["roles"] = {}
	player_data = client_data["init_player_data"]
	print("======InitPlayerData======")
	print(player_data.keys())
	all_uuids = list(player_data.keys())
	for i in range(len(player_data)):
		b64_str = player_data[all_uuids[i]]["player_image"] # <-- access dict first
		player_image = BytesIO(base64.b64decode(b64_str))
		client_data["player_images"][all_uuids[i]] = pygame.image.load(player_image)
		client_data["roles"][all_uuids[i]] = player_data[all_uuids[i]]["role"]
		print("======InitPlayerImagesLoaded======")
		print(client_data["player_images"].keys())
		print(f"Loaded player images:\n{client_data['player_images']}")
	# set current player player_pos
	player_id = client_data["uuid"]
	client_data["player_pos"]["x"] = player_data[player_id]["location"]["x"]
	client_data["player_pos"]["y"] = player_data[player_id]["location"]["y"]
	client_data["role"] = player_data[player_id]["role"]
	client_data["alive"] = player_data[player_id].get("alive", True)  # Edited by Grok
	client_data["computer_locked"] = pygame.image.load("computer_locked.png")
	client_data["computer_hacked"] = pygame.image.load("computer_hacked.png")
	client_data["locker"] = pygame.image.load("locker.png")
	client_data["exit"] = pygame.image.load("exit.png")  # Edited by Grok - need exit image
	del client_data["init_player_data"]
	return client_data
