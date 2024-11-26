# mortgage/calculations.py
import datetime
import math

class MortgageCalculator:
    def __init__(self, loan_amount, current_loan_amount, original_date, interest_rate, loan_term_years):
        """
        Initialize mortgage calculation parameters
        
        :param loan_amount: Original loan amount
        :param current_loan_amount: Current remaining loan amount
        :param original_date: Date when mortgage was originated
        :param interest_rate: Annual interest rate (as a percentage)
        :param loan_term_years: Loan term in years
        """
        self.original_loan_amount = float(loan_amount)
        self.current_loan_amount = float(current_loan_amount)
        self.original_date = original_date
        self.interest_rate = float(interest_rate) / 100  # Convert to decimal
        self.loan_term_years = int(loan_term_years)
        
        # Monthly calculations
        self.monthly_rate = self.interest_rate / 12
        self.total_months = self.loan_term_years * 12
    
    def calculate_standard_payment(self):
        """
        Calculate standard monthly mortgage payment based on current loan amount
        """
        monthly_payment = self.current_loan_amount * (
            self.monthly_rate * (1 + self.monthly_rate) ** self._remaining_months()
        ) / ((1 + self.monthly_rate) ** self._remaining_months() - 1)
        return round(monthly_payment, 2)
    
    def _remaining_months(self):
        """
        Calculate remaining months based on original and current loan amount
        """
        # Calculate how many months have passed and remaining months
        months_paid = round(
            (self.original_loan_amount - self.current_loan_amount) / 
            (self.original_loan_amount / self.total_months)
        )
        return max(self.total_months - months_paid, 1)
    
    def calculate_total_remaining_interest(self):
        """
        Calculate total interest to be paid from current point
        """
        monthly_payment = self.calculate_standard_payment()
        remaining_months = self._remaining_months()
        
        total_paid = monthly_payment * remaining_months
        total_interest = total_paid - self.current_loan_amount
        return round(total_interest, 2)
    
    def calculate_original_total_interest(self):
        """
        Calculate total interest that would have been paid on original schedule
        """
        original_monthly_payment = self.original_loan_amount * (
            self.monthly_rate * (1 + self.monthly_rate) ** self.total_months
        ) / ((1 + self.monthly_rate) ** self.total_months - 1)
        
        total_paid = original_monthly_payment * self.total_months
        total_interest = total_paid - self.original_loan_amount
        return round(total_interest, 2)
    
    def calculate_extra_payment_scenarios(self, extra_monthly_payment):
        """
        Calculate scenarios with extra monthly payments
        
        :param extra_monthly_payment: Additional amount paid monthly
        :return: Dictionary of extra payment scenarios
        """
        standard_monthly_payment = self.calculate_standard_payment()
        total_monthly_payment = standard_monthly_payment + extra_monthly_payment
        
        # Remaining balance tracker
        remaining_balance = self.current_loan_amount
        month_count = 0
        total_interest_paid = 0
        
        while remaining_balance > 0:
            # Calculate interest for the month
            monthly_interest = remaining_balance * self.monthly_rate
            total_interest_paid += monthly_interest
            
            # Apply payment
            principal_payment = total_monthly_payment - monthly_interest
            remaining_balance -= principal_payment
            
            month_count += 1
            
            # Prevent infinite loop
            if month_count > (self.loan_term_years * 12 * 2):
                break
        
        # Calculate time saved and total interest saved
        original_remaining_interest = self.calculate_total_remaining_interest()
        months_saved = self._remaining_months() - month_count
        interest_saved = original_remaining_interest - total_interest_paid
        
        return {
            'new_payoff_time_months': month_count,
            'new_payoff_time_years': round(month_count / 12, 2),
            'months_saved': max(months_saved, 0),
            'current_remaining_interest': round(original_remaining_interest, 2),
            'total_interest_paid_with_extra': round(total_interest_paid, 2),
            'total_interest_saved': round(interest_saved, 2)
        }

# mortgage/serializers.py
from rest_framework import serializers

class MortgageCalculationSerializer(serializers.Serializer):
    loan_amount = serializers.FloatField()
    current_loan_amount = serializers.FloatField()
    original_date = serializers.DateField()
    interest_rate = serializers.FloatField()
    loan_term_years = serializers.IntegerField()
    extra_monthly_payment = serializers.FloatField(required=False, default=0)
    
    def validate(self, data):
        """
        Additional validation for mortgage calculation inputs
        """
        if data['loan_term_years'] not in [15, 20, 30]:
            raise serializers.ValidationError("Loan term must be 15, 20, or 30 years")
        
        if data['interest_rate'] <= 0 or data['interest_rate'] > 30:
            raise serializers.ValidationError("Interest rate must be between 0 and 30")
        
        if data['current_loan_amount'] > data['loan_amount']:
            raise serializers.ValidationError("Current loan amount cannot be greater than original loan amount")
        
        return data

# mortgage/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import MortgageCalculationSerializer
from .calculations import MortgageCalculator

class MortgageCalculationView(APIView):
    def post(self, request):
        """
        Handle mortgage calculation POST request
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
            
            # Calculate standard mortgage details
            monthly_payment = calculator.calculate_standard_payment()
            remaining_interest = calculator.calculate_total_remaining_interest()
            original_total_interest = calculator.calculate_original_total_interest()
            
            # Calculate extra payment scenario if provided
            extra_payment_scenario = calculator.calculate_extra_payment_scenarios(
                validated_data.get('extra_monthly_payment', 0)
            )
            
            # Prepare response
            response_data = {
                'monthly_payment': monthly_payment,
                'original_total_interest': original_total_interest,
                'remaining_interest': remaining_interest,
                'extra_payment_scenario': extra_payment_scenario
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
