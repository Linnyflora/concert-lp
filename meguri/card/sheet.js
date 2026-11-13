const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
for (const s of ['front','back']){await p.goto('file://'+process.cwd()+'/sheet_'+s+'.html');await p.waitForTimeout(300);
await p.pdf({path:'sheet_'+s+'.pdf',width:'210mm',height:'297mm',printBackground:true,pageRanges:'1'});}
await b.close();})();
