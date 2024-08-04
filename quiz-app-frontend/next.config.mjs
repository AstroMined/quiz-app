/** @type {import('next').NextConfig} */
const nextConfig = {
  // Remove the experimental object
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/:path*', // Proxy to Backend
      },
    ];
  },
};

export default nextConfig;