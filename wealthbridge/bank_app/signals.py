from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction as db_transaction
from django.utils import timezone
from .models import UserProfile, Transaction

User = get_user_model()

def send_transaction_email(txn, recipient_email, currency):
    """
    Sends a highly professional transactional email notification.
    """
    # Force default currency if none is set
    curr = currency if currency else "$"
    
    action_type = "Credit Alert" if txn.tx_type == 'CREDIT' else "Debit Alert"
    subject = f"🔔 StackTeller Trust - {action_type}"
    
    html_message = f"""
    <html>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #020617; color: #f8fafc;">
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #0f172a; border-radius: 16px; overflow: hidden; border: 1px solid #1e293b; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);">
            <!-- Header -->
            <tr>
                <td style="padding: 32px 24px; background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); text-align: center; border-bottom: 3px solid #2563eb;">
                    <h1 style="margin: 0; color: #ffffff; font-size: 26px; font-weight: 700; letter-spacing: 0.5px;">StackTeller Trust Bank</h1>
                    <p style="margin: 6px 0 0 0; color: #93c5fd; font-size: 14px; font-weight: 500;">Secure Online Banking Notification</p>
                </td>
            </tr>
            
            <!-- Body -->
            <tr>
                <td style="padding: 40px 32px;">
                    <p style="font-size: 16px; margin-top: 0; color: #f8fafc; font-weight: 600;">Dear Valued Customer,</p>
                    <p style="font-size: 15px; color: #94a3b8; line-height: 1.6; margin-bottom: 24px;">
                        This is an automated security alert to notify you of a recent financial transaction on your account.
                    </p>
                    
                    <table width="100%" style="border-collapse: collapse; background-color: #020617; border-radius: 12px; overflow: hidden; border: 1px solid #1e293b; margin: 24px 0;">
                        <tr style="border-bottom: 1px solid #1e293b;">
                            <td style="padding: 14px 18px; font-weight: 600; color: #64748b; font-size: 14px; width: 40%;">Transaction Type:</td>
                            <td style="padding: 14px 18px; color: #f8fafc; font-size: 14px; font-weight: 600;">{txn.transaction_type}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #1e293b;">
                            <td style="padding: 14px 18px; font-weight: 600; color: #64748b; font-size: 14px;">Action:</td>
                            <td style="padding: 14px 18px; color: {'#10b981' if txn.tx_type == 'CREDIT' else '#ef4444'}; font-size: 14px; font-weight: 700;">{txn.tx_type}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #1e293b;">
                            <td style="padding: 14px 18px; font-weight: 600; color: #64748b; font-size: 14px;">Amount:</td>
                            <td style="padding: 14px 18px; color: #ffffff; font-size: 16px; font-weight: 700;">{curr}{txn.amount:,.2f}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #1e293b;">
                            <td style="padding: 14px 18px; font-weight: 600; color: #64748b; font-size: 14px;">Previous Balance:</td>
                            <td style="padding: 14px 18px; color: #94a3b8; font-size: 14px;">{curr}{txn.previous_balance:,.2f}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #1e293b;">
                            <td style="padding: 14px 18px; font-weight: 600; color: #64748b; font-size: 14px;">Updated Balance:</td>
                            <td style="padding: 14px 18px; color: #ffffff; font-size: 16px; font-weight: 700;">{curr}{txn.balance_after:,.2f}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #1e293b;">
                            <td style="padding: 14px 18px; font-weight: 600; color: #64748b; font-size: 14px;">Description:</td>
                            <td style="padding: 14px 18px; color: #cbd5e1; font-size: 14px;">{txn.description}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #1e293b;">
                            <td style="padding: 14px 18px; font-weight: 600; color: #64748b; font-size: 14px;">Status:</td>
                            <td style="padding: 14px 18px; color: {'#10b981' if txn.status == 'Successful' else '#f59e0b'}; font-size: 14px; font-weight: 700;">{txn.status}</td>
                        </tr>
                        <tr>
                            <td style="padding: 14px 18px; font-weight: 600; color: #64748b; font-size: 14px;">Reference ID:</td>
                            <td style="padding: 14px 18px; color: #94a3b8; font-size: 14px; font-family: monospace;">#STT-{txn.id:06d}</td>
                        </tr>
                    </table>

                    <p style="font-size: 13px; color: #94a3b8; line-height: 1.5; margin-top: 32px; background-color: #020617; padding: 16px; border-radius: 8px; border-left: 4px solid #ef4444;">
                        <strong>Security Notice:</strong> If you did not authorize this activity, please log in and change your password immediately, then contact our security response desk.
                    </p>
                </td>
            </tr>
            
            <!-- Footer -->
            <tr>
                <td style="padding: 24px; background-color: #020617; text-align: center; border-top: 1px solid #1e293b;">
                    <p style="margin: 0; font-size: 12px; color: #64748b;">&copy; {timezone.now().year} StackTeller Trust Bank. All rights reserved.</p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    text_message = f"""
