/* ===============================================================
   YOUR MEDIA. Each line is  nickname:"path to the file".
   Put files in the media folder, add a line here, then use the
   nickname as an app's icon or in a gallery / video / shake tab.
   =============================================================== */
const MEDIA={dorito:"media/SpinningDorito_pixel.gif",browser:"media/Browser_icon.png",nugget:"media/Alone_nugget.png",cmd:"media/Dorito_cmd.png",folder:"media/Dorito_folder_icon.png",nuggetVideo:"media/alone_nugget.mp4",galleryIcon:"media/Gallery_icon.png",doritoStill:"media/Dorito_still.png"};

/* ===============================================================
   YOUR APPS. Add one object here to add an icon + popup.
     id, title, icon (a key from MEDIA), address (shown in the bar)
     w / h: window size in px (h is optional)    open:true = opens on load
     pos:[x,y]  where the icon sits on the desktop, as fractions of the screen
                (0 = left / top edge, 1 = right / bottom edge). Example [0.45,0.08]
     wpos:[x,y] OPTIONAL: where the WINDOW opens; x is where its RIGHT edge sits, y its top, as fractions of the screen ([.97,.04] = upper right)
     fw / fh    OPTIONAL: the window opens this big as a fraction of the screen
                (fw:.73 = 73% of the screen width) and its content scales to fit
     tabs: each tab has a label and a template:
        'html'   -> html:'<h2>Hi</h2><p>text or <img src=…></p>'
        'search' -> a web search box
        'video'  -> src:'a video URL or MEDIA key'
        'shake'  -> count:28   (doritos that fall and bounce when you shake the window)
        'gallery'-> folders:[{name:'Pictures', folder:'media/gallery/pictures/', images:['a.png']}]  (see GALLERY HOW-TO below)
   One tab = no tab strip is shown.
   =============================================================== */
