const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.env.DSA_TEST_URL || 'http://127.0.0.1:8746';
const content=id=>JSON.parse(fs.readFileSync(path.join(__dirname,'../../content/dsa/lessons',id+'.json'),'utf8'));
const extras={ 'avl-tree': 'function isBalanced(n){function h(n){if(!n)return 0;const a=h(n.left),b=h(n.right);return a<0||b<0||Math.abs(a-b)>1?-1:1+Math.max(a,b);}return h(n)>=0;}', dijkstra:'function relax(d,u,v,w){if(d[u]+w<d[v]){d[v]=d[u]+w;return true;}return false;}'};
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_PATH || '/snap/bin/chromium',args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1360,height:1000}}); const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base+'/tracks/dsa.html');
 await page.getByRole('heading',{name:'Your learning workspace'}).waitFor();
 for(const id of ['binary-search','avl-tree','dijkstra','knapsack','algorithmic-thinking','complexity','arrays','linked-lists']){
  await page.goto(base+'/tracks/dsa.html#topic/'+id);
  await page.locator('[data-position]').waitFor();
  console.log(id,await page.locator('[data-position]').textContent());
  await page.getByRole('button',{name:'Next',exact:true}).click();
  await page.getByRole('button',{name:'Previous',exact:true}).click();
  await page.getByRole('button',{name:'Predict next step'}).click();
  await page.locator('[data-prediction] button').first().click();
  await page.locator('[data-note]').fill('Browser-tested note for '+id);
  await page.getByRole('button',{name:'Save note',exact:true}).click();
  await page.locator('[data-run-language]').selectOption('javascript');
  await page.getByRole('button',{name:'Run tests',exact:true}).click();
  await page.locator('[data-run-results]').getByText('Not all tests passed.',{exact:true}).waitFor();
  await page.locator('[data-editor] textarea').fill(content(id).implementations.javascript+'\n'+(extras[id]||''));
  await page.getByRole('button',{name:'Run tests',exact:true}).click();
  await page.locator('[data-run-results]').getByText('All tests passed.',{exact:true}).waitFor();
  const oldEvidence=await page.evaluate(()=>DSAStore.mastery(location.hash.split('/')[1]).Implement.passed);
  assert.ok(oldEvidence>0,'passing implementation creates mastery evidence');
  await page.getByRole('button',{name:'Mark lesson complete',exact:true}).click();
  const completionId=({arrays:'dsa-1-2',complexity:'dsa-1-1'})[id]||id;
  const completed=await page.evaluate(id=>Progress.isDone(id),completionId);assert.equal(completed,true);
  const multi=content(id).quiz.find(question=>question.type==='multiple');
  if(multi) {
   const field=page.locator('[data-question-id="'+multi.id+'"]');
   await field.locator('input').nth(multi.answer[0]).check();
   await field.locator('[data-check]').click();
   assert.ok((await field.locator('[data-quiz-feedback]').textContent()).startsWith('Not quite.'));
   await page.reload(); await page.locator('[data-position]').waitFor();
   for(const index of multi.answer)await field.locator('input').nth(index).check();
   await field.locator('[data-check]').click();
   assert.ok((await field.locator('[data-quiz-feedback]').textContent()).startsWith('Correct.'));
   assert.equal(await page.getByRole('button',{name:'Mark incomplete',exact:true}).count(),1,'completion survives reload');
  }
  await page.locator('[data-question]').fill('What invariant is maintained?');
  await page.getByRole('button',{name:'Ask',exact:true}).click();
  await page.locator('[data-provider]').getByText('Local guided response — no AI model used',{exact:true}).waitFor();
 }
 for(const name of ['curriculum','paths','patterns','practice','compare','lab','complexity','memory','resources','library','graph','notes']){
  await page.goto(base+'/tracks/dsa.html#'+name);
  await page.locator('#dsa-root h2').first().waitFor();
  assert.equal(await page.getByText('Unable to load this view',{exact:true}).count(),0,name);
  console.log('route',name);
 }
 await page.goto(base+'/tracks/dsa.html#topic/linked-lists');
 await page.locator('[data-position]').waitFor();
 await page.getByText('Configure input',{exact:true}).click();
 for(const [input, result] of [
  [{values:[10,20,30],mode:'reverse'},[30,20,10]],
  [{values:[10,30],mode:'insert',index:1,value:20},[10,20,30]],
  [{values:[10,20,30],mode:'erase',index:1},[10,30]],
  [{values:[7,2,7],mode:'find',target:7},0],
  [{values:[1,3],other:[2,3],mode:'merge'},[1,2,3,3]],
  [{values:[],mode:'reverse'},[]]
 ]) {
  await page.locator('[data-input]').fill(JSON.stringify(input));
  await page.locator('[data-build]').click();
  assert.equal(await page.locator('[data-input-error]').textContent(),'');
  await page.locator('[data-seek]').evaluate(el=>{el.value=el.max;el.dispatchEvent(new Event('input',{bubbles:true}));});
  assert.ok((await page.locator('[data-position]').textContent()).includes('Result: '+JSON.stringify(result)));
  await page.getByRole('table',{name:'Node values and pointer connections, including detached nodes during updates'}).waitFor();
  await page.getByRole('img',{name:/Linked nodes/}).waitFor();
 }
 await page.goto(base+'/tracks/dsa.html#curriculum');
 await page.locator('[data-search]').fill('Binary Indexed Tree');
 await page.getByRole('link',{name:'Fenwick Tree',exact:true}).waitFor({state:'visible'});
 await page.locator('[data-search]').fill('Gomory');
 assert.equal(await page.getByRole('link',{name:'Gomory–Hu Tree',exact:true}).count(),2,'cross-listed canonical topic');
 await page.goto(base+'/tracks/dsa.html#compare/array-list');
 await page.locator('[data-comparison-body] table').waitFor();
 assert.ok((await page.locator('[data-comparison-body]').textContent()).includes('finding it can be Θ(n)'));
 await page.locator('[data-comparison]').selectOption('fenwick-segment');
 assert.ok(page.url().endsWith('#compare/fenwick-segment'));
 for(const id of ['algorithmic-thinking','complexity','arrays','linked-lists']) {
  await page.goto(base+'/tracks/dsa.html#lab');
  await page.locator('[data-alg]').selectOption(id);
  await page.locator('[data-position]').waitFor();
  assert.equal(await page.locator('[data-input-error]').textContent(),'');
  await page.getByRole('button',{name:'Next',exact:true}).click();
  if(id==='linked-lists') {
   assert.equal(await page.locator('[data-size]').isEnabled(),true);
   await page.locator('[data-size]').fill('5');
   await page.locator('[data-pattern]').selectOption('duplicates');
   await page.getByRole('button',{name:'Generate input',exact:true}).click();
   await page.locator('[data-position]').waitFor();
   const generated=JSON.parse(await page.locator('[data-input]').inputValue());
   assert.deepEqual(generated.values,[0,1,2,0,1]);
  }
 }
 await page.goto(base+'/tracks/dsa.html#resources');
 await page.getByRole('button',{name:'Save to library',exact:true}).first().click();
 await page.goto(base+'/tracks/dsa.html#library');
 await page.locator('[data-lib="notes"]').first().fill('Useful chapter');
 await page.locator('[data-lib="notes"]').first().blur();
 await page.setViewportSize({width:390,height:844});
 await page.goto(base+'/tracks/dsa.html#topic/binary-search');
 await page.locator('[data-position]').waitFor();
 const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth+2);
 await page.screenshot({path:process.env.DSA_SCREENSHOT || '/tmp/dsa-mobile.png',fullPage:true});
 assert.equal(overflow,false,'mobile horizontal overflow');
 for(const hash of ['topic/arrays','topic/linked-lists','compare/array-list','curriculum']) {
  await page.goto(base+'/tracks/dsa.html#'+hash);
  await page.locator('#dsa-root h2').first().waitFor();
  if(hash.startsWith('topic/'))await page.locator('[data-position]').waitFor();
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth+2),false,'mobile overflow: '+hash);
  if(hash==='topic/linked-lists') {
   await page.locator('[data-timeline]').scrollIntoViewIfNeeded();
   await page.locator('[data-timeline]').screenshot({path:'/tmp/dsa-linked-mobile.png'});
  }
 }
 assert.deepEqual(errors,[]);
 console.log('PASS browser routes, traces, predictions, drafts, tutor, library, notes, mobile; no JS errors');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
