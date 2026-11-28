// Ajuste la taille de police de [data-fit] pour que le texte fasse exactement la largeur cible (mm),
// puis applique les rapports [data-rel] (taille relative à l'élément de référence).
(function(){
  const f=new URLSearchParams(location.search).get('f')||'bodoni';
  document.documentElement.className='f-'+f;
  const MM=96/25.4;
  document.fonts.ready.then(()=>{
    document.querySelectorAll('[data-fit]').forEach(el=>{
      el.style.fontSize='100px'; el.style.whiteSpace='nowrap'; el.style.display='inline-block';
      const w=el.getBoundingClientRect().width; el.style.fontSize=(100*parseFloat(el.dataset.fit)*MM/w)+'px';
    });
    document.querySelectorAll('[data-rel]').forEach(el=>{
      const [id,r]=el.dataset.rel.split(':'); const ref=document.getElementById(id);
      el.style.fontSize=(parseFloat(getComputedStyle(ref).fontSize)*parseFloat(r))+'px';
    });
    // [data-maxw] : si le contenu déborde, réduit proportionnellement les tailles des descendants
    document.querySelectorAll('[data-maxw]').forEach(box=>{
      const max=parseFloat(box.dataset.maxw)*MM; const kids=[...box.querySelectorAll('[data-rel]')];
      for(let i=0;i<40 && box.scrollWidth>max;i++) kids.forEach(k=>k.style.fontSize=(parseFloat(k.style.fontSize)*.97)+'px');
    });
    document.body.dataset.ready='1';
  });
})();
