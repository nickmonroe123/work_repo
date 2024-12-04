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
    // Validation method to ensure all fields are filled and in correct format
    validateInputs() {
      // Remove $ and % signs, convert to numbers
      const cleanNumber = (val) => parseFloat(val.replace(/[$%]/g, ''));

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
          alert(`Please fill in the ${field.replace(/_/g, ' ')} field`);
          return false;
        }
      }

      // Return an object with cleaned/parsed values
      return {
        original_loan: cleanNumber(this.original_loan),
        current_loan: cleanNumber(this.current_loan),
        closing_date: this.closing_date,
        interest_rate: cleanNumber(this.interest_rate),
        loan_term: cleanNumber(this.loan_term),
        extra_monthly: cleanNumber(this.extra_monthly)
      };
    },

    async submitPayAheadEstimator() {
      const params = this.validateInputs();
      if (!params) return;

      try {
        const response = await axios.post('http://your-django-backend-url/pay-ahead-estimator/', params);
        console.log('Pay Ahead Estimator Response:', response.data);
        // Handle response as needed
      } catch (error) {
        this.handleApiError(error);
      }
    },

    async submitAmortizationSchedule() {
      const params = this.validateInputs();
      if (!params) return;

      try {
        const response = await axios.post('http://your-django-backend-url/amortization-schedule/', params);
        console.log('Amortization Schedule Response:', response.data);
        // Handle response as needed
      } catch (error) {
        this.handleApiError(error);
      }
    },

    async submitAdvancedAnalytics() {
      const params = this.validateInputs();
      if (!params) return;

      try {
        const response = await axios.post('http://your-django-backend-url/advanced-analytics/', params);
        console.log('Advanced Analytics Response:', response.data);
        // Handle response as needed
      } catch (error) {
        this.handleApiError(error);
      }
    },

    // Centralized error handling method
    handleApiError(error) {
      console.error('API Call Error:', error);
      
      if (error.response) {
        // The request was made and the server responded with a status code
        console.error('Error response:', error.response.data);
        console.error('Error status:', error.response.status);
        alert(`Error: ${error.response.data.message || 'Something went wrong'}`);
      } else if (error.request) {
        // The request was made but no response was received
        console.error('No response received:', error.request);
        alert('No response from server. Please check your connection.');
      } else {
        // Something happened in setting up the request
        console.error('Error setting up request:', error.message);
        alert('An unexpected error occurred');
      }
    }
  }
};
</script>
