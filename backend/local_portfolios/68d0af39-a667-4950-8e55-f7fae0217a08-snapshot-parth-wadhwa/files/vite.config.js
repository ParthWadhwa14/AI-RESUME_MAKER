import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { tailwindcss } from 'tailwindcss/vite';
import autoprefixer from 'autoprefixer';
import postcss from 'postcss';

export default defineConfig({
 plugins: [react(), tailwindcss()],
 css: {
 postcss: {
 plugins: [autoprefixer(), require('tailwindcss')(), require('autoprefixer')()]
 }
}
});
