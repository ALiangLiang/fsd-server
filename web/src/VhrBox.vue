<template>
  <div
    class="vhr-box"
    :style="(listMode === null) && 'height: 70px'"
  >
    <el-row align="middle" class="grey-bar" style="height: 20px">
      <el-col :span="2">
        <el-icon><CaretBottom /></el-icon>
      </el-col>
      <el-col :span="20">
        VHF
      </el-col>
      <el-col :span="2">
        <el-icon style="cursor: pointer" @click="onClickSetting"><Setting /></el-icon>
      </el-col>
    </el-row>
    <el-row :gutter="2" justify="space-between" align="middle" style="height: 25px">
      <el-col :span="14">
        <el-icon @click="listMode = (listMode !== 'channel') ? 'channel' : null"><CaretBottom /></el-icon>
        <el-icon><Antenna /></el-icon>
        118.700
      </el-col>
      <el-col :span="2">
        <span 
          v-if="!peer?.disconnected && !peer?.destroyed" 
          style="color: #54a054"
        >
          {{ (isStarted) ? 'CA' : ''}}
        </span>
      </el-col>
      <el-col :span="2">
        <span
          :class="isTalking || 'disabled-text'"
          style="cursor: pointer"
          @mousedown="() => startToTalk()"
          @mouseup="() => stopToTalk()"
        >
          TX
        </span>
      </el-col>
      <el-col :span="2">
        <el-icon style="cursor: pointer" @click="onClickReconnect"><Wifi /></el-icon>
      </el-col>
      <el-col :span="2">
        <el-icon><Headset /></el-icon>
      </el-col>
    </el-row>
    <el-row :gutter="2" justify="space-between" align="middle" style="height: 25px">
      <el-col :span="16">
        <el-icon @click="listMode = (listMode !== 'user') ? 'user' : null"><CaretBottom /></el-icon>
        {{ (isTalking) ? callsign : '' }}
        {{ talker }}
      </el-col>
      <el-col :span="2">
        <span :class="talker || 'disabled-text'">RX</span>
      </el-col>
      <el-col :span="2">
        <el-icon :class="talker || 'disabled-text'"><Search /></el-icon>
      </el-col>
      <el-col :span="2">
        <el-icon style="cursor: pointer" @click="isMuted = !isMuted">
          <Microphone :class="isMuted && 'disabled-text'" />
        </el-icon>
      </el-col>
    </el-row>
    <div v-if="listMode !== null" class="grey-bar" style="height: 14px">
      {{
        (listMode === 'channel') &&
          `Channels (${ connections.size + 1 })` ||
        (listMode === 'user') &&
          `Users (${ connections.size })` ||
          'Settings'
      }}
    </div>
    <div v-if="listMode !== null">
      <div v-if="listMode === 'setting'" class="list-container">
        <el-row class="row" justice="space-between">
          <el-col :span="12">
            Always talk
          </el-col>
          <el-col
            :span="12"
            @click="isAlwaysTalk = !isAlwaysTalk"
          >
            <!-- {{ (isAlwaysTalk) ? 'Yes' : 'No' }} -->
            {{ 'No' }}
          </el-col>
        </el-row>
        <el-row class="row" justice="space-between">
          <el-col :span="12">
            PTT key
          </el-col>
          <el-col :span="12" style="cursor: pointer" @click="onClickChangePttKey">
            {{ (isChangingPttKey) ? '' : pttKey }}
          </el-col>
        </el-row>
        <el-row class="row" justice="space-between">
          <el-col :span="12">
            Input Device
          </el-col>
          <el-col :span="12">
            {{ inputDeviceName }}
          </el-col>
        </el-row>
      </div>
      <div v-else class="list-container">
        <el-row v-if="listMode === 'channel'" class="row" justice="space-between">
          <span style="color: red">Unicom</span>
        </el-row>
        <el-row v-if="listMode === 'channel'" class="row" justice="space-between">
          {{ callsign }}
        </el-row>
        <el-row v-for="[_, conn] in connections" class="row" justice="space-between">
          <el-col :span="12">
            {{ conn.metadata.callsign }}
          </el-col>
          <el-col :span="12" style="text-align: end">
            <el-icon style="margin-right: 8px"><Headset /></el-icon>
          </el-col>
        </el-row>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { CaretBottom, Headset, Microphone, Setting } from '@element-plus/icons-vue'
import { Peer, type DataConnection, type MediaConnection } from 'peerjs'

import { getMicStream, playTxSound, playRxSound } from './utils'
import Wifi from './components/icons/Wifi.vue'
import Search from './components/icons/Search.vue'
import Antenna from './components/icons/Antenna.vue'
import type {
  Message, 
  TxMessage,
  TxEndMessage, 
  AckMessage,
  MemberListMessage 
} from './message'

const peer = ref<Peer | null>(null)
const isStarted = ref(false)
const isTalking = ref(false)
const isMuted = ref(false)
const listMode = ref<'channel' | 'user' | 'setting' | null>('user')
const micStream = ref<MediaStream | null>(null)
const urlParams = new URLSearchParams(window.location.search)
const talker = ref<string | null>(null)
const callsign = ref(
  urlParams.get('callsign') ?? ('TRAINEE-' + (Math.random() + 1).toString(36).substring(8).toUpperCase())
)
const connections = ref<Map<string, (DataConnection | MediaConnection)>>(new Map())
const isAlwaysTalk = ref(false)
const isChangingPttKey = ref(false)
const pttKey = ref(localStorage.getItem('pttKey') ?? 'Pause')
const inputDeviceName = ref('Unknown')

