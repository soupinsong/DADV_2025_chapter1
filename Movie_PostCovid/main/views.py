# main/views.py
from rest_framework import viewsets, filters
from rest_framework.response import Response       
from rest_framework.decorators import action   
from .models import Movie, BoxOfficeMonthly
from .serializers import MovieSerializer, BoxOfficeMonthlySerializer

class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Movie.objects.all().order_by('title')
    serializer_class = MovieSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'distributor', 'producer', 'genre']

   
    @action(detail=True, methods=['get'])
    def rank_trend(self, request, pk=None):
        
        movie = self.get_object() 
        
        qs = BoxOfficeMonthly.objects.filter(movie=movie).order_by('year', 'month')
        
        data = [
            {"month": f"{q.year}-{q.month:02}", "rank": q.rank} 
            for q in qs
        ]
        return Response(data)
   

class BoxOfficeMonthlyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BoxOfficeMonthlySerializer
    
    def get_queryset(self):
        
        qs = BoxOfficeMonthly.objects.select_related('movie').order_by('year','month','rank')
        y = self.request.query_params.get('year')
        m = self.request.query_params.get('month')
        t = self.request.query_params.get('title')
        g = self.request.query_params.get('genre')
        
        if y: qs = qs.filter(year=int(y))
        if m: qs = qs.filter(month=int(m))
        if t: qs = qs.filter(movie__title__icontains=t)
        if g: qs = qs.filter(movie__genre__icontains=g)
        
        return qs