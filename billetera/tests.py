from decimal import Decimal
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Cuenta, Transaccion


class BilleteraFintechTests(APITestCase):
    def setUp(self):
        # Crear dos usuarios y sus cuentas de prueba (se destruyen solos al terminar)
        self.user1 = User.objects.create_user(username="alice", password="Password123!")
        self.user2 = User.objects.create_user(username="bob", password="Password123!")

        self.cuenta_alice = Cuenta.objects.create(
            usuario=self.user1, numero_cuenta="10001", saldo=Decimal("500000.00")
        )
        self.cuenta_bob = Cuenta.objects.create(
            usuario=self.user2, numero_cuenta="10002", saldo=Decimal("100000.00")
        )

        # Obtener token JWT para Alice
        url_token = reverse("token_obtain_pair")
        resp = self.client.post(url_token, {"username": "alice", "password": "Password123!"})
        self.token_alice = resp.data["access"]

    def autenticar_alice(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token_alice}")

    def test_01_acceso_denegado_sin_token(self):
        """Verifica que nadie pueda consultar saldos sin iniciar sesión."""
        response = self.client.get(reverse("mi-cuenta"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_02_consultar_mi_cuenta(self):
        """Verifica que Alice pueda consultar su saldo correctamente."""
        self.autenticar_alice()
        response = self.client.get(reverse("mi-cuenta"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["numero_cuenta"], "10001")
        self.assertEqual(Decimal(response.data["saldo"]), Decimal("500000.00"))

    def test_03_transferencia_exitosa(self):
        """Verifica una transferencia válida y la actualización atómica de ambos saldos."""
        self.autenticar_alice()
        datos = {
            "cuenta_destino": "10002",
            "monto": "150000.00",
            "descripcion": "Pago de servicios",
        }
        response = self.client.post(reverse("transferir"), datos, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.cuenta_alice.refresh_from_db()
        self.cuenta_bob.refresh_from_db()

        self.assertEqual(self.cuenta_alice.saldo, Decimal("350000.00"))
        self.assertEqual(self.cuenta_bob.saldo, Decimal("250000.00"))
        self.assertEqual(Transaccion.objects.count(), 1)

    def test_04_rechazar_saldo_insuficiente(self):
        """Verifica que no se permita transferir más dinero del disponible."""
        self.autenticar_alice()
        datos = {"cuenta_destino": "10002", "monto": "900000.00"}
        response = self.client.post(reverse("transferir"), datos, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.cuenta_alice.refresh_from_db()
        self.assertEqual(self.cuenta_alice.saldo, Decimal("500000.00"))
        self.assertEqual(Transaccion.objects.count(), 0)

    def test_05_rechazar_autotransferencia(self):
        """Verifica que un usuario no pueda transferirse a su propia cuenta."""
        self.autenticar_alice()
        datos = {"cuenta_destino": "10001", "monto": "10000.00"}
        response = self.client.post(reverse("transferir"), datos, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_06_rechazar_monto_negativo_o_cero(self):
        """Verifica que el serializador bloquee montos inválidos."""
        self.autenticar_alice()
        datos = {"cuenta_destino": "10002", "monto": "-5000.00"}
        response = self.client.post(reverse("transferir"), datos, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
