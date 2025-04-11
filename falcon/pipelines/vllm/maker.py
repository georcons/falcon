import os
import json
import random
import string
import subprocess
from typing import List
from pathlib import Path

SHELL_SETUP = "setup.sh"

def generate_random_string(length=16):
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return random_str

def gen_json_name(directory, length=16, prefix="input_"):
    name = generate_random_string(length) + ".json"
    while os.path.exists(os.path.join(directory, name)):
        name = generate_random_string(length) + ".json"
    return prefix + name

def gen_shell_name(directory, length=6):
    name = generate_random_string(length) + ".sh"
    while os.path.exists(os.path.join(directory, name)):
        name = generate_random_string(length) + ".sh"
    return name

def shell_gen_command(
    input_name : str,
    output_name : str,
    *,
    response_count : int | None = None,
    model : str | None = None,
    temperature : float | None = None,
    max_tokens : int | None = 16000,
    gpu_count : int | None = 1,
    python_name : str | None = "python"
):
    command = ' '.join([python_name, "./runner.py", input_name, output_name])
    command += (" --gpu_count " + str(gpu_count))
    if response_count != None:
        command += (" --response_count " + str(response_count))
    if model != None:
        command += (" --model " + model)
    if temperature != None:
        command += (" --temperature " + str(temperature))
    if max_tokens != None:
        command += (" --max_tokens " + str(max_tokens))
    return command

def shell_gen_file(
    command : str,
    output : str,
    *,
    gpu_count : int | None = 1,
    gpu_type : str | None = "a6000"
):
    current_directory = os.path.dirname(os.path.realpath(__file__))
    shell_setup_path = os.path.join(current_directory, SHELL_SETUP)
    setup = ""
    with open(shell_setup_path, 'r', encoding="utf-8") as file:
        setup += file.read()
    output_path = os.path.join(current_directory, "logs", "vllm.log")
    error_path = os.path.join(current_directory, "logs", "vllm.error")
    setup += ("\n#SBATCH --output=" + output_path)
    setup += ("\n#SBATCH --error=" + error_path)
    setup += ("\n#SBATCH --gpus " + gpu_type + ":" + str(gpu_count) + "\n\n")
    path_parts = current_directory.split(os.sep)
    new_path = os.sep + os.path.join("scratch", path_parts[2], "vllm")
    setup += " ".join(["rsync -aHzv", current_directory, new_path])
    setup += ("\ncd " + new_path + "/vllm/")
    setup += "\nls"
    setup += ("\nexport CUDA_VISIBLE_DEVICES=" + ','.join([str(i) for i in range(gpu_count)]))
    setup += ("\n\nmkenv -n vllm -f environment.yml -- \\")
    setup += ("\n" + command)
    setup += ("\n\ncp " + new_path + "/vllm/output/" + output + " " + current_directory + "/output/" + output)
    shell_name = gen_shell_name(current_directory, length=6)
    shell_path = os.path.join(current_directory, "shells", shell_name)
    with open(shell_path, 'w', encoding="utf-8") as file:
        file.write(setup)
    return shell_path


def prepare_batch(
    prompts : List[str],
    model : str,
    *,
    response_count : int | None = 1,
    gpu_count : int | None = 1,
    gpu_type : str | None = "a6000",
    temperature : float | None = 1.0,
    max_tokens : int | None = 16000
):
    current_directory = os.path.dirname(os.path.realpath(__file__))
    input_directory = os.path.join(current_directory, "input")
    output_directory = os.path.join(current_directory, "output")

    input_name = gen_json_name(input_directory, length=24, prefix="input_")
    output_name = gen_json_name(output_directory, length=24, prefix="vllm_")

    input_path = os.path.join(current_directory, "input", input_name)
 
    with open(input_path, 'w') as file:
        json.dump(prompts, file)

    command = shell_gen_command(
        input_name,
        output_name,
        response_count = response_count,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        gpu_count=gpu_count
    )

    shell = shell_gen_file(
        command, 
        output_name,
        gpu_count=gpu_count,
        gpu_type=gpu_type
    )

    complete_cmd = "sbatch " + shell
    batch_id = output_name.removesuffix(".json")
    return batch_id, complete_cmd

# i, cmd = prepare_batch(["What is the capical of France?","Who are you?","WTF","AHH OHH"], "facebook/opt-125m", response_count=2)
# print(i)
# print(cmd)