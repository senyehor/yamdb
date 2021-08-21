from rest_framework import serializers
from rest_framework.fields import empty  # noqa
from rest_framework.validators import UniqueValidator

from api.models import Review, Comment, User, Category, Genre, Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    pub_date = serializers.ReadOnlyField(source='date_iso_format')

    class Meta:
        model = Review
        fields = ('id', 'author', 'text', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    review = ReviewSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'author', 'text', 'review', 'pub_date')


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'bio', 'email', 'role')
        extra_kwargs = {'username': {'required': True, 'validators': [UniqueValidator(User.objects.all())]},
                        'email': {'required': True, 'validators': [UniqueValidator(User.objects.all())]}}


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')
        extra_kwargs = {'name': {'required': True},
                        'slug': {'required': True, 'validators': [UniqueValidator(Category.objects.all())]}}


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class NameSlugField(serializers.RelatedField):

    def __init__(self, model, slug_only=True, **kwargs):
        self.model = model
        self.queryset = model.objects.all()
        self.slug_only = slug_only
        super().__init__(**kwargs)

    def to_internal_value(self, slug):
        return self.model.objects.get(slug=slug)

    def to_representation(self, field):
        if self.slug_only:
            return [obj.slug for obj in field.all()] \
                if hasattr(field, 'all') else field.slug
        return [{'name': obj.name, 'slug': obj.slug} for obj in field.all()] \
            if hasattr(field, 'all') else {'name': field.name, 'slug': field.slug}


class TitleSerializer(serializers.ModelSerializer):

    def __init__(self, instance=None, data=empty, slug_only=False, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.fields['category'] = NameSlugField(model=Category, slug_only=slug_only)
        self.fields['genre'] = NameSlugField(model=Genre, slug_only=slug_only, many=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category', 'rating')
