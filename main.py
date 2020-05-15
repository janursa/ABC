import sys
sys.path.insert(1,"/Users/matin/Downloads/testProjs/ABC/ABC/src/")
from ABC import ABC

sys.path.insert(1,"/Users/matin/Downloads/testProjs/CA")
from model import Model

import json
SCHEMES_PATH = "schemes.json"
with open(SCHEMES_PATH) as schemes_file:
    schemes = json.load(schemes_file)["schemes"]


def run(paramset,args):

	model = args["model"]
	schemes = args["schemes"]
	replica_n = args["replica_n"]
	import copy
	import numpy as np
	def distance_function(realizations,expectations):
	    import numpy as np
	    distances = []
	    for i in range(len(realizations)):
	        raw_sim_data = realizations[i]
	        sim_data = {}
	        sim_liveCellCount = np.array(raw_sim_data["agents_count"]["MSC"])
	        sim_totalCellCount = np.array(raw_sim_data["agents_count"]["MSC"]) + np.array(raw_sim_data["agents_count"]["Dead"])
	        sim_viability = sim_liveCellCount[-1]/sim_totalCellCount[-1] 
	        sim_data.update({"liveCellCount":sim_liveCellCount,
	                         "viability": sim_viability})
	                
	        exp_data = expectations[i]

	        error_liveCellCount = (sim_data["liveCellCount"] - np.array(exp_data["liveCellCount"]))/np.array(exp_data["liveCellCount"])
	        error_viability = (sim_data["viability"] - np.array(exp_data["viability"]))/np.array(exp_data["viability"])

	        all_errors = np.concatenate((error_liveCellCount,error_viability),axis=0)
	        abs_all_errors = np.abs(all_errors)

	        distances.append(np.mean(abs_all_errors)) 
	    
	    distance = np.mean(distances)
	    return distance

	schemes_copy = copy.deepcopy(schemes)
	expectations = [scheme["expectations"] for scheme in schemes]

	rep_distances = []
	for rep_i in range(replica_n):
	    try:
	        sim_results_list = model(paramset).run(schemes_copy)
	    except ValueError:
	        # None value if the param set leads to invalid definition
	        distances = np.append(distances,None) 
	        break
	    distance = distance_function(sim_results_list,expectations)
	    rep_distances.append(distance)
	error = np.mean(rep_distances)
	return error

settings = {
	"MPI_flag": True,
	"sample_n": 10,
	"top_n": 2,
	"output_path": "outputs",
	"run_func":run,
	"args":{
		"model":Model,
		"schemes":schemes,
		"replica_n":2
	}

}

free_params = {
#     "AE_H_t": [0,1],
#     "AE_L_t": [0,1],
#     "B_MSC_rec": [0.001,0.005],
    "B_MSC_Pr": [0.01,0.05],
#     "B_MSC_Mo": [0.0015,0.01],
    "CD_H_t": [0.5,1],
    "CD_L_t": [0,0.5]
#     "CD_M_t1": 0.3,
#     "CD_M_t2": 0.6,
#     "MG_H_t": [15,40],
#     "MG_L_t1": [0,10],
#     "MG_L_t2": [3,15],
#     "Mo_H_v": [2,5],
#     "Pr_N_v": [0,1],
#     "w_lactate_ph": [0.1,0.5],
#     "w_mg_ph": [0.02,0.1],
#     "w_MI_lactate": [0.05,0.1]
}
if __name__ == "__main__":
	obj = ABC(settings=settings,free_params=free_params)
	obj.sample()
	obj.run()