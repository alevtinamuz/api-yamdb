from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Value, FloatField
from django.db.models.functions import Coalesce, Round
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .filters import TitleFilter
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from reviews.models import Category, Comment, Genre, Review, Title
from .serializers import (
    ReviewSerializer, CommentSerializer,
    CategorySerializer, GenreSerializer,
    TitleReadSerializer, TitleWriteSerializer
)


class NestedModelViewSet(viewsets.ModelViewSet):
    """Базовый вьюсет для вложенных ресурсов."""
    # parent_model ← принимает модель (Title или Review)
    # parent_field ← принимает имя поля ('title' или 'review')
    # parent_id_kwarg ← принимает имя параметра из URL
    # ('title_id' или 'review_id')

    def get_parent_object(self):
        """Получает объект-родитель по параметру из URL."""
        parent_id = self.kwargs.get(self.parent_id_kwarg)
        return get_object_or_404(self.parent_model, id=parent_id)

    def get_queryset(self):
        """Фильтрует queryset по родительскому объекту."""
        parent_obj = self.get_parent_object()
        filter_kwargs = {self.parent_field: parent_obj}
        return self.queryset.filter(**filter_kwargs)

    def get_serializer_context(self):
        """Добавляет в контекст родительский объект и пользователя."""
        context = super().get_serializer_context()
        context[self.parent_field] = self.get_parent_object()
        context['user'] = self.request.user
        return context

    def perform_create(self, serializer):
        """При создании подставляет автора и родительский объект."""
        parent_obj = self.get_parent_object()
        serializer.save(
            author=self.request.user,
            **{self.parent_field: parent_obj}
        )


class ReviewViewSet(NestedModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    parent_model = Title
    parent_field = 'title'
    parent_id_kwarg = 'title_id'


class CommentViewSet(NestedModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    parent_model = Review
    parent_field = 'review'
    parent_id_kwarg = 'review_id'


class BaseCategoryGenreViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    pagination_class = PageNumberPagination


class CategoryViewSet(BaseCategoryGenreViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(BaseCategoryGenreViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return TitleWriteSerializer
        return TitleReadSerializer

    def get_queryset(self):
        """Возвращает произведения с аннотированным рейтингом."""
        return Title.objects.annotate(
            rating=Round(Coalesce(
                Avg('reviews__score'), Value(0, output_field=FloatField())), 2))
