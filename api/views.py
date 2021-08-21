from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import request as rq, status
from rest_framework.decorators import permission_classes as perm_classes
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from api.business_logic import send_code_to_user_and_save_it, user_already_has_review_on_title, \
    get_code_if_email_was_sent_else_none, create_token_for_user_by_email, \
    check_data_contains_only_allowed_to_modify_fields
from api.decorators import allowed_http_methods
from api.errors import EmailNotValid, BadRequest
from api.models import User, Title, Category, Genre, Review, Comment
from api.permissions import IsAdminElseReadOnly, IsAdminOrModeratorOrAuthorElseReadOnly, IsAdmin
from api.search_filters import TitleFilter
from api.serializers import ReviewSerializer, TitleSerializer, CommentSerializer, UserSerializer, CategorySerializer, \
    GenreSerializer


class CategoryView(ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    filter_backends = [SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'
    permission_classes = [IsAdminElseReadOnly]
    http_method_names = ['get', 'post', 'delete']

    @allowed_http_methods([None])
    def retrieve(self, request, *args, **kwargs):
        """Not supposed to happen"""
        pass


class GenreView(ModelViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    lookup_field = 'slug'
    permission_classes = [IsAdminElseReadOnly]
    http_method_names = ['get', 'post', 'delete']
    search_fields = ['name']
    filter_backends = [SearchFilter]

    @allowed_http_methods([None])
    def retrieve(self, request, *args, **kwargs):
        """Not supposed to happen"""
        pass


class CommentView(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAdminOrModeratorOrAuthorElseReadOnly]

    def get_queryset(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_pk')).comments.all()

    def get_object(self):
        requested_comment = get_object_or_404(Comment, id=self.kwargs.get('pk'))
        self.check_object_permissions(self.request, requested_comment)
        return requested_comment

    def perform_create(self, serializer):
        author = self.request.user
        review = get_object_or_404(Review, id=self.kwargs.get('review_pk'))
        serializer.save(author=author, review=review)


class TitleView(ModelViewSet):
    serializer_class = TitleSerializer
    permission_classes = [IsAdminElseReadOnly]
    queryset = Title.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter


class ReviewView(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminOrModeratorOrAuthorElseReadOnly]

    def get_queryset(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_pk')).reviews.all()

    def get_object(self):
        requested_review = get_object_or_404(Review, id=self.kwargs.get('pk'))
        self.check_object_permissions(self.request, requested_review)
        return requested_review

    @perm_classes([IsAuthenticated])
    def perform_create(self, serializer):
        user = self.request.user
        title = get_object_or_404(Title, id=self.kwargs.get('title_pk'))
        if user_already_has_review_on_title(user, title):
            raise BadRequest
        serializer.save(author=user, title=title)


def get_user_email_and_send_code_to_it(request: rq):
    if request.user.is_authenticated and request.user.is_admin:
        User.objects.create(**request.data)
        return Response(data={'success': 'User was created by admin bypassing email'}, status=status.HTTP_200_OK)
    user_email = request.data.get('email', None)
    if user_email:
        try:
            send_code_to_user_and_save_it(user_email)
        except EmailNotValid:
            return Response(data={'error_detail': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'success': 'Email was sent'}, status=status.HTTP_200_OK)

    return Response(data={'error_detail': 'Email not provided'}, status=status.HTTP_400_BAD_REQUEST)


class UserAdminView(ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'username'
    queryset = User.objects.all()

    def perform_create(self, serializer):
        request_data = self.request.data
        user_role = request_data.get('role', None)
        if user_role:
            user_role = User.convert_verbose_role_to_db_value(user_role)
            serializer.save(role=user_role)
        else:
            serializer.save()


class UserProfileView(ViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch']

    def get_own_profile_info(self, request):
        return Response(UserSerializer(request.user).data)

    def change_own_profile_info(self, request):
        if check_data_contains_only_allowed_to_modify_fields(request.data):
            user = request.user
            for field_name, value in request.data.items():
                setattr(user, field_name, value)
            user.save()
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={'error_detail': f'List of allowed fields is {User.ALLOWED_FIELDS_TO_FILL}'})


def verify_user_code(request: rq):
    user_email = request.data.get('email', None)
    registration_confirmation_code = request.data.get('code', None)
    if not user_email:
        return Response(data={'error_detail': 'Email not provided'}, status=status.HTTP_400_BAD_REQUEST)
    if not registration_confirmation_code:
        return Response(data={'error_detail': 'Code not provided'}, status=status.HTTP_400_BAD_REQUEST)

    if get_code_if_email_was_sent_else_none(user_email) == registration_confirmation_code:
        return Response(status=status.HTTP_200_OK, data=create_token_for_user_by_email(user_email))
