export interface TxMessage {
  type: 'TX'
  payload: {
    callsign: string
  }
}

export interface TxEndMessage {
  type: 'TX_END'
  payload: {
    callsign: string
  }
}

export interface AckMessage {
  type: 'ACK'
}

export interface AddMessage {
  type: 'ADD',
  payload: {
    callsign: string
  }
}

export interface KillMessage {
  type: 'KILL',
  payload: {
    callsign: string
  }
}

export type Message = AckMessage | TxMessage | TxEndMessage | AddMessage | KillMessage
