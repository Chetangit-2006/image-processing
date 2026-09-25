
const practicals = {
3:{title:"Basic Image Operations",aim:"To perform basic image operations such as reading, RGB display, grayscale conversion, resizing and cropping.",ops:["display","rgb","grayscale","resize","crop"]},
4:{title:"Negative Image",aim:"To generate the negative image of an input image.",ops:["negative"]},
5:{title:"Brightness & Contrast",aim:"To adjust the brightness and contrast of an image.",ops:["brightness"]},
6:{title:"Image Sharpening",aim:"To sharpen an image using spatial filtering and the Laplacian operator.",ops:["kernel","laplacian"]},
7:{title:"Image Smoothing / Noise Removal",aim:"To apply averaging, Gaussian, median and bilateral filters and study their effects.",ops:["averaging","gaussian","median","bilateral"]},
8:{title:"Image Inpainting",aim:"To restore damaged regions using Telea and Navier-Stokes (NS) methods.",ops:["telea","ns"]},
9:{title:"Image Compression",aim:"To study lossy and lossless image compression and compare compression ratios.",ops:["lossy","lossless"]}
};
const names={display:"Read / Display",rgb:"RGB Display",grayscale:"Grayscale",resize:"Resize",crop:"Crop",negative:"Negative",brightness:"Brightness & Contrast",kernel:"Kernel Sharpening",laplacian:"Laplacian Sharpening",averaging:"Averaging Filter",gaussian:"Gaussian Filter",median:"Median Filter",bilateral:"Bilateral Filter",telea:"Telea Method",ns:"Navier-Stokes (NS)",lossy:"Lossy JPEG",lossless:"Lossless PNG"};
let current=3, file=null, selectedOp="display";

const nav=document.getElementById("nav");
Object.keys(practicals).forEach(n=>{let b=document.createElement("button");b.className="navbtn";b.innerHTML=`<span>Practical ${n}</span><small>${practicals[n].title}</small>`;b.onclick=()=>selectPractical(+n);b.id="nav"+n;nav.appendChild(b)});

function selectPractical(n){
 current=n; selectedOp=practicals[n].ops[0];
 document.querySelectorAll(".navbtn").forEach(x=>x.classList.remove("active"));
 document.getElementById("nav"+n).classList.add("active");
 document.getElementById("pno").textContent="PRACTICAL "+n;
 document.getElementById("title").textContent=practicals[n].title;
 document.getElementById("aim").textContent=practicals[n].aim;
 renderControls();
 document.getElementById("stats").innerHTML="";
}
selectPractical(3);

const drop=document.getElementById("drop"), fileInput=document.getElementById("file");
document.getElementById("browse").onclick=()=>fileInput.click();
drop.onclick=e=>{if(e.target.tagName!=="BUTTON")fileInput.click()};
fileInput.onchange=()=>setFile(fileInput.files[0]);
["dragenter","dragover"].forEach(e=>drop.addEventListener(e,x=>{x.preventDefault();drop.classList.add("drag")}));
["dragleave","drop"].forEach(e=>drop.addEventListener(e,x=>{x.preventDefault();drop.classList.remove("drag")}));
drop.addEventListener("drop",e=>setFile(e.dataTransfer.files[0]));
document.getElementById("replace").onclick=()=>fileInput.click();

function setFile(f){if(!f)return;if(!f.type.startsWith("image/"))return alert("Please choose an image.");file=f;document.getElementById("drop").classList.add("hidden");document.getElementById("preview").classList.remove("hidden");document.getElementById("original").src=URL.createObjectURL(f);document.getElementById("filename").textContent=f.name;document.getElementById("download").classList.add("hidden");document.getElementById("resultGrid").innerHTML='<div class="placeholder">Image uploaded. Choose an operation and click Apply Operation.</div>'}

