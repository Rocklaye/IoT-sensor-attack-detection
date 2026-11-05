# Topologie et configuration du réseau de laboratoire

> Documentation de l'infrastructure réseau mise en place manuellement
> pour les expériences UQAC 8INF917 (Hiver 2026).
>
> L'objectif était de créer un réseau de laboratoire **isolé et contrôlé**
> reproduisant un environnement IoT typique : dispositifs connectés sur
> un même segment, visibles les uns des autres, sans accès Internet non
> maîtrisé.

---

## Topologie générale

```
                      ┌─────────────────────────────────────┐
                      │      PC de surveillance              │
                      │      Ubuntu 22.04 LTS               │
                      │      (Arduino IDE + Wireshark)       │
                      │                                      │
                      │  eth0 : 10.42.0.1 (hotspot filaire) │
                      │  wlan0 : connecté à "shadow"         │
                      └────────┬──────────────┬─────────────┘
                               │ Ethernet     │ USB (série)
                      Hotspot  │              │
                      NetworkManager          │
                      DHCP 10.42.0.1/24       │
                               │              │
              ┌────────────────┤              │
              │                │              │
    ┌─────────┴──────┐  ┌──────┴──────┐  ┌───┴────────────┐
    │  Caméra IP     │  │ Raspberry   │  │  Arduino Uno   │
    │  Hosafe HX-2PT1│  │ Pi 4        │  │  + ACS712      │
    │                │  │             │  │  (mesure       │
    │  10.42.0.234   │  │ 10.42.0.241 │  │   courant)     │
    │  Wi-Fi "shadow"│  │ eth0 filaire│  └────────────────┘
    │  192.168.137.41│  │ wlan0 shadow│
    └────────────────┘  └─────────────┘
              │                │
              └────────┬───────┘
                       │ Wi-Fi 802.11n
                  ┌────┴─────────────────┐
                  │  Point d'accès Wi-Fi  │
                  │  Réseau "shadow"      │
                  │  BSSID: 10:68:38:B2:58:EB  │
                  │  Canal: 6 (2,437 GHz) │
                  │  Chiffrement: WPA2    │
                  └───────────────────────┘

              ┌─────────────────────────────┐
              │  Machine attaquante          │
              │  Kali Linux                  │
              │  10.42.0.11 (eth0, filaire)  │
              │  + Alfa AWUS036ACS (wlan1)   │
              │    pour attaques Wi-Fi        │
              └─────────────────────────────┘
```

---

## Plan d'adressage IP

| Dispositif | Interface | Adresse IP | Méthode | Rôle |
|-----------|-----------|-----------|---------|------|
| PC surveillance | eth0 | 10.42.0.1 | Statique (hotspot) | Passerelle, DHCP, monitoring |
| Raspberry Pi 4 | eth0 | 10.42.0.241 | DHCP (hotspot) | Victime IoT 2 |
| Caméra Hosafe | wlan | 10.42.0.234 | DHCP (hotspot) | Victime IoT 1 |
| Caméra Hosafe | — | 192.168.137.41 | IP secondaire | Accès admin HTTP (port 80) |
| Machine Kali | eth0 | 10.42.0.11 | DHCP (hotspot) | Attaquant |
| Machine Kali | — | 10.143.63.128 | IP secondaire | (session initiale) |
| Pool de minage | — | 209.38.61.60 | Externe | rx.unmineable.com (Monero) |

---

## Mise en place du réseau

### Étape 1 — Hotspot filaire sur le PC de surveillance

Le PC Ubuntu 22.04 partage sa connexion réseau via NetworkManager, créant
un segment Ethernet isolé sur lequel tous les dispositifs de laboratoire
sont connectés.

```bash
# Créer le hotspot filaire avec NetworkManager
nmcli connection add type ethernet \
  con-name "labo-hotspot" \
  ifname eth0 \
  ipv4.method shared \
  ipv4.addresses 10.42.0.1/24

nmcli connection up "labo-hotspot"

# Vérification du service DHCP (dnsmasq intégré à NetworkManager)
sudo ss -tulnp | grep 67
# → udp  UNCONN  0  0  10.42.0.1:67  *:*  users:(("dnsmasq",…))

# Vérifier les baux DHCP actifs
cat /var/lib/NetworkManager/dnsmasq-*.leases
# → <timestamp>  <MAC>  10.42.0.234  Hosafe-camera
# → <timestamp>  <MAC>  10.42.0.241  raspberrypi
# → <timestamp>  <MAC>  10.42.0.11   kali
```

### Étape 2 — Réseau Wi-Fi "shadow"

Le réseau Wi-Fi "shadow" est utilisé pour connecter la caméra IP (Wi-Fi uniquement)
et le Raspberry Pi (double connexion : filaire + Wi-Fi pour les tests de déauth).

