import json
from faker import Faker
import random
import numpy as np
import yaml
from datetime import datetime
from scipy.optimize import bisect
# Initialize Faker with Finnish locale
def sample_age_distribution(distribution, n_samples=1):
    ages = []
    for interval, population in distribution:
        ages.extend(random.choices(range(interval[0], interval[1] + 1), k=int(population)))
    return random.choices(ages, k=n_samples)
def average_skills(pmsm, num_agents=100, pareto_param=8, num_samples=1000):
    pareto_samples = np.random.pareto(pareto_param, size=(num_samples, num_agents))
    clipped_skills = np.minimum(pmsm, (pmsm - 1) * pareto_samples + 1)
    sorted_clipped_skills = np.sort(clipped_skills, axis=1)
    return sorted_clipped_skills.mean(axis=0)
def func_to_solve(pmsm, target_average_skill):
    avg_skills = average_skills(pmsm)
    return np.mean(avg_skills) - target_average_skill

def generate(place, faker_locale, GDP, bracket_spacing, tax_model, age_dis=None, ubi=0, description='', ubi_stating_time=None):
    fake = Faker(faker_locale)
    interval_list = [0, 2454, 4838, 7565, 10777, 14712, 19603, 26015, 35469, 52370, 10000000]
    interval_str_list = []
    # us per capita DGP: 86182 https://ycharts.com/indicators/us_gdp_per_capita#:~:text=US%20GDP%20per%20Capita%20is%20at%20a%20current,data%20from%201947%20to%202024%2C%20charts%20and%20stats.
    for i in range(len(interval_list)-1):
        interval_str_list.append(f"{int(interval_list[i]/86182*GDP)}-{int(interval_list[i + 1]/86182*GDP)}")
    # print(interval_str_list)
    data = {
        "Age": [],
        "Name": [],
        "City": [],
        interval_str_list[0]: ["Intern", "Student Assistant", "Volunteer", "Camp Counselor", "Babysitter", "Dog Walker", "Lawn Mower", "House Cleaner", "Farm Hand", "Newspaper Delivery"],
        interval_str_list[1]: ["Fast Food Worker", "Cashier", "Retail Sales Associate", "Barista", "Waiter/Waitress", "Dishwasher", "Janitor", "Taxi Driver", "Library Assistant", "Hotel Front Desk Clerk"],
        interval_str_list[2]: ["Administrative Assistant", "Bank Teller", "Customer Service Representative", "Security Guard", "School Bus Driver", "Home Health Aide", "Data Entry Clerk", "Receptionist", "Mail Carrier", "Lifeguard"],
        interval_str_list[3]: ["Office Manager", "Medical Assistant", "Maintenance Worker", "Delivery Driver", "Call Center Agent", "Real Estate Agent", "Teacher's Aide", "Cable Installer", "Warehouse Worker", "Painter"],
        interval_str_list[4]: ["Licensed Practical Nurse", "Police Officer", "Firefighter", "Truck Driver", "Paralegal", "Graphic Designer", "Reporter", "Electrician", "Plumber", "Welder"],
        interval_str_list[5]: ["Registered Nurse", "Accountant", "School Teacher", "Web Developer", "Dental Hygienist", "Insurance Agent", "Mechanical Engineer", "Pharmaceutical Sales Representative", "Real Estate Broker", "Journalist"],
        interval_str_list[6]: ["Software Engineer", "Pharmacist", "Physical Therapist", "Architect", "Veterinarian", "Marketing Manager", "Environmental Scientist", "Financial Analyst", "Civil Engineer", "Occupational Therapist"],
        interval_str_list[7]: ["Attorney", "Dentist", "Optometrist", "Podiatrist", "Actuary", "Political Scientist", "Aerospace Engineer", "Human Resources Manager", "Economist", "Biomedical Engineer"],
        interval_str_list[8]: ["Surgeon", "Psychiatrist", "Pediatrician", "Obstetrician and Gynecologist", "Orthodontist", "Prosthodontist", "Physician", "CEO", "Anesthesiologist", "Oral and Maxillofacial Surgeon"],
        interval_str_list[9]: ["Tech Company Founder", "Professional Athlete", "Movie Star", "Top Executive at Fortune 500 Company", "Successful Author", "Top Surgeon Specialist", "Venture Capitalist", "International Lawyer", "Major Real Estate Developer", "Financial Market Trader"]
    }
        
    for _ in range(100):
        if age_dis:
            age = sample_age_distribution(age_dis)[0]
        else:
            age = sample_age_distribution([((20, 24), 1), ((25, 29), 1), ((30, 34), 1), ((35, 39), 1),((40, 44), 1),((45, 49), 1),((50, 54), 1),((55, 59), 1),])[0]
        # age_value = random.randint(int(age.split('-')[0]), int(age.split('-')[1]))
        data["Age"].append(age)
        data["Name"].append(fake.name())
        # data["City"].append(fake.city())
        data["City"].append("Kenya")
    # Convert to JSON
    json_data = json.dumps(data, indent=4)
    # Output the JSON to a file or print it
    with open(f'profiles_{place}.json', 'w') as f:
        f.write(json_data)
    
    pmsm_solution = bisect(func_to_solve, 0, 1000, args=(GDP / 12 / 168,))
    
    with open('../config_default.yaml', 'r') as file:
        config = yaml.safe_load(file)
    config['env']['components'][1]['PeriodicBracketTax']['bracket_spacing'] = bracket_spacing
    config['env']['components'][1]['PeriodicBracketTax']['tax_model'] = tax_model
    config['env']['components'][0]['SimpleLabor']['payment_max_skill_multiplier'] = pmsm_solution
    config['profiles'] = f'data/profiles_{place}.json'
    config['description'] = description
    config['ubi'] = ubi
    config['world_start_time'] = ubi_stating_time
    with open(f'../config_{place}.yaml', 'w') as file:
        yaml.dump(config, file)


