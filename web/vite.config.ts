import { join, parse, resolve } from "path";
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import { certificateFor } from 'devcert'

// https://vitejs.dev/config/
export default defineConfig(async ({ command }) => ({
  base: '/console',
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
    }),
    Components({
      resolvers: [ElementPlusResolver()],
    }),
  ],
  build: {
    rollupOptions: {
      input: entryPoints(
        'index.html',
        'vhr-box.html',
      ),
    },
  },
  server: {
    https: (command !== 'build') ? {
      ...(await certificateFor('dev.d.wlliou.pw')),
      maxSessionMemory: 100,
      host: '0.0.0.0'
    } : null,
    host: true,
    port: 9000
  }
}))

function entryPoints(...paths) {
  const entries = paths.map(parse).map(entry => {
    const { dir, base, name, ext } = entry;
    const key = join(dir, name);
    const path = resolve(__dirname, dir, base);
    return [key, path];
  });

  const config = Object.fromEntries(entries);
  return config;
}
