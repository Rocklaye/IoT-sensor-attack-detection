# Captures réseau

Ce dossier contient les fichiers Wireshark `.pcapng` enregistrés pendant les expériences du laboratoire.

> **Remarque :** Les fichiers `.pcapng` bruts ne sont pas versionnés dans ce dépôt
> (taille importante + données potentiellement sensibles du réseau de labo).  
> Contacter les auteurs pour obtenir les captures originales à des fins de recherche.

## Fichiers enregistrés (disponibles sur demande)

| Nom du fichier | Scénario | Taille | Durée | Filtre clé |
|----------------|----------|--------|-------|------------|
| `bruteforce_camera.pcapng` | Brute-force HTTP-GET Hydra sur caméra | ~12 Mo | ~8 min | `http.authorization` |
| `dos_synflood_camera.pcapng` | Inondation SYN hping3 sur port 80 caméra | ~45 Mo | ~2 min | `tcp.flags.syn==1 && tcp.flags.ack==0` |
| `cryptojacking_pi.pcapng` | XMRig minage Monero après compromission SSH | ~28 Mo | ~15 min | `ip.dst == 209.38.61.60` |
| `dos_deauth_pi.pcapng` | Inondation deauth aireplay-ng sur Wi-Fi Pi | ~18 Mo | ~5 min | `wlan.fc.type==0 && wlan.fc.subtype==12` |

## Rejouer l'analyse

```bash
# Installer scapy
pip install scapy

# Analyser une capture
python scripts/traffic_analyzer.py \
  --capture captures/bruteforce_camera.pcapng \
  --victime 192.168.137.41 \
  --seuil-auth 5

python scripts/traffic_analyzer.py \
  --capture captures/dos_synflood_camera.pcapng \
  --victime 192.168.137.41 \
  --seuil-syn 200

python scripts/traffic_analyzer.py \
  --capture captures/cryptojacking_pi.pcapng \
  --victime 10.42.0.241

python scripts/traffic_analyzer.py \
  --capture captures/dos_deauth_pi.pcapng \
  --mac-victime E4:5F:01:C8:64:8B
```

## Paquets remarquables observés

### Brute-force (caméra)
```
Trame 177 : GET / HTTP/1.1 avec Authorization: Basic YWRtaW46YWRtaW4xMjM0NQ==
  Décodé : admin:admin12345
Wireshark affiche "TCP Retransmission" et floods "HTTP 401 Unauthorized"
```

### Cryptojacking (Pi)
```
Trame 277 : Pi (10.42.0.241) → requête DNS pour rx.unmineable.com
Trame 279 : Réponse DNS → CNAME → 209.38.61.60
Trame 280 : TCP SYN vers 209.38.61.60:80 (pool de minage)
Trames 281+ : échanges PSH/ACK continus avec charges Stratum de 386 octets
```

### DoS Wi-Fi Deauth (Pi)
```
Trames 44560–44597 : rafales de trames Deauth ciblant E4:5F:01:C8:64:8B
Filtre Wireshark : wlan.fc.type == 0 and wlan.fc.subtype == 12
Code raison Deauth 7 : "Trame de classe 3 reçue d'une STA non associée"
```
