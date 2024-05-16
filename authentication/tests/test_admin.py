import pytest
from django.contrib import admin
from authentication.models import User
from authentication.admin import CustomerUserAdmin, UserAdmin

@pytest.fixture
def user():
    return User.objects.create(email='test@test.com', password='testpass123')

def admin_site_register_user(user):
    admin.site.register(User, CustomerUserAdmin)
    assert isinstance(admin.site._registry[User], CustomerUserAdmin)

def admin_site_unregister_user(user):
    admin.site.unregister(User)
    assert User not in admin.site._registry

def customer_user_admin_display_fields(user):
    customer_user_admin = CustomerUserAdmin(User, admin.site)
    assert customer_user_admin.list_display == ('id', 'email', 'first_name', 'last_name', 'mother_language', 'learning_language', 'is_staff', 'is_active', 'date_joined', 'role', 'objectives', 'level_target_language')

def user_admin_display_fields(user):
    user_admin = UserAdmin(User, admin.site)
    assert user_admin.list_display == ('id', 'email', 'first_name', 'last_name', 'mother_language', 'learning_language', 'is_staff', 'is_active', 'date_joined', 'role', 'objectives', 'level_target_language')

def test_customer_user_admin_search_fields():
    customer_user_admin = CustomerUserAdmin(User, admin.site)
    assert customer_user_admin.search_fields == ('email',)

def test_user_admin_search_fields():
    user_admin = UserAdmin(User, admin.site)
    assert user_admin.search_fields == ('email',)

def test_customer_user_admin_ordering():
    customer_user_admin = CustomerUserAdmin(User, admin.site)
    assert customer_user_admin.ordering == ('email',)

def test_user_admin_ordering():
    user_admin = UserAdmin(User, admin.site)
    assert user_admin.ordering == ('email',)