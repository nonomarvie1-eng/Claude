const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = process.argv[2];
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 2000, height: 2000 } });
  for (const [theme, name, out] of [
    ['blanc','Emma','orn-apercu-blanc.png'], ['blanc','','orn-impression-blanc.png'],
    ['vert','Emma','orn-apercu-vert.png'],  ['vert','','orn-impression-vert.png'],
    ['blanc','Marie-Louise','orn-test-long.png']]) {
    await p.goto('file://' + path.join(dir, 'ornament.html') + `?theme=${theme}&name=${encodeURIComponent(name)}`);
    await p.waitForSelector('body[data-ready="1"]'); await p.waitForTimeout(300);
    await p.locator('svg').screenshot({ path: path.join(dir, 'out', out), omitBackground: true });
  }
  await b.close();
})();
