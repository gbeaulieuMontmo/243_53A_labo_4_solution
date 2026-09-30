"""
Laboratoire 4 — Exercice 2 : choix du port série avec QComboBox
243-53A-MO — Interface usager de microcontrôleurs — Cours 7

Objectif : première étape de la console ESP32-C3.
  - lister les ports série avec list_ports.comports() dans un QComboBox ;
  - conserver le nom du port (ex. COM5) comme donnée cachée de chaque élément ;
  - présélectionner la carte Espressif (VID 0x303A) ;
  - bouton « Actualiser » pour relire la liste.
Le bouton « Connecter » n'est pas encore fonctionnel (exercice 3).

Préparation : pip install pyserial PySide6

Programmeur : Guillaume Beaulieu
Date de création : 2026-09-28
Dernière modification : 2026-09-28
"""

import sys
from serial.tools import list_ports
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QComboBox, QPushButton, QLabel
)

VID_ESPRESSIF = 0x303A  # identifiant USB d'Espressif : sert à repérer la carte


class Fenetre(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Console ESP32-C3")
        self.resize(560, 150)

        # --- Groupe « Connexion » : choix du port ---
        self.combo_ports = QComboBox()
        self.btn_actualiser = QPushButton("Actualiser")
        self.btn_actualiser.clicked.connect(self.remplir_ports)
        self.btn_connecter = QPushButton("Connecter")
        self.btn_connecter.clicked.connect(self.afficher_choix)
        self.label_etat = QLabel("Non connecté")

        ligne_port = QHBoxLayout()
        ligne_port.addWidget(self.combo_ports, 1)
        ligne_port.addWidget(self.btn_actualiser)
        ligne_port.addWidget(self.btn_connecter)

        groupe_connexion = QGroupBox("Connexion")
        layout_connexion = QVBoxLayout(groupe_connexion)
        layout_connexion.addLayout(ligne_port)
        layout_connexion.addWidget(self.label_etat)

        conteneur = QWidget()
        layout = QVBoxLayout(conteneur)
        layout.addWidget(groupe_connexion)
        layout.addStretch()
        self.setCentralWidget(conteneur)

        self.remplir_ports()

    def remplir_ports(self):
        self.combo_ports.clear()
        for port in list_ports.comports():
            # Texte affiché : description ; donnée cachée : le nom du port.
            self.combo_ports.addItem(f"{port.device} — {port.description}", port.device)
            if port.vid == VID_ESPRESSIF:
                # Carte Espressif détectée : on la présélectionne.
                self.combo_ports.setCurrentIndex(self.combo_ports.count() - 1)

    def afficher_choix(self):
        # Pour l'instant, on affiche seulement le port choisi (currentData()).
        nom = self.combo_ports.currentData()
        self.label_etat.setText(f"Port choisi : {nom}" if nom else "Aucun port détecté")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = Fenetre()
    fenetre.show()
    sys.exit(app.exec())
