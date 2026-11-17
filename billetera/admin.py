from django.contrib import admin
from .models import Cuenta, Transaccion


@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ("numero_cuenta", "usuario", "saldo", "moneda", "activa", "creada_en")
    search_fields = ("numero_cuenta", "usuario__username")


@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ("id_operacion", "tipo", "cuenta_origen", "cuenta_destino", "monto", "fecha")
    list_filter = ("tipo", "fecha")
    readonly_fields = ("id_operacion", "fecha")
