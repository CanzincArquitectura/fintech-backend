from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Cuenta, Transaccion
from .serializers import (
    CuentaSerializer,
    TransaccionSerializer,
    TransferenciaInputSerializer,
)


class MiCuentaView(APIView):
    def get(self, request):
        try:
            cuenta = request.user.cuenta
        except Cuenta.DoesNotExist:
            return Response(
                {"error": "El usuario no tiene una cuenta activa asignada."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(CuentaSerializer(cuenta).data)


class HistorialMovimientosView(APIView):
    def get(self, request):
        try:
            cuenta = request.user.cuenta
        except Cuenta.DoesNotExist:
            return Response(
                {"error": "El usuario no tiene una cuenta activa asignada."},
                status=status.HTTP_404_NOT_FOUND,
            )
        movimientos = Transaccion.objects.filter(
            Q(cuenta_origen=cuenta) | Q(cuenta_destino=cuenta)
        )
        return Response(TransaccionSerializer(movimientos, many=True).data)


class TransferirView(APIView):
    @transaction.atomic
    def post(self, request):
        serializer = TransferenciaInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        num_destino = serializer.validated_data["cuenta_destino"]
        monto = serializer.validated_data["monto"]
        descripcion = serializer.validated_data.get("descripcion", "")

        try:
            origen = Cuenta.objects.select_for_update().get(usuario=request.user, activa=True)
        except Cuenta.DoesNotExist:
            return Response(
                {"error": "Tu cuenta origen no existe o está inactiva."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if origen.numero_cuenta == num_destino:
            return Response(
                {"error": "No puedes transferir dinero a tu misma cuenta."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            destino = Cuenta.objects.select_for_update().get(numero_cuenta=num_destino, activa=True)
        except Cuenta.DoesNotExist:
            return Response(
                {"error": "La cuenta de destino no existe o está inactiva."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if origen.saldo < monto:
            return Response(
                {"error": "Saldo insuficiente para realizar la operación."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ejecución atómica del movimiento financiero
        origen.saldo -= monto
        destino.saldo += monto
        origen.save()
        destino.save()

        operacion = Transaccion.objects.create(
            cuenta_origen=origen,
            cuenta_destino=destino,
            tipo="TRANSFERENCIA",
            monto=monto,
            descripcion=descripcion,
        )

        return Response(
            {
                "mensaje": "Transferencia realizada con éxito.",
                "operacion": TransaccionSerializer(operacion).data,
                "nuevo_saldo": origen.saldo,
            },
            status=status.HTTP_201_CREATED,
        )
