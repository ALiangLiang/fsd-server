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
        <el-button @click="onClickCreate">Create Aircraft</el-button>
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
    <el-table-column label="Arrival" prop="flightplan.arrivalAirport" />
    <el-table-column label="Cruise Altitude" prop="flightplan.cruiseAltitude" />
    <el-table-column label="Target Altutude" prop="targetAltitude" :width="100" />
    <el-table-column label="Status" prop="status" :formatter="getAirCraftStatus" />
    <el-table-column align="right">
      <template #default="{ row: aircraft }">
        <el-button
          :type="(aircraft.status === AircraftStatus.NOT_DELIVERED) ? 'primary' : 'default'"
          @click="() => onClickClearanceDelivery(aircraft)"
        >
          Clearance Delivery
        </el-button>
        <el-button
          :type="(aircraft.status === AircraftStatus.DELIVERED) ? 'primary' : 'default'"
          :loading="isLoadingPushbackApproved"
          @click="() => onClickPushbackApproved(aircraft)"
        >
          S/U & Pushback approved
        </el-button>
        <el-button
          :type="(aircraft.status === AircraftStatus.APPROVED_PUSHBACK_STARTUP) ? 'primary' : 'default'"
          @click="() => onClickTaxiTo(aircraft)"
        >
          Taxi via...
        </el-button>
        <el-button
          :type="(aircraft.status === AircraftStatus.APPROVED_TAXI) ? 'primary' : 'default'"
          @click="() => onClickLineupAndWait(aircraft)"
        >
          Line-up and Wait
        </el-button>
        <el-button
          :type="(aircraft.status === AircraftStatus.APPROVED_TAXI) ? 'primary' : 'default'"
          @click="() => onClickClearedForTakeoff(aircraft)"
        >
          Cleared for Takeoff
        </el-button>
        <el-button
          :type="(aircraft.status === AircraftStatus.CLEARED_TAKEOFF) ? 'primary' : 'default'"
          @click="() => onClickClimbDecendMaintain(aircraft)"
        >
          Climb/Decend and Maintain
        </el-button>
      </template>
    </el-table-column>
  </el-table>
  
  <el-dialog v-model="isShowDialog" title="Form" width="400">
    <CreateAircraftForm 
      v-if="Form.__name === CreateAircraftForm.__name"
      @submit="onSubmit" 
    />
    <component 
      :is="Form"
      v-else-if="selectedAircraft !== null"
      :aircraft-id="selectedAircraft.id"
      @submit="onSubmit" 
    />
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, provide, computed, watch, onMounted } from 'vue'

import {
  serverKey,
  airportIdentKey,
  aircraftsKey,
  sidNamesKey,
  parkingsKey,
  presetFlightplansKey ,
  type extractInjectionKey,
} from './injection-keys'
import CreateAircraftForm from './components/CreateAircraftForm.vue'
import ClearanceDeliveryForm from './components/ClearanceDeliveryForm.vue'
import TaxiToForm from './components/TaxiToForm.vue'
import LineupAndWaitForm from './components/LineupAndWaitForm.vue'
import ClearedTakeoffForm from './components/ClearedTakeoffForm.vue'
import ChangeAltitudeForm from './components/ChangeAltitudeForm.vue'
import { AircraftStatus, type Aircraft } from './types'

const AircraftStatusMap = {
  [AircraftStatus.NOT_DELIVERED]: 'Not Delivered',
  [AircraftStatus.DELIVERED]: 'Clearance Delivery',
  [AircraftStatus.APPROVED_PUSHBACK_STARTUP]: 'Startup and Pushback Approved',
  [AircraftStatus.APPROVED_TAXI]: 'Approved Taxi',
  [AircraftStatus.LINEUP_WAIT]: 'Line-up and Wait',
  [AircraftStatus.CLEARED_TAKEOFF]: 'Cleared for Takeoff',
}
const getAirCraftStatus = (row: Aircraft) => AircraftStatusMap[row.status]

