<template>
  <div class="amortization-chart-wrapper">
    <div v-if="!scheduleData?.standard_schedule?.length" class="text-center text-gray-400 p-8">
      No amortization data available. Please submit the form to see the schedule.
    </div>
    <div v-else>
      <div class="chart-container">
        <div class="tabs">
          <button 
            v-for="tab in ['balance', 'payments', 'breakdown']" 
            :key="tab"
            @click="activeTab = tab"
            :class="['tab', { active: activeTab === tab }]"
          >
            {{ tab.charAt(0).toUpperCase() + tab.slice(1) }}
          </button>
        </div>
        
        <div class="chart">
          <apexchart
            type="line"
            height="400"
            :options="chartOptions"
            :series="getSeriesForTab()"
          ></apexchart>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import VueApexCharts from 'vue-apexcharts'

export default {
  name: 'AmortizationChart',
  components: {
    apexchart: VueApexCharts
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
      chartOptions: {
        chart: {
          type: 'line',
          background: '#27293d',
          foreColor: '#fff'
        },
        stroke: {
          curve: 'smooth',
          width: 2
        },
        xaxis: {
          title: {
            text: 'Month'
          }
        },
        yaxis: {
          title: {
            text: 'Amount ($)'
          },
          labels: {
            formatter: (value) => {
              return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
                minimumFractionDigits: 0
              }).format(value)
            }
          }
        },
        tooltip: {
          theme: 'dark',
          y: {
            formatter: (value) => {
              return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
                minimumFractionDigits: 2
              }).format(value)
            }
          }
        },
        grid: {
          borderColor: '#444'
        },
        legend: {
          position: 'top'
        }
      }
    }
  },
  methods: {
    getSeriesForTab() {
      const series = []
      
      if (!this.scheduleData?.standard_schedule?.length) return []

      switch (this.activeTab) {
        case 'balance':
          series.push({
            name: 'Standard Balance',
            data: this.scheduleData.standard_schedule.map(item => ({
              x: item.month,
              y: item.remaining_balance
            }))
          })
          if (this.scheduleData.extra_payment_schedule.length) {
            series.push({
              name: 'With Extra Payments',
              data: this.scheduleData.extra_payment_schedule.map(item => ({
                x: item.month,
                y: item.remaining_balance
              }))
            })
          }
          break

        case 'payments':
          series.push({
            name: 'Standard Payment',
            data: this.scheduleData.standard_schedule.map(item => ({
              x: item.month,
              y: item.payment
            }))
          })
          if (this.scheduleData.extra_payment_schedule.length) {
            series.push({
              name: 'Extra Payment',
              data: this.scheduleData.extra_payment_schedule.map(item => ({
                x: item.month,
                y: item.payment
              }))
            })
          }
          break

        case 'breakdown':
          series.push({
            name: 'Standard Principal',
            data: this.scheduleData.standard_schedule.map(item => ({
              x: item.month,
              y: item.principal
            }))
          })
          series.push({
            name: 'Standard Interest',
            data: this.scheduleData.standard_schedule.map(item => ({
              x: item.month,
              y: item.interest
            }))
          })
          if (this.scheduleData.extra_payment_schedule.length) {
            series.push({
              name: 'Extra Principal',
              data: this.scheduleData.extra_payment_schedule.map(item => ({
                x: item.month,
                y: item.principal
              }))
            })
            series.push({
              name: 'Extra Interest',
              data: this.scheduleData.extra_payment_schedule.map(item => ({
                x: item.month,
                y: item.interest
              }))
            })
          }
          break
      }
      
      return series
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

.chart-container {
  margin-top: 20px;
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

.chart {
  min-height: 400px;
}
</style>
