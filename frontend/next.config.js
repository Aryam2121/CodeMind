/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    PYTHON_AGENT_URL: process.env.PYTHON_AGENT_URL || 'http://localhost:8000',
  },
}

module.exports = nextConfig
