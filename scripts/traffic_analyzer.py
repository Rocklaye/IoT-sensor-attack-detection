#!/usr/bin/env python3
"""
traffic_analyzer.py — Détection de patterns d'attaque dans les captures Wireshark
===================================================================================
Analyse un fichier .pcap/.pcapng et signale quatre signatures d'attaque observées
lors des expériences du laboratoire 8INF917 à l'UQAC :

  1. Brute-force HTTP   — avalanche de réponses HTTP 401 ciblant la caméra
  2. DoS inondation SYN — paquets TCP SYN à haut débit sans ACK correspondant
  3. Cryptojacking      — connexions TCP sortantes vers des pools de minage connus
  4. DoS Wi-Fi deauth   — avalanche de trames 802.11 Désauthentification (type 0, sous-type 12)

Utilisation
-----------
    python traffic_analyzer.py --capture captures/bruteforce_camera.pcapng
    python traffic_analyzer.py --capture captures/cryptojacking_pi.pcapng --victime 10.42.0.241
    python traffic_analyzer.py --capture captures/dos_camera.pcapng --seuil-syn 500

Arguments
---------
  --capture      Chemin vers le fichier .pcap ou .pcapng
  --victime      Adresse IP du dispositif surveillé (optionnel — filtre les résultats)
  --seuil-syn    Paquets SYN/seconde considérés suspects (défaut : 200)
  --seuil-auth   Tentatives d'authentification HTTP/seconde suspectes (défaut : 5)
  --fenetre-s    Fenêtre de temps en secondes pour le calcul de débit (défaut : 1)
  --rapport      Écrire un rapport JSON dans ce fichier (optionnel)

Dépendances
-----------
  pip install scapy

Projet : 8INF917 — Sécurité IoT, UQAC
Auteurs : Abdoulaye Aw, Tchakouani N.E. Armandine, Fatimata Ndiaya Sall, Maha El Allem
"""

from __future__ import annotations
import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Tuple

try:
    from scapy.all import rdpcap, TCP, UDP, IP, Raw, Dot11, Dot11Deauth
except ImportError:
    print("ERREUR : scapy non installé. Exécuter :  pip install scapy", file=sys.stderr)
    sys.exit(1)


# ── Indicateurs connus des pools de minage (observés dans les captures du labo) ─
IP_POOLS_MINAGE = {
    "209.38.61.60",    # rx.unmineable.com (observé dans la capture Wireshark)
}

DOMAINES_POOLS = ["unmineable", "xmrpool", "minexmr", "supportxmr", "monerocean"]

# Protocole Stratum sur TCP, typiquement ports 3333, 5555, 14444
PORTS_STRATUM = {3333, 5555, 14444, 45560, 80, 443}


# ── Fonctions utilitaires ─────────────────────────────────────────────────────
def ts_vers_epoch(paquet) -> float:
    return float(paquet.time)


