## text and code copied from Bakker et al. (2016), except where noted by #SCZ

#1. Import the MODFLOW and utilities subpackages of
#FloPy and give them the aliases fpm and fpu,
#respectively

import numpy as np
import flopy.modflow as fpm
import flopy.utils as fpu

#2. Create a MODFLOW model object. Here, the MODFLOW
#model object is stored in a Python variable
#called model, but this can be an arbitrary name.
#This object name is important as it will be used as
#a reference to the model in the remainder of the
#FloPy script. In addition, a modelname is specified
#when the MODFLOW model object is created. This
#modelname is used for all the files that are created
#by FloPy for this model.

path_to_mf2005 = 'C:/Users/Sam/Dropbox/Work/Models/MODFLOW/MF2005.1_12/bin/mf2005.exe'  #SCZ
model = fpm.Modflow(modelname = 'gwexample', exe_name=path_to_mf2005)  #SCZ
#model = fpm.Modflow(modelname = 'gwexample')

#3. The discretization of the model is specified with the
#discretization file (DIS) of MODFLOW. The aquifer
#is divided into 201 cells of length 10m and width 1 m.
#The first input of the discretization package is the name
#of the model object. All other input arguments are self
#explanatory.

fpm.ModflowDis(model, nlay=1, nrow=1, ncol=201, delr=10, delc=1, top=50, botm=0)

#Active cells and the like are defined with the Basic
#package (BAS), which is required for every MODFLOW
#model. It contains the ibound array, which
#is used to specify which cells are active (value is
#positive), inactive (value is 0), or fixed head (value
#is negative). The numpy package (aliased as np) can
#be used to quickly initialize the ibound array with
#values of 1, and then set the ibound value for the
#first and last columns to -1. The numpy package
#(and Python, in general) uses zero-based indexing and
#supports negative indexing so that row 1 and column
#1, and row 1 and column 201, can be referenced as [0,
#0], and [0, -1], respectively. Although this simulation
#is for steady flow, starting heads still need to be
#specified. They are used as the head for fixed-head
#cells (where ibound is negative), and as a starting
#point to compute the saturated thickness for cases of
#unconfined flow.

ibound = np.ones((1, 201))
ibound[0, 0] = ibound[0, -1] = -1
fpm.ModflowBas(model, ibound=ibound, strt=20)

#The hydraulic properties of the aquifer are specified
#with the layer properties flow (LPF) package (alternatively,
#the block centered flow (BCF) package may be
#used). Only the hydraulic conductivity of the aquifer
#and the layer type (laytyp) need to be specified. The
#latter is set to 1, which means that MODFLOW will
#calculate the saturated thickness differently depending
#on whether or not the head is above the top of the
#aquifer.

fpm.ModflowLpf(model, hk=10, laytyp=1)

#4. Aquifer recharge is simulated with the Recharge
#package (RCH) and the extraction of water at the two
#ditches is simulated with the Well package (WEL); the
#length of each ditch normal to the plane of flow is equal
#to 1m (delc = 1). The latter requires specification
#of the layer, row, column, and injection rate of the
#well for each stress period. The layers, rows, columns,
#and the stress period are numbered (consistent with
#Python's zero-based numbering convention) starting at
#0. The required data are stored in a Python dictionary
#(lrcQ in the code below), which is used in FloPy to
#store data that can vary by stress period. The lrcQ
#dictionary specifies that two wells (one in cell 1, 1,
#51 and one in cell 1, 1, 151), each with a rate of
#-1 m3/d, will be active for the first stress period.
#Because this is a steady-state model, there is only
#one stress period and therefore only one entry in the
#dictionary.

fpm.ModflowRch(model, rech=0.001)
lrcQ = { 0: [[0, 0, 50, -1], [0, 0, 150, -1]]}
fpm.ModflowWel(model, stress_period_data=lrcQ)

#5. The preconditioned conjugate-gradient (PCG) solver,
#using the default settings, is specified to solve the
#model.

fpm.ModflowPcg(model)

#6. The frequency and type of output that MODFLOW
#writes to an output file is specified with the output
#control (OC) package. In this case, the budget is printed
#and heads are saved (the default), so no arguments are
#needed.

fpm.ModflowOc(model)

#7. Finally the MODFLOW input files are written (eight
#files for this model) and the model is run. This
#requires, of course, that MODFLOW is installed on
#your computer and FloPy can find the executable in
#your path.

model.write_input()
model.run_model()

#8. After MODFLOW has responded with the positive
#Normal termination of simulation, the calculated
#heads can be read from the binary output file.
#First, a file object is created. As the modelname used
#for all MODFLOW files was specified as gwexample
#in step 1, the file with the heads is called gwexample.
#hds. FloPy includes functions to read data
#from the file object, including heads for specified layers
#or time steps, or head time series at individual cells.
#For this simple mode, all computed heads are read.

hfile = fpu.HeadFile('gwexample.hds')
h = hfile.get_data(totim=1.0)

#The heads are now stored in the Python variable h.
#FloPy includes powerful plotting functions to plot the
#grid, boundary conditions, head, etc. This functionality
#is demonstrated later. For this simple one-dimensional
#example, a plot is created with the matplotlib package,
#resulting in the plot shown in Figure 1.

#SCZ below here; make plot equivalent to Figure 1 in Bakker et al. (2016)
import matplotlib.pyplot as plt
position = np.linspace(0,2000,np.size(h))
h_plot = h[0,0,:]

plt.plot(position,h_plot, color="black")
plt.xlabel("x (m)")
plt.ylabel("head (m)")
plt.show()
