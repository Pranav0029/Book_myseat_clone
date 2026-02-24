from movies.models import Movie, Theater, Booking, Seat
from django.utils import timezone
from datetime import timedelta
import json

def admin_dashboard(request):
    now = timezone.now()

    rev_today = Booking.objects.filter(booked_at__date=now.date()).count() * 12
    rev_month = Booking.objects.filter(booked_at__month=now.month, booked_at__year=now.year).count() * 12
    rev_6month = Booking.objects.filter(booked_at__gte=now - timedelta(days=180)).count() * 12
    total_revenue = Booking.objects.count() * 12

    theaters = Theater.objects.all()
    theater_yield_data = []

    theater_occupancy = []

    for t in theaters:
        def get_rev(filters):
            return Booking.objects.filter(theater=t, **filters).count() * 12

        theater_yield_data.append({
            'name': t.name,
            'today': get_rev({'booked_at__date': now.date()}),
            'month': get_rev({'booked_at__month': now.month, 'booked_at__year': now.year}),
            'six_month': get_rev({'booked_at__gte': now - timedelta(days=180)}),
            'year': get_rev({'booked_at__year': now.year}),
            'all': Booking.objects.filter(theater=t).count() * 12
        })

        total_seats = t.seats.count()
        booked_seats = t.seats.filter(is_booked=True).count()
        occupancy_percent = (booked_seats / total_seats * 100) if total_seats > 0 else 0
        # booked_seats pendind valo ko bh yahi hao , so remember jabtak vo remove nahi hoga ye nahi !

        theater_occupancy.append({
            'name': t.name,
            'percent': round(occupancy_percent, 1),
            'remaining': total_seats - booked_seats
        })


    top_7_movies = Movie.objects.annotate(bc=Count('booking')).annotate(movie_revenue=F('bc') * 12).order_by('-bc')[:7]
    theater_stats = Theater.objects.annotate(tc=Count('booking')).annotate(revenue=F('tc') * 12).order_by('-revenue')

    theater_ranks = []
    for t in theaters:
        top_movie = Movie.objects.filter(booking__theater=t) \
            .annotate(theater_specific_bookings=Count('booking')) \
            .order_by('-theater_specific_bookings').first() # ???????

        theater_ranks.append({
            'theater': t.name,
            'movie': top_movie.name if top_movie else "No Bookings",
            'count': top_movie.theater_specific_bookings if top_movie else 0
        })

    context = {
        'total_movies': Movie.objects.count(),
        'total_bookings': Booking.objects.count(),
        'total_revenue': total_revenue,
        'rev_today': rev_today,
        'rev_month': rev_month,
        'rev_6month': rev_6month,
        'top_7_movies': top_7_movies,
        'theater_yield_json': json.dumps(theater_yield_data),
        'theater_stats': theater_stats,
        'theater_labels': [t.name for t in theater_stats[:5]],
        'theater_data': [t.tc for t in theater_stats[:5]],
        'theater_occupancy': theater_occupancy,
        'theater_ranks': theater_ranks,
    }
    return render(request, "dashboard/dashboard.html", context)


def movies_data(request):

    genre_data = Movie.objects.values('genre').annotate(count=Count('id')).order_by('-count')

    movie_performance = Movie.objects.annotate(
        tickets=Count('booking'),
        revenue=Count('booking') * 12
    ).order_by('-revenue')

    scatter_data = []
    for m in movie_performance[:10]:
        scatter_data.append({'x': float(m.rating), 'y': m.revenue, 'name': m.name})

    context = {
        'total_movies': Movie.objects.count(),
        'top_rated': Movie.objects.order_by('-rating').first(),
        'most_profitable': movie_performance.first(),
        'movie_performance': movie_performance,
        'genre_labels': [g['genre'] if g['genre'] else "Other" for g in genre_data],
        'genre_values': [g['count'] for g in genre_data],
        'scatter_json': json.dumps(scatter_data),
    }
    return render(request, "dashboard/movies_data.html", context)

from django.shortcuts import render
from django.db.models import Count, F, Avg

def theaters(request):

    theater_stats = Theater.objects.values('name').annotate( # annotate creat the table row by row !
        ticket_count=Count('booking'),
        revenue=Count('booking') * 12,
        avg_movie_rating=Avg('movie__rating'),
        unique_movies=Count('movie', distinct=True)
    ).order_by('-ticket_count')

    busy_theaters = Theater.objects.values('name').annotate(
        movie_count=Count('movie', distinct=True)
    ).order_by('-movie_count')  # accrding to gemini , fetch -> count -> sort ! (logic)

    high_rated_theaters = Theater.objects.filter(movie__rating__gte=8.0).select_related('movie')


    total_theaters_count = Theater.objects.values('name').distinct().count()
    avg_occupancy = 0
    all_seats = Seat.objects.count()
    if all_seats > 0:
        booked = Seat.objects.filter(is_booked=True).count()
        avg_occupancy = round((booked / all_seats) * 100, 1)

    context = {
        'theater_stats': theater_stats,
        'busy_theaters': busy_theaters,
        'high_rated_theaters': high_rated_theaters,
        'total_fleet': total_theaters_count,
        'avg_occupancy': avg_occupancy,
        'chart_labels': [t['name'] for t in theater_stats[:6]],
        'chart_revenue': [t['revenue'] for t in theater_stats[:6]],
        'chart_variety': [t['unique_movies'] * 10 for t in theater_stats[:6]],
    }
    return render(request, "dashboard/theaters.html", context)