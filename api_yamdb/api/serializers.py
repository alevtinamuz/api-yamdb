from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Comment, Genre, Review, Title


class NestedCreateMixin:
    """Миксин для создания вложенных объектов."""
    # parent_field ← принимает имя поля ('title' или 'review')
    # parent_verbose_name ← принимает название ('Произведение' или 'Отзыв')

    def create(self, validated_data):
        parent_obj = self.context.get(self.parent_field)
        if not parent_obj:
            raise serializers.ValidationError(
                f'{self.parent_verbose_name} необходимо выбрать')

        author = self.context.get('user')
        if not author:
            raise serializers.ValidationError(
                'Автором может быть только аутентифицированный пользователь')

        if self.Meta.model == Review:
            if Review.objects.filter(title=parent_obj, author=author).exists():
                raise serializers.ValidationError(
                    'Вы уже оставили отзыв на это произведение')

        return self.Meta.model.objects.create(
            **{self.parent_field: parent_obj},
            author=author,
            **validated_data)


class ReviewSerializer(NestedCreateMixin, serializers.ModelSerializer):
    parent_field = 'title'
    parent_verbose_name = 'Произведение'

    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'score', 'author', 'pub_date')
        read_only_fields = ('author', 'pub_date')


class CommentSerializer(NestedCreateMixin, serializers.ModelSerializer):
    parent_field = 'review'
    parent_verbose_name = 'Отзыв'

    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('author', 'pub_date')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def to_representation(self, instance):
        return TitleReadSerializer(instance, context=self.context).data
