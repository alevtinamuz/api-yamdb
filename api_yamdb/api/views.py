from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.db.models.functions import Round
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST
)
from rest_framework_simplejwt.tokens import AccessToken

from .filters import TitleFilter
from reviews.models import User, Category, Comment, Genre, Review, Title
from .permissions import (
    IsAdmin, IsAdminOrReadOnly, IsAdminOrModeratorOrReadOnly
)
from .serializers import (
    SignUpSerializer, TokenSerializer, UserSerializer,
    ReviewSerializer, CommentSerializer,
    CategorySerializer, GenreSerializer,
    TitleReadSerializer, TitleWriteSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def sign_up(request):
    serializer = SignUpSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        user, _ = User.objects.get_or_create(
            username=username,
            email=email
        )
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            'YaMDb: Ваш код подтверждения',
            f'Код: {confirmation_code}',
            None,
            [email]
        )
        return Response(serializer.data, status=HTTP_200_OK)
    return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    serializer = TokenSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']
        user = get_object_or_404(User, username=username)
        if not default_token_generator.check_token(user, confirmation_code):
            return Response({
                'error': 'Неверный код подтверждения'
            }, status=HTTP_400_BAD_REQUEST)
        token = AccessToken.for_user(user)
        return Response(
            {'token': f'{token}'},
            status=HTTP_200_OK
        )
    return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    permission_classes = (IsAdmin,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data, status=HTTP_200_OK)
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


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
    permission_classes = (IsAdminOrModeratorOrReadOnly,)

    parent_model = Title
    parent_field = 'title'
    parent_id_kwarg = 'title_id'


class CommentViewSet(NestedModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAdminOrModeratorOrReadOnly,)

    parent_model = Review
    parent_field = 'review'
    parent_id_kwarg = 'review_id'


class BaseCategoryGenreViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAdminOrReadOnly,)
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
    permission_classes = (IsAdminOrReadOnly,)
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
            rating=Round(Avg('reviews__score'))
        )
