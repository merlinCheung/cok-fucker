const $ = id => document.getElementById(id);
const TOKEN = (new URLSearchParams(location.search).get('t')) || localStorage.getItem('cokToken') || '';
if (TOKEN) localStorage.setItem('cokToken', TOKEN);
const S = {state:null, lastEvents:0, busy:false};
/* 平台模式: 登录用户(后端 /api/me 给)。null = 还没问到 / 单用户模式 */
let ME = null;
/* 事件区筛选: 默认全部, 可只看异常/警告/连接/状态 */
let EV_FILTER='all', EV_SIG='';

/* ---------------- 工具 ---------------- */
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function clean(s){return String(s==null?'':s).replace(/\{\d+\}/g,'?');}
/* 千分位: 大数字(金币/兵力/进度)读起来舒服很多 */
function fmt(n){
  if(n==null||n==='') return '-';
  const v=Number(n);
  if(!isFinite(v)) return String(n);
  return Math.abs(v)>=1000 ? v.toLocaleString('zh-CN') : String(v);
}
function dur(ms){ if(!ms) return '-'; if(ms<60000) return Math.max(0,Math.round(ms/1000))+' 秒';
  const m=Math.round(ms/60000); if(m<60) return m+' 分'; return Math.floor(m/60)+' 时 '+(m%60)+' 分'; }
function ts(v){ if(!v) return '-'; const n=Number(v); if(!isFinite(n)||n<1e11) return String(v);
  const d=new Date(n+8*3600*1000), p=x=>String(x).padStart(2,'0');
  return d.getUTCFullYear()+'-'+p(d.getUTCMonth()+1)+'-'+p(d.getUTCDate())+' '+p(d.getUTCHours())+':'+p(d.getUTCMinutes()); }
function hhmmss(t){ if(!t) return '-'; const d=new Date(t*1000), p=x=>String(x).padStart(2,'0');
  return p(d.getHours())+':'+p(d.getMinutes())+':'+p(d.getSeconds()); }
function ago(t){ if(!t) return '-'; const s=Math.max(0,Date.now()/1000-t); if(s<60) return Math.round(s)+' 秒前';
  if(s<3600) return Math.round(s/60)+' 分钟前'; if(s<86400) return Math.round(s/3600)+' 小时前'; return Math.round(s/86400)+' 天前'; }

let toastTimer=null;
function toast(msg, kind){
  const t=$('toast'); t.className='toast on'+(kind?' '+kind:''); t.innerHTML=esc(msg);
  clearTimeout(toastTimer); toastTimer=setTimeout(()=>{t.className='toast'+(kind?' '+kind:'');},3800);
}

/* 持久化的操作结果: 每个区域都记住上次结果, 刷新页面也还在 */
function setRes(id, msg, kind){
  const el=$(id); if(!el) return;
  el.className='res'+(kind?' '+kind:'');
  el.innerHTML='<span class="t">'+hhmmss(Date.now()/1000)+'</span>'+esc(msg);
}
function loadRes(id, msg, kind){
  const el=$(id); if(!el) return;
  el.className='res'+(kind?' '+kind:'');
  el.innerHTML='<span class="t">'+esc(msg.ts||'')+'</span>'+esc(msg.text||'');
}

/* ---------------- 设置持久化(存后端, 刷新/换浏览器都不丢) ---------------- */
let SETTINGS = {};
let SET_SEQ = 0;               // 写入序号: 挡掉并发 POST 的乱序覆盖
const SET_DEBOUNCE = 350;      // 文本框输入防抖(ms)
const SET_FIELDS = [
  ['autoSign','chkAutoSign'],['autoShield','chkAutoShield'],['cover','chkCover'],
  ['autoPoll','chkAuto'],['hookType','selHookType'],['hookURL','inpHook'],
  ['kickReconnectPolicy','selKickPolicy'],['kickReconnectMinutes','inpKickMin'],
  ['lvLow','inpLvLow'],['lvHigh','inpLvHigh'],
  ['perType','inpPerType'],['squads','inpSquads'],['huntMax','inpHuntMax'],
  ['huntMix','inpHuntMix'],['huntAutoStamina','chkHuntAutoStamina'],
  ['dockAutoReward','chkDockAutoReward'],['dockAutoSend','chkDockAutoSend'],
  ['autoWelfare','chkAutoWelfare'],
  ['skyAutoReward','chkSkyAutoReward'],['skyAutoExplore','chkSkyAutoExplore'],
  ['scoreAutoClaim','chkScoreAutoClaim'],
  ['allianceDonate','chkAllianceDonate'],
  ['allianceDonateTier','selAllianceTier'],
  ['allianceDonateMax','inpAllianceMax'],
  ['allianceSignIn','chkAllianceSignIn'],
  ['assistAuto','chkAssistAuto'],
  ['assistAutoCostly','chkAssistCostly'],
];
async function saveSetting(k,v){
  SETTINGS[k]=v;
  try{
    const r=await api('/api/action',{action:'set-setting',key:k,value:v,seq:++SET_SEQ});
    // 服务端会把等级范围归一化(下限<=上限), 把归一化后的值同步回输入框
    if(r && r.ok && r.settings){
      for(const [kk,id] of [['lvLow','inpLvLow'],['lvHigh','inpLvHigh']]){
        const nv=r.settings[kk];
        if(nv!==undefined && nv!==null && String(nv)!==String(SETTINGS[kk])){
          SETTINGS[kk]=nv;
          const el=$(id); if(el && document.activeElement!==el) el.value=nv;
        }
      }
    }
  }catch(e){ toast('设置保存失败: '+k,'err'); }
}
function applySettings(){
  for(const [k,id] of SET_FIELDS){
    const el=$(id); if(!el) continue;
    if(el.type==='checkbox'){ if(k in SETTINGS) el.checked=!!SETTINGS[k]; }
    else { if(SETTINGS[k]!==undefined && SETTINGS[k]!==null) el.value=SETTINGS[k]; }
  }
  syncKickPolicyUI();
  renderSquadPresetSelect(null);
  renderSquadRows();
}
/* 退避分钟输入只在「退避重试」策略下有意义: 其余策略藏掉, 免得误导。 */
function syncKickPolicyUI(){
  const sel=$('selKickPolicy'), wrap=$('kickMinWrap');
  if(!sel||!wrap) return;
  wrap.style.display=(sel.value==='backoff')?'':'none';
}
function bindSettings(){
  for(const [k,id] of SET_FIELDS){
    const el=$(id); if(!el) continue;
    const instant=(el.type==='checkbox'||el.tagName==='SELECT');
    let timer=null;
    const fire=()=>saveSetting(k, el.type==='checkbox'?el.checked:el.value);
    if(instant){
      el.addEventListener('change', fire);
    }else{
      // 文本/数字输入: 防抖后再存, 避免每个按键都打一次后端
      el.addEventListener('input', ()=>{
        clearTimeout(timer);
        timer=setTimeout(fire, SET_DEBOUNCE);
      });
      el.addEventListener('change', ()=>{ clearTimeout(timer); fire(); });
    }
  }
}

/* ---------------- API ---------------- */
async function api(path, body){
  const opt={headers:{'Content-Type':'application/json'}, credentials:'same-origin'};
  if(body){ opt.method='POST'; opt.body=JSON.stringify(body); }
  const sep=path.includes('?')?'&':'?';
  const url=path+(TOKEN?sep+'t='+encodeURIComponent(TOKEN):'');
  const r=await fetch(url,opt);
  if(r.status===401||r.status===403){
    // 会话过期 / 未登录: 回登录页(带上原因, 登录页会显示)
    const j=await r.json().catch(()=>({}));
    if(j.error==='unauthorized'||j.error==='banned'){
      const reason = j.error==='banned' ? 'banned' : 'expired';
      location.replace('/login?reason='+reason);
      return {ok:false, error:'未登录'};
    }
  }
  const j=await r.json().catch(()=>({ok:false,error:'HTTP '+r.status}));
  if(j.error==='unauthorized'){ $('connText').textContent='token 无效'; }
  return j;
}

/* 统一按钮交互: 禁用 + spinner + 完成恢复
   异常必须被吃掉并变成可见反馈 —— 否则点了没反应, 用户只能猜 */
async function busy(btn, label, fn){
  if(btn) btn.disabled=true;
  const old=btn?btn.innerHTML:'';
  if(btn) btn.innerHTML='<span class="spin"></span>'+esc(label||'处理中');
  try{ return await fn(); }
  catch(e){
    const msg=(e&&e.message)?e.message:String(e);
    toast('操作失败: '+msg,'err');
    return {ok:false, error:msg};
  }
  finally{ if(btn){ btn.disabled=false; btn.innerHTML=old; } }
}

let NAMES={queue_types:{},overview_types:{},items:{},rewards:{}};
function qtype(v){const n=NAMES.queue_types[String(v)];return n||('类型'+v);}
function otype(v){const n=NAMES.overview_types[String(v)];return n||('类型'+v);}
function kv(k,v){return `<div class="kv"><span class="k">${esc(k)}</span><span class="v">${v}</span></div>`;}
function tags(list,cls){return (list||[]).map(x=>`<span class="tag ${cls||''}">${esc(x)}</span>`).join('')||'<span class="dim">-</span>';}
/* 可点击直达的标签: 点一下跳到能处理它的卡片 */
function jumpTags(list,cls,target){
  const base=tagsId(list,cls);
  if(!list||!list.length) return base;
  return base.replace(/<span /g,'<span data-jump="'+esc(target)+'" style="cursor:pointer" ');
}
document.addEventListener('click',(e)=>{
  const j=e.target.closest && e.target.closest('[data-jump]');
  if(j){ goTo(j.dataset.jump); return; }
});
function tagsId(list,cls){
  return (list||[]).map(x=>{
    if(x&&typeof x==='object'){ const nm=clean(x.name||x.id);
      return `<span class="tag ${cls||''}" title="${esc(x.id)}">${esc(nm)}</span>`; }
    return `<span class="tag ${cls||''}">${esc(x)}</span>`;
  }).join('')||'<span class="dim">-</span>';
}

/* ---------------- 队伍编成(下拉选兵种, 不用手填 id) ---------------- */
let ARMY_CHOICES = [];      // [{id,name,free,power,...}]
let ARMY_LOADED = false;
let SQUAD_PRESETS = [];     // 11 个编队预设(对齐游戏) [{index,name,spec,empty}]
let SQUAD_PRESET_SEL = '';  // 当前选中的编队号
let FORCE_SPEC=null;        // 强制用这份编成重绘(切编队时用)

function squadPresets(){
  // 从后端给的列表里取; 没有就退回本地缓存
  if(SQUAD_PRESETS && SQUAD_PRESETS.length) return SQUAD_PRESETS;
  try{
    const raw=JSON.parse(SETTINGS.squadPresets||'{}');
    const out=[];
    for(let i=1;i<=11;i++){
      const p=raw[String(i)]||{};
      out.push({index:i, name:p.name||('编队'+i), spec:p.spec||[],
                empty:!(p.spec&&p.spec.length),
                fromGame:!!p.fromGame, fromGameAccount:p.fromGameAccount||''});
    }
    return out;
  }catch(e){ return []; }
}

function renderSquadPresetSelect(st){
  const sel=$('selSquadPreset');
  if(!sel) return;
  if(st && st.squad_presets && st.squad_presets.length){
    SQUAD_PRESETS=st.squad_presets;
  }
  const cur=(st&&st.squad_preset!=null)?String(st.squad_preset):String(SETTINGS.squadPreset||'');
  const opts=squadPresets();
  // 签名要带上编成内容, 否则改了编成(队数没变)不会重绘
  const sig=opts.map(p=>p.index+':'+p.name+':'+(p.empty?'':
      p.spec.map(s=>s.army_id+'x'+s.num).join(','))).join('|')+'#'+cur;
  if(sel.dataset.sig===sig) return;
  sel.dataset.sig=sig;
  // 下拉只列**编队号** —— 不显示兵种/队数(那些在游戏里, 服务端不下发)
  sel.innerHTML='<option value="">不指定</option>'
    +opts.map(p=>'<option value="'+esc(p.index)+'"'+(String(p.index)===cur?' selected':'')+'>'
      +esc(p.name)+'</option>').join('');
  SQUAD_PRESET_SEL=cur;
  renderSquadPresetView(st);
}

function loadSquadPreset(idx){
  // 取某个编队预设的编成(不再往隐藏的手动编排表里塞)
  const p=squadPresets().find(x=>String(x.index)===String(idx));
  if(!p||!p.spec||!p.spec.length) return null;
  return p.spec;
}

// 编成 -> "狮鹫突袭者 ×50 · 天马骑士 ×2500"
function presetSpecText(spec){
  return (spec||[]).map(s=>
    armyLabel({id:s.army_id, name:''})+' ×'+(s.num||0)).join('  ·  ');
}

// 选中编队的说明: **不显示兵种/数量**(那些在游戏里, 服务端不下发)
// 这里只回答两个问题: 选了哪个编队 / 游戏里现在实际在用哪个编队
function renderSquadPresetView(st){
  const box=$('squadPresetView'), hint=$('squadPresetHint');
  if(!box) return;
  const h=(st&&st.hunt)||{};
  const fmt=String(h.format||'');
  const gameIdx=(/^\d+(;\d+)*$/.test(fmt))?fmt:'';
  const sel=String(SQUAD_PRESET_SEL||'');
  if(!sel){
    box.textContent='没选编队 —— 开始打怪时游戏会用你选的那个';
    if(hint) hint.textContent='在上面的下拉里选一个编队(编队1~11), 页面不填兵种和数量';
    return;
  }
  if(gameIdx){
    box.textContent='游戏里现在用 编队'+gameIdx.split(';').join('、')
      +(sel===gameIdx?'(就是你选的)':'');
  }else if(fmt){
    box.textContent='⚠ 游戏里存的编成格式异常(不是编队号), 建议点「用这个编队」修回';
  }else{
    box.textContent='这个号在游戏里还没设过自动打怪编成';
  }
  if(hint) hint.textContent='出征由游戏自己做 —— 兵种和数量都用你在游戏里设好的编队, 页面不填';
}

function squadSpec(){
  // 从 DOM 读当前编成: [{army_id, num}]
  const out=[];
  document.querySelectorAll('#squadRows .sqrow').forEach(row=>{
    const sel=row.querySelector('select'), num=row.querySelector('input');
    if(!sel||!sel.value) return;
    const n=parseInt(num&&num.value||'0',10);
    if(!(n>0)) return;
    out.push({army_id:sel.value, num:n});
  });
  return out;
}

function ensureChoice(id){
  // 游戏里保存的编成可能引用了**我们列表里没有**的兵种 id
  // (实测: 游戏用的 107012=蛮族督军 / 107212=修罗射手, 玩家兵种列表里没有这两种)。
  // 这种 id 也要能在下拉里选出来, 否则会被静默换成第一个选项(编成全错)。
  if(!id) return;
  if(!ARMY_CHOICES.find(a=>a.id===id)){
    ARMY_CHOICES.push({id:id, name:'', free:0, unknown:true});
  }
}

// 兵种显示名: 列表里没有的(游戏预设里的)去中文名表里查
function armyLabel(a){
  if(a.name) return a.name;
  const map=(NAMES&&NAMES.army)||(NAMES&&NAMES.items)||{};
  let nm=(map[a.id]||'').toString();
  nm=nm.replace(/[{}]/g,'').split('|')[0];
  return nm||('兵种 '+a.id);
}

function renderSquadRows(){
  const box=$('squadRows');
  if(!box) return;
  const want=Math.max(1, Math.min(8, parseInt($('inpSquads')&&$('inpSquads').value||'4',10)||4));
  let spec=[];
  try{ spec=JSON.parse(SETTINGS.squadSpec||'[]'); }catch(e){ spec=[]; }
  if(!Array.isArray(spec)) spec=[];
  // 强制指定(切编队时用): 优先于 DOM
  const cur=(FORCE_SPEC&&FORCE_SPEC.length)?FORCE_SPEC:squadSpec();
  if(cur.length) spec=cur;
  FORCE_SPEC=null;
  const opts=(sel)=>{
    if(!ARMY_CHOICES.length) return '<option value="">（还没有兵种数据, 点「刷新兵种」）</option>';
    return ARMY_CHOICES.map(a=>{
      const sel2=(sel===a.id)?' selected':'';
      return '<option value="'+esc(a.id)+'"'+sel2+'>'+esc(armyLabel(a))+' · 可用 '+esc(a.free)+'</option>';
    }).join('');
  };
  let html='';
  for(let i=0;i<want;i++){
    const s=spec[i]||{};
    // 默认按顺序给每队分配兵种(同兵种也可以多队, 判回靠行军 uuid 精确区分)
    const aid=s.army_id||(ARMY_CHOICES[i]?ARMY_CHOICES[i].id:'');
    ensureChoice(aid);
    const ch=(ARMY_CHOICES||[]).find(a=>a.id===aid);
    const free=ch?(ch.free||0):0;
    const numVal=s.num||($('inpPerType')&&$('inpPerType').value||50);
    // 数量超过可用兵数会被**静默截断**, 这里明确提示
    const over=(ch&&free>0&&numVal>free)?('<span class="mini" style="color:#f0d59a">只有 '+esc(free)+'</span>'):'';
    html+='<div class="row sqrow" data-slot="'+(i+1)+'">'
      +'<label style="min-width:auto">队'+(i+1)+'</label>'
      +'<select class="sqid" style="flex:1 1 150px;min-width:130px">'+opts(aid)+'</select>'
      +'<span class="mini">×</span>'
      +'<input class="sqnum" type="number" min="0" value="'+numVal+'" style="width:70px;flex:0 0 70px">'
      +'<span class="mini">兵</span>'+over
      +'</div>';
  }
  box.innerHTML=html;
  const hint=$('armyHint');
  if(hint){
    hint.textContent = ARMY_CHOICES.length
      ? ('可用标准兵种 '+ARMY_CHOICES.length+' 种(只列 107xxx 系列, 活动限定兵种不能混编)')
      : '正在读取可用兵种…';
  }
}

async function loadArmyChoices(){
  const hint=$('armyHint');
  if(hint) hint.textContent='正在读取可用兵种…';
  const r=await api('/api/action',{action:'hunt',op:'army'});
  if(r && r.ok && Array.isArray(r.army)){
    ARMY_CHOICES=r.army;
    ARMY_LOADED=true;
  }else{
    ARMY_CHOICES=[];
  }
  renderSquadRows();
  return ARMY_CHOICES;
}



/* ---------------- 折叠(状态存 localStorage, 跨刷新保留) ---------------- */
const FOLD_KEY='cokFolded';
function foldedIds(){
  try{ return new Set(JSON.parse(localStorage.getItem(FOLD_KEY)||'[]')); }
  catch(e){ return new Set(); }
}
function setFolded(id, on){
  const s=foldedIds();
  if(on) s.add(id); else s.delete(id);
  try{ localStorage.setItem(FOLD_KEY, JSON.stringify([...s])); }catch(e){}
}
function applyFold(){
  const s=foldedIds();
  document.querySelectorAll('.card[data-foldable], .card[id]').forEach(c=>{
    if(!c.id) return;
    const on=s.has(c.id);
    c.classList.toggle('collapsed', on);
    const b=c.querySelector('.fold');
    if(b) b.textContent=on?'＋':'－';
  });
}
document.addEventListener('click',(e)=>{
  const b=e.target.closest && e.target.closest('.fold');
  if(!b) return;
  const c=b.closest('.card'); if(!c||!c.id) return;
  const on=!c.classList.contains('collapsed');
  c.classList.toggle('collapsed',on);
  b.textContent=on?'＋':'－';
  setFolded(c.id,on);
});

/* ---------------- 侧栏导航: 看板 / 功能 ---------------- */
const TAB_KEY='cokTab';
const TAB_META={
  dash:{title:'看板', sub:'只读监控 · 事件流'},
  ops: {title:'功能', sub:'领奖 · 加速 · 打怪 · 扫描'},
};
/* 侧栏在窄屏是抽屉, 切页后自动收起(否则挡住内容) */
function closeNav(){
  const sb=$('sidebar'), sc=$('scrim');
  if(sb) sb.classList.remove('open');
  if(sc) sc.classList.remove('show');
}
function syncTabTop(){ /* 保留空实现: 老调用点仍在, 新布局不需要吸顶偏移 */ }
window.addEventListener('resize', syncTabTop);
function switchTab(name){
  name=(name==='ops')?'ops':'dash';
  const dash=$('paneDash'), ops=$('paneOps');
  if(dash) dash.style.display=(name==='dash')?'':'none';
  if(ops)  ops.style.display =(name==='ops') ?'':'none';
  document.querySelectorAll('.navItem').forEach(t=>{
    t.classList.toggle('active', t.dataset.tab===name);
  });
  const meta=TAB_META[name]||TAB_META.dash;
  const ct=$('crumbTitle'), cs=$('crumbSub');
  if(ct) ct.textContent=meta.title;
  if(cs) cs.textContent=meta.sub;
  closeNav();
  try{ localStorage.setItem(TAB_KEY,name); }catch(e){}
  window.scrollTo({top:0,behavior:'smooth'});
}
document.addEventListener('click',(e)=>{
  const t=e.target.closest && e.target.closest('.navItem');
  if(!t) return;
  switchTab(t.dataset.tab);
});
/* 汉堡按钮: 窄屏开合侧栏 */
document.addEventListener('click',(e)=>{
  if(e.target.closest && e.target.closest('#btnNav')){
    const sb=$('sidebar'), sc=$('scrim');
    if(sb) sb.classList.toggle('open');
    if(sc) sc.classList.toggle('show');
    return;
  }
  if(e.target.closest && e.target.closest('#scrim')) closeNav();
});
/* 某个卡片在哪个 Tab 里(今日待办在看板, 其余操作卡在功能) */
function tabOf(id){
  const el=document.getElementById(id);
  if(el && el.closest('#paneOps')) return 'ops';
  return 'dash';
}

