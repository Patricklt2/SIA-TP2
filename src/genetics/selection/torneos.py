import random


def tournament_selection(population, num_selected, k=3):
	if not population or num_selected <= 0:
		return []

	selected = []
	pop_size = len(population)

	k = max(2, min(k, pop_size))

	for _ in range(num_selected):
		competitors = random.sample(population, k)
		winner = max(competitors, key=lambda ind: ind.fitness)
		selected.append(winner)

	return selected

