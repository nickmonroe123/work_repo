# mortgage/advanced_calculations.py
import numpy as np
import pandas as pd
from typing import Dict, List, Any
from datetime import date, timedelta

class MortgageAdvancedAnalytics:
    def __init__(self, loan_amount, current_loan_amount, original_date, interest_rate, loan_term_years):
        """
        Advanced mortgage analytics engine
        """
        self.loan_amount = float(loan_amount)
        self.current_loan_amount = float(current_loan_amount)
        self.original_date = original_date
        self.interest_rate = float(interest_rate)
        self.loan_term_years = int(loan_term_years)
    
    def compare_refinancing_scenarios(self) -> Dict[str, Any]:
        """
        Comprehensive refinancing analysis
        
        Calculates potential savings and breakeven points for different refinancing options
        """
        refinancing_scenarios = [
            {"rate": self.interest_rate - 1, "name": "Conservative Rate Reduction"},
            {"rate": self.interest_rate - 1.5, "name": "Moderate Rate Reduction"},
            {"rate": self.interest_rate - 2, "name": "Aggressive Rate Reduction"}
        ]
        
        scenarios_analysis = []
        
        for scenario in refinancing_scenarios:
            new_rate = scenario['rate']
            
            # Skip invalid scenarios
            if new_rate <= 0:
                continue
            
            # Calculate new monthly payment
            new_monthly_payment = self.calculate_monthly_payment(
                loan_amount=self.current_loan_amount,
                interest_rate=new_rate,
                loan_term_years=self.loan_term_years
            )
            
            # Current monthly payment
            current_monthly_payment = self.calculate_monthly_payment(
                loan_amount=self.current_loan_amount,
                interest_rate=self.interest_rate,
                loan_term_years=self.loan_term_years
            )
            
            # Monthly savings
            monthly_savings = current_monthly_payment - new_monthly_payment
            
            # Estimate closing costs (typically 2-5% of loan amount)
            estimated_closing_costs = self.current_loan_amount * 0.03  # 3% assumption
            
            # Calculate breakeven point
            breakeven_months = estimated_closing_costs / monthly_savings if monthly_savings > 0 else float('inf')
            
            # Total interest comparison
            current_total_interest = self.calculate_total_interest(
                loan_amount=self.current_loan_amount,
                interest_rate=self.interest_rate,
                loan_term_years=self.loan_term_years
            )
            
            new_total_interest = self.calculate_total_interest(
                loan_amount=self.current_loan_amount,
                interest_rate=new_rate,
                loan_term_years=self.loan_term_years
            )
            
            scenarios_analysis.append({
                "scenario_name": scenario['name'],
                "new_interest_rate": new_rate,
                "current_monthly_payment": round(current_monthly_payment, 2),
                "new_monthly_payment": round(new_monthly_payment, 2),
                "monthly_savings": round(monthly_savings, 2),
                "estimated_closing_costs": round(estimated_closing_costs, 2),
                "breakeven_months": round(breakeven_months, 1),
                "current_total_interest": round(current_total_interest, 2),
                "new_total_interest": round(new_total_interest, 2),
                "total_interest_savings": round(current_total_interest - new_total_interest, 2)
            })
        
        return scenarios_analysis
    
    def calculate_monthly_payment(self, loan_amount, interest_rate, loan_term_years):
        """
        Standard monthly payment calculation
        """
        monthly_rate = interest_rate / 100 / 12
        total_months = loan_term_years * 12
        
        monthly_payment = loan_amount * (
            monthly_rate * (1 + monthly_rate) ** total_months
        ) / ((1 + monthly_rate) ** total_months - 1)
        
        return monthly_payment
    
    def calculate_total_interest(self, loan_amount, interest_rate, loan_term_years):
        """
        Calculate total interest over loan lifetime
        """
        monthly_payment = self.calculate_monthly_payment(
            loan_amount, interest_rate, loan_term_years
        )
        total_paid = monthly_payment * (loan_term_years * 12)
        total_interest = total_paid - loan_amount
        return total_interest
    
    def tax_deduction_analysis(self) -> Dict[str, Any]:
        """
        Mortgage interest tax deduction analysis
        
        Estimates potential tax benefits based on mortgage interest
        """
        # Assumptions about tax brackets and standard deduction
        standard_deduction = 13850  # 2023 standard deduction for single filer
        
        # Calculate total annual interest
        annual_interest = self.calculate_total_interest(
            self.current_loan_amount, 
            self.interest_rate, 
            1  # Calculate for one year
        )
        
        # Simplified tax benefit calculation
        tax_brackets = [
            {"bracket": 22, "rate": 0.22},
            {"bracket": 12, "rate": 0.12},
            {"bracket": 10, "rate": 0.10}
        ]
        
        tax_benefits = []
        for tax_info in tax_brackets:
            # Check if mortgage interest exceeds standard deduction
            if annual_interest > standard_deduction:
                deductible_amount = min(annual_interest, 750000)  # Mortgage interest cap
                tax_savings = deductible_amount * tax_info['rate']
                
                tax_benefits.append({
                    "tax_bracket": tax_info['bracket'],
                    "annual_mortgage_interest": round(annual_interest, 2),
                    "deductible_amount": round(deductible_amount, 2),
                    "estimated_tax_savings": round(tax_savings, 2)
                })
        
        return tax_benefits
    
    def inflation_adjusted_payment_analysis(self) -> Dict[str, Any]:
        """
        Calculate how mortgage payments change with inflation
        """
        # Typical inflation rate
        avg_inflation_rate = 0.03  # 3% annual inflation
        
        # Current monthly payment
        current_monthly_payment = self.calculate_monthly_payment(
            self.current_loan_amount, 
            self.interest_rate, 
            self.loan_term_years
        )
        
        # Inflation-adjusted analysis
        inflation_scenarios = []
        for years in [5, 10, 15, 20, 30]:
            # Calculate equivalent payment with inflation
            inflation_adjusted_payment = current_monthly_payment * ((1 + avg_inflation_rate) ** years)
            
            inflation_scenarios.append({
                "years_from_now": years,
                "current_monthly_payment": round(current_monthly_payment, 2),
                "inflation_adjusted_payment": round(inflation_adjusted_payment, 2),
                "real_value_change_percentage": round(((inflation_adjusted_payment / current_monthly_payment) - 1) * 100, 2)
            })
        
        return inflation_scenarios
    
    def equity_and_appreciation_analysis(self) -> Dict[str, Any]:
        """
        Estimate home equity and potential appreciation
        """
        # Assumptions about home appreciation
        appreciation_rates = [0.03, 0.04, 0.05]  # 3%, 4%, 5% annual appreciation
        
        equity_scenarios = []
        for rate in appreciation_rates:
            scenarios = []
            
            # Calculate equity and home value over time
            for years in [5, 10, 15, 20]:
                # Initial property value assumption (based on original loan amount)
                initial_property_value = self.loan_amount * 1.1  # 10% buffer
                
                # Projected property value
                projected_value = initial_property_value * ((1 + rate) ** years)
                
                # Projected remaining loan balance
                monthly_payment = self.calculate_monthly_payment(
                    self.current_loan_amount, 
                    self.interest_rate, 
                    self.loan_term_years
                )
                remaining_balance = self.current_loan_amount - (monthly_payment * 12 * years)
                remaining_balance = max(remaining_balance, 0)
                
                # Calculate equity
                equity = projected_value - remaining_balance
                
                scenarios.append({
                    "years": years,
                    "appreciation_rate": rate * 100,
                    "initial_property_value": round(initial_property_value, 2),
                    "projected_property_value": round(projected_value, 2),
                    "remaining_loan_balance": round(remaining_balance, 2),
                    "projected_equity": round(equity, 2)
                })
            
            equity_scenarios.extend(scenarios)
        
        return equity_scenarios

