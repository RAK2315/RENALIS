const { chromium } = require(process.env.RENALIS_PLAYWRIGHT_PATH || 'playwright');
const assert = require('node:assert/strict');
(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage();
    await page.goto('http://127.0.0.1:5173/workspace');
    await page.locator('.forecast-alert').waitFor();
    async function clock(value) {
      await page.locator('#clock').evaluate((e,v) => { Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(e,v); e.dispatchEvent(new Event('input',{bubbles:true})); },value);
      await page.waitForFunction(v => document.querySelector('#clock').value === String(v) && !document.querySelector('.cockpit').classList.contains('updating'),value);
    }
    await clock(120);
    const card = page.locator('.forecast-alert');
    const text = await card.innerText();
    console.log('Current-event card:',text.replaceAll('\n',' | '));
    assert.ok(!text.includes('of model particles'), 'Current-event card must not render a null particle percentage caption');
    assert.ok(!/NEXT \d+ MINUTES/.test(text), 'Current-event card must describe the current observation, not an advance warning');
    assert.match(text,/75\.7|mmHg/);
    assert.equal(await page.locator('#rate').isDisabled(),true);
    assert.equal(await page.locator('.scenario-results').count(),0);
    await clock(240);
    assert.match(await card.innerText(),/Session complete/);
    assert.ok(!(await card.innerText()).includes('of model particles'));
    console.log('Current-event and completed-session cards: passed');
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode=1; });
