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


import razorpay
import json
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail


@login_required(login_url='/login/')
def payment_page(request, movie_id, theater_id, seat_id):
    movie = get_object_or_404(Movie, id=movie_id)
    theater = get_object_or_404(Theater, id=theater_id)
    seat = get_object_or_404(Seat, id=seat_id)

    if seat.is_booked:
        return render(request, 'movies/payment_page.html', {
            "error": "Seat already booked!",
        })

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # Static price for example, change as needed
    amount = 12 * 100

    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    return render(request, 'movies/payment_page.html', {
        "movie": movie,
        "theater": theater,
        "seat": seat,
        "order_id": order["id"],
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "amount": amount,
        "amount_in_rupees": amount / 100
    })


@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        data = json.loads(request.body)
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        try:
            # 1. Verify Signature
            client.utility.verify_payment_signature({
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            })

            seat = get_object_or_404(Seat, id=data['seat_id'])
            if seat.is_booked:
                return JsonResponse({"status": "Seat already booked"})

            seat.is_booked = True
            seat.save()

            booking = Booking.objects.create(
                user=request.user,
                seat=seat,
                movie_id=data['movie_id'],
                theater_id=data['theater_id'],
                paid=True  # Automatically set to True on successful payment
            )

            subject = f"Booking Confirmed: {booking.movie.name}"
            message = (
                f"Hi {request.user.username},\n\n"
                f"Your booking is confirmed!\n"
                f"Movie: {booking.movie.name}\n"
                f"Theater: {booking.theater.name}\n"
                f"Seat: {booking.seat.seat_number}\n\n"
                f"Show this email at the entrance. Enjoy your movie!"
            )
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [request.user.email]

            try:
                send_mail(subject, message, email_from, recipient_list)
            except Exception as e:
                print(f"Email failed: {e}")

            return JsonResponse({"status": "Payment Successful"})

        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({"status": "Payment Failed", "message": "Invalid Signature"})
        except Exception as e:
            return JsonResponse({"status": "Error", "message": str(e)})

    return JsonResponse({"status": "Invalid Request"})