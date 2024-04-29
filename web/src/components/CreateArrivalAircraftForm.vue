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
    <el-form-item label="Interval (seconds)">
      <el-input-number v-model="form.seconds" autocomplete="off" />
    </el-form-item>
    <el-form-item>
      <el-button 
        type="primary" 
        :loading="isLoading"
        @click="() => onClickSubmit()"
      >
        Create One
      </el-button>
      <el-button 
        v-if="createWIntervalId == -1"
        type="primary" 
        :loading="isLoading"
        @click="onClickCreateWithInterval"
      >
        Create every {{ form.seconds }} seconds
      </el-button>
      <el-button 
        v-else
        type="danger" 
        :loading="isLoading"
        @click="onClickStopCreateWithInterval"
      >
        Stop create every {{ form.seconds }} seconds
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, ref, inject } from 'vue'
import { ElMessage } from 'element-plus'

import { serverKey, airportIdentKey, approachesKey, createWIntervalIdKey } from '../injection-keys'

const emit = defineEmits<{
  submit: [aircraftId: string]
}>()

const server = inject(serverKey)!
const airportIdent = inject(airportIdentKey)!
const approaches = inject(approachesKey)!
const createWIntervalId = inject(createWIntervalIdKey)!

const isLoading = ref(false)
const form = reactive({
  callsign: '',
  approachId: null,
  seconds: 300,
})

const onClickSubmit = async (approachId?: number | null) => {
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
        approachId: approachId || form.approachId,
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
const onClickCreateWithInterval = () => {
  clearInterval(createWIntervalId.value)
  onClickSubmit(form.approachId)
  createWIntervalId.value = setInterval(() => onClickSubmit(form.approachId), form.seconds * 1000)
}
const onClickStopCreateWithInterval = () => {
  clearInterval(createWIntervalId.value)
  createWIntervalId.value = -1
}
</script>

<style scoped>
</style>
