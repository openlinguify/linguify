# -*- coding: utf-8 -*-
"""
Views for Cours app
All views support HTMX for asynchronous interactions
"""
from .course_views import (
    CourseListView,
    CourseCreateView,
    CourseDetailView,
    CourseUpdateView,
    CourseDeleteView,
    CoursePublishView,
)

from .section_views import (
    SectionCreateView,
    SectionUpdateView,
    SectionDeleteView,
    SectionReorderView,
)

from .lesson_views import (
    LessonCreateView,
    LessonUpdateView,
    LessonDeleteView,
    LessonReorderView,
)

from .content_views import (
    ContentCreateView,
    ContentUpdateView,
    ContentDeleteView,
)

from .resource_views import (
    ResourceUploadView,
    ResourceDeleteView,
)

from .enrollment_views import (
    EnrollmentListView,
    EnrollmentStatsView,
)

from .review_views import (
    ReviewListView,
    ReviewModerateView,
)

from .pricing_views import (
    PricingUpdateView,
    DiscountCreateView,
)

__all__ = [
    # Course views
    'CourseListView',
    'CourseCreateView',
    'CourseDetailView',
    'CourseUpdateView',
    'CourseDeleteView',
    'CoursePublishView',

    # Section views
    'SectionCreateView',
    'SectionUpdateView',
    'SectionDeleteView',
    'SectionReorderView',

    # Lesson views
    'LessonCreateView',
    'LessonUpdateView',
    'LessonDeleteView',
    'LessonReorderView',

    # Content views
    'ContentCreateView',
    'ContentUpdateView',
    'ContentDeleteView',

    # Resource views
    'ResourceUploadView',
    'ResourceDeleteView',

    # Enrollment views
    'EnrollmentListView',
    'EnrollmentStatsView',

    # Review views
    'ReviewListView',
    'ReviewModerateView',

    # Pricing views
    'PricingUpdateView',
    'DiscountCreateView',
]
