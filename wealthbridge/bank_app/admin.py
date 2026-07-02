from django.contrib import admin
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Count, Sum
from django.utils.html import format_html
from .models import *

@admin.register(InvestmentPlan)
class InvestmentPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'min_amount', 'max_amount', 'interest_rate', 'duration_days', 'is_active']
    list_filter = ['plan_type', 'is_active']
    search_fields = ['name']

@admin.register(UserInvestment)
class UserInvestmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'investment_plan', 'amount_invested', 'expected_return', 'start_date', 'end_date', 'status']
    list_filter = ['status', 'investment_plan']
    search_fields = ['user__username', 'investment_plan__name']

@admin.register(InvestmentTransaction)
class InvestmentTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'investment', 'amount', 'transaction_type', 'created_at']
    list_filter = ['transaction_type']
    search_fields = ['user__username']

# ============ USER PROFILE ADMIN ============

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'account_number', 'balance', 'currency', 'is_linked', 'is_upgraded', 'frozenState']
    list_filter = ['is_linked', 'is_upgraded', 'frozenState', 'account_type', 'currency']
    search_fields = ['user__username', 'user__email', 'account_number', 'phone_number', 'email']
    readonly_fields = ['account_number', 'linking_code', 'tax_code', 'imf_code', 'bic_code', 'card_application_fee_code', 'created_at']
    list_editable = ['balance', 'currency']
    list_per_page = 25

    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'first_name', 'middle_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 'Gender')
        }),
        ('Account Information', {
            'fields': ('account_number', 'account_type', 'balance', 'currency', 'linking_code', 'tax_code', 'imf_code', 'bic_code')
        }),
        ('Address & Location', {
            'fields': ('address', 'zip_code', 'country')
        }),
        ('Employment & Status', {
            'fields': ('occupation', 'status')
        }),
        ('Card Details', {
            'fields': ('cardholder_name', 'card_number', 'cvv', 'expiry_date', 'card_application_fee_code'),
            'classes': ('collapse',)
        }),
        ('Security Settings', {
            'fields': ('two_factor_auth', 'four_digit_auth_key'),
        }),
        ('Account Status', {
            'fields': ('is_linked', 'is_upgraded', 'frozenState', 'refund_balance', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['freeze_accounts', 'unfreeze_accounts', 'upgrade_accounts']

    def freeze_accounts(self, request, queryset):
        updated = queryset.update(frozenState=True)
        self.message_user(request, f'{updated} account(s) have been frozen.')
    freeze_accounts.short_description = "Freeze selected accounts"

    def unfreeze_accounts(self, request, queryset):
        updated = queryset.update(frozenState=False)
        self.message_user(request, f'{updated} account(s) have been unfrozen.')
    unfreeze_accounts.short_description = "Unfreeze selected accounts"

    def upgrade_accounts(self, request, queryset):
        updated = queryset.update(is_upgraded=True)
        self.message_user(request, f'{updated} account(s) have been upgraded.')
    upgrade_accounts.short_description = "Upgrade selected accounts"


# ============ CRYPTO CURRENCY ADMIN ============

@admin.register(CryptoCurrency)
class CryptoCurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'icon_preview', 'min_deposit', 'confirmations_required', 'is_active', 'sort_order']
    list_editable = ['min_deposit', 'confirmations_required', 'is_active', 'sort_order']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    list_per_page = 20

    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'icon', 'is_active', 'sort_order')
        }),
        ('Deposit Settings', {
            'fields': ('min_deposit', 'confirmations_required'),
        }),
    )

    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<i class="{}" style="font-size: 20px; color: #667eea;"></i>', obj.icon)
        return format_html('<i class="fab fa-bitcoin" style="font-size: 20px;"></i>')
    icon_preview.short_description = 'Icon'

    actions = ['enable_cryptos', 'disable_cryptos']

    def enable_cryptos(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} cryptocurrency(s) have been enabled.')
    enable_cryptos.short_description = "Enable selected cryptocurrencies"

    def disable_cryptos(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} cryptocurrency(s) have been disabled.')
    disable_cryptos.short_description = "Disable selected cryptocurrencies"


