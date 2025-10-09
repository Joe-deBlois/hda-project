import pandas as pd
import math
import matplotlib.pyplot as plt

#first set correct working directory
from pathlib import Path

# Get the directory of the current script
wd = Path(__file__).parent

# Change the current directory to that folder
import os
datasets_dir = wd / "Datasets"
os.chdir(datasets_dir)

print("Current working directory:", Path.cwd())

ALS = pd.read_csv("Clinical_Trials_ALS.csv")
Alz = pd.read_csv("Clinical_Trials_Alzheimers.csv")
CJD = pd.read_csv("Clinical_Trials_CJD.csv")
CTE = pd.read_csv("Clinical_Trials_CTE.csv")
FTD = pd.read_csv("Clinical_Trials_FTD.csv")
Hunt = pd.read_csv("Clinical_Trials_Huntingtons.csv")
LBD = pd.read_csv("Clinical_Trials_LewyBodyDementia.csv")
MSA = pd.read_csv("Clinical_Trials_MSA.csv")
MulScle = pd.read_csv("Clinical_Trials_MultipleSclerosis.csv")
NCL = pd.read_csv("Clinical_Trials_NCL.csv")
Park = pd.read_csv("Clinical_Trials_Parkinsons.csv")
PSP = pd.read_csv("Clinical_Trials_PSP.csv")
VascDem = pd.read_csv("Clinical_Trials_VascularDementia.csv")

print("Datasets uplodaded")

datasets = {
    "ALS": ALS,
    "Alz": Alz,
    "CJD": CJD,
    "CTE": CTE,
    "FTD": FTD,
    "Hunt": Hunt,
    "LBD": LBD,
    "MSA": MSA,
    "MulScle": MulScle,
    "NCL": NCL,
    "Park": Park,
    "PSP": PSP,
    "VascDem": VascDem
}

#I checked and all datasets have exactly the same columns; only need to print once
print("Column names: ")
print(ALS.columns.tolist())

