from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Character
import json
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView



def character_list(request):
    if request.method == 'GET':
        characters = Character.objects.all().values('id', 'name')
        return JsonResponse(list(characters), safe=False)
    elif request.method == 'POST':
        data = json.loads(request.body)
        character = Character.objects.create(name=data['name'])
        return JsonResponse({'id': character.id, 'name': character.name}, status=201)

@csrf_exempt
def character_create(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        character = Character.objects.create(name=data['name'])
        return JsonResponse({'id': character.id, 'name': character.name}, status=201)

# Serve React App
index = never_cache(TemplateView.as_view(template_name='index.html'))