import os
import pygame
import math

def norm_path(unix_path):
	parts = unix_path.strip("/").split("/")  
	return os.path.join(*parts)

def load_assets(w, h, client_data=None):
	display = pygame.display.Info()
	client_data["CURRENT_W"] = display.current_w
	client_data["CURRENT_H"] = display.current_h

	# Skip if size hasn't actually changed
	if client_data["LAST_KNOWN_WH"] == (w, h):
		return client_data, None

	if w != client_data["CURRENT_W"] and h != client_data["CURRENT_H"]:
		return client_data, None

	scale = client_data["CURRENT_W"] / 1000
	LAST_KNOWN_WH = (w, h)

	# =========================
	# FIXED PLAYER IMAGE SCALING
	# =========================
	player_images = client_data.get("player_images", {})

	for uuid, image in player_images.items():
		player_images[uuid] = pygame.transform.scale(
			image,
			(
				int(client_data["CURRENT_W"] / 15),
				int(client_data["CURRENT_H"] / 15)
			)
		)

	# =========================
	# OTHER ASSETS
	# =========================
	client_data["computer_locked"] = pygame.transform.scale(
		client_data["computer_locked"],
		(
			int(client_data["CURRENT_W"] / 10),
			int(client_data["CURRENT_H"] / 10)
		)
	)

	client_data["computer_hacked"] = pygame.transform.scale(
		client_data["computer_hacked"],
		(
			int(client_data["CURRENT_W"] / 10),
			int(client_data["CURRENT_H"] / 10)
		)
	)

	client_data["locker"] = pygame.transform.scale(
		client_data["locker"],
		(
			int(client_data["CURRENT_W"] / 10),
			int(client_data["CURRENT_H"] / 10)
		)
	)

	client_data["exit"] = pygame.transform.scale(
		client_data["exit"],
		(
			int(client_data["CURRENT_W"] / 10),
			int(client_data["CURRENT_H"] / 10)
		)
	)

	# =========================
	# FONT
	# =========================
	client_data["font"] = pygame.font.Font(None, int(32 / scale))

	client_data["LAST_KNOWN_WH"] = LAST_KNOWN_WH
	return client_data, True




def get_object_player_is_on(objects, player_topleft, player_size):
	px, py = player_topleft
	pw, ph = player_size

	# Player center
	player_cx = px + pw / 2
	player_cy = py + ph / 2

	# Use the larger dimension as tolerance
	radius = max(pw, ph)

	for obj in objects.values():
		ox = obj["location"]["x"]
		oy = obj["location"]["y"]

		dx = player_cx - ox
		dy = player_cy - oy
		dist = math.hypot(dx, dy)

		if dist <= radius:
			return {
				"type": obj["type"],
				"status": obj["status"]
			}

	return None