const APPS=[
  {id:'browser',title:'Dorito OS Browser',icon:'browser',address:'dorito.net://HIIIII.html/',w:620,open:true,pos:[.432,.386],fw:.243,fh:.267,tabs:[
    {label:'Search',template:'search'},
    {label:'Home',html:'<h2>Idk got lazy nothing here yet</h2><p>My website is still under construction :)</p><div class="c"><img src="media/SpinningDorito_pixel.gif" width="120" alt="Spinning dorito"></div>'}]},
  {id:'console',title:'Console',icon:'cmd',address:'dorito.net://console',w:520,h:390,open:true,wpos:[.97,.04],pos:[.66,.56],tabs:[
    {label:'Console',template:'console'}]},
  {id:'dorito',title:'Spinning Dorito',icon:'dorito',address:'dorito.net://spinning',w:340,pos:[.32,.541],tabs:[
    {label:'Dorito',html:'<div class="c"><img src="media/SpinningDorito_pixel.gif" width="200" alt="Spinning dorito"></div>'}]},
  {id:'nugget',title:'Alone nugget (he is very lonely)',label:'Alone nugget',icon:'nugget',address:'dorito.net://alone-nugget',w:420,pos:[.641,.235],tabs:[
    {label:'Nugget',template:'video',src:'nuggetVideo'}]},
  {id:'folder',title:'Dorito Folder',icon:'folder',address:'dorito.net://my-files',w:480,h:420,pos:[.456,.084],tabs:[
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
  {id:'gallery',title:'Gallery',label:'Gallery',icon:'galleryIcon',address:'dorito.net://gallery',w:560,h:430,pos:[.231,.195],tabs:[
    {label:'Gallery',template:'gallery',folders:[

      {name:'Dorito things',folder:'media/gallery/dorito-things/',pixelated:true,images:[
        {file:'dorito',title:'Spinning dorito'},
        {file:'nugget',title:'Lonely nugget :C'},
        {file:'browser',title:'Dorito OS Browser icon'},
        {file:'folder',title:'Dorito folder icon'}
      ]}

      /* Folders below are managed by add_to_gallery.py. Do not edit between the AUTO-GALLERY markers
         by hand (you can, but the script rewrites that part). */
    ].concat(/*AUTO-GALLERY-START*/[{"name": "Pictures", "folder": "media/gallery/pictures/", "images": [{"file": "SO-SAD.gif", "title": "SO SAD"}]}, {"name": "locator", "folder": "media/gallery/locator/", "images": [], "folders": [{"name": "casino", "folder": "media/gallery/locator/casino/", "images": [{"file": "CASINO_map1.png", "title": "CASINO map1"}, {"file": "CASINO_map2.png", "title": "CASINO map2"}, {"file": "CASINO_map2_rotated.png", "title": "CASINO map2 rotated"}], "folders": [{"name": "pics", "folder": "media/gallery/locator/casino/pics/", "images": [{"file": "image_000.png", "title": "Image 000"}, {"file": "image_001.png", "title": "Image 001"}, {"file": "image_002.png", "title": "Image 002"}, {"file": "image_003.png", "title": "Image 003"}, {"file": "image_004.png", "title": "Image 004"}, {"file": "image_005.png", "title": "Image 005"}, {"file": "image_006.png", "title": "Image 006"}, {"file": "image_007.png", "title": "Image 007"}]}]}, {"name": "ccc", "folder": "media/gallery/locator/ccc/", "images": [{"file": "CCC_map1.png", "title": "CCC map1"}, {"file": "CCC_map2_metro1.png", "title": "CCC map2 metro1"}, {"file": "CCC_map3_metro2.png", "title": "CCC map3 metro2"}, {"file": "CCC_map4.png", "title": "CCC map4"}], "folders": [{"name": "old-unused", "folder": "media/gallery/locator/ccc/old-unused/", "images": [{"file": "CCC_map1.png", "title": "CCC map1"}], "folders": [{"name": "pics", "folder": "media/gallery/locator/ccc/old-unused/pics/", "images": [{"file": "image_000.png", "title": "Image 000"}, {"file": "image_001.png", "title": "Image 001"}, {"file": "image_002.png", "title": "Image 002"}, {"file": "image_003.png", "title": "Image 003"}, {"file": "image_004.png", "title": "Image 004"}, {"file": "image_005.png", "title": "Image 005"}, {"file": "image_006.png", "title": "Image 006"}, {"file": "image_007.png", "title": "Image 007"}, {"file": "image_008.png", "title": "Image 008"}, {"file": "image_009.png", "title": "Image 009"}, {"file": "image_010.png", "title": "Image 010"}, {"file": "image_011.png", "title": "Image 011"}]}]}, {"name": "pics-new", "folder": "media/gallery/locator/ccc/pics-new/", "images": [{"file": "image_000.png", "title": "Image 000"}, {"file": "image_001.png", "title": "Image 001"}, {"file": "image_002.png", "title": "Image 002"}, {"file": "image_003.png", "title": "Image 003"}, {"file": "image_004.png", "title": "Image 004"}, {"file": "image_005.png", "title": "Image 005"}, {"file": "image_006.png", "title": "Image 006"}, {"file": "image_007.png", "title": "Image 007"}, {"file": "image_008.png", "title": "Image 008"}, {"file": "image_009.png", "title": "Image 009"}, {"file": "image_010.png", "title": "Image 010"}, {"file": "image_011.png", "title": "Image 011"}, {"file": "image_012.png", "title": "Image 012"}, {"file": "image_013.png", "title": "Image 013"}, {"file": "image_014.png", "title": "Image 014"}, {"file": "image_015.png", "title": "Image 015"}, {"file": "image_016.png", "title": "Image 016"}]}]}, {"name": "fishing-mall", "folder": "media/gallery/locator/fishing-mall/", "images": [{"file": "FishMall_map1.png", "title": "FishMall map1"}, {"file": "Fishmall_map2.png", "title": "Fishmall map2"}, {"file": "Fishmall_map3.png", "title": "Fishmall map3"}], "folders": [{"name": "pics", "folder": "media/gallery/locator/fishing-mall/pics/", "images": [{"file": "image_000.png", "title": "Image 000"}, {"file": "image_001.png", "title": "Image 001"}, {"file": "image_002.png", "title": "Image 002"}, {"file": "image_003.png", "title": "Image 003"}, {"file": "image_004.png", "title": "Image 004"}, {"file": "image_005.png", "title": "Image 005"}, {"file": "image_006.png", "title": "Image 006"}, {"file": "image_007.png", "title": "Image 007"}, {"file": "image_008.png", "title": "Image 008"}, {"file": "image_009.png", "title": "Image 009"}, {"file": "image_010.png", "title": "Image 010"}, {"file": "image_011.png", "title": "Image 011"}, {"file": "image_012.png", "title": "Image 012"}, {"file": "image_013.png", "title": "Image 013"}, {"file": "image_014.png", "title": "Image 014"}, {"file": "image_015.png", "title": "Image 015"}, {"file": "image_016.png", "title": "Image 016"}, {"file": "image_017.png", "title": "Image 017"}, {"file": "image_018.png", "title": "Image 018"}]}]}, {"name": "icons", "folder": "media/gallery/locator/icons/", "images": [{"file": "file_0b4f6a84-cf67-47ab-abd9-ee3ccb49c623.png", "title": "File 0b4f6a84 cf67 47ab abd9 ee3ccb49c623"}, {"file": "file_0b9bc2a9-287d-4e77-a983-e21027aec03d.png", "title": "File 0b9bc2a9 287d 4e77 a983 e21027aec03d"}, {"file": "file_8b13a8a8-6d6c-4334-a759-f2a95226e347.png", "title": "File 8b13a8a8 6d6c 4334 a759 f2a95226e347"}, {"file": "file_8dd4c64f-8277-4615-949e-465866060d90.png", "title": "File 8dd4c64f 8277 4615 949e 465866060d90"}, {"file": "file_61ecf72c-6600-4498-b870-bafea83dbaeb.png", "title": "File 61ecf72c 6600 4498 b870 bafea83dbaeb"}, {"file": "file_75ada3be-ce68-4085-b2f5-e63127b0e7f3.png", "title": "File 75ada3be ce68 4085 b2f5 e63127b0e7f3"}, {"file": "file_abe23697-af9c-495f-84cb-45a3f5854d86.png", "title": "File abe23697 af9c 495f 84cb 45a3f5854d86"}, {"file": "file_af55ffa6-0b76-4ab1-a6ac-95566b92f59c.png", "title": "File af55ffa6 0b76 4ab1 a6ac 95566b92f59c"}]}, {"name": "luxury-trash", "folder": "media/gallery/locator/luxury-trash/", "images": [{"file": "LuxTrashMap1.png", "title": "LuxTrashMap1"}, {"file": "LuxTrashMap1_Underground.png", "title": "LuxTrashMap1 Underground"}, {"file": "LuxTrashMap_2.png", "title": "LuxTrashMap 2"}, {"file": "LuxuryTrashMap2.png", "title": "LuxuryTrashMap2"}, {"file": "LuxuryTrashMap3.png", "title": "LuxuryTrashMap3"}, {"file": "LuxuryTrashMap4.png", "title": "LuxuryTrashMap4"}], "folders": [{"name": "pics", "folder": "media/gallery/locator/luxury-trash/pics/", "images": [{"file": "image_000.png", "title": "Image 000"}, {"file": "image_001.png", "title": "Image 001"}, {"file": "image_002.png", "title": "Image 002"}, {"file": "image_003.png", "title": "Image 003"}, {"file": "image_004.png", "title": "Image 004"}, {"file": "image_005.png", "title": "Image 005"}, {"file": "image_006.png", "title": "Image 006"}, {"file": "image_007.png", "title": "Image 007"}, {"file": "image_008.png", "title": "Image 008"}, {"file": "image_009.png", "title": "Image 009"}, {"file": "image_010.png", "title": "Image 010"}, {"file": "image_011.png", "title": "Image 011"}, {"file": "image_012.png", "title": "Image 012"}, {"file": "image_013.png", "title": "Image 013"}, {"file": "image_014.png", "title": "Image 014"}, {"file": "image_015.png", "title": "Image 015"}, {"file": "image_016.png", "title": "Image 016"}, {"file": "image_017.png", "title": "Image 017"}]}]}, {"name": "retrocubic-nexus", "folder": "media/gallery/locator/retrocubic-nexus/", "images": [{"file": "RetrocubicMap_1.png", "title": "RetrocubicMap 1"}], "folders": [{"name": "pics", "folder": "media/gallery/locator/retrocubic-nexus/pics/", "images": [{"file": "image_000.png", "title": "Image 000"}, {"file": "image_001.png", "title": "Image 001"}, {"file": "image_002.png", "title": "Image 002"}, {"file": "image_003.png", "title": "Image 003"}, {"file": "image_004.png", "title": "Image 004"}, {"file": "image_005.png", "title": "Image 005"}, {"file": "image_006.png", "title": "Image 006"}, {"file": "image_007.png", "title": "Image 007"}, {"file": "image_008.png", "title": "Image 008"}, {"file": "image_009.png", "title": "Image 009"}, {"file": "image_010.png", "title": "Image 010"}, {"file": "image_011.png", "title": "Image 011"}, {"file": "image_012.png", "title": "Image 012"}, {"file": "image_013.png", "title": "Image 013"}, {"file": "image_014.png", "title": "Image 014"}, {"file": "image_015.png", "title": "Image 015"}, {"file": "image_016.png", "title": "Image 016"}]}]}, {"name": "snowfall-city", "folder": "media/gallery/locator/snowfall-city/", "images": [{"file": "SnowfallCity_map1.png", "title": "SnowfallCity map1"}, {"file": "SnowfallCity_map2.png", "title": "SnowfallCity map2"}], "folders": [{"name": "pics", "folder": "media/gallery/locator/snowfall-city/pics/", "images": [{"file": "image_000.png", "title": "Image 000"}, {"file": "image_001.png", "title": "Image 001"}, {"file": "image_002.png", "title": "Image 002"}, {"file": "image_003.png", "title": "Image 003"}, {"file": "image_004.png", "title": "Image 004"}, {"file": "image_005.png", "title": "Image 005"}, {"file": "image_006.png", "title": "Image 006"}, {"file": "image_007.png", "title": "Image 007"}, {"file": "image_008.png", "title": "Image 008"}, {"file": "image_009.png", "title": "Image 009"}, {"file": "image_010.png", "title": "Image 010"}, {"file": "image_011.png", "title": "Image 011"}, {"file": "image_012.png", "title": "Image 012"}, {"file": "image_013.png", "title": "Image 013"}, {"file": "image_014.png", "title": "Image 014"}, {"file": "image_015.png", "title": "Image 015"}, {"file": "image_016.png", "title": "Image 016"}, {"file": "image_017.png", "title": "Image 017"}, {"file": "image_018.png", "title": "Image 018"}, {"file": "image_019.png", "title": "Image 019"}, {"file": "image_020.png", "title": "Image 020"}, {"file": "image_021.png", "title": "Image 021"}, {"file": "image_022.png", "title": "Image 022"}, {"file": "image_023.png", "title": "Image 023"}, {"file": "image_024.png", "title": "Image 024"}, {"file": "image_025.png", "title": "Image 025"}, {"file": "image_026.png", "title": "Image 026"}, {"file": "image_027.png", "title": "Image 027"}, {"file": "image_028.png", "title": "Image 028"}]}]}, {"name": "the-lost-fih", "folder": "media/gallery/locator/the-lost-fih/", "images": [{"file": "LostFih_map1.png", "title": "LostFih map1"}], "folders": [{"name": "pics", "folder": "media/gallery/locator/the-lost-fih/pics/", "images": [{"file": "image_000.png", "title": "Image 000"}, {"file": "image_001.png", "title": "Image 001"}, {"file": "image_002.png", "title": "Image 002"}, {"file": "image_003.png", "title": "Image 003"}, {"file": "image_004.png", "title": "Image 004"}, {"file": "image_005.png", "title": "Image 005"}, {"file": "image_006.png", "title": "Image 006"}, {"file": "image_007.png", "title": "Image 007"}, {"file": "image_008.png", "title": "Image 008"}, {"file": "image_009.png", "title": "Image 009"}, {"file": "image_010.png", "title": "Image 010"}]}]}, {"name": "yes", "folder": "media/gallery/locator/yes/", "images": [{"file": "YES_map1.png", "title": "YES map1"}], "folders": [{"name": "pics", "folder": "media/gallery/locator/yes/pics/", "images": [{"file": "image_000.png", "title": "Image 000"}, {"file": "image_001.png", "title": "Image 001"}, {"file": "image_002.png", "title": "Image 002"}, {"file": "image_003.png", "title": "Image 003"}, {"file": "image_004.png", "title": "Image 004"}, {"file": "image_005.png", "title": "Image 005"}, {"file": "image_006.png", "title": "Image 006"}, {"file": "image_007.png", "title": "Image 007"}, {"file": "image_008.png", "title": "Image 008"}, {"file": "image_009.png", "title": "Image 009"}, {"file": "image_010.png", "title": "Image 010"}, {"file": "image_011.png", "title": "Image 011"}, {"file": "image_012.png", "title": "Image 012"}, {"file": "image_013.png", "title": "Image 013"}, {"file": "image_014.png", "title": "Image 014"}, {"file": "image_015.png", "title": "Image 015"}, {"file": "image_016.png", "title": "Image 016"}, {"file": "image_017.png", "title": "Image 017"}, {"file": "image_018.png", "title": "Image 018"}, {"file": "image_019.png", "title": "Image 019"}, {"file": "image_020.png", "title": "Image 020"}, {"file": "image_021.png", "title": "Image 021"}, {"file": "image_022.png", "title": "Image 022"}]}]}]}]/*AUTO-GALLERY-END*/)}
  ]}
];

const el=(t,c)=>{const e=document.createElement(t);if(c)e.className=c;return e},
      desk=document.getElementById('desk'),box=document.getElementById('icons'),wins={};
let z=10,count=0;
/* the Console program: one line per thing you do ("Click -> 'Gallery'", "Opening -> 'Gallery'", "Viewing -> 'a.png'") */
const CLOGS=[],CSINK=[];
function LOG(kind,what){const line=kind+' -> '+what;CLOGS.push(line);if(CLOGS.length>200)CLOGS.shift();CSINK.forEach(f=>f(line))}
const Q=t=>"'"+t+"'";
document.addEventListener('click',e=>{const t=e.target;if(!t||!t.closest||t.closest('.cpage,.cclear'))return;
  const x=t.closest('button,a,input,select,.th,.tab,.icon,.cell'),nm=x&&((x.getAttribute('aria-label')||x.title||x.innerText||(x.querySelector&&x.querySelector('img')&&x.querySelector('img').alt)||x.value||'').trim().replace(/\s+/g,' ').slice(0,40));
  LOG('Click',nm?Q(nm):'position '+Math.round(e.clientX)+', '+Math.round(e.clientY))},true);

/* tab templates */
const TEMPLATES={
  console:(t,x)=>{x.view.classList.add('flush');
    const d=el('div','cpage'),clr=el('button','btn cclear');clr.type='button';clr.textContent='Clear';
    const add=l=>{if(!d.isConnected){const i=CSINK.indexOf(add);if(i>=0)CSINK.splice(i,1);return}
      const stick=d.scrollHeight-d.scrollTop-d.clientHeight<24,r=el('div');r.textContent=l;d.appendChild(r);while(d.children.length>200)d.firstChild.remove();if(stick)d.scrollTop=d.scrollHeight};
    clr.onclick=()=>{d.replaceChildren();CLOGS.length=0};x.ex.appendChild(clr);
    CLOGS.forEach(l=>{const r=el('div');r.textContent=l;d.appendChild(r)});CSINK.push(add);setTimeout(()=>{d.scrollTop=d.scrollHeight},0);return d},
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
    /* gallery-size.txt is written by the gallery manager (one line: "Gallery size: 812.4 MB") */
    if(x.st)x.st.classList.add('gsize');let gsz='';fetch('gallery-size.txt',{cache:'no-cache'}).then(r=>r.ok?r.text():'').then(t=>{t=(t||'').trim();if(/^Gallery size:/.test(t)){gsz=t;if(x.st)x.st.textContent=t}}).catch(()=>{});
    const node=()=>path[path.length-1],cls=()=>'gal'+(path.some(n=>n.pixelated)?' px':'');
    const up=()=>{if(path.length>1){LOG('Closing folder',Q(node().name));path.pop();show()}};
    const show=()=>{cur=-1;const n=node(),subs=n.folders||[],imgs=(n.images||[]).map(norm);d.className=cls();d.innerHTML='';
      const bar=el('div','gbar'),crumb=el('span','gcrumb');
      if(path.length>1){const b=el('button','btn');b.type='button';b.textContent='Back';b.onclick=up;bar.appendChild(b)}
      crumb.textContent=path.map(p=>p.name).join(' / ');bar.appendChild(crumb);d.appendChild(bar);
      if(!subs.length&&!imgs.length){const p=el('p','empty');p.textContent='Empty :(';d.appendChild(p);d.focus();return}
      const g=el('div','gg');
      subs.forEach(f=>{const b=el('button','th fd'),im=el('img'),lb=el('span');b.type='button';b.title=f.name;im.src=MEDIA[f.icon||'folder'];im.alt='';lb.textContent=f.name;
        b.append(im,lb);b.onclick=()=>{LOG('Opening folder',Q(f.name));path.push(f);show()};g.appendChild(b)});
      imgs.forEach((it,i)=>{const b=el('button','th'),im=el('img');b.type='button';b.title=it.title||it.file;im.src=src(n,it.file);im.alt=it.title||it.file;im.loading='lazy';
        im.onerror=()=>{b.classList.add('miss');b.textContent=it.file};b.appendChild(im);b.onclick=()=>open(i);g.appendChild(b)});
      d.appendChild(g);d.focus()};
    /* downscaled download: the browser shrinks the picture so its longest side is N px (never enlarges) */
    const SIZES=[2048,1024,512,256];
    const resizeDl=(url,N,name)=>{const i=new Image();i.onload=()=>{const w=i.naturalWidth||N,h=i.naturalHeight||N,k=Math.min(1,N/Math.max(w,h)),cw=Math.max(1,Math.round(w*k)),ch=Math.max(1,Math.round(h*k)),c=document.createElement('canvas');
      c.width=cw;c.height=ch;const g=c.getContext('2d');g.imageSmoothingEnabled=true;g.imageSmoothingQuality='high';g.drawImage(i,0,0,cw,ch);
      const ext=(name.match(/\.([^.]+)$/)||[0,'png'])[1].toLowerCase(),jpg=/^jpe?g$/.test(ext),webp=ext==='webp',type=jpg?'image/jpeg':webp?'image/webp':'image/png',
        out=name.replace(/\.[^.]+$/,'')+'_'+N+(jpg?'.jpg':webp?'.webp':'.png');
      c.toBlob(bl=>{if(!bl)return;const u=URL.createObjectURL(bl),a=document.createElement('a');a.href=u;a.download=out;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),4000)},type,.92)};i.src=url};
    const open=i=>{const n=node(),list=(n.images||[]).map(norm);cur=(i+list.length)%list.length;const it=list[cur];LOG('Viewing',Q((MEDIA[it.file]||it.file).split('/').pop()));d.className=cls()+' gv';d.innerHTML='';
      const bar=el('div','gbar'),back=el('button','btn'),pv=el('button','btn'),nx=el('button','btn'),c=el('span','gn'),im=el('img','big'),cap=el('div','gcap');
      back.type=pv.type=nx.type='button';back.textContent='Back';pv.textContent='<';nx.textContent='>';pv.setAttribute('aria-label','Previous');nx.setAttribute('aria-label','Next');
      c.textContent=(cur+1)+' / '+list.length;const closeView=()=>{LOG('Closing',Q((MEDIA[it.file]||it.file).split('/').pop()));show()};back.onclick=closeView;pv.onclick=()=>open(cur-1);nx.onclick=()=>open(cur+1);
      im.src=src(n,it.file);im.alt=it.title||it.file;im.onerror=()=>{cap.textContent='Could not load '+it.file+'. Check the file name and folder.'};
      cap.textContent=it.title||'';const dim=el('span','gdim');cap.append(dim);im.addEventListener('load',()=>{if(im.naturalWidth)dim.textContent=(it.title?'  \u00b7  ':'')+im.naturalWidth+' \u00d7 '+im.naturalHeight+' px'});bar.append(back,pv,nx,c);
      /* direct download + copyable link for this picture (e.g. to load it in other programs) */
      const url=new URL(src(n,it.file),location.href).href,dl=el('div','gdl'),a=el('a','btn'),row=el('div','gcopy'),inp=el('input'),cp=el('button','btn');
      a.href=url;a.download=url.split('/').pop().split('?')[0];a.textContent='Download';
      inp.readOnly=true;inp.value=url;inp.setAttribute('aria-label','Direct link to this picture');inp.onclick=()=>inp.select();
      /* size chooser (like Unity's Max Size): the resized copies made by the gallery manager, if any */
      const szs=(!MEDIA[it.file]&&it.sizes)||[],pick=el('select');
      if(szs.length){const o=el('option');o.value='';o.textContent='Original';pick.append(o);
        szs.forEach(N=>{const o=el('option'),f=it.file,ext=(f.match(/\.[^.]+$/)||[''])[0].toLowerCase(),nm=/^\.(png|jpe?g|webp)$/.test(ext)?f:f+'.png';o.value=new URL((n.folder||'')+'size-copies/'+N+'/'+nm,location.href).href;o.textContent=N+' px';pick.append(o)});
        pick.setAttribute('aria-label','Choose the size of the linked picture');pick.onchange=()=>{inp.value=pick.value||url};}
      cp.type='button';cp.textContent='Copy link';
      cp.onclick=()=>{const ok=()=>{cp.textContent='Copied!';setTimeout(()=>cp.textContent='Copy link',1500)};
        inp.select();if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(inp.value).then(ok,()=>{document.execCommand('copy');ok()});else{document.execCommand('copy');ok()}};
      if(szs.length)row.append(pick);row.append(inp,cp);
      const top=el('div','gdr'),lab=el('span','glab'),fname=a.download,sb=SIZES.map(N=>{const b=el('button','btn');b.type='button';b.textContent=N;b.title='Download resized: longest side '+N+' px';b.onclick=()=>resizeDl(url,N,fname);return b});
      lab.textContent='Resized:';top.append(a,lab,...sb);
      im.addEventListener('load',()=>{const m=Math.max(im.naturalWidth,im.naturalHeight);sb.forEach((b,j)=>{if(m&&m<=SIZES[j]){b.disabled=true;b.title='This picture is already '+m+' px or smaller'}})});
      dl.append(top,row);d.append(bar,im,cap,dl);d.focus()};
    d.onkeydown=e=>{const k=e.key;
      if(cur>=0){if(k==='ArrowLeft')open(cur-1);else if(k==='ArrowRight')open(cur+1);else if(k==='Escape'){e.stopPropagation();const im0=(node().images||[])[cur],f0=im0&&(typeof im0==='string'?im0:im0.file);if(f0)LOG('Closing',Q((MEDIA[f0]||f0).split('/').pop()));show()}else return}
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
const ROW=142,COL=124;
const REMEMBER=false; /* true = each visitor's dragged icon positions are remembered; false = icons return to your pos:[x,y] formation every time the site opens */
let saved={};if(REMEMBER){try{saved=JSON.parse(localStorage.getItem('dorito-icons-2')||'{}')}catch(e){}}
const rows=Math.max(1,Math.floor((innerHeight-24)/ROW));
APPS.forEach((a,i)=>{
  const c=el('div','cell'),b=el('button','icon');b.type='button';b.innerHTML='<img alt=""><span></span>';
  b.firstChild.src=MEDIA[a.icon];b.lastChild.textContent=a.label||a.title;c.appendChild(b);
  const place=(x,y)=>{c.style.left=Math.max(0,Math.min(innerWidth-104,x))+'px';c.style.top=Math.max(0,Math.min(innerHeight-122,y))+'px'};
  const p=saved[a.id]||(a.pos&&innerWidth>=700?{x:a.pos[0]*innerWidth,y:a.pos[1]*innerHeight}:{x:12+Math.floor(i/rows)*COL,y:18+(i%rows)*ROW});place(p.x,p.y);
  let last=0;
  c.addEventListener('pointerdown',e=>{
    const sx=e.clientX,sy=e.clientY,ox=c.offsetLeft,oy=c.offsetTop;let moved=false;c.setPointerCapture(e.pointerId);
    const mv=v=>{if(!moved&&Math.hypot(v.clientX-sx,v.clientY-sy)<6)return;moved=true;c.classList.add('drag');place(ox+v.clientX-sx,oy+v.clientY-sy)};
    const up=()=>{c.removeEventListener('pointermove',mv);c.removeEventListener('pointerup',up);c.removeEventListener('pointercancel',up);c.classList.remove('drag');
      if(moved){if(REMEMBER){saved[a.id]={x:c.offsetLeft,y:c.offsetTop};try{localStorage.setItem('dorito-icons-2',JSON.stringify(saved))}catch(e){}}return}
      const n=Date.now();if(n-last<450||matchMedia('(pointer:coarse)').matches)launch(a);last=n};
    c.addEventListener('pointermove',mv);c.addEventListener('pointerup',up);c.addEventListener('pointercancel',up)});
  b.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();launch(a)}};
  box.appendChild(c);
});

