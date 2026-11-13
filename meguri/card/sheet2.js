const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+process.cwd()+'/sheet_front_bright.html');await p.waitForTimeout(300);
await p.pdf({path:'sheet_front_bright.pdf',width:'210mm',height:'297mm',printBackground:true,pageRanges:'1'});await b.close();})();
