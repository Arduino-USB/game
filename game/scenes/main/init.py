import pygame

def init(client_data=None):
	return client_data.update({"player_image" : pygame.image.load(client_data["PLAYER_IMAGE_PATH"]).convert()})
