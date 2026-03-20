from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Message, AIResponseEvaluation
# from .views import approve_message_view, reject_message_view
from .views import approve_message_logic, reject_message_logic

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "conversation_link",
        "customer_name",
        "customer_phone",
        "sender_type",
        "direction",
        "short_content",
        "review_status",
        "delivery_status",
        "created_at",
        "action_buttons",
    )

    list_filter = (
        "sender_type",
        "direction",
        "ai_generated",
        "review_status",
        "delivery_status",
        "channel",
        "created_at",
    )

    search_fields = (
        "content",
        "conversation__customer__identities__external_user_id",
        "conversation__customer__identities__external_display_name",
    )

    ordering = ("-id",)

    list_select_related = (
        "conversation",
        "conversation__customer",
        "conversation__tenant",
        "channel",
    )

    readonly_fields = (
        "conversation",
        "channel",
        "customer_name_readonly",
        "customer_phone_readonly",
        "sender_type",
        "direction",
        "message_type",
        "ai_generated",
        "confidence_score",
        "review_status",
        "delivery_status",
        "provider_message_id",
        "provider_status",
        "sent_at",
        "delivered_at",
        "read_at",
        "failed_at",
        "send_error",
        "raw_payload_json",
        "timestamp",
        "created_at",
        "updated_at",
        "conversation_messages_preview",
    )

    fieldsets = (
        ("Mensagem", {
            "fields": (
                "conversation",
                "channel",
                "customer_name_readonly",
                "customer_phone_readonly",
                "sender_type",
                "direction",
                "content",
                "message_type",
                "ai_generated",
                "confidence_score",
            )
        }),
        ("Revisão e envio", {
            "fields": (
                "review_status",
                "delivery_status",
                "provider_message_id",
                "provider_status",
                "sent_at",
                "delivered_at",
                "read_at",
                "failed_at",
                "send_error",
            )
        }),
        ("Últimas mensagens da conversa", {
            "fields": (
                "conversation_messages_preview",
            )
        }),
        ("Técnico", {
            "classes": ("collapse",),
            "fields": (
                "raw_payload_json",
                "timestamp",
                "created_at",
                "updated_at",
            )
        }),
    )

    # def get_queryset(self, request):
    #     return super().get_queryset(request).select_related(
    #         "conversation",
    #         "conversation__customer",
    #         "conversation__tenant",
    #         "channel",
    #     ).prefetch_related(
    #         "conversation__customer__identities",
    #         "conversation__messages",
    #     )
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(direction=Message.Direction.OUTBOUND)


    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:message_id>/approve/",
                self.admin_site.admin_view(self.approve_from_admin),
                name="messaging_message_approve_admin",
            ),
            path(
                "<int:message_id>/reject/",
                self.admin_site.admin_view(self.reject_from_admin),
                name="messaging_message_reject_admin",
            ),
        ]
        return custom_urls + urls

    def approve_from_admin(self, request, message_id):
        try:
            message = Message.objects.select_related(
                "conversation",
                "conversation__tenant",
                "conversation__channel",
                "conversation__tenant_channel_account",
                "conversation__customer",
                "channel",
            ).get(id=message_id)
        except Message.DoesNotExist:
            self.message_user(request, "Mensagem não encontrada.", level=messages.ERROR)
            return redirect(request.META.get("HTTP_REFERER", reverse("admin:messaging_message_changelist")))

        success, detail = approve_message_logic(message)

        if success:
            self.message_user(request, detail, level=messages.SUCCESS)
        else:
            self.message_user(request, detail, level=messages.ERROR)

        return redirect(request.META.get("HTTP_REFERER", reverse("admin:messaging_message_changelist")))

    def reject_from_admin(self, request, message_id):
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            self.message_user(request, "Mensagem não encontrada.", level=messages.ERROR)
            return redirect(request.META.get("HTTP_REFERER", reverse("admin:messaging_message_changelist")))

        success, detail = reject_message_logic(message)

        if success:
            self.message_user(request, detail, level=messages.WARNING)
        else:
            self.message_user(request, detail, level=messages.ERROR)

        return redirect(request.META.get("HTTP_REFERER", reverse("admin:messaging_message_changelist")))

    def customer_name(self, obj):
        identity = obj.conversation.customer.identities.filter(channel=obj.channel).first()
        if identity and identity.external_display_name:
            return identity.external_display_name
        return f"Customer {obj.conversation.customer_id}"
    customer_name.short_description = "Cliente"

    def customer_phone(self, obj):
        identity = obj.conversation.customer.identities.filter(channel=obj.channel).first()
        if not identity or not identity.external_user_id:
            return "-"

        phone = identity.external_user_id
        if phone.startswith("55") and len(phone) >= 12:
            return f"+{phone[:2]} {phone[2:4]} {phone[4:]}"
        return phone
    customer_phone.short_description = "Telefone"

    def customer_name_readonly(self, obj):
        return self.customer_name(obj)
    customer_name_readonly.short_description = "Cliente"

    def customer_phone_readonly(self, obj):
        return self.customer_phone(obj)
    customer_phone_readonly.short_description = "Telefone"

    def short_content(self, obj):
        if not obj.content:
            return "-"
        if len(obj.content) > 80:
            return obj.content[:80] + "..."
        return obj.content
    short_content.short_description = "Conteúdo"

    def conversation_link(self, obj):
        url = reverse("admin:conversations_conversation_change", args=[obj.conversation_id])
        return format_html('<a href="{}">Conversation {}</a>', url, obj.conversation_id)
    conversation_link.short_description = "Conversa"

    def conversation_messages_preview(self, obj):
        msgs = obj.conversation.messages.order_by("-id")[:10]
        msgs = list(reversed(list(msgs)))

        html = ['<div style="max-width:900px;">']
        for msg in msgs:
            who = "Cliente"
            if msg.sender_type == Message.SenderType.AI:
                who = "IA"
            elif msg.sender_type == Message.SenderType.HUMAN:
                who = "Humano"

            color = "#f6f6f6"
            if msg.sender_type == Message.SenderType.CUSTOMER:
                color = "#eef7ff"
            elif msg.sender_type == Message.SenderType.AI:
                color = "#f4fff0"

            html.append(
                f"""
                <div style="margin-bottom:10px;padding:10px;border:1px solid #ddd;border-radius:6px;background:{color};">
                    <strong>{who}</strong>
                    <span style="color:#666;"> | {msg.created_at.strftime('%d/%m/%Y %H:%M')}</span>
                    <div style="margin-top:6px;white-space:pre-wrap;">{msg.content}</div>
                </div>
                """
            )
        html.append("</div>")
        return mark_safe("".join(html))
    conversation_messages_preview.short_description = "Últimas mensagens"



    def action_buttons(self, obj):
        if obj.direction != Message.Direction.OUTBOUND:
            return "-"

        buttons = []

        edit_url = reverse("admin:messaging_message_change", args=[obj.pk])
        buttons.append(f'<a class="button" href="{edit_url}">Editar</a>')

        if obj.review_status == Message.ReviewStatus.PENDING:
            approve_url = reverse("admin:messaging_message_approve_admin", args=[obj.pk])
            reject_url = reverse("admin:messaging_message_reject_admin", args=[obj.pk])

            buttons.append(f'<a class="button" href="{approve_url}">Aprovar</a>')
            buttons.append(f'<a class="button" href="{reject_url}">Rejeitar</a>')

        if not buttons:
            return "-"

        return mark_safe(" ".join(buttons))
    action_buttons.short_description = "Ações"

    def changelist_view(self, request, extra_context=None):
        if not request.GET:
            return redirect("/admin/messaging/message/?review_status__exact=pending")
        return super().changelist_view(request, extra_context)

@admin.register(AIResponseEvaluation)
class AIResponseEvaluationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "message",
        "tenant",
        "evaluation_type",
        "created_at",
    )
    list_filter = ("evaluation_type", "tenant")
    search_fields = ("original_response", "final_response")


