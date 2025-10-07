# -*- coding: utf-8 -*-
"""
Django Admin configuration for Cours app
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Course, CourseCategory, CourseTag,
    CourseSection, CourseLesson, CourseContent,
    CourseEnrollment, CoursePricing, CourseDiscount,
    CourseReview, CourseRating, CourseResource
)


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'order', 'is_active', 'course_count']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'category_type']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

    def course_count(self, obj):
        return obj.courses.count()
    course_count.short_description = 'Courses'


@admin.register(CourseTag)
class CourseTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'usage_count']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


class CourseSectionInline(admin.TabularInline):
    model = CourseSection
    extra = 0
    fields = ['order', 'title_fr', 'is_published', 'lesson_count']
    readonly_fields = ['lesson_count']


class CoursePricingInline(admin.StackedInline):
    model = CoursePricing
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        'title_fr', 'teacher', 'category', 'level',
        'status_badge', 'enrollment_count', 'average_rating',
        'created_at'
    ]
    list_filter = [
        'status', 'level', 'category', 'is_published',
        'is_featured', 'is_bestseller', 'created_at'
    ]
    search_fields = ['title_fr', 'title_en', 'teacher__full_name']
    prepopulated_fields = {'slug': ('title_en',)}
    filter_horizontal = ['tags', 'co_instructors']
    inlines = [CoursePricingInline, CourseSectionInline]

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'teacher', 'co_instructors', 'slug', 'status'
            )
        }),
        ('Course Content (French)', {
            'fields': (
                'title_fr', 'subtitle_fr', 'description_fr'
            )
        }),
        ('Course Content (English)', {
            'fields': (
                'title_en', 'subtitle_en', 'description_en'
            ),
            'classes': ('collapse',)
        }),
        ('Course Content (Spanish)', {
            'fields': (
                'title_es', 'subtitle_es', 'description_es'
            ),
            'classes': ('collapse',)
        }),
        ('Course Content (Dutch)', {
            'fields': (
                'title_nl', 'subtitle_nl', 'description_nl'
            ),
            'classes': ('collapse',)
        }),
        ('Course Details', {
            'fields': (
                'category', 'tags', 'level', 'language',
                'learning_objectives', 'requirements', 'target_audience'
            )
        }),
        ('Media', {
            'fields': ('thumbnail', 'promo_video')
        }),
        ('Enrollment', {
            'fields': (
                'is_enrollable', 'max_students', 'enrollment_count'
            )
        }),
        ('Features', {
            'fields': (
                'has_certificate', 'has_lifetime_access',
                'is_featured', 'is_bestseller'
            )
        }),
        ('Statistics', {
            'fields': (
                'estimated_duration_hours', 'total_lectures', 'total_resources',
                'average_rating', 'total_reviews', 'view_count', 'completion_rate'
            ),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = [
        'enrollment_count', 'average_rating', 'total_reviews',
        'view_count', 'completion_rate'
    ]

    def status_badge(self, obj):
        colors = {
            'draft': 'gray',
            'in_review': 'orange',
            'published': 'green',
            'archived': 'red',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    actions = ['publish_courses', 'unpublish_courses', 'archive_courses']

    def publish_courses(self, request, queryset):
        for course in queryset:
            course.publish()
        self.message_user(request, f'{queryset.count()} courses published.')
    publish_courses.short_description = 'Publish selected courses'

    def unpublish_courses(self, request, queryset):
        for course in queryset:
            course.unpublish()
        self.message_user(request, f'{queryset.count()} courses unpublished.')
    unpublish_courses.short_description = 'Unpublish selected courses'

    def archive_courses(self, request, queryset):
        for course in queryset:
            course.archive()
        self.message_user(request, f'{queryset.count()} courses archived.')
    archive_courses.short_description = 'Archive selected courses'


class CourseLessonInline(admin.TabularInline):
    model = CourseLesson
    extra = 0
    fields = ['order', 'title_fr', 'lesson_type', 'duration_minutes', 'is_published']


@admin.register(CourseSection)
class CourseSectionAdmin(admin.ModelAdmin):
    list_display = ['title_fr', 'course', 'order', 'lesson_count', 'is_published']
    list_filter = ['is_published', 'course']
    search_fields = ['title_fr', 'title_en', 'course__title_fr']
    inlines = [CourseLessonInline]


@admin.register(CourseLesson)
class CourseLessonAdmin(admin.ModelAdmin):
    list_display = [
        'title_fr', 'course', 'section', 'order',
        'lesson_type', 'duration_minutes', 'is_published', 'is_preview'
    ]
    list_filter = ['lesson_type', 'is_published', 'is_preview', 'course']
    search_fields = ['title_fr', 'title_en', 'course__title_fr']


@admin.register(CourseContent)
class CourseContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'content_type', 'order', 'is_published']
    list_filter = ['content_type', 'is_published']
    search_fields = ['title', 'lesson__title_fr']


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'course', 'status', 'progress_percentage',
        'enrolled_at', 'is_completed', 'certificate_issued'
    ]
    list_filter = [
        'status', 'is_completed', 'certificate_issued',
        'has_lifetime_access', 'enrolled_at'
    ]
    search_fields = [
        'student__username', 'student__email',
        'course__title_fr', 'payment_reference'
    ]
    readonly_fields = ['enrolled_at', 'completed_at', 'certificate_issued_at']


@admin.register(CoursePricing)
class CoursePricingAdmin(admin.ModelAdmin):
    list_display = [
        'course', 'pricing_type', 'price', 'currency',
        'discount_badge', 'final_price'
    ]
    list_filter = ['pricing_type', 'currency', 'has_discount', 'has_trial']
    search_fields = ['course__title_fr']

    def discount_badge(self, obj):
        if obj.has_discount and obj.is_discount_active():
            return format_html(
                '<span style="background-color: red; color: white; padding: 3px 10px; border-radius: 3px;">-{}%</span>',
                obj.discount_percentage
            )
        return '-'
    discount_badge.short_description = 'Discount'


@admin.register(CourseDiscount)
class CourseDiscountAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'course', 'discount_type', 'discount_value',
        'is_active', 'current_uses', 'max_uses', 'valid_until'
    ]
    list_filter = ['is_active', 'discount_type', 'created_at']
    search_fields = ['code', 'course__title_fr']


@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = [
        'course', 'student', 'rating_stars', 'is_published',
        'is_verified_purchase', 'helpful_count', 'created_at'
    ]
    list_filter = [
        'rating', 'is_published', 'is_verified_purchase', 'created_at'
    ]
    search_fields = ['course__title_fr', 'student__username', 'title', 'review']
    readonly_fields = ['helpful_count', 'report_count']

    def rating_stars(self, obj):
        return '⭐' * obj.rating
    rating_stars.short_description = 'Rating'


@admin.register(CourseRating)
class CourseRatingAdmin(admin.ModelAdmin):
    list_display = [
        'course', 'total_ratings', 'five_star_count',
        'four_star_count', 'three_star_count', 'two_star_count', 'one_star_count'
    ]
    search_fields = ['course__title_fr']


@admin.register(CourseResource)
class CourseResourceAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'course', 'lesson', 'resource_type',
        'file_size_display', 'download_count', 'is_downloadable'
    ]
    list_filter = ['resource_type', 'is_downloadable', 'is_preview']
    search_fields = ['title', 'course__title_fr', 'lesson__title_fr']
