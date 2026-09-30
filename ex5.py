"""
Laboratoire 4 — Exercice 5 : envoi de commandes à la carte
243-53A-MO — Interface usager de microcontrôleurs — Cours 7

Objectif : ajouter à l'exercice 4 l'envoi de commandes.
  - LiaisonESP32.envoyer() ajoute le \n final et encode la commande ;
  - bouton à deux états pour allumer / éteindre la LED ;
  - commande texte libre (bouton « Envoyer » ou touche Entrée) ;
  - le bouton LED suit la réponse OK:LED:... de la carte (blockSignals) ;
  - le groupe « Commandes » est désactivé tant qu'on n'est pas connecté.

Matériel : l'ESP32-C3 Super Mini exécute le firmware de l'exercice 1.

Préparation : pip install pyserial PySide6
Fermez le moniteur série de PlatformIO avant de connecter cette interface.

Programmeur : Guillaume Beaulieu
Date de création : 2026-09-28
Dernière modification : 2026-09-28
"""

import sys
import serial
from serial.tools import list_ports
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QComboBox, QPushButton, QLabel, QLineEdit, QProgressBar, QMessageBox
)

VITESSE = 115200        # sans effet sur l'USB natif de la C3, mais requis par pyserial
VID_ESPRESSIF = 0x303A  # identifiant USB d'Espressif : sert à repérer la carte
ADC_MAX = 4095          # l'entrée analogique de l'ESP32-C3 est sur 12 bits


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
    """Gère le port série : ouverture, envoi de commandes, lecture de lignes."""

    def __init__(self):
        self.port = None

    @property
    def est_ouverte(self):
        return self.port is not None

    def ouvrir(self, nom, baud=115200):
        self.port = ouvrir_port(nom, baud)

    def fermer(self):
        if self.port is not None:
            self.port.close()
            self.port = None

    def envoyer(self, commande):
        # Toute commande se termine par \n : le séparateur attendu par l'ESP32.
        self.port.write((commande + "\n").encode())

    def lire_lignes(self):
        """Retourne la liste des lignes complètes déjà reçues (sans attendre)."""
        lignes = []
        while self.port.in_waiting:
            lignes.append(self.port.readline().decode(errors="ignore").strip())
        return lignes


