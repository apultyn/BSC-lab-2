import os
import tensorflow as tf

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import pypuf.simulation, pypuf.io
import pypuf.attack
import pypuf.metrics
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator

n_apuf_seg = np.array([8, 16, 24, 32], dtype="int")
n_xors = np.array([1, 2, 3, 4], dtype="int")
n_crps = 100000

Z = np.empty(shape=[len(n_apuf_seg), len(n_xors)], dtype="float")

for segs in range(len(n_apuf_seg)):
    for xors in range(len(n_xors)):
        print("Segments", n_apuf_seg[segs], "XORs", n_xors[xors])
        puf = pypuf.simulation.XORArbiterPUF(n=n_apuf_seg[segs], k=n_xors[xors], seed=1)
        crps = pypuf.io.ChallengeResponseSet.from_simulation(puf, N=n_crps, seed=2)

        attack = pypuf.attack.LRAttack2021(
            crps, seed=3, k=n_xors[xors], bs=1000, lr=0.001, epochs=100
        )
        attack.fit()

        model = attack.model
        wynik = pypuf.metrics.similarity(puf, model, seed=4)

        Z[segs][xors] = wynik
        print("---------------------------------------")


X, Y = np.meshgrid(n_apuf_seg, n_xors, indexing="ij")

wykres = matplotlib.pyplot.figure()
w = wykres.add_subplot(projection="3d")
w.set_proj_type("ortho")
w.view_init(elev=30, azim=45)
# print (np.amin(Z), np.amax(Z))

# w.plot_surface(X, Y, Z, cmap=plt.cm.coolwarm , linewidth=.5, rstride=1, cstride=1)
plt.show()

os.makedirs("output", exist_ok=True)
plt.savefig("output/APUF_attack1.png", dpi=300)


print("*" * 80)
