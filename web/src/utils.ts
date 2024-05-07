/// <reference types="webrtc" />

export async function getMicStream(): Promise<MediaStream> {
  const getUserMedia = (navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia)
  const devices = await navigator.mediaDevices.enumerateDevices()
  const device = devices.find((device) => device.kind === 'audioinput' && device.deviceId === 'default')
  if (!device) {
    throw new Error('No default audio input device found')
  }
  return new Promise((resolve, reject) => {
    getUserMedia(
      {
        video: false,
        audio: {
          deviceId: device.deviceId,
          echoCancellation: { exact: false },
          noiseSuppression: { exact: true },
        }
      },
      resolve,
      reject,
    )
  })
}
