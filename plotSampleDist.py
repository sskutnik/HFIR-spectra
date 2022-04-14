import os
from pathlib import Path
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl


font = { 'family' : 'sans-serif',
            'sans-serif' : 'Century Gothic',
            'size' : 14 }
sns.set_style("ticks")    
mpl.rc('font', **font)
mpl.rc('axes', titlepad=8)

samplesFile = pd.ExcelFile('./sample_locations.xlsx')


dfSamples = pd.read_excel(samplesFile, sheet_name='locations')

g = sns.catplot(x="Location", y="Height (cm)", col="Power",scale="width",kind="violin",scale_hue=True,inner="point",cut=0.5,subplot_kws={"alpha":0.5},data=dfSamples)
g.set(alpha=.75)
plt.savefig("sample_dist.pdf",bbox_inches="tight")
plt.close()

""" ax = sns.violinplot(x="Location", y="Height (cm)", hue="Power",scale="width",scale_hue=True,inner=None,split=True,data=dfSamples)
sns.swarmplot(x="Location", y="Height (cm)", data=dfSamples,hue="Power")
plt.savefig("sample_dist_swarm.pdf",bbox_inches="tight")
plt.close() """