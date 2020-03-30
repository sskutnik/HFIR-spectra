import os
from pathlib import Path
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sampleLocs = {
   "FT4" : [ "JP31" ],
   "FT5" : ["JP1","JP3","JP4","JP4","JP5","JP6","JP7",\
            "JP8","JP9","JP10","JP11","JP12","JP13","JP15",\
            "JP15","JP16","JP18","JP19","JP20","JP23","JP30",\
            "T1","T2","CTR-62","CTR-63"],\
   "PTP" : [ "JP2","JP17","CTR-30","CTR-31","CTR-32",\
             "CTR-33","CTR-34","CTR-35","CTR-36","CTR-39","CTR-40",\
             "CTR-41","CTR-41","CTR-42-43","CTR-44-45",\
             "CTR-46","CTR-47","CTR-48","CTR-53","CTR-54"],\
   "RB" : [ "RB1", "RB5","TRIST-ER-1-2","TRIST-ER-7-8",\
            "HFIR-RB-11J","HFIR-RB-12J","HFIR-MFE-RB-17J",\
            "HFIR-MFR-19J" ]
}
startDir = Path(os.getcwd()).stem

sampleDFs = list()
for root, dirs, files in os.walk(os.getcwd()):
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
      
dfSamples = pd.concat(sampleDFs,ignore_index=True)
#print(dfSamples)

#f, ax = plt.subplots(figsize=(7, 7))
#ax.set(xscale="log", yscale="log")
grid = sns.relplot(data=dfSamples,x="E (MeV)", y="Adj. F×Eavg",kind="line",\
            hue="loc")
grid.set(xscale="log",figsize=(7,7))
plt.show()