/* 概览条 / 待办 点击直达对应卡片 */
function goTo(id){
  const el=document.getElementById(id);
  if(!el) return;
  // 目标卡可能在另一个 Tab 里 —— 先切过去, 否则点了跳不过去
  switchTab(tabOf(id));
  // 折叠状态下先展开, 否则点了看不到
  if(el.classList.contains('collapsed')){
    el.classList.remove('collapsed');
    setFolded(el.id,false);
    const b=el.querySelector('.fold'); if(b) b.textContent='－';
  }
  // 切 Tab 后 pane 刚显示, 等一帧再滚动 + 高亮
  requestAnimationFrame(()=>{
    el.scrollIntoView({behavior:'smooth',block:'start'});
    el.animate([{boxShadow:'0 0 0 3px rgba(88,166,255,.55)'},{boxShadow:'0 0 0 3px rgba(88,166,255,0)'}],
               {duration:1100,easing:'ease-out'});
  });
}
document.addEventListener('click',(e)=>{
  // 侧栏「快捷跳转」：data-go 直接就是卡片 id（cardXxx）
  const j=e.target.closest && e.target.closest('.jump');
  if(j){ goTo(j.dataset.go); closeNav(); return; }
  const more=e.target.closest && e.target.closest('#ovMoreBtn');
  if(more){
    const bar=document.getElementById('ovbar');
    if(bar){
      const on=bar.classList.toggle('expanded');
      more.setAttribute('aria-expanded', on?'true':'false');
      const lb=more.querySelector('.lb'), vl=more.querySelector('.vl');
      if(lb) lb.textContent = on?'收起':'更多';
      if(vl) vl.textContent = on?'▲':'▼';
    }
    return;
  }
  const o=e.target.closest && e.target.closest('.ov');
  if(!o) return;
  const map={todo:'cardTodo',assist:'cardAssist',daily:'cardAssist',hunt:'cardHunt',dock:'cardDock',
             speed:'cardSpeed',shield:'cardShield',tasks:'cardTodo',locate:'cardLocate',
             welfare:'cardWelfare',sky:'cardSky',score:'cardScore',alliance:'cardAlliance',
             fleet:'cardFleet',stats:'cardTaskStats'};
  goTo(map[o.dataset.go]||'cardTodo');
});

/* ---------------- 概览条 + 今日待办 ---------------- */
/* 汇总"现在该做什么": 只用真实状态, 不猜 */
function collectTodos(st){
  const S2=st.states||{};
  const ds=S2.dailySign||{}, dq=S2.dailyQuest||{}, lt=S2.lordTask||{}, sk=S2.storyTask||{};
  const dk=st.dock||{}, au=st.hunter||{}, h=st.hunt||{};
  const out=[];
  const push=(ok,text,sub,btn)=>out.push({ok,text,sub,btn});
  // 签到
  if(Object.keys(ds).length){
    if(ds['今日已签']===true) push(true,'今日已签到',(ds['已签日期']||[]).length+' 天',null);
    else push(false,'今日还没签到','点「立即签到」补上',{label:'去签到',fn:'sign'});
  }
  // 日常/周/领主 任务奖励
  const dq2=(dq['可领日常任务']||[]).length;
  const wk=(dq['周任务可领奖励']||[]).length;
  const ld=(lt['可领奖励']||[]).length;
  const taskN=dq2+wk+ld;
  if(taskN>0) push(false,'有 '+taskN+' 个任务奖励可领',
      [dq2&&('日常 '+dq2),wk&&('周 '+wk),ld&&('领主 '+ld)].filter(Boolean).join(' · '),
      {label:'去领取',fn:'claim'});
  else if(Object.keys(dq).length||Object.keys(lt).length) push(true,'任务奖励都领完了','',null);
  // 港口
  const rw=(dk.rewardable||0);
  if(dk.family){
    if(rw>0) push(false,'港口有 '+rw+' 条船的奖励没领','',{label:'去领取',fn:'dockReward'});
    else push(true,'港口没有待领奖励',(dk.trading||0)+' 条在途',null);
  }
  // 福利中心(每日好礼 / 龙之馈赠)
  const wf=st.welfare||{};
  if(wf.loaded){
    const wn=wf.claimable||0;
    if(wn>0) push(false,'福利中心有 '+wn+' 项可领','每日好礼 / 龙之馈赠',{label:'去领取',fn:'welfareClaim'});
    else push(true,'福利中心今天都领完了','每日好礼 / 龙之馈赠',null);
  }
  // 加速队列
  const running=(st.queues||[]).filter(q=>q.running);
  if(running.length) push(false,running.length+' 个队列可以加速','用道具, 不花金币',{label:'去加速',fn:'goSpeed'});
  // 保护罩
  const sh=st.shield||{};
  const shieldLeft=Math.max(0,(sh.end_ms||0)-Date.now());
  if(shieldLeft>0) push(true,'保护罩还剩 '+dur(shieldLeft),'到期 '+ts(sh.end_ms),null);
  else push(false,'当前没有保护罩','被攻击会掉兵',{label:'去开罩',fn:'goShield'});
  // 体力
  const stam=(au&&au.running&&au.stamina!=null)?au.stamina:(h.stamina||0);
  if(stam<=10) push(false,'体力只剩 '+stam,stam<=0?'打不了怪':'建议等恢复或用体力道具',{label:'看打怪',fn:'goHunt'});
  return out;
}

function renderOverview(st){
  const S2=st.states||{};
  const ds=S2.dailySign||{}, dq=S2.dailyQuest||{}, lt=S2.lordTask||{};
  const dk=st.dock||{}, au=st.hunter||{}, h=st.hunt||{};
  const sh=st.shield||{};
  const set=(id,html,cls)=>{ const e=$(id); if(!e) return; e.innerHTML=html;
    const p=e.parentElement; if(p){ p.classList.remove('good','warn','err','info');
      if(cls) p.classList.add(cls); } };
  // 待办
  const todos=collectTodos(st);
  const pend=todos.filter(t=>!t.ok).length;
  set('ovTodo', pend?String(pend):'0', pend?(pend>3?'err':'warn'):'good');
  // 有待办时整块高亮, 引导用户先处理
  const ovTodoBox=$('ovTodo')&&$('ovTodo').parentElement;
  if(ovTodoBox) ovTodoBox.classList.toggle('act', pend>0);
  // Tab 角标: 看板=待办待处理数; 功能=开着的自动开关数
  const setCnt=(id,n)=>{ const e=$(id); if(!e) return;
    e.style.display=n?'':'none'; e.textContent=n||''; };
  setCnt('tabDashCnt', pend);
  const autoOn=['autoSign','autoShield','autoWelfare','dockAutoReward','dockAutoSend']
    .filter(k=>SETTINGS[k]).length + (au.running?1:0);
  setCnt('tabOpsCnt', autoOn);
  // 签到
  const signed=ds['今日已签'];
  set('ovSign', signed?'<span class="vTxt">已签</span>':'<span class="vTxt">未签</span>',
      signed?'good':'warn');
  // 体力
  const stam=(au&&au.running&&au.stamina!=null)?au.stamina:(h.stamina||0);
  const smax=(au&&au.running&&au.stamina_max)?au.stamina_max:(h.stamina_max||100);
  set('ovStamina', fmt(stam)+'<small>/'+fmt(smax)+'</small>', stam<=10?'warn':'info');
  // 自动打怪
  set('ovHunt', au.running?'<span class="vTxt">运行中</span>':'<span class="vTxt">停止</span>',
      au.running?'good':'');
  // 港口: 有待领显示数量, 否则显示在途数(更有信息量)
  const rw=(dk.rewardable||0);
  set('ovDock', dk.family?((rw?rw+' 待领':((dk.trading||0)+' 在途'))):'<span class="vTxt">-</span>',
      rw?'warn':(dk.family?'good':''));
  // 队列
  const running=(st.queues||[]).filter(q=>q.running);
  set('ovQueue', running.length?String(running.length):'<span class="vTxt">空闲</span>',
      running.length?'info':'good');
  // 保护罩
  const left=Math.max(0,(sh.end_ms||0)-Date.now());
  set('ovShield', left?dur(left):'<span class="vTxt">无罩</span>', left?'good':'warn');
  // 福利中心
  const wf2=st.welfare||{};
  const wn=(wf2.loaded?(wf2.claimable||0):null);
  set('ovWelfare', wn==null?'<span class="vTxt">-</span>'
                          :(wn?String(wn):'<span class="vTxt">已领</span>'),
      wn?'warn':(wn===0?'good':''));
  // 任务奖励
  const tn=((dq['可领日常任务']||[]).length)+((dq['周任务可领奖励']||[]).length)+((lt['可领奖励']||[]).length);
  set('ovTask', tn?String(tn):'<span class="vTxt">已清</span>', tn?'warn':'good');
  // 查玩家: 显示**索引里有多少人**(这是能不能查到人的关键指标)
  const mi=st.map_index||{};
  const idxN=mi.count||0;
  set('ovLocate', idxN?(String(idxN)+'<small> 人</small>')
                          :'<span class="vTxt">未扫描</span>',
      idxN?'info':'warn');
  // 索引状态(扫描进度 + 时效)
  // ⚠️ 索引是**扫描时刻的快照**。服务端会定时重排整张地图, 坐标会整体迁移 ——
  // 实测 2026-10-25 19:39 扫的坐标, 当天 20:20 已全部失效(原位置站着别人)。
  const li=$('locateIdx');
  const ageH=(mi.age_h==null?null:Number(mi.age_h));
  const stale=(ageH!=null && ageH>6);
  if(li){
    if(!idxN){
      li.textContent='索引: 空 —— 点「扫描附近」开始建索引';
    }else if(mi.scanning){
      li.textContent='索引: '+idxN+' 人 · 扫描中 '+mi.requests_done+'/'+mi.requests_total
        +' 次请求'+(mi.updated_at?(' · 更新于 '+ts(mi.updated_at*1000)):'');
    }else{
      li.textContent='索引: '+idxN+' 人'
        +(mi.updated_at?(' · 更新于 '+ts(mi.updated_at*1000)):'');
      if(ageH!=null){
        li.textContent+=' · 快照 '+ageH.toFixed(1)+' 小时前';
      }
      li.textContent+=' · 点「导出 Excel」拿全表';
    }
    if(stale){
      const w=document.createElement('div');
      w.style.color='#e0a44a';
      w.style.marginTop='4px';
      w.textContent='⚠️ 坐标是 '+ageH.toFixed(1)+' 小时前的快照。服务端会定时重排地图, '
        +'若坐标对不上请用「现场扫描」刷新(只扫查询点周围, 几秒)或重跑 scan_world.py。';
      li.appendChild(w);
    }
  }
  // 待办列表
  const box=$('todoList');  if(box){
    if(!todos.length){
      box.innerHTML='<div class="none">还没有状态数据 —— 连上游戏服后这里会列出今天该做的事</div>';
    }else{
      box.innerHTML=todos.map((t,i)=>{
        const act=t.btn?('<button data-todo="'+i+'">'+esc(t.btn.label)+'</button>'):'';
        return '<div class="trow'+(t.ok?' done':'')+'">'
          +'<span class="ti '+(t.ok?'n':'y')+'">'+(t.ok?'✓':'!')+'</span>'
          +'<span class="tx"><b>'+esc(t.text)+'</b>'+(t.sub?('<span class="mini">'+esc(t.sub)+'</span>'):'')+'</span>'
          +act+'</div>';
      }).join('');
    }
    const sum=$('todoSum');
    if(sum) sum.textContent = todos.length?('待办 '+pend+' / 共 '+todos.length+' 项'):'';
  }
}

/* ---------------- 任务达成统计 ---------------- */
/* 日/周/月合并成一个视图, 用下拉切换周期(默认今日) */
let TASK_STATS_PERIOD='day';
function renderTaskStats(st){
  const box=$('taskStats'), sum=$('taskStatsSum');
  if(!box) return;
  const ts=st.task_stats||{}, periods=ts.periods||{}, cur=ts.current||{};
  const names={day:'今日',week:'本周',month:'本月'};
  const order=['day','week','month'];
  if(!order.includes(TASK_STATS_PERIOD)) TASK_STATS_PERIOD='day';
  // 周期下拉在卡片标题里(静态 DOM, 不被轮询重建), 这里只做一次性绑定 ——
  // 否则每轮 innerHTML 重建下拉会把手机原生弹层刷掉, 看着就是"点不动"。
  const selP=$('taskStatsPeriod');
  if(selP){
    if(selP.value!==TASK_STATS_PERIOD) selP.value=TASK_STATS_PERIOD;
    if(!selP._bound){
      selP._bound=true;
      selP.onchange=()=>{ TASK_STATS_PERIOD=selP.value; if(S.state) renderTaskStats(S.state); };
    }
  }
  const key=TASK_STATS_PERIOD;
  const p=periods[key]||{}, rows=p.breakdown||[];
  const detail=rows.length
    ? rows.map(x=>'<span class="tag good">'+esc(x.label)+' '+esc(x.count)+'</span>').join('')
    : '<span class="mini">本周期还没有新达成记录</span>';
  const current=[];
  if(cur.signed===true) current.push('今日已签到');
  if(cur.daily_ready&&cur.daily_ready.length) current.push('日常已达成 '+cur.daily_ready.length);
  if(cur.weekly_ready&&cur.weekly_ready.length) current.push('周奖励已达成 '+cur.weekly_ready.length);
  if(cur.lord_remaining===0 && cur.lord_claimed>0) current.push('领主任务已完成');
  if(cur.story_total) current.push('主线完成 '+(cur.story_finished||[]).length+'/'+cur.story_total);
  box.innerHTML=
    '<div class="kv"><span>'+names[key]+' 累计 <span class="mini">'+esc(p.label||'-')+'</span></span>'
      +'<b>'+esc(p.total||0)+' 项</b></div>'
    +'<div style="margin-top:6px">'+detail+'</div>'
    +'<div class="mini" style="margin-top:8px">当前状态：'
      +(current.length?esc(current.join(' · ')):'等待任务数据同步')+'</div>';
  if(sum) sum.textContent=(periods.month&&periods.month.total?('本月 '+periods.month.total+' 项'):'');
}

/* 待办项的直达动作 */
const TODO_FNS={
  sign:()=>$('btnSign').click(),
  claim:()=>$('btnClaim').click(),
  dockReward:()=>$('btnDockReward').click(),
  welfareClaim:()=>$('btnWelfareClaim').click(),
  goSpeed:()=>goTo('cardSpeed'),
  goShield:()=>goTo('cardShield'),
  goHunt:()=>goTo('cardHunt'),
};
document.addEventListener('click',(e)=>{
  const b=e.target.closest && e.target.closest('[data-todo]');
  if(!b) return;
  const st=S.state; if(!st) return;
  const todos=collectTodos(st);
  const t=todos[parseInt(b.dataset.todo,10)];
  if(t&&t.btn&&TODO_FNS[t.btn.fn]) TODO_FNS[t.btn.fn]();
});

/* 多账号总览: 点某张卡 -> 切到该账号 */
document.addEventListener('click',(e)=>{
  const b=e.target.closest && e.target.closest('[data-fleet]');
  if(!b) return;
  switchAccount(b.dataset.fleet);
});

/* 折叠后的标题摘要: 不展开也能看到大概情况 */
function renderSummaries(st){
  const S2=st.states||{};
  const ds=S2.dailySign||{};
  const put=(id,txt)=>{ const e=$(id); if(e) e.textContent=txt||''; };
  put('sumAssist', ds['今日已签']===true?'今日已签':(ds['今日已签']===false?'今日未签':''));
  const running=(st.queues||[]).filter(q=>q.running);
  put('sumSpeed', running.length?(running.length+' 个进行中'):'');
  const sh=st.shield||{};
  const left=Math.max(0,(sh.end_ms||0)-Date.now());
  put('sumShield', left?('还剩 '+dur(left)):'无罩');
  const dk=st.dock||{};
  put('sumDock', dk.family?((dk.rewardable||0)+' 待领 · '+(dk.trading||0)+' 在途'):'');
  const wf=st.welfare||{};
  put('sumWelfare', wf.loaded?((wf.claimable||0)+' 待领 · '+(wf.rows||[]).length+' 项'):'');
  const au=st.hunter||{};
  put('sumHunt', au.running?('运行中 · 已打 '+(au.kills||0)):'');
  put('sumHook', $('hookRules')?$('hookRules').textContent:'');
}

/* ---------------- 渲染 ---------------- */
function renderHeader(st){
  const dot=$('connDot'), txt=$('connText');
  let cls='wait', label='空闲';
  if(st.account_error){ cls='off'; label='设备未连接'; }
  // 用户主动断开: 这是**预期**状态, 不是故障 —— 要排在 st.error 之前
  // offline_hold 是**落盘**的断开意图: 服务器刚重启、循环还没跑第一轮时,
  // 内存里的 disconnected 还是 false, 但这个已经为真 —— 一起认, 免得顶灯
  // 在重启后短暂误显示成"空闲"。
  else if(st.disconnected || st.offline_hold){ cls='wait'; label='已断开 · 点「重连」恢复'; }
  // ⚠️ 自动打怪时账号被独占是**设计内**的(让路给打怪), 不是异常 ——
  // 所以必须排在 st.error 前面, 否则会误报"连接异常"。
  else if(st.hunter&&st.hunter.running){ cls='on'; label='自动打怪中'; }
  else if(st.error){ cls='off'; label='连接异常'; }
  else if(st.connected){ cls='on'; label='已连接'; }
  // ondemand 模式轮完就断开, connected 会是 false —— 用"有数据"判定更准
  else if(st.has_data){ cls='on'; label='已连接'; }
  else if(st.app_yield){ cls='wait'; label='App 在线 · 已让出账号'; }
  dot.className='dot '+cls; txt.textContent=label;
  $('sLast').textContent = st.last_poll ? hhmmss(st.last_poll)+' ('+ago(st.last_poll)+')' : '未刷新';
  $('sDate').textContent = st.server_date||'-';
  $('sGold').textContent = st.gold==null?'-':fmt(st.gold);
  $('sMode').textContent = st.persistent ? '常驻连接(App 会被踢)' : '按需短连接';
  if(st.names) NAMES=st.names;
  if(st.settings && !Object.keys(SETTINGS).length){
    SETTINGS=st.settings||{}; applySettings();
  }
  // ⚠ 只有"用户没存过"时才用服务端默认值回填:
  // 之前无条件覆盖, 刷新页面会把用户选的 webhook 类型改回 CLI 默认值并写回文件。
  if(st.webhook_type && SETTINGS.hookType===undefined) $('selHookType').value=st.webhook_type;
  // 规则显示中文名(后端已给), 没有中文名时退回原始代号
  $('hookRules').textContent=(st.alert_rule_names||st.alert_rules||[]).join(' · ')||'-';
  renderBanner(st);
}

/* 顶部账号选择器: 下拉切换当前账号, ＋ 从设备入库, － 删除当前账号 */
let ACCT_SIG='';
function renderAccounts(st){
  const sel=$('acctSelect'); if(!sel) return;
  const a=st.accounts||{};
  const list=a.list||[];
  const active=a.active||a.current||'';
  // 只有列表/选中/后台集合变化时才重建 <option>, 否则用户正在点开下拉会被打断
  const sig=JSON.stringify(list.map(x=>[x.key,x.label,!!x.parallel]))+'|'+active;
  if(sig!==ACCT_SIG){
    ACCT_SIG=sig;
    if(!list.length){
      sel.innerHTML='<option value="">（未入库 · 点 ＋ 添加）</option>';
    }else{
      // 后台在跑的账号前面加 ● 标记, 一眼看出哪些号没在看也在工作
      sel.innerHTML=list.map(x=>'<option value="'+esc(x.key)+'"'
        +(x.key===active?' selected':'')+'>'
        +(x.parallel?'● ':'')+esc(x.label||x.key)+'</option>').join('');
    }
  }
  $('btnAcctDel').disabled=!list.length;
  // 后台运行按钮: 反映当前查看账号的并行态(亮=开)
  const cur=list.find(x=>x.key===active);
  const on=!!(cur&&cur.parallel);
  const bp=$('btnAcctParallel');
  if(bp){
    bp.disabled=!list.length;
    bp.classList.toggle('on',on);
    bp.style.color=on?'#36d399':'';
    bp.title=(on?'后台运行中(点击关闭) · ':'点击让该账号在后台运行 · ')
      +'后台账号即使不在看也会轮询/守护/打怪';
  }
}

