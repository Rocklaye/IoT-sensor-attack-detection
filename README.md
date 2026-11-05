# Détection d'attaques sur capteurs IoT — Analyse énergétique et trafic réseau

> **Mots-clés :** sécurité IoT · capteurs connectés · bâtiment intelligent · Linux embarqué · surveillance réseau · détection d'anomalies  
> **Projet académique** — 8INF917 Sécurité IoT | UQAC (Hiver 2026)  
> **Auteurs :** Abdoulaye Aw, Tchakouani Noukam E. Armandine, Fatimata Ndiaya Sall, Maha El Allem  
> **Superviseur :** Prof. Fehmi Jaafar

---

## Contexte et motivation

Les bâtiments intelligents et infrastructures IoT reposent sur des dizaines de capteurs connectés en permanence — caméras IP, capteurs environnementaux, passerelles Linux embarquées — rarement surveillés pour détecter des anomalies de sécurité. Les agents de sécurité classiques ne peuvent pas être installés sur ces dispositifs contraints.

Ce projet répond à une question concrète : **peut-on détecter des cyberattaques sur des capteurs IoT passivement, sans toucher au dispositif lui-même ?**

Nous avons surveillé deux signaux indépendants hors-bande pendant des attaques réelles :

1. **Consommation électrique** — mesurée en temps réel avec un capteur de courant ACS712 câblé sur un Arduino Uno, inséré en série sur le câble d'alimentation du dispositif
2. **Trafic réseau** — capturé et analysé avec Wireshark sur une machine Ubuntu de surveillance connectée au même segment réseau

L'hypothèse : les attaques laissent des empreintes mesurables dans la consommation électrique **et** le comportement réseau d'un capteur ciblé — détectables depuis la couche infrastructure, sans déployer d'agent sur le dispositif.

**Dispositifs testés :**
| Dispositif | Rôle | Surface d'attaque |
|---|---|---|
| Caméra IP Hosafe HX-2PT1 | Cible principale (capteur connecté) | Interface web HTTP, flux vidéo RTSP, absence de limitation de taux |
| Raspberry Pi 4 (Raspberry Pi OS) | Cible secondaire (passerelle Linux embarquée) | SSH (port 22), services exposés |

---

## Montage matériel

```
[Dispositif IoT] ──── [Capteur ACS712] ──── [Arduino Uno] ──── USB ──── [PC Ubuntu]
       │                                                                       │
       └──────────────────── LAN (Wi-Fi / Ethernet) ──────────── [Capture Wireshark]
```

**Matériel utilisé :**
- Arduino Uno (ATmega328P)
- Module capteur ACS712 (plage 5A)
- Caméra IP Hosafe HX-2PT1 (Wi-Fi, firmware V21.1.34.11.18-20220125)
- Raspberry Pi 4 (Debian Bookworm, noyau 6.12)
- Machine attaquante Kali Linux (Hydra, hping3, XMRig)
- Machine de surveillance Ubuntu (Wireshark, Arduino IDE 2.3.7)

**Câblage :** Le câble d'alimentation de chaque dispositif IoT a été coupé et l'ACS712 inséré **en série sur le fil positif**, mesurant le courant instantané via la broche analogique A0 de l'Arduino.

> 📐 Guide complet : [`docs/hardware_setup.md`](docs/hardware_setup.md)

---

## Infrastructure réseau du laboratoire

Le réseau de laboratoire a été monté et configuré manuellement pour isoler les expériences et contrôler tous les flux.

```
PC Ubuntu (10.42.0.1) ── hotspot Ethernet ── Raspberry Pi (10.42.0.241)
                     \\                   └── Caméra IP   (10.42.0.234)
                      \\                  └── Kali Linux  (10.42.0.11)
                       └── Wi-Fi "shadow" ── Caméra IP (192.168.137.41)
                            (BSSID 10:68:38:B2:58:EB, canal 6)
                                        └── Raspberry Pi (wlan0, déauth tests)
```

**Configuration réalisée manuellement :**
- Hotspot filaire Ubuntu via NetworkManager (DHCP `dnsmasq`, plage `10.42.0.1/24`)
- Réseau Wi-Fi isolé "shadow" pour connecter la caméra (Wi-Fi uniquement) et tester les attaques 802.11
- Raspberry Pi 4 sous Debian Bookworm — SSH activé, interfaces eth0 + wlan0 configurées
- Wireshark en capture sur `eth0` depuis la passerelle (voit tout le trafic du segment)
- NAT activé ponctuellement pour le test cryptojacking (accès pool de minage externe)
- Arduino Uno connecté via USB — port série `/dev/ttyACM0` lu par `serial_logger.py`

