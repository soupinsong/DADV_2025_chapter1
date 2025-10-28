# main/serializers.py
from rest_framework import serializers
from .models import Movie, BoxOfficeMonthly

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'

class BoxOfficeMonthlySerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source='movie.title', read_only=True)
    class Meta:
        model = BoxOfficeMonthly
        fields = ['id','year','month','rank','sales','audience','screens','show_count','movie','movie_title']