class Fenetre(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Console ESP32-C3")
        self.resize(560, 400)

        self.liaison = LiaisonESP32()

        # --- Groupe « Connexion » : choix du port, connecter / déconnecter ---
        self.combo_ports = QComboBox()
        self.btn_actualiser = QPushButton("Actualiser")
        self.btn_actualiser.clicked.connect(self.remplir_ports)
        self.btn_connecter = QPushButton("Connecter")
        self.btn_connecter.clicked.connect(self.basculer_connexion)
        self.label_etat = QLabel("Non connecté")

        ligne_port = QHBoxLayout()
        ligne_port.addWidget(self.combo_ports, 1)
        ligne_port.addWidget(self.btn_actualiser)
        ligne_port.addWidget(self.btn_connecter)

        groupe_connexion = QGroupBox("Connexion")
        layout_connexion = QVBoxLayout(groupe_connexion)
        layout_connexion.addLayout(ligne_port)
        layout_connexion.addWidget(self.label_etat)

        # --- Groupe « Mesure » : dernière valeur reçue ---
        self.label_mesure = QLabel("—")
        self.label_mesure.setStyleSheet("font-size: 28px; font-weight: bold;")
        self.barre_mesure = QProgressBar()
        self.barre_mesure.setRange(0, ADC_MAX)
        self.barre_mesure.setFormat("%v / 4095")

        groupe_mesure = QGroupBox("Mesure (entrée analogique, GPIO 0)")
        layout_mesure = QVBoxLayout(groupe_mesure)
        layout_mesure.addWidget(self.label_mesure)
        layout_mesure.addWidget(self.barre_mesure)

        # --- Groupe « Commandes » : LED et commande libre ---
        self.btn_led = QPushButton("LED éteinte")
        self.btn_led.setCheckable(True)          # bouton à deux états
        self.btn_led.toggled.connect(self.changer_led)

        self.champ_commande = QLineEdit()
        self.champ_commande.setPlaceholderText("Commande libre, ex. LED:ON")
        self.champ_commande.returnPressed.connect(self.envoyer_champ)   # touche Entrée
        self.btn_envoyer = QPushButton("Envoyer")
        self.btn_envoyer.clicked.connect(self.envoyer_champ)

        ligne_commande = QHBoxLayout()
        ligne_commande.addWidget(self.champ_commande, 1)
        ligne_commande.addWidget(self.btn_envoyer)

        self.groupe_commandes = QGroupBox("Commandes")
        layout_commandes = QVBoxLayout(self.groupe_commandes)
        layout_commandes.addWidget(self.btn_led)
        layout_commandes.addLayout(ligne_commande)

        # --- Assemblage de la fenêtre ---
        conteneur = QWidget()
        layout = QVBoxLayout(conteneur)
        layout.addWidget(groupe_connexion)
        layout.addWidget(groupe_mesure)
        layout.addWidget(self.groupe_commandes)
        layout.addStretch()
        self.setCentralWidget(conteneur)

        # Le QTimer lit le port toutes les 50 ms, sans jamais bloquer la fenêtre.
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.lire_port)

        self.groupe_commandes.setEnabled(False)  # inutile tant qu'on n'est pas connecté

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
        self.timer.start(50)
        self.groupe_commandes.setEnabled(True)
        self.btn_connecter.setText("Déconnecter")
        self.label_etat.setText(f"Connecté à {nom}")

    def deconnecter(self):
        self.timer.stop()
        self.liaison.fermer()
        self.groupe_commandes.setEnabled(False)
        self.btn_connecter.setText("Connecter")
        self.label_etat.setText("Non connecté")
        self.synchroniser_led(False)           # bouton remis à zéro, sans envoyer de commande
        self.label_mesure.setText("—")
        self.barre_mesure.setValue(0)

    # ---------------------------------------------------------------- envoi
    def envoyer(self, commande):
        if self.liaison.est_ouverte:
            self.liaison.envoyer(commande)

    def changer_led(self, actif):
        self.btn_led.setText("LED allumée" if actif else "LED éteinte")
        self.envoyer("LED:ON" if actif else "LED:OFF")

    def envoyer_champ(self):
        commande = self.champ_commande.text().strip()
        if commande:
            self.envoyer(commande)
            self.champ_commande.clear()

    # -------------------------------------------------------------- réception
    def lire_port(self):
        for ligne in self.liaison.lire_lignes():
            if ligne.startswith("TEMP:"):
                self.afficher_mesure(ligne)
            elif ligne in ("OK:LED:ON", "OK:LED:OFF"):
                self.synchroniser_led(ligne == "OK:LED:ON")

    def synchroniser_led(self, allumee):
        # Le bouton suit la réponse de la carte (même si la commande a été tapée
        # à la main), SANS renvoyer de commande : on bloque ses signaux.
        self.btn_led.blockSignals(True)
        self.btn_led.setChecked(allumee)
        self.btn_led.setText("LED allumée" if allumee else "LED éteinte")
        self.btn_led.blockSignals(False)

    def afficher_mesure(self, ligne):
        try:
            valeur = float(ligne.split(":")[1])
        except (IndexError, ValueError):
            return                             # ligne corrompue : on l'ignore
        self.label_mesure.setText(f"{valeur:g}")
        self.barre_mesure.setValue(max(0, min(ADC_MAX, int(valeur))))

    def closeEvent(self, evenement):
        self.deconnecter()                     # ferme le port à la fermeture de la fenêtre
        super().closeEvent(evenement)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = Fenetre()
    fenetre.show()
    sys.exit(app.exec())
