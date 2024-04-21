<template>
  <el-form :model="form">
    <el-form-item label="Runway">
      <el-input v-model="form.runway" autocomplete="off" />
    </el-form-item>
    <el-form-item>
      <el-button type="primary" :loading="isLoading" @click="onClickSubmit">Submit</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, ref, watch, inject } from 'vue'

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
  runway: '',
})

watch(() => props.aircraftId, () => {
  form.runway = ''
})

const onClickSubmit = async () => {
  isLoading.value = true
  await fetch(`${server?.value}/aircrafts/${props.aircraftId}/lineup-and-wait`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      runwayName: form.runway,
    })
  })
  isLoading.value = false
  emit('submit', props.aircraftId)
}
</script>

<style scoped>
</style>
