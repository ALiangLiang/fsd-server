<template>
  <el-form :model="form">
    <el-form-item label="Taxi via">
      <el-input v-model="form.taxiTo" autocomplete="off" />
    </el-form-item>
    <el-form-item label="Parking">
      <el-select
        v-model="form.parkingId"
        filterable
        remote
        reserve-keyword
        remote-show-suffix
        style="width: 240px"
        placeholder="Leave blank for random"
      >
        <el-option-group label="General">
          <el-option
            v-for="parking in otherParkings"
            :key="parking.id"
            :label="`${parking.name} (${parking.type})`"
            :value="parking.id"
            :disabled="getIsParkingDisabled(parking)"
          />
        </el-option-group>
        <el-option-group label="Cargo">
          <el-option
            v-for="parking in cargoParkings"
            :key="parking.id"
            :label="`${parking.name} (${parking.type})`"
            :value="parking"
            :disabled="getIsParkingDisabled(parking)"
          />
        </el-option-group>
        <el-option-group label="Military">
          <el-option
            v-for="parking in militarryParkings"
            :key="parking.id"
            :label="`${parking.name} (${parking.type})`"
            :value="parking"
            :disabled="getIsParkingDisabled(parking)"
          />
        </el-option-group>
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
import { reactive, ref, computed, inject } from 'vue'
import { ElMessage } from 'element-plus'

import { serverKey, aircraftsKey, parkingsKey } from '../injection-keys'
import type { Parking } from '../types'

const props = defineProps<{
  aircraftId: string
}>()
const emit = defineEmits<{
  submit: [aircraftId: string]
}>()

const server = inject(serverKey)!
const parkings = inject(parkingsKey)!
const aircrafts = inject(aircraftsKey)!

const isLoading = ref(false)
const form = reactive({
  parkingId: null,
  taxiTo: '',
})

const cargoParkings = computed(() =>
  parkings.value.filter(parking => parking.type.includes('Cargo'))
)
const militarryParkings = computed(() =>
  parkings.value.filter(parking => parking.type.includes('Mil'))
)
const cargoAndMilitaryParkingSet = computed(() => 
  new Set(cargoParkings.value.concat(militarryParkings.value))
)
const otherParkings = computed(() =>
  parkings.value.filter(parking => !cargoAndMilitaryParkingSet.value.has(parking))
)

function getIsParkingDisabled (parking: Parking) {
  const ocupiedParkingIds = aircrafts.value.map((ac) => ac.parking?.id)
  return ocupiedParkingIds.includes(parking.id)
}

const onClickSubmit = async () => {
  isLoading.value = true
  try {
    await fetch(`${server?.value}/aircrafts/${props.aircraftId}/taxi-to-bay`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        parkingId: form.parkingId,
        taxiPath: form.taxiTo.split(' '),
      })
    })
    emit('submit', props.aircraftId)
  } catch (err) {
    console.error(err)
    ElMessage({
      message: 'Failed to taxi to parking',
      type: 'error'
    })
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
</style>
