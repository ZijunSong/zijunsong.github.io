(()=>{
const $=(s)=>document.querySelector(s);
try{if(localStorage.getItem('zs-theme')==='dark'||(!localStorage.getItem('zs-theme')&&matchMedia('(prefers-color-scheme: dark)').matches))document.body.classList.add('dark')}catch{}
const theme=$('.theme-switch');function themeLabel(){theme?.setAttribute('aria-label',document.body.classList.contains('dark')?'Switch to light mode':'Switch to dark mode')}themeLabel();theme?.addEventListener('click',()=>{document.body.classList.toggle('dark');try{localStorage.setItem('zs-theme',document.body.classList.contains('dark')?'dark':'light')}catch{}themeLabel()});
const search=$('#search'),cards=[...document.querySelectorAll('.note-card')];let selected='All';function filter(){const q=(search?.value||'').trim().toLocaleLowerCase();let count=0;for(const card of cards){const visible=(selected==='All'||card.dataset.tags.split(' ').includes(selected))&&card.dataset.search.toLocaleLowerCase().includes(q);card.hidden=!visible;if(visible)count++}if($('.no-results'))$('.no-results').hidden=count>0;if($('.section-count'))$('.section-count').textContent=' / '+String(count).padStart(2,'0')}
search?.addEventListener('input',filter);document.querySelectorAll('[data-filter]').forEach(b=>b.addEventListener('click',()=>{selected=b.dataset.filter;document.querySelectorAll('[data-filter]').forEach(t=>t.setAttribute('aria-pressed',String(t===b)));filter()}));document.addEventListener('keydown',e=>{if(e.key==='/'&&search&&!['INPUT','TEXTAREA'].includes(document.activeElement.tagName)){e.preventDefault();search.focus()}});
async function copy(text,button){try{await navigator.clipboard.writeText(text);const old=button.textContent;button.textContent='Copied ✓';setTimeout(()=>button.textContent=old,1800)}catch{button.textContent='Select and copy manually'}}document.querySelectorAll('.copy-code').forEach(b=>b.addEventListener('click',()=>copy(b.closest('.code-wrap').querySelector('pre code').textContent,b)));$('.copy-citation')?.addEventListener('click',()=>copy($('#citation').textContent,$('.copy-citation')));
const progress=$('.reading-progress');if($('.article-main')){function update(){const h=document.documentElement.scrollHeight-innerHeight;progress.style.width=(h>0?scrollY/h*100:0)+'%'}addEventListener('scroll',update,{passive:true});update();if('IntersectionObserver'in window){const observer=new IntersectionObserver(entries=>{for(const entry of entries)if(entry.isIntersecting){document.querySelectorAll('.toc a').forEach(a=>a.classList.toggle('active',a.getAttribute('href')==='#'+entry.target.id))}},{rootMargin:'-10% 0px -70% 0px'});document.querySelectorAll('.prose h2').forEach(h=>observer.observe(h))}}
const likeBox=$('.like-box');
if(likeBox){
  const key=likeBox.dataset.likeKey;
  const button=likeBox.querySelector('.like-button');
  const countEl=likeBox.querySelector('.like-count');
  const status=likeBox.querySelector('.like-status');
  const storeKey='zs-liked-'+key;
  const namespace='zijunsong.github.io';
  const endpoint='https://abacus.jasoncameron.dev';
  const liked=()=>{try{return localStorage.getItem(storeKey)==='1'}catch{return false}};
  const setLiked=()=>{try{localStorage.setItem(storeKey,'1')}catch{}};
  const setCount=n=>{countEl.textContent=String(Math.max(0,Number(n)||0))};
  const setPressed=on=>{button.setAttribute('aria-pressed',String(on));button.classList.toggle('is-liked',on)};
  async function readCount(){
    try{
      const res=await fetch(endpoint+'/get/'+namespace+'/like-'+key);
      if(res.status===404){setCount(0);return 0}
      if(!res.ok)throw new Error('read failed');
      const data=await res.json();
      setCount(data.value);return data.value
    }catch{status.textContent='Like count is temporarily unavailable.';return null}
  }
  async function sendLike(){
    if(liked()||button.disabled)return;
    button.disabled=true;
    const prev=Number(countEl.textContent)||0;
    setCount(prev+1);setPressed(true);
    try{
      const res=await fetch(endpoint+'/hit/'+namespace+'/like-'+key);
      if(!res.ok)throw new Error('hit failed');
      const data=await res.json();
      setCount(data.value);setLiked();
      status.textContent='Thanks for the like.';
    }catch{
      setCount(prev);setPressed(false);
      status.textContent='Could not save the like. Please try again later.';
    }finally{button.disabled=false}
  }
  setPressed(liked());
  readCount().then(()=>{if(liked())status.textContent='You already liked this note.'});
  button.addEventListener('click',sendLike);
}
})();
