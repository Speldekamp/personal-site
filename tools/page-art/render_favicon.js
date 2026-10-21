const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [svgPath, outDir] = process.argv.slice(2);
  const svg = fs.readFileSync(svgPath, 'utf8');
  const b = await chromium.launch();
  for (const s of [16, 32, 48, 180]) {
    let v = svg.replace('width="16" height="16"', `width="${s}" height="${s}"`);
    if (s === 180) v = v.replace('stroke-width="1"', 'stroke-width="0.4"').replace(' shape-rendering="crispEdges"', '');
    const p = await b.newPage({ viewport: { width: s, height: s }, deviceScaleFactor: 1 });
    await p.setContent(`<html><body style="margin:0;background:transparent">${v}</body></html>`);
    await p.screenshot({ path: `${outDir}/new-${s}.png`, omitBackground: true });
    await p.close();
  }
  await b.close();
})();
