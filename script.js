/* ===============================================================
   YOUR MEDIA. Each line is  nickname:"path to the file".
   Put files in the media folder, add a line here, then use the
   nickname as an app's icon or in a gallery / video / shake tab.
   =============================================================== */
const MEDIA={dorito:"media/SpinningDorito_pixel.gif",browser:"media/Browser_icon.png",nugget:"media/Alone_nugget.png",folder:"media/Dorito_folder_icon.png",nuggetVideo:"media/alone_nugget.mp4",galleryIcon:"media/Gallery_icon.png",doritoStill:"media/Dorito_still.png"};

/* ===============================================================
   YOUR APPS. Add one object here to add an icon + popup.
     id, title, icon (a key from MEDIA), address (shown in the bar)
     w / h: window size in px (h is optional)    open:true = opens on load
     tabs: each tab has a label and a template:
        'html'   -> html:'<h2>Hi</h2><p>text or <img src=…></p>'
        'search' -> a web search box
        'video'  -> src:'a video URL or MEDIA key'
        'shake'  -> count:28   (doritos that fall and bounce when you shake the window)
        'gallery'-> folders:[{name:'Pictures', folder:'media/gallery/pictures/', images:['a.png']}]  (see GALLERY HOW-TO below)
   One tab = no tab strip is shown.
   =============================================================== */
const APPS=[
  {id:'browser',title:'Dorito OS Browser',icon:'browser',address:'dorito.net://HIIIII.html/',w:620,open:true,tabs:[
    {label:'Search',template:'search'},
    {label:'Home',html:'<h2>Idk got lazy nothing here yet</h2><p>My website is still under construction :)</p><div class="c"><img src="media/SpinningDorito_pixel.gif" width="120" alt="Spinning dorito"></div>'}]},
  {id:'dorito',title:'Spinning Dorito',icon:'dorito',address:'dorito.net://spinning',w:340,tabs:[
    {label:'Dorito',html:'<div class="c"><img src="media/SpinningDorito_pixel.gif" width="200" alt="Spinning dorito"></div>'}]},
  {id:'nugget',title:'Alone nugget (he is very lonely)',label:'Alone nugget',icon:'nugget',address:'dorito.net://alone-nugget',w:420,tabs:[
    {label:'Nugget',template:'video',src:'nuggetVideo'}]},
  {id:'folder',title:'Dorito Folder',icon:'folder',address:'dorito.net://my-files',w:480,h:420,tabs:[
    {label:'Contents',template:'shake',count:35},
    {label:'Why?',html:'<h2>Doritos :D</h2><p>pls dont steal >:(</p>'}]},

  /* ===============================================================
     GALLERY HOW-TO  (more in DORITO-DESKTOP-HOWTO.txt)

     The Gallery opens on a set of FOLDERS. Click a folder to see the
     pictures inside it; click a picture to see it big.

     ADD A PICTURE TO A FOLDER
       1. Upload the picture to that folder in your GitHub repo.
          (For the "Pictures" folder below that is media/gallery/pictures/
          : on GitHub open it > Add file > Upload files > Commit.)
       2. Add its file name to that folder's images list:
            'my-photo.png',
          or with a caption shown in the big view:
            {file:'my-photo.png', title:'Me at the beach'},
       3. Commit script.js. Your site updates after a minute or so.
       Use simple names: lowercase, no spaces (my-photo.png). Capitals
       matter: Photo.PNG and photo.png are different files.

     ADD A NEW FOLDER
       Copy a whole  {name:'...', folder:'...', images:[...]}  block,
       put a comma after the block before it, then change:
         name   = the label shown under the folder icon
         folder = where its pictures live in your repo (end with a slash)
         images = the list of file names

     FOLDERS INSIDE FOLDERS
       Put  folders:[ {name:..., folder:..., images:[...]} ]  inside a
       folder block, the same way the Gallery itself holds folders.

     OPTIONS (on any folder)
       pixelated:true   keeps pixel art crisp when enlarged (not for photos)
       icon:'key'       use a different folder icon (a key from MEDIA)

     The four sample pictures use nicknames from the MEDIA list so the gallery works out of the box.
     Delete them when you add your own.
     =============================================================== */
  {id:'gallery',title:'Gallery',label:'Gallery',icon:'galleryIcon',address:'dorito.net://gallery',w:560,h:430,tabs:[
    {label:'Gallery',template:'gallery',folders:[

      {name:'Dorito things',folder:'media/gallery/dorito-things/',pixelated:true,images:[
        {file:'dorito',title:'Spinning dorito'},
        {file:'nugget',title:'Lonely nugget :C'},
        {file:'browser',title:'Dorito OS Browser icon'},
        {file:'folder',title:'Dorito folder icon'}
      ]},

      {name:'Pictures',folder:'media/gallery/pictures/',images:[
        /* add yours here, for example:
           'my-photo.png',
           {file:'beach.jpg', title:'Beach day'}, */
      ]}

    ]}
  ]}
];