```bash
# Identifier les réseaux Wi-Fi disponibles
nmcli device wifi list

# Connexion des dispositifs au réseau "shadow"
# (réalisée via l'interface de configuration de chaque appareil)
# Caméra : configuration via application mobile Hosafe
# Pi     : via nmcli ou interface graphique Raspberry Pi OS

# Paramètres du réseau "shadow"
#   SSID    : shadow
#   BSSID   : 10:68:38:B2:58:EB
#   Canal   : 6 (fréquence 2,437 GHz)
#   Sécurité: WPA2-Personal
#   Fabricant BSSID: AzureWave Technology (NIC Wi-Fi intégré au routeur)
```

### Étape 3 — Capture Wireshark (port SPAN simulé)

Faute de switch manageable avec port SPAN, la capture du trafic est réalisée
directement depuis le PC de surveillance, qui voit tout le trafic du segment
10.42.0.1/24 (étant lui-même la passerelle).

```bash
# Lancer Wireshark en capture sur eth0 (interface hotspot)
sudo wireshark -i eth0 -k

# Ou en ligne de commande avec tshark
sudo tshark -i eth0 -w captures/bruteforce_camera.pcapng

# Filtres appliqués pendant la capture
# Brute-force caméra :
#   ip.addr == 10.42.0.234 && http
# SYN Flood caméra :
#   ip.dst == 10.42.0.234 && tcp.flags.syn==1 && tcp.flags.ack==0
# Cryptojacking Pi :
#   ip.src == 10.42.0.241
# DoS Wi-Fi (sur interface wlan0 en mode monitor) :
#   wlan.fc.type == 0 && wlan.fc.subtype == 12
```

---

## Configuration de la caméra IP Hosafe HX-2PT1

La caméra ne dispose pas d'interface CLI — sa configuration réseau initiale
est réalisée via l'application mobile Hosafe, puis vérifiée en ligne de commande.

```bash
# Découverte de la caméra sur le réseau de labo
nmap -sn 10.42.0.0/24
# → Nmap scan report for 10.42.0.234  (Hosafe HX-2PT1)
#   Host is up (0.0012s latency).
#   MAC Address: XX:XX:XX:XX:XX:XX (Hosafe Technology)

# Scan des ports ouverts
nmap -sV 10.42.0.234
# → PORT   STATE SERVICE VERSION
# → 80/tcp open  http    HiPcam RealServer (caméra IP, interface admin)
# → 554/tcp open rtsp   RTSP flux vidéo

# Accéder à l'interface d'administration
# URL : http://10.42.0.234/   (puis http://192.168.137.41/ — alias IP secondaire)
# Auth : admin / [mot de passe par défaut non changé]

# Vérifier le flux RTSP
ffplay rtsp://admin:admin@10.42.0.234:554/stream1
# → décode et affiche le flux vidéo en direct
```

---

## Vérifications de connectivité inter-dispositifs

```bash
# Depuis le PC de surveillance — ping de tous les dispositifs
ping -c 2 10.42.0.234    # caméra
ping -c 2 10.42.0.241    # Pi
ping -c 2 10.42.0.11     # Kali

# Depuis Kali — confirmer l'accès SSH au Pi
ssh pi@10.42.0.241
# → pi@raspberrypi:~$   (accès obtenu avec mot de passe 123456)

# Depuis Kali — confirmer l'accès HTTP à la caméra
curl -u admin:test http://10.42.0.234/ -o /dev/null -w "%{http_code}\n"
# → 401  (caméra répond, auth par mot de passe)
```

---

## Résumé des services réseau exposés

| Dispositif | Port | Service | Vulnérabilité identifiée |
|-----------|------|---------|--------------------------|
| Caméra Hosafe | 80/tcp | HTTP (admin web) | Auth Basic sans HTTPS, pas de verrouillage de compte |
| Caméra Hosafe | 554/tcp | RTSP | Flux accessible après auth (admin:admin12345) |
| Raspberry Pi | 22/tcp | SSH | Mot de passe trivial (pi:123456), PasswordAuth activé |
| Raspberry Pi | — | Wi-Fi client | Sans 802.11w PMF → vulnérable aux trames deauth |

---

## Isolation du labo

Le réseau 10.42.0.0/24 est isolé du réseau de l'université par le pare-feu
du PC de surveillance. Seul le trafic nécessaire aux expériences (connexion
au pool de minage pour le cryptojacking) a été autorisé ponctuellement
via NAT sur le PC Ubuntu.

```bash
# Règle iptables activée pendant le test cryptojacking uniquement
sudo iptables -t nat -A POSTROUTING -s 10.42.0.0/24 -o wlan0 -j MASQUERADE
sudo sysctl -w net.ipv4.ip_forward=1

# Désactivée après le test
sudo iptables -t nat -D POSTROUTING -s 10.42.0.0/24 -o wlan0 -j MASQUERADE
```
