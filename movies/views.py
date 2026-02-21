from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
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




def movie_trailer(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    trailer_id = None
    if movie.trailer_link:      #if - else (HTML HAI) BY the way every video cannot dispay like (radio=1 or 0 link remember !)
        pattern = r'(?:youtube\.com\/(?:.*v=|v\/|embed\/)|youtu\.be\/)([^"&?/ ]{11})'
        match = re.search(pattern, movie.trailer_link)
        if match:
            trailer_id = match.group(1)

    return render(request, 'movies/movie_trailer.html', {
        'movie': movie,
        'trailer_id': trailer_id
    })


@login_required(login_url='/login/')
def book_seats(request, theater_id):
    theater = get_object_or_404(Theater, id=theater_id)
    seats = Seat.objects.filter(theater=theater)

    available_seats_count = seats.filter(is_booked=False).count()

    if request.method == 'POST':
        selected_seats = request.POST.getlist('seats')

        if not selected_seats:
            return render(request, 'movies/seat_selection.html', {
                'theater': theater,
                'seats': seats,
                'available_count': available_seats_count,
                'error': 'No seat selected'
            })

        # Logic for selection
        seat_id = selected_seats[0]
        seat = get_object_or_404(Seat, id=seat_id, theater=theater)

        if seat.is_booked:
            return render(request, 'movies/seat_selection.html', {
                'theater': theater,
                'seats': seats,
                'available_count': available_seats_count,
                'error': 'Seat already booked'
            })

        return redirect(
            'payment_page',
            movie_id=theater.movie.id,
            theater_id=theater.id,
            seat_id=seat.id
        )

    return render(request, 'movies/seat_selection.html', {
        'theater': theater,
        'seats': seats,
        'available_count': available_seats_count  # Pass the dynamic count here
    })

@login_required(login_url='/login/')
def payment_page(request, movie_id, theater_id, seat_id):
    movie = get_object_or_404(Movie, id=movie_id)
    theater = get_object_or_404(Theater, id=theater_id)
    seat = get_object_or_404(Seat, id=seat_id)

    if request.method == "POST":
        action = request.POST.get('action')

        if action == "paid":

            if seat.is_booked:
                return render(request, 'movies/payment.html',
                              {"error": "Too late! Seat already booked.", "movie": movie})

            seat.is_booked = True
            seat.save()

            Booking.objects.create(  # proper logic na mile tab tak save krte hai database mai
                user=request.user,
                seat=seat,
                movie=movie,
                theater=theater,
                paid=False  # use nahi hai but manually(admin) save krna hai ok!
            )

            return redirect('profile')

    if seat.is_booked:
        return render(request, 'movies/payment.html', {"error": "Seat is already taken!"})

    return render(request, 'movies/payment.html', {
        "movie": movie,
        "theater": theater,
        "seat": seat,
    })