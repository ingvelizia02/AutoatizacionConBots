import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.analizador_sitio import (
    detectar_chatbots,
    detectar_whatsapp_manual,
    extraer_redes_sociales,
)


class TestDetectarChatbots(unittest.TestCase):
    def test_detecta_manychat(self):
        html = '<script src="https://widget.manychat.com/123.js"></script>'
        self.assertEqual(detectar_chatbots(html), ["ManyChat"])

    def test_detecta_varios(self):
        html = "tidio.com ... crisp.chat widget"
        self.assertEqual(detectar_chatbots(html), ["Crisp", "Tidio"])

    def test_sin_chatbot(self):
        html = "<html><body>Bienvenidos a nuestra clínica</body></html>"
        self.assertEqual(detectar_chatbots(html), [])


class TestWhatsappManual(unittest.TestCase):
    def test_detecta_wa_me(self):
        html = '<a href="https://wa.me/51999999999">Escríbenos</a>'
        self.assertTrue(detectar_whatsapp_manual(html))

    def test_detecta_api_whatsapp(self):
        html = '<a href="https://api.whatsapp.com/send?phone=51999999999">Chat</a>'
        self.assertTrue(detectar_whatsapp_manual(html))

    def test_sin_whatsapp(self):
        html = "<html><body>Contáctanos por correo</body></html>"
        self.assertFalse(detectar_whatsapp_manual(html))


class TestRedesSociales(unittest.TestCase):
    def test_extrae_facebook_e_instagram(self):
        html = (
            '<a href="https://www.facebook.com/miclinica">FB</a>'
            '<a href="https://www.instagram.com/miclinica">IG</a>'
        )
        redes = extraer_redes_sociales(html, "https://miclinica.com")
        self.assertEqual(redes["facebook"], "https://www.facebook.com/miclinica")
        self.assertEqual(redes["instagram"], "https://www.instagram.com/miclinica")

    def test_sin_redes(self):
        html = "<a href='/contacto'>Contacto</a>"
        redes = extraer_redes_sociales(html, "https://miclinica.com")
        self.assertEqual(redes, {})


if __name__ == "__main__":
    unittest.main()
