// ココナラ用サムネイルの素材スクリーンショットを撮る。
//   cd promo && node take_shots.js   （Playwright と Chromium が必要）
// 出力: promo/shots/en-pc.png（幅1280）, en-sp.png（幅390）, ryokan-sp.png（幅390）
// 本番サイトを撮る場合は base を https://kioiworks.com/ に変える。
const { chromium } = require('playwright');
const path = require('path');
const base = 'file://' + path.resolve(__dirname, '..') + '/';
(async () => {
  const b = await chromium.launch();
  const jobs = [
    ['en-pc.png',     'en/index.html',        1280, 800],
    ['en-sp.png',     'en/index.html',        390,  844],
    ['ryokan-sp.png', 'en/ryokan/index.html', 390,  844],
  ];
  for (const [out, path, w, h] of jobs) {
    const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 2 });
    await p.route('**/*.onrender.com/**', r => r.abort());
    await p.goto(base + path);
    await p.screenshot({ path: __dirname + '/shots/' + out, fullPage: false });
    console.log(out, w, h);
  }
  await b.close();
})();
