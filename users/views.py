from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .forms import UserRegisterForm, UserUpdateForm
from django.shortcuts import render,redirect
from django.contrib.auth import login,authenticate
from django.contrib.auth.decorators import login_required
from movies.models import Movie, Booking


def home(request):

    movies = Movie.objects.all()

    language = request.GET.get('language')
    genre = request.GET.get('genre')

    if language:
        movies = movies.filter(language=language)   # we can use or operator if need

    if genre:
        movies = movies.filter(genre=genre)

    return render(request, 'home.html', {
        'movies': movies,
        'language_filter': language,
        'genre_filter': genre
    })

from django.core.mail import send_mail
from django.conf import settings


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            email = form.cleaned_data.get('email')

            # request parameter added(here is not error but maye be authenticate can repeat ! )
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

            # Email sending
            send_mail(
                subject='Welcome to BookMySeat ',
                message=(
                    f"Hello {username},\n\n"
                    "Welcome to BookMySeat!\n\n"
                    "Your account has been successfully created.\n"
                    "Now you can book your seats easily and securely.\n\n"
                    "If you have any questions, feel free to contact us.\n\n"
                    "Happy Booking! \n"
                    "Team BookMySeat"
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

            return redirect('profile')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form=AuthenticationForm(request,data=request.POST)
        if form.is_valid():
            user=form.get_user()
            login(request,user)
            return redirect('/')
    else:
        form=AuthenticationForm()
    return render(request,'users/login.html',{'form':form})

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Booking)
def send_booking_confirmation_email(sender, instance, created, **kwargs):
    # Agar booking update hui hai (created=False) aur paid checkbox tick ho gaya hai
    if not created and instance.paid:
        subject = f"Ticket Confirmed: {instance.movie.name}"
        message = (
            f"Hello {instance.user.username},\n\n"
            f"Your ticket for '{instance.movie.name}' has been successfully booked.\n"
            f"Theater: {instance.theater.name}\n"
            f"Seat Number: {instance.seat.seat_number}\n"
            f"Status: Confirmed\n\n"
            f"Enjoy your movie!"
        )

        from_email = settings.EMAIL_HOST_USER
        recipient_list = [instance.user.email]

        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            print(f"Email error: {e}")

from django.contrib import messages

def profile(request):
    # User ki sari bookings fetch karein
    bookings = Booking.objects.filter(user=request.user).order_by('-booked_at')

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, f'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)

    context = {
        'u_form': u_form,
        'bookings': bookings,
    }
    return render(request, 'users/profile.html', context)

@login_required
def reset_password(request):            #don't know logic !
    if request.method == 'POST':
        form=PasswordChangeForm(user=request.user,data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form=PasswordChangeForm(user=request.user)
    return render(request,'users/reset_password.html',{'form':form})