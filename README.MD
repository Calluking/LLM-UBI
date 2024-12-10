# LLM Agents Empower Simulation for the Future of Work: Universal Basic Income, Employment, and Well-being

It's based on 2 Economic Simulation Framework:

  + [Foundation](https://github.com/MaciejMacko/ai-economist), announced by this paper: Zheng, Stephan, et al. "The ai economist: Improving equality and productivity with ai-driven tax policies." arXiv preprint arXiv:2004.13332 (2020).
  + [EconAgent](https://github.com/tsinghua-fib-lab/ACL24-EconAgent), announce by this paper: [EconAgent: Large Language Model-Empowered Agents for Simulating Macroeconomic Activities](https://aclanthology.org/2024.acl-long.829) (Li et al., ACL 2024)

# Generating Simulation Settings
`python data/generate.py`
Modify generate.py to generate simulation settings and agent profiles of different places.
Taxation brackets and rules can be modified in `ai_economist_ubi/foundation/components/redistribution.py`
See implementation of `finland_2017_scaled` Bracket for example.


# Running Simulations
1. Simulate a society until stable: 
    ```episode_length = 200
    starting_time = "2018.01"
    world_start_time = datetime.strptime(starting_time, '%Y.%m')
    world_start_time = world_start_time - relativedelta(months=episode_length)
    world_start_time_str = world_start_time.strftime('%Y.%m')
    place = "kenya"
    duration = 24
    ubi = 22.5
    cmd = f"""python simulate.py --episode_length={episode_length} --case="{place}" """
    origin = f"data/gpt-3-noperception-reflection-1-50agents-{episode_length}months-{place}-{world_start_time_str}"
    os.system(cmd)
    ```
    The simulation result will be saved in the `origin` path

2. CONTROL GROUP: Continue to simulate the society without any changes:
    ```
    cmd = f"""python simulate-continue.py --episode_length={episode_length} --case={place} --duration={duration} --data_path="{origin}" """
    non_ubi_path = f"data/gpt-3-noperception-reflection-1-50agents-{episode_length}months-{place}-{world_start_time_str}_continue_duration{duration}"
    os.system(cmd)
    ```
    The simulation result of control group will be saved in `non_ubi_path`

3. TREATMENT GROUP: Continue to simulate the society with UBI policy:
   ```
   cmd = f"""python simulate-continue-UBI.py --episode_length={episode_length} --case={place} --duration={duration} --data_path="{origin}" """
    ubi_path = f"data/gpt-3-noperception-reflection-1-50agents-{episode_length}months-{place}-{world_start_time_str}_continue_duration{duration}_ubi{ubi}"
    os.system(cmd)
    ```
    The simulation result of the treatment group will be saved in `ubi_path`
    
4. Measuring level of Depression and Locus of Control: 
    ```
    cmd = f"python Depression-continue.py --folder_path {ubi_path}"
    os.system(cmd)
    cmd = f"python locus_of_control_continue.py --folder_path {non_ubi_path}"
    os.system(cmd)
    ```