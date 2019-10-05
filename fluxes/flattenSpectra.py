import numpy as np
import pandas as pd
import seaborn as sb
import os
import click
import matplotlib.pyplot as plt
import palettable.cartocolors as ccolors


SHOW_FIGS = False
IMG_SUFFIX = "pdf"

def generateFluxFiles(df, zone=None):
    
    nGrp = 252
    iTherm = 0
    tNorm = 1.0
    tmpr = 300 # K
    
    fluxConfig = "{0:4d}{1:4d} {2:9.4e}{3:10.4f}{4:10.4f}\n" \
                  .format(nGrp, iTherm, tNorm, tmpr, 0.0)
                  
    miniSpec = "212  103  137  28  15  10  30  50  100  40"
    
    # Organize flux files into directories
    zonePath = os.path.join(os.getcwd(), zone)
    if not os.path.exists(zonePath):
        os.makedirs(zonePath)
    
    for pos in df['Position'].unique():        
        fileName = os.path.join( zonePath, 
            '{0:s}_axPos{1:d}_fluxCards.txt'.format(zone,pos))
        outf = open(fileName, 'w')
    
        # Write out uncertainty ranges for flux bins
        errTuples = []
        for err in df[['energy', 'sigma', 'Differential']] \
            .loc[df['Position'] == pos].itertuples(index=False,name=None):
            fluxErr = err[1] #*err[2]

            if errTuples:
                if (np.isclose(fluxErr,errTuples[-1][1],rtol=0.5,atol=1.E-4)):
                    # Use the highest uncertainty within each range of similar values                    
                    if(fluxErr > errTuples[-1][1]):
                        errTuples[-1] = (errTuples[-1][0], fluxErr)
                    continue
            errTuples.append( (err[0], fluxErr) )
 
        errE = ""
        errBin = ""
        for i in range(0,len(errTuples)):
            if((i % 8) == 0 and i > 0): 
                errE += "\n"
                errBin += "\n"
            errE += "{0:8.3e} ".format(errTuples[i][0])
            errBin += "{0:8.3e} ".format(errTuples[i][1])
        
        outf.write("Estimated flux uncertainties\n")
        outf.write("{0:4d}\n{1:s}\n{2:s}\nMCNP-estimated MG flux\n{3:s}" \
            .format(len(errTuples),errE,errBin,fluxConfig))
        
        # Now input estimated MG differential flux
        #flux = df[['energy', 'Differential']].loc[df['Position'] == pos].to_numpy()
        flux = df[['energy', 'Lethargy-weighted']].loc[df['Position'] == pos].to_numpy()
        fluxStr = ''
        # Drop underflow bin (< Emin); get NGP+1 bounds, NGP fluxes
        enStr = '{0:10.6e}'.format(flux[0,0])
        for i in range(1,flux.shape[0]):
            if((i % 6) == 0 and i > 0): 
                fluxStr += "\n"
                enStr += "\n"
            enStr += " {0:10.6e}".format(flux[i,0]) 
            fluxStr += " {0:10.6e}".format(flux[i,1]) 
              
        outf.write("{0:s}\n{1:s}\n{2:s}".format(enStr,fluxStr,miniSpec))
        outf.close()
        

def generateFluxes(df, eName, deName, talName, suffix = None):
    diffName = "Differential"
    lethName = "Lethargy-weighted"
    if(suffix is not None):
        talName  += " " + suffix
        diffName += " " + suffix
        lethName += " " + suffix
		
    df[diffName] = df[talName].div(df[deName])
    df[lethName] = df[diffName].multiply(df[eName])
    df['sigma'].fillna(1.0)
    return df


def flattenSheet(df, tallyName, sigmaName, eName, deName, suffix = None):
	df_flat = pd.wide_to_long(df,
		stubnames=[tallyName, sigmaName], i=[eName],j="Position").reset_index()
	df_flat.rename(columns = {tallyName : 'Tally',sigmaName : 'sigma'},inplace=True)
	return generateFluxes(df_flat, eName, deName, 'Tally', suffix)
	
	
# Gather data

tallyFile = pd.ExcelFile('./HFIR-tallies.xlsx')

df_FT5 = pd.read_excel(tallyFile, sheet_name='FT-5')
df_RB = pd.read_excel(tallyFile, sheet_name='RB-1')
 
 
df_HT = pd.read_excel(tallyFile, sheet_name='HT')
df_HT_flat = flattenSheet(df_HT, 'Ax pos #', 'Sigma HT', 'energy', 'deltaE')
generateFluxFiles(df_HT_flat, "HT")


df_PTP = pd.read_excel(tallyFile, sheet_name='PTP')
df_PTP_flat = flattenSheet(df_PTP, 'Ax pos #', 'Sigma PTP-', 'energy', 'deltaE')
generateFluxFiles(df_PTP_flat, "PTP")


df_FT5_axial_BOC = pd.read_excel(tallyFile, sheet_name='FT-5 Axial (BOC)')
df_FT5_axBOC = flattenSheet(df_FT5_axial_BOC, 'T(E) Zone #', 'Sigma(E) Zone #', 'energy', 'deltaE')
generateFluxFiles(df_FT5_axBOC, "FT-5")


df_FT4_axial_BOC = pd.read_excel(tallyFile, sheet_name='FT-4 Axial (BOC)')
df_FT4_axBOC = flattenSheet(df_FT4_axial_BOC, 'T(E) Zone #', 'Sigma(E) Zone #', 'energy', 'deltaE')
generateFluxFiles(df_FT4_axBOC, "FT-4")

