NOTES FOR JOE AND EMMA
----------------------

To Analyze:  
- Drugs considered across years, prevalence of those drugs, are some drugs used for multiple diseases? Maybe select only the most prevalent to do further analysis on.
- How to consider drug codes? 

PubTator example (for finding drugs and diseases on pubmed?):
https://www.ncbi.nlm.nih.gov/research/pubtator3/docsum?text=@CHEMICAL_Warfarin%20

UMLS: 
https://uts.nlm.nih.gov/uts/umls/home?_gl=1*i9kq1k*_ga*MTA2NDQ3MzMzNy4xNzQxMjc0MjEw*_ga_P1FPTH9PL4*czE3NjEwNzI2ODIkbzUkZzEkdDE3NjEwNzI3OTEkajIxJGwwJGgw*_ga_7147EPK006*czE3NjEwNzI2ODIkbzYkZzEkdDE3NjEwNzI3OTEkajIxJGwwJGgw

NetworkX: 
https://www.kaggle.com/code/alireza151/networkx-tutorial


Next Steps: 
- done ---1 consolidate all datasets, adding "DISEASE" as a label
- done ---2 break up drugs, interventions, gender, age
- done ---3 clean up drugs
- done ---4 any repeated NCT Trials across diseases??? If yes, determine how to treat these repeated trials
- done ---5 save master dataset
- mostly done ---6 exploration plots and drugs shared by >= 2 diseases
- done ---7 UMLS to find drug terminology; create master dataset for all diseases and drugs that are saved in disease_disease_relationship dataset
- 8 disease-disease network with drug connections using networkX package
- 9 find drug names in pubmed from disease&drug dataset and do similar process

