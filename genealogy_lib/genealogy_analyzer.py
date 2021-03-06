import matplotlib
matplotlib.use('Agg')
import genealogy_lib.data_utils
import genealogy_lib.genealogy as G
import genealogy_lib.graphviz as GV

from genealogy_lib.genealogy_defaults import default_genealogy_parameters
from genealogy_lib.genealogy_analyzer_figure_defaults import default_fig_parameters
from genealogy_lib.genealogy_analyzer_defaults import default_genealogy_analyzer_parameters

import matplotlib.pyplot as plt
import copy
import math
import numpy as np
from tqdm import tqdm

############################################################
### GENEALOGY ANALYZER
##
#   - Runs analyses, given parameters, and stores
#     results in a Results object.
############################################################


class GenealogyAnalyzer:

    def __init__(self, params, gen_params):
        self.parameters = params
        self.gen_params = gen_params
        self.results = {}

    def setParameters(self, params):
        for k,v in params.items():
            self.parameters[k] = v

    def setParameter(self, k, v):
        self.parameters[k] = v

    def initResult(self, resultname, meta):
        self.results[resultname] = Result(resultname, meta)

    def getResult(self, resultname):
        return self.results[resultname]

    def analyzeAbsoluteCSDistributions(self, resultname):
        result = self.getResult(resultname)
        iterations = result.meta["iterations"]
        raw = [ # [char_ind][gen_ind] -> array with entry for each iteration
            [ [] for _ in range(self.gen_params["N"]) ]
                for _ in range(2**self.gen_params["T"]) ]
        avg = [] # [char_ind][gen_ind] -> average
        # std = [] # [char_ind][gen_ind] -> standard deviation

        print("running iterations...")
        for i in tqdm(range(iterations)):
            g = G.Genealogy(self.gen_params)
            g.generate()
            d = g.getDistribution()
            for cs_ind in range(len(d)):
                d_cs = d[cs_ind]
                for gen_ind in range(len(d_cs)):
                    raw_cs_gen = raw[cs_ind][gen_ind]
                    if gen_ind == 0: raw_cs_gen.append(d_cs[gen_ind])
                    else:            raw_cs_gen.append(d_cs[gen_ind] + d_cs[gen_ind-1])

        for cs_ind in range(len(raw)):
            avg.append([])
            # std.append([])
            for gen_ind in range(len(raw[cs_ind])):
                avg[cs_ind].append(None)
                avg[cs_ind][gen_ind] = np.mean(raw[cs_ind][gen_ind])
                # std[cs_ind].append(None)
                # std[cs_ind][gen_ind] = np.std(raw[cs_ind][gen_ind])

        xs = [i for i in range(len(avg[0]))]
        for zi in range(len(avg)):
            result.addData(zi,xs,avg[zi])

    def analyzeRelativeCSDistributions(self, resultname):
        result = self.getResult(resultname)
        iterations = result.meta["iterations"]
        raw = [ # [char_ind][gen_ind] -> array with entry for each iteration
            [ [] for _ in range(self.gen_params["N"]) ]
                for _ in range(2**self.gen_params["T"]) ]
        avg = [] # [char_ind][gen_ind] -> average
        # std = [] # [char_ind][gen_ind] -> standard deviation

        # get generation sizes
        first = True
        generation_sizes = None

        print("running iterations...")
        for i in tqdm(range(iterations)):
            g = G.Genealogy(self.gen_params)
            g.generate()

            if first:
                generation_sizes = g.generation_sizes
                first = False

            d = g.getDistribution()
            for cs_ind in range(len(d)):
                d_cs = d[cs_ind]
                for gen_ind in range(len(d_cs)):
                    raw_cs_gen = raw[cs_ind][gen_ind]
                    raw_cs_gen.append(d_cs[gen_ind])
                    # if gen_ind == 0: raw_cs_gen.append(d_cs[gen_ind])
                    # else:            raw_cs_gen.append(d_cs[gen_ind] + d_cs[gen_ind-1])

        for cs_ind in range(len(raw)):
            avg.append([])
            # std.append([])
            for gen_ind in range(len(raw[cs_ind])):
                avg[cs_ind].append(
                    np.mean(raw[cs_ind][gen_ind])
                    /generation_sizes[gen_ind])
                    # /sum([generation_sizes[gi] for gi in range(gen_ind+1)]))

                # std[cs_ind].append(None)
                # std[cs_ind][gen_ind] = np.std(raw[cs_ind][gen_ind])

        xs = [i for i in range(len(avg[0]))]
        for zi in range(len(avg)):
            result.addData(zi,xs,avg[zi])

    # analyze character set evolution rate
    def analyzeCSEV(self, resultname):
        # record change in the percent of the population
        # for each possible character set
        # betweeen first and second generations
        self.gen_params["N"] = 2
        # initializations
        result = self.getResult(resultname)
        iterations = result.meta["iterations"]
        cs_count = result.meta["Z-size"]
        xs = result.meta["X-range"]
        csers_history = [ [] for _ in range(cs_count) ]

        print("running iterations...")
        for parent_number in tqdm(xs):
            raw = [ # [char_ind][gen_ind] -> array with entry for each iteration
                [ [] for _ in range(self.gen_params["N"]) ]
                    for _ in range(2**self.gen_params["T"]) ]
            avg = [] # [char_ind][gen_ind] -> average

            # get generation sizes
            first = True
            generation_sizes = None

            # set parent number
            self.gen_params["P"] = lambda i: parent_number

            for i in range(iterations):
                g = G.Genealogy(self.gen_params)
                g.generate()

                if first:
                    generation_sizes = g.generation_sizes
                    first = False

                d = g.getDistribution()
                for cs_ind in range(len(d)):
                    d_cs = d[cs_ind]
                    for gen_ind in range(len(d_cs)):
                        raw_cs_gen = raw[cs_ind][gen_ind]
                        raw_cs_gen.append(d_cs[gen_ind])

            for cs_ind in range(len(raw)):
                avg.append([])
                for gen_ind in range(len(raw[cs_ind])):
                    avg[cs_ind].append(
                        np.mean(raw[cs_ind][gen_ind])
                        /generation_sizes[gen_ind])

            for zi in range(len(avg)):
                rate = avg[zi][1] - avg[zi][0] # first minus zeroth
                csers_history[zi].append(rate)

        for zi in range(cs_count):
            result.addData(zi,xs,csers_history[zi])

    def analyzeTargetCSEV(self, resultname):
        # record change in the percent of the population
        # that has a specified character set
        # betweeen first and second generations
        self.gen_params["N"] = 2
        # initializations
        result = self.getResult(resultname)
        iterations = result.meta["iterations"]
        xs = result.meta["X-range"]
        targetcs_ind = result.meta["I-value"]
        history = []

        print("running iterations...")
        for parent_number in tqdm(xs):

            raw = [ # [gen_ind] -> array with entry for each iteration
                [] for _ in range(self.gen_params["N"]) ]
            avg = [] # [gen_ind] -> average

            # get generation sizes
            first = True
            generation_sizes = None

            # set parent number
            self.gen_params["P"] = lambda i: parent_number

            for i in range(iterations):
                g = G.Genealogy(self.gen_params)
                g.generate()

                if first:
                    generation_sizes = g.generation_sizes
                    first = False

                d = g.getDistribution()[targetcs_ind]
                for gen_ind in range(len(d)):
                    raw[gen_ind].append(d[gen_ind])

            for gen_ind in range(len(raw)):
                avg.append(
                    np.mean(raw[gen_ind])
                    /generation_sizes[gen_ind])

            rate = avg[1] - avg[0] # first minus zeroth
            history.append(rate)

        # add data
        result.addData(0,xs,history)

