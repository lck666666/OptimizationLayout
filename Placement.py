from matplotlib.pyplot import xcorr
from gurobipy import *
from PlotResult import plotResult
from Model import defineVars, setVarNames, setConstraints
from SolutionManager import SolutionManager
from DataInstance import DataInstance
import numpy as np

class Placement:
    def __init__(self, data: DataInstance, sol_mgr: SolutionManager):
        self.listOfVars = []
        self.data: DataInstance = data
        self.solNo = None
        self.X = None
        self.Y = None
        self.L = None
        self.W = None
        self.sol_mgr: SolutionManager = sol_mgr

    def solve(self, verbose=True):
        X_value = []
        Y_value = []
        L_value = []
        W_value = []
        try:
            model, N, posVars = defineVars(self.data)
            X, Y, L, W = posVars

            self.X = X
            self.Y = Y
            self.L = L
            self.W = W

            setVarNames(self.data, posVars)

            # Define objective
            model.setObjective(sum(W[element]*L[element] for element in range(N)), GRB.MAXIMIZE)
            model.params.NonConvex = 2
            setConstraints(self.data, model, posVars, N)
            self.solNo = 1
            model.write("Formular.lp")

            model.optimize(lambda model, where: self.tapSolutions(model, where))

            # Read the output file -> store new X, Y, L, W for each elements
            #model.printAttr('X')
            for v in model.getVars():
                print (v.varName, v.x)
                if('X' in v.varName):
                    X_value.append(v.x)
                elif('Y' in v.varName):
                    Y_value.append(v.x)
                elif('L' in v.varName):
                    L_value.append(v.x)
                elif('W' in v.varName):
                    W_value.append(v.x)
            print("X:",X_value)
            print("Y:",Y_value)
            print("L:",L_value)
            print("W:",W_value)
            plotResult(X_value,Y_value,L_value,W_value,self.data.canvasHeight,self.data.canvasWidth,N)

                
            
            if model.Status == GRB.Status.INFEASIBLE:
                print("Infeasible")
                return False

        except GurobiError as e:
            print('Gurobi Error code ' + str(e.errno) + ": " + str(e))

        except AttributeError as e:
            print('AttributeError:', str(e), e)

        except Exception as e:
            print('Unidentified Error:' + str(e))
        return False

    def tapSolutions(self, model: Model, where):
        if where == GRB.Callback.MIPSOL:
            objeValue = model.cbGet(GRB.Callback.MIPSOL_OBJ)
            lowerBound = model.cbGet(GRB.Callback.MIPSOL_OBJBND)
            bestKnownSolution = model.cbGet(GRB.Callback.MIPSOL_OBJBST)
            print("*** Found a solution with ObjValue = ", objeValue, " where estimate range = <", lowerBound, " -- ",
                  bestKnownSolution, ">")

            percentGap = (objeValue - lowerBound) / lowerBound
            if bestKnownSolution == 0.0:
                qualityMetric = 0.0
            else:
                qualityMetric = (objeValue - bestKnownSolution) / bestKnownSolution
            print("Quality metric at ", qualityMetric)

            t = model.cbGet(GRB.Callback.RUNTIME)
            if (percentGap > 0.99) and (qualityMetric > 0.2):
                if t < 5 or t < self.data.element_count:
                    print("Neglected poor solution because percentGap=", percentGap, " and quality metric = ",
                          qualityMetric)
                    return
            percentGap = math.floor(percentGap * 100)
            print("Entering solution at t=", t, " with pending gap%=", percentGap)

            objeValue = math.floor(objeValue * 10000) / 10000.0
            print("Tapped into Solution No", self.solNo, " of objective value ", objeValue,
                  " with lower bound at ", lowerBound)
            Xval, Yval, L_eval, W_eval = self.extractVariableValuesFromPartialSolution(model)
            self.sol_mgr.build_new_solution(self.data, self.solNo, objeValue, Xval, Yval, L_eval, W_eval)
            self.solNo += 1

    def extractVariableValuesFromPartialSolution(self, model: Model):
        Xval = []
        Yval = []
        Lval = []
        Wval = []
        for element in range(self.data.element_count):
            Xval.append(model.cbGetSolution(self.X[element]))
            Yval.append(model.cbGetSolution(self.Y[element]))
            Lval.append(model.cbGetSolution(self.L[element]))
            Wval.append(model.cbGetSolution(self.W[element]))
        return Xval, Yval, Lval, Wval