const el=(t,c)=>{const e=document.createElement(t);if(c)e.className=c;return e},
      desk=document.getElementById('desk'),box=document.getElementById('icons'),wins={};
let z=10,count=0;

/* tab templates */
const TEMPLATES={
  html:t=>{const d=el('div','page');d.innerHTML=t.html||'';return d},
  search:()=>{const d=el('div','search');
    d.innerHTML='<img alt="" src="'+MEDIA.browser+'"><h2>Dorito Search</h2><div class="sbox"><input type="search" aria-label="Search" autocomplete="off"><span class="ph" aria-hidden="true">Search...</span></div><button class="btn" type="button">Search</button>';
    const i=d.querySelector('input'),go=()=>{const q=i.value.trim();if(q)window.open('https://www.google.com/search?q='+encodeURIComponent(q),'_blank','noopener')};
    const ph=d.querySelector('.ph');i.oninput=()=>{ph.hidden=!!i.value};d.querySelector('button').onclick=go;i.onkeydown=e=>{if(e.key==='Enter')go()};setTimeout(()=>i.focus(),30);return d},
  gallery:(t,x)=>{
    x.view.classList.add('flush','galv');
    const root={name:t.name||'Gallery',folder:t.folder||'',images:t.images||[],folders:t.folders||[],pixelated:t.pixelated},
      norm=i=>typeof i==='string'?{file:i}:i,src=(n,f)=>MEDIA[f]||(n.folder||'')+f,d=el('div');
    let path=[root],cur=-1;
    const node=()=>path[path.length-1],cls=()=>'gal'+(path.some(n=>n.pixelated)?' px':'');
    const up=()=>{if(path.length>1){path.pop();show()}};
    const show=()=>{cur=-1;const n=node(),subs=n.folders||[],imgs=(n.images||[]).map(norm);d.className=cls();d.innerHTML='';
      const bar=el('div','gbar'),crumb=el('span','gcrumb');
      if(path.length>1){const b=el('button','btn');b.type='button';b.textContent='Back';b.onclick=up;bar.appendChild(b)}
      crumb.textContent=path.map(p=>p.name).join(' / ');bar.appendChild(crumb);d.appendChild(bar);
      if(!subs.length&&!imgs.length){const p=el('p','empty');p.textContent='Empty :(';d.appendChild(p);d.focus();return}
      const g=el('div','gg');
      subs.forEach(f=>{const b=el('button','th fd'),im=el('img'),lb=el('span');b.type='button';b.title=f.name;im.src=MEDIA[f.icon||'folder'];im.alt='';lb.textContent=f.name;
        b.append(im,lb);b.onclick=()=>{path.push(f);show()};g.appendChild(b)});
      imgs.forEach((it,i)=>{const b=el('button','th'),im=el('img');b.type='button';b.title=it.title||it.file;im.src=src(n,it.file);im.alt=it.title||it.file;im.loading='lazy';
        im.onerror=()=>{b.classList.add('miss');b.textContent=it.file};b.appendChild(im);b.onclick=()=>open(i);g.appendChild(b)});
      d.appendChild(g);d.focus()};
    const open=i=>{const n=node(),list=(n.images||[]).map(norm);cur=(i+list.length)%list.length;const it=list[cur];d.className=cls()+' gv';d.innerHTML='';
      const bar=el('div','gbar'),back=el('button','btn'),pv=el('button','btn'),nx=el('button','btn'),c=el('span','gn'),im=el('img','big'),cap=el('div','gcap');
      back.type=pv.type=nx.type='button';back.textContent='Back';pv.textContent='<';nx.textContent='>';pv.setAttribute('aria-label','Previous');nx.setAttribute('aria-label','Next');
      c.textContent=(cur+1)+' / '+list.length;back.onclick=show;pv.onclick=()=>open(cur-1);nx.onclick=()=>open(cur+1);
      im.src=src(n,it.file);im.alt=it.title||it.file;im.onerror=()=>{cap.textContent='Could not load '+it.file+'. Check the file name and folder.'};
      cap.textContent=it.title||'';bar.append(back,pv,nx,c);d.append(bar,im,cap);d.focus()};
    d.onkeydown=e=>{const k=e.key;
      if(cur>=0){if(k==='ArrowLeft')open(cur-1);else if(k==='ArrowRight')open(cur+1);else if(k==='Escape'){e.stopPropagation();show()}else return}
      else if(k==='Escape'&&path.length>1){e.stopPropagation();up()}else return;
      e.preventDefault()};
    d.tabIndex=0;show();return d},
  shake:(t,x)=>{
    x.view.classList.add('flush','galv');
    const box=el('div','media'),cv=el('canvas'),cx=cv.getContext('2d'),img=new Image(),D=[],still=matchMedia('(prefers-reduced-motion:reduce)').matches;
    box.style.position='relative';box.append(cv);img.src=MEDIA[t.src||'doritoStill'];
    let W=0,H=0,S=1,dpr=1,last=0,wx=NaN,wy=0,vwx=0,vwy=0,moved=0,ready=false;
    new ResizeObserver(()=>{W=box.clientWidth;H=box.clientHeight;dpr=Math.min(2,devicePixelRatio||1);cv.width=W*dpr;cv.height=H*dpr;S=Math.max(.4,Math.min(4,W/460))}).observe(box);
    const rad=d=>d.k*21*S;
    const phys=dt=>{
      D.forEach(d=>{const r=rad(d);d.vy+=2200*dt;d.x+=d.vx*dt;d.y+=d.vy*dt;d.a+=d.va*dt;d.vx*=.9985;d.vy*=.9985;d.va*=.995;
        if(d.x<r){d.x=r;d.vx=Math.abs(d.vx)*.45}if(d.x>W-r){d.x=W-r;d.vx=-Math.abs(d.vx)*.45}
        if(d.y<r){d.y=r;d.vy=Math.abs(d.vy)*.45}
        if(d.y>H-r){d.y=H-r;d.vy=-Math.abs(d.vy)*.4;d.vx*=.985;d.va+=(d.vx/r-d.va)*.08}});
      for(let k=0;k<2;k++){
        for(let i=0;i<D.length;i++)for(let j=i+1;j<D.length;j++){const a=D[i],b=D[j],R=rad(a)+rad(b);let dx=b.x-a.x,dy=b.y-a.y;const q=dx*dx+dy*dy;
          if(q>=R*R||q===0)continue;const dist=Math.sqrt(q),nx=dx/dist,ny=dy/dist,o=(R-dist)/2;a.x-=nx*o;a.y-=ny*o;b.x+=nx*o;b.y+=ny*o;
          const vn=(a.vx-b.vx)*nx+(a.vy-b.vy)*ny;if(vn>0){const m=vn*.675;a.vx-=m*nx;a.vy-=m*ny;b.vx+=m*nx;b.vy+=m*ny;a.va+=(Math.random()-.5)*vn*.004;b.va-=(Math.random()-.5)*vn*.004}}
        D.forEach(d=>{const r=rad(d);d.x=Math.max(r,Math.min(W-r,d.x));d.y=Math.max(r,Math.min(H-r,d.y))})}};
    const frame=ts=>{
      if(!cv.isConnected)return;requestAnimationFrame(frame);
      if(!W||!H||!img.complete||!img.naturalWidth){last=ts;return}
      if(!ready){ready=true;for(let i=0;i<(t.count||28);i++)D.push({k:.9+Math.random()*.2,x:Math.random()*W,y:Math.random()*H*.45,vx:(Math.random()-.5)*200,vy:0,a:Math.random()*6.28,va:(Math.random()-.5)*4});
        if(still)for(let i=0;i<240;i++)phys(1/60)}
      const dt=Math.max(1/120,Math.min((ts-last)/1000,1/30));last=ts;
      const r=x.w.getBoundingClientRect();
      if(!isNaN(wx)){const vx=(r.left-wx)/dt,vy=(r.top-wy)/dt,ax=Math.max(-3500,Math.min(3500,vx-vwx)),ay=Math.max(-3500,Math.min(3500,vy-vwy));
        if(ax||ay)D.forEach(d=>{d.vx-=ax*.55;d.vy-=ay*.55;d.va+=(Math.random()-.5)*Math.hypot(ax,ay)*.0015});
        vwx=vx;vwy=vy}
      wx=r.left;wy=r.top;
      phys(dt/2);phys(dt/2);
      cx.setTransform(dpr,0,0,dpr,0,0);cx.clearRect(0,0,W,H);cx.imageSmoothingEnabled=false;
      D.forEach(d=>{const w=d.k*52*S,h=w*img.naturalHeight/img.naturalWidth;cx.save();cx.translate(d.x,d.y);cx.rotate(d.a);cx.drawImage(img,-w/2,-h/2,w,h);cx.restore()})};
    requestAnimationFrame(frame);return box},
  video:(t,x)=>{const d=el('div','media'),m=el('button','btn'),v=el('video');
    m.type='button';m.textContent='\uD83D\uDD0A';m.setAttribute('aria-label','Mute');
    v.src=MEDIA[t.src]||t.src;v.loop=true;v.autoplay=true;v.playsInline=true;
    m.onclick=()=>{v.muted=!v.muted;m.textContent=v.muted?'\uD83D\uDD07':'\uD83D\uDD0A'};
    x.ex.replaceChildren(m);x.view.classList.add('flush');
    v.onloadedmetadata=()=>{x.view.style.minHeight='0';if(x.w._user)return;const chrome=x.w.offsetHeight-x.view.clientHeight;
      x.w.style.height=Math.min(innerHeight-12,Math.round(chrome+x.view.clientWidth*v.videoHeight/v.videoWidth))+'px'};
    d.appendChild(v);v.play().catch(()=>{});return d}
};

