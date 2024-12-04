<template>
  <card>
    <h5 slot="header" class="title">Mortgage Calculator</h5>
    <form @submit.prevent="updateProfile">
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


      <base-button native-type="submit" type="primary" class="btn-fill">
        Pay Ahead Estimator
      </base-button>
      <base-button native-type="submit" type="primary" class="btn-fill">
        Amortization Schedule
      </base-button>
      <base-button native-type="submit" type="primary" class="btn-fill">
        Advanced Analytics
      </base-button>
    </form>
  </card>
</template>
