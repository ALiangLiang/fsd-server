<template>
  <el-space direction="vertical" style="width: 100%">
    <el-row :gutter="4">
      <el-col :span="12">Server Link:<el-input v-model="server" autocomplete="off" /></el-col>
      <el-col :span="6">Airport ICAO:<el-input v-model="airportIdent" autocomplete="off" /></el-col>
      <el-col :span="6">
        <el-button @click="onClickOpenVhrBox">Open VHR Box</el-button>
      </el-col>
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
    {{ (isStarted) ? 'connected to tower' : 'not connect' }}
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
    <el-table-column :width="40">
      <template #default="{ row: aircraft }: { row: Aircraft }">
        <el-button
          :icon="Close"
          text
          circle
          @click="() => onClickShutdown(aircraft)"
        />
      </template>
    </el-table-column>
    <el-table-column label="Callsign" prop="callsign" :width="80" />
    <el-table-column label="Parking" prop="parking.name" :width="80" />
    <el-table-column label="Squawk" prop="squawkCode" :width="80" />
    <el-table-column label="Route" prop="flightplan.route" />
    <el-table-column label="Arrival" prop="flightplan.arrivalAirport" :width="80" />
    <el-table-column label="Cruise Altitude" prop="flightplan.cruiseAltitude" :width="80" />
    <el-table-column label="Target Altutude" prop="targetAltitude" :width="100" />
    <el-table-column label="Expect Runway" prop="expectRunway" :width="100" />
    <el-table-column label="Status" :width="120">
      <template #default="{ row: aircraft }: { row: Aircraft }">
        {{ AircraftStatusMap[aircraft.status] }}
        <span :style="(aircraft.status !== AircraftStatus.CLEARED_LAND) ? 'color: red' : ''">
          {{ aircraft.isInterceptIls ? '(ILS intercepted)' : '' }}
        </span>
        <span style="color: red">
          {{ aircraft.isGoAround ? '(Go around)' : '' }}
        </span>
      </template>
    </el-table-column>
    <el-table-column align="right" :min-width="160">
      <template #default="{ row: aircraft }: { row: Aircraft }">
        <el-button
          type="warning"
          plain
          :disabled="!isStarted"
          @mousedown="() => onMousedownAircraft(aircraft)"
          @mouseup="() => onMouseupAircraft(aircraft)"
        >
          Tx
        </el-button>
        <aircraft-actions :aircraft="aircraft" @click-update="onUpdateAircraft" />
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
import { ElNotification } from 'element-plus'
import { Close } from '@element-plus/icons-vue'
import { Peer, type MediaConnection, type DataConnection } from 'peerjs'

import noiseSound from './assets/noise.mp3'
import { getMicStream, playTxSound, playRxSound } from './utils'

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
import type { Message, TxMessage, TxEndMessage } from './message'

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

const intervalId = ref<ReturnType<typeof setTimeout> | null>(null)
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

const peer = ref<Peer | null>(null)
const communicatedAircraft = ref<Aircraft | null>(null)
const audioContext = new AudioContext()
const isStarted = ref(false)
const micStream = ref<MediaStream | null>(null)
const noiseAudio = ref<HTMLAudioElement | null>(null)
const soundBuffer = ref<AudioBuffer | null>(null)
const isTalking = ref(false)
const conn = ref<DataConnection | null>(null)

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
watch(aircrafts, (newAircrafts, oldAircrafts) => {
  newAircrafts.forEach((newAircraft) => {
    const oldAircraft = oldAircrafts.find((oldAircraft) => oldAircraft.id === newAircraft.id)
    if (oldAircraft === undefined) return

    if (!oldAircraft.isInterceptIls && newAircraft.isInterceptIls) {
      ElNotification({
        title: 'Aircraft Updated',
        message: `Aircraft ${newAircraft.callsign} is intercepting ILS on runway ${newAircraft.expectRunway}`,
        position: 'bottom-right',
        type: 'warning',
        duration: 10000,
      })
    }
    if (!oldAircraft.isGoAround && newAircraft.isGoAround) {
      ElNotification({
        title: 'Aircraft Updated',
        message: `Aircraft ${newAircraft.callsign} is go around`,
        position: 'bottom-right',
        type: 'error',
        duration: 10000,
      })
    }
  })
})
watch(isTalking, (isTalking) => {
  micStream.value?.getAudioTracks()
    .forEach((t) => (t.kind == 'audio') && (t.enabled = isTalking))
  if (isTalking) {
    noiseAudio.value?.play()
  } else {
    noiseAudio.value?.pause()
  }
})

