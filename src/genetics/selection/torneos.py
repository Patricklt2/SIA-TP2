import random


def tournament_selection(population, num_selected, k=3):
	"""Select `num_selected` individuals using tournament selection.

	Args:
		population (list): list of Individuals (each must have a `.fitness` attribute).
		num_selected (int): number of individuals to select.
		k (int): tournament size (number of competitors per tournament).

	Returns:
		list: selected individuals (may contain duplicates if population is small).
	"""
	if not population or num_selected <= 0:
		return []

	selected = []
	pop_size = len(population)

	# Ensure tournament size is at least 2 and no larger than population
	k = max(2, min(k, pop_size))

	for _ in range(num_selected):
		# pick k distinct competitors
		competitors = random.sample(population, k)
		# choose the best competitor (higher fitness is assumed better)
		winner = max(competitors, key=lambda ind: ind.fitness)
		selected.append(winner)

	return selected

