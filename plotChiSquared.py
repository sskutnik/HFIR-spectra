import os
from pathlib import Path
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl


font = { 'family' : 'sans-serif',
            'sans-serif' : 'Century Gothic',
            'size' : 14 }
sns.set_style("ticks")    
mpl.rc('font', **font)
mpl.rc('axes', titlepad=8)
pd.options.mode.use_inf_as_na = True

samplesFile = pd.ExcelFile('./sample_chisquared.xlsx')
dfSamples = pd.read_excel(samplesFile, sheet_name='normChiSquared')
dfSamples = dfSamples.replace({' NaN' : np.nan, ' Infinity' : np.inf})


dfSamples.dropna(inplace=True)
print(dfSamples)

g = sns.FacetGrid(dfSamples, hue="loc",col="loc",sharey=False,legend_out=True)
g = g.map(plt.hist, "ChiSquared",alpha=0.5,ls='')
g.set_xlabels(r'$\overline{\chi}^2$')
g.set_ylabels('Sample count')

plt.savefig("flux_chiSquared.pdf",bbox_inches="tight")
plt.close()
