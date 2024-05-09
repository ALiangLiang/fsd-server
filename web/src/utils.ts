/// <reference types="webrtc" />

import txSound from './assets/tx.wav'
import rx1Sound from './assets/rx1.wav'
import rx2Sound from './assets/rx2.wav'
import rx3Sound from './assets/rx3.wav'
import rx4Sound from './assets/rx4.wav'
import rx5Sound from './assets/rx5.wav'
import rx6Sound from './assets/rx6.wav'
import rx7Sound from './assets/rx7.wav'
import rx8Sound from './assets/rx8.wav'

export async function getMicStream(): Promise<[MediaStream, MediaDeviceInfo | undefined]> {
  const getUserMedia = (navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia)
  const devices = await navigator.mediaDevices.enumerateDevices()
  const device = devices.find((device) => device.kind === 'audioinput' && device.deviceId === 'default')
  return new Promise((resolve, reject) => {
    getUserMedia(
      {
        video: false,
        audio: {
          deviceId: device?.deviceId,
          echoCancellation: { exact: false },
          noiseSuppression: { exact: true },
        }
      },
      (stream) => resolve([stream, device]),
      reject,
    )
  })
}

const audio = new Audio(txSound)
export function playTxSound() {
  audio.play()
}

export function sample<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)]
}

const audio1 = new Audio(rx1Sound)
const audio2 = new Audio(rx2Sound)
const audio3 = new Audio(rx3Sound)
const audio4 = new Audio(rx4Sound)
const audio5 = new Audio(rx5Sound)
const audio6 = new Audio(rx6Sound)
const audio7 = new Audio(rx7Sound)
const audio8 = new Audio(rx8Sound)
export function playRxSound() {
  const audio = sample([
    audio1,
    audio2,
    audio3,
    audio4,
    audio5,
    audio6,
    audio7,
    audio8,
  ])
  audio.play()
}