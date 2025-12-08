# main.py
import pygame

pygame.init()
pygame.display.set_caption("mypygameapp")

from settings import FPS
import scenes

clock = pygame.time.Clock()
running = True

current_scene = "setup_scene"

# Start with square window
win = pygame.display.set_mode((1000, 1000), pygame.RESIZABLE)

# === NEW: Debounce logic for resize ===
last_resize_time = 0
RESIZE_DELAY = 1000  # milliseconds (1 second)

def force_square_window():
	global win
	w, h = win.get_size()
	new_size = min(w, h)
	if w != new_size or h != new_size:
		win = pygame.display.set_mode((new_size, new_size), pygame.RESIZABLE)

# =================================================================
while running:
	current_time = pygame.time.get_ticks()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		elif event.type == pygame.VIDEORESIZE:
			# User is dragging → just accept the new size, do nothing yet
			last_resize_time = current_time
			# (Optional) you can even remove the line below if you want raw size
			# win is already updated by pygame automatically on VIDEORESIZE

	# === Check if user stopped resizing for 1 second ===
	if last_resize_time != 0 and (current_time - last_resize_time >= RESIZE_DELAY):
		force_square_window()
		last_resize_time = 0  # reset so it only happens once

	# Your original scene logic — unchanged
	output = getattr(scenes, current_scene)()
	if output is not None:
		current_scene = output

	pygame.display.flip()
	clock.tick(FPS)

pygame.quit()
