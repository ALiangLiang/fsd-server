import type { InjectionKey, Ref } from 'vue'

import type { Aircraft, Parking, Flightplan, Approach } from './types'

export type extractInjectionKey<Type> = Type extends InjectionKey<infer X> ? X : never

export const serverKey = Symbol('server-injection-key') as InjectionKey<Ref<string>>
export const airportIdentKey = Symbol('airport-ident-injection-key') as InjectionKey<Ref<string>>
export const aircraftsKey = Symbol('aircrafts-injection-key') as InjectionKey<Ref<Aircraft[]>>
export const sidNamesKey = Symbol('sid-names-injection-key') as InjectionKey<Ref<string[]>>
export const approachesKey = Symbol('approaches-injection-key') as InjectionKey<Ref<Approach[]>>
export const parkingsKey = Symbol('parkings-injection-key') as InjectionKey<
  Ref<Parking[]>
>
export const presetFlightplansKey = Symbol('preset-flightplans-injection-key') as InjectionKey<
  Ref<Flightplan[]>
>