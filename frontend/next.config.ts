/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  distDir: 'out',
  images: {
    unoptimized: true,
  },
  // ISSO resolve o problema dos textos pretos sem estilo:
  assetPrefix: './', 
};

export default nextConfig;