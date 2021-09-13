import json
import random


def read_json_txt(file):
    with open(file, encoding='utf-8', newline='') as json_file:
        data = json.load(json_file)
        return data


def write_json_txt(result, file):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)


def get_random_time():
    value = random.random()
    scaled_value = 4 + (value * (11 - 5))
    return scaled_value
