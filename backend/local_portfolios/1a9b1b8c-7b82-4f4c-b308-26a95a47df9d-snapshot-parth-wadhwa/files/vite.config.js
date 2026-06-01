import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from 'tailwindcss';

export default defineConfig({
 plugins: [react()],
 css: {
 preprocessorOptions: {
 tailwindcss: {
 config: './tailwind.config.js',
 },
 },
 });
