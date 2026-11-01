const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
await p.goto('file://'+process.argv[2]);await p.waitForSelector('body[data-done]');
const svgs=await p.$$eval('.abc svg',x=>x.length);console.log('svgs',svgs,'errs',errs);
await p.pdf({path:process.argv[3],format:'A4',printBackground:true,
 displayHeaderFooter:true,headerTemplate:'<div></div>',footerTemplate:'<div style="font-size:8pt;width:100%;text-align:center;color:#777">Crossing the Bridge — <span class="pageNumber"></span></div>',margin:{top:'16mm',bottom:'18mm',left:'15mm',right:'15mm'}});
await b.close();})();
