import Vue from 'vue'
import { Line } from 'vue-chartjs'

// Create a reusable line chart component
Vue.component('LineChart', {
  extends: Line,
  props: {
    chartdata: {
      type: Object,
      default: null
    },
    options: {
      type: Object,
      default: null
    }
  },
  mounted() {
    this.renderChart(this.chartdata, this.options)
  },
  watch: {
    chartdata: {
      handler(newData) {
        this.$data._chart.destroy()
        this.renderChart(newData, this.options)
      },
      deep: true
    }
  }
})
