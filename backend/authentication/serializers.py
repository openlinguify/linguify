# backend/django_apps/authentication/serializers.py
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, CoachProfile, Review, UserFeedback
from django.contrib.auth.password_validation import validate_password
from decimal import Decimal

class UserSerializer(serializers.ModelSerializer):
    public_id = serializers.UUIDField(read_only=True, format='hex')
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    email = serializers.EmailField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        # Expose only necessary fields for viewing
        fields = [
            'public_id', 'username', 'first_name', 'last_name', 'email', 'age', 'gender',
            'profile_picture', 'bio', 'native_language', 'target_language',
            'language_level', 'objectives', 'is_active', 'is_coach', 'is_subscribed',
            'is_superuser', 'is_staff', 'created_at', 'updated_at'
        ]
        # Mark sensitive fields as read-only
        read_only_fields = [
            'id', 'email', 'is_active', 'is_superuser', 'is_staff',
            'created_at', 'updated_at'
        ]

    def update(self, instance, validated_data):
        "To make an update to the user profile"
        for i in self.Meta.fields:
            if i not in self.Meta.read_only_fields and i in validated_data:
                setattr(instance, i, validated_data[i])
        instance.save()
        return instance
    
    
                

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email', 'age', 'gender',
            'profile_picture', 'bio', 'native_language', 'target_language',
            'language_level', 'objectives', 'password', 'password2'
        ]


    def validate(self, attrs):
        """
        Validate the password and target language fields.

        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Your passwords must be the same."})
        if attrs['native_language'] == attrs['target_language']:
            raise serializers.ValidationError({"target_language": "Your target language must be different from your native language."})
        return attrs

    def create(self, validated_data):
        """
        Create a new user instance.

        """
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            age=validated_data.get('age'),
            gender=validated_data.get('gender'),
            profile_picture=validated_data.get('profile_picture'),
            bio=validated_data.get('bio'),
            native_language=validated_data.get('native_language'),
            target_language=validated_data.get('target_language'),
            language_level=validated_data.get('language_level'),
            objectives=validated_data.get('objectives'),
        )
        return user


# 3. UserProfileUpdateSerializer: For updating user profile data
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'age', 'gender',
            'profile_picture', 'bio', 'native_language', 'target_language',
            'language_level', 'objectives'
        ]


# 4. CoachProfileSerializer: For managing coach profiles
class CoachProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    commission_rate = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    commission_amount = serializers.SerializerMethodField(read_only=True)
    commission_override = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = CoachProfile
        fields = [
            'user', 'coaching_languages', 'price_per_hour', 'availability', 'description', 'bio',
            'commission_rate', 'commission_override', 'commission_amount'
        ]
        read_only_fields = ['user', 'commission_rate', 'commission_override', 'commission_amount']

    @staticmethod
    def get_commission_amount(obj):
        return obj.calculate_commission()

    @staticmethod
    def validate_price_per_hour(value):
        """
        Validates that the price per hour is within an acceptable range.
        """
        # Check that the price is greater than zero
        if value <= 0:
            raise serializers.ValidationError("Price per hour must be greater than zero.")

        # Check if the price is too high
        MAX_PRICE_PER_HOUR = Decimal('150.00')
        if value > MAX_PRICE_PER_HOUR:
            raise serializers.ValidationError(
                f"Price per hour must be less than {MAX_PRICE_PER_HOUR}. Please contact us if you need to set a higher price.")

        # Ensure the value has a reasonable number of decimal places (max 2)
        if value.as_tuple().exponent < -2:
            raise serializers.ValidationError("Price per hour cannot have more than two decimal places.")

        return value

    # Validation for availability
    @staticmethod
    def validate_availability(value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Availability cannot be empty.")
        if len(value) > 1000:
            raise serializers.ValidationError("Availability description is too long. Please limit to 1000 characters.")

        return value

    # Global validation method to check dependencies between fields
    def validate(self, attrs):
        price_per_hour = attrs.get('price_per_hour')
        availability = attrs.get('availability')

        if price_per_hour and price_per_hour > Decimal('100.00') and (
                not availability or len(availability.strip()) == 0):
            raise serializers.ValidationError(
                "If the price per hour exceeds 100, availability must be clearly specified.")

        return attrs

    # Update method to use validated_data effectively
    def update(self, instance, validated_data):
        """
        Update the coach profile using validated data, ensuring business logic is respected.
        """
        instance.coaching_languages = validated_data.get('coaching_languages', instance.coaching_languages)
        instance.price_per_hour = validated_data.get('price_per_hour', instance.price_per_hour)
        instance.availability = validated_data.get('availability', instance.availability)
        instance.description = validated_data.get('description', instance.description)
        instance.bio = validated_data.get('bio', instance.bio)

        instance.save()
        return instance

# 5. ReviewSerializer: For managing user reviews of coaches
class ReviewSerializer(serializers.ModelSerializer):
    reviewer_details = serializers.SerializerMethodField(read_only=True)
    coach_details = serializers.SerializerMethodField(read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, min_value=0.00, max_value=5.00, required=True)
    coach = serializers.PrimaryKeyRelatedField(queryset=CoachProfile.objects.all(), required=True)

    class Meta:
        model = Review
        fields = ['coach', 'rating', 'comment', 'review_date', 'reviewer_details', 'coach_details']
        read_only_fields = ['review_date', 'reviewer_details', 'coach_details']

    # Method to provide more detailed information about the reviewer
    @staticmethod
    def get_reviewer_details(obj):
        return {
            "username": obj.reviewer.username,
            "first_name": obj.reviewer.first_name,
            "last_name": obj.reviewer.last_name,
            "profile_picture": obj.reviewer.profile_picture.url if obj.reviewer.profile_picture else None
        }

    # Method to provide more detailed information about the coach being reviewed
    @staticmethod
    def get_coach_details(obj):
        return {
            "username": obj.coach.user.username,
            "coaching_languages": obj.coach.coaching_languages,
            "price_per_hour": obj.coach.price_per_hour,
            "availability": obj.coach.availability,
        }

    # Custom validation to ensure appropriate relationships and no duplicate reviews
    def validate(self, attrs):
        user = self.context['request'].user
        coach = attrs.get('coach')

        # Check if the user has already reviewed this coach
        if Review.objects.filter(reviewer=user, coach=coach).exists():
            raise serializers.ValidationError({"reviewer": "You have already reviewed this coach."})

        # Check if the targeted coach is actually a coach
        if not coach.user.is_coach:
            raise serializers.ValidationError({"coach": "The selected user is not a coach."})

        # Check if the reviewer is trying to review themselves
        if coach.user == user:
            raise serializers.ValidationError({"reviewer": "You cannot review yourself."})

        return attrs

    # Automatically set the reviewer to the logged-in user
    def create(self, validated_data):
        validated_data['reviewer'] = self.context['request'].user
        return super().create(validated_data)

# 6. UserFeedbackSerializer: For managing feedback by users
class UserFeedbackSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True, write_only=True)

    class Meta:
        model = UserFeedback
        fields = ['user', 'feedback_type', 'feedback_content', 'feedback_date']
        read_only_fields = ['feedback_date']

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: User):
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email
        # ...

        return token
