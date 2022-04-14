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


dfEavg = pd.read_csv("HFIR_fitted_avg.csv", usecols=[1,2,3,4], names=["E (MeV)", "loc", "Power", "Adjusted"], index_col=False, header=0)
dfAvg85MW = (dfEavg.loc[dfEavg['Power'] == 85.0])
dfAvgFlux = pd.read_csv("./fluxes/MCNP_avg.csv", header=0, usecols=[1,2,4], names=["E (MeV)","MCNP", "loc"], sep=',',index_col=False)
dfAvg85MW = dfAvg85MW[dfAvg85MW["loc"] != "RB"]

#print(dfAvgFlux)
#print(dfAvg85MW)

#print(dfAvg85MW.shape, dfAvgFlux.shape)
#dfAvgFlux.join(dfAvg85MW, on=["E (MeV)", "loc"])
#print(dfAvgFlux)
# Figure out the join op for dfAvgFlux & dfAvg85MW to plot the comparison by loc
#dfAvgFlux = pd.concat(dfAvgFlux,dfAvg85MW)
#print(dfAvgFlux)
g = sns.FacetGrid(dfAvg85MW, hue="loc", legend_out=True,aspect=1.5,height=8)
g.map(sns.lineplot, "E (MeV)", "Adjusted").add_legend()#.add_legend(bbox_to_anchor=(1.08, 0.5))

dfAvgFlux.loc[dfAvgFlux["loc"] == "PTP","MCNP"] = dfAvgFlux.loc[dfAvgFlux["loc"] == "PTP","MCNP"].mul(4E18)
dfAvgFlux.loc[dfAvgFlux["loc"] == "FT-5","MCNP"] = dfAvgFlux.loc[dfAvgFlux["loc"] == "FT-5","MCNP"].mul(3.1E18)

g2 = sns.lineplot(x="E (MeV)", y="MCNP", hue="loc", data=dfAvgFlux,ax=g.ax, dashes=True, legend=False)
g.set(xscale="log", yscale="log", ylabel=r'Lethargy-weighted flux',ylim=[1E12,1E15],xlim=[5E-10,30],title="MCNP Cycle 400 & Adjusted Flux")

for i in range(2,4):
    g2.lines[i].set_linestyle("--")


#plt.show()
plt.savefig("flux_adj_mcnp_comp.pdf",bbox_inches="tight")
plt.close()


g = sns.FacetGrid(dfAvg85MW, hue="loc", legend_out=True,aspect=1.0,height=8)
g.map(sns.lineplot, "E (MeV)", "Adjusted")
g2 = sns.lineplot(x="E (MeV)", y="MCNP", hue="loc", data=dfAvgFlux,ax=g.ax, dashes=True, legend=False)
g.set(xscale="log", yscale="log", ylabel=r'Lethargy-weighted flux',ylim=[1E12,1E15],xlim=[5E-10,1E-6])

for i in range(2,4):
    g2.lines[i].set_linestyle("--")

g.add_legend(bbox_to_anchor=(0.95, 0.5))
g.set(xlim=[5E-10,1E-6])
g.set(aspect=1.0)
plt.savefig("flux_adj_mcnp_comp_thermal.pdf",bbox_inches="tight")

