from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegistrationForm
from django.contrib.auth.decorators import login_required
from catalog.models import Product
from bookings.models import Booking
from .forms import ProfileForm

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    my_products = Product.objects.filter(owner=request.user).order_by('-created_at')
    my_bookings = Booking.objects.filter(renter=request.user).order_by('-start_date')
    
    owner_requests = Booking.objects.filter(product__owner=request.user).order_by('-created_at')
    
    context = {
        'user': request.user,
        'my_products': my_products,
        'my_bookings': my_bookings,
        'owner_requests': owner_requests,  
        'rating': round(request.user.rating, 1) if request.user.rating_count > 0 else 0.0,
        'rating_count': request.user.rating_count,
    }
    return render(request, 'users/profile.html', context)

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлён!')
            return redirect('profile')  
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'users/profile_edit.html', {'form': form})