from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse
from .models import *



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
        return redirect('lag')  # Use the URL pattern name

    recepies = Recepie.objects.all()
    return render(request, 'lag.html', {'recepies': recepies})
    
    
    queryset = Recepie.objects.all()
    context = {'recepies': queryset}
    return render(request, 'lag.html', context)

def delete_recepie(request, id):
    recepie = get_object_or_404(Recepie, id=id)
    recepie.delete()
    return redirect('lag')



def first(request):
     return render(request, 'first.html',context={'page': 'first'})