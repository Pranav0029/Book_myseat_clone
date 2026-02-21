from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('<int:movie_id>/theaters', views.theater_list, name='theater_list'),
    path('theater/<int:theater_id>/seats/book/', views.book_seats, name='book_seats'),
    path('movie/<int:movie_id>/trailer/', views.movie_trailer, name='movie_trailer'),

    # payment url with parameters
    path(
        'payment/<int:movie_id>/<int:theater_id>/<int:seat_id>/',
        views.payment_page,
        name='payment_page'
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