#data exploration loop over every dataset
for name, df in datasets.items(): 
    print(f"Dataset: {name}")
    
    count_male = (df["Sex"] == "MALE").sum()
    count_female = (df["Sex"] == "FEMALE").sum()
    count_all = (df["Sex"] == "ALL").sum()

    print("# of male-only studies: ", count_male)
    print("# of female-only studies: ", count_female)
    print("# of all-sex studies: ", count_all)
    
    df["Age"] = df["Age"].fillna("").str.split(',')
    df["Accepting Children"] = 0 #binary per row
    df["Accepting Adults"] = 0 #binary per row
    df["Accepting Older Adults"] = 0 #binary per row

    for idx, row in df.iterrows():
        if "CHILD" in row["Age"]:
            df.at[idx, "Accepting Children"] = 1
        if "ADULT" in row["Age"]:
            df.at[idx, "Accepting Adults"] = 1
        if "OLDER_ADULT" in row["Age"]:
            df.at[idx, "Accepting Older Adults"] = 1
    
    print("# of studies accepting children: ", df["Accepting Children"].sum())
    print("# of studies accepting adults: ", df["Accepting Adults"].sum())
    print("# of studies accepting older adults: ", df["Accepting Older Adults"].sum())
        
    #Standardize free-text in "Brief Summary" and "Interventions"
    df["Brief Summary"] = df["Brief Summary"].str.lower()
    df["Interventions"] = df["Interventions"].str.lower()

    #Average number of participants (rounded up to nearest integer)
    print("Average # of participants: ", math.ceil(df["Enrollment"].sum())/len(df["Enrollment"]))

    #rough plot just to find outliers
    #x-axis = list of trial IDs
    #y-axis = list of enrollment numbers
    #each point = 1 clinical trial
    trial_ids = list(df["NCT Number"])
    enrollment = list(df["Enrollment"])
    plt.scatter(trial_ids, enrollment)
    plt.plot(trial_ids, enrollment, linestyle='--', alpha=0.6)
    plt.title(f'{name} Trial Enrollments')
    plt.xlabel('Trial ID')
    plt.ylabel('Enrollment')
    plt.show()


    #trying to get all drug names from Interventions col
    df["Interventions"] = df["Interventions"].fillna("").str.split('|')
    #creates a list in each cell
    #find all drugs, devices, behavioral, and other interventions
    intervention_types = [
    "Drug Interventions",
    "Device Interventions",
    "Behavioral Interventions",
    "Diagnostic Test Interventions",
    "Other Interventions",
    "Biological Interventions"
    ]
    for col in intervention_types:
        df[col] = None
    for idx, interventions_list in df["Interventions"].items():
        drug_names = []
        device_names = []
        behavioral_names = []
        diagnostic_tests = []
        other_names = []
        biological_names = []

        if not isinstance(interventions_list, list):
            continue  # Skip rows with unexpected values

        for intervention in interventions_list:
            intervention = intervention.strip().lower()
            if intervention.startswith("drug: "):
                drug_names.append(intervention[len("drug: "):].strip())
            elif intervention.startswith("device: "):
                device_names.append(intervention[len("device: "):].strip())
            elif intervention.startswith("behavioral: "):
                behavioral_names.append(intervention[len("behavioral: "):].strip())
            elif intervention.startswith("diagnostic test: "):
                diagnostic_tests.append(intervention[len("diagnostic test: "):].strip())
            elif intervention.startswith("other: "):
                other_names.append(intervention[len("other: "):].strip())
            elif intervention.startswith("biological: "):
                biological_names.append(intervention[len("biological: "):].strip())
        df.at[idx, "Drug Interventions"] = ", ".join(drug_names) if drug_names else None
        df.at[idx, "Device Interventions"] = ", ".join(device_names) if device_names else None
        df.at[idx, "Behavioral Interventions"] = ", ".join(behavioral_names) if behavioral_names else None
        df.at[idx, "Diagnostic Test Interventions"] = ", ".join(diagnostic_tests) if diagnostic_tests else None
        df.at[idx, "Other Interventions"] = ", ".join(other_names) if other_names else None
        df.at[idx, "Biological Interventions"] = ", ".join(biological_names) if biological_names else None



#just an example to see how the drug column looks
print(ALS["Drug Interventions"].head(8))
print(Alz["Drug Interventions"].head(8))


#what drugs are common across datasets?
#first let's clean the drugs column: 
#I'm not familiar with string manipulation using "re" so I used AI and online resources to help me heavily with this function
import re

def clean_drug_name(name):
    if not isinstance(name, str):
        return None
    # lowercase
    name = name.lower()
    # remove content inside parentheses
    name = re.sub(r"\(.*?\)", "", name)
    # remove extra spaces and punctuation
    name = re.sub(r"[^a-z0-9\s\-]", "", name)
    # collapse multiple spaces
    name = re.sub(r"\s+", " ", name).strip()
    return name

#create a mapping of the dataset --> set of cleaned drug named
#this will make dataset_drug_sets look like {"ALS" : {a, b, c}, "Alz" : {c, g, a}, etc...}
from collections import defaultdict

dataset_drug_sets = {}

for name, df in datasets.items():
    # extract all drugs from that dataset
    drugs = []
    for entry in df["Drug Interventions"].dropna():
        for d in entry.split(","):
            d_clean = clean_drug_name(d)
            if d_clean:
                drugs.append(d_clean)
    dataset_drug_sets[name] = set(drugs)

#find drugs in common across datasets
drug_to_datasets = defaultdict(set)

for dataset_name, drugs in dataset_drug_sets.items():
    for drug in drugs:
        drug_to_datasets[drug].add(dataset_name)
common_drugs = {drug: ds for drug, ds in drug_to_datasets.items() if len(ds) > 1}

print("Drugs in multiple datasets:\n")
for drug, ds in sorted(common_drugs.items()):
    print(f"{drug}: {', '.join(sorted(ds))}")
print(f"\nNumber of shared drugs: {len(common_drugs)}")


print(ALS["Accepting Children"].head(5))

