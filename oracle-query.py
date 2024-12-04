```vue
<template>
  <card>
    <h5 slot="header" class="title">Mortgage Calculator</h5>
    
    <form @submit.prevent="submitMortgageData">
      <!-- Input Fields -->
      <div class="row">
        <div class="col-md-4">
          <base-input
            label="Original Loan Amount"
            type="number"
            v-model="original_loan"
            placeholder="Enter loan amount"
            required
          />
        </div>
        <div class="col-md-4">
          <base-input
            label="Current Loan Balance"
            type="number"
            v-model="current_loan"
            placeholder="Enter current balance"
            required
          />
        </div>
        <div class="col-md-4">
          <base-input
            label="Closing Date"
            type="date"
            v-model="closing_date"
            required
          />
        </div>
      </div>

      <div class="row">
        <div class="col-md-4">
          <base-input
            label="Interest Rate (%)"
            type="number"
            step="0.01"
            v-model="interest_rate"
            placeholder="Enter interest rate"
            required
          />
        </div>
        <div class="col-md-4">
          <base-input
            label="Loan Term (Months)"
            type="number"
            v-model="loan_term"
            placeholder="Enter loan term"
            required
          />
        </div>
        <div class="col-md-4">
          <base-input
            label="Extra Monthly Payment"
            type="number"
            v-model="extra_monthly"
            placeholder="Enter extra payment"
          />
        </div>
      </div>

      <!-- Buttons -->
      <div class="button-container">
        <base-button 
          @click="submitPayAheadEstimator" 
          native-type="button" 
          type="primary" 
          class="btn-fill"
        >
          Pay Ahead Estimator
        </base-button>

        <base-button 
          @click="fetchAmortizationSchedule" 
          native-type="button" 
          type="info" 
          class="btn-fill"
        >
          View Amortization Schedule
        </base-button>
      </div>
    </form>

    <!-- Pay Ahead Results Section -->
    <div v-if="showResults" class="calculation-results mt-4">
      <h4 class="text-center mb-4">Mortgage Optimization Results</h4>
      <div class="row">
        <!-- Existing result cards remain the same -->
        <!-- ... (previous result cards) ... -->
      </div>
    </div>

    <!-- Amortization Schedule Modal -->
    <modal 
      v-if="showAmortizationSchedule" 
      @close="showAmortizationSchedule = false"
    >
      <template slot="header">
        <h4 class="modal-title">Amortization Schedule</h4>
      </template>
      
      <template slot="body">
        <amortization-schedule-component 
          :schedule-data="amortizationScheduleData"
          @close="showAmortizationSchedule = false"
        />
      </template>
    </modal>
  </card>
</template>

<script>
import axios from 'axios';
import Vue from 'vue';
import AmortizationScheduleComponent from './AmortizationScheduleComponent.vue'; // New component

export default {
  components: {
    AmortizationScheduleComponent
  },
  data() {
    return {
      // Existing data properties
      original_loan: '',
      current_loan: '',
      closing_date: '',
      interest_rate: '',
      loan_term: '',
      extra_monthly: '',
      
      // Existing results properties
      showResults: false,
      remainingInterest: 0,
      monthsSaved: 0,
      newPayoffTimeMonths: 0,
      newPayoffTimeYears: 0,
      totalInterestPaid: 0,
      totalInterestSaved: 0,

      // New properties for Amortization Schedule
      showAmortizationSchedule: false,
      amortizationScheduleData: null,
      isLoading: false,
      errorMessage: ''
    };
  },
  computed: {
    // Existing computed properties
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
    // Existing methods
    formatCurrency(value) {
      const num = parseFloat(value);
      if (isNaN(num)) return '$0.00';
      
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(num);
    },

    validateInputs() {
      // Comprehensive input validation method
      const params = {
        original_loan: parseFloat(this.original_loan.trim().replace(/[^0-9.]/g, '')),
        current_loan: parseFloat(this.current_loan.trim().replace(/[^0-9.]/g, '')),
        closing_date: this.closing_date,
        interest_rate: parseFloat(this.interest_rate),
        loan_term: parseInt(this.loan_term),
        extra_monthly: parseFloat(this.extra_monthly.trim().replace(/[^0-9.]/g, '') || '0')
      };

      const validationErrors = [];

      if (isNaN(params.original_loan) || params.original_loan <= 0) {
        validationErrors.push('Invalid original loan amount');
      }
      if (isNaN(params.current_loan) || params.current_loan <= 0) {
        validationErrors.push('Invalid current loan amount');
      }
      if (isNaN(params.interest_rate) || params.interest_rate <= 0) {
        validationErrors.push('Invalid interest rate');
      }
      if (isNaN(params.loan_term) || params.loan_term <= 0) {
        validationErrors.push('Invalid loan term');
      }
      if (isNaN(params.extra_monthly) || params.extra_monthly < 0) {
        validationErrors.push('Invalid extra monthly payment');
      }

      if (validationErrors.length > 0) {
        console.error('Validation Errors:', validationErrors);
        throw new Error(validationErrors.join(', '));
      }

      return params;
    },

    async submitPayAheadEstimator() {
      try {
        const params = this.validateInputs();
        
        this.showResults = false;
        this.isLoading = true;

        const response = await axios({
          method: 'post',
          url: 'http://localhost:8000/api/pay-ahead-estimator/',
          data: params,
          headers: {
            'Content-Type': 'application/json',
          }
        });

        this.updatePayAheadResults(response.data);

      } catch (error) {
        console.error('Error in API call:', error);
        this.errorMessage = error.response?.data?.message || 
                            error.message || 
                            'An unexpected error occurred';
        this.displayErrorNotification(this.errorMessage);
      } finally {
        this.isLoading = false;
      }
    },

    updatePayAheadResults(data) {
      this.showResults = true;
      
      this.remainingInterest = data.remaining_interest || 0;
      this.monthsSaved = data.months_saved || 0;
      this.newPayoffTimeMonths = data.new_payoff_time_months || 0;
      this.newPayoffTimeYears = data.new_payoff_time_years || 0;
      this.totalInterestPaid = data.total_interest_paid || 0;
      this.totalInterestSaved = data.total_interest_saved || 0;
    },

    async fetchAmortizationSchedule() {
      try {
        const params = this.validateInputs();
        
        this.isLoading = true;
        this.errorMessage = '';

        const response = await axios({
          method: 'post',
          url: 'http://localhost:8000/api/amortization-schedule/',
          data: params,
          headers: {
            'Content-Type': 'application/json',
          }
        });

        // Store schedule data and show modal
        this.amortizationScheduleData = response.data;
        this.showAmortizationSchedule = true;

      } catch (error) {
        console.error('Error fetching amortization schedule:', error);
        this.errorMessage = error.response?.data?.message || 
                            error.message || 
                            'Unable to fetch amortization schedule';
        this.displayErrorNotification(this.errorMessage);
      } finally {
        this.isLoading = false;
      }
    },

    displayErrorNotification(message) {
      // Implement using your UI framework's toast/notification system
      // This is a placeholder - replace with actual notification method
      alert(message);
    }
  }
};
</script>

<style scoped>
.button-container {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.calculation-results {
  margin-top: 20px;
}

/* Additional styling as needed */
</style>
```