/* 多账号总览: 「全部刷新」—— 每个托管账号各刷一次(并行, 互不阻塞)。
   顶部的「立即刷新」只作用于**当前在看**的那一个号, 后台号不会动。 */
document.addEventListener('click',async(ev)=>{
  const b=ev.target.closest&&ev.target.closest('#btnFleetRefresh');
  if(!b) return;
  await busy(b,'刷新全部账号…',async()=>{
    const r=await api('/api/action',{action:'refresh-all'});
    if(r.ok){ toast(r.note||('已刷新 '+r.succeeded+' 个账号'),'ok'); }
    else {
      const bad=Object.keys(r.results||{}).filter(k=>!(r.results[k]||{}).ok);
      toast('部分账号刷新失败: '+(bad.join('、')||'未知'),'warn');
    }
    await refresh(true);
  });
});

/* 多账号总览: 把后台托管的号一屏列出, 每张卡显示关键态, 点一下切过去 */
function renderFleet(st){
  const card=$('cardFleet'); if(!card) return;
  const a=st.accounts||{};
  const list=a.list||[];
  const active=a.active||a.current||'';
  // 只有一个号(或没入库)就不显示, 避免首屏噪音
  if(list.length<2){ card.style.display='none'; return; }
  card.style.display='';
  const box=$('fleetList'), sum=$('fleetSum');
  let running=0, attn=0;
  const cells=list.map(x=>{
    const s=x.summary||null;
    const isActive=(x.key===active);
    const bg=isActive?'rgba(91,157,255,.10)':'rgba(39,48,64,.35)';
    const bd=isActive?'var(--accent)':'var(--line)';
    let tags='';
    if(!x.running){
      tags='<span class="tag">未托管</span>';
    }else{
      running++;
      if(s){
        if(s.error) { tags+='<span class="tag bad">异常</span>'; attn++; }
        else if(s.disconnected) tags+='<span class="tag">已断开</span>';
        else if(s.stale){ tags+='<span class="tag warn">久无响应</span>'; attn++; }
        if(s.hunting) tags+='<span class="tag good">打怪'+(s.hunt_kills?(' '+s.hunt_kills):'')+'</span>';
        if(s.has_shield) tags+='<span class="tag good">罩 '+dur(s.shield_ms)+'</span>';
        else { tags+='<span class="tag warn">无罩</span>'; attn++; }
        if(s.dock_rewardable){ tags+='<span class="tag warn">港口待领 '+s.dock_rewardable+'</span>'; attn++; }
        if(s.welfare_claimable){ tags+='<span class="tag warn">好礼待领</span>'; attn++; }
        if(s.app_yield) tags+='<span class="tag">让号中</span>';
        if(tags==='') tags='<span class="tag good">正常</span>';
      }else{
        tags='<span class="tag">同步中…</span>';
      }
    }
    const err=(s&&s.error)?('<div class="mini" style="margin-top:4px;color:var(--err)">'+esc(String(s.error).slice(0,80))+'</div>'):'';
    return '<button class="fleetCell" data-fleet="'+esc(x.key)+'" style="display:block;width:100%;text-align:left;'
      +'background:'+bg+';border:1px solid '+bd+';border-radius:8px;padding:9px 11px;margin:6px 0;cursor:pointer">'
      +'<div style="display:flex;align-items:center;gap:8px">'
        +'<b style="flex:1 1 auto">'+(x.parallel?'● ':'')+esc(x.label||x.key)+(isActive?' <span class="mini">(在看)</span>':'')+'</b>'
      +'</div>'
      +'<div style="margin-top:5px">'+tags+'</div>'+err
    +'</button>';
  }).join('');
  box.innerHTML=cells;
  if(sum) sum.textContent=running+' 个托管中'+(attn?(' · '+attn+' 项需关注'):'');
}

/* 顶部横幅: 把"为什么没数据"直接摆出来, 不用往下翻 */
let BANNER_KEY='', BANNER_HIDDEN=false;
function renderBanner(st){
  const bn=$('banner');
  if(!bn) return;
  const src=st.account_source||'';
  const busy=st.account_busy;
  const holder=(st.account_holder||'').trim();
  // 打怪时账号被独占是设计内的让路, 不该报"连接异常"
  const hunting=!!(st.hunter&&st.hunter.running);
  const mi=(st.map_index||{});
  // 扫描进程也独占账号 —— 但那是**正常的工作状态**, 不是故障
  const scanning=!!mi.scanning || /scan-world/.test(holder);
  const key = st.account_error ? ('acc:'+st.account_error)
            : (busy ? ('busy:'+holder+':'+(mi.requests_done||0))
            : (hunting ? ''
            : (src.indexOf('内置')>=0 ? ('builtin:'+src) : (st.error ? ('err:'+st.error) : ''))));
  if(key!==BANNER_KEY){ BANNER_KEY=key; BANNER_HIDDEN=false; }
  if(!key || BANNER_HIDDEN){ bn.className='banner'; bn.innerHTML=''; return; }
  if(st.account_error){
    bn.className='banner show err';
    bn.innerHTML='<span class="x" id="bannerX" title="隐藏">×</span><b>设备未连接</b> · '+esc(st.account_error)
      +' · 设备连回来后点「立即刷新」即可恢复, 不用重启控制台';
  }else if(busy && scanning){
    bn.className='banner show';
    bn.innerHTML='<span class="x" id="bannerX" title="隐藏">×</span><b>全图扫描中</b> · '
      +'账号被扫描占用, 监控数据暂停刷新'
      +(mi.requests_total?(' · 进度 '+esc(mi.requests_done)+'/'+esc(mi.requests_total)+' 次请求'):'')
      +' · 扫完自动恢复, 也可以在「玩家坐标」卡点「停止扫描」';
  }else if(busy){
    bn.className='banner show';
    bn.innerHTML='<span class="x" id="bannerX" title="隐藏">×</span><b>账号正被占用</b> · 同账号只允许一个连接'
      +(holder?(' · 当前持有: '+esc(holder)):'')+' · 等它结束或把它停掉';
  }else if(src.indexOf('内置')>=0){
    bn.className='banner show';
    bn.innerHTML='<span class="x" id="bannerX" title="隐藏">×</span><b>当前使用内置凭据</b> · '
      +(st.account_note?esc(st.account_note)+' · ':'设备没连上, ')
      +'已改用从登录请求复原的凭据(signCode 由 APK 证书派生, 不依赖设备), 数据照常可用; '
      +'设备连回来后点「立即刷新」会优先用设备里的最新账号';
  }else{
    bn.className='banner show';
    bn.innerHTML='<span class="x" id="bannerX" title="隐藏">×</span><b>连接异常</b> · '+esc(st.error)
      +' · 点「立即刷新」重试';
  }
}

function renderHunt(st){
  const h=st.hunt||{};
  const au=st.hunter||{};
  // 编队预设下拉: 面板已隐藏(2026-10-27 收回), 不再渲染
  // 打怪时账号连接被 AutoHunter 独占, 轮询读不到体力 → 优先用 hunter 自己读的
  const cur=(au&&au.running&&au.stamina!=null)?au.stamina:(h.stamina||0);
  const mx=(au&&au.running&&au.stamina_max)?au.stamina_max:(h.stamina_max||100);
  $('staminaFill').style.width=Math.max(0,Math.min(100,cur/mx*100))+'%';
  const lv=h.lv_low||1;
  const per=(st.monster_levels||[]).find(x=>x.level===lv);
  const cost=per?per.usePower:10;
  $('staminaTxt').textContent=h.error&&!(au&&au.running)?('读取失败'):(fmt(cur)+' / '+fmt(mx));
  // 等级下拉
  const sel=$('selMonster');
  const sig=(st.monster_levels||[]).length+':'+h.max_level;
  if(sel.dataset.sig!==sig){
    sel.dataset.sig=sig;
    sel.innerHTML=(st.monster_levels||[]).filter(x=>x.level<=(h.max_level||30))
      .map(x=>`<option value="${x.level}">${x.level} 级 ${esc(x.name||'')} · 消耗 ${x.usePower} 体力</option>`).join('')
      ||'<option value="1">1 级</option>';
  }
  if(document.activeElement!==sel && h.lv_low) sel.value=String(h.lv_low);
  // 打怪状态: 游戏自己的自动打怪队列(status) + 网页自建(降级模式)
  const ah=$('autoHint');
  const gameOn=!!(h.status);          // autoQueue.status: 游戏队列开着
  const gameFmt=(h.format||'');
  const gameIdx=(/^\d+(;\d+)*$/.test(gameFmt))?gameFmt:'';
  if(au.running){
    // 降级模式: 网页自己出征
    const l=au.last||{};
    ah.innerHTML='<span class="tag good">运行中</span>(网页代打) 已打 '+esc(au.kills||0)+' 只 · 体力 '+esc(au.stamina||0)+'/'+esc(au.stamina_max||100)
      +(au.stamina_potions?(' · 已喝药水 '+esc(au.stamina_potions)+' 瓶'):'')
      +'<br><span class="mini">'+(au.wait_for?esc(au.wait_for):(l.x?('目标 ('+esc(l.x)+','+esc(l.y)+') index '+esc(l.index)+' · '+esc(l.troop||'')+' x'+esc(l.num||0)):'正在找怪…'))
      +(au.recover_per_min!=null?(' · 体力恢复约 '+esc(au.recover_per_min)+'/分钟'):'')
      +(au.auto_stamina?(' · <b>体力不足自动喝药水</b>已开'):'')+'</span>';
  }else if(gameOn){
    ah.innerHTML='<span class="tag good">运行中</span> 游戏正在用 '+(gameIdx?('编队'+gameIdx.split(';').join('、')):'(未知编成)')
      +' 打怪 · 等级 '+esc(h.lv_low)+'~'+esc(h.lv_high)+' · 并行 '+esc(h.auto_count||0)+' 队'
      +'<br><span class="mini">出征由游戏自己做(用你在游戏里设好的编队), 网页只监控</span>';
  }else{
    ah.innerHTML=(au.kills?('已停止 · 累计 '+esc(au.kills)+' 只'):'未开启')
      +(h.format?(' · 游戏里现在用 '+(gameIdx?('编队'+gameIdx):'编成串(被写坏)')+''):'')
      +(au.note?(' · '+esc(au.note)):'');
  }
  renderSquadProgress(au);
  // 按钮状态: 开了就变「已开启」并禁用, 没开时「停止」置灰
  const bStart=$('btnAutoStart'), bStop=$('btnAutoStop');
  const running=gameOn||!!(au&&au.running);
  if(bStart){
    bStart.disabled=running;
    bStart.textContent=running?'已开启':'开始打怪';
    bStart.classList.toggle('primary', !running);
  }
  if(bStop) bStop.disabled=!running;
  // 提示(不再有周卡面板, 只在运行时提示会占账号)
  const warn=$('huntWarn');
  if(running){
    warn.style.display='';
    warn.innerHTML=au&&au.running
      ? '网页代打正在占用账号连接，<b>网页轮询已自动暂停</b>，App 也会被顶下线。'
      : '游戏里的自动打怪开着, <b>网页轮询会跳过</b>, App 也会被顶下线。';
  }else{ warn.style.display='none'; }
}

/* 每支队伍的打怪进度 */
function renderSquadProgress(au){
  const box=$('squadProgress');
  if(!box) return;
  const sqs=(au&&au.squads)||[];
  if(!sqs.length){
    box.innerHTML='<div class="mini">还没有队伍(点「开始打怪」后按每队兵数自动分配)</div>';
    return;
  }
  const stateText={idle:['待命',''], marching:['出征中','good'], done:['已回来','']};
  box.innerHTML='<table class="sqtable"><thead><tr><th>队</th><th>兵种</th><th>数量</th><th>状态</th><th>目标</th><th>已打</th></tr></thead><tbody>'
    + sqs.map(s=>{
        const st=stateText[s.state]||['-',''];
        const tgt=(s.x!=null)?('('+esc(s.x)+','+esc(s.y)+')'):'-';
        const extra=(s.state==='marching'&&s.elapsed!=null)?(' <span class="mini">'+(s.elapsed||0)+'s</span>'):'';
        // 混编队: 数量列显示**每个兵种的人数**(A 300 + B 200)
        const tp=s.troops||[];
        const qty=(tp.length>1)
          ? tp.map(t=>esc((t.name||t.army_id||'?')+' '+(t.num||0))).join(' + ')
          : esc(s.num||0);
        return '<tr><td>'+esc(s.slot||'-')+'</td>'
          +'<td>'+esc(s.name||s.army_id||'-')+'</td>'
          +'<td>'+qty+'</td>'
          +'<td><span class="tag '+st[1]+'">'+st[0]+'</span>'+extra+'</td>'
          +'<td class="mini">'+tgt+'</td>'
          +'<td>'+esc(s.kills||0)+'</td></tr>';
      }).join('')
    + '</tbody></table>';
}

function renderCards(st){
  const S2=st.states||{};
  const c=[];
  const empty=(why)=>'<div class="empty">'+esc(why)+'</div>';
  // 卡片里只说结论, 完整原因在顶部横幅(避免同一句话刷 8 遍)
  // ⚠️ 打怪占用连接时 st.error 是设计内的让路提示, 不是故障
  const hunting=!!(st.hunter&&st.hunter.running);
  const why = st.account_error ? '设备未连接 —— 详情见顶部横幅'
              : (hunting ? '自动打怪占用账号连接，监控数据暂停刷新'
              : (st.error ? ('连接异常: '+st.error) : (st.app_yield ? 'App 在线，账号已让出，稍后自动刷新'
              : (st.last_poll?'':'等待首轮轮询…'))));

  // 签到
  const ds=S2.dailySign||{};
  c.push('<div class="card"><h2>每日签到</h2>'
    + (Object.keys(ds).length? kv('今日已签', ds['今日已签']===true?'<span class="tag good">已签</span>':'<span class="tag bad">未签</span>')
        + kv('剩余补签次数', esc(ds['剩余补签次数']))
        + kv('已签日期', tags((ds['已签日期']||[]).slice(-8)))
      : empty(why))+'</div>');

  // 周任务
  const dq=S2.dailyQuest||{};
  c.push('<div class="card"><h2>周任务</h2>'
    + (Object.keys(dq).length? kv('周任务积分', esc(dq['周任务积分']))
        + kv('可领周奖励', jumpTags(dq['周任务可领奖励'],'good','cardAssist'))
        + kv('周结束时间', esc(ts(dq['周结束时间'])))
      : empty(why))+'</div>');

  // 日常任务
  const dq2=(dq['可领日常任务']||[]);
  c.push('<div class="card"><h2>可领日常任务 <span class="sub">'+dq2.length+' 项</span></h2>'
    + (dq2.length? '<div>'+dq2.map(x=>'<span class="tag warn" title="'+esc(x.id)+'">'+esc(x['名称']||x.id)+' '+esc(x['进度']||'')+'</span>').join('')+'</div>'
        + '<div class="mini" style="margin-top:6px">点下面「领取奖励」可一次领完</div>'
      : (Object.keys(dq).length? empty('没有可领的日常任务') : empty(why)))+'</div>');

  // 领主任务
  const lt=S2.lordTask||{};
  const un=lt['未完成']||[];
  c.push('<div class="card"><h2>领主任务</h2>'
    + (Object.keys(lt).length? kv('当前进度', esc(lt['当前进度']))
        + kv('已领档位', esc(lt['已领档位数']))
        + kv('可领奖励', jumpTags(lt['可领奖励'],'good','cardAssist'))
        + (un.length? ('<div class="mini" style="margin-top:6px">未完成 '+un.length+' 项</div><div>'
            + un.map(x=>'<span class="tag" title="'+esc(x.id)+'">'+esc(x['名称']||('任务 '+x.id))+' '+esc(x['进度']||'')+'</span>').join('')+'</div>')
          : '<div class="mini" style="margin-top:6px">全部完成</div>')
      : empty(why))+'</div>');

  // 主线任务
  const sk=S2.storyTask||{};
  const tk=sk['任务']||[];
  c.push('<div class="card"><h2>主线任务</h2>'
    + (Object.keys(sk).length? kv('章节', esc(sk['章节名']||sk['章节']))
        + kv('任务数', esc(sk['任务数']))
        + (tk.length? ('<div style="margin-top:5px">'+tk.map(x=>'<span class="tag info" title="'+esc(x.id)+'">'+esc(x['名称']||x.id)+' '+esc(x['进度']||'')+'</span>').join('')+'</div>') : '')
      : empty(why))+'</div>');

  // 联盟 boss
  const bs=(S2.boss||{}).boss||[];
  c.push('<div class="card"><h2>联盟 Boss</h2>'
    + (bs.length? bs.map(b=>kv('点 '+esc(b.pointId), (b['在位']?'<span class="tag good">在位</span>':'<span class="tag">不在</span>')+' 次数 '+esc(b.num))).join('')
      : (Object.keys(S2.boss||{}).length? empty('暂无 Boss') : empty(why)))+'</div>');

  // 进行中的队列
  const running=(st.queues||[]).filter(q=>q.running);
  c.push('<div class="card"><h2>进行中的队列 <span class="sub">'+(st.queues||[]).length+' 个槽位</span></h2>'
    + (running.length? running.map(q=>kv(esc(q.type_name||qtype(q.type)), dur(q.totalTime)+(q.building_name?(' <span class="dim">'+esc(q.building_name)+'</span>'):''))).join('')
      : ((st.queues||[]).length? empty('当前没有进行中的队列') : empty(why)))+'</div>');

  // 功能概览
  const ov=(S2.overview||{})['队列']||[];
  const byType={};
  ov.forEach(x=>{ const k=(x['类型']||otype(x.type)); (byType[k]=byType[k]||[]).push(x['进度']); });
  c.push('<div class="card"><h2>功能概览</h2>'
    + (Object.keys(byType).length? Object.keys(byType).map(k=>kv(esc(k), byType[k].map(esc).join(' · '))).join('')
      : empty(why))+'</div>');

  $('cards').innerHTML=c.join('');
}

/* 监控卡片: 每张卡可折叠 + 内容没变就不重绘(避免每 5 秒闪一下) */
const CARD_SIG={};
function renderCardsStable(st){
  const S2=st.states||{};
  const running=(st.queues||[]).filter(q=>q.running);
  // 用关键状态做签名, 变了才重画整块
  const sig=JSON.stringify([
    S2.dailySign, S2.dailyQuest, S2.lordTask, S2.storyTask, S2.boss,
    running.map(q=>[q.uuid,q.totalTime,q.type]), S2.overview
  ]);
  if(CARD_SIG.main===sig) return;
  CARD_SIG.main=sig;
  renderCards(st);
  // 给每张监控卡挂上折叠按钮
  document.querySelectorAll('#cards .card').forEach((c,i)=>{
    if(c.querySelector('.fold')) return;
    if(!c.querySelector('h2')) return;
    const id='cardMon'+i;
    c.id=id;
    const h=c.querySelector('h2');
    const b=document.createElement('button');
    b.className='fold'; b.dataset.fold=id; b.textContent='－'; b.title='折叠/展开';
    /* 标题改成两段式 .hd/.hdTools —— 静态卡片已经是这个结构, 动态卡补上,
       否则折叠按钮会绝对定位到卡片角上、和 sumline 挤在一行。
       (顺序：先把 h2 挪进 .hd-t，再把整块 .hd 插到卡片最前面) */
    const tools=document.createElement('div');
    tools.className='hdTools';
    tools.appendChild(b);
    const row=document.createElement('div');
    row.className='hd-t';
    h.parentNode.insertBefore(row, h);
    row.appendChild(h);
    const hd=document.createElement('div');
    hd.className='hd';
    hd.appendChild(row);
    hd.appendChild(tools);
    c.insertBefore(hd, c.firstChild);
  });
  applyFold();
  applyMonSummaries(st);
}

/* 监控卡的折叠摘要: 折叠后也能看到关键数字 */
function applyMonSummaries(st){
  const S2=st.states||{};
  const ds=S2.dailySign||{}, dq=S2.dailyQuest||{}, lt=S2.lordTask||{};
  const summaries=[
    ()=> ds['今日已签']===true?'已签':(ds['今日已签']===false?'未签':''),
    ()=> ((dq['周任务可领奖励']||[]).length)?((dq['周任务可领奖励']||[]).length+' 个周奖励可领'):'',
    ()=> ((dq['可领日常任务']||[]).length)?((dq['可领日常任务']||[]).length+' 个日常可领'):'',
    ()=> ((lt['可领奖励']||[]).length)?((lt['可领奖励']||[]).length+' 个可领'):'',
    ()=> (S2.storyTask&&S2.storyTask['章节名'])?S2.storyTask['章节名']:'',
    ()=> (((S2.boss||{}).boss||[]).length)?(((S2.boss||{}).boss||[]).length+' 个 Boss'):'',
    ()=> { const r=(st.queues||[]).filter(q=>q.running).length; return r?(r+' 个进行中'):''; },
    ()=> { const ov=(S2.overview||{})['队列']||[]; return ov.length?(ov.length+' 类'):''; },
  ];
  document.querySelectorAll('#cards .card').forEach((c,i)=>{
    const h=c.querySelector('h2');
    if(!h) return;
    let s=h.querySelector('.sumline');
    if(!s){ s=document.createElement('span'); s.className='sumline';
             h.insertBefore(s,h.querySelector('.fold')); }
    s.textContent=(summaries[i]?summaries[i]():'');
  });
}

