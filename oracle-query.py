<template>
  <card>
    <h5 slot="header" class="title">Mortgage Calculator</h5>
    
    <form @submit.prevent="submitMortgageData">
      <!-- Previous input fields remain the same -->

      <base-button @click="submitPayAheadEstimator" native-type="button" type="primary" class="btn-fill">
        Pay Ahead Estimator
      </base-button>
      <!-- Other buttons remain the same -->
    </form>

    <!-- Output Section with Explicit Rendering -->
    <div v-if="showResults" class="calculation-results mt-4">
      <h4 class="text-center mb-4">Mortgage Optimization Results</h4>
      <div class="row">
        <div class="col-md-4 mb-3">
          <div class="result-card">
            <div class="result-icon">
              <i class="tim-icons icon-money-coins"></i>
            </div>
            <div class="result-content">
              <h5>Remaining Interest</h5>
              <p class="text-primary">{{ formattedRemainingInterest }}</p>
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
              <p class="text-success">{{ monthsSaved }} months</p>
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
                {{ newPayoffTimeMonths }} months 
                ({{ newPayoffTimeYears }} years)
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
              <p class="text-danger">{{ formattedTotalInterestPaid }}</p>
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
              <p class="text-success">{{ formattedTotalInterestSaved }}</p>
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
                <span class="text-success">{{ formattedTotalInterestSaved }}</span> 
                and shorten your loan by 
                <span class="text-warning">{{ monthsSaved }} months</span>.
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
import Vue from 'vue';

export default {
  data() {
    return {
      original_loan: '',
      current_loan: '',
      closing_date: '',
      interest_rate: '',
      loan_term: '',
      extra_monthly: '',
      
      // Explicit reactive properties for results
      showResults: false,
      remainingInterest: 0,
      monthsSaved: 0,
      newPayoffTimeMonths: 0,
      newPayoffTimeYears: 0,
      totalInterestPaid: 0,
      totalInterestSaved: 0
    };
  },
  computed: {
    // Computed properties for formatted values
    formattedRemainingInterest() {
      return this.formatCurrency(this.remainingInterest);
    },
    formattedTotalInterestPaid() {
      return this.formatCurrency(this.totalInterestPaid);
    },
    formattedTotalInterestSaved() {
      return this.formatCurrency(this.totalInterestSaved);
    }
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
        
        const response = await axios({
          method: 'post',
          url: 'http://localhost:8000/api/pay-ahead-estimator/',
          data: params,
          headers: {
            'Content-Type': 'application/json',
          }
        });

        console.log('Full API Response:', response.data);

        // Explicitly update reactive properties
        // Use Vue.set to ensure reactivity for nested updates
        this.showResults = true;
        
        // Use Vue.set or this.$set to ensure reactivity
        Vue.set(this, 'remainingInterest', response.data.remaining_interest || 0);
        Vue.set(this, 'monthsSaved', response.data.months_saved || 0);
        Vue.set(this, 'newPayoffTimeMonths', response.data.new_payoff_time_months || 0);
        Vue.set(this, 'newPayoffTimeYears', response.data.new_payoff_time_years || 0);
        Vue.set(this, 'totalInterestPaid', response.data.total_interest_paid || 0);
        Vue.set(this, 'totalInterestSaved', response.data.total_interest_saved || 0);

        // Force update if needed
        this.$forceUpdate();

      } catch (error) {
        // Error handling remains the same as previous example
        console.error('Error in API call:', error);
        this.showResults = false;
      }
    },

    // Other methods remain the same
  }
};
</script>

<style scoped>
/* Previous styling remains the same */
</style>
