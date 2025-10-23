import pandas as pd
import networkx as nx


#first set correct working directory
from pathlib import Path

# Get the directory of the current script
wd = Path(__file__).parent

# Change the current directory to that folder
import os
working_dir = wd / "CT DDN Data"
os.chdir(working_dir)

print("Current working directory:", Path.cwd())

