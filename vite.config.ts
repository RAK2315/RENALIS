import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  // Film compositions and exported source folders are not application entries.
  optimizeDeps: { entries: ['index.html'] },
  server: { port: 5173, strictPort: true,
    watch: { ignored: ['**/artifacts/**','**/tmp/**','**/data/**','**/output/**','**/.venv*/**','**/.chart-data-*/**'] },
    proxy: { '/api': 'http://127.0.0.1:8000' } },
  preview: { port: 5173, strictPort: true, proxy: { '/api': 'http://127.0.0.1:8000' } },
});
