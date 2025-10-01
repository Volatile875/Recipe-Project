from django.shortcuts import render,redirect, get_object_or_404
from .models import Recepie
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required(login_url='/login/')
def lag(request):
    if request.method == 'POST':
        recepie_image = request.FILES.get('recepie_image')
        recepie_name = request.POST.get('recepie_name')
        recepie_description = request.POST.get('recepie_description')

        Recepie.objects.create(
            recepie_image=recepie_image,
            recepie_name=recepie_name,
            recepie_description=recepie_description,
        )
        return redirect('lag')  # use the named URL

    
    queryset = Recepie.objects.all()
    
    if request.GET.get('search'):
        queryset = queryset.filter(recepie_name__icontains= request.GET.get('search'))
    
    context = {'recepies': queryset}
    return render(request, 'lag.html', context)


@login_required(login_url='/login/')
def update_recepie(request, id):
    queryset = get_object_or_404(Recepie, id=id)
    context = {'recepie': queryset}

    return render(request,'lag.html', context)

@login_required(login_url='/login/')
def delete_recepie(request, id):
    recepie = get_object_or_404(Recepie, id=id)
    recepie.delete()
    return redirect('lag')


def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, 'Invalid username or password')
            return redirect('login_page')

        # If authentication succeeded, log the user in and redirect
        login(request, user)
        return redirect('lag')

    # For GET (and other methods) render the login form
    return render(request, 'login.html')

def register_view(request):
    # Handle POST: create a new user after validating fields
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Basic validation
        if not username or not password:
            messages.error(request, 'Username and password are required')
            return render(request, 'register.html')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'register.html')

        # create_user hashes the password correctly
        User.objects.create_user(
            username=username,
            email=email or None,
            password=password,
            first_name=first_name or '',
            last_name=last_name or '',
        )

        messages.success(request, 'Account created. Please log in.')
        return redirect('/login/')

    # For GET (and any other methods) render the registration form
    return render(request, 'register.html')


def logout_page(request):
    logout(request)
    return redirect('/login/')