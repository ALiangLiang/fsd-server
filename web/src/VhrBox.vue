<template>
  <div
    class="vhr-box"
    :style="(listMode === null) && 'height: 70px'"
  >
    <el-row align="middle" class="grey-bar" style="height: 20px">
      <el-col :span="2">
        <el-icon><CaretBottom /></el-icon>
      </el-col>
      <el-col :span="12">
        VHF
      </el-col>
    </el-row>
    <el-row :gutter="2" justify="space-between" align="middle" style="height: 25px">
      <el-col :span="14">
        <el-icon @click="listMode = (listMode !== 'channel') ? 'channel' : null"><CaretBottom /></el-icon>
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
        <span :class="isTalking || 'disabled-text'">TX</span>
      </el-col>
      <el-col :span="2">
        <el-icon style="cursor: pointer" @click="onClickReconnect"><Connection /></el-icon>
      </el-col>
      <el-col :span="2">
        <el-icon><Headset /></el-icon>
      </el-col>
    </el-row>
    <el-row :gutter="2" justify="space-between" align="middle" style="height: 25px">
      <el-col :span="14">
        <el-icon @click="listMode = (listMode !== 'user') ? 'user' : null"><CaretBottom /></el-icon>
        {{ (isTalking) ? callsign : '' }}
      </el-col>
      <el-col :span="2">
        <span class="disabled-text">RX</span>
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
          `Channels (${ Object.keys(peer?.connections ?? {}).length + 1 })` ||
          `Users (${ Object.keys(peer?.connections ?? {}).length })`
      }}
    </div>
    <div v-if="listMode !== null">
      <div class="list-container">
        <el-row v-if="listMode === 'channel'" class="row" justice="space-between">
          <span style="color: red">Unicom</span>
        </el-row>
        <el-row v-if="listMode === 'channel'" class="row" justice="space-between">
          {{ callsign }}
        </el-row>
        <el-row v-for="_, id in peer?.connections" class="row" justice="space-between">
          <el-col :span="12">
            {{ id }}
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
import { CaretBottom, Connection, Headset, Microphone } from '@element-plus/icons-vue'
import { Peer } from 'peerjs'

import { getMicStream } from './utils'

const peer = ref<Peer | null>(null)
const isStarted = ref(false)
const isTalking = ref(false)
const isMuted = ref(false)
const listMode = ref<'channel' | 'user' | null>('user')
const micStream = ref<MediaStream | null>(null)
const urlParams = new URLSearchParams(window.location.search)
const callsign = ref(
  urlParams.get('airport') + '-TWR'
)

watch([isTalking, isMuted], ([isTalking, isMuted]) => {
  micStream.value.getAudioTracks()
    .forEach(t => t.kind == 'audio' && (t.enabled = isTalking && !isMuted))
})

const onClickReconnect = () => {
  peer.value?.disconnect()
  peer.value?.reconnect()
}

function startToTalk(e: KeyboardEvent) {
  if (e.key === 'Pause' && !isTalking.value) {
    if (!micStream.value) return

    isTalking.value = true
    Object.values(peer.value.connections)
      .forEach((connections) => {
        connections.forEach((conn) => {
          conn.answer(micStream.value)
        })
      })
  }
}
function stopToTalk(e: KeyboardEvent) {
  if (e.key === 'Pause') {
    isTalking.value = false
  }
}
onMounted(async () => {
  getMicStream()
    .then((stream) => {
      micStream.value = stream
      micStream.value.getAudioTracks()
        .forEach((t) => t.kind == 'audio' && (t.enabled = false))

      createPeer(stream)
    })
  document.addEventListener('keydown', startToTalk)
  document.addEventListener('keyup', stopToTalk)
})
onUnmounted(() => {
  document.removeEventListener('keydown', startToTalk)
  document.removeEventListener('keyup', stopToTalk)
})

function createPeer (micStream: MediaStream) {
  peer.value = new Peer('fsd-training-server-' + callsign.value.toLowerCase(), {
		host: 'dev.d.wlliou.pw',
		port: 10000,
		path: '/myapp',
    secure: false,
	})
  peer.value.on('open', () => {
    isStarted.value = true
  })
  peer.value.on('connection', (conn) => {
    console.log('connection', conn)
    conn.on('data', (data) => {
      // Will print 'hi!'
      console.log(data)
    })
    conn.on('open', () => {
      conn.send('hello!')
    })
  })

  peer.value.on('call', (call) => {
    call.answer(micStream)
    callsign.value = call.metadata.callsign
    
    call.on('stream', (remoteStream) => {
      console.log('stream', remoteStream)
      const audio = document.createElement('audio')
      audio.srcObject = remoteStream
      audio.play()
    })
  }, console.error)
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
