import pytest
from rest_framework.test import APIClient
from rest_framework import status
from .models import User, CoachProfile

@pytest.mark.django_db
class TestUserAPI:
    def setup_method(self):
        self.client = APIClient()
        self.superuser = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass",
            first_name="Test",
            last_name="User",
            age=25
        )

    def test_register_user(self):
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
            "first_name": "New",
            "last_name": "User",
            "age": 30
        }
        response = self.client.post("/api/authentication/users/register/", payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["message"] == "User registered successfully."

    def test_get_user_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/authentication/users/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == self.user.email

    def test_deactivate_user(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(f"/api/authentication/users/{self.user.public_id}/deactivate/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "User deactivated successfully."
        self.user.refresh_from_db()
        assert self.user.is_active is False

    def test_reactivate_user(self):
        self.client.force_authenticate(user=self.superuser)
        self.user.deactivate_user()
        response = self.client.post(f"/api/authentication/users/{self.user.public_id}/reactivate/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "User reactivated successfully."
        self.user.refresh_from_db()
        assert self.user.is_active is True

    def test_get_users_as_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get("/api/authentication/users/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2

    def test_get_users_as_regular_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/authentication/users/")
        assert response.status_code == status.HTTP_200_OK
        assert not any(user["is_superuser"] for user in response.data)


@pytest.mark.django_db
class TestCoachProfileAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="coachuser",
            email="coach@example.com",
            password="coachpass",
            first_name="Coach",
            last_name="User",
            is_coach=True
        )
        self.coach_profile = CoachProfile.objects.create(
            user=self.user,
            coaching_languages="EN",
            price_per_hour=50.00,
            availability="Monday to Friday",
            description="Experienced English coach."
        )

    def test_get_coach_profiles(self):
        response = self.client.get("/api/authentication/coaches/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_update_availability(self):
        self.client.force_authenticate(user=self.user)
        payload = {"availability": "Weekends only"}
        response = self.client.patch(f"/api/authentication/coaches/{self.coach_profile.id}/update_availability/", payload)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "Availability updated successfully."
        self.coach_profile.refresh_from_db()
        assert self.coach_profile.availability == "Weekends only"

    def test_update_price(self):
        self.client.force_authenticate(user=self.user)
        payload = {"price_per_hour": 75.00}
        response = self.client.patch(f"/api/authentication/coaches/{self.coach_profile.id}/update_price/", payload)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "Price updated successfully."
        self.coach_profile.refresh_from_db()
        assert self.coach_profile.price_per_hour == 75.00
