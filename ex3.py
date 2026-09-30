"""
Laboratoire 4 — Exercice 3 : connexion et déconnexion (classe LiaisonESP32)
243-53A-MO — Interface usager de microcontrôleurs — Cours 7

Objectif : ajouter à l'exercice 2 l'ouverture et la fermeture du port.
  - ouvrir_port() ouvre le port sans redémarrer l'ESP32-C3 (DTR/RTS à False) ;
  - la classe LiaisonESP32 encapsule le port série ;
  - le bouton « Connecter » devient un bouton bascule ;
  - les erreurs d'ouverture sont signalées par un QMessageBox ;
  - le port est fermé à la fermeture de la fenêtre (closeEvent).

Préparation : pip install pyserial PySide6
Fermez le moniteur série de PlatformIO avant de connecter cette interface.

Programmeur : Guillaume Beaulieu
Date de création : 2026-09-28
Dernière modification : 2026-09-28
"""

import sys
import serial
from serial.tools import list_ports
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QComboBox, QPushButton, QLabel, QMessageBox
)

VITESSE = 115200        # sans effet sur l'USB natif de la C3, mais requis par pyserial
VID_ESPRESSIF = 0x303A  # identifiant USB d'Espressif : sert à repérer la carte


def ouvrir_port(nom, vitesse=115200, timeout=0.1):
    """Ouvre le port sans redémarrer l'ESP32-C3.

    Sur l'USB natif de la C3, l'ouverture d'un port active les signaux DTR et
    RTS, ce qui peut réinitialiser la carte. On crée donc l'objet Serial
    FERMÉ, on met dtr et rts à False, puis seulement on appelle open().
    """
    esp = serial.Serial()          # port créé fermé
    esp.port = nom
    esp.baudrate = vitesse
    esp.timeout = timeout
    esp.dtr = False                # DTR/RTS au repos avant l'ouverture
    esp.rts = False
    esp.open()
    return esp


class LiaisonESP32:
    """Gère le port série : ouverture et fermeture."""

    def __init__(self):
        self.port = None

    @property #indique que est_ouverte est une propriété, pas une méthode
    def est_ouverte(self):
        return self.port is not None

    #fonction pour ouvrir le port série, on utilise la fonction ouvrir_port() définie plus haut
    def ouvrir(self, nom, baud=115200):
        self.port = ouvrir_port(nom, baud)

    #fonction pour fermer le port série, si le port est ouvert, on le ferme et on met self.port à None
    def fermer(self):
        if self.port is not None:
            self.port.close()
            self.port = None


class Fenetre(QMainWindow):
    def __init__(self):
        super().__init__() #appelle le constructeur de la classe parente QMainWindow
        self.setWindowTitle("Console ESP32-C3")
        self.resize(560, 150)

        self.liaison = LiaisonESP32() #crée une instance de la classe LiaisonESP32 pour gérer le port série

        # --- Groupe « Connexion » : choix du port, connecter / déconnecter ---
        #création des widgets pour le choix du port série, le bouton d'actualisation, le bouton de connexion et le label d'état
        self.combo_ports = QComboBox()

        self.btn_actualiser = QPushButton("Actualiser")
        self.btn_actualiser.clicked.connect(self.remplir_ports)

        self.btn_connecter = QPushButton("Connecter")
        self.btn_connecter.clicked.connect(self.basculer_connexion)

        self.label_etat = QLabel("Non connecté")

        # --- Layouts ---
        ligne_port = QHBoxLayout()
        ligne_port.addWidget(self.combo_ports, 1)
        ligne_port.addWidget(self.btn_actualiser)
        ligne_port.addWidget(self.btn_connecter)

        # --- Groupe « Connexion » ---
        groupe_connexion = QGroupBox("Connexion")
        layout_connexion = QVBoxLayout(groupe_connexion) #ajoute le layout vertical au groupe de connexion
        layout_connexion.addLayout(ligne_port) #ajoute le layout horizontal contenant le combo box et les boutons au layout vertical du groupe de connexion
        layout_connexion.addWidget(self.label_etat) #ajoute le label d'état au layout vertical du groupe de connexion

        # --- Conteneur principal ---
        conteneur = QWidget()
        layout = QVBoxLayout(conteneur)
        layout.addWidget(groupe_connexion)
        layout.addStretch()
        self.setCentralWidget(conteneur)

        #actualise la liste des ports série disponibles au démarrage de l'application
        self.remplir_ports()

    # ------------------------------------------------------------------ ports
    def remplir_ports(self):
        self.combo_ports.clear()
        for port in list_ports.comports():
            self.combo_ports.addItem(f"{port.device} — {port.description}", port.device)
            if port.vid == VID_ESPRESSIF:
                self.combo_ports.setCurrentIndex(self.combo_ports.count() - 1)

    def basculer_connexion(self):
        if self.liaison.est_ouverte:
            self.deconnecter()
        else:
            self.connecter()

    def connecter(self):
        nom = self.combo_ports.currentData()
        if nom is None:
            QMessageBox.warning(self, "Port série", "Aucun port série détecté.")
            return
        try:
            self.liaison.ouvrir(nom, VITESSE)
        except serial.SerialException as erreur:
            # Port absent ou déjà occupé (moniteur série de PlatformIO ouvert ?).
            QMessageBox.critical(self, "Port série", f"Ouverture impossible : {erreur}")
            return
        self.btn_connecter.setText("Déconnecter")
        self.label_etat.setText(f"Connecté à {nom}")

    def deconnecter(self):
        self.liaison.fermer()
        self.btn_connecter.setText("Connecter")
        self.label_etat.setText("Non connecté")

    def closeEvent(self, evenement):
        self.deconnecter()                     # ferme le port à la fermeture de la fenêtre
        super().closeEvent(evenement)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = Fenetre()
    fenetre.show()
    sys.exit(app.exec())