/* desktop icons: drag them anywhere; positions are remembered */
const ROW=142,COL=124;let saved={};try{saved=JSON.parse(localStorage.getItem('dorito-icons-2')||'{}')}catch(e){}
const rows=Math.max(1,Math.floor((innerHeight-24)/ROW));
APPS.forEach((a,i)=>{
  const c=el('div','cell'),b=el('button','icon');b.type='button';b.innerHTML='<img alt=""><span></span>';
  b.firstChild.src=MEDIA[a.icon];b.lastChild.textContent=a.label||a.title;c.appendChild(b);
  const place=(x,y)=>{c.style.left=Math.max(0,Math.min(innerWidth-104,x))+'px';c.style.top=Math.max(0,Math.min(innerHeight-122,y))+'px'};
  const p=saved[a.id]||{x:12+Math.floor(i/rows)*COL,y:18+(i%rows)*ROW};place(p.x,p.y);
  let last=0;
  c.addEventListener('pointerdown',e=>{
    const sx=e.clientX,sy=e.clientY,ox=c.offsetLeft,oy=c.offsetTop;let moved=false;c.setPointerCapture(e.pointerId);
    const mv=v=>{if(!moved&&Math.hypot(v.clientX-sx,v.clientY-sy)<6)return;moved=true;c.classList.add('drag');place(ox+v.clientX-sx,oy+v.clientY-sy)};
    const up=()=>{c.removeEventListener('pointermove',mv);c.removeEventListener('pointerup',up);c.removeEventListener('pointercancel',up);c.classList.remove('drag');
      if(moved){saved[a.id]={x:c.offsetLeft,y:c.offsetTop};try{localStorage.setItem('dorito-icons-2',JSON.stringify(saved))}catch(e){}return}
      const n=Date.now();if(n-last<450||matchMedia('(pointer:coarse)').matches)launch(a);last=n};
    c.addEventListener('pointermove',mv);c.addEventListener('pointerup',up);c.addEventListener('pointercancel',up)});
  b.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();launch(a)}};
  box.appendChild(c);
});

