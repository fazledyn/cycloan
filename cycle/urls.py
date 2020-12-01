from django.urls import path
from . import views

urlpatterns = [
    path('<int:cycle_id>',  views.CycleSingleView.as_view(),    name='cycle-single-view'),
    path('add/',             views.CycleAddView.as_view(),       name='cycle-add-view'),
    path('delete/<int:cycle_id>',         views.CycleDeleteView.as_view(),     name='cycle-delete-view'),
]