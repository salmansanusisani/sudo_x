import { test, expect } from '@playwright/test'
import { type } from 'node:os'

const token = 'test-fixture-token-not-for-real-use-00001'
const connect = async (page: import('@playwright/test').Page) => {
  await page.goto(`/#token=${token}`)
  await expect(page.getByText('LOCAL SESSION', { exact: true })).toBeVisible()
  await expect(page).not.toHaveURL(/token=/)
}

test('preview is usable and never performs external requests', async ({ page }) => {
  const external: string[] = []
  const errors: string[] = []
  page.on('request', request => { if (!request.url().startsWith('http://127.0.0.1:8766')) external.push(request.url()) })
  page.on('pageerror', error => errors.push(error.message))
  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'Mission control.' })).toBeVisible()
  await expect(page.getByText('Interface preview', { exact: true })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Bring Nigeria into focus' })).toBeDisabled()
  await expect(page.getByRole('img', { name: 'Offline reference globe centered on Africa' })).toBeVisible()
  await page.screenshot({ path: 'test-results/desktop-overview.png', fullPage: true })
  expect(external).toEqual([])
  expect(errors).toEqual([])
})

test('real snapshot produces evidence and persists across refresh', async ({ page }) => {
  await connect(page)
  await page.getByRole('button', { name: 'Inspect this machine', exact: true }).click()
  await expect(page.getByText(/Read-only local system snapshot collected. No system changes made./).first()).toBeVisible()
  await expect(page.getByText('Operating system', { exact: true })).toBeVisible()
  await expect(page.getByText(type() === 'Windows_NT' ? 'Windows' : type(), { exact: true })).toBeVisible()
  await expect(page.getByLabel('Execution trace')).toContainText('No system changes made')
  await page.reload()
  await page.getByRole('button', { name: 'Mission history', exact: true }).click()
  await expect(page.getByRole('button', { name: /Collect a read-only system snapshot/ }).first()).toBeVisible()
  await page.getByRole('button', { name: /Collect a read-only system snapshot/ }).first().click()
  await expect(page.getByText('Operating system', { exact: true })).toBeVisible()
})

test('Nigeria focuses real geography without fabricating current news', async ({ page }) => {
  await connect(page)
  await page.getByRole('button', { name: 'Bring Nigeria into focus' }).click()
  await expect(page.getByRole('heading', { name: 'Nigeria.' })).toBeVisible()
  await expect(page.getByLabel('Execution trace')).toContainText('the news request is not fulfilled')
  await expect(page.getByText('No current news fetched')).toBeVisible()
  await expect(page.getByRole('img', { name: /Geographic map focused on Nigeria/ })).toBeVisible()
  await page.screenshot({ path: 'test-results/nigeria-map.png', fullPage: true })
})

test('Tavily research is opt-in and shows public sources', async ({ page }) => {
  test.skip(!process.env.SUDOX_LIVE_E2E, 'Live Tavily test spends API credit.')
  await connect(page)
  await page.getByRole('button', { name: 'Fetch current Nigeria sources', exact: true }).click()
  await expect(page.getByRole('region', { name: 'Nigeria news research' })).toContainText('CURRENT PUBLIC SOURCES')
  await expect(page.getByText('CLOUD DISCLOSURE', { exact: true })).toBeVisible()
})

test('unsupported instructions are safely rendered and blocked', async ({ page }) => {
  await connect(page)
  await page.getByLabel('Your mission').fill('<script>alert(1)</script> run nmap on the Internet')
  await page.getByRole('button', { name: 'Send mission' }).click()
  await expect(page.getByLabel('Execution trace')).toContainText('No shell commands, file searches, or external actions were performed.')
  await expect(page.getByText('<script>alert(1)</script> run nmap on the Internet', { exact: true })).toBeVisible()
})

test('planner preview is explicit and non-executable', async ({ page }) => {
  await connect(page)
  await page.getByLabel('Your mission').fill('inspect my project and run a command')
  await page.getByRole('button', { name: 'Preview plan', exact: true }).click()
  await expect(page.getByRole('alert')).toContainText('No non-executable planner is configured')
  await expect(page.getByText('NON-EXECUTABLE PLAN', { exact: true })).toHaveCount(0)
})

