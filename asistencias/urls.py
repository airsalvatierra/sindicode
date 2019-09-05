from django.urls import path
from asistencias import views

app_name = 'asistencias'

urlpatterns = [
    path('crear/',views.crear_asistencia,name='nueva'),
    path('lista/',views.AsistenciaEncListView.as_view(),name='lista'),
    path('<int:pk>/',views.AsistenciaDetListView.as_view(),name='listadet'),
    path('edit/<int:pk>/',views.AsistenciaDetUpdateView.as_view(),name='updatedet'),
    path('lista_CE/',views.AsistenciaEncListViewCE.as_view(),name='lista_CE'),
    path('lista_CE/<int:pk>/',views.AsistenciaDetListViewCE.as_view(),name='lista_det_CE'),
    path('edit_CE/<int:pk>/',views.AsistenciaDetUpdateViewCE.as_view(),name='detalle_CE'),
    path('<int:pk>/xls/', views.export_asistencias_xls, name='export_asistencias_xls'),
    path('<int:pk>/pdf/', views.export_asistencias_pdf, name='export_asistencias_pdf'),
    path('crear_CE/',views.crear_asistencia_CE,name='nuevaCE'),
]
