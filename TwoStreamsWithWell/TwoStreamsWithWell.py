## TwoStreamsWithWell.py
# Two streams at different elevations with a well halfway in between.

import numpy as np
import flopy
import flopy.utils.binaryfile as bf
import matplotlib.pyplot as plt
import flopy.utils.postprocessing as pp

runid = 'BigPumpK1e-6'
modelname = 'TwoStreamsWithWell'
modflow_v = 'mfnwt'
path2mf = 'C:/Users/Sam/Dropbox/Work/Models/MODFLOW/MODFLOW-NWT_1.1.4/bin/MODFLOW-NWT.exe'

# key parameters to experiment with
Qw = -2
head_L = 110
head_R = 90
hk = 1e-6*86400  # horizontal K [m/d], convert K [m/s] to K [m/d]
vka = 1.         # Kv = Kh/vka

# Assign name and create modflow model object
mf = flopy.modflow.Modflow(modelname, exe_name=path2mf, 
                           version=modflow_v,
                           model_ws="C:/Users/Sam/WorkGits/FloPy_Tutorials/TwoStreamsWithWell")

# discretization (space) - these should be the same as in your R script                         
nlay = 1
nrow = 1
ncol = 101
delr = 100
delc = 24

xcoord = np.linspace((delc/2), ncol*delc-(delc/2), ncol)

# discretization (time)
nper = 1
perlen = [1]
nstp = [1]
steady = [True]

# make top elevation
ibound = np.ones([nrow,ncol])
tops = ibound*np.linspace(head_L, head_R, ncol)
bots = tops - 100

## set up flow properties and solver depending on version of MODFLOW
sy = 0.10   # specific yield (using 50% of domain mean porosity for now)
ss = 1e-5   # specific storage
laytyp = 1  # layer type
layvka = 1  # if layvka != 0, Kv = Kh/vka

# make modflow objects
dis = flopy.modflow.ModflowDis(mf, nlay, nrow, ncol, 
                               delr=delr, delc=delc,
                               top=tops, botm=bots,
                               nper=nper, perlen=perlen, 
                               nstp=nstp, steady=steady)
bas = flopy.modflow.ModflowBas(mf, ibound=ibound, strt=tops)
upw = flopy.modflow.ModflowUpw(mf, hk=hk, vka=vka, sy=sy, ss=ss, layvka=layvka, laytyp=laytyp)
nwt = flopy.modflow.ModflowNwt(mf)

# set up river
riv_cond = round(hk*10*10*1)   # river bottom conductance
riv_list = [
           [0, 0, 0, tops[0,0], riv_cond, tops[0,0]-10],  
           [0, 0, ncol-1, tops[0,ncol-1], riv_cond, tops[0,ncol-1]-10]
           ]
riv_spd = {0: riv_list}
    
# make MODFLOW object
riv = flopy.modflow.ModflowRiv(mf, stress_period_data=riv_spd, ipakcb=61,
                               filenames=[modelname+'.riv', modelname+'.riv.out'])

## output control
spd = {(0, 0): ['save head', 'save budget', 'save drawdown', 'print head', 'print budget', 'print drawdown']}
oc = flopy.modflow.ModflowOc(mf, stress_period_data=spd, compact=True)

## write input and run
mf.write_input()

# run model
success, mfoutput = mf.run_model()
if not success:
    raise Exception('MODFLOW did not terminate normally.')

## look at budget outputs
rivout = bf.CellBudgetFile(modelname+'.riv.out', verbose=False)
rivout_3D = rivout.get_data(totim=1, text='RIVER LEAKAGE')
leakage_L_noPump = rivout_3D[0][0][1]
leakage_R_noPump = rivout_3D[0][1][1]
rivout.close()

## get head
h = bf.HeadFile(modelname+'.hds', text='head')
head_noPump = h.get_data(totim=1)
h.close()

## now: set up pumping well
wel_spd = {0: [[0, 0, round(ncol/2), Qw]]}
wel = flopy.modflow.ModflowWel(mf, stress_period_data=wel_spd)

# write input, run
mf.write_input()
success, mfoutput = mf.run_model()
if not success:
    raise Exception('MODFLOW did not terminate normally.')
    
# get output
rivout = bf.CellBudgetFile(modelname+'.riv.out', verbose=False)
rivout_3D = rivout.get_data(totim=1, text='RIVER LEAKAGE')
leakage_L_pump = rivout_3D[0][0][1]
leakage_R_pump = rivout_3D[0][1][1]
rivout.close()

