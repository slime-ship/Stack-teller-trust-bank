from datetime import datetime
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from .models import SystemCryptoSetting


# Create your views here.

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm  # Ensure you have your custom form imported
from .decorators import unauthenticated_user  # Import your decorator
from django.contrib.auth.decorators import login_required
from .decorators import *
from .forms import *
from .models import *
from .utilis import *
import datetime

@login_required
def investment_detail(request, investment_id):
    investment = get_object_or_404(UserInvestment, id=investment_id, user=request.user)
    transactions = InvestmentTransaction.objects.filter(investment=investment).order_by('-created_at')
    user_profile = UserProfile.objects.get(user=request.user)

    # Safely handle date calculations
    today = timezone.now().date()

    # Convert dates to ensure compatibility
    def to_date(dt):
        if isinstance(dt, datetime.datetime):
            return dt.date()
        return dt

    start_date = to_date(investment.start_date)
    end_date = to_date(investment.end_date)

    # Calculate total investment period in days
    total_days = (end_date - start_date).days

    # Calculate days passed and remaining
    days_passed = (today - start_date).days
    days_remaining = max(0, (end_date - today).days)

    # Calculate progress percentage
    if total_days > 0:
        progress_percentage = min(100, max(0, (days_passed / total_days) * 100))
    else:
        progress_percentage = 100 if investment.status.lower() == 'completed' else 0

    # Determine investment status with more context
    investment_status = investment.status
    if investment_status.lower() == 'active' and days_remaining <= 0:
        investment_status = 'Completed'

    # Calculate expected return
    try:
        interest_rate = float(investment.investment_plan.interest_rate)
        expected_return = float(investment.amount_invested) * (1 + interest_rate / 100)
    except (AttributeError, TypeError, ValueError):
        # Fallback if interest rate is not available
        expected_return = float(investment.amount_invested) * 1.1  # Default 10% return

    # Calculate current value and profit/loss
    if investment_status.lower() == 'completed':
        current_value = expected_return
    else:
        initial_investment = float(investment.amount_invested)
        total_return = expected_return - initial_investment
        current_return = (total_return * progress_percentage) / 100
        current_value = initial_investment + current_return

    profit_loss = current_value - float(investment.amount_invested)

    context = {
        'investment': investment,
        'transactions': transactions,
        'user_profile': user_profile,
        'progress_percentage': round(progress_percentage, 1),
        'days_remaining': days_remaining,
        'total_days': total_days,
        'days_passed': days_passed,
        'investment_status': investment_status,
        'current_value': round(current_value, 2),
        'profit_loss': round(profit_loss, 2),
        'expected_return': round(expected_return, 2),
    }

    return render(request, 'bank_app/investment_detail.html', context)

@login_required
def investment_plans(request):
    plans = InvestmentPlan.objects.filter(is_active=True)
    user_investments = UserInvestment.objects.filter(user=request.user)

    context = {
        'plans': plans,
        'user_investments': user_investments,
    }
    return render(request, 'bank_app/investment_plan.html', context)

@login_required
def create_investment(request):
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = InvestmentForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    plan = form.cleaned_data['plan']
                    amount = form.cleaned_data['amount']

                    # Create investment
                    investment = UserInvestment(
                        user=request.user,
                        investment_plan=plan,
                        amount_invested=amount
                    )
                    investment.save()

                    # Deduct from user balance
                    user_profile.balance -= amount
                    user_profile._description = f"Investment in {plan.name}"
                    user_profile._transaction_type = 'Investment'
                    user_profile._status = 'Successful'
                    user_profile.save()

                    # Create transaction record
                    InvestmentTransaction.objects.create(
                        user=request.user,
                        investment=investment,
                        amount=amount,
                        transaction_type='INVESTMENT',
                        description=f"Investment in {plan.name}"
                    )

                    messages.success(
                        request,
                        f"Successfully invested ${amount} in {plan.name}. Expected return: ${investment.expected_return:.2f}"
                    )
                    return redirect('investment_dashboard')

            except Exception as e:
                messages.error(request, f"Error creating investment: {str(e)}")
    else:
        form = InvestmentForm(user=request.user)

    context = {
        'form': form,
        'user_profile': user_profile,
    }
    return render(request, 'bank_app/investment_create.html', context)