function renderControls(){
 let c=document.getElementById("controls"); let ops=practicals[current].ops;
 let html=`<div class="controlrow"><label>Operation</label><select id="operation">${ops.map(o=>`<option value="${o}">${names[o]}</option>`).join("")}</select></div>`;
 if(current===3) html+=`<div id="extra" class="controlrow" style="margin-top:14px"></div>`;
 if(current===5) html+=`<div class="controlrow" style="margin-top:16px"><label>Brightness</label><input id="brightness" type="range" min="-100" max="100" value="10"><span class="value" id="bv">10</span><label>Contrast</label><input id="contrast" type="range" min="0.1" max="3" step="0.1" value="1.5"><span class="value" id="cv">1.5</span></div>`;
 if(current===9) html+=`<div class="controlrow" style="margin-top:16px"><label>JPEG Quality</label><input id="quality" type="range" min="10" max="100" value="30"><span class="value" id="qv">30</span><label>PNG Compression</label><input id="compression" type="range" min="0" max="9" value="9"><span class="value" id="pv">9</span></div>`;
 if(current===8) html+=`<p class="hint">For inpainting, draw a white mask over the damaged region. This prototype uses the uploaded image as the canvas and creates a mask in the browser.</p><div class="controlrow" style="margin-top:10px"><label>Brush</label><input id="brush" type="range" min="5" max="60" value="20"><button class="secondary" id="clearMask">Clear Mask</button></div><canvas id="maskCanvas" style="width:100%;max-width:700px;margin-top:12px;background:#111;border-radius:10px"></canvas>`;
 c.innerHTML=html;
 document.getElementById("operation").onchange=()=>{selectedOp=document.getElementById("operation").value;renderExtra()};
 if(document.getElementById("brightness")){brightness.oninput=()=>bv.textContent=brightness.value;contrast.oninput=()=>cv.textContent=contrast.value}
 if(document.getElementById("quality")){quality.oninput=()=>qv.textContent=quality.value;compression.oninput=()=>pv.textContent=compression.value}
 if(current===8) setupMask();
 renderExtra();
}
function renderExtra(){
 let e=document.getElementById("extra");if(!e)return;
 let op=document.getElementById("operation").value;
 if(op==="resize")e.innerHTML=`<label>Width <input id="width" type="number" value="250"></label><label>Height <input id="height" type="number" value="200"></label>`;
 else if(op==="crop")e.innerHTML=`<label>X <input id="x" type="number" value="100"></label><label>Y <input id="y" type="number" value="100"></label><label>Width <input id="width" type="number" value="200"></label><label>Height <input id="height" type="number" value="200"></label>`;
 else e.innerHTML="";
}
function setupMask(){
 const c=document.getElementById("maskCanvas"); if(!c)return;
 let img=new Image(); img.onload=()=>{let scale=Math.min(700/img.width,1);c.width=img.width*scale;c.height=img.height*scale;let ctx=c.getContext("2d");ctx.fillStyle="black";ctx.fillRect(0,0,c.width,c.height);let drawing=false;c.onmousedown=()=>drawing=true;c.onmouseup=()=>drawing=false;c.onmouseleave=()=>drawing=false;c.onmousemove=e=>{if(!drawing)return;ctx.fillStyle="white";ctx.beginPath();ctx.arc(e.offsetX,e.offsetY,+document.getElementById("brush").value,0,Math.PI*2);ctx.fill()};document.getElementById("clearMask").onclick=()=>{ctx.fillStyle="black";ctx.fillRect(0,0,c.width,c.height)}};if(file)img.src=URL.createObjectURL(file);}

document.getElementById("apply").onclick=async()=>{
 if(!file)return alert("Please upload an image first.");
 let fd=new FormData();fd.append("image",file);fd.append("practical",current);fd.append("operation",document.getElementById("operation").value);
 if(current===3){["width","height","x","y"].forEach(id=>{let x=document.getElementById(id);if(x)fd.append(id,x.value)})}
 if(current===5){fd.append("brightness",brightness.value);fd.append("contrast",contrast.value)}
 if(current===9){fd.append("quality",quality.value);fd.append("compression",compression.value)}
 if(current===8){let c=document.getElementById("maskCanvas");let blob=await new Promise(r=>c.toBlob(r,"image/png"));fd.append("mask",blob,"mask.png")}
 document.getElementById("status").textContent="Processing…";
 try{let r=await fetch("/process",{method:"POST",body:fd});let d=await r.json();if(!r.ok)throw Error(d.error||"Processing failed");document.getElementById("resultGrid").innerHTML=`<div class="result-box"><label>ORIGINAL</label><img src="${document.getElementById("original").src}"></div><div class="result-box"><label>PROCESSED — ${names[document.getElementById("operation").value]}</label><img src="${d.result}"></div>`;let a=document.getElementById("download");a.href=d.download;a.classList.remove("hidden");a.textContent="Download Result";if(d.original_kb!==undefined)document.getElementById("stats").innerHTML=`<div class="stats"><div class="stat"><small>Original</small><b>${d.original_kb} KB</b></div><div class="stat"><small>Compressed</small><b>${d.compressed_kb} KB</b></div><div class="stat"><small>Compression Ratio</small><b>${d.ratio}:1</b></div></div>`;document.getElementById("status").textContent="Completed"}catch(e){alert(e.message);document.getElementById("status").textContent="Error"}};
