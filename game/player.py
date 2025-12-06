# player.py
import pygame
from settings import WALKSPEED, PLAYER_IMAGE_PATH

player_image = pygame.image.load(PLAYER_IMAGE_PATH).convert()
player_image.set_colorkey((255, 255, 255))
player_image = pygame.transform.scale(player_image, (100, 100))



font = pygame.font.Font(None, 32)

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

def draw_players(screen, server_data):
	print(f"Draw players here, this is the server data\n{server_data}")
	for user_id, current_user_dict in server_data.items():
		if "location" in current_user_dict:
			
			location = current_user_dict["location"]
			username_surface = font.render(current_user_dict["username"], True, (0, 0, 0))
			
			player_rect = player_image.get_rect(topleft=(location["x"], location["y"]))
            # TEXT RECT
			text_rect = username_surface.get_rect()

			# Center the bottom of the text at the top center of the player
			text_rect.midbottom = player_rect.midtop

			# Move it up a little so it doesn't touch the head
			text_rect.y -= 25

			
			
			
			screen.blit(username_surface, text_rect)
			
			screen.blit(player_image, player_rect)

