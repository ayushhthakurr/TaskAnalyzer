const tasks = [];

function parseDeps(v){
  if(!v) return [];
  return v.split(',').map(s=>s.trim()).filter(Boolean);
}

function badge(score){
  if(score>70) return {text:'High', cls:'high'};
  if(score>40) return {text:'Medium', cls:'medium'};
  return {text:'Low', cls:'low'};
}

function renderTaskList(){
  const el = document.getElementById('taskList');
  el.innerHTML = tasks.map(t=>`<span class="chip">${t.id}: ${t.title}</span>`).join('');
}

function addTask(){
  const title = document.getElementById('title').value.trim();
  const due_date = document.getElementById('due_date').value.trim();
  const hours = parseFloat(document.getElementById('hours').value||'1');
  const importance = parseInt(document.getElementById('importance').value||'5',10);
  const dependencies = parseDeps(document.getElementById('dependencies').value);
  const err = document.getElementById('error');
  err.textContent = '';
  if(!title){ err.textContent = 'Title is required'; return; }
  const id = title || `T${tasks.length+1}`;
  tasks.push({id,title,due_date,estimated_hours:hours,importance,dependencies});
  renderTaskList();
}

async function analyze(){
  const bulk = document.getElementById('bulk').value.trim();
  const strategy = document.getElementById('strategy').value;
  const loading = document.getElementById('loading');
  const results = document.getElementById('results');
  const cycles = document.getElementById('cycles');
  const err = document.getElementById('error');
  err.textContent = '';
  results.innerHTML = '';
  cycles.innerHTML = '';
  loading.textContent = 'Analyzing...';

  let payloadTasks = tasks;
  if(bulk){
    try{ payloadTasks = JSON.parse(bulk); }
    catch{ loading.textContent=''; err.textContent='Invalid bulk JSON'; return; }
  }

  const body = { tasks: payloadTasks };
  if(strategy) body.strategy = strategy;

  try{
    const res = await fetch('http://127.0.0.1:8000/api/tasks/analyze/',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify(body)
    });
    loading.textContent = '';
    if(!res.ok){
      let msg = res.statusText;
      try{ const j = await res.json(); msg = j.error||msg; }catch{}
      err.textContent = msg; return;
    }
    const data = await res.json();
    renderResults(data);
  }catch(e){
    loading.textContent='';
    err.textContent = 'Network error';
  }
}

function renderResults(data){
  const results = document.getElementById('results');
  const cycles = document.getElementById('cycles');
  results.innerHTML = (data.tasks||[]).map(t=>{
    const b = badge(t.score);
    return `
      <div class="card">
        <div class="title">${t.title}<span class="badge ${b.cls}">${b.text}</span></div>
        <div class="score">${t.score}</div>
        <div class="meta">
          <span>Due: ${t.due_date||'-'}</span>
          <span>Hours: ${t.estimated_hours}</span>
          <span>Importance: ${t.importance}</span>
        </div>
        <div>${t.explanation||''}</div>
      </div>
    `;
  }).join('');
  cycles.innerHTML = (data.cycles||[]).length ? `Cycles: ${(data.cycles||[]).map(c=>c.join(' → ')).join(' | ')}` : '';
}

document.getElementById('addTask').addEventListener('click', addTask);
document.getElementById('analyze').addEventListener('click', analyze);