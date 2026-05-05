from django.urls import path
from . import views

urlpatterns = [
    path('hirex/',                views.home,           name='home'),
    path('join/',                 views.join,           name='join'),
    path('interview/',            views.interview,      name='interview'),
    path('tool/',                 views.tool,           name='tool'),
    path('interview/feedback/',   views.feedback,       name='feedback'),
    path('proctoring/',           views.proctoring_view, name='proctoring'),
    path('iot/event/',            views.iot_event,      name='iot_event'),   # IoT camera endpoint
]
