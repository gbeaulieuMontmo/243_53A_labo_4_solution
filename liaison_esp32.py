"""
Laboratoire 4 — Exercice 6 : classe LiaisonESP32
243-53A-MO — Interface usager de microcontrôleurs — Cours 7

Encapsule la communication série avec l'ESP32-C3 : ouverture du port (sans
redémarrer la carte), envoi de commandes et lecture des lignes reçues.

Préparation : pip install pyserial

Programmeur : Guillaume Beaulieu
Date de création : 2026-09-21
Dernière modification : 2026-09-30
"""

import serial


def ouvrir_port(nom, vitesse=115200, timeout=0.1):
    """Ouvre le port sans redémarrer l'ESP32-C3.

    Sur l'USB natif de la C3, l'ouverture d'un port active les signaux DTR et
    RTS, ce qui peut réinitialiser la carte. On crée donc l'objet Serial
    FERMÉ, on met dtr et rts à False, puis seulement on appelle open().
    """
    esp = serial.Serial()          # port créé fermé
    esp.port = nom
    esp.baudrate = vitesse         # sans effet sur l'USB natif, mais requis par pyserial
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
