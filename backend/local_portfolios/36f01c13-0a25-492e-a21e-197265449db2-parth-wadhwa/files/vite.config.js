import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { tailwind } from './tailwind.config.js';

export default defineConfig({
 plugins: [react(), tailwind],
 css: {
 postcss: {
 plugins: [
 require('tailwindcss'),
 require('autoprefixer'),
 ],
 },
 },
});
