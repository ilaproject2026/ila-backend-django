from django.db import models


class RewardPlan(models.Model):
    plan_name = models.CharField(max_length=200)
    tier_level = models.CharField(
        max_length=50,
        choices=[
            ("Bronze Consultant", "Bronze Consultant (5% Commission)"),
            ("Silver Ambassador", "Silver Ambassador (10% Commission)"),
            ("Gold Strategic Partner", "Gold Strategic Partner (15% Commission)"),
            ("Platinum Institutional Lead", "Platinum Institutional Lead (20% Commission)"),
        ],
        default="Bronze Consultant",
    )
    referral_bonus_cash = models.CharField(max_length=100, default="₹3,000 / Referral")
    points_per_referral = models.IntegerField(default=50)
    milestone_threshold = models.IntegerField(default=5, help_text="Number of candidates to unlock tier")
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=50,
        choices=[("Active", "Active"), ("Archived", "Archived")],
        default="Active",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.plan_name} ({self.tier_level})"


class RewardRule(models.Model):
    action_title = models.CharField(max_length=255)
    category = models.CharField(
        max_length=100,
        choices=[
            ("Referral", "Referral & Candidate Sourcing"),
            ("Course Milestone", "Academic Milestone Completion"),
            ("Community", "Community & Brand Promotion"),
            ("Institutional", "College MoU / Institutional Tie-Up"),
        ],
        default="Referral",
    )
    points_reward = models.IntegerField(default=50)
    cash_incentive = models.CharField(max_length=100, default="₹3,000 Payout")
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=50,
        choices=[("Active", "Active"), ("Inactive", "Inactive")],
        default="Active",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action_title} (+{self.points_reward} pts)"


class RewardCatalogItem(models.Model):
    title = models.CharField(max_length=255)
    item_type = models.CharField(
        max_length=100,
        choices=[
            ("Gift Package", "Gift Package"),
            ("Tour Package", "Tour Package (Europe / Goa Trip)"),
            ("Salary Incentive", "Salary Incentive Bonus"),
            ("Course Subsidy", "Course Subsidy Voucher"),
            ("Cashback", "Direct Bank Cashback"),
        ],
        default="Gift Package",
    )
    points_cost = models.IntegerField(default=250)
    monetary_value = models.CharField(max_length=100, default="₹25,000 Value")
    badge = models.CharField(max_length=50, default="Popular")
    stock_status = models.CharField(
        max_length=50,
        choices=[("In Stock", "In Stock"), ("Limited Availability", "Limited Availability"), ("On Request", "On Request")],
        default="In Stock",
    )
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.points_cost} Pts)"


class RewardRedemption(models.Model):
    user_name = models.CharField(max_length=200)
    user_email = models.EmailField()
    user_phone = models.CharField(max_length=50)
    reward_item = models.ForeignKey(RewardCatalogItem, on_delete=models.CASCADE)
    points_spent = models.IntegerField()
    payout_mode = models.CharField(max_length=100, default="Direct Bank Transfer (NEFT/IMPS)")
    bank_details = models.TextField(blank=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ("Pending Review", "Pending Review"),
            ("Approved by Marketing", "Approved by Marketing"),
            ("Fulfilled / Disbursed", "Fulfilled / Disbursed"),
            ("Rejected", "Rejected"),
        ],
        default="Pending Review",
    )
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name} -> {self.reward_item.title} ({self.status})"


class RewardPromotionBroadcast(models.Model):
    campaign_title = models.CharField(max_length=255)
    message_copy = models.TextField()
    target_channels = models.JSONField(default=list, help_text="e.g. ['Meta Ads', 'LinkedIn', 'WhatsApp']")
    sent_to_users_count = models.IntegerField(default=0)
    dispatched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Broadcast: {self.campaign_title} ({self.sent_to_users_count} recipients)"
