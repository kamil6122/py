import random
import math
import json
import csv

# constants
MAX_NUMBER_OF_ROUNDS = 50
NUMBER_OF_SHEEP = 15
COORDINATE_LIMIT = 10
DISTANCE_SHEEP_MOVEMENT = 0.5
DISTANCE_WOLF_MOVEMENT = 1.0


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

    # variables
    list_of_dicts = []
    list_of_csv_rows = []
    last_sheep_eaten = None
    number_of_alive_sheep = NUMBER_OF_SHEEP

    # initialize wolf and sheeps
    wolf = Wolf(0, 0)
    sheep_array = []
    for i in range(0, NUMBER_OF_SHEEP):
        random_x = random.uniform(-COORDINATE_LIMIT, COORDINATE_LIMIT)
        random_y = random.uniform(-COORDINATE_LIMIT, COORDINATE_LIMIT)
        # print(random_x, random_y)
        sheep_array.append(Sheep(i, random_x, random_y, True))

    # start rounds
    for round_number in range(0, MAX_NUMBER_OF_ROUNDS):

        # start of round

        # sheep movement
        distances = []  # array of tuples: (sheep_number, distance)
        for sheep in sheep_array:
            if sheep.alive:
                direction = random.randint(1, 4)  # N, S, E, W
                match direction:
                    case 1:
                        sheep.y -= DISTANCE_SHEEP_MOVEMENT
                    case 2:
                        sheep.y += DISTANCE_SHEEP_MOVEMENT
                    case 3:
                        sheep.x += DISTANCE_SHEEP_MOVEMENT
                    case 4:
                        sheep.x -= DISTANCE_SHEEP_MOVEMENT
                # after move, we can calculate distance to wolf
                distances.append((sheep.sheep_number, math.dist([sheep.x, sheep.y], [wolf.x, wolf.y])))

        # choosing closest sheep
        distances.sort(key=lambda a: a[1])
        number_of_closest_sheep, distance_of_closest_sheep = distances[0]
        closest_sheep = sheep_array[number_of_closest_sheep]

        # if sheep is in range of wolf attack
        if distance_of_closest_sheep <= DISTANCE_WOLF_MOVEMENT:
            # wolf eats the sheep
            wolf.x, wolf.y = closest_sheep.x, closest_sheep.y
            closest_sheep.alive = False
            chased_sheep_number = None
            last_sheep_eaten = closest_sheep.sheep_number
            number_of_alive_sheep -= 1

        # if sheep is out of range of wolf attack
        else:
            # wolf chases the sheep
            chased_sheep_number = number_of_closest_sheep
            wolf.x += (closest_sheep.x - wolf.x) * (DISTANCE_WOLF_MOVEMENT / distance_of_closest_sheep)
            wolf.y += (closest_sheep.y - wolf.y) * (DISTANCE_WOLF_MOVEMENT / distance_of_closest_sheep)

        list_of_sheep_positions = []
        for sheep in sheep_array:
            if sheep.alive:
                list_of_sheep_positions.append((sheep.x, sheep.y))
            else:
                list_of_sheep_positions.append(None)

        # end of round summary

        real_round_number = round_number + 1

        # json
        list_of_dicts.append({'round_no': real_round_number,
                              'wolf_pos': (wolf.x, wolf.y),
                              'sheep_pos': list_of_sheep_positions})

        # csv
        list_of_csv_rows.append([real_round_number, number_of_alive_sheep])

        # terminal
        info = (
                'round number: ' + str(real_round_number)
                + ', wolf position (x, y): (' + str(round(wolf.x, 3)) + ', ' + str(round(wolf.y, 3)) + '), '
                + str(number_of_alive_sheep) + ' alive sheep, '
                )
        if chased_sheep_number is None:
            info += 'sheep: ' + str(last_sheep_eaten) + ' WAS EATEN.'
        else:
            info += 'sheep: ' + str(chased_sheep_number) + ' is chased.'
        print(info)

        if number_of_alive_sheep == 0:
            break

    # after all rounds

    # save to json
    json_object = json.dumps(list_of_dicts, indent=4)
    with open('pos.json', 'w') as output:
        output.write(json_object)

    # save to csv
    with open('alive.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(list_of_csv_rows)


if __name__ == '__main__':
    main()