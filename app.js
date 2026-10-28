const data=[
{file:"app/routes.py",type:"direct",distance:1,why:"Imports app.service"},
{file:"app/worker.py",type:"direct",distance:1,why:"Imports app.service"},
{file:"tests/test_service.py",type:"test",distance:1,why:"Imports app.service"},
{file:"app/api.py",type:"transitive",distance:2,why:"Depends on app.routes"},
{file:"app/jobs.py",type:"transitive",distance:2,why:"Depends on app.worker"},
{file:"tests/test_routes.py",type:"test",distance:2,why:"Covers route behavior"},
{file:"app/summary.py",type:"transitive",distance:3,why:"Depends on app.jobs"},
{file:"tests/test_api.py",type:"test",distance:3,why:"Covers API behavior"}];
const tests=[["tests/test_service.py","Direct import of the changed service","HIGH"],["tests/test_routes.py","Route behavior may depend on service output","HIGH"],["tests/test_api.py","Transitive path through app.api","MEDIUM"],["tests/test_worker.py","Worker uses service calculations","MEDIUM"],["tests/test_summary.py","Downstream summary behavior","MEDIUM"]];
const evidence=[{line:4,code:"from app.service import calculate_total",file:"app/routes.py"},{line:2,code:"from app.service import calculate_total",file:"app/worker.py"},{line:1,code:"from app.service import calculate_total, format_total",file:"tests/test_service.py"}];
const $=s=>document.querySelector(s), esc=s=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
function render(){let q=$("#search").value.toLowerCase(),f=$("#filter").value;let rows=data.filter(x=>(x.file+" "+x.why).toLowerCase().includes(q)&&(f==="all"||x.type===f));$("#rows").innerHTML=rows.map(x=>`<tr><td class="file">${esc(x.file)}</td><td><span class="type ${x.type}">${x.type==="test"?"Test candidate":x.type==="direct"?"Direct impact":"Transitive"}</span></td><td><span class="distance">${x.distance}</span></td><td class="why">${esc(x.why)}</td><td><button class="inspect" data-file="${esc(x.file)}" aria-label="Inspect ${esc(x.file)}">↗</button></td></tr>`).join("");$("#count").textContent=`Showing ${rows.length} of ${data.length} sample rows`}
$("#test-list").innerHTML=tests.map(t=>`<div class="list-row"><span class="check">✓</span><div><b>${esc(t[0])}</b><small>${esc(t[1])}</small></div><span class="confidence">${t[2]}</span></div>`).join("");
$("#evidence-list").innerHTML=evidence.map(e=>`<div class="evidence-row"><span class="line">L${e.line}</span><div><code>${esc(e.code)}</code><small>${esc(e.file)}</small></div></div>`).join("");
function show(file){let e=evidence.filter(x=>x.file===file);$("#detail-title").textContent=file;$("#detail-code").textContent=e.length?e.map(x=>`${x.file}:${x.line}\n${x.code}`).join("\n\n"):"No specific import snippet is attached to this sample node.";$("#details").showModal();$("#copy").dataset.path=file}
function download(name,body,type){let u=URL.createObjectURL(new Blob([body],{type})),a=document.createElement("a");a.href=u;a.download=name;a.click();URL.revokeObjectURL(u)}
$("#search").addEventListener("input",render);$("#filter").addEventListener("change",render);
$("#export").addEventListener("click",()=>download("ripplemap-sample-report.json",JSON.stringify({notice:"Illustrative static data, not a live scan",changed_file:"app/service.py",impacted_files:data,candidate_tests:tests,evidence},null,2),"application/json"));
$("#export-tests").addEventListener("click",()=>download("ripplemap-candidate-tests.txt",tests.map(t=>`${t[0]} — ${t[2]}: ${t[1]}`).join("\n"),"text/plain"));
$("#reset").addEventListener("click",()=>{$("#search").value="";$("#filter").value="all";render()});
$("#inspect").addEventListener("click",()=>$("#evidence").scrollIntoView({behavior:"smooth"}));
document.addEventListener("click",e=>{let n=e.target.closest("[data-file]");if(n)show(n.dataset.file)});
$("#close").addEventListener("click",()=>$("#details").close());
$("#copy").addEventListener("click",async()=>{try{await navigator.clipboard.writeText($("#copy").dataset.path);$("#copy").textContent="Copied"}catch{$("#copy").textContent=$("#copy").dataset.path}});
render();