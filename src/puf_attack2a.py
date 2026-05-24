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


def puf_attack_2a():
    n_values = np.array([8, 16, 24, 32, 64], dtype="int")
    k_down_values = np.array([2, 4, 8], dtype="int")
    n_crps = 100000

    results = np.empty(shape=[len(n_values), len(k_down_values)], dtype="float")

    for ni in range(len(n_values)):
        for ki in range(len(k_down_values)):
            n = n_values[ni]
            k = k_down_values[ki]
            print(f"n={n}, k_down={k}")
            puf = pypuf.simulation.InterposePUF(n=n, k_down=k, seed=1, k_up=1)
            crps = pypuf.io.ChallengeResponseSet.from_simulation(puf, N=n_crps, seed=2)

            attack = pypuf.attack.LRAttack2021(
                crps, seed=3, k=k + 1, bs=1000, lr=0.001, epochs=100
            )
            attack.fit()

            model = attack.model
            wynik = pypuf.metrics.similarity(puf, model, seed=4)

            results[ni][ki] = wynik
            print("---------------------------------------")

    os.makedirs("output", exist_ok=True)

    with open("output/InterposePUF_LR_attack.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["n", "k_down", "similarity"])
        for ni in range(len(n_values)):
            for ki in range(len(k_down_values)):
                writer.writerow([n_values[ni], k_down_values[ki], results[ni][ki]])

    wykres, ax = plt.subplots(figsize=(8, 5))
    for ni, n in enumerate(n_values):
        ax.plot(k_down_values, results[ni], marker="o", label=f"n={n}")

    ax.set_xlabel("Liczba XOR (k_down)")
    ax.set_ylabel("Podobieństwo modelu")
    ax.set_title("LRAttack2021 na InterposePUF")
    ax.set_xticks(k_down_values)
    ax.legend()
    ax.grid(True)

    plt.savefig("output/InterposePUF_LR_attack.png", dpi=300)
    plt.show()

    print("*" * 80)
