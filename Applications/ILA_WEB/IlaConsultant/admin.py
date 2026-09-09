from django.contrib import admin
from .models import AITokenUsageLog


@admin.register(AITokenUsageLog)
class AITokenUsageLogAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp',
        'topic',
        'model_name',
        'prompt_tokens',
        'completion_tokens',
        'total_tokens',
        'display_estimated_cost'
    )
    list_filter = ('topic', 'model_name', 'timestamp')
    search_fields = ('ip_address', 'topic')
    readonly_fields = ('timestamp', 'display_estimated_cost')

    def display_estimated_cost(self, obj):
        return f"${obj.estimated_cost_usd:.6f}"
    display_estimated_cost.short_description = "Est. Cost (USD)"
