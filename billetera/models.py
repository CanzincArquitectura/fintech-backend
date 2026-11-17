import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User


class Cuenta(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cuenta")
    numero_cuenta = models.CharField(max_length=20, unique=True)
    saldo = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    moneda = models.CharField(max_length=3, default="CLP")
    activa = models.BooleanField(default=True)
    creada_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.numero_cuenta} - {self.usuario.username} (${self.saldo} {self.moneda})"


class Transaccion(models.Model):
    TIPO_CHOICES = [
        ("DEPOSITO", "Depósito"),
        ("TRANSFERENCIA", "Transferencia"),
        ("RETIRO", "Retiro"),
    ]

    id_operacion = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    cuenta_origen = models.ForeignKey(
        Cuenta, on_delete=models.PROTECT, related_name="envios", null=True, blank=True
    )
    cuenta_destino = models.ForeignKey(
        Cuenta, on_delete=models.PROTECT, related_name="recepciones"
    )
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    monto = models.DecimalField(max_digits=14, decimal_places=2)
    descripcion = models.CharField(max_length=255, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"[{self.tipo}] {self.monto} -> {self.cuenta_destino.numero_cuenta}"
