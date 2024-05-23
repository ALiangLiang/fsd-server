export function openWebsocket(url: string = 'ws://localhost:8088') {
  return new Promise<[WebSocket, (command: string) => void]>((resolve, reject) => {
    try {
      const socket = new WebSocket(url, ['binary'])

      socket.addEventListener('open', function () {
        function sendCommand(command: string) {
          const blob = new Blob([command + '\r\n'], { type: 'text/plain' })
          socket.send(blob)
        }
        resolve([socket, sendCommand])
      })

      socket.addEventListener('close', () => reject())

      socket.addEventListener('error', reject)
    } catch (err) {
      reject(err)
    }
  })
}