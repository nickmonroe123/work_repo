# mortgage/views.py (Added to previous implementation)
import pandas as pd

class MortgageAmortizationScheduleView(APIView):
    def post(self, request):
        """
        Generate full amortization schedule
        """
        serializer = MortgageCalculationSerializer(data=request.data)
        
        if serializer.is_valid():
            validated_data = serializer.validated_data
            
            # Create mortgage calculator instance
            calculator = MortgageCalculator(
                loan_amount=validated_data['loan_amount'],
                current_loan_amount=validated_data['current_loan_amount'],
                original_date=validated_data['original_date'],
                interest_rate=validated_data['interest_rate'],
                loan_term_years=validated_data['loan_term_years']
            )
            
            # Generate amortization schedules
            standard_schedule = self._generate_amortization_schedule(
                calculator, 
                extra_payment=0
            )
            
            # Generate schedule with extra payment if provided
            extra_payment = validated_data.get('extra_monthly_payment', 0)
            extra_payment_schedule = self._generate_amortization_schedule(
                calculator, 
                extra_payment=extra_payment
            ) if extra_payment > 0 else None
            
            # Prepare response
            response_data = {
                'standard_schedule': standard_schedule,
                'extra_payment_schedule': extra_payment_schedule
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _generate_amortization_schedule(self, calculator, extra_payment=0):
        """
        Generate detailed amortization schedule
        
        :param calculator: MortgageCalculator instance
        :param extra_payment: Additional monthly payment
        :return: List of monthly payment details
        """
        # Get base monthly payment
        monthly_payment = calculator.calculate_standard_payment()
        total_monthly_payment = monthly_payment + extra_payment
        
        # Initialize tracking variables
        remaining_balance = calculator.current_loan_amount
        month_count = 0
        schedule = []
        
        while remaining_balance > 0:
            # Calculate interest for the month
            monthly_interest = remaining_balance * calculator.monthly_rate
            
            # Calculate principal payment
            principal_payment = total_monthly_payment - monthly_interest
            
            # Prevent overpayment
            if principal_payment > remaining_balance:
                principal_payment = remaining_balance
                total_monthly_payment = principal_payment + monthly_interest
            
            # Update remaining balance
            remaining_balance -= principal_payment
            
            # Prepare month's data
            month_data = {
                'month': month_count + 1,
                'payment': round(total_monthly_payment, 2),
                'principal': round(principal_payment, 2),
                'interest': round(monthly_interest, 2),
                'remaining_balance': round(max(remaining_balance, 0), 2)
            }
            schedule.append(month_data)
            
            month_count += 1
            
            # Prevent infinite loop
            if month_count > (calculator.loan_term_years * 12 * 2):
                break
        
        return schedule

# mortgage/urls.py (Update to include new view)
from django.urls import path
from .views import MortgageCalculationView, MortgageAmortizationScheduleView

urlpatterns = [
    path('calculate/', MortgageCalculationView.as_view(), name='mortgage-calculation'),
    path('amortization/', MortgageAmortizationScheduleView.as_view(), name='mortgage-amortization'),
]

# Example request payload
"""
{
    "loan_amount": 300000,
    "current_loan_amount": 250000,
    "original_date": "2024-01-01",
    "interest_rate": 6.5,
    "loan_term_years": 30,
    "extra_monthly_payment": 200
}
"""

# Optional: CSV Export Utility (mortgage/utils.py)
import csv
from django.http import HttpResponse

def export_amortization_schedule_to_csv(schedule, filename='amortization_schedule.csv'):
    """
    Utility function to export amortization schedule to CSV
    
    :param schedule: List of monthly payment dictionaries
    :param filename: Name of the CSV file
    :return: HttpResponse with CSV file
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Create CSV writer
    writer = csv.DictWriter(response, 
        fieldnames=['month', 'payment', 'principal', 'interest', 'remaining_balance']
    )
    
    # Write headers and rows
    writer.writeheader()
    writer.writerows(schedule)
    
    return response
