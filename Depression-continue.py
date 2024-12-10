import os
import re
import json
import multiprocessing
import concurrent
from pebble import ProcessPool
import tqdm
import fire
import pickle as pkl
import concurrent.futures
import openai


def get_completion(dialogs, temperature=1, max_tokens=1000):
    openai.api_key = "fill in your key here"
    prompt_cost_1k, completion_cost_1k = 0.001, 0.002
    max_retries = 200
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
            temp = json.loads(response.choices[0].message["content"])
            if type(temp) != dict:
                raise
            if len((temp.keys())) != 20:
                raise
            for i in temp.keys():
                if int(i) not in range(1, 21):
                    raise
            for i in temp:
                if temp[i] not in ["Rarely", "Some", "Occasionally", "Most"]:
                    raise
                if i not in [str(i) for i in range(40)]:
                    raise
            return response.choices[0].message["content"], this_cost
        except Exception:
            pass


def multi(function, inputs, workers=50, timeout=60):
    created_pool = []
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
    return updated_pool


def get_multiple_completion(
    dialogs, num_cpus=50, temperature=0, max_tokens=1000
):
    results = multi(get_completion, dialogs, workers=num_cpus)
    total_cost = sum([cost for _, cost in results])
    return [response for response, _ in results], total_cost


def main(folder_path):
    dialogs = {}
    rating_prompt = f"""Please fill in the following questionnaire:
    Indicate how often you have felt this way during the last week by choosing one of the following options:
    "Rarely" means Rarely or none of the time (less than 1 day),
    "Some" means Some or a little of the time (1-2 days),
    "Occasionally" means Occasionally or a moderate amount of the time (3-4 days),
    "Most" means Most or all of the time (5-7 days).
    Statement 1: I was bothered by things that usually don't bother me.  
    Statement 2: I did not feel like eating; my appetite was poor.
    Statement 3: I felt that I could not shake off the blues even with help from my family or friends.
    Statement 4: I felt that I was just as good as other people.
    Statement 5: I had trouble keeping my mind on what I was doing.
    Statement 6: I felt depressed.
    Statement 7: I felt that everything I did was an effort.
    Statement 8: I felt hopeful about the future.
    Statement 9: I thought my life had been a failure.
    Statement 10: I felt fearful.
    Statement 11: My sleep was restless.
    Statement 12: I was happy.
    Statement 13: I talked less than usual.
    Statement 14: I felt lonely.
    Statement 15: People were unfriendly.
    Statement 16: I enjoyed life.
    Statement 17: I had crying spells.
    Statement 18: I felt sad.
    Statement 19: I felt that people disliked me.
    Statement 20: I could not get "going".
    Please response with json format with keys being numbers 1-20 and values being one of "Rarely", "Some", "Occasionally", "Most".
    """

    dialog = {}
    steps = [1 + i * 3 for i in range(7)]
    for step in steps:
        r_f = pkl.load(open(f"{folder_path}/dialog4ref_{200+step}.pkl", "rb"))
        dialog[step] = {}
        for i in range(50):
            dialog[step][i] = list(r_f[i])[1:]
            dialog[step][i].append({"role": "user", "content": rating_prompt})
    dialogs = dialog

    if not os.path.exists(folder_path + "/depression"):
        os.makedirs(folder_path + "/depression")
    for i in tqdm.tqdm(dialogs.keys()):
        multi_input = [dialogs[i][idx] for idx in range(50)]
        results, cost = get_multiple_completion(multi_input)
        with open(folder_path + f"/depression/{i}.json", "w") as file:
            json.dump(results, file, indent=4)


if __name__ == "__main__":
    fire.Fire(main)