async function updateAircraft () {
  return fetch(`${server.value}/aircrafts`)
    .then((response) => response.json())
    .then((json: Aircraft[]) => (aircrafts.value = json))
}

const onClickShutdown = async (aircraft: Aircraft) => {
  await fetch(`${server.value}/aircrafts/${aircraft.id}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json'
    }
  })
  await updateAircraft()
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

const onClickOpenVhrBox = () => {
  window.open(
    'vhr-box.html?callsign=' + airportIdent.value + '_TWR',
    'vhrboxwindow',
    'popup=1,width=201,height=400'
  )
}

const onUpdateAircraft = async (aircraftId: string) => {
  const aircrafts = await updateAircraft()
  if (activeStatus.value === -1) return

  const aircraft = aircrafts.find((aircraft) => aircraft.id === aircraftId)
  if (aircraft === undefined) return
  activeStatus.value = aircraft.status
}

const call = ref<MediaConnection | null>(null)
const onMousedownAircraft = async (aircraft: Aircraft) => {
  communicatedAircraft.value = aircraft
  
  if (!soundBuffer.value) {
    console.error('Sound effect not loaded yet.')
    return
  }
  conn.value?.send({ type: 'TX', payload: { callsign: aircraft.callsign } } as TxMessage)

  isTalking.value = true
}
const onMouseupAircraft = async (aircraft: Aircraft) => {
  communicatedAircraft.value = null
  isTalking.value = false
  playTxSound()
  conn.value?.send({ type: 'TX_END', payload: { callsign: aircraft.callsign } } as TxEndMessage)
}

onMounted(() => {
  server.value = localStorage.getItem('server') ?? document.location.origin
  airportIdent.value = localStorage.getItem('airportIdent') ?? ''

  return updateAircraft()
})

onMounted(async () => {
  fetch(noiseSound)
    .then(response => response.arrayBuffer())
    .then(arrayBuffer => audioContext.decodeAudioData(arrayBuffer))
    .then(audioBuffer => {
      soundBuffer.value = audioBuffer
    })
    .catch(error => console.error('Error loading sound effect:', error))

  peer.value = new Peer({
    host: 'fsd.wlliou.pw',
    port: 2087,
    path: '/',
    key: 'peerjs',
    secure: true,
  })
  peer.value.on('open', function() {
    if (!peer.value) return

    conn.value = peer.value.connect(`fsd-training-server-${airportIdent.value.toLowerCase()}_twr`, {
       reliable: false,
       metadata: {
          callsign: 'OBS'
        },
     })
    conn.value.on('open', () => {
      conn.value?.on('data', (rData) => {
        const data = rData as Message
        if (data.type === 'ACK') {
          isStarted.value = true
        } else if (data.type === 'TX_END') {
          playRxSound()
        }
      })
    })
    conn.value.on('close', () => console.log('close'))
    conn.value.on('error', (err) => console.error('error', err))
  })


  getMicStream()
    .then((stream) => {
      micStream.value = stream
      micStream.value.getAudioTracks()
        .forEach((t) => (t.kind == 'audio') && (t.enabled = false))

      noiseAudio.value = new Audio(noiseSound)
      // @ts-expect-error
      const ctx = new (window.AudioContext || window.webkitAudioContext)()
      const gainNode = ctx.createGain()
      gainNode.gain.value = 0.1
      const streamDest = ctx.createMediaStreamDestination()
      const source = ctx.createMediaElementSource(noiseAudio.value)
      source.connect(gainNode)
      gainNode.connect(streamDest)
      const audioTrack = streamDest.stream

      // const mediaStream = audioContext.createMediaStreamDestination().stream
      // const audioTracks = mediaStream.getAudioTracks()
      // const audioTrack = audioTracks[0]
      const mergedStream = new MediaStream([...audioTrack.getAudioTracks(), ...micStream.value.getAudioTracks()])
      if (!call.value && peer.value) {
        console.log(`fsd-training-server-${airportIdent.value.toLowerCase()}_twr`)
        call.value = peer.value.call(`fsd-training-server-${airportIdent.value.toLowerCase()}_twr`, mergedStream, {
          metadata: {
            callsign: 'OBS'
          },
        })
        call.value.on('stream', (remoteStream) => {
          const audio = document.createElement('audio')
          audio.srcObject = remoteStream
          audio.play()
        })
        call.value.on('error', console.error)
      }
    })
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
  if (intervalId.value === null) return
  clearInterval(intervalId.value)
})
</script>

<style scoped>

</style>
