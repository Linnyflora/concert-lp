const { chromium } = require('playwright');
(async()=>{const [,,html,png,pdf]=process.argv;const b=await chromium.launch();
const p=await b.newPage({viewport:{width:344,height:208},deviceScaleFactor:600/96});
await p.goto('file://'+html);await p.waitForTimeout(300);
await p.screenshot({path:png,clip:{x:0,y:0,width:91/25.4*96,height:55/25.4*96}});
if(pdf) await p.pdf({path:pdf,width:'91mm',height:'55mm',printBackground:true,pageRanges:'1'});
await b.close();})();
