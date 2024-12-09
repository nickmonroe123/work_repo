<template>
  <div class="amortization-chart-wrapper">
    <div v-if="!hasData" class="text-center text-gray-400 p-8">
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
        <LineChart
          :chartdata="chartData"
          :options="chartOptions"
          :styles="{ height: '400px' }"
        />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AmortizationChart',
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
    hasData() {
      return this.scheduleData?.standard_schedule?.length > 0
    },
    chartData() {
      const labels = this.scheduleData.standard_schedule.map(item => `Month ${item.month}`)
      const datasets = []

      switch (this.activeTab) {
        case 'balance':
          datasets.push({
            label: 'Standard Balance',
            data: this.scheduleData.standard_schedule.map(item => item.remaining_balance),
            borderColor: '#3b82f6',
            fill: false,
            tension: 0.1
          })
          if (this.scheduleData.extra_payment_schedule.length) {
            datasets.push({
              label: 'With Extra Payments',
              data: this.scheduleData.extra_payment_schedule.map(item => item.remaining_balance),
              borderColor: '#22c55e',
              fill: false,
              tension: 0.1
            })
          }
          break

        case 'payments':
          datasets.push({
            label: 'Standard Payment',
            data: this.scheduleData.standard_schedule.map(item => item.payment),
            borderColor: '#3b82f6',
            fill: false,
            tension: 0.1
          })
          if (this.scheduleData.extra_payment_schedule.length) {
            datasets.push({
              label: 'Extra Payment',
              data: this.scheduleData.extra_payment_schedule.map(item => item.payment),
              borderColor: '#22c55e',
              fill: false,
              tension: 0.1
            })
          }
          break

        case 'breakdown':
          datasets.push({
            label: 'Standard Principal',
            data: this.scheduleData.standard_schedule.map(item => item.principal),
            borderColor: '#3b82f6',
            fill: false,
            tension: 0.1
          })
          datasets.push({
            label: 'Standard Interest',
            data: this.scheduleData.standard_schedule.map(item => item.interest),
            borderColor: '#ef4444',
            fill: false,
            tension: 0.1
          })
          if (this.scheduleData.extra_payment_schedule.length) {
            datasets.push({
              label: 'Extra Principal',
              data: this.scheduleData.extra_payment_schedule.map(item => item.principal),
              borderColor: '#22c55e',
              fill: false,
              tension: 0.1
            })
            datasets.push({
              label: 'Extra Interest',
              data: this.scheduleData.extra_payment_schedule.map(item => item.interest),
              borderColor: '#f97316',
              fill: false,
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
              callback: function(value) {
                return new Intl.NumberFormat('en-US', {
                  style: 'currency',
                  currency: 'USD',
                  maximumFractionDigits: 0
                }).format(value);
              }
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
            label: function(tooltipItem, data) {
              let label = data.datasets[tooltipItem.datasetIndex].label || '';
              if (label) {
                label += ': ';
              }
              label += new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD'
              }).format(tooltipItem.yLabel);
              return label;
            }
          }
        }
      }
    }
  }
}
</script>
