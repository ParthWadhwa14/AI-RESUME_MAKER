/** @type {import('next').NextConfig} */
const nextConfig = {
  // Add this new property right here:
  allowedDevOrigins: ['10.82.139.86', 'http://10.82.139.86:3000'],
  
  // ... any other config options you already had below
};

export default nextConfig;