function front(w){document.querySelectorAll('.win').forEach(x=>x.classList.remove('top'));w.classList.add('top');w.style.zIndex=++z}

function launch(a){
  if(wins[a.id]){front(wins[a.id]);return}
  const w=el('div','win');
  w.innerHTML='<div class="tb"><img alt=""><b></b><button class="btn x" type="button" aria-label="Close">X</button></div><div class="addr"><span>Address:</span><input class="url" type="text" spellcheck="false" autocomplete="off" aria-label="Address"></div><div class="tabs" role="tablist"></div><div class="view"><div class="load"><img alt="" src="'+MEDIA.dorito+'"><div>Loading\u2026</div><div class="bar"><u></u></div></div><div class="pg"></div></div><div class="stat"><span class="stt"></span><span>Dorito OS</span><span class="ex"></span><i class="grip" title="Resize"></i></div>';
  const $=s=>w.querySelector(s),pg=$('.pg'),load=$('.load'),st=$('.stt'),tabsEl=$('.tabs');
  $('.tb img').src=MEDIA[a.icon];$('.tb b').textContent=a.title;const url=$('.url'),home=a.address||'dorito.net://';url.value=home;
  url.onkeydown=e=>{if(e.key!=='Enter')return;const q=url.value.trim();if(!q||q===home)return;
    const isSite=/^https?:\/\/\S+$/i.test(q)||/^[^\s\/]+\.[a-z]{2,}(\/\S*)?$/i.test(q);
    window.open(isSite?(/^https?:/i.test(q)?q:'https://'+q):'https://www.google.com/search?q='+encodeURIComponent(q),'_blank','noopener');url.value=home;url.blur()};
  url.addEventListener('focus',()=>url.select());
  const W=Math.min(a.w||420,innerWidth-12);w.style.width=W+'px';if(a.h)w.style.height=Math.min(a.h,innerHeight-12)+'px';
  desk.appendChild(w);wins[a.id]=w;
  const off=(count++%5)*28,H=w.offsetHeight;
  w.style.left=Math.max(6,Math.min((innerWidth-W)/2+off-30,innerWidth-W-6))+'px';
  w.style.top=Math.max(6,Math.min((innerHeight-H)/2+off-30,innerHeight-H-6))+'px';
  front(w);w.addEventListener('pointerdown',()=>front(w));
  let timer;const ctx={w,view:$('.view'),ex:$('.ex')};
  /* scale the window's contents with the window (set once you start resizing) */
  const fit=()=>{const c=pg.firstElementChild;if(!c||c.classList.contains('media')||!w._base)return;
    const v=ctx.view;c.style.zoom=Math.max(.35,Math.min(6,Math.min(v.clientWidth/w._base.w,v.clientHeight/w._base.h)))};
  new ResizeObserver(fit).observe(ctx.view);
  const show=t=>{clearTimeout(timer);ctx.view.classList.remove('flush','galv');ctx.view.style.minHeight='';ctx.ex.replaceChildren();load.classList.remove('on');void load.offsetWidth;load.classList.add('on');pg.innerHTML='';$('.view').scrollTop=0;st.textContent='Loading '+t.label+'\u2026';
    timer=setTimeout(()=>{load.classList.remove('on');st.textContent='';pg.appendChild((TEMPLATES[t.template||'html']||TEMPLATES.html)(t,ctx));fit()},820)};
  if(a.tabs.length>1)a.tabs.forEach((t,i)=>{const b=el('button','tab');b.type='button';b.role='tab';b.textContent=t.label;b.setAttribute('aria-selected',i===0);
    b.onclick=()=>{[...tabsEl.children].forEach(c=>c.setAttribute('aria-selected',c===b));show(t)};tabsEl.appendChild(b)});
  show(a.tabs[0]);
  $('.x').onclick=()=>{clearTimeout(timer);w.remove();delete wins[a.id]};
  ['nw','ne','sw'].forEach(d=>{const h=el('i','rz '+d);h.dataset.dir=d;w.appendChild(h)});
  $('.grip').dataset.dir='se';
  w.querySelectorAll('.rz,.grip').forEach(h=>h.addEventListener('pointerdown',e=>{
    e.preventDefault();e.stopPropagation();const d=h.dataset.dir,r=w.getBoundingClientRect(),sx=e.clientX,sy=e.clientY;h.setPointerCapture(e.pointerId);if(!w._base)w._base={w:ctx.view.clientWidth,h:ctx.view.clientHeight};w.style.width=r.width+'px';w.style.height=r.height+'px';w._user=1;w.classList.add('sized');
    const mv=v=>{const dx=v.clientX-sx,dy=v.clientY-sy;
      if(d.includes('e'))w.style.width=Math.max(260,Math.min(innerWidth-r.left-2,r.width+dx))+'px';
      if(d.includes('w')){const nw=Math.max(260,Math.min(r.right,r.width-dx));w.style.width=nw+'px';w.style.left=(r.right-nw)+'px'}
      if(d.includes('s'))w.style.height=Math.max(200,Math.min(innerHeight-r.top-2,r.height+dy))+'px';
      if(d.includes('n')){const nh=Math.max(200,Math.min(r.bottom,r.height-dy));w.style.height=nh+'px';w.style.top=(r.bottom-nh)+'px'}};
    const up=()=>{h.removeEventListener('pointermove',mv);h.removeEventListener('pointerup',up)};h.addEventListener('pointermove',mv);h.addEventListener('pointerup',up)}));
  const tb=$('.tb');tb.addEventListener('pointerdown',e=>{
    if(e.target.closest('button'))return;const r=w.getBoundingClientRect(),dx=e.clientX-r.left,dy=e.clientY-r.top;tb.setPointerCapture(e.pointerId);
    const mv=v=>{w.style.left=Math.max(-r.width+80,Math.min(innerWidth-80,v.clientX-dx))+'px';w.style.top=Math.max(0,Math.min(innerHeight-30,v.clientY-dy))+'px'};
    const up=()=>{tb.removeEventListener('pointermove',mv);tb.removeEventListener('pointerup',up)};tb.addEventListener('pointermove',mv);tb.addEventListener('pointerup',up)});
}
addEventListener('keydown',e=>{if(e.key==='Escape'){const t=document.querySelector('.win.top .x');if(t)t.click()}});

APPS.filter(a=>a.open).forEach(launch); /* the Dorito OS Browser opens first */
