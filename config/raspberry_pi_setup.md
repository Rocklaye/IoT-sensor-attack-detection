# Configuration du Raspberry Pi — Environnement de laboratoire

> Documentation de la mise en place système du Raspberry Pi utilisé comme
> dispositif IoT victime dans les expériences UQAC 8INF917 (Hiver 2026).
>
> Cette configuration a été réalisée manuellement avant chaque campagne
> d'attaque afin de reproduire un déploiement IoT réaliste mais volontairement
> sous-sécurisé.

---

## Matériel

| Composant | Détail |
|-----------|--------|
| Modèle | Raspberry Pi 4 Model B |
| RAM | 1,80 Go (détectée via htop) |
| Stockage | Carte microSD SanDisk Ultra 32 Go |
| Alimentation | USB-C 5V / 3A |
| Connectivité | Wi-Fi intégré 802.11ac + Ethernet (eth0) |
| Adaptateur Wi-Fi attaquant | Alfa AWUS036ACS (RTL8812AU) — sur machine Kali |

---

## Système d'exploitation

```
Système    : Debian GNU/Linux 12 (Bookworm) — Raspberry Pi OS 64 bits
Noyau      : Linux 6.12.x (aarch64)
Uptime     : ~57 mins (lors des expériences)
Résolution : 1920×1080 (sortie HDMI)
Thème      : PiXFlat (GTK3)
Terminal   : x-terminal-emulator
CPU        : 4 cœurs ARM Cortex-A72 @ 1 800 MHz
Mémoire    : ~442 Mo / 1 849 Mo au repos
```

> Source : capture neofetch réalisée en début de session d'expérimentation.

### Installation initiale

```bash
# 1. Flasher l'image sur carte microSD (depuis la machine de surveillance)
#    Outil : Raspberry Pi Imager 1.8.x
#    Image : Raspberry Pi OS (64-bit) Bookworm — version sans bureau optionnelle,
#            mais bureau activé ici pour faciliter l'observation via HDMI

# 2. Premier démarrage — configuration initiale via raspi-config
sudo raspi-config
#   → Localisation : fr_CA.UTF-8
#   → Timezone     : America/Toronto
#   → Hostname     : raspberrypi
#   → Mot de passe : [intentionnellement faible pour les tests — voir section SSH]
```

---

## Configuration réseau

### Interfaces actives

```
eth0   : IP statique 10.42.0.241 / 24  (réseau de labo — hotspot PC de surveillance)
wlan0  : connecté au réseau Wi-Fi "shadow"  BSSID 10:68:38:B2:58:EB  canal 6
         IP DHCP attribuée par le point d'accès
```

### Configuration eth0 (IP statique)

Le Pi est connecté en Ethernet au PC Ubuntu 22.04 qui partage sa connexion via
NetworkManager (hotspot filaire). L'adresse 10.42.0.241 est attribuée par le
serveur DHCP de NetworkManager (`dnsmasq` intégré, plage 10.42.0.1/24).

```bash
# Vérification de l'adresse sur le Pi
ip addr show eth0
# → inet 10.42.0.241/24  brd 10.42.0.255  scope global dynamic eth0

# Table de routage
ip route
# → default via 10.42.0.1 dev eth0
# → 10.42.0.0/24 dev eth0 proto kernel scope link
```

### Configuration wlan0 (Wi-Fi "shadow")

```bash
# Connexion au réseau Wi-Fi de test via nmcli
sudo nmcli device wifi connect "shadow" password "<mot_de_passe_labo>"

# Vérification
nmcli connection show
# → shadow  <uuid>  802-11-wireless  wlan0

iwconfig wlan0
# → ESSID:"shadow"
# → Access Point: 10:68:38:B2:58:EB
# → Frequency:2.437 GHz  (Canal 6)
# → Bit Rate=54 Mb/s
```

---

## Service SSH — Configuration intentionnellement vulnérable

> ⚠️ **Environnement de laboratoire uniquement** — ces paramètres ne doivent
> jamais être appliqués en production.

SSH a été activé et configuré avec des paramètres délibérément faibles pour
permettre la simulation de compromission par force brute.

```bash
# Activation de SSH
sudo systemctl enable ssh
sudo systemctl start ssh

# Vérification du statut
sudo systemctl status ssh
# → Active: active (running)
```

### `/etc/ssh/sshd_config` — extraits pertinents

```
Port 22
PermitRootLogin no
PasswordAuthentication yes          # ← autorise l'auth par mot de passe
PubkeyAuthentication yes
MaxAuthTries 6                      # ← pas de limitation agressive
LoginGraceTime 2m
```

### Mot de passe utilisateur `pi` (labo)

```
Utilisateur : pi
Mot de passe : 123456               # ← intentionnellement trivial (test)
```

Ce mot de passe volontairement faible reproduit le comportement de nombreux
appareils IoT déployés sans changement des identifiants par défaut — cible
principale de l'attaque par cryptojacking simulée.

---

## Outils installés sur le Pi

```bash
# Mise à jour système (commande exécutée au début de chaque session)
sudo apt-get update && sudo apt-get upgrade -y

# Outils de surveillance système (observateurs côté victime)
sudo apt-get install -y htop net-tools tcpdump

# Dépendances installées par le script d'attaque cryptojacking (post-compromission)
sudo apt-get install -y build-essential cmake libssl-dev libhwloc-dev
```

---

## Vérifications pré-expérience

Avant chaque scénario d'attaque, les points suivants étaient confirmés :

```bash
# 1. Connectivité réseau
ping -c 3 10.42.0.1          # joindre le PC de surveillance
ping -c 3 10.42.0.234        # joindre la caméra IP

# 2. SSH accessible depuis Kali
#    (testé depuis la machine attaquante)
#    ssh pi@10.42.0.241

# 3. Consommation électrique de référence (état veille stable)
#    → enregistrer 300 échantillons via capteur ACS712 avant l'attaque
#    → confirmer ~0,30 A au repos

# 4. Aucun processus inhabituel
ps aux | grep -v "^pi\|^root\|^www"
htop  # → charge CPU < 5 % en veille
```

---

## Service systemd créé par l'attaque cryptojacking

> Cette section documente l'artefact laissé par l'attaque — utile pour
> comprendre les indicateurs de compromission (IoC) à surveiller.

```bash
# Service créé par le script crytojacking2.sh (post-compromission)
cat /etc/systemd/system/system_update_daemon.service
```

```ini
[Unit]
Description=System Update Daemon

[Service]
ExecStart=/usr/local/bin/system-update-daemon --config /etc/systemd/update.json
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Binaire réel : XMRig renommé pour ressembler à un service système
ls -la /usr/local/bin/system-update-daemon
# → -rwxr-xr-x  1 root root  3,2M  /usr/local/bin/system-update-daemon

# Détection de la compromission
sudo systemctl list-units | grep daemon
# → system_update_daemon.service  active running

# Nettoyage post-expérience
sudo systemctl stop system_update_daemon
sudo systemctl disable system_update_daemon
sudo rm /etc/systemd/system/system_update_daemon.service
sudo rm /usr/local/bin/system-update-daemon
sudo systemctl daemon-reload
```
