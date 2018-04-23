## MNW2-SimpleExample.py
# This is the simple example described in the FloPy notebook:
# https://github.com/modflowpy/flopy/blob/develop/examples/Notebooks/flopy3_mnw2package_example.ipynb

import pandas as pd
import flopy

# set up basic model
m = flopy.modflow.Modflow('mnw2example', model_ws='.')
dis = flopy.modflow.ModflowDis(nrow=5, ncol=5, nlay=3, nper=3, top=10, botm=0, model=m)

## build MNW2 package
# node data: example from iPython notebook
node_data = pd.DataFrame(
    [[1, 1, 9.5, 7.1, 'well1', 'skin', -1, 0, 0, 0, 1., 2., 5., 6.2],
     [1, 1, 7.1, 5.1, 'well1', 'skin', -1, 0, 0, 0, 1., 2., 5., 6.2],
     [3, 3, 9.1, 3.7, 'well2', 'skin', -1, 0, 0, 0, 1., 2., 5., 4.1]],
    columns=['i', 'j', 'ztop', 'zbotm', 'wellid', 'losstype', 'pumploc', 
    'qlimit', 'ppflag', 'pumpcap', 'rw', 'rskin', 'kskin', 'zpump'])
node_data = node_data.to_records()

# stress period information
stress_period_data = pd.DataFrame(
                         [[0, 'well1', 0],
                          [1, 'well1', 100.0],
                          [0, 'well2', 0],
                          [1, 'well2', 1000.]], 
        columns=['per', 'wellid', 'qdes'])
pers = stress_period_data.groupby('per')
stress_period_data = {i: pers.get_group(i).to_records() for i in [0, 1]}

# make package object
mnw2 = flopy.modflow.ModflowMnw2(model=m, mnwmax=2,
                 node_data=node_data, 
                 stress_period_data=stress_period_data, 
                 itmp=[2, 2, -1], # reuse second per pumping for last stress period
                 )

# inspect package
mnw2.nodtot
pd.DataFrame(mnw2.node_data)

## now, we should be able to define 'well1' based only on ztop and zbotm
node_data = pd.DataFrame(
    [[1, 1, 9.5, 5.1, 'well1', 'skin', -1, 0, 0, 0, 1., 2., 5., 6.2],
     [3, 3, 9.1, 3.7, 'well2', 'skin', -1, 0, 0, 0, 1., 2., 5., 4.1]],
    columns=['i', 'j', 'ztop', 'zbotm', 'wellid', 'losstype', 'pumploc', 
    'qlimit', 'ppflag', 'pumpcap', 'rw', 'rskin', 'kskin', 'zpump'])
node_data = node_data.to_records()

mnw2 = flopy.modflow.ModflowMnw2(model=m, mnwmax=2,
                 node_data=node_data, 
                 stress_period_data=stress_period_data, 
                 itmp=[2, 2, -1], # reuse second per pumping for last stress period
                 )

# inspect package
mnw2.nodtot
pd.DataFrame(mnw2.node_data)

## what if we try manually defining the layer number for each node
# this seems to work!
node_data = pd.DataFrame(
    [[1, 1, 1, 9.5, 5.1, 'well1', 'skin', -1, 0, 0, 0, 1., 2., 5., 6.2],
     [2, 1, 1, 4.9, 3.7, 'well1', 'skin', -1, 0, 0, 0, 1., 2., 5., 6.2],
     [1, 3, 3, 9.1, 7.5, 'well2', 'skin', -1, 0, 0, 0, 1., 2., 5., 4.1]],
    columns=['k','i', 'j', 'ztop', 'zbotm', 'wellid', 'losstype', 'pumploc', 
    'qlimit', 'ppflag', 'pumpcap', 'rw', 'rskin', 'kskin', 'zpump'])
node_data = node_data.to_records()

mnw2 = flopy.modflow.ModflowMnw2(model=m, mnwmax=2,
                 node_data=node_data, 
                 stress_period_data=stress_period_data, 
                 itmp=[2, 2, -1], # reuse second per pumping for last stress period
                 )

# inspect package
mnw2.nodtot
pd.DataFrame(mnw2.node_data)

m.write_input()