test('live planner preview shows cloud disclosure when enabled', async ({ page }) => {
  test.skip(!process.env.SUDOX_LIVE_E2E, 'Live provider test spends inference credit.')
  await connect(page)
  await page.getByLabel('Your mission').fill('Prepare a read-only system observation plan.')
  await page.getByRole('button', { name: 'Preview plan', exact: true }).click()
  await expect(page.getByText('CLOUD DISCLOSURE', { exact: true })).toBeVisible()
  await expect(page.getByText('Nebius Token Factory', { exact: true })).toBeVisible()
  await expect(page.getByText(/No tool, file, network, or machine action/)).toBeVisible()
})

test('desktop view and privacy controls disclose boundaries', async ({ page }) => {
  await connect(page)
  await page.getByRole('button', { name: 'Open my desktop view' }).click()
  await expect(page.getByText('View-only. Computer control is not implemented.')).toBeVisible()
  await page.getByRole('button', { name: 'Start voice input' }).click()
  await expect(page.getByRole('alert')).toContainText(/Voice input|microphone/i)
  await page.getByRole('button', { name: 'Dismiss notification' }).click()
  await page.getByRole('button', { name: 'Settings and privacy' }).click()
  const motion = page.getByRole('switch', { name: 'Interface motion' })
  await expect(motion).toHaveAttribute('aria-checked', 'false')
  await motion.click()
  await expect(motion).toHaveAttribute('aria-checked', 'true')
  await expect(page.getByText('Reasoning provider', { exact: true })).toBeVisible()
  const registry = page.getByRole('region', { name: 'What SUDO X can do.' })
  await expect(registry).toBeVisible()
  await expect(registry.getByText('Authorized network observation', { exact: true })).toBeVisible()
  await expect(registry.getByText('Asset authorization, egress enforcement, and parser gates are not implemented.', { exact: true })).toBeVisible()
})

test('all sections fit mobile without horizontal overflow', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await connect(page)
  const assertFits = async () => expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true)
  await assertFits()
  await page.screenshot({ path: 'test-results/mobile-overview.png', fullPage: true })
  for (const name of ['Mission history', 'Security lab', 'Code workspace', 'Settings and privacy']) {
    await page.getByRole('button', { name, exact: true }).click()
    await assertFits()
  }
  await page.getByRole('button', { name: 'Mission control', exact: true }).click()
  await page.getByRole('button', { name: 'Bring Nigeria into focus' }).click()
  await expect(page.getByRole('heading', { name: 'Nigeria.' })).toBeVisible()
  await assertFits()
})

test('expired session is explicit and never enables task controls', async ({ page }) => {
  await page.goto('/#token=incorrect-session-token-with-at-least-32-chars')
  await expect(page.getByRole('alert')).toContainText('Session expired')
  await expect(page.getByRole('button', { name: 'Bring Nigeria into focus' })).toBeDisabled()
})

test('build information is keyboard accessible and closes with Escape', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('button', { name: 'About this build' }).click()
  await expect(page.getByRole('dialog')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Close build information' })).toBeFocused()
  await page.keyboard.press('Escape')
  await expect(page.getByRole('dialog')).toHaveCount(0)
  await page.keyboard.press('Control+k')
  await expect(page.getByLabel('Your mission')).toBeFocused()
})

test('screen preview stops its tracks without uploading frames', async ({ page }) => {
  await page.addInitScript(() => {
    const canvas = document.createElement('canvas')
    canvas.width = 320; canvas.height = 180
    const context = canvas.getContext('2d')!
    context.fillStyle = '#123456'; context.fillRect(0, 0, 320, 180)
    const stream = canvas.captureStream(1)
    Object.defineProperty(navigator.mediaDevices, 'getDisplayMedia', { value: async () => stream })
    ;(window as unknown as { testCapture: MediaStream }).testCapture = stream
  })
  await page.goto('/')
  await page.getByRole('button', { name: 'Open my desktop view' }).click()
  await page.getByRole('button', { name: 'Choose a screen' }).click()
  await expect(page.getByText(/Screen sharing active/)).toBeVisible()
  await expect(page.getByLabel('Locally shared screen preview')).toBeVisible()
  await expect.poll(() => page.getByLabel('Locally shared screen preview').evaluate((video: HTMLVideoElement) => video.readyState)).toBeGreaterThanOrEqual(2)
  await page.getByRole('button', { name: 'Stop sharing' }).click()
  await expect(page.getByLabel('Locally shared screen preview')).toHaveCount(0)
  expect(await page.evaluate(() => (window as unknown as { testCapture: MediaStream }).testCapture.getTracks().every(track => track.readyState === 'ended'))).toBe(true)
})