Dear Valued Customer,

This is a security alert to notify you of a recent transaction on your account.

Transaction Details:
----------------------------------------
Transaction Type: {txn.transaction_type}
Action: {txn.tx_type}
Amount: {curr}{txn.amount:,.2f}
Previous Balance: {curr}{txn.previous_balance:,.2f}
Updated Balance: {curr}{txn.balance_after:,.2f}
Description: {txn.description}
Status: {txn.status}
Reference ID: #STT-{txn.id:06d}
Date & Time: {txn.timestamp.strftime('%Y-%m-%d %H:%M:%S')} UTC

Security Notice: If you did not authorize this transaction, please change your password immediately and contact our support team.

Thank you for choosing StackTeller Trust Bank.
    """
    
    import threading
    def send():
        def run():
            try:
                send_mail(
                    subject,
                    text_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [recipient_email],
                    html_message=html_message,
                    fail_silently=True
                )
            except Exception:
                pass
        
        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()

    # Wait until database transaction commits to send email in the background
    db_transaction.on_commit(send)


@receiver(post_save, sender=UserProfile)
def create_transaction_and_send_email(sender, instance, created, **kwargs):
    if created:
        return

    # Check if main balance changed
    old_balance = getattr(instance, '_old_balance', None)
    new_balance = instance.balance
    
    if old_balance is not None and old_balance != new_balance:
        balance_diff = new_balance - old_balance
        amount = abs(balance_diff)
        tx_type = 'CREDIT' if balance_diff > 0 else 'DEBIT'
        
        # Pull metadata set by view/admin, or fallback
        description = getattr(instance, '_description', 'Account Credit' if balance_diff > 0 else 'Account Debit')
        transaction_type = getattr(instance, '_transaction_type', 'Deposit' if balance_diff > 0 else 'Withdrawal')
        status = getattr(instance, '_status', 'Successful')
        
        # Create transaction
        txn = Transaction.objects.create(
            user=instance.user,
            amount=amount,
            previous_balance=old_balance,
            balance_after=new_balance,
            description=description,
            tx_type=tx_type,
            transaction_type=transaction_type,
            status=status
        )
        
        # Send Email Alert
        send_transaction_email(txn, instance.user.email or instance.email, instance.currency)

    # Check if refund balance changed
    old_refund = getattr(instance, '_old_refund', None)
    new_refund = instance.refund_balance
    
    if old_refund is not None and old_refund != new_refund:
        refund_diff = new_refund - old_refund
        amount = abs(refund_diff)
        tx_type = 'CREDIT' if refund_diff > 0 else 'DEBIT'
        
        description = getattr(instance, '_refund_description', 'Refund Credit' if refund_diff > 0 else 'Refund Debit')
        transaction_type = 'Refund'
        status = 'Successful'
        
        # Create transaction
        txn = Transaction.objects.create(
            user=instance.user,
            amount=amount,
            previous_balance=old_refund,
            balance_after=new_refund,
            description=description,
            tx_type=tx_type,
            transaction_type=transaction_type,
            status=status
        )
        
        # Send Email Alert
        send_transaction_email(txn, instance.user.email or instance.email, instance.currency)


# Automatically create a profile when a new user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, balance=0, email=instance.email)


# Track balance changes and save original values before save
@receiver(pre_save, sender=UserProfile)
def track_balance_changes(sender, instance, **kwargs):
    if not instance.pk:
        return

    # Fetch original instance from the database
    old_instance = UserProfile.objects.filter(pk=instance.pk).first()
    if not old_instance:
        return

    # Store old balances on the instance to evaluate in post_save
    if instance.balance != old_instance.balance:
        instance._old_balance = old_instance.balance

    if instance.refund_balance != old_instance.refund_balance:
        instance._old_refund = old_instance.refund_balance
