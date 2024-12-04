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
        original_loan: cleanNumber(this.original_loan),
        current_loan: cleanNumber(this.current_loan),
        closing_date: validateClosingDate(this.closing_date),
        interest_rate: validateInterestRate(this.interest_rate),
        loan_term: validateLoanTerm(this.loan_term),
        extra_monthly: cleanNumber(this.extra_monthly)
      };
    },

    async submitPayAheadEstimator() {
      try {
        const params = this.validateInputs();
        const response = await axios.post('http://your-django-backend-url/pay-ahead-estimator/', params);
        console.log('Pay Ahead Estimator Response:', response.data);
      } catch (error) {
        this.handleError(error);
      }
    },

    async submitAmortizationSchedule() {
      try {
        const params = this.validateInputs();
        const response = await axios.post('http://your-django-backend-url/amortization-schedule/', params);
        console.log('Amortization Schedule Response:', response.data);
      } catch (error) {
        this.handleError(error);
      }
    },

    async submitAdvancedAnalytics() {
      try {
        const params = this.validateInputs();
        const response = await axios.post('http://your-django-backend-url/advanced-analytics/', params);
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
