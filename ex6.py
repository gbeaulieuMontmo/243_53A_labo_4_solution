"""
Laboratoire 4 — Exercice 6 : console de communication complète (synthèse)
243-53A-MO — Interface usager de microcontrôleurs — Laboratoire 4

Objectif : une interface PySide6 simple qui réunit les notions du cours 7 :
  - choisir le port dans un QComboBox, puis se connecter / se déconnecter ;
  - afficher la dernière mesure reçue (QLabel + QProgressBar) ;
  - allumer / éteindre la LED de la carte (bouton à deux états, qui suit
    la réponse OK:LED:... de la carte) ;
  - envoyer une commande texte libre (ex. LED:ON) ;
  - garder un journal de tout ce qui est envoyé (→) et reçu (←).

Le port est lu par un QTimer (aucune attente : la fenêtre ne fige jamais),
la communication est encapsulée dans la classe LiaisonESP32, et les erreurs
(port occupé, câble débranché) sont signalées par un QMessageBox.

Organisation des fichiers :
  - ex6.py           : point d'entrée (lance l'application) ;
  - fenetre.py       : classe Fenetre (l'interface PySide6) ;
  - liaison_esp32.py : classe LiaisonESP32 (la communication série).

Matériel : l'ESP32-C3 Super Mini exécute le firmware de l'exercice 1 (src/main.cpp)
  (envoie TEMP:xxx chaque seconde ; obéit à LED:ON / LED:OFF et répond OK:...).
Préparation : pip install pyserial PySide6
Fermez le moniteur série de PlatformIO avant de connecter cette interface.

Programmeur : Guillaume Beaulieu
Date de création : 2026-09-21
Dernière modification : 2026-09-30
"""

import sys
from PySide6.QtWidgets import QApplication

from fenetre import Fenetre


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = Fenetre()
    fenetre.show()
    sys.exit(app.exec())
