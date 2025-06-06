from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import (
    ReportViewSet, ReportModifierViewSet, JobViewSet,
    EventViewSet, EventGroupViewSet, RingEventViewSet,
    BoxEventViewSet, GeoEventViewSet
)

router = DefaultRouter()
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'report-modifiers', ReportModifierViewSet, basename='report-modifier')
router.register(r'jobs', JobViewSet, basename='job')
router.register(r'events', EventViewSet, basename='event')
router.register(r'event-groups', EventGroupViewSet, basename='event-group')
router.register(r'ring-events', RingEventViewSet, basename='ring-event')
router.register(r'box-events', BoxEventViewSet, basename='box-event')
router.register(r'geo-events', GeoEventViewSet, basename='geo-event')

urlpatterns = [
    path('', include(router.urls)),
]
