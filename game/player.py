# player.py
import pygame
from settings import WALKSPEED, PLAYER_IMAGE_PATH
import tempfile
import zipfile
import os
import json

CURRENT_MAP = "test"
MAP_CONF = None
map_path = tempfile.TemporaryDirectory()
X = None
Y = None
CURRENT_BLOCK = None
def norm_path(path):
	parts = unix_path.strip("/").split("/")  # split by /
	return os.path.join(*parts)


def get_cell(x, y):
	for cell in MAP_CONF.get("cells", []):
		if cell.get("x") == x and cell.get("y") == y:
			return cell
	return None

def get_coords():
	pass

def load_current_map(x,y, scale):
	global X, Y, CURRENT_BLOCK
	x_ = int(x / 1000)
	y_ = int(y / 1000)
	
	if X == x_ and Y == y_:
		screen.blit(CURRENT_BLOCK, (0,0))	
			
		
	cell = get_cell(X, Y)
	
	CURRENT_BLOCK = pygame.image.load(norm_path(cell["image"])).convert()
	
	pygame.transform.scale(CURRENT_BLOCK, (scale, scale))
	screen.blit(CURRENT_BLOCK, (0,0))
	
	
def load_map_init():
	global MAP_CONF
	with zipfile.ZipFile(os.path.join("maps", f"{CURRENT_MAP}.zip"), "r") as zip_ref:
		zip_ref.extractall(map_path.name)
	
	with open(os.path.join(f"{map_path.name}", "config.json")) as f:
		MAP_CONF = json.load(f)
	
	print(f"MAP_CONF: {MAP_CONF}")
		
	
	
	


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



def draw_players(screen, server_data, player_image, font, scale, client_data):
	
	load_current_map(client_data["x"], client_data["y"], scale)
	
	for user_id, current_user_dict in server_data.items():
		if "location" in current_user_dict:
		
			
			#print(f" SCALE: {scale}, FONT_SIZE : ({font.get_height()}, {font.get_linesize()}), PLAYER_SIZE: {player_image.get_size()}")
			 
			
			location = current_user_dict["location"]
			username_surface = font.render(current_user_dict["username"], True, (0, 0, 0))
			new_w = int(username_surface.get_width() * scale)
			new_h = int(username_surface.get_height() * scale)

			username_surface = pygame.transform.scale(username_surface, (new_w, new_h))

			
			player_rect = player_image.get_rect(topleft=(location["x"] * scale, location["y"] * scale))
            # TEXT RECT
			text_rect = username_surface.get_rect()

			# Center the bottom of the text at the top center of the player
			text_rect.midbottom = player_rect.midtop

			# Move it up a little so it doesn't touch the head
			text_rect.y -= 25

			
			
			
			screen.blit(username_surface, text_rect)
			
			screen.blit(player_image, player_rect)