function renderQueues(st){
  const sel=$('selQueue'), cur=sel.value;
  const run=(st.queues||[]).filter(q=>q.running);
  const list=run.length?run:(st.queues||[]);
  sel.innerHTML=list.map(q=>`<option value="${esc(q.uuid)}">${esc(q.type_name||qtype(q.type))} · ${dur(q.totalTime)}${q.building_name?' · '+esc(q.building_name):''}</option>`).join('')
    ||'<option value="">（无队列）</option>';
  if(cur) sel.value=cur;
}

function renderItems(st){
  const sel=$('selItem'), cur=sel.value;
  const its=st.items||[];
  sel.innerHTML=its.map(x=>`<option value="${esc(x.uuid)}" data-cnt="${esc(x.count)}">${esc(x.name||x.itemId)} · x${esc(x.count)}${x.label?(' · '+esc(x.label)):''}</option>`).join('')
    ||'<option value="">（背包为空）</option>';
  if(cur) sel.value=cur;
  const cnt=$('inpCount');
  if(cnt && sel.selectedElement){
    const d=sel.selectedElement.dataset.cnt;
    if(d) cnt.max=Math.max(1,Number(d));
  }
  // 背包数据来源/时间: 让人知道这是实时读的还是快照
  const bs=st.bag_source||{};
  const hint=$('bagHint');
  if(hint){
    hint.textContent = bs.file
      ? ('背包数据来源: '+bs.label+(bs.detail?(' · '+bs.detail):'')+' · 共 '+its.length+' 种')
      : '背包数据不可用(需要手机连上后用 dump_bag.py 采集)';
  }
  // 保护罩下拉的数据新鲜度提示(共用 st.bag_at: login.init 快照时间)
  const shb=$('shieldBagHint');
  if(shb){
    if(!st.bag_at){
      shb.innerHTML='<span style="color:#e5484d">背包列表尚未拉取 —— 点「刷新道具」拉一次真实背包</span>';
    }else{
      shb.textContent='背包数据: '+hhmmss(st.bag_at/1000)+' 拉取'
        +(Date.now()/1000-st.bag_at>3600?(' · 已过期 '+Math.floor((Date.now()/1000-st.bag_at)/3600)+' 小时，建议刷新'):'');
    }
  }
}

function renderShield(st){
  const sh=st.shield||{};
  const end=sh.end_ms||0;
  const now=Date.now();
  const left=Math.max(0,end-now);
  const untilTxt=end?(' · 到期 '+ts(end)):'';
  $('shieldHint').innerHTML='当前状态: '+(left>0?('<span class="tag good">罩中 · 还剩 '+dur(left)+'</span>'):'<span class="tag">当前无罩</span>')
    +untilTxt+' · 自动开罩 '+(sh.autoshield?'<span class="tag good">开</span>':'<span class="tag">关</span>')
    // 推送监听心跳: 被攻击的响应速度就靠它(没有它推送要等下一轮轮询才被发现)
    +(sh.autoshield?(' · 推送监听 '+(sh.watch_interval||20)+'s'
      +(sh.watch_ticks!=null?(' · 已 '+sh.watch_ticks+' 次'):'')
      +(sh.persistent?'':' <span class="tag bad">非常驻连接, 收不到推送</span>')):'');
  // 保护罩道具下拉: 显示背包里实际持有的保护罩道具 + 库存数量
  const specSel=$('selShieldSpec');
  const items=sh.backpack_items||[];
  if(specSel){
    const sig=items.map(x=>x.itemId+':'+x.count).join(',');
    if(specSel.dataset.sig!==sig){
      specSel.dataset.sig=sig;
      const cur=specSel.value;
      specSel.innerHTML=items.map(x=>
        `<option value="${esc(x.itemId)}">${esc(x.name)}${x.duration?(' · '+esc(x.duration)):''} · 库存 ${esc(x.count)}</option>`
      ).join('')||'<option value="">（背包中没有保护罩道具）</option>';
      if(cur) specSel.value=cur;
    }
  }
  // 槽位信息提示（只读，不再作为主要交互）
  const slotHint=$('shieldSlotHint');
  if(slotHint){
    const configured=(sh.slots||[]).filter(s=>(s.items||[]).length>0);
    const noStock=configured.filter(s=>(s.items||[]).some(i=>i.no_stock));
    slotHint.textContent=configured.length
      ? ('已配置 '+configured.length+' 个槽位'
         +(noStock.length?(' · <span style="color:#e5484d">有槽位道具库存为 0，开罩会失败</span>'):''))
      : '未配置槽位';
  }
  // 背包数据新鲜度: 保护罩列表来自 login.init 快照, 没拉过时列表不可信
  const bagHint=$('shieldBagHint');
  if(bagHint){
    if(!sh.bag_at){
      bagHint.innerHTML='<span style="color:#e5484d">背包列表尚未拉取 —— 点「刷新道具」拉一次真实背包(login.init 约需 45 秒)</span>';
    }else{
      const bt=new Date(sh.bag_at*1000);
      bagHint.textContent='背包数据: '+hhmmss(sh.bag_at/1000)+' 拉取'
        +(Date.now()/1000-sh.bag_at>3600?(' · 已过期 '+Math.floor((Date.now()/1000-sh.bag_at)/3600)+' 小时，建议刷新'):'');
    }
  }
  // 自动开罩的代价说明: 它靠服务端推送, 必须常驻连接
  const ah=$('shieldAutoHint');
  if(ah){
    if(sh.autoshield){
      ah.style.display='';
      ah.innerHTML='自动开罩已开: 网页会<b>保持常驻连接</b>来接收「被攻击」推送，'
        +'所以 App 会被顶下线、网页轮询也会变慢 —— 这是收推送的必要代价。';
    }else{
      ah.style.display='none';
    }
  }
}

/* 港口(码头航海贸易) */
function renderDock(st){
  const dk=st.dock||{};
  const box=$('dockList');
  if(!box) return;
  const ships=dk.ships||[];
  if(dk.disabled){
    box.innerHTML='<div class="empty">'+esc(dk.note||'港口功能未开启')
      +' —— 服务端还没开放这个功能</div>';
  }else if(dk.error){
    box.innerHTML='<div class="empty">读取港口失败: '+esc(dk.error)+'</div>';
  }else if(!ships.length){
    box.innerHTML='<div class="empty">没有船只(可能港口还没解锁, 或账号没有贸易港)</div>';
  }else{
    const cls={0:'',1:'',2:'warn',3:'good'};
    box.innerHTML='<table class="sqtable"><thead><tr><th>#</th><th>状态</th><th>载货</th><th>加速</th></tr></thead><tbody>'
      + ships.map((s,i)=>{
          // 码头宝箱(type=0 的那格)不是船, 是港口活动奖励位:
          // 显示"当前奖励物品 + 到下一次刷新的倒计时", 不显示"空载"。
          if(s.is_activity){
            const rt=s.rewardTime||0;
            const cd=(rt>1e12)?Math.max(0,rt-Date.now()):0;
            const cdTxt=(rt>1e12)?(cd>0?(' <span class="mini">'+dur(cd)+'后刷新</span>')
                                       :' <span class="mini">(可领取)</span>'):'';
            const cargo=esc(s.cargo_text||'码头宝箱');
            return '<tr><td>'+(i+1)+'</td>'
              +'<td><span class="tag good">'+esc(s.state_text||'码头宝箱')+'</span>'+cdTxt+'</td>'
              +'<td class="mini">'+cargo+'</td>'
              +'<td class="mini">-</td></tr>';
          }
          const left=(s.endTime&&s.endTime>1e12)?Math.max(0,s.endTime-Date.now()):0;
          const t=(s.state===2)?(' <span class="mini">'+(left?dur(left):'—')+'</span>'):'';
          // state=3 = 有奖励但还没领
          const tag=(s.state===3)?' <span class="mini">(未领取)</span>':'';
          const cargo=esc(s.cargo_text||s.itemId||'空载');
          return '<tr><td>'+(i+1)+'</td>'
            +'<td><span class="tag '+(cls[s.state]||'')+'">'+esc(s.state_text||'未知')+'</span>'+t+tag+'</td>'
            +'<td class="mini">'+cargo+'</td>'
            +'<td class="mini">'+esc(s.speedTimes?('加速 '+s.speedTimes):'-')+'</td></tr>';
        }).join('')
      + '</tbody></table>';
  }
  // 上次领取明细: 领了多少 / 哪些没领到(刷新页面后仍在)
  const rbox=$('dockResult');
  if(rbox){
    const lr=dk.last_reward;
    if(lr){
      const got=(lr.rewards||[]).map(g=>'<li>领到: '+esc(g.name||g.itemId)
        +(g.addNum?(' ×'+esc(String(g.addNum))):'')
        +(g.from?(' <span class="mini">('+esc(g.from)+')</span>'):'')+'</li>').join('');
      const miss=(lr.unclaimed||[]).map(u=>'<li>未领取: '+esc((u.state_text||'可领奖')+' · '+(u.uuid||'').slice(0,8))+'</li>').join('');
      rbox.innerHTML='<div class="mini">上次领取 @'+esc(ts(lr.at))+' · 本次可领 '+(lr.pending||0)
        +' 条 · 实领 '+(lr.count||0)+' 条</div>'
        +(lr.cargo?('<div class="mini">'+esc(lr.cargo)+'</div>'):'')
        +(got?'<ul class="mini">'+got+'</ul>':'')
        +(miss?'<ul class="mini">'+miss+'</ul>':'')
        +((!got&&!miss)?'<div class="mini">没有可领取的奖励</div>':'');
    }else{
      rbox.innerHTML='';
    }
  }
  const hint=$('dockHint');
  if(hint){
    if(dk.disabled){
      hint.textContent='港口功能未开启 —— 自动领取/自动分派已自动停用(每轮空转没有意义)';
    }else{
      // 码头宝箱(港口活动奖励位): 奖励物品 + 下次刷新倒计时
      const act=ships.find(s=>s.is_activity);
      const cg=dk.cargo||{};
      let cgTxt='';
      if(act){
        const rt=act.rewardTime||0;
        const cd=(rt>1e12)?Math.max(0,rt-Date.now()):0;
        cgTxt=' · 码头宝箱 '+(act.cargo_text||'')
          +(rt>1e12?(cd>0?(' · '+dur(cd)+'后刷新'):' · 可领取'):'')
          +(act.times?(' · 今日已领 '+act.times+' 次'):'');
      }else if(cg.itemId){
        cgTxt=' · 码头宝箱 '+cg.itemId+(cg.count?(' ×'+cg.count):'');
      }
      hint.textContent=(dk.family?('命令族 '+dk.family+' · '):'')
        +'空闲 '+(dk.idle||0)+' 条 · 贸易中 '+(dk.trading||0)+' 条 · '
        +'可领奖 '+(dk.rewardable||0)+' 条(未领取)'
        +(dk.shipLimit?(' · 船位上限 '+dk.shipLimit):'')
        +cgTxt
        +(dk.last_auto?(' · '+dk.last_auto):'')
        +(dk.autoReward||dk.autoSend?(' · 自动: 领='+(dk.autoReward?'开':'关')+' 派='+(dk.autoSend?'开':'关')):'');
    }
  }
  // 有可领的就把按钮点亮提示(码头宝箱也算"可领取")
  const rb=$('btnDockReward');
  if(rb){
    const n=(dk.rewardable||0)+(dk.cargo_claimable?1:0);
    rb.classList.toggle('primary', n>0);
    rb.textContent = n>0 ? ('一键领取 ('+n+')') : '一键领取';
  }
}

/* 天空之境(TheHeavens): 探索 / 领取 */
function renderSky(st){
  const sk=st.sky||{};
  const box=$('skyList');
  if(!box) return;
  // 状态机: 0 空闲 / 1 探索中 / 2 完成未领奖
  const stateTag={0:'info',1:'warn',2:'good'};
  if(sk.disabled){
    box.innerHTML='<div class="empty">'+esc(sk.note||'天空之境读取失败/未开启')+'</div>';
  }else if(sk.error){
    box.innerHTML='<div class="empty">读取天空之境失败: '+esc(sk.error)+'</div>';
  }else if(!sk.ok){
    box.innerHTML='<div class="empty">点「刷新」读取天空之境状态</div>';
  }else{
    const remain=(sk.state===1&&sk.remain)?(' <span class="mini">'+dur(sk.remain*1000)+'后完成</span>'):'';
    box.innerHTML='<table class="sqtable"><tbody>'
      +'<tr><td>状态</td><td><span class="tag '+(stateTag[sk.state]||'')+'">'
        +esc(sk.state_text||'未知')+'</span>'+remain+'</td></tr>'
      +(sk.exploreLv!=null?('<tr><td>探索等级</td><td>'+esc(String(sk.exploreLv))+'</td></tr>'):'')
      +((sk.has_general!=null||sk.has_reward!=null)?('<tr><td>探索准备</td><td class="mini">'
        +'英雄 '+(sk.has_general?'<span class="tag good">已选</span>':'<span class="tag bad">未选</span>')
        +' · 奖励 '+(sk.has_reward?'<span class="tag good">已选</span>':'<span class="tag bad">未选</span>')
        +'</td></tr>'):'')
      +((sk.needPower!=null)?('<tr><td>战力</td><td class="mini">'+esc(String(sk.curPower!=null?sk.curPower:'?'))
        +' / 需 '+esc(String(sk.needPower))+'</td></tr>'):'')
      +(sk.family?('<tr><td>命令族</td><td class="mini">'+esc(sk.family)+(sk.new?' (新版)':' (旧版)')+'</td></tr>'):'')
      +'</tbody></table>';
  }
  const hint=$('skyHint');
  if(hint){
    if(sk.disabled){
      hint.textContent='天空之境未开启或命令不被服务端接受 —— 自动功能已停用';
    }else if(sk.ok){
      // 空闲但不能探索时, 把真实原因讲清楚(没选英雄/奖励/等级/战力)
      let base;
      if(sk.state===2) base='有可领取的探索奖励';
      else if(sk.state===1) base='探索进行中';
      else if(sk.can_explore) base='空闲, 可开始探索';
      else base='空闲, 但暂不能探索'+(sk.explore_reason?('('+sk.explore_reason+')'):'');
      hint.textContent=base
        +(sk.last_auto?(' · '+sk.last_auto):'')
        +(' · 自动: 领='+(sk.autoReward?'开':'关')+' 探='+(sk.autoExplore?'开':'关'));
    }else{
      hint.textContent='-';
    }
  }
  // 探索按钮: 只在"探索中"或旧版命令族时禁用, 其余一律放行 ——
  // 具体前提(英雄/奖励/战力)由服务端裁定, 不用反编译猜测去拦(会误伤已配置好的账号)。
  const be=$('btnSkyExplore');
  if(be){
    const oldFamily=(sk.ok&&!sk.new);
    const busy=(sk.ok && sk.state===1);   // 探索中
    be.disabled=(oldFamily||busy);
    be.title=oldFamily
      ? '当前区服是旧版天空之境, 探索需先在游戏里选将/龙, 无法一键自动'
      : (busy ? '探索进行中, 完成后可再次探索'
              : '一次性探索(消耗战力/部队)');
  }
  // 有奖励可领就把领取按钮点亮
  const rb=$('btnSkyReward');
  if(rb){
    rb.classList.toggle('primary', !!sk.can_reward);
    rb.textContent = sk.can_reward ? '一键领取 (1)' : '一键领取';
  }
  // 自动探索开着时亮出风险提示
  const warn=$('skyWarn');
  if(warn) warn.style.display = sk.autoExplore ? 'block' : 'none';
}

/* 积分商城(积分好礼): 积分任务奖励 */
function renderScore(st){
  const sc=st.score||{};
  const box=$('scoreList');
  if(!box) return;
  const tasks=sc.tasks||[];
  if(sc.error||sc.errorCode){
    box.innerHTML='<div class="empty">读取积分商城失败: '+esc(sc.error||sc.errorCode)+'</div>';
  }else if(!sc.ok){
    box.innerHTML='<div class="empty">点「刷新」读取积分商城</div>';
  }else if(!tasks.length){
    // 响应里没有 taskArr: 把真实字段名摆出来, 方便对照修正
    box.innerHTML='<div class="empty">没有积分任务'
      +(sc.has_taskArr?'':(' · 响应字段: '+esc((sc.keys||[]).join(', ')||'-')))+'</div>';
  }else{
    box.innerHTML='<table class="sqtable"><thead><tr><th>任务</th><th>进度</th><th>状态</th></tr></thead><tbody>'
      +tasks.map(t=>{
        const tag=t.claimable?'<span class="tag good">可领取</span>'
                 :(t.claimed?'<span class="tag">已领取</span>':'<span class="tag warn">未完成</span>');
        return '<tr><td>'+esc(t.name||t.taskId||'-')+' <span class="mini">'+esc(t.taskId||'')+'</span></td>'
          +'<td class="mini">'+esc(String(t.cur!=null?t.cur:'-'))+' / '+esc(String(t.target!=null?t.target:'-'))+'</td>'
          +'<td>'+tag+'</td></tr>';
      }).join('')
      +'</tbody></table>';
  }
  const hint=$('scoreHint');
  if(hint){
    hint.textContent=sc.ok
      ? ('本月积分 '+(sc.monthIntegral!=null?sc.monthIntegral:'-')
         +' · 可领 '+(sc.claimable||0)+' · 已领 '+(sc.claimed||0)+'/'+(sc.total||0)
         +(sc.last_auto?(' · '+sc.last_auto):'')
         +' · 自动领='+(sc.autoClaim?'开':'关'))
      : '-';
  }
  const b=$('btnScoreClaim');
  if(b){
    const n=sc.claimable||0;
    b.classList.toggle('primary', n>0);
    b.textContent=n>0?('一键领取 ('+n+')'):'一键领取';
  }
  const sum=$('sumScore');
  if(sum) sum.textContent=sc.ok?('积分 '+(sc.monthIntegral!=null?sc.monthIntegral:'-')+' · 可领 '+(sc.claimable||0)):'';
}

/* 福利中心(每日好礼 / 龙之馈赠) */
function renderWelfare(st){
  const wf=st.welfare||{};
  const box=$('welfareList');
  if(!box) return;
  const rows=wf.rows||[];
  if(!wf.loaded){
    box.innerHTML='<div class="empty">还没读到福利中心数据(等下一轮轮询)</div>';
  }else if(wf.error){
    box.innerHTML='<div class="empty">读取福利中心失败: '+esc(wf.error)+'</div>';
  }else if(!rows.length){
    box.innerHTML='<div class="empty">福利中心没有可领的项目(账号可能没开这些活动)</div>';
  }else{
    const cls={};
    box.innerHTML='<table class="sqtable"><thead><tr><th>项目</th><th>状态</th><th>奖励</th></tr></thead><tbody>'
      + rows.map(r=>{
          const tag=(r.claimable?'<span class="tag good">'+esc(r.state)+'</span>'
                                 :'<span class="tag">'+esc(r.state)+'</span>');
          const rw=(r.rewards||[]).map(g=>esc(g.name||g.itemId||'')+(g.num!=null?(' ×'+esc(String(g.num))):'')).join(', ');
          return '<tr><td>'+esc(r.name)+'</td>'
            +'<td>'+tag+(r.note?(' <span class="mini">'+esc(r.note)+'</span>'):'')+'</td>'
            +'<td class="mini">'+esc(rw||'-')+'</td></tr>';
        }).join('')
      + '</tbody></table>';
  }
  const hint=$('welfareHint');
  if(hint){
    hint.textContent=(wf.claimable?('可领 '+wf.claimable+' 项'):'今天都领完了')
      +(wf.last_auto?(' · '+wf.last_auto):'')
      +' · 自动领: '+(st.autoWelfare?'开':'关');
  }
  const btn=$('btnWelfareClaim');
  if(btn){
    const n=wf.claimable||0;
    btn.classList.toggle('primary', n>0);
    btn.textContent = n>0 ? ('一键领取 ('+n+')') : '一键领取';
  }
}

/* ---------------- 一键完成(CityAssist 面板) ---------------- */
function renderAssist(st){
  const as=st.assist||{};
  const box=$('assistList');
  if(!box) return;
  const items=as.items||[];
  const sum=$('sumAssist');
  if(sum){
    const parts=[];
    if(as.auto){ parts.push('每天自动执行'+(as.lastDay?(' · 上次 '+as.lastDay):'(今日待执行)')); }
    else if(items.length){ const autoN=items.filter(i=>i.autoKind==='free').length; parts.push('面板 '+items.length+' 项 · 无损 '+autoN+' 项'); }
    sum.textContent=parts.join(' ');
  }
  if(!items.length){
    box.innerHTML='<div class="empty">面板清单还没读到（点「一键完成」或等下一轮轮询）</div>';
  }else{
    const groups={};
    items.forEach(it=>{ (groups[it.groupName||('组'+it.group)]=groups[it.groupName||('组'+it.group)]||[]).push(it); });
    const kindTag={auto:'<span class="tag good">自动</span>',
                   dock:'<span class="tag info">港口规则</span>',
                   manual:'<span class="tag">不自动</span>'};
    box.innerHTML=Object.keys(groups).map(g=>{
      const rows=groups[g].map(it=>{
        const stCls = it.state==='可收取'||it.state==='可执行' ? 'good' : '';
        return '<tr><td>'+esc(it.name)+'</td>'
          +'<td>'+(kindTag[it.autoKind]||'')+'</td>'
          +'<td class="mini">'+esc(it.cost||'')+'</td>'
          +'<td class="mini"><span class="tag '+stCls+'">'+esc(it.state||'')+'</span></td></tr>';
      }).join('');
      return '<div class="alblock"><div class="alhead">'+esc(g)+'</div>'
        +'<div class="aloverflow"><table class="sqtable"><thead><tr><th>项目</th><th>执行</th><th>代价</th><th>状态</th></tr></thead><tbody>'
        +rows+'</tbody></table></div></div>';
    }).join('');
  }
}

