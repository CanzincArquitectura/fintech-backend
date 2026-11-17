from django.urls import path
from .views import MiCuentaView, HistorialMovimientosView, TransferirView

urlpatterns = [
    path("mi-cuenta/", MiCuentaView.as_view(), name="mi-cuenta"),
    path("movimientos/", HistorialMovimientosView.as_view(), name="movimientos"),
    path("transferir/", TransferirView.as_view(), name="transferir"),
]
