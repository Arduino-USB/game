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

	for cell in map_conf.get("cells", []):
		for region in cell.get("regions", []):
			if region.get("name") == region_name:
				# Compute center of the rectangle as representative point
				x = (region.get("x1", 0) + region.get("x2", 0)) // 2
				y = (region.get("y1", 0) + region.get("y2", 0)) // 2
				coords.append((x, y))

	return coords

