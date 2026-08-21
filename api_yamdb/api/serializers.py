from rest_framework import serializers
from rest_framework.relations import SlugRelatedField


from reviews.models import Comment, Review, Title, User


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'score', 'author', 'pub_date')
        read_only_fields = ('author', 'pub_date')

    def create(self, validated_data):
        title = self.context.get('title')
        if not title:
            raise serializers.ValidationError('Title is required')

        author = self.context.get('user')
        if not author:
            raise serializers.ValidationError('User is not authenticated')

        if Review.objects.filter(title=title, author=author).exists():
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на это произведение')

        return Review.objects.create(
            title=title,
            author=author,
            **validated_data)


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('author', 'pub_date')

    def create(self, validated_data):
        review = self.context.get('review')
        if not review:
            raise serializers.ValidationError('Review is required')

        author = self.context.get('user')
        if not author:
            raise serializers.ValidationError('User is not authenticated')

        return Comment.objects.create(
            review=review,
            author=author,
            **validated_data
        )