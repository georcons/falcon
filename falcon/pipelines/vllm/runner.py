import os
import json
import argparse
from typing import List
#from vllm import LLM, SamplingParams

def load_input(
    rel_path : str, 
    response_count : int | None = 1
):
    current_directory = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(current_directory, "input", rel_path)
    with open(file_path, 'r') as file:
        data = json.load(file)
        prompts = [prompt for prompt in data for _ in range(response_count)]
        return prompts


def run_vllm(
    model : str,
    prompts : List[str],
    *,
    temperature : float | None = 1.0,
    max_tokens : int | None = None,
    gpu_count : int | None = 1
) -> List[str]:
    # Load LLM
    llm = LLM(model=model, gpu_memory_utilization=0.9, tensor_parallel_size=gpu_count)
    # Set up sampling parameters
    sampling_params = (SamplingParams(temperature=temperature, max_tokens=max_tokens) if max_tokens != None 
                        else SamplingParams(temperature=temperature))
    # Run LLM
    outputs = llm.generate(prompts, sampling_params)
    # Return output
    return outputs


def save_output(
    outputs : List[str],
    rel_path : str,
    response_count : int | None = 1
) -> None:
    current_directory = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(current_directory, "output", rel_path)
    data_dict = {
        'response_count': response_count,
        'results': outputs
    }
    with open(file_path, 'w') as file:
        json.dump(data_dict, file)


def main():
    # Make sure required directories exist
    _required_directories = ['input/', 'logs/', 'output/', 'shells/']
    for directory in _required_directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="Name of input JSON file")
    parser.add_argument("output", type=str, help="Name of output JSON file")
    parser.add_argument("--response_count", type=int, help="Number of retries for each prompt", default=1)
    parser.add_argument("--model", type=str, help="vLLM model name", default="facebook/opt-125m")
    parser.add_argument("--temperature", type=float, help="Model temperature", default=1.0)
    parser.add_argument("--max_tokens", type=int, help="Maximum number of generated tokens", default=None)
    parser.add_argument("--gpu_count", type=int, help="Number is GPUs to except", default=1)
    args = parser.parse_args()

    # Load prompts
    prompts = load_input(args.input, args.response_count)

    # Run model
    generated = run_vllm(args.model, prompts, temperature=args.temperature, max_tokens=args.max_tokens, gpu_count=args.gpu_count)
    
    # Extract Outputs
    outputs = [output.outputs[0].text.strip() for output in generated]
    
    # Save Outputs
    save_output(outputs, args.output, args.response_count)

if __name__ == "__main__":
    main()