watch([isTalking, isMuted], ([isTalking, isMuted]) => {
  micStream.value?.getAudioTracks()
    .forEach(t => t.kind == 'audio' && (t.enabled = isTalking && !isMuted))
})
watch(pttKey, (pttKey) => localStorage.setItem('pttKey', pttKey))

const onClickReconnect = () => {
  peer.value?.disconnect()
  peer.value?.reconnect()
}

const onClickSetting = () => {
  listMode.value = (listMode.value === 'setting') ? null : 'setting'
}

const onClickChangePttKey = () => {
  isChangingPttKey.value = true
  console.log(isChangingPttKey.value)
  function onkeydown (e: KeyboardEvent) {
    if (e.key !== 'Escape') {
      pttKey.value = e.key
    }
    isChangingPttKey.value = false
    document.removeEventListener('keydown', onkeydown)
  }
  document.addEventListener('keydown', onkeydown)
}

function startToTalk () {
  if (!micStream.value) return

  isTalking.value = true
  broadcastMessage({
    type: 'TX',
    payload: {
      callsign: callsign.value
    }
  } as TxMessage)
  connections.value.forEach((conn) => {
    if (conn.type === 'media' && micStream.value) {
      (conn as MediaConnection).answer(micStream.value)
    }
  })
}
function stopToTalk () {
  isTalking.value = false
  playTxSound()
  broadcastMessage({
    type: 'TX_END',
    payload: {
      callsign: callsign.value
    }
  } as TxEndMessage)
}
function onKeydown(e: KeyboardEvent) {
  if (e.key === pttKey.value && !isTalking.value) {
    startToTalk()
  }
}
function onKeyUp(e: KeyboardEvent) {
  if (e.key === pttKey.value) {
    stopToTalk()
  }
}
function onMousedown(e: MouseEvent) {
  if (e.button === 1 && !isTalking.value) {
    startToTalk()
  }
}
function onMouseup(e: MouseEvent) {
  if (e.button === 1) {
    stopToTalk()
  }
}
function broadcastMessage(message: Message) {
  connections.value.forEach((conn) => {
    if (conn.type === 'data') {
      console.log(conn.peer, message);
      (conn as DataConnection).send(message)
    }
  })
}

onMounted(async () => {
  getMicStream()
    .then(([stream, device]) => {
      micStream.value = stream
      micStream.value.getAudioTracks()
        .forEach((t) => t.kind == 'audio' && (t.enabled = false))
      if (device) {
        inputDeviceName.value = device.label
      }

      createPeer(stream)
    })
  document.addEventListener('keydown', onKeydown)
  document.addEventListener('keyup', onKeyUp)
  document.addEventListener('mousedown', onMousedown)
  document.addEventListener('mouseup', onMouseup)
})
onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
  document.removeEventListener('keyup', onKeyUp)
  document.removeEventListener('mousedown', onMousedown)
  document.removeEventListener('mouseup', onMouseup)
})

function createPeer (micStream: MediaStream) {
  peer.value = new Peer('fsd-training-server-' + callsign.value.toLowerCase(), {
    // host: 'd.wlliou.pw',
    host: 'fsd.wlliou.pw',
    port: 2087,
    path: '/',
    key: 'peerjs',
    secure: true,
  })
  peer.value.on('open', () => {
    isStarted.value = true
  })
  peer.value.on('connection', (conn) => {
    connections.value.set(conn.peer, conn)

    conn.on('data', (rData) => {
        const data = rData as Message
      if (data.type === 'TX') {
        talker.value = (data as TxMessage).payload.callsign
      } else if (data.type === 'TX_END') {
        if (talker.value === (data as TxEndMessage).payload.callsign) {
          talker.value = null
          playRxSound()
        }
      }
    })
    conn.on('open', () => {
      conn.send({ type: 'ACK' } as AckMessage)
      conn.send({
        type: 'MEMBER_LIST',
        payload: {
          members: Array.from(connections.value.values())
            .filter((conn) => conn.type === 'media')
            .map((conn) => conn.peer)
        }
      } as MemberListMessage)
    })
    conn.on('close', () => {
      connections.value.delete(conn.peer)
    })
  })

  peer.value.on('call', (call) => {
    connections.value.set(call.peer, call)

    call.answer(micStream)
    
    call.on('stream', (remoteStream) => {
      console.log('stream', remoteStream)
      const audio = document.createElement('audio')
      audio.srcObject = remoteStream
      audio.play()
    })

    call.on('close', () => {
      connections.value.delete(call.peer)
    })

    call.on('error', console.error)
  })
  peer.value.on('disconnected', () => console.log('disconnected'))
  peer.value.on('close', () => console.log('close'))
  peer.value.on('error', (err) => console.error('error', err))
}
onUnmounted(() => {
  peer.value?.destroy()
})
</script>

<style scoped>
.vhr-box {
  width: 200px;
  height: 100vh;
  background-color: #252525;
  color: white;
  font-size: 12px;
  font-family: Segoe UI;
  cursor: default;
}

.vhr-box > * {
  padding-left: 4px;
  padding-right: 4px;
}

.grey-bar {
  background-color: #707070;
}

.disabled-text {
  color: #a0a0a0;
}

.list-container {
  background-color: #303030;
}

.list-container .row:nth-child(odd) {
  background-color: #555555;
  height: 18px;
  line-height: normal;
}

.list-container .row:nth-child(even) {
  background-color: #525252;
  height: 18px;
  line-height: normal;
}
</style>
