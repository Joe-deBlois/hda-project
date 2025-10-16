import pandas as pd
import math
import matplotlib.pyplot as plt
import seaborn as sns

#first set correct working directory
from pathlib import Path

# Get the directory of the current script
wd = Path(__file__).parent

# Change the current directory to that folder
import os
datasets_dir = wd / "Datasets"
os.chdir(datasets_dir)

print("Current working directory:", Path.cwd())

master_df = pd.read_csv("CT_Master_DataFrame.csv")
drug_inventory = pd.read_csv("CT_Drug_Inventory.csv")

#how many diseases being considered? 13
#color mapping (should be visible for colorblind people, too)
palette_mapping = {
    "disease: MulScle":  "#EE6677",
    "disease: NCL": "#228833",
    "disease: CJD":  "#4477AA",
    "disease: CTE": "#CCBB44",
    "disease: FTD" : "#66CCEE",
    "disease: Hunt": "#AA3377", 
    "disease: PSP" : "#BBBBBB",
    "disease: MSA": "#000000",
    "disease: ALS" : "#FFA500", 
    "disease: ALZ" :"#00CC99",
    "disease: Park" : "#9966CC", 
    "disease: LBD" :"#FF99CC", 
    "disease: VascDem" :"#6699FF"
}

diseases = ['disease: CJD', 'disease: LBD', 'disease: MSA',  'disease: Hunt', 'disease: Park', 'disease: MulScle', 'disease: CTE', 'disease: VascDem', 'disease: ALS', 'disease: PSP', 'disease: FTD', 'disease: Alz', 'disease: NCL']






#sexes considered for trials by disease: 
for disease in diseases:
    subset = master_df[master_df[disease] == 1]

    count_male = (subset["Sex"] == "MALE").sum()
    count_female = (subset["Sex"] == "FEMALE").sum()
    count_all = (subset["Sex"] == "ALL").sum()

    print(f"\n{disease}:")
    print("# of male-only studies: " + str(count_male) + "     " + str(round((count_male/(count_male + count_female + count_all))*100, 2)) + "%")
    print("# of female-only studies: "+ str(count_female) + "     " + str(round((count_female/(count_male + count_female + count_all))*100, 2)) + "%")
    print("# of all-sex studies: "+ str(count_all) + "     " + str(round((count_all/(count_male + count_female + count_all))*100, 2)) + "%")







#ages considered for trials by disease: 







#Average number of participants (rounded up to nearest integer) over all trials by disease: 







#Rough plot to find outliers for # of participants in each trial by disease







#what drugs are common across datasets?
#create a mapping of the dataset --> set of cleaned drug named
#this will make dataset_drug_sets look like {"ALS" : {a, b, c}, "Alz" : {c, g, a}, etc...}







#cycle through drugs over the years, frequency of how many studies they appeared in and for what disease (color-code diseases). 



    
    print("# of studies accepting children: ", df["Accepting Children"].sum())
    print("# of studies accepting adults: ", df["Accepting Adults"].sum())
    print("# of studies accepting older adults: ", df["Accepting Older Adults"].sum())
        
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


    #Graph the breakdown of gender by year over all studies of this disease
    #x-axis: start dates (year)
    #y-axis: sex
    #each datapoint is a clinical trial
    df["Start Year"] = pd.to_datetime(df["Start Date"], format="mixed", errors="coerce").dt.year
    df["Sex"] = df["Sex"].str.upper().fillna("UNKNOWN")
    palette = {
    "FEMALE": "deeppink",
    "MALE": "royalblue",
    "ALL": "mediumseagreen",
    "UNKNOWN": "gray"}
    sns.countplot(data=df, x="Start Year", hue="Sex", palette = palette)
    plt.title(f"{name} Trials by Gender Eligibility and Year")
    plt.xlabel("Start Year")
    plt.ylabel("Number of Trials")
    plt.legend(title="Sex Category")
    plt.show()

    #Graph the breakdown of age by year over all studies of this disease
    #x-axis: start dates (year)
    #y-axis: age
    #each datapoint is a clinical trial
    plt.figure(figsize=(10,6))
    for col, color in zip(
        ["Accepting Children", "Accepting Adults", "Accepting Older Adults"],
        ["gold", "red", "royalblue"]
    ):
        yearly = df.groupby("Start Year")[col].sum()
        plt.plot(yearly.index, yearly.values, marker="o", label=col.replace("Accepting ", ""), color=color, alpha = 0.5)

    plt.title(f"{name} Trials — Age Inclusion Trends Over Time")
    plt.xlabel("Start Year")
    plt.ylabel("Number of Trials")
    plt.legend(title="Age Group")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.show()



#what drugs are common across datasets?

#create a mapping of the dataset --> set of cleaned drug named
#this will make dataset_drug_sets look like {"ALS" : {a, b, c}, "Alz" : {c, g, a}, etc...}
from collections import defaultdict

dataset_drug_sets = {}
all_drugs = [] 
for name, df in datasets.items():
    # extract all drugs from that dataset
    drugs = []
    for entry in df["Drug Interventions"].dropna():
        for d in entry.split(","):
            d_clean = clean_drug_name(d)
            if d_clean:
                drugs.append(d_clean)
                all_drugs.append(d_clean)
    dataset_drug_sets[name] = set(drugs)
all_drugs = list(set(all_drugs))

#check each drug by hand now
#number of unchecked drugs: 
len(all_drugs)

keywords = ["saline", "cell", "therapy", "therapies", "placebo", "vehicle", "treatment", "infusion", "injection", "anesthesia", "physician", "injection", "control", "study", "18f", "11c", "pet", "f18", "radiotracer", "f18", "11c", "piB", "florbet", "tau", "ioflupane", "gadoter", "mbq", "neuraceq", "pe2i", "ucb-j", "definity"]
all_drugs = [drug for drug in all_drugs if not any(k in drug for k in keywords)]

#number of checked drugs
len(all_drugs)

#some drugs say "and"


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
print(f"\nNumber of all drugs: {len(all_drugs)}")

