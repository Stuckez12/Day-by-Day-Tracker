import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'


export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      'components': path.resolve(__dirname, 'src/components'),
      'pages': path.resolve(__dirname, 'src/pages'),
      'scripts': path.resolve(__dirname, 'src/scripts'),
      'styles': path.resolve(__dirname, 'src/styles'),
    },
  },
})
