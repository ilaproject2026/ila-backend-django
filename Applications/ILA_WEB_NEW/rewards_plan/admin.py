from django.contrib import admin
from .models import RewardPlan, RewardRule, RewardCatalogItem, RewardRedemption, RewardPromotionBroadcast


@admin.register(RewardPlan)
class RewardPlanAdmin(admin.ModelAdmin):
    list_display = ("plan_name", "tier_level", "referral_bonus_cash", "points_per_referral", "status")
    list_filter = ("tier_level", "status")
    search_fields = ("plan_name",)


@admin.register(RewardRule)
class RewardRuleAdmin(admin.ModelAdmin):
    list_display = ("action_title", "category", "points_reward", "cash_incentive", "status")
    list_filter = ("category", "status")
    search_fields = ("action_title",)


@admin.register(RewardCatalogItem)
class RewardCatalogItemAdmin(admin.ModelAdmin):
    list_display = ("title", "item_type", "points_cost", "monetary_value", "stock_status")
    list_filter = ("item_type", "stock_status")
    search_fields = ("title",)


@admin.register(RewardRedemption)
class RewardRedemptionAdmin(admin.ModelAdmin):
    list_display = ("user_name", "reward_item", "points_spent", "payout_mode", "status", "requested_at")
    list_filter = ("status", "payout_mode")
    search_fields = ("user_name", "user_email", "user_phone")


@admin.register(RewardPromotionBroadcast)
class RewardPromotionBroadcastAdmin(admin.ModelAdmin):
    list_display = ("campaign_title", "sent_to_users_count", "dispatched_at")
    search_fields = ("campaign_title",)
