<template>
  <div class="mortgage-calculator">
    <div class="input-section">
      <!-- Mortgage Input Fields -->
      <input v-model.number="loanAmount" type="number" placeholder="Loan Amount" />
      <input v-model.number="interestRate" type="number" placeholder="Interest Rate (%)" step="0.01" />
      <input v-model.number="loanTermYears" type="number" placeholder="Loan Term (Years)" />
      <input v-model.number="extraPayment" type="number" placeholder="Extra Monthly Payment" />
      
      <button @click="calculateAmortization">Calculate Amortization</button>
    </div>

    <div class="display-options">
      <button @click="displayMode = 'graph'">Graph View</button>
      <button @click="displayMode = 'table'">Table View</button>
    </div>

    <!-- Graph View -->
    <div v-if="displayMode === 'graph' && regularSchedule.length" class="graph-container">
      <Line 
        :data="chartData" 
        :options="chartOptions"
      />
    </div>

    <!-- Table View -->
    <div v-if="displayMode === 'table' && regularSchedule.length" class="table-container">
      <h3>Regular Payment Schedule</h3>
      <table>
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
          <tr v-for="(payment, index) in regularSchedule" :key="`regular-${index}`">
            <td>{{ payment.month }}</td>
            <td>{{ payment.payment.toFixed(2) }}</td>
            <td>{{ payment.principal.toFixed(2) }}</td>
            <td>{{ payment.interest.toFixed(2) }}</td>
            <td>{{ payment.remainingBalance.toFixed(2) }}</td>
          </tr>
        </tbody>
      </table>

      <div v-if="extraSchedule.length">
        <h3>Extra Payment Schedule</h3>
        <table>
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
            <tr v-for="(payment, index) in extraSchedule" :key="`extra-${index}`">
              <td>{{ payment.month }}</td>
              <td>{{ payment.payment.toFixed(2) }}</td>
              <td>{{ payment.principal.toFixed(2) }}</td>
              <td>{{ payment.interest.toFixed(2) }}</td>
              <td>{{ payment.remainingBalance.toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { Line } from 'vue-chartjs'
import { 
  Chart as ChartJS, 
  Title, 
  Tooltip, 
  Legend, 
  LineElement, 
  LinearScale, 
  PointElement, 
  CategoryScale 
} from 'chart.js'

ChartJS.register(
  Title, 
  Tooltip, 
  Legend, 
  LineElement, 
  LinearScale, 
  PointElement, 
  CategoryScale
)

export default {
  components: { Line },
  data() {
    return {
      loanAmount: 300000,
      interestRate: 4.5,
      loanTermYears: 30,
      extraPayment: 0,
      displayMode: 'graph',
      regularSchedule: [],
      extraSchedule: []
    }
  },
  computed: {
    chartData() {
      return {
        labels: this.regularSchedule.map(payment => `Month ${payment.month}`),
        datasets: [
          {
            label: 'Remaining Balance (Regular)',
            data: this.regularSchedule.map(payment => payment.remainingBalance),
            borderColor: 'blue',
            tension: 0.1
          },
          ...(this.extraSchedule.length ? [{
            label: 'Remaining Balance (Extra Payments)',
            data: this.extraSchedule.map(payment => payment.remainingBalance),
            borderColor: 'green',
            tension: 0.1
          }] : [])
        ]
      }
    },
    chartOptions() {
      return {
        responsive: true,
        scales: {
          y: {
            beginAtZero: false,
            title: {
              display: true,
              text: 'Remaining Balance ($)'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Months'
            }
          }
        }
      }
    }
  },
  methods: {
    calculateAmortization() {
      // Regular Payment Schedule Calculation
      this.regularSchedule = this.calculateSchedule(this.loanAmount, this.interestRate, this.loanTermYears, 0)
      
      // Extra Payment Schedule Calculation (if extra payment > 0)
      this.extraSchedule = this.extraPayment > 0 
        ? this.calculateSchedule(this.loanAmount, this.interestRate, this.loanTermYears, this.extraPayment)
        : []
    },
    calculateSchedule(principal, annualRate, termYears, extraPayment) {
      const monthlyRate = annualRate / 100 / 12
      const totalMonths = termYears * 12
      const regularPayment = principal * 
        (monthlyRate * Math.pow(1 + monthlyRate, totalMonths)) / 
        (Math.pow(1 + monthlyRate, totalMonths) - 1)

      let schedule = []
      let currentBalance = principal
      let month = 1

      while (currentBalance > 0 && month <= totalMonths) {
        // Calculate interest and principal for this month
        const monthlyInterest = currentBalance * monthlyRate
        const monthlyPrincipal = regularPayment - monthlyInterest + extraPayment

        // Adjust final payment if needed
        const payment = Math.min(currentBalance + monthlyInterest, regularPayment + extraPayment)
        
        // Update balance
        currentBalance = Math.max(0, currentBalance - (payment - monthlyInterest))

        // Add to schedule
        schedule.push({
          month,
          payment,
          principal: monthlyPrincipal,
          interest: monthlyInterest,
          remainingBalance: currentBalance
        })

        month++
      }

      return schedule
    }
  }
}
</script>

<style scoped>
.mortgage-calculator {
  max-width: 800px;
  margin: 0 auto;
}

.input-section {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.input-section input {
  flex: 1;
  padding: 8px;
}

.display-options {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.table-container table {
  width: 100%;
  border-collapse: collapse;
}

.table-container th, 
.table-container td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: right;
}

.graph-container {
  height: 400px;
}
</style>
