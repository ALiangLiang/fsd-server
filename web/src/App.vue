<template>
  <el-space direction="vertical" style="width: 100%">
    <el-row :gutter="4">
      <el-col :span="12">Server Link:<el-input v-model="server" autocomplete="off" /></el-col>
      <el-col :span="6">Airport ICAO:<el-input v-model="airportIdent" autocomplete="off" /></el-col>
    </el-row>
    <el-row :gutter="4">
      <el-col :span="12">
        <span>Filter:</span>
        <el-input v-model="callsignFilter" autocomplete="off" />
      </el-col>
      <el-col :span="12">
        <el-button @click="onClickCreateOnbound">Create Departure Aircraft</el-button>
        <el-button @click="onClickCreateInbound">Create Arrival Aircraft</el-button>
      </el-col>
    </el-row>
  </el-space>

  <el-tabs
    v-model="activeStatus"
    type="card"
  >
    <el-tab-pane label="All" :name="-1" />
    <el-tab-pane
      v-for="val, key in AircraftStatusMap" 
      :key="key"
      :label="`${val}(${aircrafts.reduce((sum, prev) => sum + Number(prev.status === Number(key)), 0)})`" 
      :name="Number(key)" 
    />
  </el-tabs>

  <el-table :data="filteredAircrafts" style="width: 100%">
    <el-table-column label="Callsign" prop="callsign" :width="80" />
    <el-table-column label="Parking" prop="parking.name" :width="80" />
    <el-table-column label="Squawk" prop="squawkCode" :width="80" />
    <el-table-column label="Route" prop="flightplan.route" />
    <el-table-column label="Arrival" prop="flightplan.arrivalAirport" :width="80" />
    <el-table-column label="Cruise Altitude" prop="flightplan.cruiseAltitude" :width="80" />
    <el-table-column label="Target Altutude" prop="targetAltitude" :width="100" />
    <el-table-column label="Expect Runway" prop="expectRunway" :width="100" />
    <el-table-column label="Status" prop="status" :formatter="getAirCraftStatus" :width="120" />
    <el-table-column align="right" :min-width="160">
      <template #default="{ row: aircraft }">
        <aircraft-actions :aircraft="aircraft" @update-aircraft="onUpdateAircraft" />
      </template>
    </el-table-column>
  </el-table>
  
  <el-dialog v-model="isShowDialog" title="Form" width="400">
    <CreateAircraftForm 
      v-if="Form.__name === CreateAircraftForm.__name"
      @submit="onUpdateAircraft" 
    />
    <CreateArrivalAircraftForm 
      v-else-if="Form.__name === CreateArrivalAircraftForm.__name"
      @submit="onUpdateAircraft" 
    />
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, provide, computed, watch, onMounted, onUnmounted } from 'vue'

import {
  serverKey,
  airportIdentKey,
  aircraftsKey,
  sidNamesKey,
  approachesKey,
  parkingsKey,
  presetFlightplansKey,
  createWIntervalIdKey,
  type extractInjectionKey,
} from './injection-keys'
import CreateAircraftForm from './components/CreateAircraftForm.vue'
import CreateArrivalAircraftForm from './components/CreateArrivalAircraftForm.vue'
import { AircraftStatus, type Aircraft, type Approach } from './types'

const AircraftStatusMap = {
  [AircraftStatus.NOT_DELIVERED]: 'Not Delivered',
  [AircraftStatus.DELIVERED]: 'Clearance Delivery',
  [AircraftStatus.APPROVED_PUSHBACK_STARTUP]: 'Startup and Pushback Approved',
  [AircraftStatus.APPROVED_TAXI_TO_RWY]: 'Approved Taxi',
  [AircraftStatus.LINEUP_WAIT]: 'Line-up and Wait',
  [AircraftStatus.CLEARED_TAKEOFF]: 'Cleared for Takeoff',
  [AircraftStatus.CLEARED_LAND]: 'Cleared to Land',
  [AircraftStatus.MISSED_APPROACH]: 'Missed Approach',
  [AircraftStatus.VACATE_RUNWAY]: 'Vacate Runway',
  [AircraftStatus.APPROVED_TAXI_TO_BAY]: 'Approved Taxi to Bay',
}
const getAirCraftStatus = (row: Aircraft) => AircraftStatusMap[row.status]

const intervalId = ref(-1)
const isShowDialog = ref(false)
const createWIntervalId = ref(-1)
const callsignFilter = ref('')
const server = ref(document.location.origin)
const airportIdent = ref('')
const sidNames = ref<string[]>([])
const approaches = ref<Approach[]>([])
const parkings = ref([]) as extractInjectionKey<typeof parkingsKey>
const aircrafts = ref<Aircraft[]>([])
const presetFlightplans = ref([]) as extractInjectionKey<typeof presetFlightplansKey>
const selectedAircraft = ref<Aircraft | null>(null)
const activeStatus = ref(-1)
const Form = ref(CreateAircraftForm)

const filteredAircrafts = computed(() =>
  aircrafts.value.filter((aircraft) => {
    return aircraft.callsign.includes(callsignFilter.value.toUpperCase()) && 
    (activeStatus.value === -1 || aircraft.status === activeStatus.value)
  }).filter((aircraft) => [
    aircraft.flightplan?.departureAirport,
    aircraft.flightplan?.arrivalAirport
  ].includes(airportIdent.value))
)

provide(serverKey, server)
provide(airportIdentKey, airportIdent)
provide(aircraftsKey, aircrafts)
provide(sidNamesKey, sidNames)
provide(approachesKey, approaches)
provide(parkingsKey, parkings)
provide(presetFlightplansKey, presetFlightplans)
provide(createWIntervalIdKey, createWIntervalId)

watch([server, airportIdent], () => {
  localStorage.setItem('server', server.value)
  localStorage.setItem('airportIdent', airportIdent.value)
})

async function updateAircraft () {
  return fetch(`${server.value}/aircrafts`)
    .then((response) => response.json())
    .then((json: Aircraft[]) => (aircrafts.value = json))
}

const onClickCreateOnbound = () => {
  Form.value = CreateAircraftForm
  selectedAircraft.value = null
  isShowDialog.value = true
}

const onClickCreateInbound = () => {
  Form.value = CreateArrivalAircraftForm
  selectedAircraft.value = null
  isShowDialog.value = true
}

const onUpdateAircraft = async (aircraftId: string) => {
  const aircrafts = await updateAircraft()
  if (activeStatus.value === -1) return

  const aircraft = aircrafts.find((aircraft) => aircraft.id === aircraftId)
  if (aircraft === undefined) return
  activeStatus.value = aircraft.status
}

onMounted(() => {
  server.value = localStorage.getItem('server') ?? document.location.origin
  airportIdent.value = localStorage.getItem('airportIdent') ?? ''

  return updateAircraft()
})

onMounted(() => {
  fetch(`${server.value}/airports/${airportIdent.value}/sids`)
    .then((response) => response.json())
    .then((json) => (sidNames.value = json))
  fetch(`${server.value}/airports/${airportIdent.value}/approaches`)
    .then((response) => response.json())
    .then((json) => (approaches.value = json))
  fetch(`${server.value}/airports/${airportIdent.value}/parkings`)
    .then((response) => response.json())
    .then((json) => (parkings.value = json))
  fetch(`${server.value}/preset-flightplans`)
    .then((response) => response.json())
    .then((json) => (presetFlightplans.value = json))

  intervalId.value = setInterval(updateAircraft, 2000)
})
onUnmounted(() => {
  clearInterval(intervalId.value)
})
</script>

<style scoped>

</style>
