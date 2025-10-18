import pandas as pd
import math
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.ticker as ticker  

from collections import defaultdict

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
    "disease: MulScle": "#A6CEE3",
    "disease: NCL": "#1F78B4",
    "disease: CJD": "#08306B",
    "disease: CTE": "#FDBF6F",
    "disease: FTD": "#FF7F00",
    "disease: Hunt": "#B15928",
    "disease: PSP": "#CAB2D6",
    "disease: MSA": "#6A3D9A",
    "disease: ALS": "#8E0152",
    "disease: Alz": "#CCCCCC",
    "disease: Park": "#777777",
    "disease: LBD": "#1B9E77",
    "disease: VascDem": "#444444"
}

diseases = ['disease: CJD', 'disease: LBD', 'disease: MSA',  'disease: Hunt', 'disease: Park', 'disease: MulScle', 'disease: CTE', 'disease: VascDem', 'disease: ALS', 'disease: PSP', 'disease: FTD', 'disease: Alz', 'disease: NCL']





#################################################
#   sexes considered for trials by disease:     #
#################################################

count_male = dict()
count_female = dict()
count_all = dict()
percent_male = dict()
percent_female = dict()
percent_all = dict() 

for disease in diseases:
    subset = master_df[master_df[disease].astype(str) == "1"]

    count_male[disease] = (subset["Sex"] == "MALE").sum()
    count_female[disease] = (subset["Sex"] == "FEMALE").sum()
    count_all[disease] = (subset["Sex"] == "ALL").sum()
    percent_male[disease] = round((count_male[disease]/(count_male[disease] + count_female[disease] + count_all[disease]))*100, 2)
    percent_female[disease] = round((count_female[disease]/(count_male[disease] + count_female[disease] + count_all[disease]))*100, 2)
    percent_all[disease] = round((count_all[disease]/(count_male[disease] + count_female[disease] + count_all[disease]))*100, 2)

    print(count_male)

    #plot: y-axis = %, x-axis = disease, 3 columns per disease (%male, %female, %all, # of trials in each bar)
group_spacing = 4
width = 1 #width of each bar
x = np.arange(len(diseases)) * group_spacing
offsets = [-width, 0, width]  

male_vals = [percent_male[d] for d in diseases]
female_vals = [percent_female[d] for d in diseases]
all_vals = [percent_all[d] for d in diseases]
fig, ax = plt.subplots(figsize=(12, 6))  
bars_male = ax.bar(x + offsets[0], male_vals, width, label='Male', color = "#A6CEE3")
bars_female = ax.bar(x + offsets[1], female_vals, width, label='Female', color="#1F78B4")
bars_all = ax.bar(x + offsets[2], all_vals, width, label='All', color="#08306B")

# Add count numbers inside the bars 
import matplotlib.patheffects as path_effects

for i, disease in enumerate(diseases):
    # Define values and counts for all three subgroups
    subgroups = [
        (male_vals[i], offsets[0], count_male[disease]),
        (female_vals[i], offsets[1], count_female[disease]),
        (all_vals[i], offsets[2], count_all[disease])
    ]

    # Plot each label with the same style and outline
    for val, offset, count in subgroups:
        txt = ax.text(
            x[i] + offset,
            val / 2,
            str(count),
            ha='center',
            va='center',
            fontsize=8,
            color='white',
            weight='bold'
        )
        txt.set_path_effects([
            path_effects.Stroke(linewidth=1, foreground='black'),
            path_effects.Normal()
        ])

#Labels and Formatting
ax.set_ylabel("Percentage of Trials (%)")
ax.set_xlabel("Diseases")
ax.set_title("Percentage of Trials Accepting Each Sex by Disease")
ax.set_xticks(x)
disease_labels = [d.replace("disease: ", "") for d in diseases]
ax.set_xticklabels(disease_labels, rotation=45, ha='right')
ax.legend()
plt.tight_layout()
plt.show()







################################################
#   ages considered for trials by disease:     # 
# ############################################## 
count_children = dict()
count_adults = dict()
count_older_adults = dict()
percent_children = dict()
percent_adults = dict()
percent_older_adults = dict() 

