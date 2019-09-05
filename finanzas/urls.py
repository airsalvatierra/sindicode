from django.urls import path
from finanzas import views

app_name = 'finanzas'

urlpatterns = [
    path('crear/',views.ingreso_egreso_create_view,name='crear'),
    path('movimientos/',views.lista_ingreso_egreso,name='movimientos'),
    path('saldos/',views.lista_saldos,name='saldos'),
    path('pendientes/',views.lista_pendientes,name='pendientes'),
    path('aprobar/<int:pk>',views.aprobar_pendientes,name='aprobar'),
    path('log_finanzas',views.list_log_finanzas,name='log_finanzas'),
    path('saldos/xls/', views.export_saldos_xls, name='export_saldos_xls'),
    path('saldos/pdf/', views.export_saldos_pdf, name='export_saldos_pdf'),
    path('movimientos/xls/', views.export_movimientos_xls, name='export_movimientos_xls'),
    path('movimientos/pdf/', views.export_movimientos_pdf, name='export_movimientos_pdf'),
    path('movimientos_edit/',views.lista_movimientos,name='movimientos_edit'),
    path('movimientos_edit/<int:pk>/',views.edit_movimiento,name='edit_movimiento'),
    path('movimientos_edit_full/<int:pk>/',views.edit_movimiento_full,name='edit_movimiento_full'),
    path('movimientos_view/<int:pk>/',views.view_movimiento,name='view_movimiento'),
    path('delete/<int:pk>/',views.delete_movimiento,name='delete_movimiento'),
    path('add_presupuesto_masivo/',views.add_presupuesto_masivo,name='add_presupuesto_masivo'),
    path('cerrar_mes/',views.cerrar_mes,name='cerrar_mes'),
    path('movimientos_socios/',views.lista_movimientos_socios,name='mov_socios'),
]
