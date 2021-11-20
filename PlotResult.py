import matplotlib.pyplot as plt

def plotResult(X,Y,L,W,canvasW,canvasL,N):
    count = len(X)
    fig,ax = plt.subplots()
    ax.set_ylim(0, canvasL)
    ax.set_xlim(0, canvasW)
    for i in range(count):
        rect = plt.Rectangle((X[i],Y[i]),W[i],L[i],edgecolor = 'pink',lw=5)
        ax.add_patch(rect)
    plt.savefig(f'./results/{count}elements.jpg')
    plt.show()