for disease in diseases:
    subset = master_df[master_df[disease].astype(str) == "1"]

    count_children[disease] = (subset["Accepting Children"]  == 1).sum()
    count_adults[disease] = (subset["Accepting Adults"] == 1).sum()
    count_older_adults[disease] = (subset["Accepting Older Adults"] ==1).sum()
    
    total = len(subset)

    #since a study can accept multiple age ranges, the % is calculated differently here to avoid overcounting trials
    percent_children[disease] = round((count_children[disease] / total) * 100, 2)
    percent_adults[disease] = round((count_adults[disease] / total) * 100, 2)
    percent_older_adults[disease] = round((count_older_adults[disease] / total) * 100, 2)

   #plot: y-axis = %, x-axis = disease, 3 columns per disease (%children, %adults, %older adults, # of trials in each bar)
group_spacing = 4
width = 1 #width of each bar
x = np.arange(len(diseases)) * group_spacing
offsets = [-width, 0, width]  

children_vals = [percent_children[d] for d in diseases]
adults_vals = [percent_adults[d] for d in diseases]
older_adults_vals = [percent_older_adults[d] for d in diseases]
fig, ax = plt.subplots(figsize=(12, 6))  
bars_chilren = ax.bar(x + offsets[0], children_vals, width, label='Accepting Children', color = "#A6CEE3")
bars_adults = ax.bar(x + offsets[1], adults_vals, width, label='Accepting Adults', color="#1F78B4")
bars_older_adults = ax.bar(x + offsets[2], older_adults_vals, width, label='Accepting Older Adults', color="#08306B")

# Add count numbers inside the bars 
import matplotlib.patheffects as path_effects

for i, disease in enumerate(diseases):
    # Define values and counts for all three subgroups
    subgroups = [
        (children_vals[i], offsets[0], count_children[disease]),
        (adults_vals[i], offsets[1], count_adults[disease]),
        (older_adults_vals[i], offsets[2], count_older_adults[disease]),
    ]

    # Plot each label with the same style and outline
    for val, offset, count in subgroups:
        txt = ax.text(
            x[i] + offset,
            val / 2,
            str(count),
            ha='center',
            va='center',
            fontsize=8,
            color='white',
            weight='bold'
        )
        txt.set_path_effects([
            path_effects.Stroke(linewidth=1, foreground='black'),
            path_effects.Normal()
        ])

#Labels and Formatting
ax.set_ylabel("Percentage of Trials (%)")
ax.set_xlabel("Age Ranges")
ax.set_title("Percentage of Trials Accepting Age Range by Disease")
ax.set_xticks(x)
disease_labels = [d.replace("disease: ", "") for d in diseases]
ax.set_xticklabels(disease_labels, rotation=45, ha='right')
ax.legend()
plt.tight_layout()
plt.show()











#################################################################
#   Average number of participants over all trials by disease:  # 
#################################################################
print("Average # of participants: ", math.ceil(master_df["Enrollment"].sum())/len(master_df["Enrollment"]))

for disease in diseases: 
    subset = master_df[master_df[disease].astype(str) == "1"]

    print(f"Average # of participants for {disease}: " + str(math.ceil((subset["Enrollment"].sum())/len(subset["Enrollment"]))))
  













######################################################
#       # of participants in each trial by disease    #
######################################################
#rough plot just to find outliers
#x-axis = list of trial IDs
#y-axis = list of enrollment numbers
#each point = 1 clinical trial

###Individual plots###
for disease in diseases:
    subset = master_df[master_df[disease].astype(str) == "1"]
    trial_ids = list(subset["NCT Number"])
    enrollment = list(subset["Enrollment"])
    plt.scatter(trial_ids, enrollment)
    plt.plot(trial_ids, enrollment, linestyle='--', alpha=0.6)
    plt.title(f'{disease} Trial Enrollments')
    plt.xlabel('Trial ID')
    plt.ylabel('Enrollment')
    plt.show()

###Group plot with outliers###
plot_df = pd.DataFrame([
    {"Disease": disease, "Enrollment": row["Enrollment"]}
    for _, row in master_df.iterrows()
    for disease in diseases
    if str(row.get(disease, 0)) == "1" and pd.notna(row["Enrollment"])
])

# Drop any invalid or zero enrollments if desired
plot_df = plot_df[plot_df["Enrollment"] > 0]

# Sort diseases by median enrollment
median_order = (
    plot_df.groupby("Disease")["Enrollment"]
    .median()
    .sort_values(ascending=True)
    .index
)

# Build color-blind-safe palette from your mapping
palette = {d: palette_mapping.get(d) for d in diseases}

# Make figure
plt.figure(figsize=(10, 8))

# Horizontal boxplot (stacked vertically)
ax = sns.boxplot(
    data=plot_df,
    y="Disease",
    x="Enrollment",
    order=median_order,
    palette=palette,
    showfliers= True #show outliers
)