/* ---------------- 联盟(科技 / 任务板 / 捐献 / 使命) ---------------- */
function alCut(v,n){
  const t=String(v==null?'':v);
  return t.length>n ? (t.slice(0,n)+'…') : t;
}
function renderAlliance(st){
  const al=st.alliance||{};
  const box=$('allianceList');
  if(!box) return;
  const sum=$('sumAlliance');
  if(sum){
    const s=al.summary||{};
    sum.textContent = al.loaded
      ? ('在研科技 '+(s.researching||'无')+' · 任务位 '+(s.taskAcceptLeft||0)+' · 联盟积分 '+(s.alliancePoint||0))
      : '';
  }
  if(!al.loaded){
    box.innerHTML='<div class="empty">还没读到联盟数据(点「刷新」读一次)</div>';
  }else if(al.error){
    box.innerHTML='<div class="empty">读取联盟失败: '+esc(al.error)+'</div>';
  }else{
    const html=[];
    /* --- 科技 + 捐献面板 --- */
    const r=al.researching;
    html.push('<div class="alblock"><div class="alhead">联盟科技</div>');
    if(r){
      html.push('<div class="mini">在研 <b>'+esc(r.scienceId)+'</b> · 等级 '+esc(String(r.level))
        +' · 星级 '+esc(String(r.star))+' · 进度 '+esc(String(r.currentPro))+'/'+esc(String(r.needPro))
        +' ('+esc(String(r.percent))+'%)'+(r.full?' <span class="tag warn">已攒满</span>':'')
        +(r.speedUp?' <span class="tag good">加速中</span>':'')+'</div>');
    }else{
      html.push('<div class="mini">当前没有正在研究的联盟科技</div>');
    }
    const tiers=al.tiers||[];
    if(tiers.length){
      html.push('<div class="aloverflow"><table class="sqtable"><thead><tr><th>档位</th><th>消耗</th><th>联盟贡献</th><th>科技进度</th><th>状态</th></tr></thead><tbody>');
      tiers.forEach(t=>{
        const av=t.available;
        const stt = (av===1||av===true) ? '<span class="tag good">可捐</span>'
                 : (av===0 ? '<span class="tag">不可捐</span>' : '<span class="tag">默认</span>');
        html.push('<tr><td>'+esc(t.name)+'</td><td>'+esc(String(t.resName||('资源#'+t.res)))
          +' ×'+esc(String(t.num))+'</td><td>'+esc(String(t.contribute))+'</td><td>'+esc(String(t.progress))
          +'</td><td>'+stt+'</td></tr>');
      });
      html.push('</tbody></table></div>');
    }
    if(al.donateReason){
      html.push('<div class="alwarn">'+esc(al.donateReason)+'</div>');
    }
    html.push('</div>');

    /* --- 任务板 --- */
    const tk=al.task||{};
    const pub=tk.published||[], avl=tk.available||[];
    html.push('<div class="alblock"><div class="alhead">联盟任务板'
      +' <span class="mini">可接 '+esc(String(tk.acceptLeft||0))+' 个 · 还能接 '+esc(String(tk.leftRequestCount||0))
      +' 次 · 可发 '+esc(String(tk.publishLeft||0))+' 个</span></div>');
    if(!pub.length && !avl.length){
      html.push('<div class="empty">任务板上暂时没有任务</div>');
    }else{
      html.push('<div class="aloverflow"><table class="sqtable"><thead><tr><th>任务</th><th>发布人</th><th>奖励</th><th>状态</th></tr></thead><tbody>');
      pub.forEach(t=>{
        const stt = t.acceptUid ? '<span class="tag good">已接取</span>'
                 : (t.requested ? '<span class="tag good">已申请</span>' : '<span class="tag">可接取</span>');
        html.push('<tr><td title="'+esc(t.publishName||t.uid)+'">'+esc(alCut(t.publishName||t.uid,14))
          +'</td><td>'+esc(alCut(t.publishUid||'-',12))+'</td>'
          +'<td class="mini" title="'+esc(t.acceptReward||'')+'">'+esc(alCut(t.acceptReward||'-',26))
          +'</td><td>'+stt+'</td></tr>');
      });
      avl.forEach(t=>{
        html.push('<tr><td title="'+esc(t.publishName||t.uid)+'">'+esc(alCut(t.publishName||t.uid,14))
          +'</td><td>'+esc(alCut(t.publishUid||'-',12))+'</td>'
          +'<td class="mini" title="'+esc(t.baseReward||'')+'">'+esc(alCut(t.baseReward||'-',26))
          +'</td><td><span class="tag">我发布的</span></td></tr>');
      });
      html.push('</tbody></table></div>');
    }
    html.push('</div>');

    /* --- 使命 + 签到 --- */
    const ms=al.mission||{};
    const sg=ms.signIn||{};
    html.push('<div class="alblock"><div class="alhead">联盟使命</div>');
    html.push('<div class="mini">联盟签到: '+esc(String(sg.signIn_days||0))+' 天一轮 · '
      +(sg.signInReward_state==1?'<span class="tag good">今日已签</span>':'<span class="tag warn">今日未签</span>')
      +(sg.signIn_reward?(' · 奖励 '+esc(sg.signIn_reward)):'')+'</div>');
    const all=(ms.common||[]).concat(ms.random||[]);
    if(!all.length){
      html.push('<div class="empty">没有联盟使命</div>');
    }else{
      html.push('<div class="aloverflow"><table class="sqtable"><thead><tr><th>使命</th><th>当前</th><th>阶段</th></tr></thead><tbody>');
      all.forEach(m=>{
        const stg=(m.stages||[]).map(s=>'<span class="tag '+(s.claimed?'good':(s.reached?'good':''))+'">'
          +esc(String(s.target))+'</span>').join(' ');
        html.push('<tr><td>'+esc(m.missionId)+'</td><td>'+esc(String(m.currentValue))
          +'</td><td>'+stg+'</td></tr>');
      });
      html.push('</tbody></table></div>');
    }
    html.push('</div>');

    /* --- 捐献排行 + 资源池 + 商店 --- */
    const rk=al.donateRank||[];
    html.push('<div class="alblock"><div class="alhead">捐献排行 / 联盟资源</div>');
    if(rk.length){
      html.push('<table class="sqtable"><thead><tr><th>#</th><th>玩家</th><th>今日捐献</th><th>联盟荣誉</th></tr></thead><tbody>');
      rk.slice(0,8).forEach(t=>{
        html.push('<tr><td>'+esc(String(t.rank||'-'))+'</td><td>'+esc(t.name||t.uid)+'</td><td>'
          +esc(String(t.donation))+'</td><td>'+esc(String(t.alliance_honor))+'</td></tr>');
      });
      html.push('</tbody></table>');
    }
    const res=al.res||{};
    const rk2=Object.keys(res);
    if(rk2.length){
      html.push('<div class="mini">联盟资源池: '+rk2.map(k=>esc(res[k].name||('资源#'+k))
        +' '+esc(String(res[k].have))+(res[k].max?('/'+esc(String(res[k].max))):'')).join(' · ')+'</div>');
    }
    const sh=al.shop||{};
    html.push('<div class="mini">联盟商店: 联盟积分 '+esc(String(sh.alliancePoint||0))
      +' · 商品 '+esc(String((sh.goods||[]).length))+' 件</div>');
    html.push('</div>');

    box.innerHTML=html.join('');
  }
  const hint=$('allianceHint');
  if(hint){
    const s=al.summary||{};
    hint.textContent = al.loaded
      ? ('在研科技 '+(s.researching||'无')+' · 任务位 '+(s.taskAcceptLeft||0)+'/'
         +((al.task&&al.task.record&&al.task.record.maxAcceptCount)||0)
         +' · 捐献: '+(s.donateReady?'可捐':(s.donateReason||'不可')))
      : '-';
  }
  const dbtn=$('btnAllianceDonate');
  if(dbtn){
    dbtn.disabled = !al.donateReady;
    dbtn.title = al.donateReady ? '给在研科技随机捐一档(消耗资源)' : (al.donateReason||'当前不能捐');
    dbtn.textContent = al.autoTier==='random' ? '随机捐献' : ('捐献·'+(al.autoTier||'low'));
  }
  const ahint=$('allianceAutoHint');
  if(ahint){
    const a=al.auto||{};
    const tierName={random:'随机',cheapest:'最省资源',low:'低档',mid:'中档',high:'高档'}[al.autoTier||'random'];
    if(a.at){
      const when=new Date(a.at*1000).toLocaleTimeString();
      const done=(a.acted||[]).length;
      ahint.innerHTML='自动捐献: '+(al.autoEnabled?'<b>开</b>':'关')
        +' · 档位 '+(tierName||'随机')+' · 单轮上限 '+(al.autoMax||20)+' 次'
        +'<br>上次 '+(when)+' · '+(done?('捐了 '+done+' 次'):'没有捐成')
        +(a.stop?(' · '+esc(a.stop)):'')
        +(a.capReached?' <span class="tag good">已达上限</span>':'');
    }else{
      ahint.textContent='自动捐献: '+(al.autoEnabled?'开':'关')+' · 档位 '+(tierName||'随机')
        +' · 单轮上限 '+(al.autoMax||20)+' 次'
        +' · 进度满就停, 不会花金币重置科技';
    }
  }
  const sbtn=$('btnAllianceSignIn');
  if(sbtn){
    sbtn.disabled = !!al.signInDone;
    sbtn.textContent = al.signInDone ? '今日已签到' : '领取联盟签到';
    sbtn.title = al.signInDone ? ('已连续签到 '+(al.signIn&&al.signIn.signIn_days||0)+' 天') : '领取今天的联盟签到奖励';
  }
  const abtn=$('btnAllianceAccept');
  if(abtn){
    const n=((al.task&&al.task.published)||[]).filter(t=>!t.acceptUid&&!t.requested).length;
    abtn.textContent = n>0 ? ('一键接任务 ('+n+')') : '一键接任务';
  }
}

function renderEvents(st){
  const evs=st.events||[];
  const box=$('logs');
  if(!box) return;
  const filter=EV_FILTER;
  const shown=filter==='all'?evs:evs.filter(e=>e.kind===filter);
  // 签名带上"最后一条的 kind": 只有长度 + 时间戳时, 同一秒内到达的**不同**事件
  // 会被当成"没变化"直接跳过 —— 表现就是新事件刷不出来, 得清空筛选才看到。
  const lastEv=shown.length?shown[shown.length-1]:null;
  const sig=shown.length+':'+(lastEv?lastEv.ts:'')+':'
    +(lastEv?String(lastEv.kind||''):'')+':'+filter;
  if(sig===EV_SIG) return;
  EV_SIG=sig;
  const cnt=$('logCount');
  if(cnt) cnt.textContent=shown.length+' 条'+(filter==='all'?'':' / 共 '+evs.length);
  if(!shown.length){
    box.innerHTML='<div class="empty">'+(evs.length?'当前筛选下没有事件':'还没有事件。连上游戏服后, 签到/领奖/开罩/被打等情况会实时出现在这里。')+'</div>';
    return;
  }
  const cls={connected:'s',error:'e',warning:'w',state:'k'};
  box.innerHTML=shown.slice(-200).map(e=>{
    const c=cls[e.kind]||'';
    let d=e.data;
    if(typeof d==='object'){ try{ d=JSON.stringify(d); }catch(_){ d=String(d); } }
    return '<div><span class="t">'+esc(e.ts)+'</span> <span class="'+c+'">'+esc(e.kind)+'</span> '+esc(String(d).slice(0,400))+'</div>';
  }).join('');
  box.scrollTop=box.scrollHeight;
}

/* ---------------- 主刷新 ---------------- */
async function refresh(silent){
  let st=null;
  try{ st=await api('/api/state'); }
  catch(e){
    const dot=$('connDot'), txt=$('connText');
    if(dot){ dot.className='dot off'; txt.textContent='控制台无响应'; }
    if(!silent) toast('控制台无响应: '+(e&&e.message?e.message:e),'err');
    return null;
  }
  if(!st) return null;
  if(st.error==='unauthorized'){ $('connText').textContent='token 无效'; return null; }
  S.state=st;
  renderHeader(st); renderAccounts(st); renderFleet(st); renderCardsStable(st); renderTaskStats(st); renderQueues(st); renderItems(st);
  renderShield(st); renderEvents(st); renderHunt(st); renderDock(st); renderSky(st); renderWelfare(st); renderScore(st); renderAlliance(st); renderAssist(st);
  renderStaminaItems(st.stamina_items);
  renderOverview(st); renderSummaries(st); renderScan(st);
  if(!silent) $('sLast').title='页面读取时间';
  return st;
}

/* 切换账号后: 后台那一轮同步要走一个网络往返才完成, 单刷一次多半还是旧的
   离线态。这里短时追刷几次, 一旦"已连接/拿到数据"就停, 避免来回切换时
   顶灯在"离线 -> 已连接"之间空等 5 秒定时轮询。*/
async function refreshUntilConnected(tries, gapMs){
  tries=tries||6; gapMs=gapMs||800;
  for(let i=0;i<tries;i++){
    const st=await refresh(true);
    if(st && (st.connected || st.has_data)) return st;
    if(st && (st.disconnected || st.account_error)) return st; // 明确离线态就别空刷
    await new Promise(r=>setTimeout(r,gapMs));
  }
  return S.state;
}

/* ---------------- 操作 ---------------- */
$('btnRefresh').onclick=async()=>{
  await busy($('btnRefresh'),'连接游戏服…',async()=>{
    const r=await api('/api/action',{action:'refresh-now'});
    if(r.ok){ toast('已刷新 · '+(r.note||''),'ok'); }
    else { toast(r.note||'刷新失败','warn'); }
    await refresh(true);
  });
};
$('btnReconnect').onclick=async()=>{
  await busy($('btnReconnect'),'重连…',async()=>{
    const r=await api('/api/action',{action:'reconnect'});
    toast(r.ok?'已重连':(r.error||'重连失败'), r.ok?'ok':'err');
    await refresh(true);
  });
};
$('btnDisconnect').onclick=async()=>{
  await busy($('btnDisconnect'),'断开中…',async()=>{
    const r=await api('/api/action',{action:'disconnect'});
    toast(r.ok?('已断开 · '+(r.note||'')):(r.error||'断开失败'), r.ok?'ok':'err');
    await refresh(true);
  });
};
/* 账号切换: 下拉和多账号总览卡片共用同一条路径 */
async function switchAccount(key, label){
  if(!key) return;
  // 切换瞬间先把顶灯打成"切换中", 不要让旧账号的"已连接/离线"残留误导
  const dot=$('connDot'), txt=$('connText');
  if(dot){ dot.className='dot wait'; txt.textContent='切换账号中…'; }
  const r=await api('/api/action',{action:'account-switch',key});
  toast(r.ok?('已切到 '+(label||r.label||key)):(r.error||'切换失败'), r.ok?'ok':'err');
  ACCT_SIG='';           // 强制下一次重建下拉(selected 会变)
  ARMY_LOADED=false;     // 库存是每个号自己的 -> 切号后要重读
  // 后端已在切换时催目标引擎同步一次; 这里短时追刷, 连上就停
  await refreshUntilConnected();
}
$('acctSelect').addEventListener('change',e=>switchAccount(e.target.value));
/* 队伍编成: 用这个编队(把选中的编队号写回游戏) */
$('btnPresetApply').onclick=async()=>{
  const idx=$('selSquadPreset').value;
  if(!idx){ toast('先选一个编队','warn'); return; }
  await busy($('btnPresetApply'),'写入中…',async()=>{
    // ⚠️ 写的是**槽位索引**, 不是编成串 —— 游戏客户端存的就是索引,
    //    写编成串会把游戏面板的设置写坏(客户端 atoi 后越界, 直接丢弃)。
    const r=await api('/api/action',{action:'hunt',op:'set-format',format:String(idx)});
    if(r&&r.ok!==false){
      setRes('resHunt','已把游戏「自动打怪」的编队设成 编队'+idx+' · 之后游戏会自己用这个编队','ok');
      toast('游戏里现在用 编队'+idx,'ok');
    }else{
      setRes('resHunt','写回失败: '+((r&&(r.error||r.errorCode))||'未知'),'err');
      toast('写回失败','err');
    }
    await refresh(true);
  });
};
/* 可派兵种: 刷新 */
/* 账号: ＋ 从设备入库(一次加手机上所有渠道包的号) */
$('btnAcctAdd').onclick=async()=>{
  const label=(prompt('给新账号起个名字(留空用角色名/UID; 加了多个包时这个名字会忽略):')||'').trim();
  await busy($('btnAcctAdd'),'读设备…',async()=>{
    const r=await api('/api/action',{action:'account-add-device',label});
    if(r.ok){
      const names=(r.added||[]).map(a=>a.label||a.key);
      toast('已加入: '+(names.join('、')||r.label||r.key),'ok');
      if((r.skipped||[]).length) toast('跳过: '+r.skipped.join('; '),'warn');
    }else{
      toast((r.error||'添加失败')+(r.detail&&r.detail.length?(' — '+r.detail.join('; ')):''),'err');
    }
    ACCT_SIG='';
    await refresh(true);
  });
};
/* 账号: － 删除当前账号 */
$('btnAcctDel').onclick=async()=>{
  const a=(S.state&&S.state.accounts)||{};
  const key=a.active||a.current||'';
  if(!key){ toast('没有可删除的账号','warn'); return; }
  const cur=(a.list||[]).find(x=>x.key===key);
  if(!confirm('从账号库删除「'+((cur&&cur.label)||key)+'」? (不会动已扫到的数据)')) return;
  const r=await api('/api/action',{action:'account-remove',key});
  toast(r.ok?'已删除':(r.error||'删除失败'), r.ok?'ok':'err');
  ACCT_SIG='';
  await refresh(true);
};
/* 账号: ⏻ 开/关当前账号的后台运行(并行) */
$('btnAcctParallel').onclick=async()=>{
  const a=(S.state&&S.state.accounts)||{};
  const key=a.active||a.current||'';
  if(!key){ toast('先选一个账号','warn'); return; }
  const cur=(a.list||[]).find(x=>x.key===key);
  const on=!(cur&&cur.parallel);   // 翻转
  const r=await api('/api/action',{action:'account-parallel',key,on});
  if(r.ok){ toast(on?'已在后台运行':'已停止后台运行','ok'); }
  else { toast(r.error||'操作失败','err'); }
  ACCT_SIG='';
  await refresh(true);
};
/* 账号: 🔑 渠道账号密码登录 —— 纯 PC, 不用手机/模拟器 */
let CHAN_SID='', CHAN_ITEMS=[], CHAN_NAME='果盘';
/* 渠道下拉: 从后端拉档案(cok_channels.py), 协议模块没就绪的标出来 */
async function chanLoadChannels(){
  const sel=$('chanSel');
  try{
    const r=await api('/api/action',{action:'channel-list'});
    const list=(r&&r.channels)||[];
    if(!list.length){ sel.innerHTML='<option value="guopan">果盘</option>'; return; }
    sel.innerHTML=list.map(c=>{
      const dis=c.ready?'':' disabled';
      const tip=c.ready?(c.note||''):((c.note||'')+' · 协议模块未就绪');
      return '<option value="'+esc(c.id)+'"'+dis+' title="'+esc(tip)+'">'+esc(c.name)+'</option>';
    }).join('');
  }catch(e){
    sel.innerHTML='<option value="guopan">果盘</option>';
  }
  chanSyncChannelLabel();
}
function chanSyncChannelLabel(){
  const sel=$('chanSel');
  const opt=sel.options[sel.selectedIndex];
  const name=opt?opt.textContent:'渠道';
  CHAN_NAME=name;
  $('chanAcctLbl').textContent=name+'账号';
  $('chanAcct').placeholder=name+'账号';
  $('chanTtl').textContent='渠道登录 · '+name;
}
/* 页脚(「添加选中」按钮)是弹窗的直接子元素, 固定在弹窗底部;
   显隐要跟列表一起切 —— 还没列出游戏号时不该出现。 */
