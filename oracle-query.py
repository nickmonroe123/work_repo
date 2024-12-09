<template>
  <div class="advanced-analytics-wrapper">
    <div v-if="!analyticsData" class="text-center text-gray-400 p-8">
      No analytics data available. Please submit the form to see the analysis.
    </div>
    <div v-else>
      <div class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.value"
          @click="activeTab = tab.value"
          :class="['tab', { active: activeTab === tab.value }]"
        >
          {{ tab.label }}
        </button>
      </div>
      
      <div class="chart-container">
        <LineChart
          v-if="activeTab !== 'refinancing'"
          :chartdata="chartData"
          :options="chartOptions"
          :styles="{ height: '400px' }"
        />
        <div v-else class="refinancing-grid">
          <div v-for="(scenario, index) in analyticsData.refinancing_scenarios" 
               :key="index"
               class="scenario-card"
          >
            <h3>{{ scenario.scenario_name }}</h3>
            <div class="scenario-details">
              <p>New Rate: {{ formatPercent(scenario.new_interest_rate) }}</p>
              <p>Monthly Savings: {{ formatCurrency(scenario.monthly_savings) }}</p>
              <p>Break-even: {{ Math.round(scenario.breakeven_months) }} months</p>
              <p class="savings">Total Savings: {{ formatCurrency(scenario.total_interest_savings) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdvancedAnalyticsChart',
  props: {
    analyticsData: {
      type: Object,
      default: () => null
    }
  },
  data() {
    return {
      activeTab: 'refinancing',
      tabs: [
        { value: 'refinancing', label: 'Refinancing Options' },
        { value: 'inflation', label: 'Inflation Impact' },
        { value: 'equity', label: 'Equity Projection' }
      ],
      appreciationRate: 3
    }
  },
  methods: {
    formatCurrency(value) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(value)
    },
    formatPercent(value) {
      return `${value}%`
    }
  },
  computed: {
    chartData() {
      if (!this.analyticsData) return { labels: [], datasets: [] }

      switch (this.activeTab) {
        case 'inflation':
          return {
            labels: this.analyticsData.inflation_adjusted_payments.map(item => `Year ${item.years_from_now}`),
            datasets: [
              {
                label: 'Inflation Adjusted Payment',
                data: this.analyticsData.inflation_adjusted_payments.map(item => item.inflation_adjusted_payment),
                borderColor: '#22c55e',
                fill: false
              },
              {
                label: 'Current Payment',
                data: this.analyticsData.inflation_adjusted_payments.map(item => item.current_monthly_payment),
                borderColor: '#3b82f6',
                fill: false
              }
            ]
          }

        case 'equity':
          const filteredEquity = this.analyticsData.equity_and_appreciation.filter(
            item => item.appreciation_rate === this.appreciationRate
          )
          return {
            labels: filteredEquity.map(item => `Year ${item.years}`),
            datasets: [
              {
                label: 'Property Value',
                data: filteredEquity.map(item => item.projected_property_value),
                borderColor: '#3b82f6',
                fill: false
              },
              {
                label: 'Equity',
                data: filteredEquity.map(item => item.projected_equity),
                borderColor: '#22c55e',
                fill: false
              },
              {
                label: 'Loan Balance',
                data: filteredEquity.map(item => item.remaining_loan_balance),
                borderColor: '#ef4444',
                fill: false
              }
            ]
          }

        default:
          return { labels: [], datasets: [] }
      }
    },
    chartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        legend: {
          position: 'top',
          labels: {
            fontColor: 'white'
          }
        },
        scales: {
          yAxes: [{
            ticks: {
              fontColor: 'white',
              callback: value => this.formatCurrency(value)
            }
          }],
          xAxes: [{
            ticks: {
              fontColor: 'white'
            }
          }]
        },
        tooltips: {
          callbacks: {
            label: (tooltipItem, data) => {
              let label = data.datasets[tooltipItem.datasetIndex].label || ''
              if (label) {
                label += ': '
              }
              label += this.formatCurrency(tooltipItem.yLabel)
              return label
            }
          }
        }
      }
    }
  }
}
</script>

<style scoped>
.advanced-analytics-wrapper {
  background-color: #27293d;
  border-radius: 10px;
  padding: 20px;
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.tab {
  padding: 8px 16px;
  background-color: #1e1e2f;
  border: none;
  border-radius: 5px;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s;
}

.tab.active {
  background-color: #3b82f6;
}

.chart-container {
  position: relative;
  height: 400px;
}

.refinancing-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px 0;
}

.scenario-card {
  background-color: #1e1e2f;
  border-radius: 10px;
  padding: 20px;
}

.scenario-card h3 {
  color: white;
  margin-bottom: 15px;
  font-size: 18px;
}

.scenario-details {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.scenario-details p {
  color: #a0aec0;
}

.scenario-details .savings {
  color: #22c55e;
  font-weight: bold;
}

.appreciation-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.appreciation-button {
  padding: 8px 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.appreciation-button.active {
  background-color: #3b82f6;
  color: white;
}
</style>