df_FT3_axial_BOC = pd.read_excel(tallyFile, sheet_name='FT-3 Axial (BOC)')
df_FT3_axBOC = flattenSheet(df_FT3_axial_BOC, 'T(E) Zone #', 'Sigma(E) Zone #', 'energy', 'deltaE')
generateFluxFiles(df_FT3_axBOC, "FT-3")

#plt.savefig("RB_flux.png")


plt.yscale('log')
plt.xscale('log')
plt.title("Radial flux variation through the flux trap region")
plt.ylim([1E-6,1E-3])


sb.lineplot(data=df_FT3_axBOC,x="energy",y="Lethargy-weighted", label="FT-3", \
		palette=sb.diverging_palette(240, 10, l=75.,s=99, n=9,center="dark"))	
sb.lineplot(data=df_FT4_axBOC,x="energy",y="Lethargy-weighted", label="FT-4", \
		palette=sb.diverging_palette(240, 10, l=75.,s=99, n=9,center="dark"))		
sb.lineplot(data=df_FT5_axBOC,x="energy",y="Lethargy-weighted", label="FT-5", \
		palette=sb.diverging_palette(240, 10, l=75.,s=99, n=9,center="dark"))
sb.lineplot(data=df_HT_flat,x="energy",y="Lethargy-weighted", label='HT', \
		palette=sb.diverging_palette(240, 10, l=75.,s=99, n=9,center="dark"))
plt.legend()
plt.savefig("FT_fluxComp." + IMG_SUFFIX)
if(SHOW_FIGS): plt.show()
plt.close()
	
		

plt.yscale('log')
plt.xscale('log')
sb.lineplot(data=df_HT_flat,x="energy",y="Lethargy-weighted",hue="Position", \
			palette=sb.diverging_palette(240, 10, l=75.,s=99, n=9,center="dark"))
	
	

plt.ylim([1E-6,1E-3])
plt.title("Hydraulic tube (B-3)")
plt.ylabel("Lethargy-weighted flux (A.U.)")
plt.xlabel("Energy (MeV)")
plt.savefig("HT_flux." + IMG_SUFFIX)
if(SHOW_FIGS): plt.show()
plt.close()



plt.yscale('log')
plt.xscale('log')
sb.lineplot(data=df_PTP_flat,x="energy",y="Lethargy-weighted",hue="Position", \
			palette=sb.diverging_palette(240, 10, l=75.,s=99, n=7,center="dark"))
			#palette=sb.color_palette(ccolors.diverging.Geyser_7.mpl_colors, n_colors=9))
	
plt.ylim([1E-6,1E-3])
plt.title("Peripheral target position (PTP)")
plt.ylabel("Lethargy-weighted flux (A.U.)")
plt.xlabel("Energy (MeV)")
plt.savefig("PTP_flux." + IMG_SUFFIX)
if(SHOW_FIGS): plt.show()
plt.close()
	
	

plt.xscale("log")
plt.yscale("log")


df_RB = generateFluxes(df_RB, "energy", "deltaE", "T", "(BOC)")
df_RB = generateFluxes(df_RB, "energy", "deltaE", "T", "(EOC)")
#df_FT5 = generateFluxes(df_FT5, "energy", "deltaE", "T", "(BOC)")
#df_FT5 = generateFluxes(df_FT5, "energy", "deltaE", "T", "(EOC)")

plt.errorbar(x=df_RB["energy"],y=df_RB["Lethargy-weighted (BOC)"],\
	yerr=df_RB["Sigma (BOC)"]*df_RB["Lethargy-weighted (BOC)"], label="RB (BOC)")
plt.errorbar(x=df_RB["energy"],y=df_RB["Lethargy-weighted (EOC)"],
	yerr=df_RB["Sigma (EOC)"]*df_RB["Lethargy-weighted (EOC)"],label="RB (EOC)")

#plt.errorbar(x=df_FT5["energy"],y=df_FT5["Lethargy-weighted (BOC)"],\
#	yerr=df_FT5["Sigma (BOC)"]*df_FT5["Lethargy-weighted (BOC)"], label="FT-5 (BOC)")
#plt.errorbar(x=df_FT5["energy"],y=df_FT5["Lethargy-weighted (EOC)"],
#	yerr=df_FT5["Sigma (EOC)"]*df_FT5["Lethargy-weighted (EOC)"],label="FT-5 (EOC)")
		
plt.ylim([1E-6,1E-3])

plt.legend()
#plt.savefig("RB_flux.png")


plt.yscale('log')
plt.xscale('log')
plt.title("Flux comparison: Hyd. tube, Outer flux trap (region 5), & Rem. Be")
sb.lineplot(data=df_HT_flat,x="energy",y="Lethargy-weighted", label="HT", \
		palette=sb.diverging_palette(240, 10, l=75.,s=99, n=9,center="dark"))
sb.lineplot(data=df_FT5_axBOC,x="energy",y="Lethargy-weighted", label="FT-5", \
		palette=sb.diverging_palette(240, 10, l=75.,s=99, n=9,center="dark"))
sb.lineplot(data=df_FT4_axBOC,x="energy",y="Lethargy-weighted", label="FT-4", \
		palette=sb.diverging_palette(240, 10, l=75.,s=99, n=9,center="dark"))
sb.lineplot(data=df_FT3_axBOC,x="energy",y="Lethargy-weighted", label="FT-3", \
		palette=sb.diverging_palette(240, 10, l=75.,s=99, n=9,center="dark"))		

		
plt.savefig("RB_comparison." + IMG_SUFFIX)
if(SHOW_FIGS): plt.show()
