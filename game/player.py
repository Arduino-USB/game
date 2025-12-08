# player.py
import pygame
from settings import WALKSPEED, PLAYER_IMAGE_PATH
import tempfile
import zipfile
import os
import json

CURRENT_MAP = "goodmap"
MAP_CONF = None
map_path = tempfile.TemporaryDirectory()
X = None
Y = None
CURRENT_BLOCK = None

def get_region(x, y, width, height):
	"""Return the name of the region the player touches, or None if no region."""
	for cell in MAP_CONF.get("cells", []):
		cell_x = cell["x"] * MAP_CONF["tileSize"]
		cell_y = cell["y"] * MAP_CONF["tileSize"]

		# Check if player's bbox intersects this cell
		if x + width >= cell_x and x <= cell_x + MAP_CONF["tileSize"] and \
		   y + height >= cell_y and y <= cell_y + MAP_CONF["tileSize"]:
			# Player coordinates relative to cell
			player_x1 = x - cell_x
			player_y1 = y - cell_y
			player_x2 = player_x1 + width
			player_y2 = player_y1 + height

			for region in cell.get("regions", []):
				# Check if player bbox overlaps region bbox
				if not (player_x2 < region["x1"] or player_x1 > region["x2"] or
						player_y2 < region["y1"] or player_y1 > region["y2"]):
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


def load_current_map(x, y, scale, screen):
	global X, Y, CURRENT_BLOCK
	x_ = grid(x)
	y_ = grid(y)
	
	if X == x_ and Y == y_ and CURRENT_BLOCK is not None and CURRENT_BLOCK.get_size() == (scale, scale):
		screen.blit(CURRENT_BLOCK, (0,0))	
		return None
	
	X, Y = x_, y_
	cell = get_cell(x_, y_)
	
	current_image_path = os.path.join(map_path.name, norm_path(cell["image"]))
	
	#print(f"CUrrent map path: {current_image_path}, Scale: {scale}")	
	
	CURRENT_BLOCK = pygame.image.load(current_image_path).convert()
	CURRENT_BLOCK = pygame.transform.scale(CURRENT_BLOCK, (1000 * scale, 1000 * scale))
	screen.blit(CURRENT_BLOCK, (0,0))

	
	
def load_map_init():
	global MAP_CONF
	with zipfile.ZipFile(os.path.join("maps", f"{CURRENT_MAP}.zip"), "r") as zip_ref:
		zip_ref.extractall(map_path.name)
	
	with open(os.path.join(f"{map_path.name}", "config.json")) as f:
		MAP_CONF = json.load(f)
	
	#print(f"MAP_CONF: {MAP_CONF}")
		
	
	
	


def try_move(player_pos, target_x, target_y, player_width, player_height):
	
	
	"""Attempt to move player to (target_x, target_y). Returns True if moved."""
	if get_cell(grid(target_x), grid(target_y)) is None:
		#print(f"try_move: grid doesnt exist {grid(target_x)}, {grid(target_y)}")
		return False
		
	if get_region(target_x , target_y, player_width, player_height) == "no_walk_zone":
		#print("No walk zone here!!")
		return False
	player_pos["x"] = target_x
	player_pos["y"] = target_y
	
	
	return True


def handle_input(player_pos, player_width, player_height):
    keys = pygame.key.get_pressed()
    moved = False

    # Right / Left
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        moved |= try_move(player_pos, player_pos["x"] + WALKSPEED, player_pos["y"], player_width, player_height)
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        moved |= try_move(player_pos, player_pos["x"] - WALKSPEED, player_pos["y"], player_width, player_height)

    # Down / Up
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        moved |= try_move(player_pos, player_pos["x"], player_pos["y"] + WALKSPEED, player_width, player_height)
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        moved |= try_move(player_pos, player_pos["x"], player_pos["y"] - WALKSPEED, player_width, player_height)

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

	
load_map_init()

