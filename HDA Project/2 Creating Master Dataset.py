import pandas as pd
import math
import matplotlib.pyplot as plt
import seaborn as sns
import re
from collections import Counter

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

#############################################
#           CREATE A MASTER DATASET         #
#############################################

# Add a Disease column to each dataset and combine them all
for disease_name, df in datasets.items():
    df["Disease"] = disease_name  # adds a new column with the disease name

# Combine all datasets vertically into one master dataframe
master_df = pd.concat(datasets.values(), ignore_index=True)

print("Master dataset created successfully!")
print("Shape:", master_df.shape)
print("Columns:", master_df.columns.tolist())

# Optional: preview a few rows
print(master_df.head())

print("Column names: ")
print(master_df.columns.tolist())

#############################################
#           CLEAN AGE COLUMN                #
#############################################
# Ensure Age is a list of strings
master_df["Age"] = master_df["Age"].fillna("").astype(str).str.upper().str.split(',')

# Initialize columns
master_df["Accepting Children"] = 0
master_df["Accepting Adults"] = 0
master_df["Accepting Older Adults"] = 0

# Iterate and update flags
for idx, row in master_df.iterrows():
    age_groups = [a.strip() for a in row["Age"] if a.strip()]  # clean empty strings

    if any("CHILD" in a for a in age_groups):
        master_df.at[idx, "Accepting Children"] = 1
    if any("ADULT" in a and "OLDER" not in a for a in age_groups):
        master_df.at[idx, "Accepting Adults"] = 1
    if any("OLDER" in a for a in age_groups):
        master_df.at[idx, "Accepting Older Adults"] = 1

#############################################
#           CLEAN DRUG COLUMN                #
#############################################
import re
from collections import Counter

#Standardize the key text columns
master_df["Interventions"] = master_df["Interventions"].fillna("").str.lower()
master_df["Brief Summary"] = master_df["Brief Summary"].fillna("").str.lower()

# Extract "drug:" interventions
# Each entry may contain multiple interventions separated by "|"
master_df["Interventions"] = master_df["Interventions"].str.split("|")

def extract_drugs(interventions_list):
    """Return a list of drug names found in the intervention column."""
    if not isinstance(interventions_list, list):
        return []
    drugs = []
    for i in interventions_list:
        i = i.strip().lower()
        if i.startswith("drug:"):
            # Remove 'drug:' prefix
            drug_str = i.replace("drug:", "").strip()
            # Split on ' and ' to separate multiple drugs
            parts = [part.strip() for part in drug_str.split(" and ")]
            drugs.extend(parts)
    return drugs

master_df["Drug Interventions"] = master_df["Interventions"].apply(extract_drugs)

# Clean each drug name
def clean_drug_name(name):
    if not isinstance(name, str):
        return None
    name = name.lower()
    if "placebo" in name or "saline" in name:
        return None  # Drop placebos
    # Remove parentheses and make their contents another entry
    name = re.sub(r"\((.*?)\)", r", \1", name)
    # Remove punctuation except hyphens
    name = re.sub(r"[^a-z0-9\s\-]", "", name)
    # Collapse multiple spaces
    name = re.sub(r"\s+", " ", name).strip()
    # Insert space before digits if stuck to letters (e.g. 'sildenafil25 mg' -> 'sildenafil 25 mg')
    name = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', name)
    #Remove dosage info before the drug name
    name = re.sub(r'^\s*\d+(\.\d+)?\s*(mg|g|mcg|ml|units|tablet|capsule|drops)?\s+', '', name)
    # Remove dosage info after the drug name
    name = re.sub(r'\s+\d+(\.\d+)?\s*(mg|g|mcg|ml|units|tablet|capsule|drops)?', '', name)
    # Remove 'injection' and 'intranasal', etc. words from drug name
    name = re.sub(r'\binjection\b', '', name).strip()
    name = re.sub(r'\bintranasal\b', '', name)
    name = re.sub(r'\bintra-detrusor of\b', '', name)
    name = re.sub(r'\bintravenous\b', '', name)
    name = re.sub(r'\bplatinum-based\b', '', name)
    if name.isdigit() == True:
        return None 
    
    return name if name else None
   
master_df["Drug Interventions"] = master_df["Drug Interventions"].apply(
    lambda lst: [cleaned for d in lst for cleaned in [clean_drug_name(d)] if cleaned]
)

