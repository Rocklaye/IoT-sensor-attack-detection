/*
 * Détection d'attaques sur capteurs IoT — Moniteur de courant ACS712
 * ===================================================================
 * Matériel : Arduino Uno (ATmega328P)
 *            Module capteur de courant ACS712 (plage 5A)
 *            Inséré en série sur le fil positif du câble d'alimentation
 *            du dispositif IoT surveillé (caméra IP ou Raspberry Pi)
 *
 * Sortie   : Lecture du courant en Ampères, affichée sur le port Série
 *            à 9600 bauds toutes les ~300 ms.
 *            Lisible en direct avec le Moniteur/Traceur Série de l'Arduino IDE
 *            ou journalisé en CSV via scripts/serial_logger.py
 *
 * Notes de calibration
 * --------------------
 *  BIAS      = décalage mesuré du capteur quand le dispositif est ÉTEINT (en volts)
 *  Vcc       = 5,0 V (alimentation USB depuis le PC)
 *  PAS_ADC   = 1023  (CAN 10 bits sur ATmega328P, plage 0–1023)
 *  Sensibilité du module ACS712 5A : 185 mV par Ampère
 *
 * Valeurs de référence mesurées (Hiver 2026, laboratoire UQAC)
 *  - Caméra en veille            : 0,08 – 0,10 A
 *  - Caméra streaming            : 0,21 – 0,25 A
 *  - Caméra brute-force HTTP     : 0,10 – 0,12 A
 *  - Caméra DoS inondation SYN   : 0,12 – 0,13 A
 *  - Raspberry Pi en veille      : 0,30 – 0,36 A
 *  - Raspberry Pi cryptojacking (XMRig) : 0,85 – 1,01 A
 *  - Raspberry Pi DoS Wi-Fi (deauth)    : 0,35 – 0,40 A
 *
 * Projet : 8INF917 — Sécurité IoT, UQAC
 * Auteurs : Abdoulaye Aw, Tchakouani N.E. Armandine,
 *           Fatimata Ndiaya Sall, Maha El Allem
 * Superviseur : Prof. Fehmi Jaafar
 */

// ── Configuration ────────────────────────────────────────────────────────────
#define BROCHE_CAPTEUR  A0      // Sortie ACS712 connectée à la broche analogique A0
#define NB_ECHANTILLONS 300     // Échantillons moyennés par lecture (réduction du bruit)
#define DELAI_ECHANT    3       // ms entre deux échantillons → total ~900 ms par lecture
#define VITESSE_SERIE   9600

#define VCC             5.0     // Tension d'alimentation (Volts)
#define PAS_ADC         1023.0  // Valeur maximale du CAN 10 bits
#define SENSIBILITE     0.185   // ACS712-5A : 185 mV par Ampère
#define VREF            2.5     // Sortie ACS712 à 0 A = Vcc/2
float   BIAS          = 0.007;  // Correction de décalage empirique (Volts)
                                 // Mesurer avec le dispositif ÉTEINT et ajuster si nécessaire

// ── Initialisation ───────────────────────────────────────────────────────────
void setup() {
  Serial.begin(VITESSE_SERIE);
  // Pause de chauffe — la sortie ACS712 se stabilise ~100 ms après la mise sous tension
  delay(500);
  Serial.println("# Moniteur de courant ACS712 — Laboratoire IoT UQAC");
  Serial.println("# Colonne : courant_A");
}

// ── Boucle principale ────────────────────────────────────────────────────────
void loop() {
  long somme_brute = 0;

  // Collecter NB_ECHANTILLONS lectures CAN et les sommer
  for (int i = 0; i < NB_ECHANTILLONS; i++) {
    somme_brute += analogRead(BROCHE_CAPTEUR);
    delay(DELAI_ECHANT);
  }

  // Convertir moyenne CAN → tension → courant
  float moy_adc  = somme_brute / (float)NB_ECHANTILLONS;
  float tension  = moy_adc * (VCC / PAS_ADC);
  float courant  = -(tension - VREF - BIAS) / SENSIBILITE;

  // abs() élimine l'ambiguïté de signe liée à l'orientation du capteur
  Serial.println(abs(courant), 3);   // ex. : "0.218"
}
