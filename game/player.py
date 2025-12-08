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

def get_region(x, y):
	"""Return the name of the region at (x, y) or None if no region."""
	for cell in MAP_CONF.get("cells", []):
		# Compute cell boundaries in world coordinates
		cell_x = cell["x"] * MAP_CONF["tileSize"]
		cell_y = cell["y"] * MAP_CONF["tileSize"]

		# Check if (x, y) is inside this cell
		if cell_x <= x < cell_x + MAP_CONF["tileSize"] and cell_y <= y < cell_y + MAP_CONF["tileSize"]:
			# Coordinates relative to cell
			rel_x = x - cell_x
			rel_y = y - cell_y
			# Check each region in the cell
			for region in cell.get("regions", []):
				if region["x1"] <= rel_x <= region["x2"] and region["y1"] <= rel_y <= region["y2"]:
					return region["name"]
	return None

def grid(p):
	if p >= 0:
		return p // 1000
	else:
		return -((abs(p) - 1) // 1000 + 1)



def norm_path(unix_path):
	parts = unix_path.strip("/").split("/")  # split by /
	return os.path.join(*parts)


def get_cell(x, y):
	for cell in MAP_CONF.get("cells", []):
		if cell.get("x") == x and cell.get("y") == y:
			return cell

	return None

def get_coords():
	pass

def load_current_map(x,y, scale, screen):
	global X, Y, CURRENT_BLOCK
	x_ = grid(x)
	y_ = grid(y)
	
	if X == x_ and Y == y_:
		screen.blit(CURRENT_BLOCK, (0,0))	
		return None
	
	print("Notequal")
	print(f"X : {x_}, Y: {y_}")
	cell = get_cell(x_, y_)
	
	CURRENT_BLOCK = pygame.image.load(os.path.join(map_path.name, norm_path(cell["image"]))).convert()
	
	pygame.transform.scale(CURRENT_BLOCK, (scale, scale))
	screen.blit(CURRENT_BLOCK, (0,0))
	
	
def load_map_init():
	global MAP_CONF
	with zipfile.ZipFile(os.path.join("maps", f"{CURRENT_MAP}.zip"), "r") as zip_ref:
		zip_ref.extractall(map_path.name)
	
	with open(os.path.join(f"{map_path.name}", "config.json")) as f:
		MAP_CONF = json.load(f)
	
	print(f"MAP_CONF: {MAP_CONF}")
		
	
	
	


def try_move(player_pos, target_x, target_y):
	"""Attempt to move player to (target_x, target_y). Returns True if moved."""
	if get_cell(grid(target_x), grid(target_y)) is None:
		return False
		
	if get_region(target_x, target_y+ 100) == "no_walk_zone":
		return False
	player_pos["x"] = target_x
	player_pos["y"] = target_y
	return True


def handle_input(player_pos):
    keys = pygame.key.get_pressed()
    moved = False

    # Right / Left
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        moved |= try_move(player_pos, player_pos["x"] + WALKSPEED, player_pos["y"])
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        moved |= try_move(player_pos, player_pos["x"] - WALKSPEED, player_pos["y"])

    # Down / Up
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        moved |= try_move(player_pos, player_pos["x"], player_pos["y"] + WALKSPEED)
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        moved |= try_move(player_pos, player_pos["x"], player_pos["y"] - WALKSPEED)

    return moved



def simplify_coords(x, y):
	subtract_by_x = int(x / 1000) * 1000
	subtract_by_y = int(y / 1000) * 1000
	
	return x - subtract_by_x, y - subtract_by_y

def filter_server_data(server_data):
	pass
	

def draw_players(screen, server_data, player_image, font, scale, client_data):
	
	load_current_map(client_data["x"], client_data["y"], scale, screen)
	
	for user_id, current_user_dict in server_data.items():
		if "location" in current_user_dict:
		
			
			#print(f" SCALE: {scale}, FONT_SIZE : ({font.get_height()}, {font.get_linesize()}), PLAYER_SIZE: {player_image.get_size()}")
			 
			
			location = current_user_dict["location"]
			username_surface = font.render(current_user_dict["username"], True, (0, 0, 0))
			new_w = int(username_surface.get_width() * scale)
			new_h = int(username_surface.get_height() * scale)

			username_surface = pygame.transform.scale(username_surface, (new_w, new_h))
			graph_x, graph_y = simplify_coords(location["x"], location["y"])
			
			player_rect = player_image.get_rect(topleft=(graph_x * scale, graph_y * scale))
            # TEXT RECT
			text_rect = username_surface.get_rect()

			# Center the bottom of the text at the top center of the player
			text_rect.midbottom = player_rect.midtop

			# Move it up a little so it doesn't touch the head
			text_rect.y -= 25

			
			
			
			screen.blit(username_surface, text_rect)
			
			screen.blit(player_image, player_rect)