#get rid of repetitions of drugs by row
def unique_drugs(drug_list):
    return list(set(drug_list))

master_df["Drug Interventions"] = master_df["Drug Interventions"].apply(unique_drugs)

#now go through what's left manually
delete = ["standard of care", "discontinuation"]
def manual_filtering(drug_list):
    clean_list = []
    for d in drug_list:
        if d in delete or any(term in d for term in delete): 
            continue
            clean_list.append(d)
        elif d == "donepezil-":
            clean_list.append("donepezil")
        elif d == "insulin100":
            clean_list.append("insulin")
        elif "interferon" in d: 
            clean_list.append("interferon")
        elif "paclitaxel" in d: 
            clean_list.append("paclitaxel")
        elif "pembrolizumab-3475" in d: 
            clean_list.append("pembrolizumab")
        elif "pemetrexed" in d: 
            clean_list.append("pemetrexed")
        elif "pimavanserin" in d: 
            clean_list.append("pimavanserin")
        elif d == "rebif-beta-1a": 
            clean_list.append("rebif")
        elif "rivastigmine" in d: 
            clean_list.append("rivastigmine")
        elif d == "lipoic-3":
            clean_list.append("lipoic")
        elif "5-fu" in d or "5-flu" in d: 
            clean_list.append("5-fluorouracil")
        elif d == "3tc": 
            clean_list.append("lamivudine")
        elif d == "acth":
            clean_list.append("adrenocorticotropic hormone")
        elif d == "dha": 
            clean_list.append("docosahexaenoic acid")
        elif d == "fingolimod720" or d =="fty720":
            clean_list.append("fingolimod")
        elif d == "g-csf":
            clean_list.append("granulocyte-colony stimulating factor")
        elif d == "ifn":
            clean_list.append("interferon")
        elif d == "ismn":
            clean_list.append("isosorbide mononitrate")
        elif d == "l-dopa":
            clean_list.append("levodopa")
        elif "n-acetyl" in d: 
            clean_list.append("acetylcysteine")
        elif d == "sildenafil25":
            clean_list.append("sildenafil")
        elif d == "tas-102":
            clean_list.append("trifluridine")
            clean_list.append("tipiracil")
        elif "mci-186" in d: 
            clean_list.append("mci-186")
        elif "memantine" in d: 
            clean_list.append("memantine")
        elif "onabotulinumtoxin-a" in d: 
            clean_list.append("onabotulinumtoxin-a")
        elif "egcg" in d: 
            clean_list.append("egcg")
        elif "rivastigmine" in d: 
            clean_list.append("rivastigmine")
        elif "rifaximinmilligrams" in d: 
            clean_list.append("rifaximinmilligrams")
        else:
            # If none of the above conditions match, just keep the original
            clean_list.append(d)
    for item in range(len(clean_list)):
        clean_list[item] = clean_list[item].strip()
    return clean_list

master_df["Drug Interventions"] = master_df["Drug Interventions"].apply(manual_filtering)


# Flatten to get all unique drug names
all_drugs = [d for sublist in master_df["Drug Interventions"] for d in sublist]
unique_drugs = sorted(set(all_drugs))

print(f"Number of unique cleaned drugs: {len(unique_drugs)}")

potential_drug_codes = ['gsk3888130b',]

##################################################
#        CLEAN OTHER INTERVENTIONS               #
##################################################
intervention_types = [
    "Drug Interventions",
    "Device Interventions",
    "Behavioral Interventions",
    "Diagnostic Test Interventions",
    "Other Interventions",
    "Biological Interventions"
    ]
for col in intervention_types:
    master_df[col] = None
for idx, interventions_list in master_df["Interventions"].items():
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
    master_df.at[idx, "Drug Interventions"] = ", ".join(drug_names) if drug_names else None
    master_df.at[idx, "Device Interventions"] = ", ".join(device_names) if device_names else None
    master_df.at[idx, "Behavioral Interventions"] = ", ".join(behavioral_names) if behavioral_names else None
    master_df.at[idx, "Diagnostic Test Interventions"] = ", ".join(diagnostic_tests) if diagnostic_tests else None
    master_df.at[idx, "Other Interventions"] = ", ".join(other_names) if other_names else None
    master_df.at[idx, "Biological Interventions"] = ", ".join(biological_names) if biological_names else None