# ============ CRYPTO WALLET ADDRESS INLINE ============

class CryptoWalletAddressInline(admin.TabularInline):
    model = CryptoWalletAddress
    extra = 1
    fields = ['address', 'network', 'is_primary', 'is_active', 'notes']
    show_change_link = True
    classes = ['collapse']


# ============ CRYPTO WALLET ADDRESS ADMIN - FIXED ============

# bank_app/admin.py - Update CryptoWalletAddressAdmin

@admin.register(CryptoWalletAddress)
class CryptoWalletAddressAdmin(admin.ModelAdmin):
    list_display = ['crypto', 'address_short', 'network', 'is_primary', 'is_active', 'created_at']
    list_editable = ['is_primary', 'is_active']
    list_filter = ['crypto', 'network', 'is_primary', 'is_active']
    search_fields = ['address', 'crypto__name', 'crypto__code', 'notes']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    list_per_page = 25

    # Remove the copy_button from list_display to simplify
    fieldsets = (
        ('Cryptocurrency Information', {
            'fields': ('crypto', 'network')
        }),
        ('Wallet Address', {
            'fields': ('address', 'is_primary', 'is_active', 'notes'),
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

    def address_short(self, obj):
        short = obj.get_short_address()
        return format_html('<code style="font-size: 12px;">{}</code>', short)
    address_short.short_description = 'Address'

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user.username
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        # Use select_related but avoid complex joins
        return super().get_queryset(request).select_related('crypto')

    # Remove custom actions that might cause cursor issues
    actions = ['mark_as_active', 'mark_as_inactive']

    def mark_as_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} address(es) marked as active.')
    mark_as_active.short_description = "Mark as active"

    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} address(es) marked as inactive.')
    mark_as_inactive.short_description = "Mark as inactive"

# ============ SYSTEM CRYPTO SETTINGS ADMIN ============

@admin.register(SystemCryptoSetting)
class SystemCryptoSettingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SystemCryptoSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    fieldsets = (
        ('Deposit Settings', {
            'fields': ('auto_approve_deposits', 'deposit_fee_percentage', 'min_deposit_amount', 'max_deposit_amount'),
        }),
        ('Metadata', {
            'fields': ('updated_by',),
            'classes': ('collapse',),
        }),
    )

    list_display = ['auto_approve_deposits', 'deposit_fee_percentage', 'min_deposit_amount', 'max_deposit_amount', 'updated_at']
    readonly_fields = ['updated_at']

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


# Uncomment to use custom admin site
# admin_site = CustomAdminSite(name='custom_admin')
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'balance_after', 'timestamp', 'description']  # Specify fields to display in the admin list
    search_fields = ['user__username', 'description']  # Search by user and description
    list_filter = ['timestamp', 'user']  # Add filters for timestamp and user
    ordering = ['-timestamp']

class YourModelAdmin(admin.ModelAdmin):
    list_display = ('image_display',)

    def image_display(self, obj):
        return obj.image.url if obj.image else None

# ============ ADMIN AUDIT LOGS ============

from django.contrib.admin.models import LogEntry

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['action_time', 'user', 'content_type', 'object_repr', 'action_flag_display', 'change_message']
    list_filter = ['action_time', 'user', 'action_flag']
    search_fields = ['object_repr', 'change_message']
    readonly_fields = ['action_time', 'user', 'content_type', 'object_id', 'object_repr', 'action_flag', 'change_message']

    def action_flag_display(self, obj):
        from django.contrib.admin.models import ADDITION, CHANGE, DELETION
        if obj.action_flag == ADDITION:
            return format_html('<span style="color: #27AE60; font-weight: bold;">{}</span>', 'Addition')
        elif obj.action_flag == CHANGE:
            return format_html('<span style="color: #F39C12; font-weight: bold;">{}</span>', 'Change')
        elif obj.action_flag == DELETION:
            return format_html('<span style="color: #C0392B; font-weight: bold;">{}</span>', 'Deletion')
        return format_html('<span>{}</span>', 'Unknown')
    action_flag_display.short_description = 'Action'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
