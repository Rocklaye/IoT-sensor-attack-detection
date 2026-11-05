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

<svg viewBox="0 0 820 540" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Topologie du réseau de laboratoire IoT — PC Ubuntu central connecté via Ethernet à Raspberry Pi, Caméra IP et Kali Linux, et via USB à l'Arduino" style="max-width:100%;height:auto;background:#0d1117;border-radius:10px;display:block;">
  <defs>
    <!-- Arrowhead marker -->
    <marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <polygon points="0 0, 7 3, 0 6" fill="#58a6ff"/>
    </marker>
    <marker id="arr-orange" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <polygon points="0 0, 7 3, 0 6" fill="#f0883e"/>
    </marker>
    <marker id="arr-green" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <polygon points="0 0, 7 3, 0 6" fill="#3fb950"/>
    </marker>
    <marker id="arr-purple" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <polygon points="0 0, 7 3, 0 6" fill="#bc8cff"/>
    </marker>
    <!-- Drop shadow filter -->
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000" flood-opacity="0.5"/>
    </filter>
  </defs>

  <!-- ═══ PC UBUNTU — centre/hub ═══ -->
  <rect x="280" y="20" width="260" height="100" rx="10" fill="#161b22" stroke="#58a6ff" stroke-width="2" filter="url(#glow)"/>
  <rect x="280" y="20" width="260" height="28" rx="10" fill="#1f4b7c"/>
  <rect x="280" y="38" width="260" height="10" fill="#1f4b7c"/>
  <text x="410" y="40" font-family="'Segoe UI',system-ui,sans-serif" font-size="12" font-weight="700" fill="#58a6ff" text-anchor="middle" letter-spacing="0.5">PC de surveillance</text>
  <text x="410" y="62" font-family="'Segoe UI',system-ui,sans-serif" font-size="11" fill="#c9d1d9" text-anchor="middle">Ubuntu 22.04 LTS</text>
  <text x="410" y="78" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#8b949e" text-anchor="middle">Wireshark · Arduino IDE 2.3.7</text>
  <text x="410" y="95" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#3fb950" text-anchor="middle">eth0 10.42.0.1 (hotspot) · wlan0 "shadow"</text>

  <!-- ═══ HOTSPOT DHCP badge ═══ -->
  <rect x="330" y="130" width="160" height="22" rx="6" fill="#161b22" stroke="#30363d" stroke-width="1"/>
  <text x="410" y="145" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#8b949e" text-anchor="middle">NetworkManager DHCP 10.42.0.1/24</text>

  <!-- ═══ Ethernet lines from PC to hub ═══ -->
  <!-- line center down to hub badge -->
  <line x1="410" y1="120" x2="410" y2="130" stroke="#58a6ff" stroke-width="1.5" stroke-dasharray="4,3"/>

  <!-- ═══ RASPBERRY PI ═══ -->
  <rect x="80" y="230" width="195" height="100" rx="10" fill="#161b22" stroke="#3fb950" stroke-width="2" filter="url(#glow)"/>
  <rect x="80" y="230" width="195" height="28" rx="10" fill="#1a3d26"/>
  <rect x="80" y="248" width="195" height="10" fill="#1a3d26"/>
  <text x="177" y="250" font-family="'Segoe UI',system-ui,sans-serif" font-size="12" font-weight="700" fill="#3fb950" text-anchor="middle">Raspberry Pi 4</text>
  <text x="177" y="270" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#c9d1d9" text-anchor="middle">Debian Bookworm · SSH :22</text>
  <text x="177" y="286" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#8b949e" text-anchor="middle">eth0 · 10.42.0.241</text>
  <text x="177" y="301" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#8b949e" text-anchor="middle">wlan0 · réseau "shadow"</text>
  <text x="177" y="317" font-family="'Segoe UI',system-ui,sans-serif" font-size="9" fill="#f85149" text-anchor="middle">pi:123456 (intentionnel)</text>

  <!-- ═══ CAMERA IP ═══ -->
  <rect x="313" y="310" width="195" height="110" rx="10" fill="#161b22" stroke="#f0883e" stroke-width="2" filter="url(#glow)"/>
  <rect x="313" y="310" width="195" height="28" rx="10" fill="#3d2814"/>
  <rect x="313" y="328" width="195" height="10" fill="#3d2814"/>
  <text x="410" y="330" font-family="'Segoe UI',system-ui,sans-serif" font-size="12" font-weight="700" fill="#f0883e" text-anchor="middle">Caméra IP Hosafe HX-2PT1</text>
  <text x="410" y="352" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#c9d1d9" text-anchor="middle">Wi-Fi "shadow" · HTTP :80 · RTSP :554</text>
  <text x="410" y="368" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#8b949e" text-anchor="middle">10.42.0.234 (wlan)</text>
  <text x="410" y="384" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#8b949e" text-anchor="middle">192.168.137.41 (alias admin)</text>
  <text x="410" y="400" font-family="'Segoe UI',system-ui,sans-serif" font-size="9" fill="#f85149" text-anchor="middle">Auth Basic HTTP en clair</text>
  <text x="410" y="413" font-family="'Segoe UI',system-ui,sans-serif" font-size="9" fill="#f85149" text-anchor="middle">Pas de verrouillage de compte</text>

  <!-- ═══ KALI LINUX ═══ -->
  <rect x="545" y="230" width="195" height="100" rx="10" fill="#161b22" stroke="#bc8cff" stroke-width="2" filter="url(#glow)"/>
  <rect x="545" y="230" width="195" height="28" rx="10" fill="#2d1f4a"/>
  <rect x="545" y="248" width="195" height="10" fill="#2d1f4a"/>
  <text x="642" y="250" font-family="'Segoe UI',system-ui,sans-serif" font-size="12" font-weight="700" fill="#bc8cff" text-anchor="middle">Kali Linux</text>
  <text x="642" y="270" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#c9d1d9" text-anchor="middle">Hydra · hping3 · aireplay-ng</text>
  <text x="642" y="286" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#8b949e" text-anchor="middle">eth0 · 10.42.0.11</text>
  <text x="642" y="301" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#8b949e" text-anchor="middle">wlan1 · Alfa AWUS036ACS</text>
  <text x="642" y="317" font-family="'Segoe UI',system-ui,sans-serif" font-size="9" fill="#bc8cff" text-anchor="middle">Attaquant</text>

  <!-- ═══ ARDUINO ═══ -->
  <rect x="600" y="380" width="185" height="80" rx="10" fill="#161b22" stroke="#e3b341" stroke-width="2" filter="url(#glow)"/>
  <rect x="600" y="380" width="185" height="26" rx="10" fill="#3d2e00"/>
  <rect x="600" y="396" width="185" height="10" fill="#3d2e00"/>
  <text x="692" y="398" font-family="'Segoe UI',system-ui,sans-serif" font-size="12" font-weight="700" fill="#e3b341" text-anchor="middle">Arduino Uno</text>
  <text x="692" y="418" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#c9d1d9" text-anchor="middle">ACS712 · /dev/ttyACM0</text>
  <text x="692" y="434" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#8b949e" text-anchor="middle">9600 bauds · mesure courant</text>
  <text x="692" y="450" font-family="'Segoe UI',system-ui,sans-serif" font-size="9" fill="#e3b341" text-anchor="middle">USB série vers PC</text>

  <!-- ═══ POOL MINAGE ═══ -->
  <rect x="80" y="390" width="175" height="60" rx="10" fill="#161b22" stroke="#f85149" stroke-width="1.5" stroke-dasharray="6,3"/>
  <text x="167" y="413" font-family="'Segoe UI',system-ui,sans-serif" font-size="11" font-weight="700" fill="#f85149" text-anchor="middle">Pool minage XMR</text>
  <text x="167" y="430" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#8b949e" text-anchor="middle">rx.unmineable.com</text>
  <text x="167" y="445" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#8b949e" text-anchor="middle">209.38.61.60 (externe)</text>

  <!-- ═══ WI-FI AP "shadow" ═══ -->
  <ellipse cx="410" cy="500" rx="130" ry="25" fill="#161b22" stroke="#58a6ff" stroke-width="1.5" stroke-dasharray="5,3"/>
  <text x="410" y="497" font-family="'Segoe UI',system-ui,sans-serif" font-size="11" font-weight="600" fill="#58a6ff" text-anchor="middle">Wi-Fi "shadow"</text>
  <text x="410" y="511" font-family="'Segoe UI',system-ui,sans-serif" font-size="9" fill="#8b949e" text-anchor="middle">BSSID 10:68:38:B2:58:EB · ch.6 · WPA2</text>

  <!-- ═══════════ CONNEXIONS ═══════════ -->

  <!-- PC → Raspberry Pi : Ethernet hotspot -->
  <line x1="280" y1="85" x2="177" y2="230" stroke="#3fb950" stroke-width="1.8" marker-end="url(#arr-green)"/>
  <rect x="168" y="145" width="90" height="18" rx="4" fill="#0d1117"/>
  <text x="213" y="158" font-family="'Segoe UI',system-ui,sans-serif" font-size="9" fill="#3fb950" text-anchor="middle">Ethernet</text>

  <!-- PC → Kali : Ethernet hotspot -->
  <line x1="540" y1="85" x2="642" y2="230" stroke="#bc8cff" stroke-width="1.8" marker-end="url(#arr-purple)"/>
  <rect x="560" y="143" width="90" height="18" rx="4" fill="#0d1117"/>
  <text x="605" y="156" font-family="'Segoe UI',system-ui,sans-serif" font-size="9" fill="#bc8cff" text-anchor="middle">Ethernet</text>

  <!-- PC → Arduino : USB -->
  <line x1="540" y1="70" x2="692" y2="380" stroke="#e3b341" stroke-width="1.8" stroke-dasharray="6,3" marker-end="url(#arr)"/>
  <rect x="638" y="195" width="60" height="18" rx="4" fill="#0d1117"/>
  <text x="668" y="208" font-family="'Segoe UI',system-ui,sans-serif" font-size="9" fill="#e3b341" text-anchor="middle">USB série</text>

  <!-- Raspberry Pi → Wi-Fi AP -->
  <line x1="220" y1="330" x2="310" y2="492" stroke="#58a6ff" stroke-width="1.5" stroke-dasharray="5,3" marker-end="url(#arr)"/>

  <!-- Caméra IP → Wi-Fi AP -->
  <line x1="410" y1="420" x2="410" y2="475" stroke="#f0883e" stroke-width="1.8" stroke-dasharray="5,3" marker-end="url(#arr-orange)"/>
  <rect x="415" y="443" width="68" height="16" rx="4" fill="#0d1117"/>
  <text x="449" y="455" font-family="'Segoe UI',system-ui,sans-serif" font-size="9" fill="#f0883e" text-anchor="middle">Wi-Fi 802.11n</text>

  <!-- Raspberry Pi → Pool minage (NAT) -->
  <line x1="130" y1="330" x2="130" y2="390" stroke="#f85149" stroke-width="1.5" stroke-dasharray="4,4" marker-end="url(#arr)"/>
  <rect x="60" y="355" width="130" height="16" rx="4" fill="#0d1117"/>
  <text x="125" y="367" font-family="'Segoe UI',system-ui,sans-serif" font-size="9" fill="#f85149" text-anchor="middle">XMRig (NAT ponctuel)</text>

  <!-- Kali wlan1 → Wi-Fi AP deauth -->
  <line x1="600" y1="330" x2="510" y2="490" stroke="#bc8cff" stroke-width="1.5" stroke-dasharray="5,3" marker-end="url(#arr-purple)"/>
  <rect x="535" y="395" width="85" height="16" rx="4" fill="#0d1117"/>
  <text x="577" y="407" font-family="'Segoe UI',system-ui,sans-serif" font-size="9" fill="#bc8cff" text-anchor="middle">deauth flood</text>

  <!-- Wireshark capture label on eth0 line -->
  <rect x="232" y="118" width="88" height="16" rx="4" fill="#1f4b7c"/>
  <text x="276" y="130" font-family="'Segoe UI',system-ui,sans-serif" font-size="9" fill="#58a6ff" text-anchor="middle">Wireshark eth0</text>

  <!-- PC wlan0 → Wi-Fi AP badge -->
  <line x1="410" y1="120" x2="410" y2="475" stroke="#58a6ff" stroke-width="1" stroke-dasharray="3,5" opacity="0.4"/>

  <!-- Légende -->
  <rect x="22" y="22" width="230" height="130" rx="8" fill="#161b22" stroke="#30363d" stroke-width="1"/>
  <text x="35" y="42" font-family="'Segoe UI',system-ui,sans-serif" font-size="11" font-weight="700" fill="#c9d1d9">Légende</text>
  <line x1="35" y1="58" x2="65" y2="58" stroke="#3fb950" stroke-width="2"/>
  <text x="72" y="62" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#8b949e">Ethernet filaire</text>
  <line x1="35" y1="78" x2="65" y2="78" stroke="#f0883e" stroke-width="2" stroke-dasharray="5,3"/>
  <text x="72" y="82" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#8b949e">Wi-Fi 802.11n</text>
  <line x1="35" y1="98" x2="65" y2="98" stroke="#e3b341" stroke-width="2" stroke-dasharray="6,3"/>
  <text x="72" y="102" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#8b949e">USB série</text>
  <line x1="35" y1="118" x2="65" y2="118" stroke="#f85149" stroke-width="1.5" stroke-dasharray="4,4"/>
  <text x="72" y="122" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#8b949e">NAT ponctuel (XMRig)</text>
  <line x1="35" y1="138" x2="65" y2="138" stroke="#bc8cff" stroke-width="1.5" stroke-dasharray="5,3"/>
  <text x="72" y="142" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#8b949e">Attaque Wi-Fi (deauth)</text>
</svg>

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
