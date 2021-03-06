import genealogy_lib.genealogy as G
import genealogy_lib.graphviz as GV
import genealogy_lib.genealogy_analyzer as GA

experimentname = "exp_csev"

values = [
    0.10, 0.01,
    0.01, 1.00
]

init_distribution = [
    0.98, 0.01, 0.01, 0.00
]

def CF(cs):
    cs = [ 1 if c else 0 for c in cs ]
    return values[ cs[1]*2 + cs[0] ]

def F(agent, ref_gen_ind, A):
    return agent.absolute_fitness * (ref_gen_ind - agent.gen_ind) ** A

gen_params = {
    "name" : experimentname,
    
    "M"  : lambda m, i: 100,

    "A"  : 0,
    "C"  : 0,
    "G"  : 1,
    
    "T"  : 2,
    "CF" : CF,
    "F"  : F,

    "init_distribution": init_distribution,
    "replacement" : True
}

analyzer_params = {}

meta = {
    "X-name": "Parent Number", "X-range": [i for i in range(1,50,2)],
    "Y-name": "Evolution Rate",
    "Z-names": [ "CS#" + str(i) for i in range(2**gen_params["T"])],
    "Z-size": 2**gen_params["T"],
    "iterations": 50,
}

analyzer = GA.GenealogyAnalyzer(analyzer_params, gen_params)
analyzer.initResult(experimentname, meta)
analyzer.analyzeCSEV(experimentname)

result = analyzer.getResult(experimentname)
result.setFigParameter("title","Evolution Rate respective to each Character Set")
result.setFigParameter("legend",True)
result.figPlot()
result.figShow()
result.figSave(
    "outputs/" + experimentname +
    "_m"    + str(gen_params["M"](0)) +
    "_repl" + str(gen_params["replacement"]) +
    "_i"    + str(meta["iterations"]) +
    ".png")
