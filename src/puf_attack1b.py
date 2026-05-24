import csv
import os
import tensorflow as tf

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import pypuf.simulation, pypuf.io
import pypuf.attack
import pypuf.metrics
import numpy as np
import matplotlib
import matplotlib.pyplot as plt


def puf_attack_1b():
    n_apuf_seg = np.array([8, 16, 24, 32], dtype="int")
    n_xors = np.array([1, 2, 3, 4], dtype="int")
    n_crps = 100000

    Z = np.empty(shape=[len(n_apuf_seg), len(n_xors)], dtype="float")

    for segs in range(len(n_apuf_seg)):
        for xors in range(len(n_xors)):
            k = n_xors[xors]
            print("Segments", n_apuf_seg[segs], "XORs", k)
            puf = pypuf.simulation.XORArbiterPUF(n=n_apuf_seg[segs], k=k, seed=1)
            crps = pypuf.io.ChallengeResponseSet.from_simulation(puf, N=n_crps, seed=2)  # type: ignore[arg-type]

            attack = pypuf.attack.MLPAttack2021(
                crps,
                seed=3,
                net=[2**k, 2**k],
                bs=1000,
                lr=0.001,
                epochs=100,
                early_stop=0.01,
            )
            attack.fit()

            model = attack.model
            wynik = pypuf.metrics.similarity(puf, model, seed=4)

            Z[segs][xors] = wynik
            print("---------------------------------------")

    os.makedirs("output", exist_ok=True)
    with open("output/APUF_MLP_attack.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["n", "k", "similarity"])
        for segs in range(len(n_apuf_seg)):
            for xors in range(len(n_xors)):
                writer.writerow([n_apuf_seg[segs], n_xors[xors], Z[segs][xors]])

    X, Y = np.meshgrid(n_apuf_seg, n_xors, indexing="ij")

    wykres = matplotlib.pyplot.figure()
    w = wykres.add_subplot(projection="3d")
    w.set_proj_type("ortho")
    w.view_init(elev=30, azim=45)

    surf = w.plot_surface(X, Y, Z, cmap="coolwarm", linewidth=0.5, rstride=1, cstride=1)
    w.set_xlabel("Segmenty (n)")
    w.set_ylabel("Liczba XOR (k)")
    w.set_zlabel("Podobieństwo modelu")
    w.set_title("MLPAttack2021 na XOR APUF")
    wykres.colorbar(surf, shrink=0.5)

    plt.savefig("output/APUF_MLP_attack.png", dpi=300)
    plt.show()

    print("*" * 80)