function chanFootShow(on){ const f=$('chanFoot'); if(f) f.style.display=on?'flex':'none'; }
function chanOpen(){
  $('chanRes').style.display='none';
  $('chanRes').innerHTML='';
  $('chanListWrap').style.display='none'; chanFootShow(false);
  $('chanList').innerHTML='';
  CHAN_SID=''; CHAN_ITEMS=[];
  $('chanOvl').classList.add('show');
  chanLoadChannels();
  setTimeout(()=>$('chanAcct').focus(),30);
}
function chanClose(){ $('chanOvl').classList.remove('show'); }
$('btnChanLogin').onclick=chanOpen;
$('chanClose').onclick=chanClose;
$('chanSel').onchange=chanSyncChannelLabel;
$('chanOvl').addEventListener('click',e=>{ if(e.target===$('chanOvl')) chanClose(); });
/* 游戏号列表: 每行一个复选框; 已在控制台/没角色的行不可选 */
function chanSelCount(){ return CHAN_ITEMS.filter(i=>i._sel).length; }
function chanSyncFoot(){
  $('chanAdd').textContent='添加选中('+chanSelCount()+')';
  const addable=CHAN_ITEMS.filter(i=>!i.hasCharacter).length;
  $('chanListNote').textContent= addable? ('有 '+addable+' 个还没在游戏里开过号, 需先开号') : '';
}
function chanRenderList(items){
  CHAN_ITEMS=items||[];
  const box=$('chanList');
  if(!CHAN_ITEMS.length){
    box.innerHTML='<div class="mnote">这个账号下没有列出任何游戏号(可能还没在 COK 里开过号)。</div>';
    $('chanListWrap').style.display='block'; chanFootShow(true);
    chanSyncFoot(); return;
  }
  box.innerHTML=CHAN_ITEMS.map((it,idx)=>{
    const can=!!it.hasCharacter;
    const tag= can ? (it.inLibrary?'<span class="mtag have">已在控制台</span>'
                              :'<span class="mtag new">可添加</span>')
                   : '<span class="mtag no">未开号</span>';
    const meta= can
      ? ('gameUid <code>'+esc(it.gameUid||'')+'</code> · 区服 '+esc(it.zn||'')+
         (it.gameUserLevel?(' · 等级 '+esc(it.gameUserLevel)):'')+
         (it.uuid?(' · uuid <code>'+esc(it.uuid)+'</code>'):'')+
         '<br>pfId <code>'+esc(it.pfId||'')+'</code>')
      : ('pfId <code>'+esc(it.pfId||'')+'</code><br>'+esc(it.note||'游戏服还没有这个身份的角色'));
    return '<label class="mitem'+(can?'':' dis')+(it._sel?' sel':'')+'" data-i="'+idx+'">'+
             '<input type="checkbox" '+(it._sel?'checked':'')+(can?'':' disabled')+'>'+
             '<div class="mbody"><div class="mtitle">'+esc(it.roleName||it.name||'(无名)')+tag+'</div>'+
             '<div class="mmeta">'+meta+'</div></div></label>';
  }).join('');
  box.querySelectorAll('.mitem').forEach(el=>{
    el.addEventListener('click',ev=>{
      const it=CHAN_ITEMS[+el.dataset.i];
      if(!it||!it.hasCharacter) return;
      if(ev.target.tagName==='INPUT'){ it._sel=ev.target.checked; }
      else { it._sel=!it._sel; }
      el.classList.toggle('sel',!!it._sel);
      const cb=el.querySelector('input'); if(cb) cb.checked=!!it._sel;
      chanSyncFoot();
    });
  });
  $('chanListWrap').style.display='block'; chanFootShow(true);
  chanSyncFoot();
}
$('chanSelAll').onclick=()=>{
  CHAN_ITEMS.forEach(it=>{ if(it.hasCharacter && !it.inLibrary) it._sel=true; });
  chanRenderList(CHAN_ITEMS);
};
async function chanSubmit(){
  const channel=$('chanSel').value||'guopan';
  const account=$('chanAcct').value.trim();
  const password=$('chanPwd').value;
  if(!account||!password){ toast('请填写账号和密码','warn'); return; }
  await busy($('chanSubmit'),'登录中…',async()=>{
    const r=await api('/api/action',{action:'channel-login',channel,account,password});
    const box=$('chanRes'); box.style.display='block';
    $('chanListWrap').style.display='none'; chanFootShow(false);
    if(!r.ok){
      box.className='res err';
      box.innerHTML='<b>失败</b> · '+esc(r.error||'未知错误');
      toast(r.error||'登录失败','err');
      return;
    }
    if(r.succeeded){
      CHAN_SID=r.sessionId||'';
      box.className='res ok';
      const cn=r.channelName||CHAN_NAME||'渠道';
      let h='<b>'+esc(cn)+'登录成功</b> · 账号 '+esc(r.account||'');
      if(r.guopanUid) h+=' · 果盘UID '+esc(r.guopanUid);
      h+='<br><span class="dim">'+esc(r.note||'')+'</span>';
      box.innerHTML=h;
      chanRenderList(r.smallAccounts||[]);
      toast('已列出游戏号, 勾选后添加','ok');
    }else{
      box.className='res warn';
      box.innerHTML='<b>协议正常, 登录未通过</b>'
        +(r.bizCodes&&r.bizCodes.length?'<br>业务码: <code>'+esc(r.bizCodes.join(', '))+'</code>':'')
        +'<br><span class="dim">'+esc(r.note||'')+'</span>';
      toast('登录未通过(账号/密码?)','warn');
    }
  });
}
async function chanAdd(){
  const ids=CHAN_ITEMS.filter(i=>i._sel&&i.hasCharacter).map(i=>i.perGameId);
  if(!ids.length){ toast('先勾选要添加的游戏号','warn'); return; }
  await busy($('chanAdd'),'添加中…',async()=>{
    const r=await api('/api/action',{action:'channel-add',sessionId:CHAN_SID,perGameIds:ids});
    if(!r.ok){ toast(r.error||'添加失败','err'); return; }
    toast('已添加: '+(r.added||[]).map(a=>a.label||a.key).join(', '),'ok');
    const box=$('chanRes');
    box.className='res ok';
    let h='<b>已加入控制台</b>';
    (r.added||[]).forEach(a=>{ h+='<br>'+esc(a.label||a.key)+' · gameUid <code>'+esc(a.gameUid||'')+'</code>'; });
    if((r.skipped||[]).length) h+='<br><span class="dim">跳过: '+esc(r.skipped.join('; '))+'</span>';
    box.innerHTML=h;
    $('chanListWrap').style.display='none'; chanFootShow(false);
    $('chanPwd').value='';
    ACCT_SIG='';
    await refresh(true);
  });
}
$('chanAdd').onclick=chanAdd;
$('chanSubmit').onclick=chanSubmit;
$('chanPwd').addEventListener('keydown',e=>{ if(e.key==='Enter') chanSubmit(); });
$('btnSign').onclick=async()=>{
  await busy($('btnSign'),'签到中…',async()=>{
    const r=await api('/api/action',{action:'sign'});
    const ok=r.ok!==false;
    setRes('resAssist', ok?('已触发签到: '+(r.note||'')):('签到失败: '+(r.error||'')), ok?'ok':'err');
    toast(ok?'已触发签到':'签到失败: '+(r.error||''), ok?'ok':'err');
    await refresh(true);
  });
};
$('btnClaim').onclick=async()=>{
  await busy($('btnClaim'),'领奖中…',async()=>{
    const r=await api('/api/action',{action:'claim'});
    const ok=r.ok!==false;
    setRes('resAssist', ok?('已触发领奖: '+(r.note||'')):('领奖失败: '+(r.error||'')), ok?'ok':'err');
    toast(ok?'已触发领奖':'领奖失败: '+(r.error||''), ok?'ok':'err');
    await refresh(true);
  });
};
// 领地辅助 - 一键完成(等同游戏里那个按钮: 按面板顺序逐项执行)
$('btnAssistOneKey').onclick=async()=>{
  const costly=!!($('chkAssistCostly')&&$('chkAssistCostly').checked);
  if(costly && !confirm('连消耗项一起跑?\n\n'+
      '英雄试炼 / 龙塔试炼 / 研习 / 招募 / 献祭 会消耗金币、道具或体力。\n'+
      '确定要一起执行吗?')) return;
  await busy($('btnAssistOneKey'),'一键完成中…',async()=>{
    const r=await api('/api/action',{action:'assist-onekey',costly:costly});
    const ok=r.ok!==false;
    let msg='';
    if(r.steps&&r.steps.length){
      msg=r.steps.map(s=>(s['项']||'')+'：'+(s['结果']||'')+(s['详情']?('('+s['详情']+')'):'')).join('；');
    } else msg=(r.note||r.error||'');
    setRes('resAssist', ok?msg:('失败: '+(r.error||msg)), ok?'ok':'err');
    toast(ok?msg:('一键完成失败: '+(r.error||'')), ok?'ok':'err');
    await refresh(true);
  });
};
$('btnSpeed').onclick=async()=>{
  const q=$('selQueue').value, it=$('selItem').value, c=parseInt($('inpCount').value||'1',10);
  if(!q||!it){ toast('需要选择队列和道具','err'); setRes('resSpeed','需要先选队列和道具','err'); return; }
  if(!confirm('确认用道具加速该队列？\n会立即完成队列并消耗道具。')) return;
  await busy($('btnSpeed'),'加速中…',async()=>{
    const r=await api('/api/action',{action:'speedup',uuid:q,itemUuid:it,count:c});
    const ok=r.ok!==false;
    setRes('resSpeed', ok?('加速成功 · '+($('selItem').selectedOptions[0]?$('selItem').selectedOptions[0].text:'')):('失败: '+(r.error||JSON.stringify(r.result||'').slice(0,120))), ok?'ok':'err');
    toast(ok?'加速成功':'加速失败', ok?'ok':'err');
    await refresh(true);
  });
};
$('btnSpeedGold').onclick=async()=>{
  const q=$('selQueue').value;
  if(!q){ toast('需要选择队列','err'); setRes('resSpeed','需要先选队列','err'); return; }
  if(!confirm('确认用金币加速？\n会实扣金币。')) return;
  await busy($('btnSpeedGold'),'加速中…',async()=>{
    const r=await api('/api/action',{action:'speedup',uuid:q,gold:true,qtype:1});
    const ok=r.ok!==false;
    setRes('resSpeed', ok?'金币加速成功':('失败: '+(r.error||'')), ok?'ok':'err');
    toast(ok?'金币加速成功':'金币加速失败', ok?'ok':'err');
    await refresh(true);
  });
};
$('btnShield').onclick=async()=>{
  const slot=1, cover=$('chkCover').checked?1:0;
  const spec=$('selShieldSpec').value||'';
  if(!spec){ toast('先选保护罩规格','err'); setRes('resShield','需要先选保护罩规格','err'); return; }
  if(!confirm('确认开保护罩？\n规格: '+(($('selShieldSpec').selectedOptions[0]||{}).text||spec)
    +'\n槽位 '+slot+'\n会真实消耗 1 个保护罩道具。')) return;
  await busy($('btnShield'),'开罩中…',async()=>{
    const r=await api('/api/action',{action:'shield',slot:slot,coverOld:cover,spec:spec});
    const ok=r.ok!==false;
    const note=(r.notes&&r.notes.length)?(' · '+r.notes.join(' · ')):'';
    setRes('resShield', ok?('保护罩已开启(槽位 '+slot+')'+note+(r.shieldEndTime?(' · 到期 '+ts(r.shieldEndTime)):''))
                          :('失败: '+(r.error||'')), ok?'ok':'err');
    toast(ok?'保护罩已开启':'开罩失败', ok?'ok':'err');
    await refresh(true);
  });
};
$('btnSlots').onclick=async()=>{
  await busy($('btnSlots'),'拉背包中(约 45 秒)…',async()=>{
    // 背包列表 = login.init 实时快照(保护罩道具 + 真实数量都在里面)
    const r=await api('/api/action',{action:'bag-refresh'});
    const ok=r&&r.ok!==false;
    setRes('resShield', ok?(r.note||'背包拉取中…'):('拉背包失败: '+(r.error||'')), ok?'ok':'err');
    toast(ok?'已发起拉取, 完成后列表自动更新':'拉背包失败', ok?'ok':'err');
  });
};
$('btnDockReward').onclick=async()=>{
  await busy($('btnDockReward'),'领取中…',async()=>{
    const r=await api('/api/action',{action:'dock',op:'reward'});
    const ok=r.ok!==false;
    const box=$('dockResult');
    if(ok){
      const rw=r.rewards||[];
      const un=r.unclaimed||[];
      if(!rw.length && !un.length){
        setRes('resDock','没有可领取的奖励(没有船在等待)'
          +(r.cargo?(' · '+r.cargo):''),'warn');
        toast('没有可领取的奖励','warn');
        if(box) box.innerHTML='<div class="mini">上次领取: 没有可领取的奖励</div>';
      }else{
        let msg='已领取 '+(rw.length||r.count||0)+' 条';
        if(un.length) msg+=' · 仍有 '+un.length+' 条未领取';
        setRes('resDock', msg, 'ok');
        toast(msg, 'ok');
        if(box){
          const got=rw.map(g=>'<li>领到: <b>'+esc(g.name||g.itemId)+'</b> ×'+esc(g.addNum)+'</li>').join('');
          const miss=un.map(s=>'<li>未领取: '+esc(s.uuid||'?')+' ('+esc(s.state_text||'')+')</li>').join('');
          box.innerHTML='<div class="mini" style="margin-top:6px"><b>上次领取</b>'
            +(got?'<ul style="margin:3px 0 0 16px;padding:0">'+got+'</ul>':'')
            +(miss?'<ul style="margin:3px 0 0 16px;padding:0">'+miss+'</ul>':'')
            +'</div>';
        }
      }
    }else{
      const why=r.errorText||r.errorCode||r.error||'未知错误';
      setRes('resDock','领取失败: '+why,'err');
      toast('领取失败: '+why,'err');
      if(box) box.innerHTML='<div class="mini" style="margin-top:6px;color:#f0d59a">上次领取失败: '+esc(why)+'</div>';
    }    await refresh(true);
  });
};
$('btnDockSend').onclick=async()=>{
  if(!confirm('确认一键分派船只？\n会**派出空闲的船**(消耗载货/资源)。')) return;
  await busy($('btnDockSend'),'分派中…',async()=>{
    const r=await api('/api/action',{action:'dock',op:'send'});
    const ok=r.ok!==false;
    const n=r.count||0;
    setRes('resDock', ok?('已一键分派'+(n?(' '+n+' 条'):'')):('分派失败: '+(r.errorText||r.errorCode||r.error||'')), ok?'ok':'err');
    toast(ok?'已分派':'分派失败', ok?'ok':'err');
    await refresh(true);
  });
};
$('btnDockRefresh').onclick=async()=>{
  await busy($('btnDockRefresh'),'读取中…',async()=>{
    const r=await api('/api/action',{action:'dock',op:'read'});
    const ok=r.ok!==false;
    setRes('resDock', ok?('港口: 空闲 '+(r.idle||0)+' · 贸易中 '+(r.trading||0)+' · 可领 '+(r.rewardable||0))
                        :('读取失败: '+(r.error||'')), ok?'ok':'err');
    toast(ok?'港口已刷新':'读取失败', ok?'ok':'err');
    await refresh(true);
  });
};
$('btnSkyReward').onclick=async()=>{
  await busy($('btnSkyReward'),'领取中…',async()=>{
    const r=await api('/api/action',{action:'sky',op:'reward'});
    const ok=r.ok!==false;
    if(ok){
      const rw=r.rewards||[];
      if(!rw.length){
        setRes('resSky','没有可领取的探索奖励','warn');
        toast('没有可领取的奖励','warn');
      }else{
        const msg='已领取探索奖励 '+(rw.length||r.count||0)+' 项';
        setRes('resSky', msg+' · '+rw.map(g=>esc(g.name||g.itemId)+(g.count?('×'+g.count):'')).join(', '), 'ok');
        toast(msg,'ok');
      }
    }else{
      const why=r.errorText||r.errorCode||r.error||'未知错误';
      setRes('resSky','领取失败: '+why,'err'); toast('领取失败: '+why,'err');
    }
    await refresh(true);
  });
};
$('btnSkyExplore').onclick=async()=>{
  if(!confirm('确认开始探索？\n探索会按服务端规则**消耗战力/部队**(不是零成本)。')) return;
  await busy($('btnSkyExplore'),'探索中…',async()=>{
    const r=await api('/api/action',{action:'sky',op:'explore'});
    const ok=r.ok!==false;
    setRes('resSky', ok?('已开始探索 · 当前'+(r.state_text||'探索中'))
                       :('探索失败: '+(r.errorText||r.errorCode||r.error||'')), ok?'ok':'err');
    toast(ok?'已开始探索':'探索失败', ok?'ok':'err');
    await refresh(true);
  });
};
$('btnSkyRefresh').onclick=async()=>{
  await busy($('btnSkyRefresh'),'读取中…',async()=>{
    const r=await api('/api/action',{action:'sky',op:'read'});
    const ok=r.ok!==false;
    setRes('resSky', ok?('天空之境: '+(r.state_text||'已读取')+(r.family?(' · '+r.family):''))
                       :('读取失败: '+(r.errorText||r.errorCode||r.error||'功能可能未开启')), ok?'ok':'err');
    toast(ok?'已刷新':'读取失败', ok?'ok':'err');
    await refresh(true);
  });
};
$('btnWelfareClaim').onclick=async()=>{
  await busy($('btnWelfareClaim'),'领取中…',async()=>{
    const r=await api('/api/action',{action:'welfare',op:'claim'});
    const acted=r.acted||[];
    if(r.ok!==false && acted.length){
      setRes('resWelfare','已领取: '+acted.join('; '),'ok');
      toast('已领取 '+acted.length+' 项','ok');
    }else{
      setRes('resWelfare', (r.error||'没有可领取的福利(今天都领过了)'),'warn');
      toast('没有可领取的福利','warn');
    }
    await refresh(true);
  });
};
$('btnWelfareRefresh').onclick=async()=>{
  await busy($('btnWelfareRefresh'),'读取中…',async()=>{
    const r=await api('/api/action',{action:'welfare',op:'read'});
    const v=r.view||{};
    setRes('resWelfare', r.ok!==false?('可领 '+(v.claimable||0)+' 项'):('读取失败: '+(r.error||'')),
            r.ok!==false?'ok':'err');
    toast(r.ok!==false?'福利中心已刷新':'读取失败', r.ok!==false?'ok':'err');
    await refresh(true);
  });
};
$('btnAllianceRefresh').onclick=async()=>{
  await busy($('btnAllianceRefresh'),'读取中…',async()=>{
    const r=await api('/api/action',{action:'alliance',op:'read'});
    setRes('resAlliance', r.ok!==false?'联盟数据已刷新':('读取失败: '+(r.error||'')),
            r.ok!==false?'ok':'err');
    toast(r.ok!==false?'联盟已刷新':'读取失败', r.ok!==false?'ok':'err');
    await refresh(true);
  });
};
$('btnAllianceAccept').onclick=async()=>{
  await busy($('btnAllianceAccept'),'接取中…',async()=>{
    const r=await api('/api/action',{action:'alliance',op:'accept-all'});
    const res=(r.result||{});
    const acted=res.acted||[], failed=res.failed||[];
    if(acted.length){
      setRes('resAlliance','已接取: '+acted.join(', ')+(failed.length?(' · 失败 '+failed.join(', ')):''),'ok');
      toast('接取 '+acted.length+' 个任务','ok');
    }else{
      setRes('resAlliance', failed.length?('接取失败: '+failed.join(', '))
              :((res.note||'没有可接的任务(任务位已满或没有新任务)')),'warn');
      toast('没有接取到任务','warn');
    }
    await refresh(true);
  });
};
$('btnAllianceDonate').onclick=async()=>{
  await busy($('btnAllianceDonate'),'捐献中…',async()=>{
    const st=(S&&S.state)||{};
    const al=st.alliance||{};
    const sid=(al.summary||{}).researching||((al.researching||{}).scienceId)||'';
    if(!sid){ setRes('resAlliance','当前没有正在研究的联盟科技','warn'); toast('没有在研科技','warn'); return; }
    const tier=(al.autoTier||'random');
    const r=await api('/api/action',{action:'alliance',op:'donate',scienceId:sid,tier:tier});
    if(r.ok!==false){
      const rs=(r.result||{});
      setRes('resAlliance','捐献成功('+(rs.tierName||rs.tier||tier)+')','ok');
      toast('捐献成功','ok');
    }else{
      const txt=r.errorText||r.error||'捐献失败';
      setRes('resAlliance','捐献失败: '+txt+(r.errorCode?(' ('+r.errorCode+')'):''),'warn');
      toast('捐献失败: '+txt,'warn');
    }
    await refresh(true);
  });
};
$('btnAllianceSignIn').onclick=async()=>{
  await busy($('btnAllianceSignIn'),'签到中…',async()=>{
    const r=await api('/api/action',{action:'alliance',op:'sign-in'});
    if(r.ok!==false){
      const n=(r.result||{}).count||0;
      setRes('resAlliance','联盟签到成功, 领到 '+n+' 项奖励','ok');
      toast('联盟签到成功','ok');
    }else{
      const txt=r.errorText||r.error||'签到失败';
      setRes('resAlliance','联盟签到失败: '+txt,'warn');
      toast('联盟签到失败: '+txt,'warn');
    }
    await refresh(true);
  });
};
$('btnAllianceDonateAuto').onclick=async()=>{
  await busy($('btnAllianceDonateAuto'),'自动捐献中…',async()=>{
    const st=(S&&S.state)||{};
    const al=st.alliance||{};
    const r=await api('/api/action',{action:'alliance',op:'donate-auto',tier:al.autoTier||'random'});
    const rs=(r.result||{});
    const acted=rs.acted||[];
    if(r.ok!==false && acted.length){
      const names=acted.map(a=>a.tierName||a.tier).join('、');
      setRes('resAlliance','自动捐献: 捐了 '+acted.length+' 次('+names+')'+(rs.stop?(' · '+rs.stop):''),'ok');
      toast('捐了 '+acted.length+' 次','ok');
    }else{
      const txt=r.errorText||r.error||rs.stop||'没有捐成';
      setRes('resAlliance','自动捐献: '+txt,'warn');
      toast('自动捐献: '+txt,'warn');
    }
    await refresh(true);
  });
};
$('btnAllianceHelpAll').onclick=async()=>{
  await busy($('btnAllianceHelpAll'),'发送中…',async()=>{
    const r=await api('/api/action',{action:'alliance',op:'help-all'});
    if(r.ok!==false){
      setRes('resAlliance','已帮助联盟全体','ok'); toast('已帮助全体','ok');
    }else{
      const txt=r.errorText||r.error||'操作失败';
      setRes('resAlliance','操作失败: '+txt,'warn'); toast('操作失败: '+txt,'warn');
    }
    await refresh(true);
  });
};
$('btnScoreClaim').onclick=async()=>{
  await busy($('btnScoreClaim'),'领取中…',async()=>{
    const r=await api('/api/action',{action:'score',op:'claim-all'});
    if(r.ok===false){
      const why=r.errorText||r.errorCode||r.error||'未知错误';
      setRes('resScore','读取失败: '+why,'err'); toast('积分商城读取失败: '+why,'err');
    }else if(!r.pending){
      setRes('resScore','没有可领取的积分任务','warn'); toast('没有可领取的积分任务','warn');
    }else{
      const got=(r.rewards||[]).map(g=>(g.name||g.itemId)+(g.num!=null?('×'+g.num):'')).join(', ');
      const msg='已领取 '+(r.claimed||0)+'/'+(r.pending||0)+' 个积分任务'
        +(r.failed?(' · 失败 '+r.failed+' 个'):'')+(got?(' · '+got):'');
      setRes('resScore', msg, r.failed?'warn':'ok'); toast(msg, r.failed?'warn':'ok');
    }
    await refresh(true);
  });
};
$('btnScoreRefresh').onclick=async()=>{
  await busy($('btnScoreRefresh'),'读取中…',async()=>{
    const r=await api('/api/action',{action:'score',op:'read'});
    const ok=r.ok!==false;
    setRes('resScore', ok?('本月积分 '+(r.monthIntegral!=null?r.monthIntegral:'-')+' · 可领 '+(r.claimable||0)+' 个任务')
                       :('读取失败: '+(r.errorText||r.errorCode||r.error||'')), ok?'ok':'err');
    toast(ok?'积分商城已刷新':'读取失败', ok?'ok':'err');
    await refresh(true);
  });
};

