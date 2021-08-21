from django.urls import path
from rest_framework_nested import routers

from api.views import TitleView, ReviewView, \
    CommentView, get_user_email_and_send_code_to_it, verify_user_code, UserAdminView, UserProfileView, CategoryView, \
    GenreView

main_router = routers.SimpleRouter()
main_router.register(prefix='titles', viewset=TitleView, basename='titles')
main_router.register(prefix='users', viewset=UserAdminView, basename='users')
main_router.register(prefix='categories', viewset=CategoryView, basename='categories')
main_router.register(prefix='genres', viewset=GenreView, basename='genres')

reviews_router = routers.NestedSimpleRouter(parent_router=main_router, parent_prefix='titles', lookup='title')
reviews_router.register(prefix='reviews', viewset=ReviewView, basename='reviews')

comments_router = routers.NestedSimpleRouter(parent_router=reviews_router, parent_prefix='reviews', lookup='review')
comments_router.register(prefix='comments', viewset=CommentView, basename='comments')

user_profile_view = UserProfileView.as_view({'get': 'get_own_profile_info', 'patch': 'change_own_profile_info'})

urlpatterns = [
    path('auth/email/', get_user_email_and_send_code_to_it,
         name='get_user_email_and_send_code_to_it'),
    path('auth/token/', verify_user_code, name='verify_user_code'),
    path('users/me/', user_profile_view, name='self_info'),
]
urlpatterns += main_router.urls + reviews_router.urls + comments_router.urls
