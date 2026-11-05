#!/usr/bin/env python3
"""
serial_logger.py — Journalisation des mesures ACS712 (Arduino) vers CSV
=============================================================================
Lit la sortie numérique de current_sensor.ino via le port série USB et
écrit des lignes horodatées dans un fichier CSV.

Utilisation
-----------
    python serial_logger.py --port /dev/ttyACM0 --etiquette veille --duree 60
    python serial_logger.py --port COM3          --etiquette bruteforce --duree 120

Arguments
---------
  --port      Port série où l'Arduino est connecté
              Linux   : /dev/ttyACM0 ou /dev/ttyUSB0
              macOS   : /dev/cu.usbmodem...
              Windows : COM3, COM4, ...
  --etiquette Étiquette d'état ajoutée à chaque ligne du CSV
              Exemples : veille, streaming, bruteforce, dos_syn, cryptojacking, dos_wifi
  --duree     Durée d'enregistrement en secondes (défaut : 60)
  --sortie    Chemin du fichier CSV (généré automatiquement si omis)
  --bauds     Vitesse du port série (défaut : 9600, correspond à VITESSE_SERIE dans .ino)

Colonnes de sortie
------------------
  horodatage_iso   Horodatage ISO-8601 (heure locale)
  temps_ecoule_s   Secondes depuis le début de la capture
  courant_A        Lecture du courant en Ampères (valeur abs depuis l'Arduino)
  etiquette        Étiquette d'état fournie au lancement

Dépendances
-----------
  pip install pyserial

Projet : 8INF917 — Sécurité IoT, UQAC
Auteurs : Abdoulaye Aw, Tchakouani N.E. Armandine, Fatimata Ndiaya Sall, Maha El Allem
"""

import argparse
import csv
import os
import sys
import time
from datetime import datetime

try:
    import serial
except ImportError:
    print("ERREUR : pyserial non installé. Exécuter :  pip install pyserial", file=sys.stderr)
    sys.exit(1)


def parse_args():
    p = argparse.ArgumentParser(
        description="Journalisation des mesures de courant ACS712 (Arduino) vers CSV"
    )
    p.add_argument("--port",      required=True,  help="Port série (ex. /dev/ttyACM0 ou COM3)")
    p.add_argument("--etiquette", required=True,  help="Étiquette d'état : veille|streaming|bruteforce|dos_syn|cryptojacking|dos_wifi")
    p.add_argument("--duree",     type=int, default=60,   help="Durée d'enregistrement en secondes (défaut : 60)")
    p.add_argument("--bauds",     type=int, default=9600, help="Vitesse du port série (défaut : 9600)")
    p.add_argument("--sortie",    default=None,   help="Chemin du fichier CSV (généré automatiquement si omis)")
    return p.parse_args()


def construire_chemin_sortie(etiquette: str) -> str:
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    ici      = os.path.dirname(os.path.abspath(__file__))
    rep_data = os.path.join(ici, "..", "donnees")
    os.makedirs(rep_data, exist_ok=True)
    return os.path.join(rep_data, f"measures_{etiquette}_{ts}.csv")


def main():
    args         = parse_args()
    chemin_sortie = args.sortie or construire_chemin_sortie(args.etiquette)

    print(f"Ouverture du port série  : {args.port} @ {args.bauds} bauds")
    print(f"Durée d'enregistrement   : {args.duree} s")
    print(f"Étiquette d'état         : {args.etiquette}")
    print(f"Fichier de sortie        : {chemin_sortie}")
    print("─" * 55)
    print("Appuyer sur Ctrl+C pour arrêter avant la fin.\n")

    try:
        ser = serial.Serial(args.port, args.bauds, timeout=2)
    except serial.SerialException as e:
        print(f"ERREUR : impossible d'ouvrir {args.port} : {e}", file=sys.stderr)
        sys.exit(1)

    # Vider le tampon avant de commencer l'enregistrement
    time.sleep(2)
    ser.reset_input_buffer()

    debut       = time.monotonic()
    nb_lignes   = 0

    with open(chemin_sortie, "w", newline="", encoding="utf-8") as fichier_csv:
        writer = csv.writer(fichier_csv)
        writer.writerow(["horodatage_iso", "temps_ecoule_s", "courant_A", "etiquette"])

        try:
            while True:
                ecoule = time.monotonic() - debut
                if ecoule > args.duree:
                    break

                ligne_brute = ser.readline().decode("ascii", errors="replace").strip()

                # Ignorer les lignes de commentaire du sketch
                if not ligne_brute or ligne_brute.startswith("#"):
                    continue

                try:
                    courant_a = float(ligne_brute)
                except ValueError:
                    continue   # ignorer les lignes mal formées

                ts_iso = datetime.now().isoformat(timespec="milliseconds")
                writer.writerow([ts_iso, f"{ecoule:.2f}", f"{courant_a:.4f}", args.etiquette])
                nb_lignes += 1

                # Retour console toutes les 5 lignes
                if nb_lignes % 5 == 0:
                    print(f"  t={ecoule:6.1f}s  courant={courant_a:.3f} A  ({nb_lignes} échantillons)")

        except KeyboardInterrupt:
            print("\nArrêté par l'utilisateur.")

    ser.close()
    print(f"\n✓ {nb_lignes} lignes écrites dans {chemin_sortie}")

    # Statistiques rapides
    if nb_lignes > 0:
        import statistics
        valeurs = []
        with open(chemin_sortie, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            valeurs = [float(r["courant_A"]) for r in reader]
        if valeurs:
            print(f"  min={min(valeurs):.3f}  max={max(valeurs):.3f}  "
                  f"moy={statistics.mean(valeurs):.3f}  "
                  f"ecart-type={statistics.stdev(valeurs):.4f}  A")


if __name__ == "__main__":
    main()
