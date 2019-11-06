import os

CLEANUP_ONLY = False
STAYSL_EXE = \
    'C:\Program Files (x86)\STAYSL_PNNL_Suite\STAYSL_PNNL\STAYSL_PNNL.exe'
    
xsLib = os.path.join(os.getcwd(), 'xsectlib_claw_725.dat')
covLib = os.path.join(os.getcwd(), 'covarlib_claw_725.dat')
shLib = os.path.join(os.getcwd(), 'sshldlib_claw_725.dat')

for root, dirs, files in os.walk(os.getcwd()):
    
    # Clean up any existing links before creating new ones
    for file in files:
        #Skip the current working directory and anything within fluxes
        if(root == os.getcwd() or 'fluxes' in root or 'BCF' in root): 
            files = []
            break
            
        if os.path.islink( os.path.join(root,file)):
            os.unlink( os.path.join(root,file) )
        # Clean up any prior outputs
        if (('_dam.dat' in file) or ('staysl_pnnl_error' in file) or   
            ('_fir.dat' in file) or ('fort.41' in file) or 
           (('.out' in file or '_xfr.dat' in file) and (not CLEANUP_ONLY))): 
            os.remove(os.path.join(root,file))
            files = list(filter(lambda f: f != file, files))
            #print(files)

    if(CLEANUP_ONLY): continue # Just cleanup; don't execute
    
    hasInputs = any(('.dat' in f or '.inp' in f) for f in files) 
    if(not hasInputs): continue 
    
    # Determine any input files, save for our libraries
    inpFiles = [f for f in files if 
        ('.dat' in f and not ('_725.dat' in f)) 
         or ('.inp' in f) ]

    xsPath = os.path.join(root, 'xsectlib_claw_725.dat')
    covPath = os.path.join(root, 'covarlib_claw_725.dat')
    sshldPath = os.path.join(root, 'sshldlib_claw_725.dat')
    
    if(not os.path.isfile(xsPath) and not os.path.islink(xsPath) ):
        os.symlink(xsLib, xsPath)
    if(not os.path.isfile(covPath) and not os.path.islink(covPath) ):        
        os.symlink(covLib, covPath)
    if(not os.path.isfile(sshldPath) and not os.path.islink(sshldPath) ):    
        os.symlink(shLib, sshldPath)
        
    # Now run STAYSL on any inputs found
    for f in inpFiles:
        print("Now running {0:s}...".format(f))
        print(root)
        os.chdir(root) 
        runStr = '"{0:s}" "{1:s}" /Y'.format(STAYSL_EXE, os.path.join(root,f))
        os.system('"' + runStr + '"')