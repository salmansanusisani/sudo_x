import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  workers: 1,
  reporter: 'list',
  use: {
    baseURL: 'http://127.0.0.1:8766',
    launchOptions: process.env.CHROMIUM_PATH
      ? { executablePath: process.env.CHROMIUM_PATH }
      : {},
    viewport: { width: 1440, height: 1000 },
    reducedMotion: 'reduce',
  },
  webServer: {
    command: process.platform === 'win32'
      ? '"..\\.venv\\Scripts\\python.exe" "..\\tests\\serve_e2e.py"'
      : '../.venv/bin/python ../tests/serve_e2e.py',
    url: 'http://127.0.0.1:8766/',
    reuseExistingServer: false,
    timeout: 30000,
  },
})