# mortgage/views.py (Add to existing views)
class MortgageAdvancedAnalyticsView(APIView):
    def post(self, request):
        """
        Provide comprehensive mortgage analytics
        """
        serializer = MortgageCalculationSerializer(data=request.data)
        
        if serializer.is_valid():
            validated_data = serializer.validated_data
            
            # Create advanced analytics instance
            analytics = MortgageAdvancedAnalytics(
                loan_amount=validated_data['loan_amount'],
                current_loan_amount=validated_data['current_loan_amount'],
                original_date=validated_data['original_date'],
                interest_rate=validated_data['interest_rate'],
                loan_term_years=validated_data['loan_term_years']
            )
            
            # Collect advanced analyses
            advanced_analytics = {
                "refinancing_scenarios": analytics.compare_refinancing_scenarios(),
                "tax_deduction_analysis": analytics.tax_deduction_analysis(),
                "inflation_adjusted_payments": analytics.inflation_adjusted_payment_analysis(),
                "equity_and_appreciation": analytics.equity_and_appreciation_analysis()
            }
            
            return Response(advanced_analytics, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Update urls.py
urlpatterns = [
    # ... existing paths ...
    path('advanced-analytics/', MortgageAdvancedAnalyticsView.as_view(), name='mortgage-advanced-analytics'),
]
