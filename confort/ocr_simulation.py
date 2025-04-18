# ocr_simulation.py

"""
Ce module simule une lecture de texte via OCR (reconnaissance optique de caractères)
à partir d'une image, pour les lunettes intelligentes pour aveugles.
L'objectif est de tester localement la détection et la lecture de texte simple.
"""

import pytesseract
from PIL import Image

def lire_texte_image(image_path):
    """
    Simule l'extraction de texte depuis une image.
    :param image_path: Chemin vers l'image à analyser.
    :return: Texte détecté.
    """
    image = Image.open(image_path)
    texte = pytesseract.image_to_string(image, lang='fra')
    return texte

if __name__ == "__main__":
    chemin_image = "../ressources/1000_F_24929799_qZBxvyNb0KekDRXzxevbLBNmO2EXv7vc.jpg"
    texte_detecte = lire_texte_image(chemin_image)
    print("Texte détecté :")
    print(texte_detecte)