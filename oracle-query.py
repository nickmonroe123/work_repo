<template>
  <card>
    <h5 slot="header" class="title">Mortgage Calculator</h5>
    <form @submit.prevent="submitMortgageData">
      <div class="row">
        <div class="col-md-4">
          <base-input
            type="text"
            label="Original Loan Amount"
            placeholder="$100,000"
            v-model="original_loan"
          >
          </base-input>
        </div>
        <div class="col-md-4">
          <base-input
            type="text"
            label="Current Loan Amount"
            placeholder="$100,000"
            v-model="current_loan"
          >
          </base-input>
        </div>
        <div class="col-md-4">
          <base-input
            type="text"
            label="Closing Date"
            placeholder="2021-12-12"
            v-model="closing_date"
          >
          </base-input>
        </div>
      </div>

      <div class="row">
        <div class="col-md-4">
          <base-input
            type="text"
            label="Interest Rate"
            placeholder="4%"
            v-model="interest_rate"
          >
          </base-input>
        </div>
        <div class="col-md-4">
          <base-input
            type="text"
            label="Loan Term Years"
            placeholder="30"
            v-model="loan_term"
          >
          </base-input>
        </div>
        <div class="col-md-4">
          <base-input
            type="text"
            label="Extra Monthly Payments"
            placeholder="$300"
            v-model="extra_monthly"
          >
          </base-input>
        </div>
      </div>

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
      extra_monthly: ''
    };
  },
  methods: {
    validateInputs() {
      // Remove $ and % signs, convert to numbers
      const cleanNumber = (val) => parseFloat(val.replace(/[$%]/g, ''));

      // Validate closing date (yyyy-mm-dd format)
      const validateClosingDate = (date) => {
        const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
        if (!dateRegex.test(date)) {
          throw new Error('Closing date must be in yyyy-mm-dd format');
        }

        // Optional: Additional date validation
        const parsedDate = new Date(date);
        if (isNaN(parsedDate.getTime())) {
          throw new Error('Invalid date');
        }

        return date;
      };

      // Validate interest rate
      const validateInterestRate = (rate) => {
        const numRate = cleanNumber(rate);
        if (isNaN(numRate) || numRate < 0 || numRate > 20) {
          throw new Error('Interest rate must be between 0% and 20%');
        }
        return numRate;
      };

      // Validate loan term
      const validateLoanTerm = (term) => {
        const numTerm = cleanNumber(term);
        const validTerms = [15, 20, 30];
        if (!validTerms.includes(numTerm)) {
          throw new Error('Loan term must be 15, 20, or 30 years');
        }
        return numTerm;
      };

      // Check if all fields are filled
      const requiredFields = [
        'original_loan',
        'current_loan',
        'closing_date',
        'interest_rate',
        'loan_term',
        'extra_monthly'
      ];

      for (let field of requiredFields) {
        if (!this[field]) {
          throw new Error(`Please fill in the ${field.replace(/_/g, ' ')} field`);
        }
      }

      // Return validated and cleaned values
      return {
        loan_amount: cleanNumber(this.original_loan),
        current_loan_amount: cleanNumber(this.current_loan),
        original_date: validateClosingDate(this.closing_date),
        interest_rate: validateInterestRate(this.interest_rate),
        loan_term_years: validateLoanTerm(this.loan_term),
        extra_monthly_payment: cleanNumber(this.extra_monthly)
      };
    },

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
        const response = await axios.post('http://127.0.0.1:8000/api/mortgage/pay-ahead/', params);

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

    async submitAmortizationSchedule() {
      try {
        const params = this.validateInputs();
        const response = await axios.post('http://127.0.0.1:8000/api/mortgage/amortization/', params);
        console.log('Amortization Schedule Response:', response.data);
      } catch (error) {
        this.handleError(error);
      }
    },

    async submitAdvancedAnalytics() {
      try {
        const params = this.validateInputs();
        const response = await axios.post('http://127.0.0.1:8000/api/mortgage/advanced-analytics/', params);
        console.log('Advanced Analytics Response:', response.data);
      } catch (error) {
        this.handleError(error);
      }
    },

    handleError(error) {
      // If it's a validation error, show the specific message
      if (error.message) {
        alert(error.message);
      } else {
        // Generic error handling for API errors
        console.error('API Call Error:', error);

        if (error.response) {
          console.error('Error response:', error.response.data);
          alert(`Error: ${error.response.data.message || 'Something went wrong'}`);
        } else if (error.request) {
          console.error('No response received:', error.request);
          alert('No response from server. Please check your connection.');
        } else {
          console.error('Error:', error.message);
          alert('An unexpected error occurred');
        }
      }
    }
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
