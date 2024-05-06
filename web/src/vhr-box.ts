import { createApp } from 'vue'
import './style.css'
import VhrBox from './VhrBox.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './reset.css'

const app = createApp(VhrBox)
app.use(ElementPlus)
app.mount('#app')
