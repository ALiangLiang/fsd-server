<template>
  <el-form :model="form">
    <el-form-item label="Callsign">
      <el-input v-model="form.callsign" autocomplete="off" placeholder="Leave blank for random" />
    </el-form-item>
    <el-form-item label="Runway">
      <el-select
        v-model="form.approachId"
        filterable
        remote
        reserve-keyword
        remote-show-suffix
        style="width: 240px"
        placeholder="Leave blank for random"
      >
        <el-option
          v-for="approach in approaches"
          :key="approach.id"
          :label="approach.name"
          :value="approach.id"
        />
      </el-select>
    </el-form-item>
    <el-form-item>
      <el-button 
        type="primary" 
        :loading="isLoading"
        @click="onClickSubmit"
      >
        Submit
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, ref, inject } from 'vue'
import { ElMessage } from 'element-plus'

import { serverKey, airportIdentKey, approachesKey } from '../injection-keys'

const emit = defineEmits<{
  submit: [aircraftId: string]
}>()

const server = inject(serverKey)!
const airportIdent = inject(airportIdentKey)!
const approaches = inject(approachesKey)!

const isLoading = ref(false)
const form = reactive({
  callsign: '',
  approachId: null,
})

const onClickSubmit = async () => {
  isLoading.value = true
  try {
    const resp = await fetch(`${server?.value}/aircrafts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        intention: 'arrival',
        callsign: (form.callsign) ? form.callsign.toUpperCase() : null,
        approachId: form.approachId,
        flightplan: null,
        arrival_airport: airportIdent.value,
      })
    })
    const data = await resp.json()
    ElMessage({
      message: 'Aircraft created successfully, callsign: ' + data.callsign,
      type: 'success'
    })
    emit('submit', data.id)
  } catch (err) {
    console.error(err)
    ElMessage({
      message: 'Failed to create aircraft',
      type: 'error'
    })
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
</style>
