// @ts-check
const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./specs",
  timeout: 30_000,
  retries: 0,
  use: {
    baseURL: "http://127.0.0.1:5111",
    video: "retain-on-failure",
    trace: "retain-on-failure",
    screenshot: "on",
  },
  projects: [
    {
      name: "desktop",
      use: { viewport: { width: 1280, height: 720 } },
    },
    {
      name: "mobile",
      use: { viewport: { width: 375, height: 667 } },
    },
  ],
  webServer: {
    command: "python serve.py",
    url: "http://127.0.0.1:5111",
    reuseExistingServer: !process.env.CI,
    timeout: 10_000,
  },
});
