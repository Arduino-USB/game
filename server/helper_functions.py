import zipfile
import os 
import uuid
import tempfile
import json

import uuid

def list_to_dict(name, coords_list):
	master_dih = {}

	for i in range(len(coords_list)):
		x, y = coords_list[i]
		obj_uuid = str(uuid.uuid4())

		master_dih[obj_uuid] = {
			"type": name,
			"uuid": obj_uuid,
			"status" : None,
			"location": {
				"x": x,
				"y": y
			}
		}

	return master_dih


def norm_path(p):
	parts = p.strip("/").split("/")
	return os.path.join(*parts)

def load_map_init(map_name):
	
	map_path = tempfile.TemporaryDirectory()
	with zipfile.ZipFile(os.path.join("maps", map_name), "r") as zip_ref:
		zip_ref.extractall(map_path.name)
	
	with open(os.path.join(map_path.name, "config.json")) as f:
		MAP_CONF = json.load(f)

	return map_path, MAP_CONF

def get_region_coords(map_conf, region_name):
	coords = []

	tile_size = map_conf.get("tileSize", 1000)

	for cell in map_conf.get("cells", []):
		cell_x = cell.get("x", 0)
		cell_y = cell.get("y", 0)

		for region in cell.get("regions", []):
			if region.get("name") == region_name:
				x1 = region.get("x1", 0)
				x2 = region.get("x2", 0)
				y1 = region.get("y1", 0)
				y2 = region.get("y2", 0)

				# Ensure x1 <= x2, y1 <= y2
				x_min, x_max = min(x1, x2), max(x1, x2)
				y_min, y_max = min(y1, y2), max(y1, y2)

				# Use the top-left corner for placement
				abs_x = cell_x * tile_size + x_min
				abs_y = cell_y * tile_size + y_min

				# Or center if you prefer
				# abs_x = cell_x * tile_size + (x_min + x_max) // 2
				# abs_y = cell_y * tile_size + (y_min + y_max) // 2

				coords.append((abs_x, abs_y))

	return coords



