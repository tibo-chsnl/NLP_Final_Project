import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Required for Docker standalone output
  output: "standalone",
};

export default nextConfig;
