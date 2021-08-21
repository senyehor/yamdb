from django_filters import rest_framework as filters

from api.models import Title


class TitleFilter(filters.FilterSet):
    genre = filters.CharFilter(field_name='genre', method='slugs__exact')
    category = filters.CharFilter(field_name='category', lookup_expr='slug__exact')
    name = filters.CharFilter(field_name='name', lookup_expr='iexact')

    def slugs__exact(self, queryset, name, value):
        return queryset.filter(genre__slug__exact=value)

    class Meta:
        model = Title
        fields = ['name', 'genre', 'category', 'year']
