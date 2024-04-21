import type { InjectionKey, Ref } from 'vue'

export const serverKey = Symbol('server-key') as InjectionKey<Ref<string>>
export const airportIdentKey = Symbol('airport-ident-key') as InjectionKey<Ref<string>>
export const sidNamesKey = Symbol('sid-names-injection-key') as InjectionKey<Ref<string[]>>