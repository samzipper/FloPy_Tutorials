## SquareWithWell-SteadyState.py
# This script creates a square domain with the dimension
# 1000 m x 1000 m, with a well in the center (500,500).
# The top (y=1000) and bottom (y=0) sides of the domain 
# are no-flow boundaries, and the left (x=0) and right (x=1000)
# sides are constant head boundaries at 100 m. The well 
# pumps are a rate of 1000 m3/day.
#
# Using default units of ITMUNI=4 (days) and LENUNI=2 (meters)

import numpy as np
import flopy 
import platform

# what version of modflow to use?
modflow_v = 'mf2005'  # 'mfnwt' or 'mf2005'

# where is your MODFLOW executable?
if (modflow_v=='mf2005'):
    if platform.system() == 'Windows':
        path2mf = 'C:/Users/Sam/Dropbox/Work/Models/MODFLOW/MF2005.1_12/bin/mf2005.exe'
    else: 
        path2mf = modflow_v
elif (modflow_v=='mfnwt'):
    if platform.system() == 'Windows':
        path2mf = 'C:/Users/Sam/Dropbox/Work/Models/MODFLOW/MODFLOW-NWT_1.1.3/bin/MODFLOW-NWT.exe'
    else:
        path2mf = modflow_v

# Assign name and create modflow model object
modelname = 'SquareWithWell-SteadyState'
mf = flopy.modflow.Modflow(modelname, exe_name=path2mf, version='mfnwt')

# Model domain and grid definition
Lx = 1000.
Ly = 1000.
ztop = 100.
zbot = 0.
nlay = 1
nrow = 50
ncol = 100
delr = Lx / ncol
delc = Ly / nrow
delv = (ztop - zbot) / nlay
x_coord = np.linspace(delr/2, Lx-delr/2, num=ncol)
y_coord = np.linspace(Ly-delc/2, delc/2, num=nrow)
botm = np.linspace(ztop, zbot, nlay + 1)
hk = 1.
vka = 1.
sy = 0.1
ss = 1.e-4
laytyp = 1

# define boundary conditions: 1 everywhere except 
# left and right edges, which are -1
ibound = np.ones((nlay, nrow, ncol), dtype=np.int32)
ibound[:,:,(0,ncol-1)] = -1.0

# initial conditions
strt = 100. * np.ones((nlay, nrow, ncol), dtype=np.float32)

# Time step parameters
nper = 1
perlen = [1]
nstp = [1]
steady = [True]

# Flopy objects
dis = flopy.modflow.ModflowDis(mf, nlay, nrow, ncol, delr=delr, delc=delc,
                               top=ztop, botm=botm[1:],
                               nper=nper, perlen=perlen, nstp=nstp, steady=steady)
bas = flopy.modflow.ModflowBas(mf, ibound=ibound, strt=strt)
lpf = flopy.modflow.ModflowLpf(mf, hk=hk, vka=vka, sy=sy, ss=ss, laytyp=laytyp)

if (modflow_v=='mf2005'):
    pcg = flopy.modflow.ModflowPcg(mf)
elif (modflow_v=='mfnwt'):
    nwt = flopy.modflow.ModflowNwt(mf)

# set up pumping well
r_well = round(nrow/2)
c_well = round(ncol/2)
pumping_rate = -1000.
wel_sp1 = [[0, r_well, c_well, pumping_rate]]
stress_period_data = {0: wel_sp1}
wel = flopy.modflow.ModflowWel(mf, stress_period_data=stress_period_data)

# Output control
spd = {(0, 0): ['save head','save drawdown']}
oc = flopy.modflow.ModflowOc(mf, stress_period_data=spd,
                             compact=True)

# Write the model input files
mf.write_input()

# Run the model
success, mfoutput = mf.run_model(silent=False, pause=False, report=True)
if not success:
    raise Exception('MODFLOW did not terminate normally.')

# Imports
import matplotlib.pyplot as plt
import flopy.utils.binaryfile as bf

# Create the headfile object
headobj = bf.HeadFile(modelname+'.hds', text='head')
ddnobj = bf.HeadFile(modelname+'.ddn', text='drawdown')

# get data
time = headobj.get_times()[0]
head = headobj.get_data(totim=time)
ddn = ddnobj.get_data(totim=time)
extent = (x_coord[0],x_coord[ncol-1],y_coord[0],y_coord[nrow-1])

# Well point
wpt = (float(round(ncol/2)+0.5)*delr, float(round(nrow/2)+0.5)*delc)

# plot of head
plt.subplot(2,2,1)
plt.imshow(head[0,:,:], extent=extent, cmap='BrBG')
plt.colorbar()
plt.plot(wpt[0], wpt[1], lw=0, marker='o', markersize=8,
             markeredgewidth=0.5,
             markeredgecolor='black', 
             markerfacecolor='none', 
             zorder=9)

# plot of drawdown
plt.subplot(2,2,3)
plt.imshow(ddn[0,:,:], extent=extent, cmap='BrBG')
plt.colorbar()
plt.plot(wpt[0], wpt[1], lw=0, marker='o', markersize=8,
             markeredgewidth=0.5,
             markeredgecolor='black', 
             markerfacecolor='none', 
             zorder=9)

# cross-section (L-R) of head through the well
plt.subplot(2,2,2)
plt.plot(x_coord, head[0,r_well,:])
plt.subplot(2,2,4)
plt.plot(x_coord, ddn[0,r_well,:])
plt.show()

# cross-section (B-T) of head through the well
plt.plot(head[0,:,c_well], y_coord)
plt.plot(ddn[0,:,c_well], y_coord)