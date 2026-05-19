import os
import tensorflow as tf

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import pypuf.simulation, pypuf.io
import pypuf.attack
import pypuf.metrics
import numpy as np
import matplotlib
import matplotlib.pyplot as plt


def puf_attack_2b():
    n_values = np.array([32, 64], dtype="int")
    k_down_values = np.array([2, 4, 8], dtype="int")
    n_crps = 100000

    results = np.empty(shape=[len(n_values), len(k_down_values)], dtype="float")

    for ni in range(len(n_values)):
        for ki in range(len(k_down_values)):
            n = n_values[ni]
            k = k_down_values[ki]
            print(f"n={n}, k_down={k}")
            puf = pypuf.simulation.InterposePUF(n=n, k_down=k, seed=1, k_up=1)
            crps = pypuf.io.ChallengeResponseSet.from_simulation(puf, N=n_crps, seed=2)  # type: ignore[arg-type]

            attack = pypuf.attack.MLPAttack2021(
                crps,
                seed=3,
                net=[2 ** (k + 1), 2 ** (k + 1)],
                bs=1000,
                lr=0.001,
                epochs=100,
                early_stop=0.01,
            )
            attack.fit()

            model = attack.model
            wynik = pypuf.metrics.similarity(puf, model, seed=4)

            results[ni][ki] = wynik
            print("---------------------------------------")

    os.makedirs("output", exist_ok=True)

    wykres, ax = plt.subplots(figsize=(8, 5))
    for ni, n in enumerate(n_values):
        ax.plot(k_down_values, results[ni], marker="o", label=f"n={n}")

    ax.set_xlabel("Liczba XOR (k_down)")
    ax.set_ylabel("Podobieństwo modelu")
    ax.set_title("MLPAttack2021 na InterposePUF")
    ax.set_xticks(k_down_values)
    ax.legend()
    ax.grid(True)

    plt.savefig("output/InterposePUF_MLP_attack.png", dpi=300)
    plt.show()

    print("*" * 80)
