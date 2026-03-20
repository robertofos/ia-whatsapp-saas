"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.tenants.views import TenantViewSet
from apps.conversations.views import ConversationViewSet
from apps.messaging.views import MessageViewSet, whatsapp_webhook_mock, pending_messages_view
from apps.messaging.views import  approve_message_view, reject_message_view, edit_and_approve_message_view,edited_messages_view, rejected_messages_view, reviewed_messages_view

router = DefaultRouter()
router.register(r"tenants", TenantViewSet, basename="tenant")
router.register(r"conversations", ConversationViewSet, basename="conversation")
router.register(r"messages", MessageViewSet, basename="message")

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/webhooks/whatsapp/mock/", whatsapp_webhook_mock),
    path("api/messages/pending/", pending_messages_view),
    path("api/messages/edited/", edited_messages_view),
    path("api/messages/rejected/", rejected_messages_view),
    path("api/messages/reviewed/", reviewed_messages_view),
    path("api/messages/<int:message_id>/approve/", approve_message_view),
    path("api/messages/<int:message_id>/reject/", reject_message_view),
    path("api/messages/<int:message_id>/edit-approve/", edit_and_approve_message_view),
    
    path("api/", include(router.urls)),
    path("api/", include("apps.knowledge.urls")),

]