place = 'Kenya'
faker_locale = 'sw'
GDP = 1983
bracket_spacing = 'kenya2018'
tax_model = 'kenya_2018_scaled'
age_distribution = [((20, 24), 4649785), ((25, 29), 4170962), ((30, 34), 3651803), ((35, 39), 2960204), ((40, 44), 2367457), ((45, 49), 1910683),((50, 54), 1490819),((55, 59), 1099172),]
ubi = 22.5
ubi_stating_time = '2018.01'
description = f""""""
generate(place, faker_locale, GDP, bracket_spacing, tax_model, age_distribution, ubi, description, ubi_stating_time)

'''
place = 'finland'
faker_locale = 'fi_FI'
GDP = 46412
bracket_spacing = 'finland2017'
tax_model = 'finland_2017_scaled'
age_distribution = [((20, 24), 331397), ((25, 29), 351089), ((30, 34), 354415), ((35, 39), 348552),((40, 44), 328797),((45, 49), 333843),((50, 54), 371251),((55, 59), 365113),]
ubi = 604
ubi_stating_time = '2017.01'
description = ""
'''
'''
place = 'texas'
faker_locale = 'en_US'
GDP = 63296
bracket_spacing = 'us2020'
tax_model = 'us_2020_scaled'
age_distribution = [((20, 21), 816270.0), ((21, 22), 798044.0), ((22, 23), 804354.0), ((23, 24), 817136.0), ((24, 25), 825642.0), ((25, 26), 838436.0), ((26, 27), 852790.0), ((27, 28), 868022.0), ((28, 29), 891840.0), ((29, 30), 895084.0), ((30, 31), 889468.0), ((31, 32), 861414.0), ((32, 33), 848528.0), ((33, 34), 843846.0), ((34, 35), 847712.0), ((35, 36), 853204.0), ((36, 37), 827940.0), ((37, 38), 840702.0), ((38, 39), 836508.0), ((39, 40), 824760.0), ((40, 41), 834124.0), ((41, 42), 775842.0), ((42, 43), 757906.0), ((43, 44), 751690.0), ((44, 45), 735842.0), ((45, 46), 748792.0), ((46, 47), 723400.0), ((47, 48), 725860.0), ((48, 49), 741048.0), ((49, 50), 761672.0), ((50, 51), 752982.0), ((51, 52), 701792.0), ((52, 53), 676742.0), ((53, 54), 660354.0), ((54, 55), 661028.0), ((55, 56), 689368.0), ((56, 57), 693232.0), ((57, 58), 688744.0), ((58, 59), 680230.0), ((59, 60), 675682.0)]
ubi = 1000
ubi_stating_time = '2020.01'
description = ""
'''
'''
place = 'nambia'
faker_locale = 'zu_ZA'
GDP = 5687
bracket_spacing = 'namibia2020'
tax_model = 'namibia_2008_scaled'
age_distribution =  [((20, 24), 260864), ((25, 29), 256820), ((30, 34), 244613), ((35, 39), 197787),((40, 44), 164268),((45, 49), 134217),((50, 54), 106564),((55, 59), 81760),]
ubi = 5
ubi_stating_time = '2008.01'
description = ""
'''
'''
place = 'california'
faker_locale = 'en_US'
GDP = 81593
bracket_spacing = 'us2020'
tax_model = 'us_2020_scaled'
age_distribution = [((20, 24), 2639873), ((25, 29), 3092545), ((30, 34), 2954993), ((35, 39), 2776974), ((40, 44), 2496802), ((45, 49), 2510078), ((50, 54), 2458499), ((55, 59), 2503819)]
ubi = 500
ubi_stating_time = '2019.02'
description = ""
generate(place, faker_locale, GDP, bracket_spacing, tax_model, age_distribution, ubi, description, ubi_stating_time)
'''
'''
place = 'Namibia'
faker_locale = 'zu_ZA'
GDP = 63296
bracket_spacing = 'us2020'
tax_model = 'us_2020_scaled'
age_distribution = [((20, 24), 4649785), ((25, 29), 4170962), ((30, 34), 3651803), ((35, 39), 2960204), ((40, 44), 2367457), ((45, 49), 1910683),((50, 54), 1490819),((55, 59), 1099172),]
ubi = 1000
ubi_stating_time = '2020.01'
description = f""""""
generate(place, faker_locale, GDP, bracket_spacing, tax_model, age_distribution, ubi, description, ubi_stating_time)
'''
