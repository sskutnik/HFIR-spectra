import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

def fit_group(dfFlux, loc, power, egroups):

   for eGrp in egroups:
       #print(eGrp)
       fitData = dfFlux.loc[(dfFlux["Power"] == power) & (dfFlux["Loc"] == loc) & (dfFlux["Group"] == eGrp)][["Height (cm)","Flux"]]
       #print(eGrp,fitData[["Height (cm)", "Flux"]].to_numpy())#.loc[fitData])
       xData = fitData["Height (cm)"].to_numpy(dtype="float32")
       yData = fitData["Flux"].to_numpy()
       params = np.polyfit(xData,yData,2)
       print(loc, eGrp, power, params / params[2])

 
# Generate raw CSV from STAYSL greps
df_egroups = pd.read_table('./egroups.dat', usecols=[0,1,2,5], engine='python', 
                            encoding='utf-16', names=['Path', 'Group', 'Flux', 'Uncert'],sep='\s+')

df_egroups[['Experiment', 'Sample', 'garbage']] = df_egroups.Path.str.split("\\",2,expand=True)
df_egroups.drop(['Path', 'garbage'],axis=1,inplace=True)
df_egroups.replace({'Sample_' : ''},regex=True,inplace=True)
df_egroups.to_csv('./egroups.csv')

# Processed data with power & location metadata
df_egroups = pd.read_csv('./egroups_extended.csv')
df_egroups.replace({'thermal' : 'Thermal', 'epithermal' : 'Epithermal', \
                    'fast' : 'Fast', 'fast_2' : '> 1.0 MeV'}, inplace=True)

df_axLocs = pd.read_excel('STAYSL_PNNL Data.xlsx', sheet_name='Sheet3', usecols=[1,3,4]).fillna(method='ffill')

df_axLocs.rename(columns={"Sample ID" : 'Sample'},inplace=True)
df_egroups = df_egroups.merge(df_axLocs,on=['Experiment', 'Sample'])

for power in (85.0, 100.0):
   fit_group(df_egroups, "PTP", power, ["Thermal", "Epithermal", "Fast"])
   fit_group(df_egroups, "FT-5", power, ["Thermal", "Epithermal", "Fast"])
   fit_group(df_egroups, "RB", power, ["Thermal", "Epithermal", "Fast"])

df_egroups.to_csv('egroups_locs.csv')
#g = sns.relplot(data=df_egroups,x='Height (cm)', y='Flux',col='Loc', row='Power', hue='Group')

#plt.show()

g = sns.catplot(data=df_egroups,x='Group',y='Flux',hue='Power',col='Loc',kind='box',aspect=0.9)
#plt.show()
plt.savefig('energy_dist.pdf', bbox_inches='tight')
plt.close()

#df_egroups["Uncert"] = df_egroups["Uncert"].div(100.)

avgSeries = []
dfAvgFluxes = pd.DataFrame(columns=['Group', 'Power', 'Loc', 'Avg. Flux', 'Uncertainty'])
for n, grp in df_egroups.groupby(['Group', 'Power', 'Loc']):    
    avgFlux = grp["Flux"].mean()
    # Calculate root mean square of sigmas for each position
    avgSig = np.sqrt(grp["Uncert"].apply(np.square,raw=True).sum())/grp["Sample"].nunique()
    dataVals = list(n)
    dataVals.extend([avgFlux,avgSig])
    grpSeries = pd.Series(data=dataVals, index=dfAvgFluxes.columns)
    avgSeries.append(grpSeries)
    #dfAvgFluxes = pd.concat([dfAvgFluxes,grpSeries],ignore_index=True,axis=0)

dfAvgFluxes = pd.DataFrame(avgSeries)
#    print(serAvg)
    #pd.concat(dfAvgFluxes, pd.Series(grp, avgFlux, avgSig))
    #print(n)
    #print(grp["Flux"].mean())
    
#print(dfAvgFluxes)
