## TiltedVwithSFR-SteadyState.py
# This script creates a square domain with the dimension
# 1000 m x 1000 m which is a tilted V ('open book') aquifer
# drained by a stream down the middle.
#
# Using default units of ITMUNI=4 (days) and LENUNI=2 (meters)

import numpy as np
import flopy 

# where is your MODFLOW-2005 executable?
path2mf = 'C:/Users/Sam/Dropbox/Work/Models/MODFLOW/MF2005.1_12/bin/mf2005.exe'

# Assign name and create modflow model object
modelname = 'TiltedVwithSFR-SteadyState'
mf = flopy.modflow.Modflow(modelname, exe_name=path2mf)

# Model domain and grid definition
Lx = 1000.
Ly = 1000.
nlay = 1
nrow = 20
ncol = 21
delr = Lx / ncol
delc = Ly / nrow

# top and initial conditions
ztop = np.zeros((nrow,ncol), dtype='float')
ztop[0,:] = np.concatenate([np.arange(25,19.9,-0.5), np.arange(20.5,25.1,0.5)])

strt = np.zeros((nrow,ncol), dtype='float')
strt[0,:] = min(ztop[0,:]) + (max(ztop[0,:]) - min(ztop[0,:]))/2
for x in range(1, nrow):
    ztop[x,:] = ztop[x-1,:]-0.5
    strt[x,:] = min(ztop[x,:]) + (max(ztop[x,:]) - min(ztop[x,:]))/2

zbot = 0.0
delv = (ztop - zbot) / nlay
hk = 1.
vka = 1.
sy = 0.1
ss = 1.e-4
laytyp = 1

# define boundary conditions: 1 everywhere except 
# left and right edges, which are -1 (constant head)
ibound = np.ones((nlay, nrow, ncol), dtype=np.int32)
ibound[:,:,(0,ncol-1)] = -1.0

# Time step parameters
nper = 1
perlen = [1]
nstp = [1]
steady = [True]

# Flopy objects
dis = flopy.modflow.ModflowDis(mf, nlay, nrow, ncol, delr=delr, delc=delc,
                               top=ztop, botm=zbot,
                               nper=nper, perlen=perlen, nstp=nstp, steady=steady)
bas = flopy.modflow.ModflowBas(mf, ibound=ibound, strt=strt)
lpf = flopy.modflow.ModflowLpf(mf, hk=hk, vka=vka, sy=sy, ss=ss, laytyp=laytyp)
pcg = flopy.modflow.ModflowPcg(mf)
oc = flopy.modflow.ModflowOc(mf, save_every=True, compact=True)

## make stream network
# set up stream reach data (Dataset 2)
#  (KRCH, IRCH, JRCH, ISEG, IREACH)
slope=(ztop[0,10]-ztop[1,10])/delc
reach_data = np.array(
              [(0, 0, 10, 1, 1, delc, ztop[0,10]-1, slope, 1.0, hk/10),
               (0, 1, 10, 1, 2, delc, ztop[1,10]-1, slope, 1.0, hk/10),
               (0, 2, 10, 1, 3, delc, ztop[2,10]-1, slope, 1.0, hk/10),
               (0, 3, 10, 1, 4, delc, ztop[3,10]-1, slope, 1.0, hk/10),
               (0, 4, 10, 1, 5, delc, ztop[4,10]-1, slope, 1.0, hk/10),
               (0, 5, 10, 1, 6, delc, ztop[5,10]-1, slope, 1.0, hk/10),
               (0, 6, 10, 1, 7, delc, ztop[6,10]-1, slope, 1.0, hk/10),
               (0, 7, 10, 1, 8, delc, ztop[7,10]-1, slope, 1.0, hk/10),
               (0, 8, 10, 1, 9, delc, ztop[8,10]-1, slope, 1.0, hk/10),
               (0, 9, 10, 1, 10, delc, ztop[9,10]-1, slope, 1.0, hk/10),
               (0, 10, 10, 1, 11, delc, ztop[10,10]-1, slope, 1.0, hk/10),
               (0, 11, 10, 1, 12, delc, ztop[11,10]-1, slope, 1.0, hk/10),
               (0, 12, 10, 1, 13, delc, ztop[12,10]-1, slope, 1.0, hk/10),
               (0, 13, 10, 1, 14, delc, ztop[13,10]-1, slope, 1.0, hk/10),
               (0, 14, 10, 1, 15, delc, ztop[14,10]-1, slope, 1.0, hk/10),
               (0, 15, 10, 1, 16, delc, ztop[15,10]-1, slope, 1.0, hk/10),
               (0, 16, 10, 1, 17, delc, ztop[16,10]-1, slope, 1.0, hk/10),
               (0, 17, 10, 1, 18, delc, ztop[17,10]-1, slope, 1.0, hk/10),
               (0, 18, 10, 1, 19, delc, ztop[18,10]-1, slope, 1.0, hk/10),
               (0, 19, 10, 1, 20, delc, ztop[19,10]-1, slope, 1.0, hk/10)], 
      dtype=[('k', '<f8'), ('i', '<f8'), ('j', '<f8'), ('iseg', '<f8'), ('ireach', '<f8'), ('rchlen', '<f8'),
             ('strtop', '<f8'), ('slope', '<f8'), ('strthick', '<f8'), ('strhc1', '<f8')])

# segment data (Dataset 6a-c)
#   (NSEG, ICALC, OUTSEG, IUPSEG, FLOW, RUNOFF, ETSW, PPTSW, ROUGHCH)
segment_data = {0: np.array([(1, 1, 0, 0, 
                              0, 0, 0, 0, 0.03, 
                              3, 3)],
                             dtype=[('nseg', '<f8'), ('icalc', '<f8'), ('outseg', '<f8'), ('iupseg', '<f8'), 
                                    ('flow', '<f8'), ('runoff', '<f8'), ('etsw', '<f8'), ('pptsw', '<f8'), ('roughch', '<f8'),
                                    ('width1', '<f8'), ('width2', '<f8')])}

# constants (dataset 1c)
nstrm = -len(reach_data) # number of reaches
nss = 1 # number of segments
nsfrpar = 0 # number of parameters (not supported)
nparseg = 0
const = 86400    # constant for manning's equation, units of m3/d
dleak = 0.0001 # closure tolerance for stream stage computation
ipakcb = 53 # ISTCB1= flag for writing SFR output to cell-by-cell budget (on unit 53)
istcb2 = 81 # flag for writing SFR output to text file
isfropt = 1  # no vertical unsat flow beneath streams
irtflg = 0

# dataset 5
dataset_5 = {0: [nss, 0, 0]} # [itmp, irdflag, iptflag]

sfr = flopy.modflow.ModflowSfr2(mf, nstrm=nstrm, nss=nss, const=const, dleak=dleak, ipakcb=ipakcb, istcb2=istcb2, 
                                reach_data=reach_data,
                                segment_data=segment_data,
                                isfropt=isfropt,
                                irtflg=irtflg,
                                dataset_5=dataset_5,
                                unit_number=16)

# write input datasets
mf.write_input()

# run model
success, mfoutput = mf.run_model()
if not success:
    raise Exception('MODFLOW did not terminate normally.')

## look at output
# Imports
import matplotlib.pyplot as plt
import flopy.utils.binaryfile as bf

# land surface
plt.imshow(ztop, cmap='BrBG')
plt.colorbar()

# Create the headfile object
h = bf.HeadFile(modelname+'.hds', text='head')

# get data
time = h.times
h.plot(totim=time[0], contour=True, grid=True, colorbar=True)

# sfr output
sfr.plot(key='iseg')