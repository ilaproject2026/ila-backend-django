from django.db import models
from django.utils import timezone


class AITokenUsageLog(models.Model):
    """Tracks token consumption and estimated API costs for every AI interaction."""
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    topic = models.CharField(max_length=50, default='general')
    model_name = models.CharField(max_length=100, default='gemini-1.5-flash')
    prompt_tokens = models.PositiveIntegerField(default=0)
    completion_tokens = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "AI Token Usage Log"
        verbose_name_plural = "AI Token Usage Logs"

    @property
    def estimated_cost_usd(self):
        """
        Gemini 1.5 Flash Pricing (Standard Tier):
        - Input:  $0.075 per 1,000,000 tokens ($0.000075 / 1k tokens)
        - Output: $0.30  per 1,000,000 tokens ($0.00030  / 1k tokens)
        (Note: Free tier allows up to 15 RPM with $0 cost)
        """
        input_cost = (self.prompt_tokens / 1_000_000) * 0.075
        output_cost = (self.completion_tokens / 1_000_000) * 0.30
        return round(input_cost + output_cost, 6)

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {self.model_name} - {self.total_tokens} tokens"