############################################################
### RESULT
##
#   - Stores data collected from an analysis,
#     including experiment and graphing parameters.
############################################################
        

class Result:

    def __init__(self, name, meta):
        self.name = name
        self.meta = meta
        self.data = np.empty([meta["Z-size"], 2],object)
        self.fig_parameters = default_fig_parameters

    # data organized as
    # - data[zi][0] = xs
    # - data[zi][1] = ys
    def addData(self, zi, xs, ys):
        self.data[zi][0] = xs
        self.data[zi][1] = ys

    def getDataXs(self, zi): return self.data[zi][0]
    def getDataYs(self, zi): return self.data[zi][1]

    def setFigParameters(self, params):
        for k,v in params.items():
            self.fig_parameters[k] = v

    def setFigParameter(self,k,v):
        self.fig_parameters[k] = v

    def getColor(self, zi):
        if "colors" in self.fig_parameters:
            return self.fig_parameters["colors"][i%len(self.fig_parameters["colors"])]

    def figPlot(self):
        # figure
        plt.figure(figsize=self.fig_parameters["figsize"])
        plt.title(self.fig_parameters["title"])
        # labels
        plt.xlabel(self.meta["X-name"])
        plt.ylabel(self.meta["Y-name"])
        # plot all
        for zi in range(self.meta["Z-size"]):
            plt.plot(
                self.getDataXs(zi),
                self.getDataYs(zi),
                self.fig_parameters["point"],
                label = self.meta["Z-names"][zi],
                c = self.getColor(zi) )
        # legend
        if self.fig_parameters["legend"]: plt.legend()

    def figShow(self):
        plt.show()

    def figSave(self, name):
        plt.savefig(name)
