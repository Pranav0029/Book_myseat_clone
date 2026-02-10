from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.mail import send_mail
from django.conf import settings
import re
from .models import Movie, Theater, Seat, Booking


def movie_list(request):

    search_query = request.GET.get('search')

    if search_query:
        movies = Movie.objects.filter(name__icontains=search_query)
    else:
        movies = Movie.objects.all()

    return render(request, 'movies/movie_list.html', {
        'movies': movies
    })


def theater_list(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    theaters = Theater.objects.filter(movie=movie)

    return render(request, 'movies/theater_list.html', {
        'movie': movie,
        'theaters': theaters
    })


@login_required(login_url='/login/')
def book_seats(request, theater_id):
    theater = get_object_or_404(Theater, id=theater_id)
    seats = Seat.objects.filter(theater=theater)

    if request.method == 'POST':
        selected_seats = request.POST.getlist('seats')

        if not selected_seats:
            return render(request, 'movies/seat_selection.html', {
                'theaters': theater,
                'seats': seats,
                'error': 'No seat selected'
            })
        booked_seats = []
        error_seats = []
        for seat_id in selected_seats:
            seat = get_object_or_404(Seat, id=seat_id, theater=theater)

            if seat.is_booked:
                error_seats.append(seat.seat_number)
                continue

            try:
                Booking.objects.create(
                    user=request.user,
                    seat=seat,
                    movie=theater.movie,
                    theater=theater
                )
                seat.is_booked = True
                seat.save()
                booked_seats.append(seat.seat_number)

            except IntegrityError:
                error_seats.append(seat.seat_number)
        if error_seats:
            return render(request, 'movies/seat_selection.html', {
                'theaters': theater,
                'seats': seats,
                'error': 'Seats already booked: ' + ', '.join(error_seats)
            })

        send_mail(
            subject='Seat Booking Confirmed - BookMySeat',
            message=(
                f"Hello {request.user.username},\n\n"
                "Your booking is confirmed.\n\n"
                f"Movie: {theater.movie}\n"
                f"Theater: {theater.name}\n"
                f"Seats: {', '.join(booked_seats)}\n\n"
                "Enjoy your movie!\n\n"
                "BookMySeat Team"
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[request.user.email],
            fail_silently=False
        )
        return redirect('profile')

    return render(request, 'movies/seat_selection.html', {
        'theaters': theater,
        'seats': seats })


def movie_trailer(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    trailer_id = None
    if movie.trailer_link:
        pattern = r'(?:youtube\.com\/(?:.*v=|v\/|embed\/)|youtu\.be\/)([^"&?/ ]{11})'
        match = re.search(pattern, movie.trailer_link)
        if match:
            trailer_id = match.group(1)

    return render(request, 'movies/movie_trailer.html', {
        'movie': movie,
        'trailer_id': trailer_id
    })
