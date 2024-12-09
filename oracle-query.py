<template>
  <div class="amortization-chart-wrapper">
    <div v-if="!chartData.datasets.length" class="text-center text-gray-400 p-8">
      No amortization data available. Please submit the form to see the schedule.
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
        <Line
          :data="chartData"
          :options="chartOptions"
          class="chart"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

export default {
  name: 'AmortizationChart',
  components: {
    Line
  },
  props: {
    scheduleData: {
      type: Object,
      default: () => ({ standard_schedule: [], extra_payment_schedule: [] })
    }
  },
  data() {
    return {
      activeTab: 'balance',
      tabs: [
        { value: 'balance', label: 'Loan Balance' },
        { value: 'payments', label: 'Monthly Payments' },
        { value: 'breakdown', label: 'Payment Breakdown' }
      ]
    }
  },
  computed: {
    chartData() {
      const labels = this.scheduleData.standard_schedule.map(item => `Month ${item.month}`)
      const datasets = []

      switch (this.activeTab) {
        case 'balance':
          datasets.push({
            label: 'Standard Balance',
            data: this.scheduleData.standard_schedule.map(item => item.remaining_balance),
            borderColor: '#3b82f6',
            tension: 0.1
          })
          if (this.scheduleData.extra_payment_schedule.length) {
            datasets.push({
              label: 'With Extra Payments',
              data: this.scheduleData.extra_payment_schedule.map(item => item.remaining_balance),
              borderColor: '#22c55e',
              tension: 0.1
            })
          }
          break

        case 'payments':
          datasets.push({
            label: 'Standard Payment',
            data: this.scheduleData.standard_schedule.map(item => item.payment),
            borderColor: '#3b82f6',
            tension: 0.1
          })
          if (this.scheduleData.extra_payment_schedule.length) {
            datasets.push({
              label: 'Extra Payment',
              data: this.scheduleData.extra_payment_schedule.map(item => item.payment),
              borderColor: '#22c55e',
              tension: 0.1
            })
          }
          break

        case 'breakdown':
          datasets.push({
            label: 'Standard Principal',
            data: this.scheduleData.standard_schedule.map(item => item.principal),
            borderColor: '#3b82f6',
            tension: 0.1
          })
          datasets.push({
            label: 'Standard Interest',
            data: this.scheduleData.standard_schedule.map(item => item.interest),
            borderColor: '#ef4444',
            tension: 0.1
          })
          if (this.scheduleData.extra_payment_schedule.length) {
            datasets.push({
              label: 'Extra Principal',
              data: this.scheduleData.extra_payment_schedule.map(item => item.principal),
              borderColor: '#22c55e',
              tension: 0.1
            })
            datasets.push({
              label: 'Extra Interest',
              data: this.scheduleData.extra_payment_schedule.map(item => item.interest),
              borderColor: '#f97316',
              tension: 0.1
            })
          }
          break
      }

      return {
        labels,
        datasets
      }
    },
    chartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                let label = context.dataset.label || '';
                if (label) {
                  label += ': ';
                }
                label += new Intl.NumberFormat('en-US', {
                  style: 'currency',
                  currency: 'USD'
                }).format(context.parsed.y);
                return label;
              }
            }
          }
        },
        scales: {
          y: {
            ticks: {
              callback: function(value) {
                return new Intl.NumberFormat('en-US', {
                  style: 'currency',
                  currency: 'USD',
                  maximumFractionDigits: 0
                }).format(value);
              }
            }
          }
        }
      }
    }
  }
}
</script>

<style scoped>
.amortization-chart-wrapper {
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

.chart {
  background-color: #27293d;
}
</style>