def tranche(epoch: float, fenetre_s: int) -> int:
    return int(epoch // fenetre_s)


# ── Détecteurs ────────────────────────────────────────────────────────────────
def detecter_inondation_syn(
    paquets,
    victime_ip: str | None,
    seuil: int,
    fenetre_s: int,
) -> List[dict]:
    """Comptabilise les paquets TCP SYN par (ip_src, ip_dst, tranche_temporelle)."""
    compteur_syn: Dict[Tuple, int] = defaultdict(int)

    for p in paquets:
        if not (p.haslayer(IP) and p.haslayer(TCP)):
            continue
        tcp = p[TCP]
        # Drapeau SYN activé, drapeau ACK désactivé → SYN pur
        if tcp.flags & 0x02 and not (tcp.flags & 0x10):
            dst = p[IP].dst
            if victime_ip and dst != victime_ip:
                continue
            cle = (p[IP].src, dst, tranche(ts_vers_epoch(p), fenetre_s))
            compteur_syn[cle] += 1

    resultats = []
    for (src, dst, t), nb in compteur_syn.items():
        if nb >= seuil:
            resultats.append({
                "type": "INONDATION_SYN",
                "ip_source": src,
                "ip_destination": dst,
                "tranche_temporelle": t * fenetre_s,
                "syn_par_fenetre": nb,
                "seuil": seuil,
                "severite": "ÉLEVÉE" if nb > seuil * 5 else "MOYENNE",
                "detail": (
                    f"{nb} paquets SYN/s depuis {src} → {dst}. "
                    "Correspond au pattern hping3 '-S -p 80 -i u1000' observé en labo."
                ),
            })
    return resultats


def detecter_bruteforce_http(
    paquets,
    victime_ip: str | None,
    seuil: int,
    fenetre_s: int,
) -> List[dict]:
    """
    Détecte les répétitions de HTTP 401 OU de requêtes HTTP avec
    en-tête Authorization: Basic vers la même destination.
    """
    compteur_req_auth: Dict[Tuple, int] = defaultdict(int)
    compteur_rep_401: Dict[Tuple, int] = defaultdict(int)
    identifiants_clair: List[str] = []

    for p in paquets:
        if not (p.haslayer(IP) and p.haslayer(TCP) and p.haslayer(Raw)):
            continue
        charge = bytes(p[Raw].load)
        try:
            texte = charge.decode("utf-8", errors="ignore")
        except Exception:
            continue

        ip_dst = p[IP].dst
        ip_src = p[IP].src
        t = tranche(ts_vers_epoch(p), fenetre_s)

        # Requêtes HTTP sortantes avec en-tête Basic auth
        if b"GET" in charge or b"POST" in charge:
            if b"Authorization: Basic" in charge:
                if not (victime_ip and ip_dst != victime_ip):
                    compteur_req_auth[(ip_src, ip_dst, t)] += 1
                    for ligne in texte.split("\r\n"):
                        if ligne.startswith("Authorization: Basic "):
                            b64 = ligne.split(" ", 2)[-1].strip()
                            if b64 not in identifiants_clair:
                                identifiants_clair.append(b64)

        # Réponses HTTP 401 de la caméra
        if b"HTTP/1." in charge and b"401" in charge:
            if not (victime_ip and ip_src != victime_ip):
                compteur_rep_401[(ip_src, ip_dst, t)] += 1

    resultats = []
    for (src, dst, t), nb in compteur_req_auth.items():
        if nb >= seuil:
            resultats.append({
                "type": "BRUTE_FORCE_HTTP",
                "ip_attaquant": src,
                "ip_cible": dst,
                "tranche_temporelle": t * fenetre_s,
                "requetes_auth_par_fenetre": nb,
                "seuil": seuil,
                "severite": "ÉLEVÉE",
                "detail": (
                    f"{nb} requêtes HTTP avec en-tête Authorization: Basic/s "
                    f"depuis {src} → {dst}. "
                    "Aucun HTTPS — identifiants visibles en clair. "
                    f"Blobs Base64 observés : {identifiants_clair[:3]}"
                ),
            })

    for (src, dst, t), nb in compteur_rep_401.items():
        if nb >= seuil:
            resultats.append({
                "type": "FLOOD_HTTP_401",
                "ip_camera": src,
                "ip_attaquant": dst,
                "tranche_temporelle": t * fenetre_s,
                "reponses_par_fenetre": nb,
                "seuil": seuil,
                "severite": "MOYENNE",
                "detail": f"Caméra {src} : {nb} réponses HTTP 401/s — brute-force en cours.",
            })

    return resultats


def detecter_cryptojacking(paquets, victime_ip: str | None) -> List[dict]:
    """
    Détecte les connexions sortantes vers des pools Monero connus.
    Signature observée : Pi (10.42.0.241) → 209.38.61.60 sur port 80
    avec échanges PSH/ACK transportant le protocole Stratum.
    """
    resultats = []
    deja_vu: set = set()

    for p in paquets:
        if not (p.haslayer(IP) and p.haslayer(TCP)):
            continue
        src   = p[IP].src
        dst   = p[IP].dst
        dport = p[TCP].dport

        if victime_ip and src != victime_ip:
            continue

        est_pool_ip = dst in IP_POOLS_MINAGE or any(d in dst for d in DOMAINES_POOLS)

        charge_stratum = False
        if p.haslayer(Raw):
            try:
                texte_brut = p[Raw].load.decode("utf-8", errors="ignore")
                if "stratum" in texte_brut.lower() or '"method":"mining.' in texte_brut:
                    charge_stratum = True
            except Exception:
                pass

        if (est_pool_ip or charge_stratum) and (src, dst) not in deja_vu:
            deja_vu.add((src, dst))
            resultats.append({
                "type": "CRYPTOJACKING",
                "ip_victime": src,
                "ip_pool": dst,
                "port": dport,
                "severite": "CRITIQUE",
                "detail": (
                    f"Connexion de minage sortante : {src} → {dst}:{dport}. "
                    "Correspond au pattern XMRig/Stratum/Monero observé en labo. "
                    "Processus déguisé en 'system_update_daemon' sur le Pi — "
                    "CPU ~97,6 %, RAM 691 Mo / 1,80 Go."
                ),
            })

    return resultats


def detecter_deauth_wifi(paquets, mac_victime: str | None) -> List[dict]:
    """
    Comptabilise les trames 802.11 Désauthentification.
    Filtre : wlan.fc.type == 0 et wlan.fc.subtype == 12
    Commande observée en labo :
      aireplay-ng --deauth 0 -a 10:68:38:B2:58:EB -c E4:5F:01:C8:64:8B wlan0
    """
    compteur_deauth: Dict[Tuple, int] = defaultdict(int)

    for p in paquets:
        if p.haslayer(Dot11Deauth):
            src = p.addr2 or "inconnu"
            dst = p.addr1 or "broadcast"
            if mac_victime and dst.lower() not in (mac_victime.lower(), "ff:ff:ff:ff:ff:ff"):
                continue
            compteur_deauth[(src, dst)] += 1

    resultats = []
    for (src, dst), nb in compteur_deauth.items():
        if nb > 10:
            resultats.append({
                "type": "FLOOD_DEAUTH_WIFI",
                "bssid_attaquant": src,
                "mac_victime": dst,
                "trames_deauth": nb,
                "severite": "ÉLEVÉE",
                "detail": (
                    f"{nb} trames Deauth depuis {src} → {dst}. "
                    "Raspberry Pi (MAC E4:5F:01:C8:64:8B) déconnecté en continu ; "
                    "chaque tentative de reconnexion est immédiatement interrompue."
                ),
            })

    return resultats


# ── Point d'entrée ────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(description="Détection de patterns d'attaque dans des captures PCAP")
    p.add_argument("--capture",    required=True, help="Chemin vers le fichier .pcap ou .pcapng")
    p.add_argument("--victime",    default=None,  help="Adresse IP du dispositif surveillé (optionnel)")
    p.add_argument("--mac-victime",default=None,  help="Adresse MAC pour la détection deauth Wi-Fi (optionnel)")
    p.add_argument("--seuil-syn",  type=int, default=200, help="Paquets SYN/fenêtre pour alerte inondation (défaut : 200)")
    p.add_argument("--seuil-auth", type=int, default=5,   help="Requêtes auth/fenêtre pour alerte brute-force (défaut : 5)")
    p.add_argument("--fenetre-s",  type=int, default=1,   help="Fenêtre de temps en secondes (défaut : 1)")
    p.add_argument("--rapport",    default=None,  help="Écrire le rapport JSON dans ce fichier")
    args = p.parse_args()

    print(f"Chargement de la capture : {args.capture}")
    try:
        paquets = rdpcap(args.capture)
    except FileNotFoundError:
        print(f"ERREUR : fichier introuvable : {args.capture}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERREUR lors de la lecture du pcap : {e}", file=sys.stderr)
        sys.exit(1)

    total = len(paquets)
    print(f"Paquets chargés : {total}")
    print("─" * 60)

    tous_resultats = []

    tous_resultats += detecter_inondation_syn(paquets, args.victime, args.seuil_syn, args.fenetre_s)
    tous_resultats += detecter_bruteforce_http(paquets, args.victime, args.seuil_auth, args.fenetre_s)
    tous_resultats += detecter_cryptojacking(paquets, args.victime)
    tous_resultats += detecter_deauth_wifi(paquets, args.mac_victime)

    # Affichage des résultats
    if not tous_resultats:
        print("Aucun pattern d'attaque détecté.")
    else:
        print(f"\n{'=' * 60}")
        print(f"  {len(tous_resultats)} RÉSULTAT(S) DÉTECTÉ(S)")
        print(f"{'=' * 60}\n")
        for i, r in enumerate(tous_resultats, 1):
            sev = r.get("severite", "?")
            icone = {"CRITIQUE": "🔴", "ÉLEVÉE": "🟠", "MOYENNE": "🟡"}.get(sev, "⚪")
            print(f"[{i}] {icone} {r['type']}  ({sev})")
            print(f"    {r['detail']}")
            print()

    # Rapport JSON
    rapport = {
        "fichier_capture": args.capture,
        "heure_analyse": datetime.now(timezone.utc).isoformat(),
        "total_paquets": total,
        "ip_victime": args.victime,
        "nb_resultats": len(tous_resultats),
        "resultats": tous_resultats,
    }

    if args.rapport:
        with open(args.rapport, "w", encoding="utf-8") as fh:
            json.dump(rapport, fh, indent=2, ensure_ascii=False)
        print(f"Rapport JSON écrit dans {args.rapport}")
    else:
        print(json.dumps(rapport, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
