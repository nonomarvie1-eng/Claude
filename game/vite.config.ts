import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { viteSingleFile } from 'vite-plugin-singlefile';
import path from 'node:path';

// SINGLEFILE=1 inlines every asset into one index.html (shareable demo build).
const single = process.env.SINGLEFILE === '1';

export default defineConfig({
  base: './', // Stake Engine serves the game from /{team}/{game}/{version}/ -> relative paths
  plugins: [svelte(), ...(single ? [viteSingleFile()] : [])],
  resolve: { alias: { $shared: path.resolve(__dirname, '../shared') } },
  build: {
    target: 'es2020',
    assetsInlineLimit: single ? 100_000_000 : 4096,
    chunkSizeWarningLimit: 2000,
  },
  server: { fs: { allow: ['..'] } },
  test: { environment: 'node', include: ['src/**/*.test.ts'] },
});
