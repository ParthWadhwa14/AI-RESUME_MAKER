module.exports = {
 content: [
 './index.html',
 './src/**/*.{js,ts,jsx,tsx}',
 ],
 theme: {
 extend: {
 colors: {
 primary: '#1A1D23',
 secondary: '#2E3439',
 accent: '#4B5154',
 background: '#0A0C0D',
 foreground: '#FFFFFF',
 },
 typography: {
 fontFamily: ['Inter', 'sans-serif'],
 },
 spacing: {
 1: '4px',
 2: '8px',
 3: '12px',
 4: '16px',
 5: '20px',
 6: '24px',
 },
 borderRadius: {
 none: '0px',
 sm: '4px',
 md: '8px',
 lg: '12px',
 xl: '16px',
 },
 boxShadow: {
 sm: '0 1px 2px 0 rgba(0, 0, 0, 0.04)',
 md: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
 lg: '0 1px 5px 0 rgba(0, 0, 0, 0.2)',
 },
 },
 },
 plugins: [],
};