$('btnTestHook').onclick=async()=>{
  const type=$('selHookType').value, url=$('inpHook').value.trim();
  if(!url){ toast('先填 Webhook URL','err'); setRes('resHook','需要先填 Webhook URL','err'); return; }
  await busy($('btnTestHook'),'发送中…',async()=>{
    const r=await api('/api/action',{action:'hook-test',type:type,url:url});
    const ok=r.ok!==false;
    setRes('resHook', ok?('测试已发送: '+type):('发送失败: '+(r.error||'')), ok?'ok':'err');
    toast(ok?'测试已发送':'发送失败', ok?'ok':'err');
  });
};
$('btnFind').onclick=async()=>{
  const lv=parseInt($('selMonster').value||'1',10);
  await busy($('btnFind'),'搜索中…',async()=>{
    const r=await api('/api/action',{action:'hunt',op:'find',level:lv});
    const ok=!!r.ok;
    setRes('resHunt', ok?('找到 '+lv+' 级'+(r.name?(' '+r.name):'')+' 坐标 '+r.x+','+r.y):('没找到: '+(r.errorCode||'无结果')), ok?'ok':'warn');
    toast(ok?('坐标 '+r.x+','+r.y):'没找到该等级野怪', ok?'ok':'warn');
  });
};
$('btnLv').onclick=async()=>{
  const lo=parseInt($('inpLvLow').value||'1',10), hi=parseInt($('inpLvHigh').value||'1',10);
  if(lo>hi){ toast('下限不能大于上限','err'); setRes('resHunt','下限不能大于上限(现在是 '+lo+' - '+hi+')','err'); return; }
  await busy($('btnLv'),'保存中…',async()=>{
    const r=await api('/api/action',{action:'hunt',op:'set-level',low:lo,high:hi});
    const ok=!!r.ok;
    setRes('resHunt', ok?('等级范围已设为 '+r.lv):('失败: '+(r.error||'')), ok?'ok':'err');
    toast(ok?('等级范围 '+r.lv):'保存失败', ok?'ok':'err');
    await refresh(true);
  });
};

/* ---------------- 巨型狮鹫 · 集结 ---------------- */
let RALLY_STATE=null;
let RALLY_LEVEL='0';      // 0 = 全部等级
function rallyBosses(r){
  const all=(r&&r.bosses)||[];
  if(RALLY_LEVEL==='0') return all;
  return all.filter(b=>String(b.level)===RALLY_LEVEL);
}
function renderRally(r){
  if(!r||r.ok===false){ $('rallyHint').textContent='读取失败: '+(r&&r.error||'未知'); return; }
  RALLY_STATE=r;
  // 集结时间档位(服务端下发的 4 档, 每次都读)
  const slotSel=$('selRallySlot');
  const slots=r.slots||[];
  const sig=slots.map(s=>s.slot+':'+s.minutes).join(',');
  if(slotSel.dataset.sig!==sig){
    slotSel.dataset.sig=sig;
    slotSel.innerHTML=slots.map(s=>`<option value="${s.slot}">${s.minutes} 分钟(第 ${s.slot} 档)</option>`).join('')
      ||'<option value="1">5 分钟</option>';
  }
  // 等级下拉(巨型狮鹫有 12/21/30/35 级, 等级差很多, 必须让用户挑)
  const lvSel=$('selRallyLevel');
  const lvAll=(r.bosses||[]);
  const lvList=[];
  lvAll.forEach(b=>{ if(b.level!=null && !lvList.some(x=>String(x)===String(b.level))) lvList.push(b.level); });
  lvList.sort((a,b)=>a-b);
  const lvSig=lvList.join(',');
  if(lvSel.dataset.sig!==lvSig){
    lvSel.dataset.sig=lvSig;
    const prev=RALLY_LEVEL;
    lvSel.innerHTML='<option value="0">全部</option>'+lvList.map(l=>`<option value="${l}">${l} 级</option>`).join('');
    lvSel.value=(prev!=null && [...lvSel.options].some(o=>o.value===String(prev)))?prev:'0';
    RALLY_LEVEL=lvSel.value;
  }
  // 目标下拉: 已知的巨型狮鹫(按等级过滤)
  const bossSel=$('selRallyBoss');
  const bosses=rallyBosses(r);
  const bsig=bosses.map(b=>b.index+':'+b.level+':'+b.hp+':'+(b.busy?1:0)).join(',');
  if(bossSel.dataset.sig!==bsig){
    const prev=bossSel.value;
    bossSel.dataset.sig=bsig;
    bossSel.innerHTML=bosses.map(b=>{
      const hp=(b.hp!=null&&b.maxHp)?(' · 血量 '+fmt(b.hp)+'/'+fmt(b.maxHp)):'';
      const busy=b.busy?' · [已有集结]':'';
      return `<option value="${b.index}">${b.level} 级巨型狮鹫${hp}${busy}</option>`;
    }).join('') ||'<option value="">没扫到该等级的巨型狮鹫</option>';
    if(prev && bosses.some(b=>String(b.index)===prev)) bossSel.value=prev;
    else{
      // 默认挑一个**没有集结**的(同一目标只能一支), 优先等级低的
      const free=bosses.find(b=>!b.busy);
      if(free) bossSel.value=String(free.index);
    }
  }
  const mine=r.my_rallies||[];
  const cnt=r.rally_count||0;
  const sc=r.scan||{};
  let html;
  if(mine.length){
    const m=mine[0];
    html='<span class="tag good">集结中</span> 已建 1 支集结'
      +(m.monsterId?(' · 目标 '+m.monsterId):'')
      +(m.wait_minutes?(' · 等待 '+m.wait_minutes+' 分钟'):'')
      +(m.totalTroops?(' · '+fmt(m.totalTroops)+' 兵'):'')
      +'<br><span class="mini">同一目标只能有一支集结, 打完才能再发</span>';
  }else if(bosses.length){
    html='已知 '+bosses.length+' 只巨型狮鹫 · 联盟现有集结 '+cnt+' 支'
      +(sc.known?(' · 已扫 '+sc.known+' 只'):'')
      +'<br><span class="mini">集结 = 联盟成员一起打, 时间越长盟友越容易加入</span>';
  }else{
    html='<span class="mini">还没扫到该等级的巨型狮鹫, 点「扫描」刷新</span>';
  }
  if(r.stamina!=null) html+='<br><span class="mini">体力 '+fmt(r.stamina)+' · 每次集结消耗 '+fmt(r.stamina_cost||20)+'</span>';
  $('rallyHint').innerHTML=html;
}
$('selRallyLevel').onchange=()=>{
  RALLY_LEVEL=$('selRallyLevel').value;
  if(RALLY_STATE){ renderRally(RALLY_STATE); }
};
$('btnRallyScan').onclick=async()=>{
  await busy($('btnRallyScan'),'扫描中…',async()=>{
    const r=await api('/api/action',{action:'hunt',op:'rally-state',force:true});
    renderRally(r);
    const n=(r.bosses||[]).length;
    toast(n?('已知 '+n+' 只巨型狮鹫'):'没扫到巨型狮鹫', n?'ok':'warn');
  });
};
/* 集结状态不塞进主轮询(要发 world.get 拉地块, 会拖慢刷新),
   只在「打野怪」卡可见时每隔几秒按需拉一次。 */
let RALLY_TIMER=null;
function scheduleRally(){
  if(RALLY_TIMER){ clearInterval(RALLY_TIMER); RALLY_TIMER=null; }
  const panel=$('cardHunt');
  if(!panel) return;
  RALLY_TIMER=setInterval(async()=>{
    if(!panel.offsetParent) return;              // 卡被折叠/隐藏就不拉
    if(S.busy) return;
    try{ const r=await api('/api/action',{action:'hunt',op:'rally-state'}); renderRally(r); }
    catch(e){}
  }, 15000);
}
$('btnRallyStart').onclick=async()=>{
  const idx=$('selRallyBoss').value;
  if(!idx){ toast('没扫到巨型狮鹫, 先点「扫描」','err'); return; }
  const slot=parseInt($('selRallySlot').value||'1',10);
  const num=Math.max(1,parseInt($('inpRallyNum').value||'2000',10)||2000);
  const mins=((RALLY_STATE&&RALLY_STATE.slots)||[]).find(s=>s.slot===slot);
  const label=($('selRallyBoss').selectedOptions[0]||{}).textContent||idx;
  const lv=$('selRallyLevel').value;
  if(!confirm('确认发起集结？\n目标: '+label+'\n等级: '+(lv==='0'?'按目标':lv+' 级')
    +'\n集结时间: '+(mins?mins.minutes:slot)+' 分钟\n派兵: '+num+' 个'
    +'\n\n真实消耗士兵与体力(首领怪 20 体力/次), 并在联盟里建一个集结。')) return;
  await busy($('btnRallyStart'),'发起中…',async()=>{
    const r=await api('/api/action',{action:'hunt',op:'rally-start',index:parseInt(idx,10),slot:slot,num:num});
    const ok=!!r.ok;
    setRes('resHunt', ok?(r.note||'集结已发起'):('失败: '+(r.note||r.error||r.errorCode||'未知')), ok?'ok':'err');
    toast(ok?'集结已发起':(r.note||'发起失败'), ok?'ok':'err');
    if(ok){ const r2=await api('/api/action',{action:'hunt',op:'rally-state'}); renderRally(r2); }
  });
};
$('btnAutoStart').onclick=async()=>{
  const num=Math.max(1,parseInt($('inpPerType').value||'5000',10)||5000);
  const squads=Math.max(1,Math.min(8,parseInt($('inpSquads').value||'4',10)||4));
  const mix=Math.max(1,Math.min(4,parseInt($('inpHuntMix')&&$('inpHuntMix').value||'1',10)||1));
  const mx=parseInt($('inpHuntMax').value||'0',10);
  const mixTxt=mix>1?('每队最多 '+mix+' 种兵(混编)'):'每队只用一种兵';
  const autoStam=!!($('chkHuntAutoStamina')&&$('chkHuntAutoStamina').checked);
  const stamTxt=autoStam?'\n体力不足时会自动喝背包里的体力药水(会消耗药水)。':'';
  if(!confirm('确认开始打怪？\n'+squads+' 队并行, 每队最多 '+num+' 个兵, '+mixTxt+'。\n兵种按库存自动搭配, 库存不够会自动摊薄每队人数。\n真实消耗士兵与体力。'+stamTxt+'\n开启期间网页会占用账号连接，App 会被踢下线。')) return;
  await busy($('btnAutoStart'),'启动中…',async()=>{
    // 网页自己出征: 兵种由**后端**按可用库存自动搭配(数量 = min(每队兵数,
    // 该兵可用量)) —— 页面不填兵种。mix>=2 时每队可混编**多个同类兵种**。
    const lv=parseInt($('inpLvLow').value||'1',10);   // 目标野怪等级 = 等级范围下限
    const r=await api('/api/action',{action:'hunt',op:'auto-start',
                                      level:lv, num:num, squads:squads, maxKills:mx,
                                      mix:mix, autoStamina:autoStam});
    const ok=!!r.ok;
    setRes('resHunt', ok?(r.note||'已开始打怪'):('启动失败: '+(r.note||r.error||'')), ok?'ok':'err');
    toast(ok?(r.note||'已开始打怪'):(r.note||r.error||'启动失败'), ok?'ok':'err');
    await refresh(true);
  });
};
/* 体力药水: 同步背包里的道具实例(login.init 实时背包)。
   2026-11-17 服务器实测: login.init 就能直接拿到体力药水的实例 uuid + 数量,
   不再需要"领一份含药水的奖励"碰运气。 */
function renderStaminaItems(st){
  const el=$('staminaItemHint'); if(!el) return;
  if(!st||!st.known){ el.textContent='还没抓到药水的道具实例(点「同步体力药水」拉背包)'; return; }
  const gain={200380:10,200381:50,200382:100};
  const keys=Object.keys(st.items||{});
  const cnt=st.counts||{};
  const txt=keys.length?keys.map(k=>k+'(+'+gain[k]+'体力'+(cnt[k]!=null?' ×'+cnt[k]:'')+')').join('、'):(st.itemId||'');
  el.textContent='已抓到实例: '+(txt||st.itemId)+' · 每瓶 +'+(st.gain||0)+' 体力';
}
$('btnStaminaSync').onclick=async()=>{
  await busy($('btnStaminaSync'),'拉背包中(约 45 秒)…',async()=>{
    // 统一走 bag-refresh: 拉一次 login.init, 保护罩列表 + 药水 uuid/数量
    // 都从这一份快照里出(见后端 _refresh_bag_snapshot)
    const r=await api('/api/action',{action:'bag-refresh'});
    const ok=!!(r&&r.ok!==false);
    setRes('resHunt', ok?(r.note||'背包拉取中, 完成后自动更新'):(('同步失败: '+(r.error||'未知'))), ok?'ok':'err');
    toast(ok?'已发起拉取, 约 45 秒后自动更新':'同步失败', ok?'ok':'err');
    // 拉取是后台任务: 3 秒后刷新一次页面状态(完成时也会有事件推送)
    setTimeout(()=>refresh(true), 3000);
  });
};
/* 编队预设: 切编队 / 从游戏里读设置(读到的直接存进当前编队) */
$('selSquadPreset').onchange=async()=>{
  const idx=$('selSquadPreset').value;
  SQUAD_PRESET_SEL=idx;
  SETTINGS.squadPreset=idx;
  await api('/api/action',{action:'set-setting',key:'squadPreset',value:idx,seq:++SET_SEQ});
  renderSquadPresetView(null);
  if(idx){
    const p=squadPresets().find(x=>String(x.index)===String(idx));
    if(p&&p.spec&&p.spec.length){
      setRes('resHunt','已切到 '+p.name+'('+p.spec.length+' 队)','ok');
      toast('已切到 '+p.name,'ok');
    }else{
      setRes('resHunt','该编队还是空的 —— 点「读游戏当前编成」把游戏里的编成存进来','warn');
    }
  }
  await refresh(true);
};
$('btnPresetGame').onclick=async()=>{
  await busy($('btnPresetGame'),'读取中…',async()=>{
    const r=await api('/api/action',{action:'hunt',op:'autoqueue'});
    if(!r || r.ok===false){
      setRes('resHunt','读游戏设置失败: '+((r&&(r.error||r.errorCode))||'未知'),'err');
      toast('读游戏设置失败','err');
      return;
    }
    // 等级范围 / 并行队数: 一并用游戏里的
    if(r.lvLow){ $('inpLvLow').value=r.lvLow; $('inpLvHigh').value=(r.lvHigh||r.lvLow); }
    if(r.autoCount){ const sv=$('squadsView'); if(sv) sv.textContent=Math.min(8,Math.max(1,r.autoCount))+' 队'; }
    const sq=r.squads||[];
    const who=r.account||'当前账号';
    let msg='游戏里('+who+')的自动打怪设置: ';
    const idx=$('selSquadPreset').value;
    if(r.kind==='index'){
      // 游戏里存的是**槽位索引** —— 这是正常形式, 意思就是"用游戏里的编队N"
      const names=(r.indices||[]).map(i=>'编队'+i).join('、');
      msg+='用的是 '+names+' · ';
      // 把网页这边的下拉定位到游戏用的那个编队
      const first=(r.indices||[])[0];
      if(first && $('selSquadPreset')){
        $('selSquadPreset').value=String(first);
        SQUAD_PRESET_SEL=String(first);
        SETTINGS.squadPreset=String(first);
        await api('/api/action',{action:'set-setting',key:'squadPreset',value:String(first),seq:++SET_SEQ});
      }
    }else if(sq.length){
      msg+='编成 '+presetSpecText(sq)+' · ';
      if(idx){
        // 存进**当前账号**的编队桶(后端按账号分桶存, 不会串号)
        const sr=await api('/api/action',{action:'hunt',op:'autoqueue-store',
                                          index:String(idx), spec:sq});
        if(sr&&sr.ok!==false) msg+='已存进 编队'+idx+' · ';
        else msg+='存进 编队'+idx+' 失败 · ';
      }
    }else{
      msg+='这个号在游戏里没设过「自动打怪」的编成 · ';
    }
    msg+='等级 '+r.lvLow+'~'+r.lvHigh+' · 并行 '+r.autoCount+' 队';
    setRes('resHunt', msg+(r.note?('\n'+r.note):''), sq.length?'ok':'warn');
    if(r.kind==='army'){
      toast('游戏里的设置是编成串(被写坏的格式), 建议改回索引','warn');
    }else if(sq.length){
      toast('已读取游戏里的设置','ok');
    }else{
      toast('该账号在游戏里没设过自动打怪编成','warn');
    }
    await refresh(true);
  });
};
$('btnAutoStop').onclick=async()=>{
  await busy($('btnAutoStop'),'停止中…',async()=>{
    const r=await api('/api/action',{action:'hunt',op:'auto-stop'});
    const ok=!!r.ok;
    setRes('resHunt', ok?(r.note||'已停止'):('失败: '+(r.error||'')), ok?'ok':'warn');
    toast(ok?(r.note||'已停止'):'停止失败', ok?'ok':'err');
    await refresh(true);
  });
};

