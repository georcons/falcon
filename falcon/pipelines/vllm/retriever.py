import os
import json

def split_array(arr, n):
    avg = len(arr) // n
    remainder = len(arr) % n
    result = []
    start = 0

    for i in range(n):
        end = start + avg + (1 if i < remainder else 0)
        result.append(arr[start:end])
        start = end

    return result


def retrieve_batch(
    batch_id : str
):
    current_directory = os.path.dirname(os.path.realpath(__file__))
    json_path = os.path.join(current_directory, "output", batch_id + ".json")
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        res_count = data['response_count']
        results = data['results']
        if len(results) % res_count != 0:
            raise Exception("Invalid file.")
        return split_array(results, int(len(results) / res_count))