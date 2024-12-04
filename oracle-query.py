<template>
  <card>
    <h5 slot="header" class="title">Mortgage Calculator</h5>
    
    <!-- Input Form (Previous Form Remains the Same) -->
    <form @submit.prevent="submitMortgageData">
      <!-- ... (previous input fields remain unchanged) ... -->

      <base-button @click="submitPayAheadEstimator" native-type="button" type="primary" class="btn-fill">
        Pay Ahead Estimator
      </base-button>
      <base-button @click="submitAmortizationSchedule" native-type="button" type="primary" class="btn-fill">
        Amortization Schedule
      </base-button>
      <base-button @click="submitAdvancedAnalytics" native-type="button" type="primary" class="btn-fill">
        Advanced Analytics
      </base-button>
    </form>

    <!-- New Output Section -->
    <div v-if="calculationResult" class="calculation-results mt-4">
      <h4 class="text-center mb-4">Mortgage Optimization Results</h4>
      <div class="row">
        <div class="col-md-4 mb-3">
          <div class="result-card">
            <div class="result-icon">
              <i class="tim-icons icon-money-coins"></i>
            </div>
            <div class="result-content">
              <h5>Remaining Interest</h5>
              <p class="text-primary">{{ formatCurrency(calculationResult.remaining_interest) }}</p>
            </div>
          </div>
        </div>
        
        <div class="col-md-4 mb-3">
          <div class="result-card">
            <div class="result-icon">
              <i class="tim-icons icon-calendar-60"></i>
            </div>
            <div class="result-content">
              <h5>Months Saved</h5>
              <p class="text-success">{{ calculationResult.months_saved }} months</p>
            </div>
          </div>
        </div>
        
        <div class="col-md-4 mb-3">
          <div class="result-card">
            <div class="result-icon">
              <i class="tim-icons icon-time-alarm"></i>
            </div>
            <div class="result-content">
              <h5>New Payoff Time</h5>
              <p class="text-warning">
                {{ calculationResult.new_payoff_time_months }} months 
                ({{ calculationResult.new_payoff_time_years }} years)
              </p>
            </div>
          </div>
        </div>
        
        <div class="col-md-4 mb-3">
          <div class="result-card">
            <div class="result-icon">
              <i class="tim-icons icon-paper"></i>
            </div>
            <div class="result-content">
              <h5>Total Interest Paid</h5>
              <p class="text-danger">{{ formatCurrency(calculationResult.total_interest_paid) }}</p>
            </div>
          </div>
        </div>
        
        <div class="col-md-4 mb-3">
          <div class="result-card">
            <div class="result-icon">
              <i class="tim-icons icon-coins"></i>
            </div>
            <div class="result-content">
              <h5>Total Interest Saved</h5>
              <p class="text-success">{{ formatCurrency(calculationResult.total_interest_saved) }}</p>
            </div>
          </div>
        </div>
        
        <div class="col-md-4 mb-3">
          <div class="result-card">
            <div class="result-icon">
              <i class="tim-icons icon-chart-bar-32"></i>
            </div>
            <div class="result-content">
              <h5>Optimization Summary</h5>
              <p>
                By making extra payments, you can save 
                <span class="text-success">{{ formatCurrency(calculationResult.total_interest_saved) }}</span> 
                and shorten your loan by 
                <span class="text-warning">{{ calculationResult.months_saved }} months</span>.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </card>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      original_loan: '',
      current_loan: '',
      closing_date: '',
      interest_rate: '',
      loan_term: '',
      extra_monthly: '',
      calculationResult: null
    };
  },
  methods: {
    formatCurrency(value) {
      // Ensure value is a number
      const num = parseFloat(value);
      
      // Check if it's a valid number
      if (isNaN(num)) return '$0.00';
      
      // Format as currency
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(num);
    },

    async submitPayAheadEstimator() {
      try {
        const params = this.validateInputs();
        const response = await axios.post('http://your-django-backend-url/pay-ahead-estimator/', params);
        
        // Assuming the response has the 6 outputs you mentioned
        this.calculationResult = {
          remaining_interest: response.data.remaining_interest,
          months_saved: response.data.months_saved,
          new_payoff_time_months: response.data.new_payoff_time_months,
          new_payoff_time_years: response.data.new_payoff_time_years,
          total_interest_paid: response.data.total_interest_paid,
          total_interest_saved: response.data.total_interest_saved
        };

        console.log('Pay Ahead Estimator Response:', response.data);
      } catch (error) {
        this.handleError(error);
      }
    },
    
    // ... (previous methods remain the same)
  }
};
</script>

<style scoped>
.result-card {
  display: flex;
  align-items: center;
  background-color: #27293d;
  border-radius: 10px;
  padding: 15px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
}

.result-card:hover {
  transform: translateY(-5px);
}

.result-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: rgba(255,255,255,0.1);
  margin-right: 15px;
}

.result-icon i {
  font-size: 24px;
  color: #ffffff;
}

.result-content h5 {
  color: #ffffff;
  margin-bottom: 5px;
  font-size: 16px;
}

.result-content p {
  margin: 0;
  font-size: 18px;
  font-weight: bold;
}

.calculation-results {
  background-color: #1e1e2f;
  border-radius: 10px;
  padding: 20px;
}
</style>
