const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = process.argv[2];
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 2409, height: 1169 } });
  const jobs = [
    ['blanc', 'Emma', 'apercu-blanc-Emma.png'],
    ['blanc', '', 'impression-blanc-sans-prenom.png'],
    ['vert', 'Emma', 'apercu-vert-Emma.png'],
    ['vert', '', 'impression-vert-sans-prenom.png'],
    ['blanc', 'Marie-Louise', 'test-prenom-long.png'],
  ];
  for (const [theme, name, out] of jobs) {
    await p.goto('file://' + path.join(dir, 'design.html') + `?theme=${theme}&name=${encodeURIComponent(name)}`);
    await p.waitForSelector('body[data-ready="1"]');
    await p.waitForTimeout(300);
    await p.locator('svg').screenshot({ path: path.join(dir, 'out', out), omitBackground: true });
  }
  await b.close();
})();
