import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.scoring import ALTA, BAJA, DESCARTAR, MEDIA, calcular_relevancia


def señales(accesible=True, chatbots=None, whatsapp=False, facebook=None, instagram=None):
    return {
        "accesible": accesible,
        "chatbots_detectados": chatbots or [],
        "whatsapp_manual": whatsapp,
        "facebook": facebook,
        "instagram": instagram,
    }


class TestCalcularRelevancia(unittest.TestCase):
    def test_sitio_no_accesible(self):
        r = calcular_relevancia(señales(accesible=False))
        self.assertEqual(r["categoria"], BAJA)
        self.assertEqual(r["puntaje"], 0)

    def test_ya_tiene_chatbot_se_descarta(self):
        r = calcular_relevancia(señales(chatbots=["ManyChat"]))
        self.assertEqual(r["categoria"], DESCARTAR)

    def test_whatsapp_manual_y_redes_es_alta(self):
        r = calcular_relevancia(señales(whatsapp=True, facebook="https://facebook.com/x"))
        self.assertEqual(r["puntaje"], 4)
        self.assertEqual(r["categoria"], ALTA)

    def test_solo_whatsapp_es_media(self):
        r = calcular_relevancia(señales(whatsapp=True))
        self.assertEqual(r["puntaje"], 3)
        self.assertEqual(r["categoria"], MEDIA)

    def test_sin_señales_es_baja(self):
        r = calcular_relevancia(señales())
        self.assertEqual(r["puntaje"], 0)
        self.assertEqual(r["categoria"], BAJA)


if __name__ == "__main__":
    unittest.main()
