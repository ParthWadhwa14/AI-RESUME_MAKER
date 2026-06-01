import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwind from 'vite-plugin-tailwind';
import { resolve } from 'path';

export default defineConfig({
 plugins: [react(), tailwind({
 config: './tailwind.config.js',
 })],
 css: {
 postcss: './postcss.config.js',
 },
 resolve: {
 alias: {
 '@': resolve(__dirname, './src'),
 },
 },
})