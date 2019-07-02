
from game.game import Game

import math

def count_legal_two_steps(game: Game, pos: list):
	count = 0
	for move in game.get_legal_moves():
		hist_move = game.play(move, 0)
		count += len(game.get_legal_moves())
		game.undo(hist_move)
	
	return count

def count_adj(game: Game, pos: list, color: int):
	count_match = 0
	count_mismatch = 0
	count_wall = 0

	for conn in game.connect_matrix:
		adj_pos = [pos[0] + conn[0], pos[1] + conn[1]]
		if game.is_inside(adj_pos):
			if game.board[adj_pos[0], adj_pos[1]] == color:
				count_match += 1
			else:
				count_mismatch += 1
		else:
			count_wall += 1
	return count_match, count_mismatch, count_wall

# count diagonally connected tiles (not obstructed)
def count_diag(game: Game, pos: list, cluster: list, color: int):
	diag_unobstructed_count = 0
	diag_half_obstructed_count = 0

	for dx in [-1, 1]:
		for dy in [-1, 1]:
			adj_pos = [pos[0] + dx, pos[1] + dy]

			# check diagonal (same color but not in cluster)
			if (
				game.is_inside(adj_pos)
				 and adj_pos not in cluster
				 and game.board[adj_pos[0], adj_pos[1]] == color
			):
				# check obstruction
				obstruction = 0
				if game.board[pos[0] + dx, pos[1]] != 0:
					obstruction += 1
				
				if game.board[pos[0], pos[1] + dy] != 0:
					obstruction += 1
				
				if obstruction == 0:
					diag_unobstructed_count += 1
				elif obstruction == 1:
					diag_half_obstructed_count += 1

	return diag_unobstructed_count, diag_half_obstructed_count

def count_obstructing(game: Game, pos: list, cluster: list, color: int):
	diag_obstruct_count = 0

	for dx in [-1, 1]:
		for dy in [-1, 1]:
			adj_pos = [pos[0] + dx, pos[1] + dy]

			# check diagonal (not in cluster)
			if (
				game.is_inside(adj_pos)
				 and adj_pos not in cluster
			):
				# d  v
				# h  b
				h_color = game.board[adj_pos[0], pos[1]]
				v_color = game.board[pos[0], adj_pos[1]]
				d_color = game.board[adj_pos[0], adj_pos[1]]
				if (
					# diag can be connected from base but got blocked
					h_color == v_color
					and h_color != color
					and d_color != 0
					and h_color != d_color
				):
					diag_obstruct_count += 1
	
	return diag_obstruct_count

def count_liberties(game: Game, cluster: list, color: int):
	# find all tiles adjacent to cluster
	adj_tiles = []
	for tile in cluster:
		for conn in game.connect_matrix:
			adj_pos = [tile[0] + conn[0], tile[1] + conn[1]]
			if game.is_inside(adj_pos) and adj_pos not in cluster and adj_pos not in adj_tiles:
				adj_tiles.append(adj_pos)
	
	count_liberty = 0
	count_blocked = 0
	for adj_tile in adj_tiles:
		if game.board[adj_tile[0], adj_tile[1]] == 0:
			count_liberty += 1
		else:
			count_blocked += 1
	
	return count_liberty, count_blocked

def eval_move(game: Game, target_pos: list, tile: int):
	color = game.tile_queue[tile]
	cluster = game.get_connected_tiles(target_pos, color)
	diag_unobstructed_count, diag_half_obstructed_count = count_diag(game, target_pos, cluster, color)
	diag_obstructing_count = count_obstructing(game, target_pos, cluster, color)
	count_match, count_mismatch, count_wall = count_adj(game, target_pos, color)

	score = (
		len(cluster)
		+ 0.75 * diag_unobstructed_count
		+ 0.5 * diag_half_obstructed_count
#		- 0.25 * count_mismatch
#		- 2 * diag_obstructing_count
	)

	# bonus for connecting clusters with low liberty
	#count_liberty, count_blocked = count_liberties(game, lucster, color)
	return score
