# player.py
import pygame
from settings import WALKSPEED, PLAYER_IMAGE_PATH

player_image = pygame.image.load(PLAYER_IMAGE_PATH).convert()

def handle_input(player_pos):
	keys = pygame.key.get_pressed()
	moved = False
	if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
		player_pos["x"] += WALKSPEED
		moved = True
	if keys[pygame.K_LEFT] or keys[pygame.K_a]:
		player_pos["x"] -= WALKSPEED
		moved = True
	if keys[pygame.K_DOWN] or keys[pygame.K_s]:
		player_pos["y"] += WALKSPEED
		moved = True
	if keys[pygame.K_UP] or keys[pygame.K_w]:
		player_pos["y"] -= WALKSPEED
		moved = True
	return moved

def draw_players(surface, server_data):
	for user_id, current_user_dict in server_data.items():
		if "location" in current_user_dict:
			location = current_user_dict["location"]
			surface.blit(player_image, (location["x"], location["y"]))

