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

#what are all possible weights?
unique_weights = ct_ddn_df["Weight"].unique()
print(len(unique_weights))
print(unique_weights)

#step 1: initialize graph
G = nx.Graph()

#step 2: fill graph
for idx, row in ct_ddn_df.iterrows():
    G.add_edge(row["Disease 1"], row["Disease 2"], weight = row["Weight"])


#step 3: dictionaries of node and edge colors/styles
#edge_mapping = {
#    4: "#A6CEE3",
#    8: "#1F78B4",
#    24: "#08306B",
#    5: "#FDBF6F",
#    6: "#FF7F00",
#    7: "#B15928",
#    3: "#CAB2D6",
#    19: "#6A3D9A",
#    21: "#8E0152",
#    1: "#CCCCCC",
#    2: "#777777",
#    10: "#1B9E77",
#}

#edge_colors = [edge_mapping[G[u][v]['weight']] for u, v in G.edges()]

scale_factor = 0.3  # adjust for aesthetics
edge_widths = [G[u][v]['weight'] * scale_factor for u, v in G.edges()]

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

#white nodes with black outlines
nx.draw_networkx_nodes(
    G, 
    pos,
    node_color='white',
    edgecolors='black',
    node_size=1000,
    linewidths=2  # thickness of the black border
)

#edges with colors mapped by weight
nx.draw_networkx_edges(G, pos, edge_color= "#1B9E77", width=edge_widths)


#disease labels
nx.draw_networkx_labels(G, pos, labels=labels, font_size=9, font_weight='bold')

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
                          markerfacecolor='white', markeredgecolor='black', markersize=10)
                   for abbr, full in legend_diseases.items()]

# Place legend outside plot
plt.legend(handles=legend_elements, bbox_to_anchor=(1, 0.8), loc='upper left', fontsize=10)

# Adjust layout to make room for legend
plt.tight_layout()

plt.show()
