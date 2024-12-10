import numpy as np
import matplotlib.pyplot as plt
import re
import concurrent.futures
import concurrent
import json
from pebble import ProcessPool
import tqdm

save_path = "./"

brackets = list(np.array([0, 97, 394.75, 842, 1607.25, 2041, 5103]) * 100 / 12)
quantiles = [0, 0.25, 0.5, 0.75, 1.0]

prompt_cost_1k, completion_cost_1k = 0.001, 0.002


def prettify_document(document: str) -> str:
    cleaned = re.sub(r"\s+", " ", document).strip()
    return cleaned


def extract_json(output_str):
    try:
        start = output_str.find("{")
        end = output_str.rfind("}")
        json_str = output_str[start : end + 1]
        return json_str
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Failed to extract JSON: {e}")
        return None


def get_multiple_completion_025(
    inputs, workers=10, timeout=60, temperature=0, max_tokens=100
):
    created_pool = []
    function = get_completion_025
    with ProcessPool(max_workers=workers) as pool:
        for i in range(len(inputs)):
            created_pool.append(
                pool.schedule(function, [inputs[i]], timeout=timeout)
            )
        updated_pool = list(range(len(created_pool)))
        retry_index = [i for i in range(len(created_pool))]
        while retry_index:
            new_retry_index = []
            for i in tqdm.tqdm(retry_index):
                try:
                    updated_pool[i] = created_pool[i].result()
                except concurrent.futures._base.TimeoutError:
                    new_retry_index.append(i)
                    created_pool[i] = pool.schedule(
                        function, [inputs[i]], timeout=timeout
                    )
            retry_index = new_retry_index
    updated_pool_0 = [i[0] for i in updated_pool]
    updated_pool_1 = [i[1] for i in updated_pool]
    return updated_pool_0, sum(updated_pool_1)


def get_multiple_completion(
    inputs, workers=10, timeout=60, temperature=0, max_tokens=100
):
    created_pool = []
    function = get_completion
    with ProcessPool(max_workers=workers) as pool:
        for i in range(len(inputs)):
            created_pool.append(
                pool.schedule(function, [inputs[i]], timeout=timeout)
            )
        updated_pool = list(range(len(created_pool)))
        retry_index = [i for i in range(len(created_pool))]
        while retry_index:
            new_retry_index = []
            for i in tqdm.tqdm(retry_index):
                try:
                    updated_pool[i] = created_pool[i].result()
                except concurrent.futures._base.TimeoutError:
                    new_retry_index.append(i)
                    created_pool[i] = pool.schedule(
                        function, [inputs[i]], timeout=timeout
                    )
            retry_index = new_retry_index
    updated_pool_0 = [i[0] for i in updated_pool]
    updated_pool_1 = [i[1] for i in updated_pool]
    return updated_pool_0, sum(updated_pool_1)


def get_multiple_completion_non_json(
    inputs, workers=50, timeout=60, temperature=0, max_tokens=100
):
    created_pool = []
    function = get_completion_non_json
    with ProcessPool(max_workers=workers) as pool:
        for i in range(len(inputs)):
            created_pool.append(
                pool.schedule(function, [inputs[i]], timeout=timeout)
            )
        updated_pool = list(range(len(created_pool)))
        retry_index = [i for i in range(len(created_pool))]
        while retry_index:
            new_retry_index = []
            for i in tqdm.tqdm(retry_index):
                try:
                    updated_pool[i] = created_pool[i].result()
                except concurrent.futures._base.TimeoutError:
                    new_retry_index.append(i)
                    created_pool[i] = pool.schedule(
                        function, [inputs[i]], timeout=timeout
                    )
            retry_index = new_retry_index
    updated_pool_0 = [i[0] for i in updated_pool]
    updated_pool_1 = [i[1] for i in updated_pool]
    return updated_pool_0, sum(updated_pool_1)


def get_completion(dialogs, temperature=0, max_tokens=100):
    import openai

    openai.api_key = "fill in your key here"
    import time

    max_retries = 20
    for i in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=dialogs,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            this_cost = (
                prompt_tokens / 1000 * prompt_cost_1k
                + completion_tokens / 1000 * completion_cost_1k
            )
            return (
                extract_json(response.choices[0].message["content"]),
                this_cost,
            )
        except Exception as e:
            if i < max_retries - 1:
                time.sleep(6)
            else:
                print(f"An error of type {type(e).__name__} occurred: {e}")
                return "Error"


def get_completion_025(dialogs, temperature=0, max_tokens=100):
    import openai

    openai.api_key = "fill in your key here"
    import time

    max_retries = 20
    for i in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=dialogs,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            this_cost = (
                prompt_tokens / 1000 * prompt_cost_1k
                + completion_tokens / 1000 * completion_cost_1k
            )
            temp = json.loads(
                extract_json(response.choices[0].message["content"])
            )
            for key in temp.keys():
                if key not in [str(i) for i in range(5)]:
                    raise
            return (
                extract_json(response.choices[0].message["content"]),
                this_cost,
            )
        except Exception as e:
            if i < max_retries - 1:
                time.sleep(6)
            else:
                print(f"An error of type {type(e).__name__} occurred: {e}")
                return "Error"


def get_completion_non_json(dialogs, temperature=0, max_tokens=100):
    import openai

    openai.api_key = "fill in your key here"
    import time

    max_retries = 20
    for i in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=dialogs,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            this_cost = (
                prompt_tokens / 1000 * prompt_cost_1k
                + completion_tokens / 1000 * completion_cost_1k
            )
            return response.choices[0].message["content"], this_cost
        except Exception as e:
            if i < max_retries - 1:
                time.sleep(6)
            else:
                print(f"An error of type {type(e).__name__} occurred: {e}")
                return "Error"


def format_numbers(numbers):
    return "[" + ", ".join("{:.2f}".format(num) for num in numbers) + "]"


def format_percentages(numbers):
    return "[" + ", ".join("{:.2%}".format(num) for num in numbers) + "]"
