import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(),
  tailwindcss(),
  ],
  base: './', // Makes the subdirectory accessible to access the assets folder
  build: {
    outDir: 'dist-react',
  },
})
