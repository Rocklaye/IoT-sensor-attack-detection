#!/usr/bin/env python3
"""
plot_energy.py — Visualisation de la consommation électrique par scénario d'attaque
========================================================================================
Génère deux histogrammes côte à côte depuis data/measurements_summary.csv :
  - Gauche  : Caméra IP Hosafe (4 états)
  - Droite  : Raspberry Pi 4 (3 états)

Sortie : docs/energy_comparison.png

Utilisation
-----------
    python scripts/plot_energy.py

Dépendances
-----------
    pip install matplotlib pandas numpy

Projet : 8INF917 — Sécurité IoT, UQAC
Auteurs : Abdoulaye Aw et al.
"""

import os
import sys

try:
    import matplotlib
    matplotlib.use("Agg")  # rendu sans interface graphique
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
except ImportError:
    print("ERREUR : installer matplotlib : pip install matplotlib numpy", file=sys.stderr)
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print("ERREUR : installer pandas : pip install pandas", file=sys.stderr)
    sys.exit(1)


# ── Chemins ───────────────────────────────────────────────────────────────────
ICI         = os.path.dirname(os.path.abspath(__file__))
CHEMIN_CSV  = os.path.join(ICI, "..", "data", "measurements_summary.csv")
CHEMIN_SORTIE = os.path.join(ICI, "..", "docs", "energy_comparison.png")


# ── Palette de couleurs — neutre, accessible aux daltoniens ───────────────────
COULEUR_VEILLE       = "#6baed6"   # bleu
COULEUR_NORMAL       = "#74c476"   # vert
COULEUR_ATTAQUE_FAIB = "#fd8d3c"   # orange
COULEUR_ATTAQUE_MOY  = "#e6550d"   # orange foncé
COULEUR_ATTAQUE_FORT = "#d62728"   # rouge


def charger_donnees(chemin_csv: str) -> pd.DataFrame:
    return pd.read_csv(chemin_csv)


def donnees_camera(df: pd.DataFrame):
    cam = df[df["dispositif"].str.contains("Caméra")].copy()
    ordre = ["É1_veille", "É2_streaming", "É3_bruteforce", "É4_dos"]
    cam = cam.set_index("etiquette").reindex(ordre).reset_index()
    return cam


def donnees_pi(df: pd.DataFrame):
    pi = df[df["dispositif"].str.contains("Raspberry")].copy()
    ordre = ["Pi_veille", "Pi_cryptojacking", "Pi_dos_wifi"]
    pi = pi.set_index("etiquette").reindex(ordre).reset_index()
    return pi


