import pandas as pd
import networkx as nx
import random
import matplotlib.pyplot as plt

random.seed(12345)

#first set correct working directory
from pathlib import Path

# Get the directory of the current script
wd = Path(__file__).parent

# Change the current directory to that folder
import os
working_dir = wd / "CT DDN Data"
os.chdir(working_dir)

print("Current working directory:", Path.cwd())

#import graph data
ct_ddn_df = pd.read_csv("CT_DDN.csv")

#import num trials per disease (col1 = "Disease", col2 = "Trial Count")
disease_trials_counts = pd.read_csv("CT_disease_trials_counts_df.csv")
trial_count_dict = pd.Series(disease_trials_counts['Trial Count'].values,
                             index=disease_trials_counts['Disease']).to_dict()

#what are all possible weights?
unique_weights = ct_ddn_df["Weight"].unique()
print(len(unique_weights))
print(unique_weights)

#step 1: initialize graph
G = nx.Graph()

#step 2: fill graph
for idx, row in ct_ddn_df.iterrows():
    G.add_edge(row["Disease 1"], row["Disease 2"], weight = row["Weight"])


#step 3: dictionaries of node and edge aethetics
edge_scale_factor = 0.3  
edge_widths = [G[u][v]['weight'] * edge_scale_factor for u, v in G.edges()]

node_mapping = {
    "LBD" : "LBD",
    "ALS" : "ALS",
    "CTE" : "CTE", 
    "Hunt" : "Hunt",
    "Alz" : "Alz", 
    "MSA" : "MSA",
    "PSP" : "PSP", 
    "Park" : "Park", 
    "NCL" : "NCL", 
    "MulScle" : "MS", 
    "VascDem" : "VD", 
    "FTD" : "FTD", 
    "CJD" : "CJD"
}

labels = {node: node_mapping.get(node, node) for node in G.nodes()}

# Scale node outlines based on trial counts
max_trials = max(trial_count_dict.values())
min_width = 1
max_width = 20

# Map trial counts to linewidths between 1 and 5
node_linewidths = [
    min_width + (max_width - min_width) * (trial_count_dict.get(node, 1) / max_trials)
    for node in G.nodes()
]

#step 4: define layout options and choose one 
layout_choice = "two_rows" 

if layout_choice == "two_rows":
    nodes = list(G.nodes())
    n = len(nodes)
    half = n // 2
    pos = {}
    for i, node in enumerate (nodes):
        if i < half: 
            pos[node] = (i, 1) #top row
        else: 
            pos[node] = (i- half, 0) #bottom row: 
elif layout_choice == "circular":
    pos = nx.circular_layout(G)
else: 
    pos = nx.spring_layout(G)

#step 5: draw the graph
plt.figure(figsize=(16, 8))

#white nodes with green outlines
#node outlines scale with the number of trials per disease in the DDN
nx.draw_networkx_nodes(
    G, 
    pos,
    node_color='white',
    edgecolors='#1B9E77',
    node_size=1000,
    linewidths= node_linewidths  # thickness of the black border
)

#edges with colors mapped by weight
nx.draw_networkx_edges(G, pos, edge_color= "#1B9E77", width=edge_widths)


#disease labels (placing the text over the node outlines)
nx.draw_networkx_labels(
    G, 
    pos, 
    labels=labels, 
    font_size=12, 
    font_weight='bold', 
    font_color='black',           
    horizontalalignment='center', 
    verticalalignment='center'    
)

#title & show plot
plt.title("Clinical Trials Data Disease-Disease Network", fontsize=14)
plt.axis("off")

legend_diseases = {
    "LBD" : "Lewy Body Dementia", 
    "Park" : "Parkinson's",
    "MS" : "Multiple Sclerosis", 
    "VD" : "Vascular Dementia", 
    "ALS" : "Amyotrophic Lateral Sclerosis", 
    "PSP" : "Progressive Supranuclear Palsy",
    "FTD" : "Frontotemporal Dementia",
    "Alz" : "Alzheimer's", 
    "MSA" : "Multiple System Atrophy",
    "Hunt" : "Huntington's",
    "CTE" : "Chronic Traumatic Encephalopathy",
    "NCL" : "Neuronal Ceroid Lipofuscinoses"
}

# Create custom legend
from matplotlib.lines import Line2D

legend_elements = [Line2D([0], [0], marker='o', color='w', label=f"{abbr} - {full}",
                          markerfacecolor='white', markeredgecolor='#1B9E77', markersize=10)
                   for abbr, full in legend_diseases.items()]

# Place legend outside plot
plt.legend(handles=legend_elements, bbox_to_anchor=(1, 0.8), loc='upper left', fontsize=10)

# Show plot
plt.tight_layout()
plt.show()
