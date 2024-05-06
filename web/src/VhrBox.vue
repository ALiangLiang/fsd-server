<template>
  <div style="width: 200px; max-height: 400px; background-color: #252525; color: white; font-size: 12px; font-family: Segoe UI; cursor: default;">
    <el-row align="middle" style="background-color: #707070; height: 20px">
      <el-col :span="2">
        <el-icon><CaretBottom /></el-icon>
      </el-col>
      <el-col :span="12">
        VHF
      </el-col>
    </el-row>
    <el-row :gutter="2" justify="space-between" align="middle" style="height: 25px">
      <el-col :span="14">
        <el-icon><CaretBottom /></el-icon>
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
        <span style="color: #a0a0a0">TX</span>
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
        <el-icon><CaretBottom /></el-icon>
        {{ (isTalking) ? (callsign + '_TWR') : '' }}
      </el-col>
      <el-col :span="2">
        <span style="color: #a0a0a0">RX</span>
      </el-col>
      <el-col :span="2">
        <el-icon><Microphone /></el-icon>
      </el-col>
    </el-row>
    <div style="background-color: #707070; height: 14px; padding-left: 6px">
      Channels ({{ Object.keys(peer?.connections ?? {}).length + 1 }})
    </div>
    <div style="background-color: #303030">
      <div style="background-color: #555555; margin: 0 4px">
        <div style="color: red; height: 18px">
          Unicom
        </div>
        <div v-for="conn, id in peer?.connections" style="background-color: #525252; height: 18px">
          {{ id }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, provide, computed, watch, onMounted, onUnmounted } from 'vue'
import { CaretBottom, Connection, Headset, Microphone } from '@element-plus/icons-vue'
import { Peer } from 'peerjs'

import { getMicStream } from './utils'

const peer = ref<Peer | null>(null)
const isStarted = ref(false)
const isTalking = ref(false)
const micStream = ref<MediaStream | null>(null)
const urlParams = new URLSearchParams(window.location.search)
const callsign = ref(
  urlParams.get('airport')
)

watch(isTalking, (isTalking) => {
  micStream.value.getAudioTracks().map(t => t.kind == 'audio' && (t.enabled = isTalking))
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
  peer.value = new Peer('fsd-training-server-rctp-twr', {
		host: 'dev.d.wlliou.pw',
		port: 10000,
		path: '/myapp',
    secure: false,
	})
  peer.value.on('open', function(id) {
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

</style>