def generer_graphique():
    df  = charger_donnees(CHEMIN_CSV)
    cam = donnees_camera(df)
    pi  = donnees_pi(df)

    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    fig.patch.set_facecolor("#0d1117")  # fond sombre style GitHub

    for ax in axes:
        ax.set_facecolor("#161b22")
        ax.tick_params(colors="#c9d1d9")
        ax.xaxis.label.set_color("#c9d1d9")
        ax.yaxis.label.set_color("#c9d1d9")
        ax.title.set_color("#f0f6fc")
        for spine in ax.spines.values():
            spine.set_edgecolor("#30363d")

    # ── Graphique gauche : Caméra IP ──────────────────────────────────────────
    ax = axes[0]
    etiquettes_cam = ["Veille", "Streaming\n(utilisation\nnormale)", "Brute-force\nHTTP (Hydra)", "DoS SYN\n(hping3)"]
    couleurs_cam   = [COULEUR_VEILLE, COULEUR_NORMAL, COULEUR_ATTAQUE_FAIB, COULEUR_ATTAQUE_MOY]
    x = np.arange(len(etiquettes_cam))
    barres = ax.bar(x, cam["courant_moy_A"].values, 0.55, color=couleurs_cam,
                    edgecolor="#30363d", linewidth=0.8)

    # Barres d'erreur (min/max)
    err_bas  = cam["courant_moy_A"].values - cam["courant_min_A"].values
    err_haut = cam["courant_max_A"].values - cam["courant_moy_A"].values
    ax.errorbar(x, cam["courant_moy_A"].values,
                yerr=[err_bas, err_haut],
                fmt="none", ecolor="#f0f6fc", elinewidth=1.2, capsize=4)

    # Annotation valeur moyenne
    for barre, moy in zip(barres, cam["courant_moy_A"].values):
        ax.text(barre.get_x() + barre.get_width() / 2,
                barre.get_height() + 0.004,
                f"{moy:.2f} A",
                ha="center", va="bottom", fontsize=9, color="#f0f6fc", fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(etiquettes_cam, fontsize=9)
    ax.set_ylabel("Courant moyen (A)", fontsize=10)
    ax.set_title("Caméra IP Hosafe HX-2PT1\nConsommation électrique par état", fontsize=11, fontweight="bold")
    ax.set_ylim(0, 0.35)
    ax.yaxis.grid(True, color="#30363d", linewidth=0.6, alpha=0.8)
    ax.set_axisbelow(True)

    # Annotation clé : streaming > brute-force
    ax.annotate("⚠ Streaming consomme\nPLUS que le brute-force\n→ énergie seule insuffisante",
                xy=(2, cam["courant_moy_A"].values[2]),
                xytext=(2.4, 0.26),
                fontsize=7.5, color="#f0a832",
                arrowprops=dict(arrowstyle="->", color="#f0a832", lw=1.0))

    # ── Graphique droit : Raspberry Pi ───────────────────────────────────────
    ax = axes[1]
    etiquettes_pi = ["Veille", "Cryptojacking\n(XMRig / Monero)", "DoS Wi-Fi\n(inondation Deauth)"]
    couleurs_pi   = [COULEUR_VEILLE, COULEUR_ATTAQUE_FORT, COULEUR_ATTAQUE_MOY]
    x = np.arange(len(etiquettes_pi))
    barres = ax.bar(x, pi["courant_moy_A"].values, 0.55, color=couleurs_pi,
                    edgecolor="#30363d", linewidth=0.8)

    err_bas  = pi["courant_moy_A"].values - pi["courant_min_A"].values
    err_haut = pi["courant_max_A"].values - pi["courant_moy_A"].values
    ax.errorbar(x, pi["courant_moy_A"].values,
                yerr=[err_bas, err_haut],
                fmt="none", ecolor="#f0f6fc", elinewidth=1.2, capsize=4)

    for barre, moy in zip(barres, pi["courant_moy_A"].values):
        ax.text(barre.get_x() + barre.get_width() / 2,
                barre.get_height() + 0.01,
                f"{moy:.2f} A",
                ha="center", va="bottom", fontsize=9, color="#f0f6fc", fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(etiquettes_pi, fontsize=9)
    ax.set_ylabel("Courant moyen (A)", fontsize=10)
    ax.set_title("Raspberry Pi 4 — Passerelle Linux embarquée\nConsommation électrique par état", fontsize=11, fontweight="bold")
    ax.set_ylim(0, 1.25)
    ax.yaxis.grid(True, color="#30363d", linewidth=0.6, alpha=0.8)
    ax.set_axisbelow(True)

    ax.annotate("+200% vs veille\n97,6% CPU (htop)",
                xy=(1, pi["courant_moy_A"].values[1]),
                xytext=(1.35, 0.60),
                fontsize=8, color="#ff6b6b",
                arrowprops=dict(arrowstyle="->", color="#ff6b6b", lw=1.0))

    # ── Légende commune ───────────────────────────────────────────────────────
    entrees_legende = [
        mpatches.Patch(color=COULEUR_VEILLE,       label="Veille / état normal"),
        mpatches.Patch(color=COULEUR_NORMAL,        label="Utilisation normale (streaming)"),
        mpatches.Patch(color=COULEUR_ATTAQUE_FAIB,  label="Attaque faible intensité"),
        mpatches.Patch(color=COULEUR_ATTAQUE_MOY,   label="Attaque moyenne intensité"),
        mpatches.Patch(color=COULEUR_ATTAQUE_FORT,  label="Attaque haute intensité"),
    ]
    fig.legend(handles=entrees_legende, loc="lower center", ncol=5,
               frameon=True, facecolor="#161b22", edgecolor="#30363d",
               labelcolor="#c9d1d9", fontsize=8.5,
               bbox_to_anchor=(0.5, -0.02))

    fig.suptitle(
        "Détection d'attaques sur capteurs IoT — Analyse de la consommation électrique hors-bande\n"
        "UQAC 8INF917 · Hiver 2026",
        fontsize=13, fontweight="bold", color="#f0f6fc", y=1.01
    )

    plt.tight_layout(rect=[0, 0.06, 1, 1])

    os.makedirs(os.path.dirname(CHEMIN_SORTIE), exist_ok=True)
    fig.savefig(CHEMIN_SORTIE, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    print(f"Graphique enregistré → {CHEMIN_SORTIE}")


if __name__ == "__main__":
    generer_graphique()
