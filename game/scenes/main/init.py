import pygame
from scenes.main.map import load_map_init

def init(client_data=None):
	print("INIT MAIN")
	client_data = load_map_init(client_data=client_data)
	client_data.update({"player_image" : pygame.image.load(client_data["PLAYER_IMAGE_PATH"]).convert()})
	return client_data
