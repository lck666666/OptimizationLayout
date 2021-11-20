from gurobipy import *
from DataInstance import DataInstance
from GurobiUtils import define1DIntVarArray, define2DBoolVarArrayArray

# Decision variables
def defineVars(data: DataInstance):
    model = Model("model")
    X = define1DIntVarArray(model, data.element_count, "X")
    Y = define1DIntVarArray(model, data.element_count, "Y")
    L = define1DIntVarArray(model, data.element_count, "L")
    W = define1DIntVarArray(model, data.element_count, "W")
    N = data.element_count
    return model, N, (X, Y, L, W)

def setVarNames(data:DataInstance, posVars):
    X, Y, L, W, = posVars
    for element in range(data.element_count):
        X[element].LB = data.borderXPadding
        X[element].UB = data.canvasWidth-data.elements[element].minWidth

        Y[element].LB = data.borderYPadding
        Y[element].UB = data.canvasHeight - data.elements[element].minHeight

        W[element].LB = data.elements[element].minWidth
        W[element].UB = data.elements[element].maxWidth

        L[element].LB = data.elements[element].minHeight
        L[element].UB = data.elements[element].maxHeight

# Ser constraints
def setConstraints(data: DataInstance, model: Model, posVars, N):
    X, Y, L, W = posVars
    k_1 = 0.2
    k_2 = 0.2
    R = 0.3
    A = 0.1
   
    # Constraint 0
    model.addConstr((sum(W[i] for i in range(N)) <= data.canvasWidth), "sumation")
    # Constraint 1
    for element in range(N):
        model.addConstr((R-k_1)*L[element] <= W[element], "Re-k1<We/Le("+str(element)+")")
        model.addConstr((R+k_1)*L[element] >= W[element], "Re+k1>We/Le("+str(element)+")")

    # Constraint 2
    for element in range(N):
        model.addConstr(X[element]+W[element] <= data.canvasWidth, "Xe+We<W("+str(element)+")")
        model.addConstr(Y[element]+L[element] <= data.canvasHeight, "Ye+Le<L("+str(element)+")")

    # Constraint 3
    for element in range(N):
       #model.addConstr(W[element] >= 50) #L[element].LB)
       #model.addConstr(W[element] <= 800) #L[element].UB)
       model.addConstr((A-k_2)*(data.canvasHeight*data.canvasHeight) <= W[element]*L[element],
                       "Ae-k2<(We*Le)/(W*L)["+str(element)+"]")
       model.addConstr((A+k_2)*(data.canvasHeight*data.canvasHeight) >= W[element]*L[element],
                       "Ae+k2>(We*Le)/(W*L)["+str(element)+"]")

    # Avoid overlapping
    z = model.addMVar((N,N), vtype=GRB.BINARY, name='z')
    model.addConstrs((z[i][j] == 1) >> (X[j] - X[i] >= W[i]) for i in range(N) for j in range(N) if i != j)
    model.addConstrs((z[i][j] == 0) >> (X[i] - X[j] >= W[j]) for i in range(N) for j in range(N) if i != j)

    

def extractVariableValues(N, L, X, Y, W, model, solNo):
    model.Params.SolutionNumber = solNo
    Xval = []
    Yval = []
    Wval = []
    Lval = []
    for element in range(N):
        Xval.append(X[element].xn)
        Yval.append(Y[element].xn)
        Wval.append(W[element].xn)
        Lval.append(L[element].xn)
    return Xval, Yval, Wval, Lval