/* 玩家坐标查询 */
let LOCATE_CANDS=[];
let LAST_LOCATE=null;      // 上次查到的坐标, 给概览条显示
function renderLocate(res){
  const box=$('locateList');
  if(!box) return;
  if(!res){ box.innerHTML=''; return; }
  if(res.ok){
    const srcTxt={index:'本地索引',scan:'现场扫描',item:'道具查询',
                  'index+verified':'本地索引 + 服务端实时校验'}[res.source]||'';
    const ps=(res.players||[]);
    let extra='';
    if(ps.length>1){
      extra='<div class="mini" style="margin-top:5px">同名 '+ps.length+' 个, 点名字切换:</div>'
        +'<div>'+ps.map(p=>'<span class="tag info" data-locate-uid="'+esc(p.uid||'')+'" '
          +'style="cursor:pointer" title="'+esc(p.uid||'')+'">'+esc(p.name||p.uid||'?')
          +' ('+esc(p.x)+','+esc(p.y)+')</span>').join('')+'</div>';
    }
    box.innerHTML=ps.map(p=>
      '<div class="trow done" style="margin-top:4px">'
      +'<span class="ti n">✓</span>'
      +'<span class="tx"><b>'+esc(p.name||'(无名)')+'</b>'
      +'<span class="mini">坐标 X '+esc(p.x)+' · Y '+esc(p.y)
      +(p.level!=null?(' · 等级 '+esc(p.level)):'')+'</span></span>'
      +'<button data-copy="'+esc(p.x)+','+esc(p.y)+'" style="padding:3px 10px;font-size:12px">复制坐标</button>'
      +'</div>').join('')
      +'<div class="mini" style="margin-top:5px">来源: '+esc(srcTxt)
      +(res.index_total?(' · 索引共 '+esc(res.index_total)+' 人'):'')
      +(res.index_updated?(' · 更新于 '+esc(ts(res.index_updated*1000))):'')
      +(res.scan?(' · 扫描 '+esc(res.scan.requests)+' 次请求'):'')
      +(res.stale?(' · <span style="color:#e0a44a">索引坐标已过期(服务端重排过地图), 本次为现场扫描结果</span>'):'')
      +'</div>'+extra;
    const p0=ps[0];
    if(p0){
      LAST_LOCATE={name:p0.name, x:p0.x, y:p0.y};
      const sum=$('sumLocate');
      if(sum) sum.textContent=(p0.name||'')+' · '+p0.x+','+p0.y;
      if(S.state) renderOverview(S.state);
    }
  }else{
    // 优先显示人话提示(后端已给), 其次是错误码中文
    const why=res.error||res.errorText||res.errorCode||'查询失败';
    box.innerHTML='<div class="empty">'+esc(why)
      +(res.errorText&&res.error&&res.errorText!==res.error?(' ('+esc(res.errorText)+')'):'')
      +'<br><span class="mini">索引里没有这个人。可以点「扫描附近」用 world.get 扫一片区域建索引(不消耗任何道具)。</span></div>';
    const sum=$('sumLocate');
    if(sum) sum.textContent='';
  }
}
document.addEventListener('click',(e)=>{
  const cp=e.target.closest && e.target.closest('[data-copy]');
  if(cp){
    const txt=cp.getAttribute('data-copy');
    if(navigator.clipboard&&navigator.clipboard.writeText){
      navigator.clipboard.writeText(txt).then(()=>toast('已复制 '+txt,'ok'),
                                            ()=>toast('复制失败: '+txt,'warn'));
    }else{ toast('坐标: '+txt); }
    return;
  }
  const t=e.target.closest && e.target.closest('[data-locate-uid]');
  if(!t) return;
  const uid=t.getAttribute('data-locate-uid');
  const name=$('inpLocate').value.trim();
  if(!name) return;
  busy(null,'',async()=>{
    const r=await api('/api/action',{action:'locate',name:name,uid:uid});
    if(r.ok!==false){
      setRes('resLocate','已查到坐标','ok');
      toast('已查到坐标','ok');
    }else{
      setRes('resLocate','查询失败: '+(r.error||r.errorText||'未知错误'),'err');
      toast('查询失败: '+(r.error||r.errorText||''),'err');
    }
    renderLocate(r);
  });
});
$('btnLocate').onclick=async()=>{
  const name=$('inpLocate').value.trim();
  if(!name){ toast('先输入玩家名字','err'); setRes('resLocate','需要先输入玩家名字','err'); return; }
  await busy($('btnLocate'),'查询中…',async()=>{
    const r=await api('/api/action',{action:'locate',name:name});
    if(r.ok!==false){
      const ps=r.players||[];
      setRes('resLocate','已查到 '+(ps.length||1)+' 个匹配玩家的坐标','ok');
      toast('已查到坐标','ok');
    }else{
      setRes('resLocate','查询失败: '+(r.error||r.errorText||'未知错误'),'err');
      toast('查询失败: '+(r.error||r.errorText||''),'err');
    }
    renderLocate(r);
  });
};
$('btnLocateScan').onclick=async()=>{
  await busy($('btnLocateScan'),'扫描中…',async()=>{
    const r=await api('/api/action',{action:'locate',name:$('inpLocate').value.trim()||'',op:'scan'});
    if(r.ok!==false){
      const sc=r.scan||{};
      setRes('resLocate','扫描完成: '+sc.requests+' 次请求 · '+sc.tiles+' 地块 · 新增 '+sc.new+' 名玩家','ok');
      toast('索引共 '+(r.index_total||0)+' 人','ok');
    }else{
      setRes('resLocate','扫描失败: '+(r.error||'未知错误'),'err');
    }
    renderLocate(r);
  });
};
$('inpLocate').addEventListener('keydown',(e)=>{ if(e.key==='Enter'){ $('btnLocate').click(); e.preventDefault(); } });
/* blob -> base64(给安卓 WebView 的原生落盘桥用) */
function blobToBase64(blob){
  return new Promise((resolve,reject)=>{
    const fr=new FileReader();
    fr.onload=()=>{ const s=String(fr.result||''); resolve(s.slice(s.indexOf(',')+1)); };
    fr.onerror=()=>reject(new Error('读取导出内容失败'));
    fr.readAsDataURL(blob);
  });
}
$('btnExport').onclick=async()=>{
  const onlyReal=$('chkExportReal')&&$('chkExportReal').checked;
  await busy($('btnExport'),'导出中…',async()=>{
    try{
      const url='/api/export?t='+encodeURIComponent(TOKEN)+(onlyReal?'&players=1':'');
      const r=await fetch(url);
      if(!r.ok){
        let msg='HTTP '+r.status;
        try{ const j=await r.json(); msg=j.error||msg; }catch(e){}
        toast('导出失败: '+msg,'err');
        setRes('resLocate','导出失败: '+msg,'err');
        return;
      }
      const blob=await r.blob();
      const fname=onlyReal?'cok-players-real.xlsx':'cok-players.xlsx';
      const kb=Math.round(blob.size/1024);
      /* 安卓内嵌 WebView: blob 下载**不会落盘**, 页面还会假装成功。
         有原生桥就交给原生写到 下载/COK/。 */
      if(window.CokAndroid && typeof window.CokAndroid.saveExport==='function'){
        const b64=await blobToBase64(blob);
        const msg=window.CokAndroid.saveExport(fname,b64);
        const bad=/失败/.test(String(msg));
        setRes('resLocate',String(msg),bad?'err':'ok');
        toast(String(msg),bad?'err':'ok');
        return;
      }
      const url2=URL.createObjectURL(blob);
      const a=document.createElement('a');
      a.href=url2; a.download=fname;
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(()=>URL.revokeObjectURL(url2), 5000);
      setRes('resLocate','已导出 Excel ('+kb+' KB'+(onlyReal?', 仅真实玩家':'')+')','ok');
      toast('已导出 '+kb+' KB','ok');
    }catch(e){
      toast('导出失败: '+(e&&e.message?e.message:e),'err');
    }
  });
};

/* ---------------- 全图扫描(独立进程) ---------------- */
function renderScan(st){
  const mi=(st&&st.map_index)||{};
  const running=!!mi.scanning;
  const bA=$('btnScanAll'), bS=$('btnScanStop');
  if(bA){ bA.disabled=running; bA.textContent=running?'扫描中…':'一键全图重扫'; }
  if(bS){ bS.disabled=!running; }
  const box=$('scanProgress');
  if(!box) return;
  if(running){
    const d=mi.requests_done||0, t=mi.requests_total||0;
    const pct=t?Math.min(100,Math.round(100*d/t)):0;
    box.innerHTML='<div style="margin-top:8px">'
      +'<div style="display:flex;justify-content:space-between;font-size:12px;color:#9fb4c8">'
      +'<span>扫描中 '+d+'/'+t+' 次请求</span><span>'+pct+'%</span></div>'
      +'<div style="height:6px;background:#1b2733;border-radius:3px;margin-top:4px;overflow:hidden">'
      +'<div style="height:100%;width:'+pct+'%;background:linear-gradient(90deg,#2f7fd6,#38bdf8)"></div>'
      +'</div></div>';
  }else{
    const h=[];
    if(mi.mismatched) h.push('错位丢弃 '+mi.mismatched);
    if(mi.dropped) h.push('越界剔除 '+mi.dropped);
    if(mi.errors) h.push('失败 '+mi.errors);
    box.innerHTML=h.length?('<div class="mini" style="margin-top:6px;color:#e0a44a">上次扫描健康指标: '
      +esc(h.join(' · '))+'</div>'):'';
  }
}

async function loadScanHistory(){
  const box=$('scanHistory'); if(!box) return;
  try{
    const d=await api('/api/scan/history');
    const runs=(d&&d.runs)||[];
    if(!runs.length){ box.textContent='还没有扫描记录'; return; }
    const rows=runs.map(r=>{
      const stt={running:'运行中',completed:'已完成',interrupted:'已中断'}[r.status]||(r.status||'-');
      const cls=r.status==='completed'?'good':(r.status==='running'?'info':'warn');
      const t0=r.started_at?hhmmss(r.started_at*1000):'-';
      const dur=(r.finished_at&&r.started_at)?(Math.round(r.finished_at-r.started_at)+'s'):'-';
      const hl=[];
      if(r.mismatched_responses) hl.push('错位 '+r.mismatched_responses);
      if(r.dropped_out_of_range) hl.push('越界 '+r.dropped_out_of_range);
      if(r.errors) hl.push('失败 '+r.errors);
      const sp=(r.self_point&&r.self_point.x!=null)?(' · 自('+r.self_point.x+','+r.self_point.y+')'):'';
      return '<tr><td>'+esc(t0)+'</td>'
        +'<td><span class="tag '+cls+'">'+esc(stt)+'</span></td>'
        +'<td>'+esc((r.requests_done||0)+'/'+(r.requests_total||0))+'</td>'
        +'<td>'+esc(r.players||0)+' <span class="mini">('+esc(r.real_players||0)+' 真人)</span></td>'
        +'<td>'+esc(hl.join(' · ')||'-')+esc(sp)+'</td>'
        +'<td>'+esc(dur)+'</td></tr>';
    }).join('');
    box.innerHTML='<table style="width:100%;border-collapse:collapse">'
      +'<tr style="color:#8fa6bd;text-align:left"><th>开始</th><th>状态</th><th>请求</th>'
      +'<th>玩家</th><th>健康</th><th>耗时</th></tr>'+rows+'</table>';
  }catch(e){ box.textContent='读取失败: '+(e&&e.message?e.message:e); }
}

$('btnScanAll').onclick=async()=>{
  const step=Number($('selScanStep').value||12);
  const resume=!!($('chkScanResume')&&$('chkScanResume').checked);
  await busy($('btnScanAll'),'启动中…',async()=>{
    const r=await api('/api/scan/start',{step,resume});
    if(r&&r.ok){
      toast(r.note||'扫描已启动','ok');
      setRes('resLocate',(r.note||'扫描已启动')+(r.resumed?'(从上次断点继续)':''),'ok');
    }else{
      const msg=(r&&r.error)||'未知错误';
      toast('启动失败: '+msg,'err');
      setRes('resLocate','启动失败: '+msg,'err');
    }
    setTimeout(loadScanHistory,1500);
  });
};
$('btnScanStop').onclick=async()=>{
  await busy($('btnScanStop'),'停止中…',async()=>{
    const r=await api('/api/scan/stop',{});
    if(r&&r.ok){ toast(r.note||'已停止','ok'); setRes('resLocate',r.note||'已停止','ok'); }
    else{ toast('停止失败: '+((r&&r.error)||'未知'),'err'); }
    setTimeout(loadScanHistory,1200);
  });
};

/* ---------------- 事件区工具条 ---------------- */
document.querySelectorAll('.logbar .chip[data-ev]').forEach(c=>{
  c.addEventListener('click',()=>{
    EV_FILTER=c.dataset.ev;
    document.querySelectorAll('.logbar .chip[data-ev]').forEach(x=>x.classList.toggle('on',x===c));
    EV_SIG='';           // 强制重绘
    if(S.state) renderEvents(S.state);
  });
});
$('btnLogClear').onclick=()=>{
  const box=$('logs');
  if(box) box.innerHTML='<div class="empty">已清空显示(后端的历史事件还在, 下一轮会重新出现)</div>';
  EV_SIG='';
};
const LOG_H=[280,420,620];
let LOG_HI=0;
$('btnLogSize').onclick=()=>{
  LOG_HI=(LOG_HI+1)%LOG_H.length;
  $('logs').style.height=LOG_H[LOG_HI]+'px';
  toast('日志区高度 '+LOG_H[LOG_HI]+'px');
};

/* ---------------- 快捷键 ---------------- */
$('btnKeys').onclick=()=>{ $('kbar').classList.toggle('show'); };

/* ---------------- 平台层: 当前用户 / 退出 ---------------- */
async function loadMe(){
  try{
    const r=await fetch('/api/me',{credentials:'same-origin'});
    if(!r.ok){ ME=null; renderMe(); return null; }
    const j=await r.json();
    if(!j||!j.ok){ ME=null; renderMe(); return null; }
    ME=j; renderMe(); return j;
  }catch(e){ ME=null; renderMe(); return null; }
}
function renderMe(){
  const box=$('userBadge'), name=$('userName');
  if(!box||!name) return;
  if(!ME || !ME.platform){
    box.style.display='none';
    // 退出登录/取不到用户时把顶栏那份也收回去 —— 否则按钮还在, 点了弹「无权限」
    const w=$('admTopWrap'); if(w) w.classList.remove('admOn');
    return;
  }
  box.style.display='';
  name.textContent = ME.user + (ME.role==='admin'?' (管理员)':'');
  // 管理后台入口: 只有 admin 能看。侧栏那份用内联 display(mobile-console.css
  // 在任何宽度都会藏 .sbUser, 所以要靠 JS 把它放出来), 顶栏那份切 class。
  const isAdm = ME.role==='admin';
  const ent=$('btnAdminSite2');
  if(ent) ent.style.display = isAdm?'':'none';
  const wrap=$('admTopWrap');
  if(wrap) wrap.classList.toggle('admOn', isAdm);
  // 顶栏那个按钮直接跳 /admin(不弹浮层): 管理后台是完整的一页,
  // 塞进浮层等于又回到"一屏只放一张表"的老问题。
  // ⚠ 必须走 goAdmin(): 安卓宿主 App 用 ?t=<token> 免登录, 不带 token
  //   跳过去就是 403 → 登录页 → App 里没这个页面 → 白屏。
  const site=$('btnAdminSite');
  if(site) site.onclick=()=>{ goAdmin(); };
  const ent2=$('btnAdminSite2');
  if(ent2) ent2.onclick=(e)=>{ e.preventDefault(); goAdmin(); };
  // 退出登录: 宿主 App(本机管理员)没有"退出"这回事 —— 退出只会把页面
  // 踢到 /login, 而 App 里打不开登录页, 表现是"点了退出就白屏"。
  // 所以只在**真平台部署**(有会话 Cookie)时才显示这个按钮。
  const lo=$('btnLogout');
  if(lo) lo.style.display = ME.local_admin ? 'none' : '';
}
function goAdmin(){
  location.href = TOKEN ? ('/admin?t='+encodeURIComponent(TOKEN)) : '/admin';
}

/* 审计日志与用户管理已移到独立的 /admin 页面。
   原来这里各有一份浮层实现(打开时现拼 innerHTML), 与 /admin 里的表格
   重复维护: 字段、筛选、动作两边不一样, 改一处忘一处。
   现在只剩一个入口按钮 -> /admin。 */

function closeTopOverlay(){
  const list=[].filter.call(document.querySelectorAll('.ovl.show'),
                           el=>getComputedStyle(el).display!=='none');
  if(!list.length) return false;
  // 后加入的在 DOM 里更靠后 => 先关它(近似"最上层")
  list[list.length-1].classList.remove('show');
  return true;
}
document.addEventListener('click',(e)=>{
  // 点遮罩空白处关闭(原来只有渠道登录有这个行为, 其它浮层没有)
  if(e.target.classList && e.target.classList.contains('ovl')){
    e.target.classList.remove('show'); return;
  }
  const c=e.target.closest && e.target.closest('[data-close]');
  if(c){ const box=document.getElementById(c.getAttribute('data-close'));
          if(box) box.classList.remove('show'); }
});
document.addEventListener('keydown',(e)=>{
  // ESC 优先处理：任何地方(包括输入框里)都该能关掉浮层 —— 否则按了没反应
  if(e.key==='Escape'||e.key==='Esc'){
    const kb=$('kbar');
    if(kb&&kb.classList.contains('show')){ kb.classList.remove('show'); e.preventDefault(); return; }
    if(closeTopOverlay()){ e.preventDefault(); return; }
  }
  // 输入框/下拉里不劫持其余按键
  const tag=(e.target&&e.target.tagName)||'';
  if(tag==='INPUT'||tag==='SELECT'||tag==='TEXTAREA') return;
  if(e.metaKey||e.ctrlKey||e.altKey) return;
  const k=(e.key||'').toUpperCase();
  if(k==='?'){ $('kbar').classList.toggle('show'); e.preventDefault(); return; }
  // 快捷键面板开着时，其它单键不再触发（免得在面板上误触刷新）
  const kb=$('kbar');
  if(kb&&kb.classList.contains('show')) return;
  if(k==='R'){ $('btnRefresh').click(); e.preventDefault(); return; }
  if(k==='S'){ $('btnSign').click(); e.preventDefault(); return; }
  if(k==='C'){ $('btnClaim').click(); e.preventDefault(); return; }
  if(k==='D'){ $('btnDockReward').click(); e.preventDefault(); return; }
  if(k==='L'){ goTo('cardLocate'); $('inpLocate').focus(); e.preventDefault(); return; }
  if(k==='1'){ switchTab('dash'); e.preventDefault(); return; }
  if(k==='2'){ switchTab('ops'); e.preventDefault(); return; }
  if(k==='F'){
    // 折叠/展开**当前可见 Tab** 里的卡(隐藏页的卡不动, 否则切回去全是折的)
    const pane=document.querySelector('.tabpane:not([style*="display:none"]):not([style*="display: none"])')||document;
    const cards=[...pane.querySelectorAll('.card')].filter(c=>c.id&&c.querySelector('.fold'));
    if(!cards.length){ e.preventDefault(); return; }
    const anyOpen=cards.some(c=>!c.classList.contains('collapsed'));
    cards.forEach(c=>{
      c.classList.toggle('collapsed',anyOpen);
      const b=c.querySelector('.fold'); if(b) b.textContent=anyOpen?'＋':'－';
      setFolded(c.id,anyOpen);
    });
    toast(anyOpen?'已折叠全部卡片':'已展开全部卡片');
    e.preventDefault();
  }
});

/* ---------------- 启动 ---------------- */
bindSettings();
applyFold();
// 被踢策略切换时, 立即切换退避分钟输入的显隐(保存走 SET_FIELDS 的通用绑定)。
(function(){ const s=$('selKickPolicy'); if(s) s.addEventListener('change', syncKickPolicyUI); })();
$('banner').addEventListener('click',(e)=>{
  if(e.target && e.target.id==='bannerX'){ BANNER_HIDDEN=true; $('banner').className='banner'; $('banner').innerHTML=''; }
});
(async function init(){
  // 平台模式: 先确认登录状态(没登录后端会直接给登录页, 这里只是拿用户名)
  await loadMe();
  // 恢复上次所在的 Tab(默认看板)
  try{ switchTab(localStorage.getItem(TAB_KEY)||'dash'); }catch(e){ switchTab('dash'); }
  const st=await refresh(true);
  // header/横幅渲染后可能换行变高, 再对齐一次 Tab 吸顶位置
  syncTabTop();
  // 设置回填后, 若后端有已保存的编成/等级, 同步到输入框
  if(st && st.settings){ SETTINGS=st.settings||{}; applySettings(); }
  // 读取可用兵种(下拉数据)
  await loadArmyChoices();
  // 扫描历史(展开「扫描历史」时也会刷新)
  loadScanHistory();
  const histBox=$('scanHistory');
  if(histBox && histBox.closest('details')){
    histBox.closest('details').addEventListener('toggle',()=>{ if(histBox.closest('details').open) loadScanHistory(); });
  }
  setTimeout(()=>refresh(true),1200);
  // 主轮询拉的是 /api/state(单账号 ~200KB)。页面在后台/最小化时没人看,
  // 还每 5s 拉一次纯属浪费带宽(10 人挂着 = 每秒几百 KB)。所以**不可见时跳过**,
  // 切回前台立刻补一轮 —— 回来不至于看到一屏旧数据。
  setInterval(()=>{ if(!document.hidden) refresh(true); },5000);
  document.addEventListener('visibilitychange',()=>{ if(!document.hidden) refresh(true); });
  // 巨型狮鹫集结: 独立定时拉(不塞进主轮询, 免得拖慢刷新)
  scheduleRally();
  // 扫描历史每 30 秒刷一次(扫描进行中时进度靠 state, 这里只刷历史)
  setInterval(()=>{ const d=$('scanHistory'); if(d && d.closest('details') && d.closest('details').open) loadScanHistory(); },30000);
})();
