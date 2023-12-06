import random
import math

# constants
max_number_of_rounds = 50
number_of_sheep = 15
coordinate_limit = 10
distance_sheep_movement = 0.5
distance_wolf_movement = 1.0

# def euclidean_distance:

class Sheep:
    def __init__(self, sheep_number, x, y, alive: bool):
        self.sheep_number = sheep_number
        self.x = x
        self.y = y
        self.alive = alive

class Wolf:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def main():

    # initialize wolf and sheeps
    wolf = Wolf(0, 0)
    sheep_array = []
    for i in range(0, number_of_sheep):
        random_x = random.uniform(-coordinate_limit, coordinate_limit)
        random_y = random.uniform(-coordinate_limit, coordinate_limit)
        print(random_x, random_y)
        sheep_array.append(Sheep(i + 1, random_x, random_y, True))

    # start rounds
    for round_number in range(0, max_number_of_rounds):

        # start of round
        # sheep movement
        distances = []  # array of tuples: (sheep_number, distance)
        for sheep in sheep_array:
            if sheep.alive:
                direction = random.randint(1, 4) # N, S, E, W
                match direction:
                    case 1:
                        sheep.y -= distance_sheep_movement
                    case 2:
                        sheep.y += distance_sheep_movement
                    case 3:
                        sheep.x += distance_sheep_movement
                    case 4:
                        sheep.x -= distance_sheep_movement
                # after move, we can calculate distance to wolf
                distances.append((sheep.sheep_number, math.dist([sheep.x, sheep.y], [wolf.x, wolf.y])))

        # wolf movement
        distances.sort(key=lambda a: a[1])
        print(distances)
        number_of_closest_sheep, distance_of_closest_sheep = distances[0]


if __name__ == '__main__':
    main()