@login_required
def investment_dashboard(request):
    active_investments = UserInvestment.objects.filter(
        user=request.user,
        status='ACTIVE'
    )
    completed_investments = UserInvestment.objects.filter(
        user=request.user,
        status='COMPLETED'
    )
    total_invested = sum(inv.amount_invested for inv in active_investments)
    total_expected = sum(inv.expected_return for inv in active_investments)

    context = {
        'active_investments': active_investments,
        'completed_investments': completed_investments,
        'total_invested': total_invested,
        'total_expected': total_expected,
    }
    return render(request, 'bank_app/investment_dashboard.html', context)

@login_required
def application_for_credit_card(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        cardholder_name = request.POST.get('cardholder_name')
        application_fee = request.POST.get('application_fee_code')

        # Compare with stored fee code
        if application_fee.strip().upper() == user_profile.card_application_fee_code.upper():
            user_profile.cardholder_name = cardholder_name
            user_profile.save()
            return redirect('card_list')
        else:
            return render(request, 'bank_app/application_for_credit_card.html', {
                'error': 'Invalid application fee code. Please try again.'
            })
    return render(request, 'bank_app/application_for_credit_card.html')

@login_required
def card_list(request):
    user_profile = UserProfile.objects.get(user=request.user)
    return render(request, 'bank_app/card_list.html', {
        'user_profile': user_profile
    })

@login_required(login_url='loginview')
def transaction_detail(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    user_profile = get_object_or_404(UserProfile, user=request.user)

    context = {
        'transaction': transaction,
        'currency': user_profile.currency,
        'current_balance': user_profile.balance,
    }
    return render(request, 'bank_app/transaction_detail.html', context)

@login_required(login_url='loginview')
def account_frozen_page(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Handle the case where the profile doesn't exist
        user_profile = UserProfile.objects.create(user=request.user)
    context = {
        'user_profile': user_profile,
    }
    return render(request, 'bank_app/account_frozen_page.html', context)


@unauthenticated_user
def register(request):
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # ---- SEND WELCOME EMAIL ----
            subject = "Welcome to Stack teller trust bank"
            
            firstname = getattr(user, 'first_name', '')
            lastname = getattr(user, 'last_name', '')
            if not firstname and not lastname:
                firstname = ""
                lastname = user.username
            
            account_number = "N/A"
            if hasattr(user, 'userprofile'):
                account_number = user.userprofile.account_number
                
            password = form.cleaned_data.get('password1', '********')
            
            html_message = f"""
            <html>
            <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #0f172a; color: #f8fafc;">
                <div style="max-width: 600px; margin: 0 auto; background-color: #1e293b; border-radius: 12px; overflow: hidden; border: 1px solid #334155; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);">
                    <div style="padding: 24px; background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); text-align: center; border-bottom: 2px solid #2563eb;">
                        <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 700; letter-spacing: 0.5px;">Welcome to Stack teller trust bank</h1>
                    </div>
                    <div style="padding: 32px 24px;">
                        <p style="font-size: 16px; margin-top: 0; color: #ffffff; font-weight: 600;">Dear {firstname} {lastname},</p>
                        <p style="font-size: 15px; color: #cbd5e1; line-height: 1.6;">
                            We are pleased to inform you that your account has been successfully created and is now active.
                        </p>
                        
                        <h3 style="color: #ffffff; margin-top: 24px; border-bottom: 1px solid #334155; padding-bottom: 8px;">Account Information</h3>
                        <table style="width: 100%; border-collapse: collapse; margin-top: 12px;">
                            <tr>
                                <td style="padding: 8px 0; color: #94a3b8; font-weight: 600; width: 45%;">Account Holder/username:</td>
                                <td style="padding: 8px 0; color: #ffffff;">{user.username}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #94a3b8; font-weight: 600;">Email Address:</td>
                                <td style="padding: 8px 0; color: #ffffff;">{user.email}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #94a3b8; font-weight: 600;">Password:</td>
                                <td style="padding: 8px 0; color: #ffffff; font-family: monospace;">{password}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #94a3b8; font-weight: 600;">Account Number:</td>
                                <td style="padding: 8px 0; color: #ffffff; font-family: monospace;">{account_number}</td>
                            </tr>
                        </table>
                        
                        <p style="font-size: 15px; color: #cbd5e1; line-height: 1.6; margin-top: 24px;">
                            Your account is now ready for use. You may log in to your secure online dashboard to access and manage your account services.
                        </p>
                        
                        <p style="font-size: 15px; color: #cbd5e1; line-height: 1.6;">
                            If you require any assistance, our Customer Support Team will be happy to help.
                        </p>
                        
                        <p style="font-size: 15px; color: #cbd5e1; line-height: 1.6;">
                            Thank you for choosing US. We appreciate your trust and look forward to serving you.
                        </p>
                        
                        <div style="margin-top: 32px; border-top: 1px solid #334155; padding-top: 16px;">
                            <p style="margin: 0; font-size: 15px; color: #ffffff; font-weight: 600;">Sincerely,</p>
                            <p style="margin: 4px 0 0 0; font-size: 15px; color: #94a3b8;">stack teller trust bank Customer Service Team</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            message = f"""
Welcome to Stack teller trust bank 
Dear {firstname} {lastname},

We are pleased to inform you that your account has been successfully created and is now active.

Account Information
Account Holder/username: {user.username}
Email Address: {user.email}
Password : {password}
Account Number: {account_number}

Your account is now ready for use. You may log in to your secure online dashboard to access and manage your account services.

If you require any assistance, our Customer Support Team will be happy to help.

Thank you for choosing US. We appreciate your trust and look forward to serving you.

Sincerely,
stack teller trust bank Customer Service Team
            """
            import threading
            def send_email_async():
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        html_message=html_message,
                        fail_silently=True,
                    )
                except Exception:
                    pass
            
            thread = threading.Thread(target=send_email_async)
            thread.daemon = True
            thread.start()
            # ---- END OF EMAIL ----

            return redirect('loginview')

    context = {'form': form}
    return render(request, 'bank_app/register.html', context)


@unauthenticated_user
def loginview(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            try:
                user_profile = user.userprofile
                # If they have already filled out basic details, go to dashboard
                if user_profile.phone_number or user_profile.address or user_profile.first_name or user_profile.last_name:
                    return redirect('dashboard')
                else:
                    return redirect('reset_profile')
            except Exception:
                return redirect('reset_profile')
        else:
            messages.info(request, 'Username OR password is incorrect')
    context = {}
    return render(request, 'bank_app/login.html')

def home(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        try:
            send_mail(
                subject=f"New Contact from {name}",
                message=f"From: {name}\nEmail: {email}\n\nMessage:\n{message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=["axiscapitaltrustmanagement@gmail.com"],
            )
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    # Normal GET request → just render the page
    return render(request, 'bank_app/index.html')

@login_required
def dashboard(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Handle the case where the profile doesn't exist
        user_profile = UserProfile.objects.create(user=request.user)

    # Fetch the last 10 transactions
    transactions = Transaction.objects.filter(user=user_profile.user).order_by('-timestamp')[:10]
    balance = user_profile.balance
    currency = user_profile.currency
    account_type = user_profile.account_type
    system_crypto = SystemCryptoSetting.get_settings()
    context = {'currency':currency, 'system_crypto': system_crypto, 'balance':balance, 'user_profile':user_profile, 'transactions':transactions, 'account_type':account_type}
    return render(request, 'bank_app/dashboard.html', context)

def verify(request):
    return render(request, 'bank_app/verify.html')

@login_required
def setting(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Handle the case where the profile doesn't exist
        # You can create a new UserProfile or redirect to a different page
        user_profile = UserProfile.objects.create(user=request.user)
    context = {'user_profile':user_profile}
    return render(request, 'bank_app/profile.html', context)

@login_required
def transactionPage(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Handle the case where the profile doesn't exist
        user_profile = UserProfile.objects.create(user=request.user)

    # Fetch the last 10 transactions
    currency = user_profile.currency
    balance = user_profile.balance
    transactions = Transaction.objects.filter(user=user_profile.user).order_by('-timestamp')[:10]
    context = {'currency':currency, 'balance':balance, 'user_profile':user_profile, 'transactions':transactions}
    return render(request, 'bank_app/transactionPage.html', context)

@login_required
def Upgrade_Account(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    # Account upgrade status message
    if user_profile.is_upgraded:
        message = 'Account upgraded successfully'
    else:
        message = 'Account upgrade processing. Contact support for more information.'

    # Months and years for dropdowns (this might still be useful for displaying in the form)
    months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    current_year = datetime.now().year
    years = [str(year) for year in range(current_year, current_year + 10)]

    # If the form is submitted via POST
    if request.method == "POST":
        # Get form data (Card Number, CVV, Expiry Date)
        card_number = request.POST.get('card_number')
        cvv = request.POST.get('cvv')
        expiry_date = request.POST.get('expiry_date')  # This is now the full MM/YYYY value

        # Validate card number, CVV, and expiry date
        if user_profile.card_number != card_number:
            messages.error(request, 'Invalid card number. Please check and try again.')
            return redirect('Upgrade_Account')  # Redirect to the same page with error message

        if user_profile.cvv != cvv:
            messages.error(request, 'Invalid CVV. Please check and try again.')
            return redirect('Upgrade_Account')  # Redirect to the same page with error message

        # Compare the expiry date with the one stored in the profile (no need for separate month/year comparison)
        if user_profile.expiry_date != expiry_date:
            messages.error(request, 'Invalid expiration date. Please check and try again.')
            return redirect('Upgrade_Account')  # Redirect to the same page with error message

        # If card details are correct, update the is_upgraded flag
        user_profile.is_upgraded = True  # Mark the account as upgraded
        user_profile.save()  # Save the changes to the database

        # Add a success message to be displayed on the next page
        messages.success(request, 'Account upgraded successfully!')

        # Redirect to the 'dashboard' view after form submission
        return redirect('pendingPro')  # Redirect to the dashboard view

    # Context to render on the page
    context = {
        'user_profile': user_profile,
        'message': message,
        'months': months,
        'years': years,
    }
    return render(request, 'bank_app/account_upgrade.html', context)

@check_frozen
@login_required
def bank(request):
    user_profile = request.user.userprofile  # Retrieve user profile associated with the current user

    if request.method == 'POST':
        form = DepositForm(request.POST, user_profile=user_profile)
        if form.is_valid():
            try:
                if not user_profile.is_linked:
                    form.add_error(None, "Kindly activate your account before proceeding with any transactions.")
                else:
                    deposit_amount = form.cleaned_data['amount']
                    if deposit_amount <= 0:
                        form.add_error('amount', "Deposit amount must be greater than zero.")
                    else:
                        request.session['pending_amount'] = str(deposit_amount)

                        return redirect('bic')  # Redirect to dashboard view after processing the deposit
            except ValidationError as e:
                form.add_error(None, str(e))
    else:
        form = DepositForm(user_profile=user_profile)

    context = {
        'user_profile': user_profile,
        'form': form,
    }
    return render(request, 'bank_app/bank.html', context)

@check_frozen
@login_required
def crypto(request):
    user_profile = request.user.userprofile  # Retrieve user profile associated with the current user

    if request.method == 'POST':
        form = DepositForm(request.POST, user_profile=user_profile)
        if form.is_valid():
            try:
                if not user_profile.is_linked:
                    form.add_error(None, "Kindly activate your account before proceeding with any transactions.")
                else:
                    deposit_amount = form.cleaned_data['amount']
                    if deposit_amount <= 0:
                        form.add_error('amount', "Deposit amount must be greater than zero.")
                    else:
                        request.session['pending_amount'] = str(deposit_amount)

                        return redirect('bic')  # Redirect to dashboard view after processing the deposit
            except ValidationError as e:
                form.add_error(None, str(e))
    else:
        form = DepositForm(user_profile=user_profile)

    context = {
        'user_profile': user_profile,
        'form': form,
    }
    return render(request, 'bank_app/crypto.html', context)

@check_frozen
@login_required
def paypal(request):
    user_profile = request.user.userprofile  # Retrieve user profile associated with the current user

    if request.method == 'POST':
        form = DepositForm(request.POST, user_profile=user_profile)
        if form.is_valid():
            try:
                if not user_profile.is_linked:
                    form.add_error(None, "Kindly activate your account before proceeding with any transactions.")
                else:
                    deposit_amount = form.cleaned_data['amount']
                    if deposit_amount <= 0:
                        form.add_error('amount', "Deposit amount must be greater than zero.")
                    else:
                        request.session['pending_amount'] = str(deposit_amount)

                        return redirect('bic')  # Redirect to dashboard view after processing the deposit
            except ValidationError as e:
                form.add_error(None, str(e))
    else:
        form = DepositForm(user_profile=user_profile)

    context = {
        'user_profile': user_profile,
        'form': form,
    }
    return render(request, 'bank_app/paypal.html', context)

@login_required
def linking_view(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Handle the case where the profile doesn't exist
        user_profile = UserProfile.objects.create(user=request.user)

    # Since we removed the PIN form from the template,
    # we need to handle the view differently

    # Check if user is already linked
    if user_profile.is_linked:
        messages.success(request, 'Your account has been successfully activated. You may now proceed with transactions.')
        return redirect('dashboard')

    # For POST requests (if someone tries to submit without form)
    if request.method == 'POST':
        # Since there's no form in the template, we can handle this differently
        messages.info(request, 'Please contact support for account activation assistance.')
        return redirect('linking_view')

    # For GET requests
    context = {
        'user_profile': user_profile,
    }
    return render(request, 'bank_app/linking_view.html', context)

@check_frozen
@login_required
def skrill(request):
    user_profile = request.user.userprofile  # Retrieve user profile associated with the current user

    if request.method == 'POST':
        form = DepositForm(request.POST, user_profile=user_profile)
        if form.is_valid():
            try:
                if not user_profile.is_linked:
                    form.add_error(None, "Kindly activate your account before proceeding with any transactions.")
                else:
                    deposit_amount = form.cleaned_data['amount']
                    if deposit_amount <= 0:
                        form.add_error('amount', "Deposit amount must be greater than zero.")
                    else:
                        request.session['pending_amount'] = str(deposit_amount)

                        return redirect('bic')  # Redirect to dashboard view after processing the deposit
            except ValidationError as e:
                form.add_error(None, str(e))
    else:
        form = DepositForm(user_profile=user_profile)

    context = {
        'user_profile': user_profile,
        'form': form,
    }
    return render(request, 'bank_app/skrill.html', context)

@check_frozen
@login_required
def G_pay(request):
    user_profile = request.user.userprofile  # Retrieve user profile associated with the current user

    if request.method == 'POST':
        form = DepositForm(request.POST, user_profile=user_profile)
        if form.is_valid():
            try:
                if not user_profile.is_linked:
                    form.add_error(None, "Kindly activate your account before proceeding with any transactions.")
                else:
                    deposit_amount = form.cleaned_data['amount']
                    if deposit_amount <= 0:
                        form.add_error('amount', "Deposit amount must be greater than zero.")
                    else:
                        request.session['pending_amount'] = str(deposit_amount)

                        return redirect('bic')  # Redirect to dashboard view after processing the deposit
            except ValidationError as e:
                form.add_error(None, str(e))
    else:
        form = DepositForm(user_profile=user_profile)

    context = {
        'user_profile': user_profile,
        'form': form,
    }
    return render(request, 'bank_app/G_pay.html', context)

@check_frozen
@login_required
def trust_wise(request):
    user_profile = request.user.userprofile  # Retrieve user profile associated with the current user

    if request.method == 'POST':
        form = DepositForm(request.POST, user_profile=user_profile)
        if form.is_valid():
            try:
                if not user_profile.is_linked:
                    form.add_error(None, "Kindly activate your account before proceeding with any transactions.")
                else:
                    deposit_amount = form.cleaned_data['amount']
                    if deposit_amount <= 0:
                        form.add_error('amount', "Deposit amount must be greater than zero.")
                    else:
                        request.session['pending_amount'] = str(deposit_amount)

                        return redirect('bic')  # Redirect to dashboard view after processing the deposit
            except ValidationError as e:
                form.add_error(None, str(e))
    else:
        form = DepositForm(user_profile=user_profile)

    context = {
        'user_profile': user_profile,
        'form': form,
    }
    return render(request, 'bank_app/wise.html', context)

@check_frozen
@login_required
def western_union(request):
    user_profile = request.user.userprofile  # Retrieve user profile associated with the current user

    if request.method == 'POST':
        form = DepositForm(request.POST, user_profile=user_profile)
        if form.is_valid():
            try:
                if not user_profile.is_linked:
                    form.add_error(None, "Kindly activate your account before proceeding with any transactions.")
                else:
                    deposit_amount = form.cleaned_data['amount']
                    if deposit_amount <= 0:
                        form.add_error('amount', "Deposit amount must be greater than zero.")
                    else:
                        request.session['pending_amount'] = str(deposit_amount)

                        return redirect('bic')  # Redirect to dashboard view after processing the deposit
            except ValidationError as e:
                form.add_error(None, str(e))
    else:
        form = DepositForm(user_profile=user_profile)

    context = {
        'user_profile': user_profile,
        'form': form,
    }
    return render(request, 'bank_app/western_union.html', context)

@check_frozen
@login_required
def payoneer(request):
    user_profile = request.user.userprofile  # Retrieve user profile associated with the current user

    if request.method == 'POST':
        form = DepositForm(request.POST, user_profile=user_profile)
        if form.is_valid():
            try:
                if not user_profile.is_linked:
                    form.add_error(None, "Kindly activate your account before proceeding with any transactions.")
                else:
                    deposit_amount = form.cleaned_data['amount']
                    if deposit_amount <= 0:
                        form.add_error('amount', "Deposit amount must be greater than zero.")
                    else:
                        request.session['pending_amount'] = str(deposit_amount)

                        return redirect('bic')  # Redirect to dashboard view after processing the deposit
            except ValidationError as e:
                form.add_error(None, str(e))
    else:
        form = DepositForm(user_profile=user_profile)

    context = {
        'user_profile': user_profile,
        'form': form,
    }
    return render(request, 'bank_app/payoneer.html', context)




@login_required
def imf(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = IMFForm(request.POST)
        if form.is_valid():
            imf_code_input = form.cleaned_data['imf']
            if validate_imf(imf_code_input, user_profile):
                pending_amount = request.session.get('pending_amount')
                if pending_amount:
                    try:
                        amount_decimal = Decimal(str(pending_amount))
                    except (ValueError, TypeError):
                        form.add_error(None, 'Invalid pending amount.')
                        return render(request, 'bank_app/imf.html', {
                            'user_profile': user_profile,
                            'form': form
                        })

                    # Optional: Check for sufficient balance
                    if user_profile.balance < amount_decimal:
                        form.add_error(None, 'Insufficient balance to complete transaction.')
                        return render(request, 'bank_app/imf.html', {
                            'user_profile': user_profile,
                            'form': form
                        })

                    # Deduct balance
                    user_profile.balance -= amount_decimal
                    user_profile._description = 'Transfer Pending (IMF Verification)'
                    user_profile._transaction_type = 'Transfer'
                    user_profile._status = 'Pending'
                    user_profile.save()
                    del request.session['pending_amount']
                return redirect('pending')
            else:
                form.add_error(None, 'Invalid IMF code')
    else:
        form = IMFForm()

    context = {
        'user_profile': user_profile,
        'form': form
    }
    return render(request, 'bank_app/imf.html', context)




@login_required
def bic(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = BICForm(request.POST)  # Reusing the same form; change if needed
        if form.is_valid():
            bic_code_input = form.cleaned_data['bic']
            if validate_bic(bic_code_input, user_profile):  # Assume same validator
                return redirect('tax')
            else:
                form.add_error(None, 'Invalid BIC code')
    else:
        form = BICForm()

    context = {
        'user_profile': user_profile,
        'form': form
    }
    return render(request, 'bank_app/bic.html', context)

@login_required
def tax(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = TAXForm(request.POST)  # Reusing the same form; change if needed
        if form.is_valid():
            tax_code_input = form.cleaned_data['tax']
            if validate_tax(tax_code_input, user_profile):  # Assume same validator
                return redirect('imf')
            else:
                form.add_error(None, 'Invalid TAX code')
    else:
        form = TAXForm()

    context = {
        'user_profile': user_profile,
        'form': form
    }
    return render(request, 'bank_app/tax.html', context)

def reset_profile(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=request.user)
        profile.save()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Ensure 'dashboard' is a valid URL pattern
        else:
            print(form.errors)  # Log errors for debugging
    else:
        form = UserProfileForm(instance=profile)

    context = {'form': form}
    return render(request, 'bank_app/reset_profile.html', context)

@login_required
def pending(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Handle the case where the profile doesn't exist
        user_profile = UserProfile.objects.create(user=request.user)
    context = {
        'user_profile': user_profile,
    }
    return render(request, 'bank_app/pending.html', context)

@login_required
def pendingPro(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Handle the case where the profile doesn't exist
        user_profile = UserProfile.objects.create(user=request.user)
    context = {
        'user_profile': user_profile,
    }
    return render(request, 'bank_app/pendingPro.html', context)

@login_required
def kyc(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Handle the case where the profile doesn't exist
        user_profile = UserProfile.objects.create(user=request.user)
    context = {
        'user_profile': user_profile,
    }
    return render(request, 'bank_app/kyc.html', context)

@login_required
def loans(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Handle the case where the profile doesn't exist
        user_profile = UserProfile.objects.create(user=request.user)
    context = {
        'user_profile': user_profile,
    }
    return render(request, 'bank_app/loans.html', context)


def LogoutPage(request):
    logout(request)
    return redirect('reg')

def test_email_status(request):
    from django.core.mail import send_mail
    from django.http import HttpResponse
    from django.conf import settings
    import traceback
    try:
        send_mail(
            "Test SMTP Connection",
            "This is a diagnostic SMTP connection test.",
            settings.DEFAULT_FROM_EMAIL,
            ["roryisaiah66@gmail.com"],
            fail_silently=False
        )
        return HttpResponse("SUCCESS: SMTP connection and email delivery succeeded!")
    except Exception as e:
        return HttpResponse(f"FAILED: {str(e)}<br><br><pre>{traceback.format_exc()}</pre>")

