#Next steps: 
#done ---1) consolidate all datasets, adding "DISEASE" as a label
#done ---2) break up drugs, interventions, gender, age
#done ---3) clean up drugs
#4) any repeated NCT Trials across diseases??? If yes, determine how to treat these repeated trials
#5) save master dataset
#6) exploration plots and drugs shared by >= 2 diseases
#7) network?
#8) find drug names in pubmed and do similar process




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

unique_drugs = set(drug for drugs in master_df["Drug Interventions"] for drug in drugs)
print(f"Number of unique drugs before manual cleaning: {len(unique_drugs)}") #858
print(f"Number of empty rows in Drug Interventions column before manual cleaning: {sum(master_df['Drug Interventions'].apply(lambda x: x == []))}") #678
print("\nThe next step in the drug intervention cleaning is to accept only drug codes, drug code candidates, and drugs (including supplements). This omits imaging agents, tracers, and other non-drug strings")

#now go through what's left manually
delete = ["standard of care", "discontinuation", "11c-er", "11c-pbr", "11c-pib", "11cmk-6884", "11cpei", "18f flutemetamol", "18f-flutemetamol", "18fflutemetamol", "18f-av-1451", "18fav-1451", "18f-dtbz av-133", "18f-fdg", "18f-florbetaben", "18f-mk-6240", "18fmk-6240mbq", "18fflorbetapir pet imaging", "18fgtp", "18fmk-3328", "3ka-apc protein", "acr", "active comparator", "ain", "akst", "al", "alks", "all subjects", "amdxp", "amx", "androgen deprivation therapy adt", "antihistamine", "antiparkinsonian agent s", "atm fog in pd", "auto-m-bfs", "autonomic testing on", "bac treatment", "baf", "baseline disease modifying therapies dmts", "bg", "bgdmf", "bi", "bi25 mg", "bi50mg", "bidose", "biib", "bpn", "bym", "cct", "chf1x", "chf2x", "chf3x", "cholinesterase inhibitor", "cle", "cnp", "control", "cor", "corticosteroid", "cpib", "ct", "cvn", "cvnhigh dose", "cvnlow dose", "cystoscopic of botox into the urinary bladder", "disease modifying therapy", "dose", "e", "egb", "elnd", "ena", "endothelin receptor antagonists", "fab", "fdc blue", "gaml", "general anesthesia with isoflurane", "glpg", "gold nanocrystals", "grf", "gsk", "gsk25 mg tablet", "gskb", "gwp-p", "gz", "ib", "idmt", "incb", "infusion", "infusions of young plasma", "intensive control of sbp","ir cd-ld", "lka", "locally approved contrast medium for contrast enhanced magnetic resonance imaging mri", "lps", "lu ae", "lunasin regimen", "ly", "ly- iv", "ly- sc", "matched vehicle", "mesenchymal stem cells", "mk", "nd", "neod", "nt", "ocr", "off levodopa", "opc", "optimal drug therapy", "optimized antiparkinsonian treatment", "optimized medical treatment", "other parkinsons disease treatments", "pbt", "pdeinhibitor", "proiv", "prosc", "prospekta", "rad", "rnf", "rns", "ro", "rop", "rorg", "rpc", "rphbotanical drug product", "sar", "sparchigh dose", "sparclow dose", "spm", "srx", "standard control of sbp", "standard ms dmt", "standard ms dmts", "standard treatment with a conventional drug", "sti", "study drug", "syn", "tb", "thndosage a", "thndosage b", "thndosage c", "tissue selective estrogen complex", "trx16 mgday", "trx8 mgday", "ucb-j", "cystoscopic of botox into the urinary bladder", "discontinuation of disease modifying therapy", "locally approved contrast medium for contrast enhanced magnetic resonance imaging mri", "methylene blue", "sham discontinuation", "folfiri", "mfolfox", "ne", "bi50 mg"]
def manual_filtering(drug_list):
    clean_list = []
    for d in drug_list:
        #make sure this matches EXACT terms in delete, not "term in d"
        if d in delete or "contrast enhanced magnetic" in d or "botox into the" in d or "active treatment" in d or "infusion" in d: 
            continue
        elif d == "cisplatinm":
            clean_list.append("cisplatin")
        elif "suvorexant" in d: 
            clean_list.append("suvorexant")
        elif "abiraterone" in d: 
            clean_list.append("abiraterone")
        elif "4-amino" in d: 
            clean_list.append("fampridine")
        elif "fluorouracil" in d: 
            clean_list.append("fluorouracil")
        elif "zolpidem" in d: 
            clean_list.append("zolpidem")
        elif "safinamide" in d: 
            clean_list.append("safinamide")
        elif d == "vx-745":
            clean_list.append("neflamapimod")
        elif "vamorolone" in d: 
            clean_list.append("vamorolone")
        elif "estriol" in d: 
            clean_list.append("estriol")
        elif d == "ulevostinag":
            clean_list.append("ulevostinib")
        elif "tysabri" in d:
            clean_list.append("natalizumab")
        elif d == "tvp-1012":
            clean_list.append("rasagiline")
        elif "triheptanoin" in d: 
            clean_list.append("triheptanoin")
        elif "propofol" in d: 
            clean_list.append("propofol")
        elif d == "tj-68":
            clean_list.append("yokukansan")
        elif d == "tigan":
            clean_list.append("trimethobenzamide")
        elif d == "theracurmin hp":
            clean_list.append("curcumin")
        elif "tetrabenazine" in d: 
            clean_list.append("tetrabenazine")
        elif "testosterone" in d: 
            clean_list.append("testosterone")
        elif "teriflunomide" in d: 
            clean_list.append("teriflunomide")
        elif "tenofovir alafenamide" in d: 
            clean_list.append("tenofovir alafenamide")
        elif "temelimab" in d: 
            clean_list.append("temelimab")
        elif d == "tecfidera":
            clean_list.append("dimethyl fumarate")
        elif "td-9855" in d: 
            clean_list.append("ampreloxetine")
        elif "sirolimus" in d: 
            clean_list.append("sirolimus")
        elif "tauroursodeoxycholic acid" in d: 
            clean_list.append("tauroursodeoxycholic acid")
        elif "trifluridine" in d: 
            clean_list.append("trifluridine")
        elif d == "tak-935":
            clean_list.append("soticlestat")
        elif "t-817ma" in d: 
            clean_list.append("t-817ma")
        elif "suvn-502" in d: 
            clean_list.append("suvorexant")
        elif "apomorphine" in d: 
            clean_list.append("apomorphine")
        elif d == "strattera":
            clean_list.append("atomoxetine")
        elif "fish oil" in d: 
            clean_list.append("omega-3 fatty acids")
        elif "som2" in d or "som3" in d: 
            clean_list.append("som")
        elif "solifenacin" in d: 
            clean_list.append("solifenacin")
        elif d == "sodium oligo-mannurarate":
            clean_list.append("sodium oligomannate")
        elif d == "sls-005":
            clean_list.append("trehalose")
        elif "sirolimus" in d: 
            clean_list.append("sirolimus")
        elif "sinemet" in d: 
            clean_list.append("carbidopa-levodopa")
        elif "simufilam" in d: 
            clean_list.append("simufilam")
        elif "sep-363856" in d: 
            clean_list.append("ulotaront")
        elif "sebelipase alfa" in d or "sbc-102" in d: 
            clean_list.append("sebelipase alfa")
        elif "scopolamine" in d or d == "sd-809": 
            clean_list.append("scopolamine")
        elif d == "sativex":
            clean_list.append("nabiximols")
        elif "sage-217" in d: 
            clean_list.append("zuranolone")
        elif "wve-003" in d: 
            clean_list.append("wve-003")
        elif d == "s-warfarin":
            clean_list.append("warfarin")
        elif d == "rvt-101":
            clean_list.append("intepirdine")
        elif "rotigotine" in d: 
            clean_list.append("rotigotine")
        elif "rosiglitazone" in d: 
            clean_list.append("rosiglitazone")
        elif "ropinirolel-dopa" in d or d == "ropl-dopa":
            clean_list.append("ropinirole + levodopa")
        elif "ropinirole" in d: 
            clean_list.append("ropinirole")
        elif "rituximab" in d: 
            clean_list.append("rituximab")
        elif "rifaximin" in d: 
            clean_list.append("rifaximin")
        elif "revusiran" in d: 
            clean_list.append("revusiran")
        elif "requip" in d: 
            clean_list.append("requip")
        elif "corticotropin" in d: 
            clean_list.append("corticotropin")
        elif d == "rebif" or "rebif new" in d: 
            clean_list.append("interferon beta-1a")
        elif "rasagiline" in d: 
            clean_list.append("rasagiline")
        elif d == "rapamune" or d == "rapamycin":
            clean_list.append("sirolimus")
        elif "pramipexole" in d: 
            clean_list.append("pramipexole")
        elif "quinidine" in d: 
            clean_list.append("quinidine")
        elif d == "qr-110": 
            clean_list.append("sepofarsen")
        elif "pti-125" in d: 
            clean_list.append("simufilam")
        elif "preladenant" in d: 
            clean_list.append("preladenant")
        elif "pramipexole" in d: 
            clean_list.append("pramipexole")
        elif "phenazopyridine" in d: 
            clean_list.append("phenazopyridine")
        elif "pf-06751979" in d: 
            clean_list.append("pf-06751979")
        elif "pramipexole rasagiline" in d: 
            clean_list.append("pramipexole rasagiline")
        elif "pb0607" in d: 
            clean_list.append("pb060")
        elif "adrabetadex" in d: 
            clean_list.append("adrabetadex")
        elif "oxaloacetate" in d: 
            clean_list.append("oxaloacetate")
        elif "selegiline" in d: 
            clean_list.append("selegiline")
        elif "levodopacarbidopa" in d: 
            clean_list.append("levodopa-carbidopa")
        elif d == "onabotulinumtoxin-a": 
            clean_list.append("onabotulinumtoxin a")
        elif "ofatumumab" in d: 
            clean_list.append("ofatumumab")
        elif "ocrelizumab" in d: 
            clean_list.append("ocrelizumab")
        elif "nuedexta" in d: 
            clean_list.append("nuedexta")
        elif "nicotinamide" in d: 
            clean_list.append("nicotinamide")
        elif d == "newgamivig": 
            clean_list.append("immunoglobulin")
        elif "ndlevodopacarbidopa" in d: 
            clean_list.append("levodopa-carbidopa")
        elif "natalizumab" in d: 
            clean_list.append("natalizumab")
        elif "acetylcysteine" in d: 
            clean_list.append("acetylcysteine")
        elif "moxifloxacin" in d: 
            clean_list.append("moxifloxacin")
        elif d == "mirapex la": 
            clean_list.append("pramipexole")
        elif "miglustat" in d: 
            clean_list.append("miglustat")
        elif "methylphenidate" in d: 
            clean_list.append("methylphenidate")
        elif "mesdopetam" in d: 
            clean_list.append("mesdopetam")
        elif "melphalan" in d: 
            clean_list.append("melphalan")
        elif "melperone" in d: 
            clean_list.append("melperone")
        elif "medi-551" in d: 
            clean_list.append("medi-551")
        elif "pramipexole" in d: 
            clean_list.append("pramipexole")
        elif "madopar" in d: 
            clean_list.append("madopar")
        elif "nicotine" in d or d == "nic-15": 
            clean_list.append("nicotine")
        elif "cannabis" in d: 
            clean_list.append("cannabis")
        elif "lipoic acid" in d: 
            clean_list.append("lipoic acid")
        elif "levodopa carbidopa" in d or "levodopa-carbidopa" in d or d == "levodopabenserazide" or d == "levodopabenzerazide" or d == "levodopacarbidopa" or d == "levodopacarbidopa ldcd": 
            clean_list.append("levodopa-carbidopa") 
        elif "leucovorin" in d: 
            clean_list.append("leucovorin")
        elif "istradefylline" in d: 
            clean_list.append("istradefylline")
        elif d == "ismn xl" or "isosorbide mononitrate" in d:
            clean_list.append("isosorbide mononitrate")
        elif "isis1" in d or "isis3" in d or "isis6" in d or "isis9" in d: 
            clean_list.append("isis")
        elif "ipx1" in d or "ipx2" in d or "ipx9" in d or "ipxer cd" in d: 
            clean_list.append("ipx")
        elif "insulin" in d: 
            clean_list.append("insulin")
        elif d == "incobotulinumtoxina":
            clean_list.append("incobotulinum toxin a")
        elif "immunoglobulin" in d: 
            clean_list.append("immunoglobulin")
        elif "ifn betaa tiw" in d: 
            clean_list.append("interferon beta")
        elif "icosapent ethyl" in d: 
            clean_list.append("icosapent ethyl")
        elif "gocovri" in d: 
            clean_list.append("gocovri")
        elif "glatiramer acetate" in d: 
            clean_list.append("glatiramer acetate")
        elif "galantamine" in d: 
            clean_list.append("galantamine")
        elif "filgrastim" in d or d == "granulocyte-colony stimulating factor g-csf": 
            clean_list.append("filgrastim")
        elif d == "fty": 
            clean_list.append("fingolimod")
        elif "flutemetamol" in d: 
            clean_list.append("flutemetamol")
        elif "fluorouracil" in d: 
            clean_list.append("fluorouracil")
        elif "florbetapir" in d: 
            clean_list.append("florbetapir")
        elif "florbetaben" in d: 
            clean_list.append("florbetaben")
        elif "fingolimod" in d or d == "gilenya": 
            clean_list.append("fingolimod")
        elif "fampridine" in d: 
            clean_list.append("fampridine")
        elif "glatiramer acetate" in d: 
            clean_list.append("glatiramer acetate")
        elif "exenatide" in d: 
            clean_list.append("exenatide")
        elif "exelon" in d: 
            clean_list.append("rivastigmine")
        elif "evp-6124" in d: 
            clean_list.append("evp-6124")
        elif "everolimus" in d: 
            clean_list.append("everolimus")
        elif "es-citalopram" in d: 
            clean_list.append("escitalopram")
        elif "empagliflozin" in d: 
            clean_list.append("empagliflozin")
        elif "scyllo-inositol" in d: 
            clean_list.append("scyllo-inositol")
        elif d == "egcg": 
            clean_list.append("epigallocatechin gallate")
        elif "vigabatrin" in d: 
            clean_list.append("vigabatrin")
        elif "isradipine" in d: 
            clean_list.append("isradipine")
        elif "duloxetine" in d: 
            clean_list.append("duloxetine")
        elif "dronabinol" in d: 
            clean_list.append("dronabinol")
        elif "droxidopa" in d: 
            clean_list.append("droxidopa")
        elif "donepezil" in d: 
            clean_list.append("donepezil")
        elif "docosahexaenoic acid" in d: 
            clean_list.append("docosahexaenoic acid")
        elif d == "dl-alpha-tocopherol":
            clean_list.append("vitamin e")
        elif "diclofenac" in d: 
            clean_list.append("diclofenac")
        elif d == "dextromethorphanquinidine dmq": 
            clean_list.append("dextromethorphan + quinidine")
        elif "dextromethorphan" in d and "dextromethorphanqui" not in d: 
            clean_list.append("dextromethorphan")
        elif "dexpramipexole" in d: 
            clean_list.append("dexpramipexole")
        elif d == "datscan ioflupanei": 
            clean_list.append("datscan ioflupane")
        elif "dantrolene" in d: 
            clean_list.append("dantrolene")
        elif "dalfampridine" in d: 
            clean_list.append("dalfampridine")
        elif d == "daily citalopram":
            clean_list.append("citalopram")
        elif "cvt-301" in d: 
            clean_list.append("cvt-301")
        elif "creatine" in d: 
            clean_list.append("creatine")
        elif d == "coq" or "coenzyme q" in d: 
            clean_list.append("coenzyme q10")
        elif "nilotinib" in d: 
            clean_list.append("nilotinib")
        elif "clonidine" in d: 
            clean_list.append("clonidine")
        elif "cere-120" in d: 
            clean_list.append("cere-120")
        elif "carboplatin" in d: 
            clean_list.append("carboplatin")
        elif "carbidopa-levodopa" in d or d == "carbidopalevodopa as prescribed by treating physician":
            clean_list.append("carbidopa-levodopa")
        elif "brexpiprazole" in d: 
            clean_list.append("brexpiprazole")
        elif "natalizumab" in d: 
            clean_list.append("natalizumab")
        elif "bay-9172" in d: 
            clean_list.append("florbetaben")
        elif "azd" in d: 
            clean_list.append("azd")
        elif "azilect" in d: 
            clean_list.append("rasagiline")
        elif "avp-786" in d:
            clean_list.append("avp-786")
        elif "avp-923" in d: 
            clean_list.append("avp-923")
        elif "avi-4658" in d: 
            clean_list.append("eteplirsen")
        elif "donepezil" in d or d == "aricept evess": 
            clean_list.append("donepezil")
        elif "aspirin" in d: 
            clean_list.append("aspirin")
        elif d == "apo-go" or d == "apokyn" or "apomorphine" in d:
            clean_list.append("apomorphine")
        elif "doxorubicin" in d: 
            clean_list.append("doxorubicin")
        elif "synera" in d: 
            clean_list.append("synera")
        elif "ht-1001" in d: 
            clean_list.append("ht-1001")
        elif "cap-1002" in d: 
            clean_list.append("cap-1002")
        elif "alemtuzumab" in d: 
            clean_list.append("alemtuzumab")
        elif "agb220" in d: 
            clean_list.append("agb220")
        elif "ent-01" in d: 
            clean_list.append("ent-01")
        elif "ads-5102" in d: 
            clean_list.append("amantadine")
        elif "acetaminophen" in d or "paracetamol" in d: 
            clean_list.append("acetaminophen")
            clean_list.append("paracetamol")
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
            clean_list.append("fluorouracil")
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
            clean_list.append("onabotulinumtoxin a")
        elif "egcg" in d: 
            clean_list.append("egcg")
        elif "rivastigmine" in d: 
            clean_list.append("rivastigmine")
        elif "rifaximinmilligrams" in d: 
            clean_list.append("rifaximinmilligrams")
        elif "amantadine" in d: 
            clean_list.append("amantadine")
        elif "pembrolizumab" in d: 
            clean_list.append("pembrolizumab")
        elif "betaferonbetaseron" in d: 
            clean_list.append("interferon beta-1b")
        elif d == "methyloprednisolone":
            clean_list.append("methylprednisolone")
        elif "-128800" in d: 
            clean_list.append("act-128800")
        else:
            # If none of the above conditions match, just keep the original
            clean_list.append(d)
    for item in range(len(clean_list)):
        clean_list[item] = clean_list[item].strip()
    return clean_list

master_df["Drug Interventions"] = master_df["Drug Interventions"].apply(manual_filtering)


# Flatten to get all unique drug names
unique_drugs = None
unique_drugs = sorted(set(drug for drugs in master_df["Drug Interventions"] for drug in drugs))
print(f"Number of unique drugs after manual cleaning: {len(unique_drugs)}") #452
print(f"Number of empty rows in Drug Interventions column after manual cleaning: {sum(master_df['Drug Interventions'].apply(lambda x: x == []))}") #826

#Some of the drugs I kept looked like drug codes, so those are here for later reference:
potential_drug_codes = []
for d in unique_drugs:
    if any(char.isdigit() for char in d):
        if "omega" not in d and "interferon" not in d and "antibody" not in d and "coenzyme" not in d: 
            potential_drug_codes.append(d)

drugs = []
for d in unique_drugs:
    if d not in potential_drug_codes:
        drugs.append(d)

print("Should be equal: " + str(len(unique_drugs)) + " and " +str(len(potential_drug_codes)+len(drugs)))











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










##################################################
#     SAVE MASTER DATASET (CLINICALTRIALS.GOV)   #
##################################################