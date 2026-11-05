# Montage matériel — Câblage du capteur de courant ACS712

> Guide de montage détaillé pour le dispositif de surveillance énergétique hors-bande
> utilisé lors des expériences du laboratoire UQAC 8INF917.

---

## Liste du matériel

| Composant | Modèle | Spécification |
|-----------|--------|---------------|
| Microcontrôleur | Arduino Uno | ATmega328P, 5V, CAN 10 bits |
| Capteur de courant | Module ACS712 | Plage 5A, sensibilité 185 mV/A |
| Caméra IP | Hosafe HX-2PT1 | Alimentation USB-C 5V/2A |
| Nano-ordinateur | Raspberry Pi 4 | Alimentation USB-C 5V/3A |
| PC de surveillance | Ubuntu 22.04 | Arduino IDE 2.3.7, Wireshark |
| Machine attaquante | Kali Linux | Hydra, hping3, aireplay-ng |

---

## Capteur ACS712 — Principe de fonctionnement

L'ACS712 est un capteur de courant à effet Hall. Il produit une tension proportionnelle
au courant traversant son conducteur :

```
Vsortie = Vcc/2 + (Sensibilité × I)
        = 2,5 V  + (0,185 V/A × I)    ← pour le module 5A

En réarrangeant :
  I = (Vsortie - 2,5 - BIAS) / 0,185
```

L'Arduino lit Vsortie sur la broche analogique A0 (0–1023 pas CAN pour 0–5V) :
```
Vsortie = lecture_CAN × (5,0 / 1023,0)
```

**BIAS = 0,007 V** a été mesuré empiriquement avec le dispositif ÉTEINT
(aucun courant ne circule), pour compenser le décalage continu du capteur.

---

## Schéma de câblage

