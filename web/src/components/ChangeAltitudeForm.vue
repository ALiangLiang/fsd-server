<template>
  <el-form :model="form">
    <el-form-item label="Altitude">
      <el-input-number 
        v-model="form.altitude"
        :min="0" 
        :max="50000"
        :step="1000"
      />
    </el-form-item>
    <el-form-item>
      <el-button type="primary" :loading="isLoading" @click="onClickSubmit">Submit</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, ref, watch, inject } from 'vue'
import { ElMessage } from 'element-plus'

import { serverKey } from '../injection-keys'

const props = defineProps<{
  aircraftId: string
}>()
const emit = defineEmits<{
  submit: [aircraftId: string]
}>()

const server = inject(serverKey)

const isLoading = ref(false)
const form = reactive({
  altitude: 3000,
})

watch(() => props.aircraftId, () => {
  form.altitude = 3000
})

const onClickSubmit = async () => {
  isLoading.value = true
  try{
    await fetch(`${server?.value}/aircrafts/${props.aircraftId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        targetAltitude: form.altitude,
      })
    })
    emit('submit', props.aircraftId)
  } catch (err) {
    console.error(err)
    ElMessage({
      message: 'Failed to change altitude',
      type: 'error'
    })
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
</style>