function front(w){document.querySelectorAll('.win').forEach(x=>x.classList.remove('top'));w.classList.add('top');w.style.zIndex=++z}

function launch(a){
  if(wins[a.id]){LOG('Focus',Q(a.title));front(wins[a.id]);return}
  LOG('Opening',Q(a.title));
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
  if(a.wpos&&innerWidth>=700){const ww=w.offsetWidth,wh=w.offsetHeight;w.style.left=Math.max(6,Math.min(innerWidth-ww-6,a.wpos[0]*innerWidth-ww))+'px';w.style.top=Math.max(6,Math.min(innerHeight-wh-6,a.wpos[1]*innerHeight))+'px'}
  front(w);w.addEventListener('pointerdown',()=>front(w));
  let timer;const ctx={w,view:$('.view'),ex:$('.ex'),st};
  /* scale the window's contents with the window (set once you start resizing) */
  const fit=()=>{const c=pg.firstElementChild;if(!c||c.classList.contains('media')||!w._base)return;
    const v=ctx.view;c.style.zoom=Math.max(.35,Math.min(6,Math.min(v.clientWidth/w._base.w,v.clientHeight/w._base.h)))};
  new ResizeObserver(fit).observe(ctx.view);
  const show=t=>{clearTimeout(timer);ctx.view.classList.remove('flush','galv');ctx.view.style.minHeight='';ctx.ex.replaceChildren();load.classList.remove('on');void load.offsetWidth;load.classList.add('on');pg.innerHTML='';$('.view').scrollTop=0;st.textContent='Loading '+t.label+'\u2026';
    timer=setTimeout(()=>{load.classList.remove('on');st.textContent='';st.classList.remove('gsize');pg.appendChild((TEMPLATES[t.template||'html']||TEMPLATES.html)(t,ctx));fit()},820)};
  if(a.tabs.length>1)a.tabs.forEach((t,i)=>{const b=el('button','tab');b.type='button';b.role='tab';b.textContent=t.label;b.setAttribute('aria-selected',i===0);
    b.onclick=()=>{[...tabsEl.children].forEach(c=>c.setAttribute('aria-selected',c===b));LOG('Tab',Q(t.label));show(t)};tabsEl.appendChild(b)});
  if(a.fw&&innerWidth>=700){ /* open big: measure the normal size first so the content can scale up from it */
    pg.appendChild((TEMPLATES[a.tabs[0].template||'html']||TEMPLATES.html)(a.tabs[0],ctx));
    w._base={w:ctx.view.clientWidth,h:ctx.view.clientHeight};pg.innerHTML='';
    const BW=Math.min(innerWidth-12,Math.round(a.fw*innerWidth)),BH=Math.min(innerHeight-12,Math.round((a.fh||a.fw)*innerHeight));
    w.style.width=BW+'px';w.style.height=BH+'px';w.style.left=Math.round((innerWidth-BW)/2)+'px';w.style.top=Math.round((innerHeight-BH)/2)+'px';w._user=1;w.classList.add('sized')}
  show(a.tabs[0]);
  $('.x').onclick=()=>{LOG('Closing',Q(a.title));clearTimeout(timer);w.remove();delete wins[a.id]};
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
