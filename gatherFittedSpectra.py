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

sampleLocs = {
   #"FT4" : [ "JP31" ],
   "FT5" : ["JP1","JP3","JP6","JP7","JP9","JP10","JP11",\
            "JP12","JP13","JP15","JP15","JP16","JP18",\
            "JP19","JP20","JP23","JP30","T1","T2",\
            "CTR-62","CTR-63", "JP31"],\
   "PTP" : [ "JP2","JP4","JP5","JP8","JP17","CTR-30",\
             "CTR-31","CTR-32","CTR-33","CTR-34","CTR-35",\
             "CTR-36","CTR-39","CTR-40","CTR-41","CTR-41",\
             "CTR-42-43","CTR-44-45","CTR-46","CTR-47",\
             "CTR-48","CTR-53","CTR-54"],\
   "RB" : [ "RB1", "RB5","TRIST-ER-1-2","TRIST-ER-7-8",\
            "HFIR-RB-11J","HFIR-RB-12J","HFIR-MFE-RB-17J",\
            "HFIR-MFR-19J" ]
}
startDir = Path(os.getcwd()).stem

sampleDFs = list()
for root, dirs, files in os.walk(os.getcwd()):
   print(files)
   if('sta_xfr.dat') in files:
      
      specDir = Path(root)
      if(Path(root).stem == "BOC" or Path(root).stem == "EOC"):
         specDir = Path(root).parent
         
      sampleNum = specDir.parent.stem
      if(sampleNum == startDir):
         print(sampleNum, specDir, Path(root))
         sampleNum = specDir.stem
         subSample = ""
      else:
         subSample = specDir.stem

      thisLoc = ""
      for k in sampleLocs.keys():
         if( sampleNum in sampleLocs[k]):
            thisLoc = k
      if(thisLoc == ""):
         print("NULL LOC: ", root)      
      print(os.path.join(root,"sta_xfr.dat"))
      dfTmp = pd.read_csv(os.path.join(root,"sta_xfr.dat"),sep='\t',\
                          skipinitialspace=True,encoding="ANSI")
      dfTmp["loc"] = thisLoc
      dfTmp["sample"] = sampleNum
      dfTmp["subsample"] = subSample
      
      sampleDFs.append(dfTmp)

print(sampleDFs)      
dfSamples = pd.concat(sampleDFs,ignore_index=True)

grid = sns.relplot(data=dfSamples,x="E (MeV)", y="Adj. F×Eavg",\
            kind="line",ci="sd",\
            hue="loc", aspect=1.5)
grid.set(xscale="log",yscale="log",ylim=(1E13,1E15),ylabel=r"Lethargy-weighted flux $\left(\frac{n}{cm^2\cdot MeV}\right)$")

dfSamples.to_csv("HFIR_fitted.csv")

samples85MW = ["JP9","JP10","JP11","JP12","JP13","JP15","JP16", "JP17","JP18",\
         "JP19","JP20","JP23","JP31","CTR-62","CTR-63","TRIST-ER-1-2","TRIST-ER-7-8"]

dfSamples = dfSamples.assign(Power=100.0)
dfSamples.loc[dfSamples["sample"].isin(samples85MW),'Power'] = 85.0

grid = sns.relplot(data=dfSamples,x="E (MeV)", y="Adj. F×Eavg",\
            kind="line",ci="sd",col="Power",\
            hue="loc", aspect=1.5)
grid.set(xscale="log",yscale="log",ylim=(1E13,1E15),xlim=(1E-9,2.5E1),ylabel=r"Lethargy-weighted flux $\left(\frac{n}{cm^2\cdot MeV}\right)$")
grid.set_titles(col_template="{col_var} = {col_name} MW")
plt.title = ("HFIR Adjusted Flux Spectrum")
plt.savefig("HFIR_fitted.pdf",bbox_inches="tight")
plt.close()

eGrouped = dfSamples.groupby(["E (MeV)", "loc", "Power"])
dfFluxAvg = pd.DataFrame(columns=["E (MeV)", "loc", "Power", "Avg. Flux"])
eSeries = [ ]
for n,grp in eGrouped:
   rowData = list(n)
   rowData.append(grp["Adj. F×Eavg"].mean())
   rowSeries = pd.Series(rowData,copy=False,index=["E (MeV)","loc", "Power", "Avg. Flux"])
   eSeries.append(rowSeries)

dfEavg = pd.DataFrame(eSeries)
dfEavg.to_csv("HFIR_fitted_avg.csv")

dfAvg85MW = (dfEavg.loc[dfEavg['Power'] == 85.0]).reset_index()
dfAvg100MW = (dfEavg.loc[dfEavg['Power'] == 100.0]).reset_index()

dfRatio = dfAvg100MW[['E (MeV)', 'loc', 'Avg. Flux']]
dfRatio = dfRatio.assign(Ratio = (dfAvg85MW['Avg. Flux'] / dfAvg100MW["Avg. Flux"]))
#dfRatio.assign(Ratio = ratio)

gridAvg = sns.relplot(data=dfRatio,x="E (MeV)", y="Ratio",\
            kind="line",hue="loc",aspect=1.5)
gridAvg.set(xscale="log",xlim=(1E-9,2.5E1),ylabel="Flux ratio (85 MW : 100 MW)",\
   title="HFIR adjusted flux ratio (85 MW : 100 MW)")
plt.title = ("HFIR Adjusted Flux Spectrum")
plt.savefig("HFIR_ratio.pdf",bbox_inches="tight")
plt.close()

dfAvgFlux = pd.read_csv("./fluxes/MCNP_avg.csv").drop("Unnamed: 0",axis=1).rename({"Lethargy-weighted" : "MCNP"})

print(dfAvg85MW["loc"].unique())

RB_rows = dfAvg85MW.loc[dfAvg85MW["loc"] == "RB"]
dfAvg85MW = dfAvg85MW.drop(RB_rows).reset_index()
#print(dfAvgFlux)
dfAvgFlux.join(dfAvg85MW, on=["E (MeV)", "loc"])
print(dfAvgFlux)
# Figure out the join op for dfAvgFlux & dfAvg85MW to plot the comparison by loc
#dfAvgFlux = pd.concat(dfAvgFlux,dfAvg85MW)
#print(dfAvgFlux)
#plt.plot("E (MeV)", "Avg. Flux", data=dfEavg)
#plt.show()