> 📋 Topologie détaillée et commandes : [`config/lab_network.md`](config/lab_network.md)  
> 🖥️ Configuration OS du Pi (Bookworm, SSH, services) : [`config/raspberry_pi_setup.md`](config/raspberry_pi_setup.md)

---

## Sketch Arduino — Mesure de courant

```cpp
float BIAS = 0.007;  // Décalage de calibration en volts

void setup() {
  Serial.begin(9600);
}

void loop() {
  long echantillons = 0;
  for (int i = 0; i < 300; i++) {
    echantillons += analogRead(A0);
    delay(3);
  }
  float tension   = (echantillons / 300.0) * (5.0 / 1023.0);
  float courant   = -(tension - 2.5 - BIAS) / 0.185;  // Sensibilité ACS712 : 185 mV/A
  Serial.println(abs(courant));
}
```

Les données sont lues depuis le port série de l'Arduino (9600 bauds) et tracées en direct dans le Serial Plotter de l'Arduino IDE.

---

## Résultats — Graphique de consommation énergétique

![Comparaison de la consommation selon les scénarios d'attaque](docs/energy_comparison.png)

> Généré depuis les mesures réelles avec `scripts/plot_energy.py`. Point clé :
> le cryptojacking sur le Raspberry Pi produit un **pic énergétique de +200%**
> détectable depuis l'infrastructure. La caméra IP montre des variations plus subtiles —
> **l'analyse réseau est le canal de détection principal** pour le brute-force et le DoS.

---

## Expériences et résultats

### Cible 1 — Caméra IP Hosafe

Quatre états de fonctionnement mesurés et comparés :

| État | Description | Courant moy. (A) | Courant max (A) | Observation clé |
|---|---|---|---|---|
| **É1 — Veille** | Caméra allumée, Wi-Fi connecté, aucun spectateur | ~0,08 | ~0,10 | Minimal : keepalive Wi-Fi uniquement |
| **É2 — Utilisation normale** | Client en train de visionner le flux RTSP/HTTP | ~0,21 | ~0,25 | +160% vs veille : encodage vidéo + TX Wi-Fi |
| **É3 — Brute-force** | Hydra HTTP-GET, attaque par dictionnaire | ~0,10 | ~0,12 | +20% vs veille : CPU traite les requêtes d'authentification |
| **É4 — DoS (inondation SYN)** | hping3 `-i u1000` sur le port 80 | ~0,12 | ~0,13 | +30% vs veille : pile réseau saturée |

**Méthodologie — Brute-force :**
```bash
# Étape 1 : générer un dictionnaire avec Crunch (500 mots de passe, 4-9 caractères)
crunch 4 9 abc123 -c 500 -o dictionnaire.txt

# Étape 2 : attaque monothread avec délai pour éviter les faux positifs
hydra -l admin -P dictionnaire.txt -t 1 -W 2 192.168.2.39 http-get /
# Résultat : mot de passe "admin12345" trouvé — aucun mécanisme de verrouillage
```

**Méthodologie — DoS :**
```bash
# Inondation SYN à 1000 paquets par seconde
hping3 192.168.137.41 -S -p 80 -i u1000
# Résultat : 80073 paquets envoyés, flux vidéo gelé, interface admin inaccessible
```

**Analyse réseau (Wireshark) :**
- Brute-force : répétition de `GET / HTTP/1.1` avec en-têtes `Authorization: Basic`, identifiants encodés en Base64 visibles en clair — aucun HTTPS
- DoS : avalanche de paquets SYN verts depuis l'IP attaquant, alertes "TCP Port numbers reused", serveur épuisant sa table de connexions

---

### Cible 2 — Raspberry Pi 4

| Attaque | Description | Signature énergétique | Signature réseau |
|---|---|---|---|
| **Cryptojacking** | XMRig minage Monero (build ARM) | Charge CPU soutenue → pic de courant significatif (+200%) | Connexions sortantes persistantes vers le pool de minage |
| **DoS Wi-Fi** | Inondation Deauth ciblant le Wi-Fi du Pi | Légère hausse liée aux tentatives de reconnexion | Trames d'association/désassociation répétées |

**Méthodologie — Cryptojacking :**
```bash
# Après brute-force SSH (mot de passe "123456" trouvé pour l'utilisateur "pi")
# Script de post-exploitation déployé sur le Pi :
apt-get update && apt-get install -y build-essential cmake libssl-dev
# XMRig compilé pour ARM, configuré pour miner XMR vers le portefeuille attaquant
# Service systemd nommé "system_update_daemon" pour la persistance
# Minage silencieux en arrière-plan — 100% CPU sur tous les cœurs
```

---

## Résultats clés

1. **La consommation énergétique seule est insuffisante** comme signal de détection pour la caméra IP : la différence entre le streaming normal (~0,21 A) et un brute-force actif (~0,10 A) est **inversée** — le streaming consomme plus que l'attaque. Un seuil énergétique naïf génèrerait des faux négatifs. Ce point est critique pour les déploiements en bâtiment intelligent où les caméras alimentées par PoE sont supposées « saines » tant qu'elles consomment de l'énergie.

2. **L'analyse réseau est le signal primaire le plus fiable** — les captures Wireshark distinguent sans ambiguïté les patterns d'attaque (floods HTTP 401, tempêtes SYN) du trafic normal. Sur un réseau de bâtiment, cette analyse peut tourner sur le switch principal via un port SPAN dédié sur le VLAN de surveillance.

3. **La corrélation capteur + réseau est l'approche la plus robuste** : pattern réseau anormal + pic énergétique corrélé → détection d'attaque à haute confiance, réduction des faux positifs. Cette approche double-signal est déployable sur n'importe quelle infrastructure IoT PoE sans agent sur l'endpoint.

4. **Les caméras connectées transmettent les identifiants en clair via HTTP** (encodés Base64, non chiffrés). N'importe quel dispositif sur le même segment réseau — y compris d'autres capteurs IoT compromis — peut les intercepter directement dans une capture réseau.

5. **Aucun mécanisme de limitation ou de verrouillage de compte** sur l'interface d'administration web de la caméra : un attaquant peut tester des milliers de mots de passe par minute depuis n'importe quel point du même VLAN.

---

## Outils utilisés

| Outil | Version | Usage |
|---|---|---|
| Arduino IDE | 2.3.7 | Téléversement du sketch + Serial Plotter |
| Wireshark | — | Capture et analyse réseau |
| Hydra | v9.6 | Brute-force HTTP |
| hping3 | — | DoS par inondation SYN |
| Crunch | — | Génération de dictionnaire |
| XMRig | — | Simulation de cryptojacking |
| Kali Linux | — | Plateforme d'attaque |

---

## Structure du dépôt

```
iot-sensor-attack-detection/
├── arduino/
│   └── current_sensor.ino          # Sketch Arduino (lecteur ACS712)
├── scripts/
│   ├── serial_logger.py        # Journalisation port série Arduino → CSV
│   ├── traffic_analyzer.py          # Détection de patterns d'attaque dans .pcap (scapy)
│   └── plot_energy.py            # Génération du graphique de comparaison énergétique
├── config/                   # ← Configuration matérielle, réseau et OS
│   ├── lab_network.md               # Topologie réseau, plan IP, hotspot, Wi-Fi "shadow"
│   └── raspberry_pi.md              # OS Debian Bookworm, SSH, interfaces réseau, services
├── data/
│   ├── measurements_summary.csv           # Résultats agrégés (tous les scénarios)
│   ├── energy_camera.csv           # Lectures brutes — caméra IP
│   └── energy_pi.csv               # Lectures brutes — Raspberry Pi
├── docs/
│   ├── attack_signatures.md       # Référence : attaque → signature énergie + réseau
│   ├── hardware_setup.md          # Schéma de câblage ACS712 + guide de calibration
│   └── energy_comparison.png      # Graphique généré
├── captures/
│   └── README.md                    # Inventaire des captures + filtres Wireshark
└── README.md
```

---

## Contexte académique

Ce projet a été réalisé en contexte academique. L'environnement expérimental était isolé (réseau privé, aucun dispositif exposé sur Internet) et toutes les attaques ont été effectuées à des fins pédagogiques uniquement.

---

## Références

- Fiche technique ACS712 — Allegro MicroSystems
- Documentation Wireshark — https://www.wireshark.org/docs/
- THC Hydra — https://github.com/vanhauser-thc/thc-hydra
- Manuel hping3 — http://www.hping.org/
