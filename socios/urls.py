from django.urls import path
from socios import views

app_name = 'socios'

urlpatterns = [
    path('nuevo/',views.create_socio,name='nuevo'),
    path('lista/',views.list_socio,name='lista'),
    path('editar/<int:pk>/',views.edit_socio,name='editar'),
    path('roles/',views.list_socio_roles,name='roles'),
    # path('roles/<int:pk>',views.edit_roles,name='edit_roles'),
    path('user_login/',views.user_login,name='user_login'),
    path('editar/<int:pk>/editarol/', views.editar_roles, name='editar_roles'),
    path('miinformacion/', views.mi_informacion, name='mi_informacion'),
    path('log_socios/',views.list_log_socio,name='log_socios'),
    path('cargas/',views.list_socios_cargas,name='list_socio_cargas'),
    # path('cargas/<int:pk>/',views.list_cargas,name='list_cargas'),
    path('editar/<int:pk>/crear/',views.crear_carga,name='crear_carga'),
    path('eliminar/<int:pk>',views.delete_carga,name='delete_carga'),
    path('editar/<int:pk>/crear_evento/',views.crear_evento,name='crear_evento'),
]
