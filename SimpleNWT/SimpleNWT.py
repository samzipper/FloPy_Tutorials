## SimpleNWT
# Super simple model to see if I can get MODFLOW-NWT to work.

import flopy.modflow as mf
import platform

# what version of modflow to use?
modflow_v = 'mfnwt'  # 'mfnwt' or 'mf2005'

# where is your MODFLOW executable?
if (modflow_v=='mf2005'):
    if platform.system() == 'Windows':
        path2mf = 'C:/Users/Sam/Dropbox/Work/Models/MODFLOW/MF2005.1_12/bin/mf2005.exe'
    else: 
        path2mf = modflow_v
elif (modflow_v=='mfnwt'):
    if platform.system() == 'Windows':
        path2mf = 'C:/Users/Sam/Dropbox/Work/Models/MODFLOW/MODFLOW-NWT_1.1.4/bin/MODFLOW-NWT.exe'
    else:
        path2mf = modflow_v
        
# set up super simple model
ml = mf.Modflow(modelname="testmodel", exe_name=path2mf, version=modflow_v)
dis = mf.ModflowDis(ml)
bas = mf.ModflowBas(ml)
oc = mf.ModflowOc(ml)

# choose solver package depending on modflow version
if (modflow_v=='mf2005'):
    lpf = mf.ModflowLpf(ml)
    pcg = mf.ModflowPcg(ml)
elif (modflow_v=='mfnwt'):
    upw = mf.ModflowUpw(ml)
    nwt = mf.ModflowNwt(ml)

ml.write_input()
ml.run_model()