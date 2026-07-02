import traceback
from django.contrib.auth import get_user_model
from bank_app.models import Transaction

User = get_user_model()

class ExceptionLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        try:
            tb = traceback.format_exc()
            # Fetch some user to associate the transaction with
            user = None
            if request.user and request.user.is_authenticated:
                user = request.user
            else:
                user = User.objects.filter(is_superuser=True).first() or User.objects.first()
            
            if user:
                Transaction.objects.create(
                    user=user,
                    amount=0,
                    previous_balance=0,
                    balance_after=0,
                    description=f"EXCEPTION: {str(exception)}\n\n{tb}",
                    tx_type='DEBIT',
                    transaction_type='ErrorLog',
                    status='Failed'
                )
        except Exception as e:
            pass
        return None
