```vue
<template>
  <div class="amortization-schedule-container">
    <!-- Viewing Mode Selector -->
    <div class="view-mode-selector mb-3">
      <base-button 
        @click="currentView = 'graph'"
        :class="{ 'btn-primary': currentView === 'graph', 'btn-outline-primary': currentView !== 'graph' }"
      >
        Graphical View
      </base-button>
      <base-button 
        @click="currentView = 'table'"
        :class="{ 'btn-primary': currentView === 'table', 'btn-outline-primary': currentView !== 'table' }"
      >
        Tabular View
      </base-button>
    </div>

    <!-- Graph View -->
    <div v-if="currentView === 'graph'" class="graph-container">
      <line-chart 
        :chart-data="chartData" 
        :options="chartOptions"
      />
    </div>

    <!-- Table View -->
    <div v-if="currentView === 'table'" class="table-container">
      <table class="table table-striped table-responsive">
        <thead>
          <tr>
            <th>Month</th>
            <th>Payment</th>
            <th>Principal</th>
            <th>Interest</th>
            <th>Remaining Balance</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="(payment, index) in combinedSchedule" 
            :key="index"
            :class="{
              'table-info': payment.type === 'extra_payment',
              'table-default': payment.type === 'regular'
            }"
          >
            <td>{{ payment.month }}</td>
            <td>{{ formatCurrency(payment.payment) }}</td>
            <td>{{ formatCurrency(payment.principal) }}</td>
            <td>{{ formatCurrency(payment.interest) }}</td>
            <td>{{ formatCurrency(payment.remaining_balance) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import Vue from 'vue';
import { Line } from 'vue-chartjs';
import axios from 'axios';

export default {
  components: {
    'line-chart': Line
  },
  data() {
    return {
      currentView: 'graph',
      regularSchedule: [],
      extraPaymentSchedule: [],
      combinedSchedule: [],
      chartData: {
        labels: [],
        datasets: [
          {
            label: 'Remaining Balance (Regular)',
            borderColor: '#007bff',
            backgroundColor: 'rgba(0, 123, 255, 0.1)',
            data: []
          },
          {
            label: 'Remaining Balance (Extra Payment)',
            borderColor: '#28a745',
            backgroundColor: 'rgba(40, 167, 69, 0.1)',
            data: []
          }
        ]
      },
      chartOptions: {
        responsive: true,
        title: {
          display: true,
          text: 'Mortgage Amortization Schedule'
        },
        scales: {
          xAxes: [{
            scaleLabel: {
              display: true,
              labelString: 'Months'
            }
          }],
          yAxes: [{
            scaleLabel: {
              display: true,
              labelString: 'Remaining Balance ($)'
            },
            ticks: {
              callback: (value) => this.formatCurrency(value)
            }
          }]
        }
      }
    };
  },
  methods: {
    formatCurrency(value) {
      if (!value && value !== 0) return '$0.00';
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(value);
    },

    async fetchAmortizationSchedule() {
      try {
        const params = this.validateInputs(); // Reuse existing validation method
        
        const response = await axios({
          method: 'post',
          url: 'http://localhost:8000/api/amortization-schedule/',
          data: params,
          headers: {
            'Content-Type': 'application/json',
          }
        });

        // Process schedules
        this.processSchedules(response.data);
      } catch (error) {
        console.error('Error fetching amortization schedule:', error);
        // Implement error handling (toast/notification)
      }
    },

    processSchedules(data) {
      // Regular schedule is always present
      this.regularSchedule = (data.regular_schedule || []).map(payment => ({
        ...payment,
        type: 'regular'
      }));

      // Extra payment schedule is optional
      this.extraPaymentSchedule = (data.extra_payment_schedule || []).map(payment => ({
        ...payment,
        type: 'extra_payment'
      }));

      // Combine schedules, prioritizing extra payment schedule if exists
      this.combinedSchedule = this.extraPaymentSchedule.length > 0 
        ? this.extraPaymentSchedule 
        : this.regularSchedule;

      // Prepare chart data
      this.prepareChartData();
    },

    prepareChartData() {
      // Reset chart data
      this.chartData.labels = [];
      this.chartData.datasets[0].data = [];
      this.chartData.datasets[1].data = [];

      // Populate regular schedule data
      this.regularSchedule.forEach((payment, index) => {
        this.chartData.labels.push(index + 1);
        this.chartData.datasets[0].data.push(payment.remaining_balance);
      });

      // If extra payment schedule exists, add it to the chart
      if (this.extraPaymentSchedule.length > 0) {
        this.extraPaymentSchedule.forEach((payment, index) => {
          // Ensure we don't duplicate labels
          if (index >= this.chartData.labels.length) {
            this.chartData.labels.push(index + 1);
          }
          this.chartData.datasets[1].data.push(payment.remaining_balance);
        });
      }

      // Force chart update
      this.$nextTick(() => {
        this.$refs.chart.update();
      });
    }
  },
  mounted() {
    // Optionally trigger fetch on component mount
    // Or bind to a button click in parent component
    this.fetchAmortizationSchedule();
  }
}
</script>

<style scoped>
.amortization-schedule-container {
  padding: 20px;
}

.view-mode-selector {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 20px;
}

.graph-container, .table-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.table {
  font-size: 0.9rem;
}

.table-info {
  background-color: rgba(0, 123, 255, 0.1);
}
</style>
```
