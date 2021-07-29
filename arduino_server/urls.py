from django.conf.urls import url
from django.urls import path, include

from arduino_server import views

urlpatterns = [
    # path('', views.hello_world, name="hello_world"),
    path('', views.index, name="arduino_server_index"),
    # path(r'^$', views.index, name="arduino_server_index"),
    # path(r'^meter/(\d+)/$', views.meter, name="arduino_server_meter"),
    # path(r'^interval/(\d+)/json/$', views.interval_json, name="arduino_server_interval_json"),
    path('meter/<int:meter_id>/', views.meter, name="arduino_server_meter"),
    path('interval/<int:meter_id>/json/', views.interval_json, name="arduino_server_interval_json"),

]

#
# urlpatterns = patterns('',
#     url('^$', 'arduinodataserver.views.index', name='arduinodataserver_index'),
#     url('^meter/(\d+)/$', 'arduinodataserver.views.meter', name='arduinodataserver_meter'),
#     url('^interval/(\d+)/json/$', 'arduinodataserver.views.interval_json', name='arduinodataserver_interval_json'),
# )

# if settings.DEBUG:
#     urlpatterns += staticfiles_urlpatterns()
#     urlpatterns += patterns('',
#         url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
#             'document_root': settings.MEDIA_ROOT,
#         }),
#    )