const isShowDialog = ref(false)
const isLoadingPushbackApproved = ref(false)
const callsignFilter = ref('')
const server = ref('http://localhost:8000')
const airportIdent = ref('')
const sidNames = ref<string[]>([])
const parkings = ref([]) as extractInjectionKey<typeof parkingsKey>
const aircrafts = ref<Aircraft[]>([])
const presetFlightplans = ref([]) as extractInjectionKey<typeof presetFlightplansKey>
const selectedAircraft = ref<Aircraft | null>(null)
const activeStatus = ref(-1)
const Form = ref(ClearanceDeliveryForm)

const filteredAircrafts = computed(() =>
  aircrafts.value.filter((aircraft) => {
    return aircraft.callsign.includes(callsignFilter.value.toUpperCase()) && 
    (activeStatus.value === -1 || aircraft.status === activeStatus.value)
  })
)

provide(serverKey, server)
provide(airportIdentKey, airportIdent)
provide(aircraftsKey, aircrafts)
provide(sidNamesKey, sidNames)
provide(parkingsKey, parkings)
provide(presetFlightplansKey, presetFlightplans)

watch([server, airportIdent], () => {
  localStorage.setItem('server', server.value)
  localStorage.setItem('airportIdent', airportIdent.value)
})

async function updateAircraft () {
  return fetch(`${server.value}/aircrafts`)
    .then((response) => response.json())
    .then((json: Aircraft[]) => (aircrafts.value = json))
}

const onClickCreate = () => {
  Form.value = CreateAircraftForm
  selectedAircraft.value = null
  isShowDialog.value = true
}

const onSubmit = async (aircraftId: string) => {
  isShowDialog.value = false
  const aircrafts = await updateAircraft()
  if (activeStatus.value === -1) return

  const aircraft = aircrafts.find((aircraft) => aircraft.id === aircraftId)
  if (aircraft === undefined) return
  activeStatus.value = aircraft.status
}

const onClickClearanceDelivery = async (aircraft: Aircraft) => {
  Form.value = ClearanceDeliveryForm
  selectedAircraft.value = aircraft
  isShowDialog.value = true
}
const onClickPushbackApproved = async (aircraft: Aircraft) => {
  isLoadingPushbackApproved.value = true
  await fetch(`${server.value}/aircrafts/${aircraft.id}/startup-pushback-approved`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  })
  isLoadingPushbackApproved.value = false
  await updateAircraft()
}
const onClickTaxiTo = async (aircraft: Aircraft) => {
  Form.value = TaxiToForm
  selectedAircraft.value = aircraft
  isShowDialog.value = true
}
const onClickLineupAndWait = async (aircraft: Aircraft) => {
  Form.value = LineupAndWaitForm
  selectedAircraft.value = aircraft
  isShowDialog.value = true
}
const onClickClearedForTakeoff = async (aircraft: Aircraft) => {
  Form.value = ClearedTakeoffForm
  selectedAircraft.value = aircraft
  isShowDialog.value = true
}
const onClickClimbDecendMaintain = async (aircraft: Aircraft) => {
  Form.value = ChangeAltitudeForm
  selectedAircraft.value = aircraft
  isShowDialog.value = true
}

onMounted(() => {
  server.value = localStorage.getItem('server') ?? 'localhost:8000'
  airportIdent.value = localStorage.getItem('airportIdent') ?? ''

  return updateAircraft()
})

onMounted(() => {
  fetch(`${server.value}/airports/${airportIdent.value}/sids`)
    .then((response) => response.json())
    .then((json) => (sidNames.value = json))
  fetch(`${server.value}/airports/${airportIdent.value}/parkings`)
    .then((response) => response.json())
    .then((json) => (parkings.value = json))
  fetch(`${server.value}/preset-flightplans`)
    .then((response) => response.json())
    .then((json) => (presetFlightplans.value = json))
})
</script>

<style scoped>

</style>
