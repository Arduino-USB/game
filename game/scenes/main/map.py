import pygame
import tempfile
import zipfile
import os
import json

from scenes.main.helper_functions import norm_path

def load_map_init(client_data=None):
	
	client_data["map_path"] = tempfile.TemporaryDirectory()
	with zipfile.ZipFile(os.path.join("maps", f"{client_data['CURRENT_MAP']}.zip"), "r") as zip_ref:
		zip_ref.extractall(client_data["map_path"].name)
	
	with open(os.path.join(f"{client_data['map_path'].name}", "config.json")) as f:
		client_data["MAP_CONF"] = json.load(f)

	return client_data
	

def get_region(client_data=None):
	
	x = client_data["player_pos"]["x"]
	y = client_data["player_pos"]["y"]
	"""Return the name of the region the player touches, or None if no region."""
	for cell in client_data["MAP_CONF"].get("cells", []):
		cell_x = cell["x"] * client_data["MAP_CONF"]["tileSize"]
		cell_y = cell["y"] * client_data["MAP_CONF"]["tileSize"]

		# Check if player's bbox intersects this cell
		if x + client_data["player_width"] >= cell_x and x <= cell_x + client_data["MAP_CONF"]["tileSize"] and \
		   y + client_data["player_height"] >= cell_y and y <= cell_y + client_data["MAP_CONF"]["tileSize"]:
			# Player coordinates relative to cell
			player_x1 = x - cell_x
			player_y1 = y - cell_y
			player_x2 = player_x1 + client_data["player_width"] 
			player_y2 = player_y1 + client_data["player_height"] 

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



def get_cell(x, y, client_data=None):
	for cell in client_data["MAP_CONF"].get("cells", []):
		if cell.get("x") == x and cell.get("y") == y:
			return cell
	return None


def load_current_map(x, y, client_data=None):

	x = grid(x)
	y = grid(y)
	
	if client_data["BLOCK_X"] == x and client_data["BLOCK_Y"] == y and client_data["CURRENT_BLOCK"] is not None and client_data["CURRENT_BLOCK"].get_size() == (client_data["scale"], client_data["scale"]):
		client_data["screen"].blit(client_data["CURRENT_BLOCK"], (0,0))	
		return client_data, None
	
	client_data["BLOCK_X"], client_data["BLOCK_Y"] = x, y
	cell = get_cell(x, y, client_data=client_data)
	
	current_image_path = os.path.join(client_data["map_path"].name, norm_path(cell["image"]))
	
	#print(f"CUrrent map path: {current_image_path}, Scale: {scale}")	
	
	client_data["CURRENT_BLOCK"] = pygame.image.load(current_image_path).convert()
	client_data["CURRENT_BLOCK"] = pygame.transform.scale(client_data["CURRENT_BLOCK"], (1000 * client_data["scale"], 1000 * client_data["scale"]))
	client_data["screen"].blit(client_data["CURRENT_BLOCK"], (0,0))
	
	return client_data, True
