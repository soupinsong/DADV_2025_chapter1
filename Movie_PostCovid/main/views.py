from rest_framework import viewsets, filters
from .models import Movie, BoxOfficeMonthly
from .serializers import MovieSerializer, BoxOfficeMonthlySerializer

class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Movie.objects.all().order_by('title')
    serializer_class = MovieSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title','distributor','producer','genre']

class BoxOfficeMonthlyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BoxOfficeMonthlySerializer
    def get_queryset(self):
        qs = BoxOfficeMonthly.objects.select_related('movie').order_by('year','month','rank')
        y = self.request.query_params.get('year')
        m = self.request.query_params.get('month')
        t = self.request.query_params.get('title')
        if y: qs = qs.filter(year=int(y))
        if m: qs = qs.filter(month=int(m))
        if t: qs = qs.filter(movie__title__icontains=t)
        return qs
