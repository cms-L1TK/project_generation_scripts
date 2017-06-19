# dictionaries that stores lists of possible projections for a given seeding

proj_dict = {'L1L2':['L3','L4','L5','L6','D1','D2','D3','D4'],
             'L3L4':['L1','L2','L5','L6','D1','D2'],
             'L5L6':['L1','L2','L3','L4'],
             'D1D2':['L1','L2','D3','D4','D5'],
             'D3D4':['L1','D1','D2','D5'],
             'D1L1':['D2','D3','D4','D5'],
             'D1L2':['L1','D1','D2','D3','D4']}

# barrel only
proj_dict_L = {'L1L2':['L3','L4','L5','L6'],
               'L3L4':['L1','L2','L5','L6'],
               'L5L6':['L1','L2','L3','L4']}

# disk only
proj_dict_D = {'D1D2':['D3','D4','D5'],
               'D3D4':['D1','D2','D5']}

# hybrid
# TODO
proj_dict_H = {'D1L1':['D2','D3','D4','D5'],
               'D1L2':['L1','D1','D2','D3','D4'],
               # ?
               'L1L2':['L3','L4','L5','L6','D1','D2','D3','D4'],
               'L3L4':['L1','L2','L5','L6','D1','D2'],
               'D1D2':['L1','L2','D3','D4','D5'],
               'D3D4':['L1','D1','D2','D5']}
