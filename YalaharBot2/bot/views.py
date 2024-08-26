from rest_framework import viewsets
from .models import DiscordUser, Character, DiscordUserAndCharacters
from .serializers import DiscordUserSerializer, CharacterSerializer, DiscordUserAndCharactersSerializer
from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache

class DiscordUserViewSet(viewsets.ModelViewSet):
    queryset = DiscordUser.objects.all()
    serializer_class = DiscordUserSerializer

class CharacterViewSet(viewsets.ModelViewSet):
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer

class DiscordUserAndCharactersViewSet(viewsets.ModelViewSet):
    queryset = DiscordUserAndCharacters.objects.all()
    serializer_class = DiscordUserAndCharactersSerializer

# Serve React App
index = never_cache(TemplateView.as_view(template_name='index.html'))