plt.title("Trial Enrollment Sizes by Disease\n(including outliers)", fontsize=16, pad=20)
plt.xlabel("Enrollment (participants)", fontsize=12)
plt.ylabel("")
plt.grid(axis="x", linestyle="--", alpha=0.6)
plt.tight_layout()
plt.show()



###Group plot without outliers ###
plot_df = pd.DataFrame([
    {"Disease": disease, "Enrollment": row["Enrollment"]}
    for _, row in master_df.iterrows()
    for disease in diseases
    if str(row.get(disease, 0)) == "1" and pd.notna(row["Enrollment"])
])

# Drop any invalid or zero enrollments if desired
plot_df = plot_df[plot_df["Enrollment"] > 0]

# Sort diseases by median enrollment
median_order = (
    plot_df.groupby("Disease")["Enrollment"]
    .median()
    .sort_values(ascending=True)
    .index
)

# Build color-blind-safe palette from your mapping
palette = {d: palette_mapping.get(d) for d in diseases}

# Make figure
plt.figure(figsize=(10, 8))

# Horizontal boxplot (stacked vertically)
ax = sns.boxplot(
    data=plot_df,
    y="Disease",
    x="Enrollment",
    order=median_order,
    palette=palette,
    showfliers= False #don't  outliers
)

plt.title("Trial Enrollment Sizes by Disease\n(not including outliers)", fontsize=16, pad=20)
plt.xlabel("Enrollment (participants)", fontsize=12)
plt.ylabel("")
plt.grid(axis="x", linestyle="--", alpha=0.6)
plt.tight_layout()
plt.show()














######################################################
#       # of participants in each disease by year    #
######################################################
#all diseases on one plot
#x-axis: year (start date)
#y-axis: enrollment

enrollment_by_disease = {d: {} for d in diseases}

#Create a column that gives "Start Year" for plotting simplification (defined as 4 nm)
master_df["Start Year"] = master_df["Year"] = master_df["Start Date"].astype(str).str.extract(r'(\d{4})')
master_df["Start Year"] = pd.to_numeric(master_df["Start Year"], errors="coerce")
# Drop rows where Start Year is NaN or Enrollment missing
master_df = master_df.dropna(subset=["Start Year", "Enrollment"])

# Convert year to integer safely
master_df["Start Year"] = master_df["Start Year"].astype(int)

for disease in diseases:
    subset = master_df[(master_df[disease].astype(str) == "1") & (master_df["Start Year"] >= 2005)]
    if subset.empty:
        continue
    for _, row in subset.iterrows():
        year = row["Start Year"]
        enrollment = row["Enrollment"]
        if year in enrollment_by_disease[disease]:
            enrollment_by_disease[disease][year] += enrollment
        else:
            enrollment_by_disease[disease][year] = enrollment

plt.figure(figsize=(10, 6))

for disease in diseases:
    if not enrollment_by_disease[disease]:
        continue
    #sort years data
    sorted_items = sorted(enrollment_by_disease[disease].items())
    years, values = zip(*sorted_items) #"*" is the "unpacking" operator
    plt.plot(
        years, values,
        marker='o',
        label=disease.replace("disease: ", ""),
        color=palette_mapping.get(disease),
        alpha=0.8
    )

plt.title("Trial Enrollments by Disease and Year \n (starting in 2005)")
plt.xlabel("Start Year")
plt.ylabel("Enrollment")
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
ax = plt.gca()
ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
plt.tight_layout()
plt.show()



















#########################################################
#       how long did trials tend to last per disease?   #
#########################################################
#box and whisker plots; 13 (one for each disease)
#length = ["Completion Date"] - ["Start Date"]

#add columns for formatting master_df["Start Date"], master_df["Completion Date"] (only want month and year for comparison purposes): call "Completion Year-Month" and "Start Year-Month"
#right now the formats are "yyyy-mm" and "yyyy-mm-dd"

#add dummy day to date just so it can be read as datetime (not considering days because of this)
def fix_dates(x):
    if isinstance(x, str) and len(x) == 7 and x[4] == '-':  # format yyyy-mm
        return x + '-01'
    return x

master_df["Start Date"] = master_df["Start Date"].apply(fix_dates)
master_df["Start Date"] = pd.to_datetime(master_df["Start Date"], errors='coerce')

