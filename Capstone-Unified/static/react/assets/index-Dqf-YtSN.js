var ov=Object.defineProperty;var cv=(n,s,l)=>s in n?ov(n,s,{enumerable:!0,configurable:!0,writable:!0,value:l}):n[s]=l;var nu=(n,s,l)=>cv(n,typeof s!="symbol"?s+"":s,l);function dv(n,s){for(var l=0;l<s.length;l++){const o=s[l];if(typeof o!="string"&&!Array.isArray(o)){for(const d in o)if(d!=="default"&&!(d in n)){const f=Object.getOwnPropertyDescriptor(o,d);f&&Object.defineProperty(n,d,f.get?f:{enumerable:!0,get:()=>o[d]})}}}return Object.freeze(Object.defineProperty(n,Symbol.toStringTag,{value:"Module"}))}(function(){const s=document.createElement("link").relList;if(s&&s.supports&&s.supports("modulepreload"))return;for(const d of document.querySelectorAll('link[rel="modulepreload"]'))o(d);new MutationObserver(d=>{for(const f of d)if(f.type==="childList")for(const m of f.addedNodes)m.tagName==="LINK"&&m.rel==="modulepreload"&&o(m)}).observe(document,{childList:!0,subtree:!0});function l(d){const f={};return d.integrity&&(f.integrity=d.integrity),d.referrerPolicy&&(f.referrerPolicy=d.referrerPolicy),d.crossOrigin==="use-credentials"?f.credentials="include":d.crossOrigin==="anonymous"?f.credentials="omit":f.credentials="same-origin",f}function o(d){if(d.ep)return;d.ep=!0;const f=l(d);fetch(d.href,f)}})();function Jg(n){return n&&n.__esModule&&Object.prototype.hasOwnProperty.call(n,"default")?n.default:n}var iu={exports:{}},$r={};/**
 * @license React
 * react-jsx-runtime.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var Op;function uv(){if(Op)return $r;Op=1;var n=Symbol.for("react.transitional.element"),s=Symbol.for("react.fragment");function l(o,d,f){var m=null;if(f!==void 0&&(m=""+f),d.key!==void 0&&(m=""+d.key),"key"in d){f={};for(var p in d)p!=="key"&&(f[p]=d[p])}else f=d;return d=f.ref,{$$typeof:n,type:o,key:m,ref:d!==void 0?d:null,props:f}}return $r.Fragment=s,$r.jsx=l,$r.jsxs=l,$r}var Up;function fv(){return Up||(Up=1,iu.exports=uv()),iu.exports}var t=fv(),su={exports:{}},it={};/**
 * @license React
 * react.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var Lp;function hv(){if(Lp)return it;Lp=1;var n=Symbol.for("react.transitional.element"),s=Symbol.for("react.portal"),l=Symbol.for("react.fragment"),o=Symbol.for("react.strict_mode"),d=Symbol.for("react.profiler"),f=Symbol.for("react.consumer"),m=Symbol.for("react.context"),p=Symbol.for("react.forward_ref"),g=Symbol.for("react.suspense"),h=Symbol.for("react.memo"),x=Symbol.for("react.lazy"),v=Symbol.iterator;function b(z){return z===null||typeof z!="object"?null:(z=v&&z[v]||z["@@iterator"],typeof z=="function"?z:null)}var _={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},C=Object.assign,E={};function A(z,G,ie){this.props=z,this.context=G,this.refs=E,this.updater=ie||_}A.prototype.isReactComponent={},A.prototype.setState=function(z,G){if(typeof z!="object"&&typeof z!="function"&&z!=null)throw Error("takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,z,G,"setState")},A.prototype.forceUpdate=function(z){this.updater.enqueueForceUpdate(this,z,"forceUpdate")};function L(){}L.prototype=A.prototype;function q(z,G,ie){this.props=z,this.context=G,this.refs=E,this.updater=ie||_}var P=q.prototype=new L;P.constructor=q,C(P,A.prototype),P.isPureReactComponent=!0;var M=Array.isArray,X={H:null,A:null,T:null,S:null,V:null},Q=Object.prototype.hasOwnProperty;function K(z,G,ie,oe,re,Te){return ie=Te.ref,{$$typeof:n,type:z,key:G,ref:ie!==void 0?ie:null,props:Te}}function se(z,G){return K(z.type,G,void 0,void 0,void 0,z.props)}function Ae(z){return typeof z=="object"&&z!==null&&z.$$typeof===n}function we(z){var G={"=":"=0",":":"=2"};return"$"+z.replace(/[=:]/g,function(ie){return G[ie]})}var ge=/\/+/g;function Ne(z,G){return typeof z=="object"&&z!==null&&z.key!=null?we(""+z.key):G.toString(36)}function me(){}function xe(z){switch(z.status){case"fulfilled":return z.value;case"rejected":throw z.reason;default:switch(typeof z.status=="string"?z.then(me,me):(z.status="pending",z.then(function(G){z.status==="pending"&&(z.status="fulfilled",z.value=G)},function(G){z.status==="pending"&&(z.status="rejected",z.reason=G)})),z.status){case"fulfilled":return z.value;case"rejected":throw z.reason}}throw z}function He(z,G,ie,oe,re){var Te=typeof z;(Te==="undefined"||Te==="boolean")&&(z=null);var ue=!1;if(z===null)ue=!0;else switch(Te){case"bigint":case"string":case"number":ue=!0;break;case"object":switch(z.$$typeof){case n:case s:ue=!0;break;case x:return ue=z._init,He(ue(z._payload),G,ie,oe,re)}}if(ue)return re=re(z),ue=oe===""?"."+Ne(z,0):oe,M(re)?(ie="",ue!=null&&(ie=ue.replace(ge,"$&/")+"/"),He(re,G,ie,"",function(ne){return ne})):re!=null&&(Ae(re)&&(re=se(re,ie+(re.key==null||z&&z.key===re.key?"":(""+re.key).replace(ge,"$&/")+"/")+ue)),G.push(re)),1;ue=0;var je=oe===""?".":oe+":";if(M(z))for(var Le=0;Le<z.length;Le++)oe=z[Le],Te=je+Ne(oe,Le),ue+=He(oe,G,ie,Te,re);else if(Le=b(z),typeof Le=="function")for(z=Le.call(z),Le=0;!(oe=z.next()).done;)oe=oe.value,Te=je+Ne(oe,Le++),ue+=He(oe,G,ie,Te,re);else if(Te==="object"){if(typeof z.then=="function")return He(xe(z),G,ie,oe,re);throw G=String(z),Error("Objects are not valid as a React child (found: "+(G==="[object Object]"?"object with keys {"+Object.keys(z).join(", ")+"}":G)+"). If you meant to render a collection of children, use an array instead.")}return ue}function S(z,G,ie){if(z==null)return z;var oe=[],re=0;return He(z,oe,"","",function(Te){return G.call(ie,Te,re++)}),oe}function H(z){if(z._status===-1){var G=z._result;G=G(),G.then(function(ie){(z._status===0||z._status===-1)&&(z._status=1,z._result=ie)},function(ie){(z._status===0||z._status===-1)&&(z._status=2,z._result=ie)}),z._status===-1&&(z._status=0,z._result=G)}if(z._status===1)return z._result.default;throw z._result}var F=typeof reportError=="function"?reportError:function(z){if(typeof window=="object"&&typeof window.ErrorEvent=="function"){var G=new window.ErrorEvent("error",{bubbles:!0,cancelable:!0,message:typeof z=="object"&&z!==null&&typeof z.message=="string"?String(z.message):String(z),error:z});if(!window.dispatchEvent(G))return}else if(typeof process=="object"&&typeof process.emit=="function"){process.emit("uncaughtException",z);return}console.error(z)};function _e(){}return it.Children={map:S,forEach:function(z,G,ie){S(z,function(){G.apply(this,arguments)},ie)},count:function(z){var G=0;return S(z,function(){G++}),G},toArray:function(z){return S(z,function(G){return G})||[]},only:function(z){if(!Ae(z))throw Error("React.Children.only expected to receive a single React element child.");return z}},it.Component=A,it.Fragment=l,it.Profiler=d,it.PureComponent=q,it.StrictMode=o,it.Suspense=g,it.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE=X,it.__COMPILER_RUNTIME={__proto__:null,c:function(z){return X.H.useMemoCache(z)}},it.cache=function(z){return function(){return z.apply(null,arguments)}},it.cloneElement=function(z,G,ie){if(z==null)throw Error("The argument must be a React element, but you passed "+z+".");var oe=C({},z.props),re=z.key,Te=void 0;if(G!=null)for(ue in G.ref!==void 0&&(Te=void 0),G.key!==void 0&&(re=""+G.key),G)!Q.call(G,ue)||ue==="key"||ue==="__self"||ue==="__source"||ue==="ref"&&G.ref===void 0||(oe[ue]=G[ue]);var ue=arguments.length-2;if(ue===1)oe.children=ie;else if(1<ue){for(var je=Array(ue),Le=0;Le<ue;Le++)je[Le]=arguments[Le+2];oe.children=je}return K(z.type,re,void 0,void 0,Te,oe)},it.createContext=function(z){return z={$$typeof:m,_currentValue:z,_currentValue2:z,_threadCount:0,Provider:null,Consumer:null},z.Provider=z,z.Consumer={$$typeof:f,_context:z},z},it.createElement=function(z,G,ie){var oe,re={},Te=null;if(G!=null)for(oe in G.key!==void 0&&(Te=""+G.key),G)Q.call(G,oe)&&oe!=="key"&&oe!=="__self"&&oe!=="__source"&&(re[oe]=G[oe]);var ue=arguments.length-2;if(ue===1)re.children=ie;else if(1<ue){for(var je=Array(ue),Le=0;Le<ue;Le++)je[Le]=arguments[Le+2];re.children=je}if(z&&z.defaultProps)for(oe in ue=z.defaultProps,ue)re[oe]===void 0&&(re[oe]=ue[oe]);return K(z,Te,void 0,void 0,null,re)},it.createRef=function(){return{current:null}},it.forwardRef=function(z){return{$$typeof:p,render:z}},it.isValidElement=Ae,it.lazy=function(z){return{$$typeof:x,_payload:{_status:-1,_result:z},_init:H}},it.memo=function(z,G){return{$$typeof:h,type:z,compare:G===void 0?null:G}},it.startTransition=function(z){var G=X.T,ie={};X.T=ie;try{var oe=z(),re=X.S;re!==null&&re(ie,oe),typeof oe=="object"&&oe!==null&&typeof oe.then=="function"&&oe.then(_e,F)}catch(Te){F(Te)}finally{X.T=G}},it.unstable_useCacheRefresh=function(){return X.H.useCacheRefresh()},it.use=function(z){return X.H.use(z)},it.useActionState=function(z,G,ie){return X.H.useActionState(z,G,ie)},it.useCallback=function(z,G){return X.H.useCallback(z,G)},it.useContext=function(z){return X.H.useContext(z)},it.useDebugValue=function(){},it.useDeferredValue=function(z,G){return X.H.useDeferredValue(z,G)},it.useEffect=function(z,G,ie){var oe=X.H;if(typeof ie=="function")throw Error("useEffect CRUD overload is not enabled in this build of React.");return oe.useEffect(z,G)},it.useId=function(){return X.H.useId()},it.useImperativeHandle=function(z,G,ie){return X.H.useImperativeHandle(z,G,ie)},it.useInsertionEffect=function(z,G){return X.H.useInsertionEffect(z,G)},it.useLayoutEffect=function(z,G){return X.H.useLayoutEffect(z,G)},it.useMemo=function(z,G){return X.H.useMemo(z,G)},it.useOptimistic=function(z,G){return X.H.useOptimistic(z,G)},it.useReducer=function(z,G,ie){return X.H.useReducer(z,G,ie)},it.useRef=function(z){return X.H.useRef(z)},it.useState=function(z){return X.H.useState(z)},it.useSyncExternalStore=function(z,G,ie){return X.H.useSyncExternalStore(z,G,ie)},it.useTransition=function(){return X.H.useTransition()},it.version="19.1.1",it}var Bp;function Hu(){return Bp||(Bp=1,su.exports=hv()),su.exports}var N=Hu();const Fs=Jg(N),mv=dv({__proto__:null,default:Fs},[N]);var ru={exports:{}},Fr={},lu={exports:{}},ou={};/**
 * @license React
 * scheduler.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var qp;function pv(){return qp||(qp=1,(function(n){function s(S,H){var F=S.length;S.push(H);e:for(;0<F;){var _e=F-1>>>1,z=S[_e];if(0<d(z,H))S[_e]=H,S[F]=z,F=_e;else break e}}function l(S){return S.length===0?null:S[0]}function o(S){if(S.length===0)return null;var H=S[0],F=S.pop();if(F!==H){S[0]=F;e:for(var _e=0,z=S.length,G=z>>>1;_e<G;){var ie=2*(_e+1)-1,oe=S[ie],re=ie+1,Te=S[re];if(0>d(oe,F))re<z&&0>d(Te,oe)?(S[_e]=Te,S[re]=F,_e=re):(S[_e]=oe,S[ie]=F,_e=ie);else if(re<z&&0>d(Te,F))S[_e]=Te,S[re]=F,_e=re;else break e}}return H}function d(S,H){var F=S.sortIndex-H.sortIndex;return F!==0?F:S.id-H.id}if(n.unstable_now=void 0,typeof performance=="object"&&typeof performance.now=="function"){var f=performance;n.unstable_now=function(){return f.now()}}else{var m=Date,p=m.now();n.unstable_now=function(){return m.now()-p}}var g=[],h=[],x=1,v=null,b=3,_=!1,C=!1,E=!1,A=!1,L=typeof setTimeout=="function"?setTimeout:null,q=typeof clearTimeout=="function"?clearTimeout:null,P=typeof setImmediate<"u"?setImmediate:null;function M(S){for(var H=l(h);H!==null;){if(H.callback===null)o(h);else if(H.startTime<=S)o(h),H.sortIndex=H.expirationTime,s(g,H);else break;H=l(h)}}function X(S){if(E=!1,M(S),!C)if(l(g)!==null)C=!0,Q||(Q=!0,Ne());else{var H=l(h);H!==null&&He(X,H.startTime-S)}}var Q=!1,K=-1,se=5,Ae=-1;function we(){return A?!0:!(n.unstable_now()-Ae<se)}function ge(){if(A=!1,Q){var S=n.unstable_now();Ae=S;var H=!0;try{e:{C=!1,E&&(E=!1,q(K),K=-1),_=!0;var F=b;try{t:{for(M(S),v=l(g);v!==null&&!(v.expirationTime>S&&we());){var _e=v.callback;if(typeof _e=="function"){v.callback=null,b=v.priorityLevel;var z=_e(v.expirationTime<=S);if(S=n.unstable_now(),typeof z=="function"){v.callback=z,M(S),H=!0;break t}v===l(g)&&o(g),M(S)}else o(g);v=l(g)}if(v!==null)H=!0;else{var G=l(h);G!==null&&He(X,G.startTime-S),H=!1}}break e}finally{v=null,b=F,_=!1}H=void 0}}finally{H?Ne():Q=!1}}}var Ne;if(typeof P=="function")Ne=function(){P(ge)};else if(typeof MessageChannel<"u"){var me=new MessageChannel,xe=me.port2;me.port1.onmessage=ge,Ne=function(){xe.postMessage(null)}}else Ne=function(){L(ge,0)};function He(S,H){K=L(function(){S(n.unstable_now())},H)}n.unstable_IdlePriority=5,n.unstable_ImmediatePriority=1,n.unstable_LowPriority=4,n.unstable_NormalPriority=3,n.unstable_Profiling=null,n.unstable_UserBlockingPriority=2,n.unstable_cancelCallback=function(S){S.callback=null},n.unstable_forceFrameRate=function(S){0>S||125<S?console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported"):se=0<S?Math.floor(1e3/S):5},n.unstable_getCurrentPriorityLevel=function(){return b},n.unstable_next=function(S){switch(b){case 1:case 2:case 3:var H=3;break;default:H=b}var F=b;b=H;try{return S()}finally{b=F}},n.unstable_requestPaint=function(){A=!0},n.unstable_runWithPriority=function(S,H){switch(S){case 1:case 2:case 3:case 4:case 5:break;default:S=3}var F=b;b=S;try{return H()}finally{b=F}},n.unstable_scheduleCallback=function(S,H,F){var _e=n.unstable_now();switch(typeof F=="object"&&F!==null?(F=F.delay,F=typeof F=="number"&&0<F?_e+F:_e):F=_e,S){case 1:var z=-1;break;case 2:z=250;break;case 5:z=1073741823;break;case 4:z=1e4;break;default:z=5e3}return z=F+z,S={id:x++,callback:H,priorityLevel:S,startTime:F,expirationTime:z,sortIndex:-1},F>_e?(S.sortIndex=F,s(h,S),l(g)===null&&S===l(h)&&(E?(q(K),K=-1):E=!0,He(X,F-_e))):(S.sortIndex=z,s(g,S),C||_||(C=!0,Q||(Q=!0,Ne()))),S},n.unstable_shouldYield=we,n.unstable_wrapCallback=function(S){var H=b;return function(){var F=b;b=H;try{return S.apply(this,arguments)}finally{b=F}}}})(ou)),ou}var Hp;function gv(){return Hp||(Hp=1,lu.exports=pv()),lu.exports}var cu={exports:{}},Ta={};/**
 * @license React
 * react-dom.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var Ip;function xv(){if(Ip)return Ta;Ip=1;var n=Hu();function s(g){var h="https://react.dev/errors/"+g;if(1<arguments.length){h+="?args[]="+encodeURIComponent(arguments[1]);for(var x=2;x<arguments.length;x++)h+="&args[]="+encodeURIComponent(arguments[x])}return"Minified React error #"+g+"; visit "+h+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}function l(){}var o={d:{f:l,r:function(){throw Error(s(522))},D:l,C:l,L:l,m:l,X:l,S:l,M:l},p:0,findDOMNode:null},d=Symbol.for("react.portal");function f(g,h,x){var v=3<arguments.length&&arguments[3]!==void 0?arguments[3]:null;return{$$typeof:d,key:v==null?null:""+v,children:g,containerInfo:h,implementation:x}}var m=n.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE;function p(g,h){if(g==="font")return"";if(typeof h=="string")return h==="use-credentials"?h:""}return Ta.__DOM_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE=o,Ta.createPortal=function(g,h){var x=2<arguments.length&&arguments[2]!==void 0?arguments[2]:null;if(!h||h.nodeType!==1&&h.nodeType!==9&&h.nodeType!==11)throw Error(s(299));return f(g,h,null,x)},Ta.flushSync=function(g){var h=m.T,x=o.p;try{if(m.T=null,o.p=2,g)return g()}finally{m.T=h,o.p=x,o.d.f()}},Ta.preconnect=function(g,h){typeof g=="string"&&(h?(h=h.crossOrigin,h=typeof h=="string"?h==="use-credentials"?h:"":void 0):h=null,o.d.C(g,h))},Ta.prefetchDNS=function(g){typeof g=="string"&&o.d.D(g)},Ta.preinit=function(g,h){if(typeof g=="string"&&h&&typeof h.as=="string"){var x=h.as,v=p(x,h.crossOrigin),b=typeof h.integrity=="string"?h.integrity:void 0,_=typeof h.fetchPriority=="string"?h.fetchPriority:void 0;x==="style"?o.d.S(g,typeof h.precedence=="string"?h.precedence:void 0,{crossOrigin:v,integrity:b,fetchPriority:_}):x==="script"&&o.d.X(g,{crossOrigin:v,integrity:b,fetchPriority:_,nonce:typeof h.nonce=="string"?h.nonce:void 0})}},Ta.preinitModule=function(g,h){if(typeof g=="string")if(typeof h=="object"&&h!==null){if(h.as==null||h.as==="script"){var x=p(h.as,h.crossOrigin);o.d.M(g,{crossOrigin:x,integrity:typeof h.integrity=="string"?h.integrity:void 0,nonce:typeof h.nonce=="string"?h.nonce:void 0})}}else h==null&&o.d.M(g)},Ta.preload=function(g,h){if(typeof g=="string"&&typeof h=="object"&&h!==null&&typeof h.as=="string"){var x=h.as,v=p(x,h.crossOrigin);o.d.L(g,x,{crossOrigin:v,integrity:typeof h.integrity=="string"?h.integrity:void 0,nonce:typeof h.nonce=="string"?h.nonce:void 0,type:typeof h.type=="string"?h.type:void 0,fetchPriority:typeof h.fetchPriority=="string"?h.fetchPriority:void 0,referrerPolicy:typeof h.referrerPolicy=="string"?h.referrerPolicy:void 0,imageSrcSet:typeof h.imageSrcSet=="string"?h.imageSrcSet:void 0,imageSizes:typeof h.imageSizes=="string"?h.imageSizes:void 0,media:typeof h.media=="string"?h.media:void 0})}},Ta.preloadModule=function(g,h){if(typeof g=="string")if(h){var x=p(h.as,h.crossOrigin);o.d.m(g,{as:typeof h.as=="string"&&h.as!=="script"?h.as:void 0,crossOrigin:x,integrity:typeof h.integrity=="string"?h.integrity:void 0})}else o.d.m(g)},Ta.requestFormReset=function(g){o.d.r(g)},Ta.unstable_batchedUpdates=function(g,h){return g(h)},Ta.useFormState=function(g,h,x){return m.H.useFormState(g,h,x)},Ta.useFormStatus=function(){return m.H.useHostTransitionStatus()},Ta.version="19.1.1",Ta}var $p;function Wg(){if($p)return cu.exports;$p=1;function n(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(n)}catch(s){console.error(s)}}return n(),cu.exports=xv(),cu.exports}/**
 * @license React
 * react-dom-client.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var Fp;function yv(){if(Fp)return Fr;Fp=1;var n=gv(),s=Hu(),l=Wg();function o(e){var a="https://react.dev/errors/"+e;if(1<arguments.length){a+="?args[]="+encodeURIComponent(arguments[1]);for(var i=2;i<arguments.length;i++)a+="&args[]="+encodeURIComponent(arguments[i])}return"Minified React error #"+e+"; visit "+a+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}function d(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11)}function f(e){var a=e,i=e;if(e.alternate)for(;a.return;)a=a.return;else{e=a;do a=e,(a.flags&4098)!==0&&(i=a.return),e=a.return;while(e)}return a.tag===3?i:null}function m(e){if(e.tag===13){var a=e.memoizedState;if(a===null&&(e=e.alternate,e!==null&&(a=e.memoizedState)),a!==null)return a.dehydrated}return null}function p(e){if(f(e)!==e)throw Error(o(188))}function g(e){var a=e.alternate;if(!a){if(a=f(e),a===null)throw Error(o(188));return a!==e?null:e}for(var i=e,r=a;;){var c=i.return;if(c===null)break;var u=c.alternate;if(u===null){if(r=c.return,r!==null){i=r;continue}break}if(c.child===u.child){for(u=c.child;u;){if(u===i)return p(c),e;if(u===r)return p(c),a;u=u.sibling}throw Error(o(188))}if(i.return!==r.return)i=c,r=u;else{for(var y=!1,w=c.child;w;){if(w===i){y=!0,i=c,r=u;break}if(w===r){y=!0,r=c,i=u;break}w=w.sibling}if(!y){for(w=u.child;w;){if(w===i){y=!0,i=u,r=c;break}if(w===r){y=!0,r=u,i=c;break}w=w.sibling}if(!y)throw Error(o(189))}}if(i.alternate!==r)throw Error(o(190))}if(i.tag!==3)throw Error(o(188));return i.stateNode.current===i?e:a}function h(e){var a=e.tag;if(a===5||a===26||a===27||a===6)return e;for(e=e.child;e!==null;){if(a=h(e),a!==null)return a;e=e.sibling}return null}var x=Object.assign,v=Symbol.for("react.element"),b=Symbol.for("react.transitional.element"),_=Symbol.for("react.portal"),C=Symbol.for("react.fragment"),E=Symbol.for("react.strict_mode"),A=Symbol.for("react.profiler"),L=Symbol.for("react.provider"),q=Symbol.for("react.consumer"),P=Symbol.for("react.context"),M=Symbol.for("react.forward_ref"),X=Symbol.for("react.suspense"),Q=Symbol.for("react.suspense_list"),K=Symbol.for("react.memo"),se=Symbol.for("react.lazy"),Ae=Symbol.for("react.activity"),we=Symbol.for("react.memo_cache_sentinel"),ge=Symbol.iterator;function Ne(e){return e===null||typeof e!="object"?null:(e=ge&&e[ge]||e["@@iterator"],typeof e=="function"?e:null)}var me=Symbol.for("react.client.reference");function xe(e){if(e==null)return null;if(typeof e=="function")return e.$$typeof===me?null:e.displayName||e.name||null;if(typeof e=="string")return e;switch(e){case C:return"Fragment";case A:return"Profiler";case E:return"StrictMode";case X:return"Suspense";case Q:return"SuspenseList";case Ae:return"Activity"}if(typeof e=="object")switch(e.$$typeof){case _:return"Portal";case P:return(e.displayName||"Context")+".Provider";case q:return(e._context.displayName||"Context")+".Consumer";case M:var a=e.render;return e=e.displayName,e||(e=a.displayName||a.name||"",e=e!==""?"ForwardRef("+e+")":"ForwardRef"),e;case K:return a=e.displayName||null,a!==null?a:xe(e.type)||"Memo";case se:a=e._payload,e=e._init;try{return xe(e(a))}catch{}}return null}var He=Array.isArray,S=s.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE,H=l.__DOM_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE,F={pending:!1,data:null,method:null,action:null},_e=[],z=-1;function G(e){return{current:e}}function ie(e){0>z||(e.current=_e[z],_e[z]=null,z--)}function oe(e,a){z++,_e[z]=e.current,e.current=a}var re=G(null),Te=G(null),ue=G(null),je=G(null);function Le(e,a){switch(oe(ue,a),oe(Te,e),oe(re,null),a.nodeType){case 9:case 11:e=(e=a.documentElement)&&(e=e.namespaceURI)?cp(e):0;break;default:if(e=a.tagName,a=a.namespaceURI)a=cp(a),e=dp(a,e);else switch(e){case"svg":e=1;break;case"math":e=2;break;default:e=0}}ie(re),oe(re,e)}function ne(){ie(re),ie(Te),ie(ue)}function D(e){e.memoizedState!==null&&oe(je,e);var a=re.current,i=dp(a,e.type);a!==i&&(oe(Te,e),oe(re,i))}function I(e){Te.current===e&&(ie(re),ie(Te)),je.current===e&&(ie(je),Lr._currentValue=F)}var J=Object.prototype.hasOwnProperty,be=n.unstable_scheduleCallback,Me=n.unstable_cancelCallback,Ve=n.unstable_shouldYield,at=n.unstable_requestPaint,Ke=n.unstable_now,ta=n.unstable_getCurrentPriorityLevel,_t=n.unstable_ImmediatePriority,Tt=n.unstable_UserBlockingPriority,Ft=n.unstable_NormalPriority,Zt=n.unstable_LowPriority,ae=n.unstable_IdlePriority,De=n.log,Fe=n.unstable_setDisableYieldValue,ke=null,Be=null;function vt(e){if(typeof De=="function"&&Fe(e),Be&&typeof Be.setStrictMode=="function")try{Be.setStrictMode(ke,e)}catch{}}var ft=Math.clz32?Math.clz32:U,V=Math.log,Re=Math.LN2;function U(e){return e>>>=0,e===0?32:31-(V(e)/Re|0)|0}var fe=256,ee=4194304;function Ce(e){var a=e&42;if(a!==0)return a;switch(e&-e){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:return 64;case 128:return 128;case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return e&4194048;case 4194304:case 8388608:case 16777216:case 33554432:return e&62914560;case 67108864:return 67108864;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 0;default:return e}}function Xe(e,a,i){var r=e.pendingLanes;if(r===0)return 0;var c=0,u=e.suspendedLanes,y=e.pingedLanes;e=e.warmLanes;var w=r&134217727;return w!==0?(r=w&~u,r!==0?c=Ce(r):(y&=w,y!==0?c=Ce(y):i||(i=w&~e,i!==0&&(c=Ce(i))))):(w=r&~u,w!==0?c=Ce(w):y!==0?c=Ce(y):i||(i=r&~e,i!==0&&(c=Ce(i)))),c===0?0:a!==0&&a!==c&&(a&u)===0&&(u=c&-c,i=a&-a,u>=i||u===32&&(i&4194048)!==0)?a:c}function et(e,a){return(e.pendingLanes&~(e.suspendedLanes&~e.pingedLanes)&a)===0}function ve(e,a){switch(e){case 1:case 2:case 4:case 8:case 64:return a+250;case 16:case 32:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return a+5e3;case 4194304:case 8388608:case 16777216:case 33554432:return-1;case 67108864:case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}function Ot(){var e=fe;return fe<<=1,(fe&4194048)===0&&(fe=256),e}function St(){var e=ee;return ee<<=1,(ee&62914560)===0&&(ee=4194304),e}function Ee(e){for(var a=[],i=0;31>i;i++)a.push(e);return a}function R(e,a){e.pendingLanes|=a,a!==268435456&&(e.suspendedLanes=0,e.pingedLanes=0,e.warmLanes=0)}function ce(e,a,i,r,c,u){var y=e.pendingLanes;e.pendingLanes=i,e.suspendedLanes=0,e.pingedLanes=0,e.warmLanes=0,e.expiredLanes&=i,e.entangledLanes&=i,e.errorRecoveryDisabledLanes&=i,e.shellSuspendCounter=0;var w=e.entanglements,k=e.expirationTimes,Y=e.hiddenUpdates;for(i=y&~i;0<i;){var le=31-ft(i),ye=1<<le;w[le]=0,k[le]=-1;var Z=Y[le];if(Z!==null)for(Y[le]=null,le=0;le<Z.length;le++){var W=Z[le];W!==null&&(W.lane&=-536870913)}i&=~ye}r!==0&&Ie(e,r,0),u!==0&&c===0&&e.tag!==0&&(e.suspendedLanes|=u&~(y&~a))}function Ie(e,a,i){e.pendingLanes|=a,e.suspendedLanes&=~a;var r=31-ft(a);e.entangledLanes|=a,e.entanglements[r]=e.entanglements[r]|1073741824|i&4194090}function rt(e,a){var i=e.entangledLanes|=a;for(e=e.entanglements;i;){var r=31-ft(i),c=1<<r;c&a|e[r]&a&&(e[r]|=a),i&=~c}}function wt(e){switch(e){case 2:e=1;break;case 8:e=4;break;case 32:e=16;break;case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:e=128;break;case 268435456:e=134217728;break;default:e=0}return e}function ht(e){return e&=-e,2<e?8<e?(e&134217727)!==0?32:268435456:8:2}function Ct(){var e=H.p;return e!==0?e:(e=window.event,e===void 0?32:zp(e.type))}function Bt(e,a){var i=H.p;try{return H.p=e,a()}finally{H.p=i}}var mt=Math.random().toString(36).slice(2),Oe="__reactFiber$"+mt,lt="__reactProps$"+mt,Ut="__reactContainer$"+mt,qt="__reactEvents$"+mt,Ia="__reactListeners$"+mt,en="__reactHandles$"+mt,Ht="__reactResources$"+mt,fn="__reactMarker$"+mt;function $a(e){delete e[Oe],delete e[lt],delete e[qt],delete e[Ia],delete e[en]}function Da(e){var a=e[Oe];if(a)return a;for(var i=e.parentNode;i;){if(a=i[Ut]||i[Oe]){if(i=a.alternate,a.child!==null||i!==null&&i.child!==null)for(e=mp(e);e!==null;){if(i=e[Oe])return i;e=mp(e)}return a}e=i,i=e.parentNode}return null}function tn(e){if(e=e[Oe]||e[Ut]){var a=e.tag;if(a===5||a===6||a===13||a===26||a===27||a===3)return e}return null}function sa(e){var a=e.tag;if(a===5||a===26||a===27||a===6)return e.stateNode;throw Error(o(33))}function Aa(e){var a=e[Ht];return a||(a=e[Ht]={hoistableStyles:new Map,hoistableScripts:new Map}),a}function gt(e){e[fn]=!0}var tt=new Set,Fa={};function Ya(e,a){Ga(e,a),Ga(e+"Capture",a)}function Ga(e,a){for(Fa[e]=a,e=0;e<a.length;e++)tt.add(a[e])}var da=RegExp("^[:A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD][:A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD\\-.0-9\\u00B7\\u0300-\\u036F\\u203F-\\u2040]*$"),ni={},is={};function Qs(e){return J.call(is,e)?!0:J.call(ni,e)?!1:da.test(e)?is[e]=!0:(ni[e]=!0,!1)}function En(e,a,i){if(Qs(a))if(i===null)e.removeAttribute(a);else{switch(typeof i){case"undefined":case"function":case"symbol":e.removeAttribute(a);return;case"boolean":var r=a.toLowerCase().slice(0,5);if(r!=="data-"&&r!=="aria-"){e.removeAttribute(a);return}}e.setAttribute(a,""+i)}}function ii(e,a,i){if(i===null)e.removeAttribute(a);else{switch(typeof i){case"undefined":case"function":case"symbol":case"boolean":e.removeAttribute(a);return}e.setAttribute(a,""+i)}}function Ra(e,a,i,r){if(r===null)e.removeAttribute(i);else{switch(typeof r){case"undefined":case"function":case"symbol":case"boolean":e.removeAttribute(i);return}e.setAttributeNS(a,i,""+r)}}var Mn,Dn;function ua(e){if(Mn===void 0)try{throw Error()}catch(i){var a=i.stack.trim().match(/\n( *(at )?)/);Mn=a&&a[1]||"",Dn=-1<i.stack.indexOf(`
    at`)?" (<anonymous>)":-1<i.stack.indexOf("@")?"@unknown:0:0":""}return`
`+Mn+e+Dn}var Rn=!1;function On(e,a){if(!e||Rn)return"";Rn=!0;var i=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{var r={DetermineComponentFrameRoot:function(){try{if(a){var ye=function(){throw Error()};if(Object.defineProperty(ye.prototype,"props",{set:function(){throw Error()}}),typeof Reflect=="object"&&Reflect.construct){try{Reflect.construct(ye,[])}catch(W){var Z=W}Reflect.construct(e,[],ye)}else{try{ye.call()}catch(W){Z=W}e.call(ye.prototype)}}else{try{throw Error()}catch(W){Z=W}(ye=e())&&typeof ye.catch=="function"&&ye.catch(function(){})}}catch(W){if(W&&Z&&typeof W.stack=="string")return[W.stack,Z.stack]}return[null,null]}};r.DetermineComponentFrameRoot.displayName="DetermineComponentFrameRoot";var c=Object.getOwnPropertyDescriptor(r.DetermineComponentFrameRoot,"name");c&&c.configurable&&Object.defineProperty(r.DetermineComponentFrameRoot,"name",{value:"DetermineComponentFrameRoot"});var u=r.DetermineComponentFrameRoot(),y=u[0],w=u[1];if(y&&w){var k=y.split(`
`),Y=w.split(`
`);for(c=r=0;r<k.length&&!k[r].includes("DetermineComponentFrameRoot");)r++;for(;c<Y.length&&!Y[c].includes("DetermineComponentFrameRoot");)c++;if(r===k.length||c===Y.length)for(r=k.length-1,c=Y.length-1;1<=r&&0<=c&&k[r]!==Y[c];)c--;for(;1<=r&&0<=c;r--,c--)if(k[r]!==Y[c]){if(r!==1||c!==1)do if(r--,c--,0>c||k[r]!==Y[c]){var le=`
`+k[r].replace(" at new "," at ");return e.displayName&&le.includes("<anonymous>")&&(le=le.replace("<anonymous>",e.displayName)),le}while(1<=r&&0<=c);break}}}finally{Rn=!1,Error.prepareStackTrace=i}return(i=e?e.displayName||e.name:"")?ua(i):""}function zi(e){switch(e.tag){case 26:case 27:case 5:return ua(e.type);case 16:return ua("Lazy");case 13:return ua("Suspense");case 19:return ua("SuspenseList");case 0:case 15:return On(e.type,!1);case 11:return On(e.type.render,!1);case 1:return On(e.type,!0);case 31:return ua("Activity");default:return""}}function ss(e){try{var a="";do a+=zi(e),e=e.return;while(e);return a}catch(i){return`
Error generating stack: `+i.message+`
`+i.stack}}function ga(e){switch(typeof e){case"bigint":case"boolean":case"number":case"string":case"undefined":return e;case"object":return e;default:return""}}function hn(e){var a=e.type;return(e=e.nodeName)&&e.toLowerCase()==="input"&&(a==="checkbox"||a==="radio")}function rs(e){var a=hn(e)?"checked":"value",i=Object.getOwnPropertyDescriptor(e.constructor.prototype,a),r=""+e[a];if(!e.hasOwnProperty(a)&&typeof i<"u"&&typeof i.get=="function"&&typeof i.set=="function"){var c=i.get,u=i.set;return Object.defineProperty(e,a,{configurable:!0,get:function(){return c.call(this)},set:function(y){r=""+y,u.call(this,y)}}),Object.defineProperty(e,a,{enumerable:i.enumerable}),{getValue:function(){return r},setValue:function(y){r=""+y},stopTracking:function(){e._valueTracker=null,delete e[a]}}}}function an(e){e._valueTracker||(e._valueTracker=rs(e))}function Un(e){if(!e)return!1;var a=e._valueTracker;if(!a)return!0;var i=a.getValue(),r="";return e&&(r=hn(e)?e.checked?"true":"false":e.value),e=r,e!==i?(a.setValue(e),!0):!1}function Ln(e){if(e=e||(typeof document<"u"?document:void 0),typeof e>"u")return null;try{return e.activeElement||e.body}catch{return e.body}}var si=/[\n"\\]/g;function Gt(e){return e.replace(si,function(a){return"\\"+a.charCodeAt(0).toString(16)+" "})}function ki(e,a,i,r,c,u,y,w){e.name="",y!=null&&typeof y!="function"&&typeof y!="symbol"&&typeof y!="boolean"?e.type=y:e.removeAttribute("type"),a!=null?y==="number"?(a===0&&e.value===""||e.value!=a)&&(e.value=""+ga(a)):e.value!==""+ga(a)&&(e.value=""+ga(a)):y!=="submit"&&y!=="reset"||e.removeAttribute("value"),a!=null?te(e,y,ga(a)):i!=null?te(e,y,ga(i)):r!=null&&e.removeAttribute("value"),c==null&&u!=null&&(e.defaultChecked=!!u),c!=null&&(e.checked=c&&typeof c!="function"&&typeof c!="symbol"),w!=null&&typeof w!="function"&&typeof w!="symbol"&&typeof w!="boolean"?e.name=""+ga(w):e.removeAttribute("name")}function T(e,a,i,r,c,u,y,w){if(u!=null&&typeof u!="function"&&typeof u!="symbol"&&typeof u!="boolean"&&(e.type=u),a!=null||i!=null){if(!(u!=="submit"&&u!=="reset"||a!=null))return;i=i!=null?""+ga(i):"",a=a!=null?""+ga(a):i,w||a===e.value||(e.value=a),e.defaultValue=a}r=r??c,r=typeof r!="function"&&typeof r!="symbol"&&!!r,e.checked=w?e.checked:!!r,e.defaultChecked=!!r,y!=null&&typeof y!="function"&&typeof y!="symbol"&&typeof y!="boolean"&&(e.name=y)}function te(e,a,i){a==="number"&&Ln(e.ownerDocument)===e||e.defaultValue===""+i||(e.defaultValue=""+i)}function de(e,a,i,r){if(e=e.options,a){a={};for(var c=0;c<i.length;c++)a["$"+i[c]]=!0;for(i=0;i<e.length;i++)c=a.hasOwnProperty("$"+e[i].value),e[i].selected!==c&&(e[i].selected=c),c&&r&&(e[i].defaultSelected=!0)}else{for(i=""+ga(i),a=null,c=0;c<e.length;c++){if(e[c].value===i){e[c].selected=!0,r&&(e[c].defaultSelected=!0);return}a!==null||e[c].disabled||(a=e[c])}a!==null&&(a.selected=!0)}}function ze(e,a,i){if(a!=null&&(a=""+ga(a),a!==e.value&&(e.value=a),i==null)){e.defaultValue!==a&&(e.defaultValue=a);return}e.defaultValue=i!=null?""+ga(i):""}function Ze(e,a,i,r){if(a==null){if(r!=null){if(i!=null)throw Error(o(92));if(He(r)){if(1<r.length)throw Error(o(93));r=r[0]}i=r}i==null&&(i=""),a=i}i=ga(a),e.defaultValue=i,r=e.textContent,r===i&&r!==""&&r!==null&&(e.value=r)}function $e(e,a){if(a){var i=e.firstChild;if(i&&i===e.lastChild&&i.nodeType===3){i.nodeValue=a;return}}e.textContent=a}var Yt=new Set("animationIterationCount aspectRatio borderImageOutset borderImageSlice borderImageWidth boxFlex boxFlexGroup boxOrdinalGroup columnCount columns flex flexGrow flexPositive flexShrink flexNegative flexOrder gridArea gridRow gridRowEnd gridRowSpan gridRowStart gridColumn gridColumnEnd gridColumnSpan gridColumnStart fontWeight lineClamp lineHeight opacity order orphans scale tabSize widows zIndex zoom fillOpacity floodOpacity stopOpacity strokeDasharray strokeDashoffset strokeMiterlimit strokeOpacity strokeWidth MozAnimationIterationCount MozBoxFlex MozBoxFlexGroup MozLineClamp msAnimationIterationCount msFlex msZoom msFlexGrow msFlexNegative msFlexOrder msFlexPositive msFlexShrink msGridColumn msGridColumnSpan msGridRow msGridRowSpan WebkitAnimationIterationCount WebkitBoxFlex WebKitBoxFlexGroup WebkitBoxOrdinalGroup WebkitColumnCount WebkitColumns WebkitFlex WebkitFlexGrow WebkitFlexPositive WebkitFlexShrink WebkitLineClamp".split(" "));function Qt(e,a,i){var r=a.indexOf("--")===0;i==null||typeof i=="boolean"||i===""?r?e.setProperty(a,""):a==="float"?e.cssFloat="":e[a]="":r?e.setProperty(a,i):typeof i!="number"||i===0||Yt.has(a)?a==="float"?e.cssFloat=i:e[a]=(""+i).trim():e[a]=i+"px"}function wa(e,a,i){if(a!=null&&typeof a!="object")throw Error(o(62));if(e=e.style,i!=null){for(var r in i)!i.hasOwnProperty(r)||a!=null&&a.hasOwnProperty(r)||(r.indexOf("--")===0?e.setProperty(r,""):r==="float"?e.cssFloat="":e[r]="");for(var c in a)r=a[c],a.hasOwnProperty(c)&&i[c]!==r&&Qt(e,c,r)}else for(var u in a)a.hasOwnProperty(u)&&Qt(e,u,a[u])}function j(e){if(e.indexOf("-")===-1)return!1;switch(e){case"annotation-xml":case"color-profile":case"font-face":case"font-face-src":case"font-face-uri":case"font-face-format":case"font-face-name":case"missing-glyph":return!1;default:return!0}}var pe=new Map([["acceptCharset","accept-charset"],["htmlFor","for"],["httpEquiv","http-equiv"],["crossOrigin","crossorigin"],["accentHeight","accent-height"],["alignmentBaseline","alignment-baseline"],["arabicForm","arabic-form"],["baselineShift","baseline-shift"],["capHeight","cap-height"],["clipPath","clip-path"],["clipRule","clip-rule"],["colorInterpolation","color-interpolation"],["colorInterpolationFilters","color-interpolation-filters"],["colorProfile","color-profile"],["colorRendering","color-rendering"],["dominantBaseline","dominant-baseline"],["enableBackground","enable-background"],["fillOpacity","fill-opacity"],["fillRule","fill-rule"],["floodColor","flood-color"],["floodOpacity","flood-opacity"],["fontFamily","font-family"],["fontSize","font-size"],["fontSizeAdjust","font-size-adjust"],["fontStretch","font-stretch"],["fontStyle","font-style"],["fontVariant","font-variant"],["fontWeight","font-weight"],["glyphName","glyph-name"],["glyphOrientationHorizontal","glyph-orientation-horizontal"],["glyphOrientationVertical","glyph-orientation-vertical"],["horizAdvX","horiz-adv-x"],["horizOriginX","horiz-origin-x"],["imageRendering","image-rendering"],["letterSpacing","letter-spacing"],["lightingColor","lighting-color"],["markerEnd","marker-end"],["markerMid","marker-mid"],["markerStart","marker-start"],["overlinePosition","overline-position"],["overlineThickness","overline-thickness"],["paintOrder","paint-order"],["panose-1","panose-1"],["pointerEvents","pointer-events"],["renderingIntent","rendering-intent"],["shapeRendering","shape-rendering"],["stopColor","stop-color"],["stopOpacity","stop-opacity"],["strikethroughPosition","strikethrough-position"],["strikethroughThickness","strikethrough-thickness"],["strokeDasharray","stroke-dasharray"],["strokeDashoffset","stroke-dashoffset"],["strokeLinecap","stroke-linecap"],["strokeLinejoin","stroke-linejoin"],["strokeMiterlimit","stroke-miterlimit"],["strokeOpacity","stroke-opacity"],["strokeWidth","stroke-width"],["textAnchor","text-anchor"],["textDecoration","text-decoration"],["textRendering","text-rendering"],["transformOrigin","transform-origin"],["underlinePosition","underline-position"],["underlineThickness","underline-thickness"],["unicodeBidi","unicode-bidi"],["unicodeRange","unicode-range"],["unitsPerEm","units-per-em"],["vAlphabetic","v-alphabetic"],["vHanging","v-hanging"],["vIdeographic","v-ideographic"],["vMathematical","v-mathematical"],["vectorEffect","vector-effect"],["vertAdvY","vert-adv-y"],["vertOriginX","vert-origin-x"],["vertOriginY","vert-origin-y"],["wordSpacing","word-spacing"],["writingMode","writing-mode"],["xmlnsXlink","xmlns:xlink"],["xHeight","x-height"]]),Se=/^[\u0000-\u001F ]*j[\r\n\t]*a[\r\n\t]*v[\r\n\t]*a[\r\n\t]*s[\r\n\t]*c[\r\n\t]*r[\r\n\t]*i[\r\n\t]*p[\r\n\t]*t[\r\n\t]*:/i;function Ue(e){return Se.test(""+e)?"javascript:throw new Error('React has blocked a javascript: URL as a security precaution.')":e}var Je=null;function Ge(e){return e=e.target||e.srcElement||window,e.correspondingUseElement&&(e=e.correspondingUseElement),e.nodeType===3?e.parentNode:e}var nt=null,xa=null;function Na(e){var a=tn(e);if(a&&(e=a.stateNode)){var i=e[lt]||null;e:switch(e=a.stateNode,a.type){case"input":if(ki(e,i.value,i.defaultValue,i.defaultValue,i.checked,i.defaultChecked,i.type,i.name),a=i.name,i.type==="radio"&&a!=null){for(i=e;i.parentNode;)i=i.parentNode;for(i=i.querySelectorAll('input[name="'+Gt(""+a)+'"][type="radio"]'),a=0;a<i.length;a++){var r=i[a];if(r!==e&&r.form===e.form){var c=r[lt]||null;if(!c)throw Error(o(90));ki(r,c.value,c.defaultValue,c.defaultValue,c.checked,c.defaultChecked,c.type,c.name)}}for(a=0;a<i.length;a++)r=i[a],r.form===e.form&&Un(r)}break e;case"textarea":ze(e,i.value,i.defaultValue);break e;case"select":a=i.value,a!=null&&de(e,!!i.multiple,a,!1)}}}var xt=!1;function Pt(e,a,i){if(xt)return e(a,i);xt=!0;try{var r=e(a);return r}finally{if(xt=!1,(nt!==null||xa!==null)&&(eo(),nt&&(a=nt,e=xa,xa=nt=null,Na(a),e)))for(a=0;a<e.length;a++)Na(e[a])}}function _a(e,a){var i=e.stateNode;if(i===null)return null;var r=i[lt]||null;if(r===null)return null;i=r[a];e:switch(a){case"onClick":case"onClickCapture":case"onDoubleClick":case"onDoubleClickCapture":case"onMouseDown":case"onMouseDownCapture":case"onMouseMove":case"onMouseMoveCapture":case"onMouseUp":case"onMouseUpCapture":case"onMouseEnter":(r=!r.disabled)||(e=e.type,r=!(e==="button"||e==="input"||e==="select"||e==="textarea")),e=!r;break e;default:e=!1}if(e)return null;if(i&&typeof i!="function")throw Error(o(231,a,typeof i));return i}var mn=!(typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"),Js=!1;if(mn)try{var It={};Object.defineProperty(It,"passive",{get:function(){Js=!0}}),window.addEventListener("test",It,It),window.removeEventListener("test",It,It)}catch{Js=!1}var ya=null,Va=null,gl=null;function hf(){if(gl)return gl;var e,a=Va,i=a.length,r,c="value"in ya?ya.value:ya.textContent,u=c.length;for(e=0;e<i&&a[e]===c[e];e++);var y=i-e;for(r=1;r<=y&&a[i-r]===c[u-r];r++);return gl=c.slice(e,1<r?1-r:void 0)}function xl(e){var a=e.keyCode;return"charCode"in e?(e=e.charCode,e===0&&a===13&&(e=13)):e=a,e===10&&(e=13),32<=e||e===13?e:0}function yl(){return!0}function mf(){return!1}function Oa(e){function a(i,r,c,u,y){this._reactName=i,this._targetInst=c,this.type=r,this.nativeEvent=u,this.target=y,this.currentTarget=null;for(var w in e)e.hasOwnProperty(w)&&(i=e[w],this[w]=i?i(u):u[w]);return this.isDefaultPrevented=(u.defaultPrevented!=null?u.defaultPrevented:u.returnValue===!1)?yl:mf,this.isPropagationStopped=mf,this}return x(a.prototype,{preventDefault:function(){this.defaultPrevented=!0;var i=this.nativeEvent;i&&(i.preventDefault?i.preventDefault():typeof i.returnValue!="unknown"&&(i.returnValue=!1),this.isDefaultPrevented=yl)},stopPropagation:function(){var i=this.nativeEvent;i&&(i.stopPropagation?i.stopPropagation():typeof i.cancelBubble!="unknown"&&(i.cancelBubble=!0),this.isPropagationStopped=yl)},persist:function(){},isPersistent:yl}),a}var Ei={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(e){return e.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},vl=Oa(Ei),Ws=x({},Ei,{view:0,detail:0}),o0=Oa(Ws),oc,cc,Ks,bl=x({},Ws,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:uc,button:0,buttons:0,relatedTarget:function(e){return e.relatedTarget===void 0?e.fromElement===e.srcElement?e.toElement:e.fromElement:e.relatedTarget},movementX:function(e){return"movementX"in e?e.movementX:(e!==Ks&&(Ks&&e.type==="mousemove"?(oc=e.screenX-Ks.screenX,cc=e.screenY-Ks.screenY):cc=oc=0,Ks=e),oc)},movementY:function(e){return"movementY"in e?e.movementY:cc}}),pf=Oa(bl),c0=x({},bl,{dataTransfer:0}),d0=Oa(c0),u0=x({},Ws,{relatedTarget:0}),dc=Oa(u0),f0=x({},Ei,{animationName:0,elapsedTime:0,pseudoElement:0}),h0=Oa(f0),m0=x({},Ei,{clipboardData:function(e){return"clipboardData"in e?e.clipboardData:window.clipboardData}}),p0=Oa(m0),g0=x({},Ei,{data:0}),gf=Oa(g0),x0={Esc:"Escape",Spacebar:" ",Left:"ArrowLeft",Up:"ArrowUp",Right:"ArrowRight",Down:"ArrowDown",Del:"Delete",Win:"OS",Menu:"ContextMenu",Apps:"ContextMenu",Scroll:"ScrollLock",MozPrintableKey:"Unidentified"},y0={8:"Backspace",9:"Tab",12:"Clear",13:"Enter",16:"Shift",17:"Control",18:"Alt",19:"Pause",20:"CapsLock",27:"Escape",32:" ",33:"PageUp",34:"PageDown",35:"End",36:"Home",37:"ArrowLeft",38:"ArrowUp",39:"ArrowRight",40:"ArrowDown",45:"Insert",46:"Delete",112:"F1",113:"F2",114:"F3",115:"F4",116:"F5",117:"F6",118:"F7",119:"F8",120:"F9",121:"F10",122:"F11",123:"F12",144:"NumLock",145:"ScrollLock",224:"Meta"},v0={Alt:"altKey",Control:"ctrlKey",Meta:"metaKey",Shift:"shiftKey"};function b0(e){var a=this.nativeEvent;return a.getModifierState?a.getModifierState(e):(e=v0[e])?!!a[e]:!1}function uc(){return b0}var j0=x({},Ws,{key:function(e){if(e.key){var a=x0[e.key]||e.key;if(a!=="Unidentified")return a}return e.type==="keypress"?(e=xl(e),e===13?"Enter":String.fromCharCode(e)):e.type==="keydown"||e.type==="keyup"?y0[e.keyCode]||"Unidentified":""},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:uc,charCode:function(e){return e.type==="keypress"?xl(e):0},keyCode:function(e){return e.type==="keydown"||e.type==="keyup"?e.keyCode:0},which:function(e){return e.type==="keypress"?xl(e):e.type==="keydown"||e.type==="keyup"?e.keyCode:0}}),w0=Oa(j0),N0=x({},bl,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0}),xf=Oa(N0),_0=x({},Ws,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:uc}),S0=Oa(_0),T0=x({},Ei,{propertyName:0,elapsedTime:0,pseudoElement:0}),C0=Oa(T0),A0=x({},bl,{deltaX:function(e){return"deltaX"in e?e.deltaX:"wheelDeltaX"in e?-e.wheelDeltaX:0},deltaY:function(e){return"deltaY"in e?e.deltaY:"wheelDeltaY"in e?-e.wheelDeltaY:"wheelDelta"in e?-e.wheelDelta:0},deltaZ:0,deltaMode:0}),z0=Oa(A0),k0=x({},Ei,{newState:0,oldState:0}),E0=Oa(k0),M0=[9,13,27,32],fc=mn&&"CompositionEvent"in window,er=null;mn&&"documentMode"in document&&(er=document.documentMode);var D0=mn&&"TextEvent"in window&&!er,yf=mn&&(!fc||er&&8<er&&11>=er),vf=" ",bf=!1;function jf(e,a){switch(e){case"keyup":return M0.indexOf(a.keyCode)!==-1;case"keydown":return a.keyCode!==229;case"keypress":case"mousedown":case"focusout":return!0;default:return!1}}function wf(e){return e=e.detail,typeof e=="object"&&"data"in e?e.data:null}var ls=!1;function R0(e,a){switch(e){case"compositionend":return wf(a);case"keypress":return a.which!==32?null:(bf=!0,vf);case"textInput":return e=a.data,e===vf&&bf?null:e;default:return null}}function O0(e,a){if(ls)return e==="compositionend"||!fc&&jf(e,a)?(e=hf(),gl=Va=ya=null,ls=!1,e):null;switch(e){case"paste":return null;case"keypress":if(!(a.ctrlKey||a.altKey||a.metaKey)||a.ctrlKey&&a.altKey){if(a.char&&1<a.char.length)return a.char;if(a.which)return String.fromCharCode(a.which)}return null;case"compositionend":return yf&&a.locale!=="ko"?null:a.data;default:return null}}var U0={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function Nf(e){var a=e&&e.nodeName&&e.nodeName.toLowerCase();return a==="input"?!!U0[e.type]:a==="textarea"}function _f(e,a,i,r){nt?xa?xa.push(r):xa=[r]:nt=r,a=ro(a,"onChange"),0<a.length&&(i=new vl("onChange","change",null,i,r),e.push({event:i,listeners:a}))}var tr=null,ar=null;function L0(e){ip(e,0)}function jl(e){var a=sa(e);if(Un(a))return e}function Sf(e,a){if(e==="change")return a}var Tf=!1;if(mn){var hc;if(mn){var mc="oninput"in document;if(!mc){var Cf=document.createElement("div");Cf.setAttribute("oninput","return;"),mc=typeof Cf.oninput=="function"}hc=mc}else hc=!1;Tf=hc&&(!document.documentMode||9<document.documentMode)}function Af(){tr&&(tr.detachEvent("onpropertychange",zf),ar=tr=null)}function zf(e){if(e.propertyName==="value"&&jl(ar)){var a=[];_f(a,ar,e,Ge(e)),Pt(L0,a)}}function B0(e,a,i){e==="focusin"?(Af(),tr=a,ar=i,tr.attachEvent("onpropertychange",zf)):e==="focusout"&&Af()}function q0(e){if(e==="selectionchange"||e==="keyup"||e==="keydown")return jl(ar)}function H0(e,a){if(e==="click")return jl(a)}function I0(e,a){if(e==="input"||e==="change")return jl(a)}function $0(e,a){return e===a&&(e!==0||1/e===1/a)||e!==e&&a!==a}var Pa=typeof Object.is=="function"?Object.is:$0;function nr(e,a){if(Pa(e,a))return!0;if(typeof e!="object"||e===null||typeof a!="object"||a===null)return!1;var i=Object.keys(e),r=Object.keys(a);if(i.length!==r.length)return!1;for(r=0;r<i.length;r++){var c=i[r];if(!J.call(a,c)||!Pa(e[c],a[c]))return!1}return!0}function kf(e){for(;e&&e.firstChild;)e=e.firstChild;return e}function Ef(e,a){var i=kf(e);e=0;for(var r;i;){if(i.nodeType===3){if(r=e+i.textContent.length,e<=a&&r>=a)return{node:i,offset:a-e};e=r}e:{for(;i;){if(i.nextSibling){i=i.nextSibling;break e}i=i.parentNode}i=void 0}i=kf(i)}}function Mf(e,a){return e&&a?e===a?!0:e&&e.nodeType===3?!1:a&&a.nodeType===3?Mf(e,a.parentNode):"contains"in e?e.contains(a):e.compareDocumentPosition?!!(e.compareDocumentPosition(a)&16):!1:!1}function Df(e){e=e!=null&&e.ownerDocument!=null&&e.ownerDocument.defaultView!=null?e.ownerDocument.defaultView:window;for(var a=Ln(e.document);a instanceof e.HTMLIFrameElement;){try{var i=typeof a.contentWindow.location.href=="string"}catch{i=!1}if(i)e=a.contentWindow;else break;a=Ln(e.document)}return a}function pc(e){var a=e&&e.nodeName&&e.nodeName.toLowerCase();return a&&(a==="input"&&(e.type==="text"||e.type==="search"||e.type==="tel"||e.type==="url"||e.type==="password")||a==="textarea"||e.contentEditable==="true")}var F0=mn&&"documentMode"in document&&11>=document.documentMode,os=null,gc=null,ir=null,xc=!1;function Rf(e,a,i){var r=i.window===i?i.document:i.nodeType===9?i:i.ownerDocument;xc||os==null||os!==Ln(r)||(r=os,"selectionStart"in r&&pc(r)?r={start:r.selectionStart,end:r.selectionEnd}:(r=(r.ownerDocument&&r.ownerDocument.defaultView||window).getSelection(),r={anchorNode:r.anchorNode,anchorOffset:r.anchorOffset,focusNode:r.focusNode,focusOffset:r.focusOffset}),ir&&nr(ir,r)||(ir=r,r=ro(gc,"onSelect"),0<r.length&&(a=new vl("onSelect","select",null,a,i),e.push({event:a,listeners:r}),a.target=os)))}function Mi(e,a){var i={};return i[e.toLowerCase()]=a.toLowerCase(),i["Webkit"+e]="webkit"+a,i["Moz"+e]="moz"+a,i}var cs={animationend:Mi("Animation","AnimationEnd"),animationiteration:Mi("Animation","AnimationIteration"),animationstart:Mi("Animation","AnimationStart"),transitionrun:Mi("Transition","TransitionRun"),transitionstart:Mi("Transition","TransitionStart"),transitioncancel:Mi("Transition","TransitionCancel"),transitionend:Mi("Transition","TransitionEnd")},yc={},Of={};mn&&(Of=document.createElement("div").style,"AnimationEvent"in window||(delete cs.animationend.animation,delete cs.animationiteration.animation,delete cs.animationstart.animation),"TransitionEvent"in window||delete cs.transitionend.transition);function Di(e){if(yc[e])return yc[e];if(!cs[e])return e;var a=cs[e],i;for(i in a)if(a.hasOwnProperty(i)&&i in Of)return yc[e]=a[i];return e}var Uf=Di("animationend"),Lf=Di("animationiteration"),Bf=Di("animationstart"),Y0=Di("transitionrun"),G0=Di("transitionstart"),V0=Di("transitioncancel"),qf=Di("transitionend"),Hf=new Map,vc="abort auxClick beforeToggle cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");vc.push("scrollEnd");function pn(e,a){Hf.set(e,a),Ya(a,[e])}var If=new WeakMap;function nn(e,a){if(typeof e=="object"&&e!==null){var i=If.get(e);return i!==void 0?i:(a={value:e,source:a,stack:ss(a)},If.set(e,a),a)}return{value:e,source:a,stack:ss(a)}}var sn=[],ds=0,bc=0;function wl(){for(var e=ds,a=bc=ds=0;a<e;){var i=sn[a];sn[a++]=null;var r=sn[a];sn[a++]=null;var c=sn[a];sn[a++]=null;var u=sn[a];if(sn[a++]=null,r!==null&&c!==null){var y=r.pending;y===null?c.next=c:(c.next=y.next,y.next=c),r.pending=c}u!==0&&$f(i,c,u)}}function Nl(e,a,i,r){sn[ds++]=e,sn[ds++]=a,sn[ds++]=i,sn[ds++]=r,bc|=r,e.lanes|=r,e=e.alternate,e!==null&&(e.lanes|=r)}function jc(e,a,i,r){return Nl(e,a,i,r),_l(e)}function us(e,a){return Nl(e,null,null,a),_l(e)}function $f(e,a,i){e.lanes|=i;var r=e.alternate;r!==null&&(r.lanes|=i);for(var c=!1,u=e.return;u!==null;)u.childLanes|=i,r=u.alternate,r!==null&&(r.childLanes|=i),u.tag===22&&(e=u.stateNode,e===null||e._visibility&1||(c=!0)),e=u,u=u.return;return e.tag===3?(u=e.stateNode,c&&a!==null&&(c=31-ft(i),e=u.hiddenUpdates,r=e[c],r===null?e[c]=[a]:r.push(a),a.lane=i|536870912),u):null}function _l(e){if(50<zr)throw zr=0,Cd=null,Error(o(185));for(var a=e.return;a!==null;)e=a,a=e.return;return e.tag===3?e.stateNode:null}var fs={};function P0(e,a,i,r){this.tag=e,this.key=i,this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null,this.index=0,this.refCleanup=this.ref=null,this.pendingProps=a,this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null,this.mode=r,this.subtreeFlags=this.flags=0,this.deletions=null,this.childLanes=this.lanes=0,this.alternate=null}function Xa(e,a,i,r){return new P0(e,a,i,r)}function wc(e){return e=e.prototype,!(!e||!e.isReactComponent)}function Bn(e,a){var i=e.alternate;return i===null?(i=Xa(e.tag,a,e.key,e.mode),i.elementType=e.elementType,i.type=e.type,i.stateNode=e.stateNode,i.alternate=e,e.alternate=i):(i.pendingProps=a,i.type=e.type,i.flags=0,i.subtreeFlags=0,i.deletions=null),i.flags=e.flags&65011712,i.childLanes=e.childLanes,i.lanes=e.lanes,i.child=e.child,i.memoizedProps=e.memoizedProps,i.memoizedState=e.memoizedState,i.updateQueue=e.updateQueue,a=e.dependencies,i.dependencies=a===null?null:{lanes:a.lanes,firstContext:a.firstContext},i.sibling=e.sibling,i.index=e.index,i.ref=e.ref,i.refCleanup=e.refCleanup,i}function Ff(e,a){e.flags&=65011714;var i=e.alternate;return i===null?(e.childLanes=0,e.lanes=a,e.child=null,e.subtreeFlags=0,e.memoizedProps=null,e.memoizedState=null,e.updateQueue=null,e.dependencies=null,e.stateNode=null):(e.childLanes=i.childLanes,e.lanes=i.lanes,e.child=i.child,e.subtreeFlags=0,e.deletions=null,e.memoizedProps=i.memoizedProps,e.memoizedState=i.memoizedState,e.updateQueue=i.updateQueue,e.type=i.type,a=i.dependencies,e.dependencies=a===null?null:{lanes:a.lanes,firstContext:a.firstContext}),e}function Sl(e,a,i,r,c,u){var y=0;if(r=e,typeof e=="function")wc(e)&&(y=1);else if(typeof e=="string")y=Zy(e,i,re.current)?26:e==="html"||e==="head"||e==="body"?27:5;else e:switch(e){case Ae:return e=Xa(31,i,a,c),e.elementType=Ae,e.lanes=u,e;case C:return Ri(i.children,c,u,a);case E:y=8,c|=24;break;case A:return e=Xa(12,i,a,c|2),e.elementType=A,e.lanes=u,e;case X:return e=Xa(13,i,a,c),e.elementType=X,e.lanes=u,e;case Q:return e=Xa(19,i,a,c),e.elementType=Q,e.lanes=u,e;default:if(typeof e=="object"&&e!==null)switch(e.$$typeof){case L:case P:y=10;break e;case q:y=9;break e;case M:y=11;break e;case K:y=14;break e;case se:y=16,r=null;break e}y=29,i=Error(o(130,e===null?"null":typeof e,"")),r=null}return a=Xa(y,i,a,c),a.elementType=e,a.type=r,a.lanes=u,a}function Ri(e,a,i,r){return e=Xa(7,e,r,a),e.lanes=i,e}function Nc(e,a,i){return e=Xa(6,e,null,a),e.lanes=i,e}function _c(e,a,i){return a=Xa(4,e.children!==null?e.children:[],e.key,a),a.lanes=i,a.stateNode={containerInfo:e.containerInfo,pendingChildren:null,implementation:e.implementation},a}var hs=[],ms=0,Tl=null,Cl=0,rn=[],ln=0,Oi=null,qn=1,Hn="";function Ui(e,a){hs[ms++]=Cl,hs[ms++]=Tl,Tl=e,Cl=a}function Yf(e,a,i){rn[ln++]=qn,rn[ln++]=Hn,rn[ln++]=Oi,Oi=e;var r=qn;e=Hn;var c=32-ft(r)-1;r&=~(1<<c),i+=1;var u=32-ft(a)+c;if(30<u){var y=c-c%5;u=(r&(1<<y)-1).toString(32),r>>=y,c-=y,qn=1<<32-ft(a)+c|i<<c|r,Hn=u+e}else qn=1<<u|i<<c|r,Hn=e}function Sc(e){e.return!==null&&(Ui(e,1),Yf(e,1,0))}function Tc(e){for(;e===Tl;)Tl=hs[--ms],hs[ms]=null,Cl=hs[--ms],hs[ms]=null;for(;e===Oi;)Oi=rn[--ln],rn[ln]=null,Hn=rn[--ln],rn[ln]=null,qn=rn[--ln],rn[ln]=null}var za=null,Jt=null,Nt=!1,Li=null,Nn=!1,Cc=Error(o(519));function Bi(e){var a=Error(o(418,""));throw lr(nn(a,e)),Cc}function Gf(e){var a=e.stateNode,i=e.type,r=e.memoizedProps;switch(a[Oe]=e,a[lt]=r,i){case"dialog":dt("cancel",a),dt("close",a);break;case"iframe":case"object":case"embed":dt("load",a);break;case"video":case"audio":for(i=0;i<Er.length;i++)dt(Er[i],a);break;case"source":dt("error",a);break;case"img":case"image":case"link":dt("error",a),dt("load",a);break;case"details":dt("toggle",a);break;case"input":dt("invalid",a),T(a,r.value,r.defaultValue,r.checked,r.defaultChecked,r.type,r.name,!0),an(a);break;case"select":dt("invalid",a);break;case"textarea":dt("invalid",a),Ze(a,r.value,r.defaultValue,r.children),an(a)}i=r.children,typeof i!="string"&&typeof i!="number"&&typeof i!="bigint"||a.textContent===""+i||r.suppressHydrationWarning===!0||op(a.textContent,i)?(r.popover!=null&&(dt("beforetoggle",a),dt("toggle",a)),r.onScroll!=null&&dt("scroll",a),r.onScrollEnd!=null&&dt("scrollend",a),r.onClick!=null&&(a.onclick=lo),a=!0):a=!1,a||Bi(e)}function Vf(e){for(za=e.return;za;)switch(za.tag){case 5:case 13:Nn=!1;return;case 27:case 3:Nn=!0;return;default:za=za.return}}function sr(e){if(e!==za)return!1;if(!Nt)return Vf(e),Nt=!0,!1;var a=e.tag,i;if((i=a!==3&&a!==27)&&((i=a===5)&&(i=e.type,i=!(i!=="form"&&i!=="button")||Fd(e.type,e.memoizedProps)),i=!i),i&&Jt&&Bi(e),Vf(e),a===13){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(o(317));e:{for(e=e.nextSibling,a=0;e;){if(e.nodeType===8)if(i=e.data,i==="/$"){if(a===0){Jt=xn(e.nextSibling);break e}a--}else i!=="$"&&i!=="$!"&&i!=="$?"||a++;e=e.nextSibling}Jt=null}}else a===27?(a=Jt,ji(e.type)?(e=Pd,Pd=null,Jt=e):Jt=a):Jt=za?xn(e.stateNode.nextSibling):null;return!0}function rr(){Jt=za=null,Nt=!1}function Pf(){var e=Li;return e!==null&&(Ba===null?Ba=e:Ba.push.apply(Ba,e),Li=null),e}function lr(e){Li===null?Li=[e]:Li.push(e)}var Ac=G(null),qi=null,In=null;function ri(e,a,i){oe(Ac,a._currentValue),a._currentValue=i}function $n(e){e._currentValue=Ac.current,ie(Ac)}function zc(e,a,i){for(;e!==null;){var r=e.alternate;if((e.childLanes&a)!==a?(e.childLanes|=a,r!==null&&(r.childLanes|=a)):r!==null&&(r.childLanes&a)!==a&&(r.childLanes|=a),e===i)break;e=e.return}}function kc(e,a,i,r){var c=e.child;for(c!==null&&(c.return=e);c!==null;){var u=c.dependencies;if(u!==null){var y=c.child;u=u.firstContext;e:for(;u!==null;){var w=u;u=c;for(var k=0;k<a.length;k++)if(w.context===a[k]){u.lanes|=i,w=u.alternate,w!==null&&(w.lanes|=i),zc(u.return,i,e),r||(y=null);break e}u=w.next}}else if(c.tag===18){if(y=c.return,y===null)throw Error(o(341));y.lanes|=i,u=y.alternate,u!==null&&(u.lanes|=i),zc(y,i,e),y=null}else y=c.child;if(y!==null)y.return=c;else for(y=c;y!==null;){if(y===e){y=null;break}if(c=y.sibling,c!==null){c.return=y.return,y=c;break}y=y.return}c=y}}function or(e,a,i,r){e=null;for(var c=a,u=!1;c!==null;){if(!u){if((c.flags&524288)!==0)u=!0;else if((c.flags&262144)!==0)break}if(c.tag===10){var y=c.alternate;if(y===null)throw Error(o(387));if(y=y.memoizedProps,y!==null){var w=c.type;Pa(c.pendingProps.value,y.value)||(e!==null?e.push(w):e=[w])}}else if(c===je.current){if(y=c.alternate,y===null)throw Error(o(387));y.memoizedState.memoizedState!==c.memoizedState.memoizedState&&(e!==null?e.push(Lr):e=[Lr])}c=c.return}e!==null&&kc(a,e,i,r),a.flags|=262144}function Al(e){for(e=e.firstContext;e!==null;){if(!Pa(e.context._currentValue,e.memoizedValue))return!0;e=e.next}return!1}function Hi(e){qi=e,In=null,e=e.dependencies,e!==null&&(e.firstContext=null)}function Sa(e){return Xf(qi,e)}function zl(e,a){return qi===null&&Hi(e),Xf(e,a)}function Xf(e,a){var i=a._currentValue;if(a={context:a,memoizedValue:i,next:null},In===null){if(e===null)throw Error(o(308));In=a,e.dependencies={lanes:0,firstContext:a},e.flags|=524288}else In=In.next=a;return i}var X0=typeof AbortController<"u"?AbortController:function(){var e=[],a=this.signal={aborted:!1,addEventListener:function(i,r){e.push(r)}};this.abort=function(){a.aborted=!0,e.forEach(function(i){return i()})}},Z0=n.unstable_scheduleCallback,Q0=n.unstable_NormalPriority,ra={$$typeof:P,Consumer:null,Provider:null,_currentValue:null,_currentValue2:null,_threadCount:0};function Ec(){return{controller:new X0,data:new Map,refCount:0}}function cr(e){e.refCount--,e.refCount===0&&Z0(Q0,function(){e.controller.abort()})}var dr=null,Mc=0,ps=0,gs=null;function J0(e,a){if(dr===null){var i=dr=[];Mc=0,ps=Rd(),gs={status:"pending",value:void 0,then:function(r){i.push(r)}}}return Mc++,a.then(Zf,Zf),a}function Zf(){if(--Mc===0&&dr!==null){gs!==null&&(gs.status="fulfilled");var e=dr;dr=null,ps=0,gs=null;for(var a=0;a<e.length;a++)(0,e[a])()}}function W0(e,a){var i=[],r={status:"pending",value:null,reason:null,then:function(c){i.push(c)}};return e.then(function(){r.status="fulfilled",r.value=a;for(var c=0;c<i.length;c++)(0,i[c])(a)},function(c){for(r.status="rejected",r.reason=c,c=0;c<i.length;c++)(0,i[c])(void 0)}),r}var Qf=S.S;S.S=function(e,a){typeof a=="object"&&a!==null&&typeof a.then=="function"&&J0(e,a),Qf!==null&&Qf(e,a)};var Ii=G(null);function Dc(){var e=Ii.current;return e!==null?e:$t.pooledCache}function kl(e,a){a===null?oe(Ii,Ii.current):oe(Ii,a.pool)}function Jf(){var e=Dc();return e===null?null:{parent:ra._currentValue,pool:e}}var ur=Error(o(460)),Wf=Error(o(474)),El=Error(o(542)),Rc={then:function(){}};function Kf(e){return e=e.status,e==="fulfilled"||e==="rejected"}function Ml(){}function eh(e,a,i){switch(i=e[i],i===void 0?e.push(a):i!==a&&(a.then(Ml,Ml),a=i),a.status){case"fulfilled":return a.value;case"rejected":throw e=a.reason,ah(e),e;default:if(typeof a.status=="string")a.then(Ml,Ml);else{if(e=$t,e!==null&&100<e.shellSuspendCounter)throw Error(o(482));e=a,e.status="pending",e.then(function(r){if(a.status==="pending"){var c=a;c.status="fulfilled",c.value=r}},function(r){if(a.status==="pending"){var c=a;c.status="rejected",c.reason=r}})}switch(a.status){case"fulfilled":return a.value;case"rejected":throw e=a.reason,ah(e),e}throw fr=a,ur}}var fr=null;function th(){if(fr===null)throw Error(o(459));var e=fr;return fr=null,e}function ah(e){if(e===ur||e===El)throw Error(o(483))}var li=!1;function Oc(e){e.updateQueue={baseState:e.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,lanes:0,hiddenCallbacks:null},callbacks:null}}function Uc(e,a){e=e.updateQueue,a.updateQueue===e&&(a.updateQueue={baseState:e.baseState,firstBaseUpdate:e.firstBaseUpdate,lastBaseUpdate:e.lastBaseUpdate,shared:e.shared,callbacks:null})}function oi(e){return{lane:e,tag:0,payload:null,callback:null,next:null}}function ci(e,a,i){var r=e.updateQueue;if(r===null)return null;if(r=r.shared,(At&2)!==0){var c=r.pending;return c===null?a.next=a:(a.next=c.next,c.next=a),r.pending=a,a=_l(e),$f(e,null,i),a}return Nl(e,r,a,i),_l(e)}function hr(e,a,i){if(a=a.updateQueue,a!==null&&(a=a.shared,(i&4194048)!==0)){var r=a.lanes;r&=e.pendingLanes,i|=r,a.lanes=i,rt(e,i)}}function Lc(e,a){var i=e.updateQueue,r=e.alternate;if(r!==null&&(r=r.updateQueue,i===r)){var c=null,u=null;if(i=i.firstBaseUpdate,i!==null){do{var y={lane:i.lane,tag:i.tag,payload:i.payload,callback:null,next:null};u===null?c=u=y:u=u.next=y,i=i.next}while(i!==null);u===null?c=u=a:u=u.next=a}else c=u=a;i={baseState:r.baseState,firstBaseUpdate:c,lastBaseUpdate:u,shared:r.shared,callbacks:r.callbacks},e.updateQueue=i;return}e=i.lastBaseUpdate,e===null?i.firstBaseUpdate=a:e.next=a,i.lastBaseUpdate=a}var Bc=!1;function mr(){if(Bc){var e=gs;if(e!==null)throw e}}function pr(e,a,i,r){Bc=!1;var c=e.updateQueue;li=!1;var u=c.firstBaseUpdate,y=c.lastBaseUpdate,w=c.shared.pending;if(w!==null){c.shared.pending=null;var k=w,Y=k.next;k.next=null,y===null?u=Y:y.next=Y,y=k;var le=e.alternate;le!==null&&(le=le.updateQueue,w=le.lastBaseUpdate,w!==y&&(w===null?le.firstBaseUpdate=Y:w.next=Y,le.lastBaseUpdate=k))}if(u!==null){var ye=c.baseState;y=0,le=Y=k=null,w=u;do{var Z=w.lane&-536870913,W=Z!==w.lane;if(W?(pt&Z)===Z:(r&Z)===Z){Z!==0&&Z===ps&&(Bc=!0),le!==null&&(le=le.next={lane:0,tag:w.tag,payload:w.payload,callback:null,next:null});e:{var We=e,Pe=w;Z=a;var Dt=i;switch(Pe.tag){case 1:if(We=Pe.payload,typeof We=="function"){ye=We.call(Dt,ye,Z);break e}ye=We;break e;case 3:We.flags=We.flags&-65537|128;case 0:if(We=Pe.payload,Z=typeof We=="function"?We.call(Dt,ye,Z):We,Z==null)break e;ye=x({},ye,Z);break e;case 2:li=!0}}Z=w.callback,Z!==null&&(e.flags|=64,W&&(e.flags|=8192),W=c.callbacks,W===null?c.callbacks=[Z]:W.push(Z))}else W={lane:Z,tag:w.tag,payload:w.payload,callback:w.callback,next:null},le===null?(Y=le=W,k=ye):le=le.next=W,y|=Z;if(w=w.next,w===null){if(w=c.shared.pending,w===null)break;W=w,w=W.next,W.next=null,c.lastBaseUpdate=W,c.shared.pending=null}}while(!0);le===null&&(k=ye),c.baseState=k,c.firstBaseUpdate=Y,c.lastBaseUpdate=le,u===null&&(c.shared.lanes=0),xi|=y,e.lanes=y,e.memoizedState=ye}}function nh(e,a){if(typeof e!="function")throw Error(o(191,e));e.call(a)}function ih(e,a){var i=e.callbacks;if(i!==null)for(e.callbacks=null,e=0;e<i.length;e++)nh(i[e],a)}var xs=G(null),Dl=G(0);function sh(e,a){e=Zn,oe(Dl,e),oe(xs,a),Zn=e|a.baseLanes}function qc(){oe(Dl,Zn),oe(xs,xs.current)}function Hc(){Zn=Dl.current,ie(xs),ie(Dl)}var di=0,st=null,Et=null,aa=null,Rl=!1,ys=!1,$i=!1,Ol=0,gr=0,vs=null,K0=0;function Kt(){throw Error(o(321))}function Ic(e,a){if(a===null)return!1;for(var i=0;i<a.length&&i<e.length;i++)if(!Pa(e[i],a[i]))return!1;return!0}function $c(e,a,i,r,c,u){return di=u,st=a,a.memoizedState=null,a.updateQueue=null,a.lanes=0,S.H=e===null||e.memoizedState===null?$h:Fh,$i=!1,u=i(r,c),$i=!1,ys&&(u=lh(a,i,r,c)),rh(e),u}function rh(e){S.H=Il;var a=Et!==null&&Et.next!==null;if(di=0,aa=Et=st=null,Rl=!1,gr=0,vs=null,a)throw Error(o(300));e===null||fa||(e=e.dependencies,e!==null&&Al(e)&&(fa=!0))}function lh(e,a,i,r){st=e;var c=0;do{if(ys&&(vs=null),gr=0,ys=!1,25<=c)throw Error(o(301));if(c+=1,aa=Et=null,e.updateQueue!=null){var u=e.updateQueue;u.lastEffect=null,u.events=null,u.stores=null,u.memoCache!=null&&(u.memoCache.index=0)}S.H=ry,u=a(i,r)}while(ys);return u}function ey(){var e=S.H,a=e.useState()[0];return a=typeof a.then=="function"?xr(a):a,e=e.useState()[0],(Et!==null?Et.memoizedState:null)!==e&&(st.flags|=1024),a}function Fc(){var e=Ol!==0;return Ol=0,e}function Yc(e,a,i){a.updateQueue=e.updateQueue,a.flags&=-2053,e.lanes&=~i}function Gc(e){if(Rl){for(e=e.memoizedState;e!==null;){var a=e.queue;a!==null&&(a.pending=null),e=e.next}Rl=!1}di=0,aa=Et=st=null,ys=!1,gr=Ol=0,vs=null}function Ua(){var e={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};return aa===null?st.memoizedState=aa=e:aa=aa.next=e,aa}function na(){if(Et===null){var e=st.alternate;e=e!==null?e.memoizedState:null}else e=Et.next;var a=aa===null?st.memoizedState:aa.next;if(a!==null)aa=a,Et=e;else{if(e===null)throw st.alternate===null?Error(o(467)):Error(o(310));Et=e,e={memoizedState:Et.memoizedState,baseState:Et.baseState,baseQueue:Et.baseQueue,queue:Et.queue,next:null},aa===null?st.memoizedState=aa=e:aa=aa.next=e}return aa}function Vc(){return{lastEffect:null,events:null,stores:null,memoCache:null}}function xr(e){var a=gr;return gr+=1,vs===null&&(vs=[]),e=eh(vs,e,a),a=st,(aa===null?a.memoizedState:aa.next)===null&&(a=a.alternate,S.H=a===null||a.memoizedState===null?$h:Fh),e}function Ul(e){if(e!==null&&typeof e=="object"){if(typeof e.then=="function")return xr(e);if(e.$$typeof===P)return Sa(e)}throw Error(o(438,String(e)))}function Pc(e){var a=null,i=st.updateQueue;if(i!==null&&(a=i.memoCache),a==null){var r=st.alternate;r!==null&&(r=r.updateQueue,r!==null&&(r=r.memoCache,r!=null&&(a={data:r.data.map(function(c){return c.slice()}),index:0})))}if(a==null&&(a={data:[],index:0}),i===null&&(i=Vc(),st.updateQueue=i),i.memoCache=a,i=a.data[a.index],i===void 0)for(i=a.data[a.index]=Array(e),r=0;r<e;r++)i[r]=we;return a.index++,i}function Fn(e,a){return typeof a=="function"?a(e):a}function Ll(e){var a=na();return Xc(a,Et,e)}function Xc(e,a,i){var r=e.queue;if(r===null)throw Error(o(311));r.lastRenderedReducer=i;var c=e.baseQueue,u=r.pending;if(u!==null){if(c!==null){var y=c.next;c.next=u.next,u.next=y}a.baseQueue=c=u,r.pending=null}if(u=e.baseState,c===null)e.memoizedState=u;else{a=c.next;var w=y=null,k=null,Y=a,le=!1;do{var ye=Y.lane&-536870913;if(ye!==Y.lane?(pt&ye)===ye:(di&ye)===ye){var Z=Y.revertLane;if(Z===0)k!==null&&(k=k.next={lane:0,revertLane:0,action:Y.action,hasEagerState:Y.hasEagerState,eagerState:Y.eagerState,next:null}),ye===ps&&(le=!0);else if((di&Z)===Z){Y=Y.next,Z===ps&&(le=!0);continue}else ye={lane:0,revertLane:Y.revertLane,action:Y.action,hasEagerState:Y.hasEagerState,eagerState:Y.eagerState,next:null},k===null?(w=k=ye,y=u):k=k.next=ye,st.lanes|=Z,xi|=Z;ye=Y.action,$i&&i(u,ye),u=Y.hasEagerState?Y.eagerState:i(u,ye)}else Z={lane:ye,revertLane:Y.revertLane,action:Y.action,hasEagerState:Y.hasEagerState,eagerState:Y.eagerState,next:null},k===null?(w=k=Z,y=u):k=k.next=Z,st.lanes|=ye,xi|=ye;Y=Y.next}while(Y!==null&&Y!==a);if(k===null?y=u:k.next=w,!Pa(u,e.memoizedState)&&(fa=!0,le&&(i=gs,i!==null)))throw i;e.memoizedState=u,e.baseState=y,e.baseQueue=k,r.lastRenderedState=u}return c===null&&(r.lanes=0),[e.memoizedState,r.dispatch]}function Zc(e){var a=na(),i=a.queue;if(i===null)throw Error(o(311));i.lastRenderedReducer=e;var r=i.dispatch,c=i.pending,u=a.memoizedState;if(c!==null){i.pending=null;var y=c=c.next;do u=e(u,y.action),y=y.next;while(y!==c);Pa(u,a.memoizedState)||(fa=!0),a.memoizedState=u,a.baseQueue===null&&(a.baseState=u),i.lastRenderedState=u}return[u,r]}function oh(e,a,i){var r=st,c=na(),u=Nt;if(u){if(i===void 0)throw Error(o(407));i=i()}else i=a();var y=!Pa((Et||c).memoizedState,i);y&&(c.memoizedState=i,fa=!0),c=c.queue;var w=uh.bind(null,r,c,e);if(yr(2048,8,w,[e]),c.getSnapshot!==a||y||aa!==null&&aa.memoizedState.tag&1){if(r.flags|=2048,bs(9,Bl(),dh.bind(null,r,c,i,a),null),$t===null)throw Error(o(349));u||(di&124)!==0||ch(r,a,i)}return i}function ch(e,a,i){e.flags|=16384,e={getSnapshot:a,value:i},a=st.updateQueue,a===null?(a=Vc(),st.updateQueue=a,a.stores=[e]):(i=a.stores,i===null?a.stores=[e]:i.push(e))}function dh(e,a,i,r){a.value=i,a.getSnapshot=r,fh(a)&&hh(e)}function uh(e,a,i){return i(function(){fh(a)&&hh(e)})}function fh(e){var a=e.getSnapshot;e=e.value;try{var i=a();return!Pa(e,i)}catch{return!0}}function hh(e){var a=us(e,2);a!==null&&Ka(a,e,2)}function Qc(e){var a=Ua();if(typeof e=="function"){var i=e;if(e=i(),$i){vt(!0);try{i()}finally{vt(!1)}}}return a.memoizedState=a.baseState=e,a.queue={pending:null,lanes:0,dispatch:null,lastRenderedReducer:Fn,lastRenderedState:e},a}function mh(e,a,i,r){return e.baseState=i,Xc(e,Et,typeof r=="function"?r:Fn)}function ty(e,a,i,r,c){if(Hl(e))throw Error(o(485));if(e=a.action,e!==null){var u={payload:c,action:e,next:null,isTransition:!0,status:"pending",value:null,reason:null,listeners:[],then:function(y){u.listeners.push(y)}};S.T!==null?i(!0):u.isTransition=!1,r(u),i=a.pending,i===null?(u.next=a.pending=u,ph(a,u)):(u.next=i.next,a.pending=i.next=u)}}function ph(e,a){var i=a.action,r=a.payload,c=e.state;if(a.isTransition){var u=S.T,y={};S.T=y;try{var w=i(c,r),k=S.S;k!==null&&k(y,w),gh(e,a,w)}catch(Y){Jc(e,a,Y)}finally{S.T=u}}else try{u=i(c,r),gh(e,a,u)}catch(Y){Jc(e,a,Y)}}function gh(e,a,i){i!==null&&typeof i=="object"&&typeof i.then=="function"?i.then(function(r){xh(e,a,r)},function(r){return Jc(e,a,r)}):xh(e,a,i)}function xh(e,a,i){a.status="fulfilled",a.value=i,yh(a),e.state=i,a=e.pending,a!==null&&(i=a.next,i===a?e.pending=null:(i=i.next,a.next=i,ph(e,i)))}function Jc(e,a,i){var r=e.pending;if(e.pending=null,r!==null){r=r.next;do a.status="rejected",a.reason=i,yh(a),a=a.next;while(a!==r)}e.action=null}function yh(e){e=e.listeners;for(var a=0;a<e.length;a++)(0,e[a])()}function vh(e,a){return a}function bh(e,a){if(Nt){var i=$t.formState;if(i!==null){e:{var r=st;if(Nt){if(Jt){t:{for(var c=Jt,u=Nn;c.nodeType!==8;){if(!u){c=null;break t}if(c=xn(c.nextSibling),c===null){c=null;break t}}u=c.data,c=u==="F!"||u==="F"?c:null}if(c){Jt=xn(c.nextSibling),r=c.data==="F!";break e}}Bi(r)}r=!1}r&&(a=i[0])}}return i=Ua(),i.memoizedState=i.baseState=a,r={pending:null,lanes:0,dispatch:null,lastRenderedReducer:vh,lastRenderedState:a},i.queue=r,i=qh.bind(null,st,r),r.dispatch=i,r=Qc(!1),u=ad.bind(null,st,!1,r.queue),r=Ua(),c={state:a,dispatch:null,action:e,pending:null},r.queue=c,i=ty.bind(null,st,c,u,i),c.dispatch=i,r.memoizedState=e,[a,i,!1]}function jh(e){var a=na();return wh(a,Et,e)}function wh(e,a,i){if(a=Xc(e,a,vh)[0],e=Ll(Fn)[0],typeof a=="object"&&a!==null&&typeof a.then=="function")try{var r=xr(a)}catch(y){throw y===ur?El:y}else r=a;a=na();var c=a.queue,u=c.dispatch;return i!==a.memoizedState&&(st.flags|=2048,bs(9,Bl(),ay.bind(null,c,i),null)),[r,u,e]}function ay(e,a){e.action=a}function Nh(e){var a=na(),i=Et;if(i!==null)return wh(a,i,e);na(),a=a.memoizedState,i=na();var r=i.queue.dispatch;return i.memoizedState=e,[a,r,!1]}function bs(e,a,i,r){return e={tag:e,create:i,deps:r,inst:a,next:null},a=st.updateQueue,a===null&&(a=Vc(),st.updateQueue=a),i=a.lastEffect,i===null?a.lastEffect=e.next=e:(r=i.next,i.next=e,e.next=r,a.lastEffect=e),e}function Bl(){return{destroy:void 0,resource:void 0}}function _h(){return na().memoizedState}function ql(e,a,i,r){var c=Ua();r=r===void 0?null:r,st.flags|=e,c.memoizedState=bs(1|a,Bl(),i,r)}function yr(e,a,i,r){var c=na();r=r===void 0?null:r;var u=c.memoizedState.inst;Et!==null&&r!==null&&Ic(r,Et.memoizedState.deps)?c.memoizedState=bs(a,u,i,r):(st.flags|=e,c.memoizedState=bs(1|a,u,i,r))}function Sh(e,a){ql(8390656,8,e,a)}function Th(e,a){yr(2048,8,e,a)}function Ch(e,a){return yr(4,2,e,a)}function Ah(e,a){return yr(4,4,e,a)}function zh(e,a){if(typeof a=="function"){e=e();var i=a(e);return function(){typeof i=="function"?i():a(null)}}if(a!=null)return e=e(),a.current=e,function(){a.current=null}}function kh(e,a,i){i=i!=null?i.concat([e]):null,yr(4,4,zh.bind(null,a,e),i)}function Wc(){}function Eh(e,a){var i=na();a=a===void 0?null:a;var r=i.memoizedState;return a!==null&&Ic(a,r[1])?r[0]:(i.memoizedState=[e,a],e)}function Mh(e,a){var i=na();a=a===void 0?null:a;var r=i.memoizedState;if(a!==null&&Ic(a,r[1]))return r[0];if(r=e(),$i){vt(!0);try{e()}finally{vt(!1)}}return i.memoizedState=[r,a],r}function Kc(e,a,i){return i===void 0||(di&1073741824)!==0?e.memoizedState=a:(e.memoizedState=i,e=Om(),st.lanes|=e,xi|=e,i)}function Dh(e,a,i,r){return Pa(i,a)?i:xs.current!==null?(e=Kc(e,i,r),Pa(e,a)||(fa=!0),e):(di&42)===0?(fa=!0,e.memoizedState=i):(e=Om(),st.lanes|=e,xi|=e,a)}function Rh(e,a,i,r,c){var u=H.p;H.p=u!==0&&8>u?u:8;var y=S.T,w={};S.T=w,ad(e,!1,a,i);try{var k=c(),Y=S.S;if(Y!==null&&Y(w,k),k!==null&&typeof k=="object"&&typeof k.then=="function"){var le=W0(k,r);vr(e,a,le,Wa(e))}else vr(e,a,r,Wa(e))}catch(ye){vr(e,a,{then:function(){},status:"rejected",reason:ye},Wa())}finally{H.p=u,S.T=y}}function ny(){}function ed(e,a,i,r){if(e.tag!==5)throw Error(o(476));var c=Oh(e).queue;Rh(e,c,a,F,i===null?ny:function(){return Uh(e),i(r)})}function Oh(e){var a=e.memoizedState;if(a!==null)return a;a={memoizedState:F,baseState:F,baseQueue:null,queue:{pending:null,lanes:0,dispatch:null,lastRenderedReducer:Fn,lastRenderedState:F},next:null};var i={};return a.next={memoizedState:i,baseState:i,baseQueue:null,queue:{pending:null,lanes:0,dispatch:null,lastRenderedReducer:Fn,lastRenderedState:i},next:null},e.memoizedState=a,e=e.alternate,e!==null&&(e.memoizedState=a),a}function Uh(e){var a=Oh(e).next.queue;vr(e,a,{},Wa())}function td(){return Sa(Lr)}function Lh(){return na().memoizedState}function Bh(){return na().memoizedState}function iy(e){for(var a=e.return;a!==null;){switch(a.tag){case 24:case 3:var i=Wa();e=oi(i);var r=ci(a,e,i);r!==null&&(Ka(r,a,i),hr(r,a,i)),a={cache:Ec()},e.payload=a;return}a=a.return}}function sy(e,a,i){var r=Wa();i={lane:r,revertLane:0,action:i,hasEagerState:!1,eagerState:null,next:null},Hl(e)?Hh(a,i):(i=jc(e,a,i,r),i!==null&&(Ka(i,e,r),Ih(i,a,r)))}function qh(e,a,i){var r=Wa();vr(e,a,i,r)}function vr(e,a,i,r){var c={lane:r,revertLane:0,action:i,hasEagerState:!1,eagerState:null,next:null};if(Hl(e))Hh(a,c);else{var u=e.alternate;if(e.lanes===0&&(u===null||u.lanes===0)&&(u=a.lastRenderedReducer,u!==null))try{var y=a.lastRenderedState,w=u(y,i);if(c.hasEagerState=!0,c.eagerState=w,Pa(w,y))return Nl(e,a,c,0),$t===null&&wl(),!1}catch{}finally{}if(i=jc(e,a,c,r),i!==null)return Ka(i,e,r),Ih(i,a,r),!0}return!1}function ad(e,a,i,r){if(r={lane:2,revertLane:Rd(),action:r,hasEagerState:!1,eagerState:null,next:null},Hl(e)){if(a)throw Error(o(479))}else a=jc(e,i,r,2),a!==null&&Ka(a,e,2)}function Hl(e){var a=e.alternate;return e===st||a!==null&&a===st}function Hh(e,a){ys=Rl=!0;var i=e.pending;i===null?a.next=a:(a.next=i.next,i.next=a),e.pending=a}function Ih(e,a,i){if((i&4194048)!==0){var r=a.lanes;r&=e.pendingLanes,i|=r,a.lanes=i,rt(e,i)}}var Il={readContext:Sa,use:Ul,useCallback:Kt,useContext:Kt,useEffect:Kt,useImperativeHandle:Kt,useLayoutEffect:Kt,useInsertionEffect:Kt,useMemo:Kt,useReducer:Kt,useRef:Kt,useState:Kt,useDebugValue:Kt,useDeferredValue:Kt,useTransition:Kt,useSyncExternalStore:Kt,useId:Kt,useHostTransitionStatus:Kt,useFormState:Kt,useActionState:Kt,useOptimistic:Kt,useMemoCache:Kt,useCacheRefresh:Kt},$h={readContext:Sa,use:Ul,useCallback:function(e,a){return Ua().memoizedState=[e,a===void 0?null:a],e},useContext:Sa,useEffect:Sh,useImperativeHandle:function(e,a,i){i=i!=null?i.concat([e]):null,ql(4194308,4,zh.bind(null,a,e),i)},useLayoutEffect:function(e,a){return ql(4194308,4,e,a)},useInsertionEffect:function(e,a){ql(4,2,e,a)},useMemo:function(e,a){var i=Ua();a=a===void 0?null:a;var r=e();if($i){vt(!0);try{e()}finally{vt(!1)}}return i.memoizedState=[r,a],r},useReducer:function(e,a,i){var r=Ua();if(i!==void 0){var c=i(a);if($i){vt(!0);try{i(a)}finally{vt(!1)}}}else c=a;return r.memoizedState=r.baseState=c,e={pending:null,lanes:0,dispatch:null,lastRenderedReducer:e,lastRenderedState:c},r.queue=e,e=e.dispatch=sy.bind(null,st,e),[r.memoizedState,e]},useRef:function(e){var a=Ua();return e={current:e},a.memoizedState=e},useState:function(e){e=Qc(e);var a=e.queue,i=qh.bind(null,st,a);return a.dispatch=i,[e.memoizedState,i]},useDebugValue:Wc,useDeferredValue:function(e,a){var i=Ua();return Kc(i,e,a)},useTransition:function(){var e=Qc(!1);return e=Rh.bind(null,st,e.queue,!0,!1),Ua().memoizedState=e,[!1,e]},useSyncExternalStore:function(e,a,i){var r=st,c=Ua();if(Nt){if(i===void 0)throw Error(o(407));i=i()}else{if(i=a(),$t===null)throw Error(o(349));(pt&124)!==0||ch(r,a,i)}c.memoizedState=i;var u={value:i,getSnapshot:a};return c.queue=u,Sh(uh.bind(null,r,u,e),[e]),r.flags|=2048,bs(9,Bl(),dh.bind(null,r,u,i,a),null),i},useId:function(){var e=Ua(),a=$t.identifierPrefix;if(Nt){var i=Hn,r=qn;i=(r&~(1<<32-ft(r)-1)).toString(32)+i,a="«"+a+"R"+i,i=Ol++,0<i&&(a+="H"+i.toString(32)),a+="»"}else i=K0++,a="«"+a+"r"+i.toString(32)+"»";return e.memoizedState=a},useHostTransitionStatus:td,useFormState:bh,useActionState:bh,useOptimistic:function(e){var a=Ua();a.memoizedState=a.baseState=e;var i={pending:null,lanes:0,dispatch:null,lastRenderedReducer:null,lastRenderedState:null};return a.queue=i,a=ad.bind(null,st,!0,i),i.dispatch=a,[e,a]},useMemoCache:Pc,useCacheRefresh:function(){return Ua().memoizedState=iy.bind(null,st)}},Fh={readContext:Sa,use:Ul,useCallback:Eh,useContext:Sa,useEffect:Th,useImperativeHandle:kh,useInsertionEffect:Ch,useLayoutEffect:Ah,useMemo:Mh,useReducer:Ll,useRef:_h,useState:function(){return Ll(Fn)},useDebugValue:Wc,useDeferredValue:function(e,a){var i=na();return Dh(i,Et.memoizedState,e,a)},useTransition:function(){var e=Ll(Fn)[0],a=na().memoizedState;return[typeof e=="boolean"?e:xr(e),a]},useSyncExternalStore:oh,useId:Lh,useHostTransitionStatus:td,useFormState:jh,useActionState:jh,useOptimistic:function(e,a){var i=na();return mh(i,Et,e,a)},useMemoCache:Pc,useCacheRefresh:Bh},ry={readContext:Sa,use:Ul,useCallback:Eh,useContext:Sa,useEffect:Th,useImperativeHandle:kh,useInsertionEffect:Ch,useLayoutEffect:Ah,useMemo:Mh,useReducer:Zc,useRef:_h,useState:function(){return Zc(Fn)},useDebugValue:Wc,useDeferredValue:function(e,a){var i=na();return Et===null?Kc(i,e,a):Dh(i,Et.memoizedState,e,a)},useTransition:function(){var e=Zc(Fn)[0],a=na().memoizedState;return[typeof e=="boolean"?e:xr(e),a]},useSyncExternalStore:oh,useId:Lh,useHostTransitionStatus:td,useFormState:Nh,useActionState:Nh,useOptimistic:function(e,a){var i=na();return Et!==null?mh(i,Et,e,a):(i.baseState=e,[e,i.queue.dispatch])},useMemoCache:Pc,useCacheRefresh:Bh},js=null,br=0;function $l(e){var a=br;return br+=1,js===null&&(js=[]),eh(js,e,a)}function jr(e,a){a=a.props.ref,e.ref=a!==void 0?a:null}function Fl(e,a){throw a.$$typeof===v?Error(o(525)):(e=Object.prototype.toString.call(a),Error(o(31,e==="[object Object]"?"object with keys {"+Object.keys(a).join(", ")+"}":e)))}function Yh(e){var a=e._init;return a(e._payload)}function Gh(e){function a(B,O){if(e){var $=B.deletions;$===null?(B.deletions=[O],B.flags|=16):$.push(O)}}function i(B,O){if(!e)return null;for(;O!==null;)a(B,O),O=O.sibling;return null}function r(B){for(var O=new Map;B!==null;)B.key!==null?O.set(B.key,B):O.set(B.index,B),B=B.sibling;return O}function c(B,O){return B=Bn(B,O),B.index=0,B.sibling=null,B}function u(B,O,$){return B.index=$,e?($=B.alternate,$!==null?($=$.index,$<O?(B.flags|=67108866,O):$):(B.flags|=67108866,O)):(B.flags|=1048576,O)}function y(B){return e&&B.alternate===null&&(B.flags|=67108866),B}function w(B,O,$,he){return O===null||O.tag!==6?(O=Nc($,B.mode,he),O.return=B,O):(O=c(O,$),O.return=B,O)}function k(B,O,$,he){var qe=$.type;return qe===C?le(B,O,$.props.children,he,$.key):O!==null&&(O.elementType===qe||typeof qe=="object"&&qe!==null&&qe.$$typeof===se&&Yh(qe)===O.type)?(O=c(O,$.props),jr(O,$),O.return=B,O):(O=Sl($.type,$.key,$.props,null,B.mode,he),jr(O,$),O.return=B,O)}function Y(B,O,$,he){return O===null||O.tag!==4||O.stateNode.containerInfo!==$.containerInfo||O.stateNode.implementation!==$.implementation?(O=_c($,B.mode,he),O.return=B,O):(O=c(O,$.children||[]),O.return=B,O)}function le(B,O,$,he,qe){return O===null||O.tag!==7?(O=Ri($,B.mode,he,qe),O.return=B,O):(O=c(O,$),O.return=B,O)}function ye(B,O,$){if(typeof O=="string"&&O!==""||typeof O=="number"||typeof O=="bigint")return O=Nc(""+O,B.mode,$),O.return=B,O;if(typeof O=="object"&&O!==null){switch(O.$$typeof){case b:return $=Sl(O.type,O.key,O.props,null,B.mode,$),jr($,O),$.return=B,$;case _:return O=_c(O,B.mode,$),O.return=B,O;case se:var he=O._init;return O=he(O._payload),ye(B,O,$)}if(He(O)||Ne(O))return O=Ri(O,B.mode,$,null),O.return=B,O;if(typeof O.then=="function")return ye(B,$l(O),$);if(O.$$typeof===P)return ye(B,zl(B,O),$);Fl(B,O)}return null}function Z(B,O,$,he){var qe=O!==null?O.key:null;if(typeof $=="string"&&$!==""||typeof $=="number"||typeof $=="bigint")return qe!==null?null:w(B,O,""+$,he);if(typeof $=="object"&&$!==null){switch($.$$typeof){case b:return $.key===qe?k(B,O,$,he):null;case _:return $.key===qe?Y(B,O,$,he):null;case se:return qe=$._init,$=qe($._payload),Z(B,O,$,he)}if(He($)||Ne($))return qe!==null?null:le(B,O,$,he,null);if(typeof $.then=="function")return Z(B,O,$l($),he);if($.$$typeof===P)return Z(B,O,zl(B,$),he);Fl(B,$)}return null}function W(B,O,$,he,qe){if(typeof he=="string"&&he!==""||typeof he=="number"||typeof he=="bigint")return B=B.get($)||null,w(O,B,""+he,qe);if(typeof he=="object"&&he!==null){switch(he.$$typeof){case b:return B=B.get(he.key===null?$:he.key)||null,k(O,B,he,qe);case _:return B=B.get(he.key===null?$:he.key)||null,Y(O,B,he,qe);case se:var ot=he._init;return he=ot(he._payload),W(B,O,$,he,qe)}if(He(he)||Ne(he))return B=B.get($)||null,le(O,B,he,qe,null);if(typeof he.then=="function")return W(B,O,$,$l(he),qe);if(he.$$typeof===P)return W(B,O,$,zl(O,he),qe);Fl(O,he)}return null}function We(B,O,$,he){for(var qe=null,ot=null,Ye=O,Qe=O=0,ma=null;Ye!==null&&Qe<$.length;Qe++){Ye.index>Qe?(ma=Ye,Ye=null):ma=Ye.sibling;var bt=Z(B,Ye,$[Qe],he);if(bt===null){Ye===null&&(Ye=ma);break}e&&Ye&&bt.alternate===null&&a(B,Ye),O=u(bt,O,Qe),ot===null?qe=bt:ot.sibling=bt,ot=bt,Ye=ma}if(Qe===$.length)return i(B,Ye),Nt&&Ui(B,Qe),qe;if(Ye===null){for(;Qe<$.length;Qe++)Ye=ye(B,$[Qe],he),Ye!==null&&(O=u(Ye,O,Qe),ot===null?qe=Ye:ot.sibling=Ye,ot=Ye);return Nt&&Ui(B,Qe),qe}for(Ye=r(Ye);Qe<$.length;Qe++)ma=W(Ye,B,Qe,$[Qe],he),ma!==null&&(e&&ma.alternate!==null&&Ye.delete(ma.key===null?Qe:ma.key),O=u(ma,O,Qe),ot===null?qe=ma:ot.sibling=ma,ot=ma);return e&&Ye.forEach(function(Ti){return a(B,Ti)}),Nt&&Ui(B,Qe),qe}function Pe(B,O,$,he){if($==null)throw Error(o(151));for(var qe=null,ot=null,Ye=O,Qe=O=0,ma=null,bt=$.next();Ye!==null&&!bt.done;Qe++,bt=$.next()){Ye.index>Qe?(ma=Ye,Ye=null):ma=Ye.sibling;var Ti=Z(B,Ye,bt.value,he);if(Ti===null){Ye===null&&(Ye=ma);break}e&&Ye&&Ti.alternate===null&&a(B,Ye),O=u(Ti,O,Qe),ot===null?qe=Ti:ot.sibling=Ti,ot=Ti,Ye=ma}if(bt.done)return i(B,Ye),Nt&&Ui(B,Qe),qe;if(Ye===null){for(;!bt.done;Qe++,bt=$.next())bt=ye(B,bt.value,he),bt!==null&&(O=u(bt,O,Qe),ot===null?qe=bt:ot.sibling=bt,ot=bt);return Nt&&Ui(B,Qe),qe}for(Ye=r(Ye);!bt.done;Qe++,bt=$.next())bt=W(Ye,B,Qe,bt.value,he),bt!==null&&(e&&bt.alternate!==null&&Ye.delete(bt.key===null?Qe:bt.key),O=u(bt,O,Qe),ot===null?qe=bt:ot.sibling=bt,ot=bt);return e&&Ye.forEach(function(lv){return a(B,lv)}),Nt&&Ui(B,Qe),qe}function Dt(B,O,$,he){if(typeof $=="object"&&$!==null&&$.type===C&&$.key===null&&($=$.props.children),typeof $=="object"&&$!==null){switch($.$$typeof){case b:e:{for(var qe=$.key;O!==null;){if(O.key===qe){if(qe=$.type,qe===C){if(O.tag===7){i(B,O.sibling),he=c(O,$.props.children),he.return=B,B=he;break e}}else if(O.elementType===qe||typeof qe=="object"&&qe!==null&&qe.$$typeof===se&&Yh(qe)===O.type){i(B,O.sibling),he=c(O,$.props),jr(he,$),he.return=B,B=he;break e}i(B,O);break}else a(B,O);O=O.sibling}$.type===C?(he=Ri($.props.children,B.mode,he,$.key),he.return=B,B=he):(he=Sl($.type,$.key,$.props,null,B.mode,he),jr(he,$),he.return=B,B=he)}return y(B);case _:e:{for(qe=$.key;O!==null;){if(O.key===qe)if(O.tag===4&&O.stateNode.containerInfo===$.containerInfo&&O.stateNode.implementation===$.implementation){i(B,O.sibling),he=c(O,$.children||[]),he.return=B,B=he;break e}else{i(B,O);break}else a(B,O);O=O.sibling}he=_c($,B.mode,he),he.return=B,B=he}return y(B);case se:return qe=$._init,$=qe($._payload),Dt(B,O,$,he)}if(He($))return We(B,O,$,he);if(Ne($)){if(qe=Ne($),typeof qe!="function")throw Error(o(150));return $=qe.call($),Pe(B,O,$,he)}if(typeof $.then=="function")return Dt(B,O,$l($),he);if($.$$typeof===P)return Dt(B,O,zl(B,$),he);Fl(B,$)}return typeof $=="string"&&$!==""||typeof $=="number"||typeof $=="bigint"?($=""+$,O!==null&&O.tag===6?(i(B,O.sibling),he=c(O,$),he.return=B,B=he):(i(B,O),he=Nc($,B.mode,he),he.return=B,B=he),y(B)):i(B,O)}return function(B,O,$,he){try{br=0;var qe=Dt(B,O,$,he);return js=null,qe}catch(Ye){if(Ye===ur||Ye===El)throw Ye;var ot=Xa(29,Ye,null,B.mode);return ot.lanes=he,ot.return=B,ot}finally{}}}var ws=Gh(!0),Vh=Gh(!1),on=G(null),_n=null;function ui(e){var a=e.alternate;oe(la,la.current&1),oe(on,e),_n===null&&(a===null||xs.current!==null||a.memoizedState!==null)&&(_n=e)}function Ph(e){if(e.tag===22){if(oe(la,la.current),oe(on,e),_n===null){var a=e.alternate;a!==null&&a.memoizedState!==null&&(_n=e)}}else fi()}function fi(){oe(la,la.current),oe(on,on.current)}function Yn(e){ie(on),_n===e&&(_n=null),ie(la)}var la=G(0);function Yl(e){for(var a=e;a!==null;){if(a.tag===13){var i=a.memoizedState;if(i!==null&&(i=i.dehydrated,i===null||i.data==="$?"||Vd(i)))return a}else if(a.tag===19&&a.memoizedProps.revealOrder!==void 0){if((a.flags&128)!==0)return a}else if(a.child!==null){a.child.return=a,a=a.child;continue}if(a===e)break;for(;a.sibling===null;){if(a.return===null||a.return===e)return null;a=a.return}a.sibling.return=a.return,a=a.sibling}return null}function nd(e,a,i,r){a=e.memoizedState,i=i(r,a),i=i==null?a:x({},a,i),e.memoizedState=i,e.lanes===0&&(e.updateQueue.baseState=i)}var id={enqueueSetState:function(e,a,i){e=e._reactInternals;var r=Wa(),c=oi(r);c.payload=a,i!=null&&(c.callback=i),a=ci(e,c,r),a!==null&&(Ka(a,e,r),hr(a,e,r))},enqueueReplaceState:function(e,a,i){e=e._reactInternals;var r=Wa(),c=oi(r);c.tag=1,c.payload=a,i!=null&&(c.callback=i),a=ci(e,c,r),a!==null&&(Ka(a,e,r),hr(a,e,r))},enqueueForceUpdate:function(e,a){e=e._reactInternals;var i=Wa(),r=oi(i);r.tag=2,a!=null&&(r.callback=a),a=ci(e,r,i),a!==null&&(Ka(a,e,i),hr(a,e,i))}};function Xh(e,a,i,r,c,u,y){return e=e.stateNode,typeof e.shouldComponentUpdate=="function"?e.shouldComponentUpdate(r,u,y):a.prototype&&a.prototype.isPureReactComponent?!nr(i,r)||!nr(c,u):!0}function Zh(e,a,i,r){e=a.state,typeof a.componentWillReceiveProps=="function"&&a.componentWillReceiveProps(i,r),typeof a.UNSAFE_componentWillReceiveProps=="function"&&a.UNSAFE_componentWillReceiveProps(i,r),a.state!==e&&id.enqueueReplaceState(a,a.state,null)}function Fi(e,a){var i=a;if("ref"in a){i={};for(var r in a)r!=="ref"&&(i[r]=a[r])}if(e=e.defaultProps){i===a&&(i=x({},i));for(var c in e)i[c]===void 0&&(i[c]=e[c])}return i}var Gl=typeof reportError=="function"?reportError:function(e){if(typeof window=="object"&&typeof window.ErrorEvent=="function"){var a=new window.ErrorEvent("error",{bubbles:!0,cancelable:!0,message:typeof e=="object"&&e!==null&&typeof e.message=="string"?String(e.message):String(e),error:e});if(!window.dispatchEvent(a))return}else if(typeof process=="object"&&typeof process.emit=="function"){process.emit("uncaughtException",e);return}console.error(e)};function Qh(e){Gl(e)}function Jh(e){console.error(e)}function Wh(e){Gl(e)}function Vl(e,a){try{var i=e.onUncaughtError;i(a.value,{componentStack:a.stack})}catch(r){setTimeout(function(){throw r})}}function Kh(e,a,i){try{var r=e.onCaughtError;r(i.value,{componentStack:i.stack,errorBoundary:a.tag===1?a.stateNode:null})}catch(c){setTimeout(function(){throw c})}}function sd(e,a,i){return i=oi(i),i.tag=3,i.payload={element:null},i.callback=function(){Vl(e,a)},i}function em(e){return e=oi(e),e.tag=3,e}function tm(e,a,i,r){var c=i.type.getDerivedStateFromError;if(typeof c=="function"){var u=r.value;e.payload=function(){return c(u)},e.callback=function(){Kh(a,i,r)}}var y=i.stateNode;y!==null&&typeof y.componentDidCatch=="function"&&(e.callback=function(){Kh(a,i,r),typeof c!="function"&&(yi===null?yi=new Set([this]):yi.add(this));var w=r.stack;this.componentDidCatch(r.value,{componentStack:w!==null?w:""})})}function ly(e,a,i,r,c){if(i.flags|=32768,r!==null&&typeof r=="object"&&typeof r.then=="function"){if(a=i.alternate,a!==null&&or(a,i,c,!0),i=on.current,i!==null){switch(i.tag){case 13:return _n===null?zd():i.alternate===null&&Wt===0&&(Wt=3),i.flags&=-257,i.flags|=65536,i.lanes=c,r===Rc?i.flags|=16384:(a=i.updateQueue,a===null?i.updateQueue=new Set([r]):a.add(r),Ed(e,r,c)),!1;case 22:return i.flags|=65536,r===Rc?i.flags|=16384:(a=i.updateQueue,a===null?(a={transitions:null,markerInstances:null,retryQueue:new Set([r])},i.updateQueue=a):(i=a.retryQueue,i===null?a.retryQueue=new Set([r]):i.add(r)),Ed(e,r,c)),!1}throw Error(o(435,i.tag))}return Ed(e,r,c),zd(),!1}if(Nt)return a=on.current,a!==null?((a.flags&65536)===0&&(a.flags|=256),a.flags|=65536,a.lanes=c,r!==Cc&&(e=Error(o(422),{cause:r}),lr(nn(e,i)))):(r!==Cc&&(a=Error(o(423),{cause:r}),lr(nn(a,i))),e=e.current.alternate,e.flags|=65536,c&=-c,e.lanes|=c,r=nn(r,i),c=sd(e.stateNode,r,c),Lc(e,c),Wt!==4&&(Wt=2)),!1;var u=Error(o(520),{cause:r});if(u=nn(u,i),Ar===null?Ar=[u]:Ar.push(u),Wt!==4&&(Wt=2),a===null)return!0;r=nn(r,i),i=a;do{switch(i.tag){case 3:return i.flags|=65536,e=c&-c,i.lanes|=e,e=sd(i.stateNode,r,e),Lc(i,e),!1;case 1:if(a=i.type,u=i.stateNode,(i.flags&128)===0&&(typeof a.getDerivedStateFromError=="function"||u!==null&&typeof u.componentDidCatch=="function"&&(yi===null||!yi.has(u))))return i.flags|=65536,c&=-c,i.lanes|=c,c=em(c),tm(c,e,i,r),Lc(i,c),!1}i=i.return}while(i!==null);return!1}var am=Error(o(461)),fa=!1;function va(e,a,i,r){a.child=e===null?Vh(a,null,i,r):ws(a,e.child,i,r)}function nm(e,a,i,r,c){i=i.render;var u=a.ref;if("ref"in r){var y={};for(var w in r)w!=="ref"&&(y[w]=r[w])}else y=r;return Hi(a),r=$c(e,a,i,y,u,c),w=Fc(),e!==null&&!fa?(Yc(e,a,c),Gn(e,a,c)):(Nt&&w&&Sc(a),a.flags|=1,va(e,a,r,c),a.child)}function im(e,a,i,r,c){if(e===null){var u=i.type;return typeof u=="function"&&!wc(u)&&u.defaultProps===void 0&&i.compare===null?(a.tag=15,a.type=u,sm(e,a,u,r,c)):(e=Sl(i.type,null,r,a,a.mode,c),e.ref=a.ref,e.return=a,a.child=e)}if(u=e.child,!hd(e,c)){var y=u.memoizedProps;if(i=i.compare,i=i!==null?i:nr,i(y,r)&&e.ref===a.ref)return Gn(e,a,c)}return a.flags|=1,e=Bn(u,r),e.ref=a.ref,e.return=a,a.child=e}function sm(e,a,i,r,c){if(e!==null){var u=e.memoizedProps;if(nr(u,r)&&e.ref===a.ref)if(fa=!1,a.pendingProps=r=u,hd(e,c))(e.flags&131072)!==0&&(fa=!0);else return a.lanes=e.lanes,Gn(e,a,c)}return rd(e,a,i,r,c)}function rm(e,a,i){var r=a.pendingProps,c=r.children,u=e!==null?e.memoizedState:null;if(r.mode==="hidden"){if((a.flags&128)!==0){if(r=u!==null?u.baseLanes|i:i,e!==null){for(c=a.child=e.child,u=0;c!==null;)u=u|c.lanes|c.childLanes,c=c.sibling;a.childLanes=u&~r}else a.childLanes=0,a.child=null;return lm(e,a,r,i)}if((i&536870912)!==0)a.memoizedState={baseLanes:0,cachePool:null},e!==null&&kl(a,u!==null?u.cachePool:null),u!==null?sh(a,u):qc(),Ph(a);else return a.lanes=a.childLanes=536870912,lm(e,a,u!==null?u.baseLanes|i:i,i)}else u!==null?(kl(a,u.cachePool),sh(a,u),fi(),a.memoizedState=null):(e!==null&&kl(a,null),qc(),fi());return va(e,a,c,i),a.child}function lm(e,a,i,r){var c=Dc();return c=c===null?null:{parent:ra._currentValue,pool:c},a.memoizedState={baseLanes:i,cachePool:c},e!==null&&kl(a,null),qc(),Ph(a),e!==null&&or(e,a,r,!0),null}function Pl(e,a){var i=a.ref;if(i===null)e!==null&&e.ref!==null&&(a.flags|=4194816);else{if(typeof i!="function"&&typeof i!="object")throw Error(o(284));(e===null||e.ref!==i)&&(a.flags|=4194816)}}function rd(e,a,i,r,c){return Hi(a),i=$c(e,a,i,r,void 0,c),r=Fc(),e!==null&&!fa?(Yc(e,a,c),Gn(e,a,c)):(Nt&&r&&Sc(a),a.flags|=1,va(e,a,i,c),a.child)}function om(e,a,i,r,c,u){return Hi(a),a.updateQueue=null,i=lh(a,r,i,c),rh(e),r=Fc(),e!==null&&!fa?(Yc(e,a,u),Gn(e,a,u)):(Nt&&r&&Sc(a),a.flags|=1,va(e,a,i,u),a.child)}function cm(e,a,i,r,c){if(Hi(a),a.stateNode===null){var u=fs,y=i.contextType;typeof y=="object"&&y!==null&&(u=Sa(y)),u=new i(r,u),a.memoizedState=u.state!==null&&u.state!==void 0?u.state:null,u.updater=id,a.stateNode=u,u._reactInternals=a,u=a.stateNode,u.props=r,u.state=a.memoizedState,u.refs={},Oc(a),y=i.contextType,u.context=typeof y=="object"&&y!==null?Sa(y):fs,u.state=a.memoizedState,y=i.getDerivedStateFromProps,typeof y=="function"&&(nd(a,i,y,r),u.state=a.memoizedState),typeof i.getDerivedStateFromProps=="function"||typeof u.getSnapshotBeforeUpdate=="function"||typeof u.UNSAFE_componentWillMount!="function"&&typeof u.componentWillMount!="function"||(y=u.state,typeof u.componentWillMount=="function"&&u.componentWillMount(),typeof u.UNSAFE_componentWillMount=="function"&&u.UNSAFE_componentWillMount(),y!==u.state&&id.enqueueReplaceState(u,u.state,null),pr(a,r,u,c),mr(),u.state=a.memoizedState),typeof u.componentDidMount=="function"&&(a.flags|=4194308),r=!0}else if(e===null){u=a.stateNode;var w=a.memoizedProps,k=Fi(i,w);u.props=k;var Y=u.context,le=i.contextType;y=fs,typeof le=="object"&&le!==null&&(y=Sa(le));var ye=i.getDerivedStateFromProps;le=typeof ye=="function"||typeof u.getSnapshotBeforeUpdate=="function",w=a.pendingProps!==w,le||typeof u.UNSAFE_componentWillReceiveProps!="function"&&typeof u.componentWillReceiveProps!="function"||(w||Y!==y)&&Zh(a,u,r,y),li=!1;var Z=a.memoizedState;u.state=Z,pr(a,r,u,c),mr(),Y=a.memoizedState,w||Z!==Y||li?(typeof ye=="function"&&(nd(a,i,ye,r),Y=a.memoizedState),(k=li||Xh(a,i,k,r,Z,Y,y))?(le||typeof u.UNSAFE_componentWillMount!="function"&&typeof u.componentWillMount!="function"||(typeof u.componentWillMount=="function"&&u.componentWillMount(),typeof u.UNSAFE_componentWillMount=="function"&&u.UNSAFE_componentWillMount()),typeof u.componentDidMount=="function"&&(a.flags|=4194308)):(typeof u.componentDidMount=="function"&&(a.flags|=4194308),a.memoizedProps=r,a.memoizedState=Y),u.props=r,u.state=Y,u.context=y,r=k):(typeof u.componentDidMount=="function"&&(a.flags|=4194308),r=!1)}else{u=a.stateNode,Uc(e,a),y=a.memoizedProps,le=Fi(i,y),u.props=le,ye=a.pendingProps,Z=u.context,Y=i.contextType,k=fs,typeof Y=="object"&&Y!==null&&(k=Sa(Y)),w=i.getDerivedStateFromProps,(Y=typeof w=="function"||typeof u.getSnapshotBeforeUpdate=="function")||typeof u.UNSAFE_componentWillReceiveProps!="function"&&typeof u.componentWillReceiveProps!="function"||(y!==ye||Z!==k)&&Zh(a,u,r,k),li=!1,Z=a.memoizedState,u.state=Z,pr(a,r,u,c),mr();var W=a.memoizedState;y!==ye||Z!==W||li||e!==null&&e.dependencies!==null&&Al(e.dependencies)?(typeof w=="function"&&(nd(a,i,w,r),W=a.memoizedState),(le=li||Xh(a,i,le,r,Z,W,k)||e!==null&&e.dependencies!==null&&Al(e.dependencies))?(Y||typeof u.UNSAFE_componentWillUpdate!="function"&&typeof u.componentWillUpdate!="function"||(typeof u.componentWillUpdate=="function"&&u.componentWillUpdate(r,W,k),typeof u.UNSAFE_componentWillUpdate=="function"&&u.UNSAFE_componentWillUpdate(r,W,k)),typeof u.componentDidUpdate=="function"&&(a.flags|=4),typeof u.getSnapshotBeforeUpdate=="function"&&(a.flags|=1024)):(typeof u.componentDidUpdate!="function"||y===e.memoizedProps&&Z===e.memoizedState||(a.flags|=4),typeof u.getSnapshotBeforeUpdate!="function"||y===e.memoizedProps&&Z===e.memoizedState||(a.flags|=1024),a.memoizedProps=r,a.memoizedState=W),u.props=r,u.state=W,u.context=k,r=le):(typeof u.componentDidUpdate!="function"||y===e.memoizedProps&&Z===e.memoizedState||(a.flags|=4),typeof u.getSnapshotBeforeUpdate!="function"||y===e.memoizedProps&&Z===e.memoizedState||(a.flags|=1024),r=!1)}return u=r,Pl(e,a),r=(a.flags&128)!==0,u||r?(u=a.stateNode,i=r&&typeof i.getDerivedStateFromError!="function"?null:u.render(),a.flags|=1,e!==null&&r?(a.child=ws(a,e.child,null,c),a.child=ws(a,null,i,c)):va(e,a,i,c),a.memoizedState=u.state,e=a.child):e=Gn(e,a,c),e}function dm(e,a,i,r){return rr(),a.flags|=256,va(e,a,i,r),a.child}var ld={dehydrated:null,treeContext:null,retryLane:0,hydrationErrors:null};function od(e){return{baseLanes:e,cachePool:Jf()}}function cd(e,a,i){return e=e!==null?e.childLanes&~i:0,a&&(e|=cn),e}function um(e,a,i){var r=a.pendingProps,c=!1,u=(a.flags&128)!==0,y;if((y=u)||(y=e!==null&&e.memoizedState===null?!1:(la.current&2)!==0),y&&(c=!0,a.flags&=-129),y=(a.flags&32)!==0,a.flags&=-33,e===null){if(Nt){if(c?ui(a):fi(),Nt){var w=Jt,k;if(k=w){e:{for(k=w,w=Nn;k.nodeType!==8;){if(!w){w=null;break e}if(k=xn(k.nextSibling),k===null){w=null;break e}}w=k}w!==null?(a.memoizedState={dehydrated:w,treeContext:Oi!==null?{id:qn,overflow:Hn}:null,retryLane:536870912,hydrationErrors:null},k=Xa(18,null,null,0),k.stateNode=w,k.return=a,a.child=k,za=a,Jt=null,k=!0):k=!1}k||Bi(a)}if(w=a.memoizedState,w!==null&&(w=w.dehydrated,w!==null))return Vd(w)?a.lanes=32:a.lanes=536870912,null;Yn(a)}return w=r.children,r=r.fallback,c?(fi(),c=a.mode,w=Xl({mode:"hidden",children:w},c),r=Ri(r,c,i,null),w.return=a,r.return=a,w.sibling=r,a.child=w,c=a.child,c.memoizedState=od(i),c.childLanes=cd(e,y,i),a.memoizedState=ld,r):(ui(a),dd(a,w))}if(k=e.memoizedState,k!==null&&(w=k.dehydrated,w!==null)){if(u)a.flags&256?(ui(a),a.flags&=-257,a=ud(e,a,i)):a.memoizedState!==null?(fi(),a.child=e.child,a.flags|=128,a=null):(fi(),c=r.fallback,w=a.mode,r=Xl({mode:"visible",children:r.children},w),c=Ri(c,w,i,null),c.flags|=2,r.return=a,c.return=a,r.sibling=c,a.child=r,ws(a,e.child,null,i),r=a.child,r.memoizedState=od(i),r.childLanes=cd(e,y,i),a.memoizedState=ld,a=c);else if(ui(a),Vd(w)){if(y=w.nextSibling&&w.nextSibling.dataset,y)var Y=y.dgst;y=Y,r=Error(o(419)),r.stack="",r.digest=y,lr({value:r,source:null,stack:null}),a=ud(e,a,i)}else if(fa||or(e,a,i,!1),y=(i&e.childLanes)!==0,fa||y){if(y=$t,y!==null&&(r=i&-i,r=(r&42)!==0?1:wt(r),r=(r&(y.suspendedLanes|i))!==0?0:r,r!==0&&r!==k.retryLane))throw k.retryLane=r,us(e,r),Ka(y,e,r),am;w.data==="$?"||zd(),a=ud(e,a,i)}else w.data==="$?"?(a.flags|=192,a.child=e.child,a=null):(e=k.treeContext,Jt=xn(w.nextSibling),za=a,Nt=!0,Li=null,Nn=!1,e!==null&&(rn[ln++]=qn,rn[ln++]=Hn,rn[ln++]=Oi,qn=e.id,Hn=e.overflow,Oi=a),a=dd(a,r.children),a.flags|=4096);return a}return c?(fi(),c=r.fallback,w=a.mode,k=e.child,Y=k.sibling,r=Bn(k,{mode:"hidden",children:r.children}),r.subtreeFlags=k.subtreeFlags&65011712,Y!==null?c=Bn(Y,c):(c=Ri(c,w,i,null),c.flags|=2),c.return=a,r.return=a,r.sibling=c,a.child=r,r=c,c=a.child,w=e.child.memoizedState,w===null?w=od(i):(k=w.cachePool,k!==null?(Y=ra._currentValue,k=k.parent!==Y?{parent:Y,pool:Y}:k):k=Jf(),w={baseLanes:w.baseLanes|i,cachePool:k}),c.memoizedState=w,c.childLanes=cd(e,y,i),a.memoizedState=ld,r):(ui(a),i=e.child,e=i.sibling,i=Bn(i,{mode:"visible",children:r.children}),i.return=a,i.sibling=null,e!==null&&(y=a.deletions,y===null?(a.deletions=[e],a.flags|=16):y.push(e)),a.child=i,a.memoizedState=null,i)}function dd(e,a){return a=Xl({mode:"visible",children:a},e.mode),a.return=e,e.child=a}function Xl(e,a){return e=Xa(22,e,null,a),e.lanes=0,e.stateNode={_visibility:1,_pendingMarkers:null,_retryCache:null,_transitions:null},e}function ud(e,a,i){return ws(a,e.child,null,i),e=dd(a,a.pendingProps.children),e.flags|=2,a.memoizedState=null,e}function fm(e,a,i){e.lanes|=a;var r=e.alternate;r!==null&&(r.lanes|=a),zc(e.return,a,i)}function fd(e,a,i,r,c){var u=e.memoizedState;u===null?e.memoizedState={isBackwards:a,rendering:null,renderingStartTime:0,last:r,tail:i,tailMode:c}:(u.isBackwards=a,u.rendering=null,u.renderingStartTime=0,u.last=r,u.tail=i,u.tailMode=c)}function hm(e,a,i){var r=a.pendingProps,c=r.revealOrder,u=r.tail;if(va(e,a,r.children,i),r=la.current,(r&2)!==0)r=r&1|2,a.flags|=128;else{if(e!==null&&(e.flags&128)!==0)e:for(e=a.child;e!==null;){if(e.tag===13)e.memoizedState!==null&&fm(e,i,a);else if(e.tag===19)fm(e,i,a);else if(e.child!==null){e.child.return=e,e=e.child;continue}if(e===a)break e;for(;e.sibling===null;){if(e.return===null||e.return===a)break e;e=e.return}e.sibling.return=e.return,e=e.sibling}r&=1}switch(oe(la,r),c){case"forwards":for(i=a.child,c=null;i!==null;)e=i.alternate,e!==null&&Yl(e)===null&&(c=i),i=i.sibling;i=c,i===null?(c=a.child,a.child=null):(c=i.sibling,i.sibling=null),fd(a,!1,c,i,u);break;case"backwards":for(i=null,c=a.child,a.child=null;c!==null;){if(e=c.alternate,e!==null&&Yl(e)===null){a.child=c;break}e=c.sibling,c.sibling=i,i=c,c=e}fd(a,!0,i,null,u);break;case"together":fd(a,!1,null,null,void 0);break;default:a.memoizedState=null}return a.child}function Gn(e,a,i){if(e!==null&&(a.dependencies=e.dependencies),xi|=a.lanes,(i&a.childLanes)===0)if(e!==null){if(or(e,a,i,!1),(i&a.childLanes)===0)return null}else return null;if(e!==null&&a.child!==e.child)throw Error(o(153));if(a.child!==null){for(e=a.child,i=Bn(e,e.pendingProps),a.child=i,i.return=a;e.sibling!==null;)e=e.sibling,i=i.sibling=Bn(e,e.pendingProps),i.return=a;i.sibling=null}return a.child}function hd(e,a){return(e.lanes&a)!==0?!0:(e=e.dependencies,!!(e!==null&&Al(e)))}function oy(e,a,i){switch(a.tag){case 3:Le(a,a.stateNode.containerInfo),ri(a,ra,e.memoizedState.cache),rr();break;case 27:case 5:D(a);break;case 4:Le(a,a.stateNode.containerInfo);break;case 10:ri(a,a.type,a.memoizedProps.value);break;case 13:var r=a.memoizedState;if(r!==null)return r.dehydrated!==null?(ui(a),a.flags|=128,null):(i&a.child.childLanes)!==0?um(e,a,i):(ui(a),e=Gn(e,a,i),e!==null?e.sibling:null);ui(a);break;case 19:var c=(e.flags&128)!==0;if(r=(i&a.childLanes)!==0,r||(or(e,a,i,!1),r=(i&a.childLanes)!==0),c){if(r)return hm(e,a,i);a.flags|=128}if(c=a.memoizedState,c!==null&&(c.rendering=null,c.tail=null,c.lastEffect=null),oe(la,la.current),r)break;return null;case 22:case 23:return a.lanes=0,rm(e,a,i);case 24:ri(a,ra,e.memoizedState.cache)}return Gn(e,a,i)}function mm(e,a,i){if(e!==null)if(e.memoizedProps!==a.pendingProps)fa=!0;else{if(!hd(e,i)&&(a.flags&128)===0)return fa=!1,oy(e,a,i);fa=(e.flags&131072)!==0}else fa=!1,Nt&&(a.flags&1048576)!==0&&Yf(a,Cl,a.index);switch(a.lanes=0,a.tag){case 16:e:{e=a.pendingProps;var r=a.elementType,c=r._init;if(r=c(r._payload),a.type=r,typeof r=="function")wc(r)?(e=Fi(r,e),a.tag=1,a=cm(null,a,r,e,i)):(a.tag=0,a=rd(null,a,r,e,i));else{if(r!=null){if(c=r.$$typeof,c===M){a.tag=11,a=nm(null,a,r,e,i);break e}else if(c===K){a.tag=14,a=im(null,a,r,e,i);break e}}throw a=xe(r)||r,Error(o(306,a,""))}}return a;case 0:return rd(e,a,a.type,a.pendingProps,i);case 1:return r=a.type,c=Fi(r,a.pendingProps),cm(e,a,r,c,i);case 3:e:{if(Le(a,a.stateNode.containerInfo),e===null)throw Error(o(387));r=a.pendingProps;var u=a.memoizedState;c=u.element,Uc(e,a),pr(a,r,null,i);var y=a.memoizedState;if(r=y.cache,ri(a,ra,r),r!==u.cache&&kc(a,[ra],i,!0),mr(),r=y.element,u.isDehydrated)if(u={element:r,isDehydrated:!1,cache:y.cache},a.updateQueue.baseState=u,a.memoizedState=u,a.flags&256){a=dm(e,a,r,i);break e}else if(r!==c){c=nn(Error(o(424)),a),lr(c),a=dm(e,a,r,i);break e}else{switch(e=a.stateNode.containerInfo,e.nodeType){case 9:e=e.body;break;default:e=e.nodeName==="HTML"?e.ownerDocument.body:e}for(Jt=xn(e.firstChild),za=a,Nt=!0,Li=null,Nn=!0,i=Vh(a,null,r,i),a.child=i;i;)i.flags=i.flags&-3|4096,i=i.sibling}else{if(rr(),r===c){a=Gn(e,a,i);break e}va(e,a,r,i)}a=a.child}return a;case 26:return Pl(e,a),e===null?(i=yp(a.type,null,a.pendingProps,null))?a.memoizedState=i:Nt||(i=a.type,e=a.pendingProps,r=oo(ue.current).createElement(i),r[Oe]=a,r[lt]=e,ja(r,i,e),gt(r),a.stateNode=r):a.memoizedState=yp(a.type,e.memoizedProps,a.pendingProps,e.memoizedState),null;case 27:return D(a),e===null&&Nt&&(r=a.stateNode=pp(a.type,a.pendingProps,ue.current),za=a,Nn=!0,c=Jt,ji(a.type)?(Pd=c,Jt=xn(r.firstChild)):Jt=c),va(e,a,a.pendingProps.children,i),Pl(e,a),e===null&&(a.flags|=4194304),a.child;case 5:return e===null&&Nt&&((c=r=Jt)&&(r=Uy(r,a.type,a.pendingProps,Nn),r!==null?(a.stateNode=r,za=a,Jt=xn(r.firstChild),Nn=!1,c=!0):c=!1),c||Bi(a)),D(a),c=a.type,u=a.pendingProps,y=e!==null?e.memoizedProps:null,r=u.children,Fd(c,u)?r=null:y!==null&&Fd(c,y)&&(a.flags|=32),a.memoizedState!==null&&(c=$c(e,a,ey,null,null,i),Lr._currentValue=c),Pl(e,a),va(e,a,r,i),a.child;case 6:return e===null&&Nt&&((e=i=Jt)&&(i=Ly(i,a.pendingProps,Nn),i!==null?(a.stateNode=i,za=a,Jt=null,e=!0):e=!1),e||Bi(a)),null;case 13:return um(e,a,i);case 4:return Le(a,a.stateNode.containerInfo),r=a.pendingProps,e===null?a.child=ws(a,null,r,i):va(e,a,r,i),a.child;case 11:return nm(e,a,a.type,a.pendingProps,i);case 7:return va(e,a,a.pendingProps,i),a.child;case 8:return va(e,a,a.pendingProps.children,i),a.child;case 12:return va(e,a,a.pendingProps.children,i),a.child;case 10:return r=a.pendingProps,ri(a,a.type,r.value),va(e,a,r.children,i),a.child;case 9:return c=a.type._context,r=a.pendingProps.children,Hi(a),c=Sa(c),r=r(c),a.flags|=1,va(e,a,r,i),a.child;case 14:return im(e,a,a.type,a.pendingProps,i);case 15:return sm(e,a,a.type,a.pendingProps,i);case 19:return hm(e,a,i);case 31:return r=a.pendingProps,i=a.mode,r={mode:r.mode,children:r.children},e===null?(i=Xl(r,i),i.ref=a.ref,a.child=i,i.return=a,a=i):(i=Bn(e.child,r),i.ref=a.ref,a.child=i,i.return=a,a=i),a;case 22:return rm(e,a,i);case 24:return Hi(a),r=Sa(ra),e===null?(c=Dc(),c===null&&(c=$t,u=Ec(),c.pooledCache=u,u.refCount++,u!==null&&(c.pooledCacheLanes|=i),c=u),a.memoizedState={parent:r,cache:c},Oc(a),ri(a,ra,c)):((e.lanes&i)!==0&&(Uc(e,a),pr(a,null,null,i),mr()),c=e.memoizedState,u=a.memoizedState,c.parent!==r?(c={parent:r,cache:r},a.memoizedState=c,a.lanes===0&&(a.memoizedState=a.updateQueue.baseState=c),ri(a,ra,r)):(r=u.cache,ri(a,ra,r),r!==c.cache&&kc(a,[ra],i,!0))),va(e,a,a.pendingProps.children,i),a.child;case 29:throw a.pendingProps}throw Error(o(156,a.tag))}function Vn(e){e.flags|=4}function pm(e,a){if(a.type!=="stylesheet"||(a.state.loading&4)!==0)e.flags&=-16777217;else if(e.flags|=16777216,!Np(a)){if(a=on.current,a!==null&&((pt&4194048)===pt?_n!==null:(pt&62914560)!==pt&&(pt&536870912)===0||a!==_n))throw fr=Rc,Wf;e.flags|=8192}}function Zl(e,a){a!==null&&(e.flags|=4),e.flags&16384&&(a=e.tag!==22?St():536870912,e.lanes|=a,Ts|=a)}function wr(e,a){if(!Nt)switch(e.tailMode){case"hidden":a=e.tail;for(var i=null;a!==null;)a.alternate!==null&&(i=a),a=a.sibling;i===null?e.tail=null:i.sibling=null;break;case"collapsed":i=e.tail;for(var r=null;i!==null;)i.alternate!==null&&(r=i),i=i.sibling;r===null?a||e.tail===null?e.tail=null:e.tail.sibling=null:r.sibling=null}}function Xt(e){var a=e.alternate!==null&&e.alternate.child===e.child,i=0,r=0;if(a)for(var c=e.child;c!==null;)i|=c.lanes|c.childLanes,r|=c.subtreeFlags&65011712,r|=c.flags&65011712,c.return=e,c=c.sibling;else for(c=e.child;c!==null;)i|=c.lanes|c.childLanes,r|=c.subtreeFlags,r|=c.flags,c.return=e,c=c.sibling;return e.subtreeFlags|=r,e.childLanes=i,a}function cy(e,a,i){var r=a.pendingProps;switch(Tc(a),a.tag){case 31:case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return Xt(a),null;case 1:return Xt(a),null;case 3:return i=a.stateNode,r=null,e!==null&&(r=e.memoizedState.cache),a.memoizedState.cache!==r&&(a.flags|=2048),$n(ra),ne(),i.pendingContext&&(i.context=i.pendingContext,i.pendingContext=null),(e===null||e.child===null)&&(sr(a)?Vn(a):e===null||e.memoizedState.isDehydrated&&(a.flags&256)===0||(a.flags|=1024,Pf())),Xt(a),null;case 26:return i=a.memoizedState,e===null?(Vn(a),i!==null?(Xt(a),pm(a,i)):(Xt(a),a.flags&=-16777217)):i?i!==e.memoizedState?(Vn(a),Xt(a),pm(a,i)):(Xt(a),a.flags&=-16777217):(e.memoizedProps!==r&&Vn(a),Xt(a),a.flags&=-16777217),null;case 27:I(a),i=ue.current;var c=a.type;if(e!==null&&a.stateNode!=null)e.memoizedProps!==r&&Vn(a);else{if(!r){if(a.stateNode===null)throw Error(o(166));return Xt(a),null}e=re.current,sr(a)?Gf(a):(e=pp(c,r,i),a.stateNode=e,Vn(a))}return Xt(a),null;case 5:if(I(a),i=a.type,e!==null&&a.stateNode!=null)e.memoizedProps!==r&&Vn(a);else{if(!r){if(a.stateNode===null)throw Error(o(166));return Xt(a),null}if(e=re.current,sr(a))Gf(a);else{switch(c=oo(ue.current),e){case 1:e=c.createElementNS("http://www.w3.org/2000/svg",i);break;case 2:e=c.createElementNS("http://www.w3.org/1998/Math/MathML",i);break;default:switch(i){case"svg":e=c.createElementNS("http://www.w3.org/2000/svg",i);break;case"math":e=c.createElementNS("http://www.w3.org/1998/Math/MathML",i);break;case"script":e=c.createElement("div"),e.innerHTML="<script><\/script>",e=e.removeChild(e.firstChild);break;case"select":e=typeof r.is=="string"?c.createElement("select",{is:r.is}):c.createElement("select"),r.multiple?e.multiple=!0:r.size&&(e.size=r.size);break;default:e=typeof r.is=="string"?c.createElement(i,{is:r.is}):c.createElement(i)}}e[Oe]=a,e[lt]=r;e:for(c=a.child;c!==null;){if(c.tag===5||c.tag===6)e.appendChild(c.stateNode);else if(c.tag!==4&&c.tag!==27&&c.child!==null){c.child.return=c,c=c.child;continue}if(c===a)break e;for(;c.sibling===null;){if(c.return===null||c.return===a)break e;c=c.return}c.sibling.return=c.return,c=c.sibling}a.stateNode=e;e:switch(ja(e,i,r),i){case"button":case"input":case"select":case"textarea":e=!!r.autoFocus;break e;case"img":e=!0;break e;default:e=!1}e&&Vn(a)}}return Xt(a),a.flags&=-16777217,null;case 6:if(e&&a.stateNode!=null)e.memoizedProps!==r&&Vn(a);else{if(typeof r!="string"&&a.stateNode===null)throw Error(o(166));if(e=ue.current,sr(a)){if(e=a.stateNode,i=a.memoizedProps,r=null,c=za,c!==null)switch(c.tag){case 27:case 5:r=c.memoizedProps}e[Oe]=a,e=!!(e.nodeValue===i||r!==null&&r.suppressHydrationWarning===!0||op(e.nodeValue,i)),e||Bi(a)}else e=oo(e).createTextNode(r),e[Oe]=a,a.stateNode=e}return Xt(a),null;case 13:if(r=a.memoizedState,e===null||e.memoizedState!==null&&e.memoizedState.dehydrated!==null){if(c=sr(a),r!==null&&r.dehydrated!==null){if(e===null){if(!c)throw Error(o(318));if(c=a.memoizedState,c=c!==null?c.dehydrated:null,!c)throw Error(o(317));c[Oe]=a}else rr(),(a.flags&128)===0&&(a.memoizedState=null),a.flags|=4;Xt(a),c=!1}else c=Pf(),e!==null&&e.memoizedState!==null&&(e.memoizedState.hydrationErrors=c),c=!0;if(!c)return a.flags&256?(Yn(a),a):(Yn(a),null)}if(Yn(a),(a.flags&128)!==0)return a.lanes=i,a;if(i=r!==null,e=e!==null&&e.memoizedState!==null,i){r=a.child,c=null,r.alternate!==null&&r.alternate.memoizedState!==null&&r.alternate.memoizedState.cachePool!==null&&(c=r.alternate.memoizedState.cachePool.pool);var u=null;r.memoizedState!==null&&r.memoizedState.cachePool!==null&&(u=r.memoizedState.cachePool.pool),u!==c&&(r.flags|=2048)}return i!==e&&i&&(a.child.flags|=8192),Zl(a,a.updateQueue),Xt(a),null;case 4:return ne(),e===null&&Bd(a.stateNode.containerInfo),Xt(a),null;case 10:return $n(a.type),Xt(a),null;case 19:if(ie(la),c=a.memoizedState,c===null)return Xt(a),null;if(r=(a.flags&128)!==0,u=c.rendering,u===null)if(r)wr(c,!1);else{if(Wt!==0||e!==null&&(e.flags&128)!==0)for(e=a.child;e!==null;){if(u=Yl(e),u!==null){for(a.flags|=128,wr(c,!1),e=u.updateQueue,a.updateQueue=e,Zl(a,e),a.subtreeFlags=0,e=i,i=a.child;i!==null;)Ff(i,e),i=i.sibling;return oe(la,la.current&1|2),a.child}e=e.sibling}c.tail!==null&&Ke()>Wl&&(a.flags|=128,r=!0,wr(c,!1),a.lanes=4194304)}else{if(!r)if(e=Yl(u),e!==null){if(a.flags|=128,r=!0,e=e.updateQueue,a.updateQueue=e,Zl(a,e),wr(c,!0),c.tail===null&&c.tailMode==="hidden"&&!u.alternate&&!Nt)return Xt(a),null}else 2*Ke()-c.renderingStartTime>Wl&&i!==536870912&&(a.flags|=128,r=!0,wr(c,!1),a.lanes=4194304);c.isBackwards?(u.sibling=a.child,a.child=u):(e=c.last,e!==null?e.sibling=u:a.child=u,c.last=u)}return c.tail!==null?(a=c.tail,c.rendering=a,c.tail=a.sibling,c.renderingStartTime=Ke(),a.sibling=null,e=la.current,oe(la,r?e&1|2:e&1),a):(Xt(a),null);case 22:case 23:return Yn(a),Hc(),r=a.memoizedState!==null,e!==null?e.memoizedState!==null!==r&&(a.flags|=8192):r&&(a.flags|=8192),r?(i&536870912)!==0&&(a.flags&128)===0&&(Xt(a),a.subtreeFlags&6&&(a.flags|=8192)):Xt(a),i=a.updateQueue,i!==null&&Zl(a,i.retryQueue),i=null,e!==null&&e.memoizedState!==null&&e.memoizedState.cachePool!==null&&(i=e.memoizedState.cachePool.pool),r=null,a.memoizedState!==null&&a.memoizedState.cachePool!==null&&(r=a.memoizedState.cachePool.pool),r!==i&&(a.flags|=2048),e!==null&&ie(Ii),null;case 24:return i=null,e!==null&&(i=e.memoizedState.cache),a.memoizedState.cache!==i&&(a.flags|=2048),$n(ra),Xt(a),null;case 25:return null;case 30:return null}throw Error(o(156,a.tag))}function dy(e,a){switch(Tc(a),a.tag){case 1:return e=a.flags,e&65536?(a.flags=e&-65537|128,a):null;case 3:return $n(ra),ne(),e=a.flags,(e&65536)!==0&&(e&128)===0?(a.flags=e&-65537|128,a):null;case 26:case 27:case 5:return I(a),null;case 13:if(Yn(a),e=a.memoizedState,e!==null&&e.dehydrated!==null){if(a.alternate===null)throw Error(o(340));rr()}return e=a.flags,e&65536?(a.flags=e&-65537|128,a):null;case 19:return ie(la),null;case 4:return ne(),null;case 10:return $n(a.type),null;case 22:case 23:return Yn(a),Hc(),e!==null&&ie(Ii),e=a.flags,e&65536?(a.flags=e&-65537|128,a):null;case 24:return $n(ra),null;case 25:return null;default:return null}}function gm(e,a){switch(Tc(a),a.tag){case 3:$n(ra),ne();break;case 26:case 27:case 5:I(a);break;case 4:ne();break;case 13:Yn(a);break;case 19:ie(la);break;case 10:$n(a.type);break;case 22:case 23:Yn(a),Hc(),e!==null&&ie(Ii);break;case 24:$n(ra)}}function Nr(e,a){try{var i=a.updateQueue,r=i!==null?i.lastEffect:null;if(r!==null){var c=r.next;i=c;do{if((i.tag&e)===e){r=void 0;var u=i.create,y=i.inst;r=u(),y.destroy=r}i=i.next}while(i!==c)}}catch(w){Lt(a,a.return,w)}}function hi(e,a,i){try{var r=a.updateQueue,c=r!==null?r.lastEffect:null;if(c!==null){var u=c.next;r=u;do{if((r.tag&e)===e){var y=r.inst,w=y.destroy;if(w!==void 0){y.destroy=void 0,c=a;var k=i,Y=w;try{Y()}catch(le){Lt(c,k,le)}}}r=r.next}while(r!==u)}}catch(le){Lt(a,a.return,le)}}function xm(e){var a=e.updateQueue;if(a!==null){var i=e.stateNode;try{ih(a,i)}catch(r){Lt(e,e.return,r)}}}function ym(e,a,i){i.props=Fi(e.type,e.memoizedProps),i.state=e.memoizedState;try{i.componentWillUnmount()}catch(r){Lt(e,a,r)}}function _r(e,a){try{var i=e.ref;if(i!==null){switch(e.tag){case 26:case 27:case 5:var r=e.stateNode;break;case 30:r=e.stateNode;break;default:r=e.stateNode}typeof i=="function"?e.refCleanup=i(r):i.current=r}}catch(c){Lt(e,a,c)}}function Sn(e,a){var i=e.ref,r=e.refCleanup;if(i!==null)if(typeof r=="function")try{r()}catch(c){Lt(e,a,c)}finally{e.refCleanup=null,e=e.alternate,e!=null&&(e.refCleanup=null)}else if(typeof i=="function")try{i(null)}catch(c){Lt(e,a,c)}else i.current=null}function vm(e){var a=e.type,i=e.memoizedProps,r=e.stateNode;try{e:switch(a){case"button":case"input":case"select":case"textarea":i.autoFocus&&r.focus();break e;case"img":i.src?r.src=i.src:i.srcSet&&(r.srcset=i.srcSet)}}catch(c){Lt(e,e.return,c)}}function md(e,a,i){try{var r=e.stateNode;Ey(r,e.type,i,a),r[lt]=a}catch(c){Lt(e,e.return,c)}}function bm(e){return e.tag===5||e.tag===3||e.tag===26||e.tag===27&&ji(e.type)||e.tag===4}function pd(e){e:for(;;){for(;e.sibling===null;){if(e.return===null||bm(e.return))return null;e=e.return}for(e.sibling.return=e.return,e=e.sibling;e.tag!==5&&e.tag!==6&&e.tag!==18;){if(e.tag===27&&ji(e.type)||e.flags&2||e.child===null||e.tag===4)continue e;e.child.return=e,e=e.child}if(!(e.flags&2))return e.stateNode}}function gd(e,a,i){var r=e.tag;if(r===5||r===6)e=e.stateNode,a?(i.nodeType===9?i.body:i.nodeName==="HTML"?i.ownerDocument.body:i).insertBefore(e,a):(a=i.nodeType===9?i.body:i.nodeName==="HTML"?i.ownerDocument.body:i,a.appendChild(e),i=i._reactRootContainer,i!=null||a.onclick!==null||(a.onclick=lo));else if(r!==4&&(r===27&&ji(e.type)&&(i=e.stateNode,a=null),e=e.child,e!==null))for(gd(e,a,i),e=e.sibling;e!==null;)gd(e,a,i),e=e.sibling}function Ql(e,a,i){var r=e.tag;if(r===5||r===6)e=e.stateNode,a?i.insertBefore(e,a):i.appendChild(e);else if(r!==4&&(r===27&&ji(e.type)&&(i=e.stateNode),e=e.child,e!==null))for(Ql(e,a,i),e=e.sibling;e!==null;)Ql(e,a,i),e=e.sibling}function jm(e){var a=e.stateNode,i=e.memoizedProps;try{for(var r=e.type,c=a.attributes;c.length;)a.removeAttributeNode(c[0]);ja(a,r,i),a[Oe]=e,a[lt]=i}catch(u){Lt(e,e.return,u)}}var Pn=!1,ea=!1,xd=!1,wm=typeof WeakSet=="function"?WeakSet:Set,ha=null;function uy(e,a){if(e=e.containerInfo,Id=po,e=Df(e),pc(e)){if("selectionStart"in e)var i={start:e.selectionStart,end:e.selectionEnd};else e:{i=(i=e.ownerDocument)&&i.defaultView||window;var r=i.getSelection&&i.getSelection();if(r&&r.rangeCount!==0){i=r.anchorNode;var c=r.anchorOffset,u=r.focusNode;r=r.focusOffset;try{i.nodeType,u.nodeType}catch{i=null;break e}var y=0,w=-1,k=-1,Y=0,le=0,ye=e,Z=null;t:for(;;){for(var W;ye!==i||c!==0&&ye.nodeType!==3||(w=y+c),ye!==u||r!==0&&ye.nodeType!==3||(k=y+r),ye.nodeType===3&&(y+=ye.nodeValue.length),(W=ye.firstChild)!==null;)Z=ye,ye=W;for(;;){if(ye===e)break t;if(Z===i&&++Y===c&&(w=y),Z===u&&++le===r&&(k=y),(W=ye.nextSibling)!==null)break;ye=Z,Z=ye.parentNode}ye=W}i=w===-1||k===-1?null:{start:w,end:k}}else i=null}i=i||{start:0,end:0}}else i=null;for($d={focusedElem:e,selectionRange:i},po=!1,ha=a;ha!==null;)if(a=ha,e=a.child,(a.subtreeFlags&1024)!==0&&e!==null)e.return=a,ha=e;else for(;ha!==null;){switch(a=ha,u=a.alternate,e=a.flags,a.tag){case 0:break;case 11:case 15:break;case 1:if((e&1024)!==0&&u!==null){e=void 0,i=a,c=u.memoizedProps,u=u.memoizedState,r=i.stateNode;try{var We=Fi(i.type,c,i.elementType===i.type);e=r.getSnapshotBeforeUpdate(We,u),r.__reactInternalSnapshotBeforeUpdate=e}catch(Pe){Lt(i,i.return,Pe)}}break;case 3:if((e&1024)!==0){if(e=a.stateNode.containerInfo,i=e.nodeType,i===9)Gd(e);else if(i===1)switch(e.nodeName){case"HEAD":case"HTML":case"BODY":Gd(e);break;default:e.textContent=""}}break;case 5:case 26:case 27:case 6:case 4:case 17:break;default:if((e&1024)!==0)throw Error(o(163))}if(e=a.sibling,e!==null){e.return=a.return,ha=e;break}ha=a.return}}function Nm(e,a,i){var r=i.flags;switch(i.tag){case 0:case 11:case 15:mi(e,i),r&4&&Nr(5,i);break;case 1:if(mi(e,i),r&4)if(e=i.stateNode,a===null)try{e.componentDidMount()}catch(y){Lt(i,i.return,y)}else{var c=Fi(i.type,a.memoizedProps);a=a.memoizedState;try{e.componentDidUpdate(c,a,e.__reactInternalSnapshotBeforeUpdate)}catch(y){Lt(i,i.return,y)}}r&64&&xm(i),r&512&&_r(i,i.return);break;case 3:if(mi(e,i),r&64&&(e=i.updateQueue,e!==null)){if(a=null,i.child!==null)switch(i.child.tag){case 27:case 5:a=i.child.stateNode;break;case 1:a=i.child.stateNode}try{ih(e,a)}catch(y){Lt(i,i.return,y)}}break;case 27:a===null&&r&4&&jm(i);case 26:case 5:mi(e,i),a===null&&r&4&&vm(i),r&512&&_r(i,i.return);break;case 12:mi(e,i);break;case 13:mi(e,i),r&4&&Tm(e,i),r&64&&(e=i.memoizedState,e!==null&&(e=e.dehydrated,e!==null&&(i=by.bind(null,i),By(e,i))));break;case 22:if(r=i.memoizedState!==null||Pn,!r){a=a!==null&&a.memoizedState!==null||ea,c=Pn;var u=ea;Pn=r,(ea=a)&&!u?pi(e,i,(i.subtreeFlags&8772)!==0):mi(e,i),Pn=c,ea=u}break;case 30:break;default:mi(e,i)}}function _m(e){var a=e.alternate;a!==null&&(e.alternate=null,_m(a)),e.child=null,e.deletions=null,e.sibling=null,e.tag===5&&(a=e.stateNode,a!==null&&$a(a)),e.stateNode=null,e.return=null,e.dependencies=null,e.memoizedProps=null,e.memoizedState=null,e.pendingProps=null,e.stateNode=null,e.updateQueue=null}var Vt=null,La=!1;function Xn(e,a,i){for(i=i.child;i!==null;)Sm(e,a,i),i=i.sibling}function Sm(e,a,i){if(Be&&typeof Be.onCommitFiberUnmount=="function")try{Be.onCommitFiberUnmount(ke,i)}catch{}switch(i.tag){case 26:ea||Sn(i,a),Xn(e,a,i),i.memoizedState?i.memoizedState.count--:i.stateNode&&(i=i.stateNode,i.parentNode.removeChild(i));break;case 27:ea||Sn(i,a);var r=Vt,c=La;ji(i.type)&&(Vt=i.stateNode,La=!1),Xn(e,a,i),Dr(i.stateNode),Vt=r,La=c;break;case 5:ea||Sn(i,a);case 6:if(r=Vt,c=La,Vt=null,Xn(e,a,i),Vt=r,La=c,Vt!==null)if(La)try{(Vt.nodeType===9?Vt.body:Vt.nodeName==="HTML"?Vt.ownerDocument.body:Vt).removeChild(i.stateNode)}catch(u){Lt(i,a,u)}else try{Vt.removeChild(i.stateNode)}catch(u){Lt(i,a,u)}break;case 18:Vt!==null&&(La?(e=Vt,hp(e.nodeType===9?e.body:e.nodeName==="HTML"?e.ownerDocument.body:e,i.stateNode),Ir(e)):hp(Vt,i.stateNode));break;case 4:r=Vt,c=La,Vt=i.stateNode.containerInfo,La=!0,Xn(e,a,i),Vt=r,La=c;break;case 0:case 11:case 14:case 15:ea||hi(2,i,a),ea||hi(4,i,a),Xn(e,a,i);break;case 1:ea||(Sn(i,a),r=i.stateNode,typeof r.componentWillUnmount=="function"&&ym(i,a,r)),Xn(e,a,i);break;case 21:Xn(e,a,i);break;case 22:ea=(r=ea)||i.memoizedState!==null,Xn(e,a,i),ea=r;break;default:Xn(e,a,i)}}function Tm(e,a){if(a.memoizedState===null&&(e=a.alternate,e!==null&&(e=e.memoizedState,e!==null&&(e=e.dehydrated,e!==null))))try{Ir(e)}catch(i){Lt(a,a.return,i)}}function fy(e){switch(e.tag){case 13:case 19:var a=e.stateNode;return a===null&&(a=e.stateNode=new wm),a;case 22:return e=e.stateNode,a=e._retryCache,a===null&&(a=e._retryCache=new wm),a;default:throw Error(o(435,e.tag))}}function yd(e,a){var i=fy(e);a.forEach(function(r){var c=jy.bind(null,e,r);i.has(r)||(i.add(r),r.then(c,c))})}function Za(e,a){var i=a.deletions;if(i!==null)for(var r=0;r<i.length;r++){var c=i[r],u=e,y=a,w=y;e:for(;w!==null;){switch(w.tag){case 27:if(ji(w.type)){Vt=w.stateNode,La=!1;break e}break;case 5:Vt=w.stateNode,La=!1;break e;case 3:case 4:Vt=w.stateNode.containerInfo,La=!0;break e}w=w.return}if(Vt===null)throw Error(o(160));Sm(u,y,c),Vt=null,La=!1,u=c.alternate,u!==null&&(u.return=null),c.return=null}if(a.subtreeFlags&13878)for(a=a.child;a!==null;)Cm(a,e),a=a.sibling}var gn=null;function Cm(e,a){var i=e.alternate,r=e.flags;switch(e.tag){case 0:case 11:case 14:case 15:Za(a,e),Qa(e),r&4&&(hi(3,e,e.return),Nr(3,e),hi(5,e,e.return));break;case 1:Za(a,e),Qa(e),r&512&&(ea||i===null||Sn(i,i.return)),r&64&&Pn&&(e=e.updateQueue,e!==null&&(r=e.callbacks,r!==null&&(i=e.shared.hiddenCallbacks,e.shared.hiddenCallbacks=i===null?r:i.concat(r))));break;case 26:var c=gn;if(Za(a,e),Qa(e),r&512&&(ea||i===null||Sn(i,i.return)),r&4){var u=i!==null?i.memoizedState:null;if(r=e.memoizedState,i===null)if(r===null)if(e.stateNode===null){e:{r=e.type,i=e.memoizedProps,c=c.ownerDocument||c;t:switch(r){case"title":u=c.getElementsByTagName("title")[0],(!u||u[fn]||u[Oe]||u.namespaceURI==="http://www.w3.org/2000/svg"||u.hasAttribute("itemprop"))&&(u=c.createElement(r),c.head.insertBefore(u,c.querySelector("head > title"))),ja(u,r,i),u[Oe]=e,gt(u),r=u;break e;case"link":var y=jp("link","href",c).get(r+(i.href||""));if(y){for(var w=0;w<y.length;w++)if(u=y[w],u.getAttribute("href")===(i.href==null||i.href===""?null:i.href)&&u.getAttribute("rel")===(i.rel==null?null:i.rel)&&u.getAttribute("title")===(i.title==null?null:i.title)&&u.getAttribute("crossorigin")===(i.crossOrigin==null?null:i.crossOrigin)){y.splice(w,1);break t}}u=c.createElement(r),ja(u,r,i),c.head.appendChild(u);break;case"meta":if(y=jp("meta","content",c).get(r+(i.content||""))){for(w=0;w<y.length;w++)if(u=y[w],u.getAttribute("content")===(i.content==null?null:""+i.content)&&u.getAttribute("name")===(i.name==null?null:i.name)&&u.getAttribute("property")===(i.property==null?null:i.property)&&u.getAttribute("http-equiv")===(i.httpEquiv==null?null:i.httpEquiv)&&u.getAttribute("charset")===(i.charSet==null?null:i.charSet)){y.splice(w,1);break t}}u=c.createElement(r),ja(u,r,i),c.head.appendChild(u);break;default:throw Error(o(468,r))}u[Oe]=e,gt(u),r=u}e.stateNode=r}else wp(c,e.type,e.stateNode);else e.stateNode=bp(c,r,e.memoizedProps);else u!==r?(u===null?i.stateNode!==null&&(i=i.stateNode,i.parentNode.removeChild(i)):u.count--,r===null?wp(c,e.type,e.stateNode):bp(c,r,e.memoizedProps)):r===null&&e.stateNode!==null&&md(e,e.memoizedProps,i.memoizedProps)}break;case 27:Za(a,e),Qa(e),r&512&&(ea||i===null||Sn(i,i.return)),i!==null&&r&4&&md(e,e.memoizedProps,i.memoizedProps);break;case 5:if(Za(a,e),Qa(e),r&512&&(ea||i===null||Sn(i,i.return)),e.flags&32){c=e.stateNode;try{$e(c,"")}catch(W){Lt(e,e.return,W)}}r&4&&e.stateNode!=null&&(c=e.memoizedProps,md(e,c,i!==null?i.memoizedProps:c)),r&1024&&(xd=!0);break;case 6:if(Za(a,e),Qa(e),r&4){if(e.stateNode===null)throw Error(o(162));r=e.memoizedProps,i=e.stateNode;try{i.nodeValue=r}catch(W){Lt(e,e.return,W)}}break;case 3:if(fo=null,c=gn,gn=co(a.containerInfo),Za(a,e),gn=c,Qa(e),r&4&&i!==null&&i.memoizedState.isDehydrated)try{Ir(a.containerInfo)}catch(W){Lt(e,e.return,W)}xd&&(xd=!1,Am(e));break;case 4:r=gn,gn=co(e.stateNode.containerInfo),Za(a,e),Qa(e),gn=r;break;case 12:Za(a,e),Qa(e);break;case 13:Za(a,e),Qa(e),e.child.flags&8192&&e.memoizedState!==null!=(i!==null&&i.memoizedState!==null)&&(_d=Ke()),r&4&&(r=e.updateQueue,r!==null&&(e.updateQueue=null,yd(e,r)));break;case 22:c=e.memoizedState!==null;var k=i!==null&&i.memoizedState!==null,Y=Pn,le=ea;if(Pn=Y||c,ea=le||k,Za(a,e),ea=le,Pn=Y,Qa(e),r&8192)e:for(a=e.stateNode,a._visibility=c?a._visibility&-2:a._visibility|1,c&&(i===null||k||Pn||ea||Yi(e)),i=null,a=e;;){if(a.tag===5||a.tag===26){if(i===null){k=i=a;try{if(u=k.stateNode,c)y=u.style,typeof y.setProperty=="function"?y.setProperty("display","none","important"):y.display="none";else{w=k.stateNode;var ye=k.memoizedProps.style,Z=ye!=null&&ye.hasOwnProperty("display")?ye.display:null;w.style.display=Z==null||typeof Z=="boolean"?"":(""+Z).trim()}}catch(W){Lt(k,k.return,W)}}}else if(a.tag===6){if(i===null){k=a;try{k.stateNode.nodeValue=c?"":k.memoizedProps}catch(W){Lt(k,k.return,W)}}}else if((a.tag!==22&&a.tag!==23||a.memoizedState===null||a===e)&&a.child!==null){a.child.return=a,a=a.child;continue}if(a===e)break e;for(;a.sibling===null;){if(a.return===null||a.return===e)break e;i===a&&(i=null),a=a.return}i===a&&(i=null),a.sibling.return=a.return,a=a.sibling}r&4&&(r=e.updateQueue,r!==null&&(i=r.retryQueue,i!==null&&(r.retryQueue=null,yd(e,i))));break;case 19:Za(a,e),Qa(e),r&4&&(r=e.updateQueue,r!==null&&(e.updateQueue=null,yd(e,r)));break;case 30:break;case 21:break;default:Za(a,e),Qa(e)}}function Qa(e){var a=e.flags;if(a&2){try{for(var i,r=e.return;r!==null;){if(bm(r)){i=r;break}r=r.return}if(i==null)throw Error(o(160));switch(i.tag){case 27:var c=i.stateNode,u=pd(e);Ql(e,u,c);break;case 5:var y=i.stateNode;i.flags&32&&($e(y,""),i.flags&=-33);var w=pd(e);Ql(e,w,y);break;case 3:case 4:var k=i.stateNode.containerInfo,Y=pd(e);gd(e,Y,k);break;default:throw Error(o(161))}}catch(le){Lt(e,e.return,le)}e.flags&=-3}a&4096&&(e.flags&=-4097)}function Am(e){if(e.subtreeFlags&1024)for(e=e.child;e!==null;){var a=e;Am(a),a.tag===5&&a.flags&1024&&a.stateNode.reset(),e=e.sibling}}function mi(e,a){if(a.subtreeFlags&8772)for(a=a.child;a!==null;)Nm(e,a.alternate,a),a=a.sibling}function Yi(e){for(e=e.child;e!==null;){var a=e;switch(a.tag){case 0:case 11:case 14:case 15:hi(4,a,a.return),Yi(a);break;case 1:Sn(a,a.return);var i=a.stateNode;typeof i.componentWillUnmount=="function"&&ym(a,a.return,i),Yi(a);break;case 27:Dr(a.stateNode);case 26:case 5:Sn(a,a.return),Yi(a);break;case 22:a.memoizedState===null&&Yi(a);break;case 30:Yi(a);break;default:Yi(a)}e=e.sibling}}function pi(e,a,i){for(i=i&&(a.subtreeFlags&8772)!==0,a=a.child;a!==null;){var r=a.alternate,c=e,u=a,y=u.flags;switch(u.tag){case 0:case 11:case 15:pi(c,u,i),Nr(4,u);break;case 1:if(pi(c,u,i),r=u,c=r.stateNode,typeof c.componentDidMount=="function")try{c.componentDidMount()}catch(Y){Lt(r,r.return,Y)}if(r=u,c=r.updateQueue,c!==null){var w=r.stateNode;try{var k=c.shared.hiddenCallbacks;if(k!==null)for(c.shared.hiddenCallbacks=null,c=0;c<k.length;c++)nh(k[c],w)}catch(Y){Lt(r,r.return,Y)}}i&&y&64&&xm(u),_r(u,u.return);break;case 27:jm(u);case 26:case 5:pi(c,u,i),i&&r===null&&y&4&&vm(u),_r(u,u.return);break;case 12:pi(c,u,i);break;case 13:pi(c,u,i),i&&y&4&&Tm(c,u);break;case 22:u.memoizedState===null&&pi(c,u,i),_r(u,u.return);break;case 30:break;default:pi(c,u,i)}a=a.sibling}}function vd(e,a){var i=null;e!==null&&e.memoizedState!==null&&e.memoizedState.cachePool!==null&&(i=e.memoizedState.cachePool.pool),e=null,a.memoizedState!==null&&a.memoizedState.cachePool!==null&&(e=a.memoizedState.cachePool.pool),e!==i&&(e!=null&&e.refCount++,i!=null&&cr(i))}function bd(e,a){e=null,a.alternate!==null&&(e=a.alternate.memoizedState.cache),a=a.memoizedState.cache,a!==e&&(a.refCount++,e!=null&&cr(e))}function Tn(e,a,i,r){if(a.subtreeFlags&10256)for(a=a.child;a!==null;)zm(e,a,i,r),a=a.sibling}function zm(e,a,i,r){var c=a.flags;switch(a.tag){case 0:case 11:case 15:Tn(e,a,i,r),c&2048&&Nr(9,a);break;case 1:Tn(e,a,i,r);break;case 3:Tn(e,a,i,r),c&2048&&(e=null,a.alternate!==null&&(e=a.alternate.memoizedState.cache),a=a.memoizedState.cache,a!==e&&(a.refCount++,e!=null&&cr(e)));break;case 12:if(c&2048){Tn(e,a,i,r),e=a.stateNode;try{var u=a.memoizedProps,y=u.id,w=u.onPostCommit;typeof w=="function"&&w(y,a.alternate===null?"mount":"update",e.passiveEffectDuration,-0)}catch(k){Lt(a,a.return,k)}}else Tn(e,a,i,r);break;case 13:Tn(e,a,i,r);break;case 23:break;case 22:u=a.stateNode,y=a.alternate,a.memoizedState!==null?u._visibility&2?Tn(e,a,i,r):Sr(e,a):u._visibility&2?Tn(e,a,i,r):(u._visibility|=2,Ns(e,a,i,r,(a.subtreeFlags&10256)!==0)),c&2048&&vd(y,a);break;case 24:Tn(e,a,i,r),c&2048&&bd(a.alternate,a);break;default:Tn(e,a,i,r)}}function Ns(e,a,i,r,c){for(c=c&&(a.subtreeFlags&10256)!==0,a=a.child;a!==null;){var u=e,y=a,w=i,k=r,Y=y.flags;switch(y.tag){case 0:case 11:case 15:Ns(u,y,w,k,c),Nr(8,y);break;case 23:break;case 22:var le=y.stateNode;y.memoizedState!==null?le._visibility&2?Ns(u,y,w,k,c):Sr(u,y):(le._visibility|=2,Ns(u,y,w,k,c)),c&&Y&2048&&vd(y.alternate,y);break;case 24:Ns(u,y,w,k,c),c&&Y&2048&&bd(y.alternate,y);break;default:Ns(u,y,w,k,c)}a=a.sibling}}function Sr(e,a){if(a.subtreeFlags&10256)for(a=a.child;a!==null;){var i=e,r=a,c=r.flags;switch(r.tag){case 22:Sr(i,r),c&2048&&vd(r.alternate,r);break;case 24:Sr(i,r),c&2048&&bd(r.alternate,r);break;default:Sr(i,r)}a=a.sibling}}var Tr=8192;function _s(e){if(e.subtreeFlags&Tr)for(e=e.child;e!==null;)km(e),e=e.sibling}function km(e){switch(e.tag){case 26:_s(e),e.flags&Tr&&e.memoizedState!==null&&Jy(gn,e.memoizedState,e.memoizedProps);break;case 5:_s(e);break;case 3:case 4:var a=gn;gn=co(e.stateNode.containerInfo),_s(e),gn=a;break;case 22:e.memoizedState===null&&(a=e.alternate,a!==null&&a.memoizedState!==null?(a=Tr,Tr=16777216,_s(e),Tr=a):_s(e));break;default:_s(e)}}function Em(e){var a=e.alternate;if(a!==null&&(e=a.child,e!==null)){a.child=null;do a=e.sibling,e.sibling=null,e=a;while(e!==null)}}function Cr(e){var a=e.deletions;if((e.flags&16)!==0){if(a!==null)for(var i=0;i<a.length;i++){var r=a[i];ha=r,Dm(r,e)}Em(e)}if(e.subtreeFlags&10256)for(e=e.child;e!==null;)Mm(e),e=e.sibling}function Mm(e){switch(e.tag){case 0:case 11:case 15:Cr(e),e.flags&2048&&hi(9,e,e.return);break;case 3:Cr(e);break;case 12:Cr(e);break;case 22:var a=e.stateNode;e.memoizedState!==null&&a._visibility&2&&(e.return===null||e.return.tag!==13)?(a._visibility&=-3,Jl(e)):Cr(e);break;default:Cr(e)}}function Jl(e){var a=e.deletions;if((e.flags&16)!==0){if(a!==null)for(var i=0;i<a.length;i++){var r=a[i];ha=r,Dm(r,e)}Em(e)}for(e=e.child;e!==null;){switch(a=e,a.tag){case 0:case 11:case 15:hi(8,a,a.return),Jl(a);break;case 22:i=a.stateNode,i._visibility&2&&(i._visibility&=-3,Jl(a));break;default:Jl(a)}e=e.sibling}}function Dm(e,a){for(;ha!==null;){var i=ha;switch(i.tag){case 0:case 11:case 15:hi(8,i,a);break;case 23:case 22:if(i.memoizedState!==null&&i.memoizedState.cachePool!==null){var r=i.memoizedState.cachePool.pool;r!=null&&r.refCount++}break;case 24:cr(i.memoizedState.cache)}if(r=i.child,r!==null)r.return=i,ha=r;else e:for(i=e;ha!==null;){r=ha;var c=r.sibling,u=r.return;if(_m(r),r===i){ha=null;break e}if(c!==null){c.return=u,ha=c;break e}ha=u}}}var hy={getCacheForType:function(e){var a=Sa(ra),i=a.data.get(e);return i===void 0&&(i=e(),a.data.set(e,i)),i}},my=typeof WeakMap=="function"?WeakMap:Map,At=0,$t=null,ct=null,pt=0,zt=0,Ja=null,gi=!1,Ss=!1,jd=!1,Zn=0,Wt=0,xi=0,Gi=0,wd=0,cn=0,Ts=0,Ar=null,Ba=null,Nd=!1,_d=0,Wl=1/0,Kl=null,yi=null,ba=0,vi=null,Cs=null,As=0,Sd=0,Td=null,Rm=null,zr=0,Cd=null;function Wa(){if((At&2)!==0&&pt!==0)return pt&-pt;if(S.T!==null){var e=ps;return e!==0?e:Rd()}return Ct()}function Om(){cn===0&&(cn=(pt&536870912)===0||Nt?Ot():536870912);var e=on.current;return e!==null&&(e.flags|=32),cn}function Ka(e,a,i){(e===$t&&(zt===2||zt===9)||e.cancelPendingCommit!==null)&&(zs(e,0),bi(e,pt,cn,!1)),R(e,i),((At&2)===0||e!==$t)&&(e===$t&&((At&2)===0&&(Gi|=i),Wt===4&&bi(e,pt,cn,!1)),Cn(e))}function Um(e,a,i){if((At&6)!==0)throw Error(o(327));var r=!i&&(a&124)===0&&(a&e.expiredLanes)===0||et(e,a),c=r?xy(e,a):kd(e,a,!0),u=r;do{if(c===0){Ss&&!r&&bi(e,a,0,!1);break}else{if(i=e.current.alternate,u&&!py(i)){c=kd(e,a,!1),u=!1;continue}if(c===2){if(u=a,e.errorRecoveryDisabledLanes&u)var y=0;else y=e.pendingLanes&-536870913,y=y!==0?y:y&536870912?536870912:0;if(y!==0){a=y;e:{var w=e;c=Ar;var k=w.current.memoizedState.isDehydrated;if(k&&(zs(w,y).flags|=256),y=kd(w,y,!1),y!==2){if(jd&&!k){w.errorRecoveryDisabledLanes|=u,Gi|=u,c=4;break e}u=Ba,Ba=c,u!==null&&(Ba===null?Ba=u:Ba.push.apply(Ba,u))}c=y}if(u=!1,c!==2)continue}}if(c===1){zs(e,0),bi(e,a,0,!0);break}e:{switch(r=e,u=c,u){case 0:case 1:throw Error(o(345));case 4:if((a&4194048)!==a)break;case 6:bi(r,a,cn,!gi);break e;case 2:Ba=null;break;case 3:case 5:break;default:throw Error(o(329))}if((a&62914560)===a&&(c=_d+300-Ke(),10<c)){if(bi(r,a,cn,!gi),Xe(r,0,!0)!==0)break e;r.timeoutHandle=up(Lm.bind(null,r,i,Ba,Kl,Nd,a,cn,Gi,Ts,gi,u,2,-0,0),c);break e}Lm(r,i,Ba,Kl,Nd,a,cn,Gi,Ts,gi,u,0,-0,0)}}break}while(!0);Cn(e)}function Lm(e,a,i,r,c,u,y,w,k,Y,le,ye,Z,W){if(e.timeoutHandle=-1,ye=a.subtreeFlags,(ye&8192||(ye&16785408)===16785408)&&(Ur={stylesheets:null,count:0,unsuspend:Qy},km(a),ye=Wy(),ye!==null)){e.cancelPendingCommit=ye(Ym.bind(null,e,a,u,i,r,c,y,w,k,le,1,Z,W)),bi(e,u,y,!Y);return}Ym(e,a,u,i,r,c,y,w,k)}function py(e){for(var a=e;;){var i=a.tag;if((i===0||i===11||i===15)&&a.flags&16384&&(i=a.updateQueue,i!==null&&(i=i.stores,i!==null)))for(var r=0;r<i.length;r++){var c=i[r],u=c.getSnapshot;c=c.value;try{if(!Pa(u(),c))return!1}catch{return!1}}if(i=a.child,a.subtreeFlags&16384&&i!==null)i.return=a,a=i;else{if(a===e)break;for(;a.sibling===null;){if(a.return===null||a.return===e)return!0;a=a.return}a.sibling.return=a.return,a=a.sibling}}return!0}function bi(e,a,i,r){a&=~wd,a&=~Gi,e.suspendedLanes|=a,e.pingedLanes&=~a,r&&(e.warmLanes|=a),r=e.expirationTimes;for(var c=a;0<c;){var u=31-ft(c),y=1<<u;r[u]=-1,c&=~y}i!==0&&Ie(e,i,a)}function eo(){return(At&6)===0?(kr(0),!1):!0}function Ad(){if(ct!==null){if(zt===0)var e=ct.return;else e=ct,In=qi=null,Gc(e),js=null,br=0,e=ct;for(;e!==null;)gm(e.alternate,e),e=e.return;ct=null}}function zs(e,a){var i=e.timeoutHandle;i!==-1&&(e.timeoutHandle=-1,Dy(i)),i=e.cancelPendingCommit,i!==null&&(e.cancelPendingCommit=null,i()),Ad(),$t=e,ct=i=Bn(e.current,null),pt=a,zt=0,Ja=null,gi=!1,Ss=et(e,a),jd=!1,Ts=cn=wd=Gi=xi=Wt=0,Ba=Ar=null,Nd=!1,(a&8)!==0&&(a|=a&32);var r=e.entangledLanes;if(r!==0)for(e=e.entanglements,r&=a;0<r;){var c=31-ft(r),u=1<<c;a|=e[c],r&=~u}return Zn=a,wl(),i}function Bm(e,a){st=null,S.H=Il,a===ur||a===El?(a=th(),zt=3):a===Wf?(a=th(),zt=4):zt=a===am?8:a!==null&&typeof a=="object"&&typeof a.then=="function"?6:1,Ja=a,ct===null&&(Wt=1,Vl(e,nn(a,e.current)))}function qm(){var e=S.H;return S.H=Il,e===null?Il:e}function Hm(){var e=S.A;return S.A=hy,e}function zd(){Wt=4,gi||(pt&4194048)!==pt&&on.current!==null||(Ss=!0),(xi&134217727)===0&&(Gi&134217727)===0||$t===null||bi($t,pt,cn,!1)}function kd(e,a,i){var r=At;At|=2;var c=qm(),u=Hm();($t!==e||pt!==a)&&(Kl=null,zs(e,a)),a=!1;var y=Wt;e:do try{if(zt!==0&&ct!==null){var w=ct,k=Ja;switch(zt){case 8:Ad(),y=6;break e;case 3:case 2:case 9:case 6:on.current===null&&(a=!0);var Y=zt;if(zt=0,Ja=null,ks(e,w,k,Y),i&&Ss){y=0;break e}break;default:Y=zt,zt=0,Ja=null,ks(e,w,k,Y)}}gy(),y=Wt;break}catch(le){Bm(e,le)}while(!0);return a&&e.shellSuspendCounter++,In=qi=null,At=r,S.H=c,S.A=u,ct===null&&($t=null,pt=0,wl()),y}function gy(){for(;ct!==null;)Im(ct)}function xy(e,a){var i=At;At|=2;var r=qm(),c=Hm();$t!==e||pt!==a?(Kl=null,Wl=Ke()+500,zs(e,a)):Ss=et(e,a);e:do try{if(zt!==0&&ct!==null){a=ct;var u=Ja;t:switch(zt){case 1:zt=0,Ja=null,ks(e,a,u,1);break;case 2:case 9:if(Kf(u)){zt=0,Ja=null,$m(a);break}a=function(){zt!==2&&zt!==9||$t!==e||(zt=7),Cn(e)},u.then(a,a);break e;case 3:zt=7;break e;case 4:zt=5;break e;case 7:Kf(u)?(zt=0,Ja=null,$m(a)):(zt=0,Ja=null,ks(e,a,u,7));break;case 5:var y=null;switch(ct.tag){case 26:y=ct.memoizedState;case 5:case 27:var w=ct;if(!y||Np(y)){zt=0,Ja=null;var k=w.sibling;if(k!==null)ct=k;else{var Y=w.return;Y!==null?(ct=Y,to(Y)):ct=null}break t}}zt=0,Ja=null,ks(e,a,u,5);break;case 6:zt=0,Ja=null,ks(e,a,u,6);break;case 8:Ad(),Wt=6;break e;default:throw Error(o(462))}}yy();break}catch(le){Bm(e,le)}while(!0);return In=qi=null,S.H=r,S.A=c,At=i,ct!==null?0:($t=null,pt=0,wl(),Wt)}function yy(){for(;ct!==null&&!Ve();)Im(ct)}function Im(e){var a=mm(e.alternate,e,Zn);e.memoizedProps=e.pendingProps,a===null?to(e):ct=a}function $m(e){var a=e,i=a.alternate;switch(a.tag){case 15:case 0:a=om(i,a,a.pendingProps,a.type,void 0,pt);break;case 11:a=om(i,a,a.pendingProps,a.type.render,a.ref,pt);break;case 5:Gc(a);default:gm(i,a),a=ct=Ff(a,Zn),a=mm(i,a,Zn)}e.memoizedProps=e.pendingProps,a===null?to(e):ct=a}function ks(e,a,i,r){In=qi=null,Gc(a),js=null,br=0;var c=a.return;try{if(ly(e,c,a,i,pt)){Wt=1,Vl(e,nn(i,e.current)),ct=null;return}}catch(u){if(c!==null)throw ct=c,u;Wt=1,Vl(e,nn(i,e.current)),ct=null;return}a.flags&32768?(Nt||r===1?e=!0:Ss||(pt&536870912)!==0?e=!1:(gi=e=!0,(r===2||r===9||r===3||r===6)&&(r=on.current,r!==null&&r.tag===13&&(r.flags|=16384))),Fm(a,e)):to(a)}function to(e){var a=e;do{if((a.flags&32768)!==0){Fm(a,gi);return}e=a.return;var i=cy(a.alternate,a,Zn);if(i!==null){ct=i;return}if(a=a.sibling,a!==null){ct=a;return}ct=a=e}while(a!==null);Wt===0&&(Wt=5)}function Fm(e,a){do{var i=dy(e.alternate,e);if(i!==null){i.flags&=32767,ct=i;return}if(i=e.return,i!==null&&(i.flags|=32768,i.subtreeFlags=0,i.deletions=null),!a&&(e=e.sibling,e!==null)){ct=e;return}ct=e=i}while(e!==null);Wt=6,ct=null}function Ym(e,a,i,r,c,u,y,w,k){e.cancelPendingCommit=null;do ao();while(ba!==0);if((At&6)!==0)throw Error(o(327));if(a!==null){if(a===e.current)throw Error(o(177));if(u=a.lanes|a.childLanes,u|=bc,ce(e,i,u,y,w,k),e===$t&&(ct=$t=null,pt=0),Cs=a,vi=e,As=i,Sd=u,Td=c,Rm=r,(a.subtreeFlags&10256)!==0||(a.flags&10256)!==0?(e.callbackNode=null,e.callbackPriority=0,wy(Ft,function(){return Zm(),null})):(e.callbackNode=null,e.callbackPriority=0),r=(a.flags&13878)!==0,(a.subtreeFlags&13878)!==0||r){r=S.T,S.T=null,c=H.p,H.p=2,y=At,At|=4;try{uy(e,a,i)}finally{At=y,H.p=c,S.T=r}}ba=1,Gm(),Vm(),Pm()}}function Gm(){if(ba===1){ba=0;var e=vi,a=Cs,i=(a.flags&13878)!==0;if((a.subtreeFlags&13878)!==0||i){i=S.T,S.T=null;var r=H.p;H.p=2;var c=At;At|=4;try{Cm(a,e);var u=$d,y=Df(e.containerInfo),w=u.focusedElem,k=u.selectionRange;if(y!==w&&w&&w.ownerDocument&&Mf(w.ownerDocument.documentElement,w)){if(k!==null&&pc(w)){var Y=k.start,le=k.end;if(le===void 0&&(le=Y),"selectionStart"in w)w.selectionStart=Y,w.selectionEnd=Math.min(le,w.value.length);else{var ye=w.ownerDocument||document,Z=ye&&ye.defaultView||window;if(Z.getSelection){var W=Z.getSelection(),We=w.textContent.length,Pe=Math.min(k.start,We),Dt=k.end===void 0?Pe:Math.min(k.end,We);!W.extend&&Pe>Dt&&(y=Dt,Dt=Pe,Pe=y);var B=Ef(w,Pe),O=Ef(w,Dt);if(B&&O&&(W.rangeCount!==1||W.anchorNode!==B.node||W.anchorOffset!==B.offset||W.focusNode!==O.node||W.focusOffset!==O.offset)){var $=ye.createRange();$.setStart(B.node,B.offset),W.removeAllRanges(),Pe>Dt?(W.addRange($),W.extend(O.node,O.offset)):($.setEnd(O.node,O.offset),W.addRange($))}}}}for(ye=[],W=w;W=W.parentNode;)W.nodeType===1&&ye.push({element:W,left:W.scrollLeft,top:W.scrollTop});for(typeof w.focus=="function"&&w.focus(),w=0;w<ye.length;w++){var he=ye[w];he.element.scrollLeft=he.left,he.element.scrollTop=he.top}}po=!!Id,$d=Id=null}finally{At=c,H.p=r,S.T=i}}e.current=a,ba=2}}function Vm(){if(ba===2){ba=0;var e=vi,a=Cs,i=(a.flags&8772)!==0;if((a.subtreeFlags&8772)!==0||i){i=S.T,S.T=null;var r=H.p;H.p=2;var c=At;At|=4;try{Nm(e,a.alternate,a)}finally{At=c,H.p=r,S.T=i}}ba=3}}function Pm(){if(ba===4||ba===3){ba=0,at();var e=vi,a=Cs,i=As,r=Rm;(a.subtreeFlags&10256)!==0||(a.flags&10256)!==0?ba=5:(ba=0,Cs=vi=null,Xm(e,e.pendingLanes));var c=e.pendingLanes;if(c===0&&(yi=null),ht(i),a=a.stateNode,Be&&typeof Be.onCommitFiberRoot=="function")try{Be.onCommitFiberRoot(ke,a,void 0,(a.current.flags&128)===128)}catch{}if(r!==null){a=S.T,c=H.p,H.p=2,S.T=null;try{for(var u=e.onRecoverableError,y=0;y<r.length;y++){var w=r[y];u(w.value,{componentStack:w.stack})}}finally{S.T=a,H.p=c}}(As&3)!==0&&ao(),Cn(e),c=e.pendingLanes,(i&4194090)!==0&&(c&42)!==0?e===Cd?zr++:(zr=0,Cd=e):zr=0,kr(0)}}function Xm(e,a){(e.pooledCacheLanes&=a)===0&&(a=e.pooledCache,a!=null&&(e.pooledCache=null,cr(a)))}function ao(e){return Gm(),Vm(),Pm(),Zm()}function Zm(){if(ba!==5)return!1;var e=vi,a=Sd;Sd=0;var i=ht(As),r=S.T,c=H.p;try{H.p=32>i?32:i,S.T=null,i=Td,Td=null;var u=vi,y=As;if(ba=0,Cs=vi=null,As=0,(At&6)!==0)throw Error(o(331));var w=At;if(At|=4,Mm(u.current),zm(u,u.current,y,i),At=w,kr(0,!1),Be&&typeof Be.onPostCommitFiberRoot=="function")try{Be.onPostCommitFiberRoot(ke,u)}catch{}return!0}finally{H.p=c,S.T=r,Xm(e,a)}}function Qm(e,a,i){a=nn(i,a),a=sd(e.stateNode,a,2),e=ci(e,a,2),e!==null&&(R(e,2),Cn(e))}function Lt(e,a,i){if(e.tag===3)Qm(e,e,i);else for(;a!==null;){if(a.tag===3){Qm(a,e,i);break}else if(a.tag===1){var r=a.stateNode;if(typeof a.type.getDerivedStateFromError=="function"||typeof r.componentDidCatch=="function"&&(yi===null||!yi.has(r))){e=nn(i,e),i=em(2),r=ci(a,i,2),r!==null&&(tm(i,r,a,e),R(r,2),Cn(r));break}}a=a.return}}function Ed(e,a,i){var r=e.pingCache;if(r===null){r=e.pingCache=new my;var c=new Set;r.set(a,c)}else c=r.get(a),c===void 0&&(c=new Set,r.set(a,c));c.has(i)||(jd=!0,c.add(i),e=vy.bind(null,e,a,i),a.then(e,e))}function vy(e,a,i){var r=e.pingCache;r!==null&&r.delete(a),e.pingedLanes|=e.suspendedLanes&i,e.warmLanes&=~i,$t===e&&(pt&i)===i&&(Wt===4||Wt===3&&(pt&62914560)===pt&&300>Ke()-_d?(At&2)===0&&zs(e,0):wd|=i,Ts===pt&&(Ts=0)),Cn(e)}function Jm(e,a){a===0&&(a=St()),e=us(e,a),e!==null&&(R(e,a),Cn(e))}function by(e){var a=e.memoizedState,i=0;a!==null&&(i=a.retryLane),Jm(e,i)}function jy(e,a){var i=0;switch(e.tag){case 13:var r=e.stateNode,c=e.memoizedState;c!==null&&(i=c.retryLane);break;case 19:r=e.stateNode;break;case 22:r=e.stateNode._retryCache;break;default:throw Error(o(314))}r!==null&&r.delete(a),Jm(e,i)}function wy(e,a){return be(e,a)}var no=null,Es=null,Md=!1,io=!1,Dd=!1,Vi=0;function Cn(e){e!==Es&&e.next===null&&(Es===null?no=Es=e:Es=Es.next=e),io=!0,Md||(Md=!0,_y())}function kr(e,a){if(!Dd&&io){Dd=!0;do for(var i=!1,r=no;r!==null;){if(e!==0){var c=r.pendingLanes;if(c===0)var u=0;else{var y=r.suspendedLanes,w=r.pingedLanes;u=(1<<31-ft(42|e)+1)-1,u&=c&~(y&~w),u=u&201326741?u&201326741|1:u?u|2:0}u!==0&&(i=!0,tp(r,u))}else u=pt,u=Xe(r,r===$t?u:0,r.cancelPendingCommit!==null||r.timeoutHandle!==-1),(u&3)===0||et(r,u)||(i=!0,tp(r,u));r=r.next}while(i);Dd=!1}}function Ny(){Wm()}function Wm(){io=Md=!1;var e=0;Vi!==0&&(My()&&(e=Vi),Vi=0);for(var a=Ke(),i=null,r=no;r!==null;){var c=r.next,u=Km(r,a);u===0?(r.next=null,i===null?no=c:i.next=c,c===null&&(Es=i)):(i=r,(e!==0||(u&3)!==0)&&(io=!0)),r=c}kr(e)}function Km(e,a){for(var i=e.suspendedLanes,r=e.pingedLanes,c=e.expirationTimes,u=e.pendingLanes&-62914561;0<u;){var y=31-ft(u),w=1<<y,k=c[y];k===-1?((w&i)===0||(w&r)!==0)&&(c[y]=ve(w,a)):k<=a&&(e.expiredLanes|=w),u&=~w}if(a=$t,i=pt,i=Xe(e,e===a?i:0,e.cancelPendingCommit!==null||e.timeoutHandle!==-1),r=e.callbackNode,i===0||e===a&&(zt===2||zt===9)||e.cancelPendingCommit!==null)return r!==null&&r!==null&&Me(r),e.callbackNode=null,e.callbackPriority=0;if((i&3)===0||et(e,i)){if(a=i&-i,a===e.callbackPriority)return a;switch(r!==null&&Me(r),ht(i)){case 2:case 8:i=Tt;break;case 32:i=Ft;break;case 268435456:i=ae;break;default:i=Ft}return r=ep.bind(null,e),i=be(i,r),e.callbackPriority=a,e.callbackNode=i,a}return r!==null&&r!==null&&Me(r),e.callbackPriority=2,e.callbackNode=null,2}function ep(e,a){if(ba!==0&&ba!==5)return e.callbackNode=null,e.callbackPriority=0,null;var i=e.callbackNode;if(ao()&&e.callbackNode!==i)return null;var r=pt;return r=Xe(e,e===$t?r:0,e.cancelPendingCommit!==null||e.timeoutHandle!==-1),r===0?null:(Um(e,r,a),Km(e,Ke()),e.callbackNode!=null&&e.callbackNode===i?ep.bind(null,e):null)}function tp(e,a){if(ao())return null;Um(e,a,!0)}function _y(){Ry(function(){(At&6)!==0?be(_t,Ny):Wm()})}function Rd(){return Vi===0&&(Vi=Ot()),Vi}function ap(e){return e==null||typeof e=="symbol"||typeof e=="boolean"?null:typeof e=="function"?e:Ue(""+e)}function np(e,a){var i=a.ownerDocument.createElement("input");return i.name=a.name,i.value=a.value,e.id&&i.setAttribute("form",e.id),a.parentNode.insertBefore(i,a),e=new FormData(e),i.parentNode.removeChild(i),e}function Sy(e,a,i,r,c){if(a==="submit"&&i&&i.stateNode===c){var u=ap((c[lt]||null).action),y=r.submitter;y&&(a=(a=y[lt]||null)?ap(a.formAction):y.getAttribute("formAction"),a!==null&&(u=a,y=null));var w=new vl("action","action",null,r,c);e.push({event:w,listeners:[{instance:null,listener:function(){if(r.defaultPrevented){if(Vi!==0){var k=y?np(c,y):new FormData(c);ed(i,{pending:!0,data:k,method:c.method,action:u},null,k)}}else typeof u=="function"&&(w.preventDefault(),k=y?np(c,y):new FormData(c),ed(i,{pending:!0,data:k,method:c.method,action:u},u,k))},currentTarget:c}]})}}for(var Od=0;Od<vc.length;Od++){var Ud=vc[Od],Ty=Ud.toLowerCase(),Cy=Ud[0].toUpperCase()+Ud.slice(1);pn(Ty,"on"+Cy)}pn(Uf,"onAnimationEnd"),pn(Lf,"onAnimationIteration"),pn(Bf,"onAnimationStart"),pn("dblclick","onDoubleClick"),pn("focusin","onFocus"),pn("focusout","onBlur"),pn(Y0,"onTransitionRun"),pn(G0,"onTransitionStart"),pn(V0,"onTransitionCancel"),pn(qf,"onTransitionEnd"),Ga("onMouseEnter",["mouseout","mouseover"]),Ga("onMouseLeave",["mouseout","mouseover"]),Ga("onPointerEnter",["pointerout","pointerover"]),Ga("onPointerLeave",["pointerout","pointerover"]),Ya("onChange","change click focusin focusout input keydown keyup selectionchange".split(" ")),Ya("onSelect","focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" ")),Ya("onBeforeInput",["compositionend","keypress","textInput","paste"]),Ya("onCompositionEnd","compositionend focusout keydown keypress keyup mousedown".split(" ")),Ya("onCompositionStart","compositionstart focusout keydown keypress keyup mousedown".split(" ")),Ya("onCompositionUpdate","compositionupdate focusout keydown keypress keyup mousedown".split(" "));var Er="abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "),Ay=new Set("beforetoggle cancel close invalid load scroll scrollend toggle".split(" ").concat(Er));function ip(e,a){a=(a&4)!==0;for(var i=0;i<e.length;i++){var r=e[i],c=r.event;r=r.listeners;e:{var u=void 0;if(a)for(var y=r.length-1;0<=y;y--){var w=r[y],k=w.instance,Y=w.currentTarget;if(w=w.listener,k!==u&&c.isPropagationStopped())break e;u=w,c.currentTarget=Y;try{u(c)}catch(le){Gl(le)}c.currentTarget=null,u=k}else for(y=0;y<r.length;y++){if(w=r[y],k=w.instance,Y=w.currentTarget,w=w.listener,k!==u&&c.isPropagationStopped())break e;u=w,c.currentTarget=Y;try{u(c)}catch(le){Gl(le)}c.currentTarget=null,u=k}}}}function dt(e,a){var i=a[qt];i===void 0&&(i=a[qt]=new Set);var r=e+"__bubble";i.has(r)||(sp(a,e,2,!1),i.add(r))}function Ld(e,a,i){var r=0;a&&(r|=4),sp(i,e,r,a)}var so="_reactListening"+Math.random().toString(36).slice(2);function Bd(e){if(!e[so]){e[so]=!0,tt.forEach(function(i){i!=="selectionchange"&&(Ay.has(i)||Ld(i,!1,e),Ld(i,!0,e))});var a=e.nodeType===9?e:e.ownerDocument;a===null||a[so]||(a[so]=!0,Ld("selectionchange",!1,a))}}function sp(e,a,i,r){switch(zp(a)){case 2:var c=tv;break;case 8:c=av;break;default:c=Wd}i=c.bind(null,a,i,e),c=void 0,!Js||a!=="touchstart"&&a!=="touchmove"&&a!=="wheel"||(c=!0),r?c!==void 0?e.addEventListener(a,i,{capture:!0,passive:c}):e.addEventListener(a,i,!0):c!==void 0?e.addEventListener(a,i,{passive:c}):e.addEventListener(a,i,!1)}function qd(e,a,i,r,c){var u=r;if((a&1)===0&&(a&2)===0&&r!==null)e:for(;;){if(r===null)return;var y=r.tag;if(y===3||y===4){var w=r.stateNode.containerInfo;if(w===c)break;if(y===4)for(y=r.return;y!==null;){var k=y.tag;if((k===3||k===4)&&y.stateNode.containerInfo===c)return;y=y.return}for(;w!==null;){if(y=Da(w),y===null)return;if(k=y.tag,k===5||k===6||k===26||k===27){r=u=y;continue e}w=w.parentNode}}r=r.return}Pt(function(){var Y=u,le=Ge(i),ye=[];e:{var Z=Hf.get(e);if(Z!==void 0){var W=vl,We=e;switch(e){case"keypress":if(xl(i)===0)break e;case"keydown":case"keyup":W=w0;break;case"focusin":We="focus",W=dc;break;case"focusout":We="blur",W=dc;break;case"beforeblur":case"afterblur":W=dc;break;case"click":if(i.button===2)break e;case"auxclick":case"dblclick":case"mousedown":case"mousemove":case"mouseup":case"mouseout":case"mouseover":case"contextmenu":W=pf;break;case"drag":case"dragend":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"dragstart":case"drop":W=d0;break;case"touchcancel":case"touchend":case"touchmove":case"touchstart":W=S0;break;case Uf:case Lf:case Bf:W=h0;break;case qf:W=C0;break;case"scroll":case"scrollend":W=o0;break;case"wheel":W=z0;break;case"copy":case"cut":case"paste":W=p0;break;case"gotpointercapture":case"lostpointercapture":case"pointercancel":case"pointerdown":case"pointermove":case"pointerout":case"pointerover":case"pointerup":W=xf;break;case"toggle":case"beforetoggle":W=E0}var Pe=(a&4)!==0,Dt=!Pe&&(e==="scroll"||e==="scrollend"),B=Pe?Z!==null?Z+"Capture":null:Z;Pe=[];for(var O=Y,$;O!==null;){var he=O;if($=he.stateNode,he=he.tag,he!==5&&he!==26&&he!==27||$===null||B===null||(he=_a(O,B),he!=null&&Pe.push(Mr(O,he,$))),Dt)break;O=O.return}0<Pe.length&&(Z=new W(Z,We,null,i,le),ye.push({event:Z,listeners:Pe}))}}if((a&7)===0){e:{if(Z=e==="mouseover"||e==="pointerover",W=e==="mouseout"||e==="pointerout",Z&&i!==Je&&(We=i.relatedTarget||i.fromElement)&&(Da(We)||We[Ut]))break e;if((W||Z)&&(Z=le.window===le?le:(Z=le.ownerDocument)?Z.defaultView||Z.parentWindow:window,W?(We=i.relatedTarget||i.toElement,W=Y,We=We?Da(We):null,We!==null&&(Dt=f(We),Pe=We.tag,We!==Dt||Pe!==5&&Pe!==27&&Pe!==6)&&(We=null)):(W=null,We=Y),W!==We)){if(Pe=pf,he="onMouseLeave",B="onMouseEnter",O="mouse",(e==="pointerout"||e==="pointerover")&&(Pe=xf,he="onPointerLeave",B="onPointerEnter",O="pointer"),Dt=W==null?Z:sa(W),$=We==null?Z:sa(We),Z=new Pe(he,O+"leave",W,i,le),Z.target=Dt,Z.relatedTarget=$,he=null,Da(le)===Y&&(Pe=new Pe(B,O+"enter",We,i,le),Pe.target=$,Pe.relatedTarget=Dt,he=Pe),Dt=he,W&&We)t:{for(Pe=W,B=We,O=0,$=Pe;$;$=Ms($))O++;for($=0,he=B;he;he=Ms(he))$++;for(;0<O-$;)Pe=Ms(Pe),O--;for(;0<$-O;)B=Ms(B),$--;for(;O--;){if(Pe===B||B!==null&&Pe===B.alternate)break t;Pe=Ms(Pe),B=Ms(B)}Pe=null}else Pe=null;W!==null&&rp(ye,Z,W,Pe,!1),We!==null&&Dt!==null&&rp(ye,Dt,We,Pe,!0)}}e:{if(Z=Y?sa(Y):window,W=Z.nodeName&&Z.nodeName.toLowerCase(),W==="select"||W==="input"&&Z.type==="file")var qe=Sf;else if(Nf(Z))if(Tf)qe=I0;else{qe=q0;var ot=B0}else W=Z.nodeName,!W||W.toLowerCase()!=="input"||Z.type!=="checkbox"&&Z.type!=="radio"?Y&&j(Y.elementType)&&(qe=Sf):qe=H0;if(qe&&(qe=qe(e,Y))){_f(ye,qe,i,le);break e}ot&&ot(e,Z,Y),e==="focusout"&&Y&&Z.type==="number"&&Y.memoizedProps.value!=null&&te(Z,"number",Z.value)}switch(ot=Y?sa(Y):window,e){case"focusin":(Nf(ot)||ot.contentEditable==="true")&&(os=ot,gc=Y,ir=null);break;case"focusout":ir=gc=os=null;break;case"mousedown":xc=!0;break;case"contextmenu":case"mouseup":case"dragend":xc=!1,Rf(ye,i,le);break;case"selectionchange":if(F0)break;case"keydown":case"keyup":Rf(ye,i,le)}var Ye;if(fc)e:{switch(e){case"compositionstart":var Qe="onCompositionStart";break e;case"compositionend":Qe="onCompositionEnd";break e;case"compositionupdate":Qe="onCompositionUpdate";break e}Qe=void 0}else ls?jf(e,i)&&(Qe="onCompositionEnd"):e==="keydown"&&i.keyCode===229&&(Qe="onCompositionStart");Qe&&(yf&&i.locale!=="ko"&&(ls||Qe!=="onCompositionStart"?Qe==="onCompositionEnd"&&ls&&(Ye=hf()):(ya=le,Va="value"in ya?ya.value:ya.textContent,ls=!0)),ot=ro(Y,Qe),0<ot.length&&(Qe=new gf(Qe,e,null,i,le),ye.push({event:Qe,listeners:ot}),Ye?Qe.data=Ye:(Ye=wf(i),Ye!==null&&(Qe.data=Ye)))),(Ye=D0?R0(e,i):O0(e,i))&&(Qe=ro(Y,"onBeforeInput"),0<Qe.length&&(ot=new gf("onBeforeInput","beforeinput",null,i,le),ye.push({event:ot,listeners:Qe}),ot.data=Ye)),Sy(ye,e,Y,i,le)}ip(ye,a)})}function Mr(e,a,i){return{instance:e,listener:a,currentTarget:i}}function ro(e,a){for(var i=a+"Capture",r=[];e!==null;){var c=e,u=c.stateNode;if(c=c.tag,c!==5&&c!==26&&c!==27||u===null||(c=_a(e,i),c!=null&&r.unshift(Mr(e,c,u)),c=_a(e,a),c!=null&&r.push(Mr(e,c,u))),e.tag===3)return r;e=e.return}return[]}function Ms(e){if(e===null)return null;do e=e.return;while(e&&e.tag!==5&&e.tag!==27);return e||null}function rp(e,a,i,r,c){for(var u=a._reactName,y=[];i!==null&&i!==r;){var w=i,k=w.alternate,Y=w.stateNode;if(w=w.tag,k!==null&&k===r)break;w!==5&&w!==26&&w!==27||Y===null||(k=Y,c?(Y=_a(i,u),Y!=null&&y.unshift(Mr(i,Y,k))):c||(Y=_a(i,u),Y!=null&&y.push(Mr(i,Y,k)))),i=i.return}y.length!==0&&e.push({event:a,listeners:y})}var zy=/\r\n?/g,ky=/\u0000|\uFFFD/g;function lp(e){return(typeof e=="string"?e:""+e).replace(zy,`
`).replace(ky,"")}function op(e,a){return a=lp(a),lp(e)===a}function lo(){}function Mt(e,a,i,r,c,u){switch(i){case"children":typeof r=="string"?a==="body"||a==="textarea"&&r===""||$e(e,r):(typeof r=="number"||typeof r=="bigint")&&a!=="body"&&$e(e,""+r);break;case"className":ii(e,"class",r);break;case"tabIndex":ii(e,"tabindex",r);break;case"dir":case"role":case"viewBox":case"width":case"height":ii(e,i,r);break;case"style":wa(e,r,u);break;case"data":if(a!=="object"){ii(e,"data",r);break}case"src":case"href":if(r===""&&(a!=="a"||i!=="href")){e.removeAttribute(i);break}if(r==null||typeof r=="function"||typeof r=="symbol"||typeof r=="boolean"){e.removeAttribute(i);break}r=Ue(""+r),e.setAttribute(i,r);break;case"action":case"formAction":if(typeof r=="function"){e.setAttribute(i,"javascript:throw new Error('A React form was unexpectedly submitted. If you called form.submit() manually, consider using form.requestSubmit() instead. If you\\'re trying to use event.stopPropagation() in a submit event handler, consider also calling event.preventDefault().')");break}else typeof u=="function"&&(i==="formAction"?(a!=="input"&&Mt(e,a,"name",c.name,c,null),Mt(e,a,"formEncType",c.formEncType,c,null),Mt(e,a,"formMethod",c.formMethod,c,null),Mt(e,a,"formTarget",c.formTarget,c,null)):(Mt(e,a,"encType",c.encType,c,null),Mt(e,a,"method",c.method,c,null),Mt(e,a,"target",c.target,c,null)));if(r==null||typeof r=="symbol"||typeof r=="boolean"){e.removeAttribute(i);break}r=Ue(""+r),e.setAttribute(i,r);break;case"onClick":r!=null&&(e.onclick=lo);break;case"onScroll":r!=null&&dt("scroll",e);break;case"onScrollEnd":r!=null&&dt("scrollend",e);break;case"dangerouslySetInnerHTML":if(r!=null){if(typeof r!="object"||!("__html"in r))throw Error(o(61));if(i=r.__html,i!=null){if(c.children!=null)throw Error(o(60));e.innerHTML=i}}break;case"multiple":e.multiple=r&&typeof r!="function"&&typeof r!="symbol";break;case"muted":e.muted=r&&typeof r!="function"&&typeof r!="symbol";break;case"suppressContentEditableWarning":case"suppressHydrationWarning":case"defaultValue":case"defaultChecked":case"innerHTML":case"ref":break;case"autoFocus":break;case"xlinkHref":if(r==null||typeof r=="function"||typeof r=="boolean"||typeof r=="symbol"){e.removeAttribute("xlink:href");break}i=Ue(""+r),e.setAttributeNS("http://www.w3.org/1999/xlink","xlink:href",i);break;case"contentEditable":case"spellCheck":case"draggable":case"value":case"autoReverse":case"externalResourcesRequired":case"focusable":case"preserveAlpha":r!=null&&typeof r!="function"&&typeof r!="symbol"?e.setAttribute(i,""+r):e.removeAttribute(i);break;case"inert":case"allowFullScreen":case"async":case"autoPlay":case"controls":case"default":case"defer":case"disabled":case"disablePictureInPicture":case"disableRemotePlayback":case"formNoValidate":case"hidden":case"loop":case"noModule":case"noValidate":case"open":case"playsInline":case"readOnly":case"required":case"reversed":case"scoped":case"seamless":case"itemScope":r&&typeof r!="function"&&typeof r!="symbol"?e.setAttribute(i,""):e.removeAttribute(i);break;case"capture":case"download":r===!0?e.setAttribute(i,""):r!==!1&&r!=null&&typeof r!="function"&&typeof r!="symbol"?e.setAttribute(i,r):e.removeAttribute(i);break;case"cols":case"rows":case"size":case"span":r!=null&&typeof r!="function"&&typeof r!="symbol"&&!isNaN(r)&&1<=r?e.setAttribute(i,r):e.removeAttribute(i);break;case"rowSpan":case"start":r==null||typeof r=="function"||typeof r=="symbol"||isNaN(r)?e.removeAttribute(i):e.setAttribute(i,r);break;case"popover":dt("beforetoggle",e),dt("toggle",e),En(e,"popover",r);break;case"xlinkActuate":Ra(e,"http://www.w3.org/1999/xlink","xlink:actuate",r);break;case"xlinkArcrole":Ra(e,"http://www.w3.org/1999/xlink","xlink:arcrole",r);break;case"xlinkRole":Ra(e,"http://www.w3.org/1999/xlink","xlink:role",r);break;case"xlinkShow":Ra(e,"http://www.w3.org/1999/xlink","xlink:show",r);break;case"xlinkTitle":Ra(e,"http://www.w3.org/1999/xlink","xlink:title",r);break;case"xlinkType":Ra(e,"http://www.w3.org/1999/xlink","xlink:type",r);break;case"xmlBase":Ra(e,"http://www.w3.org/XML/1998/namespace","xml:base",r);break;case"xmlLang":Ra(e,"http://www.w3.org/XML/1998/namespace","xml:lang",r);break;case"xmlSpace":Ra(e,"http://www.w3.org/XML/1998/namespace","xml:space",r);break;case"is":En(e,"is",r);break;case"innerText":case"textContent":break;default:(!(2<i.length)||i[0]!=="o"&&i[0]!=="O"||i[1]!=="n"&&i[1]!=="N")&&(i=pe.get(i)||i,En(e,i,r))}}function Hd(e,a,i,r,c,u){switch(i){case"style":wa(e,r,u);break;case"dangerouslySetInnerHTML":if(r!=null){if(typeof r!="object"||!("__html"in r))throw Error(o(61));if(i=r.__html,i!=null){if(c.children!=null)throw Error(o(60));e.innerHTML=i}}break;case"children":typeof r=="string"?$e(e,r):(typeof r=="number"||typeof r=="bigint")&&$e(e,""+r);break;case"onScroll":r!=null&&dt("scroll",e);break;case"onScrollEnd":r!=null&&dt("scrollend",e);break;case"onClick":r!=null&&(e.onclick=lo);break;case"suppressContentEditableWarning":case"suppressHydrationWarning":case"innerHTML":case"ref":break;case"innerText":case"textContent":break;default:if(!Fa.hasOwnProperty(i))e:{if(i[0]==="o"&&i[1]==="n"&&(c=i.endsWith("Capture"),a=i.slice(2,c?i.length-7:void 0),u=e[lt]||null,u=u!=null?u[i]:null,typeof u=="function"&&e.removeEventListener(a,u,c),typeof r=="function")){typeof u!="function"&&u!==null&&(i in e?e[i]=null:e.hasAttribute(i)&&e.removeAttribute(i)),e.addEventListener(a,r,c);break e}i in e?e[i]=r:r===!0?e.setAttribute(i,""):En(e,i,r)}}}function ja(e,a,i){switch(a){case"div":case"span":case"svg":case"path":case"a":case"g":case"p":case"li":break;case"img":dt("error",e),dt("load",e);var r=!1,c=!1,u;for(u in i)if(i.hasOwnProperty(u)){var y=i[u];if(y!=null)switch(u){case"src":r=!0;break;case"srcSet":c=!0;break;case"children":case"dangerouslySetInnerHTML":throw Error(o(137,a));default:Mt(e,a,u,y,i,null)}}c&&Mt(e,a,"srcSet",i.srcSet,i,null),r&&Mt(e,a,"src",i.src,i,null);return;case"input":dt("invalid",e);var w=u=y=c=null,k=null,Y=null;for(r in i)if(i.hasOwnProperty(r)){var le=i[r];if(le!=null)switch(r){case"name":c=le;break;case"type":y=le;break;case"checked":k=le;break;case"defaultChecked":Y=le;break;case"value":u=le;break;case"defaultValue":w=le;break;case"children":case"dangerouslySetInnerHTML":if(le!=null)throw Error(o(137,a));break;default:Mt(e,a,r,le,i,null)}}T(e,u,w,k,Y,y,c,!1),an(e);return;case"select":dt("invalid",e),r=y=u=null;for(c in i)if(i.hasOwnProperty(c)&&(w=i[c],w!=null))switch(c){case"value":u=w;break;case"defaultValue":y=w;break;case"multiple":r=w;default:Mt(e,a,c,w,i,null)}a=u,i=y,e.multiple=!!r,a!=null?de(e,!!r,a,!1):i!=null&&de(e,!!r,i,!0);return;case"textarea":dt("invalid",e),u=c=r=null;for(y in i)if(i.hasOwnProperty(y)&&(w=i[y],w!=null))switch(y){case"value":r=w;break;case"defaultValue":c=w;break;case"children":u=w;break;case"dangerouslySetInnerHTML":if(w!=null)throw Error(o(91));break;default:Mt(e,a,y,w,i,null)}Ze(e,r,c,u),an(e);return;case"option":for(k in i)if(i.hasOwnProperty(k)&&(r=i[k],r!=null))switch(k){case"selected":e.selected=r&&typeof r!="function"&&typeof r!="symbol";break;default:Mt(e,a,k,r,i,null)}return;case"dialog":dt("beforetoggle",e),dt("toggle",e),dt("cancel",e),dt("close",e);break;case"iframe":case"object":dt("load",e);break;case"video":case"audio":for(r=0;r<Er.length;r++)dt(Er[r],e);break;case"image":dt("error",e),dt("load",e);break;case"details":dt("toggle",e);break;case"embed":case"source":case"link":dt("error",e),dt("load",e);case"area":case"base":case"br":case"col":case"hr":case"keygen":case"meta":case"param":case"track":case"wbr":case"menuitem":for(Y in i)if(i.hasOwnProperty(Y)&&(r=i[Y],r!=null))switch(Y){case"children":case"dangerouslySetInnerHTML":throw Error(o(137,a));default:Mt(e,a,Y,r,i,null)}return;default:if(j(a)){for(le in i)i.hasOwnProperty(le)&&(r=i[le],r!==void 0&&Hd(e,a,le,r,i,void 0));return}}for(w in i)i.hasOwnProperty(w)&&(r=i[w],r!=null&&Mt(e,a,w,r,i,null))}function Ey(e,a,i,r){switch(a){case"div":case"span":case"svg":case"path":case"a":case"g":case"p":case"li":break;case"input":var c=null,u=null,y=null,w=null,k=null,Y=null,le=null;for(W in i){var ye=i[W];if(i.hasOwnProperty(W)&&ye!=null)switch(W){case"checked":break;case"value":break;case"defaultValue":k=ye;default:r.hasOwnProperty(W)||Mt(e,a,W,null,r,ye)}}for(var Z in r){var W=r[Z];if(ye=i[Z],r.hasOwnProperty(Z)&&(W!=null||ye!=null))switch(Z){case"type":u=W;break;case"name":c=W;break;case"checked":Y=W;break;case"defaultChecked":le=W;break;case"value":y=W;break;case"defaultValue":w=W;break;case"children":case"dangerouslySetInnerHTML":if(W!=null)throw Error(o(137,a));break;default:W!==ye&&Mt(e,a,Z,W,r,ye)}}ki(e,y,w,k,Y,le,u,c);return;case"select":W=y=w=Z=null;for(u in i)if(k=i[u],i.hasOwnProperty(u)&&k!=null)switch(u){case"value":break;case"multiple":W=k;default:r.hasOwnProperty(u)||Mt(e,a,u,null,r,k)}for(c in r)if(u=r[c],k=i[c],r.hasOwnProperty(c)&&(u!=null||k!=null))switch(c){case"value":Z=u;break;case"defaultValue":w=u;break;case"multiple":y=u;default:u!==k&&Mt(e,a,c,u,r,k)}a=w,i=y,r=W,Z!=null?de(e,!!i,Z,!1):!!r!=!!i&&(a!=null?de(e,!!i,a,!0):de(e,!!i,i?[]:"",!1));return;case"textarea":W=Z=null;for(w in i)if(c=i[w],i.hasOwnProperty(w)&&c!=null&&!r.hasOwnProperty(w))switch(w){case"value":break;case"children":break;default:Mt(e,a,w,null,r,c)}for(y in r)if(c=r[y],u=i[y],r.hasOwnProperty(y)&&(c!=null||u!=null))switch(y){case"value":Z=c;break;case"defaultValue":W=c;break;case"children":break;case"dangerouslySetInnerHTML":if(c!=null)throw Error(o(91));break;default:c!==u&&Mt(e,a,y,c,r,u)}ze(e,Z,W);return;case"option":for(var We in i)if(Z=i[We],i.hasOwnProperty(We)&&Z!=null&&!r.hasOwnProperty(We))switch(We){case"selected":e.selected=!1;break;default:Mt(e,a,We,null,r,Z)}for(k in r)if(Z=r[k],W=i[k],r.hasOwnProperty(k)&&Z!==W&&(Z!=null||W!=null))switch(k){case"selected":e.selected=Z&&typeof Z!="function"&&typeof Z!="symbol";break;default:Mt(e,a,k,Z,r,W)}return;case"img":case"link":case"area":case"base":case"br":case"col":case"embed":case"hr":case"keygen":case"meta":case"param":case"source":case"track":case"wbr":case"menuitem":for(var Pe in i)Z=i[Pe],i.hasOwnProperty(Pe)&&Z!=null&&!r.hasOwnProperty(Pe)&&Mt(e,a,Pe,null,r,Z);for(Y in r)if(Z=r[Y],W=i[Y],r.hasOwnProperty(Y)&&Z!==W&&(Z!=null||W!=null))switch(Y){case"children":case"dangerouslySetInnerHTML":if(Z!=null)throw Error(o(137,a));break;default:Mt(e,a,Y,Z,r,W)}return;default:if(j(a)){for(var Dt in i)Z=i[Dt],i.hasOwnProperty(Dt)&&Z!==void 0&&!r.hasOwnProperty(Dt)&&Hd(e,a,Dt,void 0,r,Z);for(le in r)Z=r[le],W=i[le],!r.hasOwnProperty(le)||Z===W||Z===void 0&&W===void 0||Hd(e,a,le,Z,r,W);return}}for(var B in i)Z=i[B],i.hasOwnProperty(B)&&Z!=null&&!r.hasOwnProperty(B)&&Mt(e,a,B,null,r,Z);for(ye in r)Z=r[ye],W=i[ye],!r.hasOwnProperty(ye)||Z===W||Z==null&&W==null||Mt(e,a,ye,Z,r,W)}var Id=null,$d=null;function oo(e){return e.nodeType===9?e:e.ownerDocument}function cp(e){switch(e){case"http://www.w3.org/2000/svg":return 1;case"http://www.w3.org/1998/Math/MathML":return 2;default:return 0}}function dp(e,a){if(e===0)switch(a){case"svg":return 1;case"math":return 2;default:return 0}return e===1&&a==="foreignObject"?0:e}function Fd(e,a){return e==="textarea"||e==="noscript"||typeof a.children=="string"||typeof a.children=="number"||typeof a.children=="bigint"||typeof a.dangerouslySetInnerHTML=="object"&&a.dangerouslySetInnerHTML!==null&&a.dangerouslySetInnerHTML.__html!=null}var Yd=null;function My(){var e=window.event;return e&&e.type==="popstate"?e===Yd?!1:(Yd=e,!0):(Yd=null,!1)}var up=typeof setTimeout=="function"?setTimeout:void 0,Dy=typeof clearTimeout=="function"?clearTimeout:void 0,fp=typeof Promise=="function"?Promise:void 0,Ry=typeof queueMicrotask=="function"?queueMicrotask:typeof fp<"u"?function(e){return fp.resolve(null).then(e).catch(Oy)}:up;function Oy(e){setTimeout(function(){throw e})}function ji(e){return e==="head"}function hp(e,a){var i=a,r=0,c=0;do{var u=i.nextSibling;if(e.removeChild(i),u&&u.nodeType===8)if(i=u.data,i==="/$"){if(0<r&&8>r){i=r;var y=e.ownerDocument;if(i&1&&Dr(y.documentElement),i&2&&Dr(y.body),i&4)for(i=y.head,Dr(i),y=i.firstChild;y;){var w=y.nextSibling,k=y.nodeName;y[fn]||k==="SCRIPT"||k==="STYLE"||k==="LINK"&&y.rel.toLowerCase()==="stylesheet"||i.removeChild(y),y=w}}if(c===0){e.removeChild(u),Ir(a);return}c--}else i==="$"||i==="$?"||i==="$!"?c++:r=i.charCodeAt(0)-48;else r=0;i=u}while(i);Ir(a)}function Gd(e){var a=e.firstChild;for(a&&a.nodeType===10&&(a=a.nextSibling);a;){var i=a;switch(a=a.nextSibling,i.nodeName){case"HTML":case"HEAD":case"BODY":Gd(i),$a(i);continue;case"SCRIPT":case"STYLE":continue;case"LINK":if(i.rel.toLowerCase()==="stylesheet")continue}e.removeChild(i)}}function Uy(e,a,i,r){for(;e.nodeType===1;){var c=i;if(e.nodeName.toLowerCase()!==a.toLowerCase()){if(!r&&(e.nodeName!=="INPUT"||e.type!=="hidden"))break}else if(r){if(!e[fn])switch(a){case"meta":if(!e.hasAttribute("itemprop"))break;return e;case"link":if(u=e.getAttribute("rel"),u==="stylesheet"&&e.hasAttribute("data-precedence"))break;if(u!==c.rel||e.getAttribute("href")!==(c.href==null||c.href===""?null:c.href)||e.getAttribute("crossorigin")!==(c.crossOrigin==null?null:c.crossOrigin)||e.getAttribute("title")!==(c.title==null?null:c.title))break;return e;case"style":if(e.hasAttribute("data-precedence"))break;return e;case"script":if(u=e.getAttribute("src"),(u!==(c.src==null?null:c.src)||e.getAttribute("type")!==(c.type==null?null:c.type)||e.getAttribute("crossorigin")!==(c.crossOrigin==null?null:c.crossOrigin))&&u&&e.hasAttribute("async")&&!e.hasAttribute("itemprop"))break;return e;default:return e}}else if(a==="input"&&e.type==="hidden"){var u=c.name==null?null:""+c.name;if(c.type==="hidden"&&e.getAttribute("name")===u)return e}else return e;if(e=xn(e.nextSibling),e===null)break}return null}function Ly(e,a,i){if(a==="")return null;for(;e.nodeType!==3;)if((e.nodeType!==1||e.nodeName!=="INPUT"||e.type!=="hidden")&&!i||(e=xn(e.nextSibling),e===null))return null;return e}function Vd(e){return e.data==="$!"||e.data==="$?"&&e.ownerDocument.readyState==="complete"}function By(e,a){var i=e.ownerDocument;if(e.data!=="$?"||i.readyState==="complete")a();else{var r=function(){a(),i.removeEventListener("DOMContentLoaded",r)};i.addEventListener("DOMContentLoaded",r),e._reactRetry=r}}function xn(e){for(;e!=null;e=e.nextSibling){var a=e.nodeType;if(a===1||a===3)break;if(a===8){if(a=e.data,a==="$"||a==="$!"||a==="$?"||a==="F!"||a==="F")break;if(a==="/$")return null}}return e}var Pd=null;function mp(e){e=e.previousSibling;for(var a=0;e;){if(e.nodeType===8){var i=e.data;if(i==="$"||i==="$!"||i==="$?"){if(a===0)return e;a--}else i==="/$"&&a++}e=e.previousSibling}return null}function pp(e,a,i){switch(a=oo(i),e){case"html":if(e=a.documentElement,!e)throw Error(o(452));return e;case"head":if(e=a.head,!e)throw Error(o(453));return e;case"body":if(e=a.body,!e)throw Error(o(454));return e;default:throw Error(o(451))}}function Dr(e){for(var a=e.attributes;a.length;)e.removeAttributeNode(a[0]);$a(e)}var dn=new Map,gp=new Set;function co(e){return typeof e.getRootNode=="function"?e.getRootNode():e.nodeType===9?e:e.ownerDocument}var Qn=H.d;H.d={f:qy,r:Hy,D:Iy,C:$y,L:Fy,m:Yy,X:Vy,S:Gy,M:Py};function qy(){var e=Qn.f(),a=eo();return e||a}function Hy(e){var a=tn(e);a!==null&&a.tag===5&&a.type==="form"?Uh(a):Qn.r(e)}var Ds=typeof document>"u"?null:document;function xp(e,a,i){var r=Ds;if(r&&typeof a=="string"&&a){var c=Gt(a);c='link[rel="'+e+'"][href="'+c+'"]',typeof i=="string"&&(c+='[crossorigin="'+i+'"]'),gp.has(c)||(gp.add(c),e={rel:e,crossOrigin:i,href:a},r.querySelector(c)===null&&(a=r.createElement("link"),ja(a,"link",e),gt(a),r.head.appendChild(a)))}}function Iy(e){Qn.D(e),xp("dns-prefetch",e,null)}function $y(e,a){Qn.C(e,a),xp("preconnect",e,a)}function Fy(e,a,i){Qn.L(e,a,i);var r=Ds;if(r&&e&&a){var c='link[rel="preload"][as="'+Gt(a)+'"]';a==="image"&&i&&i.imageSrcSet?(c+='[imagesrcset="'+Gt(i.imageSrcSet)+'"]',typeof i.imageSizes=="string"&&(c+='[imagesizes="'+Gt(i.imageSizes)+'"]')):c+='[href="'+Gt(e)+'"]';var u=c;switch(a){case"style":u=Rs(e);break;case"script":u=Os(e)}dn.has(u)||(e=x({rel:"preload",href:a==="image"&&i&&i.imageSrcSet?void 0:e,as:a},i),dn.set(u,e),r.querySelector(c)!==null||a==="style"&&r.querySelector(Rr(u))||a==="script"&&r.querySelector(Or(u))||(a=r.createElement("link"),ja(a,"link",e),gt(a),r.head.appendChild(a)))}}function Yy(e,a){Qn.m(e,a);var i=Ds;if(i&&e){var r=a&&typeof a.as=="string"?a.as:"script",c='link[rel="modulepreload"][as="'+Gt(r)+'"][href="'+Gt(e)+'"]',u=c;switch(r){case"audioworklet":case"paintworklet":case"serviceworker":case"sharedworker":case"worker":case"script":u=Os(e)}if(!dn.has(u)&&(e=x({rel:"modulepreload",href:e},a),dn.set(u,e),i.querySelector(c)===null)){switch(r){case"audioworklet":case"paintworklet":case"serviceworker":case"sharedworker":case"worker":case"script":if(i.querySelector(Or(u)))return}r=i.createElement("link"),ja(r,"link",e),gt(r),i.head.appendChild(r)}}}function Gy(e,a,i){Qn.S(e,a,i);var r=Ds;if(r&&e){var c=Aa(r).hoistableStyles,u=Rs(e);a=a||"default";var y=c.get(u);if(!y){var w={loading:0,preload:null};if(y=r.querySelector(Rr(u)))w.loading=5;else{e=x({rel:"stylesheet",href:e,"data-precedence":a},i),(i=dn.get(u))&&Xd(e,i);var k=y=r.createElement("link");gt(k),ja(k,"link",e),k._p=new Promise(function(Y,le){k.onload=Y,k.onerror=le}),k.addEventListener("load",function(){w.loading|=1}),k.addEventListener("error",function(){w.loading|=2}),w.loading|=4,uo(y,a,r)}y={type:"stylesheet",instance:y,count:1,state:w},c.set(u,y)}}}function Vy(e,a){Qn.X(e,a);var i=Ds;if(i&&e){var r=Aa(i).hoistableScripts,c=Os(e),u=r.get(c);u||(u=i.querySelector(Or(c)),u||(e=x({src:e,async:!0},a),(a=dn.get(c))&&Zd(e,a),u=i.createElement("script"),gt(u),ja(u,"link",e),i.head.appendChild(u)),u={type:"script",instance:u,count:1,state:null},r.set(c,u))}}function Py(e,a){Qn.M(e,a);var i=Ds;if(i&&e){var r=Aa(i).hoistableScripts,c=Os(e),u=r.get(c);u||(u=i.querySelector(Or(c)),u||(e=x({src:e,async:!0,type:"module"},a),(a=dn.get(c))&&Zd(e,a),u=i.createElement("script"),gt(u),ja(u,"link",e),i.head.appendChild(u)),u={type:"script",instance:u,count:1,state:null},r.set(c,u))}}function yp(e,a,i,r){var c=(c=ue.current)?co(c):null;if(!c)throw Error(o(446));switch(e){case"meta":case"title":return null;case"style":return typeof i.precedence=="string"&&typeof i.href=="string"?(a=Rs(i.href),i=Aa(c).hoistableStyles,r=i.get(a),r||(r={type:"style",instance:null,count:0,state:null},i.set(a,r)),r):{type:"void",instance:null,count:0,state:null};case"link":if(i.rel==="stylesheet"&&typeof i.href=="string"&&typeof i.precedence=="string"){e=Rs(i.href);var u=Aa(c).hoistableStyles,y=u.get(e);if(y||(c=c.ownerDocument||c,y={type:"stylesheet",instance:null,count:0,state:{loading:0,preload:null}},u.set(e,y),(u=c.querySelector(Rr(e)))&&!u._p&&(y.instance=u,y.state.loading=5),dn.has(e)||(i={rel:"preload",as:"style",href:i.href,crossOrigin:i.crossOrigin,integrity:i.integrity,media:i.media,hrefLang:i.hrefLang,referrerPolicy:i.referrerPolicy},dn.set(e,i),u||Xy(c,e,i,y.state))),a&&r===null)throw Error(o(528,""));return y}if(a&&r!==null)throw Error(o(529,""));return null;case"script":return a=i.async,i=i.src,typeof i=="string"&&a&&typeof a!="function"&&typeof a!="symbol"?(a=Os(i),i=Aa(c).hoistableScripts,r=i.get(a),r||(r={type:"script",instance:null,count:0,state:null},i.set(a,r)),r):{type:"void",instance:null,count:0,state:null};default:throw Error(o(444,e))}}function Rs(e){return'href="'+Gt(e)+'"'}function Rr(e){return'link[rel="stylesheet"]['+e+"]"}function vp(e){return x({},e,{"data-precedence":e.precedence,precedence:null})}function Xy(e,a,i,r){e.querySelector('link[rel="preload"][as="style"]['+a+"]")?r.loading=1:(a=e.createElement("link"),r.preload=a,a.addEventListener("load",function(){return r.loading|=1}),a.addEventListener("error",function(){return r.loading|=2}),ja(a,"link",i),gt(a),e.head.appendChild(a))}function Os(e){return'[src="'+Gt(e)+'"]'}function Or(e){return"script[async]"+e}function bp(e,a,i){if(a.count++,a.instance===null)switch(a.type){case"style":var r=e.querySelector('style[data-href~="'+Gt(i.href)+'"]');if(r)return a.instance=r,gt(r),r;var c=x({},i,{"data-href":i.href,"data-precedence":i.precedence,href:null,precedence:null});return r=(e.ownerDocument||e).createElement("style"),gt(r),ja(r,"style",c),uo(r,i.precedence,e),a.instance=r;case"stylesheet":c=Rs(i.href);var u=e.querySelector(Rr(c));if(u)return a.state.loading|=4,a.instance=u,gt(u),u;r=vp(i),(c=dn.get(c))&&Xd(r,c),u=(e.ownerDocument||e).createElement("link"),gt(u);var y=u;return y._p=new Promise(function(w,k){y.onload=w,y.onerror=k}),ja(u,"link",r),a.state.loading|=4,uo(u,i.precedence,e),a.instance=u;case"script":return u=Os(i.src),(c=e.querySelector(Or(u)))?(a.instance=c,gt(c),c):(r=i,(c=dn.get(u))&&(r=x({},i),Zd(r,c)),e=e.ownerDocument||e,c=e.createElement("script"),gt(c),ja(c,"link",r),e.head.appendChild(c),a.instance=c);case"void":return null;default:throw Error(o(443,a.type))}else a.type==="stylesheet"&&(a.state.loading&4)===0&&(r=a.instance,a.state.loading|=4,uo(r,i.precedence,e));return a.instance}function uo(e,a,i){for(var r=i.querySelectorAll('link[rel="stylesheet"][data-precedence],style[data-precedence]'),c=r.length?r[r.length-1]:null,u=c,y=0;y<r.length;y++){var w=r[y];if(w.dataset.precedence===a)u=w;else if(u!==c)break}u?u.parentNode.insertBefore(e,u.nextSibling):(a=i.nodeType===9?i.head:i,a.insertBefore(e,a.firstChild))}function Xd(e,a){e.crossOrigin==null&&(e.crossOrigin=a.crossOrigin),e.referrerPolicy==null&&(e.referrerPolicy=a.referrerPolicy),e.title==null&&(e.title=a.title)}function Zd(e,a){e.crossOrigin==null&&(e.crossOrigin=a.crossOrigin),e.referrerPolicy==null&&(e.referrerPolicy=a.referrerPolicy),e.integrity==null&&(e.integrity=a.integrity)}var fo=null;function jp(e,a,i){if(fo===null){var r=new Map,c=fo=new Map;c.set(i,r)}else c=fo,r=c.get(i),r||(r=new Map,c.set(i,r));if(r.has(e))return r;for(r.set(e,null),i=i.getElementsByTagName(e),c=0;c<i.length;c++){var u=i[c];if(!(u[fn]||u[Oe]||e==="link"&&u.getAttribute("rel")==="stylesheet")&&u.namespaceURI!=="http://www.w3.org/2000/svg"){var y=u.getAttribute(a)||"";y=e+y;var w=r.get(y);w?w.push(u):r.set(y,[u])}}return r}function wp(e,a,i){e=e.ownerDocument||e,e.head.insertBefore(i,a==="title"?e.querySelector("head > title"):null)}function Zy(e,a,i){if(i===1||a.itemProp!=null)return!1;switch(e){case"meta":case"title":return!0;case"style":if(typeof a.precedence!="string"||typeof a.href!="string"||a.href==="")break;return!0;case"link":if(typeof a.rel!="string"||typeof a.href!="string"||a.href===""||a.onLoad||a.onError)break;switch(a.rel){case"stylesheet":return e=a.disabled,typeof a.precedence=="string"&&e==null;default:return!0}case"script":if(a.async&&typeof a.async!="function"&&typeof a.async!="symbol"&&!a.onLoad&&!a.onError&&a.src&&typeof a.src=="string")return!0}return!1}function Np(e){return!(e.type==="stylesheet"&&(e.state.loading&3)===0)}var Ur=null;function Qy(){}function Jy(e,a,i){if(Ur===null)throw Error(o(475));var r=Ur;if(a.type==="stylesheet"&&(typeof i.media!="string"||matchMedia(i.media).matches!==!1)&&(a.state.loading&4)===0){if(a.instance===null){var c=Rs(i.href),u=e.querySelector(Rr(c));if(u){e=u._p,e!==null&&typeof e=="object"&&typeof e.then=="function"&&(r.count++,r=ho.bind(r),e.then(r,r)),a.state.loading|=4,a.instance=u,gt(u);return}u=e.ownerDocument||e,i=vp(i),(c=dn.get(c))&&Xd(i,c),u=u.createElement("link"),gt(u);var y=u;y._p=new Promise(function(w,k){y.onload=w,y.onerror=k}),ja(u,"link",i),a.instance=u}r.stylesheets===null&&(r.stylesheets=new Map),r.stylesheets.set(a,e),(e=a.state.preload)&&(a.state.loading&3)===0&&(r.count++,a=ho.bind(r),e.addEventListener("load",a),e.addEventListener("error",a))}}function Wy(){if(Ur===null)throw Error(o(475));var e=Ur;return e.stylesheets&&e.count===0&&Qd(e,e.stylesheets),0<e.count?function(a){var i=setTimeout(function(){if(e.stylesheets&&Qd(e,e.stylesheets),e.unsuspend){var r=e.unsuspend;e.unsuspend=null,r()}},6e4);return e.unsuspend=a,function(){e.unsuspend=null,clearTimeout(i)}}:null}function ho(){if(this.count--,this.count===0){if(this.stylesheets)Qd(this,this.stylesheets);else if(this.unsuspend){var e=this.unsuspend;this.unsuspend=null,e()}}}var mo=null;function Qd(e,a){e.stylesheets=null,e.unsuspend!==null&&(e.count++,mo=new Map,a.forEach(Ky,e),mo=null,ho.call(e))}function Ky(e,a){if(!(a.state.loading&4)){var i=mo.get(e);if(i)var r=i.get(null);else{i=new Map,mo.set(e,i);for(var c=e.querySelectorAll("link[data-precedence],style[data-precedence]"),u=0;u<c.length;u++){var y=c[u];(y.nodeName==="LINK"||y.getAttribute("media")!=="not all")&&(i.set(y.dataset.precedence,y),r=y)}r&&i.set(null,r)}c=a.instance,y=c.getAttribute("data-precedence"),u=i.get(y)||r,u===r&&i.set(null,c),i.set(y,c),this.count++,r=ho.bind(this),c.addEventListener("load",r),c.addEventListener("error",r),u?u.parentNode.insertBefore(c,u.nextSibling):(e=e.nodeType===9?e.head:e,e.insertBefore(c,e.firstChild)),a.state.loading|=4}}var Lr={$$typeof:P,Provider:null,Consumer:null,_currentValue:F,_currentValue2:F,_threadCount:0};function ev(e,a,i,r,c,u,y,w){this.tag=1,this.containerInfo=e,this.pingCache=this.current=this.pendingChildren=null,this.timeoutHandle=-1,this.callbackNode=this.next=this.pendingContext=this.context=this.cancelPendingCommit=null,this.callbackPriority=0,this.expirationTimes=Ee(-1),this.entangledLanes=this.shellSuspendCounter=this.errorRecoveryDisabledLanes=this.expiredLanes=this.warmLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0,this.entanglements=Ee(0),this.hiddenUpdates=Ee(null),this.identifierPrefix=r,this.onUncaughtError=c,this.onCaughtError=u,this.onRecoverableError=y,this.pooledCache=null,this.pooledCacheLanes=0,this.formState=w,this.incompleteTransitions=new Map}function _p(e,a,i,r,c,u,y,w,k,Y,le,ye){return e=new ev(e,a,i,y,w,k,Y,ye),a=1,u===!0&&(a|=24),u=Xa(3,null,null,a),e.current=u,u.stateNode=e,a=Ec(),a.refCount++,e.pooledCache=a,a.refCount++,u.memoizedState={element:r,isDehydrated:i,cache:a},Oc(u),e}function Sp(e){return e?(e=fs,e):fs}function Tp(e,a,i,r,c,u){c=Sp(c),r.context===null?r.context=c:r.pendingContext=c,r=oi(a),r.payload={element:i},u=u===void 0?null:u,u!==null&&(r.callback=u),i=ci(e,r,a),i!==null&&(Ka(i,e,a),hr(i,e,a))}function Cp(e,a){if(e=e.memoizedState,e!==null&&e.dehydrated!==null){var i=e.retryLane;e.retryLane=i!==0&&i<a?i:a}}function Jd(e,a){Cp(e,a),(e=e.alternate)&&Cp(e,a)}function Ap(e){if(e.tag===13){var a=us(e,67108864);a!==null&&Ka(a,e,67108864),Jd(e,67108864)}}var po=!0;function tv(e,a,i,r){var c=S.T;S.T=null;var u=H.p;try{H.p=2,Wd(e,a,i,r)}finally{H.p=u,S.T=c}}function av(e,a,i,r){var c=S.T;S.T=null;var u=H.p;try{H.p=8,Wd(e,a,i,r)}finally{H.p=u,S.T=c}}function Wd(e,a,i,r){if(po){var c=Kd(r);if(c===null)qd(e,a,r,go,i),kp(e,r);else if(iv(c,e,a,i,r))r.stopPropagation();else if(kp(e,r),a&4&&-1<nv.indexOf(e)){for(;c!==null;){var u=tn(c);if(u!==null)switch(u.tag){case 3:if(u=u.stateNode,u.current.memoizedState.isDehydrated){var y=Ce(u.pendingLanes);if(y!==0){var w=u;for(w.pendingLanes|=2,w.entangledLanes|=2;y;){var k=1<<31-ft(y);w.entanglements[1]|=k,y&=~k}Cn(u),(At&6)===0&&(Wl=Ke()+500,kr(0))}}break;case 13:w=us(u,2),w!==null&&Ka(w,u,2),eo(),Jd(u,2)}if(u=Kd(r),u===null&&qd(e,a,r,go,i),u===c)break;c=u}c!==null&&r.stopPropagation()}else qd(e,a,r,null,i)}}function Kd(e){return e=Ge(e),eu(e)}var go=null;function eu(e){if(go=null,e=Da(e),e!==null){var a=f(e);if(a===null)e=null;else{var i=a.tag;if(i===13){if(e=m(a),e!==null)return e;e=null}else if(i===3){if(a.stateNode.current.memoizedState.isDehydrated)return a.tag===3?a.stateNode.containerInfo:null;e=null}else a!==e&&(e=null)}}return go=e,null}function zp(e){switch(e){case"beforetoggle":case"cancel":case"click":case"close":case"contextmenu":case"copy":case"cut":case"auxclick":case"dblclick":case"dragend":case"dragstart":case"drop":case"focusin":case"focusout":case"input":case"invalid":case"keydown":case"keypress":case"keyup":case"mousedown":case"mouseup":case"paste":case"pause":case"play":case"pointercancel":case"pointerdown":case"pointerup":case"ratechange":case"reset":case"resize":case"seeked":case"submit":case"toggle":case"touchcancel":case"touchend":case"touchstart":case"volumechange":case"change":case"selectionchange":case"textInput":case"compositionstart":case"compositionend":case"compositionupdate":case"beforeblur":case"afterblur":case"beforeinput":case"blur":case"fullscreenchange":case"focus":case"hashchange":case"popstate":case"select":case"selectstart":return 2;case"drag":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"mousemove":case"mouseout":case"mouseover":case"pointermove":case"pointerout":case"pointerover":case"scroll":case"touchmove":case"wheel":case"mouseenter":case"mouseleave":case"pointerenter":case"pointerleave":return 8;case"message":switch(ta()){case _t:return 2;case Tt:return 8;case Ft:case Zt:return 32;case ae:return 268435456;default:return 32}default:return 32}}var tu=!1,wi=null,Ni=null,_i=null,Br=new Map,qr=new Map,Si=[],nv="mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset".split(" ");function kp(e,a){switch(e){case"focusin":case"focusout":wi=null;break;case"dragenter":case"dragleave":Ni=null;break;case"mouseover":case"mouseout":_i=null;break;case"pointerover":case"pointerout":Br.delete(a.pointerId);break;case"gotpointercapture":case"lostpointercapture":qr.delete(a.pointerId)}}function Hr(e,a,i,r,c,u){return e===null||e.nativeEvent!==u?(e={blockedOn:a,domEventName:i,eventSystemFlags:r,nativeEvent:u,targetContainers:[c]},a!==null&&(a=tn(a),a!==null&&Ap(a)),e):(e.eventSystemFlags|=r,a=e.targetContainers,c!==null&&a.indexOf(c)===-1&&a.push(c),e)}function iv(e,a,i,r,c){switch(a){case"focusin":return wi=Hr(wi,e,a,i,r,c),!0;case"dragenter":return Ni=Hr(Ni,e,a,i,r,c),!0;case"mouseover":return _i=Hr(_i,e,a,i,r,c),!0;case"pointerover":var u=c.pointerId;return Br.set(u,Hr(Br.get(u)||null,e,a,i,r,c)),!0;case"gotpointercapture":return u=c.pointerId,qr.set(u,Hr(qr.get(u)||null,e,a,i,r,c)),!0}return!1}function Ep(e){var a=Da(e.target);if(a!==null){var i=f(a);if(i!==null){if(a=i.tag,a===13){if(a=m(i),a!==null){e.blockedOn=a,Bt(e.priority,function(){if(i.tag===13){var r=Wa();r=wt(r);var c=us(i,r);c!==null&&Ka(c,i,r),Jd(i,r)}});return}}else if(a===3&&i.stateNode.current.memoizedState.isDehydrated){e.blockedOn=i.tag===3?i.stateNode.containerInfo:null;return}}}e.blockedOn=null}function xo(e){if(e.blockedOn!==null)return!1;for(var a=e.targetContainers;0<a.length;){var i=Kd(e.nativeEvent);if(i===null){i=e.nativeEvent;var r=new i.constructor(i.type,i);Je=r,i.target.dispatchEvent(r),Je=null}else return a=tn(i),a!==null&&Ap(a),e.blockedOn=i,!1;a.shift()}return!0}function Mp(e,a,i){xo(e)&&i.delete(a)}function sv(){tu=!1,wi!==null&&xo(wi)&&(wi=null),Ni!==null&&xo(Ni)&&(Ni=null),_i!==null&&xo(_i)&&(_i=null),Br.forEach(Mp),qr.forEach(Mp)}function yo(e,a){e.blockedOn===a&&(e.blockedOn=null,tu||(tu=!0,n.unstable_scheduleCallback(n.unstable_NormalPriority,sv)))}var vo=null;function Dp(e){vo!==e&&(vo=e,n.unstable_scheduleCallback(n.unstable_NormalPriority,function(){vo===e&&(vo=null);for(var a=0;a<e.length;a+=3){var i=e[a],r=e[a+1],c=e[a+2];if(typeof r!="function"){if(eu(r||i)===null)continue;break}var u=tn(i);u!==null&&(e.splice(a,3),a-=3,ed(u,{pending:!0,data:c,method:i.method,action:r},r,c))}}))}function Ir(e){function a(k){return yo(k,e)}wi!==null&&yo(wi,e),Ni!==null&&yo(Ni,e),_i!==null&&yo(_i,e),Br.forEach(a),qr.forEach(a);for(var i=0;i<Si.length;i++){var r=Si[i];r.blockedOn===e&&(r.blockedOn=null)}for(;0<Si.length&&(i=Si[0],i.blockedOn===null);)Ep(i),i.blockedOn===null&&Si.shift();if(i=(e.ownerDocument||e).$$reactFormReplay,i!=null)for(r=0;r<i.length;r+=3){var c=i[r],u=i[r+1],y=c[lt]||null;if(typeof u=="function")y||Dp(i);else if(y){var w=null;if(u&&u.hasAttribute("formAction")){if(c=u,y=u[lt]||null)w=y.formAction;else if(eu(c)!==null)continue}else w=y.action;typeof w=="function"?i[r+1]=w:(i.splice(r,3),r-=3),Dp(i)}}}function au(e){this._internalRoot=e}bo.prototype.render=au.prototype.render=function(e){var a=this._internalRoot;if(a===null)throw Error(o(409));var i=a.current,r=Wa();Tp(i,r,e,a,null,null)},bo.prototype.unmount=au.prototype.unmount=function(){var e=this._internalRoot;if(e!==null){this._internalRoot=null;var a=e.containerInfo;Tp(e.current,2,null,e,null,null),eo(),a[Ut]=null}};function bo(e){this._internalRoot=e}bo.prototype.unstable_scheduleHydration=function(e){if(e){var a=Ct();e={blockedOn:null,target:e,priority:a};for(var i=0;i<Si.length&&a!==0&&a<Si[i].priority;i++);Si.splice(i,0,e),i===0&&Ep(e)}};var Rp=s.version;if(Rp!=="19.1.1")throw Error(o(527,Rp,"19.1.1"));H.findDOMNode=function(e){var a=e._reactInternals;if(a===void 0)throw typeof e.render=="function"?Error(o(188)):(e=Object.keys(e).join(","),Error(o(268,e)));return e=g(a),e=e!==null?h(e):null,e=e===null?null:e.stateNode,e};var rv={bundleType:0,version:"19.1.1",rendererPackageName:"react-dom",currentDispatcherRef:S,reconcilerVersion:"19.1.1"};if(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<"u"){var jo=__REACT_DEVTOOLS_GLOBAL_HOOK__;if(!jo.isDisabled&&jo.supportsFiber)try{ke=jo.inject(rv),Be=jo}catch{}}return Fr.createRoot=function(e,a){if(!d(e))throw Error(o(299));var i=!1,r="",c=Qh,u=Jh,y=Wh,w=null;return a!=null&&(a.unstable_strictMode===!0&&(i=!0),a.identifierPrefix!==void 0&&(r=a.identifierPrefix),a.onUncaughtError!==void 0&&(c=a.onUncaughtError),a.onCaughtError!==void 0&&(u=a.onCaughtError),a.onRecoverableError!==void 0&&(y=a.onRecoverableError),a.unstable_transitionCallbacks!==void 0&&(w=a.unstable_transitionCallbacks)),a=_p(e,1,!1,null,null,i,r,c,u,y,w,null),e[Ut]=a.current,Bd(e),new au(a)},Fr.hydrateRoot=function(e,a,i){if(!d(e))throw Error(o(299));var r=!1,c="",u=Qh,y=Jh,w=Wh,k=null,Y=null;return i!=null&&(i.unstable_strictMode===!0&&(r=!0),i.identifierPrefix!==void 0&&(c=i.identifierPrefix),i.onUncaughtError!==void 0&&(u=i.onUncaughtError),i.onCaughtError!==void 0&&(y=i.onCaughtError),i.onRecoverableError!==void 0&&(w=i.onRecoverableError),i.unstable_transitionCallbacks!==void 0&&(k=i.unstable_transitionCallbacks),i.formState!==void 0&&(Y=i.formState)),a=_p(e,1,!0,a,i??null,r,c,u,y,w,k,Y),a.context=Sp(null),i=a.current,r=Wa(),r=wt(r),c=oi(r),c.callback=null,ci(i,c,r),i=r,a.current.lanes=i,R(a,i),Cn(a),e[Ut]=a.current,Bd(e),new bo(a)},Fr.version="19.1.1",Fr}var Yp;function vv(){if(Yp)return ru.exports;Yp=1;function n(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(n)}catch(s){console.error(s)}}return n(),ru.exports=yv(),ru.exports}var bv=vv();const jv=Jg(bv);Wg();/**
 * @remix-run/router v1.23.0
 *
 * Copyright (c) Remix Software Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE.md file in the root directory of this source tree.
 *
 * @license MIT
 */function Kr(){return Kr=Object.assign?Object.assign.bind():function(n){for(var s=1;s<arguments.length;s++){var l=arguments[s];for(var o in l)Object.prototype.hasOwnProperty.call(l,o)&&(n[o]=l[o])}return n},Kr.apply(this,arguments)}var Ci;(function(n){n.Pop="POP",n.Push="PUSH",n.Replace="REPLACE"})(Ci||(Ci={}));const Gp="popstate";function wv(n){n===void 0&&(n={});function s(o,d){let{pathname:f,search:m,hash:p}=o.location;return _u("",{pathname:f,search:m,hash:p},d.state&&d.state.usr||null,d.state&&d.state.key||"default")}function l(o,d){return typeof d=="string"?d:ex(d)}return _v(s,l,null,n)}function ia(n,s){if(n===!1||n===null||typeof n>"u")throw new Error(s)}function Kg(n,s){if(!n){typeof console<"u"&&console.warn(s);try{throw new Error(s)}catch{}}}function Nv(){return Math.random().toString(36).substr(2,8)}function Vp(n,s){return{usr:n.state,key:n.key,idx:s}}function _u(n,s,l,o){return l===void 0&&(l=null),Kr({pathname:typeof n=="string"?n:n.pathname,search:"",hash:""},typeof s=="string"?Zs(s):s,{state:l,key:s&&s.key||o||Nv()})}function ex(n){let{pathname:s="/",search:l="",hash:o=""}=n;return l&&l!=="?"&&(s+=l.charAt(0)==="?"?l:"?"+l),o&&o!=="#"&&(s+=o.charAt(0)==="#"?o:"#"+o),s}function Zs(n){let s={};if(n){let l=n.indexOf("#");l>=0&&(s.hash=n.substr(l),n=n.substr(0,l));let o=n.indexOf("?");o>=0&&(s.search=n.substr(o),n=n.substr(0,o)),n&&(s.pathname=n)}return s}function _v(n,s,l,o){o===void 0&&(o={});let{window:d=document.defaultView,v5Compat:f=!1}=o,m=d.history,p=Ci.Pop,g=null,h=x();h==null&&(h=0,m.replaceState(Kr({},m.state,{idx:h}),""));function x(){return(m.state||{idx:null}).idx}function v(){p=Ci.Pop;let A=x(),L=A==null?null:A-h;h=A,g&&g({action:p,location:E.location,delta:L})}function b(A,L){p=Ci.Push;let q=_u(E.location,A,L);h=x()+1;let P=Vp(q,h),M=E.createHref(q);try{m.pushState(P,"",M)}catch(X){if(X instanceof DOMException&&X.name==="DataCloneError")throw X;d.location.assign(M)}f&&g&&g({action:p,location:E.location,delta:1})}function _(A,L){p=Ci.Replace;let q=_u(E.location,A,L);h=x();let P=Vp(q,h),M=E.createHref(q);m.replaceState(P,"",M),f&&g&&g({action:p,location:E.location,delta:0})}function C(A){let L=d.location.origin!=="null"?d.location.origin:d.location.href,q=typeof A=="string"?A:ex(A);return q=q.replace(/ $/,"%20"),ia(L,"No window.location.(origin|href) available to create URL for href: "+q),new URL(q,L)}let E={get action(){return p},get location(){return n(d,m)},listen(A){if(g)throw new Error("A history only accepts one active listener");return d.addEventListener(Gp,v),g=A,()=>{d.removeEventListener(Gp,v),g=null}},createHref(A){return s(d,A)},createURL:C,encodeLocation(A){let L=C(A);return{pathname:L.pathname,search:L.search,hash:L.hash}},push:b,replace:_,go(A){return m.go(A)}};return E}var Pp;(function(n){n.data="data",n.deferred="deferred",n.redirect="redirect",n.error="error"})(Pp||(Pp={}));function Sv(n,s,l){return l===void 0&&(l="/"),Tv(n,s,l)}function Tv(n,s,l,o){let d=typeof s=="string"?Zs(s):s,f=nx(d.pathname||"/",l);if(f==null)return null;let m=tx(n);Cv(m);let p=null;for(let g=0;p==null&&g<m.length;++g){let h=qv(f);p=Uv(m[g],h)}return p}function tx(n,s,l,o){s===void 0&&(s=[]),l===void 0&&(l=[]),o===void 0&&(o="");let d=(f,m,p)=>{let g={relativePath:p===void 0?f.path||"":p,caseSensitive:f.caseSensitive===!0,childrenIndex:m,route:f};g.relativePath.startsWith("/")&&(ia(g.relativePath.startsWith(o),'Absolute route path "'+g.relativePath+'" nested under path '+('"'+o+'" is not valid. An absolute child route path ')+"must start with the combined path of all its parent routes."),g.relativePath=g.relativePath.slice(o.length));let h=Qi([o,g.relativePath]),x=l.concat(g);f.children&&f.children.length>0&&(ia(f.index!==!0,"Index routes must not have child routes. Please remove "+('all child routes from route path "'+h+'".')),tx(f.children,s,x,h)),!(f.path==null&&!f.index)&&s.push({path:h,score:Rv(h,f.index),routesMeta:x})};return n.forEach((f,m)=>{var p;if(f.path===""||!((p=f.path)!=null&&p.includes("?")))d(f,m);else for(let g of ax(f.path))d(f,m,g)}),s}function ax(n){let s=n.split("/");if(s.length===0)return[];let[l,...o]=s,d=l.endsWith("?"),f=l.replace(/\?$/,"");if(o.length===0)return d?[f,""]:[f];let m=ax(o.join("/")),p=[];return p.push(...m.map(g=>g===""?f:[f,g].join("/"))),d&&p.push(...m),p.map(g=>n.startsWith("/")&&g===""?"/":g)}function Cv(n){n.sort((s,l)=>s.score!==l.score?l.score-s.score:Ov(s.routesMeta.map(o=>o.childrenIndex),l.routesMeta.map(o=>o.childrenIndex)))}const Av=/^:[\w-]+$/,zv=3,kv=2,Ev=1,Mv=10,Dv=-2,Xp=n=>n==="*";function Rv(n,s){let l=n.split("/"),o=l.length;return l.some(Xp)&&(o+=Dv),s&&(o+=kv),l.filter(d=>!Xp(d)).reduce((d,f)=>d+(Av.test(f)?zv:f===""?Ev:Mv),o)}function Ov(n,s){return n.length===s.length&&n.slice(0,-1).every((o,d)=>o===s[d])?n[n.length-1]-s[s.length-1]:0}function Uv(n,s,l){let{routesMeta:o}=n,d={},f="/",m=[];for(let p=0;p<o.length;++p){let g=o[p],h=p===o.length-1,x=f==="/"?s:s.slice(f.length)||"/",v=Lv({path:g.relativePath,caseSensitive:g.caseSensitive,end:h},x),b=g.route;if(!v)return null;Object.assign(d,v.params),m.push({params:d,pathname:Qi([f,v.pathname]),pathnameBase:Fv(Qi([f,v.pathnameBase])),route:b}),v.pathnameBase!=="/"&&(f=Qi([f,v.pathnameBase]))}return m}function Lv(n,s){typeof n=="string"&&(n={path:n,caseSensitive:!1,end:!0});let[l,o]=Bv(n.path,n.caseSensitive,n.end),d=s.match(l);if(!d)return null;let f=d[0],m=f.replace(/(.)\/+$/,"$1"),p=d.slice(1);return{params:o.reduce((h,x,v)=>{let{paramName:b,isOptional:_}=x;if(b==="*"){let E=p[v]||"";m=f.slice(0,f.length-E.length).replace(/(.)\/+$/,"$1")}const C=p[v];return _&&!C?h[b]=void 0:h[b]=(C||"").replace(/%2F/g,"/"),h},{}),pathname:f,pathnameBase:m,pattern:n}}function Bv(n,s,l){s===void 0&&(s=!1),l===void 0&&(l=!0),Kg(n==="*"||!n.endsWith("*")||n.endsWith("/*"),'Route path "'+n+'" will be treated as if it were '+('"'+n.replace(/\*$/,"/*")+'" because the `*` character must ')+"always follow a `/` in the pattern. To get rid of this warning, "+('please change the route path to "'+n.replace(/\*$/,"/*")+'".'));let o=[],d="^"+n.replace(/\/*\*?$/,"").replace(/^\/*/,"/").replace(/[\\.*+^${}|()[\]]/g,"\\$&").replace(/\/:([\w-]+)(\?)?/g,(m,p,g)=>(o.push({paramName:p,isOptional:g!=null}),g?"/?([^\\/]+)?":"/([^\\/]+)"));return n.endsWith("*")?(o.push({paramName:"*"}),d+=n==="*"||n==="/*"?"(.*)$":"(?:\\/(.+)|\\/*)$"):l?d+="\\/*$":n!==""&&n!=="/"&&(d+="(?:(?=\\/|$))"),[new RegExp(d,s?void 0:"i"),o]}function qv(n){try{return n.split("/").map(s=>decodeURIComponent(s).replace(/\//g,"%2F")).join("/")}catch(s){return Kg(!1,'The URL path "'+n+'" could not be decoded because it is is a malformed URL segment. This is probably due to a bad percent '+("encoding ("+s+").")),n}}function nx(n,s){if(s==="/")return n;if(!n.toLowerCase().startsWith(s.toLowerCase()))return null;let l=s.endsWith("/")?s.length-1:s.length,o=n.charAt(l);return o&&o!=="/"?null:n.slice(l)||"/"}function Hv(n,s){s===void 0&&(s="/");let{pathname:l,search:o="",hash:d=""}=typeof n=="string"?Zs(n):n;return{pathname:l?l.startsWith("/")?l:Iv(l,s):s,search:Yv(o),hash:Gv(d)}}function Iv(n,s){let l=s.replace(/\/+$/,"").split("/");return n.split("/").forEach(d=>{d===".."?l.length>1&&l.pop():d!=="."&&l.push(d)}),l.length>1?l.join("/"):"/"}function du(n,s,l,o){return"Cannot include a '"+n+"' character in a manually specified "+("`to."+s+"` field ["+JSON.stringify(o)+"].  Please separate it out to the ")+("`to."+l+"` field. Alternatively you may provide the full path as ")+'a string in <Link to="..."> and the router will parse it for you.'}function $v(n){return n.filter((s,l)=>l===0||s.route.path&&s.route.path.length>0)}function ix(n,s){let l=$v(n);return s?l.map((o,d)=>d===l.length-1?o.pathname:o.pathnameBase):l.map(o=>o.pathnameBase)}function sx(n,s,l,o){o===void 0&&(o=!1);let d;typeof n=="string"?d=Zs(n):(d=Kr({},n),ia(!d.pathname||!d.pathname.includes("?"),du("?","pathname","search",d)),ia(!d.pathname||!d.pathname.includes("#"),du("#","pathname","hash",d)),ia(!d.search||!d.search.includes("#"),du("#","search","hash",d)));let f=n===""||d.pathname==="",m=f?"/":d.pathname,p;if(m==null)p=l;else{let v=s.length-1;if(!o&&m.startsWith("..")){let b=m.split("/");for(;b[0]==="..";)b.shift(),v-=1;d.pathname=b.join("/")}p=v>=0?s[v]:"/"}let g=Hv(d,p),h=m&&m!=="/"&&m.endsWith("/"),x=(f||m===".")&&l.endsWith("/");return!g.pathname.endsWith("/")&&(h||x)&&(g.pathname+="/"),g}const Qi=n=>n.join("/").replace(/\/\/+/g,"/"),Fv=n=>n.replace(/\/+$/,"").replace(/^\/*/,"/"),Yv=n=>!n||n==="?"?"":n.startsWith("?")?n:"?"+n,Gv=n=>!n||n==="#"?"":n.startsWith("#")?n:"#"+n;function Vv(n){return n!=null&&typeof n.status=="number"&&typeof n.statusText=="string"&&typeof n.internal=="boolean"&&"data"in n}const rx=["post","put","patch","delete"];new Set(rx);const Pv=["get",...rx];new Set(Pv);/**
 * React Router v6.30.1
 *
 * Copyright (c) Remix Software Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE.md file in the root directory of this source tree.
 *
 * @license MIT
 */function el(){return el=Object.assign?Object.assign.bind():function(n){for(var s=1;s<arguments.length;s++){var l=arguments[s];for(var o in l)Object.prototype.hasOwnProperty.call(l,o)&&(n[o]=l[o])}return n},el.apply(this,arguments)}const Iu=N.createContext(null),Xv=N.createContext(null),dl=N.createContext(null),Ko=N.createContext(null),ts=N.createContext({outlet:null,matches:[],isDataRoute:!1}),lx=N.createContext(null);function ul(){return N.useContext(Ko)!=null}function $u(){return ul()||ia(!1),N.useContext(Ko).location}function ox(n){N.useContext(dl).static||N.useLayoutEffect(n)}function fl(){let{isDataRoute:n}=N.useContext(ts);return n?lb():Zv()}function Zv(){ul()||ia(!1);let n=N.useContext(Iu),{basename:s,future:l,navigator:o}=N.useContext(dl),{matches:d}=N.useContext(ts),{pathname:f}=$u(),m=JSON.stringify(ix(d,l.v7_relativeSplatPath)),p=N.useRef(!1);return ox(()=>{p.current=!0}),N.useCallback(function(h,x){if(x===void 0&&(x={}),!p.current)return;if(typeof h=="number"){o.go(h);return}let v=sx(h,JSON.parse(m),f,x.relative==="path");n==null&&s!=="/"&&(v.pathname=v.pathname==="/"?s:Qi([s,v.pathname])),(x.replace?o.replace:o.push)(v,x.state,x)},[s,o,m,f,n])}function Qv(n,s){return Jv(n,s)}function Jv(n,s,l,o){ul()||ia(!1);let{navigator:d}=N.useContext(dl),{matches:f}=N.useContext(ts),m=f[f.length-1],p=m?m.params:{};m&&m.pathname;let g=m?m.pathnameBase:"/";m&&m.route;let h=$u(),x;if(s){var v;let A=typeof s=="string"?Zs(s):s;g==="/"||(v=A.pathname)!=null&&v.startsWith(g)||ia(!1),x=A}else x=h;let b=x.pathname||"/",_=b;if(g!=="/"){let A=g.replace(/^\//,"").split("/");_="/"+b.replace(/^\//,"").split("/").slice(A.length).join("/")}let C=Sv(n,{pathname:_}),E=ab(C&&C.map(A=>Object.assign({},A,{params:Object.assign({},p,A.params),pathname:Qi([g,d.encodeLocation?d.encodeLocation(A.pathname).pathname:A.pathname]),pathnameBase:A.pathnameBase==="/"?g:Qi([g,d.encodeLocation?d.encodeLocation(A.pathnameBase).pathname:A.pathnameBase])})),f,l,o);return s&&E?N.createElement(Ko.Provider,{value:{location:el({pathname:"/",search:"",hash:"",state:null,key:"default"},x),navigationType:Ci.Pop}},E):E}function Wv(){let n=rb(),s=Vv(n)?n.status+" "+n.statusText:n instanceof Error?n.message:JSON.stringify(n),l=n instanceof Error?n.stack:null,d={padding:"0.5rem",backgroundColor:"rgba(200,200,200, 0.5)"};return N.createElement(N.Fragment,null,N.createElement("h2",null,"Unexpected Application Error!"),N.createElement("h3",{style:{fontStyle:"italic"}},s),l?N.createElement("pre",{style:d},l):null,null)}const Kv=N.createElement(Wv,null);class eb extends N.Component{constructor(s){super(s),this.state={location:s.location,revalidation:s.revalidation,error:s.error}}static getDerivedStateFromError(s){return{error:s}}static getDerivedStateFromProps(s,l){return l.location!==s.location||l.revalidation!=="idle"&&s.revalidation==="idle"?{error:s.error,location:s.location,revalidation:s.revalidation}:{error:s.error!==void 0?s.error:l.error,location:l.location,revalidation:s.revalidation||l.revalidation}}componentDidCatch(s,l){console.error("React Router caught the following error during render",s,l)}render(){return this.state.error!==void 0?N.createElement(ts.Provider,{value:this.props.routeContext},N.createElement(lx.Provider,{value:this.state.error,children:this.props.component})):this.props.children}}function tb(n){let{routeContext:s,match:l,children:o}=n,d=N.useContext(Iu);return d&&d.static&&d.staticContext&&(l.route.errorElement||l.route.ErrorBoundary)&&(d.staticContext._deepestRenderedBoundaryId=l.route.id),N.createElement(ts.Provider,{value:s},o)}function ab(n,s,l,o){var d;if(s===void 0&&(s=[]),l===void 0&&(l=null),o===void 0&&(o=null),n==null){var f;if(!l)return null;if(l.errors)n=l.matches;else if((f=o)!=null&&f.v7_partialHydration&&s.length===0&&!l.initialized&&l.matches.length>0)n=l.matches;else return null}let m=n,p=(d=l)==null?void 0:d.errors;if(p!=null){let x=m.findIndex(v=>v.route.id&&(p==null?void 0:p[v.route.id])!==void 0);x>=0||ia(!1),m=m.slice(0,Math.min(m.length,x+1))}let g=!1,h=-1;if(l&&o&&o.v7_partialHydration)for(let x=0;x<m.length;x++){let v=m[x];if((v.route.HydrateFallback||v.route.hydrateFallbackElement)&&(h=x),v.route.id){let{loaderData:b,errors:_}=l,C=v.route.loader&&b[v.route.id]===void 0&&(!_||_[v.route.id]===void 0);if(v.route.lazy||C){g=!0,h>=0?m=m.slice(0,h+1):m=[m[0]];break}}}return m.reduceRight((x,v,b)=>{let _,C=!1,E=null,A=null;l&&(_=p&&v.route.id?p[v.route.id]:void 0,E=v.route.errorElement||Kv,g&&(h<0&&b===0?(ob("route-fallback"),C=!0,A=null):h===b&&(C=!0,A=v.route.hydrateFallbackElement||null)));let L=s.concat(m.slice(0,b+1)),q=()=>{let P;return _?P=E:C?P=A:v.route.Component?P=N.createElement(v.route.Component,null):v.route.element?P=v.route.element:P=x,N.createElement(tb,{match:v,routeContext:{outlet:x,matches:L,isDataRoute:l!=null},children:P})};return l&&(v.route.ErrorBoundary||v.route.errorElement||b===0)?N.createElement(eb,{location:l.location,revalidation:l.revalidation,component:E,error:_,children:q(),routeContext:{outlet:null,matches:L,isDataRoute:!0}}):q()},null)}var cx=(function(n){return n.UseBlocker="useBlocker",n.UseRevalidator="useRevalidator",n.UseNavigateStable="useNavigate",n})(cx||{}),dx=(function(n){return n.UseBlocker="useBlocker",n.UseLoaderData="useLoaderData",n.UseActionData="useActionData",n.UseRouteError="useRouteError",n.UseNavigation="useNavigation",n.UseRouteLoaderData="useRouteLoaderData",n.UseMatches="useMatches",n.UseRevalidator="useRevalidator",n.UseNavigateStable="useNavigate",n.UseRouteId="useRouteId",n})(dx||{});function nb(n){let s=N.useContext(Iu);return s||ia(!1),s}function ib(n){let s=N.useContext(Xv);return s||ia(!1),s}function sb(n){let s=N.useContext(ts);return s||ia(!1),s}function ux(n){let s=sb(),l=s.matches[s.matches.length-1];return l.route.id||ia(!1),l.route.id}function rb(){var n;let s=N.useContext(lx),l=ib(),o=ux();return s!==void 0?s:(n=l.errors)==null?void 0:n[o]}function lb(){let{router:n}=nb(cx.UseNavigateStable),s=ux(dx.UseNavigateStable),l=N.useRef(!1);return ox(()=>{l.current=!0}),N.useCallback(function(d,f){f===void 0&&(f={}),l.current&&(typeof d=="number"?n.navigate(d):n.navigate(d,el({fromRouteId:s},f)))},[n,s])}const Zp={};function ob(n,s,l){Zp[n]||(Zp[n]=!0)}function cb(n,s){n==null||n.v7_startTransition,n==null||n.v7_relativeSplatPath}function yn(n){let{to:s,replace:l,state:o,relative:d}=n;ul()||ia(!1);let{future:f,static:m}=N.useContext(dl),{matches:p}=N.useContext(ts),{pathname:g}=$u(),h=fl(),x=sx(s,ix(p,f.v7_relativeSplatPath),g,d==="path"),v=JSON.stringify(x);return N.useEffect(()=>h(JSON.parse(v),{replace:l,state:o,relative:d}),[h,v,d,l,o]),null}function vn(n){ia(!1)}function db(n){let{basename:s="/",children:l=null,location:o,navigationType:d=Ci.Pop,navigator:f,static:m=!1,future:p}=n;ul()&&ia(!1);let g=s.replace(/^\/*/,"/"),h=N.useMemo(()=>({basename:g,navigator:f,static:m,future:el({v7_relativeSplatPath:!1},p)}),[g,p,f,m]);typeof o=="string"&&(o=Zs(o));let{pathname:x="/",search:v="",hash:b="",state:_=null,key:C="default"}=o,E=N.useMemo(()=>{let A=nx(x,g);return A==null?null:{location:{pathname:A,search:v,hash:b,state:_,key:C},navigationType:d}},[g,x,v,b,_,C,d]);return E==null?null:N.createElement(dl.Provider,{value:h},N.createElement(Ko.Provider,{children:l,value:E}))}function ub(n){let{children:s,location:l}=n;return Qv(Su(s),l)}new Promise(()=>{});function Su(n,s){s===void 0&&(s=[]);let l=[];return N.Children.forEach(n,(o,d)=>{if(!N.isValidElement(o))return;let f=[...s,d];if(o.type===N.Fragment){l.push.apply(l,Su(o.props.children,f));return}o.type!==vn&&ia(!1),!o.props.index||!o.props.children||ia(!1);let m={id:o.props.id||f.join("-"),caseSensitive:o.props.caseSensitive,element:o.props.element,Component:o.props.Component,index:o.props.index,path:o.props.path,loader:o.props.loader,action:o.props.action,errorElement:o.props.errorElement,ErrorBoundary:o.props.ErrorBoundary,hasErrorBoundary:o.props.ErrorBoundary!=null||o.props.errorElement!=null,shouldRevalidate:o.props.shouldRevalidate,handle:o.props.handle,lazy:o.props.lazy};o.props.children&&(m.children=Su(o.props.children,f)),l.push(m)}),l}/**
 * React Router DOM v6.30.1
 *
 * Copyright (c) Remix Software Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE.md file in the root directory of this source tree.
 *
 * @license MIT
 */const fb="6";try{window.__reactRouterVersion=fb}catch{}const hb="startTransition",Qp=mv[hb];function mb(n){let{basename:s,children:l,future:o,window:d}=n,f=N.useRef();f.current==null&&(f.current=wv({window:d,v5Compat:!0}));let m=f.current,[p,g]=N.useState({action:m.action,location:m.location}),{v7_startTransition:h}=o||{},x=N.useCallback(v=>{h&&Qp?Qp(()=>g(v)):g(v)},[g,h]);return N.useLayoutEffect(()=>m.listen(x),[m,x]),N.useEffect(()=>cb(o),[o]),N.createElement(db,{basename:s,children:l,location:p.location,navigationType:p.action,navigator:m,future:o})}var Jp;(function(n){n.UseScrollRestoration="useScrollRestoration",n.UseSubmit="useSubmit",n.UseSubmitFetcher="useSubmitFetcher",n.UseFetcher="useFetcher",n.useViewTransitionState="useViewTransitionState"})(Jp||(Jp={}));var Wp;(function(n){n.UseFetcher="useFetcher",n.UseFetchers="useFetchers",n.UseScrollRestoration="useScrollRestoration"})(Wp||(Wp={}));function ko(n,s){return n==null||s==null?NaN:n<s?-1:n>s?1:n>=s?0:NaN}function pb(n,s){return n==null||s==null?NaN:s<n?-1:s>n?1:s>=n?0:NaN}function Fu(n){let s,l,o;n.length!==2?(s=ko,l=(p,g)=>ko(n(p),g),o=(p,g)=>n(p)-g):(s=n===ko||n===pb?n:gb,l=n,o=n);function d(p,g,h=0,x=p.length){if(h<x){if(s(g,g)!==0)return x;do{const v=h+x>>>1;l(p[v],g)<0?h=v+1:x=v}while(h<x)}return h}function f(p,g,h=0,x=p.length){if(h<x){if(s(g,g)!==0)return x;do{const v=h+x>>>1;l(p[v],g)<=0?h=v+1:x=v}while(h<x)}return h}function m(p,g,h=0,x=p.length){const v=d(p,g,h,x-1);return v>h&&o(p[v-1],g)>-o(p[v],g)?v-1:v}return{left:d,center:m,right:f}}function gb(){return 0}function xb(n){return n===null?NaN:+n}const yb=Fu(ko),vb=yb.right;Fu(xb).center;function fx(n,s){let l,o;if(s===void 0)for(const d of n)d!=null&&(l===void 0?d>=d&&(l=o=d):(l>d&&(l=d),o<d&&(o=d)));else{let d=-1;for(let f of n)(f=s(f,++d,n))!=null&&(l===void 0?f>=f&&(l=o=f):(l>f&&(l=f),o<f&&(o=f)))}return[l,o]}class Kp extends Map{constructor(s,l=wb){if(super(),Object.defineProperties(this,{_intern:{value:new Map},_key:{value:l}}),s!=null)for(const[o,d]of s)this.set(o,d)}get(s){return super.get(eg(this,s))}has(s){return super.has(eg(this,s))}set(s,l){return super.set(bb(this,s),l)}delete(s){return super.delete(jb(this,s))}}function eg({_intern:n,_key:s},l){const o=s(l);return n.has(o)?n.get(o):l}function bb({_intern:n,_key:s},l){const o=s(l);return n.has(o)?n.get(o):(n.set(o,l),l)}function jb({_intern:n,_key:s},l){const o=s(l);return n.has(o)&&(l=n.get(o),n.delete(o)),l}function wb(n){return n!==null&&typeof n=="object"?n.valueOf():n}const Nb=Math.sqrt(50),_b=Math.sqrt(10),Sb=Math.sqrt(2);function Oo(n,s,l){const o=(s-n)/Math.max(0,l),d=Math.floor(Math.log10(o)),f=o/Math.pow(10,d),m=f>=Nb?10:f>=_b?5:f>=Sb?2:1;let p,g,h;return d<0?(h=Math.pow(10,-d)/m,p=Math.round(n*h),g=Math.round(s*h),p/h<n&&++p,g/h>s&&--g,h=-h):(h=Math.pow(10,d)*m,p=Math.round(n/h),g=Math.round(s/h),p*h<n&&++p,g*h>s&&--g),g<p&&.5<=l&&l<2?Oo(n,s,l*2):[p,g,h]}function Tb(n,s,l){if(s=+s,n=+n,l=+l,!(l>0))return[];if(n===s)return[n];const o=s<n,[d,f,m]=o?Oo(s,n,l):Oo(n,s,l);if(!(f>=d))return[];const p=f-d+1,g=new Array(p);if(o)if(m<0)for(let h=0;h<p;++h)g[h]=(f-h)/-m;else for(let h=0;h<p;++h)g[h]=(f-h)*m;else if(m<0)for(let h=0;h<p;++h)g[h]=(d+h)/-m;else for(let h=0;h<p;++h)g[h]=(d+h)*m;return g}function Tu(n,s,l){return s=+s,n=+n,l=+l,Oo(n,s,l)[2]}function Cu(n,s,l){s=+s,n=+n,l=+l;const o=s<n,d=o?Tu(s,n,l):Tu(n,s,l);return(o?-1:1)*(d<0?1/-d:d)}function Uo(n,s){let l;if(s===void 0)for(const o of n)o!=null&&(l<o||l===void 0&&o>=o)&&(l=o);else{let o=-1;for(let d of n)(d=s(d,++o,n))!=null&&(l<d||l===void 0&&d>=d)&&(l=d)}return l}function Cb(n,s,l){n=+n,s=+s,l=(d=arguments.length)<2?(s=n,n=0,1):d<3?1:+l;for(var o=-1,d=Math.max(0,Math.ceil((s-n)/l))|0,f=new Array(d);++o<d;)f[o]=n+o*l;return f}function Ab(n){return n}var uu=1,fu=2,Au=3,Xr=4,tg=1e-6;function zb(n){return"translate("+n+",0)"}function kb(n){return"translate(0,"+n+")"}function Eb(n){return s=>+n(s)}function Mb(n,s){return s=Math.max(0,n.bandwidth()-s*2)/2,n.round()&&(s=Math.round(s)),l=>+n(l)+s}function Db(){return!this.__axis}function hx(n,s){var l=[],o=null,d=null,f=6,m=6,p=3,g=typeof window<"u"&&window.devicePixelRatio>1?0:.5,h=n===uu||n===Xr?-1:1,x=n===Xr||n===fu?"x":"y",v=n===uu||n===Au?zb:kb;function b(_){var C=o??(s.ticks?s.ticks.apply(s,l):s.domain()),E=d??(s.tickFormat?s.tickFormat.apply(s,l):Ab),A=Math.max(f,0)+p,L=s.range(),q=+L[0]+g,P=+L[L.length-1]+g,M=(s.bandwidth?Mb:Eb)(s.copy(),g),X=_.selection?_.selection():_,Q=X.selectAll(".domain").data([null]),K=X.selectAll(".tick").data(C,s).order(),se=K.exit(),Ae=K.enter().append("g").attr("class","tick"),we=K.select("line"),ge=K.select("text");Q=Q.merge(Q.enter().insert("path",".tick").attr("class","domain").attr("stroke","currentColor")),K=K.merge(Ae),we=we.merge(Ae.append("line").attr("stroke","currentColor").attr(x+"2",h*f)),ge=ge.merge(Ae.append("text").attr("fill","currentColor").attr(x,h*A).attr("dy",n===uu?"0em":n===Au?"0.71em":"0.32em")),_!==X&&(Q=Q.transition(_),K=K.transition(_),we=we.transition(_),ge=ge.transition(_),se=se.transition(_).attr("opacity",tg).attr("transform",function(Ne){return isFinite(Ne=M(Ne))?v(Ne+g):this.getAttribute("transform")}),Ae.attr("opacity",tg).attr("transform",function(Ne){var me=this.parentNode.__axis;return v((me&&isFinite(me=me(Ne))?me:M(Ne))+g)})),se.remove(),Q.attr("d",n===Xr||n===fu?m?"M"+h*m+","+q+"H"+g+"V"+P+"H"+h*m:"M"+g+","+q+"V"+P:m?"M"+q+","+h*m+"V"+g+"H"+P+"V"+h*m:"M"+q+","+g+"H"+P),K.attr("opacity",1).attr("transform",function(Ne){return v(M(Ne)+g)}),we.attr(x+"2",h*f),ge.attr(x,h*A).text(E),X.filter(Db).attr("fill","none").attr("font-size",10).attr("font-family","sans-serif").attr("text-anchor",n===fu?"start":n===Xr?"end":"middle"),X.each(function(){this.__axis=M})}return b.scale=function(_){return arguments.length?(s=_,b):s},b.ticks=function(){return l=Array.from(arguments),b},b.tickArguments=function(_){return arguments.length?(l=_==null?[]:Array.from(_),b):l.slice()},b.tickValues=function(_){return arguments.length?(o=_==null?null:Array.from(_),b):o&&o.slice()},b.tickFormat=function(_){return arguments.length?(d=_,b):d},b.tickSize=function(_){return arguments.length?(f=m=+_,b):f},b.tickSizeInner=function(_){return arguments.length?(f=+_,b):f},b.tickSizeOuter=function(_){return arguments.length?(m=+_,b):m},b.tickPadding=function(_){return arguments.length?(p=+_,b):p},b.offset=function(_){return arguments.length?(g=+_,b):g},b}function tl(n){return hx(Au,n)}function al(n){return hx(Xr,n)}var Rb={value:()=>{}};function ec(){for(var n=0,s=arguments.length,l={},o;n<s;++n){if(!(o=arguments[n]+"")||o in l||/[\s.]/.test(o))throw new Error("illegal type: "+o);l[o]=[]}return new Eo(l)}function Eo(n){this._=n}function Ob(n,s){return n.trim().split(/^|\s+/).map(function(l){var o="",d=l.indexOf(".");if(d>=0&&(o=l.slice(d+1),l=l.slice(0,d)),l&&!s.hasOwnProperty(l))throw new Error("unknown type: "+l);return{type:l,name:o}})}Eo.prototype=ec.prototype={constructor:Eo,on:function(n,s){var l=this._,o=Ob(n+"",l),d,f=-1,m=o.length;if(arguments.length<2){for(;++f<m;)if((d=(n=o[f]).type)&&(d=Ub(l[d],n.name)))return d;return}if(s!=null&&typeof s!="function")throw new Error("invalid callback: "+s);for(;++f<m;)if(d=(n=o[f]).type)l[d]=ag(l[d],n.name,s);else if(s==null)for(d in l)l[d]=ag(l[d],n.name,null);return this},copy:function(){var n={},s=this._;for(var l in s)n[l]=s[l].slice();return new Eo(n)},call:function(n,s){if((d=arguments.length-2)>0)for(var l=new Array(d),o=0,d,f;o<d;++o)l[o]=arguments[o+2];if(!this._.hasOwnProperty(n))throw new Error("unknown type: "+n);for(f=this._[n],o=0,d=f.length;o<d;++o)f[o].value.apply(s,l)},apply:function(n,s,l){if(!this._.hasOwnProperty(n))throw new Error("unknown type: "+n);for(var o=this._[n],d=0,f=o.length;d<f;++d)o[d].value.apply(s,l)}};function Ub(n,s){for(var l=0,o=n.length,d;l<o;++l)if((d=n[l]).name===s)return d.value}function ag(n,s,l){for(var o=0,d=n.length;o<d;++o)if(n[o].name===s){n[o]=Rb,n=n.slice(0,o).concat(n.slice(o+1));break}return l!=null&&n.push({name:s,value:l}),n}var zu="http://www.w3.org/1999/xhtml";const ng={svg:"http://www.w3.org/2000/svg",xhtml:zu,xlink:"http://www.w3.org/1999/xlink",xml:"http://www.w3.org/XML/1998/namespace",xmlns:"http://www.w3.org/2000/xmlns/"};function tc(n){var s=n+="",l=s.indexOf(":");return l>=0&&(s=n.slice(0,l))!=="xmlns"&&(n=n.slice(l+1)),ng.hasOwnProperty(s)?{space:ng[s],local:n}:n}function Lb(n){return function(){var s=this.ownerDocument,l=this.namespaceURI;return l===zu&&s.documentElement.namespaceURI===zu?s.createElement(n):s.createElementNS(l,n)}}function Bb(n){return function(){return this.ownerDocument.createElementNS(n.space,n.local)}}function mx(n){var s=tc(n);return(s.local?Bb:Lb)(s)}function qb(){}function Yu(n){return n==null?qb:function(){return this.querySelector(n)}}function Hb(n){typeof n!="function"&&(n=Yu(n));for(var s=this._groups,l=s.length,o=new Array(l),d=0;d<l;++d)for(var f=s[d],m=f.length,p=o[d]=new Array(m),g,h,x=0;x<m;++x)(g=f[x])&&(h=n.call(g,g.__data__,x,f))&&("__data__"in g&&(h.__data__=g.__data__),p[x]=h);return new Ea(o,this._parents)}function px(n){return n==null?[]:Array.isArray(n)?n:Array.from(n)}function Ib(){return[]}function gx(n){return n==null?Ib:function(){return this.querySelectorAll(n)}}function $b(n){return function(){return px(n.apply(this,arguments))}}function Fb(n){typeof n=="function"?n=$b(n):n=gx(n);for(var s=this._groups,l=s.length,o=[],d=[],f=0;f<l;++f)for(var m=s[f],p=m.length,g,h=0;h<p;++h)(g=m[h])&&(o.push(n.call(g,g.__data__,h,m)),d.push(g));return new Ea(o,d)}function xx(n){return function(){return this.matches(n)}}function yx(n){return function(s){return s.matches(n)}}var Yb=Array.prototype.find;function Gb(n){return function(){return Yb.call(this.children,n)}}function Vb(){return this.firstElementChild}function Pb(n){return this.select(n==null?Vb:Gb(typeof n=="function"?n:yx(n)))}var Xb=Array.prototype.filter;function Zb(){return Array.from(this.children)}function Qb(n){return function(){return Xb.call(this.children,n)}}function Jb(n){return this.selectAll(n==null?Zb:Qb(typeof n=="function"?n:yx(n)))}function Wb(n){typeof n!="function"&&(n=xx(n));for(var s=this._groups,l=s.length,o=new Array(l),d=0;d<l;++d)for(var f=s[d],m=f.length,p=o[d]=[],g,h=0;h<m;++h)(g=f[h])&&n.call(g,g.__data__,h,f)&&p.push(g);return new Ea(o,this._parents)}function vx(n){return new Array(n.length)}function Kb(){return new Ea(this._enter||this._groups.map(vx),this._parents)}function Lo(n,s){this.ownerDocument=n.ownerDocument,this.namespaceURI=n.namespaceURI,this._next=null,this._parent=n,this.__data__=s}Lo.prototype={constructor:Lo,appendChild:function(n){return this._parent.insertBefore(n,this._next)},insertBefore:function(n,s){return this._parent.insertBefore(n,s)},querySelector:function(n){return this._parent.querySelector(n)},querySelectorAll:function(n){return this._parent.querySelectorAll(n)}};function ej(n){return function(){return n}}function tj(n,s,l,o,d,f){for(var m=0,p,g=s.length,h=f.length;m<h;++m)(p=s[m])?(p.__data__=f[m],o[m]=p):l[m]=new Lo(n,f[m]);for(;m<g;++m)(p=s[m])&&(d[m]=p)}function aj(n,s,l,o,d,f,m){var p,g,h=new Map,x=s.length,v=f.length,b=new Array(x),_;for(p=0;p<x;++p)(g=s[p])&&(b[p]=_=m.call(g,g.__data__,p,s)+"",h.has(_)?d[p]=g:h.set(_,g));for(p=0;p<v;++p)_=m.call(n,f[p],p,f)+"",(g=h.get(_))?(o[p]=g,g.__data__=f[p],h.delete(_)):l[p]=new Lo(n,f[p]);for(p=0;p<x;++p)(g=s[p])&&h.get(b[p])===g&&(d[p]=g)}function nj(n){return n.__data__}function ij(n,s){if(!arguments.length)return Array.from(this,nj);var l=s?aj:tj,o=this._parents,d=this._groups;typeof n!="function"&&(n=ej(n));for(var f=d.length,m=new Array(f),p=new Array(f),g=new Array(f),h=0;h<f;++h){var x=o[h],v=d[h],b=v.length,_=sj(n.call(x,x&&x.__data__,h,o)),C=_.length,E=p[h]=new Array(C),A=m[h]=new Array(C),L=g[h]=new Array(b);l(x,v,E,A,L,_,s);for(var q=0,P=0,M,X;q<C;++q)if(M=E[q]){for(q>=P&&(P=q+1);!(X=A[P])&&++P<C;);M._next=X||null}}return m=new Ea(m,o),m._enter=p,m._exit=g,m}function sj(n){return typeof n=="object"&&"length"in n?n:Array.from(n)}function rj(){return new Ea(this._exit||this._groups.map(vx),this._parents)}function lj(n,s,l){var o=this.enter(),d=this,f=this.exit();return typeof n=="function"?(o=n(o),o&&(o=o.selection())):o=o.append(n+""),s!=null&&(d=s(d),d&&(d=d.selection())),l==null?f.remove():l(f),o&&d?o.merge(d).order():d}function oj(n){for(var s=n.selection?n.selection():n,l=this._groups,o=s._groups,d=l.length,f=o.length,m=Math.min(d,f),p=new Array(d),g=0;g<m;++g)for(var h=l[g],x=o[g],v=h.length,b=p[g]=new Array(v),_,C=0;C<v;++C)(_=h[C]||x[C])&&(b[C]=_);for(;g<d;++g)p[g]=l[g];return new Ea(p,this._parents)}function cj(){for(var n=this._groups,s=-1,l=n.length;++s<l;)for(var o=n[s],d=o.length-1,f=o[d],m;--d>=0;)(m=o[d])&&(f&&m.compareDocumentPosition(f)^4&&f.parentNode.insertBefore(m,f),f=m);return this}function dj(n){n||(n=uj);function s(v,b){return v&&b?n(v.__data__,b.__data__):!v-!b}for(var l=this._groups,o=l.length,d=new Array(o),f=0;f<o;++f){for(var m=l[f],p=m.length,g=d[f]=new Array(p),h,x=0;x<p;++x)(h=m[x])&&(g[x]=h);g.sort(s)}return new Ea(d,this._parents).order()}function uj(n,s){return n<s?-1:n>s?1:n>=s?0:NaN}function fj(){var n=arguments[0];return arguments[0]=this,n.apply(null,arguments),this}function hj(){return Array.from(this)}function mj(){for(var n=this._groups,s=0,l=n.length;s<l;++s)for(var o=n[s],d=0,f=o.length;d<f;++d){var m=o[d];if(m)return m}return null}function pj(){let n=0;for(const s of this)++n;return n}function gj(){return!this.node()}function xj(n){for(var s=this._groups,l=0,o=s.length;l<o;++l)for(var d=s[l],f=0,m=d.length,p;f<m;++f)(p=d[f])&&n.call(p,p.__data__,f,d);return this}function yj(n){return function(){this.removeAttribute(n)}}function vj(n){return function(){this.removeAttributeNS(n.space,n.local)}}function bj(n,s){return function(){this.setAttribute(n,s)}}function jj(n,s){return function(){this.setAttributeNS(n.space,n.local,s)}}function wj(n,s){return function(){var l=s.apply(this,arguments);l==null?this.removeAttribute(n):this.setAttribute(n,l)}}function Nj(n,s){return function(){var l=s.apply(this,arguments);l==null?this.removeAttributeNS(n.space,n.local):this.setAttributeNS(n.space,n.local,l)}}function _j(n,s){var l=tc(n);if(arguments.length<2){var o=this.node();return l.local?o.getAttributeNS(l.space,l.local):o.getAttribute(l)}return this.each((s==null?l.local?vj:yj:typeof s=="function"?l.local?Nj:wj:l.local?jj:bj)(l,s))}function bx(n){return n.ownerDocument&&n.ownerDocument.defaultView||n.document&&n||n.defaultView}function Sj(n){return function(){this.style.removeProperty(n)}}function Tj(n,s,l){return function(){this.style.setProperty(n,s,l)}}function Cj(n,s,l){return function(){var o=s.apply(this,arguments);o==null?this.style.removeProperty(n):this.style.setProperty(n,o,l)}}function Aj(n,s,l){return arguments.length>1?this.each((s==null?Sj:typeof s=="function"?Cj:Tj)(n,s,l??"")):Ys(this.node(),n)}function Ys(n,s){return n.style.getPropertyValue(s)||bx(n).getComputedStyle(n,null).getPropertyValue(s)}function zj(n){return function(){delete this[n]}}function kj(n,s){return function(){this[n]=s}}function Ej(n,s){return function(){var l=s.apply(this,arguments);l==null?delete this[n]:this[n]=l}}function Mj(n,s){return arguments.length>1?this.each((s==null?zj:typeof s=="function"?Ej:kj)(n,s)):this.node()[n]}function jx(n){return n.trim().split(/^|\s+/)}function Gu(n){return n.classList||new wx(n)}function wx(n){this._node=n,this._names=jx(n.getAttribute("class")||"")}wx.prototype={add:function(n){var s=this._names.indexOf(n);s<0&&(this._names.push(n),this._node.setAttribute("class",this._names.join(" ")))},remove:function(n){var s=this._names.indexOf(n);s>=0&&(this._names.splice(s,1),this._node.setAttribute("class",this._names.join(" ")))},contains:function(n){return this._names.indexOf(n)>=0}};function Nx(n,s){for(var l=Gu(n),o=-1,d=s.length;++o<d;)l.add(s[o])}function _x(n,s){for(var l=Gu(n),o=-1,d=s.length;++o<d;)l.remove(s[o])}function Dj(n){return function(){Nx(this,n)}}function Rj(n){return function(){_x(this,n)}}function Oj(n,s){return function(){(s.apply(this,arguments)?Nx:_x)(this,n)}}function Uj(n,s){var l=jx(n+"");if(arguments.length<2){for(var o=Gu(this.node()),d=-1,f=l.length;++d<f;)if(!o.contains(l[d]))return!1;return!0}return this.each((typeof s=="function"?Oj:s?Dj:Rj)(l,s))}function Lj(){this.textContent=""}function Bj(n){return function(){this.textContent=n}}function qj(n){return function(){var s=n.apply(this,arguments);this.textContent=s??""}}function Hj(n){return arguments.length?this.each(n==null?Lj:(typeof n=="function"?qj:Bj)(n)):this.node().textContent}function Ij(){this.innerHTML=""}function $j(n){return function(){this.innerHTML=n}}function Fj(n){return function(){var s=n.apply(this,arguments);this.innerHTML=s??""}}function Yj(n){return arguments.length?this.each(n==null?Ij:(typeof n=="function"?Fj:$j)(n)):this.node().innerHTML}function Gj(){this.nextSibling&&this.parentNode.appendChild(this)}function Vj(){return this.each(Gj)}function Pj(){this.previousSibling&&this.parentNode.insertBefore(this,this.parentNode.firstChild)}function Xj(){return this.each(Pj)}function Zj(n){var s=typeof n=="function"?n:mx(n);return this.select(function(){return this.appendChild(s.apply(this,arguments))})}function Qj(){return null}function Jj(n,s){var l=typeof n=="function"?n:mx(n),o=s==null?Qj:typeof s=="function"?s:Yu(s);return this.select(function(){return this.insertBefore(l.apply(this,arguments),o.apply(this,arguments)||null)})}function Wj(){var n=this.parentNode;n&&n.removeChild(this)}function Kj(){return this.each(Wj)}function e1(){var n=this.cloneNode(!1),s=this.parentNode;return s?s.insertBefore(n,this.nextSibling):n}function t1(){var n=this.cloneNode(!0),s=this.parentNode;return s?s.insertBefore(n,this.nextSibling):n}function a1(n){return this.select(n?t1:e1)}function n1(n){return arguments.length?this.property("__data__",n):this.node().__data__}function i1(n){return function(s){n.call(this,s,this.__data__)}}function s1(n){return n.trim().split(/^|\s+/).map(function(s){var l="",o=s.indexOf(".");return o>=0&&(l=s.slice(o+1),s=s.slice(0,o)),{type:s,name:l}})}function r1(n){return function(){var s=this.__on;if(s){for(var l=0,o=-1,d=s.length,f;l<d;++l)f=s[l],(!n.type||f.type===n.type)&&f.name===n.name?this.removeEventListener(f.type,f.listener,f.options):s[++o]=f;++o?s.length=o:delete this.__on}}}function l1(n,s,l){return function(){var o=this.__on,d,f=i1(s);if(o){for(var m=0,p=o.length;m<p;++m)if((d=o[m]).type===n.type&&d.name===n.name){this.removeEventListener(d.type,d.listener,d.options),this.addEventListener(d.type,d.listener=f,d.options=l),d.value=s;return}}this.addEventListener(n.type,f,l),d={type:n.type,name:n.name,value:s,listener:f,options:l},o?o.push(d):this.__on=[d]}}function o1(n,s,l){var o=s1(n+""),d,f=o.length,m;if(arguments.length<2){var p=this.node().__on;if(p){for(var g=0,h=p.length,x;g<h;++g)for(d=0,x=p[g];d<f;++d)if((m=o[d]).type===x.type&&m.name===x.name)return x.value}return}for(p=s?l1:r1,d=0;d<f;++d)this.each(p(o[d],s,l));return this}function Sx(n,s,l){var o=bx(n),d=o.CustomEvent;typeof d=="function"?d=new d(s,l):(d=o.document.createEvent("Event"),l?(d.initEvent(s,l.bubbles,l.cancelable),d.detail=l.detail):d.initEvent(s,!1,!1)),n.dispatchEvent(d)}function c1(n,s){return function(){return Sx(this,n,s)}}function d1(n,s){return function(){return Sx(this,n,s.apply(this,arguments))}}function u1(n,s){return this.each((typeof s=="function"?d1:c1)(n,s))}function*f1(){for(var n=this._groups,s=0,l=n.length;s<l;++s)for(var o=n[s],d=0,f=o.length,m;d<f;++d)(m=o[d])&&(yield m)}var Vu=[null];function Ea(n,s){this._groups=n,this._parents=s}function hl(){return new Ea([[document.documentElement]],Vu)}function h1(){return this}Ea.prototype=hl.prototype={constructor:Ea,select:Hb,selectAll:Fb,selectChild:Pb,selectChildren:Jb,filter:Wb,data:ij,enter:Kb,exit:rj,join:lj,merge:oj,selection:h1,order:cj,sort:dj,call:fj,nodes:hj,node:mj,size:pj,empty:gj,each:xj,attr:_j,style:Aj,property:Mj,classed:Uj,text:Hj,html:Yj,raise:Vj,lower:Xj,append:Zj,insert:Jj,remove:Kj,clone:a1,datum:n1,on:o1,dispatch:u1,[Symbol.iterator]:f1};function oa(n){return typeof n=="string"?new Ea([[document.querySelector(n)]],[document.documentElement]):new Ea([[n]],Vu)}function m1(n){let s;for(;s=n.sourceEvent;)n=s;return n}function ig(n,s){if(n=m1(n),s===void 0&&(s=n.currentTarget),s){var l=s.ownerSVGElement||s;if(l.createSVGPoint){var o=l.createSVGPoint();return o.x=n.clientX,o.y=n.clientY,o=o.matrixTransform(s.getScreenCTM().inverse()),[o.x,o.y]}if(s.getBoundingClientRect){var d=s.getBoundingClientRect();return[n.clientX-d.left-s.clientLeft,n.clientY-d.top-s.clientTop]}}return[n.pageX,n.pageY]}function p1(n){return typeof n=="string"?new Ea([document.querySelectorAll(n)],[document.documentElement]):new Ea([px(n)],Vu)}const g1={passive:!1},nl={capture:!0,passive:!1};function hu(n){n.stopImmediatePropagation()}function Is(n){n.preventDefault(),n.stopImmediatePropagation()}function x1(n){var s=n.document.documentElement,l=oa(n).on("dragstart.drag",Is,nl);"onselectstart"in s?l.on("selectstart.drag",Is,nl):(s.__noselect=s.style.MozUserSelect,s.style.MozUserSelect="none")}function y1(n,s){var l=n.document.documentElement,o=oa(n).on("dragstart.drag",null);s&&(o.on("click.drag",Is,nl),setTimeout(function(){o.on("click.drag",null)},0)),"onselectstart"in l?o.on("selectstart.drag",null):(l.style.MozUserSelect=l.__noselect,delete l.__noselect)}const wo=n=>()=>n;function ku(n,{sourceEvent:s,subject:l,target:o,identifier:d,active:f,x:m,y:p,dx:g,dy:h,dispatch:x}){Object.defineProperties(this,{type:{value:n,enumerable:!0,configurable:!0},sourceEvent:{value:s,enumerable:!0,configurable:!0},subject:{value:l,enumerable:!0,configurable:!0},target:{value:o,enumerable:!0,configurable:!0},identifier:{value:d,enumerable:!0,configurable:!0},active:{value:f,enumerable:!0,configurable:!0},x:{value:m,enumerable:!0,configurable:!0},y:{value:p,enumerable:!0,configurable:!0},dx:{value:g,enumerable:!0,configurable:!0},dy:{value:h,enumerable:!0,configurable:!0},_:{value:x}})}ku.prototype.on=function(){var n=this._.on.apply(this._,arguments);return n===this._?this:n};function v1(n){return!n.ctrlKey&&!n.button}function b1(){return this.parentNode}function j1(n,s){return s??{x:n.x,y:n.y}}function w1(){return navigator.maxTouchPoints||"ontouchstart"in this}function N1(){var n=v1,s=b1,l=j1,o=w1,d={},f=ec("start","drag","end"),m=0,p,g,h,x,v=0;function b(M){M.on("mousedown.drag",_).filter(o).on("touchstart.drag",A).on("touchmove.drag",L,g1).on("touchend.drag touchcancel.drag",q).style("touch-action","none").style("-webkit-tap-highlight-color","rgba(0,0,0,0)")}function _(M,X){if(!(x||!n.call(this,M,X))){var Q=P(this,s.call(this,M,X),M,X,"mouse");Q&&(oa(M.view).on("mousemove.drag",C,nl).on("mouseup.drag",E,nl),x1(M.view),hu(M),h=!1,p=M.clientX,g=M.clientY,Q("start",M))}}function C(M){if(Is(M),!h){var X=M.clientX-p,Q=M.clientY-g;h=X*X+Q*Q>v}d.mouse("drag",M)}function E(M){oa(M.view).on("mousemove.drag mouseup.drag",null),y1(M.view,h),Is(M),d.mouse("end",M)}function A(M,X){if(n.call(this,M,X)){var Q=M.changedTouches,K=s.call(this,M,X),se=Q.length,Ae,we;for(Ae=0;Ae<se;++Ae)(we=P(this,K,M,X,Q[Ae].identifier,Q[Ae]))&&(hu(M),we("start",M,Q[Ae]))}}function L(M){var X=M.changedTouches,Q=X.length,K,se;for(K=0;K<Q;++K)(se=d[X[K].identifier])&&(Is(M),se("drag",M,X[K]))}function q(M){var X=M.changedTouches,Q=X.length,K,se;for(x&&clearTimeout(x),x=setTimeout(function(){x=null},500),K=0;K<Q;++K)(se=d[X[K].identifier])&&(hu(M),se("end",M,X[K]))}function P(M,X,Q,K,se,Ae){var we=f.copy(),ge=ig(Ae||Q,X),Ne,me,xe;if((xe=l.call(M,new ku("beforestart",{sourceEvent:Q,target:b,identifier:se,active:m,x:ge[0],y:ge[1],dx:0,dy:0,dispatch:we}),K))!=null)return Ne=xe.x-ge[0]||0,me=xe.y-ge[1]||0,function He(S,H,F){var _e=ge,z;switch(S){case"start":d[se]=He,z=m++;break;case"end":delete d[se],--m;case"drag":ge=ig(F||H,X),z=m;break}we.call(S,M,new ku(S,{sourceEvent:H,subject:xe,target:b,identifier:se,active:z,x:ge[0]+Ne,y:ge[1]+me,dx:ge[0]-_e[0],dy:ge[1]-_e[1],dispatch:we}),K)}}return b.filter=function(M){return arguments.length?(n=typeof M=="function"?M:wo(!!M),b):n},b.container=function(M){return arguments.length?(s=typeof M=="function"?M:wo(M),b):s},b.subject=function(M){return arguments.length?(l=typeof M=="function"?M:wo(M),b):l},b.touchable=function(M){return arguments.length?(o=typeof M=="function"?M:wo(!!M),b):o},b.on=function(){var M=f.on.apply(f,arguments);return M===f?b:M},b.clickDistance=function(M){return arguments.length?(v=(M=+M)*M,b):Math.sqrt(v)},b}function Pu(n,s,l){n.prototype=s.prototype=l,l.constructor=n}function Tx(n,s){var l=Object.create(n.prototype);for(var o in s)l[o]=s[o];return l}function ml(){}var il=.7,Bo=1/il,$s="\\s*([+-]?\\d+)\\s*",sl="\\s*([+-]?(?:\\d*\\.)?\\d+(?:[eE][+-]?\\d+)?)\\s*",zn="\\s*([+-]?(?:\\d*\\.)?\\d+(?:[eE][+-]?\\d+)?)%\\s*",_1=/^#([0-9a-f]{3,8})$/,S1=new RegExp(`^rgb\\(${$s},${$s},${$s}\\)$`),T1=new RegExp(`^rgb\\(${zn},${zn},${zn}\\)$`),C1=new RegExp(`^rgba\\(${$s},${$s},${$s},${sl}\\)$`),A1=new RegExp(`^rgba\\(${zn},${zn},${zn},${sl}\\)$`),z1=new RegExp(`^hsl\\(${sl},${zn},${zn}\\)$`),k1=new RegExp(`^hsla\\(${sl},${zn},${zn},${sl}\\)$`),sg={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074};Pu(ml,Wi,{copy(n){return Object.assign(new this.constructor,this,n)},displayable(){return this.rgb().displayable()},hex:rg,formatHex:rg,formatHex8:E1,formatHsl:M1,formatRgb:lg,toString:lg});function rg(){return this.rgb().formatHex()}function E1(){return this.rgb().formatHex8()}function M1(){return Cx(this).formatHsl()}function lg(){return this.rgb().formatRgb()}function Wi(n){var s,l;return n=(n+"").trim().toLowerCase(),(s=_1.exec(n))?(l=s[1].length,s=parseInt(s[1],16),l===6?og(s):l===3?new Ha(s>>8&15|s>>4&240,s>>4&15|s&240,(s&15)<<4|s&15,1):l===8?No(s>>24&255,s>>16&255,s>>8&255,(s&255)/255):l===4?No(s>>12&15|s>>8&240,s>>8&15|s>>4&240,s>>4&15|s&240,((s&15)<<4|s&15)/255):null):(s=S1.exec(n))?new Ha(s[1],s[2],s[3],1):(s=T1.exec(n))?new Ha(s[1]*255/100,s[2]*255/100,s[3]*255/100,1):(s=C1.exec(n))?No(s[1],s[2],s[3],s[4]):(s=A1.exec(n))?No(s[1]*255/100,s[2]*255/100,s[3]*255/100,s[4]):(s=z1.exec(n))?ug(s[1],s[2]/100,s[3]/100,1):(s=k1.exec(n))?ug(s[1],s[2]/100,s[3]/100,s[4]):sg.hasOwnProperty(n)?og(sg[n]):n==="transparent"?new Ha(NaN,NaN,NaN,0):null}function og(n){return new Ha(n>>16&255,n>>8&255,n&255,1)}function No(n,s,l,o){return o<=0&&(n=s=l=NaN),new Ha(n,s,l,o)}function D1(n){return n instanceof ml||(n=Wi(n)),n?(n=n.rgb(),new Ha(n.r,n.g,n.b,n.opacity)):new Ha}function Eu(n,s,l,o){return arguments.length===1?D1(n):new Ha(n,s,l,o??1)}function Ha(n,s,l,o){this.r=+n,this.g=+s,this.b=+l,this.opacity=+o}Pu(Ha,Eu,Tx(ml,{brighter(n){return n=n==null?Bo:Math.pow(Bo,n),new Ha(this.r*n,this.g*n,this.b*n,this.opacity)},darker(n){return n=n==null?il:Math.pow(il,n),new Ha(this.r*n,this.g*n,this.b*n,this.opacity)},rgb(){return this},clamp(){return new Ha(Ji(this.r),Ji(this.g),Ji(this.b),qo(this.opacity))},displayable(){return-.5<=this.r&&this.r<255.5&&-.5<=this.g&&this.g<255.5&&-.5<=this.b&&this.b<255.5&&0<=this.opacity&&this.opacity<=1},hex:cg,formatHex:cg,formatHex8:R1,formatRgb:dg,toString:dg}));function cg(){return`#${Zi(this.r)}${Zi(this.g)}${Zi(this.b)}`}function R1(){return`#${Zi(this.r)}${Zi(this.g)}${Zi(this.b)}${Zi((isNaN(this.opacity)?1:this.opacity)*255)}`}function dg(){const n=qo(this.opacity);return`${n===1?"rgb(":"rgba("}${Ji(this.r)}, ${Ji(this.g)}, ${Ji(this.b)}${n===1?")":`, ${n})`}`}function qo(n){return isNaN(n)?1:Math.max(0,Math.min(1,n))}function Ji(n){return Math.max(0,Math.min(255,Math.round(n)||0))}function Zi(n){return n=Ji(n),(n<16?"0":"")+n.toString(16)}function ug(n,s,l,o){return o<=0?n=s=l=NaN:l<=0||l>=1?n=s=NaN:s<=0&&(n=NaN),new jn(n,s,l,o)}function Cx(n){if(n instanceof jn)return new jn(n.h,n.s,n.l,n.opacity);if(n instanceof ml||(n=Wi(n)),!n)return new jn;if(n instanceof jn)return n;n=n.rgb();var s=n.r/255,l=n.g/255,o=n.b/255,d=Math.min(s,l,o),f=Math.max(s,l,o),m=NaN,p=f-d,g=(f+d)/2;return p?(s===f?m=(l-o)/p+(l<o)*6:l===f?m=(o-s)/p+2:m=(s-l)/p+4,p/=g<.5?f+d:2-f-d,m*=60):p=g>0&&g<1?0:m,new jn(m,p,g,n.opacity)}function O1(n,s,l,o){return arguments.length===1?Cx(n):new jn(n,s,l,o??1)}function jn(n,s,l,o){this.h=+n,this.s=+s,this.l=+l,this.opacity=+o}Pu(jn,O1,Tx(ml,{brighter(n){return n=n==null?Bo:Math.pow(Bo,n),new jn(this.h,this.s,this.l*n,this.opacity)},darker(n){return n=n==null?il:Math.pow(il,n),new jn(this.h,this.s,this.l*n,this.opacity)},rgb(){var n=this.h%360+(this.h<0)*360,s=isNaN(n)||isNaN(this.s)?0:this.s,l=this.l,o=l+(l<.5?l:1-l)*s,d=2*l-o;return new Ha(mu(n>=240?n-240:n+120,d,o),mu(n,d,o),mu(n<120?n+240:n-120,d,o),this.opacity)},clamp(){return new jn(fg(this.h),_o(this.s),_o(this.l),qo(this.opacity))},displayable(){return(0<=this.s&&this.s<=1||isNaN(this.s))&&0<=this.l&&this.l<=1&&0<=this.opacity&&this.opacity<=1},formatHsl(){const n=qo(this.opacity);return`${n===1?"hsl(":"hsla("}${fg(this.h)}, ${_o(this.s)*100}%, ${_o(this.l)*100}%${n===1?")":`, ${n})`}`}}));function fg(n){return n=(n||0)%360,n<0?n+360:n}function _o(n){return Math.max(0,Math.min(1,n||0))}function mu(n,s,l){return(n<60?s+(l-s)*n/60:n<180?l:n<240?s+(l-s)*(240-n)/60:s)*255}const Xu=n=>()=>n;function U1(n,s){return function(l){return n+l*s}}function L1(n,s,l){return n=Math.pow(n,l),s=Math.pow(s,l)-n,l=1/l,function(o){return Math.pow(n+o*s,l)}}function B1(n){return(n=+n)==1?Ax:function(s,l){return l-s?L1(s,l,n):Xu(isNaN(s)?l:s)}}function Ax(n,s){var l=s-n;return l?U1(n,l):Xu(isNaN(n)?s:n)}const Ho=(function n(s){var l=B1(s);function o(d,f){var m=l((d=Eu(d)).r,(f=Eu(f)).r),p=l(d.g,f.g),g=l(d.b,f.b),h=Ax(d.opacity,f.opacity);return function(x){return d.r=m(x),d.g=p(x),d.b=g(x),d.opacity=h(x),d+""}}return o.gamma=n,o})(1);function q1(n,s){s||(s=[]);var l=n?Math.min(s.length,n.length):0,o=s.slice(),d;return function(f){for(d=0;d<l;++d)o[d]=n[d]*(1-f)+s[d]*f;return o}}function H1(n){return ArrayBuffer.isView(n)&&!(n instanceof DataView)}function I1(n,s){var l=s?s.length:0,o=n?Math.min(l,n.length):0,d=new Array(o),f=new Array(l),m;for(m=0;m<o;++m)d[m]=ac(n[m],s[m]);for(;m<l;++m)f[m]=s[m];return function(p){for(m=0;m<o;++m)f[m]=d[m](p);return f}}function $1(n,s){var l=new Date;return n=+n,s=+s,function(o){return l.setTime(n*(1-o)+s*o),l}}function bn(n,s){return n=+n,s=+s,function(l){return n*(1-l)+s*l}}function F1(n,s){var l={},o={},d;(n===null||typeof n!="object")&&(n={}),(s===null||typeof s!="object")&&(s={});for(d in s)d in n?l[d]=ac(n[d],s[d]):o[d]=s[d];return function(f){for(d in l)o[d]=l[d](f);return o}}var Mu=/[-+]?(?:\d+\.?\d*|\.?\d+)(?:[eE][-+]?\d+)?/g,pu=new RegExp(Mu.source,"g");function Y1(n){return function(){return n}}function G1(n){return function(s){return n(s)+""}}function zx(n,s){var l=Mu.lastIndex=pu.lastIndex=0,o,d,f,m=-1,p=[],g=[];for(n=n+"",s=s+"";(o=Mu.exec(n))&&(d=pu.exec(s));)(f=d.index)>l&&(f=s.slice(l,f),p[m]?p[m]+=f:p[++m]=f),(o=o[0])===(d=d[0])?p[m]?p[m]+=d:p[++m]=d:(p[++m]=null,g.push({i:m,x:bn(o,d)})),l=pu.lastIndex;return l<s.length&&(f=s.slice(l),p[m]?p[m]+=f:p[++m]=f),p.length<2?g[0]?G1(g[0].x):Y1(s):(s=g.length,function(h){for(var x=0,v;x<s;++x)p[(v=g[x]).i]=v.x(h);return p.join("")})}function ac(n,s){var l=typeof s,o;return s==null||l==="boolean"?Xu(s):(l==="number"?bn:l==="string"?(o=Wi(s))?(s=o,Ho):zx:s instanceof Wi?Ho:s instanceof Date?$1:H1(s)?q1:Array.isArray(s)?I1:typeof s.valueOf!="function"&&typeof s.toString!="function"||isNaN(s)?F1:bn)(n,s)}function V1(n,s){return n=+n,s=+s,function(l){return Math.round(n*(1-l)+s*l)}}var hg=180/Math.PI,Du={translateX:0,translateY:0,rotate:0,skewX:0,scaleX:1,scaleY:1};function kx(n,s,l,o,d,f){var m,p,g;return(m=Math.sqrt(n*n+s*s))&&(n/=m,s/=m),(g=n*l+s*o)&&(l-=n*g,o-=s*g),(p=Math.sqrt(l*l+o*o))&&(l/=p,o/=p,g/=p),n*o<s*l&&(n=-n,s=-s,g=-g,m=-m),{translateX:d,translateY:f,rotate:Math.atan2(s,n)*hg,skewX:Math.atan(g)*hg,scaleX:m,scaleY:p}}var So;function P1(n){const s=new(typeof DOMMatrix=="function"?DOMMatrix:WebKitCSSMatrix)(n+"");return s.isIdentity?Du:kx(s.a,s.b,s.c,s.d,s.e,s.f)}function X1(n){return n==null||(So||(So=document.createElementNS("http://www.w3.org/2000/svg","g")),So.setAttribute("transform",n),!(n=So.transform.baseVal.consolidate()))?Du:(n=n.matrix,kx(n.a,n.b,n.c,n.d,n.e,n.f))}function Ex(n,s,l,o){function d(h){return h.length?h.pop()+" ":""}function f(h,x,v,b,_,C){if(h!==v||x!==b){var E=_.push("translate(",null,s,null,l);C.push({i:E-4,x:bn(h,v)},{i:E-2,x:bn(x,b)})}else(v||b)&&_.push("translate("+v+s+b+l)}function m(h,x,v,b){h!==x?(h-x>180?x+=360:x-h>180&&(h+=360),b.push({i:v.push(d(v)+"rotate(",null,o)-2,x:bn(h,x)})):x&&v.push(d(v)+"rotate("+x+o)}function p(h,x,v,b){h!==x?b.push({i:v.push(d(v)+"skewX(",null,o)-2,x:bn(h,x)}):x&&v.push(d(v)+"skewX("+x+o)}function g(h,x,v,b,_,C){if(h!==v||x!==b){var E=_.push(d(_)+"scale(",null,",",null,")");C.push({i:E-4,x:bn(h,v)},{i:E-2,x:bn(x,b)})}else(v!==1||b!==1)&&_.push(d(_)+"scale("+v+","+b+")")}return function(h,x){var v=[],b=[];return h=n(h),x=n(x),f(h.translateX,h.translateY,x.translateX,x.translateY,v,b),m(h.rotate,x.rotate,v,b),p(h.skewX,x.skewX,v,b),g(h.scaleX,h.scaleY,x.scaleX,x.scaleY,v,b),h=x=null,function(_){for(var C=-1,E=b.length,A;++C<E;)v[(A=b[C]).i]=A.x(_);return v.join("")}}}var Z1=Ex(P1,"px, ","px)","deg)"),Q1=Ex(X1,", ",")",")"),Gs=0,Zr=0,Yr=0,Mx=1e3,Io,Qr,$o=0,Ki=0,nc=0,rl=typeof performance=="object"&&performance.now?performance:Date,Dx=typeof window=="object"&&window.requestAnimationFrame?window.requestAnimationFrame.bind(window):function(n){setTimeout(n,17)};function Zu(){return Ki||(Dx(J1),Ki=rl.now()+nc)}function J1(){Ki=0}function Fo(){this._call=this._time=this._next=null}Fo.prototype=Qu.prototype={constructor:Fo,restart:function(n,s,l){if(typeof n!="function")throw new TypeError("callback is not a function");l=(l==null?Zu():+l)+(s==null?0:+s),!this._next&&Qr!==this&&(Qr?Qr._next=this:Io=this,Qr=this),this._call=n,this._time=l,Ru()},stop:function(){this._call&&(this._call=null,this._time=1/0,Ru())}};function Qu(n,s,l){var o=new Fo;return o.restart(n,s,l),o}function W1(){Zu(),++Gs;for(var n=Io,s;n;)(s=Ki-n._time)>=0&&n._call.call(void 0,s),n=n._next;--Gs}function mg(){Ki=($o=rl.now())+nc,Gs=Zr=0;try{W1()}finally{Gs=0,ew(),Ki=0}}function K1(){var n=rl.now(),s=n-$o;s>Mx&&(nc-=s,$o=n)}function ew(){for(var n,s=Io,l,o=1/0;s;)s._call?(o>s._time&&(o=s._time),n=s,s=s._next):(l=s._next,s._next=null,s=n?n._next=l:Io=l);Qr=n,Ru(o)}function Ru(n){if(!Gs){Zr&&(Zr=clearTimeout(Zr));var s=n-Ki;s>24?(n<1/0&&(Zr=setTimeout(mg,n-rl.now()-nc)),Yr&&(Yr=clearInterval(Yr))):(Yr||($o=rl.now(),Yr=setInterval(K1,Mx)),Gs=1,Dx(mg))}}function pg(n,s,l){var o=new Fo;return s=s==null?0:+s,o.restart(d=>{o.stop(),n(d+s)},s,l),o}var tw=ec("start","end","cancel","interrupt"),aw=[],Rx=0,gg=1,Ou=2,Mo=3,xg=4,Uu=5,Do=6;function ic(n,s,l,o,d,f){var m=n.__transition;if(!m)n.__transition={};else if(l in m)return;nw(n,l,{name:s,index:o,group:d,on:tw,tween:aw,time:f.time,delay:f.delay,duration:f.duration,ease:f.ease,timer:null,state:Rx})}function Ju(n,s){var l=wn(n,s);if(l.state>Rx)throw new Error("too late; already scheduled");return l}function kn(n,s){var l=wn(n,s);if(l.state>Mo)throw new Error("too late; already running");return l}function wn(n,s){var l=n.__transition;if(!l||!(l=l[s]))throw new Error("transition not found");return l}function nw(n,s,l){var o=n.__transition,d;o[s]=l,l.timer=Qu(f,0,l.time);function f(h){l.state=gg,l.timer.restart(m,l.delay,l.time),l.delay<=h&&m(h-l.delay)}function m(h){var x,v,b,_;if(l.state!==gg)return g();for(x in o)if(_=o[x],_.name===l.name){if(_.state===Mo)return pg(m);_.state===xg?(_.state=Do,_.timer.stop(),_.on.call("interrupt",n,n.__data__,_.index,_.group),delete o[x]):+x<s&&(_.state=Do,_.timer.stop(),_.on.call("cancel",n,n.__data__,_.index,_.group),delete o[x])}if(pg(function(){l.state===Mo&&(l.state=xg,l.timer.restart(p,l.delay,l.time),p(h))}),l.state=Ou,l.on.call("start",n,n.__data__,l.index,l.group),l.state===Ou){for(l.state=Mo,d=new Array(b=l.tween.length),x=0,v=-1;x<b;++x)(_=l.tween[x].value.call(n,n.__data__,l.index,l.group))&&(d[++v]=_);d.length=v+1}}function p(h){for(var x=h<l.duration?l.ease.call(null,h/l.duration):(l.timer.restart(g),l.state=Uu,1),v=-1,b=d.length;++v<b;)d[v].call(n,x);l.state===Uu&&(l.on.call("end",n,n.__data__,l.index,l.group),g())}function g(){l.state=Do,l.timer.stop(),delete o[s];for(var h in o)return;delete n.__transition}}function iw(n,s){var l=n.__transition,o,d,f=!0,m;if(l){s=s==null?null:s+"";for(m in l){if((o=l[m]).name!==s){f=!1;continue}d=o.state>Ou&&o.state<Uu,o.state=Do,o.timer.stop(),o.on.call(d?"interrupt":"cancel",n,n.__data__,o.index,o.group),delete l[m]}f&&delete n.__transition}}function sw(n){return this.each(function(){iw(this,n)})}function rw(n,s){var l,o;return function(){var d=kn(this,n),f=d.tween;if(f!==l){o=l=f;for(var m=0,p=o.length;m<p;++m)if(o[m].name===s){o=o.slice(),o.splice(m,1);break}}d.tween=o}}function lw(n,s,l){var o,d;if(typeof l!="function")throw new Error;return function(){var f=kn(this,n),m=f.tween;if(m!==o){d=(o=m).slice();for(var p={name:s,value:l},g=0,h=d.length;g<h;++g)if(d[g].name===s){d[g]=p;break}g===h&&d.push(p)}f.tween=d}}function ow(n,s){var l=this._id;if(n+="",arguments.length<2){for(var o=wn(this.node(),l).tween,d=0,f=o.length,m;d<f;++d)if((m=o[d]).name===n)return m.value;return null}return this.each((s==null?rw:lw)(l,n,s))}function Wu(n,s,l){var o=n._id;return n.each(function(){var d=kn(this,o);(d.value||(d.value={}))[s]=l.apply(this,arguments)}),function(d){return wn(d,o).value[s]}}function Ox(n,s){var l;return(typeof s=="number"?bn:s instanceof Wi?Ho:(l=Wi(s))?(s=l,Ho):zx)(n,s)}function cw(n){return function(){this.removeAttribute(n)}}function dw(n){return function(){this.removeAttributeNS(n.space,n.local)}}function uw(n,s,l){var o,d=l+"",f;return function(){var m=this.getAttribute(n);return m===d?null:m===o?f:f=s(o=m,l)}}function fw(n,s,l){var o,d=l+"",f;return function(){var m=this.getAttributeNS(n.space,n.local);return m===d?null:m===o?f:f=s(o=m,l)}}function hw(n,s,l){var o,d,f;return function(){var m,p=l(this),g;return p==null?void this.removeAttribute(n):(m=this.getAttribute(n),g=p+"",m===g?null:m===o&&g===d?f:(d=g,f=s(o=m,p)))}}function mw(n,s,l){var o,d,f;return function(){var m,p=l(this),g;return p==null?void this.removeAttributeNS(n.space,n.local):(m=this.getAttributeNS(n.space,n.local),g=p+"",m===g?null:m===o&&g===d?f:(d=g,f=s(o=m,p)))}}function pw(n,s){var l=tc(n),o=l==="transform"?Q1:Ox;return this.attrTween(n,typeof s=="function"?(l.local?mw:hw)(l,o,Wu(this,"attr."+n,s)):s==null?(l.local?dw:cw)(l):(l.local?fw:uw)(l,o,s))}function gw(n,s){return function(l){this.setAttribute(n,s.call(this,l))}}function xw(n,s){return function(l){this.setAttributeNS(n.space,n.local,s.call(this,l))}}function yw(n,s){var l,o;function d(){var f=s.apply(this,arguments);return f!==o&&(l=(o=f)&&xw(n,f)),l}return d._value=s,d}function vw(n,s){var l,o;function d(){var f=s.apply(this,arguments);return f!==o&&(l=(o=f)&&gw(n,f)),l}return d._value=s,d}function bw(n,s){var l="attr."+n;if(arguments.length<2)return(l=this.tween(l))&&l._value;if(s==null)return this.tween(l,null);if(typeof s!="function")throw new Error;var o=tc(n);return this.tween(l,(o.local?yw:vw)(o,s))}function jw(n,s){return function(){Ju(this,n).delay=+s.apply(this,arguments)}}function ww(n,s){return s=+s,function(){Ju(this,n).delay=s}}function Nw(n){var s=this._id;return arguments.length?this.each((typeof n=="function"?jw:ww)(s,n)):wn(this.node(),s).delay}function _w(n,s){return function(){kn(this,n).duration=+s.apply(this,arguments)}}function Sw(n,s){return s=+s,function(){kn(this,n).duration=s}}function Tw(n){var s=this._id;return arguments.length?this.each((typeof n=="function"?_w:Sw)(s,n)):wn(this.node(),s).duration}function Cw(n,s){if(typeof s!="function")throw new Error;return function(){kn(this,n).ease=s}}function Aw(n){var s=this._id;return arguments.length?this.each(Cw(s,n)):wn(this.node(),s).ease}function zw(n,s){return function(){var l=s.apply(this,arguments);if(typeof l!="function")throw new Error;kn(this,n).ease=l}}function kw(n){if(typeof n!="function")throw new Error;return this.each(zw(this._id,n))}function Ew(n){typeof n!="function"&&(n=xx(n));for(var s=this._groups,l=s.length,o=new Array(l),d=0;d<l;++d)for(var f=s[d],m=f.length,p=o[d]=[],g,h=0;h<m;++h)(g=f[h])&&n.call(g,g.__data__,h,f)&&p.push(g);return new ei(o,this._parents,this._name,this._id)}function Mw(n){if(n._id!==this._id)throw new Error;for(var s=this._groups,l=n._groups,o=s.length,d=l.length,f=Math.min(o,d),m=new Array(o),p=0;p<f;++p)for(var g=s[p],h=l[p],x=g.length,v=m[p]=new Array(x),b,_=0;_<x;++_)(b=g[_]||h[_])&&(v[_]=b);for(;p<o;++p)m[p]=s[p];return new ei(m,this._parents,this._name,this._id)}function Dw(n){return(n+"").trim().split(/^|\s+/).every(function(s){var l=s.indexOf(".");return l>=0&&(s=s.slice(0,l)),!s||s==="start"})}function Rw(n,s,l){var o,d,f=Dw(s)?Ju:kn;return function(){var m=f(this,n),p=m.on;p!==o&&(d=(o=p).copy()).on(s,l),m.on=d}}function Ow(n,s){var l=this._id;return arguments.length<2?wn(this.node(),l).on.on(n):this.each(Rw(l,n,s))}function Uw(n){return function(){var s=this.parentNode;for(var l in this.__transition)if(+l!==n)return;s&&s.removeChild(this)}}function Lw(){return this.on("end.remove",Uw(this._id))}function Bw(n){var s=this._name,l=this._id;typeof n!="function"&&(n=Yu(n));for(var o=this._groups,d=o.length,f=new Array(d),m=0;m<d;++m)for(var p=o[m],g=p.length,h=f[m]=new Array(g),x,v,b=0;b<g;++b)(x=p[b])&&(v=n.call(x,x.__data__,b,p))&&("__data__"in x&&(v.__data__=x.__data__),h[b]=v,ic(h[b],s,l,b,h,wn(x,l)));return new ei(f,this._parents,s,l)}function qw(n){var s=this._name,l=this._id;typeof n!="function"&&(n=gx(n));for(var o=this._groups,d=o.length,f=[],m=[],p=0;p<d;++p)for(var g=o[p],h=g.length,x,v=0;v<h;++v)if(x=g[v]){for(var b=n.call(x,x.__data__,v,g),_,C=wn(x,l),E=0,A=b.length;E<A;++E)(_=b[E])&&ic(_,s,l,E,b,C);f.push(b),m.push(x)}return new ei(f,m,s,l)}var Hw=hl.prototype.constructor;function Iw(){return new Hw(this._groups,this._parents)}function $w(n,s){var l,o,d;return function(){var f=Ys(this,n),m=(this.style.removeProperty(n),Ys(this,n));return f===m?null:f===l&&m===o?d:d=s(l=f,o=m)}}function Ux(n){return function(){this.style.removeProperty(n)}}function Fw(n,s,l){var o,d=l+"",f;return function(){var m=Ys(this,n);return m===d?null:m===o?f:f=s(o=m,l)}}function Yw(n,s,l){var o,d,f;return function(){var m=Ys(this,n),p=l(this),g=p+"";return p==null&&(g=p=(this.style.removeProperty(n),Ys(this,n))),m===g?null:m===o&&g===d?f:(d=g,f=s(o=m,p))}}function Gw(n,s){var l,o,d,f="style."+s,m="end."+f,p;return function(){var g=kn(this,n),h=g.on,x=g.value[f]==null?p||(p=Ux(s)):void 0;(h!==l||d!==x)&&(o=(l=h).copy()).on(m,d=x),g.on=o}}function Vw(n,s,l){var o=(n+="")=="transform"?Z1:Ox;return s==null?this.styleTween(n,$w(n,o)).on("end.style."+n,Ux(n)):typeof s=="function"?this.styleTween(n,Yw(n,o,Wu(this,"style."+n,s))).each(Gw(this._id,n)):this.styleTween(n,Fw(n,o,s),l).on("end.style."+n,null)}function Pw(n,s,l){return function(o){this.style.setProperty(n,s.call(this,o),l)}}function Xw(n,s,l){var o,d;function f(){var m=s.apply(this,arguments);return m!==d&&(o=(d=m)&&Pw(n,m,l)),o}return f._value=s,f}function Zw(n,s,l){var o="style."+(n+="");if(arguments.length<2)return(o=this.tween(o))&&o._value;if(s==null)return this.tween(o,null);if(typeof s!="function")throw new Error;return this.tween(o,Xw(n,s,l??""))}function Qw(n){return function(){this.textContent=n}}function Jw(n){return function(){var s=n(this);this.textContent=s??""}}function Ww(n){return this.tween("text",typeof n=="function"?Jw(Wu(this,"text",n)):Qw(n==null?"":n+""))}function Kw(n){return function(s){this.textContent=n.call(this,s)}}function eN(n){var s,l;function o(){var d=n.apply(this,arguments);return d!==l&&(s=(l=d)&&Kw(d)),s}return o._value=n,o}function tN(n){var s="text";if(arguments.length<1)return(s=this.tween(s))&&s._value;if(n==null)return this.tween(s,null);if(typeof n!="function")throw new Error;return this.tween(s,eN(n))}function aN(){for(var n=this._name,s=this._id,l=Lx(),o=this._groups,d=o.length,f=0;f<d;++f)for(var m=o[f],p=m.length,g,h=0;h<p;++h)if(g=m[h]){var x=wn(g,s);ic(g,n,l,h,m,{time:x.time+x.delay+x.duration,delay:0,duration:x.duration,ease:x.ease})}return new ei(o,this._parents,n,l)}function nN(){var n,s,l=this,o=l._id,d=l.size();return new Promise(function(f,m){var p={value:m},g={value:function(){--d===0&&f()}};l.each(function(){var h=kn(this,o),x=h.on;x!==n&&(s=(n=x).copy(),s._.cancel.push(p),s._.interrupt.push(p),s._.end.push(g)),h.on=s}),d===0&&f()})}var iN=0;function ei(n,s,l,o){this._groups=n,this._parents=s,this._name=l,this._id=o}function Lx(){return++iN}var Jn=hl.prototype;ei.prototype={constructor:ei,select:Bw,selectAll:qw,selectChild:Jn.selectChild,selectChildren:Jn.selectChildren,filter:Ew,merge:Mw,selection:Iw,transition:aN,call:Jn.call,nodes:Jn.nodes,node:Jn.node,size:Jn.size,empty:Jn.empty,each:Jn.each,on:Ow,attr:pw,attrTween:bw,style:Vw,styleTween:Zw,text:Ww,textTween:tN,remove:Lw,tween:ow,delay:Nw,duration:Tw,ease:Aw,easeVarying:kw,end:nN,[Symbol.iterator]:Jn[Symbol.iterator]};function sN(n){return((n*=2)<=1?n*n*n:(n-=2)*n*n+2)/2}var rN={time:null,delay:0,duration:250,ease:sN};function lN(n,s){for(var l;!(l=n.__transition)||!(l=l[s]);)if(!(n=n.parentNode))throw new Error(`transition ${s} not found`);return l}function oN(n){var s,l;n instanceof ei?(s=n._id,n=n._name):(s=Lx(),(l=rN).time=Zu(),n=n==null?null:n+"");for(var o=this._groups,d=o.length,f=0;f<d;++f)for(var m=o[f],p=m.length,g,h=0;h<p;++h)(g=m[h])&&ic(g,n,s,h,m,l||lN(g,s));return new ei(o,this._parents,n,s)}hl.prototype.interrupt=sw;hl.prototype.transition=oN;const Lu=Math.PI,Bu=2*Lu,Xi=1e-6,cN=Bu-Xi;function Bx(n){this._+=n[0];for(let s=1,l=n.length;s<l;++s)this._+=arguments[s]+n[s]}function dN(n){let s=Math.floor(n);if(!(s>=0))throw new Error(`invalid digits: ${n}`);if(s>15)return Bx;const l=10**s;return function(o){this._+=o[0];for(let d=1,f=o.length;d<f;++d)this._+=Math.round(arguments[d]*l)/l+o[d]}}class uN{constructor(s){this._x0=this._y0=this._x1=this._y1=null,this._="",this._append=s==null?Bx:dN(s)}moveTo(s,l){this._append`M${this._x0=this._x1=+s},${this._y0=this._y1=+l}`}closePath(){this._x1!==null&&(this._x1=this._x0,this._y1=this._y0,this._append`Z`)}lineTo(s,l){this._append`L${this._x1=+s},${this._y1=+l}`}quadraticCurveTo(s,l,o,d){this._append`Q${+s},${+l},${this._x1=+o},${this._y1=+d}`}bezierCurveTo(s,l,o,d,f,m){this._append`C${+s},${+l},${+o},${+d},${this._x1=+f},${this._y1=+m}`}arcTo(s,l,o,d,f){if(s=+s,l=+l,o=+o,d=+d,f=+f,f<0)throw new Error(`negative radius: ${f}`);let m=this._x1,p=this._y1,g=o-s,h=d-l,x=m-s,v=p-l,b=x*x+v*v;if(this._x1===null)this._append`M${this._x1=s},${this._y1=l}`;else if(b>Xi)if(!(Math.abs(v*g-h*x)>Xi)||!f)this._append`L${this._x1=s},${this._y1=l}`;else{let _=o-m,C=d-p,E=g*g+h*h,A=_*_+C*C,L=Math.sqrt(E),q=Math.sqrt(b),P=f*Math.tan((Lu-Math.acos((E+b-A)/(2*L*q)))/2),M=P/q,X=P/L;Math.abs(M-1)>Xi&&this._append`L${s+M*x},${l+M*v}`,this._append`A${f},${f},0,0,${+(v*_>x*C)},${this._x1=s+X*g},${this._y1=l+X*h}`}}arc(s,l,o,d,f,m){if(s=+s,l=+l,o=+o,m=!!m,o<0)throw new Error(`negative radius: ${o}`);let p=o*Math.cos(d),g=o*Math.sin(d),h=s+p,x=l+g,v=1^m,b=m?d-f:f-d;this._x1===null?this._append`M${h},${x}`:(Math.abs(this._x1-h)>Xi||Math.abs(this._y1-x)>Xi)&&this._append`L${h},${x}`,o&&(b<0&&(b=b%Bu+Bu),b>cN?this._append`A${o},${o},0,1,${v},${s-p},${l-g}A${o},${o},0,1,${v},${this._x1=h},${this._y1=x}`:b>Xi&&this._append`A${o},${o},0,${+(b>=Lu)},${v},${this._x1=s+o*Math.cos(f)},${this._y1=l+o*Math.sin(f)}`)}rect(s,l,o,d){this._append`M${this._x0=this._x1=+s},${this._y0=this._y1=+l}h${o=+o}v${+d}h${-o}Z`}toString(){return this._}}function fN(n,s){var l,o=1;n==null&&(n=0),s==null&&(s=0);function d(){var f,m=l.length,p,g=0,h=0;for(f=0;f<m;++f)p=l[f],g+=p.x,h+=p.y;for(g=(g/m-n)*o,h=(h/m-s)*o,f=0;f<m;++f)p=l[f],p.x-=g,p.y-=h}return d.initialize=function(f){l=f},d.x=function(f){return arguments.length?(n=+f,d):n},d.y=function(f){return arguments.length?(s=+f,d):s},d.strength=function(f){return arguments.length?(o=+f,d):o},d}function hN(n){const s=+this._x.call(null,n),l=+this._y.call(null,n);return qx(this.cover(s,l),s,l,n)}function qx(n,s,l,o){if(isNaN(s)||isNaN(l))return n;var d,f=n._root,m={data:o},p=n._x0,g=n._y0,h=n._x1,x=n._y1,v,b,_,C,E,A,L,q;if(!f)return n._root=m,n;for(;f.length;)if((E=s>=(v=(p+h)/2))?p=v:h=v,(A=l>=(b=(g+x)/2))?g=b:x=b,d=f,!(f=f[L=A<<1|E]))return d[L]=m,n;if(_=+n._x.call(null,f.data),C=+n._y.call(null,f.data),s===_&&l===C)return m.next=f,d?d[L]=m:n._root=m,n;do d=d?d[L]=new Array(4):n._root=new Array(4),(E=s>=(v=(p+h)/2))?p=v:h=v,(A=l>=(b=(g+x)/2))?g=b:x=b;while((L=A<<1|E)===(q=(C>=b)<<1|_>=v));return d[q]=f,d[L]=m,n}function mN(n){var s,l,o=n.length,d,f,m=new Array(o),p=new Array(o),g=1/0,h=1/0,x=-1/0,v=-1/0;for(l=0;l<o;++l)isNaN(d=+this._x.call(null,s=n[l]))||isNaN(f=+this._y.call(null,s))||(m[l]=d,p[l]=f,d<g&&(g=d),d>x&&(x=d),f<h&&(h=f),f>v&&(v=f));if(g>x||h>v)return this;for(this.cover(g,h).cover(x,v),l=0;l<o;++l)qx(this,m[l],p[l],n[l]);return this}function pN(n,s){if(isNaN(n=+n)||isNaN(s=+s))return this;var l=this._x0,o=this._y0,d=this._x1,f=this._y1;if(isNaN(l))d=(l=Math.floor(n))+1,f=(o=Math.floor(s))+1;else{for(var m=d-l||1,p=this._root,g,h;l>n||n>=d||o>s||s>=f;)switch(h=(s<o)<<1|n<l,g=new Array(4),g[h]=p,p=g,m*=2,h){case 0:d=l+m,f=o+m;break;case 1:l=d-m,f=o+m;break;case 2:d=l+m,o=f-m;break;case 3:l=d-m,o=f-m;break}this._root&&this._root.length&&(this._root=p)}return this._x0=l,this._y0=o,this._x1=d,this._y1=f,this}function gN(){var n=[];return this.visit(function(s){if(!s.length)do n.push(s.data);while(s=s.next)}),n}function xN(n){return arguments.length?this.cover(+n[0][0],+n[0][1]).cover(+n[1][0],+n[1][1]):isNaN(this._x0)?void 0:[[this._x0,this._y0],[this._x1,this._y1]]}function ka(n,s,l,o,d){this.node=n,this.x0=s,this.y0=l,this.x1=o,this.y1=d}function yN(n,s,l){var o,d=this._x0,f=this._y0,m,p,g,h,x=this._x1,v=this._y1,b=[],_=this._root,C,E;for(_&&b.push(new ka(_,d,f,x,v)),l==null?l=1/0:(d=n-l,f=s-l,x=n+l,v=s+l,l*=l);C=b.pop();)if(!(!(_=C.node)||(m=C.x0)>x||(p=C.y0)>v||(g=C.x1)<d||(h=C.y1)<f))if(_.length){var A=(m+g)/2,L=(p+h)/2;b.push(new ka(_[3],A,L,g,h),new ka(_[2],m,L,A,h),new ka(_[1],A,p,g,L),new ka(_[0],m,p,A,L)),(E=(s>=L)<<1|n>=A)&&(C=b[b.length-1],b[b.length-1]=b[b.length-1-E],b[b.length-1-E]=C)}else{var q=n-+this._x.call(null,_.data),P=s-+this._y.call(null,_.data),M=q*q+P*P;if(M<l){var X=Math.sqrt(l=M);d=n-X,f=s-X,x=n+X,v=s+X,o=_.data}}return o}function vN(n){if(isNaN(x=+this._x.call(null,n))||isNaN(v=+this._y.call(null,n)))return this;var s,l=this._root,o,d,f,m=this._x0,p=this._y0,g=this._x1,h=this._y1,x,v,b,_,C,E,A,L;if(!l)return this;if(l.length)for(;;){if((C=x>=(b=(m+g)/2))?m=b:g=b,(E=v>=(_=(p+h)/2))?p=_:h=_,s=l,!(l=l[A=E<<1|C]))return this;if(!l.length)break;(s[A+1&3]||s[A+2&3]||s[A+3&3])&&(o=s,L=A)}for(;l.data!==n;)if(d=l,!(l=l.next))return this;return(f=l.next)&&delete l.next,d?(f?d.next=f:delete d.next,this):s?(f?s[A]=f:delete s[A],(l=s[0]||s[1]||s[2]||s[3])&&l===(s[3]||s[2]||s[1]||s[0])&&!l.length&&(o?o[L]=l:this._root=l),this):(this._root=f,this)}function bN(n){for(var s=0,l=n.length;s<l;++s)this.remove(n[s]);return this}function jN(){return this._root}function wN(){var n=0;return this.visit(function(s){if(!s.length)do++n;while(s=s.next)}),n}function NN(n){var s=[],l,o=this._root,d,f,m,p,g;for(o&&s.push(new ka(o,this._x0,this._y0,this._x1,this._y1));l=s.pop();)if(!n(o=l.node,f=l.x0,m=l.y0,p=l.x1,g=l.y1)&&o.length){var h=(f+p)/2,x=(m+g)/2;(d=o[3])&&s.push(new ka(d,h,x,p,g)),(d=o[2])&&s.push(new ka(d,f,x,h,g)),(d=o[1])&&s.push(new ka(d,h,m,p,x)),(d=o[0])&&s.push(new ka(d,f,m,h,x))}return this}function _N(n){var s=[],l=[],o;for(this._root&&s.push(new ka(this._root,this._x0,this._y0,this._x1,this._y1));o=s.pop();){var d=o.node;if(d.length){var f,m=o.x0,p=o.y0,g=o.x1,h=o.y1,x=(m+g)/2,v=(p+h)/2;(f=d[0])&&s.push(new ka(f,m,p,x,v)),(f=d[1])&&s.push(new ka(f,x,p,g,v)),(f=d[2])&&s.push(new ka(f,m,v,x,h)),(f=d[3])&&s.push(new ka(f,x,v,g,h))}l.push(o)}for(;o=l.pop();)n(o.node,o.x0,o.y0,o.x1,o.y1);return this}function SN(n){return n[0]}function TN(n){return arguments.length?(this._x=n,this):this._x}function CN(n){return n[1]}function AN(n){return arguments.length?(this._y=n,this):this._y}function Hx(n,s,l){var o=new Ku(s??SN,l??CN,NaN,NaN,NaN,NaN);return n==null?o:o.addAll(n)}function Ku(n,s,l,o,d,f){this._x=n,this._y=s,this._x0=l,this._y0=o,this._x1=d,this._y1=f,this._root=void 0}function yg(n){for(var s={data:n.data},l=s;n=n.next;)l=l.next={data:n.data};return s}var Ma=Hx.prototype=Ku.prototype;Ma.copy=function(){var n=new Ku(this._x,this._y,this._x0,this._y0,this._x1,this._y1),s=this._root,l,o;if(!s)return n;if(!s.length)return n._root=yg(s),n;for(l=[{source:s,target:n._root=new Array(4)}];s=l.pop();)for(var d=0;d<4;++d)(o=s.source[d])&&(o.length?l.push({source:o,target:s.target[d]=new Array(4)}):s.target[d]=yg(o));return n};Ma.add=hN;Ma.addAll=mN;Ma.cover=pN;Ma.data=gN;Ma.extent=xN;Ma.find=yN;Ma.remove=vN;Ma.removeAll=bN;Ma.root=jN;Ma.size=wN;Ma.visit=NN;Ma.visitAfter=_N;Ma.x=TN;Ma.y=AN;function Wr(n){return function(){return n}}function Ls(n){return(n()-.5)*1e-6}function zN(n){return n.index}function vg(n,s){var l=n.get(s);if(!l)throw new Error("node not found: "+s);return l}function kN(n){var s=zN,l=v,o,d=Wr(30),f,m,p,g,h,x=1;n==null&&(n=[]);function v(A){return 1/Math.min(p[A.source.index],p[A.target.index])}function b(A){for(var L=0,q=n.length;L<x;++L)for(var P=0,M,X,Q,K,se,Ae,we;P<q;++P)M=n[P],X=M.source,Q=M.target,K=Q.x+Q.vx-X.x-X.vx||Ls(h),se=Q.y+Q.vy-X.y-X.vy||Ls(h),Ae=Math.sqrt(K*K+se*se),Ae=(Ae-f[P])/Ae*A*o[P],K*=Ae,se*=Ae,Q.vx-=K*(we=g[P]),Q.vy-=se*we,X.vx+=K*(we=1-we),X.vy+=se*we}function _(){if(m){var A,L=m.length,q=n.length,P=new Map(m.map((X,Q)=>[s(X,Q,m),X])),M;for(A=0,p=new Array(L);A<q;++A)M=n[A],M.index=A,typeof M.source!="object"&&(M.source=vg(P,M.source)),typeof M.target!="object"&&(M.target=vg(P,M.target)),p[M.source.index]=(p[M.source.index]||0)+1,p[M.target.index]=(p[M.target.index]||0)+1;for(A=0,g=new Array(q);A<q;++A)M=n[A],g[A]=p[M.source.index]/(p[M.source.index]+p[M.target.index]);o=new Array(q),C(),f=new Array(q),E()}}function C(){if(m)for(var A=0,L=n.length;A<L;++A)o[A]=+l(n[A],A,n)}function E(){if(m)for(var A=0,L=n.length;A<L;++A)f[A]=+d(n[A],A,n)}return b.initialize=function(A,L){m=A,h=L,_()},b.links=function(A){return arguments.length?(n=A,_(),b):n},b.id=function(A){return arguments.length?(s=A,b):s},b.iterations=function(A){return arguments.length?(x=+A,b):x},b.strength=function(A){return arguments.length?(l=typeof A=="function"?A:Wr(+A),C(),b):l},b.distance=function(A){return arguments.length?(d=typeof A=="function"?A:Wr(+A),E(),b):d},b}const EN=1664525,MN=1013904223,bg=4294967296;function DN(){let n=1;return()=>(n=(EN*n+MN)%bg)/bg}function RN(n){return n.x}function ON(n){return n.y}var UN=10,LN=Math.PI*(3-Math.sqrt(5));function BN(n){var s,l=1,o=.001,d=1-Math.pow(o,1/300),f=0,m=.6,p=new Map,g=Qu(v),h=ec("tick","end"),x=DN();n==null&&(n=[]);function v(){b(),h.call("tick",s),l<o&&(g.stop(),h.call("end",s))}function b(E){var A,L=n.length,q;E===void 0&&(E=1);for(var P=0;P<E;++P)for(l+=(f-l)*d,p.forEach(function(M){M(l)}),A=0;A<L;++A)q=n[A],q.fx==null?q.x+=q.vx*=m:(q.x=q.fx,q.vx=0),q.fy==null?q.y+=q.vy*=m:(q.y=q.fy,q.vy=0);return s}function _(){for(var E=0,A=n.length,L;E<A;++E){if(L=n[E],L.index=E,L.fx!=null&&(L.x=L.fx),L.fy!=null&&(L.y=L.fy),isNaN(L.x)||isNaN(L.y)){var q=UN*Math.sqrt(.5+E),P=E*LN;L.x=q*Math.cos(P),L.y=q*Math.sin(P)}(isNaN(L.vx)||isNaN(L.vy))&&(L.vx=L.vy=0)}}function C(E){return E.initialize&&E.initialize(n,x),E}return _(),s={tick:b,restart:function(){return g.restart(v),s},stop:function(){return g.stop(),s},nodes:function(E){return arguments.length?(n=E,_(),p.forEach(C),s):n},alpha:function(E){return arguments.length?(l=+E,s):l},alphaMin:function(E){return arguments.length?(o=+E,s):o},alphaDecay:function(E){return arguments.length?(d=+E,s):+d},alphaTarget:function(E){return arguments.length?(f=+E,s):f},velocityDecay:function(E){return arguments.length?(m=1-E,s):1-m},randomSource:function(E){return arguments.length?(x=E,p.forEach(C),s):x},force:function(E,A){return arguments.length>1?(A==null?p.delete(E):p.set(E,C(A)),s):p.get(E)},find:function(E,A,L){var q=0,P=n.length,M,X,Q,K,se;for(L==null?L=1/0:L*=L,q=0;q<P;++q)K=n[q],M=E-K.x,X=A-K.y,Q=M*M+X*X,Q<L&&(se=K,L=Q);return se},on:function(E,A){return arguments.length>1?(h.on(E,A),s):h.on(E)}}}function qN(){var n,s,l,o,d=Wr(-30),f,m=1,p=1/0,g=.81;function h(_){var C,E=n.length,A=Hx(n,RN,ON).visitAfter(v);for(o=_,C=0;C<E;++C)s=n[C],A.visit(b)}function x(){if(n){var _,C=n.length,E;for(f=new Array(C),_=0;_<C;++_)E=n[_],f[E.index]=+d(E,_,n)}}function v(_){var C=0,E,A,L=0,q,P,M;if(_.length){for(q=P=M=0;M<4;++M)(E=_[M])&&(A=Math.abs(E.value))&&(C+=E.value,L+=A,q+=A*E.x,P+=A*E.y);_.x=q/L,_.y=P/L}else{E=_,E.x=E.data.x,E.y=E.data.y;do C+=f[E.data.index];while(E=E.next)}_.value=C}function b(_,C,E,A){if(!_.value)return!0;var L=_.x-s.x,q=_.y-s.y,P=A-C,M=L*L+q*q;if(P*P/g<M)return M<p&&(L===0&&(L=Ls(l),M+=L*L),q===0&&(q=Ls(l),M+=q*q),M<m&&(M=Math.sqrt(m*M)),s.vx+=L*_.value*o/M,s.vy+=q*_.value*o/M),!0;if(_.length||M>=p)return;(_.data!==s||_.next)&&(L===0&&(L=Ls(l),M+=L*L),q===0&&(q=Ls(l),M+=q*q),M<m&&(M=Math.sqrt(m*M)));do _.data!==s&&(P=f[_.data.index]*o/M,s.vx+=L*P,s.vy+=q*P);while(_=_.next)}return h.initialize=function(_,C){n=_,l=C,x()},h.strength=function(_){return arguments.length?(d=typeof _=="function"?_:Wr(+_),x(),h):d},h.distanceMin=function(_){return arguments.length?(m=_*_,h):Math.sqrt(m)},h.distanceMax=function(_){return arguments.length?(p=_*_,h):Math.sqrt(p)},h.theta=function(_){return arguments.length?(g=_*_,h):Math.sqrt(g)},h}function HN(n){return Math.abs(n=Math.round(n))>=1e21?n.toLocaleString("en").replace(/,/g,""):n.toString(10)}function Yo(n,s){if((l=(n=s?n.toExponential(s-1):n.toExponential()).indexOf("e"))<0)return null;var l,o=n.slice(0,l);return[o.length>1?o[0]+o.slice(2):o,+n.slice(l+1)]}function Vs(n){return n=Yo(Math.abs(n)),n?n[1]:NaN}function IN(n,s){return function(l,o){for(var d=l.length,f=[],m=0,p=n[0],g=0;d>0&&p>0&&(g+p+1>o&&(p=Math.max(1,o-g)),f.push(l.substring(d-=p,d+p)),!((g+=p+1)>o));)p=n[m=(m+1)%n.length];return f.reverse().join(s)}}function $N(n){return function(s){return s.replace(/[0-9]/g,function(l){return n[+l]})}}var FN=/^(?:(.)?([<>=^]))?([+\-( ])?([$#])?(0)?(\d+)?(,)?(\.\d+)?(~)?([a-z%])?$/i;function Go(n){if(!(s=FN.exec(n)))throw new Error("invalid format: "+n);var s;return new ef({fill:s[1],align:s[2],sign:s[3],symbol:s[4],zero:s[5],width:s[6],comma:s[7],precision:s[8]&&s[8].slice(1),trim:s[9],type:s[10]})}Go.prototype=ef.prototype;function ef(n){this.fill=n.fill===void 0?" ":n.fill+"",this.align=n.align===void 0?">":n.align+"",this.sign=n.sign===void 0?"-":n.sign+"",this.symbol=n.symbol===void 0?"":n.symbol+"",this.zero=!!n.zero,this.width=n.width===void 0?void 0:+n.width,this.comma=!!n.comma,this.precision=n.precision===void 0?void 0:+n.precision,this.trim=!!n.trim,this.type=n.type===void 0?"":n.type+""}ef.prototype.toString=function(){return this.fill+this.align+this.sign+this.symbol+(this.zero?"0":"")+(this.width===void 0?"":Math.max(1,this.width|0))+(this.comma?",":"")+(this.precision===void 0?"":"."+Math.max(0,this.precision|0))+(this.trim?"~":"")+this.type};function YN(n){e:for(var s=n.length,l=1,o=-1,d;l<s;++l)switch(n[l]){case".":o=d=l;break;case"0":o===0&&(o=l),d=l;break;default:if(!+n[l])break e;o>0&&(o=0);break}return o>0?n.slice(0,o)+n.slice(d+1):n}var Ix;function GN(n,s){var l=Yo(n,s);if(!l)return n+"";var o=l[0],d=l[1],f=d-(Ix=Math.max(-8,Math.min(8,Math.floor(d/3)))*3)+1,m=o.length;return f===m?o:f>m?o+new Array(f-m+1).join("0"):f>0?o.slice(0,f)+"."+o.slice(f):"0."+new Array(1-f).join("0")+Yo(n,Math.max(0,s+f-1))[0]}function jg(n,s){var l=Yo(n,s);if(!l)return n+"";var o=l[0],d=l[1];return d<0?"0."+new Array(-d).join("0")+o:o.length>d+1?o.slice(0,d+1)+"."+o.slice(d+1):o+new Array(d-o.length+2).join("0")}const wg={"%":(n,s)=>(n*100).toFixed(s),b:n=>Math.round(n).toString(2),c:n=>n+"",d:HN,e:(n,s)=>n.toExponential(s),f:(n,s)=>n.toFixed(s),g:(n,s)=>n.toPrecision(s),o:n=>Math.round(n).toString(8),p:(n,s)=>jg(n*100,s),r:jg,s:GN,X:n=>Math.round(n).toString(16).toUpperCase(),x:n=>Math.round(n).toString(16)};function Ng(n){return n}var _g=Array.prototype.map,Sg=["y","z","a","f","p","n","µ","m","","k","M","G","T","P","E","Z","Y"];function VN(n){var s=n.grouping===void 0||n.thousands===void 0?Ng:IN(_g.call(n.grouping,Number),n.thousands+""),l=n.currency===void 0?"":n.currency[0]+"",o=n.currency===void 0?"":n.currency[1]+"",d=n.decimal===void 0?".":n.decimal+"",f=n.numerals===void 0?Ng:$N(_g.call(n.numerals,String)),m=n.percent===void 0?"%":n.percent+"",p=n.minus===void 0?"−":n.minus+"",g=n.nan===void 0?"NaN":n.nan+"";function h(v){v=Go(v);var b=v.fill,_=v.align,C=v.sign,E=v.symbol,A=v.zero,L=v.width,q=v.comma,P=v.precision,M=v.trim,X=v.type;X==="n"?(q=!0,X="g"):wg[X]||(P===void 0&&(P=12),M=!0,X="g"),(A||b==="0"&&_==="=")&&(A=!0,b="0",_="=");var Q=E==="$"?l:E==="#"&&/[boxX]/.test(X)?"0"+X.toLowerCase():"",K=E==="$"?o:/[%p]/.test(X)?m:"",se=wg[X],Ae=/[defgprs%]/.test(X);P=P===void 0?6:/[gprs]/.test(X)?Math.max(1,Math.min(21,P)):Math.max(0,Math.min(20,P));function we(ge){var Ne=Q,me=K,xe,He,S;if(X==="c")me=se(ge)+me,ge="";else{ge=+ge;var H=ge<0||1/ge<0;if(ge=isNaN(ge)?g:se(Math.abs(ge),P),M&&(ge=YN(ge)),H&&+ge==0&&C!=="+"&&(H=!1),Ne=(H?C==="("?C:p:C==="-"||C==="("?"":C)+Ne,me=(X==="s"?Sg[8+Ix/3]:"")+me+(H&&C==="("?")":""),Ae){for(xe=-1,He=ge.length;++xe<He;)if(S=ge.charCodeAt(xe),48>S||S>57){me=(S===46?d+ge.slice(xe+1):ge.slice(xe))+me,ge=ge.slice(0,xe);break}}}q&&!A&&(ge=s(ge,1/0));var F=Ne.length+ge.length+me.length,_e=F<L?new Array(L-F+1).join(b):"";switch(q&&A&&(ge=s(_e+ge,_e.length?L-me.length:1/0),_e=""),_){case"<":ge=Ne+ge+me+_e;break;case"=":ge=Ne+_e+ge+me;break;case"^":ge=_e.slice(0,F=_e.length>>1)+Ne+ge+me+_e.slice(F);break;default:ge=_e+Ne+ge+me;break}return f(ge)}return we.toString=function(){return v+""},we}function x(v,b){var _=h((v=Go(v),v.type="f",v)),C=Math.max(-8,Math.min(8,Math.floor(Vs(b)/3)))*3,E=Math.pow(10,-C),A=Sg[8+C/3];return function(L){return _(E*L)+A}}return{format:h,formatPrefix:x}}var To,$x,Fx;PN({thousands:",",grouping:[3],currency:["$",""]});function PN(n){return To=VN(n),$x=To.format,Fx=To.formatPrefix,To}function XN(n){return Math.max(0,-Vs(Math.abs(n)))}function ZN(n,s){return Math.max(0,Math.max(-8,Math.min(8,Math.floor(Vs(s)/3)))*3-Vs(Math.abs(n)))}function QN(n,s){return n=Math.abs(n),s=Math.abs(s)-n,Math.max(0,Vs(s)-Vs(n))+1}function sc(n,s){switch(arguments.length){case 0:break;case 1:this.range(n);break;default:this.range(s).domain(n);break}return this}const Tg=Symbol("implicit");function Vo(){var n=new Kp,s=[],l=[],o=Tg;function d(f){let m=n.get(f);if(m===void 0){if(o!==Tg)return o;n.set(f,m=s.push(f)-1)}return l[m%l.length]}return d.domain=function(f){if(!arguments.length)return s.slice();s=[],n=new Kp;for(const m of f)n.has(m)||n.set(m,s.push(m)-1);return d},d.range=function(f){return arguments.length?(l=Array.from(f),d):l.slice()},d.unknown=function(f){return arguments.length?(o=f,d):o},d.copy=function(){return Vo(s,l).unknown(o)},sc.apply(d,arguments),d}function tf(){var n=Vo().unknown(void 0),s=n.domain,l=n.range,o=0,d=1,f,m,p=!1,g=0,h=0,x=.5;delete n.unknown;function v(){var b=s().length,_=d<o,C=_?d:o,E=_?o:d;f=(E-C)/Math.max(1,b-g+h*2),p&&(f=Math.floor(f)),C+=(E-C-f*(b-g))*x,m=f*(1-g),p&&(C=Math.round(C),m=Math.round(m));var A=Cb(b).map(function(L){return C+f*L});return l(_?A.reverse():A)}return n.domain=function(b){return arguments.length?(s(b),v()):s()},n.range=function(b){return arguments.length?([o,d]=b,o=+o,d=+d,v()):[o,d]},n.rangeRound=function(b){return[o,d]=b,o=+o,d=+d,p=!0,v()},n.bandwidth=function(){return m},n.step=function(){return f},n.round=function(b){return arguments.length?(p=!!b,v()):p},n.padding=function(b){return arguments.length?(g=Math.min(1,h=+b),v()):g},n.paddingInner=function(b){return arguments.length?(g=Math.min(1,b),v()):g},n.paddingOuter=function(b){return arguments.length?(h=+b,v()):h},n.align=function(b){return arguments.length?(x=Math.max(0,Math.min(1,b)),v()):x},n.copy=function(){return tf(s(),[o,d]).round(p).paddingInner(g).paddingOuter(h).align(x)},sc.apply(v(),arguments)}function Yx(n){var s=n.copy;return n.padding=n.paddingOuter,delete n.paddingInner,delete n.paddingOuter,n.copy=function(){return Yx(s())},n}function JN(){return Yx(tf.apply(null,arguments).paddingInner(1))}function WN(n){return function(){return n}}function KN(n){return+n}var Cg=[0,1];function Bs(n){return n}function qu(n,s){return(s-=n=+n)?function(l){return(l-n)/s}:WN(isNaN(s)?NaN:.5)}function e_(n,s){var l;return n>s&&(l=n,n=s,s=l),function(o){return Math.max(n,Math.min(s,o))}}function t_(n,s,l){var o=n[0],d=n[1],f=s[0],m=s[1];return d<o?(o=qu(d,o),f=l(m,f)):(o=qu(o,d),f=l(f,m)),function(p){return f(o(p))}}function a_(n,s,l){var o=Math.min(n.length,s.length)-1,d=new Array(o),f=new Array(o),m=-1;for(n[o]<n[0]&&(n=n.slice().reverse(),s=s.slice().reverse());++m<o;)d[m]=qu(n[m],n[m+1]),f[m]=l(s[m],s[m+1]);return function(p){var g=vb(n,p,1,o)-1;return f[g](d[g](p))}}function Gx(n,s){return s.domain(n.domain()).range(n.range()).interpolate(n.interpolate()).clamp(n.clamp()).unknown(n.unknown())}function n_(){var n=Cg,s=Cg,l=ac,o,d,f,m=Bs,p,g,h;function x(){var b=Math.min(n.length,s.length);return m!==Bs&&(m=e_(n[0],n[b-1])),p=b>2?a_:t_,g=h=null,v}function v(b){return b==null||isNaN(b=+b)?f:(g||(g=p(n.map(o),s,l)))(o(m(b)))}return v.invert=function(b){return m(d((h||(h=p(s,n.map(o),bn)))(b)))},v.domain=function(b){return arguments.length?(n=Array.from(b,KN),x()):n.slice()},v.range=function(b){return arguments.length?(s=Array.from(b),x()):s.slice()},v.rangeRound=function(b){return s=Array.from(b),l=V1,x()},v.clamp=function(b){return arguments.length?(m=b?!0:Bs,x()):m!==Bs},v.interpolate=function(b){return arguments.length?(l=b,x()):l},v.unknown=function(b){return arguments.length?(f=b,v):f},function(b,_){return o=b,d=_,x()}}function Vx(){return n_()(Bs,Bs)}function i_(n,s,l,o){var d=Cu(n,s,l),f;switch(o=Go(o??",f"),o.type){case"s":{var m=Math.max(Math.abs(n),Math.abs(s));return o.precision==null&&!isNaN(f=ZN(d,m))&&(o.precision=f),Fx(o,m)}case"":case"e":case"g":case"p":case"r":{o.precision==null&&!isNaN(f=QN(d,Math.max(Math.abs(n),Math.abs(s))))&&(o.precision=f-(o.type==="e"));break}case"f":case"%":{o.precision==null&&!isNaN(f=XN(d))&&(o.precision=f-(o.type==="%")*2);break}}return $x(o)}function s_(n){var s=n.domain;return n.ticks=function(l){var o=s();return Tb(o[0],o[o.length-1],l??10)},n.tickFormat=function(l,o){var d=s();return i_(d[0],d[d.length-1],l??10,o)},n.nice=function(l){l==null&&(l=10);var o=s(),d=0,f=o.length-1,m=o[d],p=o[f],g,h,x=10;for(p<m&&(h=m,m=p,p=h,h=d,d=f,f=h);x-- >0;){if(h=Tu(m,p,l),h===g)return o[d]=m,o[f]=p,s(o);if(h>0)m=Math.floor(m/h)*h,p=Math.ceil(p/h)*h;else if(h<0)m=Math.ceil(m*h)/h,p=Math.floor(p*h)/h;else break;g=h}return n},n}function ll(){var n=Vx();return n.copy=function(){return Gx(n,ll())},sc.apply(n,arguments),s_(n)}function r_(n,s){n=n.slice();var l=0,o=n.length-1,d=n[l],f=n[o],m;return f<d&&(m=l,l=o,o=m,m=d,d=f,f=m),n[l]=s.floor(d),n[o]=s.ceil(f),n}const gu=new Date,xu=new Date;function ca(n,s,l,o){function d(f){return n(f=arguments.length===0?new Date:new Date(+f)),f}return d.floor=f=>(n(f=new Date(+f)),f),d.ceil=f=>(n(f=new Date(f-1)),s(f,1),n(f),f),d.round=f=>{const m=d(f),p=d.ceil(f);return f-m<p-f?m:p},d.offset=(f,m)=>(s(f=new Date(+f),m==null?1:Math.floor(m)),f),d.range=(f,m,p)=>{const g=[];if(f=d.ceil(f),p=p==null?1:Math.floor(p),!(f<m)||!(p>0))return g;let h;do g.push(h=new Date(+f)),s(f,p),n(f);while(h<f&&f<m);return g},d.filter=f=>ca(m=>{if(m>=m)for(;n(m),!f(m);)m.setTime(m-1)},(m,p)=>{if(m>=m)if(p<0)for(;++p<=0;)for(;s(m,-1),!f(m););else for(;--p>=0;)for(;s(m,1),!f(m););}),l&&(d.count=(f,m)=>(gu.setTime(+f),xu.setTime(+m),n(gu),n(xu),Math.floor(l(gu,xu))),d.every=f=>(f=Math.floor(f),!isFinite(f)||!(f>0)?null:f>1?d.filter(o?m=>o(m)%f===0:m=>d.count(0,m)%f===0):d)),d}const Po=ca(()=>{},(n,s)=>{n.setTime(+n+s)},(n,s)=>s-n);Po.every=n=>(n=Math.floor(n),!isFinite(n)||!(n>0)?null:n>1?ca(s=>{s.setTime(Math.floor(s/n)*n)},(s,l)=>{s.setTime(+s+l*n)},(s,l)=>(l-s)/n):Po);Po.range;const Wn=1e3,un=Wn*60,Kn=un*60,ti=Kn*24,af=ti*7,Ag=ti*30,yu=ti*365,qs=ca(n=>{n.setTime(n-n.getMilliseconds())},(n,s)=>{n.setTime(+n+s*Wn)},(n,s)=>(s-n)/Wn,n=>n.getUTCSeconds());qs.range;const nf=ca(n=>{n.setTime(n-n.getMilliseconds()-n.getSeconds()*Wn)},(n,s)=>{n.setTime(+n+s*un)},(n,s)=>(s-n)/un,n=>n.getMinutes());nf.range;const l_=ca(n=>{n.setUTCSeconds(0,0)},(n,s)=>{n.setTime(+n+s*un)},(n,s)=>(s-n)/un,n=>n.getUTCMinutes());l_.range;const sf=ca(n=>{n.setTime(n-n.getMilliseconds()-n.getSeconds()*Wn-n.getMinutes()*un)},(n,s)=>{n.setTime(+n+s*Kn)},(n,s)=>(s-n)/Kn,n=>n.getHours());sf.range;const o_=ca(n=>{n.setUTCMinutes(0,0,0)},(n,s)=>{n.setTime(+n+s*Kn)},(n,s)=>(s-n)/Kn,n=>n.getUTCHours());o_.range;const pl=ca(n=>n.setHours(0,0,0,0),(n,s)=>n.setDate(n.getDate()+s),(n,s)=>(s-n-(s.getTimezoneOffset()-n.getTimezoneOffset())*un)/ti,n=>n.getDate()-1);pl.range;const rf=ca(n=>{n.setUTCHours(0,0,0,0)},(n,s)=>{n.setUTCDate(n.getUTCDate()+s)},(n,s)=>(s-n)/ti,n=>n.getUTCDate()-1);rf.range;const c_=ca(n=>{n.setUTCHours(0,0,0,0)},(n,s)=>{n.setUTCDate(n.getUTCDate()+s)},(n,s)=>(s-n)/ti,n=>Math.floor(n/ti));c_.range;function as(n){return ca(s=>{s.setDate(s.getDate()-(s.getDay()+7-n)%7),s.setHours(0,0,0,0)},(s,l)=>{s.setDate(s.getDate()+l*7)},(s,l)=>(l-s-(l.getTimezoneOffset()-s.getTimezoneOffset())*un)/af)}const rc=as(0),Xo=as(1),d_=as(2),u_=as(3),Ps=as(4),f_=as(5),h_=as(6);rc.range;Xo.range;d_.range;u_.range;Ps.range;f_.range;h_.range;function ns(n){return ca(s=>{s.setUTCDate(s.getUTCDate()-(s.getUTCDay()+7-n)%7),s.setUTCHours(0,0,0,0)},(s,l)=>{s.setUTCDate(s.getUTCDate()+l*7)},(s,l)=>(l-s)/af)}const Px=ns(0),Zo=ns(1),m_=ns(2),p_=ns(3),Xs=ns(4),g_=ns(5),x_=ns(6);Px.range;Zo.range;m_.range;p_.range;Xs.range;g_.range;x_.range;const lf=ca(n=>{n.setDate(1),n.setHours(0,0,0,0)},(n,s)=>{n.setMonth(n.getMonth()+s)},(n,s)=>s.getMonth()-n.getMonth()+(s.getFullYear()-n.getFullYear())*12,n=>n.getMonth());lf.range;const y_=ca(n=>{n.setUTCDate(1),n.setUTCHours(0,0,0,0)},(n,s)=>{n.setUTCMonth(n.getUTCMonth()+s)},(n,s)=>s.getUTCMonth()-n.getUTCMonth()+(s.getUTCFullYear()-n.getUTCFullYear())*12,n=>n.getUTCMonth());y_.range;const ai=ca(n=>{n.setMonth(0,1),n.setHours(0,0,0,0)},(n,s)=>{n.setFullYear(n.getFullYear()+s)},(n,s)=>s.getFullYear()-n.getFullYear(),n=>n.getFullYear());ai.every=n=>!isFinite(n=Math.floor(n))||!(n>0)?null:ca(s=>{s.setFullYear(Math.floor(s.getFullYear()/n)*n),s.setMonth(0,1),s.setHours(0,0,0,0)},(s,l)=>{s.setFullYear(s.getFullYear()+l*n)});ai.range;const es=ca(n=>{n.setUTCMonth(0,1),n.setUTCHours(0,0,0,0)},(n,s)=>{n.setUTCFullYear(n.getUTCFullYear()+s)},(n,s)=>s.getUTCFullYear()-n.getUTCFullYear(),n=>n.getUTCFullYear());es.every=n=>!isFinite(n=Math.floor(n))||!(n>0)?null:ca(s=>{s.setUTCFullYear(Math.floor(s.getUTCFullYear()/n)*n),s.setUTCMonth(0,1),s.setUTCHours(0,0,0,0)},(s,l)=>{s.setUTCFullYear(s.getUTCFullYear()+l*n)});es.range;function v_(n,s,l,o,d,f){const m=[[qs,1,Wn],[qs,5,5*Wn],[qs,15,15*Wn],[qs,30,30*Wn],[f,1,un],[f,5,5*un],[f,15,15*un],[f,30,30*un],[d,1,Kn],[d,3,3*Kn],[d,6,6*Kn],[d,12,12*Kn],[o,1,ti],[o,2,2*ti],[l,1,af],[s,1,Ag],[s,3,3*Ag],[n,1,yu]];function p(h,x,v){const b=x<h;b&&([h,x]=[x,h]);const _=v&&typeof v.range=="function"?v:g(h,x,v),C=_?_.range(h,+x+1):[];return b?C.reverse():C}function g(h,x,v){const b=Math.abs(x-h)/v,_=Fu(([,,A])=>A).right(m,b);if(_===m.length)return n.every(Cu(h/yu,x/yu,v));if(_===0)return Po.every(Math.max(Cu(h,x,v),1));const[C,E]=m[b/m[_-1][2]<m[_][2]/b?_-1:_];return C.every(E)}return[p,g]}const[b_,j_]=v_(ai,lf,rc,pl,sf,nf);function vu(n){if(0<=n.y&&n.y<100){var s=new Date(-1,n.m,n.d,n.H,n.M,n.S,n.L);return s.setFullYear(n.y),s}return new Date(n.y,n.m,n.d,n.H,n.M,n.S,n.L)}function bu(n){if(0<=n.y&&n.y<100){var s=new Date(Date.UTC(-1,n.m,n.d,n.H,n.M,n.S,n.L));return s.setUTCFullYear(n.y),s}return new Date(Date.UTC(n.y,n.m,n.d,n.H,n.M,n.S,n.L))}function Gr(n,s,l){return{y:n,m:s,d:l,H:0,M:0,S:0,L:0}}function w_(n){var s=n.dateTime,l=n.date,o=n.time,d=n.periods,f=n.days,m=n.shortDays,p=n.months,g=n.shortMonths,h=Vr(d),x=Pr(d),v=Vr(f),b=Pr(f),_=Vr(m),C=Pr(m),E=Vr(p),A=Pr(p),L=Vr(g),q=Pr(g),P={a:H,A:F,b:_e,B:z,c:null,d:Rg,e:Rg,f:G_,g:tS,G:nS,H:$_,I:F_,j:Y_,L:Xx,m:V_,M:P_,p:G,q:ie,Q:Lg,s:Bg,S:X_,u:Z_,U:Q_,V:J_,w:W_,W:K_,x:null,X:null,y:eS,Y:aS,Z:iS,"%":Ug},M={a:oe,A:re,b:Te,B:ue,c:null,d:Og,e:Og,f:oS,g:yS,G:bS,H:sS,I:rS,j:lS,L:Qx,m:cS,M:dS,p:je,q:Le,Q:Lg,s:Bg,S:uS,u:fS,U:hS,V:mS,w:pS,W:gS,x:null,X:null,y:xS,Y:vS,Z:jS,"%":Ug},X={a:we,A:ge,b:Ne,B:me,c:xe,d:Mg,e:Mg,f:B_,g:Eg,G:kg,H:Dg,I:Dg,j:R_,L:L_,m:D_,M:O_,p:Ae,q:M_,Q:H_,s:I_,S:U_,u:C_,U:A_,V:z_,w:T_,W:k_,x:He,X:S,y:Eg,Y:kg,Z:E_,"%":q_};P.x=Q(l,P),P.X=Q(o,P),P.c=Q(s,P),M.x=Q(l,M),M.X=Q(o,M),M.c=Q(s,M);function Q(ne,D){return function(I){var J=[],be=-1,Me=0,Ve=ne.length,at,Ke,ta;for(I instanceof Date||(I=new Date(+I));++be<Ve;)ne.charCodeAt(be)===37&&(J.push(ne.slice(Me,be)),(Ke=zg[at=ne.charAt(++be)])!=null?at=ne.charAt(++be):Ke=at==="e"?" ":"0",(ta=D[at])&&(at=ta(I,Ke)),J.push(at),Me=be+1);return J.push(ne.slice(Me,be)),J.join("")}}function K(ne,D){return function(I){var J=Gr(1900,void 0,1),be=se(J,ne,I+="",0),Me,Ve;if(be!=I.length)return null;if("Q"in J)return new Date(J.Q);if("s"in J)return new Date(J.s*1e3+("L"in J?J.L:0));if(D&&!("Z"in J)&&(J.Z=0),"p"in J&&(J.H=J.H%12+J.p*12),J.m===void 0&&(J.m="q"in J?J.q:0),"V"in J){if(J.V<1||J.V>53)return null;"w"in J||(J.w=1),"Z"in J?(Me=bu(Gr(J.y,0,1)),Ve=Me.getUTCDay(),Me=Ve>4||Ve===0?Zo.ceil(Me):Zo(Me),Me=rf.offset(Me,(J.V-1)*7),J.y=Me.getUTCFullYear(),J.m=Me.getUTCMonth(),J.d=Me.getUTCDate()+(J.w+6)%7):(Me=vu(Gr(J.y,0,1)),Ve=Me.getDay(),Me=Ve>4||Ve===0?Xo.ceil(Me):Xo(Me),Me=pl.offset(Me,(J.V-1)*7),J.y=Me.getFullYear(),J.m=Me.getMonth(),J.d=Me.getDate()+(J.w+6)%7)}else("W"in J||"U"in J)&&("w"in J||(J.w="u"in J?J.u%7:"W"in J?1:0),Ve="Z"in J?bu(Gr(J.y,0,1)).getUTCDay():vu(Gr(J.y,0,1)).getDay(),J.m=0,J.d="W"in J?(J.w+6)%7+J.W*7-(Ve+5)%7:J.w+J.U*7-(Ve+6)%7);return"Z"in J?(J.H+=J.Z/100|0,J.M+=J.Z%100,bu(J)):vu(J)}}function se(ne,D,I,J){for(var be=0,Me=D.length,Ve=I.length,at,Ke;be<Me;){if(J>=Ve)return-1;if(at=D.charCodeAt(be++),at===37){if(at=D.charAt(be++),Ke=X[at in zg?D.charAt(be++):at],!Ke||(J=Ke(ne,I,J))<0)return-1}else if(at!=I.charCodeAt(J++))return-1}return J}function Ae(ne,D,I){var J=h.exec(D.slice(I));return J?(ne.p=x.get(J[0].toLowerCase()),I+J[0].length):-1}function we(ne,D,I){var J=_.exec(D.slice(I));return J?(ne.w=C.get(J[0].toLowerCase()),I+J[0].length):-1}function ge(ne,D,I){var J=v.exec(D.slice(I));return J?(ne.w=b.get(J[0].toLowerCase()),I+J[0].length):-1}function Ne(ne,D,I){var J=L.exec(D.slice(I));return J?(ne.m=q.get(J[0].toLowerCase()),I+J[0].length):-1}function me(ne,D,I){var J=E.exec(D.slice(I));return J?(ne.m=A.get(J[0].toLowerCase()),I+J[0].length):-1}function xe(ne,D,I){return se(ne,s,D,I)}function He(ne,D,I){return se(ne,l,D,I)}function S(ne,D,I){return se(ne,o,D,I)}function H(ne){return m[ne.getDay()]}function F(ne){return f[ne.getDay()]}function _e(ne){return g[ne.getMonth()]}function z(ne){return p[ne.getMonth()]}function G(ne){return d[+(ne.getHours()>=12)]}function ie(ne){return 1+~~(ne.getMonth()/3)}function oe(ne){return m[ne.getUTCDay()]}function re(ne){return f[ne.getUTCDay()]}function Te(ne){return g[ne.getUTCMonth()]}function ue(ne){return p[ne.getUTCMonth()]}function je(ne){return d[+(ne.getUTCHours()>=12)]}function Le(ne){return 1+~~(ne.getUTCMonth()/3)}return{format:function(ne){var D=Q(ne+="",P);return D.toString=function(){return ne},D},parse:function(ne){var D=K(ne+="",!1);return D.toString=function(){return ne},D},utcFormat:function(ne){var D=Q(ne+="",M);return D.toString=function(){return ne},D},utcParse:function(ne){var D=K(ne+="",!0);return D.toString=function(){return ne},D}}}var zg={"-":"",_:" ",0:"0"},pa=/^\s*\d+/,N_=/^%/,__=/[\\^$*+?|[\]().{}]/g;function jt(n,s,l){var o=n<0?"-":"",d=(o?-n:n)+"",f=d.length;return o+(f<l?new Array(l-f+1).join(s)+d:d)}function S_(n){return n.replace(__,"\\$&")}function Vr(n){return new RegExp("^(?:"+n.map(S_).join("|")+")","i")}function Pr(n){return new Map(n.map((s,l)=>[s.toLowerCase(),l]))}function T_(n,s,l){var o=pa.exec(s.slice(l,l+1));return o?(n.w=+o[0],l+o[0].length):-1}function C_(n,s,l){var o=pa.exec(s.slice(l,l+1));return o?(n.u=+o[0],l+o[0].length):-1}function A_(n,s,l){var o=pa.exec(s.slice(l,l+2));return o?(n.U=+o[0],l+o[0].length):-1}function z_(n,s,l){var o=pa.exec(s.slice(l,l+2));return o?(n.V=+o[0],l+o[0].length):-1}function k_(n,s,l){var o=pa.exec(s.slice(l,l+2));return o?(n.W=+o[0],l+o[0].length):-1}function kg(n,s,l){var o=pa.exec(s.slice(l,l+4));return o?(n.y=+o[0],l+o[0].length):-1}function Eg(n,s,l){var o=pa.exec(s.slice(l,l+2));return o?(n.y=+o[0]+(+o[0]>68?1900:2e3),l+o[0].length):-1}function E_(n,s,l){var o=/^(Z)|([+-]\d\d)(?::?(\d\d))?/.exec(s.slice(l,l+6));return o?(n.Z=o[1]?0:-(o[2]+(o[3]||"00")),l+o[0].length):-1}function M_(n,s,l){var o=pa.exec(s.slice(l,l+1));return o?(n.q=o[0]*3-3,l+o[0].length):-1}function D_(n,s,l){var o=pa.exec(s.slice(l,l+2));return o?(n.m=o[0]-1,l+o[0].length):-1}function Mg(n,s,l){var o=pa.exec(s.slice(l,l+2));return o?(n.d=+o[0],l+o[0].length):-1}function R_(n,s,l){var o=pa.exec(s.slice(l,l+3));return o?(n.m=0,n.d=+o[0],l+o[0].length):-1}function Dg(n,s,l){var o=pa.exec(s.slice(l,l+2));return o?(n.H=+o[0],l+o[0].length):-1}function O_(n,s,l){var o=pa.exec(s.slice(l,l+2));return o?(n.M=+o[0],l+o[0].length):-1}function U_(n,s,l){var o=pa.exec(s.slice(l,l+2));return o?(n.S=+o[0],l+o[0].length):-1}function L_(n,s,l){var o=pa.exec(s.slice(l,l+3));return o?(n.L=+o[0],l+o[0].length):-1}function B_(n,s,l){var o=pa.exec(s.slice(l,l+6));return o?(n.L=Math.floor(o[0]/1e3),l+o[0].length):-1}function q_(n,s,l){var o=N_.exec(s.slice(l,l+1));return o?l+o[0].length:-1}function H_(n,s,l){var o=pa.exec(s.slice(l));return o?(n.Q=+o[0],l+o[0].length):-1}function I_(n,s,l){var o=pa.exec(s.slice(l));return o?(n.s=+o[0],l+o[0].length):-1}function Rg(n,s){return jt(n.getDate(),s,2)}function $_(n,s){return jt(n.getHours(),s,2)}function F_(n,s){return jt(n.getHours()%12||12,s,2)}function Y_(n,s){return jt(1+pl.count(ai(n),n),s,3)}function Xx(n,s){return jt(n.getMilliseconds(),s,3)}function G_(n,s){return Xx(n,s)+"000"}function V_(n,s){return jt(n.getMonth()+1,s,2)}function P_(n,s){return jt(n.getMinutes(),s,2)}function X_(n,s){return jt(n.getSeconds(),s,2)}function Z_(n){var s=n.getDay();return s===0?7:s}function Q_(n,s){return jt(rc.count(ai(n)-1,n),s,2)}function Zx(n){var s=n.getDay();return s>=4||s===0?Ps(n):Ps.ceil(n)}function J_(n,s){return n=Zx(n),jt(Ps.count(ai(n),n)+(ai(n).getDay()===4),s,2)}function W_(n){return n.getDay()}function K_(n,s){return jt(Xo.count(ai(n)-1,n),s,2)}function eS(n,s){return jt(n.getFullYear()%100,s,2)}function tS(n,s){return n=Zx(n),jt(n.getFullYear()%100,s,2)}function aS(n,s){return jt(n.getFullYear()%1e4,s,4)}function nS(n,s){var l=n.getDay();return n=l>=4||l===0?Ps(n):Ps.ceil(n),jt(n.getFullYear()%1e4,s,4)}function iS(n){var s=n.getTimezoneOffset();return(s>0?"-":(s*=-1,"+"))+jt(s/60|0,"0",2)+jt(s%60,"0",2)}function Og(n,s){return jt(n.getUTCDate(),s,2)}function sS(n,s){return jt(n.getUTCHours(),s,2)}function rS(n,s){return jt(n.getUTCHours()%12||12,s,2)}function lS(n,s){return jt(1+rf.count(es(n),n),s,3)}function Qx(n,s){return jt(n.getUTCMilliseconds(),s,3)}function oS(n,s){return Qx(n,s)+"000"}function cS(n,s){return jt(n.getUTCMonth()+1,s,2)}function dS(n,s){return jt(n.getUTCMinutes(),s,2)}function uS(n,s){return jt(n.getUTCSeconds(),s,2)}function fS(n){var s=n.getUTCDay();return s===0?7:s}function hS(n,s){return jt(Px.count(es(n)-1,n),s,2)}function Jx(n){var s=n.getUTCDay();return s>=4||s===0?Xs(n):Xs.ceil(n)}function mS(n,s){return n=Jx(n),jt(Xs.count(es(n),n)+(es(n).getUTCDay()===4),s,2)}function pS(n){return n.getUTCDay()}function gS(n,s){return jt(Zo.count(es(n)-1,n),s,2)}function xS(n,s){return jt(n.getUTCFullYear()%100,s,2)}function yS(n,s){return n=Jx(n),jt(n.getUTCFullYear()%100,s,2)}function vS(n,s){return jt(n.getUTCFullYear()%1e4,s,4)}function bS(n,s){var l=n.getUTCDay();return n=l>=4||l===0?Xs(n):Xs.ceil(n),jt(n.getUTCFullYear()%1e4,s,4)}function jS(){return"+0000"}function Ug(){return"%"}function Lg(n){return+n}function Bg(n){return Math.floor(+n/1e3)}var Us,ol,Wx;wS({dateTime:"%x, %X",date:"%-m/%-d/%Y",time:"%-I:%M:%S %p",periods:["AM","PM"],days:["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],shortDays:["Sun","Mon","Tue","Wed","Thu","Fri","Sat"],months:["January","February","March","April","May","June","July","August","September","October","November","December"],shortMonths:["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]});function wS(n){return Us=w_(n),ol=Us.format,Wx=Us.parse,Us.utcFormat,Us.utcParse,Us}function NS(n){return new Date(n)}function _S(n){return n instanceof Date?+n:+new Date(+n)}function Kx(n,s,l,o,d,f,m,p,g,h){var x=Vx(),v=x.invert,b=x.domain,_=h(".%L"),C=h(":%S"),E=h("%I:%M"),A=h("%I %p"),L=h("%a %d"),q=h("%b %d"),P=h("%B"),M=h("%Y");function X(Q){return(g(Q)<Q?_:p(Q)<Q?C:m(Q)<Q?E:f(Q)<Q?A:o(Q)<Q?d(Q)<Q?L:q:l(Q)<Q?P:M)(Q)}return x.invert=function(Q){return new Date(v(Q))},x.domain=function(Q){return arguments.length?b(Array.from(Q,_S)):b().map(NS)},x.ticks=function(Q){var K=b();return n(K[0],K[K.length-1],Q??10)},x.tickFormat=function(Q,K){return K==null?X:h(K)},x.nice=function(Q){var K=b();return(!Q||typeof Q.range!="function")&&(Q=s(K[0],K[K.length-1],Q??10)),Q?b(r_(K,Q)):x},x.copy=function(){return Gx(x,Kx(n,s,l,o,d,f,m,p,g,h))},x}function e0(){return sc.apply(Kx(b_,j_,ai,lf,rc,pl,sf,nf,qs,ol).domain([new Date(2e3,0,1),new Date(2e3,0,2)]),arguments)}function yt(n){return function(){return n}}const qg=Math.abs,Ca=Math.atan2,Pi=Math.cos,SS=Math.max,ju=Math.min,An=Math.sin,Hs=Math.sqrt,qa=1e-12,cl=Math.PI,Qo=cl/2,Ro=2*cl;function TS(n){return n>1?0:n<-1?cl:Math.acos(n)}function Hg(n){return n>=1?Qo:n<=-1?-Qo:Math.asin(n)}function of(n){let s=3;return n.digits=function(l){if(!arguments.length)return s;if(l==null)s=null;else{const o=Math.floor(l);if(!(o>=0))throw new RangeError(`invalid digits: ${l}`);s=o}return n},()=>new uN(s)}function CS(n){return n.innerRadius}function AS(n){return n.outerRadius}function zS(n){return n.startAngle}function kS(n){return n.endAngle}function ES(n){return n&&n.padAngle}function MS(n,s,l,o,d,f,m,p){var g=l-n,h=o-s,x=m-d,v=p-f,b=v*g-x*h;if(!(b*b<qa))return b=(x*(s-f)-v*(n-d))/b,[n+b*g,s+b*h]}function Co(n,s,l,o,d,f,m){var p=n-l,g=s-o,h=(m?f:-f)/Hs(p*p+g*g),x=h*g,v=-h*p,b=n+x,_=s+v,C=l+x,E=o+v,A=(b+C)/2,L=(_+E)/2,q=C-b,P=E-_,M=q*q+P*P,X=d-f,Q=b*E-C*_,K=(P<0?-1:1)*Hs(SS(0,X*X*M-Q*Q)),se=(Q*P-q*K)/M,Ae=(-Q*q-P*K)/M,we=(Q*P+q*K)/M,ge=(-Q*q+P*K)/M,Ne=se-A,me=Ae-L,xe=we-A,He=ge-L;return Ne*Ne+me*me>xe*xe+He*He&&(se=we,Ae=ge),{cx:se,cy:Ae,x01:-x,y01:-v,x11:se*(d/X-1),y11:Ae*(d/X-1)}}function DS(){var n=CS,s=AS,l=yt(0),o=null,d=zS,f=kS,m=ES,p=null,g=of(h);function h(){var x,v,b=+n.apply(this,arguments),_=+s.apply(this,arguments),C=d.apply(this,arguments)-Qo,E=f.apply(this,arguments)-Qo,A=qg(E-C),L=E>C;if(p||(p=x=g()),_<b&&(v=_,_=b,b=v),!(_>qa))p.moveTo(0,0);else if(A>Ro-qa)p.moveTo(_*Pi(C),_*An(C)),p.arc(0,0,_,C,E,!L),b>qa&&(p.moveTo(b*Pi(E),b*An(E)),p.arc(0,0,b,E,C,L));else{var q=C,P=E,M=C,X=E,Q=A,K=A,se=m.apply(this,arguments)/2,Ae=se>qa&&(o?+o.apply(this,arguments):Hs(b*b+_*_)),we=ju(qg(_-b)/2,+l.apply(this,arguments)),ge=we,Ne=we,me,xe;if(Ae>qa){var He=Hg(Ae/b*An(se)),S=Hg(Ae/_*An(se));(Q-=He*2)>qa?(He*=L?1:-1,M+=He,X-=He):(Q=0,M=X=(C+E)/2),(K-=S*2)>qa?(S*=L?1:-1,q+=S,P-=S):(K=0,q=P=(C+E)/2)}var H=_*Pi(q),F=_*An(q),_e=b*Pi(X),z=b*An(X);if(we>qa){var G=_*Pi(P),ie=_*An(P),oe=b*Pi(M),re=b*An(M),Te;if(A<cl)if(Te=MS(H,F,oe,re,G,ie,_e,z)){var ue=H-Te[0],je=F-Te[1],Le=G-Te[0],ne=ie-Te[1],D=1/An(TS((ue*Le+je*ne)/(Hs(ue*ue+je*je)*Hs(Le*Le+ne*ne)))/2),I=Hs(Te[0]*Te[0]+Te[1]*Te[1]);ge=ju(we,(b-I)/(D-1)),Ne=ju(we,(_-I)/(D+1))}else ge=Ne=0}K>qa?Ne>qa?(me=Co(oe,re,H,F,_,Ne,L),xe=Co(G,ie,_e,z,_,Ne,L),p.moveTo(me.cx+me.x01,me.cy+me.y01),Ne<we?p.arc(me.cx,me.cy,Ne,Ca(me.y01,me.x01),Ca(xe.y01,xe.x01),!L):(p.arc(me.cx,me.cy,Ne,Ca(me.y01,me.x01),Ca(me.y11,me.x11),!L),p.arc(0,0,_,Ca(me.cy+me.y11,me.cx+me.x11),Ca(xe.cy+xe.y11,xe.cx+xe.x11),!L),p.arc(xe.cx,xe.cy,Ne,Ca(xe.y11,xe.x11),Ca(xe.y01,xe.x01),!L))):(p.moveTo(H,F),p.arc(0,0,_,q,P,!L)):p.moveTo(H,F),!(b>qa)||!(Q>qa)?p.lineTo(_e,z):ge>qa?(me=Co(_e,z,G,ie,b,-ge,L),xe=Co(H,F,oe,re,b,-ge,L),p.lineTo(me.cx+me.x01,me.cy+me.y01),ge<we?p.arc(me.cx,me.cy,ge,Ca(me.y01,me.x01),Ca(xe.y01,xe.x01),!L):(p.arc(me.cx,me.cy,ge,Ca(me.y01,me.x01),Ca(me.y11,me.x11),!L),p.arc(0,0,b,Ca(me.cy+me.y11,me.cx+me.x11),Ca(xe.cy+xe.y11,xe.cx+xe.x11),L),p.arc(xe.cx,xe.cy,ge,Ca(xe.y11,xe.x11),Ca(xe.y01,xe.x01),!L))):p.arc(0,0,b,X,M,L)}if(p.closePath(),x)return p=null,x+""||null}return h.centroid=function(){var x=(+n.apply(this,arguments)+ +s.apply(this,arguments))/2,v=(+d.apply(this,arguments)+ +f.apply(this,arguments))/2-cl/2;return[Pi(v)*x,An(v)*x]},h.innerRadius=function(x){return arguments.length?(n=typeof x=="function"?x:yt(+x),h):n},h.outerRadius=function(x){return arguments.length?(s=typeof x=="function"?x:yt(+x),h):s},h.cornerRadius=function(x){return arguments.length?(l=typeof x=="function"?x:yt(+x),h):l},h.padRadius=function(x){return arguments.length?(o=x==null?null:typeof x=="function"?x:yt(+x),h):o},h.startAngle=function(x){return arguments.length?(d=typeof x=="function"?x:yt(+x),h):d},h.endAngle=function(x){return arguments.length?(f=typeof x=="function"?x:yt(+x),h):f},h.padAngle=function(x){return arguments.length?(m=typeof x=="function"?x:yt(+x),h):m},h.context=function(x){return arguments.length?(p=x??null,h):p},h}function cf(n){return typeof n=="object"&&"length"in n?n:Array.from(n)}function t0(n){this._context=n}t0.prototype={areaStart:function(){this._line=0},areaEnd:function(){this._line=NaN},lineStart:function(){this._point=0},lineEnd:function(){(this._line||this._line!==0&&this._point===1)&&this._context.closePath(),this._line=1-this._line},point:function(n,s){switch(n=+n,s=+s,this._point){case 0:this._point=1,this._line?this._context.lineTo(n,s):this._context.moveTo(n,s);break;case 1:this._point=2;default:this._context.lineTo(n,s);break}}};function a0(n){return new t0(n)}function n0(n){return n[0]}function i0(n){return n[1]}function lc(n,s){var l=yt(!0),o=null,d=a0,f=null,m=of(p);n=typeof n=="function"?n:n===void 0?n0:yt(n),s=typeof s=="function"?s:s===void 0?i0:yt(s);function p(g){var h,x=(g=cf(g)).length,v,b=!1,_;for(o==null&&(f=d(_=m())),h=0;h<=x;++h)!(h<x&&l(v=g[h],h,g))===b&&((b=!b)?f.lineStart():f.lineEnd()),b&&f.point(+n(v,h,g),+s(v,h,g));if(_)return f=null,_+""||null}return p.x=function(g){return arguments.length?(n=typeof g=="function"?g:yt(+g),p):n},p.y=function(g){return arguments.length?(s=typeof g=="function"?g:yt(+g),p):s},p.defined=function(g){return arguments.length?(l=typeof g=="function"?g:yt(!!g),p):l},p.curve=function(g){return arguments.length?(d=g,o!=null&&(f=d(o)),p):d},p.context=function(g){return arguments.length?(g==null?o=f=null:f=d(o=g),p):o},p}function RS(n,s,l){var o=null,d=yt(!0),f=null,m=a0,p=null,g=of(h);n=typeof n=="function"?n:n===void 0?n0:yt(+n),s=typeof s=="function"?s:yt(s===void 0?0:+s),l=typeof l=="function"?l:l===void 0?i0:yt(+l);function h(v){var b,_,C,E=(v=cf(v)).length,A,L=!1,q,P=new Array(E),M=new Array(E);for(f==null&&(p=m(q=g())),b=0;b<=E;++b){if(!(b<E&&d(A=v[b],b,v))===L)if(L=!L)_=b,p.areaStart(),p.lineStart();else{for(p.lineEnd(),p.lineStart(),C=b-1;C>=_;--C)p.point(P[C],M[C]);p.lineEnd(),p.areaEnd()}L&&(P[b]=+n(A,b,v),M[b]=+s(A,b,v),p.point(o?+o(A,b,v):P[b],l?+l(A,b,v):M[b]))}if(q)return p=null,q+""||null}function x(){return lc().defined(d).curve(m).context(f)}return h.x=function(v){return arguments.length?(n=typeof v=="function"?v:yt(+v),o=null,h):n},h.x0=function(v){return arguments.length?(n=typeof v=="function"?v:yt(+v),h):n},h.x1=function(v){return arguments.length?(o=v==null?null:typeof v=="function"?v:yt(+v),h):o},h.y=function(v){return arguments.length?(s=typeof v=="function"?v:yt(+v),l=null,h):s},h.y0=function(v){return arguments.length?(s=typeof v=="function"?v:yt(+v),h):s},h.y1=function(v){return arguments.length?(l=v==null?null:typeof v=="function"?v:yt(+v),h):l},h.lineX0=h.lineY0=function(){return x().x(n).y(s)},h.lineY1=function(){return x().x(n).y(l)},h.lineX1=function(){return x().x(o).y(s)},h.defined=function(v){return arguments.length?(d=typeof v=="function"?v:yt(!!v),h):d},h.curve=function(v){return arguments.length?(m=v,f!=null&&(p=m(f)),h):m},h.context=function(v){return arguments.length?(v==null?f=p=null:p=m(f=v),h):f},h}function OS(n,s){return s<n?-1:s>n?1:s>=n?0:NaN}function US(n){return n}function LS(){var n=US,s=OS,l=null,o=yt(0),d=yt(Ro),f=yt(0);function m(p){var g,h=(p=cf(p)).length,x,v,b=0,_=new Array(h),C=new Array(h),E=+o.apply(this,arguments),A=Math.min(Ro,Math.max(-Ro,d.apply(this,arguments)-E)),L,q=Math.min(Math.abs(A)/h,f.apply(this,arguments)),P=q*(A<0?-1:1),M;for(g=0;g<h;++g)(M=C[_[g]=g]=+n(p[g],g,p))>0&&(b+=M);for(s!=null?_.sort(function(X,Q){return s(C[X],C[Q])}):l!=null&&_.sort(function(X,Q){return l(p[X],p[Q])}),g=0,v=b?(A-h*P)/b:0;g<h;++g,E=L)x=_[g],M=C[x],L=E+(M>0?M*v:0)+P,C[x]={data:p[x],index:g,value:M,startAngle:E,endAngle:L,padAngle:q};return C}return m.value=function(p){return arguments.length?(n=typeof p=="function"?p:yt(+p),m):n},m.sortValues=function(p){return arguments.length?(s=p,l=null,m):s},m.sort=function(p){return arguments.length?(l=p,s=null,m):l},m.startAngle=function(p){return arguments.length?(o=typeof p=="function"?p:yt(+p),m):o},m.endAngle=function(p){return arguments.length?(d=typeof p=="function"?p:yt(+p),m):d},m.padAngle=function(p){return arguments.length?(f=typeof p=="function"?p:yt(+p),m):f},m}function Ig(n,s,l){n._context.bezierCurveTo(n._x1+n._k*(n._x2-n._x0),n._y1+n._k*(n._y2-n._y0),n._x2+n._k*(n._x1-s),n._y2+n._k*(n._y1-l),n._x2,n._y2)}function s0(n,s){this._context=n,this._k=(1-s)/6}s0.prototype={areaStart:function(){this._line=0},areaEnd:function(){this._line=NaN},lineStart:function(){this._x0=this._x1=this._x2=this._y0=this._y1=this._y2=NaN,this._point=0},lineEnd:function(){switch(this._point){case 2:this._context.lineTo(this._x2,this._y2);break;case 3:Ig(this,this._x1,this._y1);break}(this._line||this._line!==0&&this._point===1)&&this._context.closePath(),this._line=1-this._line},point:function(n,s){switch(n=+n,s=+s,this._point){case 0:this._point=1,this._line?this._context.lineTo(n,s):this._context.moveTo(n,s);break;case 1:this._point=2,this._x1=n,this._y1=s;break;case 2:this._point=3;default:Ig(this,n,s);break}this._x0=this._x1,this._x1=this._x2,this._x2=n,this._y0=this._y1,this._y1=this._y2,this._y2=s}};const $g=(function n(s){function l(o){return new s0(o,s)}return l.tension=function(o){return n(+o)},l})(0);function Fg(n){return n<0?-1:1}function Yg(n,s,l){var o=n._x1-n._x0,d=s-n._x1,f=(n._y1-n._y0)/(o||d<0&&-0),m=(l-n._y1)/(d||o<0&&-0),p=(f*d+m*o)/(o+d);return(Fg(f)+Fg(m))*Math.min(Math.abs(f),Math.abs(m),.5*Math.abs(p))||0}function Gg(n,s){var l=n._x1-n._x0;return l?(3*(n._y1-n._y0)/l-s)/2:s}function wu(n,s,l){var o=n._x0,d=n._y0,f=n._x1,m=n._y1,p=(f-o)/3;n._context.bezierCurveTo(o+p,d+p*s,f-p,m-p*l,f,m)}function Jo(n){this._context=n}Jo.prototype={areaStart:function(){this._line=0},areaEnd:function(){this._line=NaN},lineStart:function(){this._x0=this._x1=this._y0=this._y1=this._t0=NaN,this._point=0},lineEnd:function(){switch(this._point){case 2:this._context.lineTo(this._x1,this._y1);break;case 3:wu(this,this._t0,Gg(this,this._t0));break}(this._line||this._line!==0&&this._point===1)&&this._context.closePath(),this._line=1-this._line},point:function(n,s){var l=NaN;if(n=+n,s=+s,!(n===this._x1&&s===this._y1)){switch(this._point){case 0:this._point=1,this._line?this._context.lineTo(n,s):this._context.moveTo(n,s);break;case 1:this._point=2;break;case 2:this._point=3,wu(this,Gg(this,l=Yg(this,n,s)),l);break;default:wu(this,this._t0,l=Yg(this,n,s));break}this._x0=this._x1,this._x1=n,this._y0=this._y1,this._y1=s,this._t0=l}}};Object.create(Jo.prototype).point=function(n,s){Jo.prototype.point.call(this,s,n)};function r0(n){return new Jo(n)}function Jr(n,s,l){this.k=n,this.x=s,this.y=l}Jr.prototype={constructor:Jr,scale:function(n){return n===1?this:new Jr(this.k*n,this.x,this.y)},translate:function(n,s){return n===0&s===0?this:new Jr(this.k,this.x+this.k*n,this.y+this.k*s)},apply:function(n){return[n[0]*this.k+this.x,n[1]*this.k+this.y]},applyX:function(n){return n*this.k+this.x},applyY:function(n){return n*this.k+this.y},invert:function(n){return[(n[0]-this.x)/this.k,(n[1]-this.y)/this.k]},invertX:function(n){return(n-this.x)/this.k},invertY:function(n){return(n-this.y)/this.k},rescaleX:function(n){return n.copy().domain(n.range().map(this.invertX,this).map(n.invert,n))},rescaleY:function(n){return n.copy().domain(n.range().map(this.invertY,this).map(n.invert,n))},toString:function(){return"translate("+this.x+","+this.y+") scale("+this.k+")"}};Jr.prototype;const BS=({active:n})=>{var C,E;if(!n)return null;const[s,l]=N.useState(null),[o,d]=N.useState(!0),[f,m]=N.useState(null),[p,g]=N.useState(!1),[h,x]=N.useState({});N.useEffect(()=>{v()},[]);const v=async()=>{try{d(!0);const A=localStorage.getItem("crisp_auth_token"),L=await fetch("http://localhost:8000/api/auth/profile/",{headers:{Authorization:`Bearer ${A}`,"Content-Type":"application/json"}});if(L.ok){const q=await L.json();l(q.user),x({first_name:q.user.first_name||"",last_name:q.user.last_name||"",email:q.user.email||""})}else throw new Error("Failed to fetch profile")}catch(A){m(A.message)}finally{d(!1)}},b=async()=>{try{const A=localStorage.getItem("crisp_auth_token"),L=await fetch("http://localhost:8000/api/auth/profile/",{method:"PUT",headers:{Authorization:`Bearer ${A}`,"Content-Type":"application/json"},body:JSON.stringify(h)});if(L.ok){const q=await L.json();l(q.user),g(!1)}else throw new Error("Failed to update profile")}catch(A){m(A.message)}},_=()=>{x({first_name:s.first_name||"",last_name:s.last_name||"",email:s.email||""}),g(!1)};return o?t.jsx("div",{className:"user-profile",children:t.jsxs("div",{className:"loading-state",children:[t.jsx("i",{className:"fas fa-spinner fa-spin"}),t.jsx("p",{children:"Loading profile..."})]})}):f?t.jsx("div",{className:"user-profile",children:t.jsxs("div",{className:"error-state",children:[t.jsx("i",{className:"fas fa-exclamation-triangle"}),t.jsxs("p",{children:["Error loading profile: ",f]}),t.jsx("button",{onClick:v,className:"btn btn-primary",children:"Retry"})]})}):t.jsxs("div",{className:"user-profile",children:[t.jsxs("div",{className:"header",children:[t.jsx("h2",{children:"User Profile"}),!p&&t.jsxs("button",{className:"btn btn-primary",onClick:()=>g(!0),children:[t.jsx("i",{className:"fas fa-edit"}),"Edit Profile"]})]}),t.jsxs("div",{className:"profile-card",children:[t.jsxs("div",{className:"profile-header",children:[t.jsx("div",{className:"profile-avatar",children:t.jsx("i",{className:"fas fa-user"})}),t.jsxs("div",{className:"profile-title",children:[t.jsxs("h3",{children:[s.first_name," ",s.last_name]}),t.jsx("p",{className:"profile-role",children:s.role})]})]}),t.jsx("div",{className:"profile-details",children:p?t.jsxs("form",{className:"edit-form",children:[t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"First Name"}),t.jsx("input",{type:"text",value:h.first_name,onChange:A=>x({...h,first_name:A.target.value}),className:"form-input"})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Last Name"}),t.jsx("input",{type:"text",value:h.last_name,onChange:A=>x({...h,last_name:A.target.value}),className:"form-input"})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Email"}),t.jsx("input",{type:"email",value:h.email,onChange:A=>x({...h,email:A.target.value}),className:"form-input"})]}),t.jsxs("div",{className:"form-actions",children:[t.jsxs("button",{type:"button",onClick:b,className:"btn btn-primary",children:[t.jsx("i",{className:"fas fa-save"}),"Save Changes"]}),t.jsxs("button",{type:"button",onClick:_,className:"btn btn-secondary",children:[t.jsx("i",{className:"fas fa-times"}),"Cancel"]})]})]}):t.jsxs("div",{className:"info-grid",children:[t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"Username"}),t.jsx("span",{children:s.username})]}),t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"Email"}),t.jsx("span",{children:s.email})]}),t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"First Name"}),t.jsx("span",{children:s.first_name||"Not set"})]}),t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"Last Name"}),t.jsx("span",{children:s.last_name||"Not set"})]}),t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"Organization"}),t.jsx("span",{children:((C=s.organization)==null?void 0:C.name)||"No organization"})]}),t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"Role"}),t.jsx("span",{className:`role-badge ${(E=s.role)==null?void 0:E.toLowerCase()}`,children:s.role})]}),t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"Status"}),t.jsx("span",{className:`status-badge ${s.is_active?"active":"inactive"}`,children:s.is_active?"Active":"Inactive"})]}),t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"Joined"}),t.jsx("span",{children:new Date(s.created_at).toLocaleDateString()})]})]})})]}),t.jsx("style",{jsx:!0,children:`
        .user-profile {
          padding: 20px;
          max-width: 800px;
          margin: 0 auto;
        }

        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .header h2 {
          margin: 0;
          color: #333;
        }

        .profile-card {
          background: white;
          border-radius: 12px;
          box-shadow: 0 4px 6px rgba(0,0,0,0.1);
          overflow: hidden;
        }

        .profile-header {
          background: linear-gradient(135deg, #0056b3, #004494);
          color: white;
          padding: 30px;
          display: flex;
          align-items: center;
          gap: 20px;
        }

        .profile-avatar {
          width: 80px;
          height: 80px;
          background: rgba(255,255,255,0.2);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 32px;
        }

        .profile-title h3 {
          margin: 0 0 5px 0;
          font-size: 24px;
          font-weight: 600;
        }

        .profile-role {
          margin: 0;
          opacity: 0.9;
          font-size: 16px;
        }

        .profile-details {
          padding: 30px;
        }

        .info-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 20px;
        }

        .info-item {
          display: flex;
          flex-direction: column;
          gap: 5px;
        }

        .info-item label {
          font-weight: 600;
          color: #495057;
          font-size: 14px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .info-item span {
          font-size: 16px;
          color: #333;
        }

        .edit-form {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 5px;
        }

        .form-group label {
          font-weight: 600;
          color: #495057;
          font-size: 14px;
        }

        .form-input {
          padding: 12px;
          border: 1px solid #dee2e6;
          border-radius: 6px;
          font-size: 14px;
          transition: border-color 0.2s;
        }

        .form-input:focus {
          outline: none;
          border-color: #0056b3;
        }

        .form-actions {
          display: flex;
          gap: 10px;
          justify-content: flex-end;
        }

        .btn {
          padding: 10px 20px;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          display: inline-flex;
          align-items: center;
          gap: 8px;
          transition: background-color 0.2s;
        }

        .btn-primary {
          background: #0056b3;
          color: white;
        }

        .btn-primary:hover {
          background: #004494;
        }

        .btn-secondary {
          background: #6c757d;
          color: white;
        }

        .btn-secondary:hover {
          background: #5a6268;
        }

        .role-badge,
        .status-badge {
          padding: 6px 12px;
          border-radius: 15px;
          font-size: 12px;
          font-weight: 600;
          width: fit-content;
        }

        .role-badge.admin {
          background: #e3f2fd;
          color: #1976d2;
        }

        .role-badge.user {
          background: #f3e5f5;
          color: #7b1fa2;
        }

        .role-badge.bluevisionadmin {
          background: #e8f5e8;
          color: #2e7d32;
        }

        .status-badge.active {
          background: #e8f5e8;
          color: #2e7d32;
        }

        .status-badge.inactive {
          background: #fff3e0;
          color: #f57c00;
        }

        .loading-state,
        .error-state {
          text-align: center;
          padding: 60px 20px;
        }

        .loading-state i {
          font-size: 32px;
          color: #0056b3;
          margin-bottom: 15px;
        }

        .error-state i {
          font-size: 32px;
          color: #dc3545;
          margin-bottom: 15px;
        }
      `})]})},kt="http://localhost:8000",Rt=()=>{const n=localStorage.getItem("crisp_auth_token");return{"Content-Type":"application/json",Authorization:n?`Bearer ${n}`:""}},qS=()=>{try{const n=localStorage.getItem("crisp_user");return n?JSON.parse(n):null}catch(n){return console.error("Error parsing current user from localStorage:",n),null}},HS=async(n,s)=>{const l=await fetch(`${kt}/api/auth/login/`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({username:n,password:s})});if(!l.ok){const d=await l.json().catch(()=>({}));throw new Error(d.detail||d.message||"Login failed")}const o=await l.json();return{tokens:{access:o.access,refresh:o.refresh},user:o.user}},IS=async(n={})=>{const s=new URLSearchParams(n).toString(),l=`${kt}/api/users/${s?`?${s}`:""}`,o=await fetch(l,{method:"GET",headers:Rt()});if(!o.ok){const d=await o.json().catch(()=>({}));throw new Error(d.message||"Failed to fetch users")}return await o.json()},Vg=async n=>{const s=await fetch(`${kt}/api/users/${n}/`,{method:"GET",headers:Rt()});if(!s.ok){const l=await s.json().catch(()=>({}));throw new Error(l.message||"Failed to fetch user")}return await s.json()},$S=async n=>{const s=await fetch(`${kt}/api/users/create/`,{method:"POST",headers:Rt(),body:JSON.stringify(n)});if(!s.ok){const l=await s.json().catch(()=>({}));throw new Error(l.message||"Failed to create user")}return await s.json()},FS=async(n,s)=>{const l=await fetch(`${kt}/api/users/${n}/update/`,{method:"PUT",headers:Rt(),body:JSON.stringify(s)});if(!l.ok){const o=await l.json().catch(()=>({}));throw new Error(o.message||"Failed to update user")}return await l.json()},YS=async(n,s="")=>{const l=await fetch(`${kt}/api/users/${n}/deactivate/`,{method:"POST",headers:Rt(),body:JSON.stringify({reason:s})});if(!l.ok){const o=await l.json().catch(()=>({}));throw new Error(o.message||"Failed to deactivate user")}return await l.json()},GS=async(n,s="")=>{const l=await fetch(`${kt}/api/users/${n}/reactivate/`,{method:"POST",headers:Rt(),body:JSON.stringify({reason:s})});if(!l.ok){const o=await l.json().catch(()=>({}));throw new Error(o.message||"Failed to reactivate user")}return await l.json()},VS=async(n,s="")=>{const l=await fetch(`${kt}/api/users/${n}/delete-permanently/`,{method:"DELETE",headers:Rt(),body:JSON.stringify({confirm:!0,reason:s})});if(!l.ok){const o=await l.json().catch(()=>({}));throw new Error(o.message||"Failed to permanently delete user")}return await l.json()},PS=async(n,s)=>{const l=await fetch(`${kt}/api/users/${n}/change_username/`,{method:"POST",headers:Rt(),body:JSON.stringify({username:s})});if(!l.ok){const o=await l.json().catch(()=>({}));throw new Error(o.message||"Failed to change username")}return await l.json()},df=async(n={})=>{const s=new URLSearchParams(n).toString(),l=`${kt}/api/organizations/${s?`?${s}`:""}`,o=await fetch(l,{method:"GET",headers:Rt()});if(!o.ok){const d=await o.json().catch(()=>({}));throw new Error(d.message||"Failed to fetch organizations")}return await o.json()},XS=async n=>{const s=await fetch(`${kt}/api/organizations/create/`,{method:"POST",headers:Rt(),body:JSON.stringify(n)});if(!s.ok){const l=await s.json().catch(()=>({}));throw new Error(l.message||"Failed to create organization")}return await s.json()},ZS=async(n,s)=>{const l=await fetch(`${kt}/api/organizations/${n}/update/`,{method:"PUT",headers:Rt(),body:JSON.stringify(s)});if(!l.ok){const o=await l.json().catch(()=>({}));throw new Error(o.message||"Failed to update organization")}return await l.json()},QS=async(n,s="")=>{const l=await fetch(`${kt}/api/organizations/${n}/deactivate/`,{method:"POST",headers:Rt(),body:JSON.stringify({reason:s})});if(!l.ok){const o=await l.json().catch(()=>({}));throw new Error(o.message||"Failed to deactivate organization")}return await l.json()},JS=async(n,s="")=>{const l=await fetch(`${kt}/api/organizations/${n}/reactivate/`,{method:"POST",headers:Rt(),body:JSON.stringify({reason:s})});if(!l.ok){const o=await l.json().catch(()=>({}));throw new Error(o.message||"Failed to reactivate organization")}return await l.json()},WS=async(n,s="")=>{const l=await fetch(`${kt}/api/organizations/${n}/delete-permanently/`,{method:"DELETE",headers:Rt(),body:JSON.stringify({confirm:!0,reason:s})});if(!l.ok){const o=await l.json().catch(()=>({}));throw new Error(o.message||"Failed to permanently delete organization")}return await l.json()},Pg=async n=>{const s=await fetch(`${kt}/api/organizations/${n}/`,{method:"GET",headers:Rt()});if(!s.ok){const l=await s.json().catch(()=>({}));throw new Error(l.message||"Failed to fetch organization details")}return await s.json()},KS=async()=>{const n=await fetch(`${kt}/api/organizations/types/`,{method:"GET",headers:Rt()});if(!n.ok){const s=await n.json().catch(()=>({}));throw new Error(s.message||"Failed to fetch organization types")}return await n.json()},e2=async(n={})=>{const s=new URLSearchParams(n).toString(),l=`${kt}/api/trust/bilateral/${s?`?${s}`:""}`,o=await fetch(l,{method:"GET",headers:Rt()});if(!o.ok){const d=await o.json().catch(()=>({}));throw new Error(d.message||"Failed to fetch trust relationships")}return await o.json()},t2=async n=>{const s={responding_organization_id:n.target_organization,trust_level:n.trust_level,message:n.notes||""},l=await fetch(`${kt}/api/trust/bilateral/request/`,{method:"POST",headers:Rt(),body:JSON.stringify(s)});if(!l.ok){const o=await l.json().catch(()=>({}));throw new Error(o.message||"Failed to create trust relationship")}return await l.json()},Xg=async(n,s)=>{const l=await fetch(`${kt}/api/trust/bilateral/${n}/update/`,{method:"PUT",headers:Rt(),body:JSON.stringify(s)});if(!l.ok){const o=await l.json().catch(()=>({}));throw new Error(o.message||"Failed to update trust relationship")}return await l.json()},a2=async(n,s,l=null,o="")=>{const d=await fetch(`${kt}/api/trust/bilateral/${n}/respond/`,{method:"POST",headers:Rt(),body:JSON.stringify({action:s,trust_level:l,message:o})});if(!d.ok){const f=await d.json().catch(()=>({}));throw new Error(f.message||"Failed to respond to trust relationship")}return await d.json()},n2=async(n,s="")=>{const l=await fetch(`${kt}/api/trust/bilateral/${n}/revoke/`,{method:"DELETE",headers:Rt(),body:JSON.stringify({message:s})});if(!l.ok){const o=await l.json().catch(()=>({}));throw new Error(o.message||"Failed to delete trust relationship")}return await l.json()},i2=async(n={})=>{const s=new URLSearchParams(n).toString(),l=`${kt}/api/trust/community/${s?`?${s}`:""}`,o=await fetch(l,{method:"GET",headers:Rt()});if(!o.ok){const d=await o.json().catch(()=>({}));throw new Error(d.message||"Failed to fetch trust groups")}return await o.json()},s2=async n=>{const s=await fetch(`${kt}/api/trust/community/`,{method:"POST",headers:Rt(),body:JSON.stringify(n)});if(!s.ok){const l=await s.json().catch(()=>({}));throw new Error(l.message||"Failed to create trust group")}return await s.json()},r2=async(n,s)=>{const l=await fetch(`${kt}/api/trust-management/groups/${n}/`,{method:"PUT",headers:Rt(),body:JSON.stringify(s)});if(!l.ok){const o=await l.json().catch(()=>({}));throw new Error(o.message||"Failed to update trust group")}return await l.json()},l2=async n=>{const s=await fetch(`${kt}/api/trust-management/groups/${n}/`,{method:"DELETE",headers:Rt()});if(!s.ok){const l=await s.json().catch(()=>({}));throw new Error(l.message||"Failed to delete trust group")}return await s.json()},o2=async n=>{const s=await fetch(`${kt}/api/trust-management/groups/${n}/join/`,{method:"POST",headers:Rt()});if(!s.ok){const l=await s.json().catch(()=>({}));throw new Error(l.message||"Failed to join trust group")}return await s.json()},c2=async()=>{const n=await fetch(`${kt}/api/trust-management/metrics/`,{method:"GET",headers:Rt()});if(!n.ok){const s=await n.json().catch(()=>({}));throw new Error(s.message||"Failed to fetch trust metrics")}return await n.json()},d2=async()=>{const n=await fetch(`${kt}/api/trust/levels/`,{method:"GET",headers:Rt()});if(!n.ok){const s=await n.json().catch(()=>({}));throw new Error(s.message||"Failed to fetch trust levels")}return await n.json()};class Wo{static show(s="medium"){if(this.isActive)return;this.isActive=!0,this.overlayElement=document.createElement("div"),this.overlayElement.id="bluevision-loading-overlay",this.overlayElement.style.cssText=`
      position: fixed !important;
      top: 0 !important;
      left: 0 !important;
      width: 100vw !important;
      height: 100vh !important;
      background-color: white !important;
      display: flex !important;
      justify-content: center !important;
      align-items: center !important;
      z-index: 2147483647 !important;
      margin: 0 !important;
      padding: 0 !important;
      pointer-events: all !important;
    `;const l={small:"32px",medium:"48px",large:"64px"};this.overlayElement.innerHTML=`
      <style>
        .bluevision-loader {
          transform-style: preserve-3d;
          perspective: 1000px;
          border-radius: 50%;
          width: ${l[s]};
          height: ${l[s]};
          color: #FF3D00;
          position: relative;
          animation: spinDiagonal 2s linear infinite;
        }

        .bluevision-loader:before,
        .bluevision-loader:after {
          content: '';
          display: block;
          position: absolute;
          top: 0;
          left: 0;
          width: inherit;
          height: inherit;
          border-radius: 50%;
          transform: rotateX(70deg);
          animation: 1s spin linear infinite;
        }

        .bluevision-loader:after {
          color: #2196f3;
          transform: rotateY(70deg);
          animation-delay: .4s;
        }

        @keyframes spin {
          0%, 100% {
            box-shadow: .2em 0px 0 0px currentcolor;
          }
          12% {
            box-shadow: .2em .2em 0 0 currentcolor;
          }
          25% {
            box-shadow: 0 .2em 0 0px currentcolor;
          }
          37% {
            box-shadow: -.2em .2em 0 0 currentcolor;
          }
          50% {
            box-shadow: -.2em 0 0 0 currentcolor;
          }
          62% {
            box-shadow: -.2em -.2em 0 0 currentcolor;
          }
          75% {
            box-shadow: 0px -.2em 0 0 currentcolor;
          }
          87% {
            box-shadow: .2em -.2em 0 0 currentcolor;
          }
        }

        @keyframes spinDiagonal {
          0% {
            transform: rotate3d(1, 1, 0, 0deg);
          }
          100% {
            transform: rotate3d(1, 1, 0, 360deg);
          }
        }
        
        .bluevision-rotated {
          display: inline-block;
          transform: rotate(45deg);
        }
      </style>
      <div class="bluevision-rotated">
        <span class="bluevision-loader"></span>
      </div>
    `,document.body.appendChild(this.overlayElement)}static hide(){this.isActive&&(this.isActive=!1,this.overlayElement&&(document.body.removeChild(this.overlayElement),this.overlayElement=null))}}nu(Wo,"overlayElement",null),nu(Wo,"isActive",!1);const Ai=({size:n="medium",fullscreen:s=!1})=>{if(N.useEffect(()=>{if(s)return Wo.show(n),()=>Wo.hide()},[s,n]),s)return null;const l={small:{width:"32px",height:"32px"},medium:{width:"48px",height:"48px"},large:{width:"64px",height:"64px"}};return t.jsxs(t.Fragment,{children:[t.jsx("style",{children:`
          .bluevision-loader {
            transform-style: preserve-3d;
            perspective: 1000px;
            border-radius: 50%;
            color: #FF3D00;
            position: relative;
            animation: spinDiagonal 2s linear infinite;
          }

          .bluevision-loader:before,
          .bluevision-loader:after {
            content: '';
            display: block;
            position: absolute;
            top: 0;
            left: 0;
            width: inherit;
            height: inherit;
            border-radius: 50%;
            transform: rotateX(70deg);
            animation: 1s spin linear infinite;
          }

          .bluevision-loader:after {
            color: #2196f3;
            transform: rotateY(70deg);
            animation-delay: .4s;
          }

          @keyframes spin {
            0%, 100% {
              box-shadow: .2em 0px 0 0px currentcolor;
            }
            12% {
              box-shadow: .2em .2em 0 0 currentcolor;
            }
            25% {
              box-shadow: 0 .2em 0 0px currentcolor;
            }
            37% {
              box-shadow: -.2em .2em 0 0 currentcolor;
            }
            50% {
              box-shadow: -.2em 0 0 0 currentcolor;
            }
            62% {
              box-shadow: -.2em -.2em 0 0 currentcolor;
            }
            75% {
              box-shadow: 0px -.2em 0 0 currentcolor;
            }
            87% {
              box-shadow: .2em -.2em 0 0 currentcolor;
            }
          }

          @keyframes spinDiagonal {
            0% {
              transform: rotate3d(1, 1, 0, 0deg);
            }
            100% {
              transform: rotate3d(1, 1, 0, 360deg);
            }
          }
          
          .bluevision-rotated {
            display: inline-block;
            transform: rotate(45deg);
          }
        `}),t.jsx("div",{style:{display:"flex",justifyContent:"center",alignItems:"center",padding:"40px 20px"},children:t.jsx("div",{className:"bluevision-rotated",children:t.jsx("span",{className:"bluevision-loader",style:l[n]})})})]})},uf=({isOpen:n,onClose:s,onConfirm:l,title:o,message:d,confirmText:f="Confirm",cancelText:m="Cancel",confirmButtonClass:p="confirm-btn",isDestructive:g=!1,actionType:h="default"})=>{const x=()=>{l(),s()},v=()=>{s()},b=Fs.useCallback(()=>h==="activate"||h==="reactivate"?"btn btn-success confirmation-btn-green":h==="deactivate"||h==="delete"?"btn btn-danger confirmation-btn-red":`btn ${g?"btn-danger":"btn-primary"}`,[h,g]);return Fs.useEffect(()=>{if(!n)return;const _=C=>{C.key==="Escape"&&s()};return document.addEventListener("keydown",_),document.body.style.overflow="hidden",()=>{document.removeEventListener("keydown",_),document.body.style.overflow="unset"}},[n,s]),n?t.jsx("div",{className:"confirmation-modal-overlay",onClick:v,children:t.jsxs("div",{className:"confirmation-modal",onClick:_=>_.stopPropagation(),children:[t.jsxs("div",{className:"confirmation-modal-header",children:[t.jsx("h3",{children:o}),t.jsx("button",{className:"confirmation-modal-close",onClick:v,"aria-label":"Close",children:"×"})]}),t.jsx("div",{className:"confirmation-modal-body",children:t.jsx("p",{children:d})}),t.jsxs("div",{className:"confirmation-modal-footer",children:[t.jsx("button",{className:"btn btn-secondary",onClick:v,children:m}),t.jsx("button",{className:b(),onClick:x,children:f})]})]})}):null},ff=({currentPage:n,totalItems:s,itemsPerPage:l,onPageChange:o,showInfo:d=!0,showJumpToPage:f=!0})=>{const m=Math.ceil(s/l),p=(n-1)*l+1,g=Math.min(n*l,s);if(m<=1)return null;const h=()=>{const b=[],_=[];for(let C=Math.max(2,n-2);C<=Math.min(m-1,n+2);C++)b.push(C);return n-2>2?_.push(1,"..."):_.push(1),_.push(...b),n+2<m-1?_.push("...",m):_.push(m),_},x=v=>{if(v.key==="Enter"){const b=parseInt(v.target.value);b>=1&&b<=m&&(o(b),v.target.value="")}};return t.jsxs("div",{className:"pagination-container",children:[d&&t.jsxs("div",{className:"pagination-info",children:["Showing ",p,"-",g," of ",s," items"]}),t.jsxs("div",{className:"pagination-controls",children:[t.jsx("button",{className:"pagination-btn",onClick:()=>o(1),disabled:n===1,title:"Go to first page",children:"⏮ First"}),t.jsx("button",{className:"pagination-btn",onClick:()=>o(n-1),disabled:n===1,title:"Go to previous page",children:"← Previous"}),t.jsx("div",{className:"pagination-pages",children:h().map((v,b)=>t.jsx(Fs.Fragment,{children:v==="..."?t.jsx("span",{className:"pagination-dots",children:"..."}):t.jsx("button",{className:`pagination-page ${n===v?"active":""}`,onClick:()=>o(v),children:v})},b))}),t.jsx("button",{className:"pagination-btn",onClick:()=>o(n+1),disabled:n===m,title:"Go to next page",children:"Next →"}),t.jsx("button",{className:"pagination-btn",onClick:()=>o(m),disabled:n===m,title:"Go to last page",children:"Last ⏭"})]}),f&&m>5&&t.jsxs("div",{className:"pagination-jump",children:[t.jsxs("label",{children:["Jump to page:",t.jsx("input",{type:"number",min:"1",max:m,placeholder:`1-${m}`,onKeyPress:x,className:"pagination-jump-input",title:`Enter a page number between 1 and ${m}`})]}),t.jsx("button",{className:"pagination-btn pagination-jump-btn",onClick:()=>{const v=document.querySelector(".pagination-jump-input"),b=parseInt(v.value);b>=1&&b<=m&&(o(b),v.value="")},title:"Jump to entered page",children:"Go"})]})]})},u2=({active:n=!0,initialSection:s=null})=>{const[l,o]=N.useState([]),[d,f]=N.useState([]),[m,p]=N.useState(!0),[g,h]=N.useState(null),[x,v]=N.useState(null),[b,_]=N.useState(()=>s==="create"?!0:new URLSearchParams(window.location.search).get("section")==="create"),[C,E]=N.useState(()=>{if(s==="create")return"add";const Re=new URLSearchParams(window.location.search).get("section");return"add"}),[A,L]=N.useState(null),[q,P]=N.useState(""),[M,X]=N.useState(""),[Q,K]=N.useState(!1),[se,Ae]=N.useState(!1),[we,ge]=N.useState(!1),[Ne,me]=N.useState(!1),[xe,He]=N.useState(null),[S,H]=N.useState(!1),[F,_e]=N.useState(null),[z,G]=N.useState(1),[ie,oe]=N.useState(10),[re,Te]=N.useState([]),[ue,je]=N.useState({username:"",email:"",first_name:"",last_name:"",password:"",role:"viewer",organization_id:"",is_verified:!1,is_active:!0}),Le=["admin","publisher","viewer"],ne=(x==null?void 0:x.role)==="publisher";(x==null?void 0:x.role)==="admin"||(x==null||x.role);const D=()=>ne?["viewer"]:Le,I=V=>ne?V?!["publisher","admin","BlueVisionAdmin"].includes(V.role):!1:!0;N.useEffect(()=>{if(n){const V=qS();v(V),J(),be()}},[n]),N.useEffect(()=>{s==="create"?(console.log("UserManagement: Opening create modal from prop"),_(!0),E("add")):(s==="roles"||s==="passwords")&&(console.log("UserManagement: Section from prop:",s),_(!1))},[s]),N.useEffect(()=>{const V=()=>{const U=new URLSearchParams(window.location.search).get("section");U==="create"?(_(!0),E("add")):(U==="roles"||U==="passwords")&&_(!1)};return window.addEventListener("popstate",V),()=>{window.removeEventListener("popstate",V)}},[]);const J=async()=>{try{p(!0),h(null),await new Promise(fe=>setTimeout(fe,1e3));const V=await IS();console.log("Users API response:",V),console.log("Full response object:",JSON.stringify(V,null,2));let Re=[];V.results&&V.results.users?Re=V.results.users:V.data&&V.data.users?Re=V.data.users:V.users?Re=V.users:V.data&&Array.isArray(V.data)?Re=V.data:Array.isArray(V)&&(Re=V),console.log("Extracted users data:",Re),console.log("Users data length:",Re.length);const U=Array.isArray(Re)?Re:[];Te(U),o(U)}catch(V){console.error("Failed to load users:",V),h("Failed to load users: "+V.message),o([])}finally{p(!1)}},be=async()=>{try{const V=await df();console.log("Organizations API response:",V);let Re=[];V.results&&V.results.organizations?Re=V.results.organizations:V.data&&V.data.organizations?Re=V.data.organizations:V.organizations?Re=V.organizations:V.data&&Array.isArray(V.data)?Re=V.data:Array.isArray(V)&&(Re=V),console.log("Extracted organizations data:",Re),f(Array.isArray(Re)?Re:[])}catch(V){console.error("Failed to load organizations:",V),f([])}},Me=N.useMemo(()=>{let V=[...re];return q&&(V=V.filter(Re=>{var U,fe,ee,Ce;return((U=Re.username)==null?void 0:U.toLowerCase().includes(q.toLowerCase()))||((fe=Re.first_name)==null?void 0:fe.toLowerCase().includes(q.toLowerCase()))||((ee=Re.last_name)==null?void 0:ee.toLowerCase().includes(q.toLowerCase()))||((Ce=Re.email)==null?void 0:Ce.toLowerCase().includes(q.toLowerCase()))})),M&&(V=V.filter(Re=>Re.role===M)),V},[re,q,M]),Ve=N.useMemo(()=>{const V=(z-1)*ie,Re=V+ie;return Me.slice(V,Re)},[Me,z,ie]);N.useEffect(()=>{o(Ve)},[Ve]);const at=V=>{G(V)},Ke=V=>{oe(V),G(1)},ta=()=>{E("add"),L(null),h(null),je({username:"",email:"",first_name:"",last_name:"",password:"",role:"viewer",organization_id:"",is_verified:!1,is_active:!0}),_(!0)},_t=async V=>{var Re,U,fe;try{K(!0),h(null),await new Promise(et=>setTimeout(et,800));const ee=await Vg(V);console.log("Edit user response:",ee);let Ce=null;if(ee.success&&((Re=ee.data)!=null&&Re.user))Ce=ee.data.user;else if((U=ee.data)!=null&&U.user)Ce=ee.data.user;else if(ee.user)Ce=ee.user;else if(ee.data&&typeof ee.data=="object"&&ee.data.username)Ce=ee.data;else throw console.error("Unable to extract user from response:",ee),new Error("Invalid response format");if(console.log("Edit user data:",Ce),ne&&Ce){const et=Ce.role;if(et==="publisher"||et==="admin"||et==="BlueVisionAdmin"){h("Publishers cannot edit users with publisher, admin, or BlueVisionAdmin roles"),K(!1);return}}if(!Ce||!Ce.username)throw console.error("User data not found or invalid in response. Full response:",ee),new Error("User data not found or invalid in response");E("edit"),L(Ce);const Xe={username:Ce.username||"",email:Ce.email||"",first_name:Ce.first_name||"",last_name:Ce.last_name||"",password:"",role:Ce.role||"viewer",organization_id:((fe=Ce.organization)==null?void 0:fe.id)||Ce.organization_id||"",is_verified:!!Ce.is_verified,is_active:Ce.is_active!==!1};console.log("Setting form data for edit:",Xe),je(Xe),_(!0)}catch(ee){console.error("Error in handleEditUser:",ee),h("Failed to load user details: "+(ee.message||ee))}finally{K(!1)}},Tt=async V=>{var Re,U,fe;try{K(!0),h(null),await new Promise(et=>setTimeout(et,800));const ee=await Vg(V);console.log("View user response:",ee);let Ce=null;if(ee.success&&((Re=ee.data)!=null&&Re.user))Ce=ee.data.user;else if((U=ee.data)!=null&&U.user)Ce=ee.data.user;else if(ee.user)Ce=ee.user;else if(ee.data&&typeof ee.data=="object"&&ee.data.username)Ce=ee.data;else throw console.error("Unable to extract user from response:",ee),new Error("Invalid response format");if(console.log("View user data:",Ce),ne&&Ce){const et=Ce.role;if(et==="publisher"||et==="admin"||et==="BlueVisionAdmin"){h("Publishers cannot view users with publisher, admin, or BlueVisionAdmin roles"),K(!1);return}}if(!Ce||!Ce.username)throw console.error("User data not found or invalid in response. Full response:",ee),new Error("User data not found or invalid in response");E("view"),L(Ce);const Xe={username:Ce.username||"",email:Ce.email||"",first_name:Ce.first_name||"",last_name:Ce.last_name||"",password:"",role:Ce.role||"viewer",organization_id:((fe=Ce.organization)==null?void 0:fe.id)||Ce.organization_id||"",is_verified:!!Ce.is_verified,is_active:Ce.is_active!==!1};console.log("Setting form data for view:",Xe),je(Xe),_(!0)}catch(ee){console.error("Error in handleViewUser:",ee),h("Failed to load user details: "+(ee.message||ee))}finally{K(!1)}},Ft=(V,Re)=>{if(ne){const U=re.find(fe=>fe.id===V);if(U&&(U.role==="publisher"||U.role==="admin"||U.role==="BlueVisionAdmin")){h("Publishers cannot deactivate users with publisher, admin, or BlueVisionAdmin roles");return}}_e({title:"Deactivate User",message:`Are you sure you want to deactivate user "${Re}"?`,confirmText:"Deactivate",isDestructive:!0,actionType:"deactivate",action:async()=>{try{ge(!0),await new Promise(U=>setTimeout(U,800)),await YS(V,"Deactivated by admin"),J()}catch(U){h("Failed to deactivate user: "+U.message)}finally{ge(!1)}}}),H(!0)},Zt=(V,Re)=>{if(ne){const U=re.find(fe=>fe.id===V);if(U&&(U.role==="publisher"||U.role==="admin"||U.role==="BlueVisionAdmin")){h("Publishers cannot reactivate users with publisher, admin, or BlueVisionAdmin roles");return}}_e({title:"Reactivate User",message:`Are you sure you want to reactivate user "${Re}"?`,confirmText:"Reactivate",isDestructive:!1,actionType:"reactivate",action:async()=>{try{ge(!0),await new Promise(U=>setTimeout(U,800)),await GS(V,"Reactivated by admin"),J()}catch(U){h("Failed to reactivate user: "+U.message)}finally{ge(!1)}}}),H(!0)},ae=(V,Re)=>{_e({title:"Permanently Delete User",message:`Are you sure you want to PERMANENTLY DELETE user "${Re}"? This action cannot be undone.`,confirmText:"Delete Permanently",isDestructive:!0,actionType:"delete",action:async()=>{try{ge(!0),await new Promise(U=>setTimeout(U,800)),await VS(V,"Deleted by admin"),J(),me(!1),He(null)}catch(U){h("Failed to delete user: "+U.message)}finally{ge(!1)}}}),H(!0)},De=V=>{if(V.preventDefault(),C==="edit"&&ue.username){const fe=ue.username.trim();if(fe.length<3){h("Username must be at least 3 characters long");return}if(!/^[a-zA-Z0-9_]+$/.test(fe)){h("Username can only contain letters, numbers, and underscores");return}}const Re=C==="add"?"create":"update",U=C==="add"?ue.username:A==null?void 0:A.username;_e({title:`${C==="add"?"Create":"Update"} User`,message:`Are you sure you want to ${Re} user "${U}"?`,confirmText:C==="add"?"Create User":"Update User",isDestructive:!1,actionType:"default",action:async()=>{try{if(Ae(!0),await new Promise(fe=>setTimeout(fe,1e3)),C==="add"){console.log("Creating user with data:",ue);const fe=await $S(ue);console.log("User creation successful:",fe)}else if(C==="edit"){const fe={...ue};fe.password||delete fe.password,fe.username!==A.username&&(console.log("Username changed, updating via changeUsername API"),await PS(A.id,fe.username),delete fe.username),Object.keys(fe).length>0&&(console.log("Updating user with data:",fe),console.log("Selected user ID:",A.id),await FS(A.id,fe))}_(!1),h(null),console.log("About to reload users..."),await J(),console.log("Users reloaded successfully")}catch(fe){console.error("Error in handleSubmit:",fe),Array.isArray(fe)?h(fe.join(", ")):h(typeof fe=="string"?fe:"Failed to save user: "+(fe.message||"Unknown error"))}finally{Ae(!1)}}}),H(!0)},Fe=V=>{const{name:Re,value:U,type:fe,checked:ee}=V.target;console.log("Input change:",{name:Re,value:U,type:fe,checked:ee}),je(Ce=>{const Xe={...Ce,[Re]:fe==="checkbox"?ee:U};return console.log("Updated form data:",Xe),Xe})},ke=Me.length,Be=V=>{const Re=d.find(U=>U.id===V);return Re?Re.name:"N/A"},vt=V=>{He(V),me(!0)},ft=()=>{me(!1),He(null)};return n?m?t.jsx(Ai,{fullscreen:!0}):g?t.jsx("div",{style:{padding:"2rem",color:"red"},children:g}):t.jsxs("div",{style:{padding:"2rem",fontFamily:"Arial, sans-serif",position:"relative"},children:[(we||se)&&t.jsx(Ai,{fullscreen:!0}),t.jsxs("div",{style:{marginBottom:"2rem"},children:[t.jsx("h1",{style:{marginBottom:"0.5rem",color:"#333"},children:"User Management"}),ne&&t.jsxs("div",{style:{padding:"0.75rem 1rem",backgroundColor:"#fff3cd",color:"#856404",borderRadius:"6px",border:"1px solid #ffeaa7",fontSize:"0.875rem",fontWeight:"500"},children:[t.jsx("strong",{children:"Publisher Mode:"})," You can view and manage users from your organization and organizations with trusted relationships. You can only create viewer users, and role changes are restricted."]})]}),t.jsxs("div",{style:{display:"flex",gap:"1rem",marginBottom:"2rem",flexWrap:"wrap",alignItems:"center"},children:[t.jsx("input",{type:"text",placeholder:"Search users...",value:q,onChange:V=>P(V.target.value),style:{padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",minWidth:"200px",backgroundColor:"white",color:"#666"}}),t.jsxs("select",{value:M,onChange:V=>X(V.target.value),style:{padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:"white",color:"#666"},children:[t.jsx("option",{value:"",children:"All Roles"}),D().map(V=>t.jsx("option",{value:V,children:V},V))]}),t.jsx("button",{onClick:ta,style:{padding:"0.5rem 1rem",backgroundColor:"#007bff",color:"white",border:"none",borderRadius:"4px",cursor:"pointer"},children:"Add User"}),t.jsx("div",{className:"items-per-page",children:t.jsxs("label",{children:["Show:",t.jsxs("select",{value:ie,onChange:V=>Ke(parseInt(V.target.value)),children:[t.jsx("option",{value:5,children:"5"}),t.jsx("option",{value:10,children:"10"}),t.jsx("option",{value:25,children:"25"}),t.jsx("option",{value:50,children:"50"})]}),"items per page"]})})]}),t.jsx("div",{style:{marginBottom:"1rem",color:"#6c757d",fontSize:"0.875rem",textAlign:"center"},children:"💡 Click on any user row to view available actions"}),t.jsx("div",{style:{backgroundColor:"white",borderRadius:"12px",boxShadow:"0 4px 6px rgba(0,0,0,0.1)",border:"1px solid #e9ecef"},children:l.map(V=>{var Re;return t.jsxs("div",{onClick:U=>{U.preventDefault(),U.stopPropagation(),vt(V)},style:{display:"flex",alignItems:"center",padding:"1.25rem",borderBottom:"1px solid #e9ecef",transition:"all 0.2s ease",cursor:"pointer",backgroundColor:"transparent"},onMouseEnter:U=>{U.currentTarget.style.backgroundColor="#f8f9fa",U.currentTarget.style.transform="translateX(4px)"},onMouseLeave:U=>{U.currentTarget.style.backgroundColor="transparent",U.currentTarget.style.transform="translateX(0px)"},children:[t.jsxs("div",{style:{flex:"1",minWidth:"0"},children:[t.jsxs("div",{style:{display:"flex",alignItems:"center",gap:"1rem",flexWrap:"wrap"},children:[t.jsx("div",{style:{fontWeight:"600",color:"#212529",fontSize:"1.1rem"},children:V.username}),t.jsx("div",{style:{color:"#495057"},children:`${V.first_name||""} ${V.last_name||""}`.trim()||"N/A"}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:V.role==="admin"?"#d4edda":V.role==="publisher"?"#fff3cd":"#f8f9fa",color:V.role==="admin"?"#155724":V.role==="publisher"?"#856404":"#495057"},children:V.role}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:V.is_active?"#d4edda":"#f8d7da",color:V.is_active?"#155724":"#721c24"},children:V.is_active?"Active":"Inactive"})]}),t.jsxs("div",{style:{marginTop:"0.5rem",color:"#6c757d",fontSize:"0.875rem",display:"flex",gap:"1rem",flexWrap:"wrap"},children:[t.jsx("span",{children:V.email||"No email"}),t.jsxs("span",{children:["Org: ",((Re=V.organization)==null?void 0:Re.name)||Be(V.organization_id)||"N/A"]})]})]}),t.jsx("div",{style:{fontSize:"1.2rem",color:"#6c757d",marginLeft:"1rem",transition:"all 0.2s ease",display:"flex",alignItems:"center",justifyContent:"center",width:"40px",height:"40px",borderRadius:"50%",backgroundColor:"rgba(108, 117, 125, 0.1)"},children:"→"})]},V.id)})}),l.length===0&&re.length>0&&t.jsx("div",{style:{textAlign:"center",padding:"2rem",color:"#666"},children:"No users found matching your criteria."}),re.length===0&&t.jsx("div",{style:{textAlign:"center",padding:"2rem",color:"#666"},children:'No users available. Click "Add User" to create the first user.'}),re.length>0&&t.jsx(ff,{currentPage:z,totalItems:ke,itemsPerPage:ie,onPageChange:at,showInfo:!0,showJumpToPage:!0}),b&&t.jsx("div",{style:{position:"fixed",top:0,left:0,width:"100%",height:"100%",backgroundColor:"rgba(0, 0, 0, 0.5)",display:"flex",alignItems:"center",justifyContent:"center",zIndex:1e3},children:t.jsxs("div",{style:{backgroundColor:"white",padding:"2rem",borderRadius:"8px",maxWidth:"500px",width:"90%",maxHeight:"80vh",overflowY:"auto"},children:[t.jsx("h2",{style:{marginBottom:"1.5rem",color:"#333"},children:C==="add"?"Add New User":C==="edit"?"Edit User":"View User"}),Q?t.jsx(Ai,{size:"medium"}):t.jsxs(t.Fragment,{children:[g&&t.jsx("div",{style:{padding:"1rem",backgroundColor:"#f8d7da",color:"#721c24",borderRadius:"4px",marginBottom:"1rem",border:"1px solid #f5c6cb"},children:g}),t.jsxs("form",{onSubmit:De,children:[t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsxs("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:["Username ",!ue.username&&C==="add"&&t.jsx("span",{style:{color:"red"},children:"*"})]}),t.jsx("input",{type:"text",name:"username",value:ue.username,onChange:Fe,disabled:C==="view",required:!0,pattern:"[a-zA-Z0-9_]+",title:"Username can only contain letters, numbers, and underscores",style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:C==="view"?"#f8f9fa":"white",color:C==="view"?"#333":"#000"}}),C==="edit"&&t.jsx("div",{style:{fontSize:"0.875rem",color:"#666",marginTop:"0.25rem"},children:"Only letters, numbers, and underscores allowed (minimum 3 characters)"})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsxs("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:["Email ",C==="add"&&!ue.email&&t.jsx("span",{style:{color:"red"},children:"*"})," ",!ue.email&&C==="view"&&"(Not available at current access level)"]}),t.jsx("input",{type:"email",name:"email",value:ue.email,onChange:Fe,disabled:C==="view",required:C==="add",placeholder:!ue.email&&C!=="add"?"Email not available":"",style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:C==="view"?"#f8f9fa":"white",color:C==="view"?"#333":"#000"}})]}),t.jsxs("div",{style:{display:"flex",gap:"1rem",marginBottom:"1rem"},children:[t.jsxs("div",{style:{flex:1},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"First Name"}),t.jsx("input",{type:"text",name:"first_name",value:ue.first_name,onChange:Fe,disabled:C==="view",style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:C==="view"?"#f8f9fa":"white",color:C==="view"?"#333":"#000"}})]}),t.jsxs("div",{style:{flex:1},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Last Name"}),t.jsx("input",{type:"text",name:"last_name",value:ue.last_name,onChange:Fe,disabled:C==="view",style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:C==="view"?"#f8f9fa":"white",color:C==="view"?"#333":"#000"}})]})]}),C==="add"&&t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsxs("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:["Password ",!ue.password&&t.jsx("span",{style:{color:"red"},children:"*"})]}),t.jsx("input",{type:"password",name:"password",value:ue.password,onChange:Fe,required:!0,style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:"white",color:"#999"}})]}),C==="edit"&&t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"New Password (leave blank to keep current)"}),t.jsx("input",{type:"password",name:"password",value:ue.password,onChange:Fe,style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:"white",color:"#999"}})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsxs("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:["Role",ne&&C!=="view"&&t.jsx("span",{style:{fontSize:"0.75rem",color:"#856404",marginLeft:"0.5rem"},children:"(Limited to viewer role)"})]}),t.jsx("select",{name:"role",value:ue.role,onChange:Fe,disabled:C==="view"||ne&&C==="edit",style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:C==="view"||ne&&C==="edit"?"#f8f9fa":"white",color:C==="view"||ne&&C==="edit"?"#666":"#000"},children:D().map(V=>t.jsx("option",{value:V,children:V},V))}),ne&&C==="edit"&&t.jsx("div",{style:{fontSize:"0.75rem",color:"#666",marginTop:"0.25rem"},children:"Role changes are restricted for publisher users"})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsxs("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:["Organization ",C==="add"&&!ue.organization_id&&t.jsx("span",{style:{color:"red"},children:"*"})]}),t.jsxs("select",{name:"organization_id",value:ue.organization_id,onChange:Fe,disabled:C==="view",required:C==="add",style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:C==="view"?"#f8f9fa":"white",color:C==="view"?"#333":"#000"},children:[t.jsx("option",{value:"",children:"Select Organization"}),d.map(V=>t.jsx("option",{value:V.id,children:V.name},V.id))]})]}),t.jsxs("div",{style:{display:"flex",gap:"1rem",marginBottom:"1rem"},children:[t.jsxs("label",{style:{display:"flex",alignItems:"center",gap:"0.5rem"},children:[t.jsx("input",{type:"checkbox",name:"is_verified",checked:ue.is_verified,onChange:Fe,disabled:C==="view"}),"Verified"]}),t.jsxs("label",{style:{display:"flex",alignItems:"center",gap:"0.5rem"},children:[t.jsx("input",{type:"checkbox",name:"is_active",checked:ue.is_active,onChange:Fe,disabled:C==="view"}),"Active"]})]}),t.jsxs("div",{style:{display:"flex",gap:"1rem",justifyContent:"flex-end"},children:[t.jsx("button",{type:"button",onClick:()=>_(!1),style:{padding:"0.5rem 1rem",border:"1px solid #ddd",backgroundColor:"white",color:"#666",borderRadius:"4px",cursor:"pointer"},children:C==="view"?"Close":"Cancel"}),C!=="view"&&t.jsx("button",{type:"submit",style:{padding:"0.5rem 1rem",backgroundColor:"#007bff",color:"white",border:"none",borderRadius:"4px",cursor:"pointer"},children:C==="add"?"Add User":"Update User"})]})]})]})]})}),Ne&&xe&&t.jsx("div",{style:{position:"fixed",top:0,left:0,width:"100%",height:"100%",backgroundColor:"rgba(0, 0, 0, 0.5)",display:"flex",alignItems:"center",justifyContent:"center",zIndex:1001},children:t.jsxs("div",{style:{backgroundColor:"white",padding:"2rem",borderRadius:"12px",minWidth:"300px",maxWidth:"400px",boxShadow:"0 10px 25px rgba(0,0,0,0.1)"},children:[t.jsxs("div",{style:{marginBottom:"1.5rem"},children:[t.jsx("h3",{style:{margin:"0 0 0.5rem 0",color:"#333",fontSize:"1.25rem",wordBreak:"break-word",lineHeight:"1.3"},children:xe.username}),t.jsx("div",{style:{color:"#666",fontSize:"0.875rem",marginBottom:"0.5rem"},children:`${xe.first_name||""} ${xe.last_name||""}`.trim()||"N/A"}),t.jsxs("div",{style:{color:"#666",fontSize:"0.875rem",display:"flex",gap:"0.5rem",alignItems:"center"},children:[t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:xe.role==="admin"?"#d4edda":xe.role==="publisher"?"#fff3cd":"#f8f9fa",color:xe.role==="admin"?"#155724":xe.role==="publisher"?"#856404":"#495057"},children:xe.role}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:xe.is_active?"#d4edda":"#f8d7da",color:xe.is_active?"#155724":"#721c24"},children:xe.is_active?"Active":"Inactive"})]})]}),t.jsxs("div",{style:{display:"flex",flexDirection:"column",gap:"0.75rem"},children:[I(xe)&&t.jsx("button",{onClick:()=>{ft(),Tt(xe.id)},style:{padding:"0.75rem 1rem",backgroundColor:"#5D8AA8",color:"white",border:"none",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:V=>V.target.style.backgroundColor="#4A7088",onMouseLeave:V=>V.target.style.backgroundColor="#5D8AA8",children:"View Details"}),I(xe)&&t.jsx("button",{onClick:()=>{ft(),_t(xe.id)},style:{padding:"0.75rem 1rem",backgroundColor:"#5D8AA8",color:"white",border:"none",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:V=>V.target.style.backgroundColor="#4A7088",onMouseLeave:V=>V.target.style.backgroundColor="#5D8AA8",children:"Edit User"}),I(xe)&&(xe.is_active?t.jsx("button",{onClick:()=>{ft(),Ft(xe.id,xe.username)},style:{padding:"0.75rem 1rem",backgroundColor:"white",color:"#5D8AA8",border:"2px solid #5D8AA8",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:V=>{V.target.style.borderColor="#dc3545",V.target.style.color="#dc3545"},onMouseLeave:V=>{V.target.style.borderColor="#5D8AA8",V.target.style.color="#5D8AA8"},children:"Deactivate User"}):t.jsx("button",{onClick:()=>{ft(),Zt(xe.id,xe.username)},style:{padding:"0.75rem 1rem",backgroundColor:"white",color:"#5D8AA8",border:"2px solid #5D8AA8",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:V=>{V.target.style.borderColor="#28a745",V.target.style.color="#28a745"},onMouseLeave:V=>{V.target.style.borderColor="#5D8AA8",V.target.style.color="#5D8AA8"},children:"Reactivate User"})),t.jsx("button",{onClick:()=>{ft(),ae(xe.id,xe.username)},style:{padding:"0.75rem 1rem",backgroundColor:"#5D8AA8",color:"white",border:"none",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:V=>V.target.style.backgroundColor="#4A7088",onMouseLeave:V=>V.target.style.backgroundColor="#5D8AA8",children:"Permanently Delete"})]}),t.jsx("div",{style:{marginTop:"1.5rem",paddingTop:"1rem",borderTop:"1px solid #e9ecef"},children:t.jsx("button",{onClick:ft,style:{padding:"0.5rem 1rem",border:"1px solid #ddd",backgroundColor:"white",color:"#666",borderRadius:"6px",cursor:"pointer",width:"100%",fontSize:"0.875rem"},children:"Cancel"})})]})}),t.jsx(uf,{isOpen:S,onClose:()=>H(!1),onConfirm:F==null?void 0:F.action,title:F==null?void 0:F.title,message:F==null?void 0:F.message,confirmText:F==null?void 0:F.confirmText,isDestructive:F==null?void 0:F.isDestructive,actionType:F==null?void 0:F.actionType})]}):null},f2=({active:n=!0,initialSection:s=null})=>{const[l,o]=N.useState([]),[d,f]=N.useState(["educational","government","private"]),[m,p]=N.useState(!0),[g,h]=N.useState(null),[x,v]=N.useState(()=>s==="create"?!0:new URLSearchParams(window.location.search).get("section")==="create"),[b,_]=N.useState(()=>{if(s==="create")return"add";const De=new URLSearchParams(window.location.search).get("section");return"add"}),[C,E]=N.useState(null),[A,L]=N.useState(""),[q,P]=N.useState(""),[M,X]=N.useState(!1),[Q,K]=N.useState(!1),[se,Ae]=N.useState(!1),[we,ge]=N.useState(!1),[Ne,me]=N.useState(null),[xe,He]=N.useState(!1),[S,H]=N.useState(null),[F,_e]=N.useState(1),[z,G]=N.useState(10),[ie,oe]=N.useState([]),[re,Te]=N.useState({name:"",domain:"",contact_email:"",description:"",website:"",organization_type:"educational",primary_user:{username:"",email:"",password:"",first_name:"",last_name:""}}),ue=async()=>{var ae;try{const De=await KS();if(console.log("Organization types response:",De),De.success&&((ae=De.data)!=null&&ae.organization_types)){const Fe=De.data.organization_types.map(ke=>ke.value);f(Fe),console.log("Loaded organization types:",Fe)}}catch(De){console.error("Failed to load organization types:",De)}};N.useEffect(()=>{n&&(je(),ue())},[n]),N.useEffect(()=>{s==="create"?(console.log("OrganisationManagement: Opening create modal from prop"),v(!0),_("add")):(s==="roles"||s==="passwords")&&(console.log("OrganisationManagement: Section from prop:",s),v(!1))},[s]),N.useEffect(()=>{const ae=()=>{new URLSearchParams(window.location.search).get("section")==="create"&&(v(!0),_("add"))};return window.addEventListener("popstate",ae),()=>{window.removeEventListener("popstate",ae)}},[]);const je=async()=>{try{p(!0),h(null),await new Promise(ke=>setTimeout(ke,1e3));const ae=await df();console.log("Organizations API response:",ae),console.log("Full response object:",JSON.stringify(ae,null,2));let De=[];ae.results&&ae.results.organizations?De=ae.results.organizations:ae.data&&ae.data.organizations?De=ae.data.organizations:ae.organizations?De=ae.organizations:ae.data&&Array.isArray(ae.data)?De=ae.data:Array.isArray(ae)&&(De=ae),console.log("Extracted organizations data:",De),console.log("Organizations data length:",De.length);const Fe=Array.isArray(De)?De:[];oe(Fe),o(Fe)}catch(ae){console.error("Failed to load organizations:",ae),h("Failed to load organizations: "+ae.message),o([])}finally{p(!1)}},Le=N.useMemo(()=>{let ae=[...ie];return A&&(ae=ae.filter(De=>{var Fe,ke,Be;return((Fe=De.name)==null?void 0:Fe.toLowerCase().includes(A.toLowerCase()))||((ke=De.domain)==null?void 0:ke.toLowerCase().includes(A.toLowerCase()))||((Be=De.contact_email)==null?void 0:Be.toLowerCase().includes(A.toLowerCase()))})),q&&(ae=ae.filter(De=>De.organization_type===q)),ae},[ie,A,q]),ne=N.useMemo(()=>{const ae=(F-1)*z,De=ae+z;return Le.slice(ae,De)},[Le,F,z]);N.useEffect(()=>{o(ne)},[ne]);const D=ae=>{_e(ae)},I=ae=>{G(ae),_e(1)},J=()=>{_("add"),E(null),h(null),Te({name:"",domain:"",contact_email:"",description:"",website:"",organization_type:"educational",primary_user:{username:"",email:"",password:"",first_name:"",last_name:""}}),v(!0)},be=async ae=>{var De,Fe;try{X(!0),h(null),await new Promise(ft=>setTimeout(ft,800));const ke=await Pg(ae);console.log("Edit organization response:",ke);let Be=null;if(ke.success&&((De=ke.data)!=null&&De.organization))Be=ke.data.organization;else if((Fe=ke.data)!=null&&Fe.organization)Be=ke.data.organization;else if(ke.organization)Be=ke.organization;else if(ke.data&&typeof ke.data=="object"&&ke.data.name)Be=ke.data;else throw console.error("Unable to extract organization from response:",ke),new Error("Invalid response format");if(console.log("Edit organization data:",Be),!Be||!Be.name)throw console.error("Organization data not found or invalid in response. Full response:",ke),new Error("Organization data not found or invalid in response");_("edit"),E(Be);const vt={name:Be.name||"",domain:Be.domain||"",contact_email:Be.contact_email||"",description:Be.description||"",website:Be.website||"",organization_type:Be.organization_type||"educational",primary_user:{username:"",email:"",password:"",first_name:"",last_name:""}};console.log("Setting form data for edit:",vt),Te(vt),v(!0)}catch(ke){console.error("Error in handleEditOrganization:",ke),h("Failed to load organization details: "+(ke.message||ke))}finally{X(!1)}},Me=async ae=>{var De,Fe;try{X(!0),h(null),await new Promise(ft=>setTimeout(ft,800));const ke=await Pg(ae);console.log("View organization response:",ke);let Be=null;if(ke.success&&((De=ke.data)!=null&&De.organization))Be=ke.data.organization;else if((Fe=ke.data)!=null&&Fe.organization)Be=ke.data.organization;else if(ke.organization)Be=ke.organization;else if(ke.data&&typeof ke.data=="object"&&ke.data.name)Be=ke.data;else throw console.error("Unable to extract organization from response:",ke),new Error("Invalid response format");if(console.log("View organization data:",Be),!Be||!Be.name)throw console.error("Organization data not found or invalid in response. Full response:",ke),new Error("Organization data not found or invalid in response");_("view"),E(Be);const vt={name:Be.name||"",domain:Be.domain||"",contact_email:Be.contact_email||"",description:Be.description||"",website:Be.website||"",organization_type:Be.organization_type||"educational",primary_user:{username:"",email:"",password:"",first_name:"",last_name:""}};console.log("Setting form data for view:",vt),Te(vt),v(!0)}catch(ke){console.error("Error in handleViewOrganization:",ke),h("Failed to load organization details: "+(ke.message||ke))}finally{X(!1)}},Ve=(ae,De)=>{H({title:"Deactivate Organization",message:`Are you sure you want to deactivate organisation "${De}"?`,confirmText:"Deactivate",isDestructive:!0,actionType:"deactivate",action:async()=>{try{Ae(!0),await new Promise(Fe=>setTimeout(Fe,800)),await QS(ae,"Deactivated by admin"),je()}catch(Fe){h("Failed to deactivate organization: "+Fe.message)}finally{Ae(!1)}}}),He(!0)},at=(ae,De)=>{H({title:"Reactivate Organization",message:`Are you sure you want to reactivate organisation "${De}"?`,confirmText:"Reactivate",isDestructive:!1,actionType:"reactivate",action:async()=>{try{Ae(!0),await new Promise(Fe=>setTimeout(Fe,800)),await JS(ae,"Reactivated by admin"),je()}catch(Fe){h("Failed to reactivate organization: "+Fe.message)}finally{Ae(!1)}}}),He(!0)},Ke=(ae,De)=>{H({title:"Permanently Delete Organization",message:`Are you sure you want to PERMANENTLY DELETE organization "${De}"? This action cannot be undone.`,confirmText:"Delete Permanently",isDestructive:!0,actionType:"delete",action:async()=>{try{Ae(!0),await new Promise(Fe=>setTimeout(Fe,800)),await WS(ae,"Deleted by admin"),je(),ge(!1),me(null)}catch(Fe){h("Failed to delete organization: "+Fe.message)}finally{Ae(!1)}}}),He(!0)},ta=ae=>{ae.preventDefault();const De=b==="add"?"create":"update",Fe=b==="add"?re.name:C==null?void 0:C.name;H({title:`${b==="add"?"Create":"Update"} Organization`,message:`Are you sure you want to ${De} organization "${Fe}"?`,confirmText:b==="add"?"Create Organization":"Update Organization",isDestructive:!1,actionType:"default",action:async()=>{try{if(K(!0),await new Promise(ke=>setTimeout(ke,1e3)),b==="add")console.log("Creating organization with data:",re),await XS(re);else if(b==="edit"){const ke={...re};delete ke.primary_user,console.log("Updating organization with data:",ke),console.log("Selected organization ID:",C.id),await ZS(C.id,ke)}v(!1),h(null),je()}catch(ke){console.error("Error in handleSubmit:",ke),Array.isArray(ke)?h(ke.join(", ")):h(typeof ke=="string"?ke:"Failed to save organization: "+(ke.message||"Unknown error"))}finally{K(!1)}}}),He(!0)},_t=ae=>{const{name:De,value:Fe}=ae.target;if(console.log("Input change:",{name:De,value:Fe}),De.startsWith("primary_user.")){const ke=De.substring(13);Te(Be=>({...Be,primary_user:{...Be.primary_user,[ke]:Fe}}))}else Te(ke=>({...ke,[De]:Fe}))},Tt=Le.length,Ft=ae=>{me(ae),ge(!0)},Zt=()=>{ge(!1),me(null)};return n?m?t.jsx(Ai,{fullscreen:!0}):g?t.jsx("div",{style:{padding:"2rem",color:"red"},children:g}):t.jsxs("div",{style:{padding:"2rem",fontFamily:"Arial, sans-serif",position:"relative"},children:[(se||Q)&&t.jsx(Ai,{fullscreen:!0}),t.jsx("h1",{style:{marginBottom:"2rem",color:"#333"},children:"Organisation Management"}),t.jsxs("div",{style:{display:"flex",gap:"1rem",marginBottom:"2rem",flexWrap:"wrap",alignItems:"center"},children:[t.jsx("input",{type:"text",placeholder:"Search organisations...",value:A,onChange:ae=>L(ae.target.value),style:{padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",minWidth:"200px",backgroundColor:"white",color:"#666"}}),t.jsxs("select",{value:q,onChange:ae=>P(ae.target.value),style:{padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:"white",color:"#666"},children:[t.jsx("option",{value:"",children:"All Types"}),d.map(ae=>t.jsx("option",{value:ae,children:ae},ae))]}),t.jsx("button",{onClick:J,style:{padding:"0.5rem 1rem",backgroundColor:"#007bff",color:"white",border:"none",borderRadius:"4px",cursor:"pointer"},children:"Add Organisation"}),t.jsx("div",{className:"items-per-page",children:t.jsxs("label",{children:["Show:",t.jsxs("select",{value:z,onChange:ae=>I(parseInt(ae.target.value)),children:[t.jsx("option",{value:5,children:"5"}),t.jsx("option",{value:10,children:"10"}),t.jsx("option",{value:25,children:"25"}),t.jsx("option",{value:50,children:"50"})]}),"items per page"]})})]}),t.jsx("div",{style:{marginBottom:"1rem",color:"#6c757d",fontSize:"0.875rem",textAlign:"center"},children:"💡 Click on any organisation row to view available actions"}),t.jsx("div",{style:{backgroundColor:"white",borderRadius:"12px",boxShadow:"0 4px 6px rgba(0,0,0,0.1)",border:"1px solid #e9ecef"},children:l.map(ae=>t.jsxs("div",{onClick:De=>{De.preventDefault(),De.stopPropagation(),Ft(ae)},style:{display:"flex",alignItems:"center",padding:"1.25rem",borderBottom:"1px solid #e9ecef",transition:"all 0.2s ease",cursor:"pointer",backgroundColor:"transparent"},onMouseEnter:De=>{De.currentTarget.style.backgroundColor="#f8f9fa",De.currentTarget.style.transform="translateX(4px)"},onMouseLeave:De=>{De.currentTarget.style.backgroundColor="transparent",De.currentTarget.style.transform="translateX(0px)"},children:[t.jsxs("div",{style:{flex:"1",minWidth:"0"},children:[t.jsxs("div",{style:{display:"flex",alignItems:"center",gap:"1rem",flexWrap:"wrap"},children:[t.jsx("div",{style:{fontWeight:"600",color:"#212529",fontSize:"1.1rem"},children:ae.name}),t.jsx("div",{style:{color:"#495057"},children:ae.domain||"N/A"}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:ae.organization_type==="educational"?"#d4edda":ae.organization_type==="government"?"#fff3cd":"#f8f9fa",color:ae.organization_type==="educational"?"#155724":ae.organization_type==="government"?"#856404":"#495057"},children:ae.organization_type}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:ae.is_active?"#d4edda":"#f8d7da",color:ae.is_active?"#155724":"#721c24"},children:ae.is_active?"Active":"Inactive"})]}),t.jsxs("div",{style:{marginTop:"0.5rem",color:"#6c757d",fontSize:"0.875rem",display:"flex",gap:"1rem",flexWrap:"wrap"},children:[t.jsx("span",{children:ae.contact_email||"No email"}),ae.description&&t.jsxs("span",{children:[ae.description.substring(0,50),"..."]})]})]}),t.jsx("div",{style:{fontSize:"1.2rem",color:"#6c757d",marginLeft:"1rem",transition:"all 0.2s ease",display:"flex",alignItems:"center",justifyContent:"center",width:"40px",height:"40px",borderRadius:"50%",backgroundColor:"rgba(108, 117, 125, 0.1)"},children:"→"})]},ae.id))}),l.length===0&&ie.length>0&&t.jsx("div",{style:{textAlign:"center",padding:"2rem",color:"#666"},children:"No organisations found matching your criteria."}),ie.length===0&&t.jsx("div",{style:{textAlign:"center",padding:"2rem",color:"#666"},children:'No organisations available. Click "Add Organisation" to create the first organization.'}),ie.length>0&&t.jsx(ff,{currentPage:F,totalItems:Tt,itemsPerPage:z,onPageChange:D,showInfo:!0,showJumpToPage:!0}),x&&t.jsx("div",{style:{position:"fixed",top:0,left:0,width:"100%",height:"100%",backgroundColor:"rgba(0, 0, 0, 0.5)",display:"flex",alignItems:"center",justifyContent:"center",zIndex:1e3},children:t.jsxs("div",{style:{backgroundColor:"white",padding:"2rem",borderRadius:"8px",maxWidth:"600px",width:"90%",maxHeight:"80vh",overflowY:"auto"},children:[t.jsx("h2",{style:{marginBottom:"1.5rem",color:"#333"},children:b==="add"?"Add New Organisation":b==="edit"?"Edit Organisation":"View Organisation"}),M?t.jsx(Ai,{size:"medium"}):t.jsxs(t.Fragment,{children:[g&&t.jsx("div",{style:{padding:"1rem",backgroundColor:"#f8d7da",color:"#721c24",borderRadius:"4px",marginBottom:"1rem",border:"1px solid #f5c6cb"},children:g}),t.jsxs("form",{onSubmit:ta,children:[t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Organisation Name *"}),t.jsx("input",{type:"text",name:"name",value:re.name,onChange:_t,disabled:b==="view",required:!0,style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:b==="view"?"#f8f9fa":"white",color:"#333"}})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Domain"}),t.jsx("input",{type:"text",name:"domain",value:re.domain,onChange:_t,disabled:b==="view",placeholder:"e.g., university.edu",style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:b==="view"?"#f8f9fa":"white",color:"#333"}})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Contact Email *"}),t.jsx("input",{type:"email",name:"contact_email",value:re.contact_email,onChange:_t,disabled:b==="view",required:!0,style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:b==="view"?"#f8f9fa":"white",color:"#333"}})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Organisation Type *"}),t.jsx("select",{name:"organization_type",value:re.organization_type,onChange:_t,disabled:b==="view",required:!0,style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:b==="view"?"#f8f9fa":"white",color:"#333"},children:d.map(ae=>t.jsx("option",{value:ae,children:ae},ae))})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Description"}),t.jsx("textarea",{name:"description",value:re.description,onChange:_t,disabled:b==="view",rows:"3",style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:b==="view"?"#f8f9fa":"white",color:"#333",resize:"vertical"}})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Website"}),t.jsx("input",{type:"url",name:"website",value:re.website,onChange:_t,disabled:b==="view",placeholder:"https://www.example.com",style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:b==="view"?"#f8f9fa":"white",color:"#333"}})]}),b==="add"&&t.jsxs("div",{children:[t.jsx("h3",{style:{marginBottom:"1rem",color:"#333",borderTop:"1px solid #ddd",paddingTop:"1rem"},children:"Primary User (Administrator)"}),t.jsxs("div",{style:{display:"flex",gap:"1rem",marginBottom:"1rem"},children:[t.jsxs("div",{style:{flex:1},children:[t.jsxs("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:["Username ",!re.primary_user.username&&t.jsx("span",{style:{color:"red"},children:"*"})]}),t.jsx("input",{type:"text",name:"primary_user.username",value:re.primary_user.username,onChange:_t,required:!0,style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:"white",color:"#000"}})]}),t.jsxs("div",{style:{flex:1},children:[t.jsxs("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:["Email ",!re.primary_user.email&&t.jsx("span",{style:{color:"red"},children:"*"})]}),t.jsx("input",{type:"email",name:"primary_user.email",value:re.primary_user.email,onChange:_t,required:!0,style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:"white",color:"#000"}})]})]}),t.jsxs("div",{style:{display:"flex",gap:"1rem",marginBottom:"1rem"},children:[t.jsxs("div",{style:{flex:1},children:[t.jsxs("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:["First Name ",!re.primary_user.first_name&&t.jsx("span",{style:{color:"red"},children:"*"})]}),t.jsx("input",{type:"text",name:"primary_user.first_name",value:re.primary_user.first_name,onChange:_t,required:!0,style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:"white",color:"#000"}})]}),t.jsxs("div",{style:{flex:1},children:[t.jsxs("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:["Last Name ",!re.primary_user.last_name&&t.jsx("span",{style:{color:"red"},children:"*"})]}),t.jsx("input",{type:"text",name:"primary_user.last_name",value:re.primary_user.last_name,onChange:_t,required:!0,style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:"white",color:"#000"}})]})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsxs("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:["Password ",!re.primary_user.password&&t.jsx("span",{style:{color:"red"},children:"*"})]}),t.jsx("input",{type:"password",name:"primary_user.password",value:re.primary_user.password,onChange:_t,required:!0,style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:"white",color:"#999"}})]})]}),t.jsxs("div",{style:{display:"flex",gap:"1rem",justifyContent:"flex-end"},children:[t.jsx("button",{type:"button",onClick:()=>v(!1),style:{padding:"0.5rem 1rem",border:"1px solid #ddd",backgroundColor:"white",color:"#666",borderRadius:"4px",cursor:"pointer"},children:b==="view"?"Close":"Cancel"}),b!=="view"&&t.jsx("button",{type:"submit",style:{padding:"0.5rem 1rem",backgroundColor:"#007bff",color:"white",border:"none",borderRadius:"4px",cursor:"pointer"},children:b==="add"?"Add Organisation":"Update Organisation"})]})]})]})]})}),we&&Ne&&t.jsx("div",{style:{position:"fixed",top:0,left:0,width:"100%",height:"100%",backgroundColor:"rgba(0, 0, 0, 0.5)",display:"flex",alignItems:"center",justifyContent:"center",zIndex:1001},children:t.jsxs("div",{style:{backgroundColor:"white",padding:"2rem",borderRadius:"12px",minWidth:"300px",maxWidth:"400px",boxShadow:"0 10px 25px rgba(0,0,0,0.1)"},children:[t.jsxs("div",{style:{marginBottom:"1.5rem"},children:[t.jsx("h3",{style:{margin:"0 0 0.5rem 0",color:"#333",fontSize:"1.25rem"},children:Ne.name}),t.jsx("div",{style:{color:"#666",fontSize:"0.875rem",marginBottom:"0.5rem"},children:Ne.domain||"No domain"}),t.jsxs("div",{style:{color:"#666",fontSize:"0.875rem",display:"flex",gap:"0.5rem",alignItems:"center"},children:[t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:Ne.organization_type==="educational"?"#d4edda":Ne.organization_type==="government"?"#fff3cd":"#f8f9fa",color:Ne.organization_type==="educational"?"#155724":Ne.organization_type==="government"?"#856404":"#495057"},children:Ne.organization_type}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:Ne.is_active?"#d4edda":"#f8d7da",color:Ne.is_active?"#155724":"#721c24"},children:Ne.is_active?"Active":"Inactive"})]})]}),t.jsxs("div",{style:{display:"flex",flexDirection:"column",gap:"0.75rem"},children:[t.jsx("button",{onClick:()=>{Zt(),Me(Ne.id)},style:{padding:"0.75rem 1rem",backgroundColor:"#5D8AA8",color:"white",border:"none",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:ae=>ae.target.style.backgroundColor="#4A7088",onMouseLeave:ae=>ae.target.style.backgroundColor="#5D8AA8",children:"View Details"}),t.jsx("button",{onClick:()=>{Zt(),be(Ne.id)},style:{padding:"0.75rem 1rem",backgroundColor:"#5D8AA8",color:"white",border:"none",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:ae=>ae.target.style.backgroundColor="#4A7088",onMouseLeave:ae=>ae.target.style.backgroundColor="#5D8AA8",children:"Edit Organisation"}),Ne.is_active?t.jsx("button",{onClick:()=>{Zt(),Ve(Ne.id,Ne.name)},style:{padding:"0.75rem 1rem",backgroundColor:"white",color:"#5D8AA8",border:"2px solid #5D8AA8",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:ae=>{ae.target.style.borderColor="#dc3545",ae.target.style.color="#dc3545"},onMouseLeave:ae=>{ae.target.style.borderColor="#5D8AA8",ae.target.style.color="#5D8AA8"},children:"Deactivate Organisation"}):t.jsx("button",{onClick:()=>{Zt(),at(Ne.id,Ne.name)},style:{padding:"0.75rem 1rem",backgroundColor:"white",color:"#5D8AA8",border:"2px solid #5D8AA8",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:ae=>{ae.target.style.borderColor="#28a745",ae.target.style.color="#28a745"},onMouseLeave:ae=>{ae.target.style.borderColor="#5D8AA8",ae.target.style.color="#5D8AA8"},children:"Reactivate Organisation"}),t.jsx("button",{onClick:()=>{Zt(),Ke(Ne.id,Ne.name)},style:{padding:"0.75rem 1rem",backgroundColor:"#5D8AA8",color:"white",border:"none",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:ae=>ae.target.style.backgroundColor="#4A7088",onMouseLeave:ae=>ae.target.style.backgroundColor="#5D8AA8",children:"Permanently Delete"})]}),t.jsx("div",{style:{marginTop:"1.5rem",paddingTop:"1rem",borderTop:"1px solid #e9ecef"},children:t.jsx("button",{onClick:Zt,style:{padding:"0.5rem 1rem",border:"1px solid #ddd",backgroundColor:"white",color:"#666",borderRadius:"6px",cursor:"pointer",width:"100%",fontSize:"0.875rem"},children:"Cancel"})})]})}),t.jsx(uf,{isOpen:xe,onClose:()=>He(!1),onConfirm:S==null?void 0:S.action,title:S==null?void 0:S.title,message:S==null?void 0:S.message,confirmText:S==null?void 0:S.confirmText,isDestructive:S==null?void 0:S.isDestructive,actionType:S==null?void 0:S.actionType})]}):null};function h2({active:n,initialTab:s=null}){var vt,ft,V,Re;const[l,o]=N.useState({relationships:[],groups:[],metrics:{},organizations:[],trustLevels:[]}),[d,f]=N.useState(!0),[m,p]=N.useState(null),[g,h]=N.useState(null),[x,v]=N.useState(()=>s&&["relationships","groups","metrics"].includes(s)?s:new URLSearchParams(window.location.search).get("tab")||"relationships"),[b,_]=N.useState(!1),[C,E]=N.useState("add"),[A,L]=N.useState("relationship"),[q,P]=N.useState(null),[M,X]=N.useState(!1),[Q,K]=N.useState(!1),[se,Ae]=N.useState(!1),[we,ge]=N.useState(null),[Ne,me]=N.useState(!1),[xe,He]=N.useState(null),[S,H]=N.useState(!1),[F,_e]=N.useState(null),[z,G]=N.useState(!1),[ie,oe]=N.useState(""),[re,Te]=N.useState(""),[ue,je]=N.useState(1),[Le,ne]=N.useState(10),[D,I]=N.useState({source_organization:"",target_organization:"",trust_level:"",relationship_type:"bilateral",notes:"",name:"",description:"",group_type:"industry",is_public:!1,requires_approval:!0}),be=JSON.parse(localStorage.getItem("crisp_user")||"{}").role==="BlueVisionAdmin";N.useEffect(()=>{n&&Me()},[n]),N.useEffect(()=>{s&&["relationships","groups","metrics"].includes(s)&&v(s)},[s]);const Me=async()=>{var U,fe,ee,Ce,Xe,et;try{f(!0),p(null),console.log("TrustManagement: Fetching trust data...");const[ve,Ot,St,Ee,R]=await Promise.all([e2().catch(Ie=>(console.error("Failed to fetch trust relationships:",Ie),{data:[]})),i2().catch(Ie=>(console.error("Failed to fetch trust groups:",Ie),{data:[]})),c2().catch(Ie=>(console.error("Failed to fetch trust metrics:",Ie),{data:{}})),df().catch(Ie=>(console.error("Failed to fetch organizations:",Ie),{data:{organizations:[]}})),d2().catch(Ie=>(console.error("Failed to fetch trust levels:",Ie),[]))]);console.log("TrustManagement: API responses:",{relationships:ve,groups:Ot,metrics:St,organizations:Ee,trustLevels:R}),console.log("🔍 RELATIONSHIPS RESPONSE ANALYSIS:"),console.log("📊 Response keys:",Object.keys(ve||{}));try{console.log("📋 Full JSON:",JSON.stringify(ve,null,2))}catch(Ie){console.log("❌ JSON stringify failed:",Ie.message),console.log("📋 Raw response:",ve)}console.log("🔍 Property checks:"),console.log("  - success:",ve==null?void 0:ve.success),console.log("  - trusts:",ve==null?void 0:ve.trusts),console.log("  - data:",ve==null?void 0:ve.data),console.log("  - results:",ve==null?void 0:ve.results),console.log("  - count:",ve==null?void 0:ve.count),console.log("  - next:",ve==null?void 0:ve.next),console.log("  - previous:",ve==null?void 0:ve.previous),console.log("🔍 TRUST LEVELS DETAILED:",{trustLevelsResponse:R,isArray:Array.isArray(R),length:Array.isArray(R)?R.length:"N/A",firstItem:Array.isArray(R)&&R.length>0?R[0]:"None",allItems:Array.isArray(R)?R:"Not an array"});let ce=[];console.log("🔄 Attempting relationship extraction..."),Array.isArray(ve==null?void 0:ve.trusts)?(ce=ve.trusts,console.log("✅ Extracted relationships from .trusts property:",ce.length)):Array.isArray((U=ve==null?void 0:ve.results)==null?void 0:U.trusts)?(ce=ve.results.trusts,console.log("✅ Extracted relationships from .results.trusts property:",ce.length)):(fe=ve==null?void 0:ve.results)!=null&&fe.success&&Array.isArray((ee=ve==null?void 0:ve.results)==null?void 0:ee.trusts)?(ce=ve.results.trusts,console.log("✅ Extracted relationships from paginated .results.trusts property:",ce.length)):Array.isArray((Ce=ve==null?void 0:ve.data)==null?void 0:Ce.trusts)?(ce=ve.data.trusts,console.log("✅ Extracted relationships from .data.trusts property:",ce.length)):Array.isArray(ve==null?void 0:ve.data)?(ce=ve.data,console.log("✅ Extracted relationships from .data property:",ce.length)):Array.isArray(ve==null?void 0:ve.results)?(ce=ve.results,console.log("✅ Extracted relationships from .results property:",ce.length)):Array.isArray(ve)?(ce=ve,console.log("✅ Using relationships response directly:",ce.length)):(console.log("❌ Could not extract relationships array from response"),console.log("📋 Available properties:",Object.keys(ve||{})),console.log("📋 Type of response:",typeof ve)),o({relationships:ce,groups:Array.isArray(Ot.data)?Ot.data:Array.isArray(Ot)?Ot:[],metrics:St.data&&typeof St.data=="object"?St.data:St&&typeof St=="object"?St:{},organizations:Array.isArray((Xe=Ee.results)==null?void 0:Xe.organizations)?Ee.results.organizations:Array.isArray((et=Ee.data)==null?void 0:et.organizations)?Ee.data.organizations:Array.isArray(Ee.data)?Ee.data:Array.isArray(Ee)?Ee:[],trustLevels:Array.isArray(R.trust_levels)?R.trust_levels:Array.isArray(R.data)?R.data:Array.isArray(R)?R:[]})}catch(ve){console.error("Error fetching trust data:",ve),p("Failed to load trust data")}finally{f(!1)}},Ve=U=>{if(!["relationships","groups","metrics"].includes(U)||U===x)return;v(U);const fe=new URLSearchParams(window.location.search);fe.set("tab",U);const ee=`${window.location.pathname}?${fe.toString()}`;window.history.replaceState(null,"",ee)},at=(U,fe,ee=null)=>{var Ce,Xe,et;if(E(U),L(fe),P(ee),U==="edit"&&ee)if(fe==="relationship"){const ve=((Ce=l.trustLevels.find(Ee=>Ee.name.toLowerCase().trim()===ee.trust_level.toLowerCase().trim()||Ee.name.toUpperCase().trim()===ee.trust_level.toUpperCase().trim()||String(Ee.id).toLowerCase().trim()===ee.trust_level.toLowerCase().trim()||Ee.name===ee.trust_level||Ee.id===ee.trust_level||String(Ee.id)===String(ee.trust_level)))==null?void 0:Ce.id)||ee.trust_level.toLowerCase()||"";console.log("🔍 TRUST LEVEL MAPPING:",{itemTrustLevel:ee.trust_level,itemTrustLevelLower:ee.trust_level.toLowerCase(),availableLevels:l.trustLevels.map(Ee=>({id:Ee.id,name:Ee.name})),mappedId:ve,mapping:{exactMatch:l.trustLevels.find(Ee=>Ee.name===ee.trust_level),lowerMatch:l.trustLevels.find(Ee=>Ee.name.toLowerCase()===ee.trust_level.toLowerCase()),upperMatch:l.trustLevels.find(Ee=>Ee.name.toUpperCase()===ee.trust_level.toUpperCase()),idMatch:l.trustLevels.find(Ee=>Ee.id===ee.trust_level.toLowerCase())}}),console.log("🔧 EDIT MODE - Mapping organizations for relationship:",{relationshipItem:ee,sourceOrg:ee.source_organization,sourceOrgName:ee.source_organization_name,targetOrg:ee.target_organization,targetOrgName:ee.target_organization_name,trustLevel:ee.trust_level,availableOrgs:l.organizations.map(Ee=>({id:Ee.id,name:Ee.name})),availableTrustLevels:l.trustLevels.map(Ee=>({id:Ee.id,name:Ee.name}))});const Ot=((Xe=l.organizations.find(Ee=>Ee.name===ee.source_organization||Ee.name===ee.source_organization_name||Ee.id===ee.source_organization))==null?void 0:Xe.id)||ee.source_organization||"",St=((et=l.organizations.find(Ee=>Ee.name===ee.target_organization||Ee.name===ee.target_organization_name||Ee.id===ee.target_organization))==null?void 0:et.id)||ee.target_organization||"";console.log("✅ MAPPED - Organization IDs:",{sourceOrgId:Ot,targetOrgId:St,trustLevelId:ve,finalFormData:{source_organization:Ot,target_organization:St,trust_level:ve,relationship_type:ee.relationship_type||"bilateral",notes:ee.notes||""}}),I({source_organization:Ot,target_organization:St,trust_level:ve,relationship_type:ee.relationship_type||"bilateral",notes:ee.notes||""})}else fe==="group"&&I({name:ee.name||"",description:ee.description||"",group_type:ee.group_type||"industry",is_public:ee.is_public||!1,requires_approval:ee.requires_approval||!0,trust_level:ee.default_trust_level_id||""});else I({source_organization:"",target_organization:"",trust_level:"",relationship_type:"bilateral",notes:"",name:"",description:"",group_type:"industry",is_public:!1,requires_approval:!0});_(!0)},Ke=()=>{_(!1),P(null),X(!1),K(!1)},ta=async U=>{var Ce;U.preventDefault(),p(null);const fe=C==="add"?"create":"update",ee=A==="relationship"?`relationship with ${((Ce=l.organizations.find(Xe=>Xe.id===D.target_organization))==null?void 0:Ce.name)||"selected organization"}`:D.name;He({title:`${C==="add"?"Create":"Update"} ${A==="relationship"?"Trust Relationship":"Trust Group"}`,message:`Are you sure you want to ${fe} ${A} "${ee}"?`,confirmText:C==="add"?`Create ${A==="relationship"?"Relationship":"Group"}`:`Update ${A==="relationship"?"Relationship":"Group"}`,isDestructive:!1,actionType:"default",action:async()=>{var Xe,et;try{if(K(!0),A==="relationship"){console.log("🚀 SUBMIT - Converting form data to API format:",{formData:D,availableTrustLevels:l.trustLevels,selectedTrustLevelId:D.trust_level});const ve=((Xe=l.organizations.find(rt=>rt.id===D.source_organization))==null?void 0:Xe.name)||D.source_organization,Ot=((et=l.organizations.find(rt=>rt.id===D.target_organization))==null?void 0:et.name)||D.target_organization,St=l.trustLevels.find(rt=>rt.id===D.trust_level||rt.id==D.trust_level||rt.name===D.trust_level||rt.name.toLowerCase()===D.trust_level.toLowerCase());let Ee=(St==null?void 0:St.name)||null;const R=(St==null?void 0:St.id)||D.trust_level;if(!Ee)throw console.error("❌ TRUST LEVEL ERROR: Could not find trust level name for ID:",D.trust_level),console.error("Available trust levels:",l.trustLevels),new Error(`Trust level not found for ID: ${D.trust_level}`);let ce=Ee.toLowerCase();console.log("🔄 CONVERTED - API data:",{sourceOrgName:ve,targetOrgName:Ot,originalTrustLevelName:Ee,finalTrustLevelName:ce,trustLevelId:R,originalTrustLevelId:D.trust_level,trustLevelObj:St,currentItemTrustLevel:q==null?void 0:q.trust_level,backendExpectation:'Backend expects lowercase names like "high", "medium", "low"',conversionProcess:{input:D.trust_level,foundObject:St,outputName:Ee,finalOutputName:ce,outputId:R,willMatch:["high","medium","low"].includes(ce)}});const Ie={source_organization:D.source_organization,target_organization:D.target_organization,trust_level:ce,trust_level_id:R,relationship_type:D.relationship_type,notes:D.notes};console.log("📤 FINAL API PAYLOAD:",Ie),C==="add"?(await t2(Ie),h("Trust relationship created successfully")):(await Xg(q.id,Ie),h("Trust relationship updated successfully"))}else if(A==="group"){const ve={...D};D.trust_level&&(ve.default_trust_level_id=D.trust_level,delete ve.trust_level),C==="add"?(await s2(ve),h("Trust group created successfully")):(await r2(q.id,ve),h("Trust group updated successfully"))}setTimeout(()=>h(null),5e3),Ke(),Me()}catch(ve){console.error(`Error ${fe}ing ${A}:`,ve),p(`Failed to ${fe} ${A}: ${ve.message||ve}`)}finally{K(!1)}}}),me(!0)},_t=U=>{ge(U),Ae(!0)},Tt=()=>{Ae(!1),ge(null)},Ft=U=>{var ee,Ce,Xe;const fe=we;if(fe)switch(U){case"view":Tt(),_e(fe),H(!0);break;case"edit":Tt(),at("edit",x==="relationships"?"relationship":"group",fe);break;case"activate":He({title:"Activate Relationship",message:`Are you sure you want to activate the relationship with ${((ee=fe.target_organization)==null?void 0:ee.name)||fe.target_organization_name||"the selected organization"}?`,confirmText:"Activate",isDestructive:!1,actionType:"default",action:async()=>{try{let ve="public";if(fe.trust_level){const Ot=fe.trust_level.match(/\(([^)]+)\)/);ve=Ot?Ot[1]:fe.trust_level.toLowerCase().split(" ")[0]}await a2(fe.id,"accept",ve,"Relationship activated"),h("Relationship activated successfully"),setTimeout(()=>h(null),5e3),Tt(),Me()}catch(ve){p("Failed to activate relationship: "+ve.message)}}}),me(!0);break;case"suspend":He({title:"Suspend Relationship",message:`Are you sure you want to suspend the relationship with ${((Ce=fe.target_organization)==null?void 0:Ce.name)||fe.target_organization_name||"the selected organization"}?`,confirmText:"Suspend",isDestructive:!0,actionType:"destructive",action:async()=>{try{let ve="public";if(fe.trust_level){const Ot=fe.trust_level.match(/\(([^)]+)\)/);ve=Ot?Ot[1]:fe.trust_level.toLowerCase().split(" ")[0]}await Xg(fe.id,{trust_level:ve,message:"Relationship suspended"}),h("Relationship suspended successfully"),setTimeout(()=>h(null),5e3),Tt(),Me()}catch(ve){p("Failed to suspend relationship: "+ve.message)}}}),me(!0);break;case"delete":const et=x==="relationships"?`relationship with ${((Xe=fe.target_organization)==null?void 0:Xe.name)||fe.target_organization_name||"the selected organization"}`:`group "${fe.name}"`;He({title:`Delete ${x==="relationships"?"Trust Relationship":"Trust Group"}`,message:`Are you sure you want to delete this ${et}? This action cannot be undone.`,confirmText:"Delete",isDestructive:!0,actionType:"destructive",action:async()=>{try{x==="relationships"?(await n2(fe.id,"Relationship deleted by user"),h("Trust relationship deleted successfully")):(await l2(fe.id),h("Trust group deleted successfully")),setTimeout(()=>h(null),5e3),Tt(),Me()}catch(ve){p(`Failed to delete ${x==="relationships"?"relationship":"group"}: ${ve.message}`)}}}),me(!0);break;case"join":He({title:"Join Trust Group",message:`Are you sure you want to join the group "${fe.name}"?`,confirmText:"Join Group",isDestructive:!1,actionType:"default",action:async()=>{try{await o2(fe.id),h("Successfully joined trust group!"),setTimeout(()=>h(null),5e3),Tt(),Me()}catch(ve){p("Failed to join trust group: "+ve.message)}}}),me(!0);break}},ae=(x==="relationships"?l.relationships:l.groups).filter(ee=>{var et,ve;const Ce=ie===""||(x==="relationships"?(((et=ee.target_organization)==null?void 0:et.name)||ee.target_organization_name||((ve=ee.source_organization)==null?void 0:ve.name)||ee.source_organization_name||"").toLowerCase().includes(ie.toLowerCase()):(ee.name||"").toLowerCase().includes(ie.toLowerCase())),Xe=re===""||(x==="relationships"?ee.status===re:re==="public"?ee.is_public:!ee.is_public);return Ce&&Xe}),De=ae.length,Fe=(ue-1)*Le,ke=ae.slice(Fe,Fe+Le),Be=U=>{je(U)};return n?d?t.jsx("div",{className:"trust-management",children:t.jsx(Ai,{})}):t.jsxs("div",{style:{padding:"2rem",fontFamily:"Arial, sans-serif",position:"relative"},children:[(d||Q)&&t.jsx(Ai,{fullscreen:!0}),t.jsxs("div",{style:{marginBottom:"2rem"},children:[t.jsx("h1",{style:{marginBottom:"0.5rem",color:"#333"},children:"Trust Management"}),!be&&t.jsxs("div",{style:{padding:"0.75rem 1rem",backgroundColor:"#fff3cd",color:"#856404",borderRadius:"6px",border:"1px solid #ffeaa7",fontSize:"0.875rem",fontWeight:"500"},children:[t.jsx("strong",{children:"Publisher Mode:"})," You can manage trust relationships and groups for your organization and organizations with trusted relationships."]})]}),m&&t.jsxs("div",{style:{backgroundColor:"#f8d7da",color:"#721c24",border:"1px solid #f5c6cb",borderRadius:"4px",padding:"0.75rem 1rem",marginBottom:"1rem",display:"flex",justifyContent:"space-between",alignItems:"center"},children:[t.jsx("span",{children:m}),t.jsx("button",{onClick:()=>p(null),style:{background:"none",border:"none",color:"#721c24",fontSize:"1.25rem",cursor:"pointer",padding:"0",lineHeight:"1"},children:"×"})]}),g&&t.jsxs("div",{style:{backgroundColor:"#d4edda",color:"#155724",border:"1px solid #c3e6cb",borderRadius:"4px",padding:"0.75rem 1rem",marginBottom:"1rem",display:"flex",justifyContent:"space-between",alignItems:"center"},children:[t.jsx("span",{children:g}),t.jsx("button",{onClick:()=>h(null),style:{background:"none",border:"none",color:"#155724",fontSize:"1.25rem",cursor:"pointer",padding:"0",lineHeight:"1"},children:"×"})]}),t.jsx("div",{style:{marginBottom:"1.5rem"},children:t.jsx("div",{style:{borderBottom:"1px solid #dee2e6"},children:["relationships","groups","metrics"].map(U=>t.jsxs("button",{onClick:()=>Ve(U),style:{padding:"0.75rem 1.5rem",border:"none",backgroundColor:x===U?"#007bff":"transparent",color:x===U?"white":"#495057",borderRadius:"4px 4px 0 0",marginRight:"0.25rem",cursor:"pointer",textTransform:"capitalize",fontWeight:x===U?"600":"400"},children:[U," (",U==="relationships"?l.relationships.length:U==="groups"?l.groups.length:"N/A",")"]},U))})}),x!=="metrics"&&t.jsxs(t.Fragment,{children:[t.jsxs("div",{style:{display:"flex",gap:"1rem",marginBottom:"2rem",flexWrap:"wrap",alignItems:"center"},children:[t.jsxs("div",{style:{display:"flex",gap:"1rem",alignItems:"center",flex:1},children:[t.jsx("input",{type:"text",placeholder:`Search ${x}...`,value:ie,onChange:U=>oe(U.target.value),style:{padding:"0.5rem",border:"1px solid #ced4da",borderRadius:"4px",minWidth:"200px"}}),t.jsxs("select",{value:re,onChange:U=>Te(U.target.value),style:{padding:"0.5rem",border:"1px solid #ced4da",borderRadius:"4px",minWidth:"120px"},children:[t.jsx("option",{value:"",children:"All Status"}),x==="relationships"?t.jsxs(t.Fragment,{children:[t.jsx("option",{value:"active",children:"Active"}),t.jsx("option",{value:"pending",children:"Pending"}),t.jsx("option",{value:"suspended",children:"Suspended"})]}):t.jsxs(t.Fragment,{children:[t.jsx("option",{value:"public",children:"Public"}),t.jsx("option",{value:"private",children:"Private"})]})]})]}),t.jsxs("button",{onClick:()=>at("add",x==="relationships"?"relationship":"group"),disabled:!be&&x==="groups",style:{padding:"0.5rem 1rem",backgroundColor:!be&&x==="groups"?"#6c757d":"#007bff",color:"white",border:"none",borderRadius:"4px",cursor:!be&&x==="groups"?"not-allowed":"pointer",fontWeight:"500"},title:!be&&x==="groups"?"Only administrators can create trust groups":"",children:["Add ",x==="relationships"?"Relationship":"Group"]})]}),t.jsx("div",{style:{backgroundColor:"white",borderRadius:"8px",boxShadow:"0 4px 6px rgba(0,0,0,0.1)",border:"1px solid #e9ecef"},children:ke.length===0?t.jsxs("div",{style:{textAlign:"center",padding:"3rem",color:"#6c757d"},children:[t.jsxs("h4",{style:{marginBottom:"0.5rem"},children:["No ",x," found"]}),t.jsx("p",{style:{margin:"0"},children:ae.length===0&&(ie||re)?"No items match your search criteria.":`No ${x} available. Click "Add ${x==="relationships"?"Relationship":"Group"}" to create the first one.`})]}):ke.map(U=>{var fe,ee;return t.jsxs("div",{onClick:Ce=>{Ce.preventDefault(),Ce.stopPropagation(),_t(U)},style:{display:"flex",alignItems:"center",padding:"1.25rem",borderBottom:"1px solid #e9ecef",transition:"all 0.2s ease",cursor:"pointer",backgroundColor:"transparent"},onMouseEnter:Ce=>{Ce.currentTarget.style.backgroundColor="#f8f9fa",Ce.currentTarget.style.transform="translateX(4px)"},onMouseLeave:Ce=>{Ce.currentTarget.style.backgroundColor="transparent",Ce.currentTarget.style.transform="translateX(0px)"},children:[t.jsx("div",{style:{flex:"1",minWidth:"0"},children:x==="relationships"?t.jsxs(t.Fragment,{children:[t.jsxs("div",{style:{display:"flex",alignItems:"center",gap:"1rem",flexWrap:"wrap"},children:[t.jsxs("div",{style:{fontWeight:"600",color:"#212529",fontSize:"1.1rem"},children:[((fe=U.source_organization)==null?void 0:fe.name)||U.source_organization_name||"Unknown"," → ",((ee=U.target_organization)==null?void 0:ee.name)||U.target_organization_name||"Unknown"]}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:U.trust_level==="HIGH"?"#d4edda":U.trust_level==="MEDIUM"?"#fff3cd":"#f8f9fa",color:U.trust_level==="HIGH"?"#155724":U.trust_level==="MEDIUM"?"#856404":"#495057"},children:U.trust_level}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:U.status==="active"?"#d4edda":U.status==="pending"?"#fff3cd":"#f8d7da",color:U.status==="active"?"#155724":U.status==="pending"?"#856404":"#721c24"},children:U.status||"Unknown"})]}),t.jsxs("div",{style:{marginTop:"0.5rem",color:"#6c757d",fontSize:"0.875rem",display:"flex",gap:"1rem",flexWrap:"wrap"},children:[t.jsxs("span",{children:["Type: ",U.relationship_type]}),U.notes&&t.jsxs("span",{children:["Notes: ",U.notes]})]})]}):t.jsxs(t.Fragment,{children:[t.jsxs("div",{style:{display:"flex",alignItems:"center",gap:"1rem",flexWrap:"wrap"},children:[t.jsx("div",{style:{fontWeight:"600",color:"#212529",fontSize:"1.1rem"},children:U.name}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:U.group_type==="SECURITY"?"#d4edda":U.group_type==="BUSINESS"?"#fff3cd":"#f8f9fa",color:U.group_type==="SECURITY"?"#155724":U.group_type==="BUSINESS"?"#856404":"#495057"},children:U.group_type}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:U.is_public?"#d4edda":"#fff3cd",color:U.is_public?"#155724":"#856404"},children:U.is_public?"Public":"Private"})]}),t.jsxs("div",{style:{marginTop:"0.5rem",color:"#6c757d",fontSize:"0.875rem",display:"flex",gap:"1rem",flexWrap:"wrap"},children:[t.jsx("span",{children:U.description}),t.jsxs("span",{children:["Members: ",U.member_count||0]})]})]})}),t.jsx("div",{style:{fontSize:"1.2rem",color:"#6c757d",marginLeft:"1rem",transition:"transform 0.2s ease"},children:"→"})]},U.id)})}),De>Le&&t.jsx("div",{style:{marginTop:"1rem"},children:t.jsx(ff,{currentPage:ue,totalItems:De,itemsPerPage:Le,onPageChange:Be,showInfo:!0,showJumpToPage:!0})})]}),x==="metrics"&&t.jsx("div",{style:{display:"grid",gridTemplateColumns:"repeat(auto-fit, minmax(250px, 1fr))",gap:"1rem"},children:[{title:"Total Relationships",value:l.relationships.length,description:be?"All system relationships":"Your organization relationships"},{title:"Active Groups",value:l.groups.length,description:be?"All system groups":"Your accessible groups"},{title:"Trust Score",value:l.metrics.trust_score||"N/A",description:be?"System average":"Organization trust score"},{title:"Connected Organizations",value:l.metrics.connected_orgs||0,description:be?"Total connected orgs":"Organizations you trust"}].map((U,fe)=>t.jsxs("div",{style:{backgroundColor:"white",border:"1px solid #dee2e6",borderRadius:"8px",padding:"1.5rem",textAlign:"center"},children:[t.jsx("h4",{style:{margin:"0 0 0.5rem 0",color:"#495057",fontSize:"1rem"},children:U.title}),t.jsx("div",{style:{fontSize:"2rem",fontWeight:"bold",color:"#007bff",margin:"0.5rem 0"},children:U.value}),t.jsx("div",{style:{fontSize:"0.75rem",color:"#6c757d",fontStyle:"italic"},children:U.description})]},fe))}),b&&t.jsx("div",{style:{position:"fixed",top:0,left:0,width:"100%",height:"100%",backgroundColor:"rgba(0, 0, 0, 0.5)",display:"flex",alignItems:"center",justifyContent:"center",zIndex:1e3},children:t.jsxs("div",{style:{backgroundColor:"white",borderRadius:"8px",padding:"1.5rem",width:"90%",maxWidth:"500px",maxHeight:"90vh",overflowY:"auto"},children:[t.jsxs("h3",{style:{margin:"0 0 1rem 0"},children:[C==="add"?"Create":"Edit"," ",A==="relationship"?"Trust Relationship":"Trust Group"]}),t.jsxs("form",{onSubmit:ta,children:[A==="relationship"?t.jsxs(t.Fragment,{children:[be&&t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Source Organization *"}),t.jsxs("select",{value:D.source_organization||"",onChange:U=>I({...D,source_organization:U.target.value}),required:be,style:{width:"100%",padding:"0.5rem",border:"1px solid #ced4da",borderRadius:"4px"},children:[t.jsx("option",{value:"",children:"Select Source Organization"}),l.organizations.map(U=>t.jsx("option",{value:U.id,children:U.name},U.id))]})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Target Organization *"}),t.jsxs("select",{value:D.target_organization,onChange:U=>I({...D,target_organization:U.target.value}),required:!0,style:{width:"100%",padding:"0.5rem",border:"1px solid #ced4da",borderRadius:"4px"},children:[t.jsx("option",{value:"",children:"Select Organization"}),l.organizations.map(U=>t.jsx("option",{value:U.id,children:U.name},U.id))]})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Trust Level *"}),t.jsxs("select",{value:D.trust_level,onChange:U=>I({...D,trust_level:U.target.value}),required:!0,style:{width:"100%",padding:"0.5rem",border:"1px solid #ced4da",borderRadius:"4px"},children:[t.jsx("option",{value:"",children:"Select Trust Level"}),l.trustLevels.map(U=>t.jsx("option",{value:U.id,children:U.name},U.id))]})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Relationship Type"}),t.jsxs("select",{value:D.relationship_type,onChange:U=>I({...D,relationship_type:U.target.value}),style:{width:"100%",padding:"0.5rem",border:"1px solid #ced4da",borderRadius:"4px"},children:[t.jsx("option",{value:"bilateral",children:"Bilateral"}),t.jsx("option",{value:"unilateral",children:"Unilateral"})]})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Notes"}),t.jsx("textarea",{value:D.notes,onChange:U=>I({...D,notes:U.target.value}),rows:3,placeholder:"Optional notes about this relationship...",style:{width:"100%",padding:"0.5rem",border:"1px solid #ced4da",borderRadius:"4px",resize:"vertical"}})]})]}):t.jsxs(t.Fragment,{children:[t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Group Name *"}),t.jsx("input",{type:"text",value:D.name,onChange:U=>I({...D,name:U.target.value}),required:!0,placeholder:"Enter group name...",style:{width:"100%",padding:"0.5rem",border:"1px solid #ced4da",borderRadius:"4px"}})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Description"}),t.jsx("textarea",{value:D.description,onChange:U=>I({...D,description:U.target.value}),rows:3,placeholder:"Describe the purpose of this group...",style:{width:"100%",padding:"0.5rem",border:"1px solid #ced4da",borderRadius:"4px",resize:"vertical"}})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Group Type"}),t.jsxs("select",{value:D.group_type,onChange:U=>I({...D,group_type:U.target.value}),style:{width:"100%",padding:"0.5rem",border:"1px solid #ced4da",borderRadius:"4px"},children:[t.jsx("option",{value:"industry",children:"Industry"}),t.jsx("option",{value:"regional",children:"Regional"}),t.jsx("option",{value:"security",children:"Security"}),t.jsx("option",{value:"research",children:"Research"})]})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Trust Level"}),t.jsxs("select",{value:D.trust_level,onChange:U=>I({...D,trust_level:U.target.value}),style:{width:"100%",padding:"0.5rem",border:"1px solid #ced4da",borderRadius:"4px"},children:[t.jsx("option",{value:"",children:"Select Trust Level"}),l.trustLevels.map(U=>t.jsx("option",{value:U.id,children:U.name},U.id))]})]}),t.jsxs("div",{style:{marginBottom:"1rem",display:"flex",gap:"1rem"},children:[t.jsxs("label",{style:{display:"flex",alignItems:"center",gap:"0.5rem"},children:[t.jsx("input",{type:"checkbox",checked:D.is_public,onChange:U=>I({...D,is_public:U.target.checked})}),"Public Group"]}),t.jsxs("label",{style:{display:"flex",alignItems:"center",gap:"0.5rem"},children:[t.jsx("input",{type:"checkbox",checked:D.requires_approval,onChange:U=>I({...D,requires_approval:U.target.checked})}),"Requires Approval"]})]})]}),t.jsxs("div",{style:{display:"flex",gap:"0.5rem",justifyContent:"flex-end",marginTop:"1.5rem"},children:[t.jsx("button",{type:"button",onClick:Ke,disabled:Q,style:{padding:"0.5rem 1rem",backgroundColor:"#6c757d",color:"white",border:"none",borderRadius:"4px",cursor:Q?"not-allowed":"pointer"},children:"Cancel"}),t.jsx("button",{type:"submit",disabled:Q,style:{padding:"0.5rem 1rem",backgroundColor:"#007bff",color:"white",border:"none",borderRadius:"4px",cursor:Q?"not-allowed":"pointer"},children:Q?"Saving...":C==="add"?"Create":"Update"})]})]})]})}),se&&we&&t.jsx("div",{style:{position:"fixed",top:0,left:0,width:"100%",height:"100%",backgroundColor:"rgba(0, 0, 0, 0.5)",display:"flex",alignItems:"center",justifyContent:"center",zIndex:1001},children:t.jsxs("div",{style:{backgroundColor:"white",padding:"2rem",borderRadius:"12px",minWidth:"300px",maxWidth:"400px",boxShadow:"0 10px 25px rgba(0,0,0,0.1)"},children:[t.jsxs("div",{style:{marginBottom:"1.5rem"},children:[t.jsx("h3",{style:{margin:"0 0 0.5rem 0",color:"#333",fontSize:"1.25rem",wordBreak:"break-word",lineHeight:"1.3"},children:x==="relationships"?`${((vt=we.source_organization)==null?void 0:vt.name)||we.source_organization_name||"Unknown"} → ${((ft=we.target_organization)==null?void 0:ft.name)||we.target_organization_name||"Unknown"}`:we.name}),t.jsx("div",{style:{color:"#666",fontSize:"0.875rem",marginBottom:"0.5rem"},children:x==="relationships"?`Trust Level: ${we.trust_level}`:we.description}),t.jsx("div",{style:{color:"#666",fontSize:"0.875rem",display:"flex",gap:"0.5rem",alignItems:"center"},children:x==="relationships"?t.jsxs(t.Fragment,{children:[t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:we.relationship_type==="BILATERAL"?"#d4edda":"#fff3cd",color:we.relationship_type==="BILATERAL"?"#155724":"#856404"},children:we.relationship_type}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:we.status==="active"?"#d4edda":we.status==="pending"?"#fff3cd":"#f8d7da",color:we.status==="active"?"#155724":we.status==="pending"?"#856404":"#721c24"},children:we.status})]}):t.jsxs(t.Fragment,{children:[t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:we.group_type==="SECURITY"?"#d4edda":"#fff3cd",color:we.group_type==="SECURITY"?"#155724":"#856404"},children:we.group_type}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:we.is_public?"#d4edda":"#fff3cd",color:we.is_public?"#155724":"#856404"},children:we.is_public?"Public":"Private"})]})})]}),t.jsxs("div",{style:{display:"flex",flexDirection:"column",gap:"0.75rem"},children:[t.jsx("button",{onClick:()=>{Tt(),Ft("view")},style:{padding:"0.75rem 1rem",backgroundColor:"#5D8AA8",color:"white",border:"none",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:U=>U.target.style.backgroundColor="#4A7088",onMouseLeave:U=>U.target.style.backgroundColor="#5D8AA8",children:"View Details"}),t.jsx("button",{onClick:()=>{Tt(),Ft("edit")},style:{padding:"0.75rem 1rem",backgroundColor:"#5D8AA8",color:"white",border:"none",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:U=>U.target.style.backgroundColor="#4A7088",onMouseLeave:U=>U.target.style.backgroundColor="#5D8AA8",children:"Edit Details"}),x==="relationships"&&we.status!=="active"&&t.jsx("button",{onClick:()=>{Tt(),Ft("activate")},style:{padding:"0.75rem 1rem",backgroundColor:"#5D8AA8",color:"white",border:"none",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:U=>U.target.style.backgroundColor="#4A7088",onMouseLeave:U=>U.target.style.backgroundColor="#5D8AA8",children:"Activate Relationship"}),x==="relationships"&&we.status==="active"&&t.jsx("button",{onClick:()=>{Tt(),Ft("suspend")},style:{padding:"0.75rem 1rem",backgroundColor:"white",color:"#5D8AA8",border:"2px solid #5D8AA8",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:U=>{U.target.style.backgroundColor="#5D8AA8",U.target.style.color="white"},onMouseLeave:U=>{U.target.style.backgroundColor="white",U.target.style.color="#5D8AA8"},children:"Suspend Relationship"}),x==="groups"&&!be&&t.jsx("button",{onClick:()=>{Tt(),Ft("join")},style:{padding:"0.75rem 1rem",backgroundColor:"#5D8AA8",color:"white",border:"none",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:U=>U.target.style.backgroundColor="#4A7088",onMouseLeave:U=>U.target.style.backgroundColor="#5D8AA8",children:"Join Group"}),t.jsxs("button",{onClick:()=>{Tt(),Ft("delete")},style:{padding:"0.75rem 1rem",backgroundColor:"#5D8AA8",color:"white",border:"none",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:U=>U.target.style.backgroundColor="#4A7088",onMouseLeave:U=>U.target.style.backgroundColor="#5D8AA8",children:["Delete ",x==="relationships"?"Relationship":"Group"]})]}),t.jsx("div",{style:{marginTop:"1.5rem",paddingTop:"1rem",borderTop:"1px solid #e9ecef"},children:t.jsx("button",{onClick:Tt,style:{padding:"0.5rem 1rem",border:"1px solid #ddd",backgroundColor:"white",color:"#666",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",width:"100%"},children:"Cancel"})})]})}),Ne&&t.jsx(uf,{isOpen:Ne,onClose:()=>me(!1),onConfirm:xe==null?void 0:xe.action,title:xe==null?void 0:xe.title,message:xe==null?void 0:xe.message,confirmText:xe==null?void 0:xe.confirmText,isDestructive:xe==null?void 0:xe.isDestructive,actionType:xe==null?void 0:xe.actionType}),S&&F&&t.jsx("div",{style:{position:"fixed",top:0,left:0,width:"100%",height:"100%",backgroundColor:"rgba(0, 0, 0, 0.5)",display:"flex",alignItems:"center",justifyContent:"center",zIndex:1e3},children:t.jsxs("div",{style:{backgroundColor:"white",borderRadius:"12px",padding:"2rem",width:"90%",maxWidth:"600px",maxHeight:"90vh",overflowY:"auto",boxShadow:"0 10px 25px rgba(0,0,0,0.1)"},children:[t.jsxs("div",{style:{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:"1.5rem"},children:[t.jsx("h2",{style:{margin:"0",color:"#333"},children:x==="relationships"?"Trust Relationship Details":"Trust Group Details"}),t.jsx("button",{onClick:()=>H(!1),style:{background:"none",border:"none",fontSize:"1.5rem",cursor:"pointer",color:"#666"},children:"×"})]}),x==="relationships"?t.jsx("div",{children:t.jsxs("div",{style:{marginBottom:"1.5rem"},children:[t.jsx("h3",{style:{color:"#5D8AA8",marginBottom:"1rem"},children:"Relationship Overview"}),t.jsxs("div",{style:{display:"grid",gridTemplateColumns:"1fr 1fr",gap:"1rem",marginBottom:"1rem"},children:[t.jsxs("div",{children:[t.jsx("strong",{children:"Source Organization:"}),t.jsx("br",{}),((V=F.source_organization)==null?void 0:V.name)||F.source_organization_name||"Unknown"]}),t.jsxs("div",{children:[t.jsx("strong",{children:"Target Organization:"}),t.jsx("br",{}),((Re=F.target_organization)==null?void 0:Re.name)||F.target_organization_name||"Unknown"]}),t.jsxs("div",{children:[t.jsx("strong",{children:"Trust Level:"}),t.jsx("br",{}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.875rem",fontWeight:"600",backgroundColor:F.trust_level==="HIGH"?"#d4edda":F.trust_level==="MEDIUM"?"#fff3cd":"#f8f9fa",color:F.trust_level==="HIGH"?"#155724":F.trust_level==="MEDIUM"?"#856404":"#495057"},children:F.trust_level})]}),t.jsxs("div",{children:[t.jsx("strong",{children:"Status:"}),t.jsx("br",{}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.875rem",fontWeight:"600",backgroundColor:F.status==="active"?"#d4edda":F.status==="pending"?"#fff3cd":"#f8d7da",color:F.status==="active"?"#155724":F.status==="pending"?"#856404":"#721c24"},children:F.status})]}),t.jsxs("div",{children:[t.jsx("strong",{children:"Relationship Type:"}),t.jsx("br",{}),F.relationship_type]}),t.jsxs("div",{children:[t.jsx("strong",{children:"Created:"}),t.jsx("br",{}),F.created_at?new Date(F.created_at).toLocaleDateString():"N/A"]})]}),F.notes&&t.jsxs("div",{style:{marginTop:"1rem"},children:[t.jsx("strong",{children:"Notes:"}),t.jsx("br",{}),t.jsx("div",{style:{padding:"0.75rem",backgroundColor:"#f8f9fa",borderRadius:"4px",marginTop:"0.5rem",fontStyle:"italic"},children:F.notes})]})]})}):t.jsx("div",{children:t.jsxs("div",{style:{marginBottom:"1.5rem"},children:[t.jsx("h3",{style:{color:"#5D8AA8",marginBottom:"1rem"},children:"Group Overview"}),t.jsxs("div",{style:{display:"grid",gridTemplateColumns:"1fr 1fr",gap:"1rem",marginBottom:"1rem"},children:[t.jsxs("div",{children:[t.jsx("strong",{children:"Group Name:"}),t.jsx("br",{}),F.name]}),t.jsxs("div",{children:[t.jsx("strong",{children:"Group Type:"}),t.jsx("br",{}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.875rem",fontWeight:"600",backgroundColor:F.group_type==="SECURITY"?"#d4edda":"#fff3cd",color:F.group_type==="SECURITY"?"#155724":"#856404"},children:F.group_type})]}),t.jsxs("div",{children:[t.jsx("strong",{children:"Visibility:"}),t.jsx("br",{}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.875rem",fontWeight:"600",backgroundColor:F.is_public?"#d4edda":"#fff3cd",color:F.is_public?"#155724":"#856404"},children:F.is_public?"Public":"Private"})]}),t.jsxs("div",{children:[t.jsx("strong",{children:"Member Count:"}),t.jsx("br",{}),F.member_count||0]}),t.jsxs("div",{children:[t.jsx("strong",{children:"Requires Approval:"}),t.jsx("br",{}),F.requires_approval?"Yes":"No"]}),t.jsxs("div",{children:[t.jsx("strong",{children:"Created:"}),t.jsx("br",{}),F.created_at?new Date(F.created_at).toLocaleDateString():"N/A"]})]}),t.jsxs("div",{style:{marginTop:"1rem"},children:[t.jsx("strong",{children:"Description:"}),t.jsx("br",{}),t.jsx("div",{style:{padding:"0.75rem",backgroundColor:"#f8f9fa",borderRadius:"4px",marginTop:"0.5rem"},children:F.description||"No description provided"})]})]})}),t.jsx("div",{style:{display:"flex",justifyContent:"flex-end",marginTop:"2rem",paddingTop:"1rem",borderTop:"1px solid #e9ecef"},children:t.jsx("button",{onClick:()=>H(!1),style:{padding:"0.5rem 1rem",backgroundColor:"#6c757d",color:"white",border:"none",borderRadius:"6px",cursor:"pointer"},children:"Close"})})]})})]}):null}const m2=({active:n,api:s,showPage:l,user:o})=>{const[d,f]=N.useState([]),[m,p]=N.useState([]),[g,h]=N.useState([]),[x,v]=N.useState(!0),[b,_]=N.useState(null),[C,E]=N.useState(!1),[A,L]=N.useState(null),[q,P]=N.useState("overview"),M=N.useRef(null),X=N.useRef(null),Q=N.useRef(null),K=N.useRef(null);N.useEffect(()=>{n&&o&&localStorage.getItem("crisp_auth_token")&&se()},[n,o]),N.useEffect(()=>{d.length>0&&!x&&ge()},[d,m,q,x]);const se=async()=>{try{v(!0),_(null);const[S,H,F]=await Promise.all([s.get("/api/organizations/"),s.get("/api/trust/bilateral/"),s.get("/api/trust/community/")]);S&&S.results&&S.results.organizations?f(S.results.organizations):S&&Array.isArray(S)?f(S):S&&S.data&&Array.isArray(S.data)?f(S.data):(f([]),console.log("Organizations API response:",S)),H&&H.results&&H.results.trusts?p(H.results.trusts):(p([]),console.error("Could not fetch trust relationships",H)),F&&F.results?h(F.results.community_trusts||[]):(h([]),console.error("Could not fetch trust groups",F)),(!S||!S.results||!S.results.organizations||S.results.organizations.length===0)&&_("No organizations found. The dashboard requires at least one organization.")}catch(S){_(S.message),console.error("Error fetching dashboard data:",S)}finally{v(!1)}},Ae=S=>({government:"fas fa-landmark",private:"fas fa-building",nonprofit:"fas fa-heart",academic:"fas fa-graduation-cap",healthcare:"fas fa-hospital",financial:"fas fa-university"})[S==null?void 0:S.toLowerCase()]||"fas fa-building",we=S=>({government:"#28a745",private:"#0056b3",nonprofit:"#dc3545",academic:"#6f42c1",healthcare:"#20c997",financial:"#fd7e14"})[S==null?void 0:S.toLowerCase()]||"#6c757d",ge=()=>{q==="overview"?(Ne(),me()):q==="network"?xe():q==="activity"&&He()},Ne=()=>{const S=oa(M.current);if(S.selectAll("*").remove(),!d.length)return;const H={top:20,right:20,bottom:40,left:40},F=400-H.left-H.right,_e=300-H.bottom-H.top,G=S.append("svg").attr("width",F+H.left+H.right).attr("height",_e+H.top+H.bottom).append("g").attr("transform",`translate(${H.left},${H.top})`),ie={};d.forEach(ue=>{const je=ue.organization_type||ue.type||"private";ie[je]=(ie[je]||0)+1});const oe=Object.entries(ie).map(([ue,je])=>({type:ue,count:je})),re=tf().domain(oe.map(ue=>ue.type)).range([0,F]).padding(.1),Te=ll().domain([0,Uo(oe,ue=>ue.count)]).range([_e,0]);G.selectAll(".bar").data(oe).enter().append("rect").attr("class","bar").attr("x",ue=>re(ue.type)).attr("width",re.bandwidth()).attr("y",_e).attr("height",0).attr("fill",ue=>we(ue.type)).transition().duration(800).attr("y",ue=>Te(ue.count)).attr("height",ue=>_e-Te(ue.count)),G.selectAll(".bar-label").data(oe).enter().append("text").attr("class","bar-label").attr("x",ue=>re(ue.type)+re.bandwidth()/2).attr("y",ue=>Te(ue.count)-5).attr("text-anchor","middle").style("font-size","12px").style("fill","#333").text(ue=>ue.count),G.append("g").attr("transform",`translate(0,${_e})`).call(tl(re)).selectAll("text").style("text-transform","capitalize"),G.append("g").call(al(Te))},me=()=>{const S=oa(K.current);if(S.selectAll("*").remove(),!m.length){S.append("div").style("text-align","center").style("color","#6c757d").style("padding","40px").text("No trust relationship data available");return}const H={top:20},F=300,_e=300,z=Math.min(F,_e)/2-H.top,ie=S.append("svg").attr("width",F).attr("height",_e).append("g").attr("transform",`translate(${F/2},${_e/2})`),oe={};m.forEach(ne=>{var I;const D=((I=ne.trust_level)==null?void 0:I.name)||"Unknown";oe[D]=(oe[D]||0)+1});const re=Object.entries(oe).map(([ne,D])=>({level:ne,count:D})),Te=Vo().domain(re.map(ne=>ne.level)).range(["#28a745","#fd7e14","#dc3545","#6f42c1"]),ue=LS().value(ne=>ne.count),je=DS().innerRadius(0).outerRadius(z),Le=ie.selectAll(".arc").data(ue(re)).enter().append("g").attr("class","arc");Le.append("path").attr("d",je).attr("fill",ne=>Te(ne.data.level)).transition().duration(800).attrTween("d",function(ne){const D=ac({startAngle:0,endAngle:0},ne);return function(I){return je(D(I))}}),Le.append("text").attr("transform",ne=>`translate(${je.centroid(ne)})`).attr("text-anchor","middle").style("font-size","12px").style("fill","white").text(ne=>ne.data.count)},xe=()=>{const S=oa(X.current);if(S.selectAll("*").remove(),!d.length||!m.length){S.append("div").style("text-align","center").style("color","#6c757d").style("padding","40px").text("No network data available");return}const H=800,F=600,_e=S.append("svg").attr("width",H).attr("height",F),z=d.slice(0,20).map(I=>({id:I.id,name:I.name,type:I.organization_type||I.type||"private",group:I.organization_type||I.type||"private"})),G=m.filter(I=>z.find(J=>{var be;return J.id===((be=I.source_organization)==null?void 0:be.id)})&&z.find(J=>{var be;return J.id===((be=I.target_organization)==null?void 0:be.id)})).map(I=>{var J;return{source:I.source_organization.id,target:I.target_organization.id,value:((J=I.trust_level)==null?void 0:J.numerical_value)||50}}),ie=BN(z).force("link",kN(G).id(I=>I.id).distance(100)).force("charge",qN().strength(-300)).force("center",fN(H/2,F/2)),oe=Vo().domain(["government","private","nonprofit","academic","healthcare","financial"]).range(["#28a745","#0056b3","#dc3545","#6f42c1","#20c997","#fd7e14"]),re=_e.append("g").selectAll("line").data(G).enter().append("line").attr("stroke","#999").attr("stroke-opacity",.6).attr("stroke-width",I=>Math.sqrt(I.value/10)),Te=_e.append("g").selectAll("circle").data(z).enter().append("circle").attr("r",8).attr("fill",I=>oe(I.group)).call(N1().on("start",Le).on("drag",ne).on("end",D)),ue=_e.append("g").selectAll("text").data(z).enter().append("text").text(I=>I.name.length>15?I.name.substring(0,15)+"...":I.name).style("font-size","10px").style("fill","#333").attr("dx",12).attr("dy",4);ie.nodes(z).on("tick",je),ie.force("link").links(G);function je(){re.attr("x1",I=>I.source.x).attr("y1",I=>I.source.y).attr("x2",I=>I.target.x).attr("y2",I=>I.target.y),Te.attr("cx",I=>I.x).attr("cy",I=>I.y),ue.attr("x",I=>I.x).attr("y",I=>I.y)}function Le(I,J){I.active||ie.alphaTarget(.3).restart(),J.fx=J.x,J.fy=J.y}function ne(I,J){J.fx=I.x,J.fy=I.y}function D(I,J){I.active||ie.alphaTarget(0),J.fx=null,J.fy=null}},He=()=>{const S=oa(Q.current);if(S.selectAll("*").remove(),!d.length)return;const H={top:20,right:30,bottom:40,left:50},F=800-H.left-H.right,_e=300-H.top-H.bottom,G=S.append("svg").attr("width",F+H.left+H.right).attr("height",_e+H.top+H.bottom).append("g").attr("transform",`translate(${H.left},${H.top})`),ie=new Date,oe=[];for(let je=29;je>=0;je--){const Le=new Date(ie);Le.setDate(Le.getDate()-je);const ne=Math.floor(Math.random()*10)+1;oe.push({date:Le,count:ne})}const re=e0().domain(fx(oe,je=>je.date)).range([0,F]),Te=ll().domain([0,Uo(oe,je=>je.count)]).range([_e,0]),ue=lc().x(je=>re(je.date)).y(je=>Te(je.count)).curve(r0);G.append("path").datum(oe).attr("fill","none").attr("stroke","#0056b3").attr("stroke-width",2).attr("d",ue),G.selectAll(".dot").data(oe).enter().append("circle").attr("class","dot").attr("cx",je=>re(je.date)).attr("cy",je=>Te(je.count)).attr("r",3).attr("fill","#0056b3"),G.append("g").attr("transform",`translate(0,${_e})`).call(tl(re).tickFormat(ol("%m/%d"))),G.append("g").call(al(Te))};return n?x?t.jsx("div",{className:"institutions-page",children:t.jsxs("div",{className:"loading-state",children:[t.jsx("i",{className:"fas fa-spinner fa-spin"}),t.jsx("p",{children:"Loading organizations dashboard..."})]})}):b?t.jsx("div",{className:"institutions-page",children:t.jsxs("div",{className:"error-state",children:[t.jsx("i",{className:"fas fa-exclamation-triangle"}),t.jsxs("p",{children:["Error loading organizations: ",b]}),t.jsx("button",{onClick:se,className:"btn btn-primary",children:"Retry"})]})}):t.jsxs("section",{id:"organizations",className:`page-section ${n?"active":""}`,children:[t.jsxs("div",{className:"page-header",children:[t.jsxs("div",{children:[t.jsx("h1",{className:"page-title",children:"Organizations"}),t.jsx("p",{className:"page-subtitle",children:"Manage connected organizations and trust relationships"})]}),t.jsxs("div",{className:"action-buttons",children:[t.jsxs("button",{className:"btn btn-outline",onClick:()=>P("organizations"),children:[t.jsx("i",{className:"fas fa-building"})," All Organizations"]}),t.jsxs("button",{className:"btn btn-outline",onClick:()=>P("trust-relationships"),children:[t.jsx("i",{className:"fas fa-handshake"})," Trust Relationships"]}),t.jsxs("button",{className:"btn btn-outline",onClick:()=>P("trust-groups"),children:[t.jsx("i",{className:"fas fa-users"})," Trust Groups"]}),t.jsxs("button",{className:"btn btn-primary",onClick:()=>E(!0),children:[t.jsx("i",{className:"fas fa-plus"})," Add Organization"]})]})]}),t.jsxs("div",{className:"stats-grid",children:[t.jsxs("div",{className:"stat-card",children:[t.jsxs("div",{className:"stat-title",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-building"})}),t.jsx("span",{children:"Total Organizations"})]}),t.jsx("div",{className:"stat-value",children:d.length}),t.jsxs("div",{className:"stat-change neutral",children:[t.jsx("span",{children:t.jsx("i",{className:"fas fa-circle"})}),t.jsx("span",{children:"All registered"})]})]}),t.jsxs("div",{className:"stat-card",children:[t.jsxs("div",{className:"stat-title",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-users"})}),t.jsx("span",{children:"Total Members"})]}),t.jsx("div",{className:"stat-value",children:d.reduce((S,H)=>S+(H.member_count||0),0)}),t.jsxs("div",{className:"stat-change increase",children:[t.jsx("span",{children:t.jsx("i",{className:"fas fa-arrow-up"})}),t.jsx("span",{children:"Across all orgs"})]})]}),t.jsxs("div",{className:"stat-card",children:[t.jsxs("div",{className:"stat-title",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-handshake"})}),t.jsx("span",{children:"Trust Relationships"})]}),t.jsx("div",{className:"stat-value",children:m.length}),t.jsxs("div",{className:"stat-change neutral",children:[t.jsx("span",{children:t.jsx("i",{className:"fas fa-link"})}),t.jsx("span",{children:"Active connections"})]})]}),t.jsxs("div",{className:"stat-card",children:[t.jsxs("div",{className:"stat-title",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-shield-check"})}),t.jsx("span",{children:"Active Organizations"})]}),t.jsx("div",{className:"stat-value",children:d.filter(S=>S.is_active!==!1).length}),t.jsxs("div",{className:"stat-change increase",children:[t.jsx("span",{children:t.jsx("i",{className:"fas fa-check"})}),t.jsx("span",{children:"Online now"})]})]})]}),q==="overview"&&t.jsxs(t.Fragment,{children:[t.jsxs("div",{style:{display:"grid",gridTemplateColumns:"2fr 1fr",gap:"2rem",marginBottom:"2rem"},children:[t.jsxs("div",{style:{background:"white",borderRadius:"8px",padding:"1.5rem",boxShadow:"0 2px 4px rgba(0,0,0,0.1)",border:"1px solid #e5e7eb"},children:[t.jsxs("div",{style:{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:"1.5rem"},children:[t.jsx("h3",{style:{margin:0,fontSize:"1.125rem",fontWeight:"600",color:"#333"},children:"Recent Organizations"}),t.jsxs("button",{className:"btn btn-sm btn-outline",onClick:()=>P("organizations"),children:[t.jsx("i",{className:"fas fa-arrow-right"})," View All (",d.length,")"]})]}),t.jsx("div",{className:"table-responsive",children:t.jsxs("table",{className:"data-table",children:[t.jsx("thead",{children:t.jsxs("tr",{children:[t.jsx("th",{children:"Organization"}),t.jsx("th",{children:"Type"}),t.jsx("th",{children:"Members"}),t.jsx("th",{children:"Status"})]})}),t.jsx("tbody",{children:d.length===0?t.jsx("tr",{children:t.jsxs("td",{colSpan:"4",style:{textAlign:"center",padding:"2rem",color:"#666"},children:[t.jsx("i",{className:"fas fa-building",style:{fontSize:"2rem",marginBottom:"1rem",opacity:.3}}),t.jsx("div",{children:"No organizations found"})]})}):d.slice(0,5).map(S=>t.jsxs("tr",{children:[t.jsx("td",{children:t.jsxs("div",{style:{display:"flex",alignItems:"center",gap:"0.75rem"},children:[t.jsx("i",{className:Ae(S.organization_type||S.type),style:{color:we(S.organization_type||S.type),fontSize:"1.25rem"}}),t.jsxs("div",{children:[t.jsx("div",{style:{fontWeight:"600",color:"#333"},children:S.name}),S.description&&t.jsx("div",{style:{fontSize:"0.75rem",color:"#666",marginTop:"0.125rem"},children:S.description.length>40?S.description.substring(0,40)+"...":S.description})]})]})}),t.jsx("td",{children:t.jsx("span",{style:{backgroundColor:we(S.organization_type||S.type)+"20",color:we(S.organization_type||S.type),padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"capitalize"},children:S.organization_type||S.type||"Unknown"})}),t.jsx("td",{style:{color:"#333",fontWeight:"500"},children:S.member_count||0}),t.jsx("td",{children:t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",backgroundColor:S.is_active!==!1?"#e8f5e8":"#fff3e0",color:S.is_active!==!1?"#2e7d32":"#f57c00"},children:S.is_active!==!1?"Active":"Inactive"})})]},S.id))})]})})]}),t.jsxs("div",{style:{background:"white",borderRadius:"8px",padding:"1.5rem",boxShadow:"0 2px 4px rgba(0,0,0,0.1)",border:"1px solid #e5e7eb"},children:[t.jsxs("div",{style:{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:"1.5rem"},children:[t.jsx("h3",{style:{margin:0,fontSize:"1.125rem",fontWeight:"600",color:"#333"},children:"Trust Relationships"}),t.jsxs("button",{className:"btn btn-sm btn-outline",onClick:()=>P("trust-relationships"),children:[t.jsx("i",{className:"fas fa-arrow-right"})," View All (",m.length,")"]})]}),t.jsx("div",{style:{display:"flex",flexDirection:"column",gap:"1rem"},children:m.length===0?t.jsxs("div",{style:{textAlign:"center",padding:"2rem",color:"#666"},children:[t.jsx("i",{className:"fas fa-handshake",style:{fontSize:"2rem",marginBottom:"1rem",opacity:.3}}),t.jsx("div",{style:{fontSize:"0.875rem"},children:"No trust relationships"})]}):m.slice(0,4).map((S,H)=>{var F,_e;return t.jsxs("div",{style:{padding:"1rem",border:"1px solid #e5e7eb",borderRadius:"6px",background:"#f9fafb"},children:[t.jsxs("div",{style:{display:"flex",alignItems:"center",gap:"0.5rem",marginBottom:"0.5rem"},children:[t.jsx("i",{className:"fas fa-handshake",style:{color:"#667eea",fontSize:"1rem"}}),t.jsx("span",{style:{fontSize:"0.875rem",fontWeight:"600",color:"#333"},children:S.relationship_type||"Partnership"})]}),t.jsxs("div",{style:{fontSize:"0.75rem",color:"#666",lineHeight:1.4},children:[t.jsx("div",{children:t.jsx("strong",{children:((F=S.source_organization)==null?void 0:F.name)||"Organization A"})}),t.jsx("div",{style:{margin:"0.25rem 0",color:"#999"},children:"↔"}),t.jsx("div",{children:t.jsx("strong",{children:((_e=S.target_organization)==null?void 0:_e.name)||"Organization B"})})]}),t.jsx("div",{style:{marginTop:"0.5rem"},children:t.jsx("span",{style:{fontSize:"0.625rem",padding:"0.125rem 0.375rem",borderRadius:"3px",backgroundColor:S.status==="active"?"#dcfce7":"#fef3c7",color:S.status==="active"?"#166534":"#92400e",textTransform:"uppercase",fontWeight:"600"},children:S.status||"pending"})})]},H)})})]})]}),t.jsxs("div",{style:{background:"white",borderRadius:"8px",padding:"1.5rem",boxShadow:"0 2px 4px rgba(0,0,0,0.1)",border:"1px solid #e5e7eb",marginBottom:"2rem"},children:[t.jsxs("div",{style:{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:"1.5rem"},children:[t.jsx("h3",{style:{margin:0,fontSize:"1.125rem",fontWeight:"600",color:"#333"},children:"Trust Groups"}),t.jsxs("button",{className:"btn btn-sm btn-outline",onClick:()=>P("trust-groups"),children:[t.jsx("i",{className:"fas fa-arrow-right"})," View All (",g.length,")"]})]}),t.jsx("div",{style:{display:"grid",gridTemplateColumns:"repeat(auto-fit, minmax(280px, 1fr))",gap:"1rem"},children:g.length===0?t.jsxs("div",{style:{gridColumn:"1 / -1",textAlign:"center",padding:"3rem",color:"#666"},children:[t.jsx("i",{className:"fas fa-users",style:{fontSize:"3rem",marginBottom:"1rem",opacity:.3}}),t.jsx("div",{children:"No trust groups found"})]}):g.slice(0,3).map((S,H)=>t.jsxs("div",{style:{padding:"1.5rem",border:"1px solid #e5e7eb",borderRadius:"8px",background:"#f9fafb"},children:[t.jsxs("div",{style:{display:"flex",alignItems:"center",gap:"0.75rem",marginBottom:"1rem"},children:[t.jsx("i",{className:"fas fa-users",style:{color:"#667eea",fontSize:"1.25rem"}}),t.jsx("h4",{style:{margin:0,fontSize:"1rem",fontWeight:"600",color:"#333"},children:S.name})]}),S.description&&t.jsx("p",{style:{fontSize:"0.875rem",color:"#666",margin:"0 0 1rem 0",lineHeight:1.4},children:S.description.length>100?S.description.substring(0,100)+"...":S.description}),t.jsxs("div",{style:{display:"flex",justifyContent:"space-between",alignItems:"center"},children:[t.jsxs("span",{style:{fontSize:"0.75rem",color:"#666"},children:[S.member_count||0," members"]}),t.jsx("span",{style:{fontSize:"0.625rem",padding:"0.125rem 0.375rem",borderRadius:"3px",backgroundColor:S.is_active?"#dcfce7":"#fee2e2",color:S.is_active?"#166534":"#dc2626",textTransform:"uppercase",fontWeight:"600"},children:S.is_active?"Active":"Inactive"})]})]},H))})]})]}),q==="organizations"&&t.jsxs("div",{style:{background:"white",borderRadius:"8px",padding:"1.5rem",boxShadow:"0 2px 4px rgba(0,0,0,0.1)",border:"1px solid #e5e7eb"},children:[t.jsxs("div",{style:{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:"1.5rem"},children:[t.jsxs("h3",{style:{margin:0,fontSize:"1.125rem",fontWeight:"600",color:"#333"},children:["All Organizations (",d.length,")"]}),t.jsxs("button",{className:"btn btn-sm btn-outline",onClick:()=>P("overview"),children:[t.jsx("i",{className:"fas fa-arrow-left"})," Back to Overview"]})]}),t.jsx("div",{className:"table-responsive",children:t.jsxs("table",{className:"data-table",children:[t.jsx("thead",{children:t.jsxs("tr",{children:[t.jsx("th",{children:"Organization"}),t.jsx("th",{children:"Type"}),t.jsx("th",{children:"Members"}),t.jsx("th",{children:"Trust Relationships"}),t.jsx("th",{children:"Status"}),t.jsx("th",{children:"Created"}),t.jsx("th",{children:"Actions"})]})}),t.jsx("tbody",{children:d.length===0?t.jsx("tr",{children:t.jsxs("td",{colSpan:"7",style:{textAlign:"center",padding:"2rem",color:"#666"},children:[t.jsx("i",{className:"fas fa-building",style:{fontSize:"2rem",marginBottom:"1rem",opacity:.3}}),t.jsx("div",{children:"No organizations found"})]})}):d.map(S=>t.jsxs("tr",{children:[t.jsx("td",{children:t.jsxs("div",{style:{display:"flex",alignItems:"center",gap:"0.75rem"},children:[t.jsx("i",{className:Ae(S.organization_type||S.type),style:{color:we(S.organization_type||S.type),fontSize:"1.25rem"}}),t.jsxs("div",{children:[t.jsx("div",{style:{fontWeight:"600",color:"#333"},children:S.name}),S.description&&t.jsx("div",{style:{fontSize:"0.75rem",color:"#666",marginTop:"0.125rem"},children:S.description.length>50?S.description.substring(0,50)+"...":S.description})]})]})}),t.jsx("td",{children:t.jsx("span",{style:{backgroundColor:we(S.organization_type||S.type)+"20",color:we(S.organization_type||S.type),padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"capitalize"},children:S.organization_type||S.type||"Unknown"})}),t.jsx("td",{style:{color:"#333",fontWeight:"500"},children:S.member_count||0}),t.jsx("td",{style:{color:"#333",fontWeight:"500"},children:S.trust_relationships_count||0}),t.jsx("td",{children:t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",backgroundColor:S.is_active!==!1?"#e8f5e8":"#fff3e0",color:S.is_active!==!1?"#2e7d32":"#f57c00"},children:S.is_active!==!1?"Active":"Inactive"})}),t.jsx("td",{style:{color:"#666",fontSize:"0.875rem"},children:S.created_at?new Date(S.created_at).toLocaleDateString():"Unknown"}),t.jsx("td",{children:t.jsxs("div",{style:{display:"flex",gap:"0.5rem"},children:[t.jsx("button",{className:"btn btn-sm btn-outline",onClick:()=>L(S),style:{padding:"0.25rem 0.5rem",fontSize:"0.75rem"},children:t.jsx("i",{className:"fas fa-eye"})}),t.jsx("button",{className:"btn btn-sm btn-outline",style:{padding:"0.25rem 0.5rem",fontSize:"0.75rem"},children:t.jsx("i",{className:"fas fa-edit"})})]})})]},S.id))})]})})]}),q==="trust-relationships"&&t.jsxs("div",{style:{background:"white",borderRadius:"8px",padding:"1.5rem",boxShadow:"0 2px 4px rgba(0,0,0,0.1)",border:"1px solid #e5e7eb"},children:[t.jsxs("div",{style:{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:"1.5rem"},children:[t.jsxs("h3",{style:{margin:0,fontSize:"1.125rem",fontWeight:"600",color:"#333"},children:["All Trust Relationships (",m.length,")"]}),t.jsxs("button",{className:"btn btn-sm btn-outline",onClick:()=>P("overview"),children:[t.jsx("i",{className:"fas fa-arrow-left"})," Back to Overview"]})]}),t.jsx("div",{style:{display:"grid",gridTemplateColumns:"repeat(auto-fit, minmax(400px, 1fr))",gap:"1rem"},children:m.length===0?t.jsxs("div",{style:{gridColumn:"1 / -1",textAlign:"center",padding:"3rem",color:"#666"},children:[t.jsx("i",{className:"fas fa-handshake",style:{fontSize:"3rem",marginBottom:"1rem",opacity:.3}}),t.jsx("div",{children:"No trust relationships found"})]}):m.map((S,H)=>{var F,_e;return t.jsxs("div",{style:{padding:"1.5rem",border:"1px solid #e5e7eb",borderRadius:"8px",background:"#f9fafb"},children:[t.jsxs("div",{style:{display:"flex",alignItems:"center",gap:"0.75rem",marginBottom:"1rem"},children:[t.jsx("i",{className:"fas fa-handshake",style:{color:"#667eea",fontSize:"1.25rem"}}),t.jsx("h4",{style:{margin:0,fontSize:"1rem",fontWeight:"600",color:"#333"},children:S.relationship_type||"Partnership"}),t.jsx("span",{style:{fontSize:"0.625rem",padding:"0.25rem 0.5rem",borderRadius:"4px",backgroundColor:S.status==="active"?"#dcfce7":"#fef3c7",color:S.status==="active"?"#166534":"#92400e",textTransform:"uppercase",fontWeight:"600",marginLeft:"auto"},children:S.status||"pending"})]}),t.jsxs("div",{style:{fontSize:"0.875rem",color:"#666",lineHeight:1.5},children:[t.jsxs("div",{style:{marginBottom:"0.5rem"},children:[t.jsx("strong",{children:"From:"})," ",((F=S.source_organization)==null?void 0:F.name)||"Organization A"]}),t.jsxs("div",{style:{marginBottom:"0.5rem"},children:[t.jsx("strong",{children:"To:"})," ",((_e=S.target_organization)==null?void 0:_e.name)||"Organization B"]}),S.trust_level&&t.jsxs("div",{style:{marginBottom:"0.5rem"},children:[t.jsx("strong",{children:"Trust Level:"})," ",S.trust_level.name||S.trust_level]}),S.notes&&t.jsxs("div",{style:{marginTop:"0.75rem",fontSize:"0.75rem",fontStyle:"italic"},children:['"',S.notes,'"']})]})]},H)})})]}),q==="trust-groups"&&t.jsxs("div",{style:{background:"white",borderRadius:"8px",padding:"1.5rem",boxShadow:"0 2px 4px rgba(0,0,0,0.1)",border:"1px solid #e5e7eb"},children:[t.jsxs("div",{style:{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:"1.5rem"},children:[t.jsxs("h3",{style:{margin:0,fontSize:"1.125rem",fontWeight:"600",color:"#333"},children:["All Trust Groups (",g.length,")"]}),t.jsxs("button",{className:"btn btn-sm btn-outline",onClick:()=>P("overview"),children:[t.jsx("i",{className:"fas fa-arrow-left"})," Back to Overview"]})]}),t.jsx("div",{style:{display:"grid",gridTemplateColumns:"repeat(auto-fit, minmax(350px, 1fr))",gap:"1.5rem"},children:g.length===0?t.jsxs("div",{style:{gridColumn:"1 / -1",textAlign:"center",padding:"3rem",color:"#666"},children:[t.jsx("i",{className:"fas fa-users",style:{fontSize:"3rem",marginBottom:"1rem",opacity:.3}}),t.jsx("div",{children:"No trust groups found"})]}):g.map((S,H)=>t.jsxs("div",{style:{padding:"1.5rem",border:"1px solid #e5e7eb",borderRadius:"8px",background:"#f9fafb"},children:[t.jsxs("div",{style:{display:"flex",alignItems:"center",gap:"0.75rem",marginBottom:"1rem"},children:[t.jsx("i",{className:"fas fa-users",style:{color:"#667eea",fontSize:"1.25rem"}}),t.jsx("h4",{style:{margin:0,fontSize:"1.125rem",fontWeight:"600",color:"#333"},children:S.name}),t.jsx("span",{style:{fontSize:"0.625rem",padding:"0.25rem 0.5rem",borderRadius:"4px",backgroundColor:S.is_active?"#dcfce7":"#fee2e2",color:S.is_active?"#166534":"#dc2626",textTransform:"uppercase",fontWeight:"600",marginLeft:"auto"},children:S.is_active?"Active":"Inactive"})]}),S.description&&t.jsx("p",{style:{fontSize:"0.875rem",color:"#666",margin:"0 0 1rem 0",lineHeight:1.5},children:S.description}),t.jsxs("div",{style:{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:"1rem"},children:[t.jsxs("span",{style:{fontSize:"0.875rem",color:"#666"},children:[t.jsx("strong",{children:S.member_count||0})," members"]}),S.group_type&&t.jsx("span",{style:{fontSize:"0.75rem",color:"#667eea",backgroundColor:"#667eea20",padding:"0.25rem 0.5rem",borderRadius:"4px",textTransform:"capitalize"},children:S.group_type})]}),S.default_trust_level&&t.jsxs("div",{style:{fontSize:"0.75rem",color:"#666",marginBottom:"0.5rem"},children:[t.jsx("strong",{children:"Default Trust:"})," ",S.default_trust_level.name||S.default_trust_level]}),t.jsxs("div",{style:{display:"flex",gap:"0.5rem",marginTop:"1rem"},children:[t.jsxs("button",{className:"btn btn-sm btn-outline",style:{flex:1},children:[t.jsx("i",{className:"fas fa-eye"})," View Details"]}),t.jsxs("button",{className:"btn btn-sm btn-outline",style:{flex:1},children:[t.jsx("i",{className:"fas fa-edit"})," Edit"]})]})]},H))})]}),C&&t.jsx("div",{className:"modal-overlay",children:t.jsxs("div",{className:"modal",children:[t.jsxs("div",{className:"modal-header",children:[t.jsx("h3",{children:"Create New Institution"}),t.jsx("button",{className:"close-btn",onClick:()=>E(!1),children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsxs("div",{className:"modal-body",children:[t.jsx("p",{children:"Institution creation form will be implemented here."}),t.jsx("p",{children:"This requires backend integration for organization management."})]}),t.jsx("div",{className:"modal-footer",children:t.jsx("button",{className:"btn btn-secondary",onClick:()=>E(!1),children:"Cancel"})})]})}),A&&t.jsx("div",{className:"modal-overlay",children:t.jsxs("div",{className:"modal large",children:[t.jsxs("div",{className:"modal-header",children:[t.jsx("h3",{children:A.name}),t.jsx("button",{className:"close-btn",onClick:()=>L(null),children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsx("div",{className:"modal-body",children:t.jsxs("div",{className:"org-detail-grid",children:[t.jsxs("div",{className:"detail-section",children:[t.jsx("h4",{children:"Basic Information"}),t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Name:"}),t.jsx("span",{children:A.name})]}),t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Type:"}),t.jsx("span",{children:A.type||"Not specified"})]}),t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Description:"}),t.jsx("span",{children:A.description||"No description provided"})]})]}),t.jsxs("div",{className:"detail-section",children:[t.jsx("h4",{children:"Statistics"}),t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Members:"}),t.jsx("span",{children:A.member_count||0})]}),t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Trust Relationships:"}),t.jsx("span",{children:A.trust_relationships_count||0})]}),t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Status:"}),t.jsx("span",{className:`status-badge ${A.is_active?"active":"inactive"}`,children:A.is_active?"Active":"Inactive"})]})]})]})}),t.jsx("div",{className:"modal-footer",children:t.jsx("button",{className:"btn btn-secondary",onClick:()=>L(null),children:"Close"})})]})})]}):null};class p2 extends Fs.Component{constructor(s){super(s),this.state={hasError:!1,error:null}}static getDerivedStateFromError(s){return{hasError:!0,error:s}}componentDidCatch(s,l){console.error("Chart Error:",s,l)}render(){return this.state.hasError?t.jsxs("div",{style:{padding:"20px",textAlign:"center",background:"#fff5f5",border:"1px solid #fed7d7",borderRadius:"4px",color:"#c53030"},children:[t.jsx("i",{className:"fas fa-exclamation-triangle",style:{fontSize:"24px",marginBottom:"10px"}}),t.jsx("h3",{children:"Chart Error"}),t.jsx("p",{children:"Something went wrong with the chart visualization."}),t.jsx("button",{onClick:()=>this.setState({hasError:!1,error:null}),style:{background:"#0056b3",color:"white",border:"none",padding:"8px 16px",borderRadius:"4px",cursor:"pointer"},children:"Try Again"})]}):this.props.children}}const Ao="http://localhost:8000",Zg=new Map,g2=300*1e3,zo=()=>{const n=localStorage.getItem("crisp_auth_token"),s={"Content-Type":"application/json"};return n?s.Authorization=`Bearer ${n}`:console.warn("No authentication token found in localStorage"),s},ut={get:async n=>{try{const s=n,l=Zg.get(s);if(l&&Date.now()-l.timestamp<g2)return l.data;const o=zo();if(!localStorage.getItem("crisp_auth_token")&&!n.includes("/auth/"))return null;const f=await fetch(`${Ao}${n}`,{headers:o});if(!f.ok)throw f.status===401&&(localStorage.removeItem("crisp_auth_token"),localStorage.removeItem("crisp_user"),window.location.href="/static/react/login"),new Error(`HTTP ${f.status}`);const m=await f.json();return(n.includes("/api/threat-feeds/")||n.includes("/api/system-health/")||n.includes("/api/organizations/"))&&Zg.set(s,{data:m,timestamp:Date.now()}),m}catch(s){return s.message.includes("401")||console.error(`API Error: ${n}`,s),null}},post:async(n,s)=>{try{const l=await fetch(`${Ao}${n}`,{method:"POST",headers:zo(),body:JSON.stringify(s)});if(!l.ok)throw new Error(`HTTP ${l.status}`);return await l.json()}catch(l){return console.error(`API Error: ${n}`,l),null}},put:async(n,s)=>{try{const l=await fetch(`${Ao}${n}`,{method:"PUT",headers:zo(),body:JSON.stringify(s)});if(!l.ok)throw new Error(`HTTP ${l.status}`);return await l.json()}catch(l){return console.error(`API Error: ${n}`,l),null}},delete:async n=>{try{const s=await fetch(`${Ao}${n}`,{method:"DELETE",headers:zo()});if(!s.ok)throw new Error(`HTTP ${s.status}`);if(s.status===204)return{success:!0};const l=await s.text();return l?JSON.parse(l):{success:!0}}catch(s){return console.error(`API Error: ${n}`,s),null}}};function x2({user:n,onLogout:s,isAdmin:l}){console.log("App component - onLogout:",s,typeof s);const[o,d]=N.useState("dashboard"),[f,m]=N.useState(!0),[p,g]=N.useState({triggerModal:null,modalParams:{}});N.useEffect(()=>{const v=setTimeout(()=>{m(!1)},500);return()=>clearTimeout(v)},[]);const h=(v,b=null,_={})=>{if(d(v),g({triggerModal:b,modalParams:_}),b){const C=new URL(window.location);C.searchParams.set("modal",b),Object.keys(_).length>0&&C.searchParams.set("params",JSON.stringify(_)),window.history.pushState({},"",C)}else{const C=new URL(window.location);C.searchParams.delete("modal"),C.searchParams.delete("params"),window.history.pushState({},"",C)}},x=()=>{h("user-management","addUser")};return N.useEffect(()=>{const v=()=>{const b=new URLSearchParams(window.location.search),_=b.get("modal"),C=b.get("params");g(_?{triggerModal:_,modalParams:C?JSON.parse(C):{}}:{triggerModal:null,modalParams:{}})};return window.addEventListener("popstate",v),v(),()=>window.removeEventListener("popstate",v)},[]),f?t.jsxs("div",{style:{display:"flex",justifyContent:"center",alignItems:"center",height:"100vh",flexDirection:"column",gap:"20px",fontFamily:"Segoe UI, Tahoma, Geneva, Verdana, sans-serif",backgroundColor:"#0a0b0d",color:"#ffffff"},children:[t.jsx("div",{style:{width:"40px",height:"40px",border:"4px solid #333",borderTop:"4px solid #0056b3",borderRadius:"50%",animation:"spin 1s linear infinite"}}),t.jsx("p",{style:{color:"#718096",fontSize:"16px"},children:"Loading CRISP System..."}),t.jsx("style",{children:`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `})]}):t.jsxs("div",{className:"App",children:[t.jsx(y2,{showPage:h,user:n,onLogout:s,isAdmin:l,navigateToRegisterUser:x}),t.jsx(v2,{activePage:o,showPage:h,user:n,onLogout:s,isAdmin:l}),t.jsx("main",{className:"main-content",children:t.jsxs("div",{className:"container",children:[t.jsx(b2,{active:o==="dashboard",showPage:h,user:n}),t.jsx(j2,{active:o==="threat-feeds",navigationState:p,setNavigationState:g}),t.jsx(w2,{active:o==="ioc-management"}),t.jsx(N2,{active:o==="ttp-analysis"}),t.jsx(m2,{active:o==="institutions",api:ut,showPage:h,user:n}),t.jsx(_2,{active:o==="reports"}),t.jsx(T2,{active:o==="notifications"}),t.jsx(BS,{active:o==="profile"}),t.jsx(u2,{active:o==="user-management"}),t.jsx(f2,{active:o==="organisation-management"}),t.jsx(h2,{active:o==="trust-management"})]})})]})}function y2({showPage:n,user:s,onLogout:l,isAdmin:o,navigateToRegisterUser:d}){console.log("Header component - onLogout:",l,typeof l);const[f,m]=N.useState(!1),[p,g]=N.useState(!1),h=s&&s.username?s.username.charAt(0).toUpperCase():"A",x=s&&s.username?s.username.split("@")[0]:"Admin",v=(s==null?void 0:s.role)||"Security Analyst",b=_=>{_.preventDefault(),_.stopPropagation(),m(!f)};return N.useEffect(()=>{const _=C=>{C.target.closest(".user-profile-container")||(m(!1),g(!1))};return document.addEventListener("mousedown",_),()=>document.removeEventListener("mousedown",_)},[]),N.useEffect(()=>{f||g(!1)},[f]),t.jsx("header",{children:t.jsxs("div",{className:"container header-container",children:[t.jsxs("a",{href:"#",className:"logo",children:[t.jsx("div",{className:"logo-icon",children:t.jsx("i",{className:"fas fa-shield-alt"})}),t.jsx("div",{className:"logo-text",children:"CRISP"})]}),t.jsxs("div",{className:"nav-actions",children:[t.jsxs("div",{className:"search-bar",children:[t.jsx("span",{className:"search-icon",children:t.jsx("i",{className:"fas fa-search"})}),t.jsx("input",{type:"text",placeholder:"Search platform..."})]}),t.jsxs("div",{className:"notifications",onClick:()=>n("notifications"),style:{cursor:"pointer"},children:[t.jsx("i",{className:"fas fa-bell"}),t.jsx("span",{className:"notification-count",children:"3"})]}),t.jsxs("div",{className:"user-profile-container",children:[t.jsxs("button",{className:"user-profile",onClick:b,type:"button",children:[t.jsx("div",{className:"avatar",children:h}),t.jsxs("div",{className:"user-info",children:[t.jsx("div",{className:"user-name",children:x}),t.jsx("div",{className:"user-role",children:v})]}),t.jsx("i",{className:"fas fa-chevron-down"})]}),f&&t.jsxs("div",{className:"user-menu-dropdown",children:[t.jsxs("div",{className:"dropdown-header",children:[t.jsx("div",{className:"user-avatar-large",children:h}),t.jsxs("div",{children:[t.jsx("div",{className:"user-name-large",children:x}),t.jsx("div",{className:"user-email",children:(s==null?void 0:s.username)||"admin@example.com"})]})]}),t.jsx("div",{className:"menu-divider"}),t.jsxs("div",{className:"menu-items",children:[t.jsxs("button",{className:"menu-item",onClick:()=>{m(!1),n("profile")},type:"button",children:[t.jsx("i",{className:"fas fa-user"}),t.jsx("span",{children:"My Profile"})]}),t.jsxs("button",{className:"menu-item",onClick:()=>{m(!1),n("account-settings")},type:"button",children:[t.jsx("i",{className:"fas fa-cog"}),t.jsx("span",{children:"Account Settings"})]}),t.jsx("div",{className:"menu-divider"}),t.jsxs("div",{className:"menu-item-submenu",children:[t.jsxs("button",{className:"menu-item",onClick:()=>g(!p),type:"button",children:[t.jsx("i",{className:"fas fa-users"}),t.jsx("span",{children:"Management"}),t.jsx("i",{className:`fas fa-chevron-${p?"up":"down"} submenu-arrow`})]}),p&&t.jsxs("div",{className:"submenu",children:[t.jsxs("button",{className:"submenu-item",onClick:()=>{m(!1),g(!1),n("user-management")},type:"button",children:[t.jsx("i",{className:"fas fa-users"}),t.jsx("span",{children:"User Management"})]}),t.jsxs("button",{className:"submenu-item",onClick:()=>{m(!1),g(!1),n("organisation-management")},type:"button",children:[t.jsx("i",{className:"fas fa-university"}),t.jsx("span",{children:"Organisation Management"})]}),t.jsxs("button",{className:"submenu-item",onClick:()=>{m(!1),g(!1),n("trust-management")},type:"button",children:[t.jsx("i",{className:"fas fa-handshake"}),t.jsx("span",{children:"Trust Management"})]})]})]}),v==="BlueVisionAdmin"&&t.jsxs("button",{className:"menu-item",onClick:()=>{m(!1),n("admin-settings")},type:"button",children:[t.jsx("i",{className:"fas fa-shield-alt"}),t.jsx("span",{children:"Admin Settings"})]}),v==="BlueVisionAdmin"&&d&&t.jsxs("button",{className:"menu-item",onClick:()=>{m(!1),d()},type:"button",children:[t.jsx("i",{className:"fas fa-user-plus"}),t.jsx("span",{children:"Register New User"})]})]}),t.jsx("div",{className:"menu-divider"}),t.jsxs("button",{className:"menu-item logout-item",onClick:()=>{m(!1),console.log("Logout button clicked - onLogout:",l,typeof l),typeof l=="function"?l():(console.error("onLogout is not a function:",l),alert("Logout function not available. Please refresh the page."))},type:"button",children:[t.jsx("i",{className:"fas fa-sign-out-alt"}),t.jsx("span",{children:"Logout"})]})]})]})]})]})})}function v2({activePage:n,showPage:s,user:l,onLogout:o,isAdmin:d}){const[f,m]=N.useState("loading"),[p,g]=N.useState(!1),[h,x]=N.useState(!1);return N.useEffect(()=>{const v=async()=>{const _=await ut.get("/api/threat-feeds/");m(_?"active":"offline")};v();const b=setInterval(v,3e4);return()=>clearInterval(b)},[]),t.jsx("nav",{className:"main-nav",children:t.jsxs("div",{className:"container nav-container",children:[t.jsxs("ul",{className:"nav-links",children:[t.jsx("li",{children:t.jsxs("a",{onClick:()=>s("dashboard"),className:n==="dashboard"?"active":"",children:[t.jsx("i",{className:"fas fa-chart-line"})," Dashboard"]})}),t.jsx("li",{children:t.jsxs("a",{onClick:()=>s("threat-feeds"),className:n==="threat-feeds"?"active":"",children:[t.jsx("i",{className:"fas fa-rss"})," Threat Feeds"]})}),t.jsx("li",{children:t.jsxs("a",{onClick:()=>s("ioc-management"),className:n==="ioc-management"?"active":"",children:[t.jsx("i",{className:"fas fa-search"})," IoC Management"]})}),t.jsx("li",{children:t.jsxs("a",{onClick:()=>s("ttp-analysis"),className:n==="ttp-analysis"?"active":"",children:[t.jsx("i",{className:"fas fa-sitemap"})," TTP Analysis"]})}),t.jsx("li",{children:t.jsxs("a",{onClick:()=>s("institutions"),className:n==="institutions"?"active":"",children:[t.jsx("i",{className:"fas fa-building"})," Organisations"]})}),t.jsx("li",{children:t.jsxs("a",{onClick:()=>s("reports"),className:n==="reports"?"active":"",children:[t.jsx("i",{className:"fas fa-file-alt"})," Reports"]})})]}),t.jsxs("div",{className:"nav-right",children:[t.jsxs("div",{className:"status-indicator",children:[t.jsx("span",{className:"status-dot",style:{backgroundColor:f==="active"?"#28a745":f==="loading"?"#ffc107":"#dc3545"}}),t.jsx("span",{children:f==="active"?"System Online":f==="loading"?"Checking...":"System Offline"})]}),l&&t.jsxs("div",{className:"user-profile-container",children:[t.jsxs("button",{className:"user-profile",onClick:()=>g(!p),children:[t.jsx("div",{className:"avatar",children:(l.first_name||l.username||"U").charAt(0).toUpperCase()}),t.jsxs("div",{className:"user-info",children:[t.jsx("div",{className:"user-name",children:l.first_name&&l.last_name?`${l.first_name} ${l.last_name}`:l.username}),t.jsx("div",{className:"user-role",children:l.role})]}),t.jsx("i",{className:"fas fa-chevron-down"})]}),p&&t.jsxs("div",{className:"user-menu-dropdown",children:[t.jsxs("div",{className:"dropdown-header",children:[t.jsx("div",{className:"user-avatar-large",children:(l.first_name||l.username||"U").charAt(0).toUpperCase()}),t.jsxs("div",{children:[t.jsx("div",{className:"user-name-large",children:l.first_name&&l.last_name?`${l.first_name} ${l.last_name}`:l.username}),t.jsx("div",{className:"user-email",children:l.email||l.username})]})]}),t.jsx("div",{className:"menu-divider"}),t.jsxs("div",{className:"menu-items",children:[t.jsxs("button",{className:"menu-item",onClick:()=>{s("profile"),g(!1)},children:[t.jsx("i",{className:"fas fa-user"}),t.jsx("span",{children:"My Profile"})]}),t.jsxs("div",{className:"menu-item-submenu",children:[t.jsxs("button",{className:"menu-item",onClick:()=>x(!h),children:[t.jsx("i",{className:"fas fa-users"}),t.jsx("span",{children:"Management"}),t.jsx("i",{className:`fas fa-chevron-${h?"up":"down"} submenu-arrow`})]}),h&&t.jsxs("div",{className:"submenu",children:[t.jsxs("button",{className:"submenu-item",onClick:()=>{s("user-management"),g(!1),x(!1)},children:[t.jsx("i",{className:"fas fa-users"}),t.jsx("span",{children:"User Management"})]}),t.jsxs("button",{className:"submenu-item",onClick:()=>{s("institutions"),g(!1),x(!1)},children:[t.jsx("i",{className:"fas fa-university"}),t.jsx("span",{children:"Organisation Management"})]}),t.jsxs("button",{className:"submenu-item",onClick:()=>{s("trust-management"),g(!1),x(!1)},children:[t.jsx("i",{className:"fas fa-handshake"}),t.jsx("span",{children:"Trust Management"})]})]})]}),d&&t.jsxs("button",{className:"menu-item",onClick:()=>{s("notifications"),g(!1)},children:[t.jsx("i",{className:"fas fa-shield-alt"}),t.jsx("span",{children:"Admin Settings"})]})]}),t.jsx("div",{className:"menu-divider"}),t.jsxs("button",{className:"menu-item logout-item",onClick:()=>{o(),g(!1)},children:[t.jsx("i",{className:"fas fa-sign-out-alt"}),t.jsx("span",{children:"Logout"})]})]})]})]})]})})}function b2({active:n,showPage:s,user:l}){var Zt,ae,De,Fe,ke,Be,vt,ft,V,Re,U,fe,ee,Ce,Xe,et,ve,Ot,St,Ee;if(!n)return null;const[o,d]=N.useState({threat_feeds:0,indicators:0,ttps:0,status:"loading"}),[f,m]=N.useState([]),[p,g]=N.useState(!1),[h,x]=N.useState(null),v=N.useRef(null),b=N.useRef(null),_=N.useRef(null),[C,E]=N.useState([]),[A,L]=N.useState(!1),[q,P]=N.useState(null),[M,X]=N.useState({days:30,type:null,feed_id:null}),[Q,K]=N.useState({total_indicators:0,avg_daily:0,type_distribution:[]}),[se,Ae]=N.useState({status:"unknown",database:{status:"unknown"},services:{redis:{status:"unknown"}},system:{cpu_percent:0,memory_percent:0,disk_percent:0},feeds:{total:0,active:0,external:0,feeds:[]},errors:[],timestamp:null}),[we,ge]=N.useState(!1),[Ne,me]=N.useState(null),[xe,He]=N.useState([]),[S,H]=N.useState(!1),[F,_e]=N.useState(null),[z,G]=N.useState(!1),[ie,oe]=N.useState("json"),[re,Te]=N.useState(!1);N.useEffect(()=>{if(n){const R=localStorage.getItem("crisp_auth_token"),ce=localStorage.getItem("crisp_user");R&&ce&&(ue().catch(Ie=>console.error("Dashboard data error:",Ie)),je().catch(Ie=>console.error("Recent IoCs error:",Ie)),Le().catch(Ie=>console.error("Chart data error:",Ie)),ne().catch(Ie=>console.error("System health error:",Ie)),I().catch(Ie=>console.error("Recent activities error:",Ie)))}},[n]),N.useEffect(()=>{n&&localStorage.getItem("crisp_auth_token")&&Le()},[M,n]),N.useEffect(()=>{if(!n||!localStorage.getItem("crisp_auth_token"))return;const ce=setInterval(()=>{localStorage.getItem("crisp_auth_token")&&ne()},300*1e3);return()=>clearInterval(ce)},[n]);const ue=async()=>{const R=await ut.get("/api/threat-feeds/");if(R){let ce=0,Ie=0;const rt=(R.results||[]).slice(0,3);for(const wt of rt){const ht=await ut.get(`/api/threat-feeds/${wt.id}/status/`);ht&&(ce+=ht.indicator_count||0,Ie+=ht.ttp_count||0)}d({threat_feeds:R.count||0,indicators:ce,ttps:Ie,status:"active"})}};async function je(){g(!0),x(null);try{const R=await ut.get("/api/indicators/");if(R&&R.results){const ce=R.results.slice(0,6).map(Ie=>D(Ie));m(ce)}else m([])}catch(R){console.error("Error fetching recent IoCs:",R),x("Failed to load recent threat intelligence"),m([])}finally{g(!1)}}async function Le(){L(!0),P(null);try{const R=new URLSearchParams({days:M.days.toString()});M.type&&R.append("type",M.type),M.feed_id&&R.append("feed_id",M.feed_id);const ce=await ut.get(`/api/threat-activity-chart/?${R}`);if(ce&&ce.success)E(ce.data),K(ce.summary),v.current&&at(ce.data,ce.summary);else throw new Error("Failed to fetch chart data")}catch(R){console.error("Error fetching chart data:",R),P("Failed to load chart data"),E([])}finally{L(!1)}}async function ne(){ge(!0),me(null);try{const R=await ut.get("/api/system-health/");if(R)Ae({status:R.status||"unknown",database:R.database||{status:"unknown"},services:R.services||{redis:{status:"unknown"}},system:R.system||{cpu_percent:0,memory_percent:0,disk_percent:0},feeds:R.feeds||{total:0,active:0,external:0,feeds:[]},errors:R.errors||[],timestamp:R.timestamp||new Date().toISOString()});else throw new Error("Failed to fetch system health data")}catch(R){console.error("Error fetching system health:",R),me("Failed to load system health data"),Ae(ce=>({...ce,status:"error",timestamp:new Date().toISOString()}))}finally{ge(!1)}}const D=R=>{var Bt;const ce={ip:"IP Address",domain:"Domain",url:"URL",file_hash:"File Hash",email:"Email Address",user_agent:"User Agent"},Ie=mt=>mt>=80?{level:"high",label:"High"}:mt>=50?{level:"medium",label:"Medium"}:{level:"low",label:"Low"},rt=(mt,Oe)=>Oe==="file_hash"&&mt.length>16?mt.substring(0,16)+"...":mt.length>30?mt.substring(0,30)+"...":mt,wt=Ie(R.confidence||50),ht={ip:"fa-network-wired",domain:"fa-globe",url:"fa-link",file_hash:"fa-file-signature",email:"fa-envelope",user_agent:"fa-browser"},Ct=mt=>{const Oe=new Date(mt),Ut=Math.abs(new Date-Oe),qt=Math.ceil(Ut/(1e3*60*60*24));return qt===1?"1 day ago":qt<7?`${qt} days ago`:qt<30?`${Math.ceil(qt/7)} weeks ago`:`${Math.ceil(qt/30)} months ago`};return{id:R.id,displayType:ce[R.type]||R.type.charAt(0).toUpperCase()+R.type.slice(1),typeIcon:ht[R.type]||"fa-question-circle",rawType:R.type,title:R.name||"",value:R.value,truncatedValue:rt(R.value,R.type),source:((Bt=R.threat_feed)==null?void 0:Bt.name)||R.source||"Internal",severity:wt.label,severityClass:wt.level,confidence:R.confidence||50,status:R.is_active!==!1?"active":"inactive",isAnonymized:R.is_anonymized||!1,age:Ct(R.created_at||new Date().toISOString()),created_at:R.created_at||new Date().toISOString()}};async function I(){H(!0),_e(null);try{const R=await ut.get("/api/recent-activities/?limit=10");R&&R.success?He(R.activities||[]):_e("Failed to load recent activities")}catch(R){console.error("Error fetching recent activities:",R),_e("Failed to load recent activities")}finally{H(!1)}}const J=R=>{switch(R==null?void 0:R.toLowerCase()){case"healthy":case"connected":case"active":case"success":return"#28a745";case"warning":case"stale":return"#ffc107";case"error":case"disconnected":case"failed":case"inactive":return"#dc3545";default:return"#6c757d"}},be=R=>{switch(R==null?void 0:R.toLowerCase()){case"healthy":case"connected":case"active":case"success":return"fas fa-check-circle";case"warning":case"stale":return"fas fa-exclamation-triangle";case"error":case"disconnected":case"failed":case"inactive":return"fas fa-times-circle";default:return"fas fa-question-circle"}},Me=R=>{if(!R)return"Unknown";const ce=new Date(R),rt=new Date-ce,wt=Math.floor(rt/6e4),ht=Math.floor(rt/36e5),Ct=Math.floor(rt/864e5);return wt<1?"Just now":wt<60?`${wt}m ago`:ht<24?`${ht}h ago`:Ct<7?`${Ct}d ago`:ce.toLocaleDateString()},Ve=R=>{if(!R)return"Unknown";const ce=Math.floor(R/3600),Ie=Math.floor(R%3600/60);if(ce>24){const rt=Math.floor(ce/24),wt=ce%24;return`${rt}d ${wt}h`}return`${ce}h ${Ie}m`};N.useEffect(()=>(n&&v.current&&C.length>0&&at(C,Q),()=>{_.current&&_.current()}),[n,C,Q]),N.useEffect(()=>{if(!n)return;const R=setInterval(()=>{console.log("Auto-refreshing chart data..."),Le()},300*1e3);return()=>clearInterval(R)},[n,M]),N.useEffect(()=>{const R=()=>{n&&v.current&&C.length>0&&(clearTimeout(window.chartResizeTimeout),window.chartResizeTimeout=setTimeout(()=>{at(C,Q)},300))};return window.addEventListener("resize",R),()=>{window.removeEventListener("resize",R),clearTimeout(window.chartResizeTimeout)}},[n,C,Q]),N.useEffect(()=>()=>{_.current&&_.current(),p1(".chart-tooltip").remove(),clearTimeout(window.chartResizeTimeout)},[]);const at=(R=[],ce={})=>{if(_.current&&_.current(),v.current&&oa(v.current).selectAll("*").remove(),!v.current||!R||R.length===0){v.current&&oa(v.current).append("svg").attr("width","100%").attr("height",300).attr("viewBox",`0 0 ${v.current.clientWidth||400} 300`).append("text").attr("x","50%").attr("y","50%").attr("text-anchor","middle").attr("dominant-baseline","middle").style("font-size","14px").style("fill","#666").text(A?"Loading chart data...":"No data available");return}try{const Ie=v.current.clientWidth||400,rt=Math.max(Ie,400),wt=350,ht={top:40,right:60,bottom:60,left:70},Ct=rt-ht.left-ht.right,Bt=wt-ht.top-ht.bottom,mt=oa(v.current).append("svg").attr("width","100%").attr("height",wt).attr("viewBox",`0 0 ${rt} ${wt}`).style("max-width","100%").style("height","auto"),Oe=mt.append("g").attr("transform",`translate(${ht.left},${ht.top})`),lt=Wx("%Y-%m-%d"),Ut=R.map(tt=>({date:lt(tt.date),count:tt.count,types:tt.types||{},originalDate:tt.date})).filter(tt=>tt.date&&!isNaN(tt.count));if(Ut.length===0){mt.append("text").attr("x","50%").attr("y","50%").attr("text-anchor","middle").attr("dominant-baseline","middle").style("font-size","14px").style("fill","#666").text("No valid data to display");return}const qt=e0().domain(fx(Ut,tt=>tt.date)).range([0,Ct]),Ia=Uo(Ut,tt=>tt.count)||1,en=ll().domain([0,Ia*1.1]).range([Bt,0]).nice();let Ht=b.current;Ht||(Ht=oa("body").append("div").attr("class","chart-tooltip").style("opacity",0).style("position","absolute").style("background","rgba(0, 0, 0, 0.9)").style("color","white").style("padding","12px").style("border-radius","6px").style("font-size","13px").style("pointer-events","none").style("z-index","1000").style("box-shadow","0 4px 12px rgba(0, 0, 0, 0.3)"),b.current=Ht);const fn=mt.append("defs"),$a=`areaGradient-${Date.now()}`,Da=fn.append("linearGradient").attr("id",$a).attr("x1","0%").attr("y1","0%").attr("x2","0%").attr("y2","100%");Da.append("stop").attr("offset","0%").attr("stop-color","#0056b3").attr("stop-opacity",.8),Da.append("stop").attr("offset","100%").attr("stop-color","#00a0e9").attr("stop-opacity",.1),Oe.append("g").attr("class","grid").attr("transform",`translate(0,${Bt})`).call(tl(qt).ticks(Math.min(7,Ut.length)).tickSize(-Bt).tickFormat("")).style("stroke-dasharray","3,3").style("opacity",.3),Oe.append("g").attr("class","grid").call(al(en).ticks(6).tickSize(-Ct).tickFormat("")).style("stroke-dasharray","3,3").style("opacity",.3);const tn=RS().x(tt=>qt(tt.date)).y0(Bt).y1(tt=>en(tt.count)).curve($g);Oe.append("path").datum(Ut).attr("fill",`url(#${$a})`).attr("d",tn);const sa=lc().x(tt=>qt(tt.date)).y(tt=>en(tt.count)).curve($g);Oe.append("path").datum(Ut).attr("fill","none").attr("stroke","#0056b3").attr("stroke-width",3).attr("d",sa),Oe.selectAll(".dot").data(Ut).enter().append("circle").attr("class","dot").attr("cx",tt=>qt(tt.date)).attr("cy",tt=>en(tt.count)).attr("r",4).attr("fill","#0056b3").attr("stroke","white").attr("stroke-width",2).style("cursor","pointer").on("mouseover",function(tt,Fa){oa(this).transition().duration(200).attr("r",6).attr("fill","#ff6b35");const Ya=ol("%B %d, %Y"),Ga=Object.entries(Fa.types).map(([da,ni])=>`${da}: ${ni}`).join("<br>");Ht&&(Ht.transition().duration(200).style("opacity",.9),Ht.html(`
              <strong>${Ya(Fa.date)}</strong><br/>
              Total IoCs: <strong>${Fa.count}</strong><br/>
              ${Ga?`<br/><em>Breakdown:</em><br/>${Ga}`:""}
            `).style("left",tt.pageX+10+"px").style("top",tt.pageY-28+"px"))}).on("mouseout",function(tt,Fa){oa(this).transition().duration(200).attr("r",4).attr("fill","#0056b3"),Ht&&Ht.transition().duration(500).style("opacity",0)});const Aa=ol("%m/%d");Oe.append("g").attr("transform",`translate(0,${Bt})`).call(tl(qt).ticks(Math.min(7,Ut.length)).tickFormat(Aa)).selectAll("text").style("text-anchor","end").attr("dx","-.8em").attr("dy",".15em").attr("transform","rotate(-45)"),Oe.append("g").call(al(en).ticks(6)).append("text").attr("transform","rotate(-90)").attr("y",6).attr("dy","0.71em").attr("text-anchor","end").style("fill","#666").text("IoC Count"),Oe.append("text").attr("x",Ct/2).attr("y",-15).attr("text-anchor","middle").style("font-size","18px").style("font-weight","600").style("fill","#2d3748").text("Threat Activity Trends");const gt=`Total: ${ce.total_indicators||0} IoCs | Daily Avg: ${ce.avg_daily||0}`;Oe.append("text").attr("x",Ct/2).attr("y",Bt+50).attr("text-anchor","middle").style("font-size","12px").style("fill","#666").text(gt),_.current=()=>{b.current&&(b.current.remove(),b.current=null),v.current&&oa(v.current).selectAll("*").remove()}}catch(Ie){console.error("Error creating chart:",Ie),P("Failed to create chart visualization")}};function Ke(){G(!1),oe("json")}async function ta(){Te(!0);try{let R,ce,Ie;const rt={export_date:new Date().toISOString(),dashboard_stats:o,recent_iocs:f,system_health:se,chart_data:C,chart_summary:Q,chart_filters:M};switch(ie){case"csv":R=_t(rt),ce=`dashboard_export_${new Date().toISOString().split("T")[0]}.csv`,Ie="text/csv";break;case"json":R=Tt(rt),ce=`dashboard_export_${new Date().toISOString().split("T")[0]}.json`,Ie="application/json";break;case"summary":R=Ft(rt),ce=`dashboard_summary_${new Date().toISOString().split("T")[0]}.txt`,Ie="text/plain";break;default:throw new Error("Unsupported export format")}const wt=new Blob([R],{type:Ie}),ht=window.URL.createObjectURL(wt),Ct=document.createElement("a");Ct.href=ht,Ct.download=ce,document.body.appendChild(Ct),Ct.click(),document.body.removeChild(Ct),window.URL.revokeObjectURL(ht),Ke(),console.log(`Successfully exported dashboard data as ${ie.toUpperCase()}`)}catch(R){console.error("Dashboard export failed:",R),alert("Export failed. Please try again.")}finally{Te(!1)}}function _t(R){var Ie,rt,wt,ht,Ct,Bt,mt,Oe,lt;let ce="";return ce+=`CRISP Dashboard Export
`,ce+=`Export Date: ${new Date(R.export_date).toLocaleString()}

`,ce+=`DASHBOARD STATISTICS
`,ce+=`Metric,Value
`,ce+=`Active IoCs,${R.dashboard_stats.indicators||0}
`,ce+=`TTPs,${R.dashboard_stats.ttps||0}
`,ce+=`Threat Feeds,${R.dashboard_stats.threat_feeds||0}
`,ce+=`Platform Status,${R.dashboard_stats.status||"Unknown"}

`,R.recent_iocs&&R.recent_iocs.length>0&&(ce+=`RECENT INDICATORS OF COMPROMISE
`,ce+=`Type,Indicator,Source,Severity,Status,Created
`,R.recent_iocs.forEach(Ut=>{const qt=[Ut.displayType||"",`"${(Ut.value||"").replace(/"/g,'""')}"`,Ut.source||"",Ut.severity||"","Active",Ut.created_at||""].join(",");ce+=qt+`
`}),ce+=`
`),R.system_health&&(ce+=`SYSTEM HEALTH
`,ce+=`Component,Status,Details
`,ce+=`Overall Status,${R.system_health.status||"Unknown"},
`,ce+=`Database,${((Ie=R.system_health.database)==null?void 0:Ie.status)||"Unknown"},${((rt=R.system_health.database)==null?void 0:rt.details)||""}
`,ce+=`Redis,${((ht=(wt=R.system_health.services)==null?void 0:wt.redis)==null?void 0:ht.status)||"Unknown"},${((Bt=(Ct=R.system_health.services)==null?void 0:Ct.redis)==null?void 0:Bt.details)||""}
`,R.system_health.system&&(ce+=`CPU Usage,${((mt=R.system_health.system.cpu_percent)==null?void 0:mt.toFixed(1))||"N/A"}%,
`,ce+=`Memory Usage,${((Oe=R.system_health.system.memory_percent)==null?void 0:Oe.toFixed(1))||"N/A"}%,
`,ce+=`Disk Usage,${((lt=R.system_health.system.disk_percent)==null?void 0:lt.toFixed(1))||"N/A"}%,
`)),ce}function Tt(R){return JSON.stringify(R,null,2)}function Ft(R){var Ie,rt,wt,ht,Ct,Bt;let ce="";if(ce+=`CRISP THREAT INTELLIGENCE DASHBOARD SUMMARY
`,ce+="="+"=".repeat(48)+`

`,ce+=`Export Date: ${new Date(R.export_date).toLocaleString()}

`,ce+=`OVERVIEW
`,ce+="-".repeat(20)+`
`,ce+=`• Active IoCs: ${R.dashboard_stats.indicators||0}
`,ce+=`• TTPs: ${R.dashboard_stats.ttps||0}
`,ce+=`• Threat Feeds: ${R.dashboard_stats.threat_feeds||0}
`,ce+=`• Platform Status: ${R.dashboard_stats.status||"Unknown"}

`,R.recent_iocs&&R.recent_iocs.length>0){ce+=`RECENT THREAT INTELLIGENCE
`,ce+="-".repeat(30)+`
`,ce+=`Total Recent IoCs: ${R.recent_iocs.length}

`;const mt=R.recent_iocs.reduce((Oe,lt)=>(Oe[lt.displayType]=(Oe[lt.displayType]||0)+1,Oe),{});ce+=`Type Distribution:
`,Object.entries(mt).forEach(([Oe,lt])=>{ce+=`  • ${Oe}: ${lt}
`}),ce+=`
`}return R.system_health&&(ce+=`SYSTEM HEALTH
`,ce+="-".repeat(20)+`
`,ce+=`Overall Status: ${R.system_health.status||"Unknown"}
`,ce+=`Database: ${((Ie=R.system_health.database)==null?void 0:Ie.status)||"Unknown"}
`,ce+=`Redis: ${((wt=(rt=R.system_health.services)==null?void 0:rt.redis)==null?void 0:wt.status)||"Unknown"}
`,R.system_health.system&&(ce+=`CPU Usage: ${((ht=R.system_health.system.cpu_percent)==null?void 0:ht.toFixed(1))||"N/A"}%
`,ce+=`Memory Usage: ${((Ct=R.system_health.system.memory_percent)==null?void 0:Ct.toFixed(1))||"N/A"}%
`,ce+=`Disk Usage: ${((Bt=R.system_health.system.disk_percent)==null?void 0:Bt.toFixed(1))||"N/A"}%
`),ce+=`
`),R.chart_summary&&R.chart_summary.total_indicators>0&&(ce+=`THREAT ACTIVITY TRENDS
`,ce+="-".repeat(25)+`
`,ce+=`Total Indicators (${R.chart_filters.days} days): ${R.chart_summary.total_indicators}
`,ce+=`Daily Average: ${R.chart_summary.avg_daily}
`,ce+=`Date Range: ${R.chart_summary.start_date} to ${R.chart_summary.end_date}

`),ce+=`Generated by CRISP Threat Intelligence Platform
`,ce}return t.jsxs("section",{id:"dashboard",className:`page-section ${n?"active":""}`,children:[t.jsxs("div",{className:"page-header",children:[t.jsxs("div",{children:[t.jsx("h1",{className:"page-title",children:"Threat Intelligence Dashboard"}),t.jsx("p",{className:"page-subtitle",children:"Overview of threat intelligence and platform activity"})]}),t.jsxs("div",{className:"action-buttons",children:[t.jsxs("button",{className:"btn btn-outline",onClick:()=>G(!0),children:[t.jsx("i",{className:"fas fa-download"})," Export Data"]}),t.jsxs("button",{className:"btn btn-primary",onClick:()=>s("threat-feeds","addFeed"),children:[t.jsx("i",{className:"fas fa-plus"})," Add New Feed"]})]})]}),t.jsxs("div",{className:"stats-grid",children:[t.jsxs("div",{className:"stat-card",children:[t.jsxs("div",{className:"stat-title",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-search"})}),t.jsx("span",{children:"Active IoCs"})]}),t.jsx("div",{className:"stat-value",children:o.indicators||0}),t.jsxs("div",{className:"stat-change increase",children:[t.jsx("span",{children:t.jsx("i",{className:"fas fa-arrow-up"})}),t.jsx("span",{children:"Live data"})]})]}),t.jsxs("div",{className:"stat-card",children:[t.jsxs("div",{className:"stat-title",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-sitemap"})}),t.jsx("span",{children:"TTPs"})]}),t.jsx("div",{className:"stat-value",children:o.ttps||0}),t.jsxs("div",{className:"stat-change increase",children:[t.jsx("span",{children:t.jsx("i",{className:"fas fa-arrow-up"})}),t.jsx("span",{children:"Live data"})]})]}),t.jsxs("div",{className:"stat-card",children:[t.jsxs("div",{className:"stat-title",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-rss"})}),t.jsx("span",{children:"Threat Feeds"})]}),t.jsx("div",{className:"stat-value",children:o.threat_feeds||0}),t.jsxs("div",{className:"stat-change increase",children:[t.jsx("span",{children:t.jsx("i",{className:"fas fa-arrow-up"})}),t.jsx("span",{children:"Live data"})]})]}),t.jsxs("div",{className:"stat-card",children:[t.jsxs("div",{className:"stat-title",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-server"})}),t.jsx("span",{children:"Platform Status"})]}),t.jsx("div",{className:"stat-value",children:o.status==="active"?"Online":"Offline"}),t.jsxs("div",{className:"stat-change",children:[t.jsx("span",{children:t.jsx("i",{className:"fas fa-circle",style:{color:o.status==="active"?"#28a745":"#dc3545"}})}),t.jsx("span",{children:"Live status"})]})]})]}),t.jsxs("div",{className:"main-grid",children:[t.jsxs("div",{children:[t.jsxs("div",{className:"card",children:[t.jsxs("div",{className:"card-header",children:[t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-shield-alt card-icon"})," Recent Threat Intelligence"]}),t.jsx("div",{className:"card-actions",children:t.jsxs("button",{className:"btn btn-outline btn-sm",onClick:je,disabled:p,children:[t.jsx("i",{className:`fas fa-sync-alt ${p?"fa-spin":""}`}),p?"Refreshing...":"Refresh"]})})]}),t.jsx("div",{className:"card-content",children:p?t.jsxs("div",{className:"loading-state",children:[t.jsx("div",{className:"loading-spinner"}),t.jsx("p",{children:"Loading recent threat intelligence..."})]}):h?t.jsxs("div",{className:"error-state",children:[t.jsx("i",{className:"fas fa-exclamation-triangle"}),t.jsx("p",{children:h}),t.jsxs("button",{className:"btn btn-primary btn-sm",onClick:je,children:[t.jsx("i",{className:"fas fa-retry"})," Retry"]})]}):f.length===0?t.jsxs("div",{className:"empty-state",children:[t.jsx("i",{className:"fas fa-shield-alt"}),t.jsx("p",{children:"No threat intelligence available"}),t.jsx("p",{className:"text-muted",children:"IoCs will appear here once feeds are consumed"})]}):t.jsxs("table",{className:"data-table",children:[t.jsx("thead",{children:t.jsxs("tr",{children:[t.jsx("th",{children:"Type"}),t.jsx("th",{children:"Indicator"}),t.jsx("th",{children:"Source"}),t.jsx("th",{children:"Severity"}),t.jsx("th",{children:"Status"})]})}),t.jsx("tbody",{children:f.map((R,ce)=>t.jsxs("tr",{children:[t.jsx("td",{children:t.jsxs("div",{className:"type-indicator",children:[t.jsx("i",{className:`fas ${R.typeIcon}`}),t.jsx("span",{children:R.displayType})]})}),t.jsx("td",{children:t.jsxs("div",{className:"indicator-value",children:[t.jsx("span",{className:"value",title:R.value,children:R.truncatedValue}),R.isAnonymized&&t.jsxs("span",{className:"badge badge-anonymized",children:[t.jsx("i",{className:"fas fa-mask"})," Anonymized"]})]})}),t.jsx("td",{children:t.jsxs("div",{className:"source-info",children:[t.jsx("span",{className:"source-name",children:R.source}),t.jsx("div",{className:"source-meta",children:t.jsx("span",{className:"age-indicator",title:`Created: ${R.created_at}`,children:R.age})})]})}),t.jsx("td",{children:t.jsx("span",{className:`badge badge-${R.severityClass}`,children:R.severity})}),t.jsx("td",{children:t.jsxs("div",{className:"badge-tags",children:[t.jsx("span",{className:"badge badge-active",children:"Active"}),R.confidence>=80&&t.jsxs("span",{className:"badge badge-verified",children:[t.jsx("i",{className:"fas fa-check-circle"})," High Confidence"]}),R.confidence<50&&t.jsxs("span",{className:"badge badge-warning",children:[t.jsx("i",{className:"fas fa-exclamation-triangle"})," Low Confidence"]}),t.jsxs("span",{className:"badge badge-realtime",title:"Real-time data",children:[t.jsx("i",{className:"fas fa-broadcast-tower"})," Live"]})]})})]},`${R.id||ce}`))})]})})]}),t.jsxs("div",{className:"card",children:[t.jsxs("div",{className:"card-header",children:[t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-chart-area card-icon"})," Threat Activity Trends"]}),t.jsxs("div",{className:"card-actions",children:[t.jsxs("select",{className:"btn btn-outline btn-sm",value:M.days,onChange:R=>X({...M,days:parseInt(R.target.value)}),style:{marginRight:"10px"},children:[t.jsx("option",{value:"7",children:"Last 7 Days"}),t.jsx("option",{value:"14",children:"Last 14 Days"}),t.jsx("option",{value:"30",children:"Last 30 Days"}),t.jsx("option",{value:"60",children:"Last 60 Days"}),t.jsx("option",{value:"90",children:"Last 90 Days"})]}),t.jsxs("select",{className:"btn btn-outline btn-sm",value:M.type||"",onChange:R=>X({...M,type:R.target.value||null}),style:{marginRight:"10px"},children:[t.jsx("option",{value:"",children:"All Types"}),t.jsx("option",{value:"ip",children:"IP Address"}),t.jsx("option",{value:"domain",children:"Domain"}),t.jsx("option",{value:"url",children:"URL"}),t.jsx("option",{value:"file_hash",children:"File Hash"}),t.jsx("option",{value:"email",children:"Email"})]}),t.jsxs("button",{className:"btn btn-outline btn-sm",onClick:Le,disabled:A,title:"Refresh chart data",children:[t.jsx("i",{className:`fas fa-sync-alt ${A?"fa-spin":""}`}),A?" Loading...":" Refresh"]})]})]}),Q.total_indicators>0&&t.jsxs("div",{className:"card-status-bar",style:{background:"#f8f9fa",padding:"8px 16px",fontSize:"12px",color:"#666",borderBottom:"1px solid #e9ecef"},children:[t.jsxs("span",{children:[t.jsx("strong",{children:"Total IoCs:"})," ",Q.total_indicators]}),t.jsx("span",{style:{margin:"0 15px"},children:"|"}),t.jsxs("span",{children:[t.jsx("strong",{children:"Daily Average:"})," ",Q.avg_daily]}),t.jsx("span",{style:{margin:"0 15px"},children:"|"}),t.jsxs("span",{children:[t.jsx("strong",{children:"Date Range:"})," ",Q.start_date," to ",Q.end_date]})]}),t.jsxs("div",{className:"card-content",children:[q&&t.jsxs("div",{className:"alert alert-error",style:{background:"#fff5f5",border:"1px solid #fed7d7",color:"#c53030",padding:"12px",borderRadius:"4px",marginBottom:"16px"},children:[t.jsx("i",{className:"fas fa-exclamation-triangle"})," ",q]}),t.jsx(p2,{children:t.jsxs("div",{style:{position:"relative",minHeight:"350px"},children:[A&&t.jsxs("div",{style:{position:"absolute",top:"50%",left:"50%",transform:"translate(-50%, -50%)",textAlign:"center",zIndex:10},children:[t.jsx("i",{className:"fas fa-spinner fa-spin",style:{fontSize:"24px",color:"#0056b3"}}),t.jsx("p",{style:{marginTop:"10px",color:"#666"},children:"Loading chart data..."})]}),t.jsx("div",{className:"chart-container",ref:v,style:{minHeight:"350px",width:"100%",overflow:"visible"}})]})})]})]})]}),t.jsxs("div",{className:"side-panels",children:[t.jsxs("div",{className:"card",children:[t.jsx("div",{className:"card-header",children:t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-building card-icon"})," Connected Organisations"]})}),t.jsx("div",{className:"card-content",children:t.jsxs("ul",{className:"organisation-list",children:[t.jsxs("li",{className:"organisation-item",children:[t.jsx("div",{className:"organisation-logo",children:"UP"}),t.jsxs("div",{className:"organisation-details",children:[t.jsx("div",{className:"organisation-name",children:"University of Pretoria"}),t.jsxs("div",{className:"organisation-stats",children:[t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-exchange-alt"})," 125 IoCs"]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-clock"})," 5m ago"]})]})]}),t.jsx("div",{className:"trust-level",children:t.jsx("div",{className:"trust-fill",style:{width:"90%"}})})]}),t.jsxs("li",{className:"organisation-item",children:[t.jsx("div",{className:"organisation-logo",children:"CS"}),t.jsxs("div",{className:"organisation-details",children:[t.jsx("div",{className:"organisation-name",children:"Cyber Security Hub"}),t.jsxs("div",{className:"organisation-stats",children:[t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-exchange-alt"})," 342 IoCs"]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-clock"})," 17m ago"]})]})]}),t.jsx("div",{className:"trust-level",children:t.jsx("div",{className:"trust-fill",style:{width:"85%"}})})]}),t.jsxs("li",{className:"organisation-item",children:[t.jsx("div",{className:"organisation-logo",children:"SR"}),t.jsxs("div",{className:"organisation-details",children:[t.jsx("div",{className:"organisation-name",children:"SANReN CSIRT"}),t.jsxs("div",{className:"organisation-stats",children:[t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-exchange-alt"})," 208 IoCs"]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-clock"})," 32m ago"]})]})]}),t.jsx("div",{className:"trust-level",children:t.jsx("div",{className:"trust-fill",style:{width:"75%"}})})]}),t.jsxs("li",{className:"organisation-item",children:[t.jsx("div",{className:"organisation-logo",children:"SB"}),t.jsxs("div",{className:"organisation-details",children:[t.jsx("div",{className:"organisation-name",children:"SABRIC"}),t.jsxs("div",{className:"organisation-stats",children:[t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-exchange-alt"})," 156 IoCs"]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-clock"})," 1h ago"]})]})]}),t.jsx("div",{className:"trust-level",children:t.jsx("div",{className:"trust-fill",style:{width:"70%"}})})]})]})})]}),t.jsxs("div",{className:"card",children:[t.jsx("div",{className:"card-header",children:t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-history card-icon"})," Recent Activity"]})}),t.jsx("div",{className:"card-content",children:S?t.jsxs("div",{className:"loading-state",children:[t.jsx("div",{className:"loading-spinner"}),t.jsx("p",{children:"Loading recent activities..."})]}):F?t.jsxs("div",{className:"error-state",children:[t.jsx("i",{className:"fas fa-exclamation-triangle"}),t.jsx("p",{children:F}),t.jsxs("button",{className:"btn btn-primary btn-sm",onClick:I,children:[t.jsx("i",{className:"fas fa-retry"})," Retry"]})]}):xe.length===0?t.jsxs("div",{className:"empty-state",children:[t.jsx("i",{className:"fas fa-history"}),t.jsx("p",{children:"No recent activities"}),t.jsx("p",{className:"text-muted",children:"System activities will appear here"})]}):t.jsx("ul",{className:"activity-stream",children:xe.map(R=>t.jsxs("li",{className:"activity-item",children:[t.jsx("div",{className:"activity-icon",children:t.jsx("i",{className:R.icon})}),t.jsxs("div",{className:"activity-details",children:[t.jsx("div",{className:"activity-text",children:R.title}),R.description&&t.jsx("div",{className:"activity-description",children:R.description}),t.jsxs("div",{className:"activity-meta",children:[t.jsx("div",{className:"activity-time",children:R.time_ago}),t.jsx("span",{className:`badge ${R.badge_type}`,children:R.badge_text})]})]})]},R.id))})})]})]})]}),t.jsxs("div",{className:"card",style:{marginTop:"24px"},children:[t.jsxs("div",{className:"card-header",children:[t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-heartbeat card-icon"})," System Health & Feed Status"]}),t.jsx("div",{className:"card-actions",children:t.jsxs("button",{className:"btn btn-outline btn-sm",onClick:ne,disabled:we,title:"Refresh system health",children:[t.jsx("i",{className:`fas fa-sync-alt ${we?"fa-spin":""}`}),we?" Loading...":" Refresh"]})})]}),t.jsxs("div",{className:"card-content",children:[Ne&&t.jsxs("div",{className:"alert alert-error",style:{background:"#fff5f5",border:"1px solid #fed7d7",color:"#c53030",padding:"12px",borderRadius:"4px",marginBottom:"16px"},children:[t.jsx("i",{className:"fas fa-exclamation-triangle"})," ",Ne]}),t.jsxs("div",{className:"system-status-overview",style:{display:"grid",gridTemplateColumns:"repeat(auto-fit, minmax(200px, 1fr))",gap:"16px",marginBottom:"24px"},children:[t.jsxs("div",{className:"status-card",style:{background:"#f8f9fa",border:"1px solid #dee2e6",borderRadius:"8px",padding:"16px",textAlign:"center"},children:[t.jsx("div",{style:{fontSize:"24px",color:J(se.status),marginBottom:"8px"},children:t.jsx("i",{className:be(se.status)})}),t.jsx("h3",{style:{margin:"0 0 4px 0",fontSize:"16px"},children:"Overall Status"}),t.jsx("p",{style:{margin:"0",color:J(se.status),fontWeight:"bold",textTransform:"capitalize"},children:se.status}),t.jsxs("small",{style:{color:"#666"},children:["Last Check: ",Me(se.timestamp)]})]}),t.jsxs("div",{className:"status-card",style:{background:"#f8f9fa",border:"1px solid #dee2e6",borderRadius:"8px",padding:"16px",textAlign:"center"},children:[t.jsx("div",{style:{fontSize:"24px",color:J(((Zt=se.database)==null?void 0:Zt.status)||"unknown"),marginBottom:"8px"},children:t.jsx("i",{className:"fas fa-database"})}),t.jsx("h3",{style:{margin:"0 0 4px 0",fontSize:"16px"},children:"Database"}),t.jsx("p",{style:{margin:"0",color:J(((ae=se.database)==null?void 0:ae.status)||"unknown"),fontWeight:"bold",textTransform:"capitalize"},children:((De=se.database)==null?void 0:De.status)||"Unknown"}),t.jsx("small",{style:{color:"#666"},children:(Fe=se.database)!=null&&Fe.connection_count?`${se.database.connection_count} connections`:"Connection info unavailable"})]}),t.jsxs("div",{className:"status-card",style:{background:"#f8f9fa",border:"1px solid #dee2e6",borderRadius:"8px",padding:"16px",textAlign:"center"},children:[t.jsx("div",{style:{fontSize:"24px",color:J(((Be=(ke=se.services)==null?void 0:ke.redis)==null?void 0:Be.status)||"unknown"),marginBottom:"8px"},children:t.jsx("i",{className:"fas fa-memory"})}),t.jsx("h3",{style:{margin:"0 0 4px 0",fontSize:"16px"},children:"Redis"}),t.jsx("p",{style:{margin:"0",color:J(((ft=(vt=se.services)==null?void 0:vt.redis)==null?void 0:ft.status)||"unknown"),fontWeight:"bold",textTransform:"capitalize"},children:((Re=(V=se.services)==null?void 0:V.redis)==null?void 0:Re.status)||"Unknown"}),t.jsx("small",{style:{color:"#666"},children:(fe=(U=se.services)==null?void 0:U.redis)!=null&&fe.info?`v${se.services.redis.info}`:"Version unavailable"})]}),t.jsxs("div",{className:"status-card",style:{background:"#f8f9fa",border:"1px solid #dee2e6",borderRadius:"8px",padding:"16px",textAlign:"center"},children:[t.jsx("div",{style:{fontSize:"24px",color:((ee=se.system)==null?void 0:ee.cpu_percent)>80?"#dc3545":((Ce=se.system)==null?void 0:Ce.cpu_percent)>60?"#ffc107":"#28a745",marginBottom:"8px"},children:t.jsx("i",{className:"fas fa-microchip"})}),t.jsx("h3",{style:{margin:"0 0 4px 0",fontSize:"16px"},children:"System Resources"}),t.jsxs("p",{style:{margin:"0",fontWeight:"bold"},children:["CPU: ",((et=(Xe=se.system)==null?void 0:Xe.cpu_percent)==null?void 0:et.toFixed(1))||"N/A","%"]}),t.jsxs("small",{style:{color:"#666"},children:["RAM: ",((Ot=(ve=se.system)==null?void 0:ve.memory_percent)==null?void 0:Ot.toFixed(1))||"N/A","% | Disk: ",((Ee=(St=se.system)==null?void 0:St.disk_percent)==null?void 0:Ee.toFixed(1))||"N/A","%"]})]})]}),t.jsxs("div",{className:"feed-status-section",children:[t.jsx("h3",{style:{margin:"0 0 16px 0",fontSize:"18px",borderBottom:"2px solid #dee2e6",paddingBottom:"8px"},children:"Feed Status Monitoring"}),se.feeds&&se.feeds.total>0&&t.jsxs("div",{className:"feed-summary",style:{display:"grid",gridTemplateColumns:"repeat(auto-fit, minmax(120px, 1fr))",gap:"12px",marginBottom:"20px",padding:"16px",background:"#f1f3f4",borderRadius:"6px"},children:[t.jsxs("div",{style:{textAlign:"center"},children:[t.jsx("div",{style:{fontSize:"24px",fontWeight:"bold",color:"#0056b3"},children:se.feeds.total}),t.jsx("small",{children:"Total Feeds"})]}),t.jsxs("div",{style:{textAlign:"center"},children:[t.jsx("div",{style:{fontSize:"24px",fontWeight:"bold",color:"#28a745"},children:se.feeds.active}),t.jsx("small",{children:"Active"})]}),t.jsxs("div",{style:{textAlign:"center"},children:[t.jsx("div",{style:{fontSize:"24px",fontWeight:"bold",color:"#17a2b8"},children:se.feeds.external}),t.jsx("small",{children:"External"})]}),t.jsxs("div",{style:{textAlign:"center"},children:[t.jsx("div",{style:{fontSize:"24px",fontWeight:"bold",color:"#6c757d"},children:se.feeds.total-se.feeds.external}),t.jsx("small",{children:"Internal"})]})]}),se.feeds&&se.feeds.total===0?t.jsxs("div",{style:{textAlign:"center",color:"#666",padding:"24px",background:"#f8f9fa",borderRadius:"6px",marginTop:"16px"},children:[t.jsx("i",{className:"fas fa-rss",style:{fontSize:"32px",marginBottom:"12px"}}),t.jsx("p",{style:{margin:"0 0 12px 0"},children:"No threat feeds configured yet."}),t.jsxs("button",{className:"btn btn-primary btn-sm",onClick:()=>s("threat-feeds"),children:[t.jsx("i",{className:"fas fa-plus"})," Manage Feeds"]})]}):t.jsx("div",{style:{textAlign:"center",padding:"16px",marginTop:"16px"},children:t.jsxs("button",{className:"btn btn-outline btn-sm",onClick:()=>s("threat-feeds"),children:[t.jsx("i",{className:"fas fa-cog"})," Manage All Feeds"]})})]}),se.errors&&se.errors.length>0&&t.jsxs("div",{className:"error-summary",style:{marginTop:"24px",padding:"16px",background:"#fff5f5",border:"1px solid #fed7d7",borderRadius:"6px"},children:[t.jsxs("h4",{style:{margin:"0 0 12px 0",color:"#c53030",fontSize:"16px"},children:[t.jsx("i",{className:"fas fa-exclamation-triangle"})," System Errors (",se.errors.length,")"]}),t.jsx("ul",{style:{margin:"0",paddingLeft:"20px"},children:se.errors.map((R,ce)=>t.jsx("li",{style:{color:"#c53030",marginBottom:"4px"},children:R},ce))})]}),se.system&&Object.keys(se.system).length>0&&t.jsxs("div",{className:"system-metrics",style:{marginTop:"24px",padding:"16px",background:"#f8f9fa",borderRadius:"6px"},children:[t.jsxs("h4",{style:{margin:"0 0 12px 0",fontSize:"16px"},children:[t.jsx("i",{className:"fas fa-chart-line"})," System Metrics"]}),t.jsxs("div",{style:{display:"grid",gridTemplateColumns:"repeat(auto-fit, minmax(200px, 1fr))",gap:"12px",fontSize:"14px"},children:[se.system.uptime&&t.jsxs("div",{children:[t.jsx("strong",{children:"Uptime:"})," ",Ve(se.system.uptime)]}),se.system.load_average&&t.jsxs("div",{children:[t.jsx("strong",{children:"Load Average:"})," ",se.system.load_average.join(", ")]}),t.jsxs("div",{children:[t.jsx("strong",{children:"Last Updated:"})," ",Me(se.system.last_check)]})]})]})]})]}),z&&t.jsx("div",{className:"modal-overlay",onClick:Ke,children:t.jsxs("div",{className:"modal-content",onClick:R=>R.stopPropagation(),children:[t.jsxs("div",{className:"modal-header",children:[t.jsxs("h2",{children:[t.jsx("i",{className:"fas fa-download"})," Export Dashboard Data"]}),t.jsx("button",{className:"modal-close",onClick:Ke,children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsxs("div",{className:"modal-body",children:[t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"Export Format"}),t.jsxs("select",{className:"form-control",value:ie,onChange:R=>oe(R.target.value),children:[t.jsx("option",{value:"json",children:"JSON - Complete Data"}),t.jsx("option",{value:"csv",children:"CSV - Tabular Format"}),t.jsx("option",{value:"summary",children:"Summary Report"})]})]}),t.jsx("div",{className:"export-info",children:t.jsx("div",{className:"export-preview",children:t.jsxs("div",{children:[t.jsx("strong",{children:"Export Details:"}),t.jsx("p",{children:"Dashboard export will include:"}),t.jsxs("ul",{children:[t.jsxs("li",{children:["System statistics (",o.indicators," IoCs, ",o.ttps," TTPs, ",o.threat_feeds," feeds)"]}),t.jsxs("li",{children:["Recent threat intelligence (",f.length," items)"]}),t.jsx("li",{children:"System health data"}),t.jsxs("li",{children:["Threat activity chart data (",C.length," data points)"]})]}),ie==="csv"&&t.jsx("p",{children:t.jsx("em",{children:"CSV format includes IoCs table and summary metrics."})}),ie==="json"&&t.jsx("p",{children:t.jsx("em",{children:"JSON format includes complete structured data export."})}),ie==="summary"&&t.jsx("p",{children:t.jsx("em",{children:"Summary report includes key insights and formatted overview."})})]})})})]}),t.jsx("div",{className:"modal-footer",children:t.jsxs("div",{className:"modal-actions",children:[t.jsx("button",{type:"button",className:"btn btn-outline",onClick:Ke,disabled:re,children:"Cancel"}),t.jsx("button",{type:"button",className:"btn btn-primary",onClick:ta,disabled:re,children:re?t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Exporting..."]}):t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-download"})," Export Dashboard"]})})]})})]})})]})}function j2({active:n,navigationState:s,setNavigationState:l}){if(!n)return null;const[o,d]=N.useState([]),[f,m]=N.useState(!1),[p,g]=N.useState(!1),[h,x]=N.useState(1),[v,b]=N.useState("all"),[_,C]=N.useState(!1),[E,A]=N.useState({type:"",status:"",source:"",search:""}),L=10,[q,P]=N.useState({name:"",description:"",is_external:!0,taxii_server_url:"",taxii_api_root:"",taxii_collection_id:"",taxii_username:"",taxii_password:""}),[M,X]=N.useState(new Set),[Q,K]=N.useState(new Map),[se,Ae]=N.useState(!1),[we,ge]=N.useState(null),[Ne,me]=N.useState(!1);N.useEffect(()=>{n&&xe()},[n]),N.useEffect(()=>{n&&(s==null?void 0:s.triggerModal)==="addFeed"&&(g(!0),l({triggerModal:null,modalParams:{}}))},[n,s,l]);const xe=async()=>{m(!0);const D=await ut.get("/api/threat-feeds/");D&&D.results&&d(D.results),m(!1)},He=async D=>{X(I=>new Set([...I,D])),K(I=>new Map(I.set(D,{stage:"Initiating",message:"Starting consumption process...",percentage:0})));try{const I=await ut.post(`/api/threat-feeds/${D}/consume/`);if(I){console.log("Feed consumption started:",I);const J=setInterval(async()=>{try{const be=await ut.get(`/api/threat-feeds/${D}/consumption_progress/`);if(be&&be.success){const Me=be.progress;K(Ve=>new Map(Ve.set(D,{stage:Me.stage,message:Me.message||`${Me.stage}...`,percentage:Me.percentage||0,current:Me.current,total:Me.total}))),(Me.stage==="Completed"||Me.percentage>=100)&&(clearInterval(J),setTimeout(()=>{X(Ve=>{const at=new Set(Ve);return at.delete(D),at}),K(Ve=>{const at=new Map(Ve);return at.delete(D),at})},2e3),await xe())}}catch(be){console.error("Error fetching progress:",be)}},2e3);setTimeout(()=>{clearInterval(J),X(be=>{const Me=new Set(be);return Me.delete(D),Me}),K(be=>{const Me=new Map(be);return Me.delete(D),Me})},3e5)}}catch(I){console.error("Error consuming feed:",I),alert("Failed to consume feed. Please try again."),X(J=>{const be=new Set(J);return be.delete(D),be}),K(J=>{const be=new Map(J);return be.delete(D),be})}},S=D=>{ge(D),Ae(!0)},H=async()=>{if(we){me(!0);try{await ut.delete(`/api/threat-feeds/${we.id}/`)!==null?(console.log("Feed deleted successfully:",we.name),await xe(),F()):alert("Failed to delete threat feed. Please try again.")}catch(D){console.error("Error deleting feed:",D),alert("Error deleting threat feed. Please try again.")}finally{me(!1)}}},F=()=>{Ae(!1),ge(null)},_e=()=>{g(!0)},z=D=>{const{name:I,value:J,type:be,checked:Me}=D.target;P(Ve=>({...Ve,[I]:be==="checkbox"?Me:J}))},G=async D=>{D.preventDefault(),await ut.post("/api/threat-feeds/",q)&&(g(!1),P({name:"",description:"",is_external:!0,taxii_server_url:"",taxii_api_root:"",taxii_collection_id:"",taxii_username:"",taxii_password:""}),xe())},ie=()=>{g(!1)},oe=()=>{let D=o;return v==="active"?D=D.filter(I=>I.is_active):v==="external"?D=D.filter(I=>I.is_external):v==="internal"&&(D=D.filter(I=>!I.is_external)),E.type&&(D=D.filter(I=>E.type==="stix-taxii"&&I.taxii_server_url||E.type==="internal"&&!I.is_external||E.type==="external"&&I.is_external)),E.status&&(D=D.filter(I=>E.status==="active"&&I.is_active||E.status==="disabled"&&!I.is_active)),E.source&&(D=D.filter(I=>E.source==="external"&&I.is_external||E.source==="internal"&&!I.is_external)),E.search&&(D=D.filter(I=>I.name.toLowerCase().includes(E.search.toLowerCase())||I.description&&I.description.toLowerCase().includes(E.search.toLowerCase())||I.taxii_server_url&&I.taxii_server_url.toLowerCase().includes(E.search.toLowerCase()))),D},re=()=>{const D=oe(),I=(h-1)*L;return D.slice(I,I+L)},Te=()=>Math.ceil(oe().length/L),ue=D=>{b(D),x(1)},je=(D,I)=>{A(J=>({...J,[D]:I})),x(1)},Le=D=>{x(D)},ne=()=>{C(!_)};return t.jsxs("section",{id:"threat-feeds",className:`page-section ${n?"active":""}`,children:[t.jsxs("div",{className:"page-header",children:[t.jsxs("div",{children:[t.jsx("h1",{className:"page-title",children:"Threat Feeds"}),t.jsx("p",{className:"page-subtitle",children:"Manage and monitor all threat intelligence feeds"})]}),t.jsxs("div",{className:"action-buttons",children:[t.jsxs("button",{className:"btn btn-outline",onClick:ne,children:[t.jsx("i",{className:"fas fa-filter"})," Filter Feeds ",_?"▲":"▼"]}),t.jsxs("button",{className:"btn btn-primary",onClick:_e,children:[t.jsx("i",{className:"fas fa-plus"})," Add New Feed"]})]})]}),_&&t.jsx("div",{className:"filters-section",children:t.jsxs("div",{className:"filters-grid",children:[t.jsxs("div",{className:"filter-group",children:[t.jsx("label",{className:"filter-label",children:"Feed Type"}),t.jsx("div",{className:"filter-control",children:t.jsxs("select",{value:E.type,onChange:D=>je("type",D.target.value),children:[t.jsx("option",{value:"",children:"All Types"}),t.jsx("option",{value:"stix-taxii",children:"STIX/TAXII"}),t.jsx("option",{value:"misp",children:"MISP"}),t.jsx("option",{value:"custom",children:"Custom"}),t.jsx("option",{value:"internal",children:"Internal"})]})})]}),t.jsxs("div",{className:"filter-group",children:[t.jsx("label",{className:"filter-label",children:"Status"}),t.jsx("div",{className:"filter-control",children:t.jsxs("select",{value:E.status,onChange:D=>je("status",D.target.value),children:[t.jsx("option",{value:"",children:"All Statuses"}),t.jsx("option",{value:"active",children:"Active"}),t.jsx("option",{value:"disabled",children:"Disabled"}),t.jsx("option",{value:"error",children:"Error"})]})})]}),t.jsxs("div",{className:"filter-group",children:[t.jsx("label",{className:"filter-label",children:"Source"}),t.jsx("div",{className:"filter-control",children:t.jsxs("select",{value:E.source,onChange:D=>je("source",D.target.value),children:[t.jsx("option",{value:"",children:"All Sources"}),t.jsx("option",{value:"external",children:"External"}),t.jsx("option",{value:"internal",children:"Internal"}),t.jsx("option",{value:"partner",children:"Partner"})]})})]}),t.jsxs("div",{className:"filter-group",children:[t.jsx("label",{className:"filter-label",children:"Search Feeds"}),t.jsx("div",{className:"filter-control",children:t.jsx("input",{type:"text",placeholder:"Search by name or URL...",value:E.search,onChange:D=>je("search",D.target.value)})})]})]})}),t.jsxs("div",{className:"tabs",children:[t.jsxs("div",{className:`tab ${v==="active"?"active":""}`,onClick:()=>ue("active"),children:["Active Feeds (",o.filter(D=>D.is_active).length,")"]}),t.jsxs("div",{className:`tab ${v==="external"?"active":""}`,onClick:()=>ue("external"),children:["External (",o.filter(D=>D.is_external).length,")"]}),t.jsxs("div",{className:`tab ${v==="internal"?"active":""}`,onClick:()=>ue("internal"),children:["Internal (",o.filter(D=>!D.is_external).length,")"]}),t.jsxs("div",{className:`tab ${v==="all"?"active":""}`,onClick:()=>ue("all"),children:["All Feeds (",o.length,")"]})]}),t.jsx("div",{className:"card",children:t.jsx("div",{className:"card-content",children:f?t.jsxs("div",{style:{textAlign:"center",padding:"2rem"},children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Loading feeds..."]}):t.jsx("ul",{className:"feed-items",children:re().map(D=>{var I,J,be,Me;return t.jsxs("li",{className:"feed-item",children:[t.jsx("div",{className:"feed-icon",children:t.jsx("i",{className:D.is_external?"fas fa-globe":"fas fa-server"})}),t.jsxs("div",{className:"feed-details",children:[t.jsx("div",{className:"feed-name",children:D.name}),t.jsx("div",{className:"feed-description",children:D.description||"No description available"}),t.jsxs("div",{className:"feed-meta",children:[t.jsxs("div",{className:"feed-stats",children:[t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-link"})," ",D.taxii_collection_id||"N/A"]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-sync-alt"})," ",D.last_sync?new Date(D.last_sync).toLocaleString():"Never"]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-globe"})," ",D.is_external?"External":"Internal"]})]}),t.jsxs("div",{className:"feed-badges",children:[t.jsx("span",{className:`badge ${D.is_public?"badge-active":"badge-medium"}`,children:D.is_public?"Public":"Private"}),t.jsx("span",{className:"badge badge-connected",children:"STIX/TAXII"}),t.jsx("button",{className:"btn btn-sm btn-primary",onClick:()=>He(D.id),disabled:M.has(D.id),style:{minWidth:"140px"},children:M.has(D.id)?t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-spinner fa-spin"}),t.jsxs("div",{style:{display:"flex",flexDirection:"column",alignItems:"flex-start",fontSize:"11px"},children:[t.jsx("span",{children:((I=Q.get(D.id))==null?void 0:I.stage)||"Processing"}),((J=Q.get(D.id))==null?void 0:J.current)&&((be=Q.get(D.id))==null?void 0:be.total)&&t.jsxs("span",{style:{opacity:.8},children:[Q.get(D.id).current,"/",Q.get(D.id).total]}),((Me=Q.get(D.id))==null?void 0:Me.percentage)>0&&t.jsxs("span",{style:{opacity:.8},children:[Q.get(D.id).percentage,"%"]})]})]}):t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-download"})," Consume"]})}),t.jsx("button",{className:"btn btn-sm btn-danger",onClick:()=>S(D),disabled:M.has(D.id),title:M.has(D.id)?"Cannot delete while consuming":"Delete this threat feed",children:t.jsx("i",{className:"fas fa-trash"})})]})]})]})]},D.id)})})})}),Te()>1&&t.jsxs("div",{className:"pagination",children:[t.jsx("div",{className:`page-item ${h===1?"disabled":""}`,onClick:()=>h>1&&Le(h-1),children:t.jsx("i",{className:"fas fa-chevron-left"})}),Array.from({length:Te()},(D,I)=>I+1).map(D=>t.jsx("div",{className:`page-item ${D===h?"active":""}`,onClick:()=>Le(D),children:D},D)),t.jsx("div",{className:`page-item ${h===Te()?"disabled":""}`,onClick:()=>h<Te()&&Le(h+1),children:t.jsx("i",{className:"fas fa-chevron-right"})})]}),p&&t.jsx("div",{className:"modal-overlay",onClick:ie,children:t.jsxs("div",{className:"modal-content",onClick:D=>D.stopPropagation(),children:[t.jsxs("div",{className:"modal-header",children:[t.jsx("h2",{children:"Add New Threat Feed"}),t.jsx("button",{className:"modal-close",onClick:ie,children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsxs("form",{onSubmit:G,className:"modal-body",children:[t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Feed Name *"}),t.jsx("input",{type:"text",name:"name",value:q.name,onChange:z,placeholder:"Enter feed name",required:!0})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Description"}),t.jsx("textarea",{name:"description",value:q.description,onChange:z,placeholder:"Enter feed description",rows:"3"})]}),t.jsx("div",{className:"form-group",children:t.jsxs("label",{className:"checkbox-label",children:[t.jsx("input",{type:"checkbox",name:"is_external",checked:q.is_external,onChange:z}),"External Feed"]})}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"TAXII Server URL *"}),t.jsx("input",{type:"url",name:"taxii_server_url",value:q.taxii_server_url,onChange:z,placeholder:"https://example.com/taxii",required:!0})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"API Root"}),t.jsx("input",{type:"text",name:"taxii_api_root",value:q.taxii_api_root,onChange:z,placeholder:"api-root"})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Collection ID"}),t.jsx("input",{type:"text",name:"taxii_collection_id",value:q.taxii_collection_id,onChange:z,placeholder:"collection-id"})]}),t.jsxs("div",{className:"form-row",children:[t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Username"}),t.jsx("input",{type:"text",name:"taxii_username",value:q.taxii_username,onChange:z,placeholder:"Username"})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Password"}),t.jsx("input",{type:"password",name:"taxii_password",value:q.taxii_password,onChange:z,placeholder:"Password"})]})]}),t.jsxs("div",{className:"modal-footer",children:[t.jsx("button",{type:"button",className:"btn btn-outline",onClick:ie,children:"Cancel"}),t.jsxs("button",{type:"submit",className:"btn btn-primary",children:[t.jsx("i",{className:"fas fa-plus"})," Add Feed"]})]})]})]})}),se&&t.jsx("div",{className:"modal-overlay",onClick:F,children:t.jsxs("div",{className:"modal-content delete-modal",onClick:D=>D.stopPropagation(),children:[t.jsxs("div",{className:"modal-header",children:[t.jsxs("h2",{children:[t.jsx("i",{className:"fas fa-exclamation-triangle",style:{color:"#dc3545"}}),"Delete Threat Feed"]}),t.jsx("button",{className:"modal-close",onClick:F,children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsx("div",{className:"modal-body",children:t.jsxs("div",{className:"delete-confirmation",children:[t.jsxs("p",{children:["Are you sure you want to delete the threat feed ",t.jsxs("strong",{children:['"',we==null?void 0:we.name,'"']}),"?"]}),t.jsxs("div",{className:"warning-text",children:[t.jsx("i",{className:"fas fa-warning"}),t.jsx("span",{children:"This action cannot be undone. All associated indicators and TTP data will also be removed."})]}),we&&t.jsxs("div",{className:"feed-info",children:[t.jsxs("div",{className:"info-row",children:[t.jsx("strong",{children:"Type:"})," ",we.is_external?"External TAXII":"Internal"]}),t.jsxs("div",{className:"info-row",children:[t.jsx("strong",{children:"Collection:"})," ",we.taxii_collection_id||"N/A"]}),t.jsxs("div",{className:"info-row",children:[t.jsx("strong",{children:"Last Sync:"})," ",we.last_sync?new Date(we.last_sync).toLocaleString():"Never"]})]})]})}),t.jsx("div",{className:"modal-footer",children:t.jsxs("div",{className:"modal-actions",children:[t.jsx("button",{type:"button",className:"btn btn-outline",onClick:F,disabled:Ne,children:"Cancel"}),t.jsx("button",{type:"button",className:"btn btn-danger",onClick:H,disabled:Ne,children:Ne?t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Deleting..."]}):t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-trash"})," Delete Feed"]})})]})})]})})]})}function w2({active:n}){if(!n)return null;const[s,l]=N.useState([]),[o,d]=N.useState([]),[f,m]=N.useState(!1),[p,g]=N.useState(!1),[h,x]=N.useState({type:"",value:"",severity:"Medium",description:"",source:"",confidence:50,threatFeed:"",createNewFeed:!1,newFeedName:"",newFeedDescription:""}),[v,b]=N.useState({}),[_,C]=N.useState(!1),[E,A]=N.useState(!1),[L,q]=N.useState("csv"),[P,M]=N.useState(!1),[X,Q]=N.useState(!1),[K,se]=N.useState(null),[Ae,we]=N.useState("auto"),[ge,Ne]=N.useState(!1),[me,xe]=N.useState([]),[He,S]=N.useState(!1),[H,F]=N.useState(!1),[_e,z]=N.useState(null),[G,ie]=N.useState({type:"",value:"",description:"",confidence:50,threat_feed_id:"",threatFeedMode:"existing"}),[oe,re]=N.useState({}),[Te,ue]=N.useState(!1),[je,Le]=N.useState(""),[ne,D]=N.useState(""),[I,J]=N.useState(!1),[be,Me]=N.useState(null),[Ve,at]=N.useState({organisations:[],anonymizationLevel:"medium",shareMethod:"taxii"}),[Ke,ta]=N.useState(!1),[_t,Tt]=N.useState(""),[Ft,Zt]=N.useState(!1),[ae,De]=N.useState(-1),[Fe,ke]=N.useState("existing"),[Be,vt]=N.useState(""),[ft,V]=N.useState(!1),[Re,U]=N.useState([]),fe=["University of Pretoria","Cyber Security Hub","SANReN CSIRT","SABRIC","University of Johannesburg","University of Cape Town","University of the Witwatersrand","Stellenbosch University","Rhodes University","North-West University","University of KwaZulu-Natal","University of the Free State","Nelson Mandela University","University of Limpopo","Walter Sisulu University","Vaal University of Technology","Central University of Technology","Durban University of Technology","Cape Peninsula University of Technology","Tshwane University of Technology","CSIR","Council for Scientific and Industrial Research","South African Police Service","State Security Agency","Department of Communications","SITA (State Information Technology Agency)","Nedbank","Standard Bank","First National Bank","ABSA Bank","Capitec Bank","African Bank","Investec"],[ee,Ce]=N.useState({type:"",severity:"",status:"",source:"",dateRange:"",searchTerm:""}),[Xe,et]=N.useState(1),[ve,Ot]=N.useState(20),[St,Ee]=N.useState(0),[R,ce]=N.useState(1),[Ie,rt]=N.useState(!1);N.useEffect(()=>{n&&(ht(),wt())},[n]),N.useEffect(()=>{function T(te){Ft&&!te.target.closest(".organisation-search-container")&&(Zt(!1),De(-1))}return document.addEventListener("mousedown",T),()=>{document.removeEventListener("mousedown",T)}},[Ft]);const wt=async()=>{const T=await ut.get("/api/threat-feeds/");T&&T.results&&U(T.results)};N.useEffect(()=>{Ct()},[s,ee,Xe,ve]);const ht=async()=>{m(!0);try{const T=await ut.get("/api/threat-feeds/");if(T&&T.results){let te=[],de=0;for(const ze of T.results){const Ze=await ut.get(`/api/threat-feeds/${ze.id}/status/`);if(Ze&&Ze.indicator_count>0){de+=Ze.indicator_count;let $e=1,Yt=!0;for(;Yt;){const Qt=await ut.get(`/api/threat-feeds/${ze.id}/indicators/?page=${$e}&page_size=100`);if(Qt&&Qt.results&&Qt.results.length>0){const wa=Qt.results.map(j=>({id:j.id,type:j.type==="ip"?"IP Address":j.type==="domain"?"Domain":j.type==="url"?"URL":j.type==="file_hash"?"File Hash":j.type==="email"?"Email":j.type==="user_agent"?"User Agent":j.type==="registry"?"Registry Key":j.type==="mutex"?"Mutex":j.type==="process"?"Process":j.type,rawType:j.type,title:j.name||"",value:j.value,severity:j.confidence>=75?"High":j.confidence>=50?"Medium":"Low",confidence:j.confidence,source:j.source||ze.name||"Unknown",description:j.description||"",created:new Date(j.created_at).toISOString().split("T")[0],createdDate:new Date(j.created_at),status:j.is_anonymized?"Anonymized":"Active",feedId:ze.id,feedName:ze.name}));te.push(...wa),Yt=Qt.next!==null,$e++}else Yt=!1}}}te.sort((ze,Ze)=>Ze.createdDate-ze.createdDate),l(te),Ee(te.length),console.log(`Loaded ${te.length} indicators from ${T.results.length} feeds`)}}catch(T){console.error("Error fetching indicators:",T)}m(!1)},Ct=()=>{let T=[...s];if(ee.type&&(T=T.filter(te=>te.rawType===ee.type)),ee.severity&&(T=T.filter(te=>te.severity.toLowerCase()===ee.severity.toLowerCase())),ee.status&&(T=T.filter(te=>te.status.toLowerCase()===ee.status.toLowerCase())),ee.source&&(T=T.filter(te=>te.source.toLowerCase().includes(ee.source.toLowerCase()))),ee.searchTerm){const te=ee.searchTerm.toLowerCase();T=T.filter(de=>de.value.toLowerCase().includes(te)||de.description.toLowerCase().includes(te)||de.title&&de.title.toLowerCase().includes(te)||de.name&&de.name.toLowerCase().includes(te))}if(ee.dateRange){const te=new Date;let de;switch(ee.dateRange){case"today":de=new Date(te.getFullYear(),te.getMonth(),te.getDate());break;case"week":de=new Date(te.getTime()-10080*60*1e3);break;case"month":de=new Date(te.getTime()-720*60*60*1e3);break;case"quarter":de=new Date(te.getTime()-2160*60*60*1e3);break;default:de=null}de&&(T=T.filter(ze=>ze.createdDate>=de))}d(T),ce(Math.ceil(T.length/ve)),Xe>Math.ceil(T.length/ve)&&et(1)},Bt=(T,te)=>{Ce(de=>({...de,[T]:te})),et(1)},mt=()=>{Ce({type:"",severity:"",status:"",source:"",dateRange:"",searchTerm:""}),et(1)},Oe=()=>{const T=(Xe-1)*ve,te=T+ve;return o.slice(T,te)},lt=T=>{T>=1&&T<=R&&et(T)},Ut=()=>{ht()};return t.jsxs("section",{id:"ioc-management",className:`page-section ${n?"active":""}`,children:[t.jsxs("div",{className:"page-header",children:[t.jsxs("div",{children:[t.jsx("h1",{className:"page-title",children:"IoC Management"}),t.jsx("p",{className:"page-subtitle",children:"Manage and analyze indicators of compromise"})]}),t.jsxs("div",{className:"action-buttons",children:[t.jsxs("button",{className:"btn btn-outline",onClick:()=>A(!0),children:[t.jsx("i",{className:"fas fa-file-export"})," Export IoCs"]}),t.jsxs("button",{className:"btn btn-outline",onClick:()=>Q(!0),children:[t.jsx("i",{className:"fas fa-file-import"})," Import IoCs"]}),t.jsxs("button",{className:"btn btn-primary",onClick:()=>g(!0),children:[t.jsx("i",{className:"fas fa-plus"})," Add New IoC"]})]})]}),t.jsxs("div",{className:"filters-section",children:[t.jsxs("div",{className:"filters-header",children:[t.jsxs("h3",{children:[t.jsx("i",{className:"fas fa-filter"})," Filter & Search IoCs"]}),t.jsxs("div",{className:"filter-actions",children:[Object.values(ee).some(T=>T!=="")&&t.jsxs("button",{className:"btn btn-secondary btn-sm",onClick:mt,title:"Clear all active filters",children:[t.jsx("i",{className:"fas fa-times"})," Clear Filters"]}),t.jsx("div",{className:"results-summary",children:Object.values(ee).some(T=>T!=="")?t.jsxs("span",{className:"filtered-count",children:[t.jsx("strong",{children:o.length})," of ",t.jsx("strong",{children:s.length})," indicators match"]}):t.jsxs("span",{className:"total-count",children:[t.jsx("strong",{children:s.length})," total indicators"]})})]})]}),t.jsxs("div",{className:"filters-grid",children:[t.jsxs("div",{className:"filter-group",children:[t.jsx("label",{className:"filter-label",children:"Search"}),t.jsx("div",{className:"filter-control",children:t.jsx("input",{type:"text",placeholder:"Search by value or description...",value:ee.searchTerm,onChange:T=>Bt("searchTerm",T.target.value),className:"form-control"})})]}),t.jsxs("div",{className:"filter-group",children:[t.jsx("label",{className:"filter-label",children:"IoC Type"}),t.jsx("div",{className:"filter-control",children:t.jsxs("select",{value:ee.type,onChange:T=>Bt("type",T.target.value),className:"form-control",children:[t.jsx("option",{value:"",children:"All Types"}),t.jsx("option",{value:"ip",children:"IP Address"}),t.jsx("option",{value:"domain",children:"Domain"}),t.jsx("option",{value:"url",children:"URL"}),t.jsx("option",{value:"file_hash",children:"File Hash"}),t.jsx("option",{value:"email",children:"Email"}),t.jsx("option",{value:"user_agent",children:"User Agent"}),t.jsx("option",{value:"registry",children:"Registry Key"}),t.jsx("option",{value:"mutex",children:"Mutex"}),t.jsx("option",{value:"process",children:"Process"})]})})]}),t.jsxs("div",{className:"filter-group",children:[t.jsx("label",{className:"filter-label",children:"Severity"}),t.jsx("div",{className:"filter-control",children:t.jsxs("select",{value:ee.severity,onChange:T=>Bt("severity",T.target.value),className:"form-control",children:[t.jsx("option",{value:"",children:"All Severities"}),t.jsx("option",{value:"high",children:"High"}),t.jsx("option",{value:"medium",children:"Medium"}),t.jsx("option",{value:"low",children:"Low"})]})})]}),t.jsxs("div",{className:"filter-group",children:[t.jsx("label",{className:"filter-label",children:"Status"}),t.jsx("div",{className:"filter-control",children:t.jsxs("select",{value:ee.status,onChange:T=>Bt("status",T.target.value),className:"form-control",children:[t.jsx("option",{value:"",children:"All Statuses"}),t.jsx("option",{value:"active",children:"Active"}),t.jsx("option",{value:"anonymized",children:"Anonymized"}),t.jsx("option",{value:"inactive",children:"Inactive"}),t.jsx("option",{value:"review",children:"Under Review"})]})})]}),t.jsxs("div",{className:"filter-group",children:[t.jsx("label",{className:"filter-label",children:"Source"}),t.jsx("div",{className:"filter-control",children:t.jsx("input",{type:"text",placeholder:"Filter by source...",value:ee.source,onChange:T=>Bt("source",T.target.value),className:"form-control"})})]}),t.jsxs("div",{className:"filter-group",children:[t.jsx("label",{className:"filter-label",children:"Date Range"}),t.jsx("div",{className:"filter-control",children:t.jsxs("select",{value:ee.dateRange,onChange:T=>Bt("dateRange",T.target.value),className:"form-control",children:[t.jsx("option",{value:"",children:"All Time"}),t.jsx("option",{value:"today",children:"Today"}),t.jsx("option",{value:"week",children:"Last Week"}),t.jsx("option",{value:"month",children:"Last Month"}),t.jsx("option",{value:"quarter",children:"Last Quarter"})]})})]})]})]}),t.jsxs("div",{className:"card",children:[t.jsxs("div",{className:"card-header",children:[t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-search card-icon"})," Indicators of Compromise"]}),t.jsxs("div",{className:"card-actions",children:[t.jsxs("div",{className:"items-per-page-selector",style:{display:"flex",alignItems:"center",gap:"0.5rem",marginRight:"1rem"},children:[t.jsx("label",{htmlFor:"itemsPerPage",style:{fontSize:"0.75rem",color:"#666",whiteSpace:"nowrap"},children:"Show:"}),t.jsxs("select",{id:"itemsPerPage",value:ve,onChange:T=>{Ot(Number(T.target.value)),et(1)},className:"form-control form-control-sm",style:{height:"32px",fontSize:"0.875rem",padding:"0.25rem 0.5rem",minWidth:"100px",borderRadius:"4px",border:"1px solid #ccc"},children:[t.jsx("option",{value:10,children:"10 per page"}),t.jsx("option",{value:20,children:"20 per page"}),t.jsx("option",{value:50,children:"50 per page"}),t.jsx("option",{value:100,children:"100 per page"})]})]}),t.jsxs("button",{className:"btn btn-outline btn-sm",onClick:Ut,disabled:f,style:{height:"32px",fontSize:"0.875rem",padding:"0.25rem 0.75rem",display:"flex",alignItems:"center",gap:"0.4rem",borderRadius:"4px",lineHeight:"1",minHeight:"32px",maxHeight:"32px"},children:[t.jsx("i",{className:`fas fa-sync-alt ${f?"fa-spin":""}`}),f?"Refreshing...":"Refresh"]})]})]}),t.jsx("div",{className:"card-content",children:t.jsx("div",{className:"table-responsive",children:t.jsxs("table",{className:"data-table",children:[t.jsx("thead",{children:t.jsxs("tr",{children:[t.jsx("th",{children:t.jsx("input",{type:"checkbox"})}),t.jsx("th",{children:"Type"}),t.jsx("th",{children:"Title"}),t.jsx("th",{children:"Value"}),t.jsx("th",{children:"Description"}),t.jsx("th",{children:"Severity"}),t.jsx("th",{children:"Source"}),t.jsx("th",{children:"Date Added"}),t.jsx("th",{children:"Status"}),t.jsx("th",{children:"Actions"})]})}),t.jsx("tbody",{children:f?t.jsx("tr",{children:t.jsxs("td",{colSpan:"10",style:{textAlign:"center",padding:"2rem"},children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Loading indicators..."]})}):Oe().length>0?Oe().map(T=>t.jsxs("tr",{children:[t.jsx("td",{children:t.jsx("input",{type:"checkbox"})}),t.jsx("td",{children:t.jsx("span",{className:`type-badge type-${T.rawType}`,children:T.type})}),t.jsx("td",{className:"indicator-title",title:T.title||"",children:T.title?T.title.length>30?`${T.title.substring(0,30)}...`:T.title:t.jsx("em",{className:"text-muted",children:"No title"})}),t.jsx("td",{className:"indicator-value",title:T.value,children:T.value.length>50?`${T.value.substring(0,50)}...`:T.value}),t.jsx("td",{className:"indicator-description",title:T.description||"",children:T.description?T.description.length>40?`${T.description.substring(0,40)}...`:T.description:t.jsx("em",{className:"text-muted",children:"No description"})}),t.jsx("td",{children:t.jsx("span",{className:`badge badge-${T.severity.toLowerCase()}`,children:T.severity})}),t.jsx("td",{children:T.source}),t.jsx("td",{children:T.created}),t.jsx("td",{children:t.jsx("span",{className:`badge badge-${T.status.toLowerCase()}`,children:T.status})}),t.jsxs("td",{children:[t.jsx("button",{className:"btn btn-outline btn-sm",title:"Edit Indicator",onClick:()=>ga(T),children:t.jsx("i",{className:"fas fa-edit"})}),t.jsx("button",{className:"btn btn-outline btn-sm",title:"Share Indicator",onClick:()=>an(T),children:t.jsx("i",{className:"fas fa-share-alt"})})]})]},T.id)):o.length===0&&s.length>0?t.jsx("tr",{children:t.jsxs("td",{colSpan:"10",style:{textAlign:"center",padding:"2rem"},children:[t.jsx("i",{className:"fas fa-filter"})," No indicators match the current filters.",t.jsx("br",{}),t.jsxs("button",{className:"btn btn-outline btn-sm mt-2",onClick:mt,children:[t.jsx("i",{className:"fas fa-times"})," Clear Filters"]})]})}):t.jsx("tr",{children:t.jsxs("td",{colSpan:"10",style:{textAlign:"center",padding:"2rem"},children:[t.jsx("i",{className:"fas fa-info-circle"})," No indicators found. Try consuming threat feeds to populate data."]})})})]})})})]}),t.jsxs("div",{className:"pagination-wrapper",style:{margin:"2rem auto",display:"flex",flexDirection:"column",gap:"1rem",padding:"1.5rem",background:"#f8f9fa",borderRadius:"8px",border:"1px solid #dee2e6",maxWidth:"fit-content",width:"auto",textAlign:"center"},children:[t.jsx("div",{className:"pagination-info-detailed",children:t.jsxs("span",{className:"pagination-summary",children:["Showing ",t.jsx("strong",{children:Math.min((Xe-1)*ve+1,o.length)})," to ",t.jsx("strong",{children:Math.min(Xe*ve,o.length)})," of ",t.jsx("strong",{children:o.length}),Object.values(ee).some(T=>T!=="")?" filtered":""," indicators"]})}),R>1&&t.jsxs("div",{className:"pagination-controls-enhanced",style:{display:"flex",justifyContent:"center",alignItems:"center",gap:"0.5rem",flexWrap:"nowrap",overflowX:"auto",padding:"0.5rem",margin:"0 auto",width:"fit-content"},children:[t.jsx("button",{className:"btn btn-outline btn-sm",onClick:()=>lt(1),disabled:Xe===1,title:"First page",children:t.jsx("i",{className:"fas fa-angle-double-left"})}),t.jsx("button",{className:"btn btn-outline btn-sm",onClick:()=>lt(Xe-1),disabled:Xe===1,title:"Previous page",children:t.jsx("i",{className:"fas fa-angle-left"})}),(()=>{const T=[],te=Math.max(1,Xe-2),de=Math.min(R,Xe+2);te>1&&(T.push(t.jsx("button",{className:"btn btn-outline btn-sm",onClick:()=>lt(1),children:"1"},1)),te>2&&T.push(t.jsx("span",{className:"pagination-ellipsis",children:"..."},"ellipsis1")));for(let ze=te;ze<=de;ze++)T.push(t.jsx("button",{className:`btn btn-sm ${ze===Xe?"btn-primary":"btn-outline"}`,onClick:()=>lt(ze),children:ze},ze));return de<R&&(de<R-1&&T.push(t.jsx("span",{className:"pagination-ellipsis",children:"..."},"ellipsis2")),T.push(t.jsx("button",{className:"btn btn-outline btn-sm",onClick:()=>lt(R),children:R},R))),T})(),t.jsx("button",{className:"btn btn-outline btn-sm",onClick:()=>lt(Xe+1),disabled:Xe===R,title:"Next page",children:t.jsx("i",{className:"fas fa-angle-right"})}),t.jsx("button",{className:"btn btn-outline btn-sm",onClick:()=>lt(R),disabled:Xe===R,title:"Last page",children:t.jsx("i",{className:"fas fa-angle-double-right"})})]})]}),t.jsxs("div",{className:"card mt-4",children:[t.jsx("div",{className:"card-header",children:t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-chart-pie card-icon"})," IoC Statistics"]})}),t.jsx("div",{className:"card-content",children:t.jsxs("div",{className:"stats-grid",children:[t.jsxs("div",{className:"stat-card",children:[t.jsxs("div",{className:"stat-title",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-search"})}),t.jsxs("span",{children:["Total IoCs",Object.values(ee).some(T=>T!=="")?" (Filtered)":""]})]}),t.jsx("div",{className:"stat-value",children:Object.values(ee).some(T=>T!=="")?o.length:s.length}),t.jsx("div",{className:"stat-description",children:Object.values(ee).some(T=>T!=="")?`${o.length} of ${s.length} match filters`:"All indicators in system"})]}),t.jsxs("div",{className:"stat-card",children:[t.jsxs("div",{className:"stat-title",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-exclamation-triangle"})}),t.jsx("span",{children:"High Severity"})]}),t.jsx("div",{className:"stat-value",children:(Object.values(ee).some(T=>T!=="")?o:s).filter(T=>T.severity.toLowerCase()==="high").length}),t.jsx("div",{className:"stat-description",children:"Critical threat indicators"})]}),t.jsxs("div",{className:"stat-card",children:[t.jsxs("div",{className:"stat-title",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-user-secret"})}),t.jsx("span",{children:"Anonymized"})]}),t.jsx("div",{className:"stat-value",children:(Object.values(ee).some(T=>T!=="")?o:s).filter(T=>T.status.toLowerCase()==="anonymized").length}),t.jsx("div",{className:"stat-description",children:"Privacy-protected IoCs"})]}),t.jsxs("div",{className:"stat-card",children:[t.jsxs("div",{className:"stat-title",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-chart-line"})}),t.jsx("span",{children:"Active"})]}),t.jsx("div",{className:"stat-value",children:(Object.values(ee).some(T=>T!=="")?o:s).filter(T=>T.status.toLowerCase()==="active").length}),t.jsx("div",{className:"stat-description",children:"Currently monitored IoCs"})]})]})})]}),p&&t.jsx("div",{className:"modal-overlay",onClick:qt,children:t.jsxs("div",{className:"modal-content",onClick:T=>T.stopPropagation(),children:[t.jsxs("div",{className:"modal-header",children:[t.jsxs("h2",{children:[t.jsx("i",{className:"fas fa-plus"})," Add New IoC"]}),t.jsx("button",{className:"modal-close",onClick:qt,children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsx("div",{className:"modal-body",children:t.jsxs("form",{onSubmit:ki,children:[t.jsxs("div",{className:"form-grid",children:[t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"IoC Type *"}),t.jsxs("select",{value:h.type,onChange:T=>x({...h,type:T.target.value}),className:v.type?"form-control error":"form-control",required:!0,children:[t.jsx("option",{value:"",children:"Select Type"}),t.jsx("option",{value:"ip",children:"IP Address"}),t.jsx("option",{value:"domain",children:"Domain"}),t.jsx("option",{value:"url",children:"URL"}),t.jsx("option",{value:"file_hash",children:"File Hash"}),t.jsx("option",{value:"email",children:"Email"}),t.jsx("option",{value:"user_agent",children:"User Agent"}),t.jsx("option",{value:"registry",children:"Registry Key"}),t.jsx("option",{value:"mutex",children:"Mutex"}),t.jsx("option",{value:"process",children:"Process"})]}),v.type&&t.jsx("span",{className:"error-text",children:v.type})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"Severity"}),t.jsxs("select",{value:h.severity,onChange:T=>x({...h,severity:T.target.value}),className:"form-control",children:[t.jsx("option",{value:"Low",children:"Low"}),t.jsx("option",{value:"Medium",children:"Medium"}),t.jsx("option",{value:"High",children:"High"})]})]})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"IoC Value *"}),t.jsx("input",{type:"text",value:h.value,onChange:T=>x({...h,value:T.target.value}),className:v.value?"form-control error":"form-control",placeholder:"Enter the indicator value (e.g., 192.168.1.1, malicious.com, etc.)",required:!0}),v.value&&t.jsx("span",{className:"error-text",children:v.value})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"Source"}),t.jsx("input",{type:"text",value:h.source,onChange:T=>x({...h,source:T.target.value}),className:"form-control",placeholder:"Source of this IoC (e.g., Internal Analysis, OSINT, etc.)"})]}),t.jsxs("div",{className:"form-group",children:[t.jsxs("label",{className:"form-label",children:["Confidence Level: ",h.confidence,"%"]}),t.jsx("input",{type:"range",min:"0",max:"100",value:h.confidence,onChange:T=>x({...h,confidence:parseInt(T.target.value)}),className:"form-range"}),t.jsxs("div",{className:"range-labels",children:[t.jsx("span",{children:"Low (0%)"}),t.jsx("span",{children:"High (100%)"})]})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"Description"}),t.jsx("textarea",{value:h.description,onChange:T=>x({...h,description:T.target.value}),className:"form-control",rows:"3",placeholder:"Additional notes or description about this IoC..."})]}),t.jsxs("div",{className:"modal-actions",children:[t.jsx("button",{type:"button",className:"btn btn-outline",onClick:qt,disabled:_,children:"Cancel"}),t.jsx("button",{type:"submit",className:"btn btn-primary",disabled:_,children:_?t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Adding..."]}):t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-plus"})," Add IoC"]})})]})]})})]})}),E&&t.jsx("div",{className:"modal-overlay",onClick:Ia,children:t.jsxs("div",{className:"modal-content",onClick:T=>T.stopPropagation(),children:[t.jsxs("div",{className:"modal-header",children:[t.jsxs("h2",{children:[t.jsx("i",{className:"fas fa-file-export"})," Export IoCs"]}),t.jsx("button",{className:"modal-close",onClick:Ia,children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsxs("div",{className:"modal-body",children:[t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"Export Format"}),t.jsxs("select",{value:L,onChange:T=>q(T.target.value),className:"form-control",children:[t.jsx("option",{value:"csv",children:"CSV (Comma Separated Values)"}),t.jsx("option",{value:"json",children:"JSON (JavaScript Object Notation)"}),t.jsx("option",{value:"stix",children:"STIX 2.1 (Structured Threat Information)"})]})]}),t.jsx("div",{className:"export-info",children:t.jsxs("div",{className:"info-card",children:[t.jsx("i",{className:"fas fa-info-circle"}),t.jsxs("div",{children:[t.jsx("strong",{children:"Export Details:"}),t.jsxs("p",{children:["You are about to export ",s.length," indicators of compromise."]}),L==="csv"&&t.jsxs("p",{children:[t.jsx("strong",{children:"CSV Format:"})," Suitable for spreadsheet analysis. Includes all indicator fields in tabular format."]}),L==="json"&&t.jsxs("p",{children:[t.jsx("strong",{children:"JSON Format:"})," Machine-readable format suitable for programmatic processing and API integration."]}),L==="stix"&&t.jsxs("p",{children:[t.jsx("strong",{children:"STIX 2.1 Format:"})," Industry-standard format for threat intelligence sharing. Compatible with TAXII servers."]})]})]})}),t.jsxs("div",{className:"modal-actions",children:[t.jsx("button",{type:"button",className:"btn btn-outline",onClick:Ia,disabled:P,children:"Cancel"}),t.jsx("button",{type:"button",className:"btn btn-primary",onClick:en,disabled:P,children:P?t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Exporting..."]}):t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-download"})," Export ",s.length," IoCs"]})})]})]})]})}),X&&t.jsx("div",{className:"modal-overlay",onClick:Aa,children:t.jsxs("div",{className:"modal-content",onClick:T=>T.stopPropagation(),children:[t.jsxs("div",{className:"modal-header",children:[t.jsxs("h2",{children:[t.jsx("i",{className:"fas fa-file-import"})," Import IoCs"]}),t.jsx("button",{className:"modal-close",onClick:Aa,children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsx("div",{className:"modal-body",children:He?t.jsxs(t.Fragment,{children:[t.jsxs("div",{className:"preview-header",children:[t.jsx("h3",{children:"Import Preview"}),t.jsxs("p",{children:["Review ",me.length," indicators before importing:"]})]}),t.jsxs("div",{className:"preview-table-container",children:[t.jsxs("table",{className:"preview-table",children:[t.jsx("thead",{children:t.jsxs("tr",{children:[t.jsx("th",{children:"Type"}),t.jsx("th",{children:"Title"}),t.jsx("th",{children:"Value"}),t.jsx("th",{children:"Description"}),t.jsx("th",{children:"Severity"}),t.jsx("th",{children:"Source"}),t.jsx("th",{children:"Status"})]})}),t.jsx("tbody",{children:me.slice(0,10).map((T,te)=>{var de;return t.jsxs("tr",{children:[t.jsx("td",{children:T.type}),t.jsx("td",{className:"truncate",title:T.name||"",children:T.name||t.jsx("em",{children:"No title"})}),t.jsx("td",{className:"truncate",children:T.value}),t.jsx("td",{className:"truncate",title:T.description||"",children:T.description||t.jsx("em",{children:"No description"})}),t.jsx("td",{children:t.jsx("span",{className:`badge badge-${(de=T.severity)==null?void 0:de.toLowerCase()}`,children:T.severity})}),t.jsx("td",{children:T.source}),t.jsx("td",{children:T.status})]},te)})})]}),me.length>10&&t.jsxs("p",{className:"preview-note",children:["... and ",me.length-10," more indicators"]})]}),t.jsxs("div",{className:"modal-actions",children:[t.jsxs("button",{type:"button",className:"btn btn-outline",onClick:Ga,disabled:ge,children:[t.jsx("i",{className:"fas fa-arrow-left"})," Back"]}),t.jsx("button",{type:"button",className:"btn btn-primary",onClick:da,disabled:ge,children:ge?t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Importing..."]}):t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-upload"})," Import ",me.length," IoCs"]})})]})]}):t.jsxs(t.Fragment,{children:[t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"Import Format"}),t.jsxs("select",{value:Ae,onChange:T=>we(T.target.value),className:"form-control",children:[t.jsx("option",{value:"auto",children:"Auto-detect from file"}),t.jsx("option",{value:"csv",children:"CSV (Comma Separated Values)"}),t.jsx("option",{value:"json",children:"JSON (JavaScript Object Notation)"}),t.jsx("option",{value:"stix",children:"STIX 2.1 (Structured Threat Information)"})]})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"Select File"}),t.jsxs("div",{className:"file-upload-area",onDrop:tt,onDragOver:Fa,children:[t.jsx("input",{type:"file",accept:".csv,.json",onChange:gt,className:"file-input",id:"import-file"}),t.jsxs("label",{htmlFor:"import-file",className:"file-upload-label",children:[t.jsx("i",{className:"fas fa-cloud-upload-alt"}),t.jsx("span",{children:K?K.name:"Drop file here or click to browse"}),t.jsx("small",{children:"Supported formats: CSV, JSON, STIX (.json)"})]})]})]}),t.jsx("div",{className:"import-info",children:t.jsxs("div",{className:"info-card",children:[t.jsx("i",{className:"fas fa-info-circle"}),t.jsxs("div",{children:[t.jsx("strong",{children:"Import Guidelines:"}),t.jsxs("ul",{children:[t.jsxs("li",{children:[t.jsx("strong",{children:"CSV:"})," Must include headers: Type, Value, Severity, Source, Status"]}),t.jsxs("li",{children:[t.jsx("strong",{children:"JSON:"})," Should match the export format structure"]}),t.jsxs("li",{children:[t.jsx("strong",{children:"STIX:"})," Must be valid STIX 2.1 bundle format"]}),t.jsx("li",{children:"Duplicate indicators will be skipped automatically"})]})]})]})}),t.jsxs("div",{className:"modal-actions",children:[t.jsx("button",{type:"button",className:"btn btn-outline",onClick:Aa,disabled:ge,children:"Cancel"}),t.jsx("button",{type:"button",className:"btn btn-primary",onClick:Ya,disabled:!K||ge,children:ge?t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Processing..."]}):t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-eye"})," Preview Import"]})})]})]})})]})}),H&&t.jsx("div",{className:"modal-overlay",onClick:hn,children:t.jsxs("div",{className:"modal-content",onClick:T=>T.stopPropagation(),children:[t.jsxs("div",{className:"modal-header",children:[t.jsxs("h2",{children:[t.jsx("i",{className:"fas fa-edit"})," Edit IoC"]}),t.jsx("button",{className:"modal-close",onClick:hn,children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsx("div",{className:"modal-body",children:t.jsxs("form",{onSubmit:rs,children:[t.jsxs("div",{className:"form-grid",children:[t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"IoC Type *"}),t.jsxs("select",{value:G.type,onChange:T=>ie({...G,type:T.target.value}),className:oe.type?"form-control error":"form-control",required:!0,children:[t.jsx("option",{value:"",children:"Select Type"}),t.jsx("option",{value:"ip",children:"IP Address"}),t.jsx("option",{value:"domain",children:"Domain"}),t.jsx("option",{value:"url",children:"URL"}),t.jsx("option",{value:"file_hash",children:"File Hash"}),t.jsx("option",{value:"email",children:"Email"}),t.jsx("option",{value:"user_agent",children:"User Agent"}),t.jsx("option",{value:"registry",children:"Registry Key"}),t.jsx("option",{value:"mutex",children:"Mutex"}),t.jsx("option",{value:"process",children:"Process"})]}),oe.type&&t.jsx("span",{className:"error-text",children:oe.type})]}),t.jsxs("div",{className:"form-group",children:[t.jsxs("label",{className:"form-label",children:["Confidence Level: ",G.confidence,"%"]}),t.jsx("input",{type:"range",min:"0",max:"100",value:G.confidence,onChange:T=>ie({...G,confidence:parseInt(T.target.value)}),className:"form-range"}),t.jsxs("div",{className:"range-labels",children:[t.jsx("span",{children:"Low (0%)"}),t.jsx("span",{children:"High (100%)"})]})]})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"IoC Value *"}),t.jsx("input",{type:"text",value:G.value,onChange:T=>ie({...G,value:T.target.value}),className:oe.value?"form-control error":"form-control",placeholder:"Enter IoC value (IP, domain, hash, etc.)",required:!0}),oe.value&&t.jsx("span",{className:"error-text",children:oe.value})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"Description"}),t.jsx("textarea",{value:G.description,onChange:T=>ie({...G,description:T.target.value}),className:"form-control",placeholder:"Optional description or notes",rows:"3"})]}),oe.submit&&t.jsxs("div",{className:"error-message",children:[t.jsx("i",{className:"fas fa-exclamation-triangle"}),oe.submit]}),t.jsxs("div",{className:"modal-actions",children:[t.jsx("button",{type:"button",className:"btn btn-outline",onClick:hn,disabled:Te,children:"Cancel"}),t.jsx("button",{type:"submit",className:"btn btn-primary",disabled:Te,children:Te?t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Updating..."]}):t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-save"})," Update IoC"]})})]})]})})]})}),I&&t.jsx("div",{className:"modal-overlay",onClick:Un,children:t.jsxs("div",{className:"modal-content",onClick:T=>T.stopPropagation(),children:[t.jsxs("div",{className:"modal-header",children:[t.jsxs("h2",{children:[t.jsx("i",{className:"fas fa-share-alt"})," Share IoC"]}),t.jsx("button",{className:"modal-close",onClick:Un,children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsx("div",{className:"modal-body",children:t.jsxs("form",{onSubmit:Gt,children:[t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"IoC Details"}),t.jsxs("div",{className:"info-box",children:[t.jsxs("p",{children:[t.jsx("strong",{children:"Type:"})," ",be==null?void 0:be.type]}),t.jsxs("p",{children:[t.jsx("strong",{children:"Value:"})," ",be==null?void 0:be.value]}),t.jsxs("p",{children:[t.jsx("strong",{children:"Source:"})," ",be==null?void 0:be.source]})]})]}),t.jsxs("div",{className:"form-group",children:[t.jsxs("label",{className:"form-label",children:[t.jsx("i",{className:"fas fa-share-nodes form-icon"}),"Target Organizations"]}),t.jsx("p",{className:"form-description",children:"Select trusted organisations to share this threat intelligence with"}),t.jsxs("div",{className:"sleek-org-selector",children:[t.jsxs("div",{className:"search-field",children:[t.jsx("input",{type:"text",className:"sleek-search-input",value:Be,onChange:T=>{vt(T.target.value),V(!0)},onFocus:()=>V(!0),onBlur:T=>{setTimeout(()=>{(!T.relatedTarget||!T.relatedTarget.closest(".results-list"))&&V(!1)},200)},placeholder:"Type to search organizations..."}),t.jsx("i",{className:"fas fa-search search-icon"})]}),ft&&Be&&t.jsxs("div",{className:"results-list",children:[fe.filter(T=>!Ve.organisations.includes(T)&&T.toLowerCase().includes(Be.toLowerCase())).slice(0,5).map(T=>t.jsxs("div",{className:"result-item",onClick:()=>{Ln(T),vt(""),V(!1)},children:[t.jsx("span",{className:"result-name",children:T}),t.jsx("i",{className:"fas fa-plus add-icon"})]},T)),fe.filter(T=>!Ve.organisations.includes(T)&&T.toLowerCase().includes(Be.toLowerCase())).length===0&&t.jsx("div",{className:"no-results",children:"No organizations found"})]}),Ve.organisations.length>0&&t.jsxs("div",{className:"selected-orgs",children:[t.jsxs("div",{className:"selected-label",children:["Selected (",Ve.organisations.length,")"]}),t.jsx("div",{className:"org-tags",children:Ve.organisations.map(T=>t.jsxs("div",{className:"org-tag",children:[t.jsx("span",{children:T}),t.jsx("button",{type:"button",className:"remove-tag",onClick:()=>si(T),children:"×"})]},T))})]})]})]}),t.jsxs("div",{className:"form-grid",children:[t.jsxs("div",{className:"form-group",children:[t.jsxs("label",{className:"form-label",children:[t.jsx("i",{className:"fas fa-user-secret form-icon"}),"Anonymization Level"]}),t.jsx("p",{className:"form-description",children:"Choose how much detail to share with receiving organizations"}),t.jsxs("select",{value:Ve.anonymizationLevel,onChange:T=>at({...Ve,anonymizationLevel:T.target.value}),className:"form-control enhanced-select multiline-select",children:[t.jsx("option",{value:"none",children:"None - Full Details Complete IoC values and metadata shared"}),t.jsx("option",{value:"low",children:"Low - Minor Obfuscation Remove source identifiers and timestamps"}),t.jsx("option",{value:"medium",children:"Medium - Partial Anonymization Generalize IPs/domains (evil.com → *.com)"}),t.jsx("option",{value:"high",children:"High - Strong Anonymization Only patterns and techniques, no indicators"})]})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"Share Method"}),t.jsxs("select",{value:Ve.shareMethod,onChange:T=>at({...Ve,shareMethod:T.target.value}),className:"form-control",children:[t.jsx("option",{value:"taxii",children:"TAXII 2.1 Protocol"}),t.jsx("option",{value:"email",children:"Email Export"}),t.jsx("option",{value:"api",children:"Direct API Push"})]})]})]}),t.jsxs("div",{className:"modal-actions",children:[t.jsx("button",{type:"button",className:"btn btn-outline",onClick:Un,disabled:Ke,children:"Cancel"}),t.jsx("button",{type:"submit",className:"btn btn-primary",disabled:Ke||Ve.organisations.length===0,children:Ke?t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Sharing..."]}):t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-share-alt"})," Share with ",Ve.organisations.length," Organisation(s)"]})})]})]})})]})})]});function qt(){g(!1),x({type:"",value:"",severity:"Medium",description:"",source:"",confidence:50,threatFeed:"",createNewFeed:!1,newFeedName:"",newFeedDescription:""}),b({})}function Ia(){A(!1),q("csv")}async function en(){if(s.length===0){alert("No indicators to export");return}M(!0);try{let T,te,de;switch(L){case"csv":T=Ht(s),te=`iocs_export_${new Date().toISOString().split("T")[0]}.csv`,de="text/csv";break;case"json":T=fn(s),te=`iocs_export_${new Date().toISOString().split("T")[0]}.json`,de="application/json";break;case"stix":T=$a(s),te=`iocs_export_${new Date().toISOString().split("T")[0]}.json`,de="application/json";break;default:throw new Error("Unsupported export format")}const ze=new Blob([T],{type:de}),Ze=window.URL.createObjectURL(ze),$e=document.createElement("a");$e.href=Ze,$e.download=te,document.body.appendChild($e),$e.click(),document.body.removeChild($e),window.URL.revokeObjectURL(Ze),Ia(),console.log(`Successfully exported ${s.length} IoCs as ${L.toUpperCase()}`)}catch(T){console.error("Export failed:",T),alert("Export failed. Please try again.")}finally{M(!1)}}function Ht(T){const de=["Type","Value","Severity","Source","Date Added","Status"].join(","),ze=T.map(Ze=>[`"${Ze.type}"`,`"${Ze.value}"`,`"${Ze.severity}"`,`"${Ze.source}"`,`"${Ze.created}"`,`"${Ze.status}"`].join(","));return[de,...ze].join(`
`)}function fn(T){const te={export_date:new Date().toISOString(),total_indicators:T.length,indicators:T.map(de=>({id:de.id,type:de.type,value:de.value,severity:de.severity,source:de.source,created:de.created,status:de.status}))};return JSON.stringify(te,null,2)}function $a(T){const te={type:"bundle",id:`bundle--${Da()}`,spec_version:"2.1",created:new Date().toISOString(),modified:new Date().toISOString(),objects:T.map(de=>({type:"indicator",id:`indicator--${Da()}`,created:new Date(de.created).toISOString(),modified:new Date().toISOString(),labels:["malicious-activity"],pattern:tn(de),indicator_types:["malicious-activity"],confidence:sa(de.severity),x_crisp_source:de.source,x_crisp_severity:de.severity,x_crisp_status:de.status}))};return JSON.stringify(te,null,2)}function Da(){return"xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g,function(T){const te=Math.random()*16|0;return(T=="x"?te:te&3|8).toString(16)})}function tn(T){switch(T.type.toLowerCase()){case"ip address":return`[ipv4-addr:value = '${T.value}']`;case"domain":return`[domain-name:value = '${T.value}']`;case"url":return`[url:value = '${T.value}']`;case"file hash":return`[file:hashes.MD5 = '${T.value}' OR file:hashes.SHA1 = '${T.value}' OR file:hashes.SHA256 = '${T.value}']`;case"email":return`[email-addr:value = '${T.value}']`;default:return`[x-custom:value = '${T.value}']`}}function sa(T){switch(T.toLowerCase()){case"high":return 85;case"medium":return 60;case"low":return 30;default:return 50}}function Aa(){Q(!1),se(null),we("auto"),xe([]),S(!1)}function gt(T){const te=T.target.files[0];se(te)}function tt(T){T.preventDefault();const te=T.dataTransfer.files[0];te&&(te.type==="text/csv"||te.type==="application/json"||te.name.endsWith(".csv")||te.name.endsWith(".json"))&&se(te)}function Fa(T){T.preventDefault()}async function Ya(){if(K){Ne(!0);try{const T=await is(K);console.log(`File hash (SHA-256): ${T}`);const te=await ni(K);Qs(K,te);const de=Ae==="auto"?En(K.name,te):Ae,ze=await ii(te,de),Ze={name:K.name,size:K.size,type:K.type,hash:T,lastModified:new Date(K.lastModified).toISOString(),detectedFormat:de,recordCount:ze.length};console.log("File security validation passed:",Ze),xe(ze),S(!0)}catch(T){console.error("File validation failed:",T),alert(`Security validation failed: ${T.message}`)}finally{Ne(!1)}}}function Ga(){S(!1),xe([])}async function da(){if(me.length!==0){Ne(!0);try{const T=me.map(de=>({type:de.rawType||de.type.toLowerCase().replace(" ","_"),value:de.value.trim(),name:de.name||"",description:de.description||"",confidence:parseInt(de.confidence)||50})),te=await ut.post("/api/indicators/bulk-import/",{indicators:T});if(te&&te.success){const de=te.created_indicators.map($e=>({...$e,rawType:$e.type,title:$e.name||"",type:$e.type==="ip"?"IP Address":$e.type==="domain"?"Domain":$e.type==="url"?"URL":$e.type==="file_hash"?"File Hash":$e.type==="email"?"Email":$e.type,severity:"Medium",status:"Active",created:$e.created_at?$e.created_at.split("T")[0]:new Date().toISOString().split("T")[0]}));l($e=>[...de,...$e]),Aa();const ze=`Import completed! Added ${te.created_count} new indicators.`,Ze=te.error_count>0?` ${te.error_count} errors occurred.`:"";console.log(`${ze}${Ze}`,te.errors),alert(`${ze}${Ze}`)}else throw new Error("Bulk import failed")}catch(T){console.error("Import failed:",T),alert("Import failed. Please try again.")}finally{Ne(!1)}}}function ni(T){return new Promise((te,de)=>{const ze=new FileReader;ze.onload=Ze=>te(Ze.target.result),ze.onerror=()=>de(new Error("Failed to read file")),ze.readAsText(T)})}async function is(T){return new Promise((te,de)=>{const ze=new FileReader;ze.onload=async Ze=>{try{const $e=Ze.target.result,Yt=await crypto.subtle.digest("SHA-256",$e),wa=Array.from(new Uint8Array(Yt)).map(j=>j.toString(16).padStart(2,"0")).join("");te(wa)}catch($e){de($e)}},ze.onerror=()=>de(new Error("Failed to read file for hashing")),ze.readAsArrayBuffer(T)})}function Qs(T,te){const de=T.name.toLowerCase(),ze=10*1024*1024;if(T.size>ze)throw new Error("File size exceeds 10MB limit");const Ze={csv:{extensions:[".csv"],mimeTypes:["text/csv","application/csv","text/plain"],maxSize:5*1024*1024,contentValidation:Qt=>{const wa=Qt.split(`
`).filter(pe=>pe.trim());if(wa.length<2)return!1;const j=wa[0];return j.includes(",")&&j.split(",").length>=2}},json:{extensions:[".json"],mimeTypes:["application/json","text/json"],maxSize:5*1024*1024,contentValidation:Qt=>{try{const wa=JSON.parse(Qt);return typeof wa=="object"&&wa!==null}catch{return!1}}},txt:{extensions:[".txt"],mimeTypes:["text/plain"],maxSize:2*1024*1024,contentValidation:Qt=>![/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,/<iframe\b[^>]*>/gi,/javascript:/gi,/on\w+\s*=/gi].some(j=>j.test(Qt))}},$e=de.substring(de.lastIndexOf(".")),Yt=Object.values(Ze).find(Qt=>Qt.extensions.includes($e));if(!Yt)throw new Error(`Unsupported file type: ${$e}. Allowed types: CSV, JSON, TXT`);if(!Yt.mimeTypes.includes(T.type)&&T.type!==""&&console.warn(`MIME type mismatch: expected ${Yt.mimeTypes.join("/")}, got ${T.type}`),T.size>Yt.maxSize)throw new Error(`File size exceeds limit for ${$e.substring(1).toUpperCase()} files (${Yt.maxSize/1024/1024}MB)`);if(!Yt.contentValidation(te))throw new Error(`Invalid ${$e.substring(1).toUpperCase()} file format or content`);return!0}function En(T,te){if(T.endsWith(".csv"))return"csv";if(T.endsWith(".json"))try{const de=JSON.parse(te);return de.type==="bundle"&&de.objects?"stix":"json"}catch{return"json"}return"csv"}async function ii(T,te){switch(te){case"csv":return Ra(T);case"json":return Mn(T);case"stix":return Dn(T);default:throw new Error("Unsupported file format")}}function Ra(T){const te=T.trim().split(`
`);if(te.length<2)throw new Error("CSV file must have headers and at least one data row");const de=te[0].split(",").map(Ze=>Ze.replace(/"/g,"").trim().toLowerCase()),ze=[];for(let Ze=1;Ze<te.length;Ze++){const $e=te[Ze].split(",").map(Qt=>Qt.replace(/"/g,"").trim()),Yt={type:ua(de,$e,["type","ioc_type","indicator_type"])||"Unknown",value:ua(de,$e,["value","ioc_value","indicator"])||"",name:ua(de,$e,["name","title","indicator_name"])||"",description:ua(de,$e,["description","desc","details"])||"",severity:ua(de,$e,["severity","priority","threat_level"])||"Medium",source:ua(de,$e,["source","origin","feed"])||"Import",status:ua(de,$e,["status","state"])||"Active"};Yt.value&&ze.push(Yt)}return ze}function Mn(T){const te=JSON.parse(T);if(te.indicators&&Array.isArray(te.indicators))return te.indicators.map(de=>({type:de.type||"Unknown",value:de.value||"",name:de.name||"",description:de.description||"",severity:de.severity||"Medium",source:de.source||"Import",status:de.status||"Active"}));if(Array.isArray(te))return te.map(de=>({type:de.type||"Unknown",value:de.value||"",name:de.name||"",description:de.description||"",severity:de.severity||"Medium",source:de.source||"Import",status:de.status||"Active"}));throw new Error("Invalid JSON format. Expected array or object with indicators property.")}function Dn(T){const te=JSON.parse(T);if(te.type!=="bundle"||!te.objects)throw new Error("Invalid STIX format. Expected bundle with objects.");return te.objects.filter(ze=>ze.type==="indicator").map(ze=>({type:Rn(ze.pattern),value:On(ze.pattern),name:ze.name||"",description:ze.description||"",severity:zi(ze.confidence||50),source:ze.x_crisp_source||"STIX Import",status:ze.x_crisp_status||"Active"}))}function ua(T,te,de){for(const ze of de){const Ze=T.indexOf(ze);if(Ze!==-1&&te[Ze])return te[Ze]}return null}function Rn(T){return T.includes("ipv4-addr")?"IP Address":T.includes("domain-name")?"Domain":T.includes("url")?"URL":T.includes("file:hashes")?"File Hash":T.includes("email-addr")?"Email":"Unknown"}function On(T){const te=T.match(/'([^']+)'/);return te?te[1]:""}function zi(T){return T>=75?"High":T>=45?"Medium":"Low"}function ss(){const T={};if(h.type||(T.type="IoC type is required"),!h.value.trim())T.value="IoC value is required";else{const te=h.value.trim();switch(h.type){case"ip":/^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(te)||(T.value="Invalid IP address format");break;case"domain":/^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$/.test(te)||(T.value="Invalid domain format");break;case"url":try{new URL(te)}catch{T.value="Invalid URL format"}break;case"email":/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(te)||(T.value="Invalid email format");break;case"file_hash":(!/^[a-fA-F0-9]+$/.test(te)||![32,40,64,128].includes(te.length))&&(T.value="Invalid hash format (MD5, SHA1, SHA256, or SHA512)");break}}return T}function ga(T){z(T),ie({type:T.rawType||T.type.toLowerCase().replace(" ","_"),value:T.value,description:T.description||"",confidence:T.confidence||50,threat_feed_id:T.feedId||"",threatFeedMode:"existing"}),Le(""),D(""),re({}),F(!0)}function hn(){F(!1),z(null),ie({type:"",value:"",description:"",confidence:50,threat_feed_id:"",threatFeedMode:"existing"}),Le(""),D(""),re({})}async function rs(T){if(T.preventDefault(),!!_e){ue(!0),re({});try{let te=G.threat_feed_id;if(G.threatFeedMode==="new"&&je.trim())try{const Ze={name:je.trim(),description:ne.trim()||"",is_external:!1,is_active:!0},$e=await ut.post("/api/threat-feeds/",Ze);$e&&$e.id&&(te=$e.id,U(Yt=>[...Yt,$e]))}catch(Ze){console.error("Error creating new threat feed:",Ze),re({submit:"Failed to create new threat feed. Please try again."});return}const de={type:G.type,value:G.value.trim(),description:G.description||"",confidence:parseInt(G.confidence)||50,threat_feed_id:te},ze=await ut.put(`/api/indicators/${_e.id}/update/`,de);if(ze){const Ze={...ze,rawType:ze.type,type:ze.type==="ip"?"IP Address":ze.type==="domain"?"Domain":ze.type==="url"?"URL":ze.type==="file_hash"?"File Hash":ze.type==="email"?"Email":ze.type,severity:_e.severity,status:_e.status,created:ze.created_at?ze.created_at.split("T")[0]:_e.created};l($e=>$e.map(Yt=>Yt.id===_e.id?Ze:Yt)),hn(),alert("Indicator updated successfully!")}else throw new Error("Failed to update indicator")}catch(te){console.error("Error updating indicator:",te),re({submit:"Failed to update indicator. Please try again."})}finally{ue(!1)}}}function an(T){Me(T),at({organisations:[],anonymizationLevel:"medium",shareMethod:"taxii"}),J(!0)}function Un(){J(!1),Me(null),at({organisations:[],anonymizationLevel:"medium",shareMethod:"taxii"}),Tt(""),Zt(!1),De(-1)}function Ln(T){at(te=>({...te,organisations:[...te.organisations,T]})),Tt(""),Zt(!1),De(-1)}function si(T){at(te=>({...te,institutions:te.institutions.filter(de=>de!==T)}))}async function Gt(T){if(T.preventDefault(),!be||Ve.organisations.length===0){alert("Please select at least one organisation to share with.");return}ta(!0);try{const te={institutions:Ve.organisations,anonymization_level:Ve.anonymizationLevel,share_method:Ve.shareMethod},de=await ut.post(`/api/indicators/${be.id}/share/`,te);if(de&&de.success)Un(),alert(`Indicator shared with ${de.shared_with} organisation(s) successfully!`);else throw new Error("Failed to share indicator")}catch(te){console.error("Error sharing indicator:",te),alert("Failed to share indicator. Please try again.")}finally{ta(!1)}}async function ki(T){T.preventDefault();const te=ss();if(Object.keys(te).length>0){b(te);return}C(!0),b({});try{const de={type:h.type,value:h.value.trim(),description:h.description||"",confidence:parseInt(h.confidence)||50},ze=await ut.post("/api/indicators/",de);if(ze){const Ze={...ze,rawType:ze.type,title:ze.name||"",type:ze.type==="ip"?"IP Address":ze.type==="domain"?"Domain":ze.type==="url"?"URL":ze.type==="file_hash"?"File Hash":ze.type==="email"?"Email":ze.type,severity:h.severity||"Medium",status:"Active",created:ze.created_at?ze.created_at.split("T")[0]:new Date().toISOString().split("T")[0]};l($e=>[Ze,...$e]),qt(),console.log("IoC added successfully:",ze),alert("IoC added successfully!")}else throw new Error("Failed to create indicator")}catch(de){console.error("Error adding IoC:",de),b({submit:"Failed to add IoC. Please try again."})}finally{C(!1)}}}function N2({active:n}){var Yt,Qt,wa;if(!n)return null;const[s,l]=N.useState([]),[o,d]=N.useState([]),[f,m]=N.useState(null),[p,g]=N.useState(!1),[h,x]=N.useState(!1),[v,b]=N.useState(!1),[_,C]=N.useState("overview"),[E,A]=N.useState(null),[L,q]=N.useState(null),[P,M]=N.useState(null),[X,Q]=N.useState(!1),[K,se]=N.useState("created_at"),[Ae,we]=N.useState("desc"),[ge,Ne]=N.useState(1),[me,xe]=N.useState(20),[He,S]=N.useState(0),[H,F]=N.useState(0),[_e,z]=N.useState(!1),[G,ie]=N.useState(!1),[oe,re]=N.useState(!1),[Te,ue]=N.useState(null),[je,Le]=N.useState({search:"",tactics:[],techniques:[],severity_levels:[],date_from:"",date_to:"",threat_feed_ids:[],anonymized_only:"",has_subtechniques:""}),[ne,D]=N.useState(0),[I,J]=N.useState(!1),[be,Me]=N.useState(null),[Ve,at]=N.useState(!1),[Ke,ta]=N.useState(!1),[_t,Tt]=N.useState({}),[Ft,Zt]=N.useState([]),[ae,De]=N.useState(""),[Fe,ke]=N.useState(!1),[Be,vt]=N.useState(""),[ft,V]=N.useState(!1),[Re,U]=N.useState("json"),[fe,ee]=N.useState({tactic:"",technique_id:"",feed_id:"",include_anonymized:!0,include_original:!1,created_after:"",created_before:"",limit:1e3,fields:""}),[Ce,Xe]=N.useState(!1),[et,ve]=N.useState(""),[Ot,St]=N.useState(!1),[Ee,R]=N.useState(null),[ce,Ie]=N.useState(!1),[rt,wt]=N.useState(""),[ht,Ct]=N.useState(""),[Bt,mt]=N.useState(!1),[Oe,lt]=N.useState(null),[Ut,qt]=N.useState(!1),[Ia,en]=N.useState(""),Ht=N.useRef(null);N.useEffect(()=>{n&&(sa(),Mn(),Aa(),fn(),$a())},[n]);const fn=async()=>{try{const j=await ut.get("/api/threat-feeds/");j&&j.results?Zt(j.results):(console.log("No threat feeds found or invalid response:",j),Zt([]))}catch(j){console.error("Error fetching available feeds:",j),Zt([])}},$a=async()=>{Q(!0);try{const j=ut.get("/api/ttps/feed-comparison/?days=30").catch(nt=>(console.warn("Feed comparison endpoint not available:",nt),null)),pe=ut.get("/api/ttps/technique-frequencies/?days=30").catch(nt=>(console.warn("Technique frequencies endpoint not available:",nt),null)),Se=ut.get("/api/ttps/seasonal-patterns/?days=180").catch(nt=>(console.warn("Seasonal patterns endpoint not available:",nt),null)),[Ue,Je,Ge]=await Promise.all([j,pe,Se]);Ue&&Ue.success&&A(Ue),Je&&Je.success&&q(Je),Ge&&Ge.success&&M(Ge)}catch(j){console.error("Error fetching aggregation data:",j)}Q(!1)},Da=async()=>{if(!ae){alert("Please select a threat feed to analyze");return}ke(!0),vt("Loading TTPs from feed...");try{const j=Ft.find(Se=>Se.id==ae),pe=j?j.name:"Selected Feed";await tn(ae,pe)}catch(j){console.error("Error loading feed TTPs:",j),vt(`❌ Failed to load TTPs: ${j.message||"Unknown error"}`),setTimeout(()=>{vt("")},1e4)}finally{ke(!1)}},tn=async(j,pe)=>{let Se=[],Ue=1,Je=!0;const Ge=100;for(;Je;)try{const nt=await ut.get(`/api/threat-feeds/${j}/ttps/?page=${Ue}&page_size=${Ge}`);nt&&nt.results?(Se=[...Se,...nt.results],vt(`Loading TTPs from "${pe}"... (${Se.length} loaded)`),Je=nt.next!==null,Ue++):Je=!1}catch(nt){throw console.error(`Error loading page ${Ue} of TTPs:`,nt),Je=!1,nt}l(Se),S(Se.length),vt(`✅ Loaded ${Se.length} TTPs from "${pe}"`),Mn(),$a(),setTimeout(()=>{vt("")},5e3)},sa=async(j=null,pe=null,Se=null,Ue=null,Je=null)=>{g(!0);try{const Ge=j||K,nt=pe||Ae,xa=Se||ge,Na=Ue||me,xt=Je||je,Pt=new URLSearchParams;Pt.append("sort_by",Ge),Pt.append("sort_order",nt),Pt.append("page",xa.toString()),Pt.append("page_size",Na.toString()),xt.search&&xt.search.trim()&&Pt.append("search",xt.search.trim()),xt.tactics&&xt.tactics.length>0&&Pt.append("tactics",xt.tactics.join(",")),xt.techniques&&xt.techniques.length>0&&Pt.append("techniques",xt.techniques.join(",")),xt.severity_levels&&xt.severity_levels.length>0&&Pt.append("severity_levels",xt.severity_levels.join(",")),xt.date_from&&xt.date_from.trim()&&Pt.append("created_after",xt.date_from.trim()),xt.date_to&&xt.date_to.trim()&&Pt.append("created_before",xt.date_to.trim()),xt.threat_feed_ids&&xt.threat_feed_ids.length>0&&Pt.append("threat_feed_ids",xt.threat_feed_ids.join(",")),xt.anonymized_only&&xt.anonymized_only!==""&&Pt.append("anonymized_only",xt.anonymized_only),xt.has_subtechniques&&xt.has_subtechniques!==""&&Pt.append("has_subtechniques",xt.has_subtechniques);const _a=await ut.get(`/api/ttps/?${Pt.toString()}`);_a&&_a.success?(l(_a.results||[]),S(_a.count||0),F(_a.num_pages||0),z(_a.has_next||!1),ie(_a.has_previous||!1)):(l([]),S(0),F(0),z(!1),ie(!1))}catch(Ge){console.error("Error fetching TTP data:",Ge),l([]),S(0),F(0),z(!1),ie(!1)}g(!1)},Aa=async()=>{try{const j=await ut.get("/api/ttps/filter-options/");j&&j.success&&ue(j.options)}catch(j){console.error("Error fetching filter options:",j)}},gt=j=>{let pe="asc";K===j?pe=Ae==="asc"?"desc":"asc":pe=j==="created_at"||j==="updated_at"?"desc":"asc",se(j),we(pe),Ne(1),sa(j,pe,1,me,je)},tt=j=>{if(K!==j)return t.jsx("i",{className:"fas fa-sort",style:{color:"#ccc",marginLeft:"5px"}});const pe=Ae==="asc"?"fa-sort-up":"fa-sort-down";return t.jsx("i",{className:`fas ${pe}`,style:{color:"#0056b3",marginLeft:"5px"}})},Fa=j=>{j>=1&&j<=H&&j!==ge&&(Ne(j),sa(K,Ae,j,me,je))},Ya=j=>{xe(j),Ne(1),sa(K,Ae,1,j,je)},Ga=()=>{const j=[];if(H<=5)for(let Se=1;Se<=H;Se++)j.push(Se);else{const Se=Math.max(1,ge-2),Ue=Math.min(H,ge+2);Se>1&&(j.push(1),Se>2&&j.push("..."));for(let Je=Se;Je<=Ue;Je++)j.push(Je);Ue<H&&(Ue<H-1&&j.push("..."),j.push(H))}return j},da=(j,pe)=>{const Se={...je,[j]:pe};Le(Se),Ne(1);const Ue=En(Se);D(Ue),j==="search"?ni(K,Ae,1,me,Se):sa(K,Ae,1,me,Se)},ni=N.useRef(is((j,pe,Se,Ue,Je)=>{sa(j,pe,Se,Ue,Je)},500)).current;function is(j,pe){let Se;return function(...Je){const Ge=()=>{clearTimeout(Se),j(...Je)};clearTimeout(Se),Se=setTimeout(Ge,pe)}}const Qs=(j,pe,Se)=>{const Ue=je[j]||[];let Je;Se?Je=[...Ue,pe]:Je=Ue.filter(Ge=>Ge!==pe),da(j,Je)},En=j=>{let pe=0;return j.search&&j.search.trim()&&pe++,j.tactics&&j.tactics.length>0&&pe++,j.techniques&&j.techniques.length>0&&pe++,j.severity_levels&&j.severity_levels.length>0&&pe++,j.date_from&&j.date_from.trim()&&pe++,j.date_to&&j.date_to.trim()&&pe++,j.threat_feed_ids&&j.threat_feed_ids.length>0&&pe++,j.anonymized_only&&j.anonymized_only!==""&&pe++,j.has_subtechniques&&j.has_subtechniques!==""&&pe++,pe},ii=()=>{const j={search:"",tactics:[],techniques:[],severity_levels:[],date_from:"",date_to:"",threat_feed_ids:[],anonymized_only:"",has_subtechniques:""};Le(j),D(0),Ne(1),sa(K,Ae,1,me,j)},Ra=async()=>{x(!0);try{const j=await ut.get("/api/ttps/trends/?days=120&granularity=month&group_by=tactic");j&&j.series?d(j.series):d([])}catch(j){console.error("Error fetching TTP trends data:",j),d([])}x(!1)},Mn=async()=>{b(!0);try{const j=await ut.get("/api/ttps/mitre-matrix/");j&&j.success?m(j):m(null)}catch(j){console.error("Error fetching MITRE matrix data:",j),m(null)}b(!1)},Dn=j=>{C(j)},ua=async(j,pe=null)=>{wt(j),Ct(pe||""),Ie(!0),St(!0);try{let Se=`/api/ttps/matrix-cell-details/?tactic=${j}`;pe&&(Se+=`&technique_id=${pe}`),Se+="&include_related=true&page_size=50";const Ue=await ut.get(Se);Ue&&Ue.success?R(Ue):R(null)}catch(Se){console.error("Error fetching matrix cell details:",Se),R(null)}Ie(!1)},Rn=async j=>{en(j),qt(!0),mt(!0);try{const pe=`/api/ttps/technique-details/${j}/`,Se=await ut.get(pe);Se&&Se.success?lt(Se):lt(null)}catch(pe){console.error("Error fetching technique details:",pe),lt(null)}qt(!1)},On=()=>{St(!1),R(null),wt(""),Ct("")},zi=()=>{mt(!1),lt(null),en("")},ss=()=>{Mn()},ga=async j=>{var pe;J(!0),at(!0),ta(!1);try{const Se=await ut.get(`/api/ttps/${j}/`);Se&&Se.success?(Me(Se.ttp),Tt({name:Se.ttp.name||"",description:Se.ttp.description||"",mitre_technique_id:Se.ttp.mitre_technique_id||"",mitre_tactic:Se.ttp.mitre_tactic||"",mitre_subtechnique:Se.ttp.mitre_subtechnique||"",threat_feed_id:((pe=Se.ttp.threat_feed)==null?void 0:pe.id)||""})):(console.error("Failed to fetch TTP details"),Me(null))}catch(Se){console.error("Error fetching TTP details:",Se),Me(null)}at(!1)},hn=()=>{J(!1),Me(null),ta(!1),Tt({})},rs=()=>{ta(!Ke)},an=(j,pe)=>{Tt(Se=>({...Se,[j]:pe}))},Un=async()=>{if(be)try{const j=await ut.put(`/api/ttps/${be.id}/`,_t);j&&j.success?(l(pe=>pe.map(Se=>Se.id===be.id?{...Se,..._t}:Se)),Me({...be,..._t}),ta(!1),alert("TTP updated successfully"),Ra()):alert("Failed to update TTP")}catch(j){console.error("Error updating TTP:",j),alert("Error updating TTP: "+(j.message||"Unknown error"))}},Ln=()=>{V(!0),ve("")},si=()=>{V(!1),ve("")},Gt=(j,pe)=>{ee(Se=>({...Se,[j]:pe}))},ki=(j,pe)=>{const Se=window.URL.createObjectURL(j),Ue=document.createElement("a");Ue.href=Se,Ue.download=pe,document.body.appendChild(Ue),Ue.click(),document.body.removeChild(Ue),window.URL.revokeObjectURL(Se)},T=async()=>{Xe(!0),ve("");try{const j=new URLSearchParams;j.append("format",Re),fe.tactic&&j.append("tactic",fe.tactic),fe.technique_id&&j.append("technique_id",fe.technique_id),fe.feed_id&&j.append("feed_id",fe.feed_id),fe.created_after&&j.append("created_after",fe.created_after),fe.created_before&&j.append("created_before",fe.created_before),fe.fields&&j.append("fields",fe.fields),j.append("include_anonymized",fe.include_anonymized.toString()),j.append("include_original",fe.include_original.toString()),j.append("limit",fe.limit.toString());const pe=await fetch(`/api/ttps/export/?${j.toString()}`,{method:"GET",headers:{Accept:Re==="csv"?"text/csv":Re==="stix"?"application/stix+json":"application/json"}});if(!pe.ok)throw new Error(`Export failed: ${pe.status} ${pe.statusText}`);const Se=await pe.blob(),Ue=pe.headers.get("Content-Disposition");let Je=`ttps_export_${new Date().toISOString().slice(0,19).replace(/:/g,"-")}.${Re}`;if(Ue){const Ge=Ue.match(/filename="([^"]+)"/);Ge&&(Je=Ge[1])}ki(Se,Je),si(),alert(`Export completed successfully! Downloaded: ${Je}`)}catch(j){console.error("Export failed:",j),ve("Export failed: "+(j.message||"Unknown error"))}Xe(!1)},te=()=>{if(!f||!f.matrix)return null;const j=[{code:"initial-access",name:"Initial Access"},{code:"execution",name:"Execution"},{code:"persistence",name:"Persistence"},{code:"privilege-escalation",name:"Privilege Escalation"},{code:"defense-evasion",name:"Defense Evasion"},{code:"credential-access",name:"Credential Access"},{code:"discovery",name:"Discovery"},{code:"lateral-movement",name:"Lateral Movement"},{code:"collection",name:"Collection"},{code:"exfiltration",name:"Exfiltration"},{code:"impact",name:"Impact"}];return t.jsx("thead",{children:t.jsx("tr",{children:j.map(pe=>{const Se=f.matrix[pe.code],Ue=Se?Se.technique_count:0;return t.jsxs("th",{title:`${Ue} techniques in ${pe.name} - Click to view details`,onClick:()=>Ue>0&&ua(pe.code),style:{cursor:Ue>0?"pointer":"default",backgroundColor:Ue>0?"#f8f9fa":"transparent",transition:"background-color 0.2s ease"},onMouseEnter:Je=>{Ue>0&&(Je.target.style.backgroundColor="#e9ecef")},onMouseLeave:Je=>{Ue>0&&(Je.target.style.backgroundColor="#f8f9fa")},children:[pe.name,t.jsxs("div",{className:"tactic-count",children:["(",Ue,")"]})]},pe.code)})})})},de=()=>{if(!f||!f.matrix)return null;Object.values(f.matrix);const j=["initial-access","execution","persistence","privilege-escalation","defense-evasion","credential-access","discovery","lateral-movement","collection","exfiltration","impact"],pe=5,Se=[];for(let Ue=0;Ue<pe;Ue++){const Je=[];j.forEach(Ge=>{const nt=f.matrix[Ge];if(nt&&nt.techniques&&nt.techniques.length>Ue){const xa=nt.techniques[Ue];Je.push({technique:xa,hasData:!0,isActive:nt.technique_count>0})}else Je.push({technique:null,hasData:!1,isActive:!1})}),Je.some(Ge=>Ge.hasData)&&Se.push(Je)}return t.jsx("tbody",{children:Se.map((Ue,Je)=>t.jsx("tr",{children:Ue.map((Ge,nt)=>{const xa=j[nt];return t.jsx("td",{className:`matrix-cell ${Ge.isActive?"active":""} ${Ge.technique?"clickable":""}`,title:Ge.technique?`${Ge.technique.name} (${Ge.technique.technique_id}) - Click to view details`:"No techniques",onClick:()=>{Ge.technique?Rn(Ge.technique.technique_id):Ge.isActive&&xa&&ua(xa)},style:{cursor:Ge.technique||Ge.isActive?"pointer":"default",transition:"all 0.2s ease",position:"relative"},onMouseEnter:Na=>{(Ge.technique||Ge.isActive)&&(Na.target.style.transform="scale(1.02)",Na.target.style.boxShadow="0 2px 8px rgba(0,0,0,0.1)",Na.target.style.zIndex="1")},onMouseLeave:Na=>{(Ge.technique||Ge.isActive)&&(Na.target.style.transform="scale(1)",Na.target.style.boxShadow="none",Na.target.style.zIndex="auto")},children:Ge.technique?t.jsxs(t.Fragment,{children:[t.jsx("div",{className:"technique-name",children:Ge.technique.name.length>20?Ge.technique.name.substring(0,20)+"...":Ge.technique.name}),Ge.technique.technique_id&&t.jsx("div",{className:"technique-id",children:Ge.technique.technique_id})]}):t.jsx("div",{className:"empty-cell",children:Ge.isActive?"🔍":"-"})},nt)})},Je))})},ze=j=>{const pe=new Map;return j.forEach(Se=>{const Ue=Se.group_name?Se.group_name.toLowerCase().replace(/\s+/g,"-"):"unknown";Se.data_points.forEach(Je=>{const Ge=Je.date;pe.has(Ge)||pe.set(Ge,{date:Ge,"initial-access":0,execution:0,persistence:0,"defense-evasion":0,impact:0,"privilege-escalation":0,discovery:0,"lateral-movement":0,collection:0,"command-and-control":0,exfiltration:0});const nt=pe.get(Ge);nt.hasOwnProperty(Ue)&&(nt[Ue]=Je.count||0)})}),Array.from(pe.values()).sort((Se,Ue)=>new Date(Se.date)-new Date(Ue.date))},Ze=async j=>{if(confirm("Are you sure you want to delete this TTP? This action cannot be undone."))try{const pe=await ut.delete(`/api/ttps/${j}/`);pe&&pe.success?(l(Se=>Se.filter(Ue=>Ue.id!==j)),alert("TTP deleted successfully"),Ra()):alert("Failed to delete TTP")}catch(pe){console.error("Error deleting TTP:",pe),alert("Error deleting TTP: "+(pe.message||"Unknown error"))}};N.useEffect(()=>{n&&Ht.current&&o.length>0&&$e()},[n,o]);const $e=()=>{try{if(Ht.current&&oa(Ht.current).selectAll("*").remove(),!o||o.length===0||!Ht.current)return;const j=ze(o);if(!j||j.length===0){console.warn("No chart data available after transformation");return}const pe=Ht.current.clientWidth,Se=300,Ue={top:30,right:120,bottom:40,left:50},Je=pe-Ue.left-Ue.right,Ge=Se-Ue.top-Ue.bottom,nt=oa(Ht.current).append("svg").attr("width",pe).attr("height",Se).append("g").attr("transform",`translate(${Ue.left},${Ue.top})`),xa=JN().domain(j.map(It=>It.date)).range([0,Je]).padding(.5),Na=ll().domain([0,Uo(j,It=>Math.max(...Object.keys(Pt).map(ya=>It[ya]||0)))*1.1]).range([Ge,0]),xt=lc().x(It=>xa(It.date)).y(It=>Na(It.value)).curve(r0),Pt={"initial-access":"#0056b3",execution:"#00a0e9",persistence:"#38a169","defense-evasion":"#e53e3e",impact:"#f6ad55","privilege-escalation":"#805ad5",discovery:"#ed8936","lateral-movement":"#38b2ac",collection:"#d53f8c","command-and-control":"#319795",exfiltration:"#dd6b20"},_a=Object.keys(Pt).filter(It=>j.some(ya=>ya[It]>0)),mn={"initial-access":"Initial Access",execution:"Execution",persistence:"Persistence","defense-evasion":"Defense Evasion",impact:"Impact","privilege-escalation":"Privilege Escalation",discovery:"Discovery","lateral-movement":"Lateral Movement",collection:"Collection","command-and-control":"Command and Control",exfiltration:"Exfiltration"};_a.forEach(It=>{const ya=j.map(Va=>({date:Va.date,value:Va[It]}));nt.append("path").datum(ya).attr("fill","none").attr("stroke",Pt[It]).attr("stroke-width",2).attr("d",xt),nt.selectAll(`.dot-${It}`).data(ya).enter().append("circle").attr("class",`dot-${It}`).attr("cx",Va=>xa(Va.date)).attr("cy",Va=>Na(Va.value)).attr("r",4).attr("fill",Pt[It])}),nt.append("g").attr("transform",`translate(0,${Ge})`).call(tl(xa).tickFormat(It=>It)),nt.append("g").call(al(Na)),nt.append("text").attr("x",Je/2).attr("y",-10).attr("text-anchor","middle").style("font-size","16px").style("font-weight","600").style("fill","#2d3748").text("TTP Trends Over Time");const Js=nt.append("g").attr("transform",`translate(${Je+10}, 0)`);_a.forEach((It,ya)=>{const Va=Js.append("g").attr("transform",`translate(0, ${ya*20})`);Va.append("rect").attr("width",10).attr("height",10).attr("fill",Pt[It]),Va.append("text").attr("x",15).attr("y",10).attr("text-anchor","start").style("font-size","12px").text(mn[It])})}catch(j){console.error("Error creating TTP trends chart:",j),Ht.current&&(oa(Ht.current).selectAll("*").remove(),oa(Ht.current).append("div").style("text-align","center").style("color","#e53e3e").style("padding","20px").text("Error loading chart data. Please try refreshing."))}};return t.jsxs("section",{id:"ttp-analysis",className:`page-section ${n?"active":""}`,children:[t.jsxs("div",{className:"page-header",children:[t.jsxs("div",{children:[t.jsx("h1",{className:"page-title",children:"TTP Analysis"}),t.jsx("p",{className:"page-subtitle",children:"Track and analyze tactics, techniques, and procedures from threat intelligence feeds"})]}),t.jsxs("div",{className:"action-buttons",children:[t.jsxs("div",{className:"feed-consumption-controls",children:[t.jsxs("div",{className:"feed-selection-wrapper",children:[t.jsxs("select",{value:ae,onChange:j=>De(j.target.value),className:"form-control feed-selector",disabled:Fe,children:[t.jsx("option",{value:"",children:"Select Threat Feed to Analyze"}),Ft.length===0?t.jsx("option",{disabled:!0,children:"No threat feeds available"}):Ft.map(j=>t.jsxs("option",{value:j.id,children:[j.name," - ",j.is_external?"External TAXII":"Internal",j.is_active?" ✓":" (Inactive)",j.description?` - ${j.description}`:""]},j.id))]}),ae&&t.jsx("div",{className:"consumption-options",children:t.jsxs("small",{className:"consumption-info",children:[t.jsx("i",{className:"fas fa-info-circle"}),"Will show TTPs from this feed"]})})]}),t.jsx("button",{className:"btn btn-primary consume-btn",onClick:Da,disabled:!ae||Fe,title:ae?"Load TTPs from selected feed":"Select a feed first",children:Fe?t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Loading..."]}):t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-download"})," Load Feed TTPs"]})})]}),t.jsxs("button",{className:"btn btn-outline",onClick:Ln,children:[t.jsx("i",{className:"fas fa-upload"})," Export Analysis"]})]})]}),Be&&t.jsxs("div",{className:`alert ${Be.includes("failed")?"alert-error":"alert-success"}`,children:[t.jsx("i",{className:`fas ${Be.includes("failed")?"fa-exclamation-triangle":"fa-check-circle"}`}),Be]}),t.jsxs("div",{className:"tabs",children:[t.jsx("div",{className:`tab ${_==="overview"?"active":""}`,onClick:()=>Dn("overview"),children:"Feed Overview"}),t.jsx("div",{className:`tab ${_==="matrix"?"active":""}`,onClick:()=>Dn("matrix"),children:"MITRE ATT&CK Matrix"}),t.jsx("div",{className:`tab ${_==="list"?"active":""}`,onClick:()=>Dn("list"),children:"TTP Intelligence"}),t.jsx("div",{className:`tab ${_==="trends"?"active":""}`,onClick:()=>Dn("trends"),children:"Trends & Patterns"})]}),_==="overview"&&t.jsxs("div",{className:"feed-analysis-overview",children:[t.jsxs("div",{className:"overview-cards",children:[t.jsxs("div",{className:"card",children:[t.jsxs("div",{className:"card-header",children:[t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-chart-bar card-icon"}),"Feed Comparison Statistics"]}),t.jsxs("button",{className:"btn btn-outline btn-sm",onClick:$a,disabled:X,children:[t.jsx("i",{className:`fas ${X?"fa-spinner fa-spin":"fa-sync-alt"}`})," Refresh"]})]}),t.jsx("div",{className:"card-content",children:X?t.jsxs("div",{className:"loading-state",children:[t.jsx("i",{className:"fas fa-spinner fa-spin"}),t.jsx("p",{children:"Loading feed comparison data..."})]}):E?t.jsx("div",{className:"feed-comparison-grid",children:E.feed_statistics&&E.feed_statistics.map((j,pe)=>t.jsxs("div",{className:"feed-stat-card",children:[t.jsx("div",{className:"feed-name",children:j.threat_feed__name}),t.jsxs("div",{className:"feed-stats",children:[t.jsxs("div",{className:"stat-item",children:[t.jsx("span",{className:"stat-value",children:j.ttp_count}),t.jsx("span",{className:"stat-label",children:"TTPs"})]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("span",{className:"stat-value",children:j.unique_techniques}),t.jsx("span",{className:"stat-label",children:"Unique Techniques"})]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("span",{className:"stat-value",children:j.avg_techniques_per_day}),t.jsx("span",{className:"stat-label",children:"Avg/Day"})]})]}),t.jsx("div",{className:`feed-type ${j.threat_feed__is_external?"external":"internal"}`,children:j.threat_feed__is_external?"External Feed":"Internal Feed"})]},pe))}):t.jsxs("div",{className:"empty-state",children:[t.jsx("i",{className:"fas fa-chart-bar"}),t.jsx("p",{children:"No feed comparison data available"}),t.jsx("p",{className:"text-muted",children:"Consume threat feeds to see comparison statistics"})]})})]}),t.jsxs("div",{className:"card",children:[t.jsx("div",{className:"card-header",children:t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-fire card-icon"}),"Top Techniques"]})}),t.jsx("div",{className:"card-content",children:L&&L.techniques?t.jsx("div",{className:"technique-frequency-list",children:Object.entries(L.techniques).sort(([,j],[,pe])=>pe.count-j.count).slice(0,10).map(([j,pe],Se)=>t.jsxs("div",{className:"frequency-item",children:[t.jsxs("div",{className:"technique-rank",children:["#",pe.rank]}),t.jsxs("div",{className:"technique-details",children:[t.jsx("div",{className:"technique-id",children:j}),t.jsxs("div",{className:"technique-stats",children:[t.jsxs("span",{className:"count",children:[pe.count," occurrences"]}),t.jsxs("span",{className:"percentage",children:["(",pe.percentage,"%)"]})]})]}),t.jsx("div",{className:"frequency-bar",children:t.jsx("div",{className:"frequency-fill",style:{width:`${Math.min(pe.percentage*2,100)}%`}})})]},j))}):t.jsxs("div",{className:"empty-state",children:[t.jsx("i",{className:"fas fa-fire"}),t.jsx("p",{children:"No technique frequency data available"})]})})]})]}),t.jsxs("div",{className:"card",children:[t.jsx("div",{className:"card-header",children:t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-calendar-alt card-icon"}),"Seasonal Patterns"]})}),t.jsx("div",{className:"card-content",children:P&&P.statistics?t.jsxs("div",{className:"seasonal-analysis",children:[t.jsxs("div",{className:"seasonal-stats",children:[t.jsxs("div",{className:"stat-card",children:[t.jsx("div",{className:"stat-value",children:P.statistics.seasonality_strength}),t.jsx("div",{className:"stat-label",children:"Seasonality Strength"})]}),t.jsxs("div",{className:"stat-card",children:[t.jsx("div",{className:"stat-value",children:P.statistics.peak_period.label}),t.jsx("div",{className:"stat-label",children:"Peak Period"})]}),t.jsxs("div",{className:"stat-card",children:[t.jsx("div",{className:"stat-value",children:P.statistics.valley_period.label}),t.jsx("div",{className:"stat-label",children:"Valley Period"})]})]}),t.jsx("div",{className:"seasonal-interpretation",children:t.jsx("p",{children:P.interpretation})})]}):t.jsxs("div",{className:"empty-state",children:[t.jsx("i",{className:"fas fa-calendar-alt"}),t.jsx("p",{children:"No seasonal pattern data available"})]})})]})]}),_==="matrix"&&t.jsxs(t.Fragment,{children:[t.jsxs("div",{className:"card",children:[t.jsxs("div",{className:"card-header",children:[t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-sitemap card-icon"})," MITRE ATT&CK Enterprise Matrix"]}),t.jsxs("div",{className:"card-actions",children:[t.jsxs("button",{className:"btn btn-outline btn-sm",onClick:ss,disabled:v,title:"Refresh matrix data",children:[t.jsx("i",{className:`fas ${v?"fa-spinner fa-spin":"fa-sync-alt"}`})," Refresh"]}),t.jsxs("button",{className:"btn btn-outline btn-sm",children:[t.jsx("i",{className:"fas fa-filter"})," Filter"]})]})]}),t.jsx("div",{className:"card-content",children:t.jsx("div",{className:"matrix-container",children:v?t.jsxs("div",{style:{textAlign:"center",padding:"4rem"},children:[t.jsx("i",{className:"fas fa-spinner fa-spin",style:{fontSize:"2rem",color:"#0056b3"}}),t.jsx("p",{style:{marginTop:"1rem",color:"#666"},children:"Loading MITRE ATT&CK Matrix..."})]}):f?t.jsxs(t.Fragment,{children:[t.jsxs("table",{className:"mitre-matrix",children:[te(),de()]}),f.statistics&&t.jsx("div",{className:"matrix-stats",style:{marginTop:"1rem",padding:"1rem",backgroundColor:"#f8f9fa",borderRadius:"8px"},children:t.jsxs("div",{style:{display:"grid",gridTemplateColumns:"repeat(auto-fit, minmax(200px, 1fr))",gap:"1rem"},children:[t.jsxs("div",{children:[t.jsx("strong",{children:"Total Techniques:"})," ",f.total_techniques]}),t.jsxs("div",{children:[t.jsx("strong",{children:"Active Tactics:"})," ",f.statistics.tactics_with_techniques]}),t.jsxs("div",{children:[t.jsx("strong",{children:"Avg per Tactic:"})," ",f.statistics.average_techniques_per_tactic]}),f.statistics.most_common_tactic&&t.jsxs("div",{children:[t.jsx("strong",{children:"Top Tactic:"})," ",(Yt=f.matrix[f.statistics.most_common_tactic])==null?void 0:Yt.tactic_name]})]})})]}):t.jsxs("div",{style:{textAlign:"center",padding:"4rem"},children:[t.jsx("i",{className:"fas fa-sitemap",style:{fontSize:"3rem",color:"#ccc"}}),t.jsx("p",{style:{marginTop:"1rem",color:"#666"},children:"No MITRE ATT&CK data available"}),t.jsx("p",{style:{color:"#888",fontSize:"0.9rem"},children:"Matrix will populate as TTP data becomes available"})]})})})]}),t.jsxs("div",{className:"card mt-4",children:[t.jsxs("div",{className:"card-header",children:[t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-chart-line card-icon"})," TTP Trends"]}),t.jsx("div",{className:"card-actions",children:t.jsxs("button",{className:"btn btn-outline btn-sm",children:[t.jsx("i",{className:"fas fa-calendar-alt"})," Last 90 Days"]})})]}),t.jsx("div",{className:"card-content",children:t.jsx("div",{className:"chart-container",ref:Ht,children:h?t.jsxs("div",{style:{textAlign:"center",padding:"4rem"},children:[t.jsx("i",{className:"fas fa-spinner fa-spin",style:{fontSize:"2rem",color:"#0056b3"}}),t.jsx("p",{style:{marginTop:"1rem",color:"#666"},children:"Loading TTP trends data..."})]}):o.length===0?t.jsxs("div",{style:{textAlign:"center",padding:"4rem"},children:[t.jsx("i",{className:"fas fa-chart-line",style:{fontSize:"2rem",color:"#ccc"}}),t.jsx("p",{style:{marginTop:"1rem",color:"#666"},children:"No TTP trends data available"}),t.jsx("p",{style:{color:"#888",fontSize:"0.9rem"},children:"TTP data will appear here as it becomes available"})]}):null})})]})]}),_==="list"&&t.jsxs("div",{className:"card",children:[t.jsxs("div",{className:"card-header",children:[t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-shield-alt card-icon"})," TTP Intelligence from Threat Feeds"]}),t.jsxs("div",{className:"card-actions",children:[t.jsxs("button",{className:"btn btn-outline btn-sm",onClick:()=>re(!oe),children:[t.jsx("i",{className:"fas fa-filter"})," Filter",ne>0&&t.jsx("span",{className:"filter-count",children:ne})]}),t.jsxs("button",{className:"btn btn-outline btn-sm",onClick:Ln,children:[t.jsx("i",{className:"fas fa-download"})," Export"]})]})]}),t.jsx("div",{className:"intelligence-summary",style:{padding:"1rem",backgroundColor:"#f8f9fa",borderBottom:"1px solid #dee2e6"},children:t.jsxs("div",{className:"summary-stats",children:[t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-database"}),t.jsxs("span",{children:[He," TTPs from threat intelligence feeds"]})]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-rss"}),t.jsxs("span",{children:[Ft.length," connected threat feeds"]})]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-shield-alt"}),t.jsx("span",{children:"Automatically mapped to MITRE ATT&CK"})]})]})}),t.jsx("div",{className:"card-content",children:t.jsxs("table",{className:"data-table",children:[t.jsx("thead",{children:t.jsxs("tr",{children:[t.jsxs("th",{onClick:()=>gt("id"),style:{cursor:"pointer"},children:["ID ",tt("id")]}),t.jsxs("th",{onClick:()=>gt("name"),style:{cursor:"pointer"},children:["TTP Name ",tt("name")]}),t.jsxs("th",{onClick:()=>gt("mitre_technique_id"),style:{cursor:"pointer"},children:["MITRE Technique ",tt("mitre_technique_id")]}),t.jsxs("th",{onClick:()=>gt("mitre_tactic"),style:{cursor:"pointer"},children:["Tactic ",tt("mitre_tactic")]}),t.jsx("th",{children:"Source Feed"}),t.jsx("th",{children:"Intelligence Status"}),t.jsxs("th",{onClick:()=>gt("created_at"),style:{cursor:"pointer"},children:["Discovered ",tt("created_at")]}),t.jsx("th",{children:"Actions"})]})}),t.jsx("tbody",{children:p?t.jsx("tr",{children:t.jsxs("td",{colSpan:"8",style:{textAlign:"center",padding:"2rem"},children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Loading threat intelligence..."]})}):s.length>0?s.map(j=>t.jsxs("tr",{children:[t.jsx("td",{children:j.id}),t.jsx("td",{children:t.jsxs("div",{className:"ttp-name-cell",children:[t.jsx("div",{className:"ttp-title",children:j.name}),j.mitre_subtechnique&&t.jsx("div",{className:"ttp-subtechnique",children:j.mitre_subtechnique})]})}),t.jsx("td",{children:t.jsx("span",{className:"technique-badge",children:j.mitre_technique_id})}),t.jsx("td",{children:t.jsx("span",{className:"tactic-badge",children:j.mitre_tactic_display||j.mitre_tactic})}),t.jsx("td",{children:j.threat_feed?t.jsxs("div",{className:"feed-source-cell",children:[t.jsx("span",{className:"feed-name",children:j.threat_feed.name}),t.jsx("span",{className:`feed-type ${j.threat_feed.is_external?"external":"internal"}`,children:j.threat_feed.is_external?"External":"Internal"})]}):t.jsx("span",{className:"text-muted",children:"No Feed"})}),t.jsx("td",{children:t.jsx("div",{className:"intelligence-status",children:j.is_anonymized?t.jsxs("span",{className:"status-badge anonymized",children:[t.jsx("i",{className:"fas fa-mask"})," Anonymized"]}):t.jsxs("span",{className:"status-badge raw",children:[t.jsx("i",{className:"fas fa-eye"})," Raw Intel"]})})}),t.jsx("td",{children:j.created_at?new Date(j.created_at).toLocaleDateString():"Unknown"}),t.jsx("td",{children:t.jsx("button",{className:"btn btn-outline btn-sm",onClick:()=>ga(j.id),title:"View Intelligence Details",style:{marginRight:"5px"},children:t.jsx("i",{className:"fas fa-search"})})})]},j.id)):t.jsx("tr",{children:t.jsx("td",{colSpan:"8",style:{textAlign:"center",padding:"2rem"},children:t.jsxs("div",{className:"empty-state",children:[t.jsx("i",{className:"fas fa-shield-alt"}),t.jsx("p",{children:"No TTP intelligence available"}),t.jsx("p",{className:"text-muted",children:"Consume threat feeds to populate TTP intelligence data"})]})})})})]})}),(H>0||p)&&t.jsxs("div",{className:"pagination-wrapper",style:{marginTop:"1.5rem"},children:[t.jsx("div",{className:"pagination-info-detailed",children:t.jsx("span",{className:"pagination-summary",children:p?t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-spinner fa-spin",style:{marginRight:"5px"}}),"Loading TTPs..."]}):t.jsxs(t.Fragment,{children:["Showing ",t.jsx("strong",{children:Math.min((ge-1)*me+1,He)})," to ",t.jsx("strong",{children:Math.min(ge*me,He)})," of ",t.jsx("strong",{children:He})," TTPs"]})})}),H>1&&t.jsxs("div",{className:"pagination-controls-enhanced",children:[t.jsxs("div",{className:"items-per-page-selector",style:{marginRight:"1rem"},children:[t.jsx("label",{htmlFor:"ttp-page-size",style:{fontSize:"0.85rem",marginRight:"0.5rem"},children:"Items per page:"}),t.jsxs("select",{id:"ttp-page-size",className:"form-control-sm",value:me,onChange:j=>Ya(parseInt(j.target.value)),style:{minWidth:"70px"},disabled:p,children:[t.jsx("option",{value:10,children:"10"}),t.jsx("option",{value:20,children:"20"}),t.jsx("option",{value:50,children:"50"}),t.jsx("option",{value:100,children:"100"})]})]}),t.jsx("button",{className:`btn btn-outline btn-sm ${!G||p?"disabled":""}`,onClick:()=>Fa(ge-1),disabled:!G||p,style:{marginRight:"0.25rem"},children:t.jsx("i",{className:"fas fa-chevron-left"})}),t.jsx("div",{className:"pagination-pages",children:Ga().map((j,pe)=>j==="..."?t.jsx("span",{className:"pagination-ellipsis",children:"..."},`ellipsis-${pe}`):t.jsx("button",{className:`btn btn-sm ${j===ge?"btn-primary":"btn-outline"}`,onClick:()=>Fa(j),disabled:p,children:j},j))}),t.jsx("button",{className:`btn btn-outline btn-sm ${!_e||p?"disabled":""}`,onClick:()=>Fa(ge+1),disabled:!_e||p,style:{marginLeft:"0.25rem"},children:t.jsx("i",{className:"fas fa-chevron-right"})})]})]})]}),(_==="matrix"||_==="list")&&t.jsxs("div",{className:"card mt-4",children:[t.jsxs("div",{className:"card-header",children:[t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-chart-line card-icon"})," TTP Trends Chart"]}),t.jsx("div",{className:"card-actions",children:t.jsxs("button",{className:"btn btn-outline btn-sm",children:[t.jsx("i",{className:"fas fa-calendar-alt"})," Last 90 Days"]})})]}),t.jsx("div",{className:"card-content",children:t.jsx("div",{className:"chart-container",ref:Ht,children:h?t.jsxs("div",{style:{textAlign:"center",padding:"4rem"},children:[t.jsx("i",{className:"fas fa-spinner fa-spin",style:{fontSize:"2rem",color:"#0056b3"}}),t.jsx("p",{style:{marginTop:"1rem",color:"#666"},children:"Loading TTP trends data..."})]}):o.length===0?t.jsxs("div",{style:{textAlign:"center",padding:"4rem"},children:[t.jsx("i",{className:"fas fa-chart-line",style:{fontSize:"2rem",color:"#ccc"}}),t.jsx("p",{style:{marginTop:"1rem",color:"#666"},children:"No TTP trends data available"}),t.jsx("p",{style:{color:"#888",fontSize:"0.9rem"},children:"TTP data will appear here as it becomes available"})]}):null})})]}),_==="trends"&&t.jsx("div",{className:"trends-analysis",children:t.jsxs("div",{className:"card",children:[t.jsxs("div",{className:"card-header",children:[t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-chart-line card-icon"})," TTP Trends & Patterns"]}),t.jsxs("div",{className:"card-actions",children:[t.jsxs("select",{className:"form-control",style:{width:"auto",marginRight:"10px"},children:[t.jsx("option",{value:"30",children:"Last 30 Days"}),t.jsx("option",{value:"90",children:"Last 90 Days"}),t.jsx("option",{value:"180",children:"Last 6 Months"}),t.jsx("option",{value:"365",children:"Last Year"})]}),t.jsxs("button",{className:"btn btn-outline btn-sm",onClick:$a,disabled:X,children:[t.jsx("i",{className:`fas ${X?"fa-spinner fa-spin":"fa-sync-alt"}`})," Refresh"]})]})]}),t.jsx("div",{className:"card-content",children:X?t.jsxs("div",{className:"loading-state",children:[t.jsx("i",{className:"fas fa-spinner fa-spin"}),t.jsx("p",{children:"Loading trends analysis..."})]}):t.jsxs("div",{className:"trends-content",children:[t.jsxs("div",{className:"trend-charts-grid",children:[t.jsxs("div",{className:"chart-container",children:[t.jsx("h3",{children:"Technique Frequency Over Time"}),t.jsx("div",{className:"trend-chart",ref:Ht,style:{minHeight:"300px",width:"100%"}})]}),t.jsxs("div",{className:"tactic-distribution",children:[t.jsx("h3",{children:"Tactic Distribution"}),L&&L.tactics?t.jsx("div",{className:"tactic-bars",children:Object.entries(L.tactics).sort(([,j],[,pe])=>pe.count-j.count).slice(0,8).map(([j,pe])=>t.jsxs("div",{className:"tactic-bar-item",children:[t.jsx("div",{className:"tactic-label",children:j.replace("-"," ")}),t.jsx("div",{className:"bar-container",children:t.jsx("div",{className:"bar-fill",style:{width:`${pe.percentage}%`}})}),t.jsx("div",{className:"bar-value",children:pe.count})]},j))}):t.jsx("div",{className:"empty-state",children:t.jsx("p",{children:"No tactic distribution data available"})})]})]}),t.jsxs("div",{className:"trend-insights",children:[t.jsx("h3",{children:"Key Insights"}),t.jsxs("div",{className:"insights-grid",children:[t.jsxs("div",{className:"insight-card",children:[t.jsx("i",{className:"fas fa-trending-up"}),t.jsxs("div",{children:[t.jsx("h4",{children:"Emerging Techniques"}),t.jsx("p",{children:"New techniques appearing in recent threat intelligence"})]})]}),t.jsxs("div",{className:"insight-card",children:[t.jsx("i",{className:"fas fa-clock"}),t.jsxs("div",{children:[t.jsx("h4",{children:"Seasonal Patterns"}),t.jsx("p",{children:P&&P.interpretation?P.interpretation:"Analyzing temporal patterns in TTP usage"})]})]}),t.jsxs("div",{className:"insight-card",children:[t.jsx("i",{className:"fas fa-exclamation-triangle"}),t.jsxs("div",{children:[t.jsx("h4",{children:"High-Frequency TTPs"}),t.jsx("p",{children:"Most commonly observed techniques across all feeds"})]})]})]})]})]})})]})}),(_==="matrix"||_==="list")&&t.jsxs("div",{className:"card mt-4",children:[t.jsx("div",{className:"card-header",children:t.jsxs("div",{className:"filters-header",children:[t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-tasks card-icon"})," Recent TTP Analyses"]}),t.jsxs("div",{className:"filter-actions",children:[p&&t.jsxs("span",{style:{fontSize:"0.85rem",color:"#6c757d"},children:[t.jsx("i",{className:"fas fa-spinner fa-spin",style:{marginRight:"5px"}}),"Filtering..."]}),ne>0&&t.jsxs("span",{className:"filtered-count",children:[ne," filter",ne!==1?"s":""," applied"]}),t.jsxs("button",{className:`btn btn-outline btn-sm ${oe?"active":""}`,onClick:()=>re(!oe),disabled:p,children:[t.jsx("i",{className:"fas fa-filter"})," Filters"]}),ne>0&&t.jsxs("button",{className:"btn btn-outline btn-sm text-danger",onClick:ii,title:"Clear all filters",children:[t.jsx("i",{className:"fas fa-times"})," Clear"]})]})]})}),oe&&t.jsx("div",{className:"filters-panel",style:{borderBottom:"1px solid #e9ecef",padding:"1.5rem",background:"#f8f9fa"},children:t.jsxs("div",{className:"filters-grid",style:{display:"grid",gridTemplateColumns:"repeat(auto-fit, minmax(250px, 1fr))",gap:"1rem"},children:[t.jsxs("div",{className:"filter-group",children:[t.jsxs("label",{className:"filter-label",children:[t.jsx("i",{className:"fas fa-search",style:{marginRight:"5px"}})," Search"]}),t.jsx("input",{type:"text",className:"form-control",placeholder:"Search TTPs, techniques, descriptions...",value:je.search,onChange:j=>da("search",j.target.value),onKeyDown:j=>{j.key==="Enter"&&(j.preventDefault(),sa(K,Ae,1,me,je))},disabled:p})]}),t.jsxs("div",{className:"filter-group",children:[t.jsxs("label",{className:"filter-label",children:[t.jsx("i",{className:"fas fa-crosshairs",style:{marginRight:"5px"}})," MITRE Tactics"]}),t.jsx("select",{className:"form-control",multiple:!0,size:"4",value:je.tactics,onChange:j=>{const pe=Array.from(j.target.selectedOptions,Se=>Se.value);da("tactics",pe)},style:{fontSize:"0.85rem"},disabled:p,children:(Qt=Te==null?void 0:Te.tactics)==null?void 0:Qt.map(j=>t.jsxs("option",{value:j.value,children:[j.label," (",j.count||0,")"]},j.value))})]}),t.jsxs("div",{className:"filter-group",children:[t.jsxs("label",{className:"filter-label",children:[t.jsx("i",{className:"fas fa-exclamation-triangle",style:{marginRight:"5px"}})," Severity Levels"]}),t.jsx("div",{className:"checkbox-group",style:{display:"grid",gridTemplateColumns:"1fr 1fr",gap:"0.5rem"},children:["critical","high","medium","low"].map(j=>t.jsxs("label",{className:"checkbox-item",style:{display:"flex",alignItems:"center",fontSize:"0.85rem"},children:[t.jsx("input",{type:"checkbox",checked:je.severity_levels.includes(j),onChange:pe=>Qs("severity_levels",j,pe.target.checked),style:{marginRight:"5px"},disabled:p}),t.jsx("span",{className:`severity-badge severity-${j}`,style:{padding:"2px 8px",borderRadius:"12px",fontSize:"0.75rem",fontWeight:"500",textTransform:"capitalize"},children:j})]},j))})]}),t.jsxs("div",{className:"filter-group",children:[t.jsxs("label",{className:"filter-label",children:[t.jsx("i",{className:"fas fa-calendar-alt",style:{marginRight:"5px"}})," Date Range"]}),t.jsxs("div",{style:{display:"grid",gridTemplateColumns:"1fr 1fr",gap:"0.5rem"},children:[t.jsx("input",{type:"date",className:"form-control",value:je.date_from,onChange:j=>da("date_from",j.target.value),placeholder:"From",title:"From date",disabled:p}),t.jsx("input",{type:"date",className:"form-control",value:je.date_to,onChange:j=>da("date_to",j.target.value),placeholder:"To",title:"To date",disabled:p})]})]}),t.jsxs("div",{className:"filter-group",children:[t.jsxs("label",{className:"filter-label",children:[t.jsx("i",{className:"fas fa-rss",style:{marginRight:"5px"}})," Threat Feeds"]}),t.jsx("select",{className:"form-control",multiple:!0,size:"3",value:je.threat_feed_ids,onChange:j=>{const pe=Array.from(j.target.selectedOptions,Se=>Se.value);da("threat_feed_ids",pe)},style:{fontSize:"0.85rem"},children:(wa=Te==null?void 0:Te.threat_feeds)==null?void 0:wa.map(j=>t.jsxs("option",{value:j.id.toString(),children:[j.name," (",j.ttp_count||0,")"]},j.id))})]}),t.jsxs("div",{className:"filter-group",children:[t.jsxs("label",{className:"filter-label",children:[t.jsx("i",{className:"fas fa-toggle-on",style:{marginRight:"5px"}})," Status Filters"]}),t.jsxs("div",{style:{display:"grid",gap:"0.5rem"},children:[t.jsxs("select",{className:"form-control",value:je.anonymized_only,onChange:j=>da("anonymized_only",j.target.value),style:{fontSize:"0.85rem"},children:[t.jsx("option",{value:"",children:"All TTPs"}),t.jsx("option",{value:"true",children:"Anonymized Only"}),t.jsx("option",{value:"false",children:"Active Only"})]}),t.jsxs("select",{className:"form-control",value:je.has_subtechniques,onChange:j=>da("has_subtechniques",j.target.value),style:{fontSize:"0.85rem"},children:[t.jsx("option",{value:"",children:"All Techniques"}),t.jsx("option",{value:"true",children:"With Sub-techniques"}),t.jsx("option",{value:"false",children:"Without Sub-techniques"})]})]})]})]})}),ne>0&&t.jsx("div",{className:"active-filters-summary",style:{padding:"1rem",borderBottom:"1px solid #e9ecef",background:"#fff"},children:t.jsxs("div",{style:{display:"flex",alignItems:"center",flexWrap:"wrap",gap:"0.5rem"},children:[t.jsx("span",{style:{fontSize:"0.875rem",fontWeight:"600",color:"#495057"},children:"Active Filters:"}),je.search&&t.jsxs("span",{className:"filter-badge",style:{background:"#e3f2fd",color:"#1976d2",padding:"2px 8px",borderRadius:"12px",fontSize:"0.75rem",display:"flex",alignItems:"center",gap:"4px"},children:['Search: "',je.search,'"',t.jsx("button",{onClick:()=>da("search",""),style:{background:"none",border:"none",color:"#1976d2",cursor:"pointer",padding:"0",fontSize:"0.75rem"},children:"×"})]}),je.tactics.length>0&&t.jsxs("span",{className:"filter-badge",style:{background:"#f3e5f5",color:"#7b1fa2",padding:"2px 8px",borderRadius:"12px",fontSize:"0.75rem",display:"flex",alignItems:"center",gap:"4px"},children:[je.tactics.length," Tactic",je.tactics.length!==1?"s":"",t.jsx("button",{onClick:()=>da("tactics",[]),style:{background:"none",border:"none",color:"#7b1fa2",cursor:"pointer",padding:"0",fontSize:"0.75rem"},children:"×"})]}),je.severity_levels.length>0&&t.jsxs("span",{className:"filter-badge",style:{background:"#ffebee",color:"#c62828",padding:"2px 8px",borderRadius:"12px",fontSize:"0.75rem",display:"flex",alignItems:"center",gap:"4px"},children:[je.severity_levels.length," Severity Level",je.severity_levels.length!==1?"s":"",t.jsx("button",{onClick:()=>da("severity_levels",[]),style:{background:"none",border:"none",color:"#c62828",cursor:"pointer",padding:"0",fontSize:"0.75rem"},children:"×"})]}),(je.date_from||je.date_to)&&t.jsxs("span",{className:"filter-badge",style:{background:"#e8f5e8",color:"#2e7d32",padding:"2px 8px",borderRadius:"12px",fontSize:"0.75rem",display:"flex",alignItems:"center",gap:"4px"},children:["Date Range",t.jsx("button",{onClick:()=>{const j={...je,date_from:"",date_to:""};Le(j),Ne(1);const pe=En(j);D(pe),sa(K,Ae,1,me,j)},style:{background:"none",border:"none",color:"#2e7d32",cursor:"pointer",padding:"0",fontSize:"0.75rem"},children:"×"})]}),je.threat_feed_ids.length>0&&t.jsxs("span",{className:"filter-badge",style:{background:"#fff3e0",color:"#ef6c00",padding:"2px 8px",borderRadius:"12px",fontSize:"0.75rem",display:"flex",alignItems:"center",gap:"4px"},children:[je.threat_feed_ids.length," Feed",je.threat_feed_ids.length!==1?"s":"",t.jsx("button",{onClick:()=>da("threat_feed_ids",[]),style:{background:"none",border:"none",color:"#ef6c00",cursor:"pointer",padding:"0",fontSize:"0.75rem"},children:"×"})]})]})}),t.jsx("div",{className:"card-content",children:t.jsxs("table",{className:"data-table",children:[t.jsx("thead",{children:t.jsxs("tr",{children:[t.jsxs("th",{className:"sortable-header",onClick:()=>gt("id"),style:{cursor:"pointer",userSelect:"none"},children:["ID",tt("id")]}),t.jsxs("th",{className:"sortable-header",onClick:()=>gt("name"),style:{cursor:"pointer",userSelect:"none"},children:["Name",tt("name")]}),t.jsxs("th",{className:"sortable-header",onClick:()=>gt("mitre_technique_id"),style:{cursor:"pointer",userSelect:"none"},children:["MITRE Technique",tt("mitre_technique_id")]}),t.jsxs("th",{className:"sortable-header",onClick:()=>gt("mitre_tactic"),style:{cursor:"pointer",userSelect:"none"},children:["Tactic",tt("mitre_tactic")]}),t.jsx("th",{children:"Threat Feed"}),t.jsxs("th",{className:"sortable-header",onClick:()=>gt("created_at"),style:{cursor:"pointer",userSelect:"none"},children:["Created",tt("created_at")]}),t.jsx("th",{children:"Status"}),t.jsx("th",{children:"Actions"})]})}),t.jsx("tbody",{children:p?t.jsx("tr",{children:t.jsxs("td",{colSpan:"8",style:{textAlign:"center",padding:"2rem"},children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Loading TTPs..."]})}):s.length>0?s.map(j=>t.jsxs("tr",{children:[t.jsx("td",{children:j.id}),t.jsx("td",{children:j.name}),t.jsx("td",{children:j.mitre_technique_id}),t.jsx("td",{children:j.mitre_tactic_display||j.mitre_tactic}),t.jsx("td",{children:j.threat_feed?j.threat_feed.name:"N/A"}),t.jsx("td",{children:new Date(j.created_at).toLocaleDateString()}),t.jsx("td",{children:t.jsx("span",{className:`badge ${j.is_anonymized?"badge-info":"badge-success"}`,children:j.is_anonymized?"Anonymized":"Active"})}),t.jsxs("td",{children:[t.jsx("button",{className:"btn btn-outline btn-sm",title:"View TTP Details",onClick:()=>ga(j.id),style:{marginRight:"5px"},children:t.jsx("i",{className:"fas fa-eye"})}),t.jsx("button",{className:"btn btn-outline btn-sm",title:"Share",style:{marginRight:"5px"},children:t.jsx("i",{className:"fas fa-share-alt"})}),t.jsx("button",{className:"btn btn-outline btn-sm text-danger",title:"Delete TTP",onClick:()=>Ze(j.id),children:t.jsx("i",{className:"fas fa-trash"})})]})]},j.id)):t.jsx("tr",{children:t.jsx("td",{colSpan:"8",style:{textAlign:"center",padding:"2rem"},children:"No TTPs found"})})})]})})]}),I&&t.jsx("div",{className:"modal-overlay",onClick:hn,children:t.jsxs("div",{className:"modal-content ttp-modal",onClick:j=>j.stopPropagation(),children:[t.jsxs("div",{className:"modal-header",children:[t.jsxs("h2",{children:[t.jsx("i",{className:"fas fa-crosshairs"}),Ke?"Edit TTP Details":"TTP Details"]}),t.jsx("button",{className:"modal-close",onClick:hn,children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsx("div",{className:"modal-body",children:Ve?t.jsxs("div",{style:{textAlign:"center",padding:"3rem"},children:[t.jsx("i",{className:"fas fa-spinner fa-spin",style:{fontSize:"2rem",color:"#0056b3"}}),t.jsx("p",{style:{marginTop:"1rem",color:"#666"},children:"Loading TTP details..."})]}):be?t.jsxs("div",{className:"ttp-detail-content",children:[t.jsx("div",{className:"ttp-header-section",children:t.jsxs("div",{className:"ttp-title-section",children:[Ke?t.jsx("input",{type:"text",className:"form-control ttp-name-input",value:_t.name,onChange:j=>an("name",j.target.value),placeholder:"TTP Name"}):t.jsx("h3",{className:"ttp-title",children:be.name}),t.jsxs("div",{className:"ttp-badges",children:[t.jsx("span",{className:"badge badge-primary",children:be.mitre_technique_id||"No MITRE ID"}),t.jsx("span",{className:"badge badge-secondary",children:be.mitre_tactic_display||be.mitre_tactic||"No Tactic"}),be.is_anonymized&&t.jsx("span",{className:"badge badge-info",children:"Anonymized"})]})]})}),t.jsxs("div",{className:"ttp-details-grid",children:[t.jsxs("div",{className:"detail-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-info-circle"})," Basic Information"]}),t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Description:"}),t.jsx("div",{className:"detail-value",children:Ke?t.jsx("textarea",{className:"form-control",value:_t.description,onChange:j=>an("description",j.target.value),placeholder:"TTP Description",rows:"4"}):t.jsx("p",{children:be.description||"No description available"})})]})]}),t.jsxs("div",{className:"detail-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-crosshairs"})," MITRE ATT&CK Mapping"]}),t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Technique ID:"}),t.jsx("div",{className:"detail-value",children:Ke?t.jsx("input",{type:"text",className:"form-control",value:_t.mitre_technique_id,onChange:j=>an("mitre_technique_id",j.target.value),placeholder:"e.g., T1566.001"}):t.jsx("span",{className:"technique-id-display",children:be.mitre_technique_id||"Not specified"})})]}),t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Tactic:"}),t.jsx("div",{className:"detail-value",children:Ke?t.jsxs("select",{className:"form-control",value:_t.mitre_tactic,onChange:j=>an("mitre_tactic",j.target.value),children:[t.jsx("option",{value:"",children:"Select Tactic"}),t.jsx("option",{value:"initial-access",children:"Initial Access"}),t.jsx("option",{value:"execution",children:"Execution"}),t.jsx("option",{value:"persistence",children:"Persistence"}),t.jsx("option",{value:"privilege-escalation",children:"Privilege Escalation"}),t.jsx("option",{value:"defense-evasion",children:"Defense Evasion"}),t.jsx("option",{value:"credential-access",children:"Credential Access"}),t.jsx("option",{value:"discovery",children:"Discovery"}),t.jsx("option",{value:"lateral-movement",children:"Lateral Movement"}),t.jsx("option",{value:"collection",children:"Collection"}),t.jsx("option",{value:"command-and-control",children:"Command and Control"}),t.jsx("option",{value:"exfiltration",children:"Exfiltration"}),t.jsx("option",{value:"impact",children:"Impact"})]}):t.jsx("span",{children:be.mitre_tactic_display||be.mitre_tactic||"Not specified"})})]}),(be.mitre_subtechnique||Ke)&&t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Sub-technique:"}),t.jsx("div",{className:"detail-value",children:Ke?t.jsx("input",{type:"text",className:"form-control",value:_t.mitre_subtechnique,onChange:j=>an("mitre_subtechnique",j.target.value),placeholder:"Sub-technique name"}):t.jsx("span",{children:be.mitre_subtechnique||"None"})})]})]}),t.jsxs("div",{className:"detail-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-rss"})," Threat Feed Information"]}),t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Source Feed:"}),t.jsx("div",{className:"detail-value",children:be.threat_feed?t.jsxs("div",{className:"feed-info",children:[t.jsx("span",{className:"feed-name",children:be.threat_feed.name}),t.jsx("span",{className:`feed-type ${be.threat_feed.is_external?"external":"internal"}`,children:be.threat_feed.is_external?"External":"Internal"})]}):t.jsx("span",{className:"no-data",children:"Manual Entry"})})]})]}),t.jsxs("div",{className:"detail-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-clock"})," Metadata"]}),t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Created:"}),t.jsx("div",{className:"detail-value",children:be.created_at?new Date(be.created_at).toLocaleString():"Unknown"})]}),t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Last Modified:"}),t.jsx("div",{className:"detail-value",children:be.updated_at?new Date(be.updated_at).toLocaleString():"Never"})]}),be.stix_id&&t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"STIX ID:"}),t.jsx("div",{className:"detail-value",children:t.jsx("code",{children:be.stix_id})})]})]})]})]}):t.jsxs("div",{style:{textAlign:"center",padding:"3rem"},children:[t.jsx("i",{className:"fas fa-exclamation-triangle",style:{fontSize:"2rem",color:"#dc3545"}}),t.jsx("p",{style:{marginTop:"1rem",color:"#666"},children:"Failed to load TTP details"})]})}),t.jsxs("div",{className:"modal-footer",children:[t.jsx("button",{className:"btn btn-outline",onClick:hn,children:"Close"}),be&&!Ve&&t.jsx(t.Fragment,{children:Ke?t.jsxs(t.Fragment,{children:[t.jsx("button",{className:"btn btn-outline",onClick:rs,children:"Cancel Edit"}),t.jsxs("button",{className:"btn btn-primary",onClick:Un,children:[t.jsx("i",{className:"fas fa-save"})," Save Changes"]})]}):t.jsxs("button",{className:"btn btn-primary",onClick:rs,children:[t.jsx("i",{className:"fas fa-edit"})," Edit TTP"]})})]})]})}),ft&&t.jsx("div",{className:"modal-overlay",onClick:si,children:t.jsxs("div",{className:"modal-content export-modal",onClick:j=>j.stopPropagation(),children:[t.jsxs("div",{className:"modal-header",children:[t.jsxs("h3",{children:[t.jsx("i",{className:"fas fa-download"})," Export TTP Analysis"]}),t.jsx("button",{className:"modal-close",onClick:si,children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsxs("div",{className:"modal-body",children:[et&&t.jsxs("div",{className:"alert alert-error",children:[t.jsx("i",{className:"fas fa-exclamation-triangle"}),et]}),t.jsx("div",{className:"export-info",children:t.jsxs("div",{className:"info-card",children:[t.jsx("i",{className:"fas fa-info-circle"}),t.jsxs("div",{children:[t.jsx("strong",{children:"Export Information"}),t.jsx("p",{children:"Export your TTP analysis data in multiple formats. You can filter the data and customize the export to meet your specific needs."})]})]})}),t.jsxs("form",{children:[t.jsxs("div",{className:"form-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-file-alt"})," Export Format"]}),t.jsxs("div",{className:"format-options",children:[t.jsxs("label",{className:"format-option",children:[t.jsx("input",{type:"radio",name:"exportFormat",value:"json",checked:Re==="json",onChange:j=>U(j.target.value)}),t.jsxs("div",{className:"format-card",children:[t.jsx("i",{className:"fas fa-code"}),t.jsx("span",{children:"JSON"}),t.jsx("small",{children:"Structured data format"})]})]}),t.jsxs("label",{className:"format-option",children:[t.jsx("input",{type:"radio",name:"exportFormat",value:"csv",checked:Re==="csv",onChange:j=>U(j.target.value)}),t.jsxs("div",{className:"format-card",children:[t.jsx("i",{className:"fas fa-table"}),t.jsx("span",{children:"CSV"}),t.jsx("small",{children:"Spreadsheet compatible"})]})]}),t.jsxs("label",{className:"format-option",children:[t.jsx("input",{type:"radio",name:"exportFormat",value:"stix",checked:Re==="stix",onChange:j=>U(j.target.value)}),t.jsxs("div",{className:"format-card",children:[t.jsx("i",{className:"fas fa-shield-alt"}),t.jsx("span",{children:"STIX"}),t.jsx("small",{children:"Threat intelligence standard"})]})]})]})]}),t.jsxs("div",{className:"form-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-filter"})," Filters"]}),t.jsxs("div",{className:"form-grid",children:[t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"MITRE Tactic"}),t.jsxs("select",{className:"form-control",value:fe.tactic,onChange:j=>Gt("tactic",j.target.value),children:[t.jsx("option",{value:"",children:"All Tactics"}),t.jsx("option",{value:"initial-access",children:"Initial Access"}),t.jsx("option",{value:"execution",children:"Execution"}),t.jsx("option",{value:"persistence",children:"Persistence"}),t.jsx("option",{value:"privilege-escalation",children:"Privilege Escalation"}),t.jsx("option",{value:"defense-evasion",children:"Defense Evasion"}),t.jsx("option",{value:"credential-access",children:"Credential Access"}),t.jsx("option",{value:"discovery",children:"Discovery"}),t.jsx("option",{value:"lateral-movement",children:"Lateral Movement"}),t.jsx("option",{value:"collection",children:"Collection"}),t.jsx("option",{value:"command-and-control",children:"Command and Control"}),t.jsx("option",{value:"exfiltration",children:"Exfiltration"}),t.jsx("option",{value:"impact",children:"Impact"})]})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Technique ID"}),t.jsx("input",{type:"text",className:"form-control",value:fe.technique_id,onChange:j=>Gt("technique_id",j.target.value),placeholder:"e.g., T1059"})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Threat Feed ID"}),t.jsx("input",{type:"number",className:"form-control",value:fe.feed_id,onChange:j=>Gt("feed_id",j.target.value),placeholder:"Enter feed ID"})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Maximum Records"}),t.jsx("input",{type:"number",className:"form-control",value:fe.limit,onChange:j=>Gt("limit",parseInt(j.target.value)||1e3),min:"1",max:"10000"})]})]}),t.jsxs("div",{className:"form-row",children:[t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Created After"}),t.jsx("input",{type:"date",className:"form-control",value:fe.created_after,onChange:j=>Gt("created_after",j.target.value)})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Created Before"}),t.jsx("input",{type:"date",className:"form-control",value:fe.created_before,onChange:j=>Gt("created_before",j.target.value)})]})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Specific Fields (comma-separated)"}),t.jsx("input",{type:"text",className:"form-control",value:fe.fields,onChange:j=>Gt("fields",j.target.value),placeholder:"e.g., id,name,mitre_technique_id,description"}),t.jsx("small",{className:"form-help",children:"Leave empty to export all available fields"})]})]}),t.jsxs("div",{className:"form-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-cog"})," Advanced Options"]}),t.jsxs("div",{className:"checkbox-group",children:[t.jsxs("label",{className:"checkbox-label",children:[t.jsx("input",{type:"checkbox",checked:fe.include_anonymized,onChange:j=>Gt("include_anonymized",j.target.checked)}),t.jsx("span",{children:"Include anonymized TTPs"})]}),t.jsxs("label",{className:"checkbox-label",children:[t.jsx("input",{type:"checkbox",checked:fe.include_original,onChange:j=>Gt("include_original",j.target.checked)}),t.jsx("span",{children:"Include original data for anonymized TTPs"})]})]})]})]})]}),t.jsxs("div",{className:"modal-footer",children:[t.jsx("button",{className:"btn btn-outline",onClick:si,children:"Cancel"}),t.jsx("button",{className:"btn btn-primary",onClick:T,disabled:Ce,children:Ce?t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Exporting..."]}):t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-download"})," Export Data"]})})]})]})}),Ot&&t.jsx("div",{className:"modal-overlay",onClick:On,children:t.jsxs("div",{className:"modal-content matrix-cell-modal",onClick:j=>j.stopPropagation(),children:[t.jsxs("div",{className:"modal-header",children:[t.jsxs("h3",{children:[t.jsx("i",{className:"fas fa-th-large"}),ht?`Technique ${ht} in ${rt.replace(/_/g," ")}`:`${rt.replace(/_/g," ")} Tactic Details`]}),t.jsx("button",{className:"modal-close",onClick:On,children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsx("div",{className:"modal-body",children:ce?t.jsxs("div",{className:"loading-state",children:[t.jsx("i",{className:"fas fa-spinner fa-spin"}),t.jsx("span",{children:"Loading matrix cell details..."})]}):Ee?t.jsxs("div",{className:"matrix-cell-details",children:[t.jsx("div",{className:"cell-info-section",children:t.jsxs("div",{className:"info-grid",children:[t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"Tactic:"}),t.jsx("span",{children:Ee.cell_info.tactic_display})]}),t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"Total TTPs:"}),t.jsx("span",{children:Ee.cell_info.total_ttps_in_cell})]}),t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"Unique Techniques:"}),t.jsx("span",{children:Ee.cell_info.unique_techniques})]}),t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"Threat Feeds:"}),t.jsx("span",{children:Ee.cell_info.threat_feeds_count})]}),t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"Recent Activity (30d):"}),t.jsx("span",{children:Ee.cell_info.recent_activity})]}),t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"With Subtechniques:"}),t.jsx("span",{children:Ee.cell_info.has_subtechniques})]})]})}),Ee.related_techniques&&Ee.related_techniques.length>0&&t.jsxs("div",{className:"related-techniques-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-sitemap"})," Top Techniques in this Tactic"]}),t.jsx("div",{className:"techniques-grid",children:Ee.related_techniques.map((j,pe)=>t.jsxs("div",{className:"technique-card clickable",onClick:()=>Rn(j.mitre_technique_id),children:[t.jsx("div",{className:"technique-id",children:j.mitre_technique_id}),t.jsxs("div",{className:"technique-count",children:[j.count," TTPs"]})]},j.mitre_technique_id||pe))})]}),t.jsxs("div",{className:"ttps-list-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-list"}),"TTPs (",Ee.ttps.filtered_count,")",Ee.ttps.has_next&&t.jsxs("span",{className:"showing-info",children:["(Showing first ",Ee.ttps.page_size,")"]})]}),Ee.ttps.results.length>0?t.jsx("div",{className:"ttps-list",children:Ee.ttps.results.map(j=>t.jsxs("div",{className:"ttp-item",children:[t.jsxs("div",{className:"ttp-header",children:[t.jsx("div",{className:"ttp-name",children:j.name}),t.jsxs("div",{className:"ttp-badges",children:[j.mitre_technique_id&&t.jsx("span",{className:"badge technique-badge",children:j.mitre_technique_id}),j.severity&&t.jsx("span",{className:`badge severity-${j.severity}`,children:j.severity}),j.is_anonymized&&t.jsx("span",{className:"badge anonymized-badge",children:"Anonymized"})]})]}),t.jsx("div",{className:"ttp-description",children:j.description.length>200?j.description.substring(0,200)+"...":j.description}),t.jsxs("div",{className:"ttp-meta",children:[j.threat_feed&&t.jsxs("div",{className:"feed-info",children:[t.jsx("i",{className:"fas fa-rss"}),t.jsx("span",{children:j.threat_feed.name}),j.threat_feed.is_external&&t.jsx("span",{className:"external-indicator",children:"External"})]}),t.jsxs("div",{className:"created-date",children:[t.jsx("i",{className:"fas fa-clock"}),new Date(j.created_at).toLocaleDateString()]})]})]},j.id))}):t.jsxs("div",{className:"empty-state",children:[t.jsx("i",{className:"fas fa-info-circle"}),t.jsx("span",{children:"No TTPs found for this matrix cell"})]})]}),Ee.statistics&&t.jsxs("div",{className:"statistics-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-chart-bar"})," Statistics"]}),t.jsx("div",{className:"stats-grid",children:Ee.statistics.severity_distribution&&t.jsxs("div",{className:"stat-item",children:[t.jsx("label",{children:"Severity Distribution:"}),t.jsx("div",{className:"severity-bars",children:Object.entries(Ee.statistics.severity_distribution).map(([j,pe])=>t.jsx("div",{className:"severity-bar",children:t.jsxs("span",{className:`severity-label ${j}`,children:[j,": ",pe]})},j))})]})})]})]}):t.jsxs("div",{className:"error-state",children:[t.jsx("i",{className:"fas fa-exclamation-triangle"}),t.jsx("span",{children:"Failed to load matrix cell details"})]})}),t.jsxs("div",{className:"modal-footer",children:[t.jsx("button",{className:"btn btn-outline",onClick:On,children:"Close"}),Ee&&Ee.ttps.has_next&&t.jsxs("button",{className:"btn btn-primary",children:[t.jsx("i",{className:"fas fa-arrow-right"})," View All TTPs"]})]})]})}),Bt&&t.jsx("div",{className:"modal-overlay",onClick:zi,children:t.jsxs("div",{className:"modal-content technique-modal",onClick:j=>j.stopPropagation(),children:[t.jsxs("div",{className:"modal-header",children:[t.jsxs("h3",{children:[t.jsx("i",{className:"fas fa-bullseye"}),"Technique Details: ",Ia]}),t.jsx("button",{className:"modal-close",onClick:zi,children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsx("div",{className:"modal-body",children:Ut?t.jsxs("div",{className:"loading-state",children:[t.jsx("i",{className:"fas fa-spinner fa-spin"}),t.jsx("span",{children:"Loading technique details..."})]}):Oe?t.jsxs("div",{className:"technique-details",children:[t.jsxs("div",{className:"technique-info-section",children:[t.jsx("div",{className:"info-header",children:t.jsxs("div",{className:"technique-title",children:[t.jsx("h4",{children:Oe.technique_info.name||Ia}),t.jsxs("div",{className:"technique-badges",children:[t.jsx("span",{className:"badge technique-badge",children:Ia}),t.jsx("span",{className:`badge severity-${Oe.technique_info.severity}`,children:Oe.technique_info.severity}),Oe.technique_info.is_subtechnique&&t.jsx("span",{className:"badge subtechnique-badge",children:"Subtechnique"})]})]})}),t.jsxs("div",{className:"technique-stats",children:[t.jsxs("div",{className:"stat-item",children:[t.jsx("label",{children:"Total TTPs:"}),t.jsx("span",{children:Oe.statistics.total_ttps})]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("label",{children:"Threat Feeds:"}),t.jsx("span",{children:Oe.statistics.unique_threat_feeds})]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("label",{children:"First Seen:"}),t.jsx("span",{children:Oe.statistics.first_seen?new Date(Oe.statistics.first_seen).toLocaleDateString():"N/A"})]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("label",{children:"Last Seen:"}),t.jsx("span",{children:Oe.statistics.last_seen?new Date(Oe.statistics.last_seen).toLocaleDateString():"N/A"})]})]})]}),Oe.associated_tactics&&Oe.associated_tactics.length>0&&t.jsxs("div",{className:"tactics-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-layer-group"})," Associated Tactics"]}),t.jsx("div",{className:"tactics-grid",children:Oe.associated_tactics.map(j=>t.jsxs("div",{className:"tactic-card clickable",onClick:()=>ua(j.tactic,Ia),children:[t.jsx("div",{className:"tactic-name",children:j.tactic_display}),t.jsxs("div",{className:"tactic-count",children:[j.count," TTPs"]})]},j.tactic))})]}),Oe.variants&&Oe.variants.length>0&&t.jsxs("div",{className:"variants-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-code-branch"})," Related Variants"]}),t.jsx("div",{className:"variants-grid",children:Oe.variants.map(j=>t.jsxs("div",{className:"variant-card clickable",onClick:()=>Rn(j.mitre_technique_id),children:[t.jsx("div",{className:"variant-id",children:j.mitre_technique_id}),t.jsxs("div",{className:"variant-count",children:[j.count," TTPs"]})]},j.mitre_technique_id))})]}),Oe.statistics.recent_activity&&t.jsxs("div",{className:"activity-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-activity"})," Recent Activity"]}),t.jsxs("div",{className:"activity-stats",children:[t.jsxs("div",{className:"activity-item",children:[t.jsx("label",{children:"Last 24 hours:"}),t.jsx("span",{children:Oe.statistics.recent_activity.last_24h})]}),t.jsxs("div",{className:"activity-item",children:[t.jsx("label",{children:"Last 7 days:"}),t.jsx("span",{children:Oe.statistics.recent_activity.last_7d})]}),t.jsxs("div",{className:"activity-item",children:[t.jsx("label",{children:"Last 30 days:"}),t.jsx("span",{children:Oe.statistics.recent_activity.last_30d})]})]})]}),t.jsxs("div",{className:"technique-ttps-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-list"}),"TTPs Using This Technique (",Oe.ttps.length,")"]}),Oe.ttps.length>0?t.jsxs("div",{className:"technique-ttps-list",children:[Oe.ttps.slice(0,10).map(j=>t.jsxs("div",{className:"ttp-item",children:[t.jsxs("div",{className:"ttp-header",children:[t.jsx("div",{className:"ttp-name",children:j.name}),t.jsxs("div",{className:"ttp-badges",children:[j.mitre_tactic&&t.jsx("span",{className:"badge tactic-badge",children:j.mitre_tactic_display}),j.is_anonymized&&t.jsx("span",{className:"badge anonymized-badge",children:"Anonymized"})]})]}),t.jsx("div",{className:"ttp-description",children:j.description.length>150?j.description.substring(0,150)+"...":j.description}),t.jsxs("div",{className:"ttp-meta",children:[j.threat_feed&&t.jsxs("div",{className:"feed-info",children:[t.jsx("i",{className:"fas fa-rss"}),t.jsx("span",{children:j.threat_feed.name})]}),t.jsxs("div",{className:"created-date",children:[t.jsx("i",{className:"fas fa-clock"}),new Date(j.created_at).toLocaleDateString()]})]})]},j.id)),Oe.ttps.length>10&&t.jsxs("div",{className:"more-ttps-indicator",children:[t.jsx("i",{className:"fas fa-ellipsis-h"}),t.jsxs("span",{children:["and ",Oe.ttps.length-10," more TTPs..."]})]})]}):t.jsxs("div",{className:"empty-state",children:[t.jsx("i",{className:"fas fa-info-circle"}),t.jsx("span",{children:"No TTPs found for this technique"})]})]})]}):t.jsxs("div",{className:"error-state",children:[t.jsx("i",{className:"fas fa-exclamation-triangle"}),t.jsx("span",{children:"Failed to load technique details"})]})}),t.jsxs("div",{className:"modal-footer",children:[t.jsx("button",{className:"btn btn-outline",onClick:zi,children:"Close"}),Oe&&Oe.ttps.length>10&&t.jsxs("button",{className:"btn btn-primary",children:[t.jsx("i",{className:"fas fa-external-link-alt"})," View All TTPs"]})]})]})})]})}function _2({active:n}){const[s,l]=N.useState([]),[o,d]=N.useState(!1),f=[{id:1,title:"Weekly Threat Intelligence Summary",type:"summary",date:"2025-01-08",status:"completed",description:"Comprehensive overview of threat landscape for the week"},{id:2,title:"APT Campaign Analysis",type:"campaign",date:"2025-01-05",status:"completed",description:"Deep dive into recent APT activities and TTPs"},{id:3,title:"Vulnerability Trend Report",type:"trend",date:"2025-01-01",status:"draft",description:"Analysis of vulnerability trends and exploitation patterns"}];return N.useEffect(()=>{n&&(d(!0),setTimeout(()=>{l(f),d(!1)},1e3))},[n]),n?t.jsxs("section",{id:"reports",className:`page-section ${n?"active":""}`,children:[t.jsxs("div",{className:"page-header",children:[t.jsxs("div",{children:[t.jsx("h1",{className:"page-title",children:"Reports & Analytics"}),t.jsx("p",{className:"page-subtitle",children:"Generate and manage threat intelligence reports"})]}),t.jsx("div",{className:"action-buttons",children:t.jsxs("button",{className:"btn btn-primary",children:[t.jsx("i",{className:"fas fa-plus"})," Generate Report"]})})]}),o?t.jsxs("div",{className:"loading-state",children:[t.jsx("i",{className:"fas fa-spinner fa-spin"}),t.jsx("p",{children:"Loading reports..."})]}):t.jsxs("div",{className:"reports-grid",children:[t.jsxs("div",{className:"stats-row",children:[t.jsxs("div",{className:"stat-card",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-file-alt"})}),t.jsxs("div",{className:"stat-content",children:[t.jsx("h3",{children:s.length}),t.jsx("p",{children:"Total Reports"})]})]}),t.jsxs("div",{className:"stat-card",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-check-circle"})}),t.jsxs("div",{className:"stat-content",children:[t.jsx("h3",{children:s.filter(m=>m.status==="completed").length}),t.jsx("p",{children:"Completed"})]})]}),t.jsxs("div",{className:"stat-card",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-edit"})}),t.jsxs("div",{className:"stat-content",children:[t.jsx("h3",{children:s.filter(m=>m.status==="draft").length}),t.jsx("p",{children:"Drafts"})]})]})]}),t.jsxs("div",{className:"reports-list",children:[t.jsx("h3",{style:{marginBottom:"1rem",color:"#333"},children:"Recent Reports"}),s.length===0?t.jsxs("div",{className:"empty-state",children:[t.jsx("i",{className:"fas fa-file-alt",style:{fontSize:"48px",color:"#dee2e6"}}),t.jsx("h3",{children:"No reports available"}),t.jsx("p",{children:"Generate your first threat intelligence report."}),t.jsxs("button",{className:"btn btn-primary",children:[t.jsx("i",{className:"fas fa-plus"})," Generate Report"]})]}):t.jsx("div",{className:"reports-table",children:t.jsxs("table",{children:[t.jsx("thead",{children:t.jsxs("tr",{children:[t.jsx("th",{children:"Report Title"}),t.jsx("th",{children:"Type"}),t.jsx("th",{children:"Date"}),t.jsx("th",{children:"Status"}),t.jsx("th",{children:"Actions"})]})}),t.jsx("tbody",{children:s.map(m=>t.jsxs("tr",{children:[t.jsx("td",{children:t.jsxs("div",{className:"report-info",children:[t.jsx("div",{className:"report-title",children:m.title}),t.jsx("div",{className:"report-description",children:m.description})]})}),t.jsx("td",{children:t.jsx("span",{className:"report-type",children:m.type})}),t.jsx("td",{children:m.date}),t.jsx("td",{children:t.jsx("span",{className:`status-badge ${m.status}`,children:m.status})}),t.jsx("td",{children:t.jsxs("div",{className:"actions",children:[t.jsx("button",{className:"btn btn-sm btn-outline",children:t.jsx("i",{className:"fas fa-eye"})}),t.jsx("button",{className:"btn btn-sm btn-outline",children:t.jsx("i",{className:"fas fa-download"})})]})})]},m.id))})]})})]})]})]}):null}function S2(){return t.jsx("style",{children:`
        :root {
            --primary-blue: #0056b3;
            --secondary-blue: #007bff;
            --light-blue: #e8f4ff;
            --accent-blue: #00a0e9;
            --dark-blue: #003366;
            --white: #ffffff;
            --light-gray: #f5f7fa;
            --medium-gray: #e2e8f0;
            --text-dark: #2d3748;
            --text-muted: #718096;
            --danger: #e53e3e;
            --success: #38a169;
            --warning: #f6ad55;
            --info: #4299e1;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background-color: var(--light-gray);
            color: var(--text-dark);
            min-height: 100vh;
            overscroll-behavior: none;
        }
        
        /* Loading Screen */
        .loading-screen, .login-screen {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            background: linear-gradient(135deg, #0056b3, #004494);
            color: white;
            text-align: center;
        }
        
        .login-container {
            background: rgba(255, 255, 255, 0.1);
            padding: 2rem;
            border-radius: 12px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        }
        
        .login-container h2 {
            margin-bottom: 0.5rem;
            font-size: 28px;
            font-weight: 600;
        }
        
        .login-container p {
            margin-bottom: 2rem;
            opacity: 0.9;
        }
        
        .login-container .btn {
            padding: 12px 24px;
            font-size: 16px;
            font-weight: 600;
        }
        
        .loading-spinner {
            width: 50px;
            height: 50px;
            border: 4px solid rgba(255, 255, 255, 0.3);
            border-top: 4px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }
        
        .loading-screen h2 {
            margin-bottom: 10px;
            font-size: 28px;
            font-weight: 600;
        }
        
        .loading-screen p {
            font-size: 16px;
            opacity: 0.8;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        /* Header */
        header {
            background-color: var(--white);
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--primary-blue);
            text-decoration: none;
        }
        
        .logo-icon {
            font-size: 24px;
            background-color: var(--primary-blue);
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .logo-text {
            font-weight: 700;
            font-size: 22px;
        }
        
        .nav-actions {
            display: flex;
            align-items: center;
            gap: 16px;
        }
        
        .search-bar {
            position: relative;
        }
        
        .search-bar input {
            padding: 8px 12px 8px 36px;
            border-radius: 6px;
            border: 1px solid var(--medium-gray);
            width: 240px;
            background-color: white;
            font-size: 14px;
            transition: all 0.3s;
        }
        
        .search-bar input:focus {
            width: 280px;
            outline: none;
            border-color: var(--secondary-blue);
            background-color: var(--white);
        }
        
        .search-icon {
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
        }
        
        .notifications {
            position: relative;
            cursor: pointer;
        }
        
        .notification-count {
            position: absolute;
            top: -5px;
            right: -5px;
            background-color: var(--danger);
            color: white;
            font-size: 10px;
            font-weight: 700;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .user-profile {
            display: flex;
            align-items: center;
            gap: 10px;
            cursor: pointer;
        }
        
        .avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background-color: var(--primary-blue);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 16px;
        }
        
        .user-info {
            display: flex;
            flex-direction: column;
        }
        
        .user-name {
            font-weight: 600;
            font-size: 14px;
        }
        
        .user-role {
            font-size: 12px;
            color: var(--text-muted);
        }
        
        /* Main Navigation */
        nav.main-nav {
            background-color: var(--primary-blue);
            padding: 0;
        }
        
        .nav-container {
            display: flex;
            justify-content: space-between;
        }
        
        .nav-links {
            display: flex;
            list-style: none;
        }
        
        .nav-links li {
            position: relative;
        }
        
        .nav-links a {
            color: var(--white);
            text-decoration: none;
            padding: 16px 20px;
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 500;
            transition: background-color 0.3s;
            position: relative;
            cursor: pointer;
        }
        
        .nav-links a:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }
        
        .nav-links a.active {
            background-color: rgba(255, 255, 255, 0.2);
        }
        
        .nav-links a.active::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background-color: var(--accent-blue);
        }
        
        .nav-right {
            display: flex;
            align-items: center;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 6px;
            color: var(--white);
            padding: 0 20px;
            font-size: 14px;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: var(--success);
        }
        
        /* User Profile Dropdown */
        .user-profile-container {
            position: relative;
            margin-left: 20px;
        }
        
        .user-profile {
            display: flex;
            align-items: center;
            gap: 10px;
            background: var(--primary-blue);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 25px;
            padding: 8px 15px;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
        }
        
        .user-profile:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-1px);
        }
        
        .avatar {
            width: 32px;
            height: 32px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 14px;
        }
        
        .user-info {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            gap: 2px;
        }
        
        .user-name {
            font-weight: 600;
            font-size: 14px;
            color: white;
        }
        
        .user-role {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.8);
        }
        
        .user-profile i {
            font-size: 12px;
            transition: transform 0.3s ease;
        }
        
        .user-profile.open i {
            transform: rotate(180deg);
        }
        
        .user-menu-dropdown {
            position: absolute;
            top: 100%;
            right: 0;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            min-width: 280px;
            z-index: 1000;
            margin-top: 5px;
            overflow: hidden;
            animation: dropdownFadeIn 0.2s ease-out;
        }
        
        @keyframes dropdownFadeIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .dropdown-header {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 20px;
            background: linear-gradient(135deg, #0056b3, #004494);
            color: white;
        }
        
        .user-avatar-large {
            width: 50px;
            height: 50px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 18px;
        }
        
        .user-name-large {
            font-weight: 600;
            font-size: 16px;
            margin-bottom: 4px;
        }
        
        .user-email {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .menu-divider {
            height: 1px;
            background: #e9ecef;
        }
        
        .menu-items {
            padding: 10px 0;
        }
        
        .menu-item {
            width: 100%;
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 20px;
            background: none;
            border: none;
            color: #333;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 14px;
            text-align: left;
        }
        
        .menu-item:hover {
            background: #f8f9fa;
            color: #0056b3;
        }
        
        .menu-item i {
            width: 16px;
            text-align: center;
        }
        
        .menu-item-submenu {
            position: relative;
        }
        
        .submenu-arrow {
            margin-left: auto !important;
            font-size: 12px;
            transition: transform 0.3s ease;
        }
        
        .submenu {
            background: #f8f9fa;
            border-left: 3px solid #0056b3;
        }
        
        .submenu-item {
            width: 100%;
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 20px 10px 40px;
            background: none;
            border: none;
            color: #555;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 13px;
            text-align: left;
        }
        
        .submenu-item:hover {
            background: #e9ecef;
            color: #0056b3;
        }
        
        .submenu-item i {
            width: 14px;
            text-align: center;
        }
        
        .logout-item {
            color: #dc3545 !important;
        }
        
        .logout-item:hover {
            background: #f8d7da !important;
            color: #721c24 !important;
        }
        
        /* Main Content */
        .main-content {
            padding: 30px 0;
        }
        
        /* Page Section */
        .page-section {
            display: none;
        }
        
        .page-section.active {
            display: block;
        }
        
        /* Dashboard Header */
        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
        }
        
        .page-title {
            font-size: 24px;
            font-weight: 600;
            color: var(--dark-blue);
        }
        
        .page-subtitle {
            color: var(--text-muted);
            margin-top: 4px;
            font-size: 15px;
        }
        
        .action-buttons {
            display: flex;
            gap: 12px;
        }
        
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 10px 16px;
            border-radius: 6px;
            font-weight: 500;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
            border: none;
        }
        
        .btn-primary {
            background-color: var(--primary-blue);
            color: white;
        }
        
        .btn-primary:hover {
            background-color: var(--dark-blue);
        }
        
        .btn-secondary {
            background-color: var(--secondary-blue);
            color: white;
        }
        
        .btn-secondary:hover {
            background-color: var(--primary-blue);
        }
        
        .btn-outline {
            background-color: transparent;
            border: 1px solid var(--primary-blue);
            color: var(--primary-blue);
        }
        
        .btn-outline:hover {
            background-color: var(--light-blue);
        }
        
        .btn-danger {
            background-color: var(--danger);
            color: white;
        }
        
        .btn-danger:hover {
            background-color: #c53030;
        }
        
        .btn-sm {
            padding: 6px 12px;
            font-size: 13px;
        }
        
        /* Stats Cards */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background-color: var(--white);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        }
        
        .stat-title {
            color: var(--text-muted);
            font-size: 14px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .stat-icon {
            width: 28px;
            height: 28px;
            background-color: var(--light-blue);
            color: var(--primary-blue);
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .stat-value {
            font-size: 28px;
            font-weight: 700;
            color: var(--dark-blue);
            margin-bottom: 5px;
        }
        
        .stat-change {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 14px;
        }
        
        .increase {
            color: var(--success);
        }
        
        .decrease {
            color: var(--danger);
        }
        
        /* Main Grid */
        .main-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 24px;
        }
        
        .card {
            background-color: var(--white);
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            overflow: hidden;
            margin-bottom: 24px;
        }
        
        .card:last-child {
            margin-bottom: 0;
        }
        
        .card-header {
            padding: 16px 20px;
            border-bottom: 1px solid var(--medium-gray);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .card-title {
            font-size: 18px;
            font-weight: 600;
            color: var(--dark-blue);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .card-icon {
            color: var(--primary-blue);
        }
        
        .card-actions {
            display: flex;
            gap: 12px;
        }
        
        .card-content {
            padding: 20px;
        }
        
        /* Tables */
        .data-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .data-table th, 
        .data-table td {
            padding: 12px 15px;
            text-align: left;
        }
        
        .data-table th {
            background-color: var(--light-gray);
            color: var(--text-muted);
            font-weight: 600;
            font-size: 14px;
        }
        
        .data-table tbody tr {
            border-bottom: 1px solid var(--medium-gray);
        }
        
        .data-table tbody tr:last-child {
            border-bottom: none;
        }
        
        .data-table tbody tr:hover {
            background-color: var(--light-blue);
        }
        
        /* Badge Styles */
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .badge-high {
            background-color: rgba(229, 62, 62, 0.1);
            color: var(--danger);
        }
        
        .badge-medium {
            background-color: rgba(246, 173, 85, 0.1);
            color: var(--warning);
        }
        
        .badge-low {
            background-color: rgba(56, 161, 105, 0.1);
            color: var(--success);
        }
        
        .badge-active {
            background-color: rgba(56, 161, 105, 0.1);
            color: var(--success);
        }
        
        .badge-inactive {
            background-color: rgba(113, 128, 150, 0.1);
            color: var(--text-muted);
        }
        
        .badge-connected {
            background-color: rgba(66, 153, 225, 0.1);
            color: var(--info);
        }
        
        .badge-tags {
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
        }
        
        /* Filter Section */
        .filters-section {
            background-color: var(--light-gray);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 20px;
        }
        
        .filters-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 16px;
        }
        
        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .filter-label {
            font-size: 13px;
            font-weight: 600;
            color: var(--text-muted);
        }
        
        .filter-control {
            display: flex;
            gap: 10px;
        }
        
        .filter-control select,
        .filter-control input {
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid var(--medium-gray);
            font-size: 14px;
            background-color: white;
            flex: 1;
        }
        
        .filter-control select:focus,
        .filter-control input:focus {
            outline: none;
            border-color: var(--secondary-blue);
        }
        
        /* Organisations List */
        .organisation-list {
            list-style: none;
        }
        
        .organisation-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 0;
            border-bottom: 1px solid var(--medium-gray);
        }
        
        .organisation-item:last-child {
            border-bottom: none;
        }
        
        .organisation-logo {
            width: 40px;
            height: 40px;
            border-radius: 8px;
            background-color: var(--light-blue);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--primary-blue);
            font-weight: 600;
        }
        
        .organisation-details {
            flex: 1;
        }
        
        .organisation-name {
            font-weight: 600;
            margin-bottom: 2px;
        }
        
        .organisation-meta {
            font-size: 13px;
            color: var(--text-muted);
        }
        
        .organisation-stats {
            display: flex;
            gap: 15px;
            margin-top: 5px;
        }
        
        .stat-item {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 13px;
        }
        
        .stat-item i {
            color: var(--primary-blue);
        }
        
        .trust-level {
            width: 80px;
            height: 6px;
            background-color: var(--medium-gray);
            border-radius: 3px;
        }
        
        .trust-fill {
            height: 100%;
            border-radius: 3px;
            background-color: var(--primary-blue);
        }
        
        /* Activity Stream */
        .activity-stream {
            list-style: none;
        }
        
        .activity-item {
            padding: 15px;
            display: flex;
            gap: 15px;
            border-bottom: 1px solid var(--medium-gray);
            background-color: white;
            border-radius: 8px;
            margin-bottom: 8px;
            transition: all 0.2s ease;
        }
        
        .activity-item:hover {
            background-color: var(--light-blue);
            transform: translateX(4px);
            box-shadow: 0 2px 8px rgba(0, 123, 255, 0.1);
        }
        
        .activity-item:last-child {
            border-bottom: none;
        }
        
        .activity-icon {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background-color: var(--light-blue);
            color: var(--primary-blue);
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        
        .activity-details {
            flex: 1;
        }
        
        .activity-text {
            margin-bottom: 5px;
            line-height: 1.4;
        }
        
        .activity-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .activity-time {
            font-size: 13px;
            color: var(--text-muted);
        }
        
        /* MITRE ATT&CK Matrix */
        .matrix-container {
            overflow-x: auto;
        }
        
        .mitre-matrix {
            min-width: 900px;
            border-collapse: collapse;
        }
        
        .mitre-matrix th {
            background-color: var(--primary-blue);
            color: white;
            padding: 12px;
            text-align: center;
            font-size: 14px;
        }
        
        .matrix-cell {
            width: 100px;
            height: 60px;
            border: 1px solid var(--medium-gray);
            padding: 10px;
            font-size: 12px;
            vertical-align: top;
            position: relative;
            transition: all 0.3s;
        }
        
        .matrix-cell:hover {
            background-color: var(--light-blue);
        }
        
        .matrix-cell.active {
            background-color: rgba(0, 86, 179, 0.1);
        }
        
        .technique-count {
            position: absolute;
            top: 5px;
            right: 5px;
            background-color: var(--primary-blue);
            color: white;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
        }

        .tactic-count {
            font-size: 11px;
            color: rgba(255, 255, 255, 0.8);
            font-weight: normal;
            margin-top: 2px;
        }

        .technique-name {
            font-weight: 500;
            margin-bottom: 4px;
            line-height: 1.2;
        }

        .technique-id {
            font-size: 10px;
            color: var(--primary-blue);
            font-weight: bold;
            background-color: rgba(0, 86, 179, 0.1);
            padding: 2px 4px;
            border-radius: 3px;
            display: inline-block;
        }

        .empty-cell {
            color: #ccc;
            font-size: 18px;
            text-align: center;
        }

        .matrix-stats {
            font-size: 14px;
        }

        .matrix-stats strong {
            color: var(--primary-blue);
        }

        /* TTP Detail Modal */
        .ttp-modal {
            max-width: 900px;
            width: 90vw;
            max-height: 90vh;
            overflow-y: auto;
        }

        .ttp-detail-content {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        .ttp-header-section {
            border-bottom: 1px solid var(--medium-gray);
            padding-bottom: 1rem;
        }

        .ttp-title-section {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .ttp-title {
            margin: 0;
            color: var(--primary-blue);
            font-size: 1.5rem;
        }

        .ttp-name-input {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--primary-blue);
        }

        .ttp-badges {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }

        .ttp-details-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }

        @media (min-width: 768px) {
            .ttp-details-grid {
                grid-template-columns: 1fr 1fr;
            }
        }

        .detail-section {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 1rem;
        }

        .detail-section h4 {
            margin: 0 0 1rem 0;
            color: var(--primary-blue);
            font-size: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .detail-row {
            display: flex;
            flex-direction: column;
            margin-bottom: 1rem;
        }

        .detail-row:last-child {
            margin-bottom: 0;
        }

        .detail-row label {
            font-weight: 600;
            color: #555;
            margin-bottom: 0.25rem;
            font-size: 0.9rem;
        }

        .detail-value {
            color: #333;
        }

        .detail-value p {
            margin: 0;
            line-height: 1.5;
        }

        .technique-id-display {
            background: rgba(0, 86, 179, 0.1);
            color: var(--primary-blue);
            padding: 4px 8px;
            border-radius: 4px;
            font-family: monospace;
            font-weight: bold;
        }

        .feed-info {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .feed-name {
            font-weight: 600;
        }

        .feed-type {
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 500;
        }

        .feed-type.external {
            background: #e3f2fd;
            color: #1976d2;
        }

        .feed-type.internal {
            background: #f3e5f5;
            color: #7b1fa2;
        }

        .no-data {
            color: #999;
            font-style: italic;
        }

        .detail-value code {
            background: #f1f3f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.9rem;
        }

        /* Badge styles for TTP modal */
        .badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 500;
        }

        .badge-primary {
            background: var(--primary-blue);
            color: white;
        }

        .badge-secondary {
            background: #6c757d;
            color: white;
        }

        .badge-info {
            background: #17a2b8;
            color: white;
        }

        /* TTP Creation Modal */
        .ttp-create-modal {
            max-width: 800px;
            width: 90vw;
            max-height: 85vh;
            overflow-y: auto;
        }

        /* Delete Confirmation Modal */
        .delete-modal {
            max-width: 500px;
            width: 90vw;
        }

        .delete-confirmation p {
            font-size: 1.1rem;
            margin-bottom: 1.5rem;
            color: #333;
        }

        .warning-text {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 4px;
            padding: 1rem;
            margin: 1.5rem 0;
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            color: #856404;
        }

        .warning-text i {
            color: #f39c12;
            font-size: 1.1rem;
            margin-top: 0.1rem;
            flex-shrink: 0;
        }

        .feed-info {
            background: #f8f9fa;
            border-radius: 6px;
            padding: 1rem;
            margin-top: 1.5rem;
            border: 1px solid #e9ecef;
        }

        .info-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0;
            border-bottom: 1px solid #dee2e6;
        }

        .info-row:last-child {
            border-bottom: none;
        }

        .info-row strong {
            color: #495057;
            font-weight: 600;
        }

        .create-form-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }

        @media (min-width: 768px) {
            .create-form-grid {
                grid-template-columns: 1fr 1fr;
            }
        }

        .form-section {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 1.5rem;
            border: 1px solid #e9ecef;
        }

        .form-section h4 {
            margin: 0 0 1.5rem 0;
            color: var(--primary-blue);
            font-size: 1.1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            border-bottom: 1px solid #dee2e6;
            padding-bottom: 0.5rem;
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-group:last-child {
            margin-bottom: 0;
        }
        
        .form-row {
            display: flex;
            gap: 1rem;
        }
        
        .form-row .form-group {
            flex: 1;
        }

        .form-label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: #333;
            font-size: 0.9rem;
        }

        .required {
            color: #dc3545;
            font-weight: bold;
        }

        .form-control {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 0.9rem;
            background-color: white;
            transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
        }

        .form-control:focus {
            outline: 0;
            border-color: var(--primary-blue);
            box-shadow: 0 0 0 0.2rem rgba(0, 86, 179, 0.25);
        }

        .form-control.error {
            border-color: #dc3545;
        }

        .form-control.error:focus {
            border-color: #dc3545;
            box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25);
        }

        .error-text {
            display: block;
            margin-top: 0.25rem;
            font-size: 0.8rem;
            color: #dc3545;
        }

        .form-help {
            display: block;
            margin-top: 0.25rem;
            font-size: 0.8rem;
            color: #6c757d;
            font-style: italic;
        }

        .form-actions {
            display: flex;
            justify-content: flex-end;
            gap: 1rem;
            margin-top: 2rem;
            padding-top: 1.5rem;
            border-top: 1px solid #e9ecef;
        }

        .form-actions .btn {
            min-width: 120px;
            padding: 0.75rem 1.5rem;
        }

        /* Responsive adjustments for create modal */
        @media (max-width: 767px) {
            .create-form-grid {
                grid-template-columns: 1fr;
            }
            
            .form-actions {
                flex-direction: column;
            }
            
            .form-actions .btn {
                width: 100%;
            }
        }
        
        /* Reports Section */
        .report-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }
        
        .report-card {
            background-color: var(--white);
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .report-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        }
        
        .report-header {
            padding: 20px;
            background-color: var(--light-blue);
            border-bottom: 1px solid var(--medium-gray);
        }
        
        .report-type {
            display: inline-block;
            padding: 4px 10px;
            background-color: var(--primary-blue);
            color: white;
            font-size: 12px;
            font-weight: 600;
            border-radius: 20px;
            margin-bottom: 10px;
        }
        
        .report-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 5px;
            color: var(--dark-blue);
        }
        
        .report-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: var(--text-muted);
            font-size: 13px;
        }
        
        .report-content {
            padding: 20px;
        }
        
        .report-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .report-stat {
            text-align: center;
        }
        
        .stat-number {
            font-size: 24px;
            font-weight: 700;
            color: var(--dark-blue);
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 13px;
            color: var(--text-muted);
        }
        
        .report-actions {
            display: flex;
            justify-content: space-between;
            margin-top: 15px;
        }
        
        /* Feed Items */
        .feed-items {
            list-style: none;
        }
        
        .feed-item {
            display: flex;
            gap: 16px;
            padding: 16px 0;
            border-bottom: 1px solid var(--medium-gray);
        }
        
        .feed-item:last-child {
            border-bottom: none;
        }
        
        .feed-icon {
            width: 48px;
            height: 48px;
            border-radius: 8px;
            background-color: var(--light-blue);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--primary-blue);
            font-size: 20px;
            flex-shrink: 0;
        }
        
        .feed-details {
            flex: 1;
        }
        
        .feed-name {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 5px;
            color: var(--dark-blue);
        }
        
        .feed-description {
            color: var(--text-muted);
            font-size: 14px;
            margin-bottom: 8px;
        }
        
        .feed-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 13px;
        }
        
        .feed-stats {
            display: flex;
            gap: 15px;
        }
        
        .feed-badges {
            display: flex;
            gap: 8px;
        }
        
        /* Pagination */
        .pagination {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 5px;
            margin-top: 20px;
        }
        
        .page-item {
            width: 32px;
            height: 32px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .page-item:hover:not(.disabled) {
            background-color: var(--light-blue);
        }
        
        .page-item.active {
            background-color: var(--primary-blue);
            color: white;
        }

        .page-item.disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .tab {
            cursor: pointer;
        }
        
        /* Chart Containers */
        .chart-container {
            height: 300px;
            position: relative;
        }
        
        /* Tabs */
        .tabs {
            display: flex;
            border-bottom: 1px solid var(--medium-gray);
            margin-bottom: 20px;
        }
        
        .tab {
            padding: 12px 20px;
            font-size: 14px;
            font-weight: 600;
            color: var(--text-muted);
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }
        
        .tab:hover {
            color: var(--primary-blue);
        }
        
        .tab.active {
            color: var(--primary-blue);
            border-bottom-color: var(--primary-blue);
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        /* Helper classes */
        .text-danger {
            color: var(--danger);
        }
        
        .text-success {
            color: var(--success);
        }
        
        .text-warning {
            color: var(--warning);
        }
        
        .text-muted {
            color: var(--text-muted);
        }
        
        .mt-4 {
            margin-top: 16px;
        }
        
        .mb-4 {
            margin-bottom: 16px;
        }
        
        /* Responsive Design */
        @media (max-width: 1200px) {
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .report-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (max-width: 992px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
        }
        
        @media (max-width: 768px) {
            .nav-links a {
                padding: 16px 10px;
                font-size: 14px;
            }
            
            .search-bar input {
                width: 160px;
            }
            
            .search-bar input:focus {
                width: 200px;
            }
            
            .status-indicator {
                display: none;
            }
            
            .report-grid {
                grid-template-columns: 1fr;
            }
        }
        
        @media (max-width: 576px) {
            .header-container {
                flex-direction: column;
                gap: 15px;
            }
            
            .nav-actions {
                width: 100%;
                justify-content: center;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .page-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 15px;
            }
        }

        /* Modal Styles */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }

        .modal-content {
            background: white;
            border-radius: 8px;
            width: 90%;
            max-width: 600px;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }

        .modal-header {
            padding: 1.5rem;
            border-bottom: 1px solid var(--medium-gray);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .modal-header h2 {
            margin: 0;
            color: var(--text-dark);
            font-size: 1.25rem;
        }

        .modal-close {
            background: none;
            border: none;
            font-size: 1.2rem;
            cursor: pointer;
            color: var(--text-muted);
            padding: 0.5rem;
            border-radius: 4px;
            transition: background-color 0.2s;
        }

        .modal-close:hover {
            background-color: var(--medium-gray);
        }

        .modal-body {
            padding: 1.5rem;
        }

        .form-group {
            margin-bottom: 1rem;
        }

        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            color: var(--text-dark);
            font-weight: 500;
        }

        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid var(--medium-gray);
            border-radius: 4px;
            font-size: 0.875rem;
            transition: border-color 0.2s;
        }

        .form-group input:focus,
        .form-group textarea:focus,
        .form-group select:focus {
            outline: none;
            border-color: var(--secondary-blue);
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }

        .checkbox-label {
            display: flex !important;
            align-items: center;
            gap: 0.5rem;
            cursor: pointer;
        }

        /* Profile Styles */
        .profile-content {
            max-width: 800px;
            margin: 0 auto;
        }

        .profile-card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }

        .profile-header {
            background: linear-gradient(135deg, #0056b3, #004494);
            color: white;
            padding: 2rem;
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }

        .profile-avatar {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
        }

        .profile-info h3 {
            margin: 0 0 0.5rem 0;
            font-size: 1.5rem;
            font-weight: 600;
        }

        .profile-role {
            margin: 0;
            opacity: 0.9;
            font-size: 1rem;
            text-transform: uppercase;
            font-weight: 500;
            letter-spacing: 0.5px;
        }

        .profile-details {
            padding: 2rem;
        }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
        }

        .info-item {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .info-item label {
            font-weight: 600;
            color: #666;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .info-item span {
            font-size: 1rem;
            color: #333;
            padding: 0.5rem 0;
            border-bottom: 1px solid #eee;
        }

        .role-badge {
            display: inline-block;
            padding: 0.5rem 1rem !important;
            border-radius: 20px;
            font-size: 0.875rem !important;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border: none !important;
        }

        .role-badge.bluevisionadmin {
            background: #d4edda;
            color: #155724;
        }

        .role-badge.admin {
            background: #fff3cd;
            color: #856404;
        }

        .role-badge.publisher {
            background: #cce5ff;
            color: #004085;
        }

        .role-badge.viewer {
            background: #f8f9fa;
            color: #495057;
        }

        .edit-form {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        .form-actions {
            display: flex;
            gap: 1rem;
            justify-content: flex-end;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #eee;
        }

        .checkbox-label input[type="checkbox"] {
            width: auto !important;
            margin: 0;
        }

        .modal-footer {
            display: flex;
            gap: 1rem;
            justify-content: flex-end;
            margin-top: 1.5rem;
        }

        /* Additional styles for Add IoC Modal */
        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin-bottom: 1rem;
        }

        .form-label {
            display: block;
            margin-bottom: 0.5rem;
            color: var(--text-dark);
            font-weight: 500;
            font-size: 0.875rem;
        }

        .form-control {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid var(--medium-gray);
            border-radius: 6px;
            font-size: 0.875rem;
            background-color: white;
            transition: all 0.2s;
            box-sizing: border-box;
        }

        .form-control:focus {
            outline: none;
            border-color: var(--primary-blue);
            box-shadow: 0 0 0 3px rgba(52, 144, 220, 0.1);
        }

        .form-control.error {
            border-color: #dc3545;
        }

        .form-control.error:focus {
            border-color: #dc3545;
            box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1);
        }

        .form-range {
            width: 100%;
            -webkit-appearance: none;
            appearance: none;
            height: 6px;
            border-radius: 3px;
            background: var(--medium-gray);
            outline: none;
            margin: 0.5rem 0;
        }

        .form-range::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: var(--primary-blue);
            cursor: pointer;
            transition: background 0.2s;
        }

        .form-range::-webkit-slider-thumb:hover {
            background: var(--secondary-blue);
        }

        .form-range::-moz-range-thumb {
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: var(--primary-blue);
            cursor: pointer;
            border: none;
        }

        .range-labels {
            display: flex;
            justify-content: space-between;
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 0.25rem;
        }

        .error-text {
            color: #dc3545;
            font-size: 0.75rem;
            margin-top: 0.25rem;
            display: block;
        }

        .modal-actions {
            display: flex;
            gap: 1rem;
            justify-content: flex-end;
            margin-top: 1.5rem;
            padding-top: 1rem;
            border-top: 1px solid var(--medium-gray);
        }

        .export-info {
            margin: 1.5rem 0;
        }

        .info-card {
            display: flex;
            gap: 1rem;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 4px solid var(--primary-blue);
        }

        .info-card i {
            color: var(--primary-blue);
            font-size: 1.25rem;
            margin-top: 0.25rem;
        }

        .info-card p {
            margin: 0.5rem 0;
            font-size: 0.875rem;
            color: var(--text-muted);
        }

        .info-card strong {
            color: var(--text-dark);
        }

        /* Export Modal Styles */
        .export-modal {
            width: 90%;
            max-width: 800px;
            max-height: 90vh;
            overflow-y: auto;
        }

        .format-options {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }

        .format-option {
            cursor: pointer;
            position: relative;
        }

        .format-option input[type="radio"] {
            position: absolute;
            opacity: 0;
            pointer-events: none;
        }

        .format-card {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.5rem;
            padding: 1.5rem 1rem;
            border: 2px solid var(--light-gray);
            border-radius: 8px;
            background: white;
            transition: all 0.2s ease;
            text-align: center;
        }

        .format-option:hover .format-card {
            border-color: var(--primary-blue);
            box-shadow: 0 2px 8px rgba(52, 152, 219, 0.15);
        }

        .format-option input[type="radio"]:checked + .format-card {
            border-color: var(--primary-blue);
            background: #f8f9fa;
            box-shadow: 0 2px 8px rgba(52, 152, 219, 0.2);
        }

        .format-card i {
            font-size: 2rem;
            color: var(--text-muted);
            transition: color 0.2s ease;
        }

        .format-option:hover .format-card i,
        .format-option input[type="radio"]:checked + .format-card i {
            color: var(--primary-blue);
        }

        .format-card span {
            font-weight: 600;
            color: var(--text-dark);
            font-size: 1rem;
        }

        .format-card small {
            color: var(--text-muted);
            font-size: 0.75rem;
        }

        .form-section {
            margin: 2rem 0;
            padding: 1.5rem;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid var(--primary-blue);
        }

        .form-section h4 {
            margin: 0 0 1rem 0;
            color: var(--text-dark);
            font-size: 1.1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .form-section h4 i {
            color: var(--primary-blue);
        }

        .checkbox-group {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .checkbox-label {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            cursor: pointer;
            font-size: 0.875rem;
        }

        .checkbox-label input[type="checkbox"] {
            width: 16px;
            height: 16px;
            accent-color: var(--primary-blue);
        }

        .checkbox-label span {
            color: var(--text-dark);
        }

        .form-help {
            display: block;
            margin-top: 0.25rem;
            font-size: 0.75rem;
            color: var(--text-muted);
            font-style: italic;
        }

        .alert {
            padding: 1rem;
            border-radius: 6px;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .alert-error {
            background: #ffeaea;
            border: 1px solid #ffb3b3;
            color: #d8000c;
        }

        .alert-error i {
            color: #d8000c;
        }

        @media (max-width: 768px) {
            .modal-content {
                width: 95%;
                margin: 1rem;
            }
            
            .form-row {
                grid-template-columns: 1fr;
            }

            .form-grid {
                grid-template-columns: 1fr;
            }

            .modal-actions {
                flex-direction: column;
            }
        }

        /* Feed Consumption Controls */
        .feed-consumption-controls {
            display: flex;
            align-items: flex-start;
            gap: 1rem;
            margin-right: 1rem;
        }

        .feed-selection-wrapper {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            min-width: 280px;
        }

        .feed-selector {
            font-size: 0.875rem;
            padding: 0.5rem 0.75rem;
            border: 1px solid #ddd;
            border-radius: 6px;
            background: white;
            color: var(--text-dark);
            transition: border-color 0.2s ease;
        }

        .feed-selector:focus {
            outline: none;
            border-color: var(--primary-blue);
            box-shadow: 0 0 0 2px rgba(0, 86, 179, 0.1);
        }

        .feed-selector:disabled {
            background-color: #f5f5f5;
            cursor: not-allowed;
            opacity: 0.6;
        }

        .consumption-options {
            margin-top: 0.25rem;
        }

        .consumption-info {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--text-muted);
            font-size: 0.75rem;
            padding: 0.25rem 0.5rem;
            background: rgba(0, 86, 179, 0.05);
            border-radius: 4px;
            border: 1px solid rgba(0, 86, 179, 0.1);
        }

        .consumption-info i {
            color: var(--primary-blue);
            font-size: 0.7rem;
        }

        .consume-btn {
            align-self: flex-start;
            white-space: nowrap;
            padding: 0.5rem 1rem;
            min-height: 36px;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .consume-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        /* Feed Analysis Overview Styles */
        .feed-analysis-overview {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        .overview-cards {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 1.5rem;
        }

        .feed-comparison-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
        }

        .feed-stat-card {
            padding: 1rem;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: white;
            transition: box-shadow 0.2s ease;
        }

        .feed-stat-card:hover {
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .feed-name {
            font-weight: 600;
            color: var(--text-dark);
            margin-bottom: 0.75rem;
            font-size: 0.95rem;
        }

        .feed-stats {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.75rem;
        }

        .feed-stats .stat-item {
            text-align: center;
        }

        .feed-stats .stat-value {
            display: block;
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--primary-blue);
        }

        .feed-stats .stat-label {
            display: block;
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 0.25rem;
        }

        .feed-type {
            padding: 0.25rem 0.5rem;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .feed-type.external {
            background: rgba(255, 193, 7, 0.1);
            color: #ff8800;
            border: 1px solid rgba(255, 193, 7, 0.3);
        }

        .feed-type.internal {
            background: rgba(40, 167, 69, 0.1);
            color: #28a745;
            border: 1px solid rgba(40, 167, 69, 0.3);
        }

        /* Technique Frequency List */
        .technique-frequency-list {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .frequency-item {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 0.75rem;
            border: 1px solid #eee;
            border-radius: 6px;
            background: #fafafa;
        }

        .technique-rank {
            font-weight: 700;
            color: var(--primary-blue);
            min-width: 30px;
            text-align: center;
        }

        .technique-details {
            flex: 1;
        }

        .technique-id {
            font-weight: 600;
            color: var(--text-dark);
            margin-bottom: 0.25rem;
        }

        .technique-stats {
            font-size: 0.75rem;
            color: var(--text-muted);
        }

        .frequency-bar {
            flex: 0 0 100px;
            height: 8px;
            background: #eee;
            border-radius: 4px;
            overflow: hidden;
        }

        .frequency-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary-blue), #4CAF50);
            transition: width 0.3s ease;
        }

        /* Seasonal Analysis */
        .seasonal-analysis {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .seasonal-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 1rem;
        }

        .seasonal-stats .stat-card {
            text-align: center;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #ddd;
        }

        .seasonal-stats .stat-card .stat-value {
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--primary-blue);
        }

        .seasonal-stats .stat-card .stat-label {
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 0.5rem;
        }

        .seasonal-interpretation {
            padding: 1rem;
            background: rgba(0, 86, 179, 0.05);
            border-left: 4px solid var(--primary-blue);
            border-radius: 0 8px 8px 0;
        }

        .seasonal-interpretation p {
            margin: 0;
            color: var(--text-dark);
            font-size: 0.875rem;
            line-height: 1.5;
        }

        /* Intelligence Status Badges */
        .status-badge {
            padding: 0.25rem 0.5rem;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
        }

        .status-badge.anonymized {
            background: rgba(255, 193, 7, 0.1);
            color: #ff8800;
            border: 1px solid rgba(255, 193, 7, 0.3);
        }

        .status-badge.raw {
            background: rgba(40, 167, 69, 0.1);
            color: #28a745;
            border: 1px solid rgba(40, 167, 69, 0.3);
        }

        .technique-badge, .tactic-badge {
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
            background: rgba(0, 86, 179, 0.1);
            color: var(--primary-blue);
            border: 1px solid rgba(0, 86, 179, 0.2);
        }

        /* Intelligence Summary */
        .intelligence-summary {
            padding: 1rem;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }

        .summary-stats {
            display: flex;
            gap: 2rem;
            align-items: center;
            flex-wrap: wrap;
        }

        .intelligence-summary .summary-stats .stat-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.875rem;
            color: var(--text-dark);
        }

        .intelligence-summary .summary-stats .stat-item i {
            color: var(--primary-blue);
        }

        /* TTP Name Cell */
        .ttp-name-cell .ttp-title {
            font-weight: 500;
            color: var(--text-dark);
            margin-bottom: 0.25rem;
        }

        .ttp-name-cell .ttp-subtechnique {
            font-size: 0.75rem;
            color: var(--text-muted);
            font-style: italic;
        }

        /* Feed Source Cell */
        .feed-source-cell {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }

        .feed-source-cell .feed-name {
            font-weight: 500;
            color: var(--text-dark);
            margin-bottom: 0;
        }

        /* Trends Analysis */
        .trends-analysis {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        .trends-content {
            display: flex;
            flex-direction: column;
            gap: 2rem;
        }

        .trend-charts-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 2rem;
        }

        .chart-container h3, .tactic-distribution h3 {
            margin: 0 0 1rem 0;
            color: var(--text-dark);
            font-size: 1.1rem;
        }

        .tactic-bars {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .tactic-bar-item {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .tactic-label {
            min-width: 120px;
            font-size: 0.75rem;
            font-weight: 500;
            color: var(--text-dark);
            text-transform: capitalize;
        }

        .bar-container {
            flex: 1;
            height: 20px;
            background: #eee;
            border-radius: 10px;
            overflow: hidden;
        }

        .bar-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary-blue), #4CAF50);
            transition: width 0.3s ease;
        }

        .bar-value {
            min-width: 30px;
            text-align: right;
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--text-dark);
        }

        /* Trend Insights */
        .trend-insights h3 {
            margin: 0 0 1rem 0;
            color: var(--text-dark);
            font-size: 1.1rem;
        }

        .insights-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
        }

        .insight-card {
            display: flex;
            align-items: flex-start;
            gap: 1rem;
            padding: 1rem;
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            transition: box-shadow 0.2s ease;
        }

        .insight-card:hover {
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .insight-card i {
            color: var(--primary-blue);
            font-size: 1.5rem;
            margin-top: 0.25rem;
        }

        .insight-card h4 {
            margin: 0 0 0.5rem 0;
            color: var(--text-dark);
            font-size: 0.95rem;
        }

        .insight-card p {
            margin: 0;
            color: var(--text-muted);
            font-size: 0.825rem;
            line-height: 1.4;
        }

        /* Alert improvements */
        .alert {
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 0.875rem;
            line-height: 1.4;
        }

        .alert.alert-success {
            background: rgba(40, 167, 69, 0.1);
            color: #155724;
            border: 1px solid rgba(40, 167, 69, 0.2);
        }

        .alert.alert-error {
            background: rgba(220, 53, 69, 0.1);
            color: #721c24;
            border: 1px solid rgba(220, 53, 69, 0.2);
        }

        .alert i {
            font-size: 1rem;
            flex-shrink: 0;
        }

        @media (max-width: 768px) {
            .feed-consumption-controls {
                flex-direction: column;
                gap: 1rem;
            }

            .feed-selection-wrapper {
                min-width: auto;
            }

            .overview-cards {
                grid-template-columns: 1fr;
            }

            .trend-charts-grid {
                grid-template-columns: 1fr;
            }

            .summary-stats {
                gap: 1rem;
            }
        }

      `})}function T2({active:n}){const[s,l]=N.useState([]),[o,d]=N.useState(!0),[f,m]=N.useState(null);N.useEffect(()=>{n&&setTimeout(()=>{l([{id:"1",type:"threat_alert",title:"New High-Priority Threat Detected",message:"A new malware strain has been identified in your organization's threat feed.",severity:"high",read:!1,created_at:new Date(Date.now()-1800*1e3).toISOString()},{id:"2",type:"trust_request",title:"Trust Relationship Request",message:'Organization "CyberSecure Inc." has requested a bilateral trust relationship.',severity:"medium",read:!1,created_at:new Date(Date.now()-7200*1e3).toISOString()},{id:"3",type:"feed_update",title:"Threat Feed Updated",message:'Your subscribed threat feed "MITRE ATT&CK" has been updated with 15 new indicators.',severity:"low",read:!0,created_at:new Date(Date.now()-14400*1e3).toISOString()}]),d(!1)},500)},[n]);const p=h=>{l(x=>x.map(v=>v.id===h?{...v,read:!0}:v))},g=h=>{l(x=>x.filter(v=>v.id!==h))};return n?t.jsxs("section",{id:"notifications",className:`page-section ${n?"active":""}`,children:[t.jsxs("div",{className:"page-header",children:[t.jsxs("div",{children:[t.jsx("h1",{className:"page-title",children:"Notifications"}),t.jsx("p",{className:"page-subtitle",children:"Stay updated with system alerts and activities"})]}),t.jsx("div",{className:"action-buttons",children:t.jsxs("button",{className:"btn btn-outline",children:[t.jsx("i",{className:"fas fa-check-double"})," Mark All Read"]})})]}),o?t.jsxs("div",{className:"loading-state",children:[t.jsx("i",{className:"fas fa-spinner fa-spin"}),t.jsx("p",{children:"Loading notifications..."})]}):t.jsx("div",{className:"notifications-list",children:s.length===0?t.jsxs("div",{className:"empty-state",children:[t.jsx("i",{className:"fas fa-bell-slash",style:{fontSize:"48px",color:"#dee2e6"}}),t.jsx("h3",{children:"No notifications"}),t.jsx("p",{children:"You're all caught up! No notifications to show."})]}):s.map(h=>t.jsxs("div",{className:`notification-item ${h.read?"":"unread"}`,children:[t.jsxs("div",{className:"notification-content",children:[t.jsxs("div",{className:"notification-header",children:[t.jsx("div",{className:"notification-icon",children:t.jsx("i",{className:h.type==="threat_alert"?"fas fa-exclamation-triangle":h.type==="trust_request"?"fas fa-handshake":"fas fa-rss",style:{color:h.severity==="high"?"#dc3545":h.severity==="medium"?"#ffc107":"#28a745"}})}),t.jsxs("div",{className:"notification-meta",children:[t.jsx("h4",{children:h.title}),t.jsxs("div",{className:"meta-info",children:[t.jsx("span",{children:new Date(h.created_at).toLocaleString()}),!h.read&&t.jsx("span",{className:"unread-dot"})]})]})]}),t.jsx("p",{className:"notification-message",children:h.message})]}),t.jsxs("div",{className:"notification-actions",children:[!h.read&&t.jsx("button",{onClick:()=>p(h.id),className:"btn btn-sm btn-outline",children:t.jsx("i",{className:"fas fa-check"})}),t.jsx("button",{onClick:()=>g(h.id),className:"btn btn-sm btn-danger",children:t.jsx("i",{className:"fas fa-trash"})})]})]},h.id))})]}):null}function Nu(){return t.jsxs(t.Fragment,{children:[t.jsx(S2,{}),t.jsx(x2,{})]})}function Qg({onRegisterSuccess:n,switchView:s}){const[l,o]=N.useState({username:"",email:"",password:"",confirmPassword:"",firstName:"",lastName:"",organization:""}),[d,f]=N.useState(!1),[m,p]=N.useState(""),g=x=>{o({...l,[x.target.name]:x.target.value})},h=async x=>{if(x.preventDefault(),f(!0),p(""),l.password!==l.confirmPassword){p("Passwords do not match"),f(!1);return}try{await new Promise(b=>setTimeout(b,1e3));const v={user:{username:l.username,email:l.email,first_name:l.firstName,last_name:l.lastName},token:"mock-jwt-token"};n(v)}catch{p("Registration failed. Please try again.")}finally{f(!1)}};return t.jsx("div",{style:{minHeight:"100vh",display:"flex",justifyContent:"center",alignItems:"center",background:"#f5f7fa",padding:"2rem"},children:t.jsxs("div",{style:{background:"white",padding:"2rem",borderRadius:"8px",maxWidth:"500px",width:"100%",boxShadow:"0 4px 6px rgba(0, 0, 0, 0.1)"},children:[t.jsx("h2",{style:{textAlign:"center",marginBottom:"2rem"},children:"Register New User"}),m&&t.jsx("div",{style:{background:"#fee",color:"#c53030",padding:"1rem",borderRadius:"4px",marginBottom:"1rem"},children:m}),t.jsxs("form",{onSubmit:h,children:[t.jsxs("div",{style:{display:"grid",gridTemplateColumns:"1fr 1fr",gap:"1rem",marginBottom:"1rem"},children:[t.jsxs("div",{children:[t.jsx("label",{children:"First Name"}),t.jsx("input",{type:"text",name:"firstName",value:l.firstName,onChange:g,style:{width:"100%",padding:"0.75rem",marginTop:"0.25rem",border:"1px solid #e2e8f0",borderRadius:"4px"},required:!0})]}),t.jsxs("div",{children:[t.jsx("label",{children:"Last Name"}),t.jsx("input",{type:"text",name:"lastName",value:l.lastName,onChange:g,style:{width:"100%",padding:"0.75rem",marginTop:"0.25rem",border:"1px solid #e2e8f0",borderRadius:"4px"},required:!0})]})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{children:"Username"}),t.jsx("input",{type:"text",name:"username",value:l.username,onChange:g,style:{width:"100%",padding:"0.75rem",marginTop:"0.25rem",border:"1px solid #e2e8f0",borderRadius:"4px"},required:!0})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{children:"Email"}),t.jsx("input",{type:"email",name:"email",value:l.email,onChange:g,style:{width:"100%",padding:"0.75rem",marginTop:"0.25rem",border:"1px solid #e2e8f0",borderRadius:"4px"},required:!0})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{children:"Organization"}),t.jsx("input",{type:"text",name:"organization",value:l.organization,onChange:g,style:{width:"100%",padding:"0.75rem",marginTop:"0.25rem",border:"1px solid #e2e8f0",borderRadius:"4px"},required:!0})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{children:"Password"}),t.jsx("input",{type:"password",name:"password",value:l.password,onChange:g,style:{width:"100%",padding:"0.75rem",marginTop:"0.25rem",border:"1px solid #e2e8f0",borderRadius:"4px"},required:!0})]}),t.jsxs("div",{style:{marginBottom:"2rem"},children:[t.jsx("label",{children:"Confirm Password"}),t.jsx("input",{type:"password",name:"confirmPassword",value:l.confirmPassword,onChange:g,style:{width:"100%",padding:"0.75rem",marginTop:"0.25rem",border:"1px solid #e2e8f0",borderRadius:"4px"},required:!0})]}),t.jsx("button",{type:"submit",disabled:d,style:{width:"100%",padding:"0.75rem",background:"#0056b3",color:"white",border:"none",borderRadius:"4px",cursor:"pointer",marginBottom:"1rem"},children:d?"Registering...":"Register"}),t.jsx("div",{style:{textAlign:"center"},children:t.jsx("button",{type:"button",onClick:s,style:{background:"none",border:"none",color:"#0056b3",cursor:"pointer",textDecoration:"underline"},children:"Back to Login"})})]})]})})}const C2="/assets/BlueV-D02my35J.png";function A2({isOpen:n,onClose:s,onNavigate:l}){return n?t.jsx("div",{style:{position:"fixed",top:0,left:0,width:"100%",height:"100%",background:"rgba(0, 0, 0, 0.5)",display:"flex",justifyContent:"center",alignItems:"center",zIndex:9999},children:t.jsxs("div",{style:{background:"white",padding:"2rem",borderRadius:"8px",maxWidth:"500px",width:"90%",maxHeight:"80vh",overflow:"auto"},children:[t.jsxs("div",{style:{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:"1rem"},children:[t.jsx("h2",{children:"Help & Support"}),t.jsx("button",{onClick:s,style:{background:"none",border:"none",fontSize:"1.5rem",cursor:"pointer"},children:"×"})]}),t.jsxs("div",{style:{marginBottom:"1.5rem"},children:[t.jsx("h3",{children:"Getting Started"}),t.jsx("p",{children:"Welcome to CRISP - Cyber Risk Information Sharing Platform. This platform allows educational institutions to securely share threat intelligence."})]}),t.jsxs("div",{style:{marginBottom:"1.5rem"},children:[t.jsx("h3",{children:"Login Help"}),t.jsx("p",{children:"If you're having trouble logging in:"}),t.jsxs("ul",{children:[t.jsx("li",{children:"Ensure you're using the correct username and password"}),t.jsx("li",{children:"Contact your system administrator for account issues"}),t.jsx("li",{children:`Use the "Forgot Password" link if you've forgotten your password`})]})]}),t.jsxs("div",{style:{marginBottom:"1.5rem"},children:[t.jsx("h3",{children:"Contact Support"}),t.jsx("p",{children:"For technical support, please contact:"}),t.jsxs("p",{children:[t.jsx("strong",{children:"Email:"})," support@bluevision.com"]}),t.jsxs("p",{children:[t.jsx("strong",{children:"Phone:"})," +1 (555) 123-4567"]})]}),t.jsx("div",{style:{display:"flex",gap:"1rem",justifyContent:"flex-end"},children:t.jsx("button",{onClick:s,style:{padding:"0.5rem 1rem",background:"#0056b3",color:"white",border:"none",borderRadius:"4px",cursor:"pointer"},children:"Close"})})]})}):null}function l0(){return t.jsx("div",{style:{minHeight:"100vh",display:"flex",flexDirection:"column",justifyContent:"center",alignItems:"center",background:"linear-gradient(135deg, #0056b3 0%, #00a0e9 100%)",color:"white",textAlign:"center",padding:"2rem"},children:t.jsxs("div",{style:{maxWidth:"600px"},children:[t.jsx("div",{style:{fontSize:"4rem",marginBottom:"1rem"},children:"🚧"}),t.jsx("h1",{style:{fontSize:"2.5rem",marginBottom:"1rem"},children:"Under Construction"}),t.jsx("p",{style:{fontSize:"1.2rem",marginBottom:"2rem",opacity:.9},children:"This feature is currently being developed. We're working hard to bring you the best experience possible."}),t.jsxs("div",{style:{marginBottom:"2rem"},children:[t.jsx("h3",{children:"Coming Soon:"}),t.jsxs("ul",{style:{listStyle:"none",padding:0,marginTop:"1rem"},children:[t.jsx("li",{style:{margin:"0.5rem 0"},children:"📊 Advanced Analytics Dashboard"}),t.jsx("li",{style:{margin:"0.5rem 0"},children:"🔐 Enhanced Security Features"}),t.jsx("li",{style:{margin:"0.5rem 0"},children:"🤝 Improved Collaboration Tools"}),t.jsx("li",{style:{margin:"0.5rem 0"},children:"📱 Mobile Application"})]})]}),t.jsx("a",{href:"/",style:{display:"inline-block",padding:"1rem 2rem",background:"white",color:"#0056b3",textDecoration:"none",borderRadius:"8px",fontWeight:"bold",transition:"transform 0.3s ease"},children:"Go Back Home"})]})})}function z2({isOpen:n,onClose:s,onPasswordChanged:l}){const[o,d]=N.useState(""),[f,m]=N.useState(""),[p,g]=N.useState(""),[h,x]=N.useState(!1),[v,b]=N.useState(""),_=async C=>{if(C.preventDefault(),x(!0),b(""),f!==p){b("New passwords do not match"),x(!1);return}try{await new Promise(E=>setTimeout(E,1e3)),l(),s(),d(""),m(""),g("")}catch{b("Failed to change password")}finally{x(!1)}};return n?t.jsx("div",{style:{position:"fixed",top:0,left:0,width:"100%",height:"100%",background:"rgba(0, 0, 0, 0.5)",display:"flex",justifyContent:"center",alignItems:"center",zIndex:9999},children:t.jsxs("div",{style:{background:"white",padding:"2rem",borderRadius:"8px",maxWidth:"400px",width:"90%"},children:[t.jsx("h2",{children:"Change Password"}),v&&t.jsx("div",{style:{color:"red",marginBottom:"1rem"},children:v}),t.jsxs("form",{onSubmit:_,children:[t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{children:"Current Password"}),t.jsx("input",{type:"password",value:o,onChange:C=>d(C.target.value),style:{width:"100%",padding:"0.5rem",marginTop:"0.25rem"},required:!0})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{children:"New Password"}),t.jsx("input",{type:"password",value:f,onChange:C=>m(C.target.value),style:{width:"100%",padding:"0.5rem",marginTop:"0.25rem"},required:!0})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{children:"Confirm New Password"}),t.jsx("input",{type:"password",value:p,onChange:C=>g(C.target.value),style:{width:"100%",padding:"0.5rem",marginTop:"0.25rem"},required:!0})]}),t.jsxs("div",{style:{display:"flex",gap:"1rem",justifyContent:"flex-end"},children:[t.jsx("button",{type:"button",onClick:s,disabled:h,children:"Cancel"}),t.jsx("button",{type:"submit",disabled:h,children:h?"Changing...":"Change Password"})]})]})]})}):null}function k2({fullscreen:n=!1}){return n?t.jsxs("div",{style:{position:"fixed",top:0,left:0,width:"100%",height:"100%",background:"rgba(0, 0, 0, 0.5)",display:"flex",justifyContent:"center",alignItems:"center",zIndex:9999},children:[t.jsx("div",{style:{width:"50px",height:"50px",border:"4px solid #f3f3f3",borderTop:"4px solid #0056b3",borderRadius:"50%",animation:"spin 1s linear infinite"}}),t.jsx("style",{children:`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `})]}):t.jsx("div",{style:{width:"30px",height:"30px",border:"3px solid #f3f3f3",borderTop:"3px solid #0056b3",borderRadius:"50%",animation:"spin 1s linear infinite"}})}function E2({onLoginSuccess:n,switchView:s}){const[l,o]=N.useState(""),[d,f]=N.useState(""),[m,p]=N.useState(""),[g,h]=N.useState(!1),[x,v]=N.useState(!1),[b,_]=N.useState(!1),[C,E]=N.useState(!1);N.useEffect(()=>{if(window.feather)window.feather.replace();else{const K=document.createElement("script");K.src="https://cdnjs.cloudflare.com/ajax/libs/feather-icons/4.29.0/feather.min.js",K.onload=()=>{window.feather&&window.feather.replace()},document.head.appendChild(K)}},[]),N.useEffect(()=>{window.feather&&setTimeout(()=>window.feather.replace(),100)},[m,g,x]);const A=async K=>{K.preventDefault(),h(!0),p("");try{await new Promise(Ae=>setTimeout(Ae,1e3));const se=await HS(l,d);n(se)}catch(se){p(se.message||"Invalid username or password")}finally{h(!1)}},L=()=>{v(!0)},q=()=>{v(!1)},P=()=>{E(!0)},M=()=>{E(!1)},X=()=>{p(""),alert("Password changed successfully! You can now log in with your new password.")},Q=(K,se)=>{console.log(`Navigate to ${K} from login page with context:`,se),q(),K==="construction"&&(s&&typeof s=="function"?s("Construction"):_(!0))};return b?t.jsx(l0,{}):t.jsxs(t.Fragment,{children:[t.jsx(M2,{}),g&&t.jsx(k2,{fullscreen:!0}),t.jsx("div",{className:"login-page",children:t.jsxs("div",{className:"login-content",children:[t.jsx("div",{className:"login-left",children:t.jsxs("div",{className:"brand-info",children:[t.jsx("div",{className:"logo-container",children:t.jsx("img",{src:C2,alt:"BlueV Logo",className:"brand-logo"})}),t.jsx("h2",{children:"Cyber Risk Information Sharing Platform"}),t.jsx("p",{children:"Streamline your threat intelligence sharing and committee management"}),t.jsxs("div",{className:"feature-list",children:[t.jsxs("div",{className:"feature-item",children:[t.jsx("div",{className:"feature-icon",children:t.jsx("i",{"data-feather":"shield"})}),t.jsxs("div",{className:"feature-text",children:[t.jsx("h3",{children:"Monitor Threats"}),t.jsx("p",{children:"Track and analyze security threats across institutions"})]})]}),t.jsxs("div",{className:"feature-item",children:[t.jsx("div",{className:"feature-icon",children:t.jsx("i",{"data-feather":"repeat"})}),t.jsxs("div",{className:"feature-text",children:[t.jsx("h3",{children:"Share Intelligence"}),t.jsx("p",{children:"Securely exchange threat data with trusted partners"})]})]}),t.jsxs("div",{className:"feature-item",children:[t.jsx("div",{className:"feature-icon",children:t.jsx("i",{"data-feather":"trending-up"})}),t.jsxs("div",{className:"feature-text",children:[t.jsx("h3",{children:"Analyze Patterns"}),t.jsx("p",{children:"Identify emerging threat patterns with advanced analytics"})]})]})]})]})}),t.jsx("div",{className:"login-right",children:t.jsxs("div",{className:"login-form-container",children:[t.jsx("div",{className:"login-header",children:t.jsx("button",{className:"help-button",onClick:L,title:"Help & Support",type:"button",children:t.jsx("i",{"data-feather":"help-circle"})})}),t.jsx("h2",{children:"Welcome Back"}),t.jsx("p",{className:"subtitle",children:"Sign in to your account"}),m&&t.jsxs("div",{className:"error-message",children:[t.jsx("i",{"data-feather":"alert-circle"})," ",m]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{htmlFor:"username",children:"Email"}),t.jsxs("div",{className:"input-with-icon",children:[t.jsx("i",{"data-feather":"mail"}),t.jsx("input",{type:"text",id:"username",value:l,onChange:K=>o(K.target.value),placeholder:"username@example.com",onKeyPress:K=>K.key==="Enter"&&A(K)})]})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{htmlFor:"password",children:"Password"}),t.jsxs("div",{className:"input-with-icon",children:[t.jsx("i",{"data-feather":"lock"}),t.jsx("input",{type:"password",id:"password",value:d,onChange:K=>f(K.target.value),placeholder:"••••••••",onKeyPress:K=>K.key==="Enter"&&A(K)})]})]}),t.jsx("button",{className:"btn-sign-in",onClick:A,disabled:g,children:g?"Signing in...":"Sign In"}),t.jsxs("div",{className:"login-footer",children:[t.jsxs("p",{children:["Don't have an account? Contact ",t.jsx("a",{href:"#",className:"register-link",children:"BlueVision ITM"})," for account registration."]}),t.jsxs("div",{className:"footer-links",children:[t.jsxs("button",{className:"help-link",onClick:L,type:"button",children:[t.jsx("i",{"data-feather":"help-circle"}),"Need Help?"]}),t.jsxs("button",{className:"help-link",onClick:P,type:"button",children:[t.jsx("i",{"data-feather":"lock"}),"Change Password"]}),t.jsxs("a",{href:"/forgot-password",className:"help-link",children:[t.jsx("i",{"data-feather":"key"}),"Forgot Password?"]})]})]})]})})]})}),t.jsx(A2,{isOpen:x,onClose:q,onNavigate:Q}),t.jsx(z2,{isOpen:C,onClose:M,onPasswordChanged:X})]})}function M2(){return t.jsx("style",{children:`
        :root {
            --primary-color: #0056b3;
            --primary-dark: #003366;
            --primary-light: #007bff;
            --accent-color: #00a0e9;
            --text-light: #ffffff;
            --text-dark: #2d3748;
            --text-muted: #718096;
            --danger: #e53e3e;
            --success: #38a169;
            --warning: #f6ad55;
            --info: #4299e1;
            --bg-light: #f5f7fa;
            --bg-medium: #e2e8f0;
            --bg-dark: #1a202c;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }
        
        html, body {
            height: 100%;
            width: 100%;
            overflow-x: hidden;
        }
        
        body {
            background-color: var(--bg-light);
            color: var(--text-dark);
            min-height: 100vh;
        }
        
        /* Global Feather icon styling */
        i[data-feather] {
            stroke: currentColor;
            stroke-width: 2;
            stroke-linecap: round;
            stroke-linejoin: round;
            fill: none;
        }
        
        /* Login Styles */
        .login-page {
            min-height: 100vh;
            height: 100vh;
            display: flex;
            align-items: stretch;
            background-color: var(--bg-light);
            overflow: hidden;
        }
        
        .login-content {
            display: flex;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
        }
        
        .login-left {
            flex: 3;
            background: linear-gradient(135deg, #0056b3 0%, #00a0e9 100%);
            color: var(--text-light);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 3rem;
            position: relative;
            overflow: hidden;
        }
        
        .login-left::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA4MDAgODAwIiBwcmVzZXJ2ZUFzcGVjdFJhdGlvPSJub25lIj48ZyBmaWxsPSJub25lIiBzdHJva2U9IiNmZmYiIG9wYWNpdHk9IjAuMSIgc3Ryb2tlLXdpZHRoPSIxLjUiPjxjaXJjbGUgcj0iMTAwIiBjeD0iNDAwIiBjeT0iNDAwIi8+PGNpcmNsZSByPSIyMDAiIGN4PSI0MDAiIGN5PSI0MDAiLz48Y2lyY2xlIHI9IjMwMCIgY3g9IjQwMCIgY3k9IjQwMCIvPjxjaXJjbGUgcj0iNDAwIiBjeD0iNDAwIiBjeT0iNDAwIi8+PC9nPjxnIGZpbGw9Im5vbmUiIHN0cm9rZT0iI2ZmZiIgb3BhY2l0eT0iMC4yIiBzdHJva2Utd2lkdGg9IjEiPjxwYXRoIGQ9Ik0yMDAgMjAwIEw2MDAgNjAwIE0yMDAgNjAwIEw2MDAgMjAwIE0zMDAgMTAwIEwzMDAgNzAwIE01MDAgMTAwIEw1MDAgNzAwIE0xMDAgMzAwIEw3MDAgMzAwIE0xMDAgNTAwIEw3MDAgNTAwIi8+PC9nPjxnIGZpbGw9IiNmZmYiIG9wYWNpdHk9IjAuMiI+PGNpcmNsZSByPSIzIiBjeD0iMjAwIiBjeT0iMjAwIi8+PGNpcmNsZSByPSIzIiBjeD0iNDAwIiBjeT0iMjAwIi8+PGNpcmNsZSByPSIzIiBjeD0iNjAwIiBjeT0iMjAwIi8+PGNpcmNsZSByPSIzIiBjeD0iMjAwIiBjeT0iNDAwIi8+PGNpcmNsZSByPSIzIiBjeD0iNDAwIiBjeT0iNDAwIi8+PGNpcmNsZSByPSIzIiBjeD0iNjAwIiBjeT0iNDAwIi8+PGNpcmNsZSByPSIzIiBjeD0iMjAwIiBjeT0iNjAwIi/+PGNpcmNsZSByPSIzIiBjeD0iNDAwIiBjeT0iNjAwIi8+PGNpcmNsZSByPSIzIiBjeD0iNjAwIiBjeT0iNjAwIi8+PC9nPjxnIGZpbGw9Im5vbmUiIHN0cm9rZT0iI2ZmZiIgb3BhY2l0eT0iMC4xIiBzdHJva2Utd2lkdGg9IjEiPjxwYXRoIGQ9Ik0zMDAgMzAwIEw1MDAgNTAwIE0zMDAgNTAwIEw1MDAgMzAwIi8+PC9nPjwvc3ZnPg=='), url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNDAgMjQwIj48ZGVmcz48cGF0dGVybiBpZD0ic21hbGwtZ3JpZCIgd2lkdGg9IjEwIiBoZWlnaHQ9IjEwIiBwYXR0ZXJuVW5pdHM9InVzZXJTcGFjZU9uVXNlIj48cmVjdCB3aWR0aD0iMTAiIGhlaWdodD0iMTAiIGZpbGw9Im5vbmUiLz48cGF0aCBkPSJNIDEwIDAgTCAwIDAgTCAwIDEwIiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmYiIHN0cm9rZS13aWR0aD0iMC41IiBvcGFjaXR5PSIwLjEiLz48L3BhdHRlcm4+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjc21hbGwtZ3JpZCkiLz48L3N2Zz4=');
            background-blend-mode: overlay;
            opacity: 0.3;
        }
        
        /* Logo container styles */
        .logo-container {
            margin-bottom: 1.5rem;
        }
        
        .brand-logo {
            max-width: 250px;
            height: auto;
        }
        
        .brand-info {
            position: relative;
            z-index: 2;
            max-width: 700px;
            margin: 0 auto;
        }
        
        .brand-info h2 {
            font-size: 1.8rem;
            font-weight: 500;
            margin-bottom: 1.5rem;
            opacity: 0.9;
        }
        
        .brand-info p {
            font-size: 1.1rem;
            margin-bottom: 3rem;
            opacity: 0.8;
            line-height: 1.6;
        }
        
        .feature-list {
            margin-top: 3rem;
        }
        
        .feature-item {
            display: flex;
            align-items: center;
            margin-bottom: 1.5rem;
        }
        
        .feature-icon {
            background-color: rgba(255, 255, 255, 0.2);
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 1rem;
        }
        
        .feature-icon i {
            width: 24px;
            height: 24px;
            stroke-width: 2;
        }
        
        .feature-text h3 {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 0.3rem;
        }
        
        .feature-text p {
            font-size: 0.95rem;
            opacity: 0.8;
            margin: 0;
        }
        
        .login-right {
            flex: 1;
            background-color: var(--text-light);
            display: flex;
            align-items: center;
            justify-content: center;
            min-width: 320px;
            max-width: 400px;
            box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
            position: relative;
            z-index: 2;
        }
        
        .login-form-container {
            width: 100%;
            max-width: 300px;
            padding: 1.5rem;
            position: relative;
        }

        /* Login Header with Help Button */
        .login-header {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 1rem;
        }

        .help-button {
            background: var(--bg-light);
            border: 1px solid var(--bg-medium);
            border-radius: 50%;
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            color: var(--primary-color);
            transition: all 0.2s ease;
            font-size: 0;
        }

        .help-button:hover {
            background: var(--primary-color);
            color: var(--text-light);
            transform: scale(1.05);
        }

        .help-button i {
            width: 18px;
            height: 18px;
        }
        
        .login-form-container h2 {
            font-size: 1.75rem;
            font-weight: 600;
            color: var(--text-dark);
            margin-bottom: 0.5rem;
        }
        
        .subtitle {
            color: var(--text-muted);
            margin-bottom: 2rem;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-group label {
            display: block;
            font-weight: 500;
            margin-bottom: 0.5rem;
            color: var(--text-dark);
        }
        
        .input-with-icon {
            position: relative;
        }
        
        .input-with-icon i {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
            width: 16px;
            height: 16px;
        }
        
        .input-with-icon input {
            width: 100%;
            padding: 0.8rem 1rem 0.8rem 2.8rem;
            border: 1px solid var(--bg-medium);
            border-radius: 8px;
            font-size: 1rem;
            background-color: var(--bg-light);
            transition: all 0.3s;
            color: #000000;
        }
        
        .input-with-icon input:focus {
            outline: none;
            border-color: var(--primary-color);
            background-color: var(--text-light);
            box-shadow: 0 0 0 3px rgba(0, 86, 179, 0.1);
            color: #000000;
        }
        
        .btn-sign-in {
            width: 100%;
            padding: 0.8rem;
            background-color: var(--primary-color);
            color: var(--text-light);
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 1rem;
        }
        
        .btn-sign-in:hover {
            background-color: var(--primary-dark);
        }
        
        .btn-sign-in:disabled {
            opacity: 0.7;
            cursor: not-allowed;
        }
        
        .login-footer {
            margin-top: 2rem;
            text-align: center;
            color: var(--text-muted);
            font-size: 0.9rem;
        }

        .footer-links {
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid var(--bg-medium);
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
        }

        .help-link {
            background: none;
            border: none;
            color: var(--primary-color);
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s ease;
        }

        .help-link:hover {
            color: var(--primary-dark);
            text-decoration: underline;
        }

        .help-link i {
            width: 14px;
            height: 14px;
        }
        
        .demo-credentials {
            margin-top: 1rem;
            padding: 0.75rem;
            background-color: var(--bg-light);
            border-radius: 6px;
            border: 1px solid var(--bg-medium);
        }
        
        .demo-credentials p {
            margin: 0.2rem 0;
            font-size: 0.8rem;
        }
        
        .register-link {
            color: var(--primary-color);
            text-decoration: none;
            font-weight: 600;
        }
        
        .register-link:hover {
            text-decoration: underline;
        }
        
        .error-message {
            background-color: rgba(229, 62, 62, 0.1);
            color: var(--danger);
            padding: 0.8rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.9rem;
        }
        
        .error-message i {
            width: 16px;
            height: 16px;
            flex-shrink: 0;
        }
        
        /* Responsive Design */
        @media (max-width: 1400px) {
            .login-left {
                flex: 2.5;
                justify-content: center;
            }
            
            .login-right {
                flex: 1;
                min-width: 300px;
                max-width: 350px;
            }
            
            .brand-info {
                max-width: 600px;
            }
        }
        
        @media (max-width: 1200px) {
            .login-left {
                flex: 2;
                justify-content: center;
            }
            
            .login-right {
                flex: 1;
                min-width: 280px;
                max-width: 320px;
            }
            
            .brand-info {
                max-width: 500px;
            }
            
            .login-form-container {
                max-width: 280px;
                padding: 1.25rem;
            }
        }
        
        @media (max-width: 992px) {
            .login-content {
                flex-direction: column;
                height: auto;
                overflow: visible;
            }
            
            .login-page {
                height: auto;
                overflow: visible;
            }
            
            .login-left, .login-right {
                flex: none;
                width: 100%;
                min-width: unset;
                max-width: unset;
            }
            
            .login-left {
                padding: 2rem;
                min-height: 300px;
                justify-content: center;
            }
            
            .login-right {
                box-shadow: none;
                border-top: 1px solid var(--bg-medium);
            }
            
            .login-form-container {
                padding: 2rem;
                max-width: 400px;
            }
        }
        
        @media (max-width: 768px) {
            .brand-logo {
                max-width: 200px;
            }
            
            .brand-info h2 {
                font-size: 1.3rem;
            }
            
            .brand-info p {
                font-size: 1rem;
            }
            
            .login-form-container {
                padding: 1.5rem;
            }
        }
        
        @media (max-width: 576px) {
            .login-left {
                padding: 1.5rem;
            }
            
            .brand-logo {
                max-width: 180px;
            }
            
            .brand-info h2 {
                font-size: 1.1rem;
            }
            
            .feature-icon {
                width: 40px;
                height: 40px;
                font-size: 1.2rem;
            }
            
            .feature-text h3 {
                font-size: 1rem;
            }
            
            .feature-text p {
                font-size: 0.85rem;
            }
        }
      `})}function D2(){const[n,s]=N.useState(!1),l=fl(),o=()=>{l("/login")},d=()=>{const f=document.getElementById("features");f&&f.scrollIntoView({behavior:"smooth"})};return t.jsx("header",{className:"header",children:t.jsxs("div",{className:"container header-container",children:[t.jsxs("a",{href:"#",className:"logo",onClick:f=>{f.preventDefault(),l("/")},children:[t.jsx("i",{className:"fas fa-shield-alt logo-icon"}),t.jsx("div",{className:"logo-text",children:"CRISP"})]}),t.jsx("nav",{className:`nav ${n?"nav-open":""}`,children:t.jsxs("ul",{className:"nav-links",children:[t.jsx("li",{children:t.jsx("a",{href:"#features",children:"Features"})}),t.jsx("li",{children:t.jsx("a",{href:"#benefits",children:"Benefits"})}),t.jsx("li",{children:t.jsx("a",{href:"#about",children:"About"})}),t.jsx("li",{children:t.jsx("a",{href:"#contact",children:"Contact"})})]})}),t.jsxs("div",{className:"header-actions",children:[t.jsx("button",{onClick:d,className:"btn btn-outline",children:"Request Demo"}),t.jsx("button",{onClick:o,className:"btn btn-primary",children:"Get Started"})]}),t.jsx("button",{className:"mobile-menu-toggle",onClick:()=>s(!n),children:t.jsx("i",{className:"fas fa-bars"})})]})})}function R2(){const n=fl(),s=()=>{n("/login")};return t.jsx("section",{className:"hero",children:t.jsxs("div",{className:"container hero-container",children:[t.jsxs("div",{className:"hero-content",children:[t.jsxs("h1",{className:"hero-title",children:["Secure ",t.jsx("span",{className:"highlight",children:"Cyber Threat Intelligence"})," Sharing for Educational Institutions"]}),t.jsx("p",{className:"hero-description",children:"CRISP enables educational institutions to share anonymized threat intelligence, protecting student data while strengthening cybersecurity defenses across the education sector."}),t.jsxs("div",{className:"hero-actions",children:[t.jsxs("button",{onClick:s,className:"btn btn-primary btn-large",children:[t.jsx("i",{className:"fas fa-sign-in-alt"}),"Login to Dashboard"]}),t.jsxs("a",{href:"#features",className:"btn btn-outline btn-large",children:[t.jsx("i",{className:"fas fa-info-circle"}),"Learn More"]})]})]}),t.jsx("div",{className:"hero-visual",children:t.jsxs("div",{className:"dashboard-preview",children:[t.jsxs("div",{className:"dashboard-header",children:[t.jsxs("div",{className:"dashboard-logo",children:[t.jsx("i",{className:"fas fa-shield-alt"}),t.jsx("span",{children:"CRISP Dashboard"})]}),t.jsxs("div",{className:"dashboard-status",children:[t.jsx("span",{className:"status-dot"}),t.jsx("span",{children:"System Online"})]})]}),t.jsxs("div",{className:"dashboard-stats",children:[t.jsxs("div",{className:"stat-card",children:[t.jsx("div",{className:"stat-icon threat-icon",children:t.jsx("i",{className:"fas fa-exclamation-triangle"})}),t.jsxs("div",{className:"stat-info",children:[t.jsx("div",{className:"stat-number",children:"247"}),t.jsx("div",{className:"stat-label",children:"Active Threats"})]})]}),t.jsxs("div",{className:"stat-card",children:[t.jsx("div",{className:"stat-icon institution-icon",children:t.jsx("i",{className:"fas fa-building"})}),t.jsxs("div",{className:"stat-info",children:[t.jsx("div",{className:"stat-number",children:"45"}),t.jsx("div",{className:"stat-label",children:"Institutions"})]})]}),t.jsxs("div",{className:"stat-card",children:[t.jsx("div",{className:"stat-icon sharing-icon",children:t.jsx("i",{className:"fas fa-share-alt"})}),t.jsxs("div",{className:"stat-info",children:[t.jsx("div",{className:"stat-number",children:"1.2K"}),t.jsx("div",{className:"stat-label",children:"Shared IoCs"})]})]})]})]})})]})})}function O2(){return t.jsx("section",{id:"features",className:"features",children:t.jsxs("div",{className:"container",children:[t.jsxs("div",{className:"section-header",children:[t.jsx("h2",{children:"Powerful Features for Educational Cybersecurity"}),t.jsx("p",{children:"Discover how CRISP transforms threat intelligence sharing across educational institutions"})]}),t.jsxs("div",{className:"features-grid",children:[t.jsxs("div",{className:"feature-card",children:[t.jsx("div",{className:"feature-icon",children:t.jsx("i",{className:"fas fa-shield-alt"})}),t.jsx("h3",{className:"feature-title",children:"Secure Intelligence Sharing"}),t.jsx("p",{className:"feature-description",children:"Share threat intelligence securely between institutions while maintaining complete data anonymization and privacy protection."})]}),t.jsxs("div",{className:"feature-card",children:[t.jsx("div",{className:"feature-icon",children:t.jsx("i",{className:"fas fa-users"})}),t.jsx("h3",{className:"feature-title",children:"Trust Management"}),t.jsx("p",{className:"feature-description",children:"Build and manage trust relationships between educational institutions with granular access controls and verification systems."})]}),t.jsxs("div",{className:"feature-card",children:[t.jsx("div",{className:"feature-icon",children:t.jsx("i",{className:"fas fa-chart-line"})}),t.jsx("h3",{className:"feature-title",children:"Advanced Analytics"}),t.jsx("p",{className:"feature-description",children:"Gain insights from shared threat data with powerful analytics tools and real-time monitoring capabilities."})]}),t.jsxs("div",{className:"feature-card",children:[t.jsx("div",{className:"feature-icon",children:t.jsx("i",{className:"fas fa-bell"})}),t.jsx("h3",{className:"feature-title",children:"Real-time Alerts"}),t.jsx("p",{className:"feature-description",children:"Receive instant notifications about emerging threats relevant to your institution's security posture."})]}),t.jsxs("div",{className:"feature-card",children:[t.jsx("div",{className:"feature-icon",children:t.jsx("i",{className:"fas fa-cog"})}),t.jsx("h3",{className:"feature-title",children:"Automated Processing"}),t.jsx("p",{className:"feature-description",children:"Streamline threat intelligence workflows with automated data processing and standardized formats."})]}),t.jsxs("div",{className:"feature-card",children:[t.jsx("div",{className:"feature-icon",children:t.jsx("i",{className:"fas fa-lock"})}),t.jsx("h3",{className:"feature-title",children:"Privacy First"}),t.jsx("p",{className:"feature-description",children:"Built with privacy-by-design principles to protect sensitive educational data while enabling effective collaboration."})]})]})]})})}function U2(){return t.jsx("section",{className:"stats",children:t.jsx("div",{className:"container",children:t.jsxs("div",{className:"stats-grid",children:[t.jsxs("div",{className:"stat-item",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-university"})}),t.jsx("div",{className:"stat-number",children:"150+"}),t.jsx("div",{className:"stat-label",children:"Educational Institutions"})]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-exclamation-triangle"})}),t.jsx("div",{className:"stat-number",children:"10K+"}),t.jsx("div",{className:"stat-label",children:"Threats Detected"})]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-share-alt"})}),t.jsx("div",{className:"stat-number",children:"50K+"}),t.jsx("div",{className:"stat-label",children:"Indicators Shared"})]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-clock"})}),t.jsx("div",{className:"stat-number",children:"99.9%"}),t.jsx("div",{className:"stat-label",children:"Uptime Reliability"})]})]})})})}function L2(){const n=fl(),s=()=>{n("/login")};return t.jsx("section",{className:"cta",children:t.jsx("div",{className:"container",children:t.jsxs("div",{className:"cta-content",children:[t.jsx("h2",{children:"Ready to Strengthen Your Institution's Security?"}),t.jsx("p",{children:"Join the growing network of educational institutions sharing threat intelligence to protect students, faculty, and institutional data."}),t.jsxs("div",{className:"cta-actions",children:[t.jsxs("button",{onClick:s,className:"btn btn-primary btn-large",children:[t.jsx("i",{className:"fas fa-rocket"}),"Get Started Today"]}),t.jsxs("a",{href:"#contact",className:"btn btn-outline btn-large",children:[t.jsx("i",{className:"fas fa-phone"}),"Contact Sales"]})]}),t.jsxs("div",{className:"cta-features",children:[t.jsxs("div",{className:"cta-feature",children:[t.jsx("i",{className:"fas fa-check"}),t.jsx("span",{children:"Free 30-day trial"})]}),t.jsxs("div",{className:"cta-feature",children:[t.jsx("i",{className:"fas fa-check"}),t.jsx("span",{children:"No setup fees"})]}),t.jsxs("div",{className:"cta-feature",children:[t.jsx("i",{className:"fas fa-check"}),t.jsx("span",{children:"24/7 support"})]})]})]})})})}function B2(){return t.jsx("footer",{id:"contact",className:"footer",children:t.jsxs("div",{className:"container",children:[t.jsxs("div",{className:"footer-content",children:[t.jsxs("div",{className:"footer-main",children:[t.jsxs("div",{className:"footer-logo",children:[t.jsx("i",{className:"fas fa-shield-alt logo-icon"}),t.jsx("span",{children:"CRISP"})]}),t.jsx("p",{className:"footer-description",children:"Empowering educational institutions with secure, collaborative threat intelligence sharing to build stronger cybersecurity defenses together."}),t.jsxs("div",{className:"footer-social",children:[t.jsx("a",{href:"#","aria-label":"Twitter",children:t.jsx("i",{className:"fab fa-twitter"})}),t.jsx("a",{href:"#","aria-label":"LinkedIn",children:t.jsx("i",{className:"fab fa-linkedin"})}),t.jsx("a",{href:"#","aria-label":"GitHub",children:t.jsx("i",{className:"fab fa-github"})})]})]}),t.jsxs("div",{className:"footer-section",children:[t.jsx("h4",{children:"Product"}),t.jsxs("ul",{children:[t.jsx("li",{children:t.jsx("a",{href:"#features",children:"Features"})}),t.jsx("li",{children:t.jsx("a",{href:"#pricing",children:"Pricing"})}),t.jsx("li",{children:t.jsx("a",{href:"#security",children:"Security"})}),t.jsx("li",{children:t.jsx("a",{href:"#integrations",children:"Integrations"})})]})]}),t.jsxs("div",{className:"footer-section",children:[t.jsx("h4",{children:"Resources"}),t.jsxs("ul",{children:[t.jsx("li",{children:t.jsx("a",{href:"#documentation",children:"Documentation"})}),t.jsx("li",{children:t.jsx("a",{href:"#api",children:"API Reference"})}),t.jsx("li",{children:t.jsx("a",{href:"#guides",children:"User Guides"})}),t.jsx("li",{children:t.jsx("a",{href:"#support",children:"Support Center"})})]})]}),t.jsxs("div",{className:"footer-section",children:[t.jsx("h4",{children:"Company"}),t.jsxs("ul",{children:[t.jsx("li",{children:t.jsx("a",{href:"#about",children:"About Us"})}),t.jsx("li",{children:t.jsx("a",{href:"#careers",children:"Careers"})}),t.jsx("li",{children:t.jsx("a",{href:"#blog",children:"Blog"})}),t.jsx("li",{children:t.jsx("a",{href:"#contact",children:"Contact"})})]})]})]}),t.jsx("div",{className:"footer-bottom",children:t.jsxs("div",{className:"footer-legal",children:[t.jsx("p",{children:"© 2024 CRISP. All rights reserved."}),t.jsxs("div",{className:"footer-links",children:[t.jsx("a",{href:"#privacy",children:"Privacy Policy"}),t.jsx("a",{href:"#terms",children:"Terms of Service"}),t.jsx("a",{href:"#cookies",children:"Cookie Policy"})]})]})})]})})}function q2(){return t.jsxs("div",{className:"landing-page",children:[t.jsx("style",{children:`
          * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
          }

          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
              'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
              sans-serif;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            background-color: #0a0b0d;
            color: #ffffff;
            line-height: 1.6;
          }

          .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
          }

          /* Header Styles */
          .header {
            background: rgba(10, 11, 13, 0.95);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
          }

          .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 20px;
          }

          .logo {
            display: flex;
            align-items: center;
            text-decoration: none;
            color: #ffffff;
            font-weight: bold;
            font-size: 1.5rem;
          }

          .logo-icon {
            margin-right: 0.5rem;
            color: #4285f4;
            font-size: 1.8rem;
          }

          .nav {
            display: flex;
          }

          .nav-links {
            display: flex;
            list-style: none;
            gap: 2rem;
          }

          .nav-links a {
            color: #ffffff;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s ease;
          }

          .nav-links a:hover {
            color: #4285f4;
          }

          .header-actions {
            display: flex;
            gap: 1rem;
            align-items: center;
          }

          .mobile-menu-toggle {
            display: none;
            background: none;
            border: none;
            color: #ffffff;
            font-size: 1.5rem;
            cursor: pointer;
          }

          /* Button Styles */
          .btn {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
            cursor: pointer;
            border: none;
            font-size: 1rem;
          }

          .btn-primary {
            background: linear-gradient(135deg, #4285f4, #34a853);
            color: #ffffff;
          }

          .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(66, 133, 244, 0.3);
          }

          .btn-outline {
            background: transparent;
            border: 2px solid #4285f4;
            color: #4285f4;
          }

          .btn-outline:hover {
            background: #4285f4;
            color: #ffffff;
          }

          .btn-large {
            padding: 1rem 2rem;
            font-size: 1.1rem;
          }

          /* Hero Section */
          .hero {
            min-height: 100vh;
            padding: 80px 0;
            background: linear-gradient(135deg, #0a0b0d 0%, #1a1b1e 100%);
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: center;
          }

          .hero::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><defs><radialGradient id="grad" cx="50%" cy="50%" r="50%"><stop offset="0%" style="stop-color:%234285f4;stop-opacity:0.1" /><stop offset="100%" style="stop-color:%234285f4;stop-opacity:0" /></radialGradient></defs><circle cx="500" cy="500" r="500" fill="url(%23grad)" /></svg>') no-repeat center;
            background-size: cover;
            opacity: 0.5;
          }

          .hero-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 4rem;
            align-items: center;
            position: relative;
            z-index: 1;
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
          }

          .hero-title {
            font-size: 3.5rem;
            font-weight: 800;
            line-height: 1.2;
            margin-bottom: 1.5rem;
          }

          .highlight {
            background: linear-gradient(135deg, #4285f4, #34a853);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
          }

          .hero-description {
            font-size: 1.25rem;
            color: #b0b0b0;
            margin-bottom: 2rem;
            line-height: 1.6;
          }

          .hero-actions {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
          }

          /* Dashboard Preview */
          .dashboard-preview {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
          }

          .dashboard-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
          }

          .dashboard-logo {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: #4285f4;
            font-weight: 600;
          }

          .dashboard-status {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.9rem;
          }

          .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #34a853;
            animation: pulse 2s infinite;
          }

          @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
          }

          .dashboard-stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
          }

          .stat-card {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
          }

          .stat-icon {
            width: 40px;
            height: 40px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
          }

          .threat-icon { background: rgba(244, 67, 54, 0.2); color: #f44336; }
          .institution-icon { background: rgba(66, 133, 244, 0.2); color: #4285f4; }
          .sharing-icon { background: rgba(52, 168, 83, 0.2); color: #34a853; }

          .stat-number {
            font-size: 1.5rem;
            font-weight: 700;
            color: #ffffff;
          }

          .stat-label {
            font-size: 0.8rem;
            color: #b0b0b0;
          }

          /* Stats Section */
          .stats {
            padding: 80px 0;
            background: rgba(255, 255, 255, 0.02);
            display: flex;
            align-items: center;
            min-height: 60vh;
          }

          .stats .container {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
          }

          .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            justify-items: center;
            align-items: center;
          }

          .stat-item {
            text-align: center;
            padding: 2rem;
          }

          .stat-item .stat-icon {
            width: 80px;
            height: 80px;
            margin: 0 auto 1rem;
            background: linear-gradient(135deg, #4285f4, #34a853);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            color: #ffffff;
          }

          .stat-item .stat-number {
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #4285f4, #34a853);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
          }

          .stat-item .stat-label {
            font-size: 1.1rem;
            color: #b0b0b0;
          }

          /* Features Section */
          .features {
            padding: 80px 0;
            display: flex;
            align-items: center;
            min-height: 80vh;
          }

          .features .container {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
          }

          .section-header {
            text-align: center;
            margin-bottom: 4rem;
          }

          .section-header h2 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
          }

          .section-header p {
            font-size: 1.2rem;
            color: #b0b0b0;
            max-width: 600px;
            margin: 0 auto;
          }

          .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 2rem;
            justify-items: center;
            align-items: stretch;
            max-width: 1100px;
            margin: 0 auto;
          }

          .feature-card {
            padding: 2rem;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
          }

          .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(66, 133, 244, 0.2);
          }

          .feature-icon {
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #4285f4, #34a853);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            color: #ffffff;
            margin-bottom: 1.5rem;
          }

          .feature-title {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 1rem;
          }

          .feature-description {
            color: #b0b0b0;
            line-height: 1.6;
          }

          /* CTA Section */
          .cta {
            padding: 80px 0;
            background: linear-gradient(135deg, #4285f4, #34a853);
            text-align: center;
            display: flex;
            align-items: center;
            min-height: 60vh;
          }

          .cta .container {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
          }

          .cta-content h2 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            color: #ffffff;
          }

          .cta-content p {
            font-size: 1.2rem;
            margin-bottom: 2rem;
            color: rgba(255, 255, 255, 0.9);
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
          }

          .cta-actions {
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin-bottom: 2rem;
            flex-wrap: wrap;
          }

          .cta .btn-primary {
            background: #ffffff;
            color: #4285f4;
          }

          .cta .btn-outline {
            border-color: #ffffff;
            color: #ffffff;
          }

          .cta .btn-outline:hover {
            background: #ffffff;
            color: #4285f4;
          }

          .cta-features {
            display: flex;
            gap: 2rem;
            justify-content: center;
            flex-wrap: wrap;
          }

          .cta-feature {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: rgba(255, 255, 255, 0.9);
          }

          .cta-feature i {
            color: #ffffff;
          }

          /* Footer */
          .footer {
            background: #0a0b0d;
            padding: 60px 0 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
          }

          .footer-content {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1fr;
            gap: 3rem;
            margin-bottom: 2rem;
          }

          .footer-logo {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
            font-size: 1.5rem;
            font-weight: bold;
          }

          .footer-logo .logo-icon {
            margin-right: 0.5rem;
            color: #4285f4;
          }

          .footer-description {
            color: #b0b0b0;
            margin-bottom: 1.5rem;
            line-height: 1.6;
          }

          .footer-social {
            display: flex;
            gap: 1rem;
          }

          .footer-social a {
            width: 40px;
            height: 40px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            text-decoration: none;
            transition: background 0.3s ease;
          }

          .footer-social a:hover {
            background: #4285f4;
          }

          .footer-section h4 {
            margin-bottom: 1rem;
            color: #ffffff;
          }

          .footer-section ul {
            list-style: none;
          }

          .footer-section ul li {
            margin-bottom: 0.5rem;
          }

          .footer-section ul li a {
            color: #b0b0b0;
            text-decoration: none;
            transition: color 0.3s ease;
          }

          .footer-section ul li a:hover {
            color: #4285f4;
          }

          .footer-bottom {
            padding-top: 2rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
          }

          .footer-legal {
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: #b0b0b0;
            font-size: 0.9rem;
          }

          .footer-links {
            display: flex;
            gap: 2rem;
          }

          .footer-links a {
            color: #b0b0b0;
            text-decoration: none;
            transition: color 0.3s ease;
          }

          .footer-links a:hover {
            color: #4285f4;
          }

          /* Responsive Design */
          @media (max-width: 768px) {
            .nav {
              display: none;
            }
            
            .nav-open {
              display: block;
              position: absolute;
              top: 100%;
              left: 0;
              right: 0;
              background: rgba(10, 11, 13, 0.95);
              backdrop-filter: blur(10px);
              border-top: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .nav-open .nav-links {
              flex-direction: column;
              padding: 1rem;
              gap: 1rem;
            }
            
            .mobile-menu-toggle {
              display: block;
            }
            
            .header-actions {
              display: none;
            }
            
            .hero {
              min-height: 100vh;
              padding: 100px 0 60px;
            }
            
            .hero-container {
              grid-template-columns: 1fr;
              gap: 2rem;
              text-align: center;
            }
            
            .hero-title {
              font-size: 2.5rem;
            }
            
            .stats {
              min-height: 50vh;
              padding: 60px 0;
            }
            
            .features {
              min-height: auto;
              padding: 60px 0;
            }
            
            .cta {
              min-height: 50vh;
              padding: 60px 0;
            }
            
            .dashboard-stats {
              grid-template-columns: 1fr;
            }
            
            .features-grid {
              grid-template-columns: 1fr;
              max-width: 100%;
            }
            
            .footer-content {
              grid-template-columns: 1fr;
              gap: 2rem;
            }
            
            .footer-legal {
              flex-direction: column;
              gap: 1rem;
            }
            
            .cta-actions {
              flex-direction: column;
              align-items: center;
            }
          }
        `}),t.jsx(D2,{}),t.jsx(R2,{}),t.jsx(U2,{}),t.jsx(O2,{}),t.jsx(L2,{}),t.jsx(B2,{})]})}function H2(){const[n,s]=N.useState(""),[l,o]=N.useState(!1),[d,f]=N.useState(!1),m=async p=>{p.preventDefault(),f(!0),await new Promise(g=>setTimeout(g,1e3)),o(!0),f(!1)};return t.jsx("div",{style:{minHeight:"100vh",display:"flex",justifyContent:"center",alignItems:"center",background:"#f5f7fa"},children:t.jsx("div",{style:{background:"white",padding:"2rem",borderRadius:"8px",maxWidth:"400px",width:"90%",boxShadow:"0 4px 6px rgba(0, 0, 0, 0.1)"},children:l?t.jsxs(t.Fragment,{children:[t.jsx("h2",{children:"Check Your Email"}),t.jsxs("p",{style:{marginBottom:"1.5rem",color:"#666"},children:["We've sent a password reset link to ",n]}),t.jsx("a",{href:"/login",style:{color:"#0056b3"},children:"Back to Login"})]}):t.jsxs(t.Fragment,{children:[t.jsx("h2",{children:"Forgot Password"}),t.jsx("p",{style:{marginBottom:"1.5rem",color:"#666"},children:"Enter your email address and we'll send you a link to reset your password."}),t.jsxs("form",{onSubmit:m,children:[t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{children:"Email Address"}),t.jsx("input",{type:"email",value:n,onChange:p=>s(p.target.value),style:{width:"100%",padding:"0.75rem",marginTop:"0.25rem",border:"1px solid #e2e8f0",borderRadius:"4px"},required:!0})]}),t.jsx("button",{type:"submit",disabled:d,style:{width:"100%",padding:"0.75rem",background:"#0056b3",color:"white",border:"none",borderRadius:"4px",cursor:"pointer"},children:d?"Sending...":"Send Reset Link"})]}),t.jsx("div",{style:{marginTop:"1rem",textAlign:"center"},children:t.jsx("a",{href:"/login",style:{color:"#0056b3"},children:"Back to Login"})})]})})})}function I2(){const[n,s]=N.useState(""),[l,o]=N.useState(""),[d,f]=N.useState(!1),[m,p]=N.useState(!1),[g,h]=N.useState(""),x=async v=>{if(v.preventDefault(),p(!0),h(""),n!==l){h("Passwords do not match"),p(!1);return}await new Promise(b=>setTimeout(b,1e3)),f(!0),p(!1)};return t.jsx("div",{style:{minHeight:"100vh",display:"flex",justifyContent:"center",alignItems:"center",background:"#f5f7fa"},children:t.jsx("div",{style:{background:"white",padding:"2rem",borderRadius:"8px",maxWidth:"400px",width:"90%",boxShadow:"0 4px 6px rgba(0, 0, 0, 0.1)"},children:d?t.jsxs(t.Fragment,{children:[t.jsx("h2",{children:"Password Reset Complete"}),t.jsx("p",{style:{marginBottom:"1.5rem",color:"#666"},children:"Your password has been successfully reset."}),t.jsx("a",{href:"/login",style:{color:"#0056b3"},children:"Go to Login"})]}):t.jsxs(t.Fragment,{children:[t.jsx("h2",{children:"Reset Password"}),t.jsx("p",{style:{marginBottom:"1.5rem",color:"#666"},children:"Enter your new password below."}),g&&t.jsx("div",{style:{color:"red",marginBottom:"1rem"},children:g}),t.jsxs("form",{onSubmit:x,children:[t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{children:"New Password"}),t.jsx("input",{type:"password",value:n,onChange:v=>s(v.target.value),style:{width:"100%",padding:"0.75rem",marginTop:"0.25rem",border:"1px solid #e2e8f0",borderRadius:"4px"},required:!0})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{children:"Confirm New Password"}),t.jsx("input",{type:"password",value:l,onChange:v=>o(v.target.value),style:{width:"100%",padding:"0.75rem",marginTop:"0.25rem",border:"1px solid #e2e8f0",borderRadius:"4px"},required:!0})]}),t.jsx("button",{type:"submit",disabled:m,style:{width:"100%",padding:"0.75rem",background:"#0056b3",color:"white",border:"none",borderRadius:"4px",cursor:"pointer"},children:m?"Resetting...":"Reset Password"})]})]})})})}function $2(){const[n,s]=N.useState(!1),[l,o]=N.useState(!0),[d,f]=N.useState(null),m=fl();console.log("Current pathname:",window.location.pathname),N.useEffect(()=>{(()=>{try{const b=localStorage.getItem("crisp_auth_token"),_=localStorage.getItem("crisp_user");if(b&&_){const C=JSON.parse(_);f(C),s(!0)}}catch(b){console.error("Error validating session:",b),localStorage.removeItem("crisp_auth_token"),localStorage.removeItem("crisp_user")}finally{o(!1)}})()},[]);const p=v=>{try{localStorage.setItem("crisp_auth_token",v.tokens.access),localStorage.setItem("crisp_refresh_token",v.tokens.refresh),localStorage.setItem("crisp_user",JSON.stringify(v.user)),f(v.user),s(!0),m("/dashboard",{replace:!0})}catch(b){console.error("Error storing authentication data:",b),alert("Login error: Unable to store session data")}},g=v=>{try{localStorage.setItem("crisp_auth_token",v.tokens.access),localStorage.setItem("crisp_refresh_token",v.tokens.refresh),localStorage.setItem("crisp_user",JSON.stringify(v.user)),f(v.user),s(!0)}catch(b){console.error("Error storing authentication data:",b),alert("Registration error: Unable to store session data")}},h=()=>{localStorage.removeItem("crisp_auth_token"),localStorage.removeItem("crisp_user"),s(!1),f(null),m("/",{replace:!0})};if(l)return t.jsxs("div",{style:{display:"flex",justifyContent:"center",alignItems:"center",height:"100vh",flexDirection:"column",gap:"20px",fontFamily:"Segoe UI, Tahoma, Geneva, Verdana, sans-serif"},children:[t.jsx("div",{style:{width:"40px",height:"40px",border:"4px solid #f3f3f3",borderTop:"4px solid #0056b3",borderRadius:"50%",animation:"spin 1s linear infinite"}}),t.jsx("p",{style:{color:"#718096",fontSize:"16px"},children:"Checking authentication..."}),t.jsx("style",{children:`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `})]});const x=d&&(d.is_admin===!0||d.is_staff===!0||d.role&&["admin","administrator","bluevisionadmin","superuser","super_user"].includes(d.role.toLowerCase())||d.role&&d.role.toLowerCase().includes("admin"));return console.log("AuthRoutes Debug:"),console.log("- isAuthenticated:",n),console.log("- userData:",d),console.log("- isAdmin:",x),console.log("- handleLogout:",h,typeof h),t.jsxs(ub,{children:[t.jsx(vn,{path:"/",element:n?t.jsx(yn,{to:"/dashboard",replace:!0}):t.jsx(q2,{})}),t.jsx(vn,{path:"/construction",element:t.jsx(l0,{})}),t.jsx(vn,{path:"/login",element:n?t.jsx(yn,{to:"/dashboard",replace:!0}):t.jsx(E2,{onLoginSuccess:p})}),t.jsx(vn,{path:"/forgot-password",element:n?t.jsx(yn,{to:"/dashboard",replace:!0}):t.jsx(H2,{})}),t.jsx(vn,{path:"/reset-password",element:n?t.jsx(yn,{to:"/dashboard",replace:!0}):t.jsx(I2,{})}),t.jsx(vn,{path:"/register-user",element:n?x?t.jsx(Qg,{onRegisterSuccess:()=>{alert("User registered successfully!"),m("/dashboard")},switchView:()=>m("/dashboard")}):t.jsx(yn,{to:"/dashboard",replace:!0}):t.jsx(Qg,{onRegisterSuccess:g,switchView:()=>m("/login")})}),t.jsx(vn,{path:"/dashboard",element:n?t.jsxs(t.Fragment,{children:[console.log("Dashboard route - passing onLogout:",h,typeof h),t.jsx(Nu,{user:d,onLogout:h,isAdmin:x})]}):t.jsx(yn,{to:"/login",replace:!0})}),t.jsx(vn,{path:"/user-management",element:n?x?t.jsx(Nu,{user:d,onLogout:h,isAdmin:x}):t.jsx(yn,{to:"/dashboard",replace:!0}):t.jsx(yn,{to:"/login",replace:!0})}),t.jsx(vn,{path:"/trust-management",element:n?(d==null?void 0:d.role)==="publisher"||(d==null?void 0:d.role)==="BlueVisionAdmin"||x?t.jsx(Nu,{user:d,onLogout:h,isAdmin:x}):t.jsx(yn,{to:"/dashboard",replace:!0}):t.jsx(yn,{to:"/login",replace:!0})}),t.jsx(vn,{path:"*",element:t.jsxs(t.Fragment,{children:[console.log("Catch-all route matched for:",window.location.pathname),t.jsx(yn,{to:"/",replace:!0})]})})]})}window.addEventListener("popstate",()=>{localStorage.getItem("crisp_auth_token")||window.location.reload()});function F2(){return t.jsx(mb,{basename:"/",future:{v7_startTransition:!0,v7_relativeSplatPath:!0},children:t.jsx($2,{})})}jv.createRoot(document.getElementById("root")).render(t.jsx(Fs.StrictMode,{children:t.jsx(F2,{})}));
