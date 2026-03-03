import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 30000,
  webServer: process.env.PLAYWRIGHT_BASE_URL
    ? undefined
    : {
      command: "npm run dev -p 3001", // Use dev server for local E2E to avoid standalone build issues
      port: 3001,
      timeout: 60000,
      reuseExistingServer: true,
    },
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || "http://localhost:3001",
    headless: true,
  },
  projects: [
    {
      name: "chromium",
      use: { browserName: "chromium" },
    },
  ],
});
