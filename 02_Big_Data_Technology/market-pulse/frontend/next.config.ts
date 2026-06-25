import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Turbopack is the default bundler in Next.js 16.
  // No special config needed — the HMR loop was caused by
  // corrupted .next cache from the previous (duplicate) instance.
};

export default nextConfig;
