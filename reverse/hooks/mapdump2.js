'use strict';
function hexOf(buf){const u8=new Uint8Array(buf);let s='';for(let i=0;i<u8.length;i++)s+=('0'+u8[i].toString(16)).slice(-2);return s;}
function emit(o){try{send(o);}catch(e){}}
function rd(p){try{if(!p||p.isNull())return null;const dp=p.readPointer();const len=p.add(8).readU32();if(len===0)return{len:0,text:''};if(len>4096)return{len:len,text:null};const sso=dp.equals(p.add(16));const b=sso?p.add(16):dp;return{len:len,text:b.readUtf8String(len),sso:sso};}catch(e){return{err:String(e)};}}
Process.attachModuleObserver({onAdded(m){
 if(m.name!=='libgame.so')return;
 setTimeout(function(){
  const A=m.base.add(0x3b1a5f8).readPointer();
  if(!A||A.isNull()){emit({t:'no_singleton'});return;}
  const mapAddr=A.add(0x1a8);
  const seen=new Set();
  function walk(node,depth){
   if(node===null||depth>64)return;
   const k=node.toString(); if(seen.has(k))return; seen.add(k);
   let l,r; try{l=node.add(0x10).readPointer();r=node.add(0x18).readPointer();}catch(e){return;}
   walk(l,depth+1);
   try{
     const ik=node.add(0x20).readS32();
     const raw=hexOf(node.add(0x20).readByteArray(64));
     const v1=rd(node.add(0x28)), v2=rd(node.add(0x30)), v3=rd(node.add(0x20));
     emit({t:'entry',k:ik,raw:raw,s28:v1,s30:v2,s20:v3});
   }catch(e){}
   walk(r,depth+1);
  }
  try{walk(mapAddr.add(0x10).readPointer(),0);}catch(e){emit({t:'walk_err',msg:String(e)});}
  try{emit({t:'bf_raw',raw:hexOf(A.add(0x1d8).readByteArray(24))});}catch(e){}
 },400);
}});
emit({t:'loaded',pid:Process.id});