<svg viewBox="0 0 760 400" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Schéma de câblage ACS712 : dispositif IoT vers capteur ACS712 en série sur le fil +5V, puis vers Arduino Uno sur A0, 5V et GND" style="max-width:100%;height:auto;background:#0d1117;border-radius:10px;display:block;">
  <defs>
    <marker id="a1" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <polygon points="0 0, 7 3, 0 6" fill="#58a6ff"/>
    </marker>
    <marker id="a-red" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <polygon points="0 0, 7 3, 0 6" fill="#f85149"/>
    </marker>
    <marker id="a-green" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <polygon points="0 0, 7 3, 0 6" fill="#3fb950"/>
    </marker>
    <marker id="a-yellow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <polygon points="0 0, 7 3, 0 6" fill="#e3b341"/>
    </marker>
    <filter id="glow2">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000" flood-opacity="0.5"/>
    </filter>
  </defs>

  <!-- ═══ DISPOSITIF IOT ═══ -->
  <rect x="20" y="130" width="155" height="130" rx="10" fill="#161b22" stroke="#f0883e" stroke-width="2" filter="url(#glow2)"/>
  <rect x="20" y="130" width="155" height="28" rx="10" fill="#3d2814"/>
  <rect x="20" y="148" width="155" height="10" fill="#3d2814"/>
  <text x="97" y="150" font-family="'Segoe UI',system-ui,sans-serif" font-size="12" font-weight="700" fill="#f0883e" text-anchor="middle">Dispositif IoT</text>
  <text x="97" y="172" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#c9d1d9" text-anchor="middle">Caméra / Raspberry Pi</text>
  <text x="97" y="188" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#8b949e" text-anchor="middle">Adaptateur USB-C 5V</text>
  <!-- Fil GND sortie en bas-gauche -->
  <rect x="30" y="206" width="135" height="20" rx="4" fill="#0d1117" stroke="#30363d" stroke-width="1"/>
  <text x="97" y="220" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#8b949e" text-anchor="middle">Fil GND (non interrompu)</text>
  <!-- Fil +5V sortie -->
  <rect x="30" y="232" width="135" height="20" rx="4" fill="#1a0000" stroke="#f85149" stroke-width="1"/>
  <text x="97" y="246" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#f85149" text-anchor="middle">Fil +5V  ─── [COUPÉ] →</text>

  <!-- ═══ ACS712 ═══ -->
  <rect x="285" y="90" width="190" height="210" rx="10" fill="#161b22" stroke="#58a6ff" stroke-width="2" filter="url(#glow2)"/>
  <rect x="285" y="90" width="190" height="28" rx="10" fill="#1f4b7c"/>
  <rect x="285" y="108" width="190" height="10" fill="#1f4b7c"/>
  <text x="380" y="110" font-family="'Segoe UI',system-ui,sans-serif" font-size="12" font-weight="700" fill="#58a6ff" text-anchor="middle">Module ACS712</text>
  <text x="380" y="130" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#8b949e" text-anchor="middle">Capteur effet Hall · plage 5A</text>
  <text x="380" y="146" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#8b949e" text-anchor="middle">185 mV/A · V_offset = 2,5V</text>

  <!-- Broches ACS712 -->
  <!-- IP+ -->
  <rect x="295" y="162" width="80" height="22" rx="5" fill="#1a0000" stroke="#f85149" stroke-width="1.5"/>
  <text x="335" y="177" font-family="'Segoe UI',system-ui,sans-serif" font-size="11" font-weight="700" fill="#f85149" text-anchor="middle">IP+</text>
  <!-- IP- -->
  <rect x="385" y="162" width="80" height="22" rx="5" fill="#1a0000" stroke="#f85149" stroke-width="1.5"/>
  <text x="425" y="177" font-family="'Segoe UI',system-ui,sans-serif" font-size="11" font-weight="700" fill="#f85149" text-anchor="middle">IP−</text>
  <text x="380" y="204" font-family="'Segoe UI',system-ui,sans-serif" font-size="9" fill="#8b949e" text-anchor="middle">Conducteur Hall-effect</text>
  <!-- VCC -->
  <rect x="295" y="218" width="80" height="22" rx="5" fill="#1a3d26" stroke="#3fb950" stroke-width="1.5"/>
  <text x="335" y="233" font-family="'Segoe UI',system-ui,sans-serif" font-size="11" font-weight="700" fill="#3fb950" text-anchor="middle">VCC</text>
  <!-- GND -->
  <rect x="295" y="248" width="80" height="22" rx="5" fill="#161b22" stroke="#8b949e" stroke-width="1.5"/>
  <text x="335" y="263" font-family="'Segoe UI',system-ui,sans-serif" font-size="11" font-weight="700" fill="#8b949e" text-anchor="middle">GND</text>
  <!-- OUT -->
  <rect x="295" y="278" width="80" height="22" rx="5" fill="#3d2e00" stroke="#e3b341" stroke-width="1.5"/>
  <text x="335" y="293" font-family="'Segoe UI',system-ui,sans-serif" font-size="11" font-weight="700" fill="#e3b341" text-anchor="middle">OUT</text>
  <text x="380" y="310" font-family="'Segoe UI',system-ui,sans-serif" font-size="9" fill="#8b949e" text-anchor="middle">Vsortie = 2,5V + 0,185·I</text>

  <!-- ═══ ARDUINO UNO ═══ -->
  <rect x="575" y="130" width="165" height="160" rx="10" fill="#161b22" stroke="#e3b341" stroke-width="2" filter="url(#glow2)"/>
  <rect x="575" y="130" width="165" height="28" rx="10" fill="#3d2e00"/>
  <rect x="575" y="148" width="165" height="10" fill="#3d2e00"/>
  <text x="657" y="150" font-family="'Segoe UI',system-ui,sans-serif" font-size="12" font-weight="700" fill="#e3b341" text-anchor="middle">Arduino Uno</text>
  <text x="657" y="170" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#8b949e" text-anchor="middle">ATmega328P · CAN 10 bits</text>

  <!-- Broches Arduino -->
  <!-- 5V -->
  <rect x="585" y="186" width="60" height="22" rx="5" fill="#1a3d26" stroke="#3fb950" stroke-width="1.5"/>
  <text x="615" y="201" font-family="'Segoe UI',system-ui,sans-serif" font-size="11" font-weight="700" fill="#3fb950" text-anchor="middle">5V</text>
  <!-- GND -->
  <rect x="585" y="216" width="60" height="22" rx="5" fill="#161b22" stroke="#8b949e" stroke-width="1.5"/>
  <text x="615" y="231" font-family="'Segoe UI',system-ui,sans-serif" font-size="11" font-weight="700" fill="#8b949e" text-anchor="middle">GND</text>
  <!-- A0 -->
  <rect x="585" y="246" width="60" height="22" rx="5" fill="#3d2e00" stroke="#e3b341" stroke-width="1.5"/>
  <text x="615" y="261" font-family="'Segoe UI',system-ui,sans-serif" font-size="11" font-weight="700" fill="#e3b341" text-anchor="middle">A0</text>

  <!-- USB label -->
  <rect x="593" y="276" width="130" height="22" rx="5" fill="#0d1117" stroke="#58a6ff" stroke-width="1.5"/>
  <text x="658" y="291" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#58a6ff" text-anchor="middle">USB → PC (9600 bd)</text>

  <!-- ═══════════ CONNEXIONS ═══════════ -->

  <!-- Fil +5V : IoT → IP+ (rouge, en série) -->
  <line x1="175" y1="242" x2="295" y2="173" stroke="#f85149" stroke-width="2" marker-end="url(#a-red)"/>
  <rect x="184" y="183" width="58" height="16" rx="4" fill="#0d1117"/>
  <text x="213" y="195" font-family="'Segoe UI',system-ui,sans-serif" font-size="9" fill="#f85149" text-anchor="middle">+5V fil coupé</text>

  <!-- IP- → IoT device (retour courant) -->
  <path d="M 465 173 Q 530 100 97 128" stroke="#f85149" stroke-width="2" fill="none" stroke-dasharray="5,3" marker-end="url(#a-red)"/>
  <rect x="510" y="92" width="82" height="16" rx="4" fill="#0d1117"/>
  <text x="551" y="104" font-family="'Segoe UI',system-ui,sans-serif" font-size="9" fill="#f85149" text-anchor="middle">retour IoT</text>

  <!-- GND IoT → GND Arduino (direct, bas) -->
  <path d="M 97 260 L 97 370 L 615 370 L 615 290" stroke="#8b949e" stroke-width="1.8" fill="none" marker-end="url(#a1)"/>
  <rect x="318" y="358" width="92" height="16" rx="4" fill="#0d1117"/>
  <text x="364" y="370" font-family="'Segoe UI',system-ui,sans-serif" font-size="9" fill="#8b949e" text-anchor="middle">GND commun</text>

  <!-- VCC → 5V Arduino (vert) -->
  <line x1="375" y1="229" x2="585" y2="197" stroke="#3fb950" stroke-width="1.8" marker-end="url(#a-green)"/>
  <rect x="440" y="207" width="60" height="16" rx="4" fill="#0d1117"/>
  <text x="470" y="219" font-family="'Segoe UI',system-ui,sans-serif" font-size="9" fill="#3fb950" text-anchor="middle">VCC → 5V</text>

  <!-- GND ACS712 → GND Arduino -->
  <line x1="375" y1="259" x2="585" y2="227" stroke="#8b949e" stroke-width="1.8" marker-end="url(#a1)"/>
  <rect x="440" y="237" width="80" height="16" rx="4" fill="#0d1117"/>
  <text x="480" y="249" font-family="'Segoe UI',system-ui,sans-serif" font-size="9" fill="#8b949e" text-anchor="middle">GND → GND</text>

  <!-- OUT → A0 Arduino (jaune) -->
  <line x1="375" y1="289" x2="585" y2="257" stroke="#e3b341" stroke-width="1.8" marker-end="url(#a-yellow)"/>
  <rect x="440" y="265" width="60" height="16" rx="4" fill="#0d1117"/>
  <text x="470" y="277" font-family="'Segoe UI',system-ui,sans-serif" font-size="9" fill="#e3b341" text-anchor="middle">OUT → A0</text>

  <!-- PC label at right -->
  <rect x="593" y="20" width="145" height="50" rx="8" fill="#161b22" stroke="#58a6ff" stroke-width="1.5"/>
  <text x="665" y="42" font-family="'Segoe UI',system-ui,sans-serif" font-size="11" font-weight="700" fill="#58a6ff" text-anchor="middle">PC Ubuntu</text>
  <text x="665" y="58" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#8b949e" text-anchor="middle">Arduino IDE · serial_logger.py</text>
  <line x1="658" y1="70" x2="658" y2="130" stroke="#58a6ff" stroke-width="1.8" stroke-dasharray="5,3" marker-end="url(#a1)"/>

  <!-- BIAS note -->
  <rect x="20" y="20" width="230" height="90" rx="8" fill="#161b22" stroke="#30363d" stroke-width="1"/>
  <text x="35" y="42" font-family="'Segoe UI',system-ui,sans-serif" font-size="11" font-weight="700" fill="#c9d1d9">Calibration BIAS</text>
  <text x="35" y="60" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#8b949e">Dispositif ÉTEINT → lecture ≠ 0 ?</text>
  <text x="35" y="76" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#e3b341">BIAS = valeur lue (ex: 0,007 V)</text>
  <text x="35" y="92" font-family="'Segoe UI',system-ui,sans-serif" font-size="10" fill="#8b949e">I = (Vsortie − 2,5 − BIAS) / 0,185</text>
