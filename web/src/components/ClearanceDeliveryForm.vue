<template>
  <el-form :model="form">
    <el-form-item label="Sid Name" required>
      <el-select
        v-model="form.sidName"
        filterable
        remote
        reserve-keyword
        placeholder="Please enter a keyword"
        remote-show-suffix
        style="width: 240px"
      >
        <el-option
          v-for="sidName in sidNames"
          :key="sidName"
          :label="sidName"
          :value="sidName"
        />
      </el-select>
    </el-form-item>
    <el-form-item label="Squawk" required>
      <el-input v-model="form.squawkCode" autocomplete="off" />
    </el-form-item>
    <el-form-item label="Initial Altitude" required>
      <el-input-number 
        v-model="form.initialAltitude"
        :min="0" 
        :max="50000"
        :step="1000"
      />
    </el-form-item>
    <!-- {{ 'RCTP' }} tower, {{ 'TTW948' }}, good evening, request clearance to {{ 'RJTT' }}. FL{{ '350' }}, information {{ 'A' }} -->
    <el-form-item>
      <el-button type="primary" :loading="isLoading" @click="onClickSubmit">Submit</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, ref, watch, inject } from 'vue'
import { ElMessage } from 'element-plus'

import { serverKey, sidNamesKey } from '../injection-keys'

const props = defineProps<{
  aircraftId: string
}>()
const emit = defineEmits<{
  submit: [aircraftId: string]
}>()

const server = inject(serverKey)
const sidNames = inject(sidNamesKey)

const isLoading = ref(false)
const form = reactive({
  sidName: '',
  squawkCode: '',
  initialAltitude: 3000,
})

watch(() => props.aircraftId, () => {
  form.sidName = ''
  form.squawkCode = ''
})

const onClickSubmit = async () => {
  isLoading.value = true
  try{
    await fetch(`${server?.value}/aircrafts/${props.aircraftId}/clearance-delivery`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(form)
    })
    emit('submit', props.aircraftId)
  } catch (err) {
    console.error(err)
    ElMessage({
      message: 'Failed to clearnace delivery',
      type: 'error'
    })
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
</style>
