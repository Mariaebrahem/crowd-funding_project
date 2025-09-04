import django_filters
from projects.models import Project


class ProjectFilter(django_filters.FilterSet):
    search_tags = django_filters.CharFilter(
        field_name="tags__name", lookup_expr="icontains"
    )
    search_titles = django_filters.CharFilter(
        field_name="title", lookup_expr="icontains"
    )
    search_categories = django_filters.CharFilter(
        field_name="category__name", lookup_expr="icontains"
    )

    class Meta:
        model = Project
        fields = ["search_tags", "search_titles", "search_categories"]
