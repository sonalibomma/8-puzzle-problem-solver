function grid(state){
  let g = document.createElement("div");
  g.className = "grid";
  state.forEach(v=>{
    let c = document.createElement("div");
    c.className = "cell";
    c.innerText = v===0?"":v;
    g.appendChild(c);
  });
  return g;
}

async function solve(){
  document.getElementById("path").innerHTML = "";
  const s = document.getElementById("state").value;

  const r = await fetch("/solve",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({state:s})
  });
  const d = await r.json();
  if(!r.ok){ alert(d.error); return; }

  document.getElementById("info").innerText =
    `Moves: ${d.moves}, Nodes: ${d.nodes}, Time: ${d.time}ms`;

  d.path.forEach(p=>document.getElementById("path").appendChild(grid(p)));
}

async function history(){
  const r = await fetch("/history");
  const d = await r.json();
  document.getElementById("hist").innerText =
    d.map(x=>x.join(" | ")).join("\n");
}