</svg>

**Procédure de montage pas à pas :**

1. Couper le **fil positif** (+5V) du câble d'alimentation USB-C du dispositif IoT
2. Insérer le module ACS712 **en série** : extrémité dénudée côté alimentation → borne IP+,
   autre extrémité dénudée côté dispositif → borne IP–
3. Connecter l'alimentation du module ACS712 : VCC → 5V Arduino, GND → GND Arduino
4. Connecter la sortie ACS712 : OUT → A0 Arduino
5. Connecter l'Arduino au PC via USB
6. Téléverser `arduino/current_sensor.ino`
7. Ouvrir le Moniteur Série à **9600 bauds** pour vérifier les lectures

> ⚠️ Sécurité : intervenir uniquement sur des circuits **basse tension (5V USB)**.
> S'assurer que l'Arduino et le PC partagent la même masse GND que le dispositif surveillé.

---

## Procédure de calibration

Avant d'enregistrer des mesures, vérifier la valeur BIAS :

1. Débrancher le dispositif IoT (aucun courant ne traverse l'ACS712)
2. Ouvrir le Moniteur Série — observer les lectures
3. Lecture idéale sans courant : **0,000 A**
4. Si on lit par exemple `0,007 A`, régler `BIAS = 0,007` dans le sketch
5. Re-téléverser et vérifier que les lectures reviennent à ~0,000 A sans courant

Plage typique de BIAS : 0,005 – 0,015 V selon le module individuel.

---

## Protocole de mesure utilisé dans cette étude

Pour chaque scénario d'attaque, nous avons :

1. Laissé le dispositif atteindre l'**état stable** pendant 2 minutes avant l'enregistrement
2. Capturé **300 lectures série** (≈ 5 minutes à ~1 lecture/s)
3. Calculé min, moy, max et écart-type par scénario
4. Lancé les attaques **après** la capture de la ligne de base
5. Capturé 300 lectures supplémentaires pendant que l'attaque était active
6. Arrêté l'attaque et vérifié le retour à la consommation de base
