<template>
  <el-form :model="form">
    <el-form-item label="Callsign">
      <el-input v-model="form.callsign" autocomplete="off" placeholder="Leave blank for random" />
    </el-form-item>
    <el-form-item label="Arrival" required>
      <el-input v-model="form.arrival" autocomplete="off" placeholder="Leave blank for random" />
    </el-form-item>
    <el-form-item label="Preset Flightplan" v-if="matchedPresets.length">
      <el-select
        filterable
        remote
        reserve-keyword
        remote-show-suffix
        style="width: 240px"
        @change="(e: Flightplan) => {
          form.route = e.route
          form.cruiseAltitude = e.cruiseAltitude
        }"
        placeholder="You can select a preset flightplan"
      >
        <el-option
          v-for="flightplan in matchedPresets"
          :key="flightplan.route"
          :label="flightplan.route"
          :value="flightplan"
        />
      </el-select>
    </el-form-item>
    <el-form-item label="Route" required>
      <el-input v-model="form.route" autocomplete="off" />
    </el-form-item>
    <el-form-item label="Cruise Altitude" required>
      <el-input-number 
        v-model="form.cruiseAltitude"
        :min="0" 
        :max="50000"
        :step="1000"
      />
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

import { serverKey, airportIdentKey, aircraftsKey, parkingsKey, presetFlightplansKey } from '../injection-keys'
import type { Parking, Flightplan } from '../types'

const emit = defineEmits<{
  submit: [aircraftId: string]
}>()

const server = inject(serverKey)!
const airportIdent = inject(airportIdentKey)!
const parkings = inject(parkingsKey)!
const presetFlightplans = inject(presetFlightplansKey)!
const aircrafts = inject(aircraftsKey)!

const isLoading = ref(false)
const form = reactive({
  parkingId: null,
  route: '',
  arrival: '',
  callsign: '',
  cruiseAltitude: null as number | null,
})

const matchedPresets = computed(() =>
  presetFlightplans.value.filter((fp) => fp.departureAirport === airportIdent.value && fp.arrivalAirport === form.arrival)
)
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
    const resp = await fetch(`${server?.value}/aircrafts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        intention: 'departure',
        callsign: (form.callsign) ? form.callsign.toUpperCase() : null,
        parkingId: form.parkingId,
        flightplan: (form.arrival) ? {
          departure: airportIdent.value,
          route: form.route,
          arrival: form.arrival,
          cruiseAltitude: form.cruiseAltitude || null
        } : null
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
