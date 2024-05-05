<template>
  <el-button
    :type="(aircraft.status === AircraftStatus.NOT_DELIVERED) ? 'primary' : 'default'"
    :loading="areLoading[0]"
    :disabled="aircraft.status !== AircraftStatus.NOT_DELIVERED"
    @click="onClickClearanceDelivery"
  >
    Clearance Delivery
  </el-button>
  <el-button
    :type="(aircraft.status === AircraftStatus.DELIVERED) ? 'primary' : 'default'"
    :loading="areLoading[1]"
    :disabled="aircraft.status !== AircraftStatus.DELIVERED"
    @click="() => onClickPushbackApproved(aircraft)"
  >
    S/U & Pushback approved
  </el-button>
  <el-button
    :type="(aircraft.status === AircraftStatus.APPROVED_PUSHBACK_STARTUP) ? 'primary' : 'default'"
    :loading="areLoading[2]"
    :disabled="aircraft.status !== AircraftStatus.APPROVED_PUSHBACK_STARTUP"
    @click="onClickTaxiTo"
  >
    Taxi via...
  </el-button>
  <el-button
    :type="(aircraft.status === AircraftStatus.APPROVED_TAXI_TO_RWY) ? 'primary' : 'default'"
    :loading="areLoading[3]"
    :disabled="aircraft.status !== AircraftStatus.APPROVED_TAXI_TO_RWY"
    @click="() => onClickLineupAndWait(aircraft)"
  >
    Line-up and Wait
  </el-button>
  <el-button
    :type="([AircraftStatus.APPROVED_TAXI_TO_RWY, AircraftStatus.LINEUP_WAIT].includes(aircraft.status)) ? 'primary' : 'default'"
    :loading="areLoading[4]"
    :disabled="![AircraftStatus.APPROVED_TAXI_TO_RWY, AircraftStatus.LINEUP_WAIT].includes(aircraft.status)"
    @click="() => onClickClearedForTakeoff(aircraft)"
  >
    Cleared for Takeoff
  </el-button>
  <el-button
    :type="(aircraft.status === AircraftStatus.CLEARED_TAKEOFF) ? 'primary' : 'default'"
    :loading="areLoading[5]"
    :disabled="aircraft.status !== AircraftStatus.CLEARED_TAKEOFF"
    @click="onClickClimbDecendMaintain"
  >
    Climb/Decend and Maintain
  </el-button>
  <el-button
    :type="(aircraft.status === AircraftStatus.CLEARED_TAKEOFF) ? 'primary' : 'default'"
    :loading="areLoading[6]"
    :disabled="aircraft.status !== AircraftStatus.CLEARED_TAKEOFF"
    @click="() => onClickClearedToLand(aircraft)"
  >
    Cleared to Land
  </el-button>
  <el-button
    :type="(aircraft.status === AircraftStatus.CLEARED_TAKEOFF && aircraft.isInterceptIls) ? 'danger' : 'default'"
    :loading="areLoading[7]"
    :disabled="aircraft.status !== AircraftStatus.CLEARED_TAKEOFF || !aircraft.isInterceptIls"
    @click="() => onClickGoAround(aircraft)"
  >
    Go Around
  </el-button>
  <el-button
    :type="(aircraft.status === AircraftStatus.VACATE_RUNWAY) ? 'primary' : 'default'"
    :loading="areLoading[8]"
    :disabled="aircraft.status !== AircraftStatus.VACATE_RUNWAY"
    @click="onClickTaxi2Bay"
  >
    Taxi to Bay
  </el-button>
  <el-button
    :type="(aircraft.status === AircraftStatus.APPROVED_TAXI_TO_BAY) ? 'primary' : 'default'"
    :loading="areLoading[9]"
    @click="() => onClickShutdown(aircraft)"
  >
    Shutdown
  </el-button>
  
  <Teleport to="body">
    <el-dialog v-model="isShowDialog" title="Form" width="400">
      <component 
        :is="Form"
        :aircraft-id="aircraft.id"
        @submit="onSubmit" 
      />
    </el-dialog>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, inject } from 'vue'

import { serverKey } from '../injection-keys'
import { AircraftStatus, type Aircraft } from '../types'
import ClearanceDeliveryForm from './ClearanceDeliveryForm.vue'
import ChangeAltitudeForm from './ChangeAltitudeForm.vue'
import TaxiToForm from './TaxiToForm.vue'
import Taxi2BayForm from './Taxi2BayForm.vue'

const props = defineProps<{
  aircraft: Aircraft
}>()
const emit = defineEmits<{
  clickUpdate: [aircraft: Aircraft]
}>()

const isShowDialog = ref(false)
const areLoading = ref(Array(8).fill(false))
const Form = ref(ClearanceDeliveryForm)
const server = inject(serverKey)!

const onClickClearanceDelivery = async () => {
  Form.value = ClearanceDeliveryForm
  isShowDialog.value = true
}
const onClickPushbackApproved = async (aircraft: Aircraft) => {
  areLoading.value[1] = true
  await fetch(`${server.value}/aircrafts/${aircraft.id}/startup-pushback-approved`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  })
  areLoading.value[1] = false
  emit('clickUpdate', props.aircraft)
}
const onClickTaxiTo = async () => {
  Form.value = TaxiToForm
  isShowDialog.value = true
}
const onClickLineupAndWait = async (aircraft: Aircraft) => {
  areLoading.value[3] = true
  await fetch(`${server.value}/aircrafts/${aircraft.id}/lineup-and-wait`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({})
  })
  areLoading.value[3] = false
}
const onClickClearedForTakeoff = async (aircraft: Aircraft) => {
  areLoading.value[4] = true
  await fetch(`${server.value}/aircrafts/${aircraft.id}/cleared-takeoff`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({})
  })
  areLoading.value[4] = false
}
const onClickClimbDecendMaintain = async () => {
  Form.value = ChangeAltitudeForm
  isShowDialog.value = true
}
const onClickClearedToLand = async (aircraft: Aircraft) => {
  areLoading.value[6] = true
  await fetch(`${server.value}/aircrafts/${aircraft.id}/cleared-land`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      vacatedTaxiway: null,
    })
  })
  areLoading.value[6] = false
  emit('clickUpdate', props.aircraft)
}
const onClickGoAround = async (aircraft: Aircraft) => {
  areLoading.value[7] = true
  await fetch(`${server.value}/aircrafts/${aircraft.id}/go-around`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({})
  })
  areLoading.value[7] = false
  emit('clickUpdate', props.aircraft)
}
const onClickTaxi2Bay = async () => {
  Form.value = Taxi2BayForm
  isShowDialog.value = true
}
const onClickShutdown = async (aircraft: Aircraft) => {
  areLoading.value[9] = true
  await fetch(`${server.value}/aircrafts/${aircraft.id}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json'
    }
  })
  areLoading.value[9] = false
  emit('clickUpdate', props.aircraft)
}

const onSubmit = async () => {
  isShowDialog.value = false
  emit('clickUpdate', props.aircraft)
}
</script>