master_df["Completion Date"] = master_df["Completion Date"].apply(fix_dates)
master_df["Completion Date"] = pd.to_datetime(master_df["Completion Date"], errors='coerce')

# Create 'Start Year-Month' column as YYYY-MM string
master_df["Start Year-Month"] = master_df["Start Date"].dt.to_period("M").astype(str)

# Create 'Completion Year-Month' column as YYYY-MM string
master_df["Completion Year-Month"] = master_df["Completion Date"].dt.to_period("M").astype(str)

#want a dictionary in the form of {disease: [length1, length2, length3]} etc. , where length in months

master_df["Duration (months)"] = (
    (master_df["Completion Date"].dt.year - master_df["Start Date"].dt.year) * 12 +
    (master_df["Completion Date"].dt.month - master_df["Start Date"].dt.month)
)
# Drop any rows where duration is NaN or negative (optional)
master_df = master_df[master_df["Duration (months)"].notna() & (master_df["Duration (months)"] >= 0)]
length_of_studies = {}

for disease in diseases:
    # Select studies where this disease column == 1 (or True)
    mask = master_df[disease] == 1
    # Collect the list of durations (non-null and non-negative)
    durations = (
        master_df.loc[mask, "Duration (months)"]
        .dropna()
        .astype(int)
        .tolist()
    )
    length_of_studies[disease] = durations

# Convert dictionary to tidy DataFrame for plotting
plot_df = (
    pd.DataFrame([
        {"Disease": disease, "Duration (months)": duration}
        for disease, durations in length_of_studies.items()
        for duration in durations
    ])
)

# Sort diseases by median duration 
median_order = (
    plot_df.groupby("Disease")["Duration (months)"]
    .median()
    .sort_values(ascending=True)  # ascending so shortest is at top
    .index
)

# Build color palette (colorblind-safe)
palette = {d: palette_mapping.get(d) for d in diseases}

# Create figure
plt.figure(figsize=(10, 8))

# Horizontal boxplots
sns.boxplot(
    data=plot_df,
    y="Disease",
    x="Duration (months)",
    order=median_order,
    palette=palette,
    showfliers= True #show outliers
)

# Formatting
plt.title("Clinical Trial Durations by Disease", fontsize=16, pad=20)
plt.xlabel("Duration (months)", fontsize=12)
plt.ylabel("")
plt.grid(axis="x", linestyle="--", alpha=0.6)
plt.tight_layout()

plt.show()














#################################################
#     what drugs are common across datasets?    #
#################################################
#create a mapping of the dataset --> set of cleaned drug named
#this will make dataset_drug_sets look like {"ALS" : {a, b, c}, "Alz" : {c, g, a}, etc...}
disease_drug_relationship = {d.replace("disease: ", ""): set() for d in diseases}

def parse_drugs(drug_str):
    if pd.isna(drug_str) or drug_str == "[]" or drug_str.strip() == "":
        return []
    drug_str = drug_str.strip()
    if drug_str.startswith("[") and drug_str.endswith("]"):
        drug_str = drug_str[1:-1]
    
    drugs = []
    for item in drug_str.split(","):
        cleaned_drug = item.strip().strip("'").strip('"')
        if cleaned_drug != "":
            drugs.append(cleaned_drug)
    return drugs
master_df['Drug Interventions Parsed'] = master_df['Drug Interventions'].apply(parse_drugs)
disease_drug_relationship = {}

for disease in diseases:
    # Filter rows where the one-hot disease column == 1
    disease_rows = master_df[master_df[disease] == 1]
    
    all_drugs = set()
    for drugs in disease_rows['Drug Interventions Parsed']:
        all_drugs.update(drugs)
    
    disease_name = disease.replace("disease: ", "")
    disease_drug_relationship[disease_name] = all_drugs

# Print results
for disease, drugs in disease_drug_relationship.items():
    print(f"{disease}: {drugs}")



#make an inversion of the disease-drug relationship
drug_disease_relationship = defaultdict(set)  # drug -> set of diseases

for disease, drugs in disease_drug_relationship.items():
    for drug in drugs:
        drug_disease_relationship[drug].add(disease)

#filter drugs used in >1 disease and count diseases
multi_disease_drugs = {drug: diseases for drug, diseases in drug_disease_relationship.items() if len(diseases) > 1}

print(f"{len(multi_disease_drugs)} drugs were tested on >1 disease")








#cycle through drugs over the years, frequency of how many studies they appeared in and for what disease (color-code diseases)
#check each drug individually to make sure that they are, in fact, drugs?




