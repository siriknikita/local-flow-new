import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:8080',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: [
    {
      command: 'cd backend && uv run python main.py',
      url: 'http://localhost:8000',
      reuseExistingServer: !process.env.CI,
      timeout: 120000, // 2 minutes for model download on first run
    },
    {
      command: 'cd frontend && python3 -m http.server 8080',
      url: 'http://localhost:8080',
      reuseExistingServer: !process.env.CI,
    },
  ],
});
