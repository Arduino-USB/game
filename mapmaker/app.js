// -------------------------
// INITIAL SETUP & TILE SIZE
// -------------------------
let tileSize = parseInt(prompt("Enter tile size in pixels (e.g. 500):", "500")) || 500;

const canvas = document.getElementById("canvas");
canvas.width = tileSize;
canvas.height = tileSize;
const ctx = canvas.getContext("2d");

let currentX=0, currentY=0;
let grid={}; // "x,y": {image,file,scale,crop,regions}

function key(x,y){return `${x},${y}`;}
function ensureCell(x,y){if(!grid[key(x,y)]) grid[key(x,y)]={image:null,file:null,scale:1,crop:null,regions:[]};}
ensureCell(0,0);

function updateDisplay(){document.getElementById("coordDisplay").textContent=`(${currentX},${currentY})`;}

function render(){
	ctx.clearRect(0,0,canvas.width,canvas.height);
	let cell=grid[key(currentX,currentY)];
	if(cell.image){
		let img=new Image();
		img.src=cell.image;
		img.onload=()=>{
			if(cell.crop){
				let c=cell.crop;
				ctx.drawImage(img,c.x,c.y,c.w,c.h,0,0,tileSize,tileSize);
			}else{
				let s=cell.scale||1;
				ctx.drawImage(img,0,0,img.width*s,img.height*s);
			}
		}
	}
	// draw regions
	ctx.strokeStyle="red";
	cell.regions.forEach(r=>{
		ctx.strokeRect(r.x1,r.y1,r.x2-r.x1,r.y2-r.y1);
	});
}
updateDisplay();
render();

// -------------------------
// NAVIGATION
// -------------------------
document.getElementById("up").onclick=()=>{currentY--; ensureCell(currentX,currentY); updateDisplay(); render();}
document.getElementById("down").onclick=()=>{currentY++; ensureCell(currentX,currentY); updateDisplay(); render();}
document.getElementById("left").onclick=()=>{currentX--; ensureCell(currentX,currentY); updateDisplay(); render();}
document.getElementById("right").onclick=()=>{currentX++; ensureCell(currentX,currentY); updateDisplay(); render();}

// -------------------------
// REGION SELECTION BLUE RECT
// -------------------------
const preview=document.getElementById("regionPreview");
let selecting=false,startX,startY;

canvas.addEventListener("mousedown",e=>{
	selecting=true;
	startX=e.offsetX; startY=e.offsetY;
	preview.style.left=startX+"px";
	preview.style.top=startY+"px";
	preview.style.width="0px"; preview.style.height="0px";
	preview.style.display="block";
});
canvas.addEventListener("mousemove",e=>{
	if(!selecting) return;
	let x=e.offsetX,y=e.offsetY;
	let left=Math.min(startX,x), top=Math.min(startY,y), w=Math.abs(x-startX), h=Math.abs(y-startY);
	preview.style.left=left+"px"; preview.style.top=top+"px";
	preview.style.width=w+"px"; preview.style.height=h+"px";
});
canvas.addEventListener("mouseup",e=>{
	if(!selecting) return;
	selecting=false; preview.style.display="none";
	let x=e.offsetX,y=e.offsetY;
	let name=prompt("Name this region:"); if(!name)return;
	grid[key(currentX,currentY)].regions.push({name,x1:Math.min(startX,x),y1:Math.min(startY,y),x2:Math.max(startX,x),y2:Math.max(startY,y)});
	render();
});

// -------------------------
// IMAGE IMPORT + SCALE/FIT MODAL
// -------------------------
let pendingFile=null;
let modal=document.getElementById("modal");
let fitCanvas=document.getElementById("fitCanvas");
let fitCtx=fitCanvas.getContext("2d");
let fitOffset={x:0,y:0},fitDragging=false,imgObj=null,mode=null;

canvas.addEventListener("dragover",e=>e.preventDefault());
canvas.addEventListener("drop",e=>{
	e.preventDefault();
	let file=e.dataTransfer.files[0]; if(!file) return;
	pendingFile=file; imgObj=new Image();
	imgObj.onload=()=>{
		modal.style.display="flex";
		fitCanvas.width=tileSize; fitCanvas.height=tileSize;
		fitOffset={x:0,y:0};
		fitCtx.clearRect(0,0,tileSize,tileSize);
		fitCtx.drawImage(imgObj,fitOffset.x,fitOffset.y,imgObj.width,imgObj.height);
	}; imgObj.src=URL.createObjectURL(file);
});