h = bf.HeadFile(modelname+'.hds', text='head')
head_pump = h.get_data(totim=1)
h.close()

## now: make 10 layers
nlay = 5
bots = np.empty([nlay, nrow, ncol])
bots[0,:,:] = tops-20
bots[1,:,:] = tops-40
bots[2,:,:] = tops-60
bots[3,:,:] = tops-80
bots[4,:,:] = tops-100

dis = flopy.modflow.ModflowDis(mf, nlay, nrow, ncol, 
                               delr=delr, delc=delc,
                               top=tops, botm=bots,
                               nper=nper, perlen=perlen, 
                               nstp=nstp, steady=steady)
ibound = np.ones([nlay,nrow,ncol])
bas = flopy.modflow.ModflowBas(mf, ibound=ibound, strt=tops)
upw = flopy.modflow.ModflowUpw(mf, hk=hk, vka=vka, sy=sy, ss=ss, layvka=layvka, laytyp=laytyp)


# no pump
wel_spd = {0: [[0, 0, round(ncol/2), 0]]}
wel = flopy.modflow.ModflowWel(mf, stress_period_data=wel_spd)

# write input, run
mf.write_input()
success, mfoutput = mf.run_model()
if not success:
    raise Exception('MODFLOW did not terminate normally.')

# output
rivout = bf.CellBudgetFile(modelname+'.riv.out', verbose=False)
rivout_3D = rivout.get_data(totim=1, text='RIVER LEAKAGE')
leakage_L_noPump_10lay = rivout_3D[0][0][1]
leakage_R_noPump_10lay = rivout_3D[0][1][1]
rivout.close()
h = bf.HeadFile(modelname+'.hds', text='head')
head_noPump_10lay = h.get_data(totim=1)
h.close()

# pump
wel_spd = {0: [[0, 0, round(ncol/2), Qw]]}
wel = flopy.modflow.ModflowWel(mf, stress_period_data=wel_spd)

# write input, run
mf.write_input()
success, mfoutput = mf.run_model()
if not success:
    raise Exception('MODFLOW did not terminate normally.')

# output
rivout = bf.CellBudgetFile(modelname+'.riv.out', verbose=False)
rivout_3D = rivout.get_data(totim=1, text='RIVER LEAKAGE')
leakage_L_pump_10lay = rivout_3D[0][0][1]
leakage_R_pump_10lay = rivout_3D[0][1][1]
rivout.close()
h = bf.HeadFile(modelname+'.hds', text='head')
head_pump_10lay = h.get_data(totim=1)
h.close()

# calculate WTEs
wte_noPump = pp.get_water_table(head_noPump, nodata=-9999)
wte_noPump_10lay = pp.get_water_table(head_noPump_10lay, nodata=-9999)
wte_pump = pp.get_water_table(head_pump, nodata=-9999)
wte_pump_10lay = pp.get_water_table(head_pump_10lay, nodata=-9999)

## plots
# water table
plt.plot(xcoord, wte_noPump, 'b')
plt.plot(xcoord, wte_pump, 'r')
plt.plot(xcoord, wte_noPump_10lay, 'b--')
plt.plot(xcoord, wte_pump_10lay, 'r--')
plt.xlabel('position [m]')
plt.ylabel('water table elevation [m]')
#plt.axis([0, 1010, 88, 100])
plt.title('blue=no pumping, red=pumping;\nsolid=1 layer, dashed=5 layer\nLeft/Right Capture Fraction='+str(round((leakage_L_noPump-leakage_L_pump)/Qw, 3))+'/'+str(round((leakage_R_noPump-leakage_R_pump)/Qw, 3)))
plt.savefig('wte_'+runid+'.png')

# drawdown
ddn = wte_noPump - wte_pump
ddn_10lay = wte_noPump_10lay - wte_pump_10lay
plt.plot(xcoord, ddn, 'r')
plt.plot(xcoord, ddn_10lay, 'r--')
plt.xlabel('position [m]')
plt.ylabel('drawdown [m]')
#plt.axis([0, 1010, 0, 6])
plt.title('solid=1 layer, dashed=5 layer')
plt.gca().invert_yaxis()
plt.savefig('ddn_'+runid+'.png')

# depletion
print(round((leakage_L_noPump-leakage_L_pump)/Qw, 3),
      round((leakage_R_noPump-leakage_R_pump)/Qw, 3))

print(round((leakage_L_noPump_10lay-leakage_L_pump_10lay)/Qw, 3),
      round((leakage_R_noPump_10lay-leakage_R_pump_10lay)/Qw, 3))