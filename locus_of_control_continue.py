import os
import re
import json
import multiprocessing
import tqdm
import fire
import openai
import pickle as pkl
def get_completion(dialogs, temperature=1, max_tokens=100):
    openai.api_key = 'fill in your key here'
    prompt_cost_1k, completion_cost_1k = 0.001, 0.002
    max_retries = 20
    for i in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=dialogs,
                temperature=temperature,
                max_tokens=max_tokens
            )
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            this_cost = prompt_tokens/1000*prompt_cost_1k + completion_tokens/1000*completion_cost_1k
            temp = json.loads(response.choices[0].message["content"])
            if type(temp) != dict:
                raise
            if len((temp.keys())) != 36:
                raise
            for i in temp.keys():
                if int(i) not in range(1, 37):
                    raise
            for i in temp:
                if temp[i] not in ["Strongly Disagree", "Moderately Disagree", "Slightly Disagree", "Slightly Agree", "Moderately Agree", "Strongly Agree"]:
                    raise
                if i not in [str(i) for i in range(40)]:
                    raise
            return response.choices[0].message["content"], this_cost
        except Exception as e:
            print(f"An error of type {type(e).__name__} occurred: {e}")
            return "Error"

def get_multiple_completion(dialogs, num_cpus=50, temperature=0, max_tokens=1000):
    from functools import partial
    get_completion_partial = partial(get_completion, temperature=temperature, max_tokens=max_tokens)
    with multiprocessing.Pool(processes=num_cpus) as pool:
        results = pool.map(get_completion_partial, dialogs)
    total_cost = sum([cost for _, cost in results])
    return [response for response, _ in results], total_cost

def main(folder_path):
    dialogs = {}
    rating_prompt = f'''Please fill in the following questionnaire:
    Answer how much you agree with the following statements by choosing one of the following options:
    "Strongly Disagree",
    "Moderately Disagree",
    "Slightly Disagree",
    "Slightly Agree",
    "Moderately Agree",
    "Strongly Agree".
    Statement 1: If I get sick, it is my own behavior which determines how soon I get well again.
    Statement 2: No matter what I do, if I am going to get sick, I will get sick.
    Statement 3: Having regular contact with my physician is the best way for me to avoid illness
    Statement 4: Most things that affect my health happen to me by accident.
    Statement 5: Whenever I don't feel well, I should consult a medically trained professional.
    Statement 6: I am in control of my health.
    Statement 7: My family has a lot to do with my becoming sick or staying healthy.
    Statement 8: When I get sick, I am to blame.
    Statement 9: Luck plays a big part in determining how soon I will recover from an illness.
    Statement 10: Health professionals control my health.
    Statement 11: My good health is largely a matter of good fortune.
    Statement 12: The main thing which affects my health is what I myself do.
    Statement 13: If I take care of myself, I can avoid illness.
    Statement 14: Whenever I recover from an illness, it's usually because other people (for example, doctors, nurses, family, friends) have been taking good care of me.
    Statement 15: No matter what I do, I 'm likely to get sick.
    Statement 16: If it's meant to be, I will stay healthy.
    Statement 17: If I take the right actions, I can stay healthy.
    Statement 18: Regarding my health, I can only do what my doctor tells me to do.
    
    Statement 19:If I become sick, I have the power to make myself well again.
    Statement 20:Often I feel that no matter what I do, if I am going to get sick, I will get sick.
    Statement 21:If I see an excellent doctor regularly, I am less likely to have health problems.
    Statement 22:It seems that my health is greatly influenced by accidental happenings.
    Statement 23:I can only maintain my health by consulting health professionals.
    Statement 24:I am directly responsible for my health.
    Statement 25:Other people play a big part in whether I stay healthy or become sick.
    Statement 26:Whatever goes wrong with my health is my own fault.
    Statement 27:When I am sick, I just have to let nature run its course.
    Statement 28:Health professionals keep me healthy.
    Statement 29:When I stay healthy, I'm just plain lucky.
    Statement 30:My physical well-being depends on how well I take care of myself.
    Statement 31:When I feel ill, I know it is because I have not been taking care of myself properly.
    Statement 32:The type of care I receive from other people is what is responsible for how well I recover from an illness.
    Statement 33:Even when I take care of myself, it's easy to get sick.
    Statement 34:When I become ill, it's a matter of fate.
    Statement 35:I can pretty much stay healthy by taking good care of myself.
    Statement 36:Following doctor's orders to the letter is the best way for me to stay healthy.
    
    Please response with json format with keys being numbers 1-36 and values being one of "Strongly Disagree", "Moderately Disagree", "Slightly Disagree", "Slightly Agree", "Moderately Agree" or "Strongly Agree".
    '''

    dialog = {}
    steps = [1 + i*3 for i in range(7)]
    for step in steps:
        r_f = pkl.load(open(f"{folder_path}/dialog4ref_{200+step}.pkl", "rb"))
        dialog[step] = {}
        for i in range(50):
            dialog[step][i] = list(r_f[i])[1:]
            dialog[step][i].append({"role": "user", "content": rating_prompt})
    dialogs = dialog
    if not os.path.exists(folder_path + "/locus_of_control"):
        os.makedirs(folder_path + "/locus_of_control")
    for i in tqdm.tqdm(dialogs.keys()):
        multi_input = [dialogs[i][idx] for idx in range(50)]
        results, cost = get_multiple_completion(multi_input)
        with open(folder_path + f"/locus_of_control/{i}.json", 'w') as file:
            json.dump(results, file, indent=4)

if __name__ == "__main__":
    fire.Fire(main)