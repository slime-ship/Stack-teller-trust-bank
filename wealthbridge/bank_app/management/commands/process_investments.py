# management/commands/process_investments.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from bank_app.models import UserInvestment, InvestmentTransaction
from decimal import Decimal

class Command(BaseCommand):
    help = 'Process completed investments and distribute returns'

    def handle(self, *args, **options):
        now = timezone.now()
        completed_investments = UserInvestment.objects.filter(
            status='ACTIVE',
            end_date__lte=now
        )

        for investment in completed_investments:
            try:
                # Calculate profit
                profit = investment.expected_return - investment.amount_invested

                # Add return to user balance
                user_profile = investment.user.userprofile
                user_profile.balance += investment.expected_return
                user_profile.save()

                # Create transaction record
                InvestmentTransaction.objects.create(
                    user=investment.user,
                    investment=investment,
                    amount=investment.expected_return,
                    transaction_type='RETURN',
                    description=f"Investment return from {investment.investment_plan.name}"
                )

                # Update investment status
                investment.status = 'COMPLETED'
                investment.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Processed investment for {investment.user.username}: "
                        f"${investment.expected_return} returned"
                    )
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error processing investment {investment.id}: {str(e)}"
                    )
                )