#include <Arduino.h>
/*
  Station ESP32-C3 Super Mini : mesures + commandes (programme complet)
  243-53A-MO — Interface usager de microcontrôleurs — Laboratoire 4

  Objectif : combiner les deux programmes du cours.
    - toutes les secondes, envoie une mesure :  TEMP:512
    - reçoit les commandes LED:ON et LED:OFF, allume ou éteint la LED,
      et répond OK:LED:ON ou OK:LED:OFF.

  Comme delay() bloquerait la lecture des commandes, on mesure le temps
  avec millis() : loop() ne s'arrête jamais.

  Programmeur : Guillaume Beaulieu
  Date de création : 2026-09-21
  Dernière modification : 2026-09-21
*/

#define PIN_CAPTEUR 0             // GPIO 0 : entrée analogique (ADC1)
#define PIN_LED 8                 // LED bleue intégrée
#define LED_ALLUMEE LOW           // logique inversée sur l'ESP32-C3 Super Mini
#define LED_ETEINTE HIGH
#define INTERVALLE_MS 1000

unsigned long derniereMesure = 0;

void setup() {
  Serial.begin(115200);
  pinMode(PIN_LED, OUTPUT);
  //DDRB |= (1 << PIN_LED);        // configure la broche de la LED comme sortie
  digitalWrite(PIN_LED, LED_ETEINTE);
  //PORTB |= (1 << PIN_LED);       // éteint la LED
}

void loop() {
  // 1) Commandes reçues du PC (une par ligne, terminée par \n).
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();                        // retire le \r
    cmd.toUpperCase();                 // pour être insensible à la casse

    if (cmd == "LED:ON") {
      digitalWrite(PIN_LED, LED_ALLUMEE);
      Serial.println("OK:LED:ON");
    } else if (cmd == "LED:OFF") {
      digitalWrite(PIN_LED, LED_ETEINTE);
      Serial.println("OK:LED:OFF");
    }
  }

  // 2) Une mesure par seconde, sans bloquer la lecture des commandes.
  if (millis() - derniereMesure >= INTERVALLE_MS) {
    derniereMesure = millis();
    Serial.print("TEMP:");
    Serial.println(random(0, 4095));
  }
}
