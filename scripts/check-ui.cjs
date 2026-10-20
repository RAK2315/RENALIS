const { chromium } = require(process.env.RENALIS_PLAYWRIGHT_PATH || 'playwright');
const fs = require('fs');
const path = require('path');
const assert = require('node:assert/strict');

(async () => {
  const output = path.resolve('artifacts/qa'); fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });
    const errors = []; page.on('pageerror', error => errors.push(error.message));
    await page.goto('http://127.0.0.1:5173/workspace');
    await page.getByRole('heading', { name: 'A balance inside the patient.' }).waitFor();
    await page.getByRole('button', { name: 'Save scenario branch' }).waitFor();
    await page.waitForFunction(() => !document.querySelector('.cockpit').classList.contains('updating') && !document.querySelector('.scenario-panel .button').disabled);
    await page.locator('.recharts-wrapper').first().waitFor();
    await page.screenshot({ path: path.join(output, 'cockpit-desktop.png'), fullPage: true });
    await page.locator('#rate').evaluate(e => { const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set; set.call(e,1200); e.dispatchEvent(new Event('input',{bubbles:true})); });
    await page.waitForTimeout(500);
    await page.getByRole('button', { name: 'Step down at +15m' }).click();
    await page.waitForFunction(() => !document.querySelector('.scenario-panel .button').disabled);
    await page.getByRole('button', { name: 'Save scenario branch' }).click();
    await page.getByRole('status').filter({ hasText: 'Scenario saved' }).waitFor();
    await page.getByRole('button', { name: 'Record review' }).click();
    await page.getByLabel('Review note').fill('QA verification: review records the current patient and cutoff.');
    await page.getByRole('button', { name: 'Save review note' }).click();
    await page.getByRole('status').filter({ hasText: 'Review note saved' }).waitFor();
    await page.getByRole('button', { name: 'Reveal later readings' }).click();
    await page.locator('.outcome-note').waitFor();
    assert.match(await page.locator('.outcome-note').textContent(), /excluded from the forecast/);
    await page.getByRole('button', { name: 'Session memory' }).click();
    await page.getByRole('heading', { name: 'Saved scenario branches' }).waitFor();
    assert.ok(await page.locator('.record-list').count());
    assert.match(await page.locator('.review-history').textContent(), /QA verification/);
    await page.getByRole('button', { name: 'Unit overview' }).click();
    await page.locator('.unit-patient').first().waitFor();
    assert.equal(await page.locator('.unit-patient').count(), 4);
    await page.locator('.unit-patient').filter({ hasText: 'Leela Shah' }).click();
    await page.getByText('A fresh valid BP reading is needed before scenario comparison.').waitFor();
    assert.equal(await page.locator('#rate').isDisabled(), true);
    await page.locator('#patient').selectOption('RNL-027');
    await page.waitForFunction(() => !document.querySelector('.cockpit').classList.contains('updating'));
    await page.getByRole('button', { name: 'Model & evidence', exact: true }).first().click();
    await page.getByRole('heading', { name: 'Computed baseline comparison' }).waitFor({ timeout: 60000 });
    assert.equal(await page.locator('.benchmark-bars>div').count(), 4);
    await page.getByRole('heading', { name: 'Observed low-BP event baseline' }).waitFor();
    await page.screenshot({ path: path.join(output, 'evidence-desktop.png'), fullPage: true });
    await page.getByRole('button', { name: 'Patient twin', exact: true }).click();
    await page.locator('#patient').selectOption('RNL-014');
    await page.waitForFunction(() => !document.querySelector('.cockpit').classList.contains('updating'));
    for (const width of [1440, 1024, 768, 390, 320]) {
      await page.setViewportSize({ width, height: 1000 }); await page.waitForTimeout(150);
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 2);
      assert.equal(overflow, false, `Horizontal overflow at ${width}`);
      console.log(`Responsive layout ${width}px: passed`);
    }
    await page.screenshot({ path: path.join(output, 'cockpit-mobile.png'), fullPage: true });
    await page.locator('#clock').evaluate(e => { const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set; set.call(e,240); e.dispatchEvent(new Event('input',{bubbles:true})); });
    await page.getByText('Session complete. No further dialysis trajectory is forecast.').waitFor();
    assert.equal(await page.locator('#rate').isDisabled(), true);
    assert.deepEqual(errors, []);
    console.log('Scenario save, review save, reveal, patient switching, unit overview, benchmark and session completion: passed');
    console.log('Browser JavaScript errors: none');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
