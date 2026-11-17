from decimal import Decimal
from rest_framework import serializers
from .models import Cuenta, Transaccion


class CuentaSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField()

    class Meta:
        model = Cuenta
        fields = ["numero_cuenta", "usuario", "saldo", "moneda", "activa", "creada_en"]


class TransaccionSerializer(serializers.ModelSerializer):
    cuenta_origen = serializers.SlugRelatedField(slug_field="numero_cuenta", read_only=True)
    cuenta_destino = serializers.SlugRelatedField(slug_field="numero_cuenta", read_only=True)

    class Meta:
        model = Transaccion
        fields = ["id_operacion", "tipo", "cuenta_origen", "cuenta_destino", "monto", "descripcion", "fecha"]


class TransferenciaInputSerializer(serializers.Serializer):
    cuenta_destino = serializers.CharField(max_length=20)
    monto = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=Decimal("1.00"))
    descripcion = serializers.CharField(max_length=255, required=False, allow_blank=True)