// Modal buttons
document.getElementById("scaleBtn").onclick=()=>{mode="scale"; fitCanvas.style.display="none";}
document.getElementById("fitBtn").onclick=()=>{
	mode="fit"; fitCanvas.style.display="block";
	fitOffset={x:0,y:0}; drawFitCanvas();
};

function drawFitCanvas(){
	if(!imgObj) return;
	fitCtx.clearRect(0,0,fitCanvas.width,fitCanvas.height);
	fitCtx.drawImage(imgObj,fitOffset.x,fitOffset.y,imgObj.width,imgObj.height);
}

// Drag image in fit mode
fitCanvas.addEventListener("mousedown",e=>{fitDragging=true; fitDragStart={x:e.offsetX,y:e.offsetY};});
fitCanvas.addEventListener("mousemove",e=>{
	if(!fitDragging) return;
	let dx=e.offsetX-fitDragStart.x, dy=e.offsetY-fitDragStart.y;
	fitOffset.x+=dx; fitOffset.y+=dy;
	// Clamp: no empty space
	if(fitOffset.x>0) fitOffset.x=0;
	if(fitOffset.y>0) fitOffset.y=0;
	if(fitOffset.x+imgObj.width<tileSize) fitOffset.x=tileSize-imgObj.width;
	if(fitOffset.y+imgObj.height<tileSize) fitOffset.y=tileSize-imgObj.height;
	fitDragStart={x:e.offsetX,y:e.offsetY};
	drawFitCanvas();
});
fitCanvas.addEventListener("mouseup",e=>{fitDragging=false;});

// Apply/Cancel
document.getElementById("applyBtn").onclick=()=>{
	let cell=grid[key(currentX,currentY)];
	cell.file=pendingFile;
	if(mode=="scale"){cell.scale=tileSize/Math.max(imgObj.width,imgObj.height); cell.crop=null; cell.image=URL.createObjectURL(pendingFile);}
	else if(mode=="fit"){cell.crop={x:-fitOffset.x,y:-fitOffset.y,w:tileSize,h:tileSize}; cell.scale=1; cell.image=URL.createObjectURL(pendingFile);}
	render(); modal.style.display="none"; fitCanvas.style.display="none"; pendingFile=null; imgObj=null;
};
document.getElementById("cancelBtn").onclick=()=>{modal.style.display="none"; fitCanvas.style.display="none"; pendingFile=null; imgObj=null;}

// -------------------------
// EXPORT ZIP
// -------------------------
document.getElementById("exportBtn").onclick=async()=>{
	let zip=new JSZip();
	let imgFolder=zip.folder("imgs");
	let config={tileSize, cells:[]};
	for(let k in grid){
		let c=grid[k]; if(!c.file) continue;
		let [x,y]=k.split(",").map(Number);
		let fname=`imgs/img_${x}_${y}.png`;
		config.cells.push({x,y,image:fname,scale:c.scale,crop:c.crop,regions:c.regions});
		imgFolder.file(`img_${x}_${y}.png`,c.file);
	}
	zip.file("config.json",JSON.stringify(config,null,2));
	let blob=await zip.generateAsync({type:"blob"});
	saveAs(blob,"map_export.zip");
};

// -------------------------
// IMPORT ZIP
// -------------------------
document.getElementById("importZip").addEventListener("change",async e=>{
	let file=e.target.files[0]; let zip=await JSZip.loadAsync(file);
	let config=JSON.parse(await zip.file("config.json").async("string"));
	tileSize=config.tileSize||500; canvas.width=tileSize; canvas.height=tileSize;
	grid={};
	for(let cell of config.cells){
		let k=key(cell.x,cell.y);
		grid[k]={image:null,file:null,scale:cell.scale,crop:cell.crop,regions:cell.regions};
		let blob=await zip.file(cell.image).async("blob");
		grid[k].image=URL.createObjectURL(blob); grid[k].file=blob;
	}
	currentX=0; currentY=0; ensureCell(0,0); updateDisplay(); render();
});

