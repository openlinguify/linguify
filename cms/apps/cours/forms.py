# -*- coding: utf-8 -*-
"""
Forms for Cours app
Using modern form widgets for better UX
"""
from django import forms
from .models import (
    Course, CourseSection, CourseLesson,
    CourseContent, CourseResource, CoursePricing, CourseDiscount
)


class CourseForm(forms.ModelForm):
    """Form for creating/editing courses."""

    class Meta:
        model = Course
        fields = [
            'title_fr', 'subtitle_fr', 'description_fr',
            'title_en', 'subtitle_en', 'description_en',
            'category', 'tags', 'level', 'language',
            'learning_objectives', 'requirements', 'target_audience',
            'thumbnail', 'promo_video',
            'is_enrollable', 'max_students',
            'has_certificate', 'has_lifetime_access'
        ]
        widgets = {
            'description_fr': forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
            'description_en': forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
            'learning_objectives': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'requirements': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'target_audience': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }


class CourseSectionForm(forms.ModelForm):
    """Form for creating/editing course sections."""

    class Meta:
        model = CourseSection
        fields = [
            'title_fr', 'title_en', 'title_es', 'title_nl',
            'description_fr', 'description_en',
            'learning_objectives', 'order'
        ]
        widgets = {
            'description_fr': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'description_en': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class CourseLessonForm(forms.ModelForm):
    """Form for creating/editing lessons."""

    class Meta:
        model = CourseLesson
        fields = [
            'title_fr', 'title_en', 'description_fr', 'description_en',
            'lesson_type', 'duration_minutes',
            'video_url', 'video_file',
            'is_published', 'is_preview', 'order'
        ]
        widgets = {
            'description_fr': forms.Textarea(attrs={'rows': 3}),
            'description_en': forms.Textarea(attrs={'rows': 3}),
        }


class CourseContentForm(forms.ModelForm):
    """Form for adding content blocks to lessons."""

    class Meta:
        model = CourseContent
        fields = [
            'title', 'content_type',
            'text_content', 'media_file', 'media_url',
            'content_data', 'order'
        ]
        widgets = {
            'text_content': forms.Textarea(attrs={'rows': 10, 'class': 'rich-text-editor'}),
            'content_data': forms.Textarea(attrs={'rows': 5}),
        }


class CourseResourceForm(forms.ModelForm):
    """Form for uploading course resources."""

    class Meta:
        model = CourseResource
        fields = [
            'title', 'description', 'resource_type',
            'file', 'external_link',
            'is_downloadable', 'is_preview', 'requires_completion'
        ]


class CoursePricingForm(forms.ModelForm):
    """Form for course pricing."""

    class Meta:
        model = CoursePricing
        fields = [
            'pricing_type', 'currency', 'price', 'original_price',
            'has_discount', 'discount_percentage',
            'discount_start_date', 'discount_end_date',
            'has_trial', 'trial_period_days'
        ]
        widgets = {
            'discount_start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'discount_end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class CourseDiscountForm(forms.ModelForm):
    """Form for creating discount coupons."""

    class Meta:
        model = CourseDiscount
        fields = [
            'code', 'discount_type', 'discount_value',
            'valid_from', 'valid_until',
            'max_uses', 'max_uses_per_user',
            'minimum_purchase_amount', 'is_active'
        ]
        widgets = {
            'valid_from': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'valid_until': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
