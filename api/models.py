from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from api.errors import BadVerboseRole


class User(AbstractUser):
    USER = 1
    MODERATOR = 2
    ADMIN = 3
    DJANGO_ADMIN = 4

    ALLOWED_FIELDS_TO_FILL = ('username', 'first_name', 'last_name', 'bio', 'email')

    ROLE_CHOICES = (
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
        (DJANGO_ADMIN, 'django admin')
    )
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=False, default=USER)
    bio = models.CharField(max_length=300, blank=True)

    @property
    def is_admin(self):
        return self.role > User.MODERATOR

    @property
    def is_moderator(self):
        return self.role == User.MODERATOR

    @classmethod
    def convert_verbose_role_to_db_value(cls, role: str):
        converted_value = None
        for db_value, verbose_name in cls.ROLE_CHOICES:
            if role == verbose_name:
                converted_value = db_value
                break
        else:
            raise BadVerboseRole
        return converted_value


class Title(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    year = models.PositiveSmallIntegerField()
    category = models.ForeignKey('Category', on_delete=models.DO_NOTHING, related_name='titles')
    description = models.CharField(max_length=255, blank=True)
    rating = models.FloatField(null=True)
    genre = models.ManyToManyField(
        'Genre',
        related_name='titles',
        blank=True,
        default=None)

    def update_rating(self):
        reviews = self.reviews.all()
        self.rating = round(sum([review.score for review in reviews]) / len(reviews), 2)
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = 'Categories'


class Genre(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    text = models.CharField(max_length=300)
    score = models.IntegerField(choices=enumerate(range(11)), validators=[MaxValueValidator(10), MinValueValidator(1)])
    pub_date = models.DateTimeField(default=timezone.now)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        self.title.update_rating()

    def delete(self, using=None, keep_parents=False):
        result = super().delete(using, keep_parents)
        self.title.update_rating()
        return result

    def date_iso_format(self):
        return self.pub_date.isoformat()


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.CharField(max_length=255)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    pub_date = models.DateTimeField(auto_now_add=True)


class EmailCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=36)
