export async function getMicStream() {
  const getUserMedia = (navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia)
  const devices = await navigator.mediaDevices.enumerateDevices()
  const device = devices.find((device) => device.kind === 'audioinput' && device.deviceId === 'default')
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
