// Vector redraw of the SOGECOQ BTP SARL logo (front faces + extrusion), viewBox 950x640.
const LOGO_PIECES=[
 {id:'b1',c:'#0B2A9E',s:'#06185E',p:[[28,262],[118,210],[118,505],[28,470]]},
 {id:'b2',c:'#1236B5',s:'#06185E',p:[[143,100],[232,22],[232,238],[143,318]]},
 {id:'y1',c:'#FFE81A',s:'#F08A00',p:[[240,92],[322,45],[322,240],[240,298]]},
 {id:'y2',c:'#FFE81A',s:'#F08A00',p:[[330,42],[378,25],[378,212],[330,232]]},
 {id:'y3',c:'#FFE81A',s:'#F08A00',p:[[118,345],[238,256],[238,500],[118,566]]},
 {id:'g1',c:'#2DB52A',s:'#17761A',p:[[238,398],[330,442],[330,530],[188,606],[138,572],[238,510]]}];
function buildLogo(svg,opt={}){const NS='http://www.w3.org/2000/svg';const mk=(p,t,a)=>{const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);p.appendChild(e);return e};
 const g={pieces:{},text:null};
 LOGO_PIECES.forEach(pc=>{const grp=mk(svg,'g',{});const pts=pc.p.map(q=>q.join(',')).join(' ');const ext=pc.p.map(([x,y])=>[x+10,y+9].join(',')).join(' ');
  mk(grp,'polygon',{points:ext,fill:pc.s});mk(grp,'polygon',{points:pts,fill:pc.c});g.pieces[pc.id]=grp});
 if(opt.text!==false){const t=mk(svg,'g',{});
  const a=mk(t,'text',{x:292,y:345,'font-family':'Mont','font-weight':900,'font-size':112,fill:opt.ink||'#0B1747','letter-spacing':-2});a.textContent='SOGECOQ';
  const b=mk(t,'text',{x:366,y:468,'font-family':'Mont','font-weight':900,'font-size':112,fill:opt.ink||'#0B1747','letter-spacing':-2});b.textContent='BTP';
  const c=mk(t,'text',{x:632,y:442,'font-family':'Mont','font-weight':800,'font-size':64,fill:'#FFD400','letter-spacing':5});c.textContent='SARL';
  g.text=t;g.tSog=a;g.tBtp=b;g.tSarl=c}
 return g}
