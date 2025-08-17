var kv=Object.defineProperty;var Ev=(n,i,l)=>i in n?kv(n,i,{enumerable:!0,configurable:!0,writable:!0,value:l}):n[i]=l;var Dd=(n,i,l)=>Ev(n,typeof i!="symbol"?i+"":i,l);function Mv(n,i){for(var l=0;l<i.length;l++){const o=i[l];if(typeof o!="string"&&!Array.isArray(o)){for(const u in o)if(u!=="default"&&!(u in n)){const f=Object.getOwnPropertyDescriptor(o,u);f&&Object.defineProperty(n,u,f.get?f:{enumerable:!0,get:()=>o[u]})}}}return Object.freeze(Object.defineProperty(n,Symbol.toStringTag,{value:"Module"}))}(function(){const i=document.createElement("link").relList;if(i&&i.supports&&i.supports("modulepreload"))return;for(const u of document.querySelectorAll('link[rel="modulepreload"]'))o(u);new MutationObserver(u=>{for(const f of u)if(f.type==="childList")for(const m of f.addedNodes)m.tagName==="LINK"&&m.rel==="modulepreload"&&o(m)}).observe(document,{childList:!0,subtree:!0});function l(u){const f={};return u.integrity&&(f.integrity=u.integrity),u.referrerPolicy&&(f.referrerPolicy=u.referrerPolicy),u.crossOrigin==="use-credentials"?f.credentials="include":u.crossOrigin==="anonymous"?f.credentials="omit":f.credentials="same-origin",f}function o(u){if(u.ep)return;u.ep=!0;const f=l(u);fetch(u.href,f)}})();function xg(n){return n&&n.__esModule&&Object.prototype.hasOwnProperty.call(n,"default")?n.default:n}var Rd={exports:{}},Rr={};/**
 * @license React
 * react-jsx-runtime.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var op;function Dv(){if(op)return Rr;op=1;var n=Symbol.for("react.transitional.element"),i=Symbol.for("react.fragment");function l(o,u,f){var m=null;if(f!==void 0&&(m=""+f),u.key!==void 0&&(m=""+u.key),"key"in u){f={};for(var x in u)x!=="key"&&(f[x]=u[x])}else f=u;return u=f.ref,{$$typeof:n,type:o,key:m,ref:u!==void 0?u:null,props:f}}return Rr.Fragment=i,Rr.jsx=l,Rr.jsxs=l,Rr}var cp;function Rv(){return cp||(cp=1,Rd.exports=Dv()),Rd.exports}var t=Rv(),Ud={exports:{}},st={};/**
 * @license React
 * react.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var dp;function Uv(){if(dp)return st;dp=1;var n=Symbol.for("react.transitional.element"),i=Symbol.for("react.portal"),l=Symbol.for("react.fragment"),o=Symbol.for("react.strict_mode"),u=Symbol.for("react.profiler"),f=Symbol.for("react.consumer"),m=Symbol.for("react.context"),x=Symbol.for("react.forward_ref"),p=Symbol.for("react.suspense"),h=Symbol.for("react.memo"),v=Symbol.for("react.lazy"),y=Symbol.iterator;function N(T){return T===null||typeof T!="object"?null:(T=y&&T[y]||T["@@iterator"],typeof T=="function"?T:null)}var S={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},A=Object.assign,z={};function U(T,F,le){this.props=T,this.context=F,this.refs=z,this.updater=le||S}U.prototype.isReactComponent={},U.prototype.setState=function(T,F){if(typeof T!="object"&&typeof T!="function"&&T!=null)throw Error("takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,T,F,"setState")},U.prototype.forceUpdate=function(T){this.updater.enqueueForceUpdate(this,T,"forceUpdate")};function oe(){}oe.prototype=U.prototype;function ie(T,F,le){this.props=T,this.context=F,this.refs=z,this.updater=le||S}var me=ie.prototype=new oe;me.constructor=ie,A(me,U.prototype),me.isPureReactComponent=!0;var Ae=Array.isArray,de={H:null,A:null,T:null,S:null,V:null},pe=Object.prototype.hasOwnProperty;function W(T,F,le,ce,fe,Oe){return le=Oe.ref,{$$typeof:n,type:T,key:F,ref:le!==void 0?le:null,props:Oe}}function Ke(T,F){return W(T.type,F,void 0,void 0,void 0,T.props)}function he(T){return typeof T=="object"&&T!==null&&T.$$typeof===n}function De(T){var F={"=":"=0",":":"=2"};return"$"+T.replace(/[=:]/g,function(le){return F[le]})}var xe=/\/+/g;function je(T,F){return typeof T=="object"&&T!==null&&T.key!=null?De(""+T.key):F.toString(36)}function ze(){}function we(T){switch(T.status){case"fulfilled":return T.value;case"rejected":throw T.reason;default:switch(typeof T.status=="string"?T.then(ze,ze):(T.status="pending",T.then(function(F){T.status==="pending"&&(T.status="fulfilled",T.value=F)},function(F){T.status==="pending"&&(T.status="rejected",T.reason=F)})),T.status){case"fulfilled":return T.value;case"rejected":throw T.reason}}throw T}function Ze(T,F,le,ce,fe){var Oe=typeof T;(Oe==="undefined"||Oe==="boolean")&&(T=null);var ve=!1;if(T===null)ve=!0;else switch(Oe){case"bigint":case"string":case"number":ve=!0;break;case"object":switch(T.$$typeof){case n:case i:ve=!0;break;case v:return ve=T._init,Ze(ve(T._payload),F,le,ce,fe)}}if(ve)return fe=fe(T),ve=ce===""?"."+je(T,0):ce,Ae(fe)?(le="",ve!=null&&(le=ve.replace(xe,"$&/")+"/"),Ze(fe,F,le,"",function(re){return re})):fe!=null&&(he(fe)&&(fe=Ke(fe,le+(fe.key==null||T&&T.key===fe.key?"":(""+fe.key).replace(xe,"$&/")+"/")+ve)),F.push(fe)),1;ve=0;var ke=ce===""?".":ce+":";if(Ae(T))for(var $e=0;$e<T.length;$e++)ce=T[$e],Oe=ke+je(ce,$e),ve+=Ze(ce,F,le,Oe,fe);else if($e=N(T),typeof $e=="function")for(T=$e.call(T),$e=0;!(ce=T.next()).done;)ce=ce.value,Oe=ke+je(ce,$e++),ve+=Ze(ce,F,le,Oe,fe);else if(Oe==="object"){if(typeof T.then=="function")return Ze(we(T),F,le,ce,fe);throw F=String(T),Error("Objects are not valid as a React child (found: "+(F==="[object Object]"?"object with keys {"+Object.keys(T).join(", ")+"}":F)+"). If you meant to render a collection of children, use an array instead.")}return ve}function L(T,F,le){if(T==null)return T;var ce=[],fe=0;return Ze(T,ce,"","",function(Oe){return F.call(le,Oe,fe++)}),ce}function ne(T){if(T._status===-1){var F=T._result;F=F(),F.then(function(le){(T._status===0||T._status===-1)&&(T._status=1,T._result=le)},function(le){(T._status===0||T._status===-1)&&(T._status=2,T._result=le)}),T._status===-1&&(T._status=0,T._result=F)}if(T._status===1)return T._result.default;throw T._result}var P=typeof reportError=="function"?reportError:function(T){if(typeof window=="object"&&typeof window.ErrorEvent=="function"){var F=new window.ErrorEvent("error",{bubbles:!0,cancelable:!0,message:typeof T=="object"&&T!==null&&typeof T.message=="string"?String(T.message):String(T),error:T});if(!window.dispatchEvent(F))return}else if(typeof process=="object"&&typeof process.emit=="function"){process.emit("uncaughtException",T);return}console.error(T)};function Ue(){}return st.Children={map:L,forEach:function(T,F,le){L(T,function(){F.apply(this,arguments)},le)},count:function(T){var F=0;return L(T,function(){F++}),F},toArray:function(T){return L(T,function(F){return F})||[]},only:function(T){if(!he(T))throw Error("React.Children.only expected to receive a single React element child.");return T}},st.Component=U,st.Fragment=l,st.Profiler=u,st.PureComponent=ie,st.StrictMode=o,st.Suspense=p,st.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE=de,st.__COMPILER_RUNTIME={__proto__:null,c:function(T){return de.H.useMemoCache(T)}},st.cache=function(T){return function(){return T.apply(null,arguments)}},st.cloneElement=function(T,F,le){if(T==null)throw Error("The argument must be a React element, but you passed "+T+".");var ce=A({},T.props),fe=T.key,Oe=void 0;if(F!=null)for(ve in F.ref!==void 0&&(Oe=void 0),F.key!==void 0&&(fe=""+F.key),F)!pe.call(F,ve)||ve==="key"||ve==="__self"||ve==="__source"||ve==="ref"&&F.ref===void 0||(ce[ve]=F[ve]);var ve=arguments.length-2;if(ve===1)ce.children=le;else if(1<ve){for(var ke=Array(ve),$e=0;$e<ve;$e++)ke[$e]=arguments[$e+2];ce.children=ke}return W(T.type,fe,void 0,void 0,Oe,ce)},st.createContext=function(T){return T={$$typeof:m,_currentValue:T,_currentValue2:T,_threadCount:0,Provider:null,Consumer:null},T.Provider=T,T.Consumer={$$typeof:f,_context:T},T},st.createElement=function(T,F,le){var ce,fe={},Oe=null;if(F!=null)for(ce in F.key!==void 0&&(Oe=""+F.key),F)pe.call(F,ce)&&ce!=="key"&&ce!=="__self"&&ce!=="__source"&&(fe[ce]=F[ce]);var ve=arguments.length-2;if(ve===1)fe.children=le;else if(1<ve){for(var ke=Array(ve),$e=0;$e<ve;$e++)ke[$e]=arguments[$e+2];fe.children=ke}if(T&&T.defaultProps)for(ce in ve=T.defaultProps,ve)fe[ce]===void 0&&(fe[ce]=ve[ce]);return W(T,Oe,void 0,void 0,null,fe)},st.createRef=function(){return{current:null}},st.forwardRef=function(T){return{$$typeof:x,render:T}},st.isValidElement=he,st.lazy=function(T){return{$$typeof:v,_payload:{_status:-1,_result:T},_init:ne}},st.memo=function(T,F){return{$$typeof:h,type:T,compare:F===void 0?null:F}},st.startTransition=function(T){var F=de.T,le={};de.T=le;try{var ce=T(),fe=de.S;fe!==null&&fe(le,ce),typeof ce=="object"&&ce!==null&&typeof ce.then=="function"&&ce.then(Ue,P)}catch(Oe){P(Oe)}finally{de.T=F}},st.unstable_useCacheRefresh=function(){return de.H.useCacheRefresh()},st.use=function(T){return de.H.use(T)},st.useActionState=function(T,F,le){return de.H.useActionState(T,F,le)},st.useCallback=function(T,F){return de.H.useCallback(T,F)},st.useContext=function(T){return de.H.useContext(T)},st.useDebugValue=function(){},st.useDeferredValue=function(T,F){return de.H.useDeferredValue(T,F)},st.useEffect=function(T,F,le){var ce=de.H;if(typeof le=="function")throw Error("useEffect CRUD overload is not enabled in this build of React.");return ce.useEffect(T,F)},st.useId=function(){return de.H.useId()},st.useImperativeHandle=function(T,F,le){return de.H.useImperativeHandle(T,F,le)},st.useInsertionEffect=function(T,F){return de.H.useInsertionEffect(T,F)},st.useLayoutEffect=function(T,F){return de.H.useLayoutEffect(T,F)},st.useMemo=function(T,F){return de.H.useMemo(T,F)},st.useOptimistic=function(T,F){return de.H.useOptimistic(T,F)},st.useReducer=function(T,F,le){return de.H.useReducer(T,F,le)},st.useRef=function(T){return de.H.useRef(T)},st.useState=function(T){return de.H.useState(T)},st.useSyncExternalStore=function(T,F,le){return de.H.useSyncExternalStore(T,F,le)},st.useTransition=function(){return de.H.useTransition()},st.version="19.1.1",st}var up;function pu(){return up||(up=1,Ud.exports=Uv()),Ud.exports}var w=pu();const Ui=xg(w),Ov=Mv({__proto__:null,default:Ui},[w]);var Od={exports:{}},Ur={},Ld={exports:{}},qd={};/**
 * @license React
 * scheduler.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var fp;function Lv(){return fp||(fp=1,(function(n){function i(L,ne){var P=L.length;L.push(ne);e:for(;0<P;){var Ue=P-1>>>1,T=L[Ue];if(0<u(T,ne))L[Ue]=ne,L[P]=T,P=Ue;else break e}}function l(L){return L.length===0?null:L[0]}function o(L){if(L.length===0)return null;var ne=L[0],P=L.pop();if(P!==ne){L[0]=P;e:for(var Ue=0,T=L.length,F=T>>>1;Ue<F;){var le=2*(Ue+1)-1,ce=L[le],fe=le+1,Oe=L[fe];if(0>u(ce,P))fe<T&&0>u(Oe,ce)?(L[Ue]=Oe,L[fe]=P,Ue=fe):(L[Ue]=ce,L[le]=P,Ue=le);else if(fe<T&&0>u(Oe,P))L[Ue]=Oe,L[fe]=P,Ue=fe;else break e}}return ne}function u(L,ne){var P=L.sortIndex-ne.sortIndex;return P!==0?P:L.id-ne.id}if(n.unstable_now=void 0,typeof performance=="object"&&typeof performance.now=="function"){var f=performance;n.unstable_now=function(){return f.now()}}else{var m=Date,x=m.now();n.unstable_now=function(){return m.now()-x}}var p=[],h=[],v=1,y=null,N=3,S=!1,A=!1,z=!1,U=!1,oe=typeof setTimeout=="function"?setTimeout:null,ie=typeof clearTimeout=="function"?clearTimeout:null,me=typeof setImmediate<"u"?setImmediate:null;function Ae(L){for(var ne=l(h);ne!==null;){if(ne.callback===null)o(h);else if(ne.startTime<=L)o(h),ne.sortIndex=ne.expirationTime,i(p,ne);else break;ne=l(h)}}function de(L){if(z=!1,Ae(L),!A)if(l(p)!==null)A=!0,pe||(pe=!0,je());else{var ne=l(h);ne!==null&&Ze(de,ne.startTime-L)}}var pe=!1,W=-1,Ke=5,he=-1;function De(){return U?!0:!(n.unstable_now()-he<Ke)}function xe(){if(U=!1,pe){var L=n.unstable_now();he=L;var ne=!0;try{e:{A=!1,z&&(z=!1,ie(W),W=-1),S=!0;var P=N;try{t:{for(Ae(L),y=l(p);y!==null&&!(y.expirationTime>L&&De());){var Ue=y.callback;if(typeof Ue=="function"){y.callback=null,N=y.priorityLevel;var T=Ue(y.expirationTime<=L);if(L=n.unstable_now(),typeof T=="function"){y.callback=T,Ae(L),ne=!0;break t}y===l(p)&&o(p),Ae(L)}else o(p);y=l(p)}if(y!==null)ne=!0;else{var F=l(h);F!==null&&Ze(de,F.startTime-L),ne=!1}}break e}finally{y=null,N=P,S=!1}ne=void 0}}finally{ne?je():pe=!1}}}var je;if(typeof me=="function")je=function(){me(xe)};else if(typeof MessageChannel<"u"){var ze=new MessageChannel,we=ze.port2;ze.port1.onmessage=xe,je=function(){we.postMessage(null)}}else je=function(){oe(xe,0)};function Ze(L,ne){W=oe(function(){L(n.unstable_now())},ne)}n.unstable_IdlePriority=5,n.unstable_ImmediatePriority=1,n.unstable_LowPriority=4,n.unstable_NormalPriority=3,n.unstable_Profiling=null,n.unstable_UserBlockingPriority=2,n.unstable_cancelCallback=function(L){L.callback=null},n.unstable_forceFrameRate=function(L){0>L||125<L?console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported"):Ke=0<L?Math.floor(1e3/L):5},n.unstable_getCurrentPriorityLevel=function(){return N},n.unstable_next=function(L){switch(N){case 1:case 2:case 3:var ne=3;break;default:ne=N}var P=N;N=ne;try{return L()}finally{N=P}},n.unstable_requestPaint=function(){U=!0},n.unstable_runWithPriority=function(L,ne){switch(L){case 1:case 2:case 3:case 4:case 5:break;default:L=3}var P=N;N=L;try{return ne()}finally{N=P}},n.unstable_scheduleCallback=function(L,ne,P){var Ue=n.unstable_now();switch(typeof P=="object"&&P!==null?(P=P.delay,P=typeof P=="number"&&0<P?Ue+P:Ue):P=Ue,L){case 1:var T=-1;break;case 2:T=250;break;case 5:T=1073741823;break;case 4:T=1e4;break;default:T=5e3}return T=P+T,L={id:v++,callback:ne,priorityLevel:L,startTime:P,expirationTime:T,sortIndex:-1},P>Ue?(L.sortIndex=P,i(h,L),l(p)===null&&L===l(h)&&(z?(ie(W),W=-1):z=!0,Ze(de,P-Ue))):(L.sortIndex=T,i(p,L),A||S||(A=!0,pe||(pe=!0,je()))),L},n.unstable_shouldYield=De,n.unstable_wrapCallback=function(L){var ne=N;return function(){var P=N;N=ne;try{return L.apply(this,arguments)}finally{N=P}}}})(qd)),qd}var hp;function qv(){return hp||(hp=1,Ld.exports=Lv()),Ld.exports}var Bd={exports:{}},za={};/**
 * @license React
 * react-dom.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var mp;function Bv(){if(mp)return za;mp=1;var n=pu();function i(p){var h="https://react.dev/errors/"+p;if(1<arguments.length){h+="?args[]="+encodeURIComponent(arguments[1]);for(var v=2;v<arguments.length;v++)h+="&args[]="+encodeURIComponent(arguments[v])}return"Minified React error #"+p+"; visit "+h+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}function l(){}var o={d:{f:l,r:function(){throw Error(i(522))},D:l,C:l,L:l,m:l,X:l,S:l,M:l},p:0,findDOMNode:null},u=Symbol.for("react.portal");function f(p,h,v){var y=3<arguments.length&&arguments[3]!==void 0?arguments[3]:null;return{$$typeof:u,key:y==null?null:""+y,children:p,containerInfo:h,implementation:v}}var m=n.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE;function x(p,h){if(p==="font")return"";if(typeof h=="string")return h==="use-credentials"?h:""}return za.__DOM_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE=o,za.createPortal=function(p,h){var v=2<arguments.length&&arguments[2]!==void 0?arguments[2]:null;if(!h||h.nodeType!==1&&h.nodeType!==9&&h.nodeType!==11)throw Error(i(299));return f(p,h,null,v)},za.flushSync=function(p){var h=m.T,v=o.p;try{if(m.T=null,o.p=2,p)return p()}finally{m.T=h,o.p=v,o.d.f()}},za.preconnect=function(p,h){typeof p=="string"&&(h?(h=h.crossOrigin,h=typeof h=="string"?h==="use-credentials"?h:"":void 0):h=null,o.d.C(p,h))},za.prefetchDNS=function(p){typeof p=="string"&&o.d.D(p)},za.preinit=function(p,h){if(typeof p=="string"&&h&&typeof h.as=="string"){var v=h.as,y=x(v,h.crossOrigin),N=typeof h.integrity=="string"?h.integrity:void 0,S=typeof h.fetchPriority=="string"?h.fetchPriority:void 0;v==="style"?o.d.S(p,typeof h.precedence=="string"?h.precedence:void 0,{crossOrigin:y,integrity:N,fetchPriority:S}):v==="script"&&o.d.X(p,{crossOrigin:y,integrity:N,fetchPriority:S,nonce:typeof h.nonce=="string"?h.nonce:void 0})}},za.preinitModule=function(p,h){if(typeof p=="string")if(typeof h=="object"&&h!==null){if(h.as==null||h.as==="script"){var v=x(h.as,h.crossOrigin);o.d.M(p,{crossOrigin:v,integrity:typeof h.integrity=="string"?h.integrity:void 0,nonce:typeof h.nonce=="string"?h.nonce:void 0})}}else h==null&&o.d.M(p)},za.preload=function(p,h){if(typeof p=="string"&&typeof h=="object"&&h!==null&&typeof h.as=="string"){var v=h.as,y=x(v,h.crossOrigin);o.d.L(p,v,{crossOrigin:y,integrity:typeof h.integrity=="string"?h.integrity:void 0,nonce:typeof h.nonce=="string"?h.nonce:void 0,type:typeof h.type=="string"?h.type:void 0,fetchPriority:typeof h.fetchPriority=="string"?h.fetchPriority:void 0,referrerPolicy:typeof h.referrerPolicy=="string"?h.referrerPolicy:void 0,imageSrcSet:typeof h.imageSrcSet=="string"?h.imageSrcSet:void 0,imageSizes:typeof h.imageSizes=="string"?h.imageSizes:void 0,media:typeof h.media=="string"?h.media:void 0})}},za.preloadModule=function(p,h){if(typeof p=="string")if(h){var v=x(h.as,h.crossOrigin);o.d.m(p,{as:typeof h.as=="string"&&h.as!=="script"?h.as:void 0,crossOrigin:v,integrity:typeof h.integrity=="string"?h.integrity:void 0})}else o.d.m(p)},za.requestFormReset=function(p){o.d.r(p)},za.unstable_batchedUpdates=function(p,h){return p(h)},za.useFormState=function(p,h,v){return m.H.useFormState(p,h,v)},za.useFormStatus=function(){return m.H.useHostTransitionStatus()},za.version="19.1.1",za}var pp;function vg(){if(pp)return Bd.exports;pp=1;function n(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(n)}catch(i){console.error(i)}}return n(),Bd.exports=Bv(),Bd.exports}/**
 * @license React
 * react-dom-client.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var gp;function Hv(){if(gp)return Ur;gp=1;var n=qv(),i=pu(),l=vg();function o(e){var a="https://react.dev/errors/"+e;if(1<arguments.length){a+="?args[]="+encodeURIComponent(arguments[1]);for(var s=2;s<arguments.length;s++)a+="&args[]="+encodeURIComponent(arguments[s])}return"Minified React error #"+e+"; visit "+a+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}function u(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11)}function f(e){var a=e,s=e;if(e.alternate)for(;a.return;)a=a.return;else{e=a;do a=e,(a.flags&4098)!==0&&(s=a.return),e=a.return;while(e)}return a.tag===3?s:null}function m(e){if(e.tag===13){var a=e.memoizedState;if(a===null&&(e=e.alternate,e!==null&&(a=e.memoizedState)),a!==null)return a.dehydrated}return null}function x(e){if(f(e)!==e)throw Error(o(188))}function p(e){var a=e.alternate;if(!a){if(a=f(e),a===null)throw Error(o(188));return a!==e?null:e}for(var s=e,r=a;;){var c=s.return;if(c===null)break;var d=c.alternate;if(d===null){if(r=c.return,r!==null){s=r;continue}break}if(c.child===d.child){for(d=c.child;d;){if(d===s)return x(c),e;if(d===r)return x(c),a;d=d.sibling}throw Error(o(188))}if(s.return!==r.return)s=c,r=d;else{for(var g=!1,j=c.child;j;){if(j===s){g=!0,s=c,r=d;break}if(j===r){g=!0,r=c,s=d;break}j=j.sibling}if(!g){for(j=d.child;j;){if(j===s){g=!0,s=d,r=c;break}if(j===r){g=!0,r=d,s=c;break}j=j.sibling}if(!g)throw Error(o(189))}}if(s.alternate!==r)throw Error(o(190))}if(s.tag!==3)throw Error(o(188));return s.stateNode.current===s?e:a}function h(e){var a=e.tag;if(a===5||a===26||a===27||a===6)return e;for(e=e.child;e!==null;){if(a=h(e),a!==null)return a;e=e.sibling}return null}var v=Object.assign,y=Symbol.for("react.element"),N=Symbol.for("react.transitional.element"),S=Symbol.for("react.portal"),A=Symbol.for("react.fragment"),z=Symbol.for("react.strict_mode"),U=Symbol.for("react.profiler"),oe=Symbol.for("react.provider"),ie=Symbol.for("react.consumer"),me=Symbol.for("react.context"),Ae=Symbol.for("react.forward_ref"),de=Symbol.for("react.suspense"),pe=Symbol.for("react.suspense_list"),W=Symbol.for("react.memo"),Ke=Symbol.for("react.lazy"),he=Symbol.for("react.activity"),De=Symbol.for("react.memo_cache_sentinel"),xe=Symbol.iterator;function je(e){return e===null||typeof e!="object"?null:(e=xe&&e[xe]||e["@@iterator"],typeof e=="function"?e:null)}var ze=Symbol.for("react.client.reference");function we(e){if(e==null)return null;if(typeof e=="function")return e.$$typeof===ze?null:e.displayName||e.name||null;if(typeof e=="string")return e;switch(e){case A:return"Fragment";case U:return"Profiler";case z:return"StrictMode";case de:return"Suspense";case pe:return"SuspenseList";case he:return"Activity"}if(typeof e=="object")switch(e.$$typeof){case S:return"Portal";case me:return(e.displayName||"Context")+".Provider";case ie:return(e._context.displayName||"Context")+".Consumer";case Ae:var a=e.render;return e=e.displayName,e||(e=a.displayName||a.name||"",e=e!==""?"ForwardRef("+e+")":"ForwardRef"),e;case W:return a=e.displayName||null,a!==null?a:we(e.type)||"Memo";case Ke:a=e._payload,e=e._init;try{return we(e(a))}catch{}}return null}var Ze=Array.isArray,L=i.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE,ne=l.__DOM_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE,P={pending:!1,data:null,method:null,action:null},Ue=[],T=-1;function F(e){return{current:e}}function le(e){0>T||(e.current=Ue[T],Ue[T]=null,T--)}function ce(e,a){T++,Ue[T]=e.current,e.current=a}var fe=F(null),Oe=F(null),ve=F(null),ke=F(null);function $e(e,a){switch(ce(ve,a),ce(Oe,e),ce(fe,null),a.nodeType){case 9:case 11:e=(e=a.documentElement)&&(e=e.namespaceURI)?Om(e):0;break;default:if(e=a.tagName,a=a.namespaceURI)a=Om(a),e=Lm(a,e);else switch(e){case"svg":e=1;break;case"math":e=2;break;default:e=0}}le(fe),ce(fe,e)}function re(){le(fe),le(Oe),le(ve)}function k(e){e.memoizedState!==null&&ce(ke,e);var a=fe.current,s=Lm(a,e.type);a!==s&&(ce(Oe,e),ce(fe,s))}function se(e){Oe.current===e&&(le(fe),le(Oe)),ke.current===e&&(le(ke),zr._currentValue=P)}var V=Object.prototype.hasOwnProperty,ue=n.unstable_scheduleCallback,Se=n.unstable_cancelCallback,Fe=n.unstable_shouldYield,it=n.unstable_requestPaint,et=n.unstable_now,Gt=n.unstable_getCurrentPriorityLevel,wt=n.unstable_ImmediatePriority,Tt=n.unstable_UserBlockingPriority,It=n.unstable_NormalPriority,Kt=n.unstable_LowPriority,G=n.unstable_IdlePriority,Te=n.log,Be=n.unstable_setDisableYieldValue,Ne=null,Re=null;function xt(e){if(typeof Te=="function"&&Be(e),Re&&typeof Re.setStrictMode=="function")try{Re.setStrictMode(Ne,e)}catch{}}var ft=Math.clz32?Math.clz32:M,B=Math.log,Ce=Math.LN2;function M(e){return e>>>=0,e===0?32:31-(B(e)/Ce|0)|0}var Q=256,$=4194304;function ye(e){var a=e&42;if(a!==0)return a;switch(e&-e){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:return 64;case 128:return 128;case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return e&4194048;case 4194304:case 8388608:case 16777216:case 33554432:return e&62914560;case 67108864:return 67108864;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 0;default:return e}}function Ge(e,a,s){var r=e.pendingLanes;if(r===0)return 0;var c=0,d=e.suspendedLanes,g=e.pingedLanes;e=e.warmLanes;var j=r&134217727;return j!==0?(r=j&~d,r!==0?c=ye(r):(g&=j,g!==0?c=ye(g):s||(s=j&~e,s!==0&&(c=ye(s))))):(j=r&~d,j!==0?c=ye(j):g!==0?c=ye(g):s||(s=r&~e,s!==0&&(c=ye(s)))),c===0?0:a!==0&&a!==c&&(a&d)===0&&(d=c&-c,s=a&-a,d>=s||d===32&&(s&4194048)!==0)?a:c}function tt(e,a){return(e.pendingLanes&~(e.suspendedLanes&~e.pingedLanes)&a)===0}function ae(e,a){switch(e){case 1:case 2:case 4:case 8:case 64:return a+250;case 16:case 32:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return a+5e3;case 4194304:case 8388608:case 16777216:case 33554432:return-1;case 67108864:case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}function Ot(){var e=Q;return Q<<=1,(Q&4194048)===0&&(Q=256),e}function _t(){var e=$;return $<<=1,($&62914560)===0&&($=4194304),e}function _e(e){for(var a=[],s=0;31>s;s++)a.push(e);return a}function We(e,a){e.pendingLanes|=a,a!==268435456&&(e.suspendedLanes=0,e.pingedLanes=0,e.warmLanes=0)}function D(e,a,s,r,c,d){var g=e.pendingLanes;e.pendingLanes=s,e.suspendedLanes=0,e.pingedLanes=0,e.warmLanes=0,e.expiredLanes&=s,e.entangledLanes&=s,e.errorRecoveryDisabledLanes&=s,e.shellSuspendCounter=0;var j=e.entanglements,C=e.expirationTimes,q=e.hiddenUpdates;for(s=g&~s;0<s;){var X=31-ft(s),te=1<<X;j[X]=0,C[X]=-1;var H=q[X];if(H!==null)for(q[X]=null,X=0;X<H.length;X++){var I=H[X];I!==null&&(I.lane&=-536870913)}s&=~te}r!==0&&ee(e,r,0),d!==0&&c===0&&e.tag!==0&&(e.suspendedLanes|=d&~(g&~a))}function ee(e,a,s){e.pendingLanes|=a,e.suspendedLanes&=~a;var r=31-ft(a);e.entangledLanes|=a,e.entanglements[r]=e.entanglements[r]|1073741824|s&4194090}function at(e,a){var s=e.entangledLanes|=a;for(e=e.entanglements;s;){var r=31-ft(s),c=1<<r;c&a|e[r]&a&&(e[r]|=a),s&=~c}}function jt(e){switch(e){case 2:e=1;break;case 8:e=4;break;case 32:e=16;break;case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:e=128;break;case 268435456:e=134217728;break;default:e=0}return e}function ht(e){return e&=-e,2<e?8<e?(e&134217727)!==0?32:268435456:8:2}function kt(){var e=ne.p;return e!==0?e:(e=window.event,e===void 0?32:ap(e.type))}function vt(e,a){var s=ne.p;try{return ne.p=e,a()}finally{ne.p=s}}var St=Math.random().toString(36).slice(2),Ee="__reactFiber$"+St,Pe="__reactProps$"+St,Wt="__reactContainer$"+St,Et="__reactEvents$"+St,qt="__reactListeners$"+St,Jn="__reactHandles$"+St,Pt="__reactResources$"+St,da="__reactMarker$"+St;function Za(e){delete e[Ee],delete e[Pe],delete e[Et],delete e[qt],delete e[Jn]}function Da(e){var a=e[Ee];if(a)return a;for(var s=e.parentNode;s;){if(a=s[Wt]||s[Ee]){if(s=a.alternate,a.child!==null||s!==null&&s.child!==null)for(e=Im(e);e!==null;){if(s=e[Ee])return s;e=Im(e)}return a}e=s,s=e.parentNode}return null}function Ha(e){if(e=e[Ee]||e[Wt]){var a=e.tag;if(a===5||a===6||a===13||a===26||a===27||a===3)return e}return null}function ia(e){var a=e.tag;if(a===5||a===26||a===27||a===6)return e.stateNode;throw Error(o(33))}function ka(e){var a=e[Pt];return a||(a=e[Pt]={hoistableStyles:new Map,hoistableScripts:new Map}),a}function pt(e){e[da]=!0}var xa=new Set,ut={};function _a(e,a){Qa(e,a),Qa(e+"Capture",a)}function Qa(e,a){for(ut[e]=a,e=0;e<a.length;e++)xa.add(a[e])}var ra=RegExp("^[:A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD][:A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD\\-.0-9\\u00B7\\u0300-\\u036F\\u203F-\\u2040]*$"),Kn={},Wn={};function $i(e){return V.call(Wn,e)?!0:V.call(Kn,e)?!1:ra.test(e)?Wn[e]=!0:(Kn[e]=!0,!1)}function Sn(e,a,s){if($i(a))if(s===null)e.removeAttribute(a);else{switch(typeof s){case"undefined":case"function":case"symbol":e.removeAttribute(a);return;case"boolean":var r=a.toLowerCase().slice(0,5);if(r!=="data-"&&r!=="aria-"){e.removeAttribute(a);return}}e.setAttribute(a,""+s)}}function es(e,a,s){if(s===null)e.removeAttribute(a);else{switch(typeof s){case"undefined":case"function":case"symbol":case"boolean":e.removeAttribute(a);return}e.setAttribute(a,""+s)}}function Ra(e,a,s,r){if(r===null)e.removeAttribute(s);else{switch(typeof r){case"undefined":case"function":case"symbol":case"boolean":e.removeAttribute(s);return}e.setAttributeNS(a,s,""+r)}}var Tn,Cn;function ua(e){if(Tn===void 0)try{throw Error()}catch(s){var a=s.stack.trim().match(/\n( *(at )?)/);Tn=a&&a[1]||"",Cn=-1<s.stack.indexOf(`
    at`)?" (<anonymous>)":-1<s.stack.indexOf("@")?"@unknown:0:0":""}return`
`+Tn+e+Cn}var An=!1;function zn(e,a){if(!e||An)return"";An=!0;var s=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{var r={DetermineComponentFrameRoot:function(){try{if(a){var te=function(){throw Error()};if(Object.defineProperty(te.prototype,"props",{set:function(){throw Error()}}),typeof Reflect=="object"&&Reflect.construct){try{Reflect.construct(te,[])}catch(I){var H=I}Reflect.construct(e,[],te)}else{try{te.call()}catch(I){H=I}e.call(te.prototype)}}else{try{throw Error()}catch(I){H=I}(te=e())&&typeof te.catch=="function"&&te.catch(function(){})}}catch(I){if(I&&H&&typeof I.stack=="string")return[I.stack,H.stack]}return[null,null]}};r.DetermineComponentFrameRoot.displayName="DetermineComponentFrameRoot";var c=Object.getOwnPropertyDescriptor(r.DetermineComponentFrameRoot,"name");c&&c.configurable&&Object.defineProperty(r.DetermineComponentFrameRoot,"name",{value:"DetermineComponentFrameRoot"});var d=r.DetermineComponentFrameRoot(),g=d[0],j=d[1];if(g&&j){var C=g.split(`
`),q=j.split(`
`);for(c=r=0;r<C.length&&!C[r].includes("DetermineComponentFrameRoot");)r++;for(;c<q.length&&!q[c].includes("DetermineComponentFrameRoot");)c++;if(r===C.length||c===q.length)for(r=C.length-1,c=q.length-1;1<=r&&0<=c&&C[r]!==q[c];)c--;for(;1<=r&&0<=c;r--,c--)if(C[r]!==q[c]){if(r!==1||c!==1)do if(r--,c--,0>c||C[r]!==q[c]){var X=`
`+C[r].replace(" at new "," at ");return e.displayName&&X.includes("<anonymous>")&&(X=X.replace("<anonymous>",e.displayName)),X}while(1<=r&&0<=c);break}}}finally{An=!1,Error.prepareStackTrace=s}return(s=e?e.displayName||e.name:"")?ua(s):""}function Ss(e){switch(e.tag){case 26:case 27:case 5:return ua(e.type);case 16:return ua("Lazy");case 13:return ua("Suspense");case 19:return ua("SuspenseList");case 0:case 15:return zn(e.type,!1);case 11:return zn(e.type.render,!1);case 1:return zn(e.type,!0);case 31:return ua("Activity");default:return""}}function Ws(e){try{var a="";do a+=Ss(e),e=e.return;while(e);return a}catch(s){return`
Error generating stack: `+s.message+`
`+s.stack}}function va(e){switch(typeof e){case"bigint":case"boolean":case"number":case"string":case"undefined":return e;case"object":return e;default:return""}}function ln(e){var a=e.type;return(e=e.nodeName)&&e.toLowerCase()==="input"&&(a==="checkbox"||a==="radio")}function ei(e){var a=ln(e)?"checked":"value",s=Object.getOwnPropertyDescriptor(e.constructor.prototype,a),r=""+e[a];if(!e.hasOwnProperty(a)&&typeof s<"u"&&typeof s.get=="function"&&typeof s.set=="function"){var c=s.get,d=s.set;return Object.defineProperty(e,a,{configurable:!0,get:function(){return c.call(this)},set:function(g){r=""+g,d.call(this,g)}}),Object.defineProperty(e,a,{enumerable:s.enumerable}),{getValue:function(){return r},setValue:function(g){r=""+g},stopTracking:function(){e._valueTracker=null,delete e[a]}}}}function Ja(e){e._valueTracker||(e._valueTracker=ei(e))}function kn(e){if(!e)return!1;var a=e._valueTracker;if(!a)return!0;var s=a.getValue(),r="";return e&&(r=ln(e)?e.checked?"true":"false":e.value),e=r,e!==s?(a.setValue(e),!0):!1}function En(e){if(e=e||(typeof document<"u"?document:void 0),typeof e>"u")return null;try{return e.activeElement||e.body}catch{return e.body}}var ts=/[\n"\\]/g;function Ft(e){return e.replace(ts,function(a){return"\\"+a.charCodeAt(0).toString(16)+" "})}function Ts(e,a,s,r,c,d,g,j){e.name="",g!=null&&typeof g!="function"&&typeof g!="symbol"&&typeof g!="boolean"?e.type=g:e.removeAttribute("type"),a!=null?g==="number"?(a===0&&e.value===""||e.value!=a)&&(e.value=""+va(a)):e.value!==""+va(a)&&(e.value=""+va(a)):g!=="submit"&&g!=="reset"||e.removeAttribute("value"),a!=null?Y(e,g,va(a)):s!=null?Y(e,g,va(s)):r!=null&&e.removeAttribute("value"),c==null&&d!=null&&(e.defaultChecked=!!d),c!=null&&(e.checked=c&&typeof c!="function"&&typeof c!="symbol"),j!=null&&typeof j!="function"&&typeof j!="symbol"&&typeof j!="boolean"?e.name=""+va(j):e.removeAttribute("name")}function _(e,a,s,r,c,d,g,j){if(d!=null&&typeof d!="function"&&typeof d!="symbol"&&typeof d!="boolean"&&(e.type=d),a!=null||s!=null){if(!(d!=="submit"&&d!=="reset"||a!=null))return;s=s!=null?""+va(s):"",a=a!=null?""+va(a):s,j||a===e.value||(e.value=a),e.defaultValue=a}r=r??c,r=typeof r!="function"&&typeof r!="symbol"&&!!r,e.checked=j?e.checked:!!r,e.defaultChecked=!!r,g!=null&&typeof g!="function"&&typeof g!="symbol"&&typeof g!="boolean"&&(e.name=g)}function Y(e,a,s){a==="number"&&En(e.ownerDocument)===e||e.defaultValue===""+s||(e.defaultValue=""+s)}function Z(e,a,s,r){if(e=e.options,a){a={};for(var c=0;c<s.length;c++)a["$"+s[c]]=!0;for(s=0;s<e.length;s++)c=a.hasOwnProperty("$"+e[s].value),e[s].selected!==c&&(e[s].selected=c),c&&r&&(e[s].defaultSelected=!0)}else{for(s=""+va(s),a=null,c=0;c<e.length;c++){if(e[c].value===s){e[c].selected=!0,r&&(e[c].defaultSelected=!0);return}a!==null||e[c].disabled||(a=e[c])}a!==null&&(a.selected=!0)}}function be(e,a,s){if(a!=null&&(a=""+va(a),a!==e.value&&(e.value=a),s==null)){e.defaultValue!==a&&(e.defaultValue=a);return}e.defaultValue=s!=null?""+va(s):""}function Ve(e,a,s,r){if(a==null){if(r!=null){if(s!=null)throw Error(o(92));if(Ze(r)){if(1<r.length)throw Error(o(93));r=r[0]}s=r}s==null&&(s=""),a=s}s=va(a),e.defaultValue=s,r=e.textContent,r===s&&r!==""&&r!==null&&(e.value=r)}function qe(e,a){if(a){var s=e.firstChild;if(s&&s===e.lastChild&&s.nodeType===3){s.nodeValue=a;return}}e.textContent=a}var $t=new Set("animationIterationCount aspectRatio borderImageOutset borderImageSlice borderImageWidth boxFlex boxFlexGroup boxOrdinalGroup columnCount columns flex flexGrow flexPositive flexShrink flexNegative flexOrder gridArea gridRow gridRowEnd gridRowSpan gridRowStart gridColumn gridColumnEnd gridColumnSpan gridColumnStart fontWeight lineClamp lineHeight opacity order orphans scale tabSize widows zIndex zoom fillOpacity floodOpacity stopOpacity strokeDasharray strokeDashoffset strokeMiterlimit strokeOpacity strokeWidth MozAnimationIterationCount MozBoxFlex MozBoxFlexGroup MozLineClamp msAnimationIterationCount msFlex msZoom msFlexGrow msFlexNegative msFlexOrder msFlexPositive msFlexShrink msGridColumn msGridColumnSpan msGridRow msGridRowSpan WebkitAnimationIterationCount WebkitBoxFlex WebKitBoxFlexGroup WebkitBoxOrdinalGroup WebkitColumnCount WebkitColumns WebkitFlex WebkitFlexGrow WebkitFlexPositive WebkitFlexShrink WebkitLineClamp".split(" "));function Zt(e,a,s){var r=a.indexOf("--")===0;s==null||typeof s=="boolean"||s===""?r?e.setProperty(a,""):a==="float"?e.cssFloat="":e[a]="":r?e.setProperty(a,s):typeof s!="number"||s===0||$t.has(a)?a==="float"?e.cssFloat=s:e[a]=(""+s).trim():e[a]=s+"px"}function Sa(e,a,s){if(a!=null&&typeof a!="object")throw Error(o(62));if(e=e.style,s!=null){for(var r in s)!s.hasOwnProperty(r)||a!=null&&a.hasOwnProperty(r)||(r.indexOf("--")===0?e.setProperty(r,""):r==="float"?e.cssFloat="":e[r]="");for(var c in a)r=a[c],a.hasOwnProperty(c)&&s[c]!==r&&Zt(e,c,r)}else for(var d in a)a.hasOwnProperty(d)&&Zt(e,d,a[d])}function b(e){if(e.indexOf("-")===-1)return!1;switch(e){case"annotation-xml":case"color-profile":case"font-face":case"font-face-src":case"font-face-uri":case"font-face-format":case"font-face-name":case"missing-glyph":return!1;default:return!0}}var K=new Map([["acceptCharset","accept-charset"],["htmlFor","for"],["httpEquiv","http-equiv"],["crossOrigin","crossorigin"],["accentHeight","accent-height"],["alignmentBaseline","alignment-baseline"],["arabicForm","arabic-form"],["baselineShift","baseline-shift"],["capHeight","cap-height"],["clipPath","clip-path"],["clipRule","clip-rule"],["colorInterpolation","color-interpolation"],["colorInterpolationFilters","color-interpolation-filters"],["colorProfile","color-profile"],["colorRendering","color-rendering"],["dominantBaseline","dominant-baseline"],["enableBackground","enable-background"],["fillOpacity","fill-opacity"],["fillRule","fill-rule"],["floodColor","flood-color"],["floodOpacity","flood-opacity"],["fontFamily","font-family"],["fontSize","font-size"],["fontSizeAdjust","font-size-adjust"],["fontStretch","font-stretch"],["fontStyle","font-style"],["fontVariant","font-variant"],["fontWeight","font-weight"],["glyphName","glyph-name"],["glyphOrientationHorizontal","glyph-orientation-horizontal"],["glyphOrientationVertical","glyph-orientation-vertical"],["horizAdvX","horiz-adv-x"],["horizOriginX","horiz-origin-x"],["imageRendering","image-rendering"],["letterSpacing","letter-spacing"],["lightingColor","lighting-color"],["markerEnd","marker-end"],["markerMid","marker-mid"],["markerStart","marker-start"],["overlinePosition","overline-position"],["overlineThickness","overline-thickness"],["paintOrder","paint-order"],["panose-1","panose-1"],["pointerEvents","pointer-events"],["renderingIntent","rendering-intent"],["shapeRendering","shape-rendering"],["stopColor","stop-color"],["stopOpacity","stop-opacity"],["strikethroughPosition","strikethrough-position"],["strikethroughThickness","strikethrough-thickness"],["strokeDasharray","stroke-dasharray"],["strokeDashoffset","stroke-dashoffset"],["strokeLinecap","stroke-linecap"],["strokeLinejoin","stroke-linejoin"],["strokeMiterlimit","stroke-miterlimit"],["strokeOpacity","stroke-opacity"],["strokeWidth","stroke-width"],["textAnchor","text-anchor"],["textDecoration","text-decoration"],["textRendering","text-rendering"],["transformOrigin","transform-origin"],["underlinePosition","underline-position"],["underlineThickness","underline-thickness"],["unicodeBidi","unicode-bidi"],["unicodeRange","unicode-range"],["unitsPerEm","units-per-em"],["vAlphabetic","v-alphabetic"],["vHanging","v-hanging"],["vIdeographic","v-ideographic"],["vMathematical","v-mathematical"],["vectorEffect","vector-effect"],["vertAdvY","vert-adv-y"],["vertOriginX","vert-origin-x"],["vertOriginY","vert-origin-y"],["wordSpacing","word-spacing"],["writingMode","writing-mode"],["xmlnsXlink","xmlns:xlink"],["xHeight","x-height"]]),ge=/^[\u0000-\u001F ]*j[\r\n\t]*a[\r\n\t]*v[\r\n\t]*a[\r\n\t]*s[\r\n\t]*c[\r\n\t]*r[\r\n\t]*i[\r\n\t]*p[\r\n\t]*t[\r\n\t]*:/i;function Me(e){return ge.test(""+e)?"javascript:throw new Error('React has blocked a javascript: URL as a security precaution.')":e}var Qe=null;function Ie(e){return e=e.target||e.srcElement||window,e.correspondingUseElement&&(e=e.correspondingUseElement),e.nodeType===3?e.parentNode:e}var nt=null,ya=null;function Ta(e){var a=Ha(e);if(a&&(e=a.stateNode)){var s=e[Pe]||null;e:switch(e=a.stateNode,a.type){case"input":if(Ts(e,s.value,s.defaultValue,s.defaultValue,s.checked,s.defaultChecked,s.type,s.name),a=s.name,s.type==="radio"&&a!=null){for(s=e;s.parentNode;)s=s.parentNode;for(s=s.querySelectorAll('input[name="'+Ft(""+a)+'"][type="radio"]'),a=0;a<s.length;a++){var r=s[a];if(r!==e&&r.form===e.form){var c=r[Pe]||null;if(!c)throw Error(o(90));Ts(r,c.value,c.defaultValue,c.defaultValue,c.checked,c.defaultChecked,c.type,c.name)}}for(a=0;a<s.length;a++)r=s[a],r.form===e.form&&kn(r)}break e;case"textarea":be(e,s.value,s.defaultValue);break e;case"select":a=s.value,a!=null&&Z(e,!!s.multiple,a,!1)}}}var gt=!1;function Vt(e,a,s){if(gt)return e(a,s);gt=!0;try{var r=e(a);return r}finally{if(gt=!1,(nt!==null||ya!==null)&&(Bl(),nt&&(a=nt,e=ya,ya=nt=null,Ta(a),e)))for(a=0;a<e.length;a++)Ta(e[a])}}function Ca(e,a){var s=e.stateNode;if(s===null)return null;var r=s[Pe]||null;if(r===null)return null;s=r[a];e:switch(a){case"onClick":case"onClickCapture":case"onDoubleClick":case"onDoubleClickCapture":case"onMouseDown":case"onMouseDownCapture":case"onMouseMove":case"onMouseMoveCapture":case"onMouseUp":case"onMouseUpCapture":case"onMouseEnter":(r=!r.disabled)||(e=e.type,r=!(e==="button"||e==="input"||e==="select"||e==="textarea")),e=!r;break e;default:e=!1}if(e)return null;if(s&&typeof s!="function")throw Error(o(231,a,typeof s));return s}var on=!(typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"),Fi=!1;if(on)try{var Bt={};Object.defineProperty(Bt,"passive",{get:function(){Fi=!0}}),window.addEventListener("test",Bt,Bt),window.removeEventListener("test",Bt,Bt)}catch{Fi=!1}var ba=null,Ia=null,tl=null;function Bu(){if(tl)return tl;var e,a=Ia,s=a.length,r,c="value"in ba?ba.value:ba.textContent,d=c.length;for(e=0;e<s&&a[e]===c[e];e++);var g=s-e;for(r=1;r<=g&&a[s-r]===c[d-r];r++);return tl=c.slice(e,1<r?1-r:void 0)}function al(e){var a=e.keyCode;return"charCode"in e?(e=e.charCode,e===0&&a===13&&(e=13)):e=a,e===10&&(e=13),32<=e||e===13?e:0}function nl(){return!0}function Hu(){return!1}function Ua(e){function a(s,r,c,d,g){this._reactName=s,this._targetInst=c,this.type=r,this.nativeEvent=d,this.target=g,this.currentTarget=null;for(var j in e)e.hasOwnProperty(j)&&(s=e[j],this[j]=s?s(d):d[j]);return this.isDefaultPrevented=(d.defaultPrevented!=null?d.defaultPrevented:d.returnValue===!1)?nl:Hu,this.isPropagationStopped=Hu,this}return v(a.prototype,{preventDefault:function(){this.defaultPrevented=!0;var s=this.nativeEvent;s&&(s.preventDefault?s.preventDefault():typeof s.returnValue!="unknown"&&(s.returnValue=!1),this.isDefaultPrevented=nl)},stopPropagation:function(){var s=this.nativeEvent;s&&(s.stopPropagation?s.stopPropagation():typeof s.cancelBubble!="unknown"&&(s.cancelBubble=!0),this.isPropagationStopped=nl)},persist:function(){},isPersistent:nl}),a}var Cs={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(e){return e.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},sl=Ua(Cs),Yi=v({},Cs,{view:0,detail:0}),kx=Ua(Yi),qo,Bo,Gi,il=v({},Yi,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:Io,button:0,buttons:0,relatedTarget:function(e){return e.relatedTarget===void 0?e.fromElement===e.srcElement?e.toElement:e.fromElement:e.relatedTarget},movementX:function(e){return"movementX"in e?e.movementX:(e!==Gi&&(Gi&&e.type==="mousemove"?(qo=e.screenX-Gi.screenX,Bo=e.screenY-Gi.screenY):Bo=qo=0,Gi=e),qo)},movementY:function(e){return"movementY"in e?e.movementY:Bo}}),Iu=Ua(il),Ex=v({},il,{dataTransfer:0}),Mx=Ua(Ex),Dx=v({},Yi,{relatedTarget:0}),Ho=Ua(Dx),Rx=v({},Cs,{animationName:0,elapsedTime:0,pseudoElement:0}),Ux=Ua(Rx),Ox=v({},Cs,{clipboardData:function(e){return"clipboardData"in e?e.clipboardData:window.clipboardData}}),Lx=Ua(Ox),qx=v({},Cs,{data:0}),$u=Ua(qx),Bx={Esc:"Escape",Spacebar:" ",Left:"ArrowLeft",Up:"ArrowUp",Right:"ArrowRight",Down:"ArrowDown",Del:"Delete",Win:"OS",Menu:"ContextMenu",Apps:"ContextMenu",Scroll:"ScrollLock",MozPrintableKey:"Unidentified"},Hx={8:"Backspace",9:"Tab",12:"Clear",13:"Enter",16:"Shift",17:"Control",18:"Alt",19:"Pause",20:"CapsLock",27:"Escape",32:" ",33:"PageUp",34:"PageDown",35:"End",36:"Home",37:"ArrowLeft",38:"ArrowUp",39:"ArrowRight",40:"ArrowDown",45:"Insert",46:"Delete",112:"F1",113:"F2",114:"F3",115:"F4",116:"F5",117:"F6",118:"F7",119:"F8",120:"F9",121:"F10",122:"F11",123:"F12",144:"NumLock",145:"ScrollLock",224:"Meta"},Ix={Alt:"altKey",Control:"ctrlKey",Meta:"metaKey",Shift:"shiftKey"};function $x(e){var a=this.nativeEvent;return a.getModifierState?a.getModifierState(e):(e=Ix[e])?!!a[e]:!1}function Io(){return $x}var Fx=v({},Yi,{key:function(e){if(e.key){var a=Bx[e.key]||e.key;if(a!=="Unidentified")return a}return e.type==="keypress"?(e=al(e),e===13?"Enter":String.fromCharCode(e)):e.type==="keydown"||e.type==="keyup"?Hx[e.keyCode]||"Unidentified":""},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:Io,charCode:function(e){return e.type==="keypress"?al(e):0},keyCode:function(e){return e.type==="keydown"||e.type==="keyup"?e.keyCode:0},which:function(e){return e.type==="keypress"?al(e):e.type==="keydown"||e.type==="keyup"?e.keyCode:0}}),Yx=Ua(Fx),Gx=v({},il,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0}),Fu=Ua(Gx),Px=v({},Yi,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:Io}),Vx=Ua(Px),Xx=v({},Cs,{propertyName:0,elapsedTime:0,pseudoElement:0}),Zx=Ua(Xx),Qx=v({},il,{deltaX:function(e){return"deltaX"in e?e.deltaX:"wheelDeltaX"in e?-e.wheelDeltaX:0},deltaY:function(e){return"deltaY"in e?e.deltaY:"wheelDeltaY"in e?-e.wheelDeltaY:"wheelDelta"in e?-e.wheelDelta:0},deltaZ:0,deltaMode:0}),Jx=Ua(Qx),Kx=v({},Cs,{newState:0,oldState:0}),Wx=Ua(Kx),e0=[9,13,27,32],$o=on&&"CompositionEvent"in window,Pi=null;on&&"documentMode"in document&&(Pi=document.documentMode);var t0=on&&"TextEvent"in window&&!Pi,Yu=on&&(!$o||Pi&&8<Pi&&11>=Pi),Gu=" ",Pu=!1;function Vu(e,a){switch(e){case"keyup":return e0.indexOf(a.keyCode)!==-1;case"keydown":return a.keyCode!==229;case"keypress":case"mousedown":case"focusout":return!0;default:return!1}}function Xu(e){return e=e.detail,typeof e=="object"&&"data"in e?e.data:null}var ti=!1;function a0(e,a){switch(e){case"compositionend":return Xu(a);case"keypress":return a.which!==32?null:(Pu=!0,Gu);case"textInput":return e=a.data,e===Gu&&Pu?null:e;default:return null}}function n0(e,a){if(ti)return e==="compositionend"||!$o&&Vu(e,a)?(e=Bu(),tl=Ia=ba=null,ti=!1,e):null;switch(e){case"paste":return null;case"keypress":if(!(a.ctrlKey||a.altKey||a.metaKey)||a.ctrlKey&&a.altKey){if(a.char&&1<a.char.length)return a.char;if(a.which)return String.fromCharCode(a.which)}return null;case"compositionend":return Yu&&a.locale!=="ko"?null:a.data;default:return null}}var s0={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function Zu(e){var a=e&&e.nodeName&&e.nodeName.toLowerCase();return a==="input"?!!s0[e.type]:a==="textarea"}function Qu(e,a,s,r){nt?ya?ya.push(r):ya=[r]:nt=r,a=Gl(a,"onChange"),0<a.length&&(s=new sl("onChange","change",null,s,r),e.push({event:s,listeners:a}))}var Vi=null,Xi=null;function i0(e){Em(e,0)}function rl(e){var a=ia(e);if(kn(a))return e}function Ju(e,a){if(e==="change")return a}var Ku=!1;if(on){var Fo;if(on){var Yo="oninput"in document;if(!Yo){var Wu=document.createElement("div");Wu.setAttribute("oninput","return;"),Yo=typeof Wu.oninput=="function"}Fo=Yo}else Fo=!1;Ku=Fo&&(!document.documentMode||9<document.documentMode)}function ef(){Vi&&(Vi.detachEvent("onpropertychange",tf),Xi=Vi=null)}function tf(e){if(e.propertyName==="value"&&rl(Xi)){var a=[];Qu(a,Xi,e,Ie(e)),Vt(i0,a)}}function r0(e,a,s){e==="focusin"?(ef(),Vi=a,Xi=s,Vi.attachEvent("onpropertychange",tf)):e==="focusout"&&ef()}function l0(e){if(e==="selectionchange"||e==="keyup"||e==="keydown")return rl(Xi)}function o0(e,a){if(e==="click")return rl(a)}function c0(e,a){if(e==="input"||e==="change")return rl(a)}function d0(e,a){return e===a&&(e!==0||1/e===1/a)||e!==e&&a!==a}var $a=typeof Object.is=="function"?Object.is:d0;function Zi(e,a){if($a(e,a))return!0;if(typeof e!="object"||e===null||typeof a!="object"||a===null)return!1;var s=Object.keys(e),r=Object.keys(a);if(s.length!==r.length)return!1;for(r=0;r<s.length;r++){var c=s[r];if(!V.call(a,c)||!$a(e[c],a[c]))return!1}return!0}function af(e){for(;e&&e.firstChild;)e=e.firstChild;return e}function nf(e,a){var s=af(e);e=0;for(var r;s;){if(s.nodeType===3){if(r=e+s.textContent.length,e<=a&&r>=a)return{node:s,offset:a-e};e=r}e:{for(;s;){if(s.nextSibling){s=s.nextSibling;break e}s=s.parentNode}s=void 0}s=af(s)}}function sf(e,a){return e&&a?e===a?!0:e&&e.nodeType===3?!1:a&&a.nodeType===3?sf(e,a.parentNode):"contains"in e?e.contains(a):e.compareDocumentPosition?!!(e.compareDocumentPosition(a)&16):!1:!1}function rf(e){e=e!=null&&e.ownerDocument!=null&&e.ownerDocument.defaultView!=null?e.ownerDocument.defaultView:window;for(var a=En(e.document);a instanceof e.HTMLIFrameElement;){try{var s=typeof a.contentWindow.location.href=="string"}catch{s=!1}if(s)e=a.contentWindow;else break;a=En(e.document)}return a}function Go(e){var a=e&&e.nodeName&&e.nodeName.toLowerCase();return a&&(a==="input"&&(e.type==="text"||e.type==="search"||e.type==="tel"||e.type==="url"||e.type==="password")||a==="textarea"||e.contentEditable==="true")}var u0=on&&"documentMode"in document&&11>=document.documentMode,ai=null,Po=null,Qi=null,Vo=!1;function lf(e,a,s){var r=s.window===s?s.document:s.nodeType===9?s:s.ownerDocument;Vo||ai==null||ai!==En(r)||(r=ai,"selectionStart"in r&&Go(r)?r={start:r.selectionStart,end:r.selectionEnd}:(r=(r.ownerDocument&&r.ownerDocument.defaultView||window).getSelection(),r={anchorNode:r.anchorNode,anchorOffset:r.anchorOffset,focusNode:r.focusNode,focusOffset:r.focusOffset}),Qi&&Zi(Qi,r)||(Qi=r,r=Gl(Po,"onSelect"),0<r.length&&(a=new sl("onSelect","select",null,a,s),e.push({event:a,listeners:r}),a.target=ai)))}function As(e,a){var s={};return s[e.toLowerCase()]=a.toLowerCase(),s["Webkit"+e]="webkit"+a,s["Moz"+e]="moz"+a,s}var ni={animationend:As("Animation","AnimationEnd"),animationiteration:As("Animation","AnimationIteration"),animationstart:As("Animation","AnimationStart"),transitionrun:As("Transition","TransitionRun"),transitionstart:As("Transition","TransitionStart"),transitioncancel:As("Transition","TransitionCancel"),transitionend:As("Transition","TransitionEnd")},Xo={},of={};on&&(of=document.createElement("div").style,"AnimationEvent"in window||(delete ni.animationend.animation,delete ni.animationiteration.animation,delete ni.animationstart.animation),"TransitionEvent"in window||delete ni.transitionend.transition);function zs(e){if(Xo[e])return Xo[e];if(!ni[e])return e;var a=ni[e],s;for(s in a)if(a.hasOwnProperty(s)&&s in of)return Xo[e]=a[s];return e}var cf=zs("animationend"),df=zs("animationiteration"),uf=zs("animationstart"),f0=zs("transitionrun"),h0=zs("transitionstart"),m0=zs("transitioncancel"),ff=zs("transitionend"),hf=new Map,Zo="abort auxClick beforeToggle cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");Zo.push("scrollEnd");function cn(e,a){hf.set(e,a),_a(a,[e])}var mf=new WeakMap;function Ka(e,a){if(typeof e=="object"&&e!==null){var s=mf.get(e);return s!==void 0?s:(a={value:e,source:a,stack:Ws(a)},mf.set(e,a),a)}return{value:e,source:a,stack:Ws(a)}}var Wa=[],si=0,Qo=0;function ll(){for(var e=si,a=Qo=si=0;a<e;){var s=Wa[a];Wa[a++]=null;var r=Wa[a];Wa[a++]=null;var c=Wa[a];Wa[a++]=null;var d=Wa[a];if(Wa[a++]=null,r!==null&&c!==null){var g=r.pending;g===null?c.next=c:(c.next=g.next,g.next=c),r.pending=c}d!==0&&pf(s,c,d)}}function ol(e,a,s,r){Wa[si++]=e,Wa[si++]=a,Wa[si++]=s,Wa[si++]=r,Qo|=r,e.lanes|=r,e=e.alternate,e!==null&&(e.lanes|=r)}function Jo(e,a,s,r){return ol(e,a,s,r),cl(e)}function ii(e,a){return ol(e,null,null,a),cl(e)}function pf(e,a,s){e.lanes|=s;var r=e.alternate;r!==null&&(r.lanes|=s);for(var c=!1,d=e.return;d!==null;)d.childLanes|=s,r=d.alternate,r!==null&&(r.childLanes|=s),d.tag===22&&(e=d.stateNode,e===null||e._visibility&1||(c=!0)),e=d,d=d.return;return e.tag===3?(d=e.stateNode,c&&a!==null&&(c=31-ft(s),e=d.hiddenUpdates,r=e[c],r===null?e[c]=[a]:r.push(a),a.lane=s|536870912),d):null}function cl(e){if(50<jr)throw jr=0,nd=null,Error(o(185));for(var a=e.return;a!==null;)e=a,a=e.return;return e.tag===3?e.stateNode:null}var ri={};function p0(e,a,s,r){this.tag=e,this.key=s,this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null,this.index=0,this.refCleanup=this.ref=null,this.pendingProps=a,this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null,this.mode=r,this.subtreeFlags=this.flags=0,this.deletions=null,this.childLanes=this.lanes=0,this.alternate=null}function Fa(e,a,s,r){return new p0(e,a,s,r)}function Ko(e){return e=e.prototype,!(!e||!e.isReactComponent)}function Mn(e,a){var s=e.alternate;return s===null?(s=Fa(e.tag,a,e.key,e.mode),s.elementType=e.elementType,s.type=e.type,s.stateNode=e.stateNode,s.alternate=e,e.alternate=s):(s.pendingProps=a,s.type=e.type,s.flags=0,s.subtreeFlags=0,s.deletions=null),s.flags=e.flags&65011712,s.childLanes=e.childLanes,s.lanes=e.lanes,s.child=e.child,s.memoizedProps=e.memoizedProps,s.memoizedState=e.memoizedState,s.updateQueue=e.updateQueue,a=e.dependencies,s.dependencies=a===null?null:{lanes:a.lanes,firstContext:a.firstContext},s.sibling=e.sibling,s.index=e.index,s.ref=e.ref,s.refCleanup=e.refCleanup,s}function gf(e,a){e.flags&=65011714;var s=e.alternate;return s===null?(e.childLanes=0,e.lanes=a,e.child=null,e.subtreeFlags=0,e.memoizedProps=null,e.memoizedState=null,e.updateQueue=null,e.dependencies=null,e.stateNode=null):(e.childLanes=s.childLanes,e.lanes=s.lanes,e.child=s.child,e.subtreeFlags=0,e.deletions=null,e.memoizedProps=s.memoizedProps,e.memoizedState=s.memoizedState,e.updateQueue=s.updateQueue,e.type=s.type,a=s.dependencies,e.dependencies=a===null?null:{lanes:a.lanes,firstContext:a.firstContext}),e}function dl(e,a,s,r,c,d){var g=0;if(r=e,typeof e=="function")Ko(e)&&(g=1);else if(typeof e=="string")g=xv(e,s,fe.current)?26:e==="html"||e==="head"||e==="body"?27:5;else e:switch(e){case he:return e=Fa(31,s,a,c),e.elementType=he,e.lanes=d,e;case A:return ks(s.children,c,d,a);case z:g=8,c|=24;break;case U:return e=Fa(12,s,a,c|2),e.elementType=U,e.lanes=d,e;case de:return e=Fa(13,s,a,c),e.elementType=de,e.lanes=d,e;case pe:return e=Fa(19,s,a,c),e.elementType=pe,e.lanes=d,e;default:if(typeof e=="object"&&e!==null)switch(e.$$typeof){case oe:case me:g=10;break e;case ie:g=9;break e;case Ae:g=11;break e;case W:g=14;break e;case Ke:g=16,r=null;break e}g=29,s=Error(o(130,e===null?"null":typeof e,"")),r=null}return a=Fa(g,s,a,c),a.elementType=e,a.type=r,a.lanes=d,a}function ks(e,a,s,r){return e=Fa(7,e,r,a),e.lanes=s,e}function Wo(e,a,s){return e=Fa(6,e,null,a),e.lanes=s,e}function ec(e,a,s){return a=Fa(4,e.children!==null?e.children:[],e.key,a),a.lanes=s,a.stateNode={containerInfo:e.containerInfo,pendingChildren:null,implementation:e.implementation},a}var li=[],oi=0,ul=null,fl=0,en=[],tn=0,Es=null,Dn=1,Rn="";function Ms(e,a){li[oi++]=fl,li[oi++]=ul,ul=e,fl=a}function xf(e,a,s){en[tn++]=Dn,en[tn++]=Rn,en[tn++]=Es,Es=e;var r=Dn;e=Rn;var c=32-ft(r)-1;r&=~(1<<c),s+=1;var d=32-ft(a)+c;if(30<d){var g=c-c%5;d=(r&(1<<g)-1).toString(32),r>>=g,c-=g,Dn=1<<32-ft(a)+c|s<<c|r,Rn=d+e}else Dn=1<<d|s<<c|r,Rn=e}function tc(e){e.return!==null&&(Ms(e,1),xf(e,1,0))}function ac(e){for(;e===ul;)ul=li[--oi],li[oi]=null,fl=li[--oi],li[oi]=null;for(;e===Es;)Es=en[--tn],en[tn]=null,Rn=en[--tn],en[tn]=null,Dn=en[--tn],en[tn]=null}var Ea=null,Qt=null,Nt=!1,Ds=null,xn=!1,nc=Error(o(519));function Rs(e){var a=Error(o(418,""));throw Wi(Ka(a,e)),nc}function vf(e){var a=e.stateNode,s=e.type,r=e.memoizedProps;switch(a[Ee]=e,a[Pe]=r,s){case"dialog":ct("cancel",a),ct("close",a);break;case"iframe":case"object":case"embed":ct("load",a);break;case"video":case"audio":for(s=0;s<wr.length;s++)ct(wr[s],a);break;case"source":ct("error",a);break;case"img":case"image":case"link":ct("error",a),ct("load",a);break;case"details":ct("toggle",a);break;case"input":ct("invalid",a),_(a,r.value,r.defaultValue,r.checked,r.defaultChecked,r.type,r.name,!0),Ja(a);break;case"select":ct("invalid",a);break;case"textarea":ct("invalid",a),Ve(a,r.value,r.defaultValue,r.children),Ja(a)}s=r.children,typeof s!="string"&&typeof s!="number"&&typeof s!="bigint"||a.textContent===""+s||r.suppressHydrationWarning===!0||Um(a.textContent,s)?(r.popover!=null&&(ct("beforetoggle",a),ct("toggle",a)),r.onScroll!=null&&ct("scroll",a),r.onScrollEnd!=null&&ct("scrollend",a),r.onClick!=null&&(a.onclick=Pl),a=!0):a=!1,a||Rs(e)}function yf(e){for(Ea=e.return;Ea;)switch(Ea.tag){case 5:case 13:xn=!1;return;case 27:case 3:xn=!0;return;default:Ea=Ea.return}}function Ji(e){if(e!==Ea)return!1;if(!Nt)return yf(e),Nt=!0,!1;var a=e.tag,s;if((s=a!==3&&a!==27)&&((s=a===5)&&(s=e.type,s=!(s!=="form"&&s!=="button")||yd(e.type,e.memoizedProps)),s=!s),s&&Qt&&Rs(e),yf(e),a===13){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(o(317));e:{for(e=e.nextSibling,a=0;e;){if(e.nodeType===8)if(s=e.data,s==="/$"){if(a===0){Qt=un(e.nextSibling);break e}a--}else s!=="$"&&s!=="$!"&&s!=="$?"||a++;e=e.nextSibling}Qt=null}}else a===27?(a=Qt,xs(e.type)?(e=wd,wd=null,Qt=e):Qt=a):Qt=Ea?un(e.stateNode.nextSibling):null;return!0}function Ki(){Qt=Ea=null,Nt=!1}function bf(){var e=Ds;return e!==null&&(qa===null?qa=e:qa.push.apply(qa,e),Ds=null),e}function Wi(e){Ds===null?Ds=[e]:Ds.push(e)}var sc=F(null),Us=null,Un=null;function as(e,a,s){ce(sc,a._currentValue),a._currentValue=s}function On(e){e._currentValue=sc.current,le(sc)}function ic(e,a,s){for(;e!==null;){var r=e.alternate;if((e.childLanes&a)!==a?(e.childLanes|=a,r!==null&&(r.childLanes|=a)):r!==null&&(r.childLanes&a)!==a&&(r.childLanes|=a),e===s)break;e=e.return}}function rc(e,a,s,r){var c=e.child;for(c!==null&&(c.return=e);c!==null;){var d=c.dependencies;if(d!==null){var g=c.child;d=d.firstContext;e:for(;d!==null;){var j=d;d=c;for(var C=0;C<a.length;C++)if(j.context===a[C]){d.lanes|=s,j=d.alternate,j!==null&&(j.lanes|=s),ic(d.return,s,e),r||(g=null);break e}d=j.next}}else if(c.tag===18){if(g=c.return,g===null)throw Error(o(341));g.lanes|=s,d=g.alternate,d!==null&&(d.lanes|=s),ic(g,s,e),g=null}else g=c.child;if(g!==null)g.return=c;else for(g=c;g!==null;){if(g===e){g=null;break}if(c=g.sibling,c!==null){c.return=g.return,g=c;break}g=g.return}c=g}}function er(e,a,s,r){e=null;for(var c=a,d=!1;c!==null;){if(!d){if((c.flags&524288)!==0)d=!0;else if((c.flags&262144)!==0)break}if(c.tag===10){var g=c.alternate;if(g===null)throw Error(o(387));if(g=g.memoizedProps,g!==null){var j=c.type;$a(c.pendingProps.value,g.value)||(e!==null?e.push(j):e=[j])}}else if(c===ke.current){if(g=c.alternate,g===null)throw Error(o(387));g.memoizedState.memoizedState!==c.memoizedState.memoizedState&&(e!==null?e.push(zr):e=[zr])}c=c.return}e!==null&&rc(a,e,s,r),a.flags|=262144}function hl(e){for(e=e.firstContext;e!==null;){if(!$a(e.context._currentValue,e.memoizedValue))return!0;e=e.next}return!1}function Os(e){Us=e,Un=null,e=e.dependencies,e!==null&&(e.firstContext=null)}function Aa(e){return jf(Us,e)}function ml(e,a){return Us===null&&Os(e),jf(e,a)}function jf(e,a){var s=a._currentValue;if(a={context:a,memoizedValue:s,next:null},Un===null){if(e===null)throw Error(o(308));Un=a,e.dependencies={lanes:0,firstContext:a},e.flags|=524288}else Un=Un.next=a;return s}var g0=typeof AbortController<"u"?AbortController:function(){var e=[],a=this.signal={aborted:!1,addEventListener:function(s,r){e.push(r)}};this.abort=function(){a.aborted=!0,e.forEach(function(s){return s()})}},x0=n.unstable_scheduleCallback,v0=n.unstable_NormalPriority,la={$$typeof:me,Consumer:null,Provider:null,_currentValue:null,_currentValue2:null,_threadCount:0};function lc(){return{controller:new g0,data:new Map,refCount:0}}function tr(e){e.refCount--,e.refCount===0&&x0(v0,function(){e.controller.abort()})}var ar=null,oc=0,ci=0,di=null;function y0(e,a){if(ar===null){var s=ar=[];oc=0,ci=dd(),di={status:"pending",value:void 0,then:function(r){s.push(r)}}}return oc++,a.then(Nf,Nf),a}function Nf(){if(--oc===0&&ar!==null){di!==null&&(di.status="fulfilled");var e=ar;ar=null,ci=0,di=null;for(var a=0;a<e.length;a++)(0,e[a])()}}function b0(e,a){var s=[],r={status:"pending",value:null,reason:null,then:function(c){s.push(c)}};return e.then(function(){r.status="fulfilled",r.value=a;for(var c=0;c<s.length;c++)(0,s[c])(a)},function(c){for(r.status="rejected",r.reason=c,c=0;c<s.length;c++)(0,s[c])(void 0)}),r}var wf=L.S;L.S=function(e,a){typeof a=="object"&&a!==null&&typeof a.then=="function"&&y0(e,a),wf!==null&&wf(e,a)};var Ls=F(null);function cc(){var e=Ls.current;return e!==null?e:Ht.pooledCache}function pl(e,a){a===null?ce(Ls,Ls.current):ce(Ls,a.pool)}function _f(){var e=cc();return e===null?null:{parent:la._currentValue,pool:e}}var nr=Error(o(460)),Sf=Error(o(474)),gl=Error(o(542)),dc={then:function(){}};function Tf(e){return e=e.status,e==="fulfilled"||e==="rejected"}function xl(){}function Cf(e,a,s){switch(s=e[s],s===void 0?e.push(a):s!==a&&(a.then(xl,xl),a=s),a.status){case"fulfilled":return a.value;case"rejected":throw e=a.reason,zf(e),e;default:if(typeof a.status=="string")a.then(xl,xl);else{if(e=Ht,e!==null&&100<e.shellSuspendCounter)throw Error(o(482));e=a,e.status="pending",e.then(function(r){if(a.status==="pending"){var c=a;c.status="fulfilled",c.value=r}},function(r){if(a.status==="pending"){var c=a;c.status="rejected",c.reason=r}})}switch(a.status){case"fulfilled":return a.value;case"rejected":throw e=a.reason,zf(e),e}throw sr=a,nr}}var sr=null;function Af(){if(sr===null)throw Error(o(459));var e=sr;return sr=null,e}function zf(e){if(e===nr||e===gl)throw Error(o(483))}var ns=!1;function uc(e){e.updateQueue={baseState:e.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,lanes:0,hiddenCallbacks:null},callbacks:null}}function fc(e,a){e=e.updateQueue,a.updateQueue===e&&(a.updateQueue={baseState:e.baseState,firstBaseUpdate:e.firstBaseUpdate,lastBaseUpdate:e.lastBaseUpdate,shared:e.shared,callbacks:null})}function ss(e){return{lane:e,tag:0,payload:null,callback:null,next:null}}function is(e,a,s){var r=e.updateQueue;if(r===null)return null;if(r=r.shared,(Ct&2)!==0){var c=r.pending;return c===null?a.next=a:(a.next=c.next,c.next=a),r.pending=a,a=cl(e),pf(e,null,s),a}return ol(e,r,a,s),cl(e)}function ir(e,a,s){if(a=a.updateQueue,a!==null&&(a=a.shared,(s&4194048)!==0)){var r=a.lanes;r&=e.pendingLanes,s|=r,a.lanes=s,at(e,s)}}function hc(e,a){var s=e.updateQueue,r=e.alternate;if(r!==null&&(r=r.updateQueue,s===r)){var c=null,d=null;if(s=s.firstBaseUpdate,s!==null){do{var g={lane:s.lane,tag:s.tag,payload:s.payload,callback:null,next:null};d===null?c=d=g:d=d.next=g,s=s.next}while(s!==null);d===null?c=d=a:d=d.next=a}else c=d=a;s={baseState:r.baseState,firstBaseUpdate:c,lastBaseUpdate:d,shared:r.shared,callbacks:r.callbacks},e.updateQueue=s;return}e=s.lastBaseUpdate,e===null?s.firstBaseUpdate=a:e.next=a,s.lastBaseUpdate=a}var mc=!1;function rr(){if(mc){var e=di;if(e!==null)throw e}}function lr(e,a,s,r){mc=!1;var c=e.updateQueue;ns=!1;var d=c.firstBaseUpdate,g=c.lastBaseUpdate,j=c.shared.pending;if(j!==null){c.shared.pending=null;var C=j,q=C.next;C.next=null,g===null?d=q:g.next=q,g=C;var X=e.alternate;X!==null&&(X=X.updateQueue,j=X.lastBaseUpdate,j!==g&&(j===null?X.firstBaseUpdate=q:j.next=q,X.lastBaseUpdate=C))}if(d!==null){var te=c.baseState;g=0,X=q=C=null,j=d;do{var H=j.lane&-536870913,I=H!==j.lane;if(I?(mt&H)===H:(r&H)===H){H!==0&&H===ci&&(mc=!0),X!==null&&(X=X.next={lane:0,tag:j.tag,payload:j.payload,callback:null,next:null});e:{var Je=e,Ye=j;H=a;var Rt=s;switch(Ye.tag){case 1:if(Je=Ye.payload,typeof Je=="function"){te=Je.call(Rt,te,H);break e}te=Je;break e;case 3:Je.flags=Je.flags&-65537|128;case 0:if(Je=Ye.payload,H=typeof Je=="function"?Je.call(Rt,te,H):Je,H==null)break e;te=v({},te,H);break e;case 2:ns=!0}}H=j.callback,H!==null&&(e.flags|=64,I&&(e.flags|=8192),I=c.callbacks,I===null?c.callbacks=[H]:I.push(H))}else I={lane:H,tag:j.tag,payload:j.payload,callback:j.callback,next:null},X===null?(q=X=I,C=te):X=X.next=I,g|=H;if(j=j.next,j===null){if(j=c.shared.pending,j===null)break;I=j,j=I.next,I.next=null,c.lastBaseUpdate=I,c.shared.pending=null}}while(!0);X===null&&(C=te),c.baseState=C,c.firstBaseUpdate=q,c.lastBaseUpdate=X,d===null&&(c.shared.lanes=0),hs|=g,e.lanes=g,e.memoizedState=te}}function kf(e,a){if(typeof e!="function")throw Error(o(191,e));e.call(a)}function Ef(e,a){var s=e.callbacks;if(s!==null)for(e.callbacks=null,e=0;e<s.length;e++)kf(s[e],a)}var ui=F(null),vl=F(0);function Mf(e,a){e=Fn,ce(vl,e),ce(ui,a),Fn=e|a.baseLanes}function pc(){ce(vl,Fn),ce(ui,ui.current)}function gc(){Fn=vl.current,le(ui),le(vl)}var rs=0,rt=null,Mt=null,aa=null,yl=!1,fi=!1,qs=!1,bl=0,or=0,hi=null,j0=0;function ea(){throw Error(o(321))}function xc(e,a){if(a===null)return!1;for(var s=0;s<a.length&&s<e.length;s++)if(!$a(e[s],a[s]))return!1;return!0}function vc(e,a,s,r,c,d){return rs=d,rt=a,a.memoizedState=null,a.updateQueue=null,a.lanes=0,L.H=e===null||e.memoizedState===null?ph:gh,qs=!1,d=s(r,c),qs=!1,fi&&(d=Rf(a,s,r,c)),Df(e),d}function Df(e){L.H=Tl;var a=Mt!==null&&Mt.next!==null;if(rs=0,aa=Mt=rt=null,yl=!1,or=0,hi=null,a)throw Error(o(300));e===null||fa||(e=e.dependencies,e!==null&&hl(e)&&(fa=!0))}function Rf(e,a,s,r){rt=e;var c=0;do{if(fi&&(hi=null),or=0,fi=!1,25<=c)throw Error(o(301));if(c+=1,aa=Mt=null,e.updateQueue!=null){var d=e.updateQueue;d.lastEffect=null,d.events=null,d.stores=null,d.memoCache!=null&&(d.memoCache.index=0)}L.H=A0,d=a(s,r)}while(fi);return d}function N0(){var e=L.H,a=e.useState()[0];return a=typeof a.then=="function"?cr(a):a,e=e.useState()[0],(Mt!==null?Mt.memoizedState:null)!==e&&(rt.flags|=1024),a}function yc(){var e=bl!==0;return bl=0,e}function bc(e,a,s){a.updateQueue=e.updateQueue,a.flags&=-2053,e.lanes&=~s}function jc(e){if(yl){for(e=e.memoizedState;e!==null;){var a=e.queue;a!==null&&(a.pending=null),e=e.next}yl=!1}rs=0,aa=Mt=rt=null,fi=!1,or=bl=0,hi=null}function Oa(){var e={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};return aa===null?rt.memoizedState=aa=e:aa=aa.next=e,aa}function na(){if(Mt===null){var e=rt.alternate;e=e!==null?e.memoizedState:null}else e=Mt.next;var a=aa===null?rt.memoizedState:aa.next;if(a!==null)aa=a,Mt=e;else{if(e===null)throw rt.alternate===null?Error(o(467)):Error(o(310));Mt=e,e={memoizedState:Mt.memoizedState,baseState:Mt.baseState,baseQueue:Mt.baseQueue,queue:Mt.queue,next:null},aa===null?rt.memoizedState=aa=e:aa=aa.next=e}return aa}function Nc(){return{lastEffect:null,events:null,stores:null,memoCache:null}}function cr(e){var a=or;return or+=1,hi===null&&(hi=[]),e=Cf(hi,e,a),a=rt,(aa===null?a.memoizedState:aa.next)===null&&(a=a.alternate,L.H=a===null||a.memoizedState===null?ph:gh),e}function jl(e){if(e!==null&&typeof e=="object"){if(typeof e.then=="function")return cr(e);if(e.$$typeof===me)return Aa(e)}throw Error(o(438,String(e)))}function wc(e){var a=null,s=rt.updateQueue;if(s!==null&&(a=s.memoCache),a==null){var r=rt.alternate;r!==null&&(r=r.updateQueue,r!==null&&(r=r.memoCache,r!=null&&(a={data:r.data.map(function(c){return c.slice()}),index:0})))}if(a==null&&(a={data:[],index:0}),s===null&&(s=Nc(),rt.updateQueue=s),s.memoCache=a,s=a.data[a.index],s===void 0)for(s=a.data[a.index]=Array(e),r=0;r<e;r++)s[r]=De;return a.index++,s}function Ln(e,a){return typeof a=="function"?a(e):a}function Nl(e){var a=na();return _c(a,Mt,e)}function _c(e,a,s){var r=e.queue;if(r===null)throw Error(o(311));r.lastRenderedReducer=s;var c=e.baseQueue,d=r.pending;if(d!==null){if(c!==null){var g=c.next;c.next=d.next,d.next=g}a.baseQueue=c=d,r.pending=null}if(d=e.baseState,c===null)e.memoizedState=d;else{a=c.next;var j=g=null,C=null,q=a,X=!1;do{var te=q.lane&-536870913;if(te!==q.lane?(mt&te)===te:(rs&te)===te){var H=q.revertLane;if(H===0)C!==null&&(C=C.next={lane:0,revertLane:0,action:q.action,hasEagerState:q.hasEagerState,eagerState:q.eagerState,next:null}),te===ci&&(X=!0);else if((rs&H)===H){q=q.next,H===ci&&(X=!0);continue}else te={lane:0,revertLane:q.revertLane,action:q.action,hasEagerState:q.hasEagerState,eagerState:q.eagerState,next:null},C===null?(j=C=te,g=d):C=C.next=te,rt.lanes|=H,hs|=H;te=q.action,qs&&s(d,te),d=q.hasEagerState?q.eagerState:s(d,te)}else H={lane:te,revertLane:q.revertLane,action:q.action,hasEagerState:q.hasEagerState,eagerState:q.eagerState,next:null},C===null?(j=C=H,g=d):C=C.next=H,rt.lanes|=te,hs|=te;q=q.next}while(q!==null&&q!==a);if(C===null?g=d:C.next=j,!$a(d,e.memoizedState)&&(fa=!0,X&&(s=di,s!==null)))throw s;e.memoizedState=d,e.baseState=g,e.baseQueue=C,r.lastRenderedState=d}return c===null&&(r.lanes=0),[e.memoizedState,r.dispatch]}function Sc(e){var a=na(),s=a.queue;if(s===null)throw Error(o(311));s.lastRenderedReducer=e;var r=s.dispatch,c=s.pending,d=a.memoizedState;if(c!==null){s.pending=null;var g=c=c.next;do d=e(d,g.action),g=g.next;while(g!==c);$a(d,a.memoizedState)||(fa=!0),a.memoizedState=d,a.baseQueue===null&&(a.baseState=d),s.lastRenderedState=d}return[d,r]}function Uf(e,a,s){var r=rt,c=na(),d=Nt;if(d){if(s===void 0)throw Error(o(407));s=s()}else s=a();var g=!$a((Mt||c).memoizedState,s);g&&(c.memoizedState=s,fa=!0),c=c.queue;var j=qf.bind(null,r,c,e);if(dr(2048,8,j,[e]),c.getSnapshot!==a||g||aa!==null&&aa.memoizedState.tag&1){if(r.flags|=2048,mi(9,wl(),Lf.bind(null,r,c,s,a),null),Ht===null)throw Error(o(349));d||(rs&124)!==0||Of(r,a,s)}return s}function Of(e,a,s){e.flags|=16384,e={getSnapshot:a,value:s},a=rt.updateQueue,a===null?(a=Nc(),rt.updateQueue=a,a.stores=[e]):(s=a.stores,s===null?a.stores=[e]:s.push(e))}function Lf(e,a,s,r){a.value=s,a.getSnapshot=r,Bf(a)&&Hf(e)}function qf(e,a,s){return s(function(){Bf(a)&&Hf(e)})}function Bf(e){var a=e.getSnapshot;e=e.value;try{var s=a();return!$a(e,s)}catch{return!0}}function Hf(e){var a=ii(e,2);a!==null&&Xa(a,e,2)}function Tc(e){var a=Oa();if(typeof e=="function"){var s=e;if(e=s(),qs){xt(!0);try{s()}finally{xt(!1)}}}return a.memoizedState=a.baseState=e,a.queue={pending:null,lanes:0,dispatch:null,lastRenderedReducer:Ln,lastRenderedState:e},a}function If(e,a,s,r){return e.baseState=s,_c(e,Mt,typeof r=="function"?r:Ln)}function w0(e,a,s,r,c){if(Sl(e))throw Error(o(485));if(e=a.action,e!==null){var d={payload:c,action:e,next:null,isTransition:!0,status:"pending",value:null,reason:null,listeners:[],then:function(g){d.listeners.push(g)}};L.T!==null?s(!0):d.isTransition=!1,r(d),s=a.pending,s===null?(d.next=a.pending=d,$f(a,d)):(d.next=s.next,a.pending=s.next=d)}}function $f(e,a){var s=a.action,r=a.payload,c=e.state;if(a.isTransition){var d=L.T,g={};L.T=g;try{var j=s(c,r),C=L.S;C!==null&&C(g,j),Ff(e,a,j)}catch(q){Cc(e,a,q)}finally{L.T=d}}else try{d=s(c,r),Ff(e,a,d)}catch(q){Cc(e,a,q)}}function Ff(e,a,s){s!==null&&typeof s=="object"&&typeof s.then=="function"?s.then(function(r){Yf(e,a,r)},function(r){return Cc(e,a,r)}):Yf(e,a,s)}function Yf(e,a,s){a.status="fulfilled",a.value=s,Gf(a),e.state=s,a=e.pending,a!==null&&(s=a.next,s===a?e.pending=null:(s=s.next,a.next=s,$f(e,s)))}function Cc(e,a,s){var r=e.pending;if(e.pending=null,r!==null){r=r.next;do a.status="rejected",a.reason=s,Gf(a),a=a.next;while(a!==r)}e.action=null}function Gf(e){e=e.listeners;for(var a=0;a<e.length;a++)(0,e[a])()}function Pf(e,a){return a}function Vf(e,a){if(Nt){var s=Ht.formState;if(s!==null){e:{var r=rt;if(Nt){if(Qt){t:{for(var c=Qt,d=xn;c.nodeType!==8;){if(!d){c=null;break t}if(c=un(c.nextSibling),c===null){c=null;break t}}d=c.data,c=d==="F!"||d==="F"?c:null}if(c){Qt=un(c.nextSibling),r=c.data==="F!";break e}}Rs(r)}r=!1}r&&(a=s[0])}}return s=Oa(),s.memoizedState=s.baseState=a,r={pending:null,lanes:0,dispatch:null,lastRenderedReducer:Pf,lastRenderedState:a},s.queue=r,s=fh.bind(null,rt,r),r.dispatch=s,r=Tc(!1),d=Mc.bind(null,rt,!1,r.queue),r=Oa(),c={state:a,dispatch:null,action:e,pending:null},r.queue=c,s=w0.bind(null,rt,c,d,s),c.dispatch=s,r.memoizedState=e,[a,s,!1]}function Xf(e){var a=na();return Zf(a,Mt,e)}function Zf(e,a,s){if(a=_c(e,a,Pf)[0],e=Nl(Ln)[0],typeof a=="object"&&a!==null&&typeof a.then=="function")try{var r=cr(a)}catch(g){throw g===nr?gl:g}else r=a;a=na();var c=a.queue,d=c.dispatch;return s!==a.memoizedState&&(rt.flags|=2048,mi(9,wl(),_0.bind(null,c,s),null)),[r,d,e]}function _0(e,a){e.action=a}function Qf(e){var a=na(),s=Mt;if(s!==null)return Zf(a,s,e);na(),a=a.memoizedState,s=na();var r=s.queue.dispatch;return s.memoizedState=e,[a,r,!1]}function mi(e,a,s,r){return e={tag:e,create:s,deps:r,inst:a,next:null},a=rt.updateQueue,a===null&&(a=Nc(),rt.updateQueue=a),s=a.lastEffect,s===null?a.lastEffect=e.next=e:(r=s.next,s.next=e,e.next=r,a.lastEffect=e),e}function wl(){return{destroy:void 0,resource:void 0}}function Jf(){return na().memoizedState}function _l(e,a,s,r){var c=Oa();r=r===void 0?null:r,rt.flags|=e,c.memoizedState=mi(1|a,wl(),s,r)}function dr(e,a,s,r){var c=na();r=r===void 0?null:r;var d=c.memoizedState.inst;Mt!==null&&r!==null&&xc(r,Mt.memoizedState.deps)?c.memoizedState=mi(a,d,s,r):(rt.flags|=e,c.memoizedState=mi(1|a,d,s,r))}function Kf(e,a){_l(8390656,8,e,a)}function Wf(e,a){dr(2048,8,e,a)}function eh(e,a){return dr(4,2,e,a)}function th(e,a){return dr(4,4,e,a)}function ah(e,a){if(typeof a=="function"){e=e();var s=a(e);return function(){typeof s=="function"?s():a(null)}}if(a!=null)return e=e(),a.current=e,function(){a.current=null}}function nh(e,a,s){s=s!=null?s.concat([e]):null,dr(4,4,ah.bind(null,a,e),s)}function Ac(){}function sh(e,a){var s=na();a=a===void 0?null:a;var r=s.memoizedState;return a!==null&&xc(a,r[1])?r[0]:(s.memoizedState=[e,a],e)}function ih(e,a){var s=na();a=a===void 0?null:a;var r=s.memoizedState;if(a!==null&&xc(a,r[1]))return r[0];if(r=e(),qs){xt(!0);try{e()}finally{xt(!1)}}return s.memoizedState=[r,a],r}function zc(e,a,s){return s===void 0||(rs&1073741824)!==0?e.memoizedState=a:(e.memoizedState=s,e=om(),rt.lanes|=e,hs|=e,s)}function rh(e,a,s,r){return $a(s,a)?s:ui.current!==null?(e=zc(e,s,r),$a(e,a)||(fa=!0),e):(rs&42)===0?(fa=!0,e.memoizedState=s):(e=om(),rt.lanes|=e,hs|=e,a)}function lh(e,a,s,r,c){var d=ne.p;ne.p=d!==0&&8>d?d:8;var g=L.T,j={};L.T=j,Mc(e,!1,a,s);try{var C=c(),q=L.S;if(q!==null&&q(j,C),C!==null&&typeof C=="object"&&typeof C.then=="function"){var X=b0(C,r);ur(e,a,X,Va(e))}else ur(e,a,r,Va(e))}catch(te){ur(e,a,{then:function(){},status:"rejected",reason:te},Va())}finally{ne.p=d,L.T=g}}function S0(){}function kc(e,a,s,r){if(e.tag!==5)throw Error(o(476));var c=oh(e).queue;lh(e,c,a,P,s===null?S0:function(){return ch(e),s(r)})}function oh(e){var a=e.memoizedState;if(a!==null)return a;a={memoizedState:P,baseState:P,baseQueue:null,queue:{pending:null,lanes:0,dispatch:null,lastRenderedReducer:Ln,lastRenderedState:P},next:null};var s={};return a.next={memoizedState:s,baseState:s,baseQueue:null,queue:{pending:null,lanes:0,dispatch:null,lastRenderedReducer:Ln,lastRenderedState:s},next:null},e.memoizedState=a,e=e.alternate,e!==null&&(e.memoizedState=a),a}function ch(e){var a=oh(e).next.queue;ur(e,a,{},Va())}function Ec(){return Aa(zr)}function dh(){return na().memoizedState}function uh(){return na().memoizedState}function T0(e){for(var a=e.return;a!==null;){switch(a.tag){case 24:case 3:var s=Va();e=ss(s);var r=is(a,e,s);r!==null&&(Xa(r,a,s),ir(r,a,s)),a={cache:lc()},e.payload=a;return}a=a.return}}function C0(e,a,s){var r=Va();s={lane:r,revertLane:0,action:s,hasEagerState:!1,eagerState:null,next:null},Sl(e)?hh(a,s):(s=Jo(e,a,s,r),s!==null&&(Xa(s,e,r),mh(s,a,r)))}function fh(e,a,s){var r=Va();ur(e,a,s,r)}function ur(e,a,s,r){var c={lane:r,revertLane:0,action:s,hasEagerState:!1,eagerState:null,next:null};if(Sl(e))hh(a,c);else{var d=e.alternate;if(e.lanes===0&&(d===null||d.lanes===0)&&(d=a.lastRenderedReducer,d!==null))try{var g=a.lastRenderedState,j=d(g,s);if(c.hasEagerState=!0,c.eagerState=j,$a(j,g))return ol(e,a,c,0),Ht===null&&ll(),!1}catch{}finally{}if(s=Jo(e,a,c,r),s!==null)return Xa(s,e,r),mh(s,a,r),!0}return!1}function Mc(e,a,s,r){if(r={lane:2,revertLane:dd(),action:r,hasEagerState:!1,eagerState:null,next:null},Sl(e)){if(a)throw Error(o(479))}else a=Jo(e,s,r,2),a!==null&&Xa(a,e,2)}function Sl(e){var a=e.alternate;return e===rt||a!==null&&a===rt}function hh(e,a){fi=yl=!0;var s=e.pending;s===null?a.next=a:(a.next=s.next,s.next=a),e.pending=a}function mh(e,a,s){if((s&4194048)!==0){var r=a.lanes;r&=e.pendingLanes,s|=r,a.lanes=s,at(e,s)}}var Tl={readContext:Aa,use:jl,useCallback:ea,useContext:ea,useEffect:ea,useImperativeHandle:ea,useLayoutEffect:ea,useInsertionEffect:ea,useMemo:ea,useReducer:ea,useRef:ea,useState:ea,useDebugValue:ea,useDeferredValue:ea,useTransition:ea,useSyncExternalStore:ea,useId:ea,useHostTransitionStatus:ea,useFormState:ea,useActionState:ea,useOptimistic:ea,useMemoCache:ea,useCacheRefresh:ea},ph={readContext:Aa,use:jl,useCallback:function(e,a){return Oa().memoizedState=[e,a===void 0?null:a],e},useContext:Aa,useEffect:Kf,useImperativeHandle:function(e,a,s){s=s!=null?s.concat([e]):null,_l(4194308,4,ah.bind(null,a,e),s)},useLayoutEffect:function(e,a){return _l(4194308,4,e,a)},useInsertionEffect:function(e,a){_l(4,2,e,a)},useMemo:function(e,a){var s=Oa();a=a===void 0?null:a;var r=e();if(qs){xt(!0);try{e()}finally{xt(!1)}}return s.memoizedState=[r,a],r},useReducer:function(e,a,s){var r=Oa();if(s!==void 0){var c=s(a);if(qs){xt(!0);try{s(a)}finally{xt(!1)}}}else c=a;return r.memoizedState=r.baseState=c,e={pending:null,lanes:0,dispatch:null,lastRenderedReducer:e,lastRenderedState:c},r.queue=e,e=e.dispatch=C0.bind(null,rt,e),[r.memoizedState,e]},useRef:function(e){var a=Oa();return e={current:e},a.memoizedState=e},useState:function(e){e=Tc(e);var a=e.queue,s=fh.bind(null,rt,a);return a.dispatch=s,[e.memoizedState,s]},useDebugValue:Ac,useDeferredValue:function(e,a){var s=Oa();return zc(s,e,a)},useTransition:function(){var e=Tc(!1);return e=lh.bind(null,rt,e.queue,!0,!1),Oa().memoizedState=e,[!1,e]},useSyncExternalStore:function(e,a,s){var r=rt,c=Oa();if(Nt){if(s===void 0)throw Error(o(407));s=s()}else{if(s=a(),Ht===null)throw Error(o(349));(mt&124)!==0||Of(r,a,s)}c.memoizedState=s;var d={value:s,getSnapshot:a};return c.queue=d,Kf(qf.bind(null,r,d,e),[e]),r.flags|=2048,mi(9,wl(),Lf.bind(null,r,d,s,a),null),s},useId:function(){var e=Oa(),a=Ht.identifierPrefix;if(Nt){var s=Rn,r=Dn;s=(r&~(1<<32-ft(r)-1)).toString(32)+s,a="«"+a+"R"+s,s=bl++,0<s&&(a+="H"+s.toString(32)),a+="»"}else s=j0++,a="«"+a+"r"+s.toString(32)+"»";return e.memoizedState=a},useHostTransitionStatus:Ec,useFormState:Vf,useActionState:Vf,useOptimistic:function(e){var a=Oa();a.memoizedState=a.baseState=e;var s={pending:null,lanes:0,dispatch:null,lastRenderedReducer:null,lastRenderedState:null};return a.queue=s,a=Mc.bind(null,rt,!0,s),s.dispatch=a,[e,a]},useMemoCache:wc,useCacheRefresh:function(){return Oa().memoizedState=T0.bind(null,rt)}},gh={readContext:Aa,use:jl,useCallback:sh,useContext:Aa,useEffect:Wf,useImperativeHandle:nh,useInsertionEffect:eh,useLayoutEffect:th,useMemo:ih,useReducer:Nl,useRef:Jf,useState:function(){return Nl(Ln)},useDebugValue:Ac,useDeferredValue:function(e,a){var s=na();return rh(s,Mt.memoizedState,e,a)},useTransition:function(){var e=Nl(Ln)[0],a=na().memoizedState;return[typeof e=="boolean"?e:cr(e),a]},useSyncExternalStore:Uf,useId:dh,useHostTransitionStatus:Ec,useFormState:Xf,useActionState:Xf,useOptimistic:function(e,a){var s=na();return If(s,Mt,e,a)},useMemoCache:wc,useCacheRefresh:uh},A0={readContext:Aa,use:jl,useCallback:sh,useContext:Aa,useEffect:Wf,useImperativeHandle:nh,useInsertionEffect:eh,useLayoutEffect:th,useMemo:ih,useReducer:Sc,useRef:Jf,useState:function(){return Sc(Ln)},useDebugValue:Ac,useDeferredValue:function(e,a){var s=na();return Mt===null?zc(s,e,a):rh(s,Mt.memoizedState,e,a)},useTransition:function(){var e=Sc(Ln)[0],a=na().memoizedState;return[typeof e=="boolean"?e:cr(e),a]},useSyncExternalStore:Uf,useId:dh,useHostTransitionStatus:Ec,useFormState:Qf,useActionState:Qf,useOptimistic:function(e,a){var s=na();return Mt!==null?If(s,Mt,e,a):(s.baseState=e,[e,s.queue.dispatch])},useMemoCache:wc,useCacheRefresh:uh},pi=null,fr=0;function Cl(e){var a=fr;return fr+=1,pi===null&&(pi=[]),Cf(pi,e,a)}function hr(e,a){a=a.props.ref,e.ref=a!==void 0?a:null}function Al(e,a){throw a.$$typeof===y?Error(o(525)):(e=Object.prototype.toString.call(a),Error(o(31,e==="[object Object]"?"object with keys {"+Object.keys(a).join(", ")+"}":e)))}function xh(e){var a=e._init;return a(e._payload)}function vh(e){function a(R,E){if(e){var O=R.deletions;O===null?(R.deletions=[E],R.flags|=16):O.push(E)}}function s(R,E){if(!e)return null;for(;E!==null;)a(R,E),E=E.sibling;return null}function r(R){for(var E=new Map;R!==null;)R.key!==null?E.set(R.key,R):E.set(R.index,R),R=R.sibling;return E}function c(R,E){return R=Mn(R,E),R.index=0,R.sibling=null,R}function d(R,E,O){return R.index=O,e?(O=R.alternate,O!==null?(O=O.index,O<E?(R.flags|=67108866,E):O):(R.flags|=67108866,E)):(R.flags|=1048576,E)}function g(R){return e&&R.alternate===null&&(R.flags|=67108866),R}function j(R,E,O,J){return E===null||E.tag!==6?(E=Wo(O,R.mode,J),E.return=R,E):(E=c(E,O),E.return=R,E)}function C(R,E,O,J){var Le=O.type;return Le===A?X(R,E,O.props.children,J,O.key):E!==null&&(E.elementType===Le||typeof Le=="object"&&Le!==null&&Le.$$typeof===Ke&&xh(Le)===E.type)?(E=c(E,O.props),hr(E,O),E.return=R,E):(E=dl(O.type,O.key,O.props,null,R.mode,J),hr(E,O),E.return=R,E)}function q(R,E,O,J){return E===null||E.tag!==4||E.stateNode.containerInfo!==O.containerInfo||E.stateNode.implementation!==O.implementation?(E=ec(O,R.mode,J),E.return=R,E):(E=c(E,O.children||[]),E.return=R,E)}function X(R,E,O,J,Le){return E===null||E.tag!==7?(E=ks(O,R.mode,J,Le),E.return=R,E):(E=c(E,O),E.return=R,E)}function te(R,E,O){if(typeof E=="string"&&E!==""||typeof E=="number"||typeof E=="bigint")return E=Wo(""+E,R.mode,O),E.return=R,E;if(typeof E=="object"&&E!==null){switch(E.$$typeof){case N:return O=dl(E.type,E.key,E.props,null,R.mode,O),hr(O,E),O.return=R,O;case S:return E=ec(E,R.mode,O),E.return=R,E;case Ke:var J=E._init;return E=J(E._payload),te(R,E,O)}if(Ze(E)||je(E))return E=ks(E,R.mode,O,null),E.return=R,E;if(typeof E.then=="function")return te(R,Cl(E),O);if(E.$$typeof===me)return te(R,ml(R,E),O);Al(R,E)}return null}function H(R,E,O,J){var Le=E!==null?E.key:null;if(typeof O=="string"&&O!==""||typeof O=="number"||typeof O=="bigint")return Le!==null?null:j(R,E,""+O,J);if(typeof O=="object"&&O!==null){switch(O.$$typeof){case N:return O.key===Le?C(R,E,O,J):null;case S:return O.key===Le?q(R,E,O,J):null;case Ke:return Le=O._init,O=Le(O._payload),H(R,E,O,J)}if(Ze(O)||je(O))return Le!==null?null:X(R,E,O,J,null);if(typeof O.then=="function")return H(R,E,Cl(O),J);if(O.$$typeof===me)return H(R,E,ml(R,O),J);Al(R,O)}return null}function I(R,E,O,J,Le){if(typeof J=="string"&&J!==""||typeof J=="number"||typeof J=="bigint")return R=R.get(O)||null,j(E,R,""+J,Le);if(typeof J=="object"&&J!==null){switch(J.$$typeof){case N:return R=R.get(J.key===null?O:J.key)||null,C(E,R,J,Le);case S:return R=R.get(J.key===null?O:J.key)||null,q(E,R,J,Le);case Ke:var lt=J._init;return J=lt(J._payload),I(R,E,O,J,Le)}if(Ze(J)||je(J))return R=R.get(O)||null,X(E,R,J,Le,null);if(typeof J.then=="function")return I(R,E,O,Cl(J),Le);if(J.$$typeof===me)return I(R,E,O,ml(E,J),Le);Al(E,J)}return null}function Je(R,E,O,J){for(var Le=null,lt=null,He=E,Xe=E=0,ma=null;He!==null&&Xe<O.length;Xe++){He.index>Xe?(ma=He,He=null):ma=He.sibling;var yt=H(R,He,O[Xe],J);if(yt===null){He===null&&(He=ma);break}e&&He&&yt.alternate===null&&a(R,He),E=d(yt,E,Xe),lt===null?Le=yt:lt.sibling=yt,lt=yt,He=ma}if(Xe===O.length)return s(R,He),Nt&&Ms(R,Xe),Le;if(He===null){for(;Xe<O.length;Xe++)He=te(R,O[Xe],J),He!==null&&(E=d(He,E,Xe),lt===null?Le=He:lt.sibling=He,lt=He);return Nt&&Ms(R,Xe),Le}for(He=r(He);Xe<O.length;Xe++)ma=I(He,R,Xe,O[Xe],J),ma!==null&&(e&&ma.alternate!==null&&He.delete(ma.key===null?Xe:ma.key),E=d(ma,E,Xe),lt===null?Le=ma:lt.sibling=ma,lt=ma);return e&&He.forEach(function(Ns){return a(R,Ns)}),Nt&&Ms(R,Xe),Le}function Ye(R,E,O,J){if(O==null)throw Error(o(151));for(var Le=null,lt=null,He=E,Xe=E=0,ma=null,yt=O.next();He!==null&&!yt.done;Xe++,yt=O.next()){He.index>Xe?(ma=He,He=null):ma=He.sibling;var Ns=H(R,He,yt.value,J);if(Ns===null){He===null&&(He=ma);break}e&&He&&Ns.alternate===null&&a(R,He),E=d(Ns,E,Xe),lt===null?Le=Ns:lt.sibling=Ns,lt=Ns,He=ma}if(yt.done)return s(R,He),Nt&&Ms(R,Xe),Le;if(He===null){for(;!yt.done;Xe++,yt=O.next())yt=te(R,yt.value,J),yt!==null&&(E=d(yt,E,Xe),lt===null?Le=yt:lt.sibling=yt,lt=yt);return Nt&&Ms(R,Xe),Le}for(He=r(He);!yt.done;Xe++,yt=O.next())yt=I(He,R,Xe,yt.value,J),yt!==null&&(e&&yt.alternate!==null&&He.delete(yt.key===null?Xe:yt.key),E=d(yt,E,Xe),lt===null?Le=yt:lt.sibling=yt,lt=yt);return e&&He.forEach(function(zv){return a(R,zv)}),Nt&&Ms(R,Xe),Le}function Rt(R,E,O,J){if(typeof O=="object"&&O!==null&&O.type===A&&O.key===null&&(O=O.props.children),typeof O=="object"&&O!==null){switch(O.$$typeof){case N:e:{for(var Le=O.key;E!==null;){if(E.key===Le){if(Le=O.type,Le===A){if(E.tag===7){s(R,E.sibling),J=c(E,O.props.children),J.return=R,R=J;break e}}else if(E.elementType===Le||typeof Le=="object"&&Le!==null&&Le.$$typeof===Ke&&xh(Le)===E.type){s(R,E.sibling),J=c(E,O.props),hr(J,O),J.return=R,R=J;break e}s(R,E);break}else a(R,E);E=E.sibling}O.type===A?(J=ks(O.props.children,R.mode,J,O.key),J.return=R,R=J):(J=dl(O.type,O.key,O.props,null,R.mode,J),hr(J,O),J.return=R,R=J)}return g(R);case S:e:{for(Le=O.key;E!==null;){if(E.key===Le)if(E.tag===4&&E.stateNode.containerInfo===O.containerInfo&&E.stateNode.implementation===O.implementation){s(R,E.sibling),J=c(E,O.children||[]),J.return=R,R=J;break e}else{s(R,E);break}else a(R,E);E=E.sibling}J=ec(O,R.mode,J),J.return=R,R=J}return g(R);case Ke:return Le=O._init,O=Le(O._payload),Rt(R,E,O,J)}if(Ze(O))return Je(R,E,O,J);if(je(O)){if(Le=je(O),typeof Le!="function")throw Error(o(150));return O=Le.call(O),Ye(R,E,O,J)}if(typeof O.then=="function")return Rt(R,E,Cl(O),J);if(O.$$typeof===me)return Rt(R,E,ml(R,O),J);Al(R,O)}return typeof O=="string"&&O!==""||typeof O=="number"||typeof O=="bigint"?(O=""+O,E!==null&&E.tag===6?(s(R,E.sibling),J=c(E,O),J.return=R,R=J):(s(R,E),J=Wo(O,R.mode,J),J.return=R,R=J),g(R)):s(R,E)}return function(R,E,O,J){try{fr=0;var Le=Rt(R,E,O,J);return pi=null,Le}catch(He){if(He===nr||He===gl)throw He;var lt=Fa(29,He,null,R.mode);return lt.lanes=J,lt.return=R,lt}finally{}}}var gi=vh(!0),yh=vh(!1),an=F(null),vn=null;function ls(e){var a=e.alternate;ce(oa,oa.current&1),ce(an,e),vn===null&&(a===null||ui.current!==null||a.memoizedState!==null)&&(vn=e)}function bh(e){if(e.tag===22){if(ce(oa,oa.current),ce(an,e),vn===null){var a=e.alternate;a!==null&&a.memoizedState!==null&&(vn=e)}}else os()}function os(){ce(oa,oa.current),ce(an,an.current)}function qn(e){le(an),vn===e&&(vn=null),le(oa)}var oa=F(0);function zl(e){for(var a=e;a!==null;){if(a.tag===13){var s=a.memoizedState;if(s!==null&&(s=s.dehydrated,s===null||s.data==="$?"||Nd(s)))return a}else if(a.tag===19&&a.memoizedProps.revealOrder!==void 0){if((a.flags&128)!==0)return a}else if(a.child!==null){a.child.return=a,a=a.child;continue}if(a===e)break;for(;a.sibling===null;){if(a.return===null||a.return===e)return null;a=a.return}a.sibling.return=a.return,a=a.sibling}return null}function Dc(e,a,s,r){a=e.memoizedState,s=s(r,a),s=s==null?a:v({},a,s),e.memoizedState=s,e.lanes===0&&(e.updateQueue.baseState=s)}var Rc={enqueueSetState:function(e,a,s){e=e._reactInternals;var r=Va(),c=ss(r);c.payload=a,s!=null&&(c.callback=s),a=is(e,c,r),a!==null&&(Xa(a,e,r),ir(a,e,r))},enqueueReplaceState:function(e,a,s){e=e._reactInternals;var r=Va(),c=ss(r);c.tag=1,c.payload=a,s!=null&&(c.callback=s),a=is(e,c,r),a!==null&&(Xa(a,e,r),ir(a,e,r))},enqueueForceUpdate:function(e,a){e=e._reactInternals;var s=Va(),r=ss(s);r.tag=2,a!=null&&(r.callback=a),a=is(e,r,s),a!==null&&(Xa(a,e,s),ir(a,e,s))}};function jh(e,a,s,r,c,d,g){return e=e.stateNode,typeof e.shouldComponentUpdate=="function"?e.shouldComponentUpdate(r,d,g):a.prototype&&a.prototype.isPureReactComponent?!Zi(s,r)||!Zi(c,d):!0}function Nh(e,a,s,r){e=a.state,typeof a.componentWillReceiveProps=="function"&&a.componentWillReceiveProps(s,r),typeof a.UNSAFE_componentWillReceiveProps=="function"&&a.UNSAFE_componentWillReceiveProps(s,r),a.state!==e&&Rc.enqueueReplaceState(a,a.state,null)}function Bs(e,a){var s=a;if("ref"in a){s={};for(var r in a)r!=="ref"&&(s[r]=a[r])}if(e=e.defaultProps){s===a&&(s=v({},s));for(var c in e)s[c]===void 0&&(s[c]=e[c])}return s}var kl=typeof reportError=="function"?reportError:function(e){if(typeof window=="object"&&typeof window.ErrorEvent=="function"){var a=new window.ErrorEvent("error",{bubbles:!0,cancelable:!0,message:typeof e=="object"&&e!==null&&typeof e.message=="string"?String(e.message):String(e),error:e});if(!window.dispatchEvent(a))return}else if(typeof process=="object"&&typeof process.emit=="function"){process.emit("uncaughtException",e);return}console.error(e)};function wh(e){kl(e)}function _h(e){console.error(e)}function Sh(e){kl(e)}function El(e,a){try{var s=e.onUncaughtError;s(a.value,{componentStack:a.stack})}catch(r){setTimeout(function(){throw r})}}function Th(e,a,s){try{var r=e.onCaughtError;r(s.value,{componentStack:s.stack,errorBoundary:a.tag===1?a.stateNode:null})}catch(c){setTimeout(function(){throw c})}}function Uc(e,a,s){return s=ss(s),s.tag=3,s.payload={element:null},s.callback=function(){El(e,a)},s}function Ch(e){return e=ss(e),e.tag=3,e}function Ah(e,a,s,r){var c=s.type.getDerivedStateFromError;if(typeof c=="function"){var d=r.value;e.payload=function(){return c(d)},e.callback=function(){Th(a,s,r)}}var g=s.stateNode;g!==null&&typeof g.componentDidCatch=="function"&&(e.callback=function(){Th(a,s,r),typeof c!="function"&&(ms===null?ms=new Set([this]):ms.add(this));var j=r.stack;this.componentDidCatch(r.value,{componentStack:j!==null?j:""})})}function z0(e,a,s,r,c){if(s.flags|=32768,r!==null&&typeof r=="object"&&typeof r.then=="function"){if(a=s.alternate,a!==null&&er(a,s,c,!0),s=an.current,s!==null){switch(s.tag){case 13:return vn===null?id():s.alternate===null&&Jt===0&&(Jt=3),s.flags&=-257,s.flags|=65536,s.lanes=c,r===dc?s.flags|=16384:(a=s.updateQueue,a===null?s.updateQueue=new Set([r]):a.add(r),ld(e,r,c)),!1;case 22:return s.flags|=65536,r===dc?s.flags|=16384:(a=s.updateQueue,a===null?(a={transitions:null,markerInstances:null,retryQueue:new Set([r])},s.updateQueue=a):(s=a.retryQueue,s===null?a.retryQueue=new Set([r]):s.add(r)),ld(e,r,c)),!1}throw Error(o(435,s.tag))}return ld(e,r,c),id(),!1}if(Nt)return a=an.current,a!==null?((a.flags&65536)===0&&(a.flags|=256),a.flags|=65536,a.lanes=c,r!==nc&&(e=Error(o(422),{cause:r}),Wi(Ka(e,s)))):(r!==nc&&(a=Error(o(423),{cause:r}),Wi(Ka(a,s))),e=e.current.alternate,e.flags|=65536,c&=-c,e.lanes|=c,r=Ka(r,s),c=Uc(e.stateNode,r,c),hc(e,c),Jt!==4&&(Jt=2)),!1;var d=Error(o(520),{cause:r});if(d=Ka(d,s),br===null?br=[d]:br.push(d),Jt!==4&&(Jt=2),a===null)return!0;r=Ka(r,s),s=a;do{switch(s.tag){case 3:return s.flags|=65536,e=c&-c,s.lanes|=e,e=Uc(s.stateNode,r,e),hc(s,e),!1;case 1:if(a=s.type,d=s.stateNode,(s.flags&128)===0&&(typeof a.getDerivedStateFromError=="function"||d!==null&&typeof d.componentDidCatch=="function"&&(ms===null||!ms.has(d))))return s.flags|=65536,c&=-c,s.lanes|=c,c=Ch(c),Ah(c,e,s,r),hc(s,c),!1}s=s.return}while(s!==null);return!1}var zh=Error(o(461)),fa=!1;function ja(e,a,s,r){a.child=e===null?yh(a,null,s,r):gi(a,e.child,s,r)}function kh(e,a,s,r,c){s=s.render;var d=a.ref;if("ref"in r){var g={};for(var j in r)j!=="ref"&&(g[j]=r[j])}else g=r;return Os(a),r=vc(e,a,s,g,d,c),j=yc(),e!==null&&!fa?(bc(e,a,c),Bn(e,a,c)):(Nt&&j&&tc(a),a.flags|=1,ja(e,a,r,c),a.child)}function Eh(e,a,s,r,c){if(e===null){var d=s.type;return typeof d=="function"&&!Ko(d)&&d.defaultProps===void 0&&s.compare===null?(a.tag=15,a.type=d,Mh(e,a,d,r,c)):(e=dl(s.type,null,r,a,a.mode,c),e.ref=a.ref,e.return=a,a.child=e)}if(d=e.child,!Fc(e,c)){var g=d.memoizedProps;if(s=s.compare,s=s!==null?s:Zi,s(g,r)&&e.ref===a.ref)return Bn(e,a,c)}return a.flags|=1,e=Mn(d,r),e.ref=a.ref,e.return=a,a.child=e}function Mh(e,a,s,r,c){if(e!==null){var d=e.memoizedProps;if(Zi(d,r)&&e.ref===a.ref)if(fa=!1,a.pendingProps=r=d,Fc(e,c))(e.flags&131072)!==0&&(fa=!0);else return a.lanes=e.lanes,Bn(e,a,c)}return Oc(e,a,s,r,c)}function Dh(e,a,s){var r=a.pendingProps,c=r.children,d=e!==null?e.memoizedState:null;if(r.mode==="hidden"){if((a.flags&128)!==0){if(r=d!==null?d.baseLanes|s:s,e!==null){for(c=a.child=e.child,d=0;c!==null;)d=d|c.lanes|c.childLanes,c=c.sibling;a.childLanes=d&~r}else a.childLanes=0,a.child=null;return Rh(e,a,r,s)}if((s&536870912)!==0)a.memoizedState={baseLanes:0,cachePool:null},e!==null&&pl(a,d!==null?d.cachePool:null),d!==null?Mf(a,d):pc(),bh(a);else return a.lanes=a.childLanes=536870912,Rh(e,a,d!==null?d.baseLanes|s:s,s)}else d!==null?(pl(a,d.cachePool),Mf(a,d),os(),a.memoizedState=null):(e!==null&&pl(a,null),pc(),os());return ja(e,a,c,s),a.child}function Rh(e,a,s,r){var c=cc();return c=c===null?null:{parent:la._currentValue,pool:c},a.memoizedState={baseLanes:s,cachePool:c},e!==null&&pl(a,null),pc(),bh(a),e!==null&&er(e,a,r,!0),null}function Ml(e,a){var s=a.ref;if(s===null)e!==null&&e.ref!==null&&(a.flags|=4194816);else{if(typeof s!="function"&&typeof s!="object")throw Error(o(284));(e===null||e.ref!==s)&&(a.flags|=4194816)}}function Oc(e,a,s,r,c){return Os(a),s=vc(e,a,s,r,void 0,c),r=yc(),e!==null&&!fa?(bc(e,a,c),Bn(e,a,c)):(Nt&&r&&tc(a),a.flags|=1,ja(e,a,s,c),a.child)}function Uh(e,a,s,r,c,d){return Os(a),a.updateQueue=null,s=Rf(a,r,s,c),Df(e),r=yc(),e!==null&&!fa?(bc(e,a,d),Bn(e,a,d)):(Nt&&r&&tc(a),a.flags|=1,ja(e,a,s,d),a.child)}function Oh(e,a,s,r,c){if(Os(a),a.stateNode===null){var d=ri,g=s.contextType;typeof g=="object"&&g!==null&&(d=Aa(g)),d=new s(r,d),a.memoizedState=d.state!==null&&d.state!==void 0?d.state:null,d.updater=Rc,a.stateNode=d,d._reactInternals=a,d=a.stateNode,d.props=r,d.state=a.memoizedState,d.refs={},uc(a),g=s.contextType,d.context=typeof g=="object"&&g!==null?Aa(g):ri,d.state=a.memoizedState,g=s.getDerivedStateFromProps,typeof g=="function"&&(Dc(a,s,g,r),d.state=a.memoizedState),typeof s.getDerivedStateFromProps=="function"||typeof d.getSnapshotBeforeUpdate=="function"||typeof d.UNSAFE_componentWillMount!="function"&&typeof d.componentWillMount!="function"||(g=d.state,typeof d.componentWillMount=="function"&&d.componentWillMount(),typeof d.UNSAFE_componentWillMount=="function"&&d.UNSAFE_componentWillMount(),g!==d.state&&Rc.enqueueReplaceState(d,d.state,null),lr(a,r,d,c),rr(),d.state=a.memoizedState),typeof d.componentDidMount=="function"&&(a.flags|=4194308),r=!0}else if(e===null){d=a.stateNode;var j=a.memoizedProps,C=Bs(s,j);d.props=C;var q=d.context,X=s.contextType;g=ri,typeof X=="object"&&X!==null&&(g=Aa(X));var te=s.getDerivedStateFromProps;X=typeof te=="function"||typeof d.getSnapshotBeforeUpdate=="function",j=a.pendingProps!==j,X||typeof d.UNSAFE_componentWillReceiveProps!="function"&&typeof d.componentWillReceiveProps!="function"||(j||q!==g)&&Nh(a,d,r,g),ns=!1;var H=a.memoizedState;d.state=H,lr(a,r,d,c),rr(),q=a.memoizedState,j||H!==q||ns?(typeof te=="function"&&(Dc(a,s,te,r),q=a.memoizedState),(C=ns||jh(a,s,C,r,H,q,g))?(X||typeof d.UNSAFE_componentWillMount!="function"&&typeof d.componentWillMount!="function"||(typeof d.componentWillMount=="function"&&d.componentWillMount(),typeof d.UNSAFE_componentWillMount=="function"&&d.UNSAFE_componentWillMount()),typeof d.componentDidMount=="function"&&(a.flags|=4194308)):(typeof d.componentDidMount=="function"&&(a.flags|=4194308),a.memoizedProps=r,a.memoizedState=q),d.props=r,d.state=q,d.context=g,r=C):(typeof d.componentDidMount=="function"&&(a.flags|=4194308),r=!1)}else{d=a.stateNode,fc(e,a),g=a.memoizedProps,X=Bs(s,g),d.props=X,te=a.pendingProps,H=d.context,q=s.contextType,C=ri,typeof q=="object"&&q!==null&&(C=Aa(q)),j=s.getDerivedStateFromProps,(q=typeof j=="function"||typeof d.getSnapshotBeforeUpdate=="function")||typeof d.UNSAFE_componentWillReceiveProps!="function"&&typeof d.componentWillReceiveProps!="function"||(g!==te||H!==C)&&Nh(a,d,r,C),ns=!1,H=a.memoizedState,d.state=H,lr(a,r,d,c),rr();var I=a.memoizedState;g!==te||H!==I||ns||e!==null&&e.dependencies!==null&&hl(e.dependencies)?(typeof j=="function"&&(Dc(a,s,j,r),I=a.memoizedState),(X=ns||jh(a,s,X,r,H,I,C)||e!==null&&e.dependencies!==null&&hl(e.dependencies))?(q||typeof d.UNSAFE_componentWillUpdate!="function"&&typeof d.componentWillUpdate!="function"||(typeof d.componentWillUpdate=="function"&&d.componentWillUpdate(r,I,C),typeof d.UNSAFE_componentWillUpdate=="function"&&d.UNSAFE_componentWillUpdate(r,I,C)),typeof d.componentDidUpdate=="function"&&(a.flags|=4),typeof d.getSnapshotBeforeUpdate=="function"&&(a.flags|=1024)):(typeof d.componentDidUpdate!="function"||g===e.memoizedProps&&H===e.memoizedState||(a.flags|=4),typeof d.getSnapshotBeforeUpdate!="function"||g===e.memoizedProps&&H===e.memoizedState||(a.flags|=1024),a.memoizedProps=r,a.memoizedState=I),d.props=r,d.state=I,d.context=C,r=X):(typeof d.componentDidUpdate!="function"||g===e.memoizedProps&&H===e.memoizedState||(a.flags|=4),typeof d.getSnapshotBeforeUpdate!="function"||g===e.memoizedProps&&H===e.memoizedState||(a.flags|=1024),r=!1)}return d=r,Ml(e,a),r=(a.flags&128)!==0,d||r?(d=a.stateNode,s=r&&typeof s.getDerivedStateFromError!="function"?null:d.render(),a.flags|=1,e!==null&&r?(a.child=gi(a,e.child,null,c),a.child=gi(a,null,s,c)):ja(e,a,s,c),a.memoizedState=d.state,e=a.child):e=Bn(e,a,c),e}function Lh(e,a,s,r){return Ki(),a.flags|=256,ja(e,a,s,r),a.child}var Lc={dehydrated:null,treeContext:null,retryLane:0,hydrationErrors:null};function qc(e){return{baseLanes:e,cachePool:_f()}}function Bc(e,a,s){return e=e!==null?e.childLanes&~s:0,a&&(e|=nn),e}function qh(e,a,s){var r=a.pendingProps,c=!1,d=(a.flags&128)!==0,g;if((g=d)||(g=e!==null&&e.memoizedState===null?!1:(oa.current&2)!==0),g&&(c=!0,a.flags&=-129),g=(a.flags&32)!==0,a.flags&=-33,e===null){if(Nt){if(c?ls(a):os(),Nt){var j=Qt,C;if(C=j){e:{for(C=j,j=xn;C.nodeType!==8;){if(!j){j=null;break e}if(C=un(C.nextSibling),C===null){j=null;break e}}j=C}j!==null?(a.memoizedState={dehydrated:j,treeContext:Es!==null?{id:Dn,overflow:Rn}:null,retryLane:536870912,hydrationErrors:null},C=Fa(18,null,null,0),C.stateNode=j,C.return=a,a.child=C,Ea=a,Qt=null,C=!0):C=!1}C||Rs(a)}if(j=a.memoizedState,j!==null&&(j=j.dehydrated,j!==null))return Nd(j)?a.lanes=32:a.lanes=536870912,null;qn(a)}return j=r.children,r=r.fallback,c?(os(),c=a.mode,j=Dl({mode:"hidden",children:j},c),r=ks(r,c,s,null),j.return=a,r.return=a,j.sibling=r,a.child=j,c=a.child,c.memoizedState=qc(s),c.childLanes=Bc(e,g,s),a.memoizedState=Lc,r):(ls(a),Hc(a,j))}if(C=e.memoizedState,C!==null&&(j=C.dehydrated,j!==null)){if(d)a.flags&256?(ls(a),a.flags&=-257,a=Ic(e,a,s)):a.memoizedState!==null?(os(),a.child=e.child,a.flags|=128,a=null):(os(),c=r.fallback,j=a.mode,r=Dl({mode:"visible",children:r.children},j),c=ks(c,j,s,null),c.flags|=2,r.return=a,c.return=a,r.sibling=c,a.child=r,gi(a,e.child,null,s),r=a.child,r.memoizedState=qc(s),r.childLanes=Bc(e,g,s),a.memoizedState=Lc,a=c);else if(ls(a),Nd(j)){if(g=j.nextSibling&&j.nextSibling.dataset,g)var q=g.dgst;g=q,r=Error(o(419)),r.stack="",r.digest=g,Wi({value:r,source:null,stack:null}),a=Ic(e,a,s)}else if(fa||er(e,a,s,!1),g=(s&e.childLanes)!==0,fa||g){if(g=Ht,g!==null&&(r=s&-s,r=(r&42)!==0?1:jt(r),r=(r&(g.suspendedLanes|s))!==0?0:r,r!==0&&r!==C.retryLane))throw C.retryLane=r,ii(e,r),Xa(g,e,r),zh;j.data==="$?"||id(),a=Ic(e,a,s)}else j.data==="$?"?(a.flags|=192,a.child=e.child,a=null):(e=C.treeContext,Qt=un(j.nextSibling),Ea=a,Nt=!0,Ds=null,xn=!1,e!==null&&(en[tn++]=Dn,en[tn++]=Rn,en[tn++]=Es,Dn=e.id,Rn=e.overflow,Es=a),a=Hc(a,r.children),a.flags|=4096);return a}return c?(os(),c=r.fallback,j=a.mode,C=e.child,q=C.sibling,r=Mn(C,{mode:"hidden",children:r.children}),r.subtreeFlags=C.subtreeFlags&65011712,q!==null?c=Mn(q,c):(c=ks(c,j,s,null),c.flags|=2),c.return=a,r.return=a,r.sibling=c,a.child=r,r=c,c=a.child,j=e.child.memoizedState,j===null?j=qc(s):(C=j.cachePool,C!==null?(q=la._currentValue,C=C.parent!==q?{parent:q,pool:q}:C):C=_f(),j={baseLanes:j.baseLanes|s,cachePool:C}),c.memoizedState=j,c.childLanes=Bc(e,g,s),a.memoizedState=Lc,r):(ls(a),s=e.child,e=s.sibling,s=Mn(s,{mode:"visible",children:r.children}),s.return=a,s.sibling=null,e!==null&&(g=a.deletions,g===null?(a.deletions=[e],a.flags|=16):g.push(e)),a.child=s,a.memoizedState=null,s)}function Hc(e,a){return a=Dl({mode:"visible",children:a},e.mode),a.return=e,e.child=a}function Dl(e,a){return e=Fa(22,e,null,a),e.lanes=0,e.stateNode={_visibility:1,_pendingMarkers:null,_retryCache:null,_transitions:null},e}function Ic(e,a,s){return gi(a,e.child,null,s),e=Hc(a,a.pendingProps.children),e.flags|=2,a.memoizedState=null,e}function Bh(e,a,s){e.lanes|=a;var r=e.alternate;r!==null&&(r.lanes|=a),ic(e.return,a,s)}function $c(e,a,s,r,c){var d=e.memoizedState;d===null?e.memoizedState={isBackwards:a,rendering:null,renderingStartTime:0,last:r,tail:s,tailMode:c}:(d.isBackwards=a,d.rendering=null,d.renderingStartTime=0,d.last=r,d.tail=s,d.tailMode=c)}function Hh(e,a,s){var r=a.pendingProps,c=r.revealOrder,d=r.tail;if(ja(e,a,r.children,s),r=oa.current,(r&2)!==0)r=r&1|2,a.flags|=128;else{if(e!==null&&(e.flags&128)!==0)e:for(e=a.child;e!==null;){if(e.tag===13)e.memoizedState!==null&&Bh(e,s,a);else if(e.tag===19)Bh(e,s,a);else if(e.child!==null){e.child.return=e,e=e.child;continue}if(e===a)break e;for(;e.sibling===null;){if(e.return===null||e.return===a)break e;e=e.return}e.sibling.return=e.return,e=e.sibling}r&=1}switch(ce(oa,r),c){case"forwards":for(s=a.child,c=null;s!==null;)e=s.alternate,e!==null&&zl(e)===null&&(c=s),s=s.sibling;s=c,s===null?(c=a.child,a.child=null):(c=s.sibling,s.sibling=null),$c(a,!1,c,s,d);break;case"backwards":for(s=null,c=a.child,a.child=null;c!==null;){if(e=c.alternate,e!==null&&zl(e)===null){a.child=c;break}e=c.sibling,c.sibling=s,s=c,c=e}$c(a,!0,s,null,d);break;case"together":$c(a,!1,null,null,void 0);break;default:a.memoizedState=null}return a.child}function Bn(e,a,s){if(e!==null&&(a.dependencies=e.dependencies),hs|=a.lanes,(s&a.childLanes)===0)if(e!==null){if(er(e,a,s,!1),(s&a.childLanes)===0)return null}else return null;if(e!==null&&a.child!==e.child)throw Error(o(153));if(a.child!==null){for(e=a.child,s=Mn(e,e.pendingProps),a.child=s,s.return=a;e.sibling!==null;)e=e.sibling,s=s.sibling=Mn(e,e.pendingProps),s.return=a;s.sibling=null}return a.child}function Fc(e,a){return(e.lanes&a)!==0?!0:(e=e.dependencies,!!(e!==null&&hl(e)))}function k0(e,a,s){switch(a.tag){case 3:$e(a,a.stateNode.containerInfo),as(a,la,e.memoizedState.cache),Ki();break;case 27:case 5:k(a);break;case 4:$e(a,a.stateNode.containerInfo);break;case 10:as(a,a.type,a.memoizedProps.value);break;case 13:var r=a.memoizedState;if(r!==null)return r.dehydrated!==null?(ls(a),a.flags|=128,null):(s&a.child.childLanes)!==0?qh(e,a,s):(ls(a),e=Bn(e,a,s),e!==null?e.sibling:null);ls(a);break;case 19:var c=(e.flags&128)!==0;if(r=(s&a.childLanes)!==0,r||(er(e,a,s,!1),r=(s&a.childLanes)!==0),c){if(r)return Hh(e,a,s);a.flags|=128}if(c=a.memoizedState,c!==null&&(c.rendering=null,c.tail=null,c.lastEffect=null),ce(oa,oa.current),r)break;return null;case 22:case 23:return a.lanes=0,Dh(e,a,s);case 24:as(a,la,e.memoizedState.cache)}return Bn(e,a,s)}function Ih(e,a,s){if(e!==null)if(e.memoizedProps!==a.pendingProps)fa=!0;else{if(!Fc(e,s)&&(a.flags&128)===0)return fa=!1,k0(e,a,s);fa=(e.flags&131072)!==0}else fa=!1,Nt&&(a.flags&1048576)!==0&&xf(a,fl,a.index);switch(a.lanes=0,a.tag){case 16:e:{e=a.pendingProps;var r=a.elementType,c=r._init;if(r=c(r._payload),a.type=r,typeof r=="function")Ko(r)?(e=Bs(r,e),a.tag=1,a=Oh(null,a,r,e,s)):(a.tag=0,a=Oc(null,a,r,e,s));else{if(r!=null){if(c=r.$$typeof,c===Ae){a.tag=11,a=kh(null,a,r,e,s);break e}else if(c===W){a.tag=14,a=Eh(null,a,r,e,s);break e}}throw a=we(r)||r,Error(o(306,a,""))}}return a;case 0:return Oc(e,a,a.type,a.pendingProps,s);case 1:return r=a.type,c=Bs(r,a.pendingProps),Oh(e,a,r,c,s);case 3:e:{if($e(a,a.stateNode.containerInfo),e===null)throw Error(o(387));r=a.pendingProps;var d=a.memoizedState;c=d.element,fc(e,a),lr(a,r,null,s);var g=a.memoizedState;if(r=g.cache,as(a,la,r),r!==d.cache&&rc(a,[la],s,!0),rr(),r=g.element,d.isDehydrated)if(d={element:r,isDehydrated:!1,cache:g.cache},a.updateQueue.baseState=d,a.memoizedState=d,a.flags&256){a=Lh(e,a,r,s);break e}else if(r!==c){c=Ka(Error(o(424)),a),Wi(c),a=Lh(e,a,r,s);break e}else{switch(e=a.stateNode.containerInfo,e.nodeType){case 9:e=e.body;break;default:e=e.nodeName==="HTML"?e.ownerDocument.body:e}for(Qt=un(e.firstChild),Ea=a,Nt=!0,Ds=null,xn=!0,s=yh(a,null,r,s),a.child=s;s;)s.flags=s.flags&-3|4096,s=s.sibling}else{if(Ki(),r===c){a=Bn(e,a,s);break e}ja(e,a,r,s)}a=a.child}return a;case 26:return Ml(e,a),e===null?(s=Gm(a.type,null,a.pendingProps,null))?a.memoizedState=s:Nt||(s=a.type,e=a.pendingProps,r=Vl(ve.current).createElement(s),r[Ee]=a,r[Pe]=e,wa(r,s,e),pt(r),a.stateNode=r):a.memoizedState=Gm(a.type,e.memoizedProps,a.pendingProps,e.memoizedState),null;case 27:return k(a),e===null&&Nt&&(r=a.stateNode=$m(a.type,a.pendingProps,ve.current),Ea=a,xn=!0,c=Qt,xs(a.type)?(wd=c,Qt=un(r.firstChild)):Qt=c),ja(e,a,a.pendingProps.children,s),Ml(e,a),e===null&&(a.flags|=4194304),a.child;case 5:return e===null&&Nt&&((c=r=Qt)&&(r=sv(r,a.type,a.pendingProps,xn),r!==null?(a.stateNode=r,Ea=a,Qt=un(r.firstChild),xn=!1,c=!0):c=!1),c||Rs(a)),k(a),c=a.type,d=a.pendingProps,g=e!==null?e.memoizedProps:null,r=d.children,yd(c,d)?r=null:g!==null&&yd(c,g)&&(a.flags|=32),a.memoizedState!==null&&(c=vc(e,a,N0,null,null,s),zr._currentValue=c),Ml(e,a),ja(e,a,r,s),a.child;case 6:return e===null&&Nt&&((e=s=Qt)&&(s=iv(s,a.pendingProps,xn),s!==null?(a.stateNode=s,Ea=a,Qt=null,e=!0):e=!1),e||Rs(a)),null;case 13:return qh(e,a,s);case 4:return $e(a,a.stateNode.containerInfo),r=a.pendingProps,e===null?a.child=gi(a,null,r,s):ja(e,a,r,s),a.child;case 11:return kh(e,a,a.type,a.pendingProps,s);case 7:return ja(e,a,a.pendingProps,s),a.child;case 8:return ja(e,a,a.pendingProps.children,s),a.child;case 12:return ja(e,a,a.pendingProps.children,s),a.child;case 10:return r=a.pendingProps,as(a,a.type,r.value),ja(e,a,r.children,s),a.child;case 9:return c=a.type._context,r=a.pendingProps.children,Os(a),c=Aa(c),r=r(c),a.flags|=1,ja(e,a,r,s),a.child;case 14:return Eh(e,a,a.type,a.pendingProps,s);case 15:return Mh(e,a,a.type,a.pendingProps,s);case 19:return Hh(e,a,s);case 31:return r=a.pendingProps,s=a.mode,r={mode:r.mode,children:r.children},e===null?(s=Dl(r,s),s.ref=a.ref,a.child=s,s.return=a,a=s):(s=Mn(e.child,r),s.ref=a.ref,a.child=s,s.return=a,a=s),a;case 22:return Dh(e,a,s);case 24:return Os(a),r=Aa(la),e===null?(c=cc(),c===null&&(c=Ht,d=lc(),c.pooledCache=d,d.refCount++,d!==null&&(c.pooledCacheLanes|=s),c=d),a.memoizedState={parent:r,cache:c},uc(a),as(a,la,c)):((e.lanes&s)!==0&&(fc(e,a),lr(a,null,null,s),rr()),c=e.memoizedState,d=a.memoizedState,c.parent!==r?(c={parent:r,cache:r},a.memoizedState=c,a.lanes===0&&(a.memoizedState=a.updateQueue.baseState=c),as(a,la,r)):(r=d.cache,as(a,la,r),r!==c.cache&&rc(a,[la],s,!0))),ja(e,a,a.pendingProps.children,s),a.child;case 29:throw a.pendingProps}throw Error(o(156,a.tag))}function Hn(e){e.flags|=4}function $h(e,a){if(a.type!=="stylesheet"||(a.state.loading&4)!==0)e.flags&=-16777217;else if(e.flags|=16777216,!Qm(a)){if(a=an.current,a!==null&&((mt&4194048)===mt?vn!==null:(mt&62914560)!==mt&&(mt&536870912)===0||a!==vn))throw sr=dc,Sf;e.flags|=8192}}function Rl(e,a){a!==null&&(e.flags|=4),e.flags&16384&&(a=e.tag!==22?_t():536870912,e.lanes|=a,bi|=a)}function mr(e,a){if(!Nt)switch(e.tailMode){case"hidden":a=e.tail;for(var s=null;a!==null;)a.alternate!==null&&(s=a),a=a.sibling;s===null?e.tail=null:s.sibling=null;break;case"collapsed":s=e.tail;for(var r=null;s!==null;)s.alternate!==null&&(r=s),s=s.sibling;r===null?a||e.tail===null?e.tail=null:e.tail.sibling=null:r.sibling=null}}function Xt(e){var a=e.alternate!==null&&e.alternate.child===e.child,s=0,r=0;if(a)for(var c=e.child;c!==null;)s|=c.lanes|c.childLanes,r|=c.subtreeFlags&65011712,r|=c.flags&65011712,c.return=e,c=c.sibling;else for(c=e.child;c!==null;)s|=c.lanes|c.childLanes,r|=c.subtreeFlags,r|=c.flags,c.return=e,c=c.sibling;return e.subtreeFlags|=r,e.childLanes=s,a}function E0(e,a,s){var r=a.pendingProps;switch(ac(a),a.tag){case 31:case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return Xt(a),null;case 1:return Xt(a),null;case 3:return s=a.stateNode,r=null,e!==null&&(r=e.memoizedState.cache),a.memoizedState.cache!==r&&(a.flags|=2048),On(la),re(),s.pendingContext&&(s.context=s.pendingContext,s.pendingContext=null),(e===null||e.child===null)&&(Ji(a)?Hn(a):e===null||e.memoizedState.isDehydrated&&(a.flags&256)===0||(a.flags|=1024,bf())),Xt(a),null;case 26:return s=a.memoizedState,e===null?(Hn(a),s!==null?(Xt(a),$h(a,s)):(Xt(a),a.flags&=-16777217)):s?s!==e.memoizedState?(Hn(a),Xt(a),$h(a,s)):(Xt(a),a.flags&=-16777217):(e.memoizedProps!==r&&Hn(a),Xt(a),a.flags&=-16777217),null;case 27:se(a),s=ve.current;var c=a.type;if(e!==null&&a.stateNode!=null)e.memoizedProps!==r&&Hn(a);else{if(!r){if(a.stateNode===null)throw Error(o(166));return Xt(a),null}e=fe.current,Ji(a)?vf(a):(e=$m(c,r,s),a.stateNode=e,Hn(a))}return Xt(a),null;case 5:if(se(a),s=a.type,e!==null&&a.stateNode!=null)e.memoizedProps!==r&&Hn(a);else{if(!r){if(a.stateNode===null)throw Error(o(166));return Xt(a),null}if(e=fe.current,Ji(a))vf(a);else{switch(c=Vl(ve.current),e){case 1:e=c.createElementNS("http://www.w3.org/2000/svg",s);break;case 2:e=c.createElementNS("http://www.w3.org/1998/Math/MathML",s);break;default:switch(s){case"svg":e=c.createElementNS("http://www.w3.org/2000/svg",s);break;case"math":e=c.createElementNS("http://www.w3.org/1998/Math/MathML",s);break;case"script":e=c.createElement("div"),e.innerHTML="<script><\/script>",e=e.removeChild(e.firstChild);break;case"select":e=typeof r.is=="string"?c.createElement("select",{is:r.is}):c.createElement("select"),r.multiple?e.multiple=!0:r.size&&(e.size=r.size);break;default:e=typeof r.is=="string"?c.createElement(s,{is:r.is}):c.createElement(s)}}e[Ee]=a,e[Pe]=r;e:for(c=a.child;c!==null;){if(c.tag===5||c.tag===6)e.appendChild(c.stateNode);else if(c.tag!==4&&c.tag!==27&&c.child!==null){c.child.return=c,c=c.child;continue}if(c===a)break e;for(;c.sibling===null;){if(c.return===null||c.return===a)break e;c=c.return}c.sibling.return=c.return,c=c.sibling}a.stateNode=e;e:switch(wa(e,s,r),s){case"button":case"input":case"select":case"textarea":e=!!r.autoFocus;break e;case"img":e=!0;break e;default:e=!1}e&&Hn(a)}}return Xt(a),a.flags&=-16777217,null;case 6:if(e&&a.stateNode!=null)e.memoizedProps!==r&&Hn(a);else{if(typeof r!="string"&&a.stateNode===null)throw Error(o(166));if(e=ve.current,Ji(a)){if(e=a.stateNode,s=a.memoizedProps,r=null,c=Ea,c!==null)switch(c.tag){case 27:case 5:r=c.memoizedProps}e[Ee]=a,e=!!(e.nodeValue===s||r!==null&&r.suppressHydrationWarning===!0||Um(e.nodeValue,s)),e||Rs(a)}else e=Vl(e).createTextNode(r),e[Ee]=a,a.stateNode=e}return Xt(a),null;case 13:if(r=a.memoizedState,e===null||e.memoizedState!==null&&e.memoizedState.dehydrated!==null){if(c=Ji(a),r!==null&&r.dehydrated!==null){if(e===null){if(!c)throw Error(o(318));if(c=a.memoizedState,c=c!==null?c.dehydrated:null,!c)throw Error(o(317));c[Ee]=a}else Ki(),(a.flags&128)===0&&(a.memoizedState=null),a.flags|=4;Xt(a),c=!1}else c=bf(),e!==null&&e.memoizedState!==null&&(e.memoizedState.hydrationErrors=c),c=!0;if(!c)return a.flags&256?(qn(a),a):(qn(a),null)}if(qn(a),(a.flags&128)!==0)return a.lanes=s,a;if(s=r!==null,e=e!==null&&e.memoizedState!==null,s){r=a.child,c=null,r.alternate!==null&&r.alternate.memoizedState!==null&&r.alternate.memoizedState.cachePool!==null&&(c=r.alternate.memoizedState.cachePool.pool);var d=null;r.memoizedState!==null&&r.memoizedState.cachePool!==null&&(d=r.memoizedState.cachePool.pool),d!==c&&(r.flags|=2048)}return s!==e&&s&&(a.child.flags|=8192),Rl(a,a.updateQueue),Xt(a),null;case 4:return re(),e===null&&md(a.stateNode.containerInfo),Xt(a),null;case 10:return On(a.type),Xt(a),null;case 19:if(le(oa),c=a.memoizedState,c===null)return Xt(a),null;if(r=(a.flags&128)!==0,d=c.rendering,d===null)if(r)mr(c,!1);else{if(Jt!==0||e!==null&&(e.flags&128)!==0)for(e=a.child;e!==null;){if(d=zl(e),d!==null){for(a.flags|=128,mr(c,!1),e=d.updateQueue,a.updateQueue=e,Rl(a,e),a.subtreeFlags=0,e=s,s=a.child;s!==null;)gf(s,e),s=s.sibling;return ce(oa,oa.current&1|2),a.child}e=e.sibling}c.tail!==null&&et()>Ll&&(a.flags|=128,r=!0,mr(c,!1),a.lanes=4194304)}else{if(!r)if(e=zl(d),e!==null){if(a.flags|=128,r=!0,e=e.updateQueue,a.updateQueue=e,Rl(a,e),mr(c,!0),c.tail===null&&c.tailMode==="hidden"&&!d.alternate&&!Nt)return Xt(a),null}else 2*et()-c.renderingStartTime>Ll&&s!==536870912&&(a.flags|=128,r=!0,mr(c,!1),a.lanes=4194304);c.isBackwards?(d.sibling=a.child,a.child=d):(e=c.last,e!==null?e.sibling=d:a.child=d,c.last=d)}return c.tail!==null?(a=c.tail,c.rendering=a,c.tail=a.sibling,c.renderingStartTime=et(),a.sibling=null,e=oa.current,ce(oa,r?e&1|2:e&1),a):(Xt(a),null);case 22:case 23:return qn(a),gc(),r=a.memoizedState!==null,e!==null?e.memoizedState!==null!==r&&(a.flags|=8192):r&&(a.flags|=8192),r?(s&536870912)!==0&&(a.flags&128)===0&&(Xt(a),a.subtreeFlags&6&&(a.flags|=8192)):Xt(a),s=a.updateQueue,s!==null&&Rl(a,s.retryQueue),s=null,e!==null&&e.memoizedState!==null&&e.memoizedState.cachePool!==null&&(s=e.memoizedState.cachePool.pool),r=null,a.memoizedState!==null&&a.memoizedState.cachePool!==null&&(r=a.memoizedState.cachePool.pool),r!==s&&(a.flags|=2048),e!==null&&le(Ls),null;case 24:return s=null,e!==null&&(s=e.memoizedState.cache),a.memoizedState.cache!==s&&(a.flags|=2048),On(la),Xt(a),null;case 25:return null;case 30:return null}throw Error(o(156,a.tag))}function M0(e,a){switch(ac(a),a.tag){case 1:return e=a.flags,e&65536?(a.flags=e&-65537|128,a):null;case 3:return On(la),re(),e=a.flags,(e&65536)!==0&&(e&128)===0?(a.flags=e&-65537|128,a):null;case 26:case 27:case 5:return se(a),null;case 13:if(qn(a),e=a.memoizedState,e!==null&&e.dehydrated!==null){if(a.alternate===null)throw Error(o(340));Ki()}return e=a.flags,e&65536?(a.flags=e&-65537|128,a):null;case 19:return le(oa),null;case 4:return re(),null;case 10:return On(a.type),null;case 22:case 23:return qn(a),gc(),e!==null&&le(Ls),e=a.flags,e&65536?(a.flags=e&-65537|128,a):null;case 24:return On(la),null;case 25:return null;default:return null}}function Fh(e,a){switch(ac(a),a.tag){case 3:On(la),re();break;case 26:case 27:case 5:se(a);break;case 4:re();break;case 13:qn(a);break;case 19:le(oa);break;case 10:On(a.type);break;case 22:case 23:qn(a),gc(),e!==null&&le(Ls);break;case 24:On(la)}}function pr(e,a){try{var s=a.updateQueue,r=s!==null?s.lastEffect:null;if(r!==null){var c=r.next;s=c;do{if((s.tag&e)===e){r=void 0;var d=s.create,g=s.inst;r=d(),g.destroy=r}s=s.next}while(s!==c)}}catch(j){Lt(a,a.return,j)}}function cs(e,a,s){try{var r=a.updateQueue,c=r!==null?r.lastEffect:null;if(c!==null){var d=c.next;r=d;do{if((r.tag&e)===e){var g=r.inst,j=g.destroy;if(j!==void 0){g.destroy=void 0,c=a;var C=s,q=j;try{q()}catch(X){Lt(c,C,X)}}}r=r.next}while(r!==d)}}catch(X){Lt(a,a.return,X)}}function Yh(e){var a=e.updateQueue;if(a!==null){var s=e.stateNode;try{Ef(a,s)}catch(r){Lt(e,e.return,r)}}}function Gh(e,a,s){s.props=Bs(e.type,e.memoizedProps),s.state=e.memoizedState;try{s.componentWillUnmount()}catch(r){Lt(e,a,r)}}function gr(e,a){try{var s=e.ref;if(s!==null){switch(e.tag){case 26:case 27:case 5:var r=e.stateNode;break;case 30:r=e.stateNode;break;default:r=e.stateNode}typeof s=="function"?e.refCleanup=s(r):s.current=r}}catch(c){Lt(e,a,c)}}function yn(e,a){var s=e.ref,r=e.refCleanup;if(s!==null)if(typeof r=="function")try{r()}catch(c){Lt(e,a,c)}finally{e.refCleanup=null,e=e.alternate,e!=null&&(e.refCleanup=null)}else if(typeof s=="function")try{s(null)}catch(c){Lt(e,a,c)}else s.current=null}function Ph(e){var a=e.type,s=e.memoizedProps,r=e.stateNode;try{e:switch(a){case"button":case"input":case"select":case"textarea":s.autoFocus&&r.focus();break e;case"img":s.src?r.src=s.src:s.srcSet&&(r.srcset=s.srcSet)}}catch(c){Lt(e,e.return,c)}}function Yc(e,a,s){try{var r=e.stateNode;W0(r,e.type,s,a),r[Pe]=a}catch(c){Lt(e,e.return,c)}}function Vh(e){return e.tag===5||e.tag===3||e.tag===26||e.tag===27&&xs(e.type)||e.tag===4}function Gc(e){e:for(;;){for(;e.sibling===null;){if(e.return===null||Vh(e.return))return null;e=e.return}for(e.sibling.return=e.return,e=e.sibling;e.tag!==5&&e.tag!==6&&e.tag!==18;){if(e.tag===27&&xs(e.type)||e.flags&2||e.child===null||e.tag===4)continue e;e.child.return=e,e=e.child}if(!(e.flags&2))return e.stateNode}}function Pc(e,a,s){var r=e.tag;if(r===5||r===6)e=e.stateNode,a?(s.nodeType===9?s.body:s.nodeName==="HTML"?s.ownerDocument.body:s).insertBefore(e,a):(a=s.nodeType===9?s.body:s.nodeName==="HTML"?s.ownerDocument.body:s,a.appendChild(e),s=s._reactRootContainer,s!=null||a.onclick!==null||(a.onclick=Pl));else if(r!==4&&(r===27&&xs(e.type)&&(s=e.stateNode,a=null),e=e.child,e!==null))for(Pc(e,a,s),e=e.sibling;e!==null;)Pc(e,a,s),e=e.sibling}function Ul(e,a,s){var r=e.tag;if(r===5||r===6)e=e.stateNode,a?s.insertBefore(e,a):s.appendChild(e);else if(r!==4&&(r===27&&xs(e.type)&&(s=e.stateNode),e=e.child,e!==null))for(Ul(e,a,s),e=e.sibling;e!==null;)Ul(e,a,s),e=e.sibling}function Xh(e){var a=e.stateNode,s=e.memoizedProps;try{for(var r=e.type,c=a.attributes;c.length;)a.removeAttributeNode(c[0]);wa(a,r,s),a[Ee]=e,a[Pe]=s}catch(d){Lt(e,e.return,d)}}var In=!1,ta=!1,Vc=!1,Zh=typeof WeakSet=="function"?WeakSet:Set,ha=null;function D0(e,a){if(e=e.containerInfo,xd=Wl,e=rf(e),Go(e)){if("selectionStart"in e)var s={start:e.selectionStart,end:e.selectionEnd};else e:{s=(s=e.ownerDocument)&&s.defaultView||window;var r=s.getSelection&&s.getSelection();if(r&&r.rangeCount!==0){s=r.anchorNode;var c=r.anchorOffset,d=r.focusNode;r=r.focusOffset;try{s.nodeType,d.nodeType}catch{s=null;break e}var g=0,j=-1,C=-1,q=0,X=0,te=e,H=null;t:for(;;){for(var I;te!==s||c!==0&&te.nodeType!==3||(j=g+c),te!==d||r!==0&&te.nodeType!==3||(C=g+r),te.nodeType===3&&(g+=te.nodeValue.length),(I=te.firstChild)!==null;)H=te,te=I;for(;;){if(te===e)break t;if(H===s&&++q===c&&(j=g),H===d&&++X===r&&(C=g),(I=te.nextSibling)!==null)break;te=H,H=te.parentNode}te=I}s=j===-1||C===-1?null:{start:j,end:C}}else s=null}s=s||{start:0,end:0}}else s=null;for(vd={focusedElem:e,selectionRange:s},Wl=!1,ha=a;ha!==null;)if(a=ha,e=a.child,(a.subtreeFlags&1024)!==0&&e!==null)e.return=a,ha=e;else for(;ha!==null;){switch(a=ha,d=a.alternate,e=a.flags,a.tag){case 0:break;case 11:case 15:break;case 1:if((e&1024)!==0&&d!==null){e=void 0,s=a,c=d.memoizedProps,d=d.memoizedState,r=s.stateNode;try{var Je=Bs(s.type,c,s.elementType===s.type);e=r.getSnapshotBeforeUpdate(Je,d),r.__reactInternalSnapshotBeforeUpdate=e}catch(Ye){Lt(s,s.return,Ye)}}break;case 3:if((e&1024)!==0){if(e=a.stateNode.containerInfo,s=e.nodeType,s===9)jd(e);else if(s===1)switch(e.nodeName){case"HEAD":case"HTML":case"BODY":jd(e);break;default:e.textContent=""}}break;case 5:case 26:case 27:case 6:case 4:case 17:break;default:if((e&1024)!==0)throw Error(o(163))}if(e=a.sibling,e!==null){e.return=a.return,ha=e;break}ha=a.return}}function Qh(e,a,s){var r=s.flags;switch(s.tag){case 0:case 11:case 15:ds(e,s),r&4&&pr(5,s);break;case 1:if(ds(e,s),r&4)if(e=s.stateNode,a===null)try{e.componentDidMount()}catch(g){Lt(s,s.return,g)}else{var c=Bs(s.type,a.memoizedProps);a=a.memoizedState;try{e.componentDidUpdate(c,a,e.__reactInternalSnapshotBeforeUpdate)}catch(g){Lt(s,s.return,g)}}r&64&&Yh(s),r&512&&gr(s,s.return);break;case 3:if(ds(e,s),r&64&&(e=s.updateQueue,e!==null)){if(a=null,s.child!==null)switch(s.child.tag){case 27:case 5:a=s.child.stateNode;break;case 1:a=s.child.stateNode}try{Ef(e,a)}catch(g){Lt(s,s.return,g)}}break;case 27:a===null&&r&4&&Xh(s);case 26:case 5:ds(e,s),a===null&&r&4&&Ph(s),r&512&&gr(s,s.return);break;case 12:ds(e,s);break;case 13:ds(e,s),r&4&&Wh(e,s),r&64&&(e=s.memoizedState,e!==null&&(e=e.dehydrated,e!==null&&(s=$0.bind(null,s),rv(e,s))));break;case 22:if(r=s.memoizedState!==null||In,!r){a=a!==null&&a.memoizedState!==null||ta,c=In;var d=ta;In=r,(ta=a)&&!d?us(e,s,(s.subtreeFlags&8772)!==0):ds(e,s),In=c,ta=d}break;case 30:break;default:ds(e,s)}}function Jh(e){var a=e.alternate;a!==null&&(e.alternate=null,Jh(a)),e.child=null,e.deletions=null,e.sibling=null,e.tag===5&&(a=e.stateNode,a!==null&&Za(a)),e.stateNode=null,e.return=null,e.dependencies=null,e.memoizedProps=null,e.memoizedState=null,e.pendingProps=null,e.stateNode=null,e.updateQueue=null}var Yt=null,La=!1;function $n(e,a,s){for(s=s.child;s!==null;)Kh(e,a,s),s=s.sibling}function Kh(e,a,s){if(Re&&typeof Re.onCommitFiberUnmount=="function")try{Re.onCommitFiberUnmount(Ne,s)}catch{}switch(s.tag){case 26:ta||yn(s,a),$n(e,a,s),s.memoizedState?s.memoizedState.count--:s.stateNode&&(s=s.stateNode,s.parentNode.removeChild(s));break;case 27:ta||yn(s,a);var r=Yt,c=La;xs(s.type)&&(Yt=s.stateNode,La=!1),$n(e,a,s),Sr(s.stateNode),Yt=r,La=c;break;case 5:ta||yn(s,a);case 6:if(r=Yt,c=La,Yt=null,$n(e,a,s),Yt=r,La=c,Yt!==null)if(La)try{(Yt.nodeType===9?Yt.body:Yt.nodeName==="HTML"?Yt.ownerDocument.body:Yt).removeChild(s.stateNode)}catch(d){Lt(s,a,d)}else try{Yt.removeChild(s.stateNode)}catch(d){Lt(s,a,d)}break;case 18:Yt!==null&&(La?(e=Yt,Hm(e.nodeType===9?e.body:e.nodeName==="HTML"?e.ownerDocument.body:e,s.stateNode),Dr(e)):Hm(Yt,s.stateNode));break;case 4:r=Yt,c=La,Yt=s.stateNode.containerInfo,La=!0,$n(e,a,s),Yt=r,La=c;break;case 0:case 11:case 14:case 15:ta||cs(2,s,a),ta||cs(4,s,a),$n(e,a,s);break;case 1:ta||(yn(s,a),r=s.stateNode,typeof r.componentWillUnmount=="function"&&Gh(s,a,r)),$n(e,a,s);break;case 21:$n(e,a,s);break;case 22:ta=(r=ta)||s.memoizedState!==null,$n(e,a,s),ta=r;break;default:$n(e,a,s)}}function Wh(e,a){if(a.memoizedState===null&&(e=a.alternate,e!==null&&(e=e.memoizedState,e!==null&&(e=e.dehydrated,e!==null))))try{Dr(e)}catch(s){Lt(a,a.return,s)}}function R0(e){switch(e.tag){case 13:case 19:var a=e.stateNode;return a===null&&(a=e.stateNode=new Zh),a;case 22:return e=e.stateNode,a=e._retryCache,a===null&&(a=e._retryCache=new Zh),a;default:throw Error(o(435,e.tag))}}function Xc(e,a){var s=R0(e);a.forEach(function(r){var c=F0.bind(null,e,r);s.has(r)||(s.add(r),r.then(c,c))})}function Ya(e,a){var s=a.deletions;if(s!==null)for(var r=0;r<s.length;r++){var c=s[r],d=e,g=a,j=g;e:for(;j!==null;){switch(j.tag){case 27:if(xs(j.type)){Yt=j.stateNode,La=!1;break e}break;case 5:Yt=j.stateNode,La=!1;break e;case 3:case 4:Yt=j.stateNode.containerInfo,La=!0;break e}j=j.return}if(Yt===null)throw Error(o(160));Kh(d,g,c),Yt=null,La=!1,d=c.alternate,d!==null&&(d.return=null),c.return=null}if(a.subtreeFlags&13878)for(a=a.child;a!==null;)em(a,e),a=a.sibling}var dn=null;function em(e,a){var s=e.alternate,r=e.flags;switch(e.tag){case 0:case 11:case 14:case 15:Ya(a,e),Ga(e),r&4&&(cs(3,e,e.return),pr(3,e),cs(5,e,e.return));break;case 1:Ya(a,e),Ga(e),r&512&&(ta||s===null||yn(s,s.return)),r&64&&In&&(e=e.updateQueue,e!==null&&(r=e.callbacks,r!==null&&(s=e.shared.hiddenCallbacks,e.shared.hiddenCallbacks=s===null?r:s.concat(r))));break;case 26:var c=dn;if(Ya(a,e),Ga(e),r&512&&(ta||s===null||yn(s,s.return)),r&4){var d=s!==null?s.memoizedState:null;if(r=e.memoizedState,s===null)if(r===null)if(e.stateNode===null){e:{r=e.type,s=e.memoizedProps,c=c.ownerDocument||c;t:switch(r){case"title":d=c.getElementsByTagName("title")[0],(!d||d[da]||d[Ee]||d.namespaceURI==="http://www.w3.org/2000/svg"||d.hasAttribute("itemprop"))&&(d=c.createElement(r),c.head.insertBefore(d,c.querySelector("head > title"))),wa(d,r,s),d[Ee]=e,pt(d),r=d;break e;case"link":var g=Xm("link","href",c).get(r+(s.href||""));if(g){for(var j=0;j<g.length;j++)if(d=g[j],d.getAttribute("href")===(s.href==null||s.href===""?null:s.href)&&d.getAttribute("rel")===(s.rel==null?null:s.rel)&&d.getAttribute("title")===(s.title==null?null:s.title)&&d.getAttribute("crossorigin")===(s.crossOrigin==null?null:s.crossOrigin)){g.splice(j,1);break t}}d=c.createElement(r),wa(d,r,s),c.head.appendChild(d);break;case"meta":if(g=Xm("meta","content",c).get(r+(s.content||""))){for(j=0;j<g.length;j++)if(d=g[j],d.getAttribute("content")===(s.content==null?null:""+s.content)&&d.getAttribute("name")===(s.name==null?null:s.name)&&d.getAttribute("property")===(s.property==null?null:s.property)&&d.getAttribute("http-equiv")===(s.httpEquiv==null?null:s.httpEquiv)&&d.getAttribute("charset")===(s.charSet==null?null:s.charSet)){g.splice(j,1);break t}}d=c.createElement(r),wa(d,r,s),c.head.appendChild(d);break;default:throw Error(o(468,r))}d[Ee]=e,pt(d),r=d}e.stateNode=r}else Zm(c,e.type,e.stateNode);else e.stateNode=Vm(c,r,e.memoizedProps);else d!==r?(d===null?s.stateNode!==null&&(s=s.stateNode,s.parentNode.removeChild(s)):d.count--,r===null?Zm(c,e.type,e.stateNode):Vm(c,r,e.memoizedProps)):r===null&&e.stateNode!==null&&Yc(e,e.memoizedProps,s.memoizedProps)}break;case 27:Ya(a,e),Ga(e),r&512&&(ta||s===null||yn(s,s.return)),s!==null&&r&4&&Yc(e,e.memoizedProps,s.memoizedProps);break;case 5:if(Ya(a,e),Ga(e),r&512&&(ta||s===null||yn(s,s.return)),e.flags&32){c=e.stateNode;try{qe(c,"")}catch(I){Lt(e,e.return,I)}}r&4&&e.stateNode!=null&&(c=e.memoizedProps,Yc(e,c,s!==null?s.memoizedProps:c)),r&1024&&(Vc=!0);break;case 6:if(Ya(a,e),Ga(e),r&4){if(e.stateNode===null)throw Error(o(162));r=e.memoizedProps,s=e.stateNode;try{s.nodeValue=r}catch(I){Lt(e,e.return,I)}}break;case 3:if(Ql=null,c=dn,dn=Xl(a.containerInfo),Ya(a,e),dn=c,Ga(e),r&4&&s!==null&&s.memoizedState.isDehydrated)try{Dr(a.containerInfo)}catch(I){Lt(e,e.return,I)}Vc&&(Vc=!1,tm(e));break;case 4:r=dn,dn=Xl(e.stateNode.containerInfo),Ya(a,e),Ga(e),dn=r;break;case 12:Ya(a,e),Ga(e);break;case 13:Ya(a,e),Ga(e),e.child.flags&8192&&e.memoizedState!==null!=(s!==null&&s.memoizedState!==null)&&(ed=et()),r&4&&(r=e.updateQueue,r!==null&&(e.updateQueue=null,Xc(e,r)));break;case 22:c=e.memoizedState!==null;var C=s!==null&&s.memoizedState!==null,q=In,X=ta;if(In=q||c,ta=X||C,Ya(a,e),ta=X,In=q,Ga(e),r&8192)e:for(a=e.stateNode,a._visibility=c?a._visibility&-2:a._visibility|1,c&&(s===null||C||In||ta||Hs(e)),s=null,a=e;;){if(a.tag===5||a.tag===26){if(s===null){C=s=a;try{if(d=C.stateNode,c)g=d.style,typeof g.setProperty=="function"?g.setProperty("display","none","important"):g.display="none";else{j=C.stateNode;var te=C.memoizedProps.style,H=te!=null&&te.hasOwnProperty("display")?te.display:null;j.style.display=H==null||typeof H=="boolean"?"":(""+H).trim()}}catch(I){Lt(C,C.return,I)}}}else if(a.tag===6){if(s===null){C=a;try{C.stateNode.nodeValue=c?"":C.memoizedProps}catch(I){Lt(C,C.return,I)}}}else if((a.tag!==22&&a.tag!==23||a.memoizedState===null||a===e)&&a.child!==null){a.child.return=a,a=a.child;continue}if(a===e)break e;for(;a.sibling===null;){if(a.return===null||a.return===e)break e;s===a&&(s=null),a=a.return}s===a&&(s=null),a.sibling.return=a.return,a=a.sibling}r&4&&(r=e.updateQueue,r!==null&&(s=r.retryQueue,s!==null&&(r.retryQueue=null,Xc(e,s))));break;case 19:Ya(a,e),Ga(e),r&4&&(r=e.updateQueue,r!==null&&(e.updateQueue=null,Xc(e,r)));break;case 30:break;case 21:break;default:Ya(a,e),Ga(e)}}function Ga(e){var a=e.flags;if(a&2){try{for(var s,r=e.return;r!==null;){if(Vh(r)){s=r;break}r=r.return}if(s==null)throw Error(o(160));switch(s.tag){case 27:var c=s.stateNode,d=Gc(e);Ul(e,d,c);break;case 5:var g=s.stateNode;s.flags&32&&(qe(g,""),s.flags&=-33);var j=Gc(e);Ul(e,j,g);break;case 3:case 4:var C=s.stateNode.containerInfo,q=Gc(e);Pc(e,q,C);break;default:throw Error(o(161))}}catch(X){Lt(e,e.return,X)}e.flags&=-3}a&4096&&(e.flags&=-4097)}function tm(e){if(e.subtreeFlags&1024)for(e=e.child;e!==null;){var a=e;tm(a),a.tag===5&&a.flags&1024&&a.stateNode.reset(),e=e.sibling}}function ds(e,a){if(a.subtreeFlags&8772)for(a=a.child;a!==null;)Qh(e,a.alternate,a),a=a.sibling}function Hs(e){for(e=e.child;e!==null;){var a=e;switch(a.tag){case 0:case 11:case 14:case 15:cs(4,a,a.return),Hs(a);break;case 1:yn(a,a.return);var s=a.stateNode;typeof s.componentWillUnmount=="function"&&Gh(a,a.return,s),Hs(a);break;case 27:Sr(a.stateNode);case 26:case 5:yn(a,a.return),Hs(a);break;case 22:a.memoizedState===null&&Hs(a);break;case 30:Hs(a);break;default:Hs(a)}e=e.sibling}}function us(e,a,s){for(s=s&&(a.subtreeFlags&8772)!==0,a=a.child;a!==null;){var r=a.alternate,c=e,d=a,g=d.flags;switch(d.tag){case 0:case 11:case 15:us(c,d,s),pr(4,d);break;case 1:if(us(c,d,s),r=d,c=r.stateNode,typeof c.componentDidMount=="function")try{c.componentDidMount()}catch(q){Lt(r,r.return,q)}if(r=d,c=r.updateQueue,c!==null){var j=r.stateNode;try{var C=c.shared.hiddenCallbacks;if(C!==null)for(c.shared.hiddenCallbacks=null,c=0;c<C.length;c++)kf(C[c],j)}catch(q){Lt(r,r.return,q)}}s&&g&64&&Yh(d),gr(d,d.return);break;case 27:Xh(d);case 26:case 5:us(c,d,s),s&&r===null&&g&4&&Ph(d),gr(d,d.return);break;case 12:us(c,d,s);break;case 13:us(c,d,s),s&&g&4&&Wh(c,d);break;case 22:d.memoizedState===null&&us(c,d,s),gr(d,d.return);break;case 30:break;default:us(c,d,s)}a=a.sibling}}function Zc(e,a){var s=null;e!==null&&e.memoizedState!==null&&e.memoizedState.cachePool!==null&&(s=e.memoizedState.cachePool.pool),e=null,a.memoizedState!==null&&a.memoizedState.cachePool!==null&&(e=a.memoizedState.cachePool.pool),e!==s&&(e!=null&&e.refCount++,s!=null&&tr(s))}function Qc(e,a){e=null,a.alternate!==null&&(e=a.alternate.memoizedState.cache),a=a.memoizedState.cache,a!==e&&(a.refCount++,e!=null&&tr(e))}function bn(e,a,s,r){if(a.subtreeFlags&10256)for(a=a.child;a!==null;)am(e,a,s,r),a=a.sibling}function am(e,a,s,r){var c=a.flags;switch(a.tag){case 0:case 11:case 15:bn(e,a,s,r),c&2048&&pr(9,a);break;case 1:bn(e,a,s,r);break;case 3:bn(e,a,s,r),c&2048&&(e=null,a.alternate!==null&&(e=a.alternate.memoizedState.cache),a=a.memoizedState.cache,a!==e&&(a.refCount++,e!=null&&tr(e)));break;case 12:if(c&2048){bn(e,a,s,r),e=a.stateNode;try{var d=a.memoizedProps,g=d.id,j=d.onPostCommit;typeof j=="function"&&j(g,a.alternate===null?"mount":"update",e.passiveEffectDuration,-0)}catch(C){Lt(a,a.return,C)}}else bn(e,a,s,r);break;case 13:bn(e,a,s,r);break;case 23:break;case 22:d=a.stateNode,g=a.alternate,a.memoizedState!==null?d._visibility&2?bn(e,a,s,r):xr(e,a):d._visibility&2?bn(e,a,s,r):(d._visibility|=2,xi(e,a,s,r,(a.subtreeFlags&10256)!==0)),c&2048&&Zc(g,a);break;case 24:bn(e,a,s,r),c&2048&&Qc(a.alternate,a);break;default:bn(e,a,s,r)}}function xi(e,a,s,r,c){for(c=c&&(a.subtreeFlags&10256)!==0,a=a.child;a!==null;){var d=e,g=a,j=s,C=r,q=g.flags;switch(g.tag){case 0:case 11:case 15:xi(d,g,j,C,c),pr(8,g);break;case 23:break;case 22:var X=g.stateNode;g.memoizedState!==null?X._visibility&2?xi(d,g,j,C,c):xr(d,g):(X._visibility|=2,xi(d,g,j,C,c)),c&&q&2048&&Zc(g.alternate,g);break;case 24:xi(d,g,j,C,c),c&&q&2048&&Qc(g.alternate,g);break;default:xi(d,g,j,C,c)}a=a.sibling}}function xr(e,a){if(a.subtreeFlags&10256)for(a=a.child;a!==null;){var s=e,r=a,c=r.flags;switch(r.tag){case 22:xr(s,r),c&2048&&Zc(r.alternate,r);break;case 24:xr(s,r),c&2048&&Qc(r.alternate,r);break;default:xr(s,r)}a=a.sibling}}var vr=8192;function vi(e){if(e.subtreeFlags&vr)for(e=e.child;e!==null;)nm(e),e=e.sibling}function nm(e){switch(e.tag){case 26:vi(e),e.flags&vr&&e.memoizedState!==null&&yv(dn,e.memoizedState,e.memoizedProps);break;case 5:vi(e);break;case 3:case 4:var a=dn;dn=Xl(e.stateNode.containerInfo),vi(e),dn=a;break;case 22:e.memoizedState===null&&(a=e.alternate,a!==null&&a.memoizedState!==null?(a=vr,vr=16777216,vi(e),vr=a):vi(e));break;default:vi(e)}}function sm(e){var a=e.alternate;if(a!==null&&(e=a.child,e!==null)){a.child=null;do a=e.sibling,e.sibling=null,e=a;while(e!==null)}}function yr(e){var a=e.deletions;if((e.flags&16)!==0){if(a!==null)for(var s=0;s<a.length;s++){var r=a[s];ha=r,rm(r,e)}sm(e)}if(e.subtreeFlags&10256)for(e=e.child;e!==null;)im(e),e=e.sibling}function im(e){switch(e.tag){case 0:case 11:case 15:yr(e),e.flags&2048&&cs(9,e,e.return);break;case 3:yr(e);break;case 12:yr(e);break;case 22:var a=e.stateNode;e.memoizedState!==null&&a._visibility&2&&(e.return===null||e.return.tag!==13)?(a._visibility&=-3,Ol(e)):yr(e);break;default:yr(e)}}function Ol(e){var a=e.deletions;if((e.flags&16)!==0){if(a!==null)for(var s=0;s<a.length;s++){var r=a[s];ha=r,rm(r,e)}sm(e)}for(e=e.child;e!==null;){switch(a=e,a.tag){case 0:case 11:case 15:cs(8,a,a.return),Ol(a);break;case 22:s=a.stateNode,s._visibility&2&&(s._visibility&=-3,Ol(a));break;default:Ol(a)}e=e.sibling}}function rm(e,a){for(;ha!==null;){var s=ha;switch(s.tag){case 0:case 11:case 15:cs(8,s,a);break;case 23:case 22:if(s.memoizedState!==null&&s.memoizedState.cachePool!==null){var r=s.memoizedState.cachePool.pool;r!=null&&r.refCount++}break;case 24:tr(s.memoizedState.cache)}if(r=s.child,r!==null)r.return=s,ha=r;else e:for(s=e;ha!==null;){r=ha;var c=r.sibling,d=r.return;if(Jh(r),r===s){ha=null;break e}if(c!==null){c.return=d,ha=c;break e}ha=d}}}var U0={getCacheForType:function(e){var a=Aa(la),s=a.data.get(e);return s===void 0&&(s=e(),a.data.set(e,s)),s}},O0=typeof WeakMap=="function"?WeakMap:Map,Ct=0,Ht=null,ot=null,mt=0,At=0,Pa=null,fs=!1,yi=!1,Jc=!1,Fn=0,Jt=0,hs=0,Is=0,Kc=0,nn=0,bi=0,br=null,qa=null,Wc=!1,ed=0,Ll=1/0,ql=null,ms=null,Na=0,ps=null,ji=null,Ni=0,td=0,ad=null,lm=null,jr=0,nd=null;function Va(){if((Ct&2)!==0&&mt!==0)return mt&-mt;if(L.T!==null){var e=ci;return e!==0?e:dd()}return kt()}function om(){nn===0&&(nn=(mt&536870912)===0||Nt?Ot():536870912);var e=an.current;return e!==null&&(e.flags|=32),nn}function Xa(e,a,s){(e===Ht&&(At===2||At===9)||e.cancelPendingCommit!==null)&&(wi(e,0),gs(e,mt,nn,!1)),We(e,s),((Ct&2)===0||e!==Ht)&&(e===Ht&&((Ct&2)===0&&(Is|=s),Jt===4&&gs(e,mt,nn,!1)),jn(e))}function cm(e,a,s){if((Ct&6)!==0)throw Error(o(327));var r=!s&&(a&124)===0&&(a&e.expiredLanes)===0||tt(e,a),c=r?B0(e,a):rd(e,a,!0),d=r;do{if(c===0){yi&&!r&&gs(e,a,0,!1);break}else{if(s=e.current.alternate,d&&!L0(s)){c=rd(e,a,!1),d=!1;continue}if(c===2){if(d=a,e.errorRecoveryDisabledLanes&d)var g=0;else g=e.pendingLanes&-536870913,g=g!==0?g:g&536870912?536870912:0;if(g!==0){a=g;e:{var j=e;c=br;var C=j.current.memoizedState.isDehydrated;if(C&&(wi(j,g).flags|=256),g=rd(j,g,!1),g!==2){if(Jc&&!C){j.errorRecoveryDisabledLanes|=d,Is|=d,c=4;break e}d=qa,qa=c,d!==null&&(qa===null?qa=d:qa.push.apply(qa,d))}c=g}if(d=!1,c!==2)continue}}if(c===1){wi(e,0),gs(e,a,0,!0);break}e:{switch(r=e,d=c,d){case 0:case 1:throw Error(o(345));case 4:if((a&4194048)!==a)break;case 6:gs(r,a,nn,!fs);break e;case 2:qa=null;break;case 3:case 5:break;default:throw Error(o(329))}if((a&62914560)===a&&(c=ed+300-et(),10<c)){if(gs(r,a,nn,!fs),Ge(r,0,!0)!==0)break e;r.timeoutHandle=qm(dm.bind(null,r,s,qa,ql,Wc,a,nn,Is,bi,fs,d,2,-0,0),c);break e}dm(r,s,qa,ql,Wc,a,nn,Is,bi,fs,d,0,-0,0)}}break}while(!0);jn(e)}function dm(e,a,s,r,c,d,g,j,C,q,X,te,H,I){if(e.timeoutHandle=-1,te=a.subtreeFlags,(te&8192||(te&16785408)===16785408)&&(Ar={stylesheets:null,count:0,unsuspend:vv},nm(a),te=bv(),te!==null)){e.cancelPendingCommit=te(xm.bind(null,e,a,d,s,r,c,g,j,C,X,1,H,I)),gs(e,d,g,!q);return}xm(e,a,d,s,r,c,g,j,C)}function L0(e){for(var a=e;;){var s=a.tag;if((s===0||s===11||s===15)&&a.flags&16384&&(s=a.updateQueue,s!==null&&(s=s.stores,s!==null)))for(var r=0;r<s.length;r++){var c=s[r],d=c.getSnapshot;c=c.value;try{if(!$a(d(),c))return!1}catch{return!1}}if(s=a.child,a.subtreeFlags&16384&&s!==null)s.return=a,a=s;else{if(a===e)break;for(;a.sibling===null;){if(a.return===null||a.return===e)return!0;a=a.return}a.sibling.return=a.return,a=a.sibling}}return!0}function gs(e,a,s,r){a&=~Kc,a&=~Is,e.suspendedLanes|=a,e.pingedLanes&=~a,r&&(e.warmLanes|=a),r=e.expirationTimes;for(var c=a;0<c;){var d=31-ft(c),g=1<<d;r[d]=-1,c&=~g}s!==0&&ee(e,s,a)}function Bl(){return(Ct&6)===0?(Nr(0),!1):!0}function sd(){if(ot!==null){if(At===0)var e=ot.return;else e=ot,Un=Us=null,jc(e),pi=null,fr=0,e=ot;for(;e!==null;)Fh(e.alternate,e),e=e.return;ot=null}}function wi(e,a){var s=e.timeoutHandle;s!==-1&&(e.timeoutHandle=-1,tv(s)),s=e.cancelPendingCommit,s!==null&&(e.cancelPendingCommit=null,s()),sd(),Ht=e,ot=s=Mn(e.current,null),mt=a,At=0,Pa=null,fs=!1,yi=tt(e,a),Jc=!1,bi=nn=Kc=Is=hs=Jt=0,qa=br=null,Wc=!1,(a&8)!==0&&(a|=a&32);var r=e.entangledLanes;if(r!==0)for(e=e.entanglements,r&=a;0<r;){var c=31-ft(r),d=1<<c;a|=e[c],r&=~d}return Fn=a,ll(),s}function um(e,a){rt=null,L.H=Tl,a===nr||a===gl?(a=Af(),At=3):a===Sf?(a=Af(),At=4):At=a===zh?8:a!==null&&typeof a=="object"&&typeof a.then=="function"?6:1,Pa=a,ot===null&&(Jt=1,El(e,Ka(a,e.current)))}function fm(){var e=L.H;return L.H=Tl,e===null?Tl:e}function hm(){var e=L.A;return L.A=U0,e}function id(){Jt=4,fs||(mt&4194048)!==mt&&an.current!==null||(yi=!0),(hs&134217727)===0&&(Is&134217727)===0||Ht===null||gs(Ht,mt,nn,!1)}function rd(e,a,s){var r=Ct;Ct|=2;var c=fm(),d=hm();(Ht!==e||mt!==a)&&(ql=null,wi(e,a)),a=!1;var g=Jt;e:do try{if(At!==0&&ot!==null){var j=ot,C=Pa;switch(At){case 8:sd(),g=6;break e;case 3:case 2:case 9:case 6:an.current===null&&(a=!0);var q=At;if(At=0,Pa=null,_i(e,j,C,q),s&&yi){g=0;break e}break;default:q=At,At=0,Pa=null,_i(e,j,C,q)}}q0(),g=Jt;break}catch(X){um(e,X)}while(!0);return a&&e.shellSuspendCounter++,Un=Us=null,Ct=r,L.H=c,L.A=d,ot===null&&(Ht=null,mt=0,ll()),g}function q0(){for(;ot!==null;)mm(ot)}function B0(e,a){var s=Ct;Ct|=2;var r=fm(),c=hm();Ht!==e||mt!==a?(ql=null,Ll=et()+500,wi(e,a)):yi=tt(e,a);e:do try{if(At!==0&&ot!==null){a=ot;var d=Pa;t:switch(At){case 1:At=0,Pa=null,_i(e,a,d,1);break;case 2:case 9:if(Tf(d)){At=0,Pa=null,pm(a);break}a=function(){At!==2&&At!==9||Ht!==e||(At=7),jn(e)},d.then(a,a);break e;case 3:At=7;break e;case 4:At=5;break e;case 7:Tf(d)?(At=0,Pa=null,pm(a)):(At=0,Pa=null,_i(e,a,d,7));break;case 5:var g=null;switch(ot.tag){case 26:g=ot.memoizedState;case 5:case 27:var j=ot;if(!g||Qm(g)){At=0,Pa=null;var C=j.sibling;if(C!==null)ot=C;else{var q=j.return;q!==null?(ot=q,Hl(q)):ot=null}break t}}At=0,Pa=null,_i(e,a,d,5);break;case 6:At=0,Pa=null,_i(e,a,d,6);break;case 8:sd(),Jt=6;break e;default:throw Error(o(462))}}H0();break}catch(X){um(e,X)}while(!0);return Un=Us=null,L.H=r,L.A=c,Ct=s,ot!==null?0:(Ht=null,mt=0,ll(),Jt)}function H0(){for(;ot!==null&&!Fe();)mm(ot)}function mm(e){var a=Ih(e.alternate,e,Fn);e.memoizedProps=e.pendingProps,a===null?Hl(e):ot=a}function pm(e){var a=e,s=a.alternate;switch(a.tag){case 15:case 0:a=Uh(s,a,a.pendingProps,a.type,void 0,mt);break;case 11:a=Uh(s,a,a.pendingProps,a.type.render,a.ref,mt);break;case 5:jc(a);default:Fh(s,a),a=ot=gf(a,Fn),a=Ih(s,a,Fn)}e.memoizedProps=e.pendingProps,a===null?Hl(e):ot=a}function _i(e,a,s,r){Un=Us=null,jc(a),pi=null,fr=0;var c=a.return;try{if(z0(e,c,a,s,mt)){Jt=1,El(e,Ka(s,e.current)),ot=null;return}}catch(d){if(c!==null)throw ot=c,d;Jt=1,El(e,Ka(s,e.current)),ot=null;return}a.flags&32768?(Nt||r===1?e=!0:yi||(mt&536870912)!==0?e=!1:(fs=e=!0,(r===2||r===9||r===3||r===6)&&(r=an.current,r!==null&&r.tag===13&&(r.flags|=16384))),gm(a,e)):Hl(a)}function Hl(e){var a=e;do{if((a.flags&32768)!==0){gm(a,fs);return}e=a.return;var s=E0(a.alternate,a,Fn);if(s!==null){ot=s;return}if(a=a.sibling,a!==null){ot=a;return}ot=a=e}while(a!==null);Jt===0&&(Jt=5)}function gm(e,a){do{var s=M0(e.alternate,e);if(s!==null){s.flags&=32767,ot=s;return}if(s=e.return,s!==null&&(s.flags|=32768,s.subtreeFlags=0,s.deletions=null),!a&&(e=e.sibling,e!==null)){ot=e;return}ot=e=s}while(e!==null);Jt=6,ot=null}function xm(e,a,s,r,c,d,g,j,C){e.cancelPendingCommit=null;do Il();while(Na!==0);if((Ct&6)!==0)throw Error(o(327));if(a!==null){if(a===e.current)throw Error(o(177));if(d=a.lanes|a.childLanes,d|=Qo,D(e,s,d,g,j,C),e===Ht&&(ot=Ht=null,mt=0),ji=a,ps=e,Ni=s,td=d,ad=c,lm=r,(a.subtreeFlags&10256)!==0||(a.flags&10256)!==0?(e.callbackNode=null,e.callbackPriority=0,Y0(It,function(){return Nm(),null})):(e.callbackNode=null,e.callbackPriority=0),r=(a.flags&13878)!==0,(a.subtreeFlags&13878)!==0||r){r=L.T,L.T=null,c=ne.p,ne.p=2,g=Ct,Ct|=4;try{D0(e,a,s)}finally{Ct=g,ne.p=c,L.T=r}}Na=1,vm(),ym(),bm()}}function vm(){if(Na===1){Na=0;var e=ps,a=ji,s=(a.flags&13878)!==0;if((a.subtreeFlags&13878)!==0||s){s=L.T,L.T=null;var r=ne.p;ne.p=2;var c=Ct;Ct|=4;try{em(a,e);var d=vd,g=rf(e.containerInfo),j=d.focusedElem,C=d.selectionRange;if(g!==j&&j&&j.ownerDocument&&sf(j.ownerDocument.documentElement,j)){if(C!==null&&Go(j)){var q=C.start,X=C.end;if(X===void 0&&(X=q),"selectionStart"in j)j.selectionStart=q,j.selectionEnd=Math.min(X,j.value.length);else{var te=j.ownerDocument||document,H=te&&te.defaultView||window;if(H.getSelection){var I=H.getSelection(),Je=j.textContent.length,Ye=Math.min(C.start,Je),Rt=C.end===void 0?Ye:Math.min(C.end,Je);!I.extend&&Ye>Rt&&(g=Rt,Rt=Ye,Ye=g);var R=nf(j,Ye),E=nf(j,Rt);if(R&&E&&(I.rangeCount!==1||I.anchorNode!==R.node||I.anchorOffset!==R.offset||I.focusNode!==E.node||I.focusOffset!==E.offset)){var O=te.createRange();O.setStart(R.node,R.offset),I.removeAllRanges(),Ye>Rt?(I.addRange(O),I.extend(E.node,E.offset)):(O.setEnd(E.node,E.offset),I.addRange(O))}}}}for(te=[],I=j;I=I.parentNode;)I.nodeType===1&&te.push({element:I,left:I.scrollLeft,top:I.scrollTop});for(typeof j.focus=="function"&&j.focus(),j=0;j<te.length;j++){var J=te[j];J.element.scrollLeft=J.left,J.element.scrollTop=J.top}}Wl=!!xd,vd=xd=null}finally{Ct=c,ne.p=r,L.T=s}}e.current=a,Na=2}}function ym(){if(Na===2){Na=0;var e=ps,a=ji,s=(a.flags&8772)!==0;if((a.subtreeFlags&8772)!==0||s){s=L.T,L.T=null;var r=ne.p;ne.p=2;var c=Ct;Ct|=4;try{Qh(e,a.alternate,a)}finally{Ct=c,ne.p=r,L.T=s}}Na=3}}function bm(){if(Na===4||Na===3){Na=0,it();var e=ps,a=ji,s=Ni,r=lm;(a.subtreeFlags&10256)!==0||(a.flags&10256)!==0?Na=5:(Na=0,ji=ps=null,jm(e,e.pendingLanes));var c=e.pendingLanes;if(c===0&&(ms=null),ht(s),a=a.stateNode,Re&&typeof Re.onCommitFiberRoot=="function")try{Re.onCommitFiberRoot(Ne,a,void 0,(a.current.flags&128)===128)}catch{}if(r!==null){a=L.T,c=ne.p,ne.p=2,L.T=null;try{for(var d=e.onRecoverableError,g=0;g<r.length;g++){var j=r[g];d(j.value,{componentStack:j.stack})}}finally{L.T=a,ne.p=c}}(Ni&3)!==0&&Il(),jn(e),c=e.pendingLanes,(s&4194090)!==0&&(c&42)!==0?e===nd?jr++:(jr=0,nd=e):jr=0,Nr(0)}}function jm(e,a){(e.pooledCacheLanes&=a)===0&&(a=e.pooledCache,a!=null&&(e.pooledCache=null,tr(a)))}function Il(e){return vm(),ym(),bm(),Nm()}function Nm(){if(Na!==5)return!1;var e=ps,a=td;td=0;var s=ht(Ni),r=L.T,c=ne.p;try{ne.p=32>s?32:s,L.T=null,s=ad,ad=null;var d=ps,g=Ni;if(Na=0,ji=ps=null,Ni=0,(Ct&6)!==0)throw Error(o(331));var j=Ct;if(Ct|=4,im(d.current),am(d,d.current,g,s),Ct=j,Nr(0,!1),Re&&typeof Re.onPostCommitFiberRoot=="function")try{Re.onPostCommitFiberRoot(Ne,d)}catch{}return!0}finally{ne.p=c,L.T=r,jm(e,a)}}function wm(e,a,s){a=Ka(s,a),a=Uc(e.stateNode,a,2),e=is(e,a,2),e!==null&&(We(e,2),jn(e))}function Lt(e,a,s){if(e.tag===3)wm(e,e,s);else for(;a!==null;){if(a.tag===3){wm(a,e,s);break}else if(a.tag===1){var r=a.stateNode;if(typeof a.type.getDerivedStateFromError=="function"||typeof r.componentDidCatch=="function"&&(ms===null||!ms.has(r))){e=Ka(s,e),s=Ch(2),r=is(a,s,2),r!==null&&(Ah(s,r,a,e),We(r,2),jn(r));break}}a=a.return}}function ld(e,a,s){var r=e.pingCache;if(r===null){r=e.pingCache=new O0;var c=new Set;r.set(a,c)}else c=r.get(a),c===void 0&&(c=new Set,r.set(a,c));c.has(s)||(Jc=!0,c.add(s),e=I0.bind(null,e,a,s),a.then(e,e))}function I0(e,a,s){var r=e.pingCache;r!==null&&r.delete(a),e.pingedLanes|=e.suspendedLanes&s,e.warmLanes&=~s,Ht===e&&(mt&s)===s&&(Jt===4||Jt===3&&(mt&62914560)===mt&&300>et()-ed?(Ct&2)===0&&wi(e,0):Kc|=s,bi===mt&&(bi=0)),jn(e)}function _m(e,a){a===0&&(a=_t()),e=ii(e,a),e!==null&&(We(e,a),jn(e))}function $0(e){var a=e.memoizedState,s=0;a!==null&&(s=a.retryLane),_m(e,s)}function F0(e,a){var s=0;switch(e.tag){case 13:var r=e.stateNode,c=e.memoizedState;c!==null&&(s=c.retryLane);break;case 19:r=e.stateNode;break;case 22:r=e.stateNode._retryCache;break;default:throw Error(o(314))}r!==null&&r.delete(a),_m(e,s)}function Y0(e,a){return ue(e,a)}var $l=null,Si=null,od=!1,Fl=!1,cd=!1,$s=0;function jn(e){e!==Si&&e.next===null&&(Si===null?$l=Si=e:Si=Si.next=e),Fl=!0,od||(od=!0,P0())}function Nr(e,a){if(!cd&&Fl){cd=!0;do for(var s=!1,r=$l;r!==null;){if(e!==0){var c=r.pendingLanes;if(c===0)var d=0;else{var g=r.suspendedLanes,j=r.pingedLanes;d=(1<<31-ft(42|e)+1)-1,d&=c&~(g&~j),d=d&201326741?d&201326741|1:d?d|2:0}d!==0&&(s=!0,Am(r,d))}else d=mt,d=Ge(r,r===Ht?d:0,r.cancelPendingCommit!==null||r.timeoutHandle!==-1),(d&3)===0||tt(r,d)||(s=!0,Am(r,d));r=r.next}while(s);cd=!1}}function G0(){Sm()}function Sm(){Fl=od=!1;var e=0;$s!==0&&(ev()&&(e=$s),$s=0);for(var a=et(),s=null,r=$l;r!==null;){var c=r.next,d=Tm(r,a);d===0?(r.next=null,s===null?$l=c:s.next=c,c===null&&(Si=s)):(s=r,(e!==0||(d&3)!==0)&&(Fl=!0)),r=c}Nr(e)}function Tm(e,a){for(var s=e.suspendedLanes,r=e.pingedLanes,c=e.expirationTimes,d=e.pendingLanes&-62914561;0<d;){var g=31-ft(d),j=1<<g,C=c[g];C===-1?((j&s)===0||(j&r)!==0)&&(c[g]=ae(j,a)):C<=a&&(e.expiredLanes|=j),d&=~j}if(a=Ht,s=mt,s=Ge(e,e===a?s:0,e.cancelPendingCommit!==null||e.timeoutHandle!==-1),r=e.callbackNode,s===0||e===a&&(At===2||At===9)||e.cancelPendingCommit!==null)return r!==null&&r!==null&&Se(r),e.callbackNode=null,e.callbackPriority=0;if((s&3)===0||tt(e,s)){if(a=s&-s,a===e.callbackPriority)return a;switch(r!==null&&Se(r),ht(s)){case 2:case 8:s=Tt;break;case 32:s=It;break;case 268435456:s=G;break;default:s=It}return r=Cm.bind(null,e),s=ue(s,r),e.callbackPriority=a,e.callbackNode=s,a}return r!==null&&r!==null&&Se(r),e.callbackPriority=2,e.callbackNode=null,2}function Cm(e,a){if(Na!==0&&Na!==5)return e.callbackNode=null,e.callbackPriority=0,null;var s=e.callbackNode;if(Il()&&e.callbackNode!==s)return null;var r=mt;return r=Ge(e,e===Ht?r:0,e.cancelPendingCommit!==null||e.timeoutHandle!==-1),r===0?null:(cm(e,r,a),Tm(e,et()),e.callbackNode!=null&&e.callbackNode===s?Cm.bind(null,e):null)}function Am(e,a){if(Il())return null;cm(e,a,!0)}function P0(){av(function(){(Ct&6)!==0?ue(wt,G0):Sm()})}function dd(){return $s===0&&($s=Ot()),$s}function zm(e){return e==null||typeof e=="symbol"||typeof e=="boolean"?null:typeof e=="function"?e:Me(""+e)}function km(e,a){var s=a.ownerDocument.createElement("input");return s.name=a.name,s.value=a.value,e.id&&s.setAttribute("form",e.id),a.parentNode.insertBefore(s,a),e=new FormData(e),s.parentNode.removeChild(s),e}function V0(e,a,s,r,c){if(a==="submit"&&s&&s.stateNode===c){var d=zm((c[Pe]||null).action),g=r.submitter;g&&(a=(a=g[Pe]||null)?zm(a.formAction):g.getAttribute("formAction"),a!==null&&(d=a,g=null));var j=new sl("action","action",null,r,c);e.push({event:j,listeners:[{instance:null,listener:function(){if(r.defaultPrevented){if($s!==0){var C=g?km(c,g):new FormData(c);kc(s,{pending:!0,data:C,method:c.method,action:d},null,C)}}else typeof d=="function"&&(j.preventDefault(),C=g?km(c,g):new FormData(c),kc(s,{pending:!0,data:C,method:c.method,action:d},d,C))},currentTarget:c}]})}}for(var ud=0;ud<Zo.length;ud++){var fd=Zo[ud],X0=fd.toLowerCase(),Z0=fd[0].toUpperCase()+fd.slice(1);cn(X0,"on"+Z0)}cn(cf,"onAnimationEnd"),cn(df,"onAnimationIteration"),cn(uf,"onAnimationStart"),cn("dblclick","onDoubleClick"),cn("focusin","onFocus"),cn("focusout","onBlur"),cn(f0,"onTransitionRun"),cn(h0,"onTransitionStart"),cn(m0,"onTransitionCancel"),cn(ff,"onTransitionEnd"),Qa("onMouseEnter",["mouseout","mouseover"]),Qa("onMouseLeave",["mouseout","mouseover"]),Qa("onPointerEnter",["pointerout","pointerover"]),Qa("onPointerLeave",["pointerout","pointerover"]),_a("onChange","change click focusin focusout input keydown keyup selectionchange".split(" ")),_a("onSelect","focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" ")),_a("onBeforeInput",["compositionend","keypress","textInput","paste"]),_a("onCompositionEnd","compositionend focusout keydown keypress keyup mousedown".split(" ")),_a("onCompositionStart","compositionstart focusout keydown keypress keyup mousedown".split(" ")),_a("onCompositionUpdate","compositionupdate focusout keydown keypress keyup mousedown".split(" "));var wr="abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "),Q0=new Set("beforetoggle cancel close invalid load scroll scrollend toggle".split(" ").concat(wr));function Em(e,a){a=(a&4)!==0;for(var s=0;s<e.length;s++){var r=e[s],c=r.event;r=r.listeners;e:{var d=void 0;if(a)for(var g=r.length-1;0<=g;g--){var j=r[g],C=j.instance,q=j.currentTarget;if(j=j.listener,C!==d&&c.isPropagationStopped())break e;d=j,c.currentTarget=q;try{d(c)}catch(X){kl(X)}c.currentTarget=null,d=C}else for(g=0;g<r.length;g++){if(j=r[g],C=j.instance,q=j.currentTarget,j=j.listener,C!==d&&c.isPropagationStopped())break e;d=j,c.currentTarget=q;try{d(c)}catch(X){kl(X)}c.currentTarget=null,d=C}}}}function ct(e,a){var s=a[Et];s===void 0&&(s=a[Et]=new Set);var r=e+"__bubble";s.has(r)||(Mm(a,e,2,!1),s.add(r))}function hd(e,a,s){var r=0;a&&(r|=4),Mm(s,e,r,a)}var Yl="_reactListening"+Math.random().toString(36).slice(2);function md(e){if(!e[Yl]){e[Yl]=!0,xa.forEach(function(s){s!=="selectionchange"&&(Q0.has(s)||hd(s,!1,e),hd(s,!0,e))});var a=e.nodeType===9?e:e.ownerDocument;a===null||a[Yl]||(a[Yl]=!0,hd("selectionchange",!1,a))}}function Mm(e,a,s,r){switch(ap(a)){case 2:var c=wv;break;case 8:c=_v;break;default:c=Ad}s=c.bind(null,a,s,e),c=void 0,!Fi||a!=="touchstart"&&a!=="touchmove"&&a!=="wheel"||(c=!0),r?c!==void 0?e.addEventListener(a,s,{capture:!0,passive:c}):e.addEventListener(a,s,!0):c!==void 0?e.addEventListener(a,s,{passive:c}):e.addEventListener(a,s,!1)}function pd(e,a,s,r,c){var d=r;if((a&1)===0&&(a&2)===0&&r!==null)e:for(;;){if(r===null)return;var g=r.tag;if(g===3||g===4){var j=r.stateNode.containerInfo;if(j===c)break;if(g===4)for(g=r.return;g!==null;){var C=g.tag;if((C===3||C===4)&&g.stateNode.containerInfo===c)return;g=g.return}for(;j!==null;){if(g=Da(j),g===null)return;if(C=g.tag,C===5||C===6||C===26||C===27){r=d=g;continue e}j=j.parentNode}}r=r.return}Vt(function(){var q=d,X=Ie(s),te=[];e:{var H=hf.get(e);if(H!==void 0){var I=sl,Je=e;switch(e){case"keypress":if(al(s)===0)break e;case"keydown":case"keyup":I=Yx;break;case"focusin":Je="focus",I=Ho;break;case"focusout":Je="blur",I=Ho;break;case"beforeblur":case"afterblur":I=Ho;break;case"click":if(s.button===2)break e;case"auxclick":case"dblclick":case"mousedown":case"mousemove":case"mouseup":case"mouseout":case"mouseover":case"contextmenu":I=Iu;break;case"drag":case"dragend":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"dragstart":case"drop":I=Mx;break;case"touchcancel":case"touchend":case"touchmove":case"touchstart":I=Vx;break;case cf:case df:case uf:I=Ux;break;case ff:I=Zx;break;case"scroll":case"scrollend":I=kx;break;case"wheel":I=Jx;break;case"copy":case"cut":case"paste":I=Lx;break;case"gotpointercapture":case"lostpointercapture":case"pointercancel":case"pointerdown":case"pointermove":case"pointerout":case"pointerover":case"pointerup":I=Fu;break;case"toggle":case"beforetoggle":I=Wx}var Ye=(a&4)!==0,Rt=!Ye&&(e==="scroll"||e==="scrollend"),R=Ye?H!==null?H+"Capture":null:H;Ye=[];for(var E=q,O;E!==null;){var J=E;if(O=J.stateNode,J=J.tag,J!==5&&J!==26&&J!==27||O===null||R===null||(J=Ca(E,R),J!=null&&Ye.push(_r(E,J,O))),Rt)break;E=E.return}0<Ye.length&&(H=new I(H,Je,null,s,X),te.push({event:H,listeners:Ye}))}}if((a&7)===0){e:{if(H=e==="mouseover"||e==="pointerover",I=e==="mouseout"||e==="pointerout",H&&s!==Qe&&(Je=s.relatedTarget||s.fromElement)&&(Da(Je)||Je[Wt]))break e;if((I||H)&&(H=X.window===X?X:(H=X.ownerDocument)?H.defaultView||H.parentWindow:window,I?(Je=s.relatedTarget||s.toElement,I=q,Je=Je?Da(Je):null,Je!==null&&(Rt=f(Je),Ye=Je.tag,Je!==Rt||Ye!==5&&Ye!==27&&Ye!==6)&&(Je=null)):(I=null,Je=q),I!==Je)){if(Ye=Iu,J="onMouseLeave",R="onMouseEnter",E="mouse",(e==="pointerout"||e==="pointerover")&&(Ye=Fu,J="onPointerLeave",R="onPointerEnter",E="pointer"),Rt=I==null?H:ia(I),O=Je==null?H:ia(Je),H=new Ye(J,E+"leave",I,s,X),H.target=Rt,H.relatedTarget=O,J=null,Da(X)===q&&(Ye=new Ye(R,E+"enter",Je,s,X),Ye.target=O,Ye.relatedTarget=Rt,J=Ye),Rt=J,I&&Je)t:{for(Ye=I,R=Je,E=0,O=Ye;O;O=Ti(O))E++;for(O=0,J=R;J;J=Ti(J))O++;for(;0<E-O;)Ye=Ti(Ye),E--;for(;0<O-E;)R=Ti(R),O--;for(;E--;){if(Ye===R||R!==null&&Ye===R.alternate)break t;Ye=Ti(Ye),R=Ti(R)}Ye=null}else Ye=null;I!==null&&Dm(te,H,I,Ye,!1),Je!==null&&Rt!==null&&Dm(te,Rt,Je,Ye,!0)}}e:{if(H=q?ia(q):window,I=H.nodeName&&H.nodeName.toLowerCase(),I==="select"||I==="input"&&H.type==="file")var Le=Ju;else if(Zu(H))if(Ku)Le=c0;else{Le=l0;var lt=r0}else I=H.nodeName,!I||I.toLowerCase()!=="input"||H.type!=="checkbox"&&H.type!=="radio"?q&&b(q.elementType)&&(Le=Ju):Le=o0;if(Le&&(Le=Le(e,q))){Qu(te,Le,s,X);break e}lt&&lt(e,H,q),e==="focusout"&&q&&H.type==="number"&&q.memoizedProps.value!=null&&Y(H,"number",H.value)}switch(lt=q?ia(q):window,e){case"focusin":(Zu(lt)||lt.contentEditable==="true")&&(ai=lt,Po=q,Qi=null);break;case"focusout":Qi=Po=ai=null;break;case"mousedown":Vo=!0;break;case"contextmenu":case"mouseup":case"dragend":Vo=!1,lf(te,s,X);break;case"selectionchange":if(u0)break;case"keydown":case"keyup":lf(te,s,X)}var He;if($o)e:{switch(e){case"compositionstart":var Xe="onCompositionStart";break e;case"compositionend":Xe="onCompositionEnd";break e;case"compositionupdate":Xe="onCompositionUpdate";break e}Xe=void 0}else ti?Vu(e,s)&&(Xe="onCompositionEnd"):e==="keydown"&&s.keyCode===229&&(Xe="onCompositionStart");Xe&&(Yu&&s.locale!=="ko"&&(ti||Xe!=="onCompositionStart"?Xe==="onCompositionEnd"&&ti&&(He=Bu()):(ba=X,Ia="value"in ba?ba.value:ba.textContent,ti=!0)),lt=Gl(q,Xe),0<lt.length&&(Xe=new $u(Xe,e,null,s,X),te.push({event:Xe,listeners:lt}),He?Xe.data=He:(He=Xu(s),He!==null&&(Xe.data=He)))),(He=t0?a0(e,s):n0(e,s))&&(Xe=Gl(q,"onBeforeInput"),0<Xe.length&&(lt=new $u("onBeforeInput","beforeinput",null,s,X),te.push({event:lt,listeners:Xe}),lt.data=He)),V0(te,e,q,s,X)}Em(te,a)})}function _r(e,a,s){return{instance:e,listener:a,currentTarget:s}}function Gl(e,a){for(var s=a+"Capture",r=[];e!==null;){var c=e,d=c.stateNode;if(c=c.tag,c!==5&&c!==26&&c!==27||d===null||(c=Ca(e,s),c!=null&&r.unshift(_r(e,c,d)),c=Ca(e,a),c!=null&&r.push(_r(e,c,d))),e.tag===3)return r;e=e.return}return[]}function Ti(e){if(e===null)return null;do e=e.return;while(e&&e.tag!==5&&e.tag!==27);return e||null}function Dm(e,a,s,r,c){for(var d=a._reactName,g=[];s!==null&&s!==r;){var j=s,C=j.alternate,q=j.stateNode;if(j=j.tag,C!==null&&C===r)break;j!==5&&j!==26&&j!==27||q===null||(C=q,c?(q=Ca(s,d),q!=null&&g.unshift(_r(s,q,C))):c||(q=Ca(s,d),q!=null&&g.push(_r(s,q,C)))),s=s.return}g.length!==0&&e.push({event:a,listeners:g})}var J0=/\r\n?/g,K0=/\u0000|\uFFFD/g;function Rm(e){return(typeof e=="string"?e:""+e).replace(J0,`
`).replace(K0,"")}function Um(e,a){return a=Rm(a),Rm(e)===a}function Pl(){}function Dt(e,a,s,r,c,d){switch(s){case"children":typeof r=="string"?a==="body"||a==="textarea"&&r===""||qe(e,r):(typeof r=="number"||typeof r=="bigint")&&a!=="body"&&qe(e,""+r);break;case"className":es(e,"class",r);break;case"tabIndex":es(e,"tabindex",r);break;case"dir":case"role":case"viewBox":case"width":case"height":es(e,s,r);break;case"style":Sa(e,r,d);break;case"data":if(a!=="object"){es(e,"data",r);break}case"src":case"href":if(r===""&&(a!=="a"||s!=="href")){e.removeAttribute(s);break}if(r==null||typeof r=="function"||typeof r=="symbol"||typeof r=="boolean"){e.removeAttribute(s);break}r=Me(""+r),e.setAttribute(s,r);break;case"action":case"formAction":if(typeof r=="function"){e.setAttribute(s,"javascript:throw new Error('A React form was unexpectedly submitted. If you called form.submit() manually, consider using form.requestSubmit() instead. If you\\'re trying to use event.stopPropagation() in a submit event handler, consider also calling event.preventDefault().')");break}else typeof d=="function"&&(s==="formAction"?(a!=="input"&&Dt(e,a,"name",c.name,c,null),Dt(e,a,"formEncType",c.formEncType,c,null),Dt(e,a,"formMethod",c.formMethod,c,null),Dt(e,a,"formTarget",c.formTarget,c,null)):(Dt(e,a,"encType",c.encType,c,null),Dt(e,a,"method",c.method,c,null),Dt(e,a,"target",c.target,c,null)));if(r==null||typeof r=="symbol"||typeof r=="boolean"){e.removeAttribute(s);break}r=Me(""+r),e.setAttribute(s,r);break;case"onClick":r!=null&&(e.onclick=Pl);break;case"onScroll":r!=null&&ct("scroll",e);break;case"onScrollEnd":r!=null&&ct("scrollend",e);break;case"dangerouslySetInnerHTML":if(r!=null){if(typeof r!="object"||!("__html"in r))throw Error(o(61));if(s=r.__html,s!=null){if(c.children!=null)throw Error(o(60));e.innerHTML=s}}break;case"multiple":e.multiple=r&&typeof r!="function"&&typeof r!="symbol";break;case"muted":e.muted=r&&typeof r!="function"&&typeof r!="symbol";break;case"suppressContentEditableWarning":case"suppressHydrationWarning":case"defaultValue":case"defaultChecked":case"innerHTML":case"ref":break;case"autoFocus":break;case"xlinkHref":if(r==null||typeof r=="function"||typeof r=="boolean"||typeof r=="symbol"){e.removeAttribute("xlink:href");break}s=Me(""+r),e.setAttributeNS("http://www.w3.org/1999/xlink","xlink:href",s);break;case"contentEditable":case"spellCheck":case"draggable":case"value":case"autoReverse":case"externalResourcesRequired":case"focusable":case"preserveAlpha":r!=null&&typeof r!="function"&&typeof r!="symbol"?e.setAttribute(s,""+r):e.removeAttribute(s);break;case"inert":case"allowFullScreen":case"async":case"autoPlay":case"controls":case"default":case"defer":case"disabled":case"disablePictureInPicture":case"disableRemotePlayback":case"formNoValidate":case"hidden":case"loop":case"noModule":case"noValidate":case"open":case"playsInline":case"readOnly":case"required":case"reversed":case"scoped":case"seamless":case"itemScope":r&&typeof r!="function"&&typeof r!="symbol"?e.setAttribute(s,""):e.removeAttribute(s);break;case"capture":case"download":r===!0?e.setAttribute(s,""):r!==!1&&r!=null&&typeof r!="function"&&typeof r!="symbol"?e.setAttribute(s,r):e.removeAttribute(s);break;case"cols":case"rows":case"size":case"span":r!=null&&typeof r!="function"&&typeof r!="symbol"&&!isNaN(r)&&1<=r?e.setAttribute(s,r):e.removeAttribute(s);break;case"rowSpan":case"start":r==null||typeof r=="function"||typeof r=="symbol"||isNaN(r)?e.removeAttribute(s):e.setAttribute(s,r);break;case"popover":ct("beforetoggle",e),ct("toggle",e),Sn(e,"popover",r);break;case"xlinkActuate":Ra(e,"http://www.w3.org/1999/xlink","xlink:actuate",r);break;case"xlinkArcrole":Ra(e,"http://www.w3.org/1999/xlink","xlink:arcrole",r);break;case"xlinkRole":Ra(e,"http://www.w3.org/1999/xlink","xlink:role",r);break;case"xlinkShow":Ra(e,"http://www.w3.org/1999/xlink","xlink:show",r);break;case"xlinkTitle":Ra(e,"http://www.w3.org/1999/xlink","xlink:title",r);break;case"xlinkType":Ra(e,"http://www.w3.org/1999/xlink","xlink:type",r);break;case"xmlBase":Ra(e,"http://www.w3.org/XML/1998/namespace","xml:base",r);break;case"xmlLang":Ra(e,"http://www.w3.org/XML/1998/namespace","xml:lang",r);break;case"xmlSpace":Ra(e,"http://www.w3.org/XML/1998/namespace","xml:space",r);break;case"is":Sn(e,"is",r);break;case"innerText":case"textContent":break;default:(!(2<s.length)||s[0]!=="o"&&s[0]!=="O"||s[1]!=="n"&&s[1]!=="N")&&(s=K.get(s)||s,Sn(e,s,r))}}function gd(e,a,s,r,c,d){switch(s){case"style":Sa(e,r,d);break;case"dangerouslySetInnerHTML":if(r!=null){if(typeof r!="object"||!("__html"in r))throw Error(o(61));if(s=r.__html,s!=null){if(c.children!=null)throw Error(o(60));e.innerHTML=s}}break;case"children":typeof r=="string"?qe(e,r):(typeof r=="number"||typeof r=="bigint")&&qe(e,""+r);break;case"onScroll":r!=null&&ct("scroll",e);break;case"onScrollEnd":r!=null&&ct("scrollend",e);break;case"onClick":r!=null&&(e.onclick=Pl);break;case"suppressContentEditableWarning":case"suppressHydrationWarning":case"innerHTML":case"ref":break;case"innerText":case"textContent":break;default:if(!ut.hasOwnProperty(s))e:{if(s[0]==="o"&&s[1]==="n"&&(c=s.endsWith("Capture"),a=s.slice(2,c?s.length-7:void 0),d=e[Pe]||null,d=d!=null?d[s]:null,typeof d=="function"&&e.removeEventListener(a,d,c),typeof r=="function")){typeof d!="function"&&d!==null&&(s in e?e[s]=null:e.hasAttribute(s)&&e.removeAttribute(s)),e.addEventListener(a,r,c);break e}s in e?e[s]=r:r===!0?e.setAttribute(s,""):Sn(e,s,r)}}}function wa(e,a,s){switch(a){case"div":case"span":case"svg":case"path":case"a":case"g":case"p":case"li":break;case"img":ct("error",e),ct("load",e);var r=!1,c=!1,d;for(d in s)if(s.hasOwnProperty(d)){var g=s[d];if(g!=null)switch(d){case"src":r=!0;break;case"srcSet":c=!0;break;case"children":case"dangerouslySetInnerHTML":throw Error(o(137,a));default:Dt(e,a,d,g,s,null)}}c&&Dt(e,a,"srcSet",s.srcSet,s,null),r&&Dt(e,a,"src",s.src,s,null);return;case"input":ct("invalid",e);var j=d=g=c=null,C=null,q=null;for(r in s)if(s.hasOwnProperty(r)){var X=s[r];if(X!=null)switch(r){case"name":c=X;break;case"type":g=X;break;case"checked":C=X;break;case"defaultChecked":q=X;break;case"value":d=X;break;case"defaultValue":j=X;break;case"children":case"dangerouslySetInnerHTML":if(X!=null)throw Error(o(137,a));break;default:Dt(e,a,r,X,s,null)}}_(e,d,j,C,q,g,c,!1),Ja(e);return;case"select":ct("invalid",e),r=g=d=null;for(c in s)if(s.hasOwnProperty(c)&&(j=s[c],j!=null))switch(c){case"value":d=j;break;case"defaultValue":g=j;break;case"multiple":r=j;default:Dt(e,a,c,j,s,null)}a=d,s=g,e.multiple=!!r,a!=null?Z(e,!!r,a,!1):s!=null&&Z(e,!!r,s,!0);return;case"textarea":ct("invalid",e),d=c=r=null;for(g in s)if(s.hasOwnProperty(g)&&(j=s[g],j!=null))switch(g){case"value":r=j;break;case"defaultValue":c=j;break;case"children":d=j;break;case"dangerouslySetInnerHTML":if(j!=null)throw Error(o(91));break;default:Dt(e,a,g,j,s,null)}Ve(e,r,c,d),Ja(e);return;case"option":for(C in s)if(s.hasOwnProperty(C)&&(r=s[C],r!=null))switch(C){case"selected":e.selected=r&&typeof r!="function"&&typeof r!="symbol";break;default:Dt(e,a,C,r,s,null)}return;case"dialog":ct("beforetoggle",e),ct("toggle",e),ct("cancel",e),ct("close",e);break;case"iframe":case"object":ct("load",e);break;case"video":case"audio":for(r=0;r<wr.length;r++)ct(wr[r],e);break;case"image":ct("error",e),ct("load",e);break;case"details":ct("toggle",e);break;case"embed":case"source":case"link":ct("error",e),ct("load",e);case"area":case"base":case"br":case"col":case"hr":case"keygen":case"meta":case"param":case"track":case"wbr":case"menuitem":for(q in s)if(s.hasOwnProperty(q)&&(r=s[q],r!=null))switch(q){case"children":case"dangerouslySetInnerHTML":throw Error(o(137,a));default:Dt(e,a,q,r,s,null)}return;default:if(b(a)){for(X in s)s.hasOwnProperty(X)&&(r=s[X],r!==void 0&&gd(e,a,X,r,s,void 0));return}}for(j in s)s.hasOwnProperty(j)&&(r=s[j],r!=null&&Dt(e,a,j,r,s,null))}function W0(e,a,s,r){switch(a){case"div":case"span":case"svg":case"path":case"a":case"g":case"p":case"li":break;case"input":var c=null,d=null,g=null,j=null,C=null,q=null,X=null;for(I in s){var te=s[I];if(s.hasOwnProperty(I)&&te!=null)switch(I){case"checked":break;case"value":break;case"defaultValue":C=te;default:r.hasOwnProperty(I)||Dt(e,a,I,null,r,te)}}for(var H in r){var I=r[H];if(te=s[H],r.hasOwnProperty(H)&&(I!=null||te!=null))switch(H){case"type":d=I;break;case"name":c=I;break;case"checked":q=I;break;case"defaultChecked":X=I;break;case"value":g=I;break;case"defaultValue":j=I;break;case"children":case"dangerouslySetInnerHTML":if(I!=null)throw Error(o(137,a));break;default:I!==te&&Dt(e,a,H,I,r,te)}}Ts(e,g,j,C,q,X,d,c);return;case"select":I=g=j=H=null;for(d in s)if(C=s[d],s.hasOwnProperty(d)&&C!=null)switch(d){case"value":break;case"multiple":I=C;default:r.hasOwnProperty(d)||Dt(e,a,d,null,r,C)}for(c in r)if(d=r[c],C=s[c],r.hasOwnProperty(c)&&(d!=null||C!=null))switch(c){case"value":H=d;break;case"defaultValue":j=d;break;case"multiple":g=d;default:d!==C&&Dt(e,a,c,d,r,C)}a=j,s=g,r=I,H!=null?Z(e,!!s,H,!1):!!r!=!!s&&(a!=null?Z(e,!!s,a,!0):Z(e,!!s,s?[]:"",!1));return;case"textarea":I=H=null;for(j in s)if(c=s[j],s.hasOwnProperty(j)&&c!=null&&!r.hasOwnProperty(j))switch(j){case"value":break;case"children":break;default:Dt(e,a,j,null,r,c)}for(g in r)if(c=r[g],d=s[g],r.hasOwnProperty(g)&&(c!=null||d!=null))switch(g){case"value":H=c;break;case"defaultValue":I=c;break;case"children":break;case"dangerouslySetInnerHTML":if(c!=null)throw Error(o(91));break;default:c!==d&&Dt(e,a,g,c,r,d)}be(e,H,I);return;case"option":for(var Je in s)if(H=s[Je],s.hasOwnProperty(Je)&&H!=null&&!r.hasOwnProperty(Je))switch(Je){case"selected":e.selected=!1;break;default:Dt(e,a,Je,null,r,H)}for(C in r)if(H=r[C],I=s[C],r.hasOwnProperty(C)&&H!==I&&(H!=null||I!=null))switch(C){case"selected":e.selected=H&&typeof H!="function"&&typeof H!="symbol";break;default:Dt(e,a,C,H,r,I)}return;case"img":case"link":case"area":case"base":case"br":case"col":case"embed":case"hr":case"keygen":case"meta":case"param":case"source":case"track":case"wbr":case"menuitem":for(var Ye in s)H=s[Ye],s.hasOwnProperty(Ye)&&H!=null&&!r.hasOwnProperty(Ye)&&Dt(e,a,Ye,null,r,H);for(q in r)if(H=r[q],I=s[q],r.hasOwnProperty(q)&&H!==I&&(H!=null||I!=null))switch(q){case"children":case"dangerouslySetInnerHTML":if(H!=null)throw Error(o(137,a));break;default:Dt(e,a,q,H,r,I)}return;default:if(b(a)){for(var Rt in s)H=s[Rt],s.hasOwnProperty(Rt)&&H!==void 0&&!r.hasOwnProperty(Rt)&&gd(e,a,Rt,void 0,r,H);for(X in r)H=r[X],I=s[X],!r.hasOwnProperty(X)||H===I||H===void 0&&I===void 0||gd(e,a,X,H,r,I);return}}for(var R in s)H=s[R],s.hasOwnProperty(R)&&H!=null&&!r.hasOwnProperty(R)&&Dt(e,a,R,null,r,H);for(te in r)H=r[te],I=s[te],!r.hasOwnProperty(te)||H===I||H==null&&I==null||Dt(e,a,te,H,r,I)}var xd=null,vd=null;function Vl(e){return e.nodeType===9?e:e.ownerDocument}function Om(e){switch(e){case"http://www.w3.org/2000/svg":return 1;case"http://www.w3.org/1998/Math/MathML":return 2;default:return 0}}function Lm(e,a){if(e===0)switch(a){case"svg":return 1;case"math":return 2;default:return 0}return e===1&&a==="foreignObject"?0:e}function yd(e,a){return e==="textarea"||e==="noscript"||typeof a.children=="string"||typeof a.children=="number"||typeof a.children=="bigint"||typeof a.dangerouslySetInnerHTML=="object"&&a.dangerouslySetInnerHTML!==null&&a.dangerouslySetInnerHTML.__html!=null}var bd=null;function ev(){var e=window.event;return e&&e.type==="popstate"?e===bd?!1:(bd=e,!0):(bd=null,!1)}var qm=typeof setTimeout=="function"?setTimeout:void 0,tv=typeof clearTimeout=="function"?clearTimeout:void 0,Bm=typeof Promise=="function"?Promise:void 0,av=typeof queueMicrotask=="function"?queueMicrotask:typeof Bm<"u"?function(e){return Bm.resolve(null).then(e).catch(nv)}:qm;function nv(e){setTimeout(function(){throw e})}function xs(e){return e==="head"}function Hm(e,a){var s=a,r=0,c=0;do{var d=s.nextSibling;if(e.removeChild(s),d&&d.nodeType===8)if(s=d.data,s==="/$"){if(0<r&&8>r){s=r;var g=e.ownerDocument;if(s&1&&Sr(g.documentElement),s&2&&Sr(g.body),s&4)for(s=g.head,Sr(s),g=s.firstChild;g;){var j=g.nextSibling,C=g.nodeName;g[da]||C==="SCRIPT"||C==="STYLE"||C==="LINK"&&g.rel.toLowerCase()==="stylesheet"||s.removeChild(g),g=j}}if(c===0){e.removeChild(d),Dr(a);return}c--}else s==="$"||s==="$?"||s==="$!"?c++:r=s.charCodeAt(0)-48;else r=0;s=d}while(s);Dr(a)}function jd(e){var a=e.firstChild;for(a&&a.nodeType===10&&(a=a.nextSibling);a;){var s=a;switch(a=a.nextSibling,s.nodeName){case"HTML":case"HEAD":case"BODY":jd(s),Za(s);continue;case"SCRIPT":case"STYLE":continue;case"LINK":if(s.rel.toLowerCase()==="stylesheet")continue}e.removeChild(s)}}function sv(e,a,s,r){for(;e.nodeType===1;){var c=s;if(e.nodeName.toLowerCase()!==a.toLowerCase()){if(!r&&(e.nodeName!=="INPUT"||e.type!=="hidden"))break}else if(r){if(!e[da])switch(a){case"meta":if(!e.hasAttribute("itemprop"))break;return e;case"link":if(d=e.getAttribute("rel"),d==="stylesheet"&&e.hasAttribute("data-precedence"))break;if(d!==c.rel||e.getAttribute("href")!==(c.href==null||c.href===""?null:c.href)||e.getAttribute("crossorigin")!==(c.crossOrigin==null?null:c.crossOrigin)||e.getAttribute("title")!==(c.title==null?null:c.title))break;return e;case"style":if(e.hasAttribute("data-precedence"))break;return e;case"script":if(d=e.getAttribute("src"),(d!==(c.src==null?null:c.src)||e.getAttribute("type")!==(c.type==null?null:c.type)||e.getAttribute("crossorigin")!==(c.crossOrigin==null?null:c.crossOrigin))&&d&&e.hasAttribute("async")&&!e.hasAttribute("itemprop"))break;return e;default:return e}}else if(a==="input"&&e.type==="hidden"){var d=c.name==null?null:""+c.name;if(c.type==="hidden"&&e.getAttribute("name")===d)return e}else return e;if(e=un(e.nextSibling),e===null)break}return null}function iv(e,a,s){if(a==="")return null;for(;e.nodeType!==3;)if((e.nodeType!==1||e.nodeName!=="INPUT"||e.type!=="hidden")&&!s||(e=un(e.nextSibling),e===null))return null;return e}function Nd(e){return e.data==="$!"||e.data==="$?"&&e.ownerDocument.readyState==="complete"}function rv(e,a){var s=e.ownerDocument;if(e.data!=="$?"||s.readyState==="complete")a();else{var r=function(){a(),s.removeEventListener("DOMContentLoaded",r)};s.addEventListener("DOMContentLoaded",r),e._reactRetry=r}}function un(e){for(;e!=null;e=e.nextSibling){var a=e.nodeType;if(a===1||a===3)break;if(a===8){if(a=e.data,a==="$"||a==="$!"||a==="$?"||a==="F!"||a==="F")break;if(a==="/$")return null}}return e}var wd=null;function Im(e){e=e.previousSibling;for(var a=0;e;){if(e.nodeType===8){var s=e.data;if(s==="$"||s==="$!"||s==="$?"){if(a===0)return e;a--}else s==="/$"&&a++}e=e.previousSibling}return null}function $m(e,a,s){switch(a=Vl(s),e){case"html":if(e=a.documentElement,!e)throw Error(o(452));return e;case"head":if(e=a.head,!e)throw Error(o(453));return e;case"body":if(e=a.body,!e)throw Error(o(454));return e;default:throw Error(o(451))}}function Sr(e){for(var a=e.attributes;a.length;)e.removeAttributeNode(a[0]);Za(e)}var sn=new Map,Fm=new Set;function Xl(e){return typeof e.getRootNode=="function"?e.getRootNode():e.nodeType===9?e:e.ownerDocument}var Yn=ne.d;ne.d={f:lv,r:ov,D:cv,C:dv,L:uv,m:fv,X:mv,S:hv,M:pv};function lv(){var e=Yn.f(),a=Bl();return e||a}function ov(e){var a=Ha(e);a!==null&&a.tag===5&&a.type==="form"?ch(a):Yn.r(e)}var Ci=typeof document>"u"?null:document;function Ym(e,a,s){var r=Ci;if(r&&typeof a=="string"&&a){var c=Ft(a);c='link[rel="'+e+'"][href="'+c+'"]',typeof s=="string"&&(c+='[crossorigin="'+s+'"]'),Fm.has(c)||(Fm.add(c),e={rel:e,crossOrigin:s,href:a},r.querySelector(c)===null&&(a=r.createElement("link"),wa(a,"link",e),pt(a),r.head.appendChild(a)))}}function cv(e){Yn.D(e),Ym("dns-prefetch",e,null)}function dv(e,a){Yn.C(e,a),Ym("preconnect",e,a)}function uv(e,a,s){Yn.L(e,a,s);var r=Ci;if(r&&e&&a){var c='link[rel="preload"][as="'+Ft(a)+'"]';a==="image"&&s&&s.imageSrcSet?(c+='[imagesrcset="'+Ft(s.imageSrcSet)+'"]',typeof s.imageSizes=="string"&&(c+='[imagesizes="'+Ft(s.imageSizes)+'"]')):c+='[href="'+Ft(e)+'"]';var d=c;switch(a){case"style":d=Ai(e);break;case"script":d=zi(e)}sn.has(d)||(e=v({rel:"preload",href:a==="image"&&s&&s.imageSrcSet?void 0:e,as:a},s),sn.set(d,e),r.querySelector(c)!==null||a==="style"&&r.querySelector(Tr(d))||a==="script"&&r.querySelector(Cr(d))||(a=r.createElement("link"),wa(a,"link",e),pt(a),r.head.appendChild(a)))}}function fv(e,a){Yn.m(e,a);var s=Ci;if(s&&e){var r=a&&typeof a.as=="string"?a.as:"script",c='link[rel="modulepreload"][as="'+Ft(r)+'"][href="'+Ft(e)+'"]',d=c;switch(r){case"audioworklet":case"paintworklet":case"serviceworker":case"sharedworker":case"worker":case"script":d=zi(e)}if(!sn.has(d)&&(e=v({rel:"modulepreload",href:e},a),sn.set(d,e),s.querySelector(c)===null)){switch(r){case"audioworklet":case"paintworklet":case"serviceworker":case"sharedworker":case"worker":case"script":if(s.querySelector(Cr(d)))return}r=s.createElement("link"),wa(r,"link",e),pt(r),s.head.appendChild(r)}}}function hv(e,a,s){Yn.S(e,a,s);var r=Ci;if(r&&e){var c=ka(r).hoistableStyles,d=Ai(e);a=a||"default";var g=c.get(d);if(!g){var j={loading:0,preload:null};if(g=r.querySelector(Tr(d)))j.loading=5;else{e=v({rel:"stylesheet",href:e,"data-precedence":a},s),(s=sn.get(d))&&_d(e,s);var C=g=r.createElement("link");pt(C),wa(C,"link",e),C._p=new Promise(function(q,X){C.onload=q,C.onerror=X}),C.addEventListener("load",function(){j.loading|=1}),C.addEventListener("error",function(){j.loading|=2}),j.loading|=4,Zl(g,a,r)}g={type:"stylesheet",instance:g,count:1,state:j},c.set(d,g)}}}function mv(e,a){Yn.X(e,a);var s=Ci;if(s&&e){var r=ka(s).hoistableScripts,c=zi(e),d=r.get(c);d||(d=s.querySelector(Cr(c)),d||(e=v({src:e,async:!0},a),(a=sn.get(c))&&Sd(e,a),d=s.createElement("script"),pt(d),wa(d,"link",e),s.head.appendChild(d)),d={type:"script",instance:d,count:1,state:null},r.set(c,d))}}function pv(e,a){Yn.M(e,a);var s=Ci;if(s&&e){var r=ka(s).hoistableScripts,c=zi(e),d=r.get(c);d||(d=s.querySelector(Cr(c)),d||(e=v({src:e,async:!0,type:"module"},a),(a=sn.get(c))&&Sd(e,a),d=s.createElement("script"),pt(d),wa(d,"link",e),s.head.appendChild(d)),d={type:"script",instance:d,count:1,state:null},r.set(c,d))}}function Gm(e,a,s,r){var c=(c=ve.current)?Xl(c):null;if(!c)throw Error(o(446));switch(e){case"meta":case"title":return null;case"style":return typeof s.precedence=="string"&&typeof s.href=="string"?(a=Ai(s.href),s=ka(c).hoistableStyles,r=s.get(a),r||(r={type:"style",instance:null,count:0,state:null},s.set(a,r)),r):{type:"void",instance:null,count:0,state:null};case"link":if(s.rel==="stylesheet"&&typeof s.href=="string"&&typeof s.precedence=="string"){e=Ai(s.href);var d=ka(c).hoistableStyles,g=d.get(e);if(g||(c=c.ownerDocument||c,g={type:"stylesheet",instance:null,count:0,state:{loading:0,preload:null}},d.set(e,g),(d=c.querySelector(Tr(e)))&&!d._p&&(g.instance=d,g.state.loading=5),sn.has(e)||(s={rel:"preload",as:"style",href:s.href,crossOrigin:s.crossOrigin,integrity:s.integrity,media:s.media,hrefLang:s.hrefLang,referrerPolicy:s.referrerPolicy},sn.set(e,s),d||gv(c,e,s,g.state))),a&&r===null)throw Error(o(528,""));return g}if(a&&r!==null)throw Error(o(529,""));return null;case"script":return a=s.async,s=s.src,typeof s=="string"&&a&&typeof a!="function"&&typeof a!="symbol"?(a=zi(s),s=ka(c).hoistableScripts,r=s.get(a),r||(r={type:"script",instance:null,count:0,state:null},s.set(a,r)),r):{type:"void",instance:null,count:0,state:null};default:throw Error(o(444,e))}}function Ai(e){return'href="'+Ft(e)+'"'}function Tr(e){return'link[rel="stylesheet"]['+e+"]"}function Pm(e){return v({},e,{"data-precedence":e.precedence,precedence:null})}function gv(e,a,s,r){e.querySelector('link[rel="preload"][as="style"]['+a+"]")?r.loading=1:(a=e.createElement("link"),r.preload=a,a.addEventListener("load",function(){return r.loading|=1}),a.addEventListener("error",function(){return r.loading|=2}),wa(a,"link",s),pt(a),e.head.appendChild(a))}function zi(e){return'[src="'+Ft(e)+'"]'}function Cr(e){return"script[async]"+e}function Vm(e,a,s){if(a.count++,a.instance===null)switch(a.type){case"style":var r=e.querySelector('style[data-href~="'+Ft(s.href)+'"]');if(r)return a.instance=r,pt(r),r;var c=v({},s,{"data-href":s.href,"data-precedence":s.precedence,href:null,precedence:null});return r=(e.ownerDocument||e).createElement("style"),pt(r),wa(r,"style",c),Zl(r,s.precedence,e),a.instance=r;case"stylesheet":c=Ai(s.href);var d=e.querySelector(Tr(c));if(d)return a.state.loading|=4,a.instance=d,pt(d),d;r=Pm(s),(c=sn.get(c))&&_d(r,c),d=(e.ownerDocument||e).createElement("link"),pt(d);var g=d;return g._p=new Promise(function(j,C){g.onload=j,g.onerror=C}),wa(d,"link",r),a.state.loading|=4,Zl(d,s.precedence,e),a.instance=d;case"script":return d=zi(s.src),(c=e.querySelector(Cr(d)))?(a.instance=c,pt(c),c):(r=s,(c=sn.get(d))&&(r=v({},s),Sd(r,c)),e=e.ownerDocument||e,c=e.createElement("script"),pt(c),wa(c,"link",r),e.head.appendChild(c),a.instance=c);case"void":return null;default:throw Error(o(443,a.type))}else a.type==="stylesheet"&&(a.state.loading&4)===0&&(r=a.instance,a.state.loading|=4,Zl(r,s.precedence,e));return a.instance}function Zl(e,a,s){for(var r=s.querySelectorAll('link[rel="stylesheet"][data-precedence],style[data-precedence]'),c=r.length?r[r.length-1]:null,d=c,g=0;g<r.length;g++){var j=r[g];if(j.dataset.precedence===a)d=j;else if(d!==c)break}d?d.parentNode.insertBefore(e,d.nextSibling):(a=s.nodeType===9?s.head:s,a.insertBefore(e,a.firstChild))}function _d(e,a){e.crossOrigin==null&&(e.crossOrigin=a.crossOrigin),e.referrerPolicy==null&&(e.referrerPolicy=a.referrerPolicy),e.title==null&&(e.title=a.title)}function Sd(e,a){e.crossOrigin==null&&(e.crossOrigin=a.crossOrigin),e.referrerPolicy==null&&(e.referrerPolicy=a.referrerPolicy),e.integrity==null&&(e.integrity=a.integrity)}var Ql=null;function Xm(e,a,s){if(Ql===null){var r=new Map,c=Ql=new Map;c.set(s,r)}else c=Ql,r=c.get(s),r||(r=new Map,c.set(s,r));if(r.has(e))return r;for(r.set(e,null),s=s.getElementsByTagName(e),c=0;c<s.length;c++){var d=s[c];if(!(d[da]||d[Ee]||e==="link"&&d.getAttribute("rel")==="stylesheet")&&d.namespaceURI!=="http://www.w3.org/2000/svg"){var g=d.getAttribute(a)||"";g=e+g;var j=r.get(g);j?j.push(d):r.set(g,[d])}}return r}function Zm(e,a,s){e=e.ownerDocument||e,e.head.insertBefore(s,a==="title"?e.querySelector("head > title"):null)}function xv(e,a,s){if(s===1||a.itemProp!=null)return!1;switch(e){case"meta":case"title":return!0;case"style":if(typeof a.precedence!="string"||typeof a.href!="string"||a.href==="")break;return!0;case"link":if(typeof a.rel!="string"||typeof a.href!="string"||a.href===""||a.onLoad||a.onError)break;switch(a.rel){case"stylesheet":return e=a.disabled,typeof a.precedence=="string"&&e==null;default:return!0}case"script":if(a.async&&typeof a.async!="function"&&typeof a.async!="symbol"&&!a.onLoad&&!a.onError&&a.src&&typeof a.src=="string")return!0}return!1}function Qm(e){return!(e.type==="stylesheet"&&(e.state.loading&3)===0)}var Ar=null;function vv(){}function yv(e,a,s){if(Ar===null)throw Error(o(475));var r=Ar;if(a.type==="stylesheet"&&(typeof s.media!="string"||matchMedia(s.media).matches!==!1)&&(a.state.loading&4)===0){if(a.instance===null){var c=Ai(s.href),d=e.querySelector(Tr(c));if(d){e=d._p,e!==null&&typeof e=="object"&&typeof e.then=="function"&&(r.count++,r=Jl.bind(r),e.then(r,r)),a.state.loading|=4,a.instance=d,pt(d);return}d=e.ownerDocument||e,s=Pm(s),(c=sn.get(c))&&_d(s,c),d=d.createElement("link"),pt(d);var g=d;g._p=new Promise(function(j,C){g.onload=j,g.onerror=C}),wa(d,"link",s),a.instance=d}r.stylesheets===null&&(r.stylesheets=new Map),r.stylesheets.set(a,e),(e=a.state.preload)&&(a.state.loading&3)===0&&(r.count++,a=Jl.bind(r),e.addEventListener("load",a),e.addEventListener("error",a))}}function bv(){if(Ar===null)throw Error(o(475));var e=Ar;return e.stylesheets&&e.count===0&&Td(e,e.stylesheets),0<e.count?function(a){var s=setTimeout(function(){if(e.stylesheets&&Td(e,e.stylesheets),e.unsuspend){var r=e.unsuspend;e.unsuspend=null,r()}},6e4);return e.unsuspend=a,function(){e.unsuspend=null,clearTimeout(s)}}:null}function Jl(){if(this.count--,this.count===0){if(this.stylesheets)Td(this,this.stylesheets);else if(this.unsuspend){var e=this.unsuspend;this.unsuspend=null,e()}}}var Kl=null;function Td(e,a){e.stylesheets=null,e.unsuspend!==null&&(e.count++,Kl=new Map,a.forEach(jv,e),Kl=null,Jl.call(e))}function jv(e,a){if(!(a.state.loading&4)){var s=Kl.get(e);if(s)var r=s.get(null);else{s=new Map,Kl.set(e,s);for(var c=e.querySelectorAll("link[data-precedence],style[data-precedence]"),d=0;d<c.length;d++){var g=c[d];(g.nodeName==="LINK"||g.getAttribute("media")!=="not all")&&(s.set(g.dataset.precedence,g),r=g)}r&&s.set(null,r)}c=a.instance,g=c.getAttribute("data-precedence"),d=s.get(g)||r,d===r&&s.set(null,c),s.set(g,c),this.count++,r=Jl.bind(this),c.addEventListener("load",r),c.addEventListener("error",r),d?d.parentNode.insertBefore(c,d.nextSibling):(e=e.nodeType===9?e.head:e,e.insertBefore(c,e.firstChild)),a.state.loading|=4}}var zr={$$typeof:me,Provider:null,Consumer:null,_currentValue:P,_currentValue2:P,_threadCount:0};function Nv(e,a,s,r,c,d,g,j){this.tag=1,this.containerInfo=e,this.pingCache=this.current=this.pendingChildren=null,this.timeoutHandle=-1,this.callbackNode=this.next=this.pendingContext=this.context=this.cancelPendingCommit=null,this.callbackPriority=0,this.expirationTimes=_e(-1),this.entangledLanes=this.shellSuspendCounter=this.errorRecoveryDisabledLanes=this.expiredLanes=this.warmLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0,this.entanglements=_e(0),this.hiddenUpdates=_e(null),this.identifierPrefix=r,this.onUncaughtError=c,this.onCaughtError=d,this.onRecoverableError=g,this.pooledCache=null,this.pooledCacheLanes=0,this.formState=j,this.incompleteTransitions=new Map}function Jm(e,a,s,r,c,d,g,j,C,q,X,te){return e=new Nv(e,a,s,g,j,C,q,te),a=1,d===!0&&(a|=24),d=Fa(3,null,null,a),e.current=d,d.stateNode=e,a=lc(),a.refCount++,e.pooledCache=a,a.refCount++,d.memoizedState={element:r,isDehydrated:s,cache:a},uc(d),e}function Km(e){return e?(e=ri,e):ri}function Wm(e,a,s,r,c,d){c=Km(c),r.context===null?r.context=c:r.pendingContext=c,r=ss(a),r.payload={element:s},d=d===void 0?null:d,d!==null&&(r.callback=d),s=is(e,r,a),s!==null&&(Xa(s,e,a),ir(s,e,a))}function ep(e,a){if(e=e.memoizedState,e!==null&&e.dehydrated!==null){var s=e.retryLane;e.retryLane=s!==0&&s<a?s:a}}function Cd(e,a){ep(e,a),(e=e.alternate)&&ep(e,a)}function tp(e){if(e.tag===13){var a=ii(e,67108864);a!==null&&Xa(a,e,67108864),Cd(e,67108864)}}var Wl=!0;function wv(e,a,s,r){var c=L.T;L.T=null;var d=ne.p;try{ne.p=2,Ad(e,a,s,r)}finally{ne.p=d,L.T=c}}function _v(e,a,s,r){var c=L.T;L.T=null;var d=ne.p;try{ne.p=8,Ad(e,a,s,r)}finally{ne.p=d,L.T=c}}function Ad(e,a,s,r){if(Wl){var c=zd(r);if(c===null)pd(e,a,r,eo,s),np(e,r);else if(Tv(c,e,a,s,r))r.stopPropagation();else if(np(e,r),a&4&&-1<Sv.indexOf(e)){for(;c!==null;){var d=Ha(c);if(d!==null)switch(d.tag){case 3:if(d=d.stateNode,d.current.memoizedState.isDehydrated){var g=ye(d.pendingLanes);if(g!==0){var j=d;for(j.pendingLanes|=2,j.entangledLanes|=2;g;){var C=1<<31-ft(g);j.entanglements[1]|=C,g&=~C}jn(d),(Ct&6)===0&&(Ll=et()+500,Nr(0))}}break;case 13:j=ii(d,2),j!==null&&Xa(j,d,2),Bl(),Cd(d,2)}if(d=zd(r),d===null&&pd(e,a,r,eo,s),d===c)break;c=d}c!==null&&r.stopPropagation()}else pd(e,a,r,null,s)}}function zd(e){return e=Ie(e),kd(e)}var eo=null;function kd(e){if(eo=null,e=Da(e),e!==null){var a=f(e);if(a===null)e=null;else{var s=a.tag;if(s===13){if(e=m(a),e!==null)return e;e=null}else if(s===3){if(a.stateNode.current.memoizedState.isDehydrated)return a.tag===3?a.stateNode.containerInfo:null;e=null}else a!==e&&(e=null)}}return eo=e,null}function ap(e){switch(e){case"beforetoggle":case"cancel":case"click":case"close":case"contextmenu":case"copy":case"cut":case"auxclick":case"dblclick":case"dragend":case"dragstart":case"drop":case"focusin":case"focusout":case"input":case"invalid":case"keydown":case"keypress":case"keyup":case"mousedown":case"mouseup":case"paste":case"pause":case"play":case"pointercancel":case"pointerdown":case"pointerup":case"ratechange":case"reset":case"resize":case"seeked":case"submit":case"toggle":case"touchcancel":case"touchend":case"touchstart":case"volumechange":case"change":case"selectionchange":case"textInput":case"compositionstart":case"compositionend":case"compositionupdate":case"beforeblur":case"afterblur":case"beforeinput":case"blur":case"fullscreenchange":case"focus":case"hashchange":case"popstate":case"select":case"selectstart":return 2;case"drag":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"mousemove":case"mouseout":case"mouseover":case"pointermove":case"pointerout":case"pointerover":case"scroll":case"touchmove":case"wheel":case"mouseenter":case"mouseleave":case"pointerenter":case"pointerleave":return 8;case"message":switch(Gt()){case wt:return 2;case Tt:return 8;case It:case Kt:return 32;case G:return 268435456;default:return 32}default:return 32}}var Ed=!1,vs=null,ys=null,bs=null,kr=new Map,Er=new Map,js=[],Sv="mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset".split(" ");function np(e,a){switch(e){case"focusin":case"focusout":vs=null;break;case"dragenter":case"dragleave":ys=null;break;case"mouseover":case"mouseout":bs=null;break;case"pointerover":case"pointerout":kr.delete(a.pointerId);break;case"gotpointercapture":case"lostpointercapture":Er.delete(a.pointerId)}}function Mr(e,a,s,r,c,d){return e===null||e.nativeEvent!==d?(e={blockedOn:a,domEventName:s,eventSystemFlags:r,nativeEvent:d,targetContainers:[c]},a!==null&&(a=Ha(a),a!==null&&tp(a)),e):(e.eventSystemFlags|=r,a=e.targetContainers,c!==null&&a.indexOf(c)===-1&&a.push(c),e)}function Tv(e,a,s,r,c){switch(a){case"focusin":return vs=Mr(vs,e,a,s,r,c),!0;case"dragenter":return ys=Mr(ys,e,a,s,r,c),!0;case"mouseover":return bs=Mr(bs,e,a,s,r,c),!0;case"pointerover":var d=c.pointerId;return kr.set(d,Mr(kr.get(d)||null,e,a,s,r,c)),!0;case"gotpointercapture":return d=c.pointerId,Er.set(d,Mr(Er.get(d)||null,e,a,s,r,c)),!0}return!1}function sp(e){var a=Da(e.target);if(a!==null){var s=f(a);if(s!==null){if(a=s.tag,a===13){if(a=m(s),a!==null){e.blockedOn=a,vt(e.priority,function(){if(s.tag===13){var r=Va();r=jt(r);var c=ii(s,r);c!==null&&Xa(c,s,r),Cd(s,r)}});return}}else if(a===3&&s.stateNode.current.memoizedState.isDehydrated){e.blockedOn=s.tag===3?s.stateNode.containerInfo:null;return}}}e.blockedOn=null}function to(e){if(e.blockedOn!==null)return!1;for(var a=e.targetContainers;0<a.length;){var s=zd(e.nativeEvent);if(s===null){s=e.nativeEvent;var r=new s.constructor(s.type,s);Qe=r,s.target.dispatchEvent(r),Qe=null}else return a=Ha(s),a!==null&&tp(a),e.blockedOn=s,!1;a.shift()}return!0}function ip(e,a,s){to(e)&&s.delete(a)}function Cv(){Ed=!1,vs!==null&&to(vs)&&(vs=null),ys!==null&&to(ys)&&(ys=null),bs!==null&&to(bs)&&(bs=null),kr.forEach(ip),Er.forEach(ip)}function ao(e,a){e.blockedOn===a&&(e.blockedOn=null,Ed||(Ed=!0,n.unstable_scheduleCallback(n.unstable_NormalPriority,Cv)))}var no=null;function rp(e){no!==e&&(no=e,n.unstable_scheduleCallback(n.unstable_NormalPriority,function(){no===e&&(no=null);for(var a=0;a<e.length;a+=3){var s=e[a],r=e[a+1],c=e[a+2];if(typeof r!="function"){if(kd(r||s)===null)continue;break}var d=Ha(s);d!==null&&(e.splice(a,3),a-=3,kc(d,{pending:!0,data:c,method:s.method,action:r},r,c))}}))}function Dr(e){function a(C){return ao(C,e)}vs!==null&&ao(vs,e),ys!==null&&ao(ys,e),bs!==null&&ao(bs,e),kr.forEach(a),Er.forEach(a);for(var s=0;s<js.length;s++){var r=js[s];r.blockedOn===e&&(r.blockedOn=null)}for(;0<js.length&&(s=js[0],s.blockedOn===null);)sp(s),s.blockedOn===null&&js.shift();if(s=(e.ownerDocument||e).$$reactFormReplay,s!=null)for(r=0;r<s.length;r+=3){var c=s[r],d=s[r+1],g=c[Pe]||null;if(typeof d=="function")g||rp(s);else if(g){var j=null;if(d&&d.hasAttribute("formAction")){if(c=d,g=d[Pe]||null)j=g.formAction;else if(kd(c)!==null)continue}else j=g.action;typeof j=="function"?s[r+1]=j:(s.splice(r,3),r-=3),rp(s)}}}function Md(e){this._internalRoot=e}so.prototype.render=Md.prototype.render=function(e){var a=this._internalRoot;if(a===null)throw Error(o(409));var s=a.current,r=Va();Wm(s,r,e,a,null,null)},so.prototype.unmount=Md.prototype.unmount=function(){var e=this._internalRoot;if(e!==null){this._internalRoot=null;var a=e.containerInfo;Wm(e.current,2,null,e,null,null),Bl(),a[Wt]=null}};function so(e){this._internalRoot=e}so.prototype.unstable_scheduleHydration=function(e){if(e){var a=kt();e={blockedOn:null,target:e,priority:a};for(var s=0;s<js.length&&a!==0&&a<js[s].priority;s++);js.splice(s,0,e),s===0&&sp(e)}};var lp=i.version;if(lp!=="19.1.1")throw Error(o(527,lp,"19.1.1"));ne.findDOMNode=function(e){var a=e._reactInternals;if(a===void 0)throw typeof e.render=="function"?Error(o(188)):(e=Object.keys(e).join(","),Error(o(268,e)));return e=p(a),e=e!==null?h(e):null,e=e===null?null:e.stateNode,e};var Av={bundleType:0,version:"19.1.1",rendererPackageName:"react-dom",currentDispatcherRef:L,reconcilerVersion:"19.1.1"};if(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<"u"){var io=__REACT_DEVTOOLS_GLOBAL_HOOK__;if(!io.isDisabled&&io.supportsFiber)try{Ne=io.inject(Av),Re=io}catch{}}return Ur.createRoot=function(e,a){if(!u(e))throw Error(o(299));var s=!1,r="",c=wh,d=_h,g=Sh,j=null;return a!=null&&(a.unstable_strictMode===!0&&(s=!0),a.identifierPrefix!==void 0&&(r=a.identifierPrefix),a.onUncaughtError!==void 0&&(c=a.onUncaughtError),a.onCaughtError!==void 0&&(d=a.onCaughtError),a.onRecoverableError!==void 0&&(g=a.onRecoverableError),a.unstable_transitionCallbacks!==void 0&&(j=a.unstable_transitionCallbacks)),a=Jm(e,1,!1,null,null,s,r,c,d,g,j,null),e[Wt]=a.current,md(e),new Md(a)},Ur.hydrateRoot=function(e,a,s){if(!u(e))throw Error(o(299));var r=!1,c="",d=wh,g=_h,j=Sh,C=null,q=null;return s!=null&&(s.unstable_strictMode===!0&&(r=!0),s.identifierPrefix!==void 0&&(c=s.identifierPrefix),s.onUncaughtError!==void 0&&(d=s.onUncaughtError),s.onCaughtError!==void 0&&(g=s.onCaughtError),s.onRecoverableError!==void 0&&(j=s.onRecoverableError),s.unstable_transitionCallbacks!==void 0&&(C=s.unstable_transitionCallbacks),s.formState!==void 0&&(q=s.formState)),a=Jm(e,1,!0,a,s??null,r,c,d,g,j,C,q),a.context=Km(null),s=a.current,r=Va(),r=jt(r),c=ss(r),c.callback=null,is(s,c,r),s=r,a.current.lanes=s,We(a,s),jn(a),e[Wt]=a.current,md(e),new so(a)},Ur.version="19.1.1",Ur}var xp;function Iv(){if(xp)return Od.exports;xp=1;function n(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(n)}catch(i){console.error(i)}}return n(),Od.exports=Hv(),Od.exports}var $v=Iv();const Fv=xg($v);vg();/**
 * @remix-run/router v1.23.0
 *
 * Copyright (c) Remix Software Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE.md file in the root directory of this source tree.
 *
 * @license MIT
 */function Yr(){return Yr=Object.assign?Object.assign.bind():function(n){for(var i=1;i<arguments.length;i++){var l=arguments[i];for(var o in l)Object.prototype.hasOwnProperty.call(l,o)&&(n[o]=l[o])}return n},Yr.apply(this,arguments)}var ws;(function(n){n.Pop="POP",n.Push="PUSH",n.Replace="REPLACE"})(ws||(ws={}));const vp="popstate";function Yv(n){n===void 0&&(n={});function i(o,u){let{pathname:f,search:m,hash:x}=o.location;return Kd("",{pathname:f,search:m,hash:x},u.state&&u.state.usr||null,u.state&&u.state.key||"default")}function l(o,u){return typeof u=="string"?u:bg(u)}return Pv(i,l,null,n)}function sa(n,i){if(n===!1||n===null||typeof n>"u")throw new Error(i)}function yg(n,i){if(!n){typeof console<"u"&&console.warn(i);try{throw new Error(i)}catch{}}}function Gv(){return Math.random().toString(36).substr(2,8)}function yp(n,i){return{usr:n.state,key:n.key,idx:i}}function Kd(n,i,l,o){return l===void 0&&(l=null),Yr({pathname:typeof n=="string"?n:n.pathname,search:"",hash:""},typeof i=="string"?Ii(i):i,{state:l,key:i&&i.key||o||Gv()})}function bg(n){let{pathname:i="/",search:l="",hash:o=""}=n;return l&&l!=="?"&&(i+=l.charAt(0)==="?"?l:"?"+l),o&&o!=="#"&&(i+=o.charAt(0)==="#"?o:"#"+o),i}function Ii(n){let i={};if(n){let l=n.indexOf("#");l>=0&&(i.hash=n.substr(l),n=n.substr(0,l));let o=n.indexOf("?");o>=0&&(i.search=n.substr(o),n=n.substr(0,o)),n&&(i.pathname=n)}return i}function Pv(n,i,l,o){o===void 0&&(o={});let{window:u=document.defaultView,v5Compat:f=!1}=o,m=u.history,x=ws.Pop,p=null,h=v();h==null&&(h=0,m.replaceState(Yr({},m.state,{idx:h}),""));function v(){return(m.state||{idx:null}).idx}function y(){x=ws.Pop;let U=v(),oe=U==null?null:U-h;h=U,p&&p({action:x,location:z.location,delta:oe})}function N(U,oe){x=ws.Push;let ie=Kd(z.location,U,oe);h=v()+1;let me=yp(ie,h),Ae=z.createHref(ie);try{m.pushState(me,"",Ae)}catch(de){if(de instanceof DOMException&&de.name==="DataCloneError")throw de;u.location.assign(Ae)}f&&p&&p({action:x,location:z.location,delta:1})}function S(U,oe){x=ws.Replace;let ie=Kd(z.location,U,oe);h=v();let me=yp(ie,h),Ae=z.createHref(ie);m.replaceState(me,"",Ae),f&&p&&p({action:x,location:z.location,delta:0})}function A(U){let oe=u.location.origin!=="null"?u.location.origin:u.location.href,ie=typeof U=="string"?U:bg(U);return ie=ie.replace(/ $/,"%20"),sa(oe,"No window.location.(origin|href) available to create URL for href: "+ie),new URL(ie,oe)}let z={get action(){return x},get location(){return n(u,m)},listen(U){if(p)throw new Error("A history only accepts one active listener");return u.addEventListener(vp,y),p=U,()=>{u.removeEventListener(vp,y),p=null}},createHref(U){return i(u,U)},createURL:A,encodeLocation(U){let oe=A(U);return{pathname:oe.pathname,search:oe.search,hash:oe.hash}},push:N,replace:S,go(U){return m.go(U)}};return z}var bp;(function(n){n.data="data",n.deferred="deferred",n.redirect="redirect",n.error="error"})(bp||(bp={}));function Vv(n,i,l){return l===void 0&&(l="/"),Xv(n,i,l)}function Xv(n,i,l,o){let u=typeof i=="string"?Ii(i):i,f=wg(u.pathname||"/",l);if(f==null)return null;let m=jg(n);Zv(m);let x=null;for(let p=0;x==null&&p<m.length;++p){let h=ly(f);x=sy(m[p],h)}return x}function jg(n,i,l,o){i===void 0&&(i=[]),l===void 0&&(l=[]),o===void 0&&(o="");let u=(f,m,x)=>{let p={relativePath:x===void 0?f.path||"":x,caseSensitive:f.caseSensitive===!0,childrenIndex:m,route:f};p.relativePath.startsWith("/")&&(sa(p.relativePath.startsWith(o),'Absolute route path "'+p.relativePath+'" nested under path '+('"'+o+'" is not valid. An absolute child route path ')+"must start with the combined path of all its parent routes."),p.relativePath=p.relativePath.slice(o.length));let h=Gs([o,p.relativePath]),v=l.concat(p);f.children&&f.children.length>0&&(sa(f.index!==!0,"Index routes must not have child routes. Please remove "+('all child routes from route path "'+h+'".')),jg(f.children,i,v,h)),!(f.path==null&&!f.index)&&i.push({path:h,score:ay(h,f.index),routesMeta:v})};return n.forEach((f,m)=>{var x;if(f.path===""||!((x=f.path)!=null&&x.includes("?")))u(f,m);else for(let p of Ng(f.path))u(f,m,p)}),i}function Ng(n){let i=n.split("/");if(i.length===0)return[];let[l,...o]=i,u=l.endsWith("?"),f=l.replace(/\?$/,"");if(o.length===0)return u?[f,""]:[f];let m=Ng(o.join("/")),x=[];return x.push(...m.map(p=>p===""?f:[f,p].join("/"))),u&&x.push(...m),x.map(p=>n.startsWith("/")&&p===""?"/":p)}function Zv(n){n.sort((i,l)=>i.score!==l.score?l.score-i.score:ny(i.routesMeta.map(o=>o.childrenIndex),l.routesMeta.map(o=>o.childrenIndex)))}const Qv=/^:[\w-]+$/,Jv=3,Kv=2,Wv=1,ey=10,ty=-2,jp=n=>n==="*";function ay(n,i){let l=n.split("/"),o=l.length;return l.some(jp)&&(o+=ty),i&&(o+=Kv),l.filter(u=>!jp(u)).reduce((u,f)=>u+(Qv.test(f)?Jv:f===""?Wv:ey),o)}function ny(n,i){return n.length===i.length&&n.slice(0,-1).every((o,u)=>o===i[u])?n[n.length-1]-i[i.length-1]:0}function sy(n,i,l){let{routesMeta:o}=n,u={},f="/",m=[];for(let x=0;x<o.length;++x){let p=o[x],h=x===o.length-1,v=f==="/"?i:i.slice(f.length)||"/",y=iy({path:p.relativePath,caseSensitive:p.caseSensitive,end:h},v),N=p.route;if(!y)return null;Object.assign(u,y.params),m.push({params:u,pathname:Gs([f,y.pathname]),pathnameBase:uy(Gs([f,y.pathnameBase])),route:N}),y.pathnameBase!=="/"&&(f=Gs([f,y.pathnameBase]))}return m}function iy(n,i){typeof n=="string"&&(n={path:n,caseSensitive:!1,end:!0});let[l,o]=ry(n.path,n.caseSensitive,n.end),u=i.match(l);if(!u)return null;let f=u[0],m=f.replace(/(.)\/+$/,"$1"),x=u.slice(1);return{params:o.reduce((h,v,y)=>{let{paramName:N,isOptional:S}=v;if(N==="*"){let z=x[y]||"";m=f.slice(0,f.length-z.length).replace(/(.)\/+$/,"$1")}const A=x[y];return S&&!A?h[N]=void 0:h[N]=(A||"").replace(/%2F/g,"/"),h},{}),pathname:f,pathnameBase:m,pattern:n}}function ry(n,i,l){i===void 0&&(i=!1),l===void 0&&(l=!0),yg(n==="*"||!n.endsWith("*")||n.endsWith("/*"),'Route path "'+n+'" will be treated as if it were '+('"'+n.replace(/\*$/,"/*")+'" because the `*` character must ')+"always follow a `/` in the pattern. To get rid of this warning, "+('please change the route path to "'+n.replace(/\*$/,"/*")+'".'));let o=[],u="^"+n.replace(/\/*\*?$/,"").replace(/^\/*/,"/").replace(/[\\.*+^${}|()[\]]/g,"\\$&").replace(/\/:([\w-]+)(\?)?/g,(m,x,p)=>(o.push({paramName:x,isOptional:p!=null}),p?"/?([^\\/]+)?":"/([^\\/]+)"));return n.endsWith("*")?(o.push({paramName:"*"}),u+=n==="*"||n==="/*"?"(.*)$":"(?:\\/(.+)|\\/*)$"):l?u+="\\/*$":n!==""&&n!=="/"&&(u+="(?:(?=\\/|$))"),[new RegExp(u,i?void 0:"i"),o]}function ly(n){try{return n.split("/").map(i=>decodeURIComponent(i).replace(/\//g,"%2F")).join("/")}catch(i){return yg(!1,'The URL path "'+n+'" could not be decoded because it is is a malformed URL segment. This is probably due to a bad percent '+("encoding ("+i+").")),n}}function wg(n,i){if(i==="/")return n;if(!n.toLowerCase().startsWith(i.toLowerCase()))return null;let l=i.endsWith("/")?i.length-1:i.length,o=n.charAt(l);return o&&o!=="/"?null:n.slice(l)||"/"}function oy(n,i){i===void 0&&(i="/");let{pathname:l,search:o="",hash:u=""}=typeof n=="string"?Ii(n):n;return{pathname:l?l.startsWith("/")?l:cy(l,i):i,search:fy(o),hash:hy(u)}}function cy(n,i){let l=i.replace(/\/+$/,"").split("/");return n.split("/").forEach(u=>{u===".."?l.length>1&&l.pop():u!=="."&&l.push(u)}),l.length>1?l.join("/"):"/"}function Hd(n,i,l,o){return"Cannot include a '"+n+"' character in a manually specified "+("`to."+i+"` field ["+JSON.stringify(o)+"].  Please separate it out to the ")+("`to."+l+"` field. Alternatively you may provide the full path as ")+'a string in <Link to="..."> and the router will parse it for you.'}function dy(n){return n.filter((i,l)=>l===0||i.route.path&&i.route.path.length>0)}function _g(n,i){let l=dy(n);return i?l.map((o,u)=>u===l.length-1?o.pathname:o.pathnameBase):l.map(o=>o.pathnameBase)}function Sg(n,i,l,o){o===void 0&&(o=!1);let u;typeof n=="string"?u=Ii(n):(u=Yr({},n),sa(!u.pathname||!u.pathname.includes("?"),Hd("?","pathname","search",u)),sa(!u.pathname||!u.pathname.includes("#"),Hd("#","pathname","hash",u)),sa(!u.search||!u.search.includes("#"),Hd("#","search","hash",u)));let f=n===""||u.pathname==="",m=f?"/":u.pathname,x;if(m==null)x=l;else{let y=i.length-1;if(!o&&m.startsWith("..")){let N=m.split("/");for(;N[0]==="..";)N.shift(),y-=1;u.pathname=N.join("/")}x=y>=0?i[y]:"/"}let p=oy(u,x),h=m&&m!=="/"&&m.endsWith("/"),v=(f||m===".")&&l.endsWith("/");return!p.pathname.endsWith("/")&&(h||v)&&(p.pathname+="/"),p}const Gs=n=>n.join("/").replace(/\/\/+/g,"/"),uy=n=>n.replace(/\/+$/,"").replace(/^\/*/,"/"),fy=n=>!n||n==="?"?"":n.startsWith("?")?n:"?"+n,hy=n=>!n||n==="#"?"":n.startsWith("#")?n:"#"+n;function my(n){return n!=null&&typeof n.status=="number"&&typeof n.statusText=="string"&&typeof n.internal=="boolean"&&"data"in n}const Tg=["post","put","patch","delete"];new Set(Tg);const py=["get",...Tg];new Set(py);/**
 * React Router v6.30.1
 *
 * Copyright (c) Remix Software Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE.md file in the root directory of this source tree.
 *
 * @license MIT
 */function Gr(){return Gr=Object.assign?Object.assign.bind():function(n){for(var i=1;i<arguments.length;i++){var l=arguments[i];for(var o in l)Object.prototype.hasOwnProperty.call(l,o)&&(n[o]=l[o])}return n},Gr.apply(this,arguments)}const gu=w.createContext(null),gy=w.createContext(null),Zr=w.createContext(null),Mo=w.createContext(null),Qs=w.createContext({outlet:null,matches:[],isDataRoute:!1}),Cg=w.createContext(null);function Qr(){return w.useContext(Mo)!=null}function xu(){return Qr()||sa(!1),w.useContext(Mo).location}function Ag(n){w.useContext(Zr).static||w.useLayoutEffect(n)}function Jr(){let{isDataRoute:n}=w.useContext(Qs);return n?zy():xy()}function xy(){Qr()||sa(!1);let n=w.useContext(gu),{basename:i,future:l,navigator:o}=w.useContext(Zr),{matches:u}=w.useContext(Qs),{pathname:f}=xu(),m=JSON.stringify(_g(u,l.v7_relativeSplatPath)),x=w.useRef(!1);return Ag(()=>{x.current=!0}),w.useCallback(function(h,v){if(v===void 0&&(v={}),!x.current)return;if(typeof h=="number"){o.go(h);return}let y=Sg(h,JSON.parse(m),f,v.relative==="path");n==null&&i!=="/"&&(y.pathname=y.pathname==="/"?i:Gs([i,y.pathname])),(v.replace?o.replace:o.push)(y,v.state,v)},[i,o,m,f,n])}function vy(n,i){return yy(n,i)}function yy(n,i,l,o){Qr()||sa(!1);let{navigator:u}=w.useContext(Zr),{matches:f}=w.useContext(Qs),m=f[f.length-1],x=m?m.params:{};m&&m.pathname;let p=m?m.pathnameBase:"/";m&&m.route;let h=xu(),v;if(i){var y;let U=typeof i=="string"?Ii(i):i;p==="/"||(y=U.pathname)!=null&&y.startsWith(p)||sa(!1),v=U}else v=h;let N=v.pathname||"/",S=N;if(p!=="/"){let U=p.replace(/^\//,"").split("/");S="/"+N.replace(/^\//,"").split("/").slice(U.length).join("/")}let A=Vv(n,{pathname:S}),z=_y(A&&A.map(U=>Object.assign({},U,{params:Object.assign({},x,U.params),pathname:Gs([p,u.encodeLocation?u.encodeLocation(U.pathname).pathname:U.pathname]),pathnameBase:U.pathnameBase==="/"?p:Gs([p,u.encodeLocation?u.encodeLocation(U.pathnameBase).pathname:U.pathnameBase])})),f,l,o);return i&&z?w.createElement(Mo.Provider,{value:{location:Gr({pathname:"/",search:"",hash:"",state:null,key:"default"},v),navigationType:ws.Pop}},z):z}function by(){let n=Ay(),i=my(n)?n.status+" "+n.statusText:n instanceof Error?n.message:JSON.stringify(n),l=n instanceof Error?n.stack:null,u={padding:"0.5rem",backgroundColor:"rgba(200,200,200, 0.5)"};return w.createElement(w.Fragment,null,w.createElement("h2",null,"Unexpected Application Error!"),w.createElement("h3",{style:{fontStyle:"italic"}},i),l?w.createElement("pre",{style:u},l):null,null)}const jy=w.createElement(by,null);class Ny extends w.Component{constructor(i){super(i),this.state={location:i.location,revalidation:i.revalidation,error:i.error}}static getDerivedStateFromError(i){return{error:i}}static getDerivedStateFromProps(i,l){return l.location!==i.location||l.revalidation!=="idle"&&i.revalidation==="idle"?{error:i.error,location:i.location,revalidation:i.revalidation}:{error:i.error!==void 0?i.error:l.error,location:l.location,revalidation:i.revalidation||l.revalidation}}componentDidCatch(i,l){console.error("React Router caught the following error during render",i,l)}render(){return this.state.error!==void 0?w.createElement(Qs.Provider,{value:this.props.routeContext},w.createElement(Cg.Provider,{value:this.state.error,children:this.props.component})):this.props.children}}function wy(n){let{routeContext:i,match:l,children:o}=n,u=w.useContext(gu);return u&&u.static&&u.staticContext&&(l.route.errorElement||l.route.ErrorBoundary)&&(u.staticContext._deepestRenderedBoundaryId=l.route.id),w.createElement(Qs.Provider,{value:i},o)}function _y(n,i,l,o){var u;if(i===void 0&&(i=[]),l===void 0&&(l=null),o===void 0&&(o=null),n==null){var f;if(!l)return null;if(l.errors)n=l.matches;else if((f=o)!=null&&f.v7_partialHydration&&i.length===0&&!l.initialized&&l.matches.length>0)n=l.matches;else return null}let m=n,x=(u=l)==null?void 0:u.errors;if(x!=null){let v=m.findIndex(y=>y.route.id&&(x==null?void 0:x[y.route.id])!==void 0);v>=0||sa(!1),m=m.slice(0,Math.min(m.length,v+1))}let p=!1,h=-1;if(l&&o&&o.v7_partialHydration)for(let v=0;v<m.length;v++){let y=m[v];if((y.route.HydrateFallback||y.route.hydrateFallbackElement)&&(h=v),y.route.id){let{loaderData:N,errors:S}=l,A=y.route.loader&&N[y.route.id]===void 0&&(!S||S[y.route.id]===void 0);if(y.route.lazy||A){p=!0,h>=0?m=m.slice(0,h+1):m=[m[0]];break}}}return m.reduceRight((v,y,N)=>{let S,A=!1,z=null,U=null;l&&(S=x&&y.route.id?x[y.route.id]:void 0,z=y.route.errorElement||jy,p&&(h<0&&N===0?(ky("route-fallback"),A=!0,U=null):h===N&&(A=!0,U=y.route.hydrateFallbackElement||null)));let oe=i.concat(m.slice(0,N+1)),ie=()=>{let me;return S?me=z:A?me=U:y.route.Component?me=w.createElement(y.route.Component,null):y.route.element?me=y.route.element:me=v,w.createElement(wy,{match:y,routeContext:{outlet:v,matches:oe,isDataRoute:l!=null},children:me})};return l&&(y.route.ErrorBoundary||y.route.errorElement||N===0)?w.createElement(Ny,{location:l.location,revalidation:l.revalidation,component:z,error:S,children:ie(),routeContext:{outlet:null,matches:oe,isDataRoute:!0}}):ie()},null)}var zg=(function(n){return n.UseBlocker="useBlocker",n.UseRevalidator="useRevalidator",n.UseNavigateStable="useNavigate",n})(zg||{}),kg=(function(n){return n.UseBlocker="useBlocker",n.UseLoaderData="useLoaderData",n.UseActionData="useActionData",n.UseRouteError="useRouteError",n.UseNavigation="useNavigation",n.UseRouteLoaderData="useRouteLoaderData",n.UseMatches="useMatches",n.UseRevalidator="useRevalidator",n.UseNavigateStable="useNavigate",n.UseRouteId="useRouteId",n})(kg||{});function Sy(n){let i=w.useContext(gu);return i||sa(!1),i}function Ty(n){let i=w.useContext(gy);return i||sa(!1),i}function Cy(n){let i=w.useContext(Qs);return i||sa(!1),i}function Eg(n){let i=Cy(),l=i.matches[i.matches.length-1];return l.route.id||sa(!1),l.route.id}function Ay(){var n;let i=w.useContext(Cg),l=Ty(),o=Eg();return i!==void 0?i:(n=l.errors)==null?void 0:n[o]}function zy(){let{router:n}=Sy(zg.UseNavigateStable),i=Eg(kg.UseNavigateStable),l=w.useRef(!1);return Ag(()=>{l.current=!0}),w.useCallback(function(u,f){f===void 0&&(f={}),l.current&&(typeof u=="number"?n.navigate(u):n.navigate(u,Gr({fromRouteId:i},f)))},[n,i])}const Np={};function ky(n,i,l){Np[n]||(Np[n]=!0)}function Ey(n,i){n==null||n.v7_startTransition,n==null||n.v7_relativeSplatPath}function Nn(n){let{to:i,replace:l,state:o,relative:u}=n;Qr()||sa(!1);let{future:f,static:m}=w.useContext(Zr),{matches:x}=w.useContext(Qs),{pathname:p}=xu(),h=Jr(),v=Sg(i,_g(x,f.v7_relativeSplatPath),p,u==="path"),y=JSON.stringify(v);return w.useEffect(()=>h(JSON.parse(y),{replace:l,state:o,relative:u}),[h,y,u,l,o]),null}function fn(n){sa(!1)}function My(n){let{basename:i="/",children:l=null,location:o,navigationType:u=ws.Pop,navigator:f,static:m=!1,future:x}=n;Qr()&&sa(!1);let p=i.replace(/^\/*/,"/"),h=w.useMemo(()=>({basename:p,navigator:f,static:m,future:Gr({v7_relativeSplatPath:!1},x)}),[p,x,f,m]);typeof o=="string"&&(o=Ii(o));let{pathname:v="/",search:y="",hash:N="",state:S=null,key:A="default"}=o,z=w.useMemo(()=>{let U=wg(v,p);return U==null?null:{location:{pathname:U,search:y,hash:N,state:S,key:A},navigationType:u}},[p,v,y,N,S,A,u]);return z==null?null:w.createElement(Zr.Provider,{value:h},w.createElement(Mo.Provider,{children:l,value:z}))}function Dy(n){let{children:i,location:l}=n;return vy(Wd(i),l)}new Promise(()=>{});function Wd(n,i){i===void 0&&(i=[]);let l=[];return w.Children.forEach(n,(o,u)=>{if(!w.isValidElement(o))return;let f=[...i,u];if(o.type===w.Fragment){l.push.apply(l,Wd(o.props.children,f));return}o.type!==fn&&sa(!1),!o.props.index||!o.props.children||sa(!1);let m={id:o.props.id||f.join("-"),caseSensitive:o.props.caseSensitive,element:o.props.element,Component:o.props.Component,index:o.props.index,path:o.props.path,loader:o.props.loader,action:o.props.action,errorElement:o.props.errorElement,ErrorBoundary:o.props.ErrorBoundary,hasErrorBoundary:o.props.ErrorBoundary!=null||o.props.errorElement!=null,shouldRevalidate:o.props.shouldRevalidate,handle:o.props.handle,lazy:o.props.lazy};o.props.children&&(m.children=Wd(o.props.children,f)),l.push(m)}),l}/**
 * React Router DOM v6.30.1
 *
 * Copyright (c) Remix Software Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE.md file in the root directory of this source tree.
 *
 * @license MIT
 */const Ry="6";try{window.__reactRouterVersion=Ry}catch{}const Uy="startTransition",wp=Ov[Uy];function Oy(n){let{basename:i,children:l,future:o,window:u}=n,f=w.useRef();f.current==null&&(f.current=Yv({window:u,v5Compat:!0}));let m=f.current,[x,p]=w.useState({action:m.action,location:m.location}),{v7_startTransition:h}=o||{},v=w.useCallback(y=>{h&&wp?wp(()=>p(y)):p(y)},[p,h]);return w.useLayoutEffect(()=>m.listen(v),[m,v]),w.useEffect(()=>Ey(o),[o]),w.createElement(My,{basename:i,children:l,location:x.location,navigationType:x.action,navigator:m,future:o})}var _p;(function(n){n.UseScrollRestoration="useScrollRestoration",n.UseSubmit="useSubmit",n.UseSubmitFetcher="useSubmitFetcher",n.UseFetcher="useFetcher",n.useViewTransitionState="useViewTransitionState"})(_p||(_p={}));var Sp;(function(n){n.UseFetcher="useFetcher",n.UseFetchers="useFetchers",n.UseScrollRestoration="useScrollRestoration"})(Sp||(Sp={}));function fo(n,i){return n==null||i==null?NaN:n<i?-1:n>i?1:n>=i?0:NaN}function Ly(n,i){return n==null||i==null?NaN:i<n?-1:i>n?1:i>=n?0:NaN}function vu(n){let i,l,o;n.length!==2?(i=fo,l=(x,p)=>fo(n(x),p),o=(x,p)=>n(x)-p):(i=n===fo||n===Ly?n:qy,l=n,o=n);function u(x,p,h=0,v=x.length){if(h<v){if(i(p,p)!==0)return v;do{const y=h+v>>>1;l(x[y],p)<0?h=y+1:v=y}while(h<v)}return h}function f(x,p,h=0,v=x.length){if(h<v){if(i(p,p)!==0)return v;do{const y=h+v>>>1;l(x[y],p)<=0?h=y+1:v=y}while(h<v)}return h}function m(x,p,h=0,v=x.length){const y=u(x,p,h,v-1);return y>h&&o(x[y-1],p)>-o(x[y],p)?y-1:y}return{left:u,center:m,right:f}}function qy(){return 0}function By(n){return n===null?NaN:+n}const Hy=vu(fo),Iy=Hy.right;vu(By).center;function $y(n,i){let l,o;if(i===void 0)for(const u of n)u!=null&&(l===void 0?u>=u&&(l=o=u):(l>u&&(l=u),o<u&&(o=u)));else{let u=-1;for(let f of n)(f=i(f,++u,n))!=null&&(l===void 0?f>=f&&(l=o=f):(l>f&&(l=f),o<f&&(o=f)))}return[l,o]}class Tp extends Map{constructor(i,l=Gy){if(super(),Object.defineProperties(this,{_intern:{value:new Map},_key:{value:l}}),i!=null)for(const[o,u]of i)this.set(o,u)}get(i){return super.get(Cp(this,i))}has(i){return super.has(Cp(this,i))}set(i,l){return super.set(Fy(this,i),l)}delete(i){return super.delete(Yy(this,i))}}function Cp({_intern:n,_key:i},l){const o=i(l);return n.has(o)?n.get(o):l}function Fy({_intern:n,_key:i},l){const o=i(l);return n.has(o)?n.get(o):(n.set(o,l),l)}function Yy({_intern:n,_key:i},l){const o=i(l);return n.has(o)&&(l=n.get(o),n.delete(o)),l}function Gy(n){return n!==null&&typeof n=="object"?n.valueOf():n}const Py=Math.sqrt(50),Vy=Math.sqrt(10),Xy=Math.sqrt(2);function go(n,i,l){const o=(i-n)/Math.max(0,l),u=Math.floor(Math.log10(o)),f=o/Math.pow(10,u),m=f>=Py?10:f>=Vy?5:f>=Xy?2:1;let x,p,h;return u<0?(h=Math.pow(10,-u)/m,x=Math.round(n*h),p=Math.round(i*h),x/h<n&&++x,p/h>i&&--p,h=-h):(h=Math.pow(10,u)*m,x=Math.round(n/h),p=Math.round(i/h),x*h<n&&++x,p*h>i&&--p),p<x&&.5<=l&&l<2?go(n,i,l*2):[x,p,h]}function Zy(n,i,l){if(i=+i,n=+n,l=+l,!(l>0))return[];if(n===i)return[n];const o=i<n,[u,f,m]=o?go(i,n,l):go(n,i,l);if(!(f>=u))return[];const x=f-u+1,p=new Array(x);if(o)if(m<0)for(let h=0;h<x;++h)p[h]=(f-h)/-m;else for(let h=0;h<x;++h)p[h]=(f-h)*m;else if(m<0)for(let h=0;h<x;++h)p[h]=(u+h)/-m;else for(let h=0;h<x;++h)p[h]=(u+h)*m;return p}function eu(n,i,l){return i=+i,n=+n,l=+l,go(n,i,l)[2]}function tu(n,i,l){i=+i,n=+n,l=+l;const o=i<n,u=o?eu(i,n,l):eu(n,i,l);return(o?-1:1)*(u<0?1/-u:u)}function Mg(n,i){let l;if(i===void 0)for(const o of n)o!=null&&(l<o||l===void 0&&o>=o)&&(l=o);else{let o=-1;for(let u of n)(u=i(u,++o,n))!=null&&(l<u||l===void 0&&u>=u)&&(l=u)}return l}function Qy(n,i,l){n=+n,i=+i,l=(u=arguments.length)<2?(i=n,n=0,1):u<3?1:+l;for(var o=-1,u=Math.max(0,Math.ceil((i-n)/l))|0,f=new Array(u);++o<u;)f[o]=n+o*l;return f}function Jy(n){return n}var Id=1,$d=2,au=3,Hr=4,Ap=1e-6;function Ky(n){return"translate("+n+",0)"}function Wy(n){return"translate(0,"+n+")"}function eb(n){return i=>+n(i)}function tb(n,i){return i=Math.max(0,n.bandwidth()-i*2)/2,n.round()&&(i=Math.round(i)),l=>+n(l)+i}function ab(){return!this.__axis}function Dg(n,i){var l=[],o=null,u=null,f=6,m=6,x=3,p=typeof window<"u"&&window.devicePixelRatio>1?0:.5,h=n===Id||n===Hr?-1:1,v=n===Hr||n===$d?"x":"y",y=n===Id||n===au?Ky:Wy;function N(S){var A=o??(i.ticks?i.ticks.apply(i,l):i.domain()),z=u??(i.tickFormat?i.tickFormat.apply(i,l):Jy),U=Math.max(f,0)+x,oe=i.range(),ie=+oe[0]+p,me=+oe[oe.length-1]+p,Ae=(i.bandwidth?tb:eb)(i.copy(),p),de=S.selection?S.selection():S,pe=de.selectAll(".domain").data([null]),W=de.selectAll(".tick").data(A,i).order(),Ke=W.exit(),he=W.enter().append("g").attr("class","tick"),De=W.select("line"),xe=W.select("text");pe=pe.merge(pe.enter().insert("path",".tick").attr("class","domain").attr("stroke","currentColor")),W=W.merge(he),De=De.merge(he.append("line").attr("stroke","currentColor").attr(v+"2",h*f)),xe=xe.merge(he.append("text").attr("fill","currentColor").attr(v,h*U).attr("dy",n===Id?"0em":n===au?"0.71em":"0.32em")),S!==de&&(pe=pe.transition(S),W=W.transition(S),De=De.transition(S),xe=xe.transition(S),Ke=Ke.transition(S).attr("opacity",Ap).attr("transform",function(je){return isFinite(je=Ae(je))?y(je+p):this.getAttribute("transform")}),he.attr("opacity",Ap).attr("transform",function(je){var ze=this.parentNode.__axis;return y((ze&&isFinite(ze=ze(je))?ze:Ae(je))+p)})),Ke.remove(),pe.attr("d",n===Hr||n===$d?m?"M"+h*m+","+ie+"H"+p+"V"+me+"H"+h*m:"M"+p+","+ie+"V"+me:m?"M"+ie+","+h*m+"V"+p+"H"+me+"V"+h*m:"M"+ie+","+p+"H"+me),W.attr("opacity",1).attr("transform",function(je){return y(Ae(je)+p)}),De.attr(v+"2",h*f),xe.attr(v,h*U).text(z),de.filter(ab).attr("fill","none").attr("font-size",10).attr("font-family","sans-serif").attr("text-anchor",n===$d?"start":n===Hr?"end":"middle"),de.each(function(){this.__axis=Ae})}return N.scale=function(S){return arguments.length?(i=S,N):i},N.ticks=function(){return l=Array.from(arguments),N},N.tickArguments=function(S){return arguments.length?(l=S==null?[]:Array.from(S),N):l.slice()},N.tickValues=function(S){return arguments.length?(o=S==null?null:Array.from(S),N):o&&o.slice()},N.tickFormat=function(S){return arguments.length?(u=S,N):u},N.tickSize=function(S){return arguments.length?(f=m=+S,N):f},N.tickSizeInner=function(S){return arguments.length?(f=+S,N):f},N.tickSizeOuter=function(S){return arguments.length?(m=+S,N):m},N.tickPadding=function(S){return arguments.length?(x=+S,N):x},N.offset=function(S){return arguments.length?(p=+S,N):p},N}function nu(n){return Dg(au,n)}function su(n){return Dg(Hr,n)}var nb={value:()=>{}};function Rg(){for(var n=0,i=arguments.length,l={},o;n<i;++n){if(!(o=arguments[n]+"")||o in l||/[\s.]/.test(o))throw new Error("illegal type: "+o);l[o]=[]}return new ho(l)}function ho(n){this._=n}function sb(n,i){return n.trim().split(/^|\s+/).map(function(l){var o="",u=l.indexOf(".");if(u>=0&&(o=l.slice(u+1),l=l.slice(0,u)),l&&!i.hasOwnProperty(l))throw new Error("unknown type: "+l);return{type:l,name:o}})}ho.prototype=Rg.prototype={constructor:ho,on:function(n,i){var l=this._,o=sb(n+"",l),u,f=-1,m=o.length;if(arguments.length<2){for(;++f<m;)if((u=(n=o[f]).type)&&(u=ib(l[u],n.name)))return u;return}if(i!=null&&typeof i!="function")throw new Error("invalid callback: "+i);for(;++f<m;)if(u=(n=o[f]).type)l[u]=zp(l[u],n.name,i);else if(i==null)for(u in l)l[u]=zp(l[u],n.name,null);return this},copy:function(){var n={},i=this._;for(var l in i)n[l]=i[l].slice();return new ho(n)},call:function(n,i){if((u=arguments.length-2)>0)for(var l=new Array(u),o=0,u,f;o<u;++o)l[o]=arguments[o+2];if(!this._.hasOwnProperty(n))throw new Error("unknown type: "+n);for(f=this._[n],o=0,u=f.length;o<u;++o)f[o].value.apply(i,l)},apply:function(n,i,l){if(!this._.hasOwnProperty(n))throw new Error("unknown type: "+n);for(var o=this._[n],u=0,f=o.length;u<f;++u)o[u].value.apply(i,l)}};function ib(n,i){for(var l=0,o=n.length,u;l<o;++l)if((u=n[l]).name===i)return u.value}function zp(n,i,l){for(var o=0,u=n.length;o<u;++o)if(n[o].name===i){n[o]=nb,n=n.slice(0,o).concat(n.slice(o+1));break}return l!=null&&n.push({name:i,value:l}),n}var iu="http://www.w3.org/1999/xhtml";const kp={svg:"http://www.w3.org/2000/svg",xhtml:iu,xlink:"http://www.w3.org/1999/xlink",xml:"http://www.w3.org/XML/1998/namespace",xmlns:"http://www.w3.org/2000/xmlns/"};function Do(n){var i=n+="",l=i.indexOf(":");return l>=0&&(i=n.slice(0,l))!=="xmlns"&&(n=n.slice(l+1)),kp.hasOwnProperty(i)?{space:kp[i],local:n}:n}function rb(n){return function(){var i=this.ownerDocument,l=this.namespaceURI;return l===iu&&i.documentElement.namespaceURI===iu?i.createElement(n):i.createElementNS(l,n)}}function lb(n){return function(){return this.ownerDocument.createElementNS(n.space,n.local)}}function Ug(n){var i=Do(n);return(i.local?lb:rb)(i)}function ob(){}function yu(n){return n==null?ob:function(){return this.querySelector(n)}}function cb(n){typeof n!="function"&&(n=yu(n));for(var i=this._groups,l=i.length,o=new Array(l),u=0;u<l;++u)for(var f=i[u],m=f.length,x=o[u]=new Array(m),p,h,v=0;v<m;++v)(p=f[v])&&(h=n.call(p,p.__data__,v,f))&&("__data__"in p&&(h.__data__=p.__data__),x[v]=h);return new Ma(o,this._parents)}function Og(n){return n==null?[]:Array.isArray(n)?n:Array.from(n)}function db(){return[]}function Lg(n){return n==null?db:function(){return this.querySelectorAll(n)}}function ub(n){return function(){return Og(n.apply(this,arguments))}}function fb(n){typeof n=="function"?n=ub(n):n=Lg(n);for(var i=this._groups,l=i.length,o=[],u=[],f=0;f<l;++f)for(var m=i[f],x=m.length,p,h=0;h<x;++h)(p=m[h])&&(o.push(n.call(p,p.__data__,h,m)),u.push(p));return new Ma(o,u)}function qg(n){return function(){return this.matches(n)}}function Bg(n){return function(i){return i.matches(n)}}var hb=Array.prototype.find;function mb(n){return function(){return hb.call(this.children,n)}}function pb(){return this.firstElementChild}function gb(n){return this.select(n==null?pb:mb(typeof n=="function"?n:Bg(n)))}var xb=Array.prototype.filter;function vb(){return Array.from(this.children)}function yb(n){return function(){return xb.call(this.children,n)}}function bb(n){return this.selectAll(n==null?vb:yb(typeof n=="function"?n:Bg(n)))}function jb(n){typeof n!="function"&&(n=qg(n));for(var i=this._groups,l=i.length,o=new Array(l),u=0;u<l;++u)for(var f=i[u],m=f.length,x=o[u]=[],p,h=0;h<m;++h)(p=f[h])&&n.call(p,p.__data__,h,f)&&x.push(p);return new Ma(o,this._parents)}function Hg(n){return new Array(n.length)}function Nb(){return new Ma(this._enter||this._groups.map(Hg),this._parents)}function xo(n,i){this.ownerDocument=n.ownerDocument,this.namespaceURI=n.namespaceURI,this._next=null,this._parent=n,this.__data__=i}xo.prototype={constructor:xo,appendChild:function(n){return this._parent.insertBefore(n,this._next)},insertBefore:function(n,i){return this._parent.insertBefore(n,i)},querySelector:function(n){return this._parent.querySelector(n)},querySelectorAll:function(n){return this._parent.querySelectorAll(n)}};function wb(n){return function(){return n}}function _b(n,i,l,o,u,f){for(var m=0,x,p=i.length,h=f.length;m<h;++m)(x=i[m])?(x.__data__=f[m],o[m]=x):l[m]=new xo(n,f[m]);for(;m<p;++m)(x=i[m])&&(u[m]=x)}function Sb(n,i,l,o,u,f,m){var x,p,h=new Map,v=i.length,y=f.length,N=new Array(v),S;for(x=0;x<v;++x)(p=i[x])&&(N[x]=S=m.call(p,p.__data__,x,i)+"",h.has(S)?u[x]=p:h.set(S,p));for(x=0;x<y;++x)S=m.call(n,f[x],x,f)+"",(p=h.get(S))?(o[x]=p,p.__data__=f[x],h.delete(S)):l[x]=new xo(n,f[x]);for(x=0;x<v;++x)(p=i[x])&&h.get(N[x])===p&&(u[x]=p)}function Tb(n){return n.__data__}function Cb(n,i){if(!arguments.length)return Array.from(this,Tb);var l=i?Sb:_b,o=this._parents,u=this._groups;typeof n!="function"&&(n=wb(n));for(var f=u.length,m=new Array(f),x=new Array(f),p=new Array(f),h=0;h<f;++h){var v=o[h],y=u[h],N=y.length,S=Ab(n.call(v,v&&v.__data__,h,o)),A=S.length,z=x[h]=new Array(A),U=m[h]=new Array(A),oe=p[h]=new Array(N);l(v,y,z,U,oe,S,i);for(var ie=0,me=0,Ae,de;ie<A;++ie)if(Ae=z[ie]){for(ie>=me&&(me=ie+1);!(de=U[me])&&++me<A;);Ae._next=de||null}}return m=new Ma(m,o),m._enter=x,m._exit=p,m}function Ab(n){return typeof n=="object"&&"length"in n?n:Array.from(n)}function zb(){return new Ma(this._exit||this._groups.map(Hg),this._parents)}function kb(n,i,l){var o=this.enter(),u=this,f=this.exit();return typeof n=="function"?(o=n(o),o&&(o=o.selection())):o=o.append(n+""),i!=null&&(u=i(u),u&&(u=u.selection())),l==null?f.remove():l(f),o&&u?o.merge(u).order():u}function Eb(n){for(var i=n.selection?n.selection():n,l=this._groups,o=i._groups,u=l.length,f=o.length,m=Math.min(u,f),x=new Array(u),p=0;p<m;++p)for(var h=l[p],v=o[p],y=h.length,N=x[p]=new Array(y),S,A=0;A<y;++A)(S=h[A]||v[A])&&(N[A]=S);for(;p<u;++p)x[p]=l[p];return new Ma(x,this._parents)}function Mb(){for(var n=this._groups,i=-1,l=n.length;++i<l;)for(var o=n[i],u=o.length-1,f=o[u],m;--u>=0;)(m=o[u])&&(f&&m.compareDocumentPosition(f)^4&&f.parentNode.insertBefore(m,f),f=m);return this}function Db(n){n||(n=Rb);function i(y,N){return y&&N?n(y.__data__,N.__data__):!y-!N}for(var l=this._groups,o=l.length,u=new Array(o),f=0;f<o;++f){for(var m=l[f],x=m.length,p=u[f]=new Array(x),h,v=0;v<x;++v)(h=m[v])&&(p[v]=h);p.sort(i)}return new Ma(u,this._parents).order()}function Rb(n,i){return n<i?-1:n>i?1:n>=i?0:NaN}function Ub(){var n=arguments[0];return arguments[0]=this,n.apply(null,arguments),this}function Ob(){return Array.from(this)}function Lb(){for(var n=this._groups,i=0,l=n.length;i<l;++i)for(var o=n[i],u=0,f=o.length;u<f;++u){var m=o[u];if(m)return m}return null}function qb(){let n=0;for(const i of this)++n;return n}function Bb(){return!this.node()}function Hb(n){for(var i=this._groups,l=0,o=i.length;l<o;++l)for(var u=i[l],f=0,m=u.length,x;f<m;++f)(x=u[f])&&n.call(x,x.__data__,f,u);return this}function Ib(n){return function(){this.removeAttribute(n)}}function $b(n){return function(){this.removeAttributeNS(n.space,n.local)}}function Fb(n,i){return function(){this.setAttribute(n,i)}}function Yb(n,i){return function(){this.setAttributeNS(n.space,n.local,i)}}function Gb(n,i){return function(){var l=i.apply(this,arguments);l==null?this.removeAttribute(n):this.setAttribute(n,l)}}function Pb(n,i){return function(){var l=i.apply(this,arguments);l==null?this.removeAttributeNS(n.space,n.local):this.setAttributeNS(n.space,n.local,l)}}function Vb(n,i){var l=Do(n);if(arguments.length<2){var o=this.node();return l.local?o.getAttributeNS(l.space,l.local):o.getAttribute(l)}return this.each((i==null?l.local?$b:Ib:typeof i=="function"?l.local?Pb:Gb:l.local?Yb:Fb)(l,i))}function Ig(n){return n.ownerDocument&&n.ownerDocument.defaultView||n.document&&n||n.defaultView}function Xb(n){return function(){this.style.removeProperty(n)}}function Zb(n,i,l){return function(){this.style.setProperty(n,i,l)}}function Qb(n,i,l){return function(){var o=i.apply(this,arguments);o==null?this.style.removeProperty(n):this.style.setProperty(n,o,l)}}function Jb(n,i,l){return arguments.length>1?this.each((i==null?Xb:typeof i=="function"?Qb:Zb)(n,i,l??"")):Oi(this.node(),n)}function Oi(n,i){return n.style.getPropertyValue(i)||Ig(n).getComputedStyle(n,null).getPropertyValue(i)}function Kb(n){return function(){delete this[n]}}function Wb(n,i){return function(){this[n]=i}}function ej(n,i){return function(){var l=i.apply(this,arguments);l==null?delete this[n]:this[n]=l}}function tj(n,i){return arguments.length>1?this.each((i==null?Kb:typeof i=="function"?ej:Wb)(n,i)):this.node()[n]}function $g(n){return n.trim().split(/^|\s+/)}function bu(n){return n.classList||new Fg(n)}function Fg(n){this._node=n,this._names=$g(n.getAttribute("class")||"")}Fg.prototype={add:function(n){var i=this._names.indexOf(n);i<0&&(this._names.push(n),this._node.setAttribute("class",this._names.join(" ")))},remove:function(n){var i=this._names.indexOf(n);i>=0&&(this._names.splice(i,1),this._node.setAttribute("class",this._names.join(" ")))},contains:function(n){return this._names.indexOf(n)>=0}};function Yg(n,i){for(var l=bu(n),o=-1,u=i.length;++o<u;)l.add(i[o])}function Gg(n,i){for(var l=bu(n),o=-1,u=i.length;++o<u;)l.remove(i[o])}function aj(n){return function(){Yg(this,n)}}function nj(n){return function(){Gg(this,n)}}function sj(n,i){return function(){(i.apply(this,arguments)?Yg:Gg)(this,n)}}function ij(n,i){var l=$g(n+"");if(arguments.length<2){for(var o=bu(this.node()),u=-1,f=l.length;++u<f;)if(!o.contains(l[u]))return!1;return!0}return this.each((typeof i=="function"?sj:i?aj:nj)(l,i))}function rj(){this.textContent=""}function lj(n){return function(){this.textContent=n}}function oj(n){return function(){var i=n.apply(this,arguments);this.textContent=i??""}}function cj(n){return arguments.length?this.each(n==null?rj:(typeof n=="function"?oj:lj)(n)):this.node().textContent}function dj(){this.innerHTML=""}function uj(n){return function(){this.innerHTML=n}}function fj(n){return function(){var i=n.apply(this,arguments);this.innerHTML=i??""}}function hj(n){return arguments.length?this.each(n==null?dj:(typeof n=="function"?fj:uj)(n)):this.node().innerHTML}function mj(){this.nextSibling&&this.parentNode.appendChild(this)}function pj(){return this.each(mj)}function gj(){this.previousSibling&&this.parentNode.insertBefore(this,this.parentNode.firstChild)}function xj(){return this.each(gj)}function vj(n){var i=typeof n=="function"?n:Ug(n);return this.select(function(){return this.appendChild(i.apply(this,arguments))})}function yj(){return null}function bj(n,i){var l=typeof n=="function"?n:Ug(n),o=i==null?yj:typeof i=="function"?i:yu(i);return this.select(function(){return this.insertBefore(l.apply(this,arguments),o.apply(this,arguments)||null)})}function jj(){var n=this.parentNode;n&&n.removeChild(this)}function Nj(){return this.each(jj)}function wj(){var n=this.cloneNode(!1),i=this.parentNode;return i?i.insertBefore(n,this.nextSibling):n}function _j(){var n=this.cloneNode(!0),i=this.parentNode;return i?i.insertBefore(n,this.nextSibling):n}function Sj(n){return this.select(n?_j:wj)}function Tj(n){return arguments.length?this.property("__data__",n):this.node().__data__}function Cj(n){return function(i){n.call(this,i,this.__data__)}}function Aj(n){return n.trim().split(/^|\s+/).map(function(i){var l="",o=i.indexOf(".");return o>=0&&(l=i.slice(o+1),i=i.slice(0,o)),{type:i,name:l}})}function zj(n){return function(){var i=this.__on;if(i){for(var l=0,o=-1,u=i.length,f;l<u;++l)f=i[l],(!n.type||f.type===n.type)&&f.name===n.name?this.removeEventListener(f.type,f.listener,f.options):i[++o]=f;++o?i.length=o:delete this.__on}}}function kj(n,i,l){return function(){var o=this.__on,u,f=Cj(i);if(o){for(var m=0,x=o.length;m<x;++m)if((u=o[m]).type===n.type&&u.name===n.name){this.removeEventListener(u.type,u.listener,u.options),this.addEventListener(u.type,u.listener=f,u.options=l),u.value=i;return}}this.addEventListener(n.type,f,l),u={type:n.type,name:n.name,value:i,listener:f,options:l},o?o.push(u):this.__on=[u]}}function Ej(n,i,l){var o=Aj(n+""),u,f=o.length,m;if(arguments.length<2){var x=this.node().__on;if(x){for(var p=0,h=x.length,v;p<h;++p)for(u=0,v=x[p];u<f;++u)if((m=o[u]).type===v.type&&m.name===v.name)return v.value}return}for(x=i?kj:zj,u=0;u<f;++u)this.each(x(o[u],i,l));return this}function Pg(n,i,l){var o=Ig(n),u=o.CustomEvent;typeof u=="function"?u=new u(i,l):(u=o.document.createEvent("Event"),l?(u.initEvent(i,l.bubbles,l.cancelable),u.detail=l.detail):u.initEvent(i,!1,!1)),n.dispatchEvent(u)}function Mj(n,i){return function(){return Pg(this,n,i)}}function Dj(n,i){return function(){return Pg(this,n,i.apply(this,arguments))}}function Rj(n,i){return this.each((typeof i=="function"?Dj:Mj)(n,i))}function*Uj(){for(var n=this._groups,i=0,l=n.length;i<l;++i)for(var o=n[i],u=0,f=o.length,m;u<f;++u)(m=o[u])&&(yield m)}var ju=[null];function Ma(n,i){this._groups=n,this._parents=i}function Kr(){return new Ma([[document.documentElement]],ju)}function Oj(){return this}Ma.prototype=Kr.prototype={constructor:Ma,select:cb,selectAll:fb,selectChild:gb,selectChildren:bb,filter:jb,data:Cb,enter:Nb,exit:zb,join:kb,merge:Eb,selection:Oj,order:Mb,sort:Db,call:Ub,nodes:Ob,node:Lb,size:qb,empty:Bb,each:Hb,attr:Vb,style:Jb,property:tj,classed:ij,text:cj,html:hj,raise:pj,lower:xj,append:vj,insert:bj,remove:Nj,clone:Sj,datum:Tj,on:Ej,dispatch:Rj,[Symbol.iterator]:Uj};function hn(n){return typeof n=="string"?new Ma([[document.querySelector(n)]],[document.documentElement]):new Ma([[n]],ju)}function Lj(n){return typeof n=="string"?new Ma([document.querySelectorAll(n)],[document.documentElement]):new Ma([Og(n)],ju)}function Nu(n,i,l){n.prototype=i.prototype=l,l.constructor=n}function Vg(n,i){var l=Object.create(n.prototype);for(var o in i)l[o]=i[o];return l}function Wr(){}var Pr=.7,vo=1/Pr,Ri="\\s*([+-]?\\d+)\\s*",Vr="\\s*([+-]?(?:\\d*\\.)?\\d+(?:[eE][+-]?\\d+)?)\\s*",wn="\\s*([+-]?(?:\\d*\\.)?\\d+(?:[eE][+-]?\\d+)?)%\\s*",qj=/^#([0-9a-f]{3,8})$/,Bj=new RegExp(`^rgb\\(${Ri},${Ri},${Ri}\\)$`),Hj=new RegExp(`^rgb\\(${wn},${wn},${wn}\\)$`),Ij=new RegExp(`^rgba\\(${Ri},${Ri},${Ri},${Vr}\\)$`),$j=new RegExp(`^rgba\\(${wn},${wn},${wn},${Vr}\\)$`),Fj=new RegExp(`^hsl\\(${Vr},${wn},${wn}\\)$`),Yj=new RegExp(`^hsla\\(${Vr},${wn},${wn},${Vr}\\)$`),Ep={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074};Nu(Wr,Vs,{copy(n){return Object.assign(new this.constructor,this,n)},displayable(){return this.rgb().displayable()},hex:Mp,formatHex:Mp,formatHex8:Gj,formatHsl:Pj,formatRgb:Dp,toString:Dp});function Mp(){return this.rgb().formatHex()}function Gj(){return this.rgb().formatHex8()}function Pj(){return Xg(this).formatHsl()}function Dp(){return this.rgb().formatRgb()}function Vs(n){var i,l;return n=(n+"").trim().toLowerCase(),(i=qj.exec(n))?(l=i[1].length,i=parseInt(i[1],16),l===6?Rp(i):l===3?new Ba(i>>8&15|i>>4&240,i>>4&15|i&240,(i&15)<<4|i&15,1):l===8?ro(i>>24&255,i>>16&255,i>>8&255,(i&255)/255):l===4?ro(i>>12&15|i>>8&240,i>>8&15|i>>4&240,i>>4&15|i&240,((i&15)<<4|i&15)/255):null):(i=Bj.exec(n))?new Ba(i[1],i[2],i[3],1):(i=Hj.exec(n))?new Ba(i[1]*255/100,i[2]*255/100,i[3]*255/100,1):(i=Ij.exec(n))?ro(i[1],i[2],i[3],i[4]):(i=$j.exec(n))?ro(i[1]*255/100,i[2]*255/100,i[3]*255/100,i[4]):(i=Fj.exec(n))?Lp(i[1],i[2]/100,i[3]/100,1):(i=Yj.exec(n))?Lp(i[1],i[2]/100,i[3]/100,i[4]):Ep.hasOwnProperty(n)?Rp(Ep[n]):n==="transparent"?new Ba(NaN,NaN,NaN,0):null}function Rp(n){return new Ba(n>>16&255,n>>8&255,n&255,1)}function ro(n,i,l,o){return o<=0&&(n=i=l=NaN),new Ba(n,i,l,o)}function Vj(n){return n instanceof Wr||(n=Vs(n)),n?(n=n.rgb(),new Ba(n.r,n.g,n.b,n.opacity)):new Ba}function ru(n,i,l,o){return arguments.length===1?Vj(n):new Ba(n,i,l,o??1)}function Ba(n,i,l,o){this.r=+n,this.g=+i,this.b=+l,this.opacity=+o}Nu(Ba,ru,Vg(Wr,{brighter(n){return n=n==null?vo:Math.pow(vo,n),new Ba(this.r*n,this.g*n,this.b*n,this.opacity)},darker(n){return n=n==null?Pr:Math.pow(Pr,n),new Ba(this.r*n,this.g*n,this.b*n,this.opacity)},rgb(){return this},clamp(){return new Ba(Ps(this.r),Ps(this.g),Ps(this.b),yo(this.opacity))},displayable(){return-.5<=this.r&&this.r<255.5&&-.5<=this.g&&this.g<255.5&&-.5<=this.b&&this.b<255.5&&0<=this.opacity&&this.opacity<=1},hex:Up,formatHex:Up,formatHex8:Xj,formatRgb:Op,toString:Op}));function Up(){return`#${Ys(this.r)}${Ys(this.g)}${Ys(this.b)}`}function Xj(){return`#${Ys(this.r)}${Ys(this.g)}${Ys(this.b)}${Ys((isNaN(this.opacity)?1:this.opacity)*255)}`}function Op(){const n=yo(this.opacity);return`${n===1?"rgb(":"rgba("}${Ps(this.r)}, ${Ps(this.g)}, ${Ps(this.b)}${n===1?")":`, ${n})`}`}function yo(n){return isNaN(n)?1:Math.max(0,Math.min(1,n))}function Ps(n){return Math.max(0,Math.min(255,Math.round(n)||0))}function Ys(n){return n=Ps(n),(n<16?"0":"")+n.toString(16)}function Lp(n,i,l,o){return o<=0?n=i=l=NaN:l<=0||l>=1?n=i=NaN:i<=0&&(n=NaN),new pn(n,i,l,o)}function Xg(n){if(n instanceof pn)return new pn(n.h,n.s,n.l,n.opacity);if(n instanceof Wr||(n=Vs(n)),!n)return new pn;if(n instanceof pn)return n;n=n.rgb();var i=n.r/255,l=n.g/255,o=n.b/255,u=Math.min(i,l,o),f=Math.max(i,l,o),m=NaN,x=f-u,p=(f+u)/2;return x?(i===f?m=(l-o)/x+(l<o)*6:l===f?m=(o-i)/x+2:m=(i-l)/x+4,x/=p<.5?f+u:2-f-u,m*=60):x=p>0&&p<1?0:m,new pn(m,x,p,n.opacity)}function Zj(n,i,l,o){return arguments.length===1?Xg(n):new pn(n,i,l,o??1)}function pn(n,i,l,o){this.h=+n,this.s=+i,this.l=+l,this.opacity=+o}Nu(pn,Zj,Vg(Wr,{brighter(n){return n=n==null?vo:Math.pow(vo,n),new pn(this.h,this.s,this.l*n,this.opacity)},darker(n){return n=n==null?Pr:Math.pow(Pr,n),new pn(this.h,this.s,this.l*n,this.opacity)},rgb(){var n=this.h%360+(this.h<0)*360,i=isNaN(n)||isNaN(this.s)?0:this.s,l=this.l,o=l+(l<.5?l:1-l)*i,u=2*l-o;return new Ba(Fd(n>=240?n-240:n+120,u,o),Fd(n,u,o),Fd(n<120?n+240:n-120,u,o),this.opacity)},clamp(){return new pn(qp(this.h),lo(this.s),lo(this.l),yo(this.opacity))},displayable(){return(0<=this.s&&this.s<=1||isNaN(this.s))&&0<=this.l&&this.l<=1&&0<=this.opacity&&this.opacity<=1},formatHsl(){const n=yo(this.opacity);return`${n===1?"hsl(":"hsla("}${qp(this.h)}, ${lo(this.s)*100}%, ${lo(this.l)*100}%${n===1?")":`, ${n})`}`}}));function qp(n){return n=(n||0)%360,n<0?n+360:n}function lo(n){return Math.max(0,Math.min(1,n||0))}function Fd(n,i,l){return(n<60?i+(l-i)*n/60:n<180?l:n<240?i+(l-i)*(240-n)/60:i)*255}const wu=n=>()=>n;function Qj(n,i){return function(l){return n+l*i}}function Jj(n,i,l){return n=Math.pow(n,l),i=Math.pow(i,l)-n,l=1/l,function(o){return Math.pow(n+o*i,l)}}function Kj(n){return(n=+n)==1?Zg:function(i,l){return l-i?Jj(i,l,n):wu(isNaN(i)?l:i)}}function Zg(n,i){var l=i-n;return l?Qj(n,l):wu(isNaN(n)?i:n)}const bo=(function n(i){var l=Kj(i);function o(u,f){var m=l((u=ru(u)).r,(f=ru(f)).r),x=l(u.g,f.g),p=l(u.b,f.b),h=Zg(u.opacity,f.opacity);return function(v){return u.r=m(v),u.g=x(v),u.b=p(v),u.opacity=h(v),u+""}}return o.gamma=n,o})(1);function Wj(n,i){i||(i=[]);var l=n?Math.min(i.length,n.length):0,o=i.slice(),u;return function(f){for(u=0;u<l;++u)o[u]=n[u]*(1-f)+i[u]*f;return o}}function e1(n){return ArrayBuffer.isView(n)&&!(n instanceof DataView)}function t1(n,i){var l=i?i.length:0,o=n?Math.min(l,n.length):0,u=new Array(o),f=new Array(l),m;for(m=0;m<o;++m)u[m]=_u(n[m],i[m]);for(;m<l;++m)f[m]=i[m];return function(x){for(m=0;m<o;++m)f[m]=u[m](x);return f}}function a1(n,i){var l=new Date;return n=+n,i=+i,function(o){return l.setTime(n*(1-o)+i*o),l}}function mn(n,i){return n=+n,i=+i,function(l){return n*(1-l)+i*l}}function n1(n,i){var l={},o={},u;(n===null||typeof n!="object")&&(n={}),(i===null||typeof i!="object")&&(i={});for(u in i)u in n?l[u]=_u(n[u],i[u]):o[u]=i[u];return function(f){for(u in l)o[u]=l[u](f);return o}}var lu=/[-+]?(?:\d+\.?\d*|\.?\d+)(?:[eE][-+]?\d+)?/g,Yd=new RegExp(lu.source,"g");function s1(n){return function(){return n}}function i1(n){return function(i){return n(i)+""}}function Qg(n,i){var l=lu.lastIndex=Yd.lastIndex=0,o,u,f,m=-1,x=[],p=[];for(n=n+"",i=i+"";(o=lu.exec(n))&&(u=Yd.exec(i));)(f=u.index)>l&&(f=i.slice(l,f),x[m]?x[m]+=f:x[++m]=f),(o=o[0])===(u=u[0])?x[m]?x[m]+=u:x[++m]=u:(x[++m]=null,p.push({i:m,x:mn(o,u)})),l=Yd.lastIndex;return l<i.length&&(f=i.slice(l),x[m]?x[m]+=f:x[++m]=f),x.length<2?p[0]?i1(p[0].x):s1(i):(i=p.length,function(h){for(var v=0,y;v<i;++v)x[(y=p[v]).i]=y.x(h);return x.join("")})}function _u(n,i){var l=typeof i,o;return i==null||l==="boolean"?wu(i):(l==="number"?mn:l==="string"?(o=Vs(i))?(i=o,bo):Qg:i instanceof Vs?bo:i instanceof Date?a1:e1(i)?Wj:Array.isArray(i)?t1:typeof i.valueOf!="function"&&typeof i.toString!="function"||isNaN(i)?n1:mn)(n,i)}function r1(n,i){return n=+n,i=+i,function(l){return Math.round(n*(1-l)+i*l)}}var Bp=180/Math.PI,ou={translateX:0,translateY:0,rotate:0,skewX:0,scaleX:1,scaleY:1};function Jg(n,i,l,o,u,f){var m,x,p;return(m=Math.sqrt(n*n+i*i))&&(n/=m,i/=m),(p=n*l+i*o)&&(l-=n*p,o-=i*p),(x=Math.sqrt(l*l+o*o))&&(l/=x,o/=x,p/=x),n*o<i*l&&(n=-n,i=-i,p=-p,m=-m),{translateX:u,translateY:f,rotate:Math.atan2(i,n)*Bp,skewX:Math.atan(p)*Bp,scaleX:m,scaleY:x}}var oo;function l1(n){const i=new(typeof DOMMatrix=="function"?DOMMatrix:WebKitCSSMatrix)(n+"");return i.isIdentity?ou:Jg(i.a,i.b,i.c,i.d,i.e,i.f)}function o1(n){return n==null||(oo||(oo=document.createElementNS("http://www.w3.org/2000/svg","g")),oo.setAttribute("transform",n),!(n=oo.transform.baseVal.consolidate()))?ou:(n=n.matrix,Jg(n.a,n.b,n.c,n.d,n.e,n.f))}function Kg(n,i,l,o){function u(h){return h.length?h.pop()+" ":""}function f(h,v,y,N,S,A){if(h!==y||v!==N){var z=S.push("translate(",null,i,null,l);A.push({i:z-4,x:mn(h,y)},{i:z-2,x:mn(v,N)})}else(y||N)&&S.push("translate("+y+i+N+l)}function m(h,v,y,N){h!==v?(h-v>180?v+=360:v-h>180&&(h+=360),N.push({i:y.push(u(y)+"rotate(",null,o)-2,x:mn(h,v)})):v&&y.push(u(y)+"rotate("+v+o)}function x(h,v,y,N){h!==v?N.push({i:y.push(u(y)+"skewX(",null,o)-2,x:mn(h,v)}):v&&y.push(u(y)+"skewX("+v+o)}function p(h,v,y,N,S,A){if(h!==y||v!==N){var z=S.push(u(S)+"scale(",null,",",null,")");A.push({i:z-4,x:mn(h,y)},{i:z-2,x:mn(v,N)})}else(y!==1||N!==1)&&S.push(u(S)+"scale("+y+","+N+")")}return function(h,v){var y=[],N=[];return h=n(h),v=n(v),f(h.translateX,h.translateY,v.translateX,v.translateY,y,N),m(h.rotate,v.rotate,y,N),x(h.skewX,v.skewX,y,N),p(h.scaleX,h.scaleY,v.scaleX,v.scaleY,y,N),h=v=null,function(S){for(var A=-1,z=N.length,U;++A<z;)y[(U=N[A]).i]=U.x(S);return y.join("")}}}var c1=Kg(l1,"px, ","px)","deg)"),d1=Kg(o1,", ",")",")"),Li=0,Ir=0,Or=0,Wg=1e3,jo,$r,No=0,Xs=0,Ro=0,Xr=typeof performance=="object"&&performance.now?performance:Date,ex=typeof window=="object"&&window.requestAnimationFrame?window.requestAnimationFrame.bind(window):function(n){setTimeout(n,17)};function Su(){return Xs||(ex(u1),Xs=Xr.now()+Ro)}function u1(){Xs=0}function wo(){this._call=this._time=this._next=null}wo.prototype=tx.prototype={constructor:wo,restart:function(n,i,l){if(typeof n!="function")throw new TypeError("callback is not a function");l=(l==null?Su():+l)+(i==null?0:+i),!this._next&&$r!==this&&($r?$r._next=this:jo=this,$r=this),this._call=n,this._time=l,cu()},stop:function(){this._call&&(this._call=null,this._time=1/0,cu())}};function tx(n,i,l){var o=new wo;return o.restart(n,i,l),o}function f1(){Su(),++Li;for(var n=jo,i;n;)(i=Xs-n._time)>=0&&n._call.call(void 0,i),n=n._next;--Li}function Hp(){Xs=(No=Xr.now())+Ro,Li=Ir=0;try{f1()}finally{Li=0,m1(),Xs=0}}function h1(){var n=Xr.now(),i=n-No;i>Wg&&(Ro-=i,No=n)}function m1(){for(var n,i=jo,l,o=1/0;i;)i._call?(o>i._time&&(o=i._time),n=i,i=i._next):(l=i._next,i._next=null,i=n?n._next=l:jo=l);$r=n,cu(o)}function cu(n){if(!Li){Ir&&(Ir=clearTimeout(Ir));var i=n-Xs;i>24?(n<1/0&&(Ir=setTimeout(Hp,n-Xr.now()-Ro)),Or&&(Or=clearInterval(Or))):(Or||(No=Xr.now(),Or=setInterval(h1,Wg)),Li=1,ex(Hp))}}function Ip(n,i,l){var o=new wo;return i=i==null?0:+i,o.restart(u=>{o.stop(),n(u+i)},i,l),o}var p1=Rg("start","end","cancel","interrupt"),g1=[],ax=0,$p=1,du=2,mo=3,Fp=4,uu=5,po=6;function Uo(n,i,l,o,u,f){var m=n.__transition;if(!m)n.__transition={};else if(l in m)return;x1(n,l,{name:i,index:o,group:u,on:p1,tween:g1,time:f.time,delay:f.delay,duration:f.duration,ease:f.ease,timer:null,state:ax})}function Tu(n,i){var l=gn(n,i);if(l.state>ax)throw new Error("too late; already scheduled");return l}function _n(n,i){var l=gn(n,i);if(l.state>mo)throw new Error("too late; already running");return l}function gn(n,i){var l=n.__transition;if(!l||!(l=l[i]))throw new Error("transition not found");return l}function x1(n,i,l){var o=n.__transition,u;o[i]=l,l.timer=tx(f,0,l.time);function f(h){l.state=$p,l.timer.restart(m,l.delay,l.time),l.delay<=h&&m(h-l.delay)}function m(h){var v,y,N,S;if(l.state!==$p)return p();for(v in o)if(S=o[v],S.name===l.name){if(S.state===mo)return Ip(m);S.state===Fp?(S.state=po,S.timer.stop(),S.on.call("interrupt",n,n.__data__,S.index,S.group),delete o[v]):+v<i&&(S.state=po,S.timer.stop(),S.on.call("cancel",n,n.__data__,S.index,S.group),delete o[v])}if(Ip(function(){l.state===mo&&(l.state=Fp,l.timer.restart(x,l.delay,l.time),x(h))}),l.state=du,l.on.call("start",n,n.__data__,l.index,l.group),l.state===du){for(l.state=mo,u=new Array(N=l.tween.length),v=0,y=-1;v<N;++v)(S=l.tween[v].value.call(n,n.__data__,l.index,l.group))&&(u[++y]=S);u.length=y+1}}function x(h){for(var v=h<l.duration?l.ease.call(null,h/l.duration):(l.timer.restart(p),l.state=uu,1),y=-1,N=u.length;++y<N;)u[y].call(n,v);l.state===uu&&(l.on.call("end",n,n.__data__,l.index,l.group),p())}function p(){l.state=po,l.timer.stop(),delete o[i];for(var h in o)return;delete n.__transition}}function v1(n,i){var l=n.__transition,o,u,f=!0,m;if(l){i=i==null?null:i+"";for(m in l){if((o=l[m]).name!==i){f=!1;continue}u=o.state>du&&o.state<uu,o.state=po,o.timer.stop(),o.on.call(u?"interrupt":"cancel",n,n.__data__,o.index,o.group),delete l[m]}f&&delete n.__transition}}function y1(n){return this.each(function(){v1(this,n)})}function b1(n,i){var l,o;return function(){var u=_n(this,n),f=u.tween;if(f!==l){o=l=f;for(var m=0,x=o.length;m<x;++m)if(o[m].name===i){o=o.slice(),o.splice(m,1);break}}u.tween=o}}function j1(n,i,l){var o,u;if(typeof l!="function")throw new Error;return function(){var f=_n(this,n),m=f.tween;if(m!==o){u=(o=m).slice();for(var x={name:i,value:l},p=0,h=u.length;p<h;++p)if(u[p].name===i){u[p]=x;break}p===h&&u.push(x)}f.tween=u}}function N1(n,i){var l=this._id;if(n+="",arguments.length<2){for(var o=gn(this.node(),l).tween,u=0,f=o.length,m;u<f;++u)if((m=o[u]).name===n)return m.value;return null}return this.each((i==null?b1:j1)(l,n,i))}function Cu(n,i,l){var o=n._id;return n.each(function(){var u=_n(this,o);(u.value||(u.value={}))[i]=l.apply(this,arguments)}),function(u){return gn(u,o).value[i]}}function nx(n,i){var l;return(typeof i=="number"?mn:i instanceof Vs?bo:(l=Vs(i))?(i=l,bo):Qg)(n,i)}function w1(n){return function(){this.removeAttribute(n)}}function _1(n){return function(){this.removeAttributeNS(n.space,n.local)}}function S1(n,i,l){var o,u=l+"",f;return function(){var m=this.getAttribute(n);return m===u?null:m===o?f:f=i(o=m,l)}}function T1(n,i,l){var o,u=l+"",f;return function(){var m=this.getAttributeNS(n.space,n.local);return m===u?null:m===o?f:f=i(o=m,l)}}function C1(n,i,l){var o,u,f;return function(){var m,x=l(this),p;return x==null?void this.removeAttribute(n):(m=this.getAttribute(n),p=x+"",m===p?null:m===o&&p===u?f:(u=p,f=i(o=m,x)))}}function A1(n,i,l){var o,u,f;return function(){var m,x=l(this),p;return x==null?void this.removeAttributeNS(n.space,n.local):(m=this.getAttributeNS(n.space,n.local),p=x+"",m===p?null:m===o&&p===u?f:(u=p,f=i(o=m,x)))}}function z1(n,i){var l=Do(n),o=l==="transform"?d1:nx;return this.attrTween(n,typeof i=="function"?(l.local?A1:C1)(l,o,Cu(this,"attr."+n,i)):i==null?(l.local?_1:w1)(l):(l.local?T1:S1)(l,o,i))}function k1(n,i){return function(l){this.setAttribute(n,i.call(this,l))}}function E1(n,i){return function(l){this.setAttributeNS(n.space,n.local,i.call(this,l))}}function M1(n,i){var l,o;function u(){var f=i.apply(this,arguments);return f!==o&&(l=(o=f)&&E1(n,f)),l}return u._value=i,u}function D1(n,i){var l,o;function u(){var f=i.apply(this,arguments);return f!==o&&(l=(o=f)&&k1(n,f)),l}return u._value=i,u}function R1(n,i){var l="attr."+n;if(arguments.length<2)return(l=this.tween(l))&&l._value;if(i==null)return this.tween(l,null);if(typeof i!="function")throw new Error;var o=Do(n);return this.tween(l,(o.local?M1:D1)(o,i))}function U1(n,i){return function(){Tu(this,n).delay=+i.apply(this,arguments)}}function O1(n,i){return i=+i,function(){Tu(this,n).delay=i}}function L1(n){var i=this._id;return arguments.length?this.each((typeof n=="function"?U1:O1)(i,n)):gn(this.node(),i).delay}function q1(n,i){return function(){_n(this,n).duration=+i.apply(this,arguments)}}function B1(n,i){return i=+i,function(){_n(this,n).duration=i}}function H1(n){var i=this._id;return arguments.length?this.each((typeof n=="function"?q1:B1)(i,n)):gn(this.node(),i).duration}function I1(n,i){if(typeof i!="function")throw new Error;return function(){_n(this,n).ease=i}}function $1(n){var i=this._id;return arguments.length?this.each(I1(i,n)):gn(this.node(),i).ease}function F1(n,i){return function(){var l=i.apply(this,arguments);if(typeof l!="function")throw new Error;_n(this,n).ease=l}}function Y1(n){if(typeof n!="function")throw new Error;return this.each(F1(this._id,n))}function G1(n){typeof n!="function"&&(n=qg(n));for(var i=this._groups,l=i.length,o=new Array(l),u=0;u<l;++u)for(var f=i[u],m=f.length,x=o[u]=[],p,h=0;h<m;++h)(p=f[h])&&n.call(p,p.__data__,h,f)&&x.push(p);return new Xn(o,this._parents,this._name,this._id)}function P1(n){if(n._id!==this._id)throw new Error;for(var i=this._groups,l=n._groups,o=i.length,u=l.length,f=Math.min(o,u),m=new Array(o),x=0;x<f;++x)for(var p=i[x],h=l[x],v=p.length,y=m[x]=new Array(v),N,S=0;S<v;++S)(N=p[S]||h[S])&&(y[S]=N);for(;x<o;++x)m[x]=i[x];return new Xn(m,this._parents,this._name,this._id)}function V1(n){return(n+"").trim().split(/^|\s+/).every(function(i){var l=i.indexOf(".");return l>=0&&(i=i.slice(0,l)),!i||i==="start"})}function X1(n,i,l){var o,u,f=V1(i)?Tu:_n;return function(){var m=f(this,n),x=m.on;x!==o&&(u=(o=x).copy()).on(i,l),m.on=u}}function Z1(n,i){var l=this._id;return arguments.length<2?gn(this.node(),l).on.on(n):this.each(X1(l,n,i))}function Q1(n){return function(){var i=this.parentNode;for(var l in this.__transition)if(+l!==n)return;i&&i.removeChild(this)}}function J1(){return this.on("end.remove",Q1(this._id))}function K1(n){var i=this._name,l=this._id;typeof n!="function"&&(n=yu(n));for(var o=this._groups,u=o.length,f=new Array(u),m=0;m<u;++m)for(var x=o[m],p=x.length,h=f[m]=new Array(p),v,y,N=0;N<p;++N)(v=x[N])&&(y=n.call(v,v.__data__,N,x))&&("__data__"in v&&(y.__data__=v.__data__),h[N]=y,Uo(h[N],i,l,N,h,gn(v,l)));return new Xn(f,this._parents,i,l)}function W1(n){var i=this._name,l=this._id;typeof n!="function"&&(n=Lg(n));for(var o=this._groups,u=o.length,f=[],m=[],x=0;x<u;++x)for(var p=o[x],h=p.length,v,y=0;y<h;++y)if(v=p[y]){for(var N=n.call(v,v.__data__,y,p),S,A=gn(v,l),z=0,U=N.length;z<U;++z)(S=N[z])&&Uo(S,i,l,z,N,A);f.push(N),m.push(v)}return new Xn(f,m,i,l)}var eN=Kr.prototype.constructor;function tN(){return new eN(this._groups,this._parents)}function aN(n,i){var l,o,u;return function(){var f=Oi(this,n),m=(this.style.removeProperty(n),Oi(this,n));return f===m?null:f===l&&m===o?u:u=i(l=f,o=m)}}function sx(n){return function(){this.style.removeProperty(n)}}function nN(n,i,l){var o,u=l+"",f;return function(){var m=Oi(this,n);return m===u?null:m===o?f:f=i(o=m,l)}}function sN(n,i,l){var o,u,f;return function(){var m=Oi(this,n),x=l(this),p=x+"";return x==null&&(p=x=(this.style.removeProperty(n),Oi(this,n))),m===p?null:m===o&&p===u?f:(u=p,f=i(o=m,x))}}function iN(n,i){var l,o,u,f="style."+i,m="end."+f,x;return function(){var p=_n(this,n),h=p.on,v=p.value[f]==null?x||(x=sx(i)):void 0;(h!==l||u!==v)&&(o=(l=h).copy()).on(m,u=v),p.on=o}}function rN(n,i,l){var o=(n+="")=="transform"?c1:nx;return i==null?this.styleTween(n,aN(n,o)).on("end.style."+n,sx(n)):typeof i=="function"?this.styleTween(n,sN(n,o,Cu(this,"style."+n,i))).each(iN(this._id,n)):this.styleTween(n,nN(n,o,i),l).on("end.style."+n,null)}function lN(n,i,l){return function(o){this.style.setProperty(n,i.call(this,o),l)}}function oN(n,i,l){var o,u;function f(){var m=i.apply(this,arguments);return m!==u&&(o=(u=m)&&lN(n,m,l)),o}return f._value=i,f}function cN(n,i,l){var o="style."+(n+="");if(arguments.length<2)return(o=this.tween(o))&&o._value;if(i==null)return this.tween(o,null);if(typeof i!="function")throw new Error;return this.tween(o,oN(n,i,l??""))}function dN(n){return function(){this.textContent=n}}function uN(n){return function(){var i=n(this);this.textContent=i??""}}function fN(n){return this.tween("text",typeof n=="function"?uN(Cu(this,"text",n)):dN(n==null?"":n+""))}function hN(n){return function(i){this.textContent=n.call(this,i)}}function mN(n){var i,l;function o(){var u=n.apply(this,arguments);return u!==l&&(i=(l=u)&&hN(u)),i}return o._value=n,o}function pN(n){var i="text";if(arguments.length<1)return(i=this.tween(i))&&i._value;if(n==null)return this.tween(i,null);if(typeof n!="function")throw new Error;return this.tween(i,mN(n))}function gN(){for(var n=this._name,i=this._id,l=ix(),o=this._groups,u=o.length,f=0;f<u;++f)for(var m=o[f],x=m.length,p,h=0;h<x;++h)if(p=m[h]){var v=gn(p,i);Uo(p,n,l,h,m,{time:v.time+v.delay+v.duration,delay:0,duration:v.duration,ease:v.ease})}return new Xn(o,this._parents,n,l)}function xN(){var n,i,l=this,o=l._id,u=l.size();return new Promise(function(f,m){var x={value:m},p={value:function(){--u===0&&f()}};l.each(function(){var h=_n(this,o),v=h.on;v!==n&&(i=(n=v).copy(),i._.cancel.push(x),i._.interrupt.push(x),i._.end.push(p)),h.on=i}),u===0&&f()})}var vN=0;function Xn(n,i,l,o){this._groups=n,this._parents=i,this._name=l,this._id=o}function ix(){return++vN}var Gn=Kr.prototype;Xn.prototype={constructor:Xn,select:K1,selectAll:W1,selectChild:Gn.selectChild,selectChildren:Gn.selectChildren,filter:G1,merge:P1,selection:tN,transition:gN,call:Gn.call,nodes:Gn.nodes,node:Gn.node,size:Gn.size,empty:Gn.empty,each:Gn.each,on:Z1,attr:z1,attrTween:R1,style:rN,styleTween:cN,text:fN,textTween:pN,remove:J1,tween:N1,delay:L1,duration:H1,ease:$1,easeVarying:Y1,end:xN,[Symbol.iterator]:Gn[Symbol.iterator]};function yN(n){return((n*=2)<=1?n*n*n:(n-=2)*n*n+2)/2}var bN={time:null,delay:0,duration:250,ease:yN};function jN(n,i){for(var l;!(l=n.__transition)||!(l=l[i]);)if(!(n=n.parentNode))throw new Error(`transition ${i} not found`);return l}function NN(n){var i,l;n instanceof Xn?(i=n._id,n=n._name):(i=ix(),(l=bN).time=Su(),n=n==null?null:n+"");for(var o=this._groups,u=o.length,f=0;f<u;++f)for(var m=o[f],x=m.length,p,h=0;h<x;++h)(p=m[h])&&Uo(p,n,i,h,m,l||jN(p,i));return new Xn(o,this._parents,n,i)}Kr.prototype.interrupt=y1;Kr.prototype.transition=NN;const fu=Math.PI,hu=2*fu,Fs=1e-6,wN=hu-Fs;function rx(n){this._+=n[0];for(let i=1,l=n.length;i<l;++i)this._+=arguments[i]+n[i]}function _N(n){let i=Math.floor(n);if(!(i>=0))throw new Error(`invalid digits: ${n}`);if(i>15)return rx;const l=10**i;return function(o){this._+=o[0];for(let u=1,f=o.length;u<f;++u)this._+=Math.round(arguments[u]*l)/l+o[u]}}class SN{constructor(i){this._x0=this._y0=this._x1=this._y1=null,this._="",this._append=i==null?rx:_N(i)}moveTo(i,l){this._append`M${this._x0=this._x1=+i},${this._y0=this._y1=+l}`}closePath(){this._x1!==null&&(this._x1=this._x0,this._y1=this._y0,this._append`Z`)}lineTo(i,l){this._append`L${this._x1=+i},${this._y1=+l}`}quadraticCurveTo(i,l,o,u){this._append`Q${+i},${+l},${this._x1=+o},${this._y1=+u}`}bezierCurveTo(i,l,o,u,f,m){this._append`C${+i},${+l},${+o},${+u},${this._x1=+f},${this._y1=+m}`}arcTo(i,l,o,u,f){if(i=+i,l=+l,o=+o,u=+u,f=+f,f<0)throw new Error(`negative radius: ${f}`);let m=this._x1,x=this._y1,p=o-i,h=u-l,v=m-i,y=x-l,N=v*v+y*y;if(this._x1===null)this._append`M${this._x1=i},${this._y1=l}`;else if(N>Fs)if(!(Math.abs(y*p-h*v)>Fs)||!f)this._append`L${this._x1=i},${this._y1=l}`;else{let S=o-m,A=u-x,z=p*p+h*h,U=S*S+A*A,oe=Math.sqrt(z),ie=Math.sqrt(N),me=f*Math.tan((fu-Math.acos((z+N-U)/(2*oe*ie)))/2),Ae=me/ie,de=me/oe;Math.abs(Ae-1)>Fs&&this._append`L${i+Ae*v},${l+Ae*y}`,this._append`A${f},${f},0,0,${+(y*S>v*A)},${this._x1=i+de*p},${this._y1=l+de*h}`}}arc(i,l,o,u,f,m){if(i=+i,l=+l,o=+o,m=!!m,o<0)throw new Error(`negative radius: ${o}`);let x=o*Math.cos(u),p=o*Math.sin(u),h=i+x,v=l+p,y=1^m,N=m?u-f:f-u;this._x1===null?this._append`M${h},${v}`:(Math.abs(this._x1-h)>Fs||Math.abs(this._y1-v)>Fs)&&this._append`L${h},${v}`,o&&(N<0&&(N=N%hu+hu),N>wN?this._append`A${o},${o},0,1,${y},${i-x},${l-p}A${o},${o},0,1,${y},${this._x1=h},${this._y1=v}`:N>Fs&&this._append`A${o},${o},0,${+(N>=fu)},${y},${this._x1=i+o*Math.cos(f)},${this._y1=l+o*Math.sin(f)}`)}rect(i,l,o,u){this._append`M${this._x0=this._x1=+i},${this._y0=this._y1=+l}h${o=+o}v${+u}h${-o}Z`}toString(){return this._}}function TN(n){return Math.abs(n=Math.round(n))>=1e21?n.toLocaleString("en").replace(/,/g,""):n.toString(10)}function _o(n,i){if((l=(n=i?n.toExponential(i-1):n.toExponential()).indexOf("e"))<0)return null;var l,o=n.slice(0,l);return[o.length>1?o[0]+o.slice(2):o,+n.slice(l+1)]}function qi(n){return n=_o(Math.abs(n)),n?n[1]:NaN}function CN(n,i){return function(l,o){for(var u=l.length,f=[],m=0,x=n[0],p=0;u>0&&x>0&&(p+x+1>o&&(x=Math.max(1,o-p)),f.push(l.substring(u-=x,u+x)),!((p+=x+1)>o));)x=n[m=(m+1)%n.length];return f.reverse().join(i)}}function AN(n){return function(i){return i.replace(/[0-9]/g,function(l){return n[+l]})}}var zN=/^(?:(.)?([<>=^]))?([+\-( ])?([$#])?(0)?(\d+)?(,)?(\.\d+)?(~)?([a-z%])?$/i;function So(n){if(!(i=zN.exec(n)))throw new Error("invalid format: "+n);var i;return new Au({fill:i[1],align:i[2],sign:i[3],symbol:i[4],zero:i[5],width:i[6],comma:i[7],precision:i[8]&&i[8].slice(1),trim:i[9],type:i[10]})}So.prototype=Au.prototype;function Au(n){this.fill=n.fill===void 0?" ":n.fill+"",this.align=n.align===void 0?">":n.align+"",this.sign=n.sign===void 0?"-":n.sign+"",this.symbol=n.symbol===void 0?"":n.symbol+"",this.zero=!!n.zero,this.width=n.width===void 0?void 0:+n.width,this.comma=!!n.comma,this.precision=n.precision===void 0?void 0:+n.precision,this.trim=!!n.trim,this.type=n.type===void 0?"":n.type+""}Au.prototype.toString=function(){return this.fill+this.align+this.sign+this.symbol+(this.zero?"0":"")+(this.width===void 0?"":Math.max(1,this.width|0))+(this.comma?",":"")+(this.precision===void 0?"":"."+Math.max(0,this.precision|0))+(this.trim?"~":"")+this.type};function kN(n){e:for(var i=n.length,l=1,o=-1,u;l<i;++l)switch(n[l]){case".":o=u=l;break;case"0":o===0&&(o=l),u=l;break;default:if(!+n[l])break e;o>0&&(o=0);break}return o>0?n.slice(0,o)+n.slice(u+1):n}var lx;function EN(n,i){var l=_o(n,i);if(!l)return n+"";var o=l[0],u=l[1],f=u-(lx=Math.max(-8,Math.min(8,Math.floor(u/3)))*3)+1,m=o.length;return f===m?o:f>m?o+new Array(f-m+1).join("0"):f>0?o.slice(0,f)+"."+o.slice(f):"0."+new Array(1-f).join("0")+_o(n,Math.max(0,i+f-1))[0]}function Yp(n,i){var l=_o(n,i);if(!l)return n+"";var o=l[0],u=l[1];return u<0?"0."+new Array(-u).join("0")+o:o.length>u+1?o.slice(0,u+1)+"."+o.slice(u+1):o+new Array(u-o.length+2).join("0")}const Gp={"%":(n,i)=>(n*100).toFixed(i),b:n=>Math.round(n).toString(2),c:n=>n+"",d:TN,e:(n,i)=>n.toExponential(i),f:(n,i)=>n.toFixed(i),g:(n,i)=>n.toPrecision(i),o:n=>Math.round(n).toString(8),p:(n,i)=>Yp(n*100,i),r:Yp,s:EN,X:n=>Math.round(n).toString(16).toUpperCase(),x:n=>Math.round(n).toString(16)};function Pp(n){return n}var Vp=Array.prototype.map,Xp=["y","z","a","f","p","n","µ","m","","k","M","G","T","P","E","Z","Y"];function MN(n){var i=n.grouping===void 0||n.thousands===void 0?Pp:CN(Vp.call(n.grouping,Number),n.thousands+""),l=n.currency===void 0?"":n.currency[0]+"",o=n.currency===void 0?"":n.currency[1]+"",u=n.decimal===void 0?".":n.decimal+"",f=n.numerals===void 0?Pp:AN(Vp.call(n.numerals,String)),m=n.percent===void 0?"%":n.percent+"",x=n.minus===void 0?"−":n.minus+"",p=n.nan===void 0?"NaN":n.nan+"";function h(y){y=So(y);var N=y.fill,S=y.align,A=y.sign,z=y.symbol,U=y.zero,oe=y.width,ie=y.comma,me=y.precision,Ae=y.trim,de=y.type;de==="n"?(ie=!0,de="g"):Gp[de]||(me===void 0&&(me=12),Ae=!0,de="g"),(U||N==="0"&&S==="=")&&(U=!0,N="0",S="=");var pe=z==="$"?l:z==="#"&&/[boxX]/.test(de)?"0"+de.toLowerCase():"",W=z==="$"?o:/[%p]/.test(de)?m:"",Ke=Gp[de],he=/[defgprs%]/.test(de);me=me===void 0?6:/[gprs]/.test(de)?Math.max(1,Math.min(21,me)):Math.max(0,Math.min(20,me));function De(xe){var je=pe,ze=W,we,Ze,L;if(de==="c")ze=Ke(xe)+ze,xe="";else{xe=+xe;var ne=xe<0||1/xe<0;if(xe=isNaN(xe)?p:Ke(Math.abs(xe),me),Ae&&(xe=kN(xe)),ne&&+xe==0&&A!=="+"&&(ne=!1),je=(ne?A==="("?A:x:A==="-"||A==="("?"":A)+je,ze=(de==="s"?Xp[8+lx/3]:"")+ze+(ne&&A==="("?")":""),he){for(we=-1,Ze=xe.length;++we<Ze;)if(L=xe.charCodeAt(we),48>L||L>57){ze=(L===46?u+xe.slice(we+1):xe.slice(we))+ze,xe=xe.slice(0,we);break}}}ie&&!U&&(xe=i(xe,1/0));var P=je.length+xe.length+ze.length,Ue=P<oe?new Array(oe-P+1).join(N):"";switch(ie&&U&&(xe=i(Ue+xe,Ue.length?oe-ze.length:1/0),Ue=""),S){case"<":xe=je+xe+ze+Ue;break;case"=":xe=je+Ue+xe+ze;break;case"^":xe=Ue.slice(0,P=Ue.length>>1)+je+xe+ze+Ue.slice(P);break;default:xe=Ue+je+xe+ze;break}return f(xe)}return De.toString=function(){return y+""},De}function v(y,N){var S=h((y=So(y),y.type="f",y)),A=Math.max(-8,Math.min(8,Math.floor(qi(N)/3)))*3,z=Math.pow(10,-A),U=Xp[8+A/3];return function(oe){return S(z*oe)+U}}return{format:h,formatPrefix:v}}var co,ox,cx;DN({thousands:",",grouping:[3],currency:["$",""]});function DN(n){return co=MN(n),ox=co.format,cx=co.formatPrefix,co}function RN(n){return Math.max(0,-qi(Math.abs(n)))}function UN(n,i){return Math.max(0,Math.max(-8,Math.min(8,Math.floor(qi(i)/3)))*3-qi(Math.abs(n)))}function ON(n,i){return n=Math.abs(n),i=Math.abs(i)-n,Math.max(0,qi(i)-qi(n))+1}function Oo(n,i){switch(arguments.length){case 0:break;case 1:this.range(n);break;default:this.range(i).domain(n);break}return this}const Zp=Symbol("implicit");function dx(){var n=new Tp,i=[],l=[],o=Zp;function u(f){let m=n.get(f);if(m===void 0){if(o!==Zp)return o;n.set(f,m=i.push(f)-1)}return l[m%l.length]}return u.domain=function(f){if(!arguments.length)return i.slice();i=[],n=new Tp;for(const m of f)n.has(m)||n.set(m,i.push(m)-1);return u},u.range=function(f){return arguments.length?(l=Array.from(f),u):l.slice()},u.unknown=function(f){return arguments.length?(o=f,u):o},u.copy=function(){return dx(i,l).unknown(o)},Oo.apply(u,arguments),u}function ux(){var n=dx().unknown(void 0),i=n.domain,l=n.range,o=0,u=1,f,m,x=!1,p=0,h=0,v=.5;delete n.unknown;function y(){var N=i().length,S=u<o,A=S?u:o,z=S?o:u;f=(z-A)/Math.max(1,N-p+h*2),x&&(f=Math.floor(f)),A+=(z-A-f*(N-p))*v,m=f*(1-p),x&&(A=Math.round(A),m=Math.round(m));var U=Qy(N).map(function(oe){return A+f*oe});return l(S?U.reverse():U)}return n.domain=function(N){return arguments.length?(i(N),y()):i()},n.range=function(N){return arguments.length?([o,u]=N,o=+o,u=+u,y()):[o,u]},n.rangeRound=function(N){return[o,u]=N,o=+o,u=+u,x=!0,y()},n.bandwidth=function(){return m},n.step=function(){return f},n.round=function(N){return arguments.length?(x=!!N,y()):x},n.padding=function(N){return arguments.length?(p=Math.min(1,h=+N),y()):p},n.paddingInner=function(N){return arguments.length?(p=Math.min(1,N),y()):p},n.paddingOuter=function(N){return arguments.length?(h=+N,y()):h},n.align=function(N){return arguments.length?(v=Math.max(0,Math.min(1,N)),y()):v},n.copy=function(){return ux(i(),[o,u]).round(x).paddingInner(p).paddingOuter(h).align(v)},Oo.apply(y(),arguments)}function fx(n){var i=n.copy;return n.padding=n.paddingOuter,delete n.paddingInner,delete n.paddingOuter,n.copy=function(){return fx(i())},n}function LN(){return fx(ux.apply(null,arguments).paddingInner(1))}function qN(n){return function(){return n}}function BN(n){return+n}var Qp=[0,1];function Ei(n){return n}function mu(n,i){return(i-=n=+n)?function(l){return(l-n)/i}:qN(isNaN(i)?NaN:.5)}function HN(n,i){var l;return n>i&&(l=n,n=i,i=l),function(o){return Math.max(n,Math.min(i,o))}}function IN(n,i,l){var o=n[0],u=n[1],f=i[0],m=i[1];return u<o?(o=mu(u,o),f=l(m,f)):(o=mu(o,u),f=l(f,m)),function(x){return f(o(x))}}function $N(n,i,l){var o=Math.min(n.length,i.length)-1,u=new Array(o),f=new Array(o),m=-1;for(n[o]<n[0]&&(n=n.slice().reverse(),i=i.slice().reverse());++m<o;)u[m]=mu(n[m],n[m+1]),f[m]=l(i[m],i[m+1]);return function(x){var p=Iy(n,x,1,o)-1;return f[p](u[p](x))}}function hx(n,i){return i.domain(n.domain()).range(n.range()).interpolate(n.interpolate()).clamp(n.clamp()).unknown(n.unknown())}function FN(){var n=Qp,i=Qp,l=_u,o,u,f,m=Ei,x,p,h;function v(){var N=Math.min(n.length,i.length);return m!==Ei&&(m=HN(n[0],n[N-1])),x=N>2?$N:IN,p=h=null,y}function y(N){return N==null||isNaN(N=+N)?f:(p||(p=x(n.map(o),i,l)))(o(m(N)))}return y.invert=function(N){return m(u((h||(h=x(i,n.map(o),mn)))(N)))},y.domain=function(N){return arguments.length?(n=Array.from(N,BN),v()):n.slice()},y.range=function(N){return arguments.length?(i=Array.from(N),v()):i.slice()},y.rangeRound=function(N){return i=Array.from(N),l=r1,v()},y.clamp=function(N){return arguments.length?(m=N?!0:Ei,v()):m!==Ei},y.interpolate=function(N){return arguments.length?(l=N,v()):l},y.unknown=function(N){return arguments.length?(f=N,y):f},function(N,S){return o=N,u=S,v()}}function mx(){return FN()(Ei,Ei)}function YN(n,i,l,o){var u=tu(n,i,l),f;switch(o=So(o??",f"),o.type){case"s":{var m=Math.max(Math.abs(n),Math.abs(i));return o.precision==null&&!isNaN(f=UN(u,m))&&(o.precision=f),cx(o,m)}case"":case"e":case"g":case"p":case"r":{o.precision==null&&!isNaN(f=ON(u,Math.max(Math.abs(n),Math.abs(i))))&&(o.precision=f-(o.type==="e"));break}case"f":case"%":{o.precision==null&&!isNaN(f=RN(u))&&(o.precision=f-(o.type==="%")*2);break}}return ox(o)}function GN(n){var i=n.domain;return n.ticks=function(l){var o=i();return Zy(o[0],o[o.length-1],l??10)},n.tickFormat=function(l,o){var u=i();return YN(u[0],u[u.length-1],l??10,o)},n.nice=function(l){l==null&&(l=10);var o=i(),u=0,f=o.length-1,m=o[u],x=o[f],p,h,v=10;for(x<m&&(h=m,m=x,x=h,h=u,u=f,f=h);v-- >0;){if(h=eu(m,x,l),h===p)return o[u]=m,o[f]=x,i(o);if(h>0)m=Math.floor(m/h)*h,x=Math.ceil(x/h)*h;else if(h<0)m=Math.ceil(m*h)/h,x=Math.floor(x*h)/h;else break;p=h}return n},n}function zu(){var n=mx();return n.copy=function(){return hx(n,zu())},Oo.apply(n,arguments),GN(n)}function PN(n,i){n=n.slice();var l=0,o=n.length-1,u=n[l],f=n[o],m;return f<u&&(m=l,l=o,o=m,m=u,u=f,f=m),n[l]=i.floor(u),n[o]=i.ceil(f),n}const Gd=new Date,Pd=new Date;function ca(n,i,l,o){function u(f){return n(f=arguments.length===0?new Date:new Date(+f)),f}return u.floor=f=>(n(f=new Date(+f)),f),u.ceil=f=>(n(f=new Date(f-1)),i(f,1),n(f),f),u.round=f=>{const m=u(f),x=u.ceil(f);return f-m<x-f?m:x},u.offset=(f,m)=>(i(f=new Date(+f),m==null?1:Math.floor(m)),f),u.range=(f,m,x)=>{const p=[];if(f=u.ceil(f),x=x==null?1:Math.floor(x),!(f<m)||!(x>0))return p;let h;do p.push(h=new Date(+f)),i(f,x),n(f);while(h<f&&f<m);return p},u.filter=f=>ca(m=>{if(m>=m)for(;n(m),!f(m);)m.setTime(m-1)},(m,x)=>{if(m>=m)if(x<0)for(;++x<=0;)for(;i(m,-1),!f(m););else for(;--x>=0;)for(;i(m,1),!f(m););}),l&&(u.count=(f,m)=>(Gd.setTime(+f),Pd.setTime(+m),n(Gd),n(Pd),Math.floor(l(Gd,Pd))),u.every=f=>(f=Math.floor(f),!isFinite(f)||!(f>0)?null:f>1?u.filter(o?m=>o(m)%f===0:m=>u.count(0,m)%f===0):u)),u}const To=ca(()=>{},(n,i)=>{n.setTime(+n+i)},(n,i)=>i-n);To.every=n=>(n=Math.floor(n),!isFinite(n)||!(n>0)?null:n>1?ca(i=>{i.setTime(Math.floor(i/n)*n)},(i,l)=>{i.setTime(+i+l*n)},(i,l)=>(l-i)/n):To);To.range;const Pn=1e3,rn=Pn*60,Vn=rn*60,Zn=Vn*24,ku=Zn*7,Jp=Zn*30,Vd=Zn*365,Mi=ca(n=>{n.setTime(n-n.getMilliseconds())},(n,i)=>{n.setTime(+n+i*Pn)},(n,i)=>(i-n)/Pn,n=>n.getUTCSeconds());Mi.range;const Eu=ca(n=>{n.setTime(n-n.getMilliseconds()-n.getSeconds()*Pn)},(n,i)=>{n.setTime(+n+i*rn)},(n,i)=>(i-n)/rn,n=>n.getMinutes());Eu.range;const VN=ca(n=>{n.setUTCSeconds(0,0)},(n,i)=>{n.setTime(+n+i*rn)},(n,i)=>(i-n)/rn,n=>n.getUTCMinutes());VN.range;const Mu=ca(n=>{n.setTime(n-n.getMilliseconds()-n.getSeconds()*Pn-n.getMinutes()*rn)},(n,i)=>{n.setTime(+n+i*Vn)},(n,i)=>(i-n)/Vn,n=>n.getHours());Mu.range;const XN=ca(n=>{n.setUTCMinutes(0,0,0)},(n,i)=>{n.setTime(+n+i*Vn)},(n,i)=>(i-n)/Vn,n=>n.getUTCHours());XN.range;const el=ca(n=>n.setHours(0,0,0,0),(n,i)=>n.setDate(n.getDate()+i),(n,i)=>(i-n-(i.getTimezoneOffset()-n.getTimezoneOffset())*rn)/Zn,n=>n.getDate()-1);el.range;const Du=ca(n=>{n.setUTCHours(0,0,0,0)},(n,i)=>{n.setUTCDate(n.getUTCDate()+i)},(n,i)=>(i-n)/Zn,n=>n.getUTCDate()-1);Du.range;const ZN=ca(n=>{n.setUTCHours(0,0,0,0)},(n,i)=>{n.setUTCDate(n.getUTCDate()+i)},(n,i)=>(i-n)/Zn,n=>Math.floor(n/Zn));ZN.range;function Js(n){return ca(i=>{i.setDate(i.getDate()-(i.getDay()+7-n)%7),i.setHours(0,0,0,0)},(i,l)=>{i.setDate(i.getDate()+l*7)},(i,l)=>(l-i-(l.getTimezoneOffset()-i.getTimezoneOffset())*rn)/ku)}const Lo=Js(0),Co=Js(1),QN=Js(2),JN=Js(3),Bi=Js(4),KN=Js(5),WN=Js(6);Lo.range;Co.range;QN.range;JN.range;Bi.range;KN.range;WN.range;function Ks(n){return ca(i=>{i.setUTCDate(i.getUTCDate()-(i.getUTCDay()+7-n)%7),i.setUTCHours(0,0,0,0)},(i,l)=>{i.setUTCDate(i.getUTCDate()+l*7)},(i,l)=>(l-i)/ku)}const px=Ks(0),Ao=Ks(1),ew=Ks(2),tw=Ks(3),Hi=Ks(4),aw=Ks(5),nw=Ks(6);px.range;Ao.range;ew.range;tw.range;Hi.range;aw.range;nw.range;const Ru=ca(n=>{n.setDate(1),n.setHours(0,0,0,0)},(n,i)=>{n.setMonth(n.getMonth()+i)},(n,i)=>i.getMonth()-n.getMonth()+(i.getFullYear()-n.getFullYear())*12,n=>n.getMonth());Ru.range;const sw=ca(n=>{n.setUTCDate(1),n.setUTCHours(0,0,0,0)},(n,i)=>{n.setUTCMonth(n.getUTCMonth()+i)},(n,i)=>i.getUTCMonth()-n.getUTCMonth()+(i.getUTCFullYear()-n.getUTCFullYear())*12,n=>n.getUTCMonth());sw.range;const Qn=ca(n=>{n.setMonth(0,1),n.setHours(0,0,0,0)},(n,i)=>{n.setFullYear(n.getFullYear()+i)},(n,i)=>i.getFullYear()-n.getFullYear(),n=>n.getFullYear());Qn.every=n=>!isFinite(n=Math.floor(n))||!(n>0)?null:ca(i=>{i.setFullYear(Math.floor(i.getFullYear()/n)*n),i.setMonth(0,1),i.setHours(0,0,0,0)},(i,l)=>{i.setFullYear(i.getFullYear()+l*n)});Qn.range;const Zs=ca(n=>{n.setUTCMonth(0,1),n.setUTCHours(0,0,0,0)},(n,i)=>{n.setUTCFullYear(n.getUTCFullYear()+i)},(n,i)=>i.getUTCFullYear()-n.getUTCFullYear(),n=>n.getUTCFullYear());Zs.every=n=>!isFinite(n=Math.floor(n))||!(n>0)?null:ca(i=>{i.setUTCFullYear(Math.floor(i.getUTCFullYear()/n)*n),i.setUTCMonth(0,1),i.setUTCHours(0,0,0,0)},(i,l)=>{i.setUTCFullYear(i.getUTCFullYear()+l*n)});Zs.range;function iw(n,i,l,o,u,f){const m=[[Mi,1,Pn],[Mi,5,5*Pn],[Mi,15,15*Pn],[Mi,30,30*Pn],[f,1,rn],[f,5,5*rn],[f,15,15*rn],[f,30,30*rn],[u,1,Vn],[u,3,3*Vn],[u,6,6*Vn],[u,12,12*Vn],[o,1,Zn],[o,2,2*Zn],[l,1,ku],[i,1,Jp],[i,3,3*Jp],[n,1,Vd]];function x(h,v,y){const N=v<h;N&&([h,v]=[v,h]);const S=y&&typeof y.range=="function"?y:p(h,v,y),A=S?S.range(h,+v+1):[];return N?A.reverse():A}function p(h,v,y){const N=Math.abs(v-h)/y,S=vu(([,,U])=>U).right(m,N);if(S===m.length)return n.every(tu(h/Vd,v/Vd,y));if(S===0)return To.every(Math.max(tu(h,v,y),1));const[A,z]=m[N/m[S-1][2]<m[S][2]/N?S-1:S];return A.every(z)}return[x,p]}const[rw,lw]=iw(Qn,Ru,Lo,el,Mu,Eu);function Xd(n){if(0<=n.y&&n.y<100){var i=new Date(-1,n.m,n.d,n.H,n.M,n.S,n.L);return i.setFullYear(n.y),i}return new Date(n.y,n.m,n.d,n.H,n.M,n.S,n.L)}function Zd(n){if(0<=n.y&&n.y<100){var i=new Date(Date.UTC(-1,n.m,n.d,n.H,n.M,n.S,n.L));return i.setUTCFullYear(n.y),i}return new Date(Date.UTC(n.y,n.m,n.d,n.H,n.M,n.S,n.L))}function Lr(n,i,l){return{y:n,m:i,d:l,H:0,M:0,S:0,L:0}}function ow(n){var i=n.dateTime,l=n.date,o=n.time,u=n.periods,f=n.days,m=n.shortDays,x=n.months,p=n.shortMonths,h=qr(u),v=Br(u),y=qr(f),N=Br(f),S=qr(m),A=Br(m),z=qr(x),U=Br(x),oe=qr(p),ie=Br(p),me={a:ne,A:P,b:Ue,B:T,c:null,d:ng,e:ng,f:Ew,g:Iw,G:Fw,H:Aw,I:zw,j:kw,L:gx,m:Mw,M:Dw,p:F,q:le,Q:rg,s:lg,S:Rw,u:Uw,U:Ow,V:Lw,w:qw,W:Bw,x:null,X:null,y:Hw,Y:$w,Z:Yw,"%":ig},Ae={a:ce,A:fe,b:Oe,B:ve,c:null,d:sg,e:sg,f:Xw,g:s_,G:r_,H:Gw,I:Pw,j:Vw,L:vx,m:Zw,M:Qw,p:ke,q:$e,Q:rg,s:lg,S:Jw,u:Kw,U:Ww,V:e_,w:t_,W:a_,x:null,X:null,y:n_,Y:i_,Z:l_,"%":ig},de={a:De,A:xe,b:je,B:ze,c:we,d:tg,e:tg,f:_w,g:eg,G:Wp,H:ag,I:ag,j:bw,L:ww,m:yw,M:jw,p:he,q:vw,Q:Tw,s:Cw,S:Nw,u:hw,U:mw,V:pw,w:fw,W:gw,x:Ze,X:L,y:eg,Y:Wp,Z:xw,"%":Sw};me.x=pe(l,me),me.X=pe(o,me),me.c=pe(i,me),Ae.x=pe(l,Ae),Ae.X=pe(o,Ae),Ae.c=pe(i,Ae);function pe(re,k){return function(se){var V=[],ue=-1,Se=0,Fe=re.length,it,et,Gt;for(se instanceof Date||(se=new Date(+se));++ue<Fe;)re.charCodeAt(ue)===37&&(V.push(re.slice(Se,ue)),(et=Kp[it=re.charAt(++ue)])!=null?it=re.charAt(++ue):et=it==="e"?" ":"0",(Gt=k[it])&&(it=Gt(se,et)),V.push(it),Se=ue+1);return V.push(re.slice(Se,ue)),V.join("")}}function W(re,k){return function(se){var V=Lr(1900,void 0,1),ue=Ke(V,re,se+="",0),Se,Fe;if(ue!=se.length)return null;if("Q"in V)return new Date(V.Q);if("s"in V)return new Date(V.s*1e3+("L"in V?V.L:0));if(k&&!("Z"in V)&&(V.Z=0),"p"in V&&(V.H=V.H%12+V.p*12),V.m===void 0&&(V.m="q"in V?V.q:0),"V"in V){if(V.V<1||V.V>53)return null;"w"in V||(V.w=1),"Z"in V?(Se=Zd(Lr(V.y,0,1)),Fe=Se.getUTCDay(),Se=Fe>4||Fe===0?Ao.ceil(Se):Ao(Se),Se=Du.offset(Se,(V.V-1)*7),V.y=Se.getUTCFullYear(),V.m=Se.getUTCMonth(),V.d=Se.getUTCDate()+(V.w+6)%7):(Se=Xd(Lr(V.y,0,1)),Fe=Se.getDay(),Se=Fe>4||Fe===0?Co.ceil(Se):Co(Se),Se=el.offset(Se,(V.V-1)*7),V.y=Se.getFullYear(),V.m=Se.getMonth(),V.d=Se.getDate()+(V.w+6)%7)}else("W"in V||"U"in V)&&("w"in V||(V.w="u"in V?V.u%7:"W"in V?1:0),Fe="Z"in V?Zd(Lr(V.y,0,1)).getUTCDay():Xd(Lr(V.y,0,1)).getDay(),V.m=0,V.d="W"in V?(V.w+6)%7+V.W*7-(Fe+5)%7:V.w+V.U*7-(Fe+6)%7);return"Z"in V?(V.H+=V.Z/100|0,V.M+=V.Z%100,Zd(V)):Xd(V)}}function Ke(re,k,se,V){for(var ue=0,Se=k.length,Fe=se.length,it,et;ue<Se;){if(V>=Fe)return-1;if(it=k.charCodeAt(ue++),it===37){if(it=k.charAt(ue++),et=de[it in Kp?k.charAt(ue++):it],!et||(V=et(re,se,V))<0)return-1}else if(it!=se.charCodeAt(V++))return-1}return V}function he(re,k,se){var V=h.exec(k.slice(se));return V?(re.p=v.get(V[0].toLowerCase()),se+V[0].length):-1}function De(re,k,se){var V=S.exec(k.slice(se));return V?(re.w=A.get(V[0].toLowerCase()),se+V[0].length):-1}function xe(re,k,se){var V=y.exec(k.slice(se));return V?(re.w=N.get(V[0].toLowerCase()),se+V[0].length):-1}function je(re,k,se){var V=oe.exec(k.slice(se));return V?(re.m=ie.get(V[0].toLowerCase()),se+V[0].length):-1}function ze(re,k,se){var V=z.exec(k.slice(se));return V?(re.m=U.get(V[0].toLowerCase()),se+V[0].length):-1}function we(re,k,se){return Ke(re,i,k,se)}function Ze(re,k,se){return Ke(re,l,k,se)}function L(re,k,se){return Ke(re,o,k,se)}function ne(re){return m[re.getDay()]}function P(re){return f[re.getDay()]}function Ue(re){return p[re.getMonth()]}function T(re){return x[re.getMonth()]}function F(re){return u[+(re.getHours()>=12)]}function le(re){return 1+~~(re.getMonth()/3)}function ce(re){return m[re.getUTCDay()]}function fe(re){return f[re.getUTCDay()]}function Oe(re){return p[re.getUTCMonth()]}function ve(re){return x[re.getUTCMonth()]}function ke(re){return u[+(re.getUTCHours()>=12)]}function $e(re){return 1+~~(re.getUTCMonth()/3)}return{format:function(re){var k=pe(re+="",me);return k.toString=function(){return re},k},parse:function(re){var k=W(re+="",!1);return k.toString=function(){return re},k},utcFormat:function(re){var k=pe(re+="",Ae);return k.toString=function(){return re},k},utcParse:function(re){var k=W(re+="",!0);return k.toString=function(){return re},k}}}var Kp={"-":"",_:" ",0:"0"},ga=/^\s*\d+/,cw=/^%/,dw=/[\\^$*+?|[\]().{}]/g;function bt(n,i,l){var o=n<0?"-":"",u=(o?-n:n)+"",f=u.length;return o+(f<l?new Array(l-f+1).join(i)+u:u)}function uw(n){return n.replace(dw,"\\$&")}function qr(n){return new RegExp("^(?:"+n.map(uw).join("|")+")","i")}function Br(n){return new Map(n.map((i,l)=>[i.toLowerCase(),l]))}function fw(n,i,l){var o=ga.exec(i.slice(l,l+1));return o?(n.w=+o[0],l+o[0].length):-1}function hw(n,i,l){var o=ga.exec(i.slice(l,l+1));return o?(n.u=+o[0],l+o[0].length):-1}function mw(n,i,l){var o=ga.exec(i.slice(l,l+2));return o?(n.U=+o[0],l+o[0].length):-1}function pw(n,i,l){var o=ga.exec(i.slice(l,l+2));return o?(n.V=+o[0],l+o[0].length):-1}function gw(n,i,l){var o=ga.exec(i.slice(l,l+2));return o?(n.W=+o[0],l+o[0].length):-1}function Wp(n,i,l){var o=ga.exec(i.slice(l,l+4));return o?(n.y=+o[0],l+o[0].length):-1}function eg(n,i,l){var o=ga.exec(i.slice(l,l+2));return o?(n.y=+o[0]+(+o[0]>68?1900:2e3),l+o[0].length):-1}function xw(n,i,l){var o=/^(Z)|([+-]\d\d)(?::?(\d\d))?/.exec(i.slice(l,l+6));return o?(n.Z=o[1]?0:-(o[2]+(o[3]||"00")),l+o[0].length):-1}function vw(n,i,l){var o=ga.exec(i.slice(l,l+1));return o?(n.q=o[0]*3-3,l+o[0].length):-1}function yw(n,i,l){var o=ga.exec(i.slice(l,l+2));return o?(n.m=o[0]-1,l+o[0].length):-1}function tg(n,i,l){var o=ga.exec(i.slice(l,l+2));return o?(n.d=+o[0],l+o[0].length):-1}function bw(n,i,l){var o=ga.exec(i.slice(l,l+3));return o?(n.m=0,n.d=+o[0],l+o[0].length):-1}function ag(n,i,l){var o=ga.exec(i.slice(l,l+2));return o?(n.H=+o[0],l+o[0].length):-1}function jw(n,i,l){var o=ga.exec(i.slice(l,l+2));return o?(n.M=+o[0],l+o[0].length):-1}function Nw(n,i,l){var o=ga.exec(i.slice(l,l+2));return o?(n.S=+o[0],l+o[0].length):-1}function ww(n,i,l){var o=ga.exec(i.slice(l,l+3));return o?(n.L=+o[0],l+o[0].length):-1}function _w(n,i,l){var o=ga.exec(i.slice(l,l+6));return o?(n.L=Math.floor(o[0]/1e3),l+o[0].length):-1}function Sw(n,i,l){var o=cw.exec(i.slice(l,l+1));return o?l+o[0].length:-1}function Tw(n,i,l){var o=ga.exec(i.slice(l));return o?(n.Q=+o[0],l+o[0].length):-1}function Cw(n,i,l){var o=ga.exec(i.slice(l));return o?(n.s=+o[0],l+o[0].length):-1}function ng(n,i){return bt(n.getDate(),i,2)}function Aw(n,i){return bt(n.getHours(),i,2)}function zw(n,i){return bt(n.getHours()%12||12,i,2)}function kw(n,i){return bt(1+el.count(Qn(n),n),i,3)}function gx(n,i){return bt(n.getMilliseconds(),i,3)}function Ew(n,i){return gx(n,i)+"000"}function Mw(n,i){return bt(n.getMonth()+1,i,2)}function Dw(n,i){return bt(n.getMinutes(),i,2)}function Rw(n,i){return bt(n.getSeconds(),i,2)}function Uw(n){var i=n.getDay();return i===0?7:i}function Ow(n,i){return bt(Lo.count(Qn(n)-1,n),i,2)}function xx(n){var i=n.getDay();return i>=4||i===0?Bi(n):Bi.ceil(n)}function Lw(n,i){return n=xx(n),bt(Bi.count(Qn(n),n)+(Qn(n).getDay()===4),i,2)}function qw(n){return n.getDay()}function Bw(n,i){return bt(Co.count(Qn(n)-1,n),i,2)}function Hw(n,i){return bt(n.getFullYear()%100,i,2)}function Iw(n,i){return n=xx(n),bt(n.getFullYear()%100,i,2)}function $w(n,i){return bt(n.getFullYear()%1e4,i,4)}function Fw(n,i){var l=n.getDay();return n=l>=4||l===0?Bi(n):Bi.ceil(n),bt(n.getFullYear()%1e4,i,4)}function Yw(n){var i=n.getTimezoneOffset();return(i>0?"-":(i*=-1,"+"))+bt(i/60|0,"0",2)+bt(i%60,"0",2)}function sg(n,i){return bt(n.getUTCDate(),i,2)}function Gw(n,i){return bt(n.getUTCHours(),i,2)}function Pw(n,i){return bt(n.getUTCHours()%12||12,i,2)}function Vw(n,i){return bt(1+Du.count(Zs(n),n),i,3)}function vx(n,i){return bt(n.getUTCMilliseconds(),i,3)}function Xw(n,i){return vx(n,i)+"000"}function Zw(n,i){return bt(n.getUTCMonth()+1,i,2)}function Qw(n,i){return bt(n.getUTCMinutes(),i,2)}function Jw(n,i){return bt(n.getUTCSeconds(),i,2)}function Kw(n){var i=n.getUTCDay();return i===0?7:i}function Ww(n,i){return bt(px.count(Zs(n)-1,n),i,2)}function yx(n){var i=n.getUTCDay();return i>=4||i===0?Hi(n):Hi.ceil(n)}function e_(n,i){return n=yx(n),bt(Hi.count(Zs(n),n)+(Zs(n).getUTCDay()===4),i,2)}function t_(n){return n.getUTCDay()}function a_(n,i){return bt(Ao.count(Zs(n)-1,n),i,2)}function n_(n,i){return bt(n.getUTCFullYear()%100,i,2)}function s_(n,i){return n=yx(n),bt(n.getUTCFullYear()%100,i,2)}function i_(n,i){return bt(n.getUTCFullYear()%1e4,i,4)}function r_(n,i){var l=n.getUTCDay();return n=l>=4||l===0?Hi(n):Hi.ceil(n),bt(n.getUTCFullYear()%1e4,i,4)}function l_(){return"+0000"}function ig(){return"%"}function rg(n){return+n}function lg(n){return Math.floor(+n/1e3)}var ki,zo,bx;o_({dateTime:"%x, %X",date:"%-m/%-d/%Y",time:"%-I:%M:%S %p",periods:["AM","PM"],days:["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],shortDays:["Sun","Mon","Tue","Wed","Thu","Fri","Sat"],months:["January","February","March","April","May","June","July","August","September","October","November","December"],shortMonths:["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]});function o_(n){return ki=ow(n),zo=ki.format,bx=ki.parse,ki.utcFormat,ki.utcParse,ki}function c_(n){return new Date(n)}function d_(n){return n instanceof Date?+n:+new Date(+n)}function jx(n,i,l,o,u,f,m,x,p,h){var v=mx(),y=v.invert,N=v.domain,S=h(".%L"),A=h(":%S"),z=h("%I:%M"),U=h("%I %p"),oe=h("%a %d"),ie=h("%b %d"),me=h("%B"),Ae=h("%Y");function de(pe){return(p(pe)<pe?S:x(pe)<pe?A:m(pe)<pe?z:f(pe)<pe?U:o(pe)<pe?u(pe)<pe?oe:ie:l(pe)<pe?me:Ae)(pe)}return v.invert=function(pe){return new Date(y(pe))},v.domain=function(pe){return arguments.length?N(Array.from(pe,d_)):N().map(c_)},v.ticks=function(pe){var W=N();return n(W[0],W[W.length-1],pe??10)},v.tickFormat=function(pe,W){return W==null?de:h(W)},v.nice=function(pe){var W=N();return(!pe||typeof pe.range!="function")&&(pe=i(W[0],W[W.length-1],pe??10)),pe?N(PN(W,pe)):v},v.copy=function(){return hx(v,jx(n,i,l,o,u,f,m,x,p,h))},v}function u_(){return Oo.apply(jx(rw,lw,Qn,Ru,Lo,el,Mu,Eu,Mi,zo).domain([new Date(2e3,0,1),new Date(2e3,0,2)]),arguments)}function pa(n){return function(){return n}}function Nx(n){let i=3;return n.digits=function(l){if(!arguments.length)return i;if(l==null)i=null;else{const o=Math.floor(l);if(!(o>=0))throw new RangeError(`invalid digits: ${l}`);i=o}return n},()=>new SN(i)}function wx(n){return typeof n=="object"&&"length"in n?n:Array.from(n)}function _x(n){this._context=n}_x.prototype={areaStart:function(){this._line=0},areaEnd:function(){this._line=NaN},lineStart:function(){this._point=0},lineEnd:function(){(this._line||this._line!==0&&this._point===1)&&this._context.closePath(),this._line=1-this._line},point:function(n,i){switch(n=+n,i=+i,this._point){case 0:this._point=1,this._line?this._context.lineTo(n,i):this._context.moveTo(n,i);break;case 1:this._point=2;default:this._context.lineTo(n,i);break}}};function Sx(n){return new _x(n)}function Tx(n){return n[0]}function Cx(n){return n[1]}function Uu(n,i){var l=pa(!0),o=null,u=Sx,f=null,m=Nx(x);n=typeof n=="function"?n:n===void 0?Tx:pa(n),i=typeof i=="function"?i:i===void 0?Cx:pa(i);function x(p){var h,v=(p=wx(p)).length,y,N=!1,S;for(o==null&&(f=u(S=m())),h=0;h<=v;++h)!(h<v&&l(y=p[h],h,p))===N&&((N=!N)?f.lineStart():f.lineEnd()),N&&f.point(+n(y,h,p),+i(y,h,p));if(S)return f=null,S+""||null}return x.x=function(p){return arguments.length?(n=typeof p=="function"?p:pa(+p),x):n},x.y=function(p){return arguments.length?(i=typeof p=="function"?p:pa(+p),x):i},x.defined=function(p){return arguments.length?(l=typeof p=="function"?p:pa(!!p),x):l},x.curve=function(p){return arguments.length?(u=p,o!=null&&(f=u(o)),x):u},x.context=function(p){return arguments.length?(p==null?o=f=null:f=u(o=p),x):o},x}function f_(n,i,l){var o=null,u=pa(!0),f=null,m=Sx,x=null,p=Nx(h);n=typeof n=="function"?n:n===void 0?Tx:pa(+n),i=typeof i=="function"?i:pa(i===void 0?0:+i),l=typeof l=="function"?l:l===void 0?Cx:pa(+l);function h(y){var N,S,A,z=(y=wx(y)).length,U,oe=!1,ie,me=new Array(z),Ae=new Array(z);for(f==null&&(x=m(ie=p())),N=0;N<=z;++N){if(!(N<z&&u(U=y[N],N,y))===oe)if(oe=!oe)S=N,x.areaStart(),x.lineStart();else{for(x.lineEnd(),x.lineStart(),A=N-1;A>=S;--A)x.point(me[A],Ae[A]);x.lineEnd(),x.areaEnd()}oe&&(me[N]=+n(U,N,y),Ae[N]=+i(U,N,y),x.point(o?+o(U,N,y):me[N],l?+l(U,N,y):Ae[N]))}if(ie)return x=null,ie+""||null}function v(){return Uu().defined(u).curve(m).context(f)}return h.x=function(y){return arguments.length?(n=typeof y=="function"?y:pa(+y),o=null,h):n},h.x0=function(y){return arguments.length?(n=typeof y=="function"?y:pa(+y),h):n},h.x1=function(y){return arguments.length?(o=y==null?null:typeof y=="function"?y:pa(+y),h):o},h.y=function(y){return arguments.length?(i=typeof y=="function"?y:pa(+y),l=null,h):i},h.y0=function(y){return arguments.length?(i=typeof y=="function"?y:pa(+y),h):i},h.y1=function(y){return arguments.length?(l=y==null?null:typeof y=="function"?y:pa(+y),h):l},h.lineX0=h.lineY0=function(){return v().x(n).y(i)},h.lineY1=function(){return v().x(n).y(l)},h.lineX1=function(){return v().x(o).y(i)},h.defined=function(y){return arguments.length?(u=typeof y=="function"?y:pa(!!y),h):u},h.curve=function(y){return arguments.length?(m=y,f!=null&&(x=m(f)),h):m},h.context=function(y){return arguments.length?(y==null?f=x=null:x=m(f=y),h):f},h}function og(n,i,l){n._context.bezierCurveTo(n._x1+n._k*(n._x2-n._x0),n._y1+n._k*(n._y2-n._y0),n._x2+n._k*(n._x1-i),n._y2+n._k*(n._y1-l),n._x2,n._y2)}function Ax(n,i){this._context=n,this._k=(1-i)/6}Ax.prototype={areaStart:function(){this._line=0},areaEnd:function(){this._line=NaN},lineStart:function(){this._x0=this._x1=this._x2=this._y0=this._y1=this._y2=NaN,this._point=0},lineEnd:function(){switch(this._point){case 2:this._context.lineTo(this._x2,this._y2);break;case 3:og(this,this._x1,this._y1);break}(this._line||this._line!==0&&this._point===1)&&this._context.closePath(),this._line=1-this._line},point:function(n,i){switch(n=+n,i=+i,this._point){case 0:this._point=1,this._line?this._context.lineTo(n,i):this._context.moveTo(n,i);break;case 1:this._point=2,this._x1=n,this._y1=i;break;case 2:this._point=3;default:og(this,n,i);break}this._x0=this._x1,this._x1=this._x2,this._x2=n,this._y0=this._y1,this._y1=this._y2,this._y2=i}};const cg=(function n(i){function l(o){return new Ax(o,i)}return l.tension=function(o){return n(+o)},l})(0);function dg(n){return n<0?-1:1}function ug(n,i,l){var o=n._x1-n._x0,u=i-n._x1,f=(n._y1-n._y0)/(o||u<0&&-0),m=(l-n._y1)/(u||o<0&&-0),x=(f*u+m*o)/(o+u);return(dg(f)+dg(m))*Math.min(Math.abs(f),Math.abs(m),.5*Math.abs(x))||0}function fg(n,i){var l=n._x1-n._x0;return l?(3*(n._y1-n._y0)/l-i)/2:i}function Qd(n,i,l){var o=n._x0,u=n._y0,f=n._x1,m=n._y1,x=(f-o)/3;n._context.bezierCurveTo(o+x,u+x*i,f-x,m-x*l,f,m)}function ko(n){this._context=n}ko.prototype={areaStart:function(){this._line=0},areaEnd:function(){this._line=NaN},lineStart:function(){this._x0=this._x1=this._y0=this._y1=this._t0=NaN,this._point=0},lineEnd:function(){switch(this._point){case 2:this._context.lineTo(this._x1,this._y1);break;case 3:Qd(this,this._t0,fg(this,this._t0));break}(this._line||this._line!==0&&this._point===1)&&this._context.closePath(),this._line=1-this._line},point:function(n,i){var l=NaN;if(n=+n,i=+i,!(n===this._x1&&i===this._y1)){switch(this._point){case 0:this._point=1,this._line?this._context.lineTo(n,i):this._context.moveTo(n,i);break;case 1:this._point=2;break;case 2:this._point=3,Qd(this,fg(this,l=ug(this,n,i)),l);break;default:Qd(this,this._t0,l=ug(this,n,i));break}this._x0=this._x1,this._x1=n,this._y0=this._y1,this._y1=i,this._t0=l}}};Object.create(ko.prototype).point=function(n,i){ko.prototype.point.call(this,i,n)};function h_(n){return new ko(n)}function Fr(n,i,l){this.k=n,this.x=i,this.y=l}Fr.prototype={constructor:Fr,scale:function(n){return n===1?this:new Fr(this.k*n,this.x,this.y)},translate:function(n,i){return n===0&i===0?this:new Fr(this.k,this.x+this.k*n,this.y+this.k*i)},apply:function(n){return[n[0]*this.k+this.x,n[1]*this.k+this.y]},applyX:function(n){return n*this.k+this.x},applyY:function(n){return n*this.k+this.y},invert:function(n){return[(n[0]-this.x)/this.k,(n[1]-this.y)/this.k]},invertX:function(n){return(n-this.x)/this.k},invertY:function(n){return(n-this.y)/this.k},rescaleX:function(n){return n.copy().domain(n.range().map(this.invertX,this).map(n.invert,n))},rescaleY:function(n){return n.copy().domain(n.range().map(this.invertY,this).map(n.invert,n))},toString:function(){return"translate("+this.x+","+this.y+") scale("+this.k+")"}};Fr.prototype;const m_=({active:n})=>{var A,z;if(!n)return null;const[i,l]=w.useState(null),[o,u]=w.useState(!0),[f,m]=w.useState(null),[x,p]=w.useState(!1),[h,v]=w.useState({});w.useEffect(()=>{y()},[]);const y=async()=>{try{u(!0);const U=localStorage.getItem("crisp_auth_token"),oe=await fetch("http://localhost:8000/api/auth/profile/",{headers:{Authorization:`Bearer ${U}`,"Content-Type":"application/json"}});if(oe.ok){const ie=await oe.json();l(ie.user),v({first_name:ie.user.first_name||"",last_name:ie.user.last_name||"",email:ie.user.email||""})}else throw new Error("Failed to fetch profile")}catch(U){m(U.message)}finally{u(!1)}},N=async()=>{try{const U=localStorage.getItem("crisp_auth_token"),oe=await fetch("http://localhost:8000/api/auth/profile/",{method:"PUT",headers:{Authorization:`Bearer ${U}`,"Content-Type":"application/json"},body:JSON.stringify(h)});if(oe.ok){const ie=await oe.json();l(ie.user),p(!1)}else throw new Error("Failed to update profile")}catch(U){m(U.message)}},S=()=>{v({first_name:i.first_name||"",last_name:i.last_name||"",email:i.email||""}),p(!1)};return o?t.jsx("div",{className:"user-profile",children:t.jsxs("div",{className:"loading-state",children:[t.jsx("i",{className:"fas fa-spinner fa-spin"}),t.jsx("p",{children:"Loading profile..."})]})}):f?t.jsx("div",{className:"user-profile",children:t.jsxs("div",{className:"error-state",children:[t.jsx("i",{className:"fas fa-exclamation-triangle"}),t.jsxs("p",{children:["Error loading profile: ",f]}),t.jsx("button",{onClick:y,className:"btn btn-primary",children:"Retry"})]})}):t.jsxs("div",{className:"user-profile",children:[t.jsxs("div",{className:"header",children:[t.jsx("h2",{children:"User Profile"}),!x&&t.jsxs("button",{className:"btn btn-primary",onClick:()=>p(!0),children:[t.jsx("i",{className:"fas fa-edit"}),"Edit Profile"]})]}),t.jsxs("div",{className:"profile-card",children:[t.jsxs("div",{className:"profile-header",children:[t.jsx("div",{className:"profile-avatar",children:t.jsx("i",{className:"fas fa-user"})}),t.jsxs("div",{className:"profile-title",children:[t.jsxs("h3",{children:[i.first_name," ",i.last_name]}),t.jsx("p",{className:"profile-role",children:i.role})]})]}),t.jsx("div",{className:"profile-details",children:x?t.jsxs("form",{className:"edit-form",children:[t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"First Name"}),t.jsx("input",{type:"text",value:h.first_name,onChange:U=>v({...h,first_name:U.target.value}),className:"form-input"})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Last Name"}),t.jsx("input",{type:"text",value:h.last_name,onChange:U=>v({...h,last_name:U.target.value}),className:"form-input"})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Email"}),t.jsx("input",{type:"email",value:h.email,onChange:U=>v({...h,email:U.target.value}),className:"form-input"})]}),t.jsxs("div",{className:"form-actions",children:[t.jsxs("button",{type:"button",onClick:N,className:"btn btn-primary",children:[t.jsx("i",{className:"fas fa-save"}),"Save Changes"]}),t.jsxs("button",{type:"button",onClick:S,className:"btn btn-secondary",children:[t.jsx("i",{className:"fas fa-times"}),"Cancel"]})]})]}):t.jsxs("div",{className:"info-grid",children:[t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"Username"}),t.jsx("span",{children:i.username})]}),t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"Email"}),t.jsx("span",{children:i.email})]}),t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"First Name"}),t.jsx("span",{children:i.first_name||"Not set"})]}),t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"Last Name"}),t.jsx("span",{children:i.last_name||"Not set"})]}),t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"Organization"}),t.jsx("span",{children:((A=i.organization)==null?void 0:A.name)||"No organization"})]}),t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"Role"}),t.jsx("span",{className:`role-badge ${(z=i.role)==null?void 0:z.toLowerCase()}`,children:i.role})]}),t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"Status"}),t.jsx("span",{className:`status-badge ${i.is_active?"active":"inactive"}`,children:i.is_active?"Active":"Inactive"})]}),t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"Joined"}),t.jsx("span",{children:new Date(i.created_at).toLocaleDateString()})]})]})})]}),t.jsx("style",{jsx:!0,children:`
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
      `})]})},zt="http://localhost:8000",Ut=()=>{const n=localStorage.getItem("crisp_auth_token");return{"Content-Type":"application/json",Authorization:n?`Bearer ${n}`:""}},p_=()=>{try{const n=localStorage.getItem("crisp_user");return n?JSON.parse(n):null}catch(n){return console.error("Error parsing current user from localStorage:",n),null}},g_=async(n,i)=>{const l=await fetch(`${zt}/api/auth/login/`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({username:n,password:i})});if(!l.ok){const u=await l.json().catch(()=>({}));throw new Error(u.detail||u.message||"Login failed")}const o=await l.json();return{tokens:{access:o.access,refresh:o.refresh},user:o.user}},x_=async(n={})=>{const i=new URLSearchParams(n).toString(),l=`${zt}/api/users/${i?`?${i}`:""}`,o=await fetch(l,{method:"GET",headers:Ut()});if(!o.ok){const u=await o.json().catch(()=>({}));throw new Error(u.message||"Failed to fetch users")}return await o.json()},hg=async n=>{const i=await fetch(`${zt}/api/users/${n}/`,{method:"GET",headers:Ut()});if(!i.ok){const l=await i.json().catch(()=>({}));throw new Error(l.message||"Failed to fetch user")}return await i.json()},v_=async n=>{const i=await fetch(`${zt}/api/users/create/`,{method:"POST",headers:Ut(),body:JSON.stringify(n)});if(!i.ok){const l=await i.json().catch(()=>({}));throw new Error(l.message||"Failed to create user")}return await i.json()},y_=async(n,i)=>{const l=await fetch(`${zt}/api/users/${n}/update/`,{method:"PUT",headers:Ut(),body:JSON.stringify(i)});if(!l.ok){const o=await l.json().catch(()=>({}));throw new Error(o.message||"Failed to update user")}return await l.json()},b_=async(n,i="")=>{const l=await fetch(`${zt}/api/users/${n}/deactivate/`,{method:"POST",headers:Ut(),body:JSON.stringify({reason:i})});if(!l.ok){const o=await l.json().catch(()=>({}));throw new Error(o.message||"Failed to deactivate user")}return await l.json()},j_=async(n,i="")=>{const l=await fetch(`${zt}/api/users/${n}/reactivate/`,{method:"POST",headers:Ut(),body:JSON.stringify({reason:i})});if(!l.ok){const o=await l.json().catch(()=>({}));throw new Error(o.message||"Failed to reactivate user")}return await l.json()},N_=async(n,i="")=>{const l=await fetch(`${zt}/api/users/${n}/delete-permanently/`,{method:"DELETE",headers:Ut(),body:JSON.stringify({confirm:!0,reason:i})});if(!l.ok){const o=await l.json().catch(()=>({}));throw new Error(o.message||"Failed to permanently delete user")}return await l.json()},w_=async(n,i)=>{const l=await fetch(`${zt}/api/users/${n}/change_username/`,{method:"POST",headers:Ut(),body:JSON.stringify({username:i})});if(!l.ok){const o=await l.json().catch(()=>({}));throw new Error(o.message||"Failed to change username")}return await l.json()},Ou=async(n={})=>{const i=new URLSearchParams(n).toString(),l=`${zt}/api/organizations/${i?`?${i}`:""}`,o=await fetch(l,{method:"GET",headers:Ut()});if(!o.ok){const u=await o.json().catch(()=>({}));throw new Error(u.message||"Failed to fetch organizations")}return await o.json()},__=async n=>{const i=await fetch(`${zt}/api/organizations/create/`,{method:"POST",headers:Ut(),body:JSON.stringify(n)});if(!i.ok){const l=await i.json().catch(()=>({}));throw new Error(l.message||"Failed to create organization")}return await i.json()},S_=async(n,i)=>{const l=await fetch(`${zt}/api/organizations/${n}/update/`,{method:"PUT",headers:Ut(),body:JSON.stringify(i)});if(!l.ok){const o=await l.json().catch(()=>({}));throw new Error(o.message||"Failed to update organization")}return await l.json()},T_=async(n,i="")=>{const l=await fetch(`${zt}/api/organizations/${n}/deactivate/`,{method:"POST",headers:Ut(),body:JSON.stringify({reason:i})});if(!l.ok){const o=await l.json().catch(()=>({}));throw new Error(o.message||"Failed to deactivate organization")}return await l.json()},C_=async(n,i="")=>{const l=await fetch(`${zt}/api/organizations/${n}/reactivate/`,{method:"POST",headers:Ut(),body:JSON.stringify({reason:i})});if(!l.ok){const o=await l.json().catch(()=>({}));throw new Error(o.message||"Failed to reactivate organization")}return await l.json()},A_=async(n,i="")=>{const l=await fetch(`${zt}/api/organizations/${n}/delete-permanently/`,{method:"DELETE",headers:Ut(),body:JSON.stringify({confirm:!0,reason:i})});if(!l.ok){const o=await l.json().catch(()=>({}));throw new Error(o.message||"Failed to permanently delete organization")}return await l.json()},mg=async n=>{const i=await fetch(`${zt}/api/organizations/${n}/`,{method:"GET",headers:Ut()});if(!i.ok){const l=await i.json().catch(()=>({}));throw new Error(l.message||"Failed to fetch organization details")}return await i.json()},z_=async()=>{const n=await fetch(`${zt}/api/organizations/types/`,{method:"GET",headers:Ut()});if(!n.ok){const i=await n.json().catch(()=>({}));throw new Error(i.message||"Failed to fetch organization types")}return await n.json()},k_=async(n={})=>{const i=new URLSearchParams(n).toString(),l=`${zt}/api/trust/bilateral/${i?`?${i}`:""}`,o=await fetch(l,{method:"GET",headers:Ut()});if(!o.ok){const u=await o.json().catch(()=>({}));throw new Error(u.message||"Failed to fetch trust relationships")}return await o.json()},E_=async n=>{const i={responding_organization_id:n.target_organization,trust_level:n.trust_level,message:n.notes||""},l=await fetch(`${zt}/api/trust/bilateral/request/`,{method:"POST",headers:Ut(),body:JSON.stringify(i)});if(!l.ok){const o=await l.json().catch(()=>({}));throw new Error(o.message||"Failed to create trust relationship")}return await l.json()},pg=async(n,i)=>{const l=await fetch(`${zt}/api/trust/bilateral/${n}/update/`,{method:"PUT",headers:Ut(),body:JSON.stringify(i)});if(!l.ok){const o=await l.json().catch(()=>({}));throw new Error(o.message||"Failed to update trust relationship")}return await l.json()},M_=async(n,i,l=null,o="")=>{const u=await fetch(`${zt}/api/trust/bilateral/${n}/respond/`,{method:"POST",headers:Ut(),body:JSON.stringify({action:i,trust_level:l,message:o})});if(!u.ok){const f=await u.json().catch(()=>({}));throw new Error(f.message||"Failed to respond to trust relationship")}return await u.json()},D_=async(n,i="")=>{const l=await fetch(`${zt}/api/trust/bilateral/${n}/revoke/`,{method:"DELETE",headers:Ut(),body:JSON.stringify({message:i})});if(!l.ok){const o=await l.json().catch(()=>({}));throw new Error(o.message||"Failed to delete trust relationship")}return await l.json()},R_=async(n={})=>{const i=new URLSearchParams(n).toString(),l=`${zt}/api/trust/community/${i?`?${i}`:""}`,o=await fetch(l,{method:"GET",headers:Ut()});if(!o.ok){const u=await o.json().catch(()=>({}));throw new Error(u.message||"Failed to fetch trust groups")}return await o.json()},U_=async n=>{const i=await fetch(`${zt}/api/trust/community/`,{method:"POST",headers:Ut(),body:JSON.stringify(n)});if(!i.ok){const l=await i.json().catch(()=>({}));throw new Error(l.message||"Failed to create trust group")}return await i.json()},O_=async(n,i)=>{const l=await fetch(`${zt}/api/trust-management/groups/${n}/`,{method:"PUT",headers:Ut(),body:JSON.stringify(i)});if(!l.ok){const o=await l.json().catch(()=>({}));throw new Error(o.message||"Failed to update trust group")}return await l.json()},L_=async n=>{const i=await fetch(`${zt}/api/trust-management/groups/${n}/`,{method:"DELETE",headers:Ut()});if(!i.ok){const l=await i.json().catch(()=>({}));throw new Error(l.message||"Failed to delete trust group")}return await i.json()},q_=async n=>{const i=await fetch(`${zt}/api/trust-management/groups/${n}/join/`,{method:"POST",headers:Ut()});if(!i.ok){const l=await i.json().catch(()=>({}));throw new Error(l.message||"Failed to join trust group")}return await i.json()},B_=async()=>{const n=await fetch(`${zt}/api/trust-management/metrics/`,{method:"GET",headers:Ut()});if(!n.ok){const i=await n.json().catch(()=>({}));throw new Error(i.message||"Failed to fetch trust metrics")}return await n.json()},H_=async()=>{const n=await fetch(`${zt}/api/trust/levels/`,{method:"GET",headers:Ut()});if(!n.ok){const i=await n.json().catch(()=>({}));throw new Error(i.message||"Failed to fetch trust levels")}return await n.json()};class Eo{static show(i="medium"){if(this.isActive)return;this.isActive=!0,this.overlayElement=document.createElement("div"),this.overlayElement.id="bluevision-loading-overlay",this.overlayElement.style.cssText=`
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
          width: ${l[i]};
          height: ${l[i]};
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
    `,document.body.appendChild(this.overlayElement)}static hide(){this.isActive&&(this.isActive=!1,this.overlayElement&&(document.body.removeChild(this.overlayElement),this.overlayElement=null))}}Dd(Eo,"overlayElement",null),Dd(Eo,"isActive",!1);const _s=({size:n="medium",fullscreen:i=!1})=>{if(w.useEffect(()=>{if(i)return Eo.show(n),()=>Eo.hide()},[i,n]),i)return null;const l={small:{width:"32px",height:"32px"},medium:{width:"48px",height:"48px"},large:{width:"64px",height:"64px"}};return t.jsxs(t.Fragment,{children:[t.jsx("style",{children:`
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
        `}),t.jsx("div",{style:{display:"flex",justifyContent:"center",alignItems:"center",padding:"40px 20px"},children:t.jsx("div",{className:"bluevision-rotated",children:t.jsx("span",{className:"bluevision-loader",style:l[n]})})})]})},Lu=({isOpen:n,onClose:i,onConfirm:l,title:o,message:u,confirmText:f="Confirm",cancelText:m="Cancel",confirmButtonClass:x="confirm-btn",isDestructive:p=!1,actionType:h="default"})=>{const v=()=>{l(),i()},y=()=>{i()},N=Ui.useCallback(()=>h==="activate"||h==="reactivate"?"btn btn-success confirmation-btn-green":h==="deactivate"||h==="delete"?"btn btn-danger confirmation-btn-red":`btn ${p?"btn-danger":"btn-primary"}`,[h,p]);return Ui.useEffect(()=>{if(!n)return;const S=A=>{A.key==="Escape"&&i()};return document.addEventListener("keydown",S),document.body.style.overflow="hidden",()=>{document.removeEventListener("keydown",S),document.body.style.overflow="unset"}},[n,i]),n?t.jsx("div",{className:"confirmation-modal-overlay",onClick:y,children:t.jsxs("div",{className:"confirmation-modal",onClick:S=>S.stopPropagation(),children:[t.jsxs("div",{className:"confirmation-modal-header",children:[t.jsx("h3",{children:o}),t.jsx("button",{className:"confirmation-modal-close",onClick:y,"aria-label":"Close",children:"×"})]}),t.jsx("div",{className:"confirmation-modal-body",children:t.jsx("p",{children:u})}),t.jsxs("div",{className:"confirmation-modal-footer",children:[t.jsx("button",{className:"btn btn-secondary",onClick:y,children:m}),t.jsx("button",{className:N(),onClick:v,children:f})]})]})}):null},qu=({currentPage:n,totalItems:i,itemsPerPage:l,onPageChange:o,showInfo:u=!0,showJumpToPage:f=!0})=>{const m=Math.ceil(i/l),x=(n-1)*l+1,p=Math.min(n*l,i);if(m<=1)return null;const h=()=>{const N=[],S=[];for(let A=Math.max(2,n-2);A<=Math.min(m-1,n+2);A++)N.push(A);return n-2>2?S.push(1,"..."):S.push(1),S.push(...N),n+2<m-1?S.push("...",m):S.push(m),S},v=y=>{if(y.key==="Enter"){const N=parseInt(y.target.value);N>=1&&N<=m&&(o(N),y.target.value="")}};return t.jsxs("div",{className:"pagination-container",children:[u&&t.jsxs("div",{className:"pagination-info",children:["Showing ",x,"-",p," of ",i," items"]}),t.jsxs("div",{className:"pagination-controls",children:[t.jsx("button",{className:"pagination-btn",onClick:()=>o(1),disabled:n===1,title:"Go to first page",children:"⏮ First"}),t.jsx("button",{className:"pagination-btn",onClick:()=>o(n-1),disabled:n===1,title:"Go to previous page",children:"← Previous"}),t.jsx("div",{className:"pagination-pages",children:h().map((y,N)=>t.jsx(Ui.Fragment,{children:y==="..."?t.jsx("span",{className:"pagination-dots",children:"..."}):t.jsx("button",{className:`pagination-page ${n===y?"active":""}`,onClick:()=>o(y),children:y})},N))}),t.jsx("button",{className:"pagination-btn",onClick:()=>o(n+1),disabled:n===m,title:"Go to next page",children:"Next →"}),t.jsx("button",{className:"pagination-btn",onClick:()=>o(m),disabled:n===m,title:"Go to last page",children:"Last ⏭"})]}),f&&m>5&&t.jsxs("div",{className:"pagination-jump",children:[t.jsxs("label",{children:["Jump to page:",t.jsx("input",{type:"number",min:"1",max:m,placeholder:`1-${m}`,onKeyPress:v,className:"pagination-jump-input",title:`Enter a page number between 1 and ${m}`})]}),t.jsx("button",{className:"pagination-btn pagination-jump-btn",onClick:()=>{const y=document.querySelector(".pagination-jump-input"),N=parseInt(y.value);N>=1&&N<=m&&(o(N),y.value="")},title:"Jump to entered page",children:"Go"})]})]})},I_=({active:n=!0,initialSection:i=null})=>{console.log("UserManagement rendered with props:",{active:n,initialSection:i});const[l,o]=w.useState([]),[u,f]=w.useState([]),[m,x]=w.useState(!0),[p,h]=w.useState(null),[v,y]=w.useState(null),[N,S]=w.useState(()=>i==="create"?!0:new URLSearchParams(window.location.search).get("section")==="create"),[A,z]=w.useState(()=>{if(i==="create")return"add";const Ce=new URLSearchParams(window.location.search).get("section");return"add"}),[U,oe]=w.useState(null),[ie,me]=w.useState(""),[Ae,de]=w.useState(""),[pe,W]=w.useState(!1),[Ke,he]=w.useState(!1),[De,xe]=w.useState(!1),[je,ze]=w.useState(!1),[we,Ze]=w.useState(null),[L,ne]=w.useState(!1),[P,Ue]=w.useState(null),[T,F]=w.useState(1),[le,ce]=w.useState(10),[fe,Oe]=w.useState([]),[ve,ke]=w.useState({username:"",email:"",first_name:"",last_name:"",password:"",role:"viewer",organization_id:"",is_verified:!1,is_active:!0}),$e=["admin","publisher","viewer"],re=(v==null?void 0:v.role)==="publisher";(v==null?void 0:v.role)==="admin"||(v==null||v.role);const k=()=>re?["viewer"]:$e,se=B=>re?B?!["publisher","admin","BlueVisionAdmin"].includes(B.role):!1:!0;w.useEffect(()=>{if(n){const B=p_();y(B),V(),ue()}},[n]),w.useEffect(()=>{i==="create"?(console.log("UserManagement: Opening create modal from prop"),S(!0),z("add")):(i==="roles"||i==="passwords")&&(console.log("UserManagement: Section from prop:",i),S(!1))},[i]),w.useEffect(()=>{const B=()=>{const M=new URLSearchParams(window.location.search).get("section");M==="create"?(S(!0),z("add")):(M==="roles"||M==="passwords")&&S(!1)};return window.addEventListener("popstate",B),()=>{window.removeEventListener("popstate",B)}},[]);const V=async()=>{try{x(!0),h(null),await new Promise(Q=>setTimeout(Q,1e3));const B=await x_();console.log("Users API response:",B),console.log("Full response object:",JSON.stringify(B,null,2));let Ce=[];B.results&&B.results.users?Ce=B.results.users:B.data&&B.data.users?Ce=B.data.users:B.users?Ce=B.users:B.data&&Array.isArray(B.data)?Ce=B.data:Array.isArray(B)&&(Ce=B),console.log("Extracted users data:",Ce),console.log("Users data length:",Ce.length);const M=Array.isArray(Ce)?Ce:[];Oe(M),o(M)}catch(B){console.error("Failed to load users:",B),h("Failed to load users: "+B.message),o([])}finally{x(!1)}},ue=async()=>{try{const B=await Ou();console.log("Organizations API response:",B);let Ce=[];B.results&&B.results.organizations?Ce=B.results.organizations:B.data&&B.data.organizations?Ce=B.data.organizations:B.organizations?Ce=B.organizations:B.data&&Array.isArray(B.data)?Ce=B.data:Array.isArray(B)&&(Ce=B),console.log("Extracted organizations data:",Ce),f(Array.isArray(Ce)?Ce:[])}catch(B){console.error("Failed to load organizations:",B),f([])}},Se=w.useMemo(()=>{let B=[...fe];return ie&&(B=B.filter(Ce=>{var M,Q,$,ye;return((M=Ce.username)==null?void 0:M.toLowerCase().includes(ie.toLowerCase()))||((Q=Ce.first_name)==null?void 0:Q.toLowerCase().includes(ie.toLowerCase()))||(($=Ce.last_name)==null?void 0:$.toLowerCase().includes(ie.toLowerCase()))||((ye=Ce.email)==null?void 0:ye.toLowerCase().includes(ie.toLowerCase()))})),Ae&&(B=B.filter(Ce=>Ce.role===Ae)),B},[fe,ie,Ae]),Fe=w.useMemo(()=>{const B=(T-1)*le,Ce=B+le;return Se.slice(B,Ce)},[Se,T,le]);w.useEffect(()=>{o(Fe)},[Fe]);const it=B=>{F(B)},et=B=>{ce(B),F(1)},Gt=()=>{z("add"),oe(null),h(null),ke({username:"",email:"",first_name:"",last_name:"",password:"",role:"viewer",organization_id:"",is_verified:!1,is_active:!0}),S(!0)},wt=async B=>{var Ce,M,Q;try{W(!0),h(null),await new Promise(tt=>setTimeout(tt,800));const $=await hg(B);console.log("Edit user response:",$);let ye=null;if($.success&&((Ce=$.data)!=null&&Ce.user))ye=$.data.user;else if((M=$.data)!=null&&M.user)ye=$.data.user;else if($.user)ye=$.user;else if($.data&&typeof $.data=="object"&&$.data.username)ye=$.data;else throw console.error("Unable to extract user from response:",$),new Error("Invalid response format");if(console.log("Edit user data:",ye),re&&ye){const tt=ye.role;if(tt==="publisher"||tt==="admin"||tt==="BlueVisionAdmin"){h("Publishers cannot edit users with publisher, admin, or BlueVisionAdmin roles"),W(!1);return}}if(!ye||!ye.username)throw console.error("User data not found or invalid in response. Full response:",$),new Error("User data not found or invalid in response");z("edit"),oe(ye);const Ge={username:ye.username||"",email:ye.email||"",first_name:ye.first_name||"",last_name:ye.last_name||"",password:"",role:ye.role||"viewer",organization_id:((Q=ye.organization)==null?void 0:Q.id)||ye.organization_id||"",is_verified:!!ye.is_verified,is_active:ye.is_active!==!1};console.log("Setting form data for edit:",Ge),ke(Ge),S(!0)}catch($){console.error("Error in handleEditUser:",$),h("Failed to load user details: "+($.message||$))}finally{W(!1)}},Tt=async B=>{var Ce,M,Q;try{W(!0),h(null),await new Promise(tt=>setTimeout(tt,800));const $=await hg(B);console.log("View user response:",$);let ye=null;if($.success&&((Ce=$.data)!=null&&Ce.user))ye=$.data.user;else if((M=$.data)!=null&&M.user)ye=$.data.user;else if($.user)ye=$.user;else if($.data&&typeof $.data=="object"&&$.data.username)ye=$.data;else throw console.error("Unable to extract user from response:",$),new Error("Invalid response format");if(console.log("View user data:",ye),re&&ye){const tt=ye.role;if(tt==="publisher"||tt==="admin"||tt==="BlueVisionAdmin"){h("Publishers cannot view users with publisher, admin, or BlueVisionAdmin roles"),W(!1);return}}if(!ye||!ye.username)throw console.error("User data not found or invalid in response. Full response:",$),new Error("User data not found or invalid in response");z("view"),oe(ye);const Ge={username:ye.username||"",email:ye.email||"",first_name:ye.first_name||"",last_name:ye.last_name||"",password:"",role:ye.role||"viewer",organization_id:((Q=ye.organization)==null?void 0:Q.id)||ye.organization_id||"",is_verified:!!ye.is_verified,is_active:ye.is_active!==!1};console.log("Setting form data for view:",Ge),ke(Ge),S(!0)}catch($){console.error("Error in handleViewUser:",$),h("Failed to load user details: "+($.message||$))}finally{W(!1)}},It=(B,Ce)=>{if(re){const M=fe.find(Q=>Q.id===B);if(M&&(M.role==="publisher"||M.role==="admin"||M.role==="BlueVisionAdmin")){h("Publishers cannot deactivate users with publisher, admin, or BlueVisionAdmin roles");return}}Ue({title:"Deactivate User",message:`Are you sure you want to deactivate user "${Ce}"?`,confirmText:"Deactivate",isDestructive:!0,actionType:"deactivate",action:async()=>{try{xe(!0),await new Promise(M=>setTimeout(M,800)),await b_(B,"Deactivated by admin"),V()}catch(M){h("Failed to deactivate user: "+M.message)}finally{xe(!1)}}}),ne(!0)},Kt=(B,Ce)=>{if(re){const M=fe.find(Q=>Q.id===B);if(M&&(M.role==="publisher"||M.role==="admin"||M.role==="BlueVisionAdmin")){h("Publishers cannot reactivate users with publisher, admin, or BlueVisionAdmin roles");return}}Ue({title:"Reactivate User",message:`Are you sure you want to reactivate user "${Ce}"?`,confirmText:"Reactivate",isDestructive:!1,actionType:"reactivate",action:async()=>{try{xe(!0),await new Promise(M=>setTimeout(M,800)),await j_(B,"Reactivated by admin"),V()}catch(M){h("Failed to reactivate user: "+M.message)}finally{xe(!1)}}}),ne(!0)},G=(B,Ce)=>{Ue({title:"Permanently Delete User",message:`Are you sure you want to PERMANENTLY DELETE user "${Ce}"? This action cannot be undone.`,confirmText:"Delete Permanently",isDestructive:!0,actionType:"delete",action:async()=>{try{xe(!0),await new Promise(M=>setTimeout(M,800)),await N_(B,"Deleted by admin"),V(),ze(!1),Ze(null)}catch(M){h("Failed to delete user: "+M.message)}finally{xe(!1)}}}),ne(!0)},Te=B=>{if(B.preventDefault(),A==="edit"&&ve.username){const Q=ve.username.trim();if(Q.length<3){h("Username must be at least 3 characters long");return}if(!/^[a-zA-Z0-9_]+$/.test(Q)){h("Username can only contain letters, numbers, and underscores");return}}const Ce=A==="add"?"create":"update",M=A==="add"?ve.username:U==null?void 0:U.username;Ue({title:`${A==="add"?"Create":"Update"} User`,message:`Are you sure you want to ${Ce} user "${M}"?`,confirmText:A==="add"?"Create User":"Update User",isDestructive:!1,actionType:"default",action:async()=>{try{if(he(!0),await new Promise(Q=>setTimeout(Q,1e3)),A==="add"){console.log("Creating user with data:",ve);const Q=await v_(ve);console.log("User creation successful:",Q)}else if(A==="edit"){const Q={...ve};Q.password||delete Q.password,Q.username!==U.username&&(console.log("Username changed, updating via changeUsername API"),await w_(U.id,Q.username),delete Q.username),Object.keys(Q).length>0&&(console.log("Updating user with data:",Q),console.log("Selected user ID:",U.id),await y_(U.id,Q))}S(!1),h(null),console.log("About to reload users..."),await V(),console.log("Users reloaded successfully")}catch(Q){console.error("Error in handleSubmit:",Q),Array.isArray(Q)?h(Q.join(", ")):h(typeof Q=="string"?Q:"Failed to save user: "+(Q.message||"Unknown error"))}finally{he(!1)}}}),ne(!0)},Be=B=>{const{name:Ce,value:M,type:Q,checked:$}=B.target;console.log("Input change:",{name:Ce,value:M,type:Q,checked:$}),ke(ye=>{const Ge={...ye,[Ce]:Q==="checkbox"?$:M};return console.log("Updated form data:",Ge),Ge})},Ne=Se.length,Re=B=>{const Ce=u.find(M=>M.id===B);return Ce?Ce.name:"N/A"},xt=B=>{Ze(B),ze(!0)},ft=()=>{ze(!1),Ze(null)};return n?m?t.jsx(_s,{fullscreen:!0}):p?t.jsx("div",{style:{padding:"2rem",color:"red"},children:p}):t.jsxs("div",{style:{padding:"2rem",fontFamily:"Arial, sans-serif",position:"relative"},children:[(De||Ke)&&t.jsx(_s,{fullscreen:!0}),t.jsxs("div",{style:{marginBottom:"2rem"},children:[t.jsx("h1",{style:{marginBottom:"0.5rem",color:"#333"},children:"User Management"}),re&&t.jsxs("div",{style:{padding:"0.75rem 1rem",backgroundColor:"#fff3cd",color:"#856404",borderRadius:"6px",border:"1px solid #ffeaa7",fontSize:"0.875rem",fontWeight:"500"},children:[t.jsx("strong",{children:"Publisher Mode:"})," You can view and manage users from your organization and organizations with trusted relationships. You can only create viewer users, and role changes are restricted."]})]}),t.jsxs("div",{style:{display:"flex",gap:"1rem",marginBottom:"2rem",flexWrap:"wrap",alignItems:"center"},children:[t.jsx("input",{type:"text",placeholder:"Search users...",value:ie,onChange:B=>me(B.target.value),style:{padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",minWidth:"200px",backgroundColor:"white",color:"#666"}}),t.jsxs("select",{value:Ae,onChange:B=>de(B.target.value),style:{padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:"white",color:"#666"},children:[t.jsx("option",{value:"",children:"All Roles"}),k().map(B=>t.jsx("option",{value:B,children:B},B))]}),t.jsx("button",{onClick:Gt,style:{padding:"0.5rem 1rem",backgroundColor:"#007bff",color:"white",border:"none",borderRadius:"4px",cursor:"pointer"},children:"Add User"}),t.jsx("div",{className:"items-per-page",children:t.jsxs("label",{children:["Show:",t.jsxs("select",{value:le,onChange:B=>et(parseInt(B.target.value)),children:[t.jsx("option",{value:5,children:"5"}),t.jsx("option",{value:10,children:"10"}),t.jsx("option",{value:25,children:"25"}),t.jsx("option",{value:50,children:"50"})]}),"items per page"]})})]}),t.jsx("div",{style:{marginBottom:"1rem",color:"#6c757d",fontSize:"0.875rem",textAlign:"center"},children:"💡 Click on any user row to view available actions"}),t.jsx("div",{style:{backgroundColor:"white",borderRadius:"12px",boxShadow:"0 4px 6px rgba(0,0,0,0.1)",border:"1px solid #e9ecef"},children:l.map(B=>{var Ce;return t.jsxs("div",{onClick:M=>{M.preventDefault(),M.stopPropagation(),xt(B)},style:{display:"flex",alignItems:"center",padding:"1.25rem",borderBottom:"1px solid #e9ecef",transition:"all 0.2s ease",cursor:"pointer",backgroundColor:"transparent"},onMouseEnter:M=>{M.currentTarget.style.backgroundColor="#f8f9fa",M.currentTarget.style.transform="translateX(4px)"},onMouseLeave:M=>{M.currentTarget.style.backgroundColor="transparent",M.currentTarget.style.transform="translateX(0px)"},children:[t.jsxs("div",{style:{flex:"1",minWidth:"0"},children:[t.jsxs("div",{style:{display:"flex",alignItems:"center",gap:"1rem",flexWrap:"wrap"},children:[t.jsx("div",{style:{fontWeight:"600",color:"#212529",fontSize:"1.1rem"},children:B.username}),t.jsx("div",{style:{color:"#495057"},children:`${B.first_name||""} ${B.last_name||""}`.trim()||"N/A"}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:B.role==="admin"?"#d4edda":B.role==="publisher"?"#fff3cd":"#f8f9fa",color:B.role==="admin"?"#155724":B.role==="publisher"?"#856404":"#495057"},children:B.role}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:B.is_active?"#d4edda":"#f8d7da",color:B.is_active?"#155724":"#721c24"},children:B.is_active?"Active":"Inactive"})]}),t.jsxs("div",{style:{marginTop:"0.5rem",color:"#6c757d",fontSize:"0.875rem",display:"flex",gap:"1rem",flexWrap:"wrap"},children:[t.jsx("span",{children:B.email||"No email"}),t.jsxs("span",{children:["Org: ",((Ce=B.organization)==null?void 0:Ce.name)||Re(B.organization_id)||"N/A"]})]})]}),t.jsx("div",{style:{fontSize:"1.2rem",color:"#6c757d",marginLeft:"1rem",transition:"all 0.2s ease",display:"flex",alignItems:"center",justifyContent:"center",width:"40px",height:"40px",borderRadius:"50%",backgroundColor:"rgba(108, 117, 125, 0.1)"},children:"→"})]},B.id)})}),l.length===0&&fe.length>0&&t.jsx("div",{style:{textAlign:"center",padding:"2rem",color:"#666"},children:"No users found matching your criteria."}),fe.length===0&&t.jsx("div",{style:{textAlign:"center",padding:"2rem",color:"#666"},children:'No users available. Click "Add User" to create the first user.'}),fe.length>0&&t.jsx(qu,{currentPage:T,totalItems:Ne,itemsPerPage:le,onPageChange:it,showInfo:!0,showJumpToPage:!0}),N&&t.jsx("div",{style:{position:"fixed",top:0,left:0,width:"100%",height:"100%",backgroundColor:"rgba(0, 0, 0, 0.5)",display:"flex",alignItems:"center",justifyContent:"center",zIndex:1e3},children:t.jsxs("div",{style:{backgroundColor:"white",padding:"2rem",borderRadius:"8px",maxWidth:"500px",width:"90%",maxHeight:"80vh",overflowY:"auto"},children:[t.jsx("h2",{style:{marginBottom:"1.5rem",color:"#333"},children:A==="add"?"Add New User":A==="edit"?"Edit User":"View User"}),pe?t.jsx(_s,{size:"medium"}):t.jsxs(t.Fragment,{children:[p&&t.jsx("div",{style:{padding:"1rem",backgroundColor:"#f8d7da",color:"#721c24",borderRadius:"4px",marginBottom:"1rem",border:"1px solid #f5c6cb"},children:p}),t.jsxs("form",{onSubmit:Te,children:[t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsxs("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:["Username ",!ve.username&&A==="add"&&t.jsx("span",{style:{color:"red"},children:"*"})]}),t.jsx("input",{type:"text",name:"username",value:ve.username,onChange:Be,disabled:A==="view",required:!0,pattern:"[a-zA-Z0-9_]+",title:"Username can only contain letters, numbers, and underscores",style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:A==="view"?"#f8f9fa":"white",color:A==="view"?"#333":"#000"}}),A==="edit"&&t.jsx("div",{style:{fontSize:"0.875rem",color:"#666",marginTop:"0.25rem"},children:"Only letters, numbers, and underscores allowed (minimum 3 characters)"})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsxs("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:["Email ",A==="add"&&!ve.email&&t.jsx("span",{style:{color:"red"},children:"*"})," ",!ve.email&&A==="view"&&"(Not available at current access level)"]}),t.jsx("input",{type:"email",name:"email",value:ve.email,onChange:Be,disabled:A==="view",required:A==="add",placeholder:!ve.email&&A!=="add"?"Email not available":"",style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:A==="view"?"#f8f9fa":"white",color:A==="view"?"#333":"#000"}})]}),t.jsxs("div",{style:{display:"flex",gap:"1rem",marginBottom:"1rem"},children:[t.jsxs("div",{style:{flex:1},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"First Name"}),t.jsx("input",{type:"text",name:"first_name",value:ve.first_name,onChange:Be,disabled:A==="view",style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:A==="view"?"#f8f9fa":"white",color:A==="view"?"#333":"#000"}})]}),t.jsxs("div",{style:{flex:1},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Last Name"}),t.jsx("input",{type:"text",name:"last_name",value:ve.last_name,onChange:Be,disabled:A==="view",style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:A==="view"?"#f8f9fa":"white",color:A==="view"?"#333":"#000"}})]})]}),A==="add"&&t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsxs("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:["Password ",!ve.password&&t.jsx("span",{style:{color:"red"},children:"*"})]}),t.jsx("input",{type:"password",name:"password",value:ve.password,onChange:Be,required:!0,style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:"white",color:"#999"}})]}),A==="edit"&&t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"New Password (leave blank to keep current)"}),t.jsx("input",{type:"password",name:"password",value:ve.password,onChange:Be,style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:"white",color:"#999"}})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsxs("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:["Role",re&&A!=="view"&&t.jsx("span",{style:{fontSize:"0.75rem",color:"#856404",marginLeft:"0.5rem"},children:"(Limited to viewer role)"})]}),t.jsx("select",{name:"role",value:ve.role,onChange:Be,disabled:A==="view"||re&&A==="edit",style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:A==="view"||re&&A==="edit"?"#f8f9fa":"white",color:A==="view"||re&&A==="edit"?"#666":"#000"},children:k().map(B=>t.jsx("option",{value:B,children:B},B))}),re&&A==="edit"&&t.jsx("div",{style:{fontSize:"0.75rem",color:"#666",marginTop:"0.25rem"},children:"Role changes are restricted for publisher users"})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsxs("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:["Organization ",A==="add"&&!ve.organization_id&&t.jsx("span",{style:{color:"red"},children:"*"})]}),t.jsxs("select",{name:"organization_id",value:ve.organization_id,onChange:Be,disabled:A==="view",required:A==="add",style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:A==="view"?"#f8f9fa":"white",color:A==="view"?"#333":"#000"},children:[t.jsx("option",{value:"",children:"Select Organization"}),u.map(B=>t.jsx("option",{value:B.id,children:B.name},B.id))]})]}),t.jsxs("div",{style:{display:"flex",gap:"1rem",marginBottom:"1rem"},children:[t.jsxs("label",{style:{display:"flex",alignItems:"center",gap:"0.5rem"},children:[t.jsx("input",{type:"checkbox",name:"is_verified",checked:ve.is_verified,onChange:Be,disabled:A==="view"}),"Verified"]}),t.jsxs("label",{style:{display:"flex",alignItems:"center",gap:"0.5rem"},children:[t.jsx("input",{type:"checkbox",name:"is_active",checked:ve.is_active,onChange:Be,disabled:A==="view"}),"Active"]})]}),t.jsxs("div",{style:{display:"flex",gap:"1rem",justifyContent:"flex-end"},children:[t.jsx("button",{type:"button",onClick:()=>S(!1),style:{padding:"0.5rem 1rem",border:"1px solid #ddd",backgroundColor:"white",color:"#666",borderRadius:"4px",cursor:"pointer"},children:A==="view"?"Close":"Cancel"}),A!=="view"&&t.jsx("button",{type:"submit",style:{padding:"0.5rem 1rem",backgroundColor:"#007bff",color:"white",border:"none",borderRadius:"4px",cursor:"pointer"},children:A==="add"?"Add User":"Update User"})]})]})]})]})}),je&&we&&t.jsx("div",{style:{position:"fixed",top:0,left:0,width:"100%",height:"100%",backgroundColor:"rgba(0, 0, 0, 0.5)",display:"flex",alignItems:"center",justifyContent:"center",zIndex:1001},children:t.jsxs("div",{style:{backgroundColor:"white",padding:"2rem",borderRadius:"12px",minWidth:"300px",maxWidth:"400px",boxShadow:"0 10px 25px rgba(0,0,0,0.1)"},children:[t.jsxs("div",{style:{marginBottom:"1.5rem"},children:[t.jsx("h3",{style:{margin:"0 0 0.5rem 0",color:"#333",fontSize:"1.25rem",wordBreak:"break-word",lineHeight:"1.3"},children:we.username}),t.jsx("div",{style:{color:"#666",fontSize:"0.875rem",marginBottom:"0.5rem"},children:`${we.first_name||""} ${we.last_name||""}`.trim()||"N/A"}),t.jsxs("div",{style:{color:"#666",fontSize:"0.875rem",display:"flex",gap:"0.5rem",alignItems:"center"},children:[t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:we.role==="admin"?"#d4edda":we.role==="publisher"?"#fff3cd":"#f8f9fa",color:we.role==="admin"?"#155724":we.role==="publisher"?"#856404":"#495057"},children:we.role}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:we.is_active?"#d4edda":"#f8d7da",color:we.is_active?"#155724":"#721c24"},children:we.is_active?"Active":"Inactive"})]})]}),t.jsxs("div",{style:{display:"flex",flexDirection:"column",gap:"0.75rem"},children:[se(we)&&t.jsx("button",{onClick:()=>{ft(),Tt(we.id)},style:{padding:"0.75rem 1rem",backgroundColor:"#5D8AA8",color:"white",border:"none",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:B=>B.target.style.backgroundColor="#4A7088",onMouseLeave:B=>B.target.style.backgroundColor="#5D8AA8",children:"View Details"}),se(we)&&t.jsx("button",{onClick:()=>{ft(),wt(we.id)},style:{padding:"0.75rem 1rem",backgroundColor:"#5D8AA8",color:"white",border:"none",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:B=>B.target.style.backgroundColor="#4A7088",onMouseLeave:B=>B.target.style.backgroundColor="#5D8AA8",children:"Edit User"}),se(we)&&(we.is_active?t.jsx("button",{onClick:()=>{ft(),It(we.id,we.username)},style:{padding:"0.75rem 1rem",backgroundColor:"white",color:"#5D8AA8",border:"2px solid #5D8AA8",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:B=>{B.target.style.borderColor="#dc3545",B.target.style.color="#dc3545"},onMouseLeave:B=>{B.target.style.borderColor="#5D8AA8",B.target.style.color="#5D8AA8"},children:"Deactivate User"}):t.jsx("button",{onClick:()=>{ft(),Kt(we.id,we.username)},style:{padding:"0.75rem 1rem",backgroundColor:"white",color:"#5D8AA8",border:"2px solid #5D8AA8",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:B=>{B.target.style.borderColor="#28a745",B.target.style.color="#28a745"},onMouseLeave:B=>{B.target.style.borderColor="#5D8AA8",B.target.style.color="#5D8AA8"},children:"Reactivate User"})),t.jsx("button",{onClick:()=>{ft(),G(we.id,we.username)},style:{padding:"0.75rem 1rem",backgroundColor:"#5D8AA8",color:"white",border:"none",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:B=>B.target.style.backgroundColor="#4A7088",onMouseLeave:B=>B.target.style.backgroundColor="#5D8AA8",children:"Permanently Delete"})]}),t.jsx("div",{style:{marginTop:"1.5rem",paddingTop:"1rem",borderTop:"1px solid #e9ecef"},children:t.jsx("button",{onClick:ft,style:{padding:"0.5rem 1rem",border:"1px solid #ddd",backgroundColor:"white",color:"#666",borderRadius:"6px",cursor:"pointer",width:"100%",fontSize:"0.875rem"},children:"Cancel"})})]})}),t.jsx(Lu,{isOpen:L,onClose:()=>ne(!1),onConfirm:P==null?void 0:P.action,title:P==null?void 0:P.title,message:P==null?void 0:P.message,confirmText:P==null?void 0:P.confirmText,isDestructive:P==null?void 0:P.isDestructive,actionType:P==null?void 0:P.actionType})]}):null},$_=({active:n=!0,initialSection:i=null})=>{console.log("OrganisationManagement rendered with props:",{active:n,initialSection:i});const[l,o]=w.useState([]),[u,f]=w.useState(["educational","government","private"]),[m,x]=w.useState(!0),[p,h]=w.useState(null),[v,y]=w.useState(()=>i==="create"?!0:new URLSearchParams(window.location.search).get("section")==="create"),[N,S]=w.useState(()=>{if(i==="create")return"add";const Te=new URLSearchParams(window.location.search).get("section");return"add"}),[A,z]=w.useState(null),[U,oe]=w.useState(""),[ie,me]=w.useState(""),[Ae,de]=w.useState(!1),[pe,W]=w.useState(!1),[Ke,he]=w.useState(!1),[De,xe]=w.useState(!1),[je,ze]=w.useState(null),[we,Ze]=w.useState(!1),[L,ne]=w.useState(null),[P,Ue]=w.useState(1),[T,F]=w.useState(10),[le,ce]=w.useState([]),[fe,Oe]=w.useState({name:"",domain:"",contact_email:"",description:"",website:"",organization_type:"educational",primary_user:{username:"",email:"",password:"",first_name:"",last_name:""}}),ve=async()=>{var G;try{const Te=await z_();if(console.log("Organization types response:",Te),Te.success&&((G=Te.data)!=null&&G.organization_types)){const Be=Te.data.organization_types.map(Ne=>Ne.value);f(Be),console.log("Loaded organization types:",Be)}}catch(Te){console.error("Failed to load organization types:",Te)}};w.useEffect(()=>{n&&(ke(),ve())},[n]),w.useEffect(()=>{i==="create"?(console.log("OrganisationManagement: Opening create modal from prop"),y(!0),S("add")):(i==="roles"||i==="passwords")&&(console.log("OrganisationManagement: Section from prop:",i),y(!1))},[i]),w.useEffect(()=>{const G=()=>{new URLSearchParams(window.location.search).get("section")==="create"&&(y(!0),S("add"))};return window.addEventListener("popstate",G),()=>{window.removeEventListener("popstate",G)}},[]);const ke=async()=>{try{x(!0),h(null),await new Promise(Ne=>setTimeout(Ne,1e3));const G=await Ou();console.log("Organizations API response:",G),console.log("Full response object:",JSON.stringify(G,null,2));let Te=[];G.results&&G.results.organizations?Te=G.results.organizations:G.data&&G.data.organizations?Te=G.data.organizations:G.organizations?Te=G.organizations:G.data&&Array.isArray(G.data)?Te=G.data:Array.isArray(G)&&(Te=G),console.log("Extracted organizations data:",Te),console.log("Organizations data length:",Te.length);const Be=Array.isArray(Te)?Te:[];ce(Be),o(Be)}catch(G){console.error("Failed to load organizations:",G),h("Failed to load organizations: "+G.message),o([])}finally{x(!1)}},$e=w.useMemo(()=>{let G=[...le];return U&&(G=G.filter(Te=>{var Be,Ne,Re;return((Be=Te.name)==null?void 0:Be.toLowerCase().includes(U.toLowerCase()))||((Ne=Te.domain)==null?void 0:Ne.toLowerCase().includes(U.toLowerCase()))||((Re=Te.contact_email)==null?void 0:Re.toLowerCase().includes(U.toLowerCase()))})),ie&&(G=G.filter(Te=>Te.organization_type===ie)),G},[le,U,ie]),re=w.useMemo(()=>{const G=(P-1)*T,Te=G+T;return $e.slice(G,Te)},[$e,P,T]);w.useEffect(()=>{o(re)},[re]);const k=G=>{Ue(G)},se=G=>{F(G),Ue(1)},V=()=>{S("add"),z(null),h(null),Oe({name:"",domain:"",contact_email:"",description:"",website:"",organization_type:"educational",primary_user:{username:"",email:"",password:"",first_name:"",last_name:""}}),y(!0)},ue=async G=>{var Te,Be;try{de(!0),h(null),await new Promise(ft=>setTimeout(ft,800));const Ne=await mg(G);console.log("Edit organization response:",Ne);let Re=null;if(Ne.success&&((Te=Ne.data)!=null&&Te.organization))Re=Ne.data.organization;else if((Be=Ne.data)!=null&&Be.organization)Re=Ne.data.organization;else if(Ne.organization)Re=Ne.organization;else if(Ne.data&&typeof Ne.data=="object"&&Ne.data.name)Re=Ne.data;else throw console.error("Unable to extract organization from response:",Ne),new Error("Invalid response format");if(console.log("Edit organization data:",Re),!Re||!Re.name)throw console.error("Organization data not found or invalid in response. Full response:",Ne),new Error("Organization data not found or invalid in response");S("edit"),z(Re);const xt={name:Re.name||"",domain:Re.domain||"",contact_email:Re.contact_email||"",description:Re.description||"",website:Re.website||"",organization_type:Re.organization_type||"educational",primary_user:{username:"",email:"",password:"",first_name:"",last_name:""}};console.log("Setting form data for edit:",xt),Oe(xt),y(!0)}catch(Ne){console.error("Error in handleEditOrganization:",Ne),h("Failed to load organization details: "+(Ne.message||Ne))}finally{de(!1)}},Se=async G=>{var Te,Be;try{de(!0),h(null),await new Promise(ft=>setTimeout(ft,800));const Ne=await mg(G);console.log("View organization response:",Ne);let Re=null;if(Ne.success&&((Te=Ne.data)!=null&&Te.organization))Re=Ne.data.organization;else if((Be=Ne.data)!=null&&Be.organization)Re=Ne.data.organization;else if(Ne.organization)Re=Ne.organization;else if(Ne.data&&typeof Ne.data=="object"&&Ne.data.name)Re=Ne.data;else throw console.error("Unable to extract organization from response:",Ne),new Error("Invalid response format");if(console.log("View organization data:",Re),!Re||!Re.name)throw console.error("Organization data not found or invalid in response. Full response:",Ne),new Error("Organization data not found or invalid in response");S("view"),z(Re);const xt={name:Re.name||"",domain:Re.domain||"",contact_email:Re.contact_email||"",description:Re.description||"",website:Re.website||"",organization_type:Re.organization_type||"educational",primary_user:{username:"",email:"",password:"",first_name:"",last_name:""}};console.log("Setting form data for view:",xt),Oe(xt),y(!0)}catch(Ne){console.error("Error in handleViewOrganization:",Ne),h("Failed to load organization details: "+(Ne.message||Ne))}finally{de(!1)}},Fe=(G,Te)=>{ne({title:"Deactivate Organization",message:`Are you sure you want to deactivate organisation "${Te}"?`,confirmText:"Deactivate",isDestructive:!0,actionType:"deactivate",action:async()=>{try{he(!0),await new Promise(Be=>setTimeout(Be,800)),await T_(G,"Deactivated by admin"),ke()}catch(Be){h("Failed to deactivate organization: "+Be.message)}finally{he(!1)}}}),Ze(!0)},it=(G,Te)=>{ne({title:"Reactivate Organization",message:`Are you sure you want to reactivate organisation "${Te}"?`,confirmText:"Reactivate",isDestructive:!1,actionType:"reactivate",action:async()=>{try{he(!0),await new Promise(Be=>setTimeout(Be,800)),await C_(G,"Reactivated by admin"),ke()}catch(Be){h("Failed to reactivate organization: "+Be.message)}finally{he(!1)}}}),Ze(!0)},et=(G,Te)=>{ne({title:"Permanently Delete Organization",message:`Are you sure you want to PERMANENTLY DELETE organization "${Te}"? This action cannot be undone.`,confirmText:"Delete Permanently",isDestructive:!0,actionType:"delete",action:async()=>{try{he(!0),await new Promise(Be=>setTimeout(Be,800)),await A_(G,"Deleted by admin"),ke(),xe(!1),ze(null)}catch(Be){h("Failed to delete organization: "+Be.message)}finally{he(!1)}}}),Ze(!0)},Gt=G=>{G.preventDefault();const Te=N==="add"?"create":"update",Be=N==="add"?fe.name:A==null?void 0:A.name;ne({title:`${N==="add"?"Create":"Update"} Organization`,message:`Are you sure you want to ${Te} organization "${Be}"?`,confirmText:N==="add"?"Create Organization":"Update Organization",isDestructive:!1,actionType:"default",action:async()=>{try{if(W(!0),await new Promise(Ne=>setTimeout(Ne,1e3)),N==="add")console.log("Creating organization with data:",fe),await __(fe);else if(N==="edit"){const Ne={...fe};delete Ne.primary_user,console.log("Updating organization with data:",Ne),console.log("Selected organization ID:",A.id),await S_(A.id,Ne)}y(!1),h(null),ke()}catch(Ne){console.error("Error in handleSubmit:",Ne),Array.isArray(Ne)?h(Ne.join(", ")):h(typeof Ne=="string"?Ne:"Failed to save organization: "+(Ne.message||"Unknown error"))}finally{W(!1)}}}),Ze(!0)},wt=G=>{const{name:Te,value:Be}=G.target;if(console.log("Input change:",{name:Te,value:Be}),Te.startsWith("primary_user.")){const Ne=Te.substring(13);Oe(Re=>({...Re,primary_user:{...Re.primary_user,[Ne]:Be}}))}else Oe(Ne=>({...Ne,[Te]:Be}))},Tt=$e.length,It=G=>{ze(G),xe(!0)},Kt=()=>{xe(!1),ze(null)};return n?m?t.jsx(_s,{fullscreen:!0}):p?t.jsx("div",{style:{padding:"2rem",color:"red"},children:p}):t.jsxs("div",{style:{padding:"2rem",fontFamily:"Arial, sans-serif",position:"relative"},children:[(Ke||pe)&&t.jsx(_s,{fullscreen:!0}),t.jsx("h1",{style:{marginBottom:"2rem",color:"#333"},children:"Organisation Management"}),t.jsxs("div",{style:{display:"flex",gap:"1rem",marginBottom:"2rem",flexWrap:"wrap",alignItems:"center"},children:[t.jsx("input",{type:"text",placeholder:"Search organisations...",value:U,onChange:G=>oe(G.target.value),style:{padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",minWidth:"200px",backgroundColor:"white",color:"#666"}}),t.jsxs("select",{value:ie,onChange:G=>me(G.target.value),style:{padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:"white",color:"#666"},children:[t.jsx("option",{value:"",children:"All Types"}),u.map(G=>t.jsx("option",{value:G,children:G},G))]}),t.jsx("button",{onClick:V,style:{padding:"0.5rem 1rem",backgroundColor:"#007bff",color:"white",border:"none",borderRadius:"4px",cursor:"pointer"},children:"Add Organisation"}),t.jsx("div",{className:"items-per-page",children:t.jsxs("label",{children:["Show:",t.jsxs("select",{value:T,onChange:G=>se(parseInt(G.target.value)),children:[t.jsx("option",{value:5,children:"5"}),t.jsx("option",{value:10,children:"10"}),t.jsx("option",{value:25,children:"25"}),t.jsx("option",{value:50,children:"50"})]}),"items per page"]})})]}),t.jsx("div",{style:{marginBottom:"1rem",color:"#6c757d",fontSize:"0.875rem",textAlign:"center"},children:"💡 Click on any organisation row to view available actions"}),t.jsx("div",{style:{backgroundColor:"white",borderRadius:"12px",boxShadow:"0 4px 6px rgba(0,0,0,0.1)",border:"1px solid #e9ecef"},children:l.map(G=>t.jsxs("div",{onClick:Te=>{Te.preventDefault(),Te.stopPropagation(),It(G)},style:{display:"flex",alignItems:"center",padding:"1.25rem",borderBottom:"1px solid #e9ecef",transition:"all 0.2s ease",cursor:"pointer",backgroundColor:"transparent"},onMouseEnter:Te=>{Te.currentTarget.style.backgroundColor="#f8f9fa",Te.currentTarget.style.transform="translateX(4px)"},onMouseLeave:Te=>{Te.currentTarget.style.backgroundColor="transparent",Te.currentTarget.style.transform="translateX(0px)"},children:[t.jsxs("div",{style:{flex:"1",minWidth:"0"},children:[t.jsxs("div",{style:{display:"flex",alignItems:"center",gap:"1rem",flexWrap:"wrap"},children:[t.jsx("div",{style:{fontWeight:"600",color:"#212529",fontSize:"1.1rem"},children:G.name}),t.jsx("div",{style:{color:"#495057"},children:G.domain||"N/A"}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:G.organization_type==="educational"?"#d4edda":G.organization_type==="government"?"#fff3cd":"#f8f9fa",color:G.organization_type==="educational"?"#155724":G.organization_type==="government"?"#856404":"#495057"},children:G.organization_type}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:G.is_active?"#d4edda":"#f8d7da",color:G.is_active?"#155724":"#721c24"},children:G.is_active?"Active":"Inactive"})]}),t.jsxs("div",{style:{marginTop:"0.5rem",color:"#6c757d",fontSize:"0.875rem",display:"flex",gap:"1rem",flexWrap:"wrap"},children:[t.jsx("span",{children:G.contact_email||"No email"}),G.description&&t.jsxs("span",{children:[G.description.substring(0,50),"..."]})]})]}),t.jsx("div",{style:{fontSize:"1.2rem",color:"#6c757d",marginLeft:"1rem",transition:"all 0.2s ease",display:"flex",alignItems:"center",justifyContent:"center",width:"40px",height:"40px",borderRadius:"50%",backgroundColor:"rgba(108, 117, 125, 0.1)"},children:"→"})]},G.id))}),l.length===0&&le.length>0&&t.jsx("div",{style:{textAlign:"center",padding:"2rem",color:"#666"},children:"No organisations found matching your criteria."}),le.length===0&&t.jsx("div",{style:{textAlign:"center",padding:"2rem",color:"#666"},children:'No organisations available. Click "Add Organisation" to create the first organization.'}),le.length>0&&t.jsx(qu,{currentPage:P,totalItems:Tt,itemsPerPage:T,onPageChange:k,showInfo:!0,showJumpToPage:!0}),v&&t.jsx("div",{style:{position:"fixed",top:0,left:0,width:"100%",height:"100%",backgroundColor:"rgba(0, 0, 0, 0.5)",display:"flex",alignItems:"center",justifyContent:"center",zIndex:1e3},children:t.jsxs("div",{style:{backgroundColor:"white",padding:"2rem",borderRadius:"8px",maxWidth:"600px",width:"90%",maxHeight:"80vh",overflowY:"auto"},children:[t.jsx("h2",{style:{marginBottom:"1.5rem",color:"#333"},children:N==="add"?"Add New Organisation":N==="edit"?"Edit Organisation":"View Organisation"}),Ae?t.jsx(_s,{size:"medium"}):t.jsxs(t.Fragment,{children:[p&&t.jsx("div",{style:{padding:"1rem",backgroundColor:"#f8d7da",color:"#721c24",borderRadius:"4px",marginBottom:"1rem",border:"1px solid #f5c6cb"},children:p}),t.jsxs("form",{onSubmit:Gt,children:[t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Organisation Name *"}),t.jsx("input",{type:"text",name:"name",value:fe.name,onChange:wt,disabled:N==="view",required:!0,style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:N==="view"?"#f8f9fa":"white",color:"#333"}})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Domain"}),t.jsx("input",{type:"text",name:"domain",value:fe.domain,onChange:wt,disabled:N==="view",placeholder:"e.g., university.edu",style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:N==="view"?"#f8f9fa":"white",color:"#333"}})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Contact Email *"}),t.jsx("input",{type:"email",name:"contact_email",value:fe.contact_email,onChange:wt,disabled:N==="view",required:!0,style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:N==="view"?"#f8f9fa":"white",color:"#333"}})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Organisation Type *"}),t.jsx("select",{name:"organization_type",value:fe.organization_type,onChange:wt,disabled:N==="view",required:!0,style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:N==="view"?"#f8f9fa":"white",color:"#333"},children:u.map(G=>t.jsx("option",{value:G,children:G},G))})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Description"}),t.jsx("textarea",{name:"description",value:fe.description,onChange:wt,disabled:N==="view",rows:"3",style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:N==="view"?"#f8f9fa":"white",color:"#333",resize:"vertical"}})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Website"}),t.jsx("input",{type:"url",name:"website",value:fe.website,onChange:wt,disabled:N==="view",placeholder:"https://www.example.com",style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:N==="view"?"#f8f9fa":"white",color:"#333"}})]}),N==="add"&&t.jsxs("div",{children:[t.jsx("h3",{style:{marginBottom:"1rem",color:"#333",borderTop:"1px solid #ddd",paddingTop:"1rem"},children:"Primary User (Administrator)"}),t.jsxs("div",{style:{display:"flex",gap:"1rem",marginBottom:"1rem"},children:[t.jsxs("div",{style:{flex:1},children:[t.jsxs("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:["Username ",!fe.primary_user.username&&t.jsx("span",{style:{color:"red"},children:"*"})]}),t.jsx("input",{type:"text",name:"primary_user.username",value:fe.primary_user.username,onChange:wt,required:!0,style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:"white",color:"#000"}})]}),t.jsxs("div",{style:{flex:1},children:[t.jsxs("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:["Email ",!fe.primary_user.email&&t.jsx("span",{style:{color:"red"},children:"*"})]}),t.jsx("input",{type:"email",name:"primary_user.email",value:fe.primary_user.email,onChange:wt,required:!0,style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:"white",color:"#000"}})]})]}),t.jsxs("div",{style:{display:"flex",gap:"1rem",marginBottom:"1rem"},children:[t.jsxs("div",{style:{flex:1},children:[t.jsxs("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:["First Name ",!fe.primary_user.first_name&&t.jsx("span",{style:{color:"red"},children:"*"})]}),t.jsx("input",{type:"text",name:"primary_user.first_name",value:fe.primary_user.first_name,onChange:wt,required:!0,style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:"white",color:"#000"}})]}),t.jsxs("div",{style:{flex:1},children:[t.jsxs("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:["Last Name ",!fe.primary_user.last_name&&t.jsx("span",{style:{color:"red"},children:"*"})]}),t.jsx("input",{type:"text",name:"primary_user.last_name",value:fe.primary_user.last_name,onChange:wt,required:!0,style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:"white",color:"#000"}})]})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsxs("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:["Password ",!fe.primary_user.password&&t.jsx("span",{style:{color:"red"},children:"*"})]}),t.jsx("input",{type:"password",name:"primary_user.password",value:fe.primary_user.password,onChange:wt,required:!0,style:{width:"100%",padding:"0.5rem",border:"1px solid #ddd",borderRadius:"4px",backgroundColor:"white",color:"#999"}})]})]}),t.jsxs("div",{style:{display:"flex",gap:"1rem",justifyContent:"flex-end"},children:[t.jsx("button",{type:"button",onClick:()=>y(!1),style:{padding:"0.5rem 1rem",border:"1px solid #ddd",backgroundColor:"white",color:"#666",borderRadius:"4px",cursor:"pointer"},children:N==="view"?"Close":"Cancel"}),N!=="view"&&t.jsx("button",{type:"submit",style:{padding:"0.5rem 1rem",backgroundColor:"#007bff",color:"white",border:"none",borderRadius:"4px",cursor:"pointer"},children:N==="add"?"Add Organisation":"Update Organisation"})]})]})]})]})}),De&&je&&t.jsx("div",{style:{position:"fixed",top:0,left:0,width:"100%",height:"100%",backgroundColor:"rgba(0, 0, 0, 0.5)",display:"flex",alignItems:"center",justifyContent:"center",zIndex:1001},children:t.jsxs("div",{style:{backgroundColor:"white",padding:"2rem",borderRadius:"12px",minWidth:"300px",maxWidth:"400px",boxShadow:"0 10px 25px rgba(0,0,0,0.1)"},children:[t.jsxs("div",{style:{marginBottom:"1.5rem"},children:[t.jsx("h3",{style:{margin:"0 0 0.5rem 0",color:"#333",fontSize:"1.25rem"},children:je.name}),t.jsx("div",{style:{color:"#666",fontSize:"0.875rem",marginBottom:"0.5rem"},children:je.domain||"No domain"}),t.jsxs("div",{style:{color:"#666",fontSize:"0.875rem",display:"flex",gap:"0.5rem",alignItems:"center"},children:[t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:je.organization_type==="educational"?"#d4edda":je.organization_type==="government"?"#fff3cd":"#f8f9fa",color:je.organization_type==="educational"?"#155724":je.organization_type==="government"?"#856404":"#495057"},children:je.organization_type}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:je.is_active?"#d4edda":"#f8d7da",color:je.is_active?"#155724":"#721c24"},children:je.is_active?"Active":"Inactive"})]})]}),t.jsxs("div",{style:{display:"flex",flexDirection:"column",gap:"0.75rem"},children:[t.jsx("button",{onClick:()=>{Kt(),Se(je.id)},style:{padding:"0.75rem 1rem",backgroundColor:"#5D8AA8",color:"white",border:"none",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:G=>G.target.style.backgroundColor="#4A7088",onMouseLeave:G=>G.target.style.backgroundColor="#5D8AA8",children:"View Details"}),t.jsx("button",{onClick:()=>{Kt(),ue(je.id)},style:{padding:"0.75rem 1rem",backgroundColor:"#5D8AA8",color:"white",border:"none",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:G=>G.target.style.backgroundColor="#4A7088",onMouseLeave:G=>G.target.style.backgroundColor="#5D8AA8",children:"Edit Organisation"}),je.is_active?t.jsx("button",{onClick:()=>{Kt(),Fe(je.id,je.name)},style:{padding:"0.75rem 1rem",backgroundColor:"white",color:"#5D8AA8",border:"2px solid #5D8AA8",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:G=>{G.target.style.borderColor="#dc3545",G.target.style.color="#dc3545"},onMouseLeave:G=>{G.target.style.borderColor="#5D8AA8",G.target.style.color="#5D8AA8"},children:"Deactivate Organisation"}):t.jsx("button",{onClick:()=>{Kt(),it(je.id,je.name)},style:{padding:"0.75rem 1rem",backgroundColor:"white",color:"#5D8AA8",border:"2px solid #5D8AA8",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:G=>{G.target.style.borderColor="#28a745",G.target.style.color="#28a745"},onMouseLeave:G=>{G.target.style.borderColor="#5D8AA8",G.target.style.color="#5D8AA8"},children:"Reactivate Organisation"}),t.jsx("button",{onClick:()=>{Kt(),et(je.id,je.name)},style:{padding:"0.75rem 1rem",backgroundColor:"#5D8AA8",color:"white",border:"none",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:G=>G.target.style.backgroundColor="#4A7088",onMouseLeave:G=>G.target.style.backgroundColor="#5D8AA8",children:"Permanently Delete"})]}),t.jsx("div",{style:{marginTop:"1.5rem",paddingTop:"1rem",borderTop:"1px solid #e9ecef"},children:t.jsx("button",{onClick:Kt,style:{padding:"0.5rem 1rem",border:"1px solid #ddd",backgroundColor:"white",color:"#666",borderRadius:"6px",cursor:"pointer",width:"100%",fontSize:"0.875rem"},children:"Cancel"})})]})}),t.jsx(Lu,{isOpen:we,onClose:()=>Ze(!1),onConfirm:L==null?void 0:L.action,title:L==null?void 0:L.title,message:L==null?void 0:L.message,confirmText:L==null?void 0:L.confirmText,isDestructive:L==null?void 0:L.isDestructive,actionType:L==null?void 0:L.actionType})]}):null};function F_({active:n,initialTab:i=null}){var xt,ft,B,Ce;const[l,o]=w.useState({relationships:[],groups:[],metrics:{},organizations:[],trustLevels:[]}),[u,f]=w.useState(!0),[m,x]=w.useState(null),[p,h]=w.useState(null),[v,y]=w.useState(()=>i&&["relationships","groups","metrics"].includes(i)?i:new URLSearchParams(window.location.search).get("tab")||"relationships"),[N,S]=w.useState(!1),[A,z]=w.useState("add"),[U,oe]=w.useState("relationship"),[ie,me]=w.useState(null),[Ae,de]=w.useState(!1),[pe,W]=w.useState(!1),[Ke,he]=w.useState(!1),[De,xe]=w.useState(null),[je,ze]=w.useState(!1),[we,Ze]=w.useState(null),[L,ne]=w.useState(!1),[P,Ue]=w.useState(null),[T,F]=w.useState(!1),[le,ce]=w.useState(""),[fe,Oe]=w.useState(""),[ve,ke]=w.useState(1),[$e,re]=w.useState(10),[k,se]=w.useState({source_organization:"",target_organization:"",trust_level:"",relationship_type:"bilateral",notes:"",name:"",description:"",group_type:"industry",is_public:!1,requires_approval:!0}),ue=JSON.parse(localStorage.getItem("crisp_user")||"{}").role==="BlueVisionAdmin";w.useEffect(()=>{n&&Se()},[n]),w.useEffect(()=>{i&&["relationships","groups","metrics"].includes(i)&&y(i)},[i]);const Se=async()=>{var M,Q,$,ye,Ge,tt;try{f(!0),x(null),console.log("TrustManagement: Fetching trust data...");const[ae,Ot,_t,_e,We]=await Promise.all([k_().catch(ee=>(console.error("Failed to fetch trust relationships:",ee),{data:[]})),R_().catch(ee=>(console.error("Failed to fetch trust groups:",ee),{data:[]})),B_().catch(ee=>(console.error("Failed to fetch trust metrics:",ee),{data:{}})),Ou().catch(ee=>(console.error("Failed to fetch organizations:",ee),{data:{organizations:[]}})),H_().catch(ee=>(console.error("Failed to fetch trust levels:",ee),[]))]);console.log("TrustManagement: API responses:",{relationships:ae,groups:Ot,metrics:_t,organizations:_e,trustLevels:We}),console.log("🔍 RELATIONSHIPS RESPONSE ANALYSIS:"),console.log("📊 Response keys:",Object.keys(ae||{}));try{console.log("📋 Full JSON:",JSON.stringify(ae,null,2))}catch(ee){console.log("❌ JSON stringify failed:",ee.message),console.log("📋 Raw response:",ae)}console.log("🔍 Property checks:"),console.log("  - success:",ae==null?void 0:ae.success),console.log("  - trusts:",ae==null?void 0:ae.trusts),console.log("  - data:",ae==null?void 0:ae.data),console.log("  - results:",ae==null?void 0:ae.results),console.log("  - count:",ae==null?void 0:ae.count),console.log("  - next:",ae==null?void 0:ae.next),console.log("  - previous:",ae==null?void 0:ae.previous),console.log("🔍 TRUST LEVELS DETAILED:",{trustLevelsResponse:We,isArray:Array.isArray(We),length:Array.isArray(We)?We.length:"N/A",firstItem:Array.isArray(We)&&We.length>0?We[0]:"None",allItems:Array.isArray(We)?We:"Not an array"});let D=[];console.log("🔄 Attempting relationship extraction..."),Array.isArray(ae==null?void 0:ae.trusts)?(D=ae.trusts,console.log("✅ Extracted relationships from .trusts property:",D.length)):Array.isArray((M=ae==null?void 0:ae.results)==null?void 0:M.trusts)?(D=ae.results.trusts,console.log("✅ Extracted relationships from .results.trusts property:",D.length)):(Q=ae==null?void 0:ae.results)!=null&&Q.success&&Array.isArray(($=ae==null?void 0:ae.results)==null?void 0:$.trusts)?(D=ae.results.trusts,console.log("✅ Extracted relationships from paginated .results.trusts property:",D.length)):Array.isArray((ye=ae==null?void 0:ae.data)==null?void 0:ye.trusts)?(D=ae.data.trusts,console.log("✅ Extracted relationships from .data.trusts property:",D.length)):Array.isArray(ae==null?void 0:ae.data)?(D=ae.data,console.log("✅ Extracted relationships from .data property:",D.length)):Array.isArray(ae==null?void 0:ae.results)?(D=ae.results,console.log("✅ Extracted relationships from .results property:",D.length)):Array.isArray(ae)?(D=ae,console.log("✅ Using relationships response directly:",D.length)):(console.log("❌ Could not extract relationships array from response"),console.log("📋 Available properties:",Object.keys(ae||{})),console.log("📋 Type of response:",typeof ae)),o({relationships:D,groups:Array.isArray(Ot.data)?Ot.data:Array.isArray(Ot)?Ot:[],metrics:_t.data&&typeof _t.data=="object"?_t.data:_t&&typeof _t=="object"?_t:{},organizations:Array.isArray((Ge=_e.results)==null?void 0:Ge.organizations)?_e.results.organizations:Array.isArray((tt=_e.data)==null?void 0:tt.organizations)?_e.data.organizations:Array.isArray(_e.data)?_e.data:Array.isArray(_e)?_e:[],trustLevels:Array.isArray(We.trust_levels)?We.trust_levels:Array.isArray(We.data)?We.data:Array.isArray(We)?We:[]})}catch(ae){console.error("Error fetching trust data:",ae),x("Failed to load trust data")}finally{f(!1)}},Fe=M=>{if(!["relationships","groups","metrics"].includes(M)||M===v)return;y(M);const Q=new URLSearchParams(window.location.search);Q.set("tab",M);const $=`${window.location.pathname}?${Q.toString()}`;window.history.replaceState(null,"",$)},it=(M,Q,$=null)=>{var ye,Ge,tt;if(z(M),oe(Q),me($),M==="edit"&&$)if(Q==="relationship"){const ae=((ye=l.trustLevels.find(_e=>_e.name.toLowerCase().trim()===$.trust_level.toLowerCase().trim()||_e.name.toUpperCase().trim()===$.trust_level.toUpperCase().trim()||String(_e.id).toLowerCase().trim()===$.trust_level.toLowerCase().trim()||_e.name===$.trust_level||_e.id===$.trust_level||String(_e.id)===String($.trust_level)))==null?void 0:ye.id)||$.trust_level.toLowerCase()||"";console.log("🔍 TRUST LEVEL MAPPING:",{itemTrustLevel:$.trust_level,itemTrustLevelLower:$.trust_level.toLowerCase(),availableLevels:l.trustLevels.map(_e=>({id:_e.id,name:_e.name})),mappedId:ae,mapping:{exactMatch:l.trustLevels.find(_e=>_e.name===$.trust_level),lowerMatch:l.trustLevels.find(_e=>_e.name.toLowerCase()===$.trust_level.toLowerCase()),upperMatch:l.trustLevels.find(_e=>_e.name.toUpperCase()===$.trust_level.toUpperCase()),idMatch:l.trustLevels.find(_e=>_e.id===$.trust_level.toLowerCase())}}),console.log("🔧 EDIT MODE - Mapping organizations for relationship:",{relationshipItem:$,sourceOrg:$.source_organization,sourceOrgName:$.source_organization_name,targetOrg:$.target_organization,targetOrgName:$.target_organization_name,trustLevel:$.trust_level,availableOrgs:l.organizations.map(_e=>({id:_e.id,name:_e.name})),availableTrustLevels:l.trustLevels.map(_e=>({id:_e.id,name:_e.name}))});const Ot=((Ge=l.organizations.find(_e=>_e.name===$.source_organization||_e.name===$.source_organization_name||_e.id===$.source_organization))==null?void 0:Ge.id)||$.source_organization||"",_t=((tt=l.organizations.find(_e=>_e.name===$.target_organization||_e.name===$.target_organization_name||_e.id===$.target_organization))==null?void 0:tt.id)||$.target_organization||"";console.log("✅ MAPPED - Organization IDs:",{sourceOrgId:Ot,targetOrgId:_t,trustLevelId:ae,finalFormData:{source_organization:Ot,target_organization:_t,trust_level:ae,relationship_type:$.relationship_type||"bilateral",notes:$.notes||""}}),se({source_organization:Ot,target_organization:_t,trust_level:ae,relationship_type:$.relationship_type||"bilateral",notes:$.notes||""})}else Q==="group"&&se({name:$.name||"",description:$.description||"",group_type:$.group_type||"industry",is_public:$.is_public||!1,requires_approval:$.requires_approval||!0,trust_level:$.default_trust_level_id||""});else se({source_organization:"",target_organization:"",trust_level:"",relationship_type:"bilateral",notes:"",name:"",description:"",group_type:"industry",is_public:!1,requires_approval:!0});S(!0)},et=()=>{S(!1),me(null),de(!1),W(!1)},Gt=async M=>{var ye;M.preventDefault(),x(null);const Q=A==="add"?"create":"update",$=U==="relationship"?`relationship with ${((ye=l.organizations.find(Ge=>Ge.id===k.target_organization))==null?void 0:ye.name)||"selected organization"}`:k.name;Ze({title:`${A==="add"?"Create":"Update"} ${U==="relationship"?"Trust Relationship":"Trust Group"}`,message:`Are you sure you want to ${Q} ${U} "${$}"?`,confirmText:A==="add"?`Create ${U==="relationship"?"Relationship":"Group"}`:`Update ${U==="relationship"?"Relationship":"Group"}`,isDestructive:!1,actionType:"default",action:async()=>{var Ge,tt;try{if(W(!0),U==="relationship"){console.log("🚀 SUBMIT - Converting form data to API format:",{formData:k,availableTrustLevels:l.trustLevels,selectedTrustLevelId:k.trust_level});const ae=((Ge=l.organizations.find(at=>at.id===k.source_organization))==null?void 0:Ge.name)||k.source_organization,Ot=((tt=l.organizations.find(at=>at.id===k.target_organization))==null?void 0:tt.name)||k.target_organization,_t=l.trustLevels.find(at=>at.id===k.trust_level||at.id==k.trust_level||at.name===k.trust_level||at.name.toLowerCase()===k.trust_level.toLowerCase());let _e=(_t==null?void 0:_t.name)||null;const We=(_t==null?void 0:_t.id)||k.trust_level;if(!_e)throw console.error("❌ TRUST LEVEL ERROR: Could not find trust level name for ID:",k.trust_level),console.error("Available trust levels:",l.trustLevels),new Error(`Trust level not found for ID: ${k.trust_level}`);let D=_e.toLowerCase();console.log("🔄 CONVERTED - API data:",{sourceOrgName:ae,targetOrgName:Ot,originalTrustLevelName:_e,finalTrustLevelName:D,trustLevelId:We,originalTrustLevelId:k.trust_level,trustLevelObj:_t,currentItemTrustLevel:ie==null?void 0:ie.trust_level,backendExpectation:'Backend expects lowercase names like "high", "medium", "low"',conversionProcess:{input:k.trust_level,foundObject:_t,outputName:_e,finalOutputName:D,outputId:We,willMatch:["high","medium","low"].includes(D)}});const ee={source_organization:k.source_organization,target_organization:k.target_organization,trust_level:D,trust_level_id:We,relationship_type:k.relationship_type,notes:k.notes};console.log("📤 FINAL API PAYLOAD:",ee),A==="add"?(await E_(ee),h("Trust relationship created successfully")):(await pg(ie.id,ee),h("Trust relationship updated successfully"))}else if(U==="group"){const ae={...k};k.trust_level&&(ae.default_trust_level_id=k.trust_level,delete ae.trust_level),A==="add"?(await U_(ae),h("Trust group created successfully")):(await O_(ie.id,ae),h("Trust group updated successfully"))}setTimeout(()=>h(null),5e3),et(),Se()}catch(ae){console.error(`Error ${Q}ing ${U}:`,ae),x(`Failed to ${Q} ${U}: ${ae.message||ae}`)}finally{W(!1)}}}),ze(!0)},wt=M=>{xe(M),he(!0)},Tt=()=>{he(!1),xe(null)},It=M=>{var $,ye,Ge;const Q=De;if(Q)switch(M){case"view":Tt(),Ue(Q),ne(!0);break;case"edit":Tt(),it("edit",v==="relationships"?"relationship":"group",Q);break;case"activate":Ze({title:"Activate Relationship",message:`Are you sure you want to activate the relationship with ${(($=Q.target_organization)==null?void 0:$.name)||Q.target_organization_name||"the selected organization"}?`,confirmText:"Activate",isDestructive:!1,actionType:"default",action:async()=>{try{let ae="public";if(Q.trust_level){const Ot=Q.trust_level.match(/\(([^)]+)\)/);ae=Ot?Ot[1]:Q.trust_level.toLowerCase().split(" ")[0]}await M_(Q.id,"accept",ae,"Relationship activated"),h("Relationship activated successfully"),setTimeout(()=>h(null),5e3),Tt(),Se()}catch(ae){x("Failed to activate relationship: "+ae.message)}}}),ze(!0);break;case"suspend":Ze({title:"Suspend Relationship",message:`Are you sure you want to suspend the relationship with ${((ye=Q.target_organization)==null?void 0:ye.name)||Q.target_organization_name||"the selected organization"}?`,confirmText:"Suspend",isDestructive:!0,actionType:"destructive",action:async()=>{try{let ae="public";if(Q.trust_level){const Ot=Q.trust_level.match(/\(([^)]+)\)/);ae=Ot?Ot[1]:Q.trust_level.toLowerCase().split(" ")[0]}await pg(Q.id,{trust_level:ae,message:"Relationship suspended"}),h("Relationship suspended successfully"),setTimeout(()=>h(null),5e3),Tt(),Se()}catch(ae){x("Failed to suspend relationship: "+ae.message)}}}),ze(!0);break;case"delete":const tt=v==="relationships"?`relationship with ${((Ge=Q.target_organization)==null?void 0:Ge.name)||Q.target_organization_name||"the selected organization"}`:`group "${Q.name}"`;Ze({title:`Delete ${v==="relationships"?"Trust Relationship":"Trust Group"}`,message:`Are you sure you want to delete this ${tt}? This action cannot be undone.`,confirmText:"Delete",isDestructive:!0,actionType:"destructive",action:async()=>{try{v==="relationships"?(await D_(Q.id,"Relationship deleted by user"),h("Trust relationship deleted successfully")):(await L_(Q.id),h("Trust group deleted successfully")),setTimeout(()=>h(null),5e3),Tt(),Se()}catch(ae){x(`Failed to delete ${v==="relationships"?"relationship":"group"}: ${ae.message}`)}}}),ze(!0);break;case"join":Ze({title:"Join Trust Group",message:`Are you sure you want to join the group "${Q.name}"?`,confirmText:"Join Group",isDestructive:!1,actionType:"default",action:async()=>{try{await q_(Q.id),h("Successfully joined trust group!"),setTimeout(()=>h(null),5e3),Tt(),Se()}catch(ae){x("Failed to join trust group: "+ae.message)}}}),ze(!0);break}},G=(v==="relationships"?l.relationships:l.groups).filter($=>{var tt,ae;const ye=le===""||(v==="relationships"?(((tt=$.target_organization)==null?void 0:tt.name)||$.target_organization_name||((ae=$.source_organization)==null?void 0:ae.name)||$.source_organization_name||"").toLowerCase().includes(le.toLowerCase()):($.name||"").toLowerCase().includes(le.toLowerCase())),Ge=fe===""||(v==="relationships"?$.status===fe:fe==="public"?$.is_public:!$.is_public);return ye&&Ge}),Te=G.length,Be=(ve-1)*$e,Ne=G.slice(Be,Be+$e),Re=M=>{ke(M)};return n?u?t.jsx("div",{className:"trust-management",children:t.jsx(_s,{})}):t.jsxs("div",{style:{padding:"2rem",fontFamily:"Arial, sans-serif",position:"relative"},children:[(u||pe)&&t.jsx(_s,{fullscreen:!0}),t.jsxs("div",{style:{marginBottom:"2rem"},children:[t.jsx("h1",{style:{marginBottom:"0.5rem",color:"#333"},children:"Trust Management"}),!ue&&t.jsxs("div",{style:{padding:"0.75rem 1rem",backgroundColor:"#fff3cd",color:"#856404",borderRadius:"6px",border:"1px solid #ffeaa7",fontSize:"0.875rem",fontWeight:"500"},children:[t.jsx("strong",{children:"Publisher Mode:"})," You can manage trust relationships and groups for your organization and organizations with trusted relationships."]})]}),m&&t.jsxs("div",{style:{backgroundColor:"#f8d7da",color:"#721c24",border:"1px solid #f5c6cb",borderRadius:"4px",padding:"0.75rem 1rem",marginBottom:"1rem",display:"flex",justifyContent:"space-between",alignItems:"center"},children:[t.jsx("span",{children:m}),t.jsx("button",{onClick:()=>x(null),style:{background:"none",border:"none",color:"#721c24",fontSize:"1.25rem",cursor:"pointer",padding:"0",lineHeight:"1"},children:"×"})]}),p&&t.jsxs("div",{style:{backgroundColor:"#d4edda",color:"#155724",border:"1px solid #c3e6cb",borderRadius:"4px",padding:"0.75rem 1rem",marginBottom:"1rem",display:"flex",justifyContent:"space-between",alignItems:"center"},children:[t.jsx("span",{children:p}),t.jsx("button",{onClick:()=>h(null),style:{background:"none",border:"none",color:"#155724",fontSize:"1.25rem",cursor:"pointer",padding:"0",lineHeight:"1"},children:"×"})]}),t.jsx("div",{style:{marginBottom:"1.5rem"},children:t.jsx("div",{style:{borderBottom:"1px solid #dee2e6"},children:["relationships","groups","metrics"].map(M=>t.jsxs("button",{onClick:()=>Fe(M),style:{padding:"0.75rem 1.5rem",border:"none",backgroundColor:v===M?"#007bff":"transparent",color:v===M?"white":"#495057",borderRadius:"4px 4px 0 0",marginRight:"0.25rem",cursor:"pointer",textTransform:"capitalize",fontWeight:v===M?"600":"400"},children:[M," (",M==="relationships"?l.relationships.length:M==="groups"?l.groups.length:"N/A",")"]},M))})}),v!=="metrics"&&t.jsxs(t.Fragment,{children:[t.jsxs("div",{style:{display:"flex",gap:"1rem",marginBottom:"2rem",flexWrap:"wrap",alignItems:"center"},children:[t.jsxs("div",{style:{display:"flex",gap:"1rem",alignItems:"center",flex:1},children:[t.jsx("input",{type:"text",placeholder:`Search ${v}...`,value:le,onChange:M=>ce(M.target.value),style:{padding:"0.5rem",border:"1px solid #ced4da",borderRadius:"4px",minWidth:"200px"}}),t.jsxs("select",{value:fe,onChange:M=>Oe(M.target.value),style:{padding:"0.5rem",border:"1px solid #ced4da",borderRadius:"4px",minWidth:"120px"},children:[t.jsx("option",{value:"",children:"All Status"}),v==="relationships"?t.jsxs(t.Fragment,{children:[t.jsx("option",{value:"active",children:"Active"}),t.jsx("option",{value:"pending",children:"Pending"}),t.jsx("option",{value:"suspended",children:"Suspended"})]}):t.jsxs(t.Fragment,{children:[t.jsx("option",{value:"public",children:"Public"}),t.jsx("option",{value:"private",children:"Private"})]})]})]}),t.jsxs("button",{onClick:()=>it("add",v==="relationships"?"relationship":"group"),disabled:!ue&&v==="groups",style:{padding:"0.5rem 1rem",backgroundColor:!ue&&v==="groups"?"#6c757d":"#007bff",color:"white",border:"none",borderRadius:"4px",cursor:!ue&&v==="groups"?"not-allowed":"pointer",fontWeight:"500"},title:!ue&&v==="groups"?"Only administrators can create trust groups":"",children:["Add ",v==="relationships"?"Relationship":"Group"]})]}),t.jsx("div",{style:{backgroundColor:"white",borderRadius:"8px",boxShadow:"0 4px 6px rgba(0,0,0,0.1)",border:"1px solid #e9ecef"},children:Ne.length===0?t.jsxs("div",{style:{textAlign:"center",padding:"3rem",color:"#6c757d"},children:[t.jsxs("h4",{style:{marginBottom:"0.5rem"},children:["No ",v," found"]}),t.jsx("p",{style:{margin:"0"},children:G.length===0&&(le||fe)?"No items match your search criteria.":`No ${v} available. Click "Add ${v==="relationships"?"Relationship":"Group"}" to create the first one.`})]}):Ne.map(M=>{var Q,$;return t.jsxs("div",{onClick:ye=>{ye.preventDefault(),ye.stopPropagation(),wt(M)},style:{display:"flex",alignItems:"center",padding:"1.25rem",borderBottom:"1px solid #e9ecef",transition:"all 0.2s ease",cursor:"pointer",backgroundColor:"transparent"},onMouseEnter:ye=>{ye.currentTarget.style.backgroundColor="#f8f9fa",ye.currentTarget.style.transform="translateX(4px)"},onMouseLeave:ye=>{ye.currentTarget.style.backgroundColor="transparent",ye.currentTarget.style.transform="translateX(0px)"},children:[t.jsx("div",{style:{flex:"1",minWidth:"0"},children:v==="relationships"?t.jsxs(t.Fragment,{children:[t.jsxs("div",{style:{display:"flex",alignItems:"center",gap:"1rem",flexWrap:"wrap"},children:[t.jsxs("div",{style:{fontWeight:"600",color:"#212529",fontSize:"1.1rem"},children:[((Q=M.source_organization)==null?void 0:Q.name)||M.source_organization_name||"Unknown"," → ",(($=M.target_organization)==null?void 0:$.name)||M.target_organization_name||"Unknown"]}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:M.trust_level==="HIGH"?"#d4edda":M.trust_level==="MEDIUM"?"#fff3cd":"#f8f9fa",color:M.trust_level==="HIGH"?"#155724":M.trust_level==="MEDIUM"?"#856404":"#495057"},children:M.trust_level}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:M.status==="active"?"#d4edda":M.status==="pending"?"#fff3cd":"#f8d7da",color:M.status==="active"?"#155724":M.status==="pending"?"#856404":"#721c24"},children:M.status||"Unknown"})]}),t.jsxs("div",{style:{marginTop:"0.5rem",color:"#6c757d",fontSize:"0.875rem",display:"flex",gap:"1rem",flexWrap:"wrap"},children:[t.jsxs("span",{children:["Type: ",M.relationship_type]}),M.notes&&t.jsxs("span",{children:["Notes: ",M.notes]})]})]}):t.jsxs(t.Fragment,{children:[t.jsxs("div",{style:{display:"flex",alignItems:"center",gap:"1rem",flexWrap:"wrap"},children:[t.jsx("div",{style:{fontWeight:"600",color:"#212529",fontSize:"1.1rem"},children:M.name}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:M.group_type==="SECURITY"?"#d4edda":M.group_type==="BUSINESS"?"#fff3cd":"#f8f9fa",color:M.group_type==="SECURITY"?"#155724":M.group_type==="BUSINESS"?"#856404":"#495057"},children:M.group_type}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:M.is_public?"#d4edda":"#fff3cd",color:M.is_public?"#155724":"#856404"},children:M.is_public?"Public":"Private"})]}),t.jsxs("div",{style:{marginTop:"0.5rem",color:"#6c757d",fontSize:"0.875rem",display:"flex",gap:"1rem",flexWrap:"wrap"},children:[t.jsx("span",{children:M.description}),t.jsxs("span",{children:["Members: ",M.member_count||0]})]})]})}),t.jsx("div",{style:{fontSize:"1.2rem",color:"#6c757d",marginLeft:"1rem",transition:"transform 0.2s ease"},children:"→"})]},M.id)})}),Te>$e&&t.jsx("div",{style:{marginTop:"1rem"},children:t.jsx(qu,{currentPage:ve,totalItems:Te,itemsPerPage:$e,onPageChange:Re,showInfo:!0,showJumpToPage:!0})})]}),v==="metrics"&&t.jsx("div",{style:{display:"grid",gridTemplateColumns:"repeat(auto-fit, minmax(250px, 1fr))",gap:"1rem"},children:[{title:"Total Relationships",value:l.relationships.length,description:ue?"All system relationships":"Your organization relationships"},{title:"Active Groups",value:l.groups.length,description:ue?"All system groups":"Your accessible groups"},{title:"Trust Score",value:l.metrics.trust_score||"N/A",description:ue?"System average":"Organization trust score"},{title:"Connected Organizations",value:l.metrics.connected_orgs||0,description:ue?"Total connected orgs":"Organizations you trust"}].map((M,Q)=>t.jsxs("div",{style:{backgroundColor:"white",border:"1px solid #dee2e6",borderRadius:"8px",padding:"1.5rem",textAlign:"center"},children:[t.jsx("h4",{style:{margin:"0 0 0.5rem 0",color:"#495057",fontSize:"1rem"},children:M.title}),t.jsx("div",{style:{fontSize:"2rem",fontWeight:"bold",color:"#007bff",margin:"0.5rem 0"},children:M.value}),t.jsx("div",{style:{fontSize:"0.75rem",color:"#6c757d",fontStyle:"italic"},children:M.description})]},Q))}),N&&t.jsx("div",{style:{position:"fixed",top:0,left:0,width:"100%",height:"100%",backgroundColor:"rgba(0, 0, 0, 0.5)",display:"flex",alignItems:"center",justifyContent:"center",zIndex:1e3},children:t.jsxs("div",{style:{backgroundColor:"white",borderRadius:"8px",padding:"1.5rem",width:"90%",maxWidth:"500px",maxHeight:"90vh",overflowY:"auto"},children:[t.jsxs("h3",{style:{margin:"0 0 1rem 0"},children:[A==="add"?"Create":"Edit"," ",U==="relationship"?"Trust Relationship":"Trust Group"]}),t.jsxs("form",{onSubmit:Gt,children:[U==="relationship"?t.jsxs(t.Fragment,{children:[ue&&t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Source Organization *"}),t.jsxs("select",{value:k.source_organization||"",onChange:M=>se({...k,source_organization:M.target.value}),required:ue,style:{width:"100%",padding:"0.5rem",border:"1px solid #ced4da",borderRadius:"4px"},children:[t.jsx("option",{value:"",children:"Select Source Organization"}),l.organizations.map(M=>t.jsx("option",{value:M.id,children:M.name},M.id))]})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Target Organization *"}),t.jsxs("select",{value:k.target_organization,onChange:M=>se({...k,target_organization:M.target.value}),required:!0,style:{width:"100%",padding:"0.5rem",border:"1px solid #ced4da",borderRadius:"4px"},children:[t.jsx("option",{value:"",children:"Select Organization"}),l.organizations.map(M=>t.jsx("option",{value:M.id,children:M.name},M.id))]})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Trust Level *"}),t.jsxs("select",{value:k.trust_level,onChange:M=>se({...k,trust_level:M.target.value}),required:!0,style:{width:"100%",padding:"0.5rem",border:"1px solid #ced4da",borderRadius:"4px"},children:[t.jsx("option",{value:"",children:"Select Trust Level"}),l.trustLevels.map(M=>t.jsx("option",{value:M.id,children:M.name},M.id))]})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Relationship Type"}),t.jsxs("select",{value:k.relationship_type,onChange:M=>se({...k,relationship_type:M.target.value}),style:{width:"100%",padding:"0.5rem",border:"1px solid #ced4da",borderRadius:"4px"},children:[t.jsx("option",{value:"bilateral",children:"Bilateral"}),t.jsx("option",{value:"unilateral",children:"Unilateral"})]})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Notes"}),t.jsx("textarea",{value:k.notes,onChange:M=>se({...k,notes:M.target.value}),rows:3,placeholder:"Optional notes about this relationship...",style:{width:"100%",padding:"0.5rem",border:"1px solid #ced4da",borderRadius:"4px",resize:"vertical"}})]})]}):t.jsxs(t.Fragment,{children:[t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Group Name *"}),t.jsx("input",{type:"text",value:k.name,onChange:M=>se({...k,name:M.target.value}),required:!0,placeholder:"Enter group name...",style:{width:"100%",padding:"0.5rem",border:"1px solid #ced4da",borderRadius:"4px"}})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Description"}),t.jsx("textarea",{value:k.description,onChange:M=>se({...k,description:M.target.value}),rows:3,placeholder:"Describe the purpose of this group...",style:{width:"100%",padding:"0.5rem",border:"1px solid #ced4da",borderRadius:"4px",resize:"vertical"}})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Group Type"}),t.jsxs("select",{value:k.group_type,onChange:M=>se({...k,group_type:M.target.value}),style:{width:"100%",padding:"0.5rem",border:"1px solid #ced4da",borderRadius:"4px"},children:[t.jsx("option",{value:"industry",children:"Industry"}),t.jsx("option",{value:"regional",children:"Regional"}),t.jsx("option",{value:"security",children:"Security"}),t.jsx("option",{value:"research",children:"Research"})]})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{style:{display:"block",marginBottom:"0.5rem",fontWeight:"500"},children:"Trust Level"}),t.jsxs("select",{value:k.trust_level,onChange:M=>se({...k,trust_level:M.target.value}),style:{width:"100%",padding:"0.5rem",border:"1px solid #ced4da",borderRadius:"4px"},children:[t.jsx("option",{value:"",children:"Select Trust Level"}),l.trustLevels.map(M=>t.jsx("option",{value:M.id,children:M.name},M.id))]})]}),t.jsxs("div",{style:{marginBottom:"1rem",display:"flex",gap:"1rem"},children:[t.jsxs("label",{style:{display:"flex",alignItems:"center",gap:"0.5rem"},children:[t.jsx("input",{type:"checkbox",checked:k.is_public,onChange:M=>se({...k,is_public:M.target.checked})}),"Public Group"]}),t.jsxs("label",{style:{display:"flex",alignItems:"center",gap:"0.5rem"},children:[t.jsx("input",{type:"checkbox",checked:k.requires_approval,onChange:M=>se({...k,requires_approval:M.target.checked})}),"Requires Approval"]})]})]}),t.jsxs("div",{style:{display:"flex",gap:"0.5rem",justifyContent:"flex-end",marginTop:"1.5rem"},children:[t.jsx("button",{type:"button",onClick:et,disabled:pe,style:{padding:"0.5rem 1rem",backgroundColor:"#6c757d",color:"white",border:"none",borderRadius:"4px",cursor:pe?"not-allowed":"pointer"},children:"Cancel"}),t.jsx("button",{type:"submit",disabled:pe,style:{padding:"0.5rem 1rem",backgroundColor:"#007bff",color:"white",border:"none",borderRadius:"4px",cursor:pe?"not-allowed":"pointer"},children:pe?"Saving...":A==="add"?"Create":"Update"})]})]})]})}),Ke&&De&&t.jsx("div",{style:{position:"fixed",top:0,left:0,width:"100%",height:"100%",backgroundColor:"rgba(0, 0, 0, 0.5)",display:"flex",alignItems:"center",justifyContent:"center",zIndex:1001},children:t.jsxs("div",{style:{backgroundColor:"white",padding:"2rem",borderRadius:"12px",minWidth:"300px",maxWidth:"400px",boxShadow:"0 10px 25px rgba(0,0,0,0.1)"},children:[t.jsxs("div",{style:{marginBottom:"1.5rem"},children:[t.jsx("h3",{style:{margin:"0 0 0.5rem 0",color:"#333",fontSize:"1.25rem",wordBreak:"break-word",lineHeight:"1.3"},children:v==="relationships"?`${((xt=De.source_organization)==null?void 0:xt.name)||De.source_organization_name||"Unknown"} → ${((ft=De.target_organization)==null?void 0:ft.name)||De.target_organization_name||"Unknown"}`:De.name}),t.jsx("div",{style:{color:"#666",fontSize:"0.875rem",marginBottom:"0.5rem"},children:v==="relationships"?`Trust Level: ${De.trust_level}`:De.description}),t.jsx("div",{style:{color:"#666",fontSize:"0.875rem",display:"flex",gap:"0.5rem",alignItems:"center"},children:v==="relationships"?t.jsxs(t.Fragment,{children:[t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:De.relationship_type==="BILATERAL"?"#d4edda":"#fff3cd",color:De.relationship_type==="BILATERAL"?"#155724":"#856404"},children:De.relationship_type}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:De.status==="active"?"#d4edda":De.status==="pending"?"#fff3cd":"#f8d7da",color:De.status==="active"?"#155724":De.status==="pending"?"#856404":"#721c24"},children:De.status})]}):t.jsxs(t.Fragment,{children:[t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:De.group_type==="SECURITY"?"#d4edda":"#fff3cd",color:De.group_type==="SECURITY"?"#155724":"#856404"},children:De.group_type}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.75rem",fontWeight:"600",textTransform:"uppercase",backgroundColor:De.is_public?"#d4edda":"#fff3cd",color:De.is_public?"#155724":"#856404"},children:De.is_public?"Public":"Private"})]})})]}),t.jsxs("div",{style:{display:"flex",flexDirection:"column",gap:"0.75rem"},children:[t.jsx("button",{onClick:()=>{Tt(),It("view")},style:{padding:"0.75rem 1rem",backgroundColor:"#5D8AA8",color:"white",border:"none",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:M=>M.target.style.backgroundColor="#4A7088",onMouseLeave:M=>M.target.style.backgroundColor="#5D8AA8",children:"View Details"}),t.jsx("button",{onClick:()=>{Tt(),It("edit")},style:{padding:"0.75rem 1rem",backgroundColor:"#5D8AA8",color:"white",border:"none",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:M=>M.target.style.backgroundColor="#4A7088",onMouseLeave:M=>M.target.style.backgroundColor="#5D8AA8",children:"Edit Details"}),v==="relationships"&&De.status!=="active"&&t.jsx("button",{onClick:()=>{Tt(),It("activate")},style:{padding:"0.75rem 1rem",backgroundColor:"#5D8AA8",color:"white",border:"none",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:M=>M.target.style.backgroundColor="#4A7088",onMouseLeave:M=>M.target.style.backgroundColor="#5D8AA8",children:"Activate Relationship"}),v==="relationships"&&De.status==="active"&&t.jsx("button",{onClick:()=>{Tt(),It("suspend")},style:{padding:"0.75rem 1rem",backgroundColor:"white",color:"#5D8AA8",border:"2px solid #5D8AA8",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:M=>{M.target.style.backgroundColor="#5D8AA8",M.target.style.color="white"},onMouseLeave:M=>{M.target.style.backgroundColor="white",M.target.style.color="#5D8AA8"},children:"Suspend Relationship"}),v==="groups"&&!ue&&t.jsx("button",{onClick:()=>{Tt(),It("join")},style:{padding:"0.75rem 1rem",backgroundColor:"#5D8AA8",color:"white",border:"none",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:M=>M.target.style.backgroundColor="#4A7088",onMouseLeave:M=>M.target.style.backgroundColor="#5D8AA8",children:"Join Group"}),t.jsxs("button",{onClick:()=>{Tt(),It("delete")},style:{padding:"0.75rem 1rem",backgroundColor:"#5D8AA8",color:"white",border:"none",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",fontWeight:"500",transition:"all 0.2s ease",textAlign:"left"},onMouseEnter:M=>M.target.style.backgroundColor="#4A7088",onMouseLeave:M=>M.target.style.backgroundColor="#5D8AA8",children:["Delete ",v==="relationships"?"Relationship":"Group"]})]}),t.jsx("div",{style:{marginTop:"1.5rem",paddingTop:"1rem",borderTop:"1px solid #e9ecef"},children:t.jsx("button",{onClick:Tt,style:{padding:"0.5rem 1rem",border:"1px solid #ddd",backgroundColor:"white",color:"#666",borderRadius:"6px",cursor:"pointer",fontSize:"0.875rem",width:"100%"},children:"Cancel"})})]})}),je&&t.jsx(Lu,{isOpen:je,onClose:()=>ze(!1),onConfirm:we==null?void 0:we.action,title:we==null?void 0:we.title,message:we==null?void 0:we.message,confirmText:we==null?void 0:we.confirmText,isDestructive:we==null?void 0:we.isDestructive,actionType:we==null?void 0:we.actionType}),L&&P&&t.jsx("div",{style:{position:"fixed",top:0,left:0,width:"100%",height:"100%",backgroundColor:"rgba(0, 0, 0, 0.5)",display:"flex",alignItems:"center",justifyContent:"center",zIndex:1e3},children:t.jsxs("div",{style:{backgroundColor:"white",borderRadius:"12px",padding:"2rem",width:"90%",maxWidth:"600px",maxHeight:"90vh",overflowY:"auto",boxShadow:"0 10px 25px rgba(0,0,0,0.1)"},children:[t.jsxs("div",{style:{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:"1.5rem"},children:[t.jsx("h2",{style:{margin:"0",color:"#333"},children:v==="relationships"?"Trust Relationship Details":"Trust Group Details"}),t.jsx("button",{onClick:()=>ne(!1),style:{background:"none",border:"none",fontSize:"1.5rem",cursor:"pointer",color:"#666"},children:"×"})]}),v==="relationships"?t.jsx("div",{children:t.jsxs("div",{style:{marginBottom:"1.5rem"},children:[t.jsx("h3",{style:{color:"#5D8AA8",marginBottom:"1rem"},children:"Relationship Overview"}),t.jsxs("div",{style:{display:"grid",gridTemplateColumns:"1fr 1fr",gap:"1rem",marginBottom:"1rem"},children:[t.jsxs("div",{children:[t.jsx("strong",{children:"Source Organization:"}),t.jsx("br",{}),((B=P.source_organization)==null?void 0:B.name)||P.source_organization_name||"Unknown"]}),t.jsxs("div",{children:[t.jsx("strong",{children:"Target Organization:"}),t.jsx("br",{}),((Ce=P.target_organization)==null?void 0:Ce.name)||P.target_organization_name||"Unknown"]}),t.jsxs("div",{children:[t.jsx("strong",{children:"Trust Level:"}),t.jsx("br",{}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.875rem",fontWeight:"600",backgroundColor:P.trust_level==="HIGH"?"#d4edda":P.trust_level==="MEDIUM"?"#fff3cd":"#f8f9fa",color:P.trust_level==="HIGH"?"#155724":P.trust_level==="MEDIUM"?"#856404":"#495057"},children:P.trust_level})]}),t.jsxs("div",{children:[t.jsx("strong",{children:"Status:"}),t.jsx("br",{}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.875rem",fontWeight:"600",backgroundColor:P.status==="active"?"#d4edda":P.status==="pending"?"#fff3cd":"#f8d7da",color:P.status==="active"?"#155724":P.status==="pending"?"#856404":"#721c24"},children:P.status})]}),t.jsxs("div",{children:[t.jsx("strong",{children:"Relationship Type:"}),t.jsx("br",{}),P.relationship_type]}),t.jsxs("div",{children:[t.jsx("strong",{children:"Created:"}),t.jsx("br",{}),P.created_at?new Date(P.created_at).toLocaleDateString():"N/A"]})]}),P.notes&&t.jsxs("div",{style:{marginTop:"1rem"},children:[t.jsx("strong",{children:"Notes:"}),t.jsx("br",{}),t.jsx("div",{style:{padding:"0.75rem",backgroundColor:"#f8f9fa",borderRadius:"4px",marginTop:"0.5rem",fontStyle:"italic"},children:P.notes})]})]})}):t.jsx("div",{children:t.jsxs("div",{style:{marginBottom:"1.5rem"},children:[t.jsx("h3",{style:{color:"#5D8AA8",marginBottom:"1rem"},children:"Group Overview"}),t.jsxs("div",{style:{display:"grid",gridTemplateColumns:"1fr 1fr",gap:"1rem",marginBottom:"1rem"},children:[t.jsxs("div",{children:[t.jsx("strong",{children:"Group Name:"}),t.jsx("br",{}),P.name]}),t.jsxs("div",{children:[t.jsx("strong",{children:"Group Type:"}),t.jsx("br",{}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.875rem",fontWeight:"600",backgroundColor:P.group_type==="SECURITY"?"#d4edda":"#fff3cd",color:P.group_type==="SECURITY"?"#155724":"#856404"},children:P.group_type})]}),t.jsxs("div",{children:[t.jsx("strong",{children:"Visibility:"}),t.jsx("br",{}),t.jsx("span",{style:{padding:"0.25rem 0.5rem",borderRadius:"4px",fontSize:"0.875rem",fontWeight:"600",backgroundColor:P.is_public?"#d4edda":"#fff3cd",color:P.is_public?"#155724":"#856404"},children:P.is_public?"Public":"Private"})]}),t.jsxs("div",{children:[t.jsx("strong",{children:"Member Count:"}),t.jsx("br",{}),P.member_count||0]}),t.jsxs("div",{children:[t.jsx("strong",{children:"Requires Approval:"}),t.jsx("br",{}),P.requires_approval?"Yes":"No"]}),t.jsxs("div",{children:[t.jsx("strong",{children:"Created:"}),t.jsx("br",{}),P.created_at?new Date(P.created_at).toLocaleDateString():"N/A"]})]}),t.jsxs("div",{style:{marginTop:"1rem"},children:[t.jsx("strong",{children:"Description:"}),t.jsx("br",{}),t.jsx("div",{style:{padding:"0.75rem",backgroundColor:"#f8f9fa",borderRadius:"4px",marginTop:"0.5rem"},children:P.description||"No description provided"})]})]})}),t.jsx("div",{style:{display:"flex",justifyContent:"flex-end",marginTop:"2rem",paddingTop:"1rem",borderTop:"1px solid #e9ecef"},children:t.jsx("button",{onClick:()=>ne(!1),style:{padding:"0.5rem 1rem",backgroundColor:"#6c757d",color:"white",border:"none",borderRadius:"6px",cursor:"pointer"},children:"Close"})})]})})]}):null}class Y_ extends Ui.Component{constructor(i){super(i),this.state={hasError:!1,error:null}}static getDerivedStateFromError(i){return{hasError:!0,error:i}}componentDidCatch(i,l){console.error("Chart Error:",i,l)}render(){return this.state.hasError?t.jsxs("div",{style:{padding:"20px",textAlign:"center",background:"#fff5f5",border:"1px solid #fed7d7",borderRadius:"4px",color:"#c53030"},children:[t.jsx("i",{className:"fas fa-exclamation-triangle",style:{fontSize:"24px",marginBottom:"10px"}}),t.jsx("h3",{children:"Chart Error"}),t.jsx("p",{children:"Something went wrong with the chart visualization."}),t.jsx("button",{onClick:()=>this.setState({hasError:!1,error:null}),style:{background:"#0056b3",color:"white",border:"none",padding:"8px 16px",borderRadius:"4px",cursor:"pointer"},children:"Try Again"})]}):this.props.children}}const Di="http://localhost:8000",uo=()=>{const n=localStorage.getItem("crisp_auth_token"),i={"Content-Type":"application/json"};return n?i.Authorization=`Bearer ${n}`:console.warn("No authentication token found in localStorage"),i},dt={get:async n=>{try{const i=uo();if(!localStorage.getItem("crisp_auth_token")&&!n.includes("/auth/"))return console.warn(`Skipping API call to ${n} - no authentication token`),null;const o=await fetch(`${Di}${n}`,{headers:i});if(!o.ok)throw o.status===401&&console.warn(`Authentication failed for ${n} - token may be expired`),new Error(`HTTP ${o.status}`);return await o.json()}catch(i){return console.error(`API Error: ${n}`,i),null}},post:async(n,i)=>{try{const l=await fetch(`${Di}${n}`,{method:"POST",headers:uo(),body:JSON.stringify(i)});if(!l.ok)throw new Error(`HTTP ${l.status}`);return await l.json()}catch(l){return console.error(`API Error: ${n}`,l),null}},put:async(n,i)=>{try{const l=await fetch(`${Di}${n}`,{method:"PUT",headers:uo(),body:JSON.stringify(i)});if(!l.ok)throw new Error(`HTTP ${l.status}`);return await l.json()}catch(l){return console.error(`API Error: ${n}`,l),null}},delete:async n=>{try{const i=await fetch(`${Di}${n}`,{method:"DELETE",headers:uo()});if(!i.ok)throw new Error(`HTTP ${i.status}`);if(i.status===204)return{success:!0};const l=await i.text();return l?JSON.parse(l):{success:!0}}catch(i){return console.error(`API Error: ${n}`,i),null}}};function G_({user:n,onLogout:i,isAdmin:l}){const[o,u]=w.useState("dashboard"),[f,m]=w.useState(!1),[x,p]=w.useState(!0);w.useEffect(()=>{const S=async z=>{try{return(await fetch(`${Di}/api/auth/profile/`,{headers:{Authorization:`Bearer ${z}`}})).ok}catch(U){return console.error("Token validation error:",U),!1}};(async()=>{p(!0);const z=localStorage.getItem("crisp_auth_token");if(z)if(console.log("Validating existing token..."),await S(z)){console.log("Existing token is valid"),m(!0),p(!1);return}else console.log("Existing token is invalid, clearing and re-authenticating..."),localStorage.removeItem("crisp_auth_token"),localStorage.removeItem("crisp_refresh_token"),localStorage.removeItem("crisp_user");try{console.log("Attempting auto-login as admin...");const U=await fetch(`${Di}/api/auth/login/`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({username:"admin",password:"admin123"})});if(console.log("Login response status:",U.status),U.ok){const oe=await U.json();console.log("Login response data:",oe),oe.access?(localStorage.setItem("crisp_auth_token",oe.access),oe.refresh&&localStorage.setItem("crisp_refresh_token",oe.refresh),oe.user&&localStorage.setItem("crisp_user",JSON.stringify(oe.user)),console.log("Auto-login successful, token stored"),m(!0)):(console.error("No access token in response"),m(!1))}else{const oe=await U.text();console.error("Auto-login failed with status:",U.status,U.statusText),console.error("Error response:",oe),m(!1)}}catch(U){console.error("Auto-login error:",U),console.error("This might indicate the backend server is not running"),m(!1)}p(!1)})()},[]);const[h,v]=w.useState({triggerModal:null,modalParams:{}}),y=(S,A=null,z={})=>{if(u(S),v({triggerModal:A,modalParams:z}),A){const U=new URL(window.location);U.searchParams.set("modal",A),Object.keys(z).length>0&&U.searchParams.set("params",JSON.stringify(z)),window.history.pushState({},"",U)}else{const U=new URL(window.location);U.searchParams.delete("modal"),U.searchParams.delete("params"),window.history.pushState({},"",U)}},N=()=>{y("user-management","addUser")};return w.useEffect(()=>{const S=()=>{const A=new URLSearchParams(window.location.search),z=A.get("modal"),U=A.get("params");v(z?{triggerModal:z,modalParams:U?JSON.parse(U):{}}:{triggerModal:null,modalParams:{}})};return window.addEventListener("popstate",S),S(),()=>window.removeEventListener("popstate",S)},[]),x?t.jsx("div",{className:"App",children:t.jsxs("div",{className:"loading-screen",children:[t.jsx("div",{className:"loading-spinner"}),t.jsx("h2",{children:"Loading CRISP System..."}),t.jsx("p",{children:"Authenticating..."})]})}):f?t.jsxs("div",{className:"App",children:[t.jsx(P_,{showPage:y,user:n,onLogout:i,isAdmin:l,navigateToRegisterUser:N}),t.jsx(V_,{activePage:o,showPage:y,user:n,onLogout:i,isAdmin:l}),t.jsx("main",{className:"main-content",children:t.jsxs("div",{className:"container",children:[t.jsx(X_,{active:o==="dashboard",showPage:y,isAuthenticated:f,isAuthenticating:x}),t.jsx(Z_,{active:o==="threat-feeds",navigationState:h,setNavigationState:v}),t.jsx(Q_,{active:o==="ioc-management"}),t.jsx(J_,{active:o==="ttp-analysis"}),t.jsx(K_,{active:o==="institutions"}),t.jsx(W_,{active:o==="reports"}),t.jsx(tS,{active:o==="notifications"}),t.jsx(m_,{active:o==="profile"}),t.jsx(I_,{active:o==="user-management"}),t.jsx($_,{active:o==="organisation-management"}),t.jsx(F_,{active:o==="trust-management"})]})})]}):t.jsx("div",{className:"App",children:t.jsx("div",{className:"login-screen",children:t.jsxs("div",{className:"login-container",children:[t.jsx("h2",{children:"CRISP System Login"}),t.jsx("p",{children:"Please login to continue"}),t.jsxs("button",{className:"btn btn-primary",onClick:()=>{p(!0),m(!1),localStorage.removeItem("crisp_auth_token"),localStorage.removeItem("crisp_refresh_token"),localStorage.removeItem("crisp_user"),window.location.reload()},children:[t.jsx("i",{className:"fas fa-sign-in-alt"})," Login as Admin"]})]})})})}function P_({showPage:n,user:i,onLogout:l,isAdmin:o,navigateToRegisterUser:u}){const[f,m]=w.useState(!1),[x,p]=w.useState(!1),h=i&&i.username?i.username.charAt(0).toUpperCase():"A",v=i&&i.username?i.username.split("@")[0]:"Admin",y=(i==null?void 0:i.role)||"Security Analyst",N=S=>{S.preventDefault(),S.stopPropagation(),m(!f)};return w.useEffect(()=>{const S=A=>{A.target.closest(".user-profile-container")||(m(!1),p(!1))};return document.addEventListener("mousedown",S),()=>document.removeEventListener("mousedown",S)},[]),w.useEffect(()=>{f||p(!1)},[f]),t.jsx("header",{children:t.jsxs("div",{className:"container header-container",children:[t.jsxs("a",{href:"#",className:"logo",children:[t.jsx("div",{className:"logo-icon",children:t.jsx("i",{className:"fas fa-shield-alt"})}),t.jsx("div",{className:"logo-text",children:"CRISP"})]}),t.jsxs("div",{className:"nav-actions",children:[t.jsxs("div",{className:"search-bar",children:[t.jsx("span",{className:"search-icon",children:t.jsx("i",{className:"fas fa-search"})}),t.jsx("input",{type:"text",placeholder:"Search platform..."})]}),t.jsxs("div",{className:"notifications",onClick:()=>n("notifications"),style:{cursor:"pointer"},children:[t.jsx("i",{className:"fas fa-bell"}),t.jsx("span",{className:"notification-count",children:"3"})]}),t.jsxs("div",{className:"user-profile-container",children:[t.jsxs("button",{className:"user-profile",onClick:N,type:"button",children:[t.jsx("div",{className:"avatar",children:h}),t.jsxs("div",{className:"user-info",children:[t.jsx("div",{className:"user-name",children:v}),t.jsx("div",{className:"user-role",children:y})]}),t.jsx("i",{className:"fas fa-chevron-down"})]}),f&&t.jsxs("div",{className:"user-menu-dropdown",children:[t.jsxs("div",{className:"dropdown-header",children:[t.jsx("div",{className:"user-avatar-large",children:h}),t.jsxs("div",{children:[t.jsx("div",{className:"user-name-large",children:v}),t.jsx("div",{className:"user-email",children:(i==null?void 0:i.username)||"admin@example.com"})]})]}),t.jsx("div",{className:"menu-divider"}),t.jsxs("div",{className:"menu-items",children:[t.jsxs("button",{className:"menu-item",onClick:()=>{m(!1),n("profile")},type:"button",children:[t.jsx("i",{className:"fas fa-user"}),t.jsx("span",{children:"My Profile"})]}),t.jsxs("button",{className:"menu-item",onClick:()=>{m(!1),n("account-settings")},type:"button",children:[t.jsx("i",{className:"fas fa-cog"}),t.jsx("span",{children:"Account Settings"})]}),t.jsx("div",{className:"menu-divider"}),t.jsxs("div",{className:"menu-item-submenu",children:[t.jsxs("button",{className:"menu-item",onClick:()=>p(!x),type:"button",children:[t.jsx("i",{className:"fas fa-users"}),t.jsx("span",{children:"Management"}),t.jsx("i",{className:`fas fa-chevron-${x?"up":"down"} submenu-arrow`})]}),x&&t.jsxs("div",{className:"submenu",children:[t.jsxs("button",{className:"submenu-item",onClick:()=>{m(!1),p(!1),n("user-management")},type:"button",children:[t.jsx("i",{className:"fas fa-users"}),t.jsx("span",{children:"User Management"})]}),t.jsxs("button",{className:"submenu-item",onClick:()=>{m(!1),p(!1),n("organisation-management")},type:"button",children:[t.jsx("i",{className:"fas fa-university"}),t.jsx("span",{children:"Organisation Management"})]}),t.jsxs("button",{className:"submenu-item",onClick:()=>{m(!1),p(!1),n("trust-management")},type:"button",children:[t.jsx("i",{className:"fas fa-handshake"}),t.jsx("span",{children:"Trust Management"})]})]})]}),y==="BlueVisionAdmin"&&t.jsxs("button",{className:"menu-item",onClick:()=>{m(!1),n("admin-settings")},type:"button",children:[t.jsx("i",{className:"fas fa-shield-alt"}),t.jsx("span",{children:"Admin Settings"})]}),y==="BlueVisionAdmin"&&u&&t.jsxs("button",{className:"menu-item",onClick:()=>{m(!1),u()},type:"button",children:[t.jsx("i",{className:"fas fa-user-plus"}),t.jsx("span",{children:"Register New User"})]})]}),t.jsx("div",{className:"menu-divider"}),t.jsxs("button",{className:"menu-item logout-item",onClick:()=>{m(!1),l()},type:"button",children:[t.jsx("i",{className:"fas fa-sign-out-alt"}),t.jsx("span",{children:"Logout"})]})]})]})]})]})})}function V_({activePage:n,showPage:i,user:l,onLogout:o,isAdmin:u}){const[f,m]=w.useState("loading"),[x,p]=w.useState(!1),[h,v]=w.useState(!1);return w.useEffect(()=>{const y=async()=>{const S=await dt.get("/api/threat-feeds/");m(S?"active":"offline")};y();const N=setInterval(y,3e4);return()=>clearInterval(N)},[]),t.jsx("nav",{className:"main-nav",children:t.jsxs("div",{className:"container nav-container",children:[t.jsxs("ul",{className:"nav-links",children:[t.jsx("li",{children:t.jsxs("a",{onClick:()=>i("dashboard"),className:n==="dashboard"?"active":"",children:[t.jsx("i",{className:"fas fa-chart-line"})," Dashboard"]})}),t.jsx("li",{children:t.jsxs("a",{onClick:()=>i("threat-feeds"),className:n==="threat-feeds"?"active":"",children:[t.jsx("i",{className:"fas fa-rss"})," Threat Feeds"]})}),t.jsx("li",{children:t.jsxs("a",{onClick:()=>i("ioc-management"),className:n==="ioc-management"?"active":"",children:[t.jsx("i",{className:"fas fa-search"})," IoC Management"]})}),t.jsx("li",{children:t.jsxs("a",{onClick:()=>i("ttp-analysis"),className:n==="ttp-analysis"?"active":"",children:[t.jsx("i",{className:"fas fa-sitemap"})," TTP Analysis"]})}),t.jsx("li",{children:t.jsxs("a",{onClick:()=>i("institutions"),className:n==="institutions"?"active":"",children:[t.jsx("i",{className:"fas fa-building"})," Institutions"]})}),t.jsx("li",{children:t.jsxs("a",{onClick:()=>i("reports"),className:n==="reports"?"active":"",children:[t.jsx("i",{className:"fas fa-file-alt"})," Reports"]})})]}),t.jsxs("div",{className:"nav-right",children:[t.jsxs("div",{className:"status-indicator",children:[t.jsx("span",{className:"status-dot",style:{backgroundColor:f==="active"?"#28a745":f==="loading"?"#ffc107":"#dc3545"}}),t.jsx("span",{children:f==="active"?"System Online":f==="loading"?"Checking...":"System Offline"})]}),l&&t.jsxs("div",{className:"user-profile-container",children:[t.jsxs("button",{className:"user-profile",onClick:()=>p(!x),children:[t.jsx("div",{className:"avatar",children:(l.first_name||l.username||"U").charAt(0).toUpperCase()}),t.jsxs("div",{className:"user-info",children:[t.jsx("div",{className:"user-name",children:l.first_name&&l.last_name?`${l.first_name} ${l.last_name}`:l.username}),t.jsx("div",{className:"user-role",children:l.role})]}),t.jsx("i",{className:"fas fa-chevron-down"})]}),x&&t.jsxs("div",{className:"user-menu-dropdown",children:[t.jsxs("div",{className:"dropdown-header",children:[t.jsx("div",{className:"user-avatar-large",children:(l.first_name||l.username||"U").charAt(0).toUpperCase()}),t.jsxs("div",{children:[t.jsx("div",{className:"user-name-large",children:l.first_name&&l.last_name?`${l.first_name} ${l.last_name}`:l.username}),t.jsx("div",{className:"user-email",children:l.email||l.username})]})]}),t.jsx("div",{className:"menu-divider"}),t.jsxs("div",{className:"menu-items",children:[t.jsxs("button",{className:"menu-item",onClick:()=>{i("profile"),p(!1)},children:[t.jsx("i",{className:"fas fa-user"}),t.jsx("span",{children:"My Profile"})]}),t.jsxs("div",{className:"menu-item-submenu",children:[t.jsxs("button",{className:"menu-item",onClick:()=>v(!h),children:[t.jsx("i",{className:"fas fa-users"}),t.jsx("span",{children:"Management"}),t.jsx("i",{className:`fas fa-chevron-${h?"up":"down"} submenu-arrow`})]}),h&&t.jsxs("div",{className:"submenu",children:[t.jsxs("button",{className:"submenu-item",onClick:()=>{i("user-management"),p(!1),v(!1)},children:[t.jsx("i",{className:"fas fa-users"}),t.jsx("span",{children:"User Management"})]}),t.jsxs("button",{className:"submenu-item",onClick:()=>{i("institutions"),p(!1),v(!1)},children:[t.jsx("i",{className:"fas fa-university"}),t.jsx("span",{children:"Institution Management"})]}),t.jsxs("button",{className:"submenu-item",onClick:()=>{i("trust-management"),p(!1),v(!1)},children:[t.jsx("i",{className:"fas fa-handshake"}),t.jsx("span",{children:"Trust Management"})]})]})]}),u&&t.jsxs("button",{className:"menu-item",onClick:()=>{i("notifications"),p(!1)},children:[t.jsx("i",{className:"fas fa-shield-alt"}),t.jsx("span",{children:"Admin Settings"})]})]}),t.jsx("div",{className:"menu-divider"}),t.jsxs("button",{className:"menu-item logout-item",onClick:()=>{o(),p(!1)},children:[t.jsx("i",{className:"fas fa-sign-out-alt"}),t.jsx("span",{children:"Logout"})]})]})]})]})]})})}function X_({active:n,showPage:i,isAuthenticated:l,isAuthenticating:o}){var G,Te,Be,Ne,Re,xt,ft,B,Ce,M,Q,$,ye,Ge,tt,ae,Ot,_t,_e,We;if(!n)return null;const[u,f]=w.useState({threat_feeds:0,indicators:0,ttps:0,status:"loading"}),[m,x]=w.useState([]),[p,h]=w.useState(!1),[v,y]=w.useState(null),N=w.useRef(null),S=w.useRef(null),A=w.useRef(null),[z,U]=w.useState([]),[oe,ie]=w.useState(!1),[me,Ae]=w.useState(null),[de,pe]=w.useState({days:30,type:null,feed_id:null}),[W,Ke]=w.useState({total_indicators:0,avg_daily:0,type_distribution:[]}),[he,De]=w.useState({status:"unknown",database:{status:"unknown"},services:{redis:{status:"unknown"}},system:{cpu_percent:0,memory_percent:0,disk_percent:0},feeds:{total:0,active:0,external:0,feeds:[]},errors:[],timestamp:null}),[xe,je]=w.useState(!1),[ze,we]=w.useState(null),[Ze,L]=w.useState([]),[ne,P]=w.useState(!1),[Ue,T]=w.useState(null),[F,le]=w.useState(!1),[ce,fe]=w.useState("json"),[Oe,ve]=w.useState(!1);w.useEffect(()=>{n&&!o&&l&&(ke(),$e(),re(),k(),V())},[n,l,o]),w.useEffect(()=>{n&&!o&&l&&re()},[de,n,l,o]),w.useEffect(()=>{if(!n||o||!l)return;const D=setInterval(()=>{k()},3e4);return()=>clearInterval(D)},[n,l,o]);const ke=async()=>{const D=await dt.get("/api/threat-feeds/");if(D){let ee=0,at=0;if(D.results)for(const jt of D.results){const ht=await dt.get(`/api/threat-feeds/${jt.id}/status/`);ht&&(ee+=ht.indicator_count||0,at+=ht.ttp_count||0)}f({threat_feeds:D.count||0,indicators:ee,ttps:at,status:"active"})}},$e=async()=>{h(!0),y(null);try{const D=await dt.get("/api/indicators/");if(D&&D.results){const ee=D.results.slice(0,6).map(at=>se(at));x(ee)}else x([])}catch(D){console.error("Error fetching recent IoCs:",D),y("Failed to load recent threat intelligence"),x([])}finally{h(!1)}},re=async()=>{ie(!0),Ae(null);try{const D=new URLSearchParams({days:de.days.toString()});de.type&&D.append("type",de.type),de.feed_id&&D.append("feed_id",de.feed_id);const ee=await dt.get(`/api/threat-activity-chart/?${D}`);if(ee&&ee.success)U(ee.data),Ke(ee.summary),N.current&&et(ee.data,ee.summary);else throw new Error("Failed to fetch chart data")}catch(D){console.error("Error fetching chart data:",D),Ae("Failed to load chart data"),U([])}finally{ie(!1)}},k=async()=>{je(!0),we(null);try{const D=await dt.get("/api/system-health/");if(D)De({status:D.status||"unknown",database:D.database||{status:"unknown"},services:D.services||{redis:{status:"unknown"}},system:D.system||{cpu_percent:0,memory_percent:0,disk_percent:0},feeds:D.feeds||{total:0,active:0,external:0,feeds:[]},errors:D.errors||[],timestamp:D.timestamp||new Date().toISOString()});else throw new Error("Failed to fetch system health data")}catch(D){console.error("Error fetching system health:",D),we("Failed to load system health data"),De(ee=>({...ee,status:"error",timestamp:new Date().toISOString()}))}finally{je(!1)}},se=D=>{var St;const ee={ip:"IP Address",domain:"Domain",url:"URL",file_hash:"File Hash",email:"Email Address",user_agent:"User Agent"},at=Ee=>Ee>=80?{level:"high",label:"High"}:Ee>=50?{level:"medium",label:"Medium"}:{level:"low",label:"Low"},jt=(Ee,Pe)=>Pe==="file_hash"&&Ee.length>16?Ee.substring(0,16)+"...":Ee.length>30?Ee.substring(0,30)+"...":Ee,ht=at(D.confidence||50),kt={ip:"fa-network-wired",domain:"fa-globe",url:"fa-link",file_hash:"fa-file-signature",email:"fa-envelope",user_agent:"fa-browser"},vt=Ee=>{const Pe=new Date(Ee),Et=Math.abs(new Date-Pe),qt=Math.ceil(Et/(1e3*60*60*24));return qt===1?"1 day ago":qt<7?`${qt} days ago`:qt<30?`${Math.ceil(qt/7)} weeks ago`:`${Math.ceil(qt/30)} months ago`};return{id:D.id,displayType:ee[D.type]||D.type.charAt(0).toUpperCase()+D.type.slice(1),typeIcon:kt[D.type]||"fa-question-circle",rawType:D.type,title:D.name||"",value:D.value,truncatedValue:jt(D.value,D.type),source:((St=D.threat_feed)==null?void 0:St.name)||D.source||"Internal",severity:ht.label,severityClass:ht.level,confidence:D.confidence||50,status:D.is_active!==!1?"active":"inactive",isAnonymized:D.is_anonymized||!1,age:vt(D.created_at||new Date().toISOString()),created_at:D.created_at||new Date().toISOString()}},V=async()=>{P(!0),T(null);try{const D=await dt.get("/api/recent-activities/?limit=10");D&&D.success?L(D.activities||[]):T("Failed to load recent activities")}catch(D){console.error("Error fetching recent activities:",D),T("Failed to load recent activities")}finally{P(!1)}},ue=D=>{switch(D==null?void 0:D.toLowerCase()){case"healthy":case"connected":case"active":case"success":return"#28a745";case"warning":case"stale":return"#ffc107";case"error":case"disconnected":case"failed":case"inactive":return"#dc3545";default:return"#6c757d"}},Se=D=>{switch(D==null?void 0:D.toLowerCase()){case"healthy":case"connected":case"active":case"success":return"fas fa-check-circle";case"warning":case"stale":return"fas fa-exclamation-triangle";case"error":case"disconnected":case"failed":case"inactive":return"fas fa-times-circle";default:return"fas fa-question-circle"}},Fe=D=>{if(!D)return"Unknown";const ee=new Date(D),jt=new Date-ee,ht=Math.floor(jt/6e4),kt=Math.floor(jt/36e5),vt=Math.floor(jt/864e5);return ht<1?"Just now":ht<60?`${ht}m ago`:kt<24?`${kt}h ago`:vt<7?`${vt}d ago`:ee.toLocaleDateString()},it=D=>{if(!D)return"Unknown";const ee=Math.floor(D/3600),at=Math.floor(D%3600/60);if(ee>24){const jt=Math.floor(ee/24),ht=ee%24;return`${jt}d ${ht}h`}return`${ee}h ${at}m`};w.useEffect(()=>(n&&N.current&&z.length>0&&et(z,W),()=>{A.current&&A.current()}),[n,z,W]),w.useEffect(()=>{if(!n)return;const D=setInterval(()=>{console.log("Auto-refreshing chart data..."),re()},300*1e3);return()=>clearInterval(D)},[n,de]),w.useEffect(()=>{const D=()=>{n&&N.current&&z.length>0&&(clearTimeout(window.chartResizeTimeout),window.chartResizeTimeout=setTimeout(()=>{et(z,W)},300))};return window.addEventListener("resize",D),()=>{window.removeEventListener("resize",D),clearTimeout(window.chartResizeTimeout)}},[n,z,W]),w.useEffect(()=>()=>{A.current&&A.current(),Lj(".chart-tooltip").remove(),clearTimeout(window.chartResizeTimeout)},[]);const et=(D=[],ee={})=>{if(A.current&&A.current(),N.current&&hn(N.current).selectAll("*").remove(),!N.current||!D||D.length===0){N.current&&hn(N.current).append("svg").attr("width","100%").attr("height",300).attr("viewBox",`0 0 ${N.current.clientWidth||400} 300`).append("text").attr("x","50%").attr("y","50%").attr("text-anchor","middle").attr("dominant-baseline","middle").style("font-size","14px").style("fill","#666").text(oe?"Loading chart data...":"No data available");return}try{const at=N.current.clientWidth||400,jt=Math.max(at,400),ht=350,kt={top:40,right:60,bottom:60,left:70},vt=jt-kt.left-kt.right,St=ht-kt.top-kt.bottom,Ee=hn(N.current).append("svg").attr("width","100%").attr("height",ht).attr("viewBox",`0 0 ${jt} ${ht}`).style("max-width","100%").style("height","auto"),Pe=Ee.append("g").attr("transform",`translate(${kt.left},${kt.top})`),Wt=bx("%Y-%m-%d"),Et=D.map(ut=>({date:Wt(ut.date),count:ut.count,types:ut.types||{},originalDate:ut.date})).filter(ut=>ut.date&&!isNaN(ut.count));if(Et.length===0){Ee.append("text").attr("x","50%").attr("y","50%").attr("text-anchor","middle").attr("dominant-baseline","middle").style("font-size","14px").style("fill","#666").text("No valid data to display");return}const qt=u_().domain($y(Et,ut=>ut.date)).range([0,vt]),Jn=Mg(Et,ut=>ut.count)||1,Pt=zu().domain([0,Jn*1.1]).range([St,0]).nice();let da=S.current;da||(da=hn("body").append("div").attr("class","chart-tooltip").style("opacity",0).style("position","absolute").style("background","rgba(0, 0, 0, 0.9)").style("color","white").style("padding","12px").style("border-radius","6px").style("font-size","13px").style("pointer-events","none").style("z-index","1000").style("box-shadow","0 4px 12px rgba(0, 0, 0, 0.3)"),S.current=da);const Za=Ee.append("defs"),Da=`areaGradient-${Date.now()}`,Ha=Za.append("linearGradient").attr("id",Da).attr("x1","0%").attr("y1","0%").attr("x2","0%").attr("y2","100%");Ha.append("stop").attr("offset","0%").attr("stop-color","#0056b3").attr("stop-opacity",.8),Ha.append("stop").attr("offset","100%").attr("stop-color","#00a0e9").attr("stop-opacity",.1),Pe.append("g").attr("class","grid").attr("transform",`translate(0,${St})`).call(nu(qt).ticks(Math.min(7,Et.length)).tickSize(-St).tickFormat("")).style("stroke-dasharray","3,3").style("opacity",.3),Pe.append("g").attr("class","grid").call(su(Pt).ticks(6).tickSize(-vt).tickFormat("")).style("stroke-dasharray","3,3").style("opacity",.3);const ia=f_().x(ut=>qt(ut.date)).y0(St).y1(ut=>Pt(ut.count)).curve(cg);Pe.append("path").datum(Et).attr("fill",`url(#${Da})`).attr("d",ia);const ka=Uu().x(ut=>qt(ut.date)).y(ut=>Pt(ut.count)).curve(cg);Pe.append("path").datum(Et).attr("fill","none").attr("stroke","#0056b3").attr("stroke-width",3).attr("d",ka),Pe.selectAll(".dot").data(Et).enter().append("circle").attr("class","dot").attr("cx",ut=>qt(ut.date)).attr("cy",ut=>Pt(ut.count)).attr("r",4).attr("fill","#0056b3").attr("stroke","white").attr("stroke-width",2).style("cursor","pointer").on("mouseover",function(ut,_a){hn(this).transition().duration(200).attr("r",6).attr("fill","#ff6b35");const Qa=zo("%B %d, %Y"),ra=Object.entries(_a.types).map(([Kn,Wn])=>`${Kn}: ${Wn}`).join("<br>");da&&(da.transition().duration(200).style("opacity",.9),da.html(`
              <strong>${Qa(_a.date)}</strong><br/>
              Total IoCs: <strong>${_a.count}</strong><br/>
              ${ra?`<br/><em>Breakdown:</em><br/>${ra}`:""}
            `).style("left",ut.pageX+10+"px").style("top",ut.pageY-28+"px"))}).on("mouseout",function(ut,_a){hn(this).transition().duration(200).attr("r",4).attr("fill","#0056b3"),da&&da.transition().duration(500).style("opacity",0)});const pt=zo("%m/%d");Pe.append("g").attr("transform",`translate(0,${St})`).call(nu(qt).ticks(Math.min(7,Et.length)).tickFormat(pt)).selectAll("text").style("text-anchor","end").attr("dx","-.8em").attr("dy",".15em").attr("transform","rotate(-45)"),Pe.append("g").call(su(Pt).ticks(6)).append("text").attr("transform","rotate(-90)").attr("y",6).attr("dy","0.71em").attr("text-anchor","end").style("fill","#666").text("IoC Count"),Pe.append("text").attr("x",vt/2).attr("y",-15).attr("text-anchor","middle").style("font-size","18px").style("font-weight","600").style("fill","#2d3748").text("Threat Activity Trends");const xa=`Total: ${ee.total_indicators||0} IoCs | Daily Avg: ${ee.avg_daily||0}`;Pe.append("text").attr("x",vt/2).attr("y",St+50).attr("text-anchor","middle").style("font-size","12px").style("fill","#666").text(xa),A.current=()=>{S.current&&(S.current.remove(),S.current=null),N.current&&hn(N.current).selectAll("*").remove()}}catch(at){console.error("Error creating chart:",at),Ae("Failed to create chart visualization")}};function Gt(){le(!1),fe("json")}async function wt(){ve(!0);try{let D,ee,at;const jt={export_date:new Date().toISOString(),dashboard_stats:u,recent_iocs:m,system_health:he,chart_data:z,chart_summary:W,chart_filters:de};switch(ce){case"csv":D=Tt(jt),ee=`dashboard_export_${new Date().toISOString().split("T")[0]}.csv`,at="text/csv";break;case"json":D=It(jt),ee=`dashboard_export_${new Date().toISOString().split("T")[0]}.json`,at="application/json";break;case"summary":D=Kt(jt),ee=`dashboard_summary_${new Date().toISOString().split("T")[0]}.txt`,at="text/plain";break;default:throw new Error("Unsupported export format")}const ht=new Blob([D],{type:at}),kt=window.URL.createObjectURL(ht),vt=document.createElement("a");vt.href=kt,vt.download=ee,document.body.appendChild(vt),vt.click(),document.body.removeChild(vt),window.URL.revokeObjectURL(kt),Gt(),console.log(`Successfully exported dashboard data as ${ce.toUpperCase()}`)}catch(D){console.error("Dashboard export failed:",D),alert("Export failed. Please try again.")}finally{ve(!1)}}function Tt(D){var at,jt,ht,kt,vt,St,Ee,Pe,Wt;let ee="";return ee+=`CRISP Dashboard Export
`,ee+=`Export Date: ${new Date(D.export_date).toLocaleString()}

`,ee+=`DASHBOARD STATISTICS
`,ee+=`Metric,Value
`,ee+=`Active IoCs,${D.dashboard_stats.indicators||0}
`,ee+=`TTPs,${D.dashboard_stats.ttps||0}
`,ee+=`Threat Feeds,${D.dashboard_stats.threat_feeds||0}
`,ee+=`Platform Status,${D.dashboard_stats.status||"Unknown"}

`,D.recent_iocs&&D.recent_iocs.length>0&&(ee+=`RECENT INDICATORS OF COMPROMISE
`,ee+=`Type,Indicator,Source,Severity,Status,Created
`,D.recent_iocs.forEach(Et=>{const qt=[Et.displayType||"",`"${(Et.value||"").replace(/"/g,'""')}"`,Et.source||"",Et.severity||"","Active",Et.created_at||""].join(",");ee+=qt+`
`}),ee+=`
`),D.system_health&&(ee+=`SYSTEM HEALTH
`,ee+=`Component,Status,Details
`,ee+=`Overall Status,${D.system_health.status||"Unknown"},
`,ee+=`Database,${((at=D.system_health.database)==null?void 0:at.status)||"Unknown"},${((jt=D.system_health.database)==null?void 0:jt.details)||""}
`,ee+=`Redis,${((kt=(ht=D.system_health.services)==null?void 0:ht.redis)==null?void 0:kt.status)||"Unknown"},${((St=(vt=D.system_health.services)==null?void 0:vt.redis)==null?void 0:St.details)||""}
`,D.system_health.system&&(ee+=`CPU Usage,${((Ee=D.system_health.system.cpu_percent)==null?void 0:Ee.toFixed(1))||"N/A"}%,
`,ee+=`Memory Usage,${((Pe=D.system_health.system.memory_percent)==null?void 0:Pe.toFixed(1))||"N/A"}%,
`,ee+=`Disk Usage,${((Wt=D.system_health.system.disk_percent)==null?void 0:Wt.toFixed(1))||"N/A"}%,
`)),ee}function It(D){return JSON.stringify(D,null,2)}function Kt(D){var at,jt,ht,kt,vt,St;let ee="";if(ee+=`CRISP THREAT INTELLIGENCE DASHBOARD SUMMARY
`,ee+="="+"=".repeat(48)+`

`,ee+=`Export Date: ${new Date(D.export_date).toLocaleString()}

`,ee+=`OVERVIEW
`,ee+="-".repeat(20)+`
`,ee+=`• Active IoCs: ${D.dashboard_stats.indicators||0}
`,ee+=`• TTPs: ${D.dashboard_stats.ttps||0}
`,ee+=`• Threat Feeds: ${D.dashboard_stats.threat_feeds||0}
`,ee+=`• Platform Status: ${D.dashboard_stats.status||"Unknown"}

`,D.recent_iocs&&D.recent_iocs.length>0){ee+=`RECENT THREAT INTELLIGENCE
`,ee+="-".repeat(30)+`
`,ee+=`Total Recent IoCs: ${D.recent_iocs.length}

`;const Ee=D.recent_iocs.reduce((Pe,Wt)=>(Pe[Wt.displayType]=(Pe[Wt.displayType]||0)+1,Pe),{});ee+=`Type Distribution:
`,Object.entries(Ee).forEach(([Pe,Wt])=>{ee+=`  • ${Pe}: ${Wt}
`}),ee+=`
`}return D.system_health&&(ee+=`SYSTEM HEALTH
`,ee+="-".repeat(20)+`
`,ee+=`Overall Status: ${D.system_health.status||"Unknown"}
`,ee+=`Database: ${((at=D.system_health.database)==null?void 0:at.status)||"Unknown"}
`,ee+=`Redis: ${((ht=(jt=D.system_health.services)==null?void 0:jt.redis)==null?void 0:ht.status)||"Unknown"}
`,D.system_health.system&&(ee+=`CPU Usage: ${((kt=D.system_health.system.cpu_percent)==null?void 0:kt.toFixed(1))||"N/A"}%
`,ee+=`Memory Usage: ${((vt=D.system_health.system.memory_percent)==null?void 0:vt.toFixed(1))||"N/A"}%
`,ee+=`Disk Usage: ${((St=D.system_health.system.disk_percent)==null?void 0:St.toFixed(1))||"N/A"}%
`),ee+=`
`),D.chart_summary&&D.chart_summary.total_indicators>0&&(ee+=`THREAT ACTIVITY TRENDS
`,ee+="-".repeat(25)+`
`,ee+=`Total Indicators (${D.chart_filters.days} days): ${D.chart_summary.total_indicators}
`,ee+=`Daily Average: ${D.chart_summary.avg_daily}
`,ee+=`Date Range: ${D.chart_summary.start_date} to ${D.chart_summary.end_date}

`),ee+=`Generated by CRISP Threat Intelligence Platform
`,ee}return t.jsxs("section",{id:"dashboard",className:`page-section ${n?"active":""}`,children:[t.jsxs("div",{className:"page-header",children:[t.jsxs("div",{children:[t.jsx("h1",{className:"page-title",children:"Threat Intelligence Dashboard"}),t.jsx("p",{className:"page-subtitle",children:"Overview of threat intelligence and platform activity"})]}),t.jsxs("div",{className:"action-buttons",children:[t.jsxs("button",{className:"btn btn-outline",onClick:()=>le(!0),children:[t.jsx("i",{className:"fas fa-download"})," Export Data"]}),t.jsxs("button",{className:"btn btn-primary",onClick:()=>i("threat-feeds","addFeed"),children:[t.jsx("i",{className:"fas fa-plus"})," Add New Feed"]})]})]}),t.jsxs("div",{className:"stats-grid",children:[t.jsxs("div",{className:"stat-card",children:[t.jsxs("div",{className:"stat-title",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-search"})}),t.jsx("span",{children:"Active IoCs"})]}),t.jsx("div",{className:"stat-value",children:u.indicators||0}),t.jsxs("div",{className:"stat-change increase",children:[t.jsx("span",{children:t.jsx("i",{className:"fas fa-arrow-up"})}),t.jsx("span",{children:"Live data"})]})]}),t.jsxs("div",{className:"stat-card",children:[t.jsxs("div",{className:"stat-title",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-sitemap"})}),t.jsx("span",{children:"TTPs"})]}),t.jsx("div",{className:"stat-value",children:u.ttps||0}),t.jsxs("div",{className:"stat-change increase",children:[t.jsx("span",{children:t.jsx("i",{className:"fas fa-arrow-up"})}),t.jsx("span",{children:"Live data"})]})]}),t.jsxs("div",{className:"stat-card",children:[t.jsxs("div",{className:"stat-title",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-rss"})}),t.jsx("span",{children:"Threat Feeds"})]}),t.jsx("div",{className:"stat-value",children:u.threat_feeds||0}),t.jsxs("div",{className:"stat-change increase",children:[t.jsx("span",{children:t.jsx("i",{className:"fas fa-arrow-up"})}),t.jsx("span",{children:"Live data"})]})]}),t.jsxs("div",{className:"stat-card",children:[t.jsxs("div",{className:"stat-title",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-server"})}),t.jsx("span",{children:"Platform Status"})]}),t.jsx("div",{className:"stat-value",children:u.status==="active"?"Online":"Offline"}),t.jsxs("div",{className:"stat-change",children:[t.jsx("span",{children:t.jsx("i",{className:"fas fa-circle",style:{color:u.status==="active"?"#28a745":"#dc3545"}})}),t.jsx("span",{children:"Live status"})]})]})]}),t.jsxs("div",{className:"main-grid",children:[t.jsxs("div",{children:[t.jsxs("div",{className:"card",children:[t.jsxs("div",{className:"card-header",children:[t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-shield-alt card-icon"})," Recent Threat Intelligence"]}),t.jsx("div",{className:"card-actions",children:t.jsxs("button",{className:"btn btn-outline btn-sm",onClick:$e,disabled:p,children:[t.jsx("i",{className:`fas fa-sync-alt ${p?"fa-spin":""}`}),p?"Refreshing...":"Refresh"]})})]}),t.jsx("div",{className:"card-content",children:p?t.jsxs("div",{className:"loading-state",children:[t.jsx("div",{className:"loading-spinner"}),t.jsx("p",{children:"Loading recent threat intelligence..."})]}):v?t.jsxs("div",{className:"error-state",children:[t.jsx("i",{className:"fas fa-exclamation-triangle"}),t.jsx("p",{children:v}),t.jsxs("button",{className:"btn btn-primary btn-sm",onClick:$e,children:[t.jsx("i",{className:"fas fa-retry"})," Retry"]})]}):m.length===0?t.jsxs("div",{className:"empty-state",children:[t.jsx("i",{className:"fas fa-shield-alt"}),t.jsx("p",{children:"No threat intelligence available"}),t.jsx("p",{className:"text-muted",children:"IoCs will appear here once feeds are consumed"})]}):t.jsxs("table",{className:"data-table",children:[t.jsx("thead",{children:t.jsxs("tr",{children:[t.jsx("th",{children:"Type"}),t.jsx("th",{children:"Indicator"}),t.jsx("th",{children:"Source"}),t.jsx("th",{children:"Severity"}),t.jsx("th",{children:"Status"})]})}),t.jsx("tbody",{children:m.map((D,ee)=>t.jsxs("tr",{children:[t.jsx("td",{children:t.jsxs("div",{className:"type-indicator",children:[t.jsx("i",{className:`fas ${D.typeIcon}`}),t.jsx("span",{children:D.displayType})]})}),t.jsx("td",{children:t.jsxs("div",{className:"indicator-value",children:[t.jsx("span",{className:"value",title:D.value,children:D.truncatedValue}),D.isAnonymized&&t.jsxs("span",{className:"badge badge-anonymized",children:[t.jsx("i",{className:"fas fa-mask"})," Anonymized"]})]})}),t.jsx("td",{children:t.jsxs("div",{className:"source-info",children:[t.jsx("span",{className:"source-name",children:D.source}),t.jsx("div",{className:"source-meta",children:t.jsx("span",{className:"age-indicator",title:`Created: ${D.created_at}`,children:D.age})})]})}),t.jsx("td",{children:t.jsx("span",{className:`badge badge-${D.severityClass}`,children:D.severity})}),t.jsx("td",{children:t.jsxs("div",{className:"badge-tags",children:[t.jsx("span",{className:"badge badge-active",children:"Active"}),D.confidence>=80&&t.jsxs("span",{className:"badge badge-verified",children:[t.jsx("i",{className:"fas fa-check-circle"})," High Confidence"]}),D.confidence<50&&t.jsxs("span",{className:"badge badge-warning",children:[t.jsx("i",{className:"fas fa-exclamation-triangle"})," Low Confidence"]}),t.jsxs("span",{className:"badge badge-realtime",title:"Real-time data",children:[t.jsx("i",{className:"fas fa-broadcast-tower"})," Live"]})]})})]},`${D.id||ee}`))})]})})]}),t.jsxs("div",{className:"card",children:[t.jsxs("div",{className:"card-header",children:[t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-chart-area card-icon"})," Threat Activity Trends"]}),t.jsxs("div",{className:"card-actions",children:[t.jsxs("select",{className:"btn btn-outline btn-sm",value:de.days,onChange:D=>pe({...de,days:parseInt(D.target.value)}),style:{marginRight:"10px"},children:[t.jsx("option",{value:"7",children:"Last 7 Days"}),t.jsx("option",{value:"14",children:"Last 14 Days"}),t.jsx("option",{value:"30",children:"Last 30 Days"}),t.jsx("option",{value:"60",children:"Last 60 Days"}),t.jsx("option",{value:"90",children:"Last 90 Days"})]}),t.jsxs("select",{className:"btn btn-outline btn-sm",value:de.type||"",onChange:D=>pe({...de,type:D.target.value||null}),style:{marginRight:"10px"},children:[t.jsx("option",{value:"",children:"All Types"}),t.jsx("option",{value:"ip",children:"IP Address"}),t.jsx("option",{value:"domain",children:"Domain"}),t.jsx("option",{value:"url",children:"URL"}),t.jsx("option",{value:"file_hash",children:"File Hash"}),t.jsx("option",{value:"email",children:"Email"})]}),t.jsxs("button",{className:"btn btn-outline btn-sm",onClick:re,disabled:oe,title:"Refresh chart data",children:[t.jsx("i",{className:`fas fa-sync-alt ${oe?"fa-spin":""}`}),oe?" Loading...":" Refresh"]})]})]}),W.total_indicators>0&&t.jsxs("div",{className:"card-status-bar",style:{background:"#f8f9fa",padding:"8px 16px",fontSize:"12px",color:"#666",borderBottom:"1px solid #e9ecef"},children:[t.jsxs("span",{children:[t.jsx("strong",{children:"Total IoCs:"})," ",W.total_indicators]}),t.jsx("span",{style:{margin:"0 15px"},children:"|"}),t.jsxs("span",{children:[t.jsx("strong",{children:"Daily Average:"})," ",W.avg_daily]}),t.jsx("span",{style:{margin:"0 15px"},children:"|"}),t.jsxs("span",{children:[t.jsx("strong",{children:"Date Range:"})," ",W.start_date," to ",W.end_date]})]}),t.jsxs("div",{className:"card-content",children:[me&&t.jsxs("div",{className:"alert alert-error",style:{background:"#fff5f5",border:"1px solid #fed7d7",color:"#c53030",padding:"12px",borderRadius:"4px",marginBottom:"16px"},children:[t.jsx("i",{className:"fas fa-exclamation-triangle"})," ",me]}),t.jsx(Y_,{children:t.jsxs("div",{style:{position:"relative",minHeight:"350px"},children:[oe&&t.jsxs("div",{style:{position:"absolute",top:"50%",left:"50%",transform:"translate(-50%, -50%)",textAlign:"center",zIndex:10},children:[t.jsx("i",{className:"fas fa-spinner fa-spin",style:{fontSize:"24px",color:"#0056b3"}}),t.jsx("p",{style:{marginTop:"10px",color:"#666"},children:"Loading chart data..."})]}),t.jsx("div",{className:"chart-container",ref:N,style:{minHeight:"350px",width:"100%",overflow:"visible"}})]})})]})]})]}),t.jsxs("div",{className:"side-panels",children:[t.jsxs("div",{className:"card",children:[t.jsx("div",{className:"card-header",children:t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-building card-icon"})," Connected Institutions"]})}),t.jsx("div",{className:"card-content",children:t.jsxs("ul",{className:"institution-list",children:[t.jsxs("li",{className:"institution-item",children:[t.jsx("div",{className:"institution-logo",children:"UP"}),t.jsxs("div",{className:"institution-details",children:[t.jsx("div",{className:"institution-name",children:"University of Pretoria"}),t.jsxs("div",{className:"institution-stats",children:[t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-exchange-alt"})," 125 IoCs"]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-clock"})," 5m ago"]})]})]}),t.jsx("div",{className:"trust-level",children:t.jsx("div",{className:"trust-fill",style:{width:"90%"}})})]}),t.jsxs("li",{className:"institution-item",children:[t.jsx("div",{className:"institution-logo",children:"CS"}),t.jsxs("div",{className:"institution-details",children:[t.jsx("div",{className:"institution-name",children:"Cyber Security Hub"}),t.jsxs("div",{className:"institution-stats",children:[t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-exchange-alt"})," 342 IoCs"]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-clock"})," 17m ago"]})]})]}),t.jsx("div",{className:"trust-level",children:t.jsx("div",{className:"trust-fill",style:{width:"85%"}})})]}),t.jsxs("li",{className:"institution-item",children:[t.jsx("div",{className:"institution-logo",children:"SR"}),t.jsxs("div",{className:"institution-details",children:[t.jsx("div",{className:"institution-name",children:"SANReN CSIRT"}),t.jsxs("div",{className:"institution-stats",children:[t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-exchange-alt"})," 208 IoCs"]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-clock"})," 32m ago"]})]})]}),t.jsx("div",{className:"trust-level",children:t.jsx("div",{className:"trust-fill",style:{width:"75%"}})})]}),t.jsxs("li",{className:"institution-item",children:[t.jsx("div",{className:"institution-logo",children:"SB"}),t.jsxs("div",{className:"institution-details",children:[t.jsx("div",{className:"institution-name",children:"SABRIC"}),t.jsxs("div",{className:"institution-stats",children:[t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-exchange-alt"})," 156 IoCs"]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-clock"})," 1h ago"]})]})]}),t.jsx("div",{className:"trust-level",children:t.jsx("div",{className:"trust-fill",style:{width:"70%"}})})]})]})})]}),t.jsxs("div",{className:"card",children:[t.jsx("div",{className:"card-header",children:t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-history card-icon"})," Recent Activity"]})}),t.jsx("div",{className:"card-content",children:ne?t.jsxs("div",{className:"loading-state",children:[t.jsx("div",{className:"loading-spinner"}),t.jsx("p",{children:"Loading recent activities..."})]}):Ue?t.jsxs("div",{className:"error-state",children:[t.jsx("i",{className:"fas fa-exclamation-triangle"}),t.jsx("p",{children:Ue}),t.jsxs("button",{className:"btn btn-primary btn-sm",onClick:V,children:[t.jsx("i",{className:"fas fa-retry"})," Retry"]})]}):Ze.length===0?t.jsxs("div",{className:"empty-state",children:[t.jsx("i",{className:"fas fa-history"}),t.jsx("p",{children:"No recent activities"}),t.jsx("p",{className:"text-muted",children:"System activities will appear here"})]}):t.jsx("ul",{className:"activity-stream",children:Ze.map(D=>t.jsxs("li",{className:"activity-item",children:[t.jsx("div",{className:"activity-icon",children:t.jsx("i",{className:D.icon})}),t.jsxs("div",{className:"activity-details",children:[t.jsx("div",{className:"activity-text",children:D.title}),D.description&&t.jsx("div",{className:"activity-description",children:D.description}),t.jsxs("div",{className:"activity-meta",children:[t.jsx("div",{className:"activity-time",children:D.time_ago}),t.jsx("span",{className:`badge ${D.badge_type}`,children:D.badge_text})]})]})]},D.id))})})]})]})]}),t.jsxs("div",{className:"card",style:{marginTop:"24px"},children:[t.jsxs("div",{className:"card-header",children:[t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-heartbeat card-icon"})," System Health & Feed Status"]}),t.jsx("div",{className:"card-actions",children:t.jsxs("button",{className:"btn btn-outline btn-sm",onClick:k,disabled:xe,title:"Refresh system health",children:[t.jsx("i",{className:`fas fa-sync-alt ${xe?"fa-spin":""}`}),xe?" Loading...":" Refresh"]})})]}),t.jsxs("div",{className:"card-content",children:[ze&&t.jsxs("div",{className:"alert alert-error",style:{background:"#fff5f5",border:"1px solid #fed7d7",color:"#c53030",padding:"12px",borderRadius:"4px",marginBottom:"16px"},children:[t.jsx("i",{className:"fas fa-exclamation-triangle"})," ",ze]}),t.jsxs("div",{className:"system-status-overview",style:{display:"grid",gridTemplateColumns:"repeat(auto-fit, minmax(200px, 1fr))",gap:"16px",marginBottom:"24px"},children:[t.jsxs("div",{className:"status-card",style:{background:"#f8f9fa",border:"1px solid #dee2e6",borderRadius:"8px",padding:"16px",textAlign:"center"},children:[t.jsx("div",{style:{fontSize:"24px",color:ue(he.status),marginBottom:"8px"},children:t.jsx("i",{className:Se(he.status)})}),t.jsx("h3",{style:{margin:"0 0 4px 0",fontSize:"16px"},children:"Overall Status"}),t.jsx("p",{style:{margin:"0",color:ue(he.status),fontWeight:"bold",textTransform:"capitalize"},children:he.status}),t.jsxs("small",{style:{color:"#666"},children:["Last Check: ",Fe(he.timestamp)]})]}),t.jsxs("div",{className:"status-card",style:{background:"#f8f9fa",border:"1px solid #dee2e6",borderRadius:"8px",padding:"16px",textAlign:"center"},children:[t.jsx("div",{style:{fontSize:"24px",color:ue(((G=he.database)==null?void 0:G.status)||"unknown"),marginBottom:"8px"},children:t.jsx("i",{className:"fas fa-database"})}),t.jsx("h3",{style:{margin:"0 0 4px 0",fontSize:"16px"},children:"Database"}),t.jsx("p",{style:{margin:"0",color:ue(((Te=he.database)==null?void 0:Te.status)||"unknown"),fontWeight:"bold",textTransform:"capitalize"},children:((Be=he.database)==null?void 0:Be.status)||"Unknown"}),t.jsx("small",{style:{color:"#666"},children:(Ne=he.database)!=null&&Ne.connection_count?`${he.database.connection_count} connections`:"Connection info unavailable"})]}),t.jsxs("div",{className:"status-card",style:{background:"#f8f9fa",border:"1px solid #dee2e6",borderRadius:"8px",padding:"16px",textAlign:"center"},children:[t.jsx("div",{style:{fontSize:"24px",color:ue(((xt=(Re=he.services)==null?void 0:Re.redis)==null?void 0:xt.status)||"unknown"),marginBottom:"8px"},children:t.jsx("i",{className:"fas fa-memory"})}),t.jsx("h3",{style:{margin:"0 0 4px 0",fontSize:"16px"},children:"Redis"}),t.jsx("p",{style:{margin:"0",color:ue(((B=(ft=he.services)==null?void 0:ft.redis)==null?void 0:B.status)||"unknown"),fontWeight:"bold",textTransform:"capitalize"},children:((M=(Ce=he.services)==null?void 0:Ce.redis)==null?void 0:M.status)||"Unknown"}),t.jsx("small",{style:{color:"#666"},children:($=(Q=he.services)==null?void 0:Q.redis)!=null&&$.info?`v${he.services.redis.info}`:"Version unavailable"})]}),t.jsxs("div",{className:"status-card",style:{background:"#f8f9fa",border:"1px solid #dee2e6",borderRadius:"8px",padding:"16px",textAlign:"center"},children:[t.jsx("div",{style:{fontSize:"24px",color:((ye=he.system)==null?void 0:ye.cpu_percent)>80?"#dc3545":((Ge=he.system)==null?void 0:Ge.cpu_percent)>60?"#ffc107":"#28a745",marginBottom:"8px"},children:t.jsx("i",{className:"fas fa-microchip"})}),t.jsx("h3",{style:{margin:"0 0 4px 0",fontSize:"16px"},children:"System Resources"}),t.jsxs("p",{style:{margin:"0",fontWeight:"bold"},children:["CPU: ",((ae=(tt=he.system)==null?void 0:tt.cpu_percent)==null?void 0:ae.toFixed(1))||"N/A","%"]}),t.jsxs("small",{style:{color:"#666"},children:["RAM: ",((_t=(Ot=he.system)==null?void 0:Ot.memory_percent)==null?void 0:_t.toFixed(1))||"N/A","% | Disk: ",((We=(_e=he.system)==null?void 0:_e.disk_percent)==null?void 0:We.toFixed(1))||"N/A","%"]})]})]}),t.jsxs("div",{className:"feed-status-section",children:[t.jsx("h3",{style:{margin:"0 0 16px 0",fontSize:"18px",borderBottom:"2px solid #dee2e6",paddingBottom:"8px"},children:"Feed Status Monitoring"}),he.feeds&&he.feeds.total>0&&t.jsxs("div",{className:"feed-summary",style:{display:"grid",gridTemplateColumns:"repeat(auto-fit, minmax(120px, 1fr))",gap:"12px",marginBottom:"20px",padding:"16px",background:"#f1f3f4",borderRadius:"6px"},children:[t.jsxs("div",{style:{textAlign:"center"},children:[t.jsx("div",{style:{fontSize:"24px",fontWeight:"bold",color:"#0056b3"},children:he.feeds.total}),t.jsx("small",{children:"Total Feeds"})]}),t.jsxs("div",{style:{textAlign:"center"},children:[t.jsx("div",{style:{fontSize:"24px",fontWeight:"bold",color:"#28a745"},children:he.feeds.active}),t.jsx("small",{children:"Active"})]}),t.jsxs("div",{style:{textAlign:"center"},children:[t.jsx("div",{style:{fontSize:"24px",fontWeight:"bold",color:"#17a2b8"},children:he.feeds.external}),t.jsx("small",{children:"External"})]}),t.jsxs("div",{style:{textAlign:"center"},children:[t.jsx("div",{style:{fontSize:"24px",fontWeight:"bold",color:"#6c757d"},children:he.feeds.total-he.feeds.external}),t.jsx("small",{children:"Internal"})]})]}),he.feeds&&he.feeds.total===0?t.jsxs("div",{style:{textAlign:"center",color:"#666",padding:"24px",background:"#f8f9fa",borderRadius:"6px",marginTop:"16px"},children:[t.jsx("i",{className:"fas fa-rss",style:{fontSize:"32px",marginBottom:"12px"}}),t.jsx("p",{style:{margin:"0 0 12px 0"},children:"No threat feeds configured yet."}),t.jsxs("button",{className:"btn btn-primary btn-sm",onClick:()=>i("threat-feeds"),children:[t.jsx("i",{className:"fas fa-plus"})," Manage Feeds"]})]}):t.jsx("div",{style:{textAlign:"center",padding:"16px",marginTop:"16px"},children:t.jsxs("button",{className:"btn btn-outline btn-sm",onClick:()=>i("threat-feeds"),children:[t.jsx("i",{className:"fas fa-cog"})," Manage All Feeds"]})})]}),he.errors&&he.errors.length>0&&t.jsxs("div",{className:"error-summary",style:{marginTop:"24px",padding:"16px",background:"#fff5f5",border:"1px solid #fed7d7",borderRadius:"6px"},children:[t.jsxs("h4",{style:{margin:"0 0 12px 0",color:"#c53030",fontSize:"16px"},children:[t.jsx("i",{className:"fas fa-exclamation-triangle"})," System Errors (",he.errors.length,")"]}),t.jsx("ul",{style:{margin:"0",paddingLeft:"20px"},children:he.errors.map((D,ee)=>t.jsx("li",{style:{color:"#c53030",marginBottom:"4px"},children:D},ee))})]}),he.system&&Object.keys(he.system).length>0&&t.jsxs("div",{className:"system-metrics",style:{marginTop:"24px",padding:"16px",background:"#f8f9fa",borderRadius:"6px"},children:[t.jsxs("h4",{style:{margin:"0 0 12px 0",fontSize:"16px"},children:[t.jsx("i",{className:"fas fa-chart-line"})," System Metrics"]}),t.jsxs("div",{style:{display:"grid",gridTemplateColumns:"repeat(auto-fit, minmax(200px, 1fr))",gap:"12px",fontSize:"14px"},children:[he.system.uptime&&t.jsxs("div",{children:[t.jsx("strong",{children:"Uptime:"})," ",it(he.system.uptime)]}),he.system.load_average&&t.jsxs("div",{children:[t.jsx("strong",{children:"Load Average:"})," ",he.system.load_average.join(", ")]}),t.jsxs("div",{children:[t.jsx("strong",{children:"Last Updated:"})," ",Fe(he.system.last_check)]})]})]})]})]}),F&&t.jsx("div",{className:"modal-overlay",onClick:Gt,children:t.jsxs("div",{className:"modal-content",onClick:D=>D.stopPropagation(),children:[t.jsxs("div",{className:"modal-header",children:[t.jsxs("h2",{children:[t.jsx("i",{className:"fas fa-download"})," Export Dashboard Data"]}),t.jsx("button",{className:"modal-close",onClick:Gt,children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsxs("div",{className:"modal-body",children:[t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"Export Format"}),t.jsxs("select",{className:"form-control",value:ce,onChange:D=>fe(D.target.value),children:[t.jsx("option",{value:"json",children:"JSON - Complete Data"}),t.jsx("option",{value:"csv",children:"CSV - Tabular Format"}),t.jsx("option",{value:"summary",children:"Summary Report"})]})]}),t.jsx("div",{className:"export-info",children:t.jsx("div",{className:"export-preview",children:t.jsxs("div",{children:[t.jsx("strong",{children:"Export Details:"}),t.jsx("p",{children:"Dashboard export will include:"}),t.jsxs("ul",{children:[t.jsxs("li",{children:["System statistics (",u.indicators," IoCs, ",u.ttps," TTPs, ",u.threat_feeds," feeds)"]}),t.jsxs("li",{children:["Recent threat intelligence (",m.length," items)"]}),t.jsx("li",{children:"System health data"}),t.jsxs("li",{children:["Threat activity chart data (",z.length," data points)"]})]}),ce==="csv"&&t.jsx("p",{children:t.jsx("em",{children:"CSV format includes IoCs table and summary metrics."})}),ce==="json"&&t.jsx("p",{children:t.jsx("em",{children:"JSON format includes complete structured data export."})}),ce==="summary"&&t.jsx("p",{children:t.jsx("em",{children:"Summary report includes key insights and formatted overview."})})]})})})]}),t.jsx("div",{className:"modal-footer",children:t.jsxs("div",{className:"modal-actions",children:[t.jsx("button",{type:"button",className:"btn btn-outline",onClick:Gt,disabled:Oe,children:"Cancel"}),t.jsx("button",{type:"button",className:"btn btn-primary",onClick:wt,disabled:Oe,children:Oe?t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Exporting..."]}):t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-download"})," Export Dashboard"]})})]})})]})})]})}function Z_({active:n,navigationState:i,setNavigationState:l}){if(!n)return null;const[o,u]=w.useState([]),[f,m]=w.useState(!1),[x,p]=w.useState(!1),[h,v]=w.useState(1),[y,N]=w.useState("all"),[S,A]=w.useState(!1),[z,U]=w.useState({type:"",status:"",source:"",search:""}),oe=10,[ie,me]=w.useState({name:"",description:"",is_external:!0,taxii_server_url:"",taxii_api_root:"",taxii_collection_id:"",taxii_username:"",taxii_password:""}),[Ae,de]=w.useState(new Set),[pe,W]=w.useState(new Map),[Ke,he]=w.useState(!1),[De,xe]=w.useState(null),[je,ze]=w.useState(!1);w.useEffect(()=>{n&&we()},[n]),w.useEffect(()=>{n&&(i==null?void 0:i.triggerModal)==="addFeed"&&(p(!0),l({triggerModal:null,modalParams:{}}))},[n,i,l]);const we=async()=>{m(!0);const k=await dt.get("/api/threat-feeds/");k&&k.results&&u(k.results),m(!1)},Ze=async k=>{de(se=>new Set([...se,k])),W(se=>new Map(se.set(k,{stage:"Initiating",message:"Starting consumption process...",percentage:0})));try{const se=await dt.post(`/api/threat-feeds/${k}/consume/`);if(se){console.log("Feed consumption started:",se);const V=setInterval(async()=>{try{const ue=await dt.get(`/api/threat-feeds/${k}/consumption_progress/`);if(ue&&ue.success){const Se=ue.progress;W(Fe=>new Map(Fe.set(k,{stage:Se.stage,message:Se.message||`${Se.stage}...`,percentage:Se.percentage||0,current:Se.current,total:Se.total}))),(Se.stage==="Completed"||Se.percentage>=100)&&(clearInterval(V),setTimeout(()=>{de(Fe=>{const it=new Set(Fe);return it.delete(k),it}),W(Fe=>{const it=new Map(Fe);return it.delete(k),it})},2e3),await we())}}catch(ue){console.error("Error fetching progress:",ue)}},2e3);setTimeout(()=>{clearInterval(V),de(ue=>{const Se=new Set(ue);return Se.delete(k),Se}),W(ue=>{const Se=new Map(ue);return Se.delete(k),Se})},3e5)}}catch(se){console.error("Error consuming feed:",se),alert("Failed to consume feed. Please try again."),de(V=>{const ue=new Set(V);return ue.delete(k),ue}),W(V=>{const ue=new Map(V);return ue.delete(k),ue})}},L=k=>{xe(k),he(!0)},ne=async()=>{if(De){ze(!0);try{await dt.delete(`/api/threat-feeds/${De.id}/`)!==null?(console.log("Feed deleted successfully:",De.name),await we(),P()):alert("Failed to delete threat feed. Please try again.")}catch(k){console.error("Error deleting feed:",k),alert("Error deleting threat feed. Please try again.")}finally{ze(!1)}}},P=()=>{he(!1),xe(null)},Ue=()=>{p(!0)},T=k=>{const{name:se,value:V,type:ue,checked:Se}=k.target;me(Fe=>({...Fe,[se]:ue==="checkbox"?Se:V}))},F=async k=>{k.preventDefault(),await dt.post("/api/threat-feeds/",ie)&&(p(!1),me({name:"",description:"",is_external:!0,taxii_server_url:"",taxii_api_root:"",taxii_collection_id:"",taxii_username:"",taxii_password:""}),we())},le=()=>{p(!1)},ce=()=>{let k=o;return y==="active"?k=k.filter(se=>se.is_active):y==="external"?k=k.filter(se=>se.is_external):y==="internal"&&(k=k.filter(se=>!se.is_external)),z.type&&(k=k.filter(se=>z.type==="stix-taxii"&&se.taxii_server_url||z.type==="internal"&&!se.is_external||z.type==="external"&&se.is_external)),z.status&&(k=k.filter(se=>z.status==="active"&&se.is_active||z.status==="disabled"&&!se.is_active)),z.source&&(k=k.filter(se=>z.source==="external"&&se.is_external||z.source==="internal"&&!se.is_external)),z.search&&(k=k.filter(se=>se.name.toLowerCase().includes(z.search.toLowerCase())||se.description&&se.description.toLowerCase().includes(z.search.toLowerCase())||se.taxii_server_url&&se.taxii_server_url.toLowerCase().includes(z.search.toLowerCase()))),k},fe=()=>{const k=ce(),se=(h-1)*oe;return k.slice(se,se+oe)},Oe=()=>Math.ceil(ce().length/oe),ve=k=>{N(k),v(1)},ke=(k,se)=>{U(V=>({...V,[k]:se})),v(1)},$e=k=>{v(k)},re=()=>{A(!S)};return t.jsxs("section",{id:"threat-feeds",className:`page-section ${n?"active":""}`,children:[t.jsxs("div",{className:"page-header",children:[t.jsxs("div",{children:[t.jsx("h1",{className:"page-title",children:"Threat Feeds"}),t.jsx("p",{className:"page-subtitle",children:"Manage and monitor all threat intelligence feeds"})]}),t.jsxs("div",{className:"action-buttons",children:[t.jsxs("button",{className:"btn btn-outline",onClick:re,children:[t.jsx("i",{className:"fas fa-filter"})," Filter Feeds ",S?"▲":"▼"]}),t.jsxs("button",{className:"btn btn-primary",onClick:Ue,children:[t.jsx("i",{className:"fas fa-plus"})," Add New Feed"]})]})]}),S&&t.jsx("div",{className:"filters-section",children:t.jsxs("div",{className:"filters-grid",children:[t.jsxs("div",{className:"filter-group",children:[t.jsx("label",{className:"filter-label",children:"Feed Type"}),t.jsx("div",{className:"filter-control",children:t.jsxs("select",{value:z.type,onChange:k=>ke("type",k.target.value),children:[t.jsx("option",{value:"",children:"All Types"}),t.jsx("option",{value:"stix-taxii",children:"STIX/TAXII"}),t.jsx("option",{value:"misp",children:"MISP"}),t.jsx("option",{value:"custom",children:"Custom"}),t.jsx("option",{value:"internal",children:"Internal"})]})})]}),t.jsxs("div",{className:"filter-group",children:[t.jsx("label",{className:"filter-label",children:"Status"}),t.jsx("div",{className:"filter-control",children:t.jsxs("select",{value:z.status,onChange:k=>ke("status",k.target.value),children:[t.jsx("option",{value:"",children:"All Statuses"}),t.jsx("option",{value:"active",children:"Active"}),t.jsx("option",{value:"disabled",children:"Disabled"}),t.jsx("option",{value:"error",children:"Error"})]})})]}),t.jsxs("div",{className:"filter-group",children:[t.jsx("label",{className:"filter-label",children:"Source"}),t.jsx("div",{className:"filter-control",children:t.jsxs("select",{value:z.source,onChange:k=>ke("source",k.target.value),children:[t.jsx("option",{value:"",children:"All Sources"}),t.jsx("option",{value:"external",children:"External"}),t.jsx("option",{value:"internal",children:"Internal"}),t.jsx("option",{value:"partner",children:"Partner"})]})})]}),t.jsxs("div",{className:"filter-group",children:[t.jsx("label",{className:"filter-label",children:"Search Feeds"}),t.jsx("div",{className:"filter-control",children:t.jsx("input",{type:"text",placeholder:"Search by name or URL...",value:z.search,onChange:k=>ke("search",k.target.value)})})]})]})}),t.jsxs("div",{className:"tabs",children:[t.jsxs("div",{className:`tab ${y==="active"?"active":""}`,onClick:()=>ve("active"),children:["Active Feeds (",o.filter(k=>k.is_active).length,")"]}),t.jsxs("div",{className:`tab ${y==="external"?"active":""}`,onClick:()=>ve("external"),children:["External (",o.filter(k=>k.is_external).length,")"]}),t.jsxs("div",{className:`tab ${y==="internal"?"active":""}`,onClick:()=>ve("internal"),children:["Internal (",o.filter(k=>!k.is_external).length,")"]}),t.jsxs("div",{className:`tab ${y==="all"?"active":""}`,onClick:()=>ve("all"),children:["All Feeds (",o.length,")"]})]}),t.jsx("div",{className:"card",children:t.jsx("div",{className:"card-content",children:f?t.jsxs("div",{style:{textAlign:"center",padding:"2rem"},children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Loading feeds..."]}):t.jsx("ul",{className:"feed-items",children:fe().map(k=>{var se,V,ue,Se;return t.jsxs("li",{className:"feed-item",children:[t.jsx("div",{className:"feed-icon",children:t.jsx("i",{className:k.is_external?"fas fa-globe":"fas fa-server"})}),t.jsxs("div",{className:"feed-details",children:[t.jsx("div",{className:"feed-name",children:k.name}),t.jsx("div",{className:"feed-description",children:k.description||"No description available"}),t.jsxs("div",{className:"feed-meta",children:[t.jsxs("div",{className:"feed-stats",children:[t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-link"})," ",k.taxii_collection_id||"N/A"]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-sync-alt"})," ",k.last_sync?new Date(k.last_sync).toLocaleString():"Never"]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-globe"})," ",k.is_external?"External":"Internal"]})]}),t.jsxs("div",{className:"feed-badges",children:[t.jsx("span",{className:`badge ${k.is_public?"badge-active":"badge-medium"}`,children:k.is_public?"Public":"Private"}),t.jsx("span",{className:"badge badge-connected",children:"STIX/TAXII"}),t.jsx("button",{className:"btn btn-sm btn-primary",onClick:()=>Ze(k.id),disabled:Ae.has(k.id),style:{minWidth:"140px"},children:Ae.has(k.id)?t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-spinner fa-spin"}),t.jsxs("div",{style:{display:"flex",flexDirection:"column",alignItems:"flex-start",fontSize:"11px"},children:[t.jsx("span",{children:((se=pe.get(k.id))==null?void 0:se.stage)||"Processing"}),((V=pe.get(k.id))==null?void 0:V.current)&&((ue=pe.get(k.id))==null?void 0:ue.total)&&t.jsxs("span",{style:{opacity:.8},children:[pe.get(k.id).current,"/",pe.get(k.id).total]}),((Se=pe.get(k.id))==null?void 0:Se.percentage)>0&&t.jsxs("span",{style:{opacity:.8},children:[pe.get(k.id).percentage,"%"]})]})]}):t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-download"})," Consume"]})}),t.jsx("button",{className:"btn btn-sm btn-danger",onClick:()=>L(k),disabled:Ae.has(k.id),title:Ae.has(k.id)?"Cannot delete while consuming":"Delete this threat feed",children:t.jsx("i",{className:"fas fa-trash"})})]})]})]})]},k.id)})})})}),Oe()>1&&t.jsxs("div",{className:"pagination",children:[t.jsx("div",{className:`page-item ${h===1?"disabled":""}`,onClick:()=>h>1&&$e(h-1),children:t.jsx("i",{className:"fas fa-chevron-left"})}),Array.from({length:Oe()},(k,se)=>se+1).map(k=>t.jsx("div",{className:`page-item ${k===h?"active":""}`,onClick:()=>$e(k),children:k},k)),t.jsx("div",{className:`page-item ${h===Oe()?"disabled":""}`,onClick:()=>h<Oe()&&$e(h+1),children:t.jsx("i",{className:"fas fa-chevron-right"})})]}),x&&t.jsx("div",{className:"modal-overlay",onClick:le,children:t.jsxs("div",{className:"modal-content",onClick:k=>k.stopPropagation(),children:[t.jsxs("div",{className:"modal-header",children:[t.jsx("h2",{children:"Add New Threat Feed"}),t.jsx("button",{className:"modal-close",onClick:le,children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsxs("form",{onSubmit:F,className:"modal-body",children:[t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Feed Name *"}),t.jsx("input",{type:"text",name:"name",value:ie.name,onChange:T,placeholder:"Enter feed name",required:!0})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Description"}),t.jsx("textarea",{name:"description",value:ie.description,onChange:T,placeholder:"Enter feed description",rows:"3"})]}),t.jsx("div",{className:"form-group",children:t.jsxs("label",{className:"checkbox-label",children:[t.jsx("input",{type:"checkbox",name:"is_external",checked:ie.is_external,onChange:T}),"External Feed"]})}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"TAXII Server URL *"}),t.jsx("input",{type:"url",name:"taxii_server_url",value:ie.taxii_server_url,onChange:T,placeholder:"https://example.com/taxii",required:!0})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"API Root"}),t.jsx("input",{type:"text",name:"taxii_api_root",value:ie.taxii_api_root,onChange:T,placeholder:"api-root"})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Collection ID"}),t.jsx("input",{type:"text",name:"taxii_collection_id",value:ie.taxii_collection_id,onChange:T,placeholder:"collection-id"})]}),t.jsxs("div",{className:"form-row",children:[t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Username"}),t.jsx("input",{type:"text",name:"taxii_username",value:ie.taxii_username,onChange:T,placeholder:"Username"})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Password"}),t.jsx("input",{type:"password",name:"taxii_password",value:ie.taxii_password,onChange:T,placeholder:"Password"})]})]}),t.jsxs("div",{className:"modal-footer",children:[t.jsx("button",{type:"button",className:"btn btn-outline",onClick:le,children:"Cancel"}),t.jsxs("button",{type:"submit",className:"btn btn-primary",children:[t.jsx("i",{className:"fas fa-plus"})," Add Feed"]})]})]})]})}),Ke&&t.jsx("div",{className:"modal-overlay",onClick:P,children:t.jsxs("div",{className:"modal-content delete-modal",onClick:k=>k.stopPropagation(),children:[t.jsxs("div",{className:"modal-header",children:[t.jsxs("h2",{children:[t.jsx("i",{className:"fas fa-exclamation-triangle",style:{color:"#dc3545"}}),"Delete Threat Feed"]}),t.jsx("button",{className:"modal-close",onClick:P,children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsx("div",{className:"modal-body",children:t.jsxs("div",{className:"delete-confirmation",children:[t.jsxs("p",{children:["Are you sure you want to delete the threat feed ",t.jsxs("strong",{children:['"',De==null?void 0:De.name,'"']}),"?"]}),t.jsxs("div",{className:"warning-text",children:[t.jsx("i",{className:"fas fa-warning"}),t.jsx("span",{children:"This action cannot be undone. All associated indicators and TTP data will also be removed."})]}),De&&t.jsxs("div",{className:"feed-info",children:[t.jsxs("div",{className:"info-row",children:[t.jsx("strong",{children:"Type:"})," ",De.is_external?"External TAXII":"Internal"]}),t.jsxs("div",{className:"info-row",children:[t.jsx("strong",{children:"Collection:"})," ",De.taxii_collection_id||"N/A"]}),t.jsxs("div",{className:"info-row",children:[t.jsx("strong",{children:"Last Sync:"})," ",De.last_sync?new Date(De.last_sync).toLocaleString():"Never"]})]})]})}),t.jsx("div",{className:"modal-footer",children:t.jsxs("div",{className:"modal-actions",children:[t.jsx("button",{type:"button",className:"btn btn-outline",onClick:P,disabled:je,children:"Cancel"}),t.jsx("button",{type:"button",className:"btn btn-danger",onClick:ne,disabled:je,children:je?t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Deleting..."]}):t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-trash"})," Delete Feed"]})})]})})]})})]})}function Q_({active:n}){if(!n)return null;const[i,l]=w.useState([]),[o,u]=w.useState([]),[f,m]=w.useState(!1),[x,p]=w.useState(!1),[h,v]=w.useState({type:"",value:"",severity:"Medium",description:"",source:"",confidence:50,threatFeed:"",createNewFeed:!1,newFeedName:"",newFeedDescription:""}),[y,N]=w.useState({}),[S,A]=w.useState(!1),[z,U]=w.useState(!1),[oe,ie]=w.useState("csv"),[me,Ae]=w.useState(!1),[de,pe]=w.useState(!1),[W,Ke]=w.useState(null),[he,De]=w.useState("auto"),[xe,je]=w.useState(!1),[ze,we]=w.useState([]),[Ze,L]=w.useState(!1),[ne,P]=w.useState(!1),[Ue,T]=w.useState(null),[F,le]=w.useState({type:"",value:"",description:"",confidence:50,threat_feed_id:"",threatFeedMode:"existing"}),[ce,fe]=w.useState({}),[Oe,ve]=w.useState(!1),[ke,$e]=w.useState(""),[re,k]=w.useState(""),[se,V]=w.useState(!1),[ue,Se]=w.useState(null),[Fe,it]=w.useState({institutions:[],anonymizationLevel:"medium",shareMethod:"taxii"}),[et,Gt]=w.useState(!1),[wt,Tt]=w.useState(""),[It,Kt]=w.useState(!1),[G,Te]=w.useState(-1),[Be,Ne]=w.useState("existing"),[Re,xt]=w.useState(""),[ft,B]=w.useState(!1),[Ce,M]=w.useState([]),Q=["University of Pretoria","Cyber Security Hub","SANReN CSIRT","SABRIC","University of Johannesburg","University of Cape Town","University of the Witwatersrand","Stellenbosch University","Rhodes University","North-West University","University of KwaZulu-Natal","University of the Free State","Nelson Mandela University","University of Limpopo","Walter Sisulu University","Vaal University of Technology","Central University of Technology","Durban University of Technology","Cape Peninsula University of Technology","Tshwane University of Technology","CSIR","Council for Scientific and Industrial Research","South African Police Service","State Security Agency","Department of Communications","SITA (State Information Technology Agency)","Nedbank","Standard Bank","First National Bank","ABSA Bank","Capitec Bank","African Bank","Investec"],[$,ye]=w.useState({type:"",severity:"",status:"",source:"",dateRange:"",searchTerm:""}),[Ge,tt]=w.useState(1),[ae,Ot]=w.useState(20),[_t,_e]=w.useState(0),[We,D]=w.useState(1),[ee,at]=w.useState(!1);w.useEffect(()=>{n&&(ht(),jt())},[n]),w.useEffect(()=>{function _(Y){It&&!Y.target.closest(".institution-search-container")&&(Kt(!1),Te(-1))}return document.addEventListener("mousedown",_),()=>{document.removeEventListener("mousedown",_)}},[It]);const jt=async()=>{const _=await dt.get("/api/threat-feeds/");_&&_.results&&M(_.results)};w.useEffect(()=>{kt()},[i,$,Ge,ae]);const ht=async()=>{m(!0);try{const _=await dt.get("/api/threat-feeds/");if(_&&_.results){let Y=[],Z=0;for(const be of _.results){const Ve=await dt.get(`/api/threat-feeds/${be.id}/status/`);if(Ve&&Ve.indicator_count>0){Z+=Ve.indicator_count;let qe=1,$t=!0;for(;$t;){const Zt=await dt.get(`/api/threat-feeds/${be.id}/indicators/?page=${qe}&page_size=100`);if(Zt&&Zt.results&&Zt.results.length>0){const Sa=Zt.results.map(b=>({id:b.id,type:b.type==="ip"?"IP Address":b.type==="domain"?"Domain":b.type==="url"?"URL":b.type==="file_hash"?"File Hash":b.type==="email"?"Email":b.type==="user_agent"?"User Agent":b.type==="registry"?"Registry Key":b.type==="mutex"?"Mutex":b.type==="process"?"Process":b.type,rawType:b.type,title:b.name||"",value:b.value,severity:b.confidence>=75?"High":b.confidence>=50?"Medium":"Low",confidence:b.confidence,source:b.source||be.name||"Unknown",description:b.description||"",created:new Date(b.created_at).toISOString().split("T")[0],createdDate:new Date(b.created_at),status:b.is_anonymized?"Anonymized":"Active",feedId:be.id,feedName:be.name}));Y.push(...Sa),$t=Zt.next!==null,qe++}else $t=!1}}}Y.sort((be,Ve)=>Ve.createdDate-be.createdDate),l(Y),_e(Y.length),console.log(`Loaded ${Y.length} indicators from ${_.results.length} feeds`)}}catch(_){console.error("Error fetching indicators:",_)}m(!1)},kt=()=>{let _=[...i];if($.type&&(_=_.filter(Y=>Y.rawType===$.type)),$.severity&&(_=_.filter(Y=>Y.severity.toLowerCase()===$.severity.toLowerCase())),$.status&&(_=_.filter(Y=>Y.status.toLowerCase()===$.status.toLowerCase())),$.source&&(_=_.filter(Y=>Y.source.toLowerCase().includes($.source.toLowerCase()))),$.searchTerm){const Y=$.searchTerm.toLowerCase();_=_.filter(Z=>Z.value.toLowerCase().includes(Y)||Z.description.toLowerCase().includes(Y)||Z.title&&Z.title.toLowerCase().includes(Y)||Z.name&&Z.name.toLowerCase().includes(Y))}if($.dateRange){const Y=new Date;let Z;switch($.dateRange){case"today":Z=new Date(Y.getFullYear(),Y.getMonth(),Y.getDate());break;case"week":Z=new Date(Y.getTime()-10080*60*1e3);break;case"month":Z=new Date(Y.getTime()-720*60*60*1e3);break;case"quarter":Z=new Date(Y.getTime()-2160*60*60*1e3);break;default:Z=null}Z&&(_=_.filter(be=>be.createdDate>=Z))}u(_),D(Math.ceil(_.length/ae)),Ge>Math.ceil(_.length/ae)&&tt(1)},vt=(_,Y)=>{ye(Z=>({...Z,[_]:Y})),tt(1)},St=()=>{ye({type:"",severity:"",status:"",source:"",dateRange:"",searchTerm:""}),tt(1)},Ee=()=>{const _=(Ge-1)*ae,Y=_+ae;return o.slice(_,Y)},Pe=_=>{_>=1&&_<=We&&tt(_)},Wt=()=>{ht()};return t.jsxs("section",{id:"ioc-management",className:`page-section ${n?"active":""}`,children:[t.jsxs("div",{className:"page-header",children:[t.jsxs("div",{children:[t.jsx("h1",{className:"page-title",children:"IoC Management"}),t.jsx("p",{className:"page-subtitle",children:"Manage and analyze indicators of compromise"})]}),t.jsxs("div",{className:"action-buttons",children:[t.jsxs("button",{className:"btn btn-outline",onClick:()=>U(!0),children:[t.jsx("i",{className:"fas fa-file-export"})," Export IoCs"]}),t.jsxs("button",{className:"btn btn-outline",onClick:()=>pe(!0),children:[t.jsx("i",{className:"fas fa-file-import"})," Import IoCs"]}),t.jsxs("button",{className:"btn btn-primary",onClick:()=>p(!0),children:[t.jsx("i",{className:"fas fa-plus"})," Add New IoC"]})]})]}),t.jsxs("div",{className:"filters-section",children:[t.jsxs("div",{className:"filters-header",children:[t.jsxs("h3",{children:[t.jsx("i",{className:"fas fa-filter"})," Filter & Search IoCs"]}),t.jsxs("div",{className:"filter-actions",children:[Object.values($).some(_=>_!=="")&&t.jsxs("button",{className:"btn btn-secondary btn-sm",onClick:St,title:"Clear all active filters",children:[t.jsx("i",{className:"fas fa-times"})," Clear Filters"]}),t.jsx("div",{className:"results-summary",children:Object.values($).some(_=>_!=="")?t.jsxs("span",{className:"filtered-count",children:[t.jsx("strong",{children:o.length})," of ",t.jsx("strong",{children:i.length})," indicators match"]}):t.jsxs("span",{className:"total-count",children:[t.jsx("strong",{children:i.length})," total indicators"]})})]})]}),t.jsxs("div",{className:"filters-grid",children:[t.jsxs("div",{className:"filter-group",children:[t.jsx("label",{className:"filter-label",children:"Search"}),t.jsx("div",{className:"filter-control",children:t.jsx("input",{type:"text",placeholder:"Search by value or description...",value:$.searchTerm,onChange:_=>vt("searchTerm",_.target.value),className:"form-control"})})]}),t.jsxs("div",{className:"filter-group",children:[t.jsx("label",{className:"filter-label",children:"IoC Type"}),t.jsx("div",{className:"filter-control",children:t.jsxs("select",{value:$.type,onChange:_=>vt("type",_.target.value),className:"form-control",children:[t.jsx("option",{value:"",children:"All Types"}),t.jsx("option",{value:"ip",children:"IP Address"}),t.jsx("option",{value:"domain",children:"Domain"}),t.jsx("option",{value:"url",children:"URL"}),t.jsx("option",{value:"file_hash",children:"File Hash"}),t.jsx("option",{value:"email",children:"Email"}),t.jsx("option",{value:"user_agent",children:"User Agent"}),t.jsx("option",{value:"registry",children:"Registry Key"}),t.jsx("option",{value:"mutex",children:"Mutex"}),t.jsx("option",{value:"process",children:"Process"})]})})]}),t.jsxs("div",{className:"filter-group",children:[t.jsx("label",{className:"filter-label",children:"Severity"}),t.jsx("div",{className:"filter-control",children:t.jsxs("select",{value:$.severity,onChange:_=>vt("severity",_.target.value),className:"form-control",children:[t.jsx("option",{value:"",children:"All Severities"}),t.jsx("option",{value:"high",children:"High"}),t.jsx("option",{value:"medium",children:"Medium"}),t.jsx("option",{value:"low",children:"Low"})]})})]}),t.jsxs("div",{className:"filter-group",children:[t.jsx("label",{className:"filter-label",children:"Status"}),t.jsx("div",{className:"filter-control",children:t.jsxs("select",{value:$.status,onChange:_=>vt("status",_.target.value),className:"form-control",children:[t.jsx("option",{value:"",children:"All Statuses"}),t.jsx("option",{value:"active",children:"Active"}),t.jsx("option",{value:"anonymized",children:"Anonymized"}),t.jsx("option",{value:"inactive",children:"Inactive"}),t.jsx("option",{value:"review",children:"Under Review"})]})})]}),t.jsxs("div",{className:"filter-group",children:[t.jsx("label",{className:"filter-label",children:"Source"}),t.jsx("div",{className:"filter-control",children:t.jsx("input",{type:"text",placeholder:"Filter by source...",value:$.source,onChange:_=>vt("source",_.target.value),className:"form-control"})})]}),t.jsxs("div",{className:"filter-group",children:[t.jsx("label",{className:"filter-label",children:"Date Range"}),t.jsx("div",{className:"filter-control",children:t.jsxs("select",{value:$.dateRange,onChange:_=>vt("dateRange",_.target.value),className:"form-control",children:[t.jsx("option",{value:"",children:"All Time"}),t.jsx("option",{value:"today",children:"Today"}),t.jsx("option",{value:"week",children:"Last Week"}),t.jsx("option",{value:"month",children:"Last Month"}),t.jsx("option",{value:"quarter",children:"Last Quarter"})]})})]})]})]}),t.jsxs("div",{className:"card",children:[t.jsxs("div",{className:"card-header",children:[t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-search card-icon"})," Indicators of Compromise"]}),t.jsxs("div",{className:"card-actions",children:[t.jsxs("div",{className:"items-per-page-selector",style:{display:"flex",alignItems:"center",gap:"0.5rem",marginRight:"1rem"},children:[t.jsx("label",{htmlFor:"itemsPerPage",style:{fontSize:"0.75rem",color:"#666",whiteSpace:"nowrap"},children:"Show:"}),t.jsxs("select",{id:"itemsPerPage",value:ae,onChange:_=>{Ot(Number(_.target.value)),tt(1)},className:"form-control form-control-sm",style:{height:"32px",fontSize:"0.875rem",padding:"0.25rem 0.5rem",minWidth:"100px",borderRadius:"4px",border:"1px solid #ccc"},children:[t.jsx("option",{value:10,children:"10 per page"}),t.jsx("option",{value:20,children:"20 per page"}),t.jsx("option",{value:50,children:"50 per page"}),t.jsx("option",{value:100,children:"100 per page"})]})]}),t.jsxs("button",{className:"btn btn-outline btn-sm",onClick:Wt,disabled:f,style:{height:"32px",fontSize:"0.875rem",padding:"0.25rem 0.75rem",display:"flex",alignItems:"center",gap:"0.4rem",borderRadius:"4px",lineHeight:"1",minHeight:"32px",maxHeight:"32px"},children:[t.jsx("i",{className:`fas fa-sync-alt ${f?"fa-spin":""}`}),f?"Refreshing...":"Refresh"]})]})]}),t.jsx("div",{className:"card-content",children:t.jsx("div",{className:"table-responsive",children:t.jsxs("table",{className:"data-table",children:[t.jsx("thead",{children:t.jsxs("tr",{children:[t.jsx("th",{children:t.jsx("input",{type:"checkbox"})}),t.jsx("th",{children:"Type"}),t.jsx("th",{children:"Title"}),t.jsx("th",{children:"Value"}),t.jsx("th",{children:"Description"}),t.jsx("th",{children:"Severity"}),t.jsx("th",{children:"Source"}),t.jsx("th",{children:"Date Added"}),t.jsx("th",{children:"Status"}),t.jsx("th",{children:"Actions"})]})}),t.jsx("tbody",{children:f?t.jsx("tr",{children:t.jsxs("td",{colSpan:"10",style:{textAlign:"center",padding:"2rem"},children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Loading indicators..."]})}):Ee().length>0?Ee().map(_=>t.jsxs("tr",{children:[t.jsx("td",{children:t.jsx("input",{type:"checkbox"})}),t.jsx("td",{children:t.jsx("span",{className:`type-badge type-${_.rawType}`,children:_.type})}),t.jsx("td",{className:"indicator-title",title:_.title||"",children:_.title?_.title.length>30?`${_.title.substring(0,30)}...`:_.title:t.jsx("em",{className:"text-muted",children:"No title"})}),t.jsx("td",{className:"indicator-value",title:_.value,children:_.value.length>50?`${_.value.substring(0,50)}...`:_.value}),t.jsx("td",{className:"indicator-description",title:_.description||"",children:_.description?_.description.length>40?`${_.description.substring(0,40)}...`:_.description:t.jsx("em",{className:"text-muted",children:"No description"})}),t.jsx("td",{children:t.jsx("span",{className:`badge badge-${_.severity.toLowerCase()}`,children:_.severity})}),t.jsx("td",{children:_.source}),t.jsx("td",{children:_.created}),t.jsx("td",{children:t.jsx("span",{className:`badge badge-${_.status.toLowerCase()}`,children:_.status})}),t.jsxs("td",{children:[t.jsx("button",{className:"btn btn-outline btn-sm",title:"Edit Indicator",onClick:()=>va(_),children:t.jsx("i",{className:"fas fa-edit"})}),t.jsx("button",{className:"btn btn-outline btn-sm",title:"Share Indicator",onClick:()=>Ja(_),children:t.jsx("i",{className:"fas fa-share-alt"})})]})]},_.id)):o.length===0&&i.length>0?t.jsx("tr",{children:t.jsxs("td",{colSpan:"10",style:{textAlign:"center",padding:"2rem"},children:[t.jsx("i",{className:"fas fa-filter"})," No indicators match the current filters.",t.jsx("br",{}),t.jsxs("button",{className:"btn btn-outline btn-sm mt-2",onClick:St,children:[t.jsx("i",{className:"fas fa-times"})," Clear Filters"]})]})}):t.jsx("tr",{children:t.jsxs("td",{colSpan:"10",style:{textAlign:"center",padding:"2rem"},children:[t.jsx("i",{className:"fas fa-info-circle"})," No indicators found. Try consuming threat feeds to populate data."]})})})]})})})]}),t.jsxs("div",{className:"pagination-wrapper",style:{margin:"2rem auto",display:"flex",flexDirection:"column",gap:"1rem",padding:"1.5rem",background:"#f8f9fa",borderRadius:"8px",border:"1px solid #dee2e6",maxWidth:"fit-content",width:"auto",textAlign:"center"},children:[t.jsx("div",{className:"pagination-info-detailed",children:t.jsxs("span",{className:"pagination-summary",children:["Showing ",t.jsx("strong",{children:Math.min((Ge-1)*ae+1,o.length)})," to ",t.jsx("strong",{children:Math.min(Ge*ae,o.length)})," of ",t.jsx("strong",{children:o.length}),Object.values($).some(_=>_!=="")?" filtered":""," indicators"]})}),We>1&&t.jsxs("div",{className:"pagination-controls-enhanced",style:{display:"flex",justifyContent:"center",alignItems:"center",gap:"0.5rem",flexWrap:"nowrap",overflowX:"auto",padding:"0.5rem",margin:"0 auto",width:"fit-content"},children:[t.jsx("button",{className:"btn btn-outline btn-sm",onClick:()=>Pe(1),disabled:Ge===1,title:"First page",children:t.jsx("i",{className:"fas fa-angle-double-left"})}),t.jsx("button",{className:"btn btn-outline btn-sm",onClick:()=>Pe(Ge-1),disabled:Ge===1,title:"Previous page",children:t.jsx("i",{className:"fas fa-angle-left"})}),(()=>{const _=[],Y=Math.max(1,Ge-2),Z=Math.min(We,Ge+2);Y>1&&(_.push(t.jsx("button",{className:"btn btn-outline btn-sm",onClick:()=>Pe(1),children:"1"},1)),Y>2&&_.push(t.jsx("span",{className:"pagination-ellipsis",children:"..."},"ellipsis1")));for(let be=Y;be<=Z;be++)_.push(t.jsx("button",{className:`btn btn-sm ${be===Ge?"btn-primary":"btn-outline"}`,onClick:()=>Pe(be),children:be},be));return Z<We&&(Z<We-1&&_.push(t.jsx("span",{className:"pagination-ellipsis",children:"..."},"ellipsis2")),_.push(t.jsx("button",{className:"btn btn-outline btn-sm",onClick:()=>Pe(We),children:We},We))),_})(),t.jsx("button",{className:"btn btn-outline btn-sm",onClick:()=>Pe(Ge+1),disabled:Ge===We,title:"Next page",children:t.jsx("i",{className:"fas fa-angle-right"})}),t.jsx("button",{className:"btn btn-outline btn-sm",onClick:()=>Pe(We),disabled:Ge===We,title:"Last page",children:t.jsx("i",{className:"fas fa-angle-double-right"})})]})]}),t.jsxs("div",{className:"card mt-4",children:[t.jsx("div",{className:"card-header",children:t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-chart-pie card-icon"})," IoC Statistics"]})}),t.jsx("div",{className:"card-content",children:t.jsxs("div",{className:"stats-grid",children:[t.jsxs("div",{className:"stat-card",children:[t.jsxs("div",{className:"stat-title",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-search"})}),t.jsxs("span",{children:["Total IoCs",Object.values($).some(_=>_!=="")?" (Filtered)":""]})]}),t.jsx("div",{className:"stat-value",children:Object.values($).some(_=>_!=="")?o.length:i.length}),t.jsx("div",{className:"stat-description",children:Object.values($).some(_=>_!=="")?`${o.length} of ${i.length} match filters`:"All indicators in system"})]}),t.jsxs("div",{className:"stat-card",children:[t.jsxs("div",{className:"stat-title",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-exclamation-triangle"})}),t.jsx("span",{children:"High Severity"})]}),t.jsx("div",{className:"stat-value",children:(Object.values($).some(_=>_!=="")?o:i).filter(_=>_.severity.toLowerCase()==="high").length}),t.jsx("div",{className:"stat-description",children:"Critical threat indicators"})]}),t.jsxs("div",{className:"stat-card",children:[t.jsxs("div",{className:"stat-title",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-user-secret"})}),t.jsx("span",{children:"Anonymized"})]}),t.jsx("div",{className:"stat-value",children:(Object.values($).some(_=>_!=="")?o:i).filter(_=>_.status.toLowerCase()==="anonymized").length}),t.jsx("div",{className:"stat-description",children:"Privacy-protected IoCs"})]}),t.jsxs("div",{className:"stat-card",children:[t.jsxs("div",{className:"stat-title",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-chart-line"})}),t.jsx("span",{children:"Active"})]}),t.jsx("div",{className:"stat-value",children:(Object.values($).some(_=>_!=="")?o:i).filter(_=>_.status.toLowerCase()==="active").length}),t.jsx("div",{className:"stat-description",children:"Currently monitored IoCs"})]})]})})]}),x&&t.jsx("div",{className:"modal-overlay",onClick:Et,children:t.jsxs("div",{className:"modal-content",onClick:_=>_.stopPropagation(),children:[t.jsxs("div",{className:"modal-header",children:[t.jsxs("h2",{children:[t.jsx("i",{className:"fas fa-plus"})," Add New IoC"]}),t.jsx("button",{className:"modal-close",onClick:Et,children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsx("div",{className:"modal-body",children:t.jsxs("form",{onSubmit:Ts,children:[t.jsxs("div",{className:"form-grid",children:[t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"IoC Type *"}),t.jsxs("select",{value:h.type,onChange:_=>v({...h,type:_.target.value}),className:y.type?"form-control error":"form-control",required:!0,children:[t.jsx("option",{value:"",children:"Select Type"}),t.jsx("option",{value:"ip",children:"IP Address"}),t.jsx("option",{value:"domain",children:"Domain"}),t.jsx("option",{value:"url",children:"URL"}),t.jsx("option",{value:"file_hash",children:"File Hash"}),t.jsx("option",{value:"email",children:"Email"}),t.jsx("option",{value:"user_agent",children:"User Agent"}),t.jsx("option",{value:"registry",children:"Registry Key"}),t.jsx("option",{value:"mutex",children:"Mutex"}),t.jsx("option",{value:"process",children:"Process"})]}),y.type&&t.jsx("span",{className:"error-text",children:y.type})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"Severity"}),t.jsxs("select",{value:h.severity,onChange:_=>v({...h,severity:_.target.value}),className:"form-control",children:[t.jsx("option",{value:"Low",children:"Low"}),t.jsx("option",{value:"Medium",children:"Medium"}),t.jsx("option",{value:"High",children:"High"})]})]})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"IoC Value *"}),t.jsx("input",{type:"text",value:h.value,onChange:_=>v({...h,value:_.target.value}),className:y.value?"form-control error":"form-control",placeholder:"Enter the indicator value (e.g., 192.168.1.1, malicious.com, etc.)",required:!0}),y.value&&t.jsx("span",{className:"error-text",children:y.value})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"Source"}),t.jsx("input",{type:"text",value:h.source,onChange:_=>v({...h,source:_.target.value}),className:"form-control",placeholder:"Source of this IoC (e.g., Internal Analysis, OSINT, etc.)"})]}),t.jsxs("div",{className:"form-group",children:[t.jsxs("label",{className:"form-label",children:["Confidence Level: ",h.confidence,"%"]}),t.jsx("input",{type:"range",min:"0",max:"100",value:h.confidence,onChange:_=>v({...h,confidence:parseInt(_.target.value)}),className:"form-range"}),t.jsxs("div",{className:"range-labels",children:[t.jsx("span",{children:"Low (0%)"}),t.jsx("span",{children:"High (100%)"})]})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"Description"}),t.jsx("textarea",{value:h.description,onChange:_=>v({...h,description:_.target.value}),className:"form-control",rows:"3",placeholder:"Additional notes or description about this IoC..."})]}),t.jsxs("div",{className:"modal-actions",children:[t.jsx("button",{type:"button",className:"btn btn-outline",onClick:Et,disabled:S,children:"Cancel"}),t.jsx("button",{type:"submit",className:"btn btn-primary",disabled:S,children:S?t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Adding..."]}):t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-plus"})," Add IoC"]})})]})]})})]})}),z&&t.jsx("div",{className:"modal-overlay",onClick:qt,children:t.jsxs("div",{className:"modal-content",onClick:_=>_.stopPropagation(),children:[t.jsxs("div",{className:"modal-header",children:[t.jsxs("h2",{children:[t.jsx("i",{className:"fas fa-file-export"})," Export IoCs"]}),t.jsx("button",{className:"modal-close",onClick:qt,children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsxs("div",{className:"modal-body",children:[t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"Export Format"}),t.jsxs("select",{value:oe,onChange:_=>ie(_.target.value),className:"form-control",children:[t.jsx("option",{value:"csv",children:"CSV (Comma Separated Values)"}),t.jsx("option",{value:"json",children:"JSON (JavaScript Object Notation)"}),t.jsx("option",{value:"stix",children:"STIX 2.1 (Structured Threat Information)"})]})]}),t.jsx("div",{className:"export-info",children:t.jsxs("div",{className:"info-card",children:[t.jsx("i",{className:"fas fa-info-circle"}),t.jsxs("div",{children:[t.jsx("strong",{children:"Export Details:"}),t.jsxs("p",{children:["You are about to export ",i.length," indicators of compromise."]}),oe==="csv"&&t.jsxs("p",{children:[t.jsx("strong",{children:"CSV Format:"})," Suitable for spreadsheet analysis. Includes all indicator fields in tabular format."]}),oe==="json"&&t.jsxs("p",{children:[t.jsx("strong",{children:"JSON Format:"})," Machine-readable format suitable for programmatic processing and API integration."]}),oe==="stix"&&t.jsxs("p",{children:[t.jsx("strong",{children:"STIX 2.1 Format:"})," Industry-standard format for threat intelligence sharing. Compatible with TAXII servers."]})]})]})}),t.jsxs("div",{className:"modal-actions",children:[t.jsx("button",{type:"button",className:"btn btn-outline",onClick:qt,disabled:me,children:"Cancel"}),t.jsx("button",{type:"button",className:"btn btn-primary",onClick:Jn,disabled:me,children:me?t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Exporting..."]}):t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-download"})," Export ",i.length," IoCs"]})})]})]})]})}),de&&t.jsx("div",{className:"modal-overlay",onClick:ka,children:t.jsxs("div",{className:"modal-content",onClick:_=>_.stopPropagation(),children:[t.jsxs("div",{className:"modal-header",children:[t.jsxs("h2",{children:[t.jsx("i",{className:"fas fa-file-import"})," Import IoCs"]}),t.jsx("button",{className:"modal-close",onClick:ka,children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsx("div",{className:"modal-body",children:Ze?t.jsxs(t.Fragment,{children:[t.jsxs("div",{className:"preview-header",children:[t.jsx("h3",{children:"Import Preview"}),t.jsxs("p",{children:["Review ",ze.length," indicators before importing:"]})]}),t.jsxs("div",{className:"preview-table-container",children:[t.jsxs("table",{className:"preview-table",children:[t.jsx("thead",{children:t.jsxs("tr",{children:[t.jsx("th",{children:"Type"}),t.jsx("th",{children:"Title"}),t.jsx("th",{children:"Value"}),t.jsx("th",{children:"Description"}),t.jsx("th",{children:"Severity"}),t.jsx("th",{children:"Source"}),t.jsx("th",{children:"Status"})]})}),t.jsx("tbody",{children:ze.slice(0,10).map((_,Y)=>{var Z;return t.jsxs("tr",{children:[t.jsx("td",{children:_.type}),t.jsx("td",{className:"truncate",title:_.name||"",children:_.name||t.jsx("em",{children:"No title"})}),t.jsx("td",{className:"truncate",children:_.value}),t.jsx("td",{className:"truncate",title:_.description||"",children:_.description||t.jsx("em",{children:"No description"})}),t.jsx("td",{children:t.jsx("span",{className:`badge badge-${(Z=_.severity)==null?void 0:Z.toLowerCase()}`,children:_.severity})}),t.jsx("td",{children:_.source}),t.jsx("td",{children:_.status})]},Y)})})]}),ze.length>10&&t.jsxs("p",{className:"preview-note",children:["... and ",ze.length-10," more indicators"]})]}),t.jsxs("div",{className:"modal-actions",children:[t.jsxs("button",{type:"button",className:"btn btn-outline",onClick:Qa,disabled:xe,children:[t.jsx("i",{className:"fas fa-arrow-left"})," Back"]}),t.jsx("button",{type:"button",className:"btn btn-primary",onClick:ra,disabled:xe,children:xe?t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Importing..."]}):t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-upload"})," Import ",ze.length," IoCs"]})})]})]}):t.jsxs(t.Fragment,{children:[t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"Import Format"}),t.jsxs("select",{value:he,onChange:_=>De(_.target.value),className:"form-control",children:[t.jsx("option",{value:"auto",children:"Auto-detect from file"}),t.jsx("option",{value:"csv",children:"CSV (Comma Separated Values)"}),t.jsx("option",{value:"json",children:"JSON (JavaScript Object Notation)"}),t.jsx("option",{value:"stix",children:"STIX 2.1 (Structured Threat Information)"})]})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"Select File"}),t.jsxs("div",{className:"file-upload-area",onDrop:xa,onDragOver:ut,children:[t.jsx("input",{type:"file",accept:".csv,.json",onChange:pt,className:"file-input",id:"import-file"}),t.jsxs("label",{htmlFor:"import-file",className:"file-upload-label",children:[t.jsx("i",{className:"fas fa-cloud-upload-alt"}),t.jsx("span",{children:W?W.name:"Drop file here or click to browse"}),t.jsx("small",{children:"Supported formats: CSV, JSON, STIX (.json)"})]})]})]}),t.jsx("div",{className:"import-info",children:t.jsxs("div",{className:"info-card",children:[t.jsx("i",{className:"fas fa-info-circle"}),t.jsxs("div",{children:[t.jsx("strong",{children:"Import Guidelines:"}),t.jsxs("ul",{children:[t.jsxs("li",{children:[t.jsx("strong",{children:"CSV:"})," Must include headers: Type, Value, Severity, Source, Status"]}),t.jsxs("li",{children:[t.jsx("strong",{children:"JSON:"})," Should match the export format structure"]}),t.jsxs("li",{children:[t.jsx("strong",{children:"STIX:"})," Must be valid STIX 2.1 bundle format"]}),t.jsx("li",{children:"Duplicate indicators will be skipped automatically"})]})]})]})}),t.jsxs("div",{className:"modal-actions",children:[t.jsx("button",{type:"button",className:"btn btn-outline",onClick:ka,disabled:xe,children:"Cancel"}),t.jsx("button",{type:"button",className:"btn btn-primary",onClick:_a,disabled:!W||xe,children:xe?t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Processing..."]}):t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-eye"})," Preview Import"]})})]})]})})]})}),ne&&t.jsx("div",{className:"modal-overlay",onClick:ln,children:t.jsxs("div",{className:"modal-content",onClick:_=>_.stopPropagation(),children:[t.jsxs("div",{className:"modal-header",children:[t.jsxs("h2",{children:[t.jsx("i",{className:"fas fa-edit"})," Edit IoC"]}),t.jsx("button",{className:"modal-close",onClick:ln,children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsx("div",{className:"modal-body",children:t.jsxs("form",{onSubmit:ei,children:[t.jsxs("div",{className:"form-grid",children:[t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"IoC Type *"}),t.jsxs("select",{value:F.type,onChange:_=>le({...F,type:_.target.value}),className:ce.type?"form-control error":"form-control",required:!0,children:[t.jsx("option",{value:"",children:"Select Type"}),t.jsx("option",{value:"ip",children:"IP Address"}),t.jsx("option",{value:"domain",children:"Domain"}),t.jsx("option",{value:"url",children:"URL"}),t.jsx("option",{value:"file_hash",children:"File Hash"}),t.jsx("option",{value:"email",children:"Email"}),t.jsx("option",{value:"user_agent",children:"User Agent"}),t.jsx("option",{value:"registry",children:"Registry Key"}),t.jsx("option",{value:"mutex",children:"Mutex"}),t.jsx("option",{value:"process",children:"Process"})]}),ce.type&&t.jsx("span",{className:"error-text",children:ce.type})]}),t.jsxs("div",{className:"form-group",children:[t.jsxs("label",{className:"form-label",children:["Confidence Level: ",F.confidence,"%"]}),t.jsx("input",{type:"range",min:"0",max:"100",value:F.confidence,onChange:_=>le({...F,confidence:parseInt(_.target.value)}),className:"form-range"}),t.jsxs("div",{className:"range-labels",children:[t.jsx("span",{children:"Low (0%)"}),t.jsx("span",{children:"High (100%)"})]})]})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"IoC Value *"}),t.jsx("input",{type:"text",value:F.value,onChange:_=>le({...F,value:_.target.value}),className:ce.value?"form-control error":"form-control",placeholder:"Enter IoC value (IP, domain, hash, etc.)",required:!0}),ce.value&&t.jsx("span",{className:"error-text",children:ce.value})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"Description"}),t.jsx("textarea",{value:F.description,onChange:_=>le({...F,description:_.target.value}),className:"form-control",placeholder:"Optional description or notes",rows:"3"})]}),ce.submit&&t.jsxs("div",{className:"error-message",children:[t.jsx("i",{className:"fas fa-exclamation-triangle"}),ce.submit]}),t.jsxs("div",{className:"modal-actions",children:[t.jsx("button",{type:"button",className:"btn btn-outline",onClick:ln,disabled:Oe,children:"Cancel"}),t.jsx("button",{type:"submit",className:"btn btn-primary",disabled:Oe,children:Oe?t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Updating..."]}):t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-save"})," Update IoC"]})})]})]})})]})}),se&&t.jsx("div",{className:"modal-overlay",onClick:kn,children:t.jsxs("div",{className:"modal-content",onClick:_=>_.stopPropagation(),children:[t.jsxs("div",{className:"modal-header",children:[t.jsxs("h2",{children:[t.jsx("i",{className:"fas fa-share-alt"})," Share IoC"]}),t.jsx("button",{className:"modal-close",onClick:kn,children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsx("div",{className:"modal-body",children:t.jsxs("form",{onSubmit:Ft,children:[t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"IoC Details"}),t.jsxs("div",{className:"info-box",children:[t.jsxs("p",{children:[t.jsx("strong",{children:"Type:"})," ",ue==null?void 0:ue.type]}),t.jsxs("p",{children:[t.jsx("strong",{children:"Value:"})," ",ue==null?void 0:ue.value]}),t.jsxs("p",{children:[t.jsx("strong",{children:"Source:"})," ",ue==null?void 0:ue.source]})]})]}),t.jsxs("div",{className:"form-group",children:[t.jsxs("label",{className:"form-label",children:[t.jsx("i",{className:"fas fa-share-nodes form-icon"}),"Target Organizations"]}),t.jsx("p",{className:"form-description",children:"Select trusted institutions to share this threat intelligence with"}),t.jsxs("div",{className:"sleek-org-selector",children:[t.jsxs("div",{className:"search-field",children:[t.jsx("input",{type:"text",className:"sleek-search-input",value:Re,onChange:_=>{xt(_.target.value),B(!0)},onFocus:()=>B(!0),onBlur:_=>{setTimeout(()=>{(!_.relatedTarget||!_.relatedTarget.closest(".results-list"))&&B(!1)},200)},placeholder:"Type to search organizations..."}),t.jsx("i",{className:"fas fa-search search-icon"})]}),ft&&Re&&t.jsxs("div",{className:"results-list",children:[Q.filter(_=>!Fe.institutions.includes(_)&&_.toLowerCase().includes(Re.toLowerCase())).slice(0,5).map(_=>t.jsxs("div",{className:"result-item",onClick:()=>{En(_),xt(""),B(!1)},children:[t.jsx("span",{className:"result-name",children:_}),t.jsx("i",{className:"fas fa-plus add-icon"})]},_)),Q.filter(_=>!Fe.institutions.includes(_)&&_.toLowerCase().includes(Re.toLowerCase())).length===0&&t.jsx("div",{className:"no-results",children:"No organizations found"})]}),Fe.institutions.length>0&&t.jsxs("div",{className:"selected-orgs",children:[t.jsxs("div",{className:"selected-label",children:["Selected (",Fe.institutions.length,")"]}),t.jsx("div",{className:"org-tags",children:Fe.institutions.map(_=>t.jsxs("div",{className:"org-tag",children:[t.jsx("span",{children:_}),t.jsx("button",{type:"button",className:"remove-tag",onClick:()=>ts(_),children:"×"})]},_))})]})]})]}),t.jsxs("div",{className:"form-grid",children:[t.jsxs("div",{className:"form-group",children:[t.jsxs("label",{className:"form-label",children:[t.jsx("i",{className:"fas fa-user-secret form-icon"}),"Anonymization Level"]}),t.jsx("p",{className:"form-description",children:"Choose how much detail to share with receiving organizations"}),t.jsxs("select",{value:Fe.anonymizationLevel,onChange:_=>it({...Fe,anonymizationLevel:_.target.value}),className:"form-control enhanced-select multiline-select",children:[t.jsx("option",{value:"none",children:"None - Full Details Complete IoC values and metadata shared"}),t.jsx("option",{value:"low",children:"Low - Minor Obfuscation Remove source identifiers and timestamps"}),t.jsx("option",{value:"medium",children:"Medium - Partial Anonymization Generalize IPs/domains (evil.com → *.com)"}),t.jsx("option",{value:"high",children:"High - Strong Anonymization Only patterns and techniques, no indicators"})]})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{className:"form-label",children:"Share Method"}),t.jsxs("select",{value:Fe.shareMethod,onChange:_=>it({...Fe,shareMethod:_.target.value}),className:"form-control",children:[t.jsx("option",{value:"taxii",children:"TAXII 2.1 Protocol"}),t.jsx("option",{value:"email",children:"Email Export"}),t.jsx("option",{value:"api",children:"Direct API Push"})]})]})]}),t.jsxs("div",{className:"modal-actions",children:[t.jsx("button",{type:"button",className:"btn btn-outline",onClick:kn,disabled:et,children:"Cancel"}),t.jsx("button",{type:"submit",className:"btn btn-primary",disabled:et||Fe.institutions.length===0,children:et?t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Sharing..."]}):t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-share-alt"})," Share with ",Fe.institutions.length," Institution(s)"]})})]})]})})]})})]});function Et(){p(!1),v({type:"",value:"",severity:"Medium",description:"",source:"",confidence:50,threatFeed:"",createNewFeed:!1,newFeedName:"",newFeedDescription:""}),N({})}function qt(){U(!1),ie("csv")}async function Jn(){if(i.length===0){alert("No indicators to export");return}Ae(!0);try{let _,Y,Z;switch(oe){case"csv":_=Pt(i),Y=`iocs_export_${new Date().toISOString().split("T")[0]}.csv`,Z="text/csv";break;case"json":_=da(i),Y=`iocs_export_${new Date().toISOString().split("T")[0]}.json`,Z="application/json";break;case"stix":_=Za(i),Y=`iocs_export_${new Date().toISOString().split("T")[0]}.json`,Z="application/json";break;default:throw new Error("Unsupported export format")}const be=new Blob([_],{type:Z}),Ve=window.URL.createObjectURL(be),qe=document.createElement("a");qe.href=Ve,qe.download=Y,document.body.appendChild(qe),qe.click(),document.body.removeChild(qe),window.URL.revokeObjectURL(Ve),qt(),console.log(`Successfully exported ${i.length} IoCs as ${oe.toUpperCase()}`)}catch(_){console.error("Export failed:",_),alert("Export failed. Please try again.")}finally{Ae(!1)}}function Pt(_){const Z=["Type","Value","Severity","Source","Date Added","Status"].join(","),be=_.map(Ve=>[`"${Ve.type}"`,`"${Ve.value}"`,`"${Ve.severity}"`,`"${Ve.source}"`,`"${Ve.created}"`,`"${Ve.status}"`].join(","));return[Z,...be].join(`
`)}function da(_){const Y={export_date:new Date().toISOString(),total_indicators:_.length,indicators:_.map(Z=>({id:Z.id,type:Z.type,value:Z.value,severity:Z.severity,source:Z.source,created:Z.created,status:Z.status}))};return JSON.stringify(Y,null,2)}function Za(_){const Y={type:"bundle",id:`bundle--${Da()}`,spec_version:"2.1",created:new Date().toISOString(),modified:new Date().toISOString(),objects:_.map(Z=>({type:"indicator",id:`indicator--${Da()}`,created:new Date(Z.created).toISOString(),modified:new Date().toISOString(),labels:["malicious-activity"],pattern:Ha(Z),indicator_types:["malicious-activity"],confidence:ia(Z.severity),x_crisp_source:Z.source,x_crisp_severity:Z.severity,x_crisp_status:Z.status}))};return JSON.stringify(Y,null,2)}function Da(){return"xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g,function(_){const Y=Math.random()*16|0;return(_=="x"?Y:Y&3|8).toString(16)})}function Ha(_){switch(_.type.toLowerCase()){case"ip address":return`[ipv4-addr:value = '${_.value}']`;case"domain":return`[domain-name:value = '${_.value}']`;case"url":return`[url:value = '${_.value}']`;case"file hash":return`[file:hashes.MD5 = '${_.value}' OR file:hashes.SHA1 = '${_.value}' OR file:hashes.SHA256 = '${_.value}']`;case"email":return`[email-addr:value = '${_.value}']`;default:return`[x-custom:value = '${_.value}']`}}function ia(_){switch(_.toLowerCase()){case"high":return 85;case"medium":return 60;case"low":return 30;default:return 50}}function ka(){pe(!1),Ke(null),De("auto"),we([]),L(!1)}function pt(_){const Y=_.target.files[0];Ke(Y)}function xa(_){_.preventDefault();const Y=_.dataTransfer.files[0];Y&&(Y.type==="text/csv"||Y.type==="application/json"||Y.name.endsWith(".csv")||Y.name.endsWith(".json"))&&Ke(Y)}function ut(_){_.preventDefault()}async function _a(){if(W){je(!0);try{const _=await Wn(W);console.log(`File hash (SHA-256): ${_}`);const Y=await Kn(W);$i(W,Y);const Z=he==="auto"?Sn(W.name,Y):he,be=await es(Y,Z),Ve={name:W.name,size:W.size,type:W.type,hash:_,lastModified:new Date(W.lastModified).toISOString(),detectedFormat:Z,recordCount:be.length};console.log("File security validation passed:",Ve),we(be),L(!0)}catch(_){console.error("File validation failed:",_),alert(`Security validation failed: ${_.message}`)}finally{je(!1)}}}function Qa(){L(!1),we([])}async function ra(){if(ze.length!==0){je(!0);try{const _=ze.map(Z=>({type:Z.rawType||Z.type.toLowerCase().replace(" ","_"),value:Z.value.trim(),name:Z.name||"",description:Z.description||"",confidence:parseInt(Z.confidence)||50})),Y=await dt.post("/api/indicators/bulk-import/",{indicators:_});if(Y&&Y.success){const Z=Y.created_indicators.map(qe=>({...qe,rawType:qe.type,title:qe.name||"",type:qe.type==="ip"?"IP Address":qe.type==="domain"?"Domain":qe.type==="url"?"URL":qe.type==="file_hash"?"File Hash":qe.type==="email"?"Email":qe.type,severity:"Medium",status:"Active",created:qe.created_at?qe.created_at.split("T")[0]:new Date().toISOString().split("T")[0]}));l(qe=>[...Z,...qe]),ka();const be=`Import completed! Added ${Y.created_count} new indicators.`,Ve=Y.error_count>0?` ${Y.error_count} errors occurred.`:"";console.log(`${be}${Ve}`,Y.errors),alert(`${be}${Ve}`)}else throw new Error("Bulk import failed")}catch(_){console.error("Import failed:",_),alert("Import failed. Please try again.")}finally{je(!1)}}}function Kn(_){return new Promise((Y,Z)=>{const be=new FileReader;be.onload=Ve=>Y(Ve.target.result),be.onerror=()=>Z(new Error("Failed to read file")),be.readAsText(_)})}async function Wn(_){return new Promise((Y,Z)=>{const be=new FileReader;be.onload=async Ve=>{try{const qe=Ve.target.result,$t=await crypto.subtle.digest("SHA-256",qe),Sa=Array.from(new Uint8Array($t)).map(b=>b.toString(16).padStart(2,"0")).join("");Y(Sa)}catch(qe){Z(qe)}},be.onerror=()=>Z(new Error("Failed to read file for hashing")),be.readAsArrayBuffer(_)})}function $i(_,Y){const Z=_.name.toLowerCase(),be=10*1024*1024;if(_.size>be)throw new Error("File size exceeds 10MB limit");const Ve={csv:{extensions:[".csv"],mimeTypes:["text/csv","application/csv","text/plain"],maxSize:5*1024*1024,contentValidation:Zt=>{const Sa=Zt.split(`
`).filter(K=>K.trim());if(Sa.length<2)return!1;const b=Sa[0];return b.includes(",")&&b.split(",").length>=2}},json:{extensions:[".json"],mimeTypes:["application/json","text/json"],maxSize:5*1024*1024,contentValidation:Zt=>{try{const Sa=JSON.parse(Zt);return typeof Sa=="object"&&Sa!==null}catch{return!1}}},txt:{extensions:[".txt"],mimeTypes:["text/plain"],maxSize:2*1024*1024,contentValidation:Zt=>![/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,/<iframe\b[^>]*>/gi,/javascript:/gi,/on\w+\s*=/gi].some(b=>b.test(Zt))}},qe=Z.substring(Z.lastIndexOf(".")),$t=Object.values(Ve).find(Zt=>Zt.extensions.includes(qe));if(!$t)throw new Error(`Unsupported file type: ${qe}. Allowed types: CSV, JSON, TXT`);if(!$t.mimeTypes.includes(_.type)&&_.type!==""&&console.warn(`MIME type mismatch: expected ${$t.mimeTypes.join("/")}, got ${_.type}`),_.size>$t.maxSize)throw new Error(`File size exceeds limit for ${qe.substring(1).toUpperCase()} files (${$t.maxSize/1024/1024}MB)`);if(!$t.contentValidation(Y))throw new Error(`Invalid ${qe.substring(1).toUpperCase()} file format or content`);return!0}function Sn(_,Y){if(_.endsWith(".csv"))return"csv";if(_.endsWith(".json"))try{const Z=JSON.parse(Y);return Z.type==="bundle"&&Z.objects?"stix":"json"}catch{return"json"}return"csv"}async function es(_,Y){switch(Y){case"csv":return Ra(_);case"json":return Tn(_);case"stix":return Cn(_);default:throw new Error("Unsupported file format")}}function Ra(_){const Y=_.trim().split(`
`);if(Y.length<2)throw new Error("CSV file must have headers and at least one data row");const Z=Y[0].split(",").map(Ve=>Ve.replace(/"/g,"").trim().toLowerCase()),be=[];for(let Ve=1;Ve<Y.length;Ve++){const qe=Y[Ve].split(",").map(Zt=>Zt.replace(/"/g,"").trim()),$t={type:ua(Z,qe,["type","ioc_type","indicator_type"])||"Unknown",value:ua(Z,qe,["value","ioc_value","indicator"])||"",name:ua(Z,qe,["name","title","indicator_name"])||"",description:ua(Z,qe,["description","desc","details"])||"",severity:ua(Z,qe,["severity","priority","threat_level"])||"Medium",source:ua(Z,qe,["source","origin","feed"])||"Import",status:ua(Z,qe,["status","state"])||"Active"};$t.value&&be.push($t)}return be}function Tn(_){const Y=JSON.parse(_);if(Y.indicators&&Array.isArray(Y.indicators))return Y.indicators.map(Z=>({type:Z.type||"Unknown",value:Z.value||"",name:Z.name||"",description:Z.description||"",severity:Z.severity||"Medium",source:Z.source||"Import",status:Z.status||"Active"}));if(Array.isArray(Y))return Y.map(Z=>({type:Z.type||"Unknown",value:Z.value||"",name:Z.name||"",description:Z.description||"",severity:Z.severity||"Medium",source:Z.source||"Import",status:Z.status||"Active"}));throw new Error("Invalid JSON format. Expected array or object with indicators property.")}function Cn(_){const Y=JSON.parse(_);if(Y.type!=="bundle"||!Y.objects)throw new Error("Invalid STIX format. Expected bundle with objects.");return Y.objects.filter(be=>be.type==="indicator").map(be=>({type:An(be.pattern),value:zn(be.pattern),name:be.name||"",description:be.description||"",severity:Ss(be.confidence||50),source:be.x_crisp_source||"STIX Import",status:be.x_crisp_status||"Active"}))}function ua(_,Y,Z){for(const be of Z){const Ve=_.indexOf(be);if(Ve!==-1&&Y[Ve])return Y[Ve]}return null}function An(_){return _.includes("ipv4-addr")?"IP Address":_.includes("domain-name")?"Domain":_.includes("url")?"URL":_.includes("file:hashes")?"File Hash":_.includes("email-addr")?"Email":"Unknown"}function zn(_){const Y=_.match(/'([^']+)'/);return Y?Y[1]:""}function Ss(_){return _>=75?"High":_>=45?"Medium":"Low"}function Ws(){const _={};if(h.type||(_.type="IoC type is required"),!h.value.trim())_.value="IoC value is required";else{const Y=h.value.trim();switch(h.type){case"ip":/^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(Y)||(_.value="Invalid IP address format");break;case"domain":/^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$/.test(Y)||(_.value="Invalid domain format");break;case"url":try{new URL(Y)}catch{_.value="Invalid URL format"}break;case"email":/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(Y)||(_.value="Invalid email format");break;case"file_hash":(!/^[a-fA-F0-9]+$/.test(Y)||![32,40,64,128].includes(Y.length))&&(_.value="Invalid hash format (MD5, SHA1, SHA256, or SHA512)");break}}return _}function va(_){T(_),le({type:_.rawType||_.type.toLowerCase().replace(" ","_"),value:_.value,description:_.description||"",confidence:_.confidence||50,threat_feed_id:_.feedId||"",threatFeedMode:"existing"}),$e(""),k(""),fe({}),P(!0)}function ln(){P(!1),T(null),le({type:"",value:"",description:"",confidence:50,threat_feed_id:"",threatFeedMode:"existing"}),$e(""),k(""),fe({})}async function ei(_){if(_.preventDefault(),!!Ue){ve(!0),fe({});try{let Y=F.threat_feed_id;if(F.threatFeedMode==="new"&&ke.trim())try{const Ve={name:ke.trim(),description:re.trim()||"",is_external:!1,is_active:!0},qe=await dt.post("/api/threat-feeds/",Ve);qe&&qe.id&&(Y=qe.id,M($t=>[...$t,qe]))}catch(Ve){console.error("Error creating new threat feed:",Ve),fe({submit:"Failed to create new threat feed. Please try again."});return}const Z={type:F.type,value:F.value.trim(),description:F.description||"",confidence:parseInt(F.confidence)||50,threat_feed_id:Y},be=await dt.put(`/api/indicators/${Ue.id}/update/`,Z);if(be){const Ve={...be,rawType:be.type,type:be.type==="ip"?"IP Address":be.type==="domain"?"Domain":be.type==="url"?"URL":be.type==="file_hash"?"File Hash":be.type==="email"?"Email":be.type,severity:Ue.severity,status:Ue.status,created:be.created_at?be.created_at.split("T")[0]:Ue.created};l(qe=>qe.map($t=>$t.id===Ue.id?Ve:$t)),ln(),alert("Indicator updated successfully!")}else throw new Error("Failed to update indicator")}catch(Y){console.error("Error updating indicator:",Y),fe({submit:"Failed to update indicator. Please try again."})}finally{ve(!1)}}}function Ja(_){Se(_),it({institutions:[],anonymizationLevel:"medium",shareMethod:"taxii"}),V(!0)}function kn(){V(!1),Se(null),it({institutions:[],anonymizationLevel:"medium",shareMethod:"taxii"}),Tt(""),Kt(!1),Te(-1)}function En(_){it(Y=>({...Y,institutions:[...Y.institutions,_]})),Tt(""),Kt(!1),Te(-1)}function ts(_){it(Y=>({...Y,institutions:Y.institutions.filter(Z=>Z!==_)}))}async function Ft(_){if(_.preventDefault(),!ue||Fe.institutions.length===0){alert("Please select at least one institution to share with.");return}Gt(!0);try{const Y={institutions:Fe.institutions,anonymization_level:Fe.anonymizationLevel,share_method:Fe.shareMethod},Z=await dt.post(`/api/indicators/${ue.id}/share/`,Y);if(Z&&Z.success)kn(),alert(`Indicator shared with ${Z.shared_with} institution(s) successfully!`);else throw new Error("Failed to share indicator")}catch(Y){console.error("Error sharing indicator:",Y),alert("Failed to share indicator. Please try again.")}finally{Gt(!1)}}async function Ts(_){_.preventDefault();const Y=Ws();if(Object.keys(Y).length>0){N(Y);return}A(!0),N({});try{const Z={type:h.type,value:h.value.trim(),description:h.description||"",confidence:parseInt(h.confidence)||50},be=await dt.post("/api/indicators/",Z);if(be){const Ve={...be,rawType:be.type,title:be.name||"",type:be.type==="ip"?"IP Address":be.type==="domain"?"Domain":be.type==="url"?"URL":be.type==="file_hash"?"File Hash":be.type==="email"?"Email":be.type,severity:h.severity||"Medium",status:"Active",created:be.created_at?be.created_at.split("T")[0]:new Date().toISOString().split("T")[0]};l(qe=>[Ve,...qe]),Et(),console.log("IoC added successfully:",be),alert("IoC added successfully!")}else throw new Error("Failed to create indicator")}catch(Z){console.error("Error adding IoC:",Z),N({submit:"Failed to add IoC. Please try again."})}finally{A(!1)}}}function J_({active:n}){var $t,Zt,Sa;if(!n)return null;const[i,l]=w.useState([]),[o,u]=w.useState([]),[f,m]=w.useState(null),[x,p]=w.useState(!1),[h,v]=w.useState(!1),[y,N]=w.useState(!1),[S,A]=w.useState("overview"),[z,U]=w.useState(null),[oe,ie]=w.useState(null),[me,Ae]=w.useState(null),[de,pe]=w.useState(!1),[W,Ke]=w.useState("created_at"),[he,De]=w.useState("desc"),[xe,je]=w.useState(1),[ze,we]=w.useState(20),[Ze,L]=w.useState(0),[ne,P]=w.useState(0),[Ue,T]=w.useState(!1),[F,le]=w.useState(!1),[ce,fe]=w.useState(!1),[Oe,ve]=w.useState(null),[ke,$e]=w.useState({search:"",tactics:[],techniques:[],severity_levels:[],date_from:"",date_to:"",threat_feed_ids:[],anonymized_only:"",has_subtechniques:""}),[re,k]=w.useState(0),[se,V]=w.useState(!1),[ue,Se]=w.useState(null),[Fe,it]=w.useState(!1),[et,Gt]=w.useState(!1),[wt,Tt]=w.useState({}),[It,Kt]=w.useState([]),[G,Te]=w.useState(""),[Be,Ne]=w.useState(!1),[Re,xt]=w.useState(""),[ft,B]=w.useState(!1),[Ce,M]=w.useState("json"),[Q,$]=w.useState({tactic:"",technique_id:"",feed_id:"",include_anonymized:!0,include_original:!1,created_after:"",created_before:"",limit:1e3,fields:""}),[ye,Ge]=w.useState(!1),[tt,ae]=w.useState(""),[Ot,_t]=w.useState(!1),[_e,We]=w.useState(null),[D,ee]=w.useState(!1),[at,jt]=w.useState(""),[ht,kt]=w.useState(""),[vt,St]=w.useState(!1),[Ee,Pe]=w.useState(null),[Wt,Et]=w.useState(!1),[qt,Jn]=w.useState(""),Pt=w.useRef(null);w.useEffect(()=>{n&&(ia(),Tn(),ka(),da(),Za())},[n]);const da=async()=>{try{const b=await dt.get("/api/threat-feeds/");b&&b.results?Kt(b.results):(console.log("No threat feeds found or invalid response:",b),Kt([]))}catch(b){console.error("Error fetching available feeds:",b),Kt([])}},Za=async()=>{pe(!0);try{const b=dt.get("/api/ttps/feed-comparison/?days=30").catch(nt=>(console.warn("Feed comparison endpoint not available:",nt),null)),K=dt.get("/api/ttps/technique-frequencies/?days=30").catch(nt=>(console.warn("Technique frequencies endpoint not available:",nt),null)),ge=dt.get("/api/ttps/seasonal-patterns/?days=180").catch(nt=>(console.warn("Seasonal patterns endpoint not available:",nt),null)),[Me,Qe,Ie]=await Promise.all([b,K,ge]);Me&&Me.success&&U(Me),Qe&&Qe.success&&ie(Qe),Ie&&Ie.success&&Ae(Ie)}catch(b){console.error("Error fetching aggregation data:",b)}pe(!1)},Da=async()=>{if(!G){alert("Please select a threat feed to analyze");return}Ne(!0),xt("Loading TTPs from feed...");try{const b=It.find(ge=>ge.id==G),K=b?b.name:"Selected Feed";await Ha(G,K)}catch(b){console.error("Error loading feed TTPs:",b),xt(`❌ Failed to load TTPs: ${b.message||"Unknown error"}`),setTimeout(()=>{xt("")},1e4)}finally{Ne(!1)}},Ha=async(b,K)=>{let ge=[],Me=1,Qe=!0;const Ie=100;for(;Qe;)try{const nt=await dt.get(`/api/threat-feeds/${b}/ttps/?page=${Me}&page_size=${Ie}`);nt&&nt.results?(ge=[...ge,...nt.results],xt(`Loading TTPs from "${K}"... (${ge.length} loaded)`),Qe=nt.next!==null,Me++):Qe=!1}catch(nt){throw console.error(`Error loading page ${Me} of TTPs:`,nt),Qe=!1,nt}l(ge),L(ge.length),xt(`✅ Loaded ${ge.length} TTPs from "${K}"`),Tn(),Za(),setTimeout(()=>{xt("")},5e3)},ia=async(b=null,K=null,ge=null,Me=null,Qe=null)=>{p(!0);try{const Ie=b||W,nt=K||he,ya=ge||xe,Ta=Me||ze,gt=Qe||ke,Vt=new URLSearchParams;Vt.append("sort_by",Ie),Vt.append("sort_order",nt),Vt.append("page",ya.toString()),Vt.append("page_size",Ta.toString()),gt.search&&gt.search.trim()&&Vt.append("search",gt.search.trim()),gt.tactics&&gt.tactics.length>0&&Vt.append("tactics",gt.tactics.join(",")),gt.techniques&&gt.techniques.length>0&&Vt.append("techniques",gt.techniques.join(",")),gt.severity_levels&&gt.severity_levels.length>0&&Vt.append("severity_levels",gt.severity_levels.join(",")),gt.date_from&&gt.date_from.trim()&&Vt.append("created_after",gt.date_from.trim()),gt.date_to&&gt.date_to.trim()&&Vt.append("created_before",gt.date_to.trim()),gt.threat_feed_ids&&gt.threat_feed_ids.length>0&&Vt.append("threat_feed_ids",gt.threat_feed_ids.join(",")),gt.anonymized_only&&gt.anonymized_only!==""&&Vt.append("anonymized_only",gt.anonymized_only),gt.has_subtechniques&&gt.has_subtechniques!==""&&Vt.append("has_subtechniques",gt.has_subtechniques);const Ca=await dt.get(`/api/ttps/?${Vt.toString()}`);Ca&&Ca.success?(l(Ca.results||[]),L(Ca.count||0),P(Ca.num_pages||0),T(Ca.has_next||!1),le(Ca.has_previous||!1)):(l([]),L(0),P(0),T(!1),le(!1))}catch(Ie){console.error("Error fetching TTP data:",Ie),l([]),L(0),P(0),T(!1),le(!1)}p(!1)},ka=async()=>{try{const b=await dt.get("/api/ttps/filter-options/");b&&b.success&&ve(b.options)}catch(b){console.error("Error fetching filter options:",b)}},pt=b=>{let K="asc";W===b?K=he==="asc"?"desc":"asc":K=b==="created_at"||b==="updated_at"?"desc":"asc",Ke(b),De(K),je(1),ia(b,K,1,ze,ke)},xa=b=>{if(W!==b)return t.jsx("i",{className:"fas fa-sort",style:{color:"#ccc",marginLeft:"5px"}});const K=he==="asc"?"fa-sort-up":"fa-sort-down";return t.jsx("i",{className:`fas ${K}`,style:{color:"#0056b3",marginLeft:"5px"}})},ut=b=>{b>=1&&b<=ne&&b!==xe&&(je(b),ia(W,he,b,ze,ke))},_a=b=>{we(b),je(1),ia(W,he,1,b,ke)},Qa=()=>{const b=[];if(ne<=5)for(let ge=1;ge<=ne;ge++)b.push(ge);else{const ge=Math.max(1,xe-2),Me=Math.min(ne,xe+2);ge>1&&(b.push(1),ge>2&&b.push("..."));for(let Qe=ge;Qe<=Me;Qe++)b.push(Qe);Me<ne&&(Me<ne-1&&b.push("..."),b.push(ne))}return b},ra=(b,K)=>{const ge={...ke,[b]:K};$e(ge),je(1);const Me=Sn(ge);k(Me),b==="search"?Kn(W,he,1,ze,ge):ia(W,he,1,ze,ge)},Kn=w.useRef(Wn((b,K,ge,Me,Qe)=>{ia(b,K,ge,Me,Qe)},500)).current;function Wn(b,K){let ge;return function(...Qe){const Ie=()=>{clearTimeout(ge),b(...Qe)};clearTimeout(ge),ge=setTimeout(Ie,K)}}const $i=(b,K,ge)=>{const Me=ke[b]||[];let Qe;ge?Qe=[...Me,K]:Qe=Me.filter(Ie=>Ie!==K),ra(b,Qe)},Sn=b=>{let K=0;return b.search&&b.search.trim()&&K++,b.tactics&&b.tactics.length>0&&K++,b.techniques&&b.techniques.length>0&&K++,b.severity_levels&&b.severity_levels.length>0&&K++,b.date_from&&b.date_from.trim()&&K++,b.date_to&&b.date_to.trim()&&K++,b.threat_feed_ids&&b.threat_feed_ids.length>0&&K++,b.anonymized_only&&b.anonymized_only!==""&&K++,b.has_subtechniques&&b.has_subtechniques!==""&&K++,K},es=()=>{const b={search:"",tactics:[],techniques:[],severity_levels:[],date_from:"",date_to:"",threat_feed_ids:[],anonymized_only:"",has_subtechniques:""};$e(b),k(0),je(1),ia(W,he,1,ze,b)},Ra=async()=>{v(!0);try{const b=await dt.get("/api/ttps/trends/?days=120&granularity=month&group_by=tactic");b&&b.series?u(b.series):u([])}catch(b){console.error("Error fetching TTP trends data:",b),u([])}v(!1)},Tn=async()=>{N(!0);try{const b=await dt.get("/api/ttps/mitre-matrix/");b&&b.success?m(b):m(null)}catch(b){console.error("Error fetching MITRE matrix data:",b),m(null)}N(!1)},Cn=b=>{A(b)},ua=async(b,K=null)=>{jt(b),kt(K||""),ee(!0),_t(!0);try{let ge=`/api/ttps/matrix-cell-details/?tactic=${b}`;K&&(ge+=`&technique_id=${K}`),ge+="&include_related=true&page_size=50";const Me=await dt.get(ge);Me&&Me.success?We(Me):We(null)}catch(ge){console.error("Error fetching matrix cell details:",ge),We(null)}ee(!1)},An=async b=>{Jn(b),Et(!0),St(!0);try{const K=`/api/ttps/technique-details/${b}/`,ge=await dt.get(K);ge&&ge.success?Pe(ge):Pe(null)}catch(K){console.error("Error fetching technique details:",K),Pe(null)}Et(!1)},zn=()=>{_t(!1),We(null),jt(""),kt("")},Ss=()=>{St(!1),Pe(null),Jn("")},Ws=()=>{Tn()},va=async b=>{var K;V(!0),it(!0),Gt(!1);try{const ge=await dt.get(`/api/ttps/${b}/`);ge&&ge.success?(Se(ge.ttp),Tt({name:ge.ttp.name||"",description:ge.ttp.description||"",mitre_technique_id:ge.ttp.mitre_technique_id||"",mitre_tactic:ge.ttp.mitre_tactic||"",mitre_subtechnique:ge.ttp.mitre_subtechnique||"",threat_feed_id:((K=ge.ttp.threat_feed)==null?void 0:K.id)||""})):(console.error("Failed to fetch TTP details"),Se(null))}catch(ge){console.error("Error fetching TTP details:",ge),Se(null)}it(!1)},ln=()=>{V(!1),Se(null),Gt(!1),Tt({})},ei=()=>{Gt(!et)},Ja=(b,K)=>{Tt(ge=>({...ge,[b]:K}))},kn=async()=>{if(ue)try{const b=await dt.put(`/api/ttps/${ue.id}/`,wt);b&&b.success?(l(K=>K.map(ge=>ge.id===ue.id?{...ge,...wt}:ge)),Se({...ue,...wt}),Gt(!1),alert("TTP updated successfully"),Ra()):alert("Failed to update TTP")}catch(b){console.error("Error updating TTP:",b),alert("Error updating TTP: "+(b.message||"Unknown error"))}},En=()=>{B(!0),ae("")},ts=()=>{B(!1),ae("")},Ft=(b,K)=>{$(ge=>({...ge,[b]:K}))},Ts=(b,K)=>{const ge=window.URL.createObjectURL(b),Me=document.createElement("a");Me.href=ge,Me.download=K,document.body.appendChild(Me),Me.click(),document.body.removeChild(Me),window.URL.revokeObjectURL(ge)},_=async()=>{Ge(!0),ae("");try{const b=new URLSearchParams;b.append("format",Ce),Q.tactic&&b.append("tactic",Q.tactic),Q.technique_id&&b.append("technique_id",Q.technique_id),Q.feed_id&&b.append("feed_id",Q.feed_id),Q.created_after&&b.append("created_after",Q.created_after),Q.created_before&&b.append("created_before",Q.created_before),Q.fields&&b.append("fields",Q.fields),b.append("include_anonymized",Q.include_anonymized.toString()),b.append("include_original",Q.include_original.toString()),b.append("limit",Q.limit.toString());const K=await fetch(`/api/ttps/export/?${b.toString()}`,{method:"GET",headers:{Accept:Ce==="csv"?"text/csv":Ce==="stix"?"application/stix+json":"application/json"}});if(!K.ok)throw new Error(`Export failed: ${K.status} ${K.statusText}`);const ge=await K.blob(),Me=K.headers.get("Content-Disposition");let Qe=`ttps_export_${new Date().toISOString().slice(0,19).replace(/:/g,"-")}.${Ce}`;if(Me){const Ie=Me.match(/filename="([^"]+)"/);Ie&&(Qe=Ie[1])}Ts(ge,Qe),ts(),alert(`Export completed successfully! Downloaded: ${Qe}`)}catch(b){console.error("Export failed:",b),ae("Export failed: "+(b.message||"Unknown error"))}Ge(!1)},Y=()=>{if(!f||!f.matrix)return null;const b=[{code:"initial-access",name:"Initial Access"},{code:"execution",name:"Execution"},{code:"persistence",name:"Persistence"},{code:"privilege-escalation",name:"Privilege Escalation"},{code:"defense-evasion",name:"Defense Evasion"},{code:"credential-access",name:"Credential Access"},{code:"discovery",name:"Discovery"},{code:"lateral-movement",name:"Lateral Movement"},{code:"collection",name:"Collection"},{code:"exfiltration",name:"Exfiltration"},{code:"impact",name:"Impact"}];return t.jsx("thead",{children:t.jsx("tr",{children:b.map(K=>{const ge=f.matrix[K.code],Me=ge?ge.technique_count:0;return t.jsxs("th",{title:`${Me} techniques in ${K.name} - Click to view details`,onClick:()=>Me>0&&ua(K.code),style:{cursor:Me>0?"pointer":"default",backgroundColor:Me>0?"#f8f9fa":"transparent",transition:"background-color 0.2s ease"},onMouseEnter:Qe=>{Me>0&&(Qe.target.style.backgroundColor="#e9ecef")},onMouseLeave:Qe=>{Me>0&&(Qe.target.style.backgroundColor="#f8f9fa")},children:[K.name,t.jsxs("div",{className:"tactic-count",children:["(",Me,")"]})]},K.code)})})})},Z=()=>{if(!f||!f.matrix)return null;Object.values(f.matrix);const b=["initial-access","execution","persistence","privilege-escalation","defense-evasion","credential-access","discovery","lateral-movement","collection","exfiltration","impact"],K=5,ge=[];for(let Me=0;Me<K;Me++){const Qe=[];b.forEach(Ie=>{const nt=f.matrix[Ie];if(nt&&nt.techniques&&nt.techniques.length>Me){const ya=nt.techniques[Me];Qe.push({technique:ya,hasData:!0,isActive:nt.technique_count>0})}else Qe.push({technique:null,hasData:!1,isActive:!1})}),Qe.some(Ie=>Ie.hasData)&&ge.push(Qe)}return t.jsx("tbody",{children:ge.map((Me,Qe)=>t.jsx("tr",{children:Me.map((Ie,nt)=>{const ya=b[nt];return t.jsx("td",{className:`matrix-cell ${Ie.isActive?"active":""} ${Ie.technique?"clickable":""}`,title:Ie.technique?`${Ie.technique.name} (${Ie.technique.technique_id}) - Click to view details`:"No techniques",onClick:()=>{Ie.technique?An(Ie.technique.technique_id):Ie.isActive&&ya&&ua(ya)},style:{cursor:Ie.technique||Ie.isActive?"pointer":"default",transition:"all 0.2s ease",position:"relative"},onMouseEnter:Ta=>{(Ie.technique||Ie.isActive)&&(Ta.target.style.transform="scale(1.02)",Ta.target.style.boxShadow="0 2px 8px rgba(0,0,0,0.1)",Ta.target.style.zIndex="1")},onMouseLeave:Ta=>{(Ie.technique||Ie.isActive)&&(Ta.target.style.transform="scale(1)",Ta.target.style.boxShadow="none",Ta.target.style.zIndex="auto")},children:Ie.technique?t.jsxs(t.Fragment,{children:[t.jsx("div",{className:"technique-name",children:Ie.technique.name.length>20?Ie.technique.name.substring(0,20)+"...":Ie.technique.name}),Ie.technique.technique_id&&t.jsx("div",{className:"technique-id",children:Ie.technique.technique_id})]}):t.jsx("div",{className:"empty-cell",children:Ie.isActive?"🔍":"-"})},nt)})},Qe))})},be=b=>{const K=new Map;return b.forEach(ge=>{const Me=ge.group_name?ge.group_name.toLowerCase().replace(/\s+/g,"-"):"unknown";ge.data_points.forEach(Qe=>{const Ie=Qe.date;K.has(Ie)||K.set(Ie,{date:Ie,"initial-access":0,execution:0,persistence:0,"defense-evasion":0,impact:0,"privilege-escalation":0,discovery:0,"lateral-movement":0,collection:0,"command-and-control":0,exfiltration:0});const nt=K.get(Ie);nt.hasOwnProperty(Me)&&(nt[Me]=Qe.count||0)})}),Array.from(K.values()).sort((ge,Me)=>new Date(ge.date)-new Date(Me.date))},Ve=async b=>{if(confirm("Are you sure you want to delete this TTP? This action cannot be undone."))try{const K=await dt.delete(`/api/ttps/${b}/`);K&&K.success?(l(ge=>ge.filter(Me=>Me.id!==b)),alert("TTP deleted successfully"),Ra()):alert("Failed to delete TTP")}catch(K){console.error("Error deleting TTP:",K),alert("Error deleting TTP: "+(K.message||"Unknown error"))}};w.useEffect(()=>{n&&Pt.current&&o.length>0&&qe()},[n,o]);const qe=()=>{try{if(Pt.current&&hn(Pt.current).selectAll("*").remove(),!o||o.length===0||!Pt.current)return;const b=be(o);if(!b||b.length===0){console.warn("No chart data available after transformation");return}const K=Pt.current.clientWidth,ge=300,Me={top:30,right:120,bottom:40,left:50},Qe=K-Me.left-Me.right,Ie=ge-Me.top-Me.bottom,nt=hn(Pt.current).append("svg").attr("width",K).attr("height",ge).append("g").attr("transform",`translate(${Me.left},${Me.top})`),ya=LN().domain(b.map(Bt=>Bt.date)).range([0,Qe]).padding(.5),Ta=zu().domain([0,Mg(b,Bt=>Math.max(...Object.keys(Vt).map(ba=>Bt[ba]||0)))*1.1]).range([Ie,0]),gt=Uu().x(Bt=>ya(Bt.date)).y(Bt=>Ta(Bt.value)).curve(h_),Vt={"initial-access":"#0056b3",execution:"#00a0e9",persistence:"#38a169","defense-evasion":"#e53e3e",impact:"#f6ad55","privilege-escalation":"#805ad5",discovery:"#ed8936","lateral-movement":"#38b2ac",collection:"#d53f8c","command-and-control":"#319795",exfiltration:"#dd6b20"},Ca=Object.keys(Vt).filter(Bt=>b.some(ba=>ba[Bt]>0)),on={"initial-access":"Initial Access",execution:"Execution",persistence:"Persistence","defense-evasion":"Defense Evasion",impact:"Impact","privilege-escalation":"Privilege Escalation",discovery:"Discovery","lateral-movement":"Lateral Movement",collection:"Collection","command-and-control":"Command and Control",exfiltration:"Exfiltration"};Ca.forEach(Bt=>{const ba=b.map(Ia=>({date:Ia.date,value:Ia[Bt]}));nt.append("path").datum(ba).attr("fill","none").attr("stroke",Vt[Bt]).attr("stroke-width",2).attr("d",gt),nt.selectAll(`.dot-${Bt}`).data(ba).enter().append("circle").attr("class",`dot-${Bt}`).attr("cx",Ia=>ya(Ia.date)).attr("cy",Ia=>Ta(Ia.value)).attr("r",4).attr("fill",Vt[Bt])}),nt.append("g").attr("transform",`translate(0,${Ie})`).call(nu(ya).tickFormat(Bt=>Bt)),nt.append("g").call(su(Ta)),nt.append("text").attr("x",Qe/2).attr("y",-10).attr("text-anchor","middle").style("font-size","16px").style("font-weight","600").style("fill","#2d3748").text("TTP Trends Over Time");const Fi=nt.append("g").attr("transform",`translate(${Qe+10}, 0)`);Ca.forEach((Bt,ba)=>{const Ia=Fi.append("g").attr("transform",`translate(0, ${ba*20})`);Ia.append("rect").attr("width",10).attr("height",10).attr("fill",Vt[Bt]),Ia.append("text").attr("x",15).attr("y",10).attr("text-anchor","start").style("font-size","12px").text(on[Bt])})}catch(b){console.error("Error creating TTP trends chart:",b),Pt.current&&(hn(Pt.current).selectAll("*").remove(),hn(Pt.current).append("div").style("text-align","center").style("color","#e53e3e").style("padding","20px").text("Error loading chart data. Please try refreshing."))}};return t.jsxs("section",{id:"ttp-analysis",className:`page-section ${n?"active":""}`,children:[t.jsxs("div",{className:"page-header",children:[t.jsxs("div",{children:[t.jsx("h1",{className:"page-title",children:"TTP Analysis"}),t.jsx("p",{className:"page-subtitle",children:"Track and analyze tactics, techniques, and procedures from threat intelligence feeds"})]}),t.jsxs("div",{className:"action-buttons",children:[t.jsxs("div",{className:"feed-consumption-controls",children:[t.jsxs("div",{className:"feed-selection-wrapper",children:[t.jsxs("select",{value:G,onChange:b=>Te(b.target.value),className:"form-control feed-selector",disabled:Be,children:[t.jsx("option",{value:"",children:"Select Threat Feed to Analyze"}),It.length===0?t.jsx("option",{disabled:!0,children:"No threat feeds available"}):It.map(b=>t.jsxs("option",{value:b.id,children:[b.name," - ",b.is_external?"External TAXII":"Internal",b.is_active?" ✓":" (Inactive)",b.description?` - ${b.description}`:""]},b.id))]}),G&&t.jsx("div",{className:"consumption-options",children:t.jsxs("small",{className:"consumption-info",children:[t.jsx("i",{className:"fas fa-info-circle"}),"Will show TTPs from this feed"]})})]}),t.jsx("button",{className:"btn btn-primary consume-btn",onClick:Da,disabled:!G||Be,title:G?"Load TTPs from selected feed":"Select a feed first",children:Be?t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Loading..."]}):t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-download"})," Load Feed TTPs"]})})]}),t.jsxs("button",{className:"btn btn-outline",onClick:En,children:[t.jsx("i",{className:"fas fa-upload"})," Export Analysis"]})]})]}),Re&&t.jsxs("div",{className:`alert ${Re.includes("failed")?"alert-error":"alert-success"}`,children:[t.jsx("i",{className:`fas ${Re.includes("failed")?"fa-exclamation-triangle":"fa-check-circle"}`}),Re]}),t.jsxs("div",{className:"tabs",children:[t.jsx("div",{className:`tab ${S==="overview"?"active":""}`,onClick:()=>Cn("overview"),children:"Feed Overview"}),t.jsx("div",{className:`tab ${S==="matrix"?"active":""}`,onClick:()=>Cn("matrix"),children:"MITRE ATT&CK Matrix"}),t.jsx("div",{className:`tab ${S==="list"?"active":""}`,onClick:()=>Cn("list"),children:"TTP Intelligence"}),t.jsx("div",{className:`tab ${S==="trends"?"active":""}`,onClick:()=>Cn("trends"),children:"Trends & Patterns"})]}),S==="overview"&&t.jsxs("div",{className:"feed-analysis-overview",children:[t.jsxs("div",{className:"overview-cards",children:[t.jsxs("div",{className:"card",children:[t.jsxs("div",{className:"card-header",children:[t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-chart-bar card-icon"}),"Feed Comparison Statistics"]}),t.jsxs("button",{className:"btn btn-outline btn-sm",onClick:Za,disabled:de,children:[t.jsx("i",{className:`fas ${de?"fa-spinner fa-spin":"fa-sync-alt"}`})," Refresh"]})]}),t.jsx("div",{className:"card-content",children:de?t.jsxs("div",{className:"loading-state",children:[t.jsx("i",{className:"fas fa-spinner fa-spin"}),t.jsx("p",{children:"Loading feed comparison data..."})]}):z?t.jsx("div",{className:"feed-comparison-grid",children:z.feed_statistics&&z.feed_statistics.map((b,K)=>t.jsxs("div",{className:"feed-stat-card",children:[t.jsx("div",{className:"feed-name",children:b.threat_feed__name}),t.jsxs("div",{className:"feed-stats",children:[t.jsxs("div",{className:"stat-item",children:[t.jsx("span",{className:"stat-value",children:b.ttp_count}),t.jsx("span",{className:"stat-label",children:"TTPs"})]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("span",{className:"stat-value",children:b.unique_techniques}),t.jsx("span",{className:"stat-label",children:"Unique Techniques"})]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("span",{className:"stat-value",children:b.avg_techniques_per_day}),t.jsx("span",{className:"stat-label",children:"Avg/Day"})]})]}),t.jsx("div",{className:`feed-type ${b.threat_feed__is_external?"external":"internal"}`,children:b.threat_feed__is_external?"External Feed":"Internal Feed"})]},K))}):t.jsxs("div",{className:"empty-state",children:[t.jsx("i",{className:"fas fa-chart-bar"}),t.jsx("p",{children:"No feed comparison data available"}),t.jsx("p",{className:"text-muted",children:"Consume threat feeds to see comparison statistics"})]})})]}),t.jsxs("div",{className:"card",children:[t.jsx("div",{className:"card-header",children:t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-fire card-icon"}),"Top Techniques"]})}),t.jsx("div",{className:"card-content",children:oe&&oe.techniques?t.jsx("div",{className:"technique-frequency-list",children:Object.entries(oe.techniques).sort(([,b],[,K])=>K.count-b.count).slice(0,10).map(([b,K],ge)=>t.jsxs("div",{className:"frequency-item",children:[t.jsxs("div",{className:"technique-rank",children:["#",K.rank]}),t.jsxs("div",{className:"technique-details",children:[t.jsx("div",{className:"technique-id",children:b}),t.jsxs("div",{className:"technique-stats",children:[t.jsxs("span",{className:"count",children:[K.count," occurrences"]}),t.jsxs("span",{className:"percentage",children:["(",K.percentage,"%)"]})]})]}),t.jsx("div",{className:"frequency-bar",children:t.jsx("div",{className:"frequency-fill",style:{width:`${Math.min(K.percentage*2,100)}%`}})})]},b))}):t.jsxs("div",{className:"empty-state",children:[t.jsx("i",{className:"fas fa-fire"}),t.jsx("p",{children:"No technique frequency data available"})]})})]})]}),t.jsxs("div",{className:"card",children:[t.jsx("div",{className:"card-header",children:t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-calendar-alt card-icon"}),"Seasonal Patterns"]})}),t.jsx("div",{className:"card-content",children:me&&me.statistics?t.jsxs("div",{className:"seasonal-analysis",children:[t.jsxs("div",{className:"seasonal-stats",children:[t.jsxs("div",{className:"stat-card",children:[t.jsx("div",{className:"stat-value",children:me.statistics.seasonality_strength}),t.jsx("div",{className:"stat-label",children:"Seasonality Strength"})]}),t.jsxs("div",{className:"stat-card",children:[t.jsx("div",{className:"stat-value",children:me.statistics.peak_period.label}),t.jsx("div",{className:"stat-label",children:"Peak Period"})]}),t.jsxs("div",{className:"stat-card",children:[t.jsx("div",{className:"stat-value",children:me.statistics.valley_period.label}),t.jsx("div",{className:"stat-label",children:"Valley Period"})]})]}),t.jsx("div",{className:"seasonal-interpretation",children:t.jsx("p",{children:me.interpretation})})]}):t.jsxs("div",{className:"empty-state",children:[t.jsx("i",{className:"fas fa-calendar-alt"}),t.jsx("p",{children:"No seasonal pattern data available"})]})})]})]}),S==="matrix"&&t.jsxs(t.Fragment,{children:[t.jsxs("div",{className:"card",children:[t.jsxs("div",{className:"card-header",children:[t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-sitemap card-icon"})," MITRE ATT&CK Enterprise Matrix"]}),t.jsxs("div",{className:"card-actions",children:[t.jsxs("button",{className:"btn btn-outline btn-sm",onClick:Ws,disabled:y,title:"Refresh matrix data",children:[t.jsx("i",{className:`fas ${y?"fa-spinner fa-spin":"fa-sync-alt"}`})," Refresh"]}),t.jsxs("button",{className:"btn btn-outline btn-sm",children:[t.jsx("i",{className:"fas fa-filter"})," Filter"]})]})]}),t.jsx("div",{className:"card-content",children:t.jsx("div",{className:"matrix-container",children:y?t.jsxs("div",{style:{textAlign:"center",padding:"4rem"},children:[t.jsx("i",{className:"fas fa-spinner fa-spin",style:{fontSize:"2rem",color:"#0056b3"}}),t.jsx("p",{style:{marginTop:"1rem",color:"#666"},children:"Loading MITRE ATT&CK Matrix..."})]}):f?t.jsxs(t.Fragment,{children:[t.jsxs("table",{className:"mitre-matrix",children:[Y(),Z()]}),f.statistics&&t.jsx("div",{className:"matrix-stats",style:{marginTop:"1rem",padding:"1rem",backgroundColor:"#f8f9fa",borderRadius:"8px"},children:t.jsxs("div",{style:{display:"grid",gridTemplateColumns:"repeat(auto-fit, minmax(200px, 1fr))",gap:"1rem"},children:[t.jsxs("div",{children:[t.jsx("strong",{children:"Total Techniques:"})," ",f.total_techniques]}),t.jsxs("div",{children:[t.jsx("strong",{children:"Active Tactics:"})," ",f.statistics.tactics_with_techniques]}),t.jsxs("div",{children:[t.jsx("strong",{children:"Avg per Tactic:"})," ",f.statistics.average_techniques_per_tactic]}),f.statistics.most_common_tactic&&t.jsxs("div",{children:[t.jsx("strong",{children:"Top Tactic:"})," ",($t=f.matrix[f.statistics.most_common_tactic])==null?void 0:$t.tactic_name]})]})})]}):t.jsxs("div",{style:{textAlign:"center",padding:"4rem"},children:[t.jsx("i",{className:"fas fa-sitemap",style:{fontSize:"3rem",color:"#ccc"}}),t.jsx("p",{style:{marginTop:"1rem",color:"#666"},children:"No MITRE ATT&CK data available"}),t.jsx("p",{style:{color:"#888",fontSize:"0.9rem"},children:"Matrix will populate as TTP data becomes available"})]})})})]}),t.jsxs("div",{className:"card mt-4",children:[t.jsxs("div",{className:"card-header",children:[t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-chart-line card-icon"})," TTP Trends"]}),t.jsx("div",{className:"card-actions",children:t.jsxs("button",{className:"btn btn-outline btn-sm",children:[t.jsx("i",{className:"fas fa-calendar-alt"})," Last 90 Days"]})})]}),t.jsx("div",{className:"card-content",children:t.jsx("div",{className:"chart-container",ref:Pt,children:h?t.jsxs("div",{style:{textAlign:"center",padding:"4rem"},children:[t.jsx("i",{className:"fas fa-spinner fa-spin",style:{fontSize:"2rem",color:"#0056b3"}}),t.jsx("p",{style:{marginTop:"1rem",color:"#666"},children:"Loading TTP trends data..."})]}):o.length===0?t.jsxs("div",{style:{textAlign:"center",padding:"4rem"},children:[t.jsx("i",{className:"fas fa-chart-line",style:{fontSize:"2rem",color:"#ccc"}}),t.jsx("p",{style:{marginTop:"1rem",color:"#666"},children:"No TTP trends data available"}),t.jsx("p",{style:{color:"#888",fontSize:"0.9rem"},children:"TTP data will appear here as it becomes available"})]}):null})})]})]}),S==="list"&&t.jsxs("div",{className:"card",children:[t.jsxs("div",{className:"card-header",children:[t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-shield-alt card-icon"})," TTP Intelligence from Threat Feeds"]}),t.jsxs("div",{className:"card-actions",children:[t.jsxs("button",{className:"btn btn-outline btn-sm",onClick:()=>fe(!ce),children:[t.jsx("i",{className:"fas fa-filter"})," Filter",re>0&&t.jsx("span",{className:"filter-count",children:re})]}),t.jsxs("button",{className:"btn btn-outline btn-sm",onClick:En,children:[t.jsx("i",{className:"fas fa-download"})," Export"]})]})]}),t.jsx("div",{className:"intelligence-summary",style:{padding:"1rem",backgroundColor:"#f8f9fa",borderBottom:"1px solid #dee2e6"},children:t.jsxs("div",{className:"summary-stats",children:[t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-database"}),t.jsxs("span",{children:[Ze," TTPs from threat intelligence feeds"]})]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-rss"}),t.jsxs("span",{children:[It.length," connected threat feeds"]})]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("i",{className:"fas fa-shield-alt"}),t.jsx("span",{children:"Automatically mapped to MITRE ATT&CK"})]})]})}),t.jsx("div",{className:"card-content",children:t.jsxs("table",{className:"data-table",children:[t.jsx("thead",{children:t.jsxs("tr",{children:[t.jsxs("th",{onClick:()=>pt("id"),style:{cursor:"pointer"},children:["ID ",xa("id")]}),t.jsxs("th",{onClick:()=>pt("name"),style:{cursor:"pointer"},children:["TTP Name ",xa("name")]}),t.jsxs("th",{onClick:()=>pt("mitre_technique_id"),style:{cursor:"pointer"},children:["MITRE Technique ",xa("mitre_technique_id")]}),t.jsxs("th",{onClick:()=>pt("mitre_tactic"),style:{cursor:"pointer"},children:["Tactic ",xa("mitre_tactic")]}),t.jsx("th",{children:"Source Feed"}),t.jsx("th",{children:"Intelligence Status"}),t.jsxs("th",{onClick:()=>pt("created_at"),style:{cursor:"pointer"},children:["Discovered ",xa("created_at")]}),t.jsx("th",{children:"Actions"})]})}),t.jsx("tbody",{children:x?t.jsx("tr",{children:t.jsxs("td",{colSpan:"8",style:{textAlign:"center",padding:"2rem"},children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Loading threat intelligence..."]})}):i.length>0?i.map(b=>t.jsxs("tr",{children:[t.jsx("td",{children:b.id}),t.jsx("td",{children:t.jsxs("div",{className:"ttp-name-cell",children:[t.jsx("div",{className:"ttp-title",children:b.name}),b.mitre_subtechnique&&t.jsx("div",{className:"ttp-subtechnique",children:b.mitre_subtechnique})]})}),t.jsx("td",{children:t.jsx("span",{className:"technique-badge",children:b.mitre_technique_id})}),t.jsx("td",{children:t.jsx("span",{className:"tactic-badge",children:b.mitre_tactic_display||b.mitre_tactic})}),t.jsx("td",{children:b.threat_feed?t.jsxs("div",{className:"feed-source-cell",children:[t.jsx("span",{className:"feed-name",children:b.threat_feed.name}),t.jsx("span",{className:`feed-type ${b.threat_feed.is_external?"external":"internal"}`,children:b.threat_feed.is_external?"External":"Internal"})]}):t.jsx("span",{className:"text-muted",children:"No Feed"})}),t.jsx("td",{children:t.jsx("div",{className:"intelligence-status",children:b.is_anonymized?t.jsxs("span",{className:"status-badge anonymized",children:[t.jsx("i",{className:"fas fa-mask"})," Anonymized"]}):t.jsxs("span",{className:"status-badge raw",children:[t.jsx("i",{className:"fas fa-eye"})," Raw Intel"]})})}),t.jsx("td",{children:b.created_at?new Date(b.created_at).toLocaleDateString():"Unknown"}),t.jsx("td",{children:t.jsx("button",{className:"btn btn-outline btn-sm",onClick:()=>va(b.id),title:"View Intelligence Details",style:{marginRight:"5px"},children:t.jsx("i",{className:"fas fa-search"})})})]},b.id)):t.jsx("tr",{children:t.jsx("td",{colSpan:"8",style:{textAlign:"center",padding:"2rem"},children:t.jsxs("div",{className:"empty-state",children:[t.jsx("i",{className:"fas fa-shield-alt"}),t.jsx("p",{children:"No TTP intelligence available"}),t.jsx("p",{className:"text-muted",children:"Consume threat feeds to populate TTP intelligence data"})]})})})})]})}),(ne>0||x)&&t.jsxs("div",{className:"pagination-wrapper",style:{marginTop:"1.5rem"},children:[t.jsx("div",{className:"pagination-info-detailed",children:t.jsx("span",{className:"pagination-summary",children:x?t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-spinner fa-spin",style:{marginRight:"5px"}}),"Loading TTPs..."]}):t.jsxs(t.Fragment,{children:["Showing ",t.jsx("strong",{children:Math.min((xe-1)*ze+1,Ze)})," to ",t.jsx("strong",{children:Math.min(xe*ze,Ze)})," of ",t.jsx("strong",{children:Ze})," TTPs"]})})}),ne>1&&t.jsxs("div",{className:"pagination-controls-enhanced",children:[t.jsxs("div",{className:"items-per-page-selector",style:{marginRight:"1rem"},children:[t.jsx("label",{htmlFor:"ttp-page-size",style:{fontSize:"0.85rem",marginRight:"0.5rem"},children:"Items per page:"}),t.jsxs("select",{id:"ttp-page-size",className:"form-control-sm",value:ze,onChange:b=>_a(parseInt(b.target.value)),style:{minWidth:"70px"},disabled:x,children:[t.jsx("option",{value:10,children:"10"}),t.jsx("option",{value:20,children:"20"}),t.jsx("option",{value:50,children:"50"}),t.jsx("option",{value:100,children:"100"})]})]}),t.jsx("button",{className:`btn btn-outline btn-sm ${!F||x?"disabled":""}`,onClick:()=>ut(xe-1),disabled:!F||x,style:{marginRight:"0.25rem"},children:t.jsx("i",{className:"fas fa-chevron-left"})}),t.jsx("div",{className:"pagination-pages",children:Qa().map((b,K)=>b==="..."?t.jsx("span",{className:"pagination-ellipsis",children:"..."},`ellipsis-${K}`):t.jsx("button",{className:`btn btn-sm ${b===xe?"btn-primary":"btn-outline"}`,onClick:()=>ut(b),disabled:x,children:b},b))}),t.jsx("button",{className:`btn btn-outline btn-sm ${!Ue||x?"disabled":""}`,onClick:()=>ut(xe+1),disabled:!Ue||x,style:{marginLeft:"0.25rem"},children:t.jsx("i",{className:"fas fa-chevron-right"})})]})]})]}),(S==="matrix"||S==="list")&&t.jsxs("div",{className:"card mt-4",children:[t.jsxs("div",{className:"card-header",children:[t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-chart-line card-icon"})," TTP Trends Chart"]}),t.jsx("div",{className:"card-actions",children:t.jsxs("button",{className:"btn btn-outline btn-sm",children:[t.jsx("i",{className:"fas fa-calendar-alt"})," Last 90 Days"]})})]}),t.jsx("div",{className:"card-content",children:t.jsx("div",{className:"chart-container",ref:Pt,children:h?t.jsxs("div",{style:{textAlign:"center",padding:"4rem"},children:[t.jsx("i",{className:"fas fa-spinner fa-spin",style:{fontSize:"2rem",color:"#0056b3"}}),t.jsx("p",{style:{marginTop:"1rem",color:"#666"},children:"Loading TTP trends data..."})]}):o.length===0?t.jsxs("div",{style:{textAlign:"center",padding:"4rem"},children:[t.jsx("i",{className:"fas fa-chart-line",style:{fontSize:"2rem",color:"#ccc"}}),t.jsx("p",{style:{marginTop:"1rem",color:"#666"},children:"No TTP trends data available"}),t.jsx("p",{style:{color:"#888",fontSize:"0.9rem"},children:"TTP data will appear here as it becomes available"})]}):null})})]}),S==="trends"&&t.jsx("div",{className:"trends-analysis",children:t.jsxs("div",{className:"card",children:[t.jsxs("div",{className:"card-header",children:[t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-chart-line card-icon"})," TTP Trends & Patterns"]}),t.jsxs("div",{className:"card-actions",children:[t.jsxs("select",{className:"form-control",style:{width:"auto",marginRight:"10px"},children:[t.jsx("option",{value:"30",children:"Last 30 Days"}),t.jsx("option",{value:"90",children:"Last 90 Days"}),t.jsx("option",{value:"180",children:"Last 6 Months"}),t.jsx("option",{value:"365",children:"Last Year"})]}),t.jsxs("button",{className:"btn btn-outline btn-sm",onClick:Za,disabled:de,children:[t.jsx("i",{className:`fas ${de?"fa-spinner fa-spin":"fa-sync-alt"}`})," Refresh"]})]})]}),t.jsx("div",{className:"card-content",children:de?t.jsxs("div",{className:"loading-state",children:[t.jsx("i",{className:"fas fa-spinner fa-spin"}),t.jsx("p",{children:"Loading trends analysis..."})]}):t.jsxs("div",{className:"trends-content",children:[t.jsxs("div",{className:"trend-charts-grid",children:[t.jsxs("div",{className:"chart-container",children:[t.jsx("h3",{children:"Technique Frequency Over Time"}),t.jsx("div",{className:"trend-chart",ref:Pt,style:{minHeight:"300px",width:"100%"}})]}),t.jsxs("div",{className:"tactic-distribution",children:[t.jsx("h3",{children:"Tactic Distribution"}),oe&&oe.tactics?t.jsx("div",{className:"tactic-bars",children:Object.entries(oe.tactics).sort(([,b],[,K])=>K.count-b.count).slice(0,8).map(([b,K])=>t.jsxs("div",{className:"tactic-bar-item",children:[t.jsx("div",{className:"tactic-label",children:b.replace("-"," ")}),t.jsx("div",{className:"bar-container",children:t.jsx("div",{className:"bar-fill",style:{width:`${K.percentage}%`}})}),t.jsx("div",{className:"bar-value",children:K.count})]},b))}):t.jsx("div",{className:"empty-state",children:t.jsx("p",{children:"No tactic distribution data available"})})]})]}),t.jsxs("div",{className:"trend-insights",children:[t.jsx("h3",{children:"Key Insights"}),t.jsxs("div",{className:"insights-grid",children:[t.jsxs("div",{className:"insight-card",children:[t.jsx("i",{className:"fas fa-trending-up"}),t.jsxs("div",{children:[t.jsx("h4",{children:"Emerging Techniques"}),t.jsx("p",{children:"New techniques appearing in recent threat intelligence"})]})]}),t.jsxs("div",{className:"insight-card",children:[t.jsx("i",{className:"fas fa-clock"}),t.jsxs("div",{children:[t.jsx("h4",{children:"Seasonal Patterns"}),t.jsx("p",{children:me&&me.interpretation?me.interpretation:"Analyzing temporal patterns in TTP usage"})]})]}),t.jsxs("div",{className:"insight-card",children:[t.jsx("i",{className:"fas fa-exclamation-triangle"}),t.jsxs("div",{children:[t.jsx("h4",{children:"High-Frequency TTPs"}),t.jsx("p",{children:"Most commonly observed techniques across all feeds"})]})]})]})]})]})})]})}),(S==="matrix"||S==="list")&&t.jsxs("div",{className:"card mt-4",children:[t.jsx("div",{className:"card-header",children:t.jsxs("div",{className:"filters-header",children:[t.jsxs("h2",{className:"card-title",children:[t.jsx("i",{className:"fas fa-tasks card-icon"})," Recent TTP Analyses"]}),t.jsxs("div",{className:"filter-actions",children:[x&&t.jsxs("span",{style:{fontSize:"0.85rem",color:"#6c757d"},children:[t.jsx("i",{className:"fas fa-spinner fa-spin",style:{marginRight:"5px"}}),"Filtering..."]}),re>0&&t.jsxs("span",{className:"filtered-count",children:[re," filter",re!==1?"s":""," applied"]}),t.jsxs("button",{className:`btn btn-outline btn-sm ${ce?"active":""}`,onClick:()=>fe(!ce),disabled:x,children:[t.jsx("i",{className:"fas fa-filter"})," Filters"]}),re>0&&t.jsxs("button",{className:"btn btn-outline btn-sm text-danger",onClick:es,title:"Clear all filters",children:[t.jsx("i",{className:"fas fa-times"})," Clear"]})]})]})}),ce&&t.jsx("div",{className:"filters-panel",style:{borderBottom:"1px solid #e9ecef",padding:"1.5rem",background:"#f8f9fa"},children:t.jsxs("div",{className:"filters-grid",style:{display:"grid",gridTemplateColumns:"repeat(auto-fit, minmax(250px, 1fr))",gap:"1rem"},children:[t.jsxs("div",{className:"filter-group",children:[t.jsxs("label",{className:"filter-label",children:[t.jsx("i",{className:"fas fa-search",style:{marginRight:"5px"}})," Search"]}),t.jsx("input",{type:"text",className:"form-control",placeholder:"Search TTPs, techniques, descriptions...",value:ke.search,onChange:b=>ra("search",b.target.value),onKeyDown:b=>{b.key==="Enter"&&(b.preventDefault(),ia(W,he,1,ze,ke))},disabled:x})]}),t.jsxs("div",{className:"filter-group",children:[t.jsxs("label",{className:"filter-label",children:[t.jsx("i",{className:"fas fa-crosshairs",style:{marginRight:"5px"}})," MITRE Tactics"]}),t.jsx("select",{className:"form-control",multiple:!0,size:"4",value:ke.tactics,onChange:b=>{const K=Array.from(b.target.selectedOptions,ge=>ge.value);ra("tactics",K)},style:{fontSize:"0.85rem"},disabled:x,children:(Zt=Oe==null?void 0:Oe.tactics)==null?void 0:Zt.map(b=>t.jsxs("option",{value:b.value,children:[b.label," (",b.count||0,")"]},b.value))})]}),t.jsxs("div",{className:"filter-group",children:[t.jsxs("label",{className:"filter-label",children:[t.jsx("i",{className:"fas fa-exclamation-triangle",style:{marginRight:"5px"}})," Severity Levels"]}),t.jsx("div",{className:"checkbox-group",style:{display:"grid",gridTemplateColumns:"1fr 1fr",gap:"0.5rem"},children:["critical","high","medium","low"].map(b=>t.jsxs("label",{className:"checkbox-item",style:{display:"flex",alignItems:"center",fontSize:"0.85rem"},children:[t.jsx("input",{type:"checkbox",checked:ke.severity_levels.includes(b),onChange:K=>$i("severity_levels",b,K.target.checked),style:{marginRight:"5px"},disabled:x}),t.jsx("span",{className:`severity-badge severity-${b}`,style:{padding:"2px 8px",borderRadius:"12px",fontSize:"0.75rem",fontWeight:"500",textTransform:"capitalize"},children:b})]},b))})]}),t.jsxs("div",{className:"filter-group",children:[t.jsxs("label",{className:"filter-label",children:[t.jsx("i",{className:"fas fa-calendar-alt",style:{marginRight:"5px"}})," Date Range"]}),t.jsxs("div",{style:{display:"grid",gridTemplateColumns:"1fr 1fr",gap:"0.5rem"},children:[t.jsx("input",{type:"date",className:"form-control",value:ke.date_from,onChange:b=>ra("date_from",b.target.value),placeholder:"From",title:"From date",disabled:x}),t.jsx("input",{type:"date",className:"form-control",value:ke.date_to,onChange:b=>ra("date_to",b.target.value),placeholder:"To",title:"To date",disabled:x})]})]}),t.jsxs("div",{className:"filter-group",children:[t.jsxs("label",{className:"filter-label",children:[t.jsx("i",{className:"fas fa-rss",style:{marginRight:"5px"}})," Threat Feeds"]}),t.jsx("select",{className:"form-control",multiple:!0,size:"3",value:ke.threat_feed_ids,onChange:b=>{const K=Array.from(b.target.selectedOptions,ge=>ge.value);ra("threat_feed_ids",K)},style:{fontSize:"0.85rem"},children:(Sa=Oe==null?void 0:Oe.threat_feeds)==null?void 0:Sa.map(b=>t.jsxs("option",{value:b.id.toString(),children:[b.name," (",b.ttp_count||0,")"]},b.id))})]}),t.jsxs("div",{className:"filter-group",children:[t.jsxs("label",{className:"filter-label",children:[t.jsx("i",{className:"fas fa-toggle-on",style:{marginRight:"5px"}})," Status Filters"]}),t.jsxs("div",{style:{display:"grid",gap:"0.5rem"},children:[t.jsxs("select",{className:"form-control",value:ke.anonymized_only,onChange:b=>ra("anonymized_only",b.target.value),style:{fontSize:"0.85rem"},children:[t.jsx("option",{value:"",children:"All TTPs"}),t.jsx("option",{value:"true",children:"Anonymized Only"}),t.jsx("option",{value:"false",children:"Active Only"})]}),t.jsxs("select",{className:"form-control",value:ke.has_subtechniques,onChange:b=>ra("has_subtechniques",b.target.value),style:{fontSize:"0.85rem"},children:[t.jsx("option",{value:"",children:"All Techniques"}),t.jsx("option",{value:"true",children:"With Sub-techniques"}),t.jsx("option",{value:"false",children:"Without Sub-techniques"})]})]})]})]})}),re>0&&t.jsx("div",{className:"active-filters-summary",style:{padding:"1rem",borderBottom:"1px solid #e9ecef",background:"#fff"},children:t.jsxs("div",{style:{display:"flex",alignItems:"center",flexWrap:"wrap",gap:"0.5rem"},children:[t.jsx("span",{style:{fontSize:"0.875rem",fontWeight:"600",color:"#495057"},children:"Active Filters:"}),ke.search&&t.jsxs("span",{className:"filter-badge",style:{background:"#e3f2fd",color:"#1976d2",padding:"2px 8px",borderRadius:"12px",fontSize:"0.75rem",display:"flex",alignItems:"center",gap:"4px"},children:['Search: "',ke.search,'"',t.jsx("button",{onClick:()=>ra("search",""),style:{background:"none",border:"none",color:"#1976d2",cursor:"pointer",padding:"0",fontSize:"0.75rem"},children:"×"})]}),ke.tactics.length>0&&t.jsxs("span",{className:"filter-badge",style:{background:"#f3e5f5",color:"#7b1fa2",padding:"2px 8px",borderRadius:"12px",fontSize:"0.75rem",display:"flex",alignItems:"center",gap:"4px"},children:[ke.tactics.length," Tactic",ke.tactics.length!==1?"s":"",t.jsx("button",{onClick:()=>ra("tactics",[]),style:{background:"none",border:"none",color:"#7b1fa2",cursor:"pointer",padding:"0",fontSize:"0.75rem"},children:"×"})]}),ke.severity_levels.length>0&&t.jsxs("span",{className:"filter-badge",style:{background:"#ffebee",color:"#c62828",padding:"2px 8px",borderRadius:"12px",fontSize:"0.75rem",display:"flex",alignItems:"center",gap:"4px"},children:[ke.severity_levels.length," Severity Level",ke.severity_levels.length!==1?"s":"",t.jsx("button",{onClick:()=>ra("severity_levels",[]),style:{background:"none",border:"none",color:"#c62828",cursor:"pointer",padding:"0",fontSize:"0.75rem"},children:"×"})]}),(ke.date_from||ke.date_to)&&t.jsxs("span",{className:"filter-badge",style:{background:"#e8f5e8",color:"#2e7d32",padding:"2px 8px",borderRadius:"12px",fontSize:"0.75rem",display:"flex",alignItems:"center",gap:"4px"},children:["Date Range",t.jsx("button",{onClick:()=>{const b={...ke,date_from:"",date_to:""};$e(b),je(1);const K=Sn(b);k(K),ia(W,he,1,ze,b)},style:{background:"none",border:"none",color:"#2e7d32",cursor:"pointer",padding:"0",fontSize:"0.75rem"},children:"×"})]}),ke.threat_feed_ids.length>0&&t.jsxs("span",{className:"filter-badge",style:{background:"#fff3e0",color:"#ef6c00",padding:"2px 8px",borderRadius:"12px",fontSize:"0.75rem",display:"flex",alignItems:"center",gap:"4px"},children:[ke.threat_feed_ids.length," Feed",ke.threat_feed_ids.length!==1?"s":"",t.jsx("button",{onClick:()=>ra("threat_feed_ids",[]),style:{background:"none",border:"none",color:"#ef6c00",cursor:"pointer",padding:"0",fontSize:"0.75rem"},children:"×"})]})]})}),t.jsx("div",{className:"card-content",children:t.jsxs("table",{className:"data-table",children:[t.jsx("thead",{children:t.jsxs("tr",{children:[t.jsxs("th",{className:"sortable-header",onClick:()=>pt("id"),style:{cursor:"pointer",userSelect:"none"},children:["ID",xa("id")]}),t.jsxs("th",{className:"sortable-header",onClick:()=>pt("name"),style:{cursor:"pointer",userSelect:"none"},children:["Name",xa("name")]}),t.jsxs("th",{className:"sortable-header",onClick:()=>pt("mitre_technique_id"),style:{cursor:"pointer",userSelect:"none"},children:["MITRE Technique",xa("mitre_technique_id")]}),t.jsxs("th",{className:"sortable-header",onClick:()=>pt("mitre_tactic"),style:{cursor:"pointer",userSelect:"none"},children:["Tactic",xa("mitre_tactic")]}),t.jsx("th",{children:"Threat Feed"}),t.jsxs("th",{className:"sortable-header",onClick:()=>pt("created_at"),style:{cursor:"pointer",userSelect:"none"},children:["Created",xa("created_at")]}),t.jsx("th",{children:"Status"}),t.jsx("th",{children:"Actions"})]})}),t.jsx("tbody",{children:x?t.jsx("tr",{children:t.jsxs("td",{colSpan:"8",style:{textAlign:"center",padding:"2rem"},children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Loading TTPs..."]})}):i.length>0?i.map(b=>t.jsxs("tr",{children:[t.jsx("td",{children:b.id}),t.jsx("td",{children:b.name}),t.jsx("td",{children:b.mitre_technique_id}),t.jsx("td",{children:b.mitre_tactic_display||b.mitre_tactic}),t.jsx("td",{children:b.threat_feed?b.threat_feed.name:"N/A"}),t.jsx("td",{children:new Date(b.created_at).toLocaleDateString()}),t.jsx("td",{children:t.jsx("span",{className:`badge ${b.is_anonymized?"badge-info":"badge-success"}`,children:b.is_anonymized?"Anonymized":"Active"})}),t.jsxs("td",{children:[t.jsx("button",{className:"btn btn-outline btn-sm",title:"View TTP Details",onClick:()=>va(b.id),style:{marginRight:"5px"},children:t.jsx("i",{className:"fas fa-eye"})}),t.jsx("button",{className:"btn btn-outline btn-sm",title:"Share",style:{marginRight:"5px"},children:t.jsx("i",{className:"fas fa-share-alt"})}),t.jsx("button",{className:"btn btn-outline btn-sm text-danger",title:"Delete TTP",onClick:()=>Ve(b.id),children:t.jsx("i",{className:"fas fa-trash"})})]})]},b.id)):t.jsx("tr",{children:t.jsx("td",{colSpan:"8",style:{textAlign:"center",padding:"2rem"},children:"No TTPs found"})})})]})})]}),se&&t.jsx("div",{className:"modal-overlay",onClick:ln,children:t.jsxs("div",{className:"modal-content ttp-modal",onClick:b=>b.stopPropagation(),children:[t.jsxs("div",{className:"modal-header",children:[t.jsxs("h2",{children:[t.jsx("i",{className:"fas fa-crosshairs"}),et?"Edit TTP Details":"TTP Details"]}),t.jsx("button",{className:"modal-close",onClick:ln,children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsx("div",{className:"modal-body",children:Fe?t.jsxs("div",{style:{textAlign:"center",padding:"3rem"},children:[t.jsx("i",{className:"fas fa-spinner fa-spin",style:{fontSize:"2rem",color:"#0056b3"}}),t.jsx("p",{style:{marginTop:"1rem",color:"#666"},children:"Loading TTP details..."})]}):ue?t.jsxs("div",{className:"ttp-detail-content",children:[t.jsx("div",{className:"ttp-header-section",children:t.jsxs("div",{className:"ttp-title-section",children:[et?t.jsx("input",{type:"text",className:"form-control ttp-name-input",value:wt.name,onChange:b=>Ja("name",b.target.value),placeholder:"TTP Name"}):t.jsx("h3",{className:"ttp-title",children:ue.name}),t.jsxs("div",{className:"ttp-badges",children:[t.jsx("span",{className:"badge badge-primary",children:ue.mitre_technique_id||"No MITRE ID"}),t.jsx("span",{className:"badge badge-secondary",children:ue.mitre_tactic_display||ue.mitre_tactic||"No Tactic"}),ue.is_anonymized&&t.jsx("span",{className:"badge badge-info",children:"Anonymized"})]})]})}),t.jsxs("div",{className:"ttp-details-grid",children:[t.jsxs("div",{className:"detail-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-info-circle"})," Basic Information"]}),t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Description:"}),t.jsx("div",{className:"detail-value",children:et?t.jsx("textarea",{className:"form-control",value:wt.description,onChange:b=>Ja("description",b.target.value),placeholder:"TTP Description",rows:"4"}):t.jsx("p",{children:ue.description||"No description available"})})]})]}),t.jsxs("div",{className:"detail-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-crosshairs"})," MITRE ATT&CK Mapping"]}),t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Technique ID:"}),t.jsx("div",{className:"detail-value",children:et?t.jsx("input",{type:"text",className:"form-control",value:wt.mitre_technique_id,onChange:b=>Ja("mitre_technique_id",b.target.value),placeholder:"e.g., T1566.001"}):t.jsx("span",{className:"technique-id-display",children:ue.mitre_technique_id||"Not specified"})})]}),t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Tactic:"}),t.jsx("div",{className:"detail-value",children:et?t.jsxs("select",{className:"form-control",value:wt.mitre_tactic,onChange:b=>Ja("mitre_tactic",b.target.value),children:[t.jsx("option",{value:"",children:"Select Tactic"}),t.jsx("option",{value:"initial-access",children:"Initial Access"}),t.jsx("option",{value:"execution",children:"Execution"}),t.jsx("option",{value:"persistence",children:"Persistence"}),t.jsx("option",{value:"privilege-escalation",children:"Privilege Escalation"}),t.jsx("option",{value:"defense-evasion",children:"Defense Evasion"}),t.jsx("option",{value:"credential-access",children:"Credential Access"}),t.jsx("option",{value:"discovery",children:"Discovery"}),t.jsx("option",{value:"lateral-movement",children:"Lateral Movement"}),t.jsx("option",{value:"collection",children:"Collection"}),t.jsx("option",{value:"command-and-control",children:"Command and Control"}),t.jsx("option",{value:"exfiltration",children:"Exfiltration"}),t.jsx("option",{value:"impact",children:"Impact"})]}):t.jsx("span",{children:ue.mitre_tactic_display||ue.mitre_tactic||"Not specified"})})]}),(ue.mitre_subtechnique||et)&&t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Sub-technique:"}),t.jsx("div",{className:"detail-value",children:et?t.jsx("input",{type:"text",className:"form-control",value:wt.mitre_subtechnique,onChange:b=>Ja("mitre_subtechnique",b.target.value),placeholder:"Sub-technique name"}):t.jsx("span",{children:ue.mitre_subtechnique||"None"})})]})]}),t.jsxs("div",{className:"detail-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-rss"})," Threat Feed Information"]}),t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Source Feed:"}),t.jsx("div",{className:"detail-value",children:ue.threat_feed?t.jsxs("div",{className:"feed-info",children:[t.jsx("span",{className:"feed-name",children:ue.threat_feed.name}),t.jsx("span",{className:`feed-type ${ue.threat_feed.is_external?"external":"internal"}`,children:ue.threat_feed.is_external?"External":"Internal"})]}):t.jsx("span",{className:"no-data",children:"Manual Entry"})})]})]}),t.jsxs("div",{className:"detail-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-clock"})," Metadata"]}),t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Created:"}),t.jsx("div",{className:"detail-value",children:ue.created_at?new Date(ue.created_at).toLocaleString():"Unknown"})]}),t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Last Modified:"}),t.jsx("div",{className:"detail-value",children:ue.updated_at?new Date(ue.updated_at).toLocaleString():"Never"})]}),ue.stix_id&&t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"STIX ID:"}),t.jsx("div",{className:"detail-value",children:t.jsx("code",{children:ue.stix_id})})]})]})]})]}):t.jsxs("div",{style:{textAlign:"center",padding:"3rem"},children:[t.jsx("i",{className:"fas fa-exclamation-triangle",style:{fontSize:"2rem",color:"#dc3545"}}),t.jsx("p",{style:{marginTop:"1rem",color:"#666"},children:"Failed to load TTP details"})]})}),t.jsxs("div",{className:"modal-footer",children:[t.jsx("button",{className:"btn btn-outline",onClick:ln,children:"Close"}),ue&&!Fe&&t.jsx(t.Fragment,{children:et?t.jsxs(t.Fragment,{children:[t.jsx("button",{className:"btn btn-outline",onClick:ei,children:"Cancel Edit"}),t.jsxs("button",{className:"btn btn-primary",onClick:kn,children:[t.jsx("i",{className:"fas fa-save"})," Save Changes"]})]}):t.jsxs("button",{className:"btn btn-primary",onClick:ei,children:[t.jsx("i",{className:"fas fa-edit"})," Edit TTP"]})})]})]})}),ft&&t.jsx("div",{className:"modal-overlay",onClick:ts,children:t.jsxs("div",{className:"modal-content export-modal",onClick:b=>b.stopPropagation(),children:[t.jsxs("div",{className:"modal-header",children:[t.jsxs("h3",{children:[t.jsx("i",{className:"fas fa-download"})," Export TTP Analysis"]}),t.jsx("button",{className:"modal-close",onClick:ts,children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsxs("div",{className:"modal-body",children:[tt&&t.jsxs("div",{className:"alert alert-error",children:[t.jsx("i",{className:"fas fa-exclamation-triangle"}),tt]}),t.jsx("div",{className:"export-info",children:t.jsxs("div",{className:"info-card",children:[t.jsx("i",{className:"fas fa-info-circle"}),t.jsxs("div",{children:[t.jsx("strong",{children:"Export Information"}),t.jsx("p",{children:"Export your TTP analysis data in multiple formats. You can filter the data and customize the export to meet your specific needs."})]})]})}),t.jsxs("form",{children:[t.jsxs("div",{className:"form-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-file-alt"})," Export Format"]}),t.jsxs("div",{className:"format-options",children:[t.jsxs("label",{className:"format-option",children:[t.jsx("input",{type:"radio",name:"exportFormat",value:"json",checked:Ce==="json",onChange:b=>M(b.target.value)}),t.jsxs("div",{className:"format-card",children:[t.jsx("i",{className:"fas fa-code"}),t.jsx("span",{children:"JSON"}),t.jsx("small",{children:"Structured data format"})]})]}),t.jsxs("label",{className:"format-option",children:[t.jsx("input",{type:"radio",name:"exportFormat",value:"csv",checked:Ce==="csv",onChange:b=>M(b.target.value)}),t.jsxs("div",{className:"format-card",children:[t.jsx("i",{className:"fas fa-table"}),t.jsx("span",{children:"CSV"}),t.jsx("small",{children:"Spreadsheet compatible"})]})]}),t.jsxs("label",{className:"format-option",children:[t.jsx("input",{type:"radio",name:"exportFormat",value:"stix",checked:Ce==="stix",onChange:b=>M(b.target.value)}),t.jsxs("div",{className:"format-card",children:[t.jsx("i",{className:"fas fa-shield-alt"}),t.jsx("span",{children:"STIX"}),t.jsx("small",{children:"Threat intelligence standard"})]})]})]})]}),t.jsxs("div",{className:"form-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-filter"})," Filters"]}),t.jsxs("div",{className:"form-grid",children:[t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"MITRE Tactic"}),t.jsxs("select",{className:"form-control",value:Q.tactic,onChange:b=>Ft("tactic",b.target.value),children:[t.jsx("option",{value:"",children:"All Tactics"}),t.jsx("option",{value:"initial-access",children:"Initial Access"}),t.jsx("option",{value:"execution",children:"Execution"}),t.jsx("option",{value:"persistence",children:"Persistence"}),t.jsx("option",{value:"privilege-escalation",children:"Privilege Escalation"}),t.jsx("option",{value:"defense-evasion",children:"Defense Evasion"}),t.jsx("option",{value:"credential-access",children:"Credential Access"}),t.jsx("option",{value:"discovery",children:"Discovery"}),t.jsx("option",{value:"lateral-movement",children:"Lateral Movement"}),t.jsx("option",{value:"collection",children:"Collection"}),t.jsx("option",{value:"command-and-control",children:"Command and Control"}),t.jsx("option",{value:"exfiltration",children:"Exfiltration"}),t.jsx("option",{value:"impact",children:"Impact"})]})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Technique ID"}),t.jsx("input",{type:"text",className:"form-control",value:Q.technique_id,onChange:b=>Ft("technique_id",b.target.value),placeholder:"e.g., T1059"})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Threat Feed ID"}),t.jsx("input",{type:"number",className:"form-control",value:Q.feed_id,onChange:b=>Ft("feed_id",b.target.value),placeholder:"Enter feed ID"})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Maximum Records"}),t.jsx("input",{type:"number",className:"form-control",value:Q.limit,onChange:b=>Ft("limit",parseInt(b.target.value)||1e3),min:"1",max:"10000"})]})]}),t.jsxs("div",{className:"form-row",children:[t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Created After"}),t.jsx("input",{type:"date",className:"form-control",value:Q.created_after,onChange:b=>Ft("created_after",b.target.value)})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Created Before"}),t.jsx("input",{type:"date",className:"form-control",value:Q.created_before,onChange:b=>Ft("created_before",b.target.value)})]})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Specific Fields (comma-separated)"}),t.jsx("input",{type:"text",className:"form-control",value:Q.fields,onChange:b=>Ft("fields",b.target.value),placeholder:"e.g., id,name,mitre_technique_id,description"}),t.jsx("small",{className:"form-help",children:"Leave empty to export all available fields"})]})]}),t.jsxs("div",{className:"form-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-cog"})," Advanced Options"]}),t.jsxs("div",{className:"checkbox-group",children:[t.jsxs("label",{className:"checkbox-label",children:[t.jsx("input",{type:"checkbox",checked:Q.include_anonymized,onChange:b=>Ft("include_anonymized",b.target.checked)}),t.jsx("span",{children:"Include anonymized TTPs"})]}),t.jsxs("label",{className:"checkbox-label",children:[t.jsx("input",{type:"checkbox",checked:Q.include_original,onChange:b=>Ft("include_original",b.target.checked)}),t.jsx("span",{children:"Include original data for anonymized TTPs"})]})]})]})]})]}),t.jsxs("div",{className:"modal-footer",children:[t.jsx("button",{className:"btn btn-outline",onClick:ts,children:"Cancel"}),t.jsx("button",{className:"btn btn-primary",onClick:_,disabled:ye,children:ye?t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-spinner fa-spin"})," Exporting..."]}):t.jsxs(t.Fragment,{children:[t.jsx("i",{className:"fas fa-download"})," Export Data"]})})]})]})}),Ot&&t.jsx("div",{className:"modal-overlay",onClick:zn,children:t.jsxs("div",{className:"modal-content matrix-cell-modal",onClick:b=>b.stopPropagation(),children:[t.jsxs("div",{className:"modal-header",children:[t.jsxs("h3",{children:[t.jsx("i",{className:"fas fa-th-large"}),ht?`Technique ${ht} in ${at.replace(/_/g," ")}`:`${at.replace(/_/g," ")} Tactic Details`]}),t.jsx("button",{className:"modal-close",onClick:zn,children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsx("div",{className:"modal-body",children:D?t.jsxs("div",{className:"loading-state",children:[t.jsx("i",{className:"fas fa-spinner fa-spin"}),t.jsx("span",{children:"Loading matrix cell details..."})]}):_e?t.jsxs("div",{className:"matrix-cell-details",children:[t.jsx("div",{className:"cell-info-section",children:t.jsxs("div",{className:"info-grid",children:[t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"Tactic:"}),t.jsx("span",{children:_e.cell_info.tactic_display})]}),t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"Total TTPs:"}),t.jsx("span",{children:_e.cell_info.total_ttps_in_cell})]}),t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"Unique Techniques:"}),t.jsx("span",{children:_e.cell_info.unique_techniques})]}),t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"Threat Feeds:"}),t.jsx("span",{children:_e.cell_info.threat_feeds_count})]}),t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"Recent Activity (30d):"}),t.jsx("span",{children:_e.cell_info.recent_activity})]}),t.jsxs("div",{className:"info-item",children:[t.jsx("label",{children:"With Subtechniques:"}),t.jsx("span",{children:_e.cell_info.has_subtechniques})]})]})}),_e.related_techniques&&_e.related_techniques.length>0&&t.jsxs("div",{className:"related-techniques-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-sitemap"})," Top Techniques in this Tactic"]}),t.jsx("div",{className:"techniques-grid",children:_e.related_techniques.map((b,K)=>t.jsxs("div",{className:"technique-card clickable",onClick:()=>An(b.mitre_technique_id),children:[t.jsx("div",{className:"technique-id",children:b.mitre_technique_id}),t.jsxs("div",{className:"technique-count",children:[b.count," TTPs"]})]},b.mitre_technique_id||K))})]}),t.jsxs("div",{className:"ttps-list-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-list"}),"TTPs (",_e.ttps.filtered_count,")",_e.ttps.has_next&&t.jsxs("span",{className:"showing-info",children:["(Showing first ",_e.ttps.page_size,")"]})]}),_e.ttps.results.length>0?t.jsx("div",{className:"ttps-list",children:_e.ttps.results.map(b=>t.jsxs("div",{className:"ttp-item",children:[t.jsxs("div",{className:"ttp-header",children:[t.jsx("div",{className:"ttp-name",children:b.name}),t.jsxs("div",{className:"ttp-badges",children:[b.mitre_technique_id&&t.jsx("span",{className:"badge technique-badge",children:b.mitre_technique_id}),b.severity&&t.jsx("span",{className:`badge severity-${b.severity}`,children:b.severity}),b.is_anonymized&&t.jsx("span",{className:"badge anonymized-badge",children:"Anonymized"})]})]}),t.jsx("div",{className:"ttp-description",children:b.description.length>200?b.description.substring(0,200)+"...":b.description}),t.jsxs("div",{className:"ttp-meta",children:[b.threat_feed&&t.jsxs("div",{className:"feed-info",children:[t.jsx("i",{className:"fas fa-rss"}),t.jsx("span",{children:b.threat_feed.name}),b.threat_feed.is_external&&t.jsx("span",{className:"external-indicator",children:"External"})]}),t.jsxs("div",{className:"created-date",children:[t.jsx("i",{className:"fas fa-clock"}),new Date(b.created_at).toLocaleDateString()]})]})]},b.id))}):t.jsxs("div",{className:"empty-state",children:[t.jsx("i",{className:"fas fa-info-circle"}),t.jsx("span",{children:"No TTPs found for this matrix cell"})]})]}),_e.statistics&&t.jsxs("div",{className:"statistics-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-chart-bar"})," Statistics"]}),t.jsx("div",{className:"stats-grid",children:_e.statistics.severity_distribution&&t.jsxs("div",{className:"stat-item",children:[t.jsx("label",{children:"Severity Distribution:"}),t.jsx("div",{className:"severity-bars",children:Object.entries(_e.statistics.severity_distribution).map(([b,K])=>t.jsx("div",{className:"severity-bar",children:t.jsxs("span",{className:`severity-label ${b}`,children:[b,": ",K]})},b))})]})})]})]}):t.jsxs("div",{className:"error-state",children:[t.jsx("i",{className:"fas fa-exclamation-triangle"}),t.jsx("span",{children:"Failed to load matrix cell details"})]})}),t.jsxs("div",{className:"modal-footer",children:[t.jsx("button",{className:"btn btn-outline",onClick:zn,children:"Close"}),_e&&_e.ttps.has_next&&t.jsxs("button",{className:"btn btn-primary",children:[t.jsx("i",{className:"fas fa-arrow-right"})," View All TTPs"]})]})]})}),vt&&t.jsx("div",{className:"modal-overlay",onClick:Ss,children:t.jsxs("div",{className:"modal-content technique-modal",onClick:b=>b.stopPropagation(),children:[t.jsxs("div",{className:"modal-header",children:[t.jsxs("h3",{children:[t.jsx("i",{className:"fas fa-bullseye"}),"Technique Details: ",qt]}),t.jsx("button",{className:"modal-close",onClick:Ss,children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsx("div",{className:"modal-body",children:Wt?t.jsxs("div",{className:"loading-state",children:[t.jsx("i",{className:"fas fa-spinner fa-spin"}),t.jsx("span",{children:"Loading technique details..."})]}):Ee?t.jsxs("div",{className:"technique-details",children:[t.jsxs("div",{className:"technique-info-section",children:[t.jsx("div",{className:"info-header",children:t.jsxs("div",{className:"technique-title",children:[t.jsx("h4",{children:Ee.technique_info.name||qt}),t.jsxs("div",{className:"technique-badges",children:[t.jsx("span",{className:"badge technique-badge",children:qt}),t.jsx("span",{className:`badge severity-${Ee.technique_info.severity}`,children:Ee.technique_info.severity}),Ee.technique_info.is_subtechnique&&t.jsx("span",{className:"badge subtechnique-badge",children:"Subtechnique"})]})]})}),t.jsxs("div",{className:"technique-stats",children:[t.jsxs("div",{className:"stat-item",children:[t.jsx("label",{children:"Total TTPs:"}),t.jsx("span",{children:Ee.statistics.total_ttps})]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("label",{children:"Threat Feeds:"}),t.jsx("span",{children:Ee.statistics.unique_threat_feeds})]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("label",{children:"First Seen:"}),t.jsx("span",{children:Ee.statistics.first_seen?new Date(Ee.statistics.first_seen).toLocaleDateString():"N/A"})]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("label",{children:"Last Seen:"}),t.jsx("span",{children:Ee.statistics.last_seen?new Date(Ee.statistics.last_seen).toLocaleDateString():"N/A"})]})]})]}),Ee.associated_tactics&&Ee.associated_tactics.length>0&&t.jsxs("div",{className:"tactics-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-layer-group"})," Associated Tactics"]}),t.jsx("div",{className:"tactics-grid",children:Ee.associated_tactics.map(b=>t.jsxs("div",{className:"tactic-card clickable",onClick:()=>ua(b.tactic,qt),children:[t.jsx("div",{className:"tactic-name",children:b.tactic_display}),t.jsxs("div",{className:"tactic-count",children:[b.count," TTPs"]})]},b.tactic))})]}),Ee.variants&&Ee.variants.length>0&&t.jsxs("div",{className:"variants-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-code-branch"})," Related Variants"]}),t.jsx("div",{className:"variants-grid",children:Ee.variants.map(b=>t.jsxs("div",{className:"variant-card clickable",onClick:()=>An(b.mitre_technique_id),children:[t.jsx("div",{className:"variant-id",children:b.mitre_technique_id}),t.jsxs("div",{className:"variant-count",children:[b.count," TTPs"]})]},b.mitre_technique_id))})]}),Ee.statistics.recent_activity&&t.jsxs("div",{className:"activity-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-activity"})," Recent Activity"]}),t.jsxs("div",{className:"activity-stats",children:[t.jsxs("div",{className:"activity-item",children:[t.jsx("label",{children:"Last 24 hours:"}),t.jsx("span",{children:Ee.statistics.recent_activity.last_24h})]}),t.jsxs("div",{className:"activity-item",children:[t.jsx("label",{children:"Last 7 days:"}),t.jsx("span",{children:Ee.statistics.recent_activity.last_7d})]}),t.jsxs("div",{className:"activity-item",children:[t.jsx("label",{children:"Last 30 days:"}),t.jsx("span",{children:Ee.statistics.recent_activity.last_30d})]})]})]}),t.jsxs("div",{className:"technique-ttps-section",children:[t.jsxs("h4",{children:[t.jsx("i",{className:"fas fa-list"}),"TTPs Using This Technique (",Ee.ttps.length,")"]}),Ee.ttps.length>0?t.jsxs("div",{className:"technique-ttps-list",children:[Ee.ttps.slice(0,10).map(b=>t.jsxs("div",{className:"ttp-item",children:[t.jsxs("div",{className:"ttp-header",children:[t.jsx("div",{className:"ttp-name",children:b.name}),t.jsxs("div",{className:"ttp-badges",children:[b.mitre_tactic&&t.jsx("span",{className:"badge tactic-badge",children:b.mitre_tactic_display}),b.is_anonymized&&t.jsx("span",{className:"badge anonymized-badge",children:"Anonymized"})]})]}),t.jsx("div",{className:"ttp-description",children:b.description.length>150?b.description.substring(0,150)+"...":b.description}),t.jsxs("div",{className:"ttp-meta",children:[b.threat_feed&&t.jsxs("div",{className:"feed-info",children:[t.jsx("i",{className:"fas fa-rss"}),t.jsx("span",{children:b.threat_feed.name})]}),t.jsxs("div",{className:"created-date",children:[t.jsx("i",{className:"fas fa-clock"}),new Date(b.created_at).toLocaleDateString()]})]})]},b.id)),Ee.ttps.length>10&&t.jsxs("div",{className:"more-ttps-indicator",children:[t.jsx("i",{className:"fas fa-ellipsis-h"}),t.jsxs("span",{children:["and ",Ee.ttps.length-10," more TTPs..."]})]})]}):t.jsxs("div",{className:"empty-state",children:[t.jsx("i",{className:"fas fa-info-circle"}),t.jsx("span",{children:"No TTPs found for this technique"})]})]})]}):t.jsxs("div",{className:"error-state",children:[t.jsx("i",{className:"fas fa-exclamation-triangle"}),t.jsx("span",{children:"Failed to load technique details"})]})}),t.jsxs("div",{className:"modal-footer",children:[t.jsx("button",{className:"btn btn-outline",onClick:Ss,children:"Close"}),Ee&&Ee.ttps.length>10&&t.jsxs("button",{className:"btn btn-primary",children:[t.jsx("i",{className:"fas fa-external-link-alt"})," View All TTPs"]})]})]})})]})}function K_({active:n}){const[i,l]=w.useState([]),[o,u]=w.useState(!0),[f,m]=w.useState(null),[x,p]=w.useState(!1),[h,v]=w.useState(null),[y,N]=w.useState({name:"",domain:"",contact_email:"",description:"",website:"",organization_type:"educational",primary_user:{username:"",email:"",password:"",first_name:"",last_name:""}});w.useEffect(()=>{n&&S()},[n]);const S=async()=>{try{u(!0),m(null);const z=await dt.get("/api/organizations/");if(console.log("Organizations API response:",z),z&&z.success){const U=z.organizations||[];console.log("Setting organizations:",U),l(U)}else console.error("API response unsuccessful:",z),m("Failed to load institutions - API response unsuccessful")}catch(z){console.error("Error fetching organizations:",z),m(`Failed to load institutions: ${z.message||"Unknown error"}`)}finally{u(!1)}},A=async z=>{var U,oe;z.preventDefault(),m(null);try{const ie=await dt.post("/api/organizations/create/",y);ie&&ie.success?(p(!1),N({name:"",domain:"",contact_email:"",description:"",website:"",organization_type:"educational",primary_user:{username:"",email:"",password:"",first_name:"",last_name:""}}),S(),m(null)):ie&&ie.message?m(ie.message):m("Failed to create institution - unknown error")}catch(ie){console.error("Error creating organization:",ie);const me=((oe=(U=ie.response)==null?void 0:U.data)==null?void 0:oe.message)||ie.message||"Failed to create institution";m(me)}};return n?t.jsxs("section",{id:"institutions",className:`page-section ${n?"active":""}`,children:[t.jsxs("div",{className:"page-header",children:[t.jsxs("div",{children:[t.jsx("h1",{className:"page-title",children:"Institutions & Organizations"}),t.jsx("p",{className:"page-subtitle",children:"Manage connected institutions and organizations"})]}),t.jsx("div",{className:"action-buttons",children:t.jsxs("button",{className:"btn btn-primary",onClick:()=>p(!0),children:[t.jsx("i",{className:"fas fa-plus"})," Add Institution"]})})]}),f&&t.jsxs("div",{className:"error-message",children:[t.jsx("i",{className:"fas fa-exclamation-triangle"}),f]}),o?t.jsxs("div",{className:"loading-state",children:[t.jsx("i",{className:"fas fa-spinner fa-spin"}),t.jsx("p",{children:"Loading institutions..."})]}):t.jsxs("div",{className:"institutions-grid",children:[t.jsxs("div",{className:"stats-row",children:[t.jsxs("div",{className:"stat-card",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-building"})}),t.jsxs("div",{className:"stat-content",children:[t.jsx("h3",{children:i.length}),t.jsx("p",{children:"Total Organizations"})]})]}),t.jsxs("div",{className:"stat-card",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-users"})}),t.jsxs("div",{className:"stat-content",children:[t.jsx("h3",{children:i.reduce((z,U)=>z+(U.member_count||0),0)}),t.jsx("p",{children:"Total Members"})]})]}),t.jsxs("div",{className:"stat-card",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-handshake"})}),t.jsxs("div",{className:"stat-content",children:[t.jsx("h3",{children:i.filter(z=>z.trust_relationships_count>0).length}),t.jsx("p",{children:"Connected Orgs"})]})]}),t.jsxs("div",{className:"stat-card",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-shield-alt"})}),t.jsxs("div",{className:"stat-content",children:[t.jsx("h3",{children:i.filter(z=>z.is_active).length}),t.jsx("p",{children:"Active Orgs"})]})]})]}),t.jsx("div",{className:"organizations-list",children:i.length===0?t.jsxs("div",{className:"empty-state",children:[t.jsx("i",{className:"fas fa-building",style:{fontSize:"48px",color:"#dee2e6"}}),t.jsx("h3",{children:"No institutions found"}),t.jsx("p",{children:"Create your first institution to get started with threat intelligence sharing."}),t.jsxs("button",{className:"btn btn-primary",onClick:()=>p(!0),children:[t.jsx("i",{className:"fas fa-plus"})," Create Institution"]})]}):t.jsx("div",{className:"organizations-table",children:t.jsxs("table",{children:[t.jsx("thead",{children:t.jsxs("tr",{children:[t.jsx("th",{children:"Institution"}),t.jsx("th",{children:"Type"}),t.jsx("th",{children:"Domain"}),t.jsx("th",{children:"Members"}),t.jsx("th",{children:"Status"}),t.jsx("th",{children:"Actions"})]})}),t.jsx("tbody",{children:i.map(z=>t.jsxs("tr",{children:[t.jsx("td",{children:t.jsxs("div",{className:"org-info",children:[t.jsx("div",{className:"org-icon",children:t.jsx("i",{className:"fas fa-building"})}),t.jsxs("div",{children:[t.jsx("div",{className:"org-name",children:z.name}),t.jsx("div",{className:"org-description",children:z.description||"No description"})]})]})}),t.jsx("td",{children:t.jsx("span",{className:"org-type",children:z.organization_type||"Unknown"})}),t.jsx("td",{children:z.domain||"N/A"}),t.jsx("td",{children:z.member_count||0}),t.jsx("td",{children:t.jsx("span",{className:`status-badge ${z.is_active?"active":"inactive"}`,children:z.is_active?"Active":"Inactive"})}),t.jsx("td",{children:t.jsxs("div",{className:"actions",children:[t.jsx("button",{className:"btn btn-sm btn-outline",onClick:()=>v(z),children:t.jsx("i",{className:"fas fa-eye"})}),t.jsx("button",{className:"btn btn-sm btn-outline",children:t.jsx("i",{className:"fas fa-edit"})})]})})]},z.id))})]})})})]}),x&&t.jsx("div",{className:"modal-overlay",onClick:()=>p(!1),children:t.jsxs("div",{className:"modal-content",onClick:z=>z.stopPropagation(),children:[t.jsxs("div",{className:"modal-header",children:[t.jsx("h3",{children:"Create New Institution"}),t.jsx("button",{className:"close-btn",onClick:()=>p(!1),children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsxs("form",{onSubmit:A,children:[t.jsxs("div",{className:"modal-body",children:[t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Institution Name"}),t.jsx("input",{type:"text",value:y.name,onChange:z=>N({...y,name:z.target.value}),required:!0})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Domain"}),t.jsx("input",{type:"text",value:y.domain,onChange:z=>N({...y,domain:z.target.value}),placeholder:"example.edu"})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Contact Email"}),t.jsx("input",{type:"email",value:y.contact_email,onChange:z=>N({...y,contact_email:z.target.value}),required:!0})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Organization Type"}),t.jsxs("select",{value:y.organization_type,onChange:z=>N({...y,organization_type:z.target.value}),children:[t.jsx("option",{value:"educational",children:"Educational"}),t.jsx("option",{value:"government",children:"Government"}),t.jsx("option",{value:"private",children:"Private"}),t.jsx("option",{value:"nonprofit",children:"Non-profit"}),t.jsx("option",{value:"healthcare",children:"Healthcare"}),t.jsx("option",{value:"financial",children:"Financial"})]})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Description"}),t.jsx("textarea",{value:y.description,onChange:z=>N({...y,description:z.target.value}),rows:"3"})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Website"}),t.jsx("input",{type:"url",value:y.website,onChange:z=>N({...y,website:z.target.value}),placeholder:"https://example.edu"})]}),t.jsxs("div",{className:"form-section",children:[t.jsx("h4",{style:{marginBottom:"1rem",paddingTop:"1rem",borderTop:"1px solid #ddd",color:"#333"},children:"Primary Administrator"}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Username *"}),t.jsx("input",{type:"text",value:y.primary_user.username,onChange:z=>N({...y,primary_user:{...y.primary_user,username:z.target.value}}),required:!0})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Email *"}),t.jsx("input",{type:"email",value:y.primary_user.email,onChange:z=>N({...y,primary_user:{...y.primary_user,email:z.target.value}}),required:!0})]}),t.jsxs("div",{className:"form-row",children:[t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"First Name *"}),t.jsx("input",{type:"text",value:y.primary_user.first_name,onChange:z=>N({...y,primary_user:{...y.primary_user,first_name:z.target.value}}),required:!0})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Last Name *"}),t.jsx("input",{type:"text",value:y.primary_user.last_name,onChange:z=>N({...y,primary_user:{...y.primary_user,last_name:z.target.value}}),required:!0})]})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{children:"Password *"}),t.jsx("input",{type:"password",value:y.primary_user.password,onChange:z=>N({...y,primary_user:{...y.primary_user,password:z.target.value}}),required:!0,placeholder:"Minimum 8 characters"})]})]})]}),t.jsxs("div",{className:"modal-footer",children:[t.jsx("button",{type:"button",className:"btn btn-secondary",onClick:()=>p(!1),children:"Cancel"}),t.jsx("button",{type:"submit",className:"btn btn-primary",children:"Create Institution"})]})]})]})}),h&&t.jsx("div",{className:"modal-overlay",onClick:()=>v(null),children:t.jsxs("div",{className:"modal large",onClick:z=>z.stopPropagation(),children:[t.jsxs("div",{className:"modal-header",children:[t.jsx("h3",{children:h.name}),t.jsx("button",{className:"close-btn",onClick:()=>v(null),children:t.jsx("i",{className:"fas fa-times"})})]}),t.jsx("div",{className:"modal-body",children:t.jsxs("div",{className:"org-details",children:[t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Name:"}),t.jsx("span",{children:h.name})]}),t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Type:"}),t.jsx("span",{children:h.organization_type||"Not specified"})]}),t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Domain:"}),t.jsx("span",{children:h.domain||"Not specified"})]}),t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Contact Email:"}),t.jsx("span",{children:h.contact_email||"Not specified"})]}),t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Website:"}),t.jsx("span",{children:h.website?t.jsx("a",{href:h.website,target:"_blank",rel:"noopener noreferrer",children:h.website}):"Not specified"})]}),t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Description:"}),t.jsx("span",{children:h.description||"No description provided"})]}),t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Members:"}),t.jsx("span",{children:h.member_count||0})]}),t.jsxs("div",{className:"detail-row",children:[t.jsx("label",{children:"Status:"}),t.jsx("span",{className:`status-badge ${h.is_active?"active":"inactive"}`,children:h.is_active?"Active":"Inactive"})]})]})}),t.jsx("div",{className:"modal-footer",children:t.jsx("button",{className:"btn btn-secondary",onClick:()=>v(null),children:"Close"})})]})})]}):null}function W_({active:n}){const[i,l]=w.useState([]),[o,u]=w.useState(!1),f=[{id:1,title:"Weekly Threat Intelligence Summary",type:"summary",date:"2025-01-08",status:"completed",description:"Comprehensive overview of threat landscape for the week"},{id:2,title:"APT Campaign Analysis",type:"campaign",date:"2025-01-05",status:"completed",description:"Deep dive into recent APT activities and TTPs"},{id:3,title:"Vulnerability Trend Report",type:"trend",date:"2025-01-01",status:"draft",description:"Analysis of vulnerability trends and exploitation patterns"}];return w.useEffect(()=>{n&&(u(!0),setTimeout(()=>{l(f),u(!1)},1e3))},[n]),n?t.jsxs("section",{id:"reports",className:`page-section ${n?"active":""}`,children:[t.jsxs("div",{className:"page-header",children:[t.jsxs("div",{children:[t.jsx("h1",{className:"page-title",children:"Reports & Analytics"}),t.jsx("p",{className:"page-subtitle",children:"Generate and manage threat intelligence reports"})]}),t.jsx("div",{className:"action-buttons",children:t.jsxs("button",{className:"btn btn-primary",children:[t.jsx("i",{className:"fas fa-plus"})," Generate Report"]})})]}),o?t.jsxs("div",{className:"loading-state",children:[t.jsx("i",{className:"fas fa-spinner fa-spin"}),t.jsx("p",{children:"Loading reports..."})]}):t.jsxs("div",{className:"reports-grid",children:[t.jsxs("div",{className:"stats-row",children:[t.jsxs("div",{className:"stat-card",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-file-alt"})}),t.jsxs("div",{className:"stat-content",children:[t.jsx("h3",{children:i.length}),t.jsx("p",{children:"Total Reports"})]})]}),t.jsxs("div",{className:"stat-card",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-check-circle"})}),t.jsxs("div",{className:"stat-content",children:[t.jsx("h3",{children:i.filter(m=>m.status==="completed").length}),t.jsx("p",{children:"Completed"})]})]}),t.jsxs("div",{className:"stat-card",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-edit"})}),t.jsxs("div",{className:"stat-content",children:[t.jsx("h3",{children:i.filter(m=>m.status==="draft").length}),t.jsx("p",{children:"Drafts"})]})]})]}),t.jsxs("div",{className:"reports-list",children:[t.jsx("h3",{style:{marginBottom:"1rem",color:"#333"},children:"Recent Reports"}),i.length===0?t.jsxs("div",{className:"empty-state",children:[t.jsx("i",{className:"fas fa-file-alt",style:{fontSize:"48px",color:"#dee2e6"}}),t.jsx("h3",{children:"No reports available"}),t.jsx("p",{children:"Generate your first threat intelligence report."}),t.jsxs("button",{className:"btn btn-primary",children:[t.jsx("i",{className:"fas fa-plus"})," Generate Report"]})]}):t.jsx("div",{className:"reports-table",children:t.jsxs("table",{children:[t.jsx("thead",{children:t.jsxs("tr",{children:[t.jsx("th",{children:"Report Title"}),t.jsx("th",{children:"Type"}),t.jsx("th",{children:"Date"}),t.jsx("th",{children:"Status"}),t.jsx("th",{children:"Actions"})]})}),t.jsx("tbody",{children:i.map(m=>t.jsxs("tr",{children:[t.jsx("td",{children:t.jsxs("div",{className:"report-info",children:[t.jsx("div",{className:"report-title",children:m.title}),t.jsx("div",{className:"report-description",children:m.description})]})}),t.jsx("td",{children:t.jsx("span",{className:"report-type",children:m.type})}),t.jsx("td",{children:m.date}),t.jsx("td",{children:t.jsx("span",{className:`status-badge ${m.status}`,children:m.status})}),t.jsx("td",{children:t.jsxs("div",{className:"actions",children:[t.jsx("button",{className:"btn btn-sm btn-outline",children:t.jsx("i",{className:"fas fa-eye"})}),t.jsx("button",{className:"btn btn-sm btn-outline",children:t.jsx("i",{className:"fas fa-download"})})]})})]},m.id))})]})})]})]})]}):null}function eS(){return t.jsx("style",{children:`
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
            background: rgba(255, 255, 255, 0.1);
            border: none;
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
        }
        
        .user-role {
            font-size: 12px;
            color: var(--primary-blue);
            opacity: 0.8;
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
        
        /* Institutions List */
        .institution-list {
            list-style: none;
        }
        
        .institution-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 0;
            border-bottom: 1px solid var(--medium-gray);
        }
        
        .institution-item:last-child {
            border-bottom: none;
        }
        
        .institution-logo {
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
        
        .institution-details {
            flex: 1;
        }
        
        .institution-name {
            font-weight: 600;
            margin-bottom: 2px;
        }
        
        .institution-meta {
            font-size: 13px;
            color: var(--text-muted);
        }
        
        .institution-stats {
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

      `})}function tS({active:n}){const[i,l]=w.useState([]),[o,u]=w.useState(!0),[f,m]=w.useState(null);w.useEffect(()=>{n&&setTimeout(()=>{l([{id:"1",type:"threat_alert",title:"New High-Priority Threat Detected",message:"A new malware strain has been identified in your organization's threat feed.",severity:"high",read:!1,created_at:new Date(Date.now()-1800*1e3).toISOString()},{id:"2",type:"trust_request",title:"Trust Relationship Request",message:'Organization "CyberSecure Inc." has requested a bilateral trust relationship.',severity:"medium",read:!1,created_at:new Date(Date.now()-7200*1e3).toISOString()},{id:"3",type:"feed_update",title:"Threat Feed Updated",message:'Your subscribed threat feed "MITRE ATT&CK" has been updated with 15 new indicators.',severity:"low",read:!0,created_at:new Date(Date.now()-14400*1e3).toISOString()}]),u(!1)},500)},[n]);const x=h=>{l(v=>v.map(y=>y.id===h?{...y,read:!0}:y))},p=h=>{l(v=>v.filter(y=>y.id!==h))};return n?t.jsxs("section",{id:"notifications",className:`page-section ${n?"active":""}`,children:[t.jsxs("div",{className:"page-header",children:[t.jsxs("div",{children:[t.jsx("h1",{className:"page-title",children:"Notifications"}),t.jsx("p",{className:"page-subtitle",children:"Stay updated with system alerts and activities"})]}),t.jsx("div",{className:"action-buttons",children:t.jsxs("button",{className:"btn btn-outline",children:[t.jsx("i",{className:"fas fa-check-double"})," Mark All Read"]})})]}),o?t.jsxs("div",{className:"loading-state",children:[t.jsx("i",{className:"fas fa-spinner fa-spin"}),t.jsx("p",{children:"Loading notifications..."})]}):t.jsx("div",{className:"notifications-list",children:i.length===0?t.jsxs("div",{className:"empty-state",children:[t.jsx("i",{className:"fas fa-bell-slash",style:{fontSize:"48px",color:"#dee2e6"}}),t.jsx("h3",{children:"No notifications"}),t.jsx("p",{children:"You're all caught up! No notifications to show."})]}):i.map(h=>t.jsxs("div",{className:`notification-item ${h.read?"":"unread"}`,children:[t.jsxs("div",{className:"notification-content",children:[t.jsxs("div",{className:"notification-header",children:[t.jsx("div",{className:"notification-icon",children:t.jsx("i",{className:h.type==="threat_alert"?"fas fa-exclamation-triangle":h.type==="trust_request"?"fas fa-handshake":"fas fa-rss",style:{color:h.severity==="high"?"#dc3545":h.severity==="medium"?"#ffc107":"#28a745"}})}),t.jsxs("div",{className:"notification-meta",children:[t.jsx("h4",{children:h.title}),t.jsxs("div",{className:"meta-info",children:[t.jsx("span",{children:new Date(h.created_at).toLocaleString()}),!h.read&&t.jsx("span",{className:"unread-dot"})]})]})]}),t.jsx("p",{className:"notification-message",children:h.message})]}),t.jsxs("div",{className:"notification-actions",children:[!h.read&&t.jsx("button",{onClick:()=>x(h.id),className:"btn btn-sm btn-outline",children:t.jsx("i",{className:"fas fa-check"})}),t.jsx("button",{onClick:()=>p(h.id),className:"btn btn-sm btn-danger",children:t.jsx("i",{className:"fas fa-trash"})})]})]},h.id))})]}):null}function Jd(){return t.jsxs(t.Fragment,{children:[t.jsx(eS,{}),t.jsx(G_,{})]})}function gg({onRegisterSuccess:n,switchView:i}){const[l,o]=w.useState({username:"",email:"",password:"",confirmPassword:"",firstName:"",lastName:"",organization:""}),[u,f]=w.useState(!1),[m,x]=w.useState(""),p=v=>{o({...l,[v.target.name]:v.target.value})},h=async v=>{if(v.preventDefault(),f(!0),x(""),l.password!==l.confirmPassword){x("Passwords do not match"),f(!1);return}try{await new Promise(N=>setTimeout(N,1e3));const y={user:{username:l.username,email:l.email,first_name:l.firstName,last_name:l.lastName},token:"mock-jwt-token"};n(y)}catch{x("Registration failed. Please try again.")}finally{f(!1)}};return t.jsx("div",{style:{minHeight:"100vh",display:"flex",justifyContent:"center",alignItems:"center",background:"#f5f7fa",padding:"2rem"},children:t.jsxs("div",{style:{background:"white",padding:"2rem",borderRadius:"8px",maxWidth:"500px",width:"100%",boxShadow:"0 4px 6px rgba(0, 0, 0, 0.1)"},children:[t.jsx("h2",{style:{textAlign:"center",marginBottom:"2rem"},children:"Register New User"}),m&&t.jsx("div",{style:{background:"#fee",color:"#c53030",padding:"1rem",borderRadius:"4px",marginBottom:"1rem"},children:m}),t.jsxs("form",{onSubmit:h,children:[t.jsxs("div",{style:{display:"grid",gridTemplateColumns:"1fr 1fr",gap:"1rem",marginBottom:"1rem"},children:[t.jsxs("div",{children:[t.jsx("label",{children:"First Name"}),t.jsx("input",{type:"text",name:"firstName",value:l.firstName,onChange:p,style:{width:"100%",padding:"0.75rem",marginTop:"0.25rem",border:"1px solid #e2e8f0",borderRadius:"4px"},required:!0})]}),t.jsxs("div",{children:[t.jsx("label",{children:"Last Name"}),t.jsx("input",{type:"text",name:"lastName",value:l.lastName,onChange:p,style:{width:"100%",padding:"0.75rem",marginTop:"0.25rem",border:"1px solid #e2e8f0",borderRadius:"4px"},required:!0})]})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{children:"Username"}),t.jsx("input",{type:"text",name:"username",value:l.username,onChange:p,style:{width:"100%",padding:"0.75rem",marginTop:"0.25rem",border:"1px solid #e2e8f0",borderRadius:"4px"},required:!0})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{children:"Email"}),t.jsx("input",{type:"email",name:"email",value:l.email,onChange:p,style:{width:"100%",padding:"0.75rem",marginTop:"0.25rem",border:"1px solid #e2e8f0",borderRadius:"4px"},required:!0})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{children:"Organization"}),t.jsx("input",{type:"text",name:"organization",value:l.organization,onChange:p,style:{width:"100%",padding:"0.75rem",marginTop:"0.25rem",border:"1px solid #e2e8f0",borderRadius:"4px"},required:!0})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{children:"Password"}),t.jsx("input",{type:"password",name:"password",value:l.password,onChange:p,style:{width:"100%",padding:"0.75rem",marginTop:"0.25rem",border:"1px solid #e2e8f0",borderRadius:"4px"},required:!0})]}),t.jsxs("div",{style:{marginBottom:"2rem"},children:[t.jsx("label",{children:"Confirm Password"}),t.jsx("input",{type:"password",name:"confirmPassword",value:l.confirmPassword,onChange:p,style:{width:"100%",padding:"0.75rem",marginTop:"0.25rem",border:"1px solid #e2e8f0",borderRadius:"4px"},required:!0})]}),t.jsx("button",{type:"submit",disabled:u,style:{width:"100%",padding:"0.75rem",background:"#0056b3",color:"white",border:"none",borderRadius:"4px",cursor:"pointer",marginBottom:"1rem"},children:u?"Registering...":"Register"}),t.jsx("div",{style:{textAlign:"center"},children:t.jsx("button",{type:"button",onClick:i,style:{background:"none",border:"none",color:"#0056b3",cursor:"pointer",textDecoration:"underline"},children:"Back to Login"})})]})]})})}const aS="/assets/BlueV-D02my35J.png";function nS({isOpen:n,onClose:i,onNavigate:l}){return n?t.jsx("div",{style:{position:"fixed",top:0,left:0,width:"100%",height:"100%",background:"rgba(0, 0, 0, 0.5)",display:"flex",justifyContent:"center",alignItems:"center",zIndex:9999},children:t.jsxs("div",{style:{background:"white",padding:"2rem",borderRadius:"8px",maxWidth:"500px",width:"90%",maxHeight:"80vh",overflow:"auto"},children:[t.jsxs("div",{style:{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:"1rem"},children:[t.jsx("h2",{children:"Help & Support"}),t.jsx("button",{onClick:i,style:{background:"none",border:"none",fontSize:"1.5rem",cursor:"pointer"},children:"×"})]}),t.jsxs("div",{style:{marginBottom:"1.5rem"},children:[t.jsx("h3",{children:"Getting Started"}),t.jsx("p",{children:"Welcome to CRISP - Cyber Risk Information Sharing Platform. This platform allows educational institutions to securely share threat intelligence."})]}),t.jsxs("div",{style:{marginBottom:"1.5rem"},children:[t.jsx("h3",{children:"Login Help"}),t.jsx("p",{children:"If you're having trouble logging in:"}),t.jsxs("ul",{children:[t.jsx("li",{children:"Ensure you're using the correct username and password"}),t.jsx("li",{children:"Contact your system administrator for account issues"}),t.jsx("li",{children:`Use the "Forgot Password" link if you've forgotten your password`})]})]}),t.jsxs("div",{style:{marginBottom:"1.5rem"},children:[t.jsx("h3",{children:"Contact Support"}),t.jsx("p",{children:"For technical support, please contact:"}),t.jsxs("p",{children:[t.jsx("strong",{children:"Email:"})," support@bluevision.com"]}),t.jsxs("p",{children:[t.jsx("strong",{children:"Phone:"})," +1 (555) 123-4567"]})]}),t.jsx("div",{style:{display:"flex",gap:"1rem",justifyContent:"flex-end"},children:t.jsx("button",{onClick:i,style:{padding:"0.5rem 1rem",background:"#0056b3",color:"white",border:"none",borderRadius:"4px",cursor:"pointer"},children:"Close"})})]})}):null}function zx(){return t.jsx("div",{style:{minHeight:"100vh",display:"flex",flexDirection:"column",justifyContent:"center",alignItems:"center",background:"linear-gradient(135deg, #0056b3 0%, #00a0e9 100%)",color:"white",textAlign:"center",padding:"2rem"},children:t.jsxs("div",{style:{maxWidth:"600px"},children:[t.jsx("div",{style:{fontSize:"4rem",marginBottom:"1rem"},children:"🚧"}),t.jsx("h1",{style:{fontSize:"2.5rem",marginBottom:"1rem"},children:"Under Construction"}),t.jsx("p",{style:{fontSize:"1.2rem",marginBottom:"2rem",opacity:.9},children:"This feature is currently being developed. We're working hard to bring you the best experience possible."}),t.jsxs("div",{style:{marginBottom:"2rem"},children:[t.jsx("h3",{children:"Coming Soon:"}),t.jsxs("ul",{style:{listStyle:"none",padding:0,marginTop:"1rem"},children:[t.jsx("li",{style:{margin:"0.5rem 0"},children:"📊 Advanced Analytics Dashboard"}),t.jsx("li",{style:{margin:"0.5rem 0"},children:"🔐 Enhanced Security Features"}),t.jsx("li",{style:{margin:"0.5rem 0"},children:"🤝 Improved Collaboration Tools"}),t.jsx("li",{style:{margin:"0.5rem 0"},children:"📱 Mobile Application"})]})]}),t.jsx("a",{href:"/",style:{display:"inline-block",padding:"1rem 2rem",background:"white",color:"#0056b3",textDecoration:"none",borderRadius:"8px",fontWeight:"bold",transition:"transform 0.3s ease"},children:"Go Back Home"})]})})}function sS({isOpen:n,onClose:i,onPasswordChanged:l}){const[o,u]=w.useState(""),[f,m]=w.useState(""),[x,p]=w.useState(""),[h,v]=w.useState(!1),[y,N]=w.useState(""),S=async A=>{if(A.preventDefault(),v(!0),N(""),f!==x){N("New passwords do not match"),v(!1);return}try{await new Promise(z=>setTimeout(z,1e3)),l(),i(),u(""),m(""),p("")}catch{N("Failed to change password")}finally{v(!1)}};return n?t.jsx("div",{style:{position:"fixed",top:0,left:0,width:"100%",height:"100%",background:"rgba(0, 0, 0, 0.5)",display:"flex",justifyContent:"center",alignItems:"center",zIndex:9999},children:t.jsxs("div",{style:{background:"white",padding:"2rem",borderRadius:"8px",maxWidth:"400px",width:"90%"},children:[t.jsx("h2",{children:"Change Password"}),y&&t.jsx("div",{style:{color:"red",marginBottom:"1rem"},children:y}),t.jsxs("form",{onSubmit:S,children:[t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{children:"Current Password"}),t.jsx("input",{type:"password",value:o,onChange:A=>u(A.target.value),style:{width:"100%",padding:"0.5rem",marginTop:"0.25rem"},required:!0})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{children:"New Password"}),t.jsx("input",{type:"password",value:f,onChange:A=>m(A.target.value),style:{width:"100%",padding:"0.5rem",marginTop:"0.25rem"},required:!0})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{children:"Confirm New Password"}),t.jsx("input",{type:"password",value:x,onChange:A=>p(A.target.value),style:{width:"100%",padding:"0.5rem",marginTop:"0.25rem"},required:!0})]}),t.jsxs("div",{style:{display:"flex",gap:"1rem",justifyContent:"flex-end"},children:[t.jsx("button",{type:"button",onClick:i,disabled:h,children:"Cancel"}),t.jsx("button",{type:"submit",disabled:h,children:h?"Changing...":"Change Password"})]})]})]})}):null}function iS({fullscreen:n=!1}){return n?t.jsxs("div",{style:{position:"fixed",top:0,left:0,width:"100%",height:"100%",background:"rgba(0, 0, 0, 0.5)",display:"flex",justifyContent:"center",alignItems:"center",zIndex:9999},children:[t.jsx("div",{style:{width:"50px",height:"50px",border:"4px solid #f3f3f3",borderTop:"4px solid #0056b3",borderRadius:"50%",animation:"spin 1s linear infinite"}}),t.jsx("style",{children:`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `})]}):t.jsx("div",{style:{width:"30px",height:"30px",border:"3px solid #f3f3f3",borderTop:"3px solid #0056b3",borderRadius:"50%",animation:"spin 1s linear infinite"}})}function rS({onLoginSuccess:n,switchView:i}){const[l,o]=w.useState(""),[u,f]=w.useState(""),[m,x]=w.useState(""),[p,h]=w.useState(!1),[v,y]=w.useState(!1),[N,S]=w.useState(!1),[A,z]=w.useState(!1);w.useEffect(()=>{if(window.feather)window.feather.replace();else{const W=document.createElement("script");W.src="https://cdnjs.cloudflare.com/ajax/libs/feather-icons/4.29.0/feather.min.js",W.onload=()=>{window.feather&&window.feather.replace()},document.head.appendChild(W)}},[]),w.useEffect(()=>{window.feather&&setTimeout(()=>window.feather.replace(),100)},[m,p,v]);const U=async W=>{W.preventDefault(),h(!0),x("");try{await new Promise(he=>setTimeout(he,1e3));const Ke=await g_(l,u);n(Ke)}catch(Ke){x(Ke.message||"Invalid username or password")}finally{h(!1)}},oe=()=>{y(!0)},ie=()=>{y(!1)},me=()=>{z(!0)},Ae=()=>{z(!1)},de=()=>{x(""),alert("Password changed successfully! You can now log in with your new password.")},pe=(W,Ke)=>{console.log(`Navigate to ${W} from login page with context:`,Ke),ie(),W==="construction"&&(i&&typeof i=="function"?i("Construction"):S(!0))};return N?t.jsx(zx,{}):t.jsxs(t.Fragment,{children:[t.jsx(lS,{}),p&&t.jsx(iS,{fullscreen:!0}),t.jsx("div",{className:"login-page",children:t.jsxs("div",{className:"login-content",children:[t.jsx("div",{className:"login-left",children:t.jsxs("div",{className:"brand-info",children:[t.jsx("div",{className:"logo-container",children:t.jsx("img",{src:aS,alt:"BlueV Logo",className:"brand-logo"})}),t.jsx("h2",{children:"Cyber Risk Information Sharing Platform"}),t.jsx("p",{children:"Streamline your threat intelligence sharing and committee management"}),t.jsxs("div",{className:"feature-list",children:[t.jsxs("div",{className:"feature-item",children:[t.jsx("div",{className:"feature-icon",children:t.jsx("i",{"data-feather":"shield"})}),t.jsxs("div",{className:"feature-text",children:[t.jsx("h3",{children:"Monitor Threats"}),t.jsx("p",{children:"Track and analyze security threats across institutions"})]})]}),t.jsxs("div",{className:"feature-item",children:[t.jsx("div",{className:"feature-icon",children:t.jsx("i",{"data-feather":"repeat"})}),t.jsxs("div",{className:"feature-text",children:[t.jsx("h3",{children:"Share Intelligence"}),t.jsx("p",{children:"Securely exchange threat data with trusted partners"})]})]}),t.jsxs("div",{className:"feature-item",children:[t.jsx("div",{className:"feature-icon",children:t.jsx("i",{"data-feather":"trending-up"})}),t.jsxs("div",{className:"feature-text",children:[t.jsx("h3",{children:"Analyze Patterns"}),t.jsx("p",{children:"Identify emerging threat patterns with advanced analytics"})]})]})]})]})}),t.jsx("div",{className:"login-right",children:t.jsxs("div",{className:"login-form-container",children:[t.jsx("div",{className:"login-header",children:t.jsx("button",{className:"help-button",onClick:oe,title:"Help & Support",type:"button",children:t.jsx("i",{"data-feather":"help-circle"})})}),t.jsx("h2",{children:"Welcome Back"}),t.jsx("p",{className:"subtitle",children:"Sign in to your account"}),m&&t.jsxs("div",{className:"error-message",children:[t.jsx("i",{"data-feather":"alert-circle"})," ",m]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{htmlFor:"username",children:"Email"}),t.jsxs("div",{className:"input-with-icon",children:[t.jsx("i",{"data-feather":"mail"}),t.jsx("input",{type:"text",id:"username",value:l,onChange:W=>o(W.target.value),placeholder:"username@example.com",onKeyPress:W=>W.key==="Enter"&&U(W)})]})]}),t.jsxs("div",{className:"form-group",children:[t.jsx("label",{htmlFor:"password",children:"Password"}),t.jsxs("div",{className:"input-with-icon",children:[t.jsx("i",{"data-feather":"lock"}),t.jsx("input",{type:"password",id:"password",value:u,onChange:W=>f(W.target.value),placeholder:"••••••••",onKeyPress:W=>W.key==="Enter"&&U(W)})]})]}),t.jsx("button",{className:"btn-sign-in",onClick:U,disabled:p,children:p?"Signing in...":"Sign In"}),t.jsxs("div",{className:"login-footer",children:[t.jsxs("p",{children:["Don't have an account? Contact ",t.jsx("a",{href:"#",className:"register-link",children:"BlueVision ITM"})," for account registration."]}),t.jsxs("div",{className:"footer-links",children:[t.jsxs("button",{className:"help-link",onClick:oe,type:"button",children:[t.jsx("i",{"data-feather":"help-circle"}),"Need Help?"]}),t.jsxs("button",{className:"help-link",onClick:me,type:"button",children:[t.jsx("i",{"data-feather":"lock"}),"Change Password"]}),t.jsxs("a",{href:"/forgot-password",className:"help-link",children:[t.jsx("i",{"data-feather":"key"}),"Forgot Password?"]})]})]})]})})]})}),t.jsx(nS,{isOpen:v,onClose:ie,onNavigate:pe}),t.jsx(sS,{isOpen:A,onClose:Ae,onPasswordChanged:de})]})}function lS(){return t.jsx("style",{children:`
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
      `})}function oS(){const[n,i]=w.useState(!1),l=Jr(),o=()=>{l("/login")},u=()=>{const f=document.getElementById("features");f&&f.scrollIntoView({behavior:"smooth"})};return t.jsx("header",{className:"header",children:t.jsxs("div",{className:"container header-container",children:[t.jsxs("a",{href:"#",className:"logo",onClick:f=>{f.preventDefault(),l("/")},children:[t.jsx("i",{className:"fas fa-shield-alt logo-icon"}),t.jsx("div",{className:"logo-text",children:"CRISP"})]}),t.jsx("nav",{className:`nav ${n?"nav-open":""}`,children:t.jsxs("ul",{className:"nav-links",children:[t.jsx("li",{children:t.jsx("a",{href:"#features",children:"Features"})}),t.jsx("li",{children:t.jsx("a",{href:"#benefits",children:"Benefits"})}),t.jsx("li",{children:t.jsx("a",{href:"#about",children:"About"})}),t.jsx("li",{children:t.jsx("a",{href:"#contact",children:"Contact"})})]})}),t.jsxs("div",{className:"header-actions",children:[t.jsx("button",{onClick:u,className:"btn btn-outline",children:"Request Demo"}),t.jsx("button",{onClick:o,className:"btn btn-primary",children:"Get Started"})]}),t.jsx("button",{className:"mobile-menu-toggle",onClick:()=>i(!n),children:t.jsx("i",{className:"fas fa-bars"})})]})})}function cS(){const n=Jr(),i=()=>{n("/login")};return t.jsx("section",{className:"hero",children:t.jsxs("div",{className:"container hero-container",children:[t.jsxs("div",{className:"hero-content",children:[t.jsxs("h1",{className:"hero-title",children:["Secure ",t.jsx("span",{className:"highlight",children:"Cyber Threat Intelligence"})," Sharing for Educational Institutions"]}),t.jsx("p",{className:"hero-description",children:"CRISP enables educational institutions to share anonymized threat intelligence, protecting student data while strengthening cybersecurity defenses across the education sector."}),t.jsxs("div",{className:"hero-actions",children:[t.jsxs("button",{onClick:i,className:"btn btn-primary btn-large",children:[t.jsx("i",{className:"fas fa-sign-in-alt"}),"Login to Dashboard"]}),t.jsxs("a",{href:"#features",className:"btn btn-outline btn-large",children:[t.jsx("i",{className:"fas fa-info-circle"}),"Learn More"]})]})]}),t.jsx("div",{className:"hero-visual",children:t.jsxs("div",{className:"dashboard-preview",children:[t.jsxs("div",{className:"dashboard-header",children:[t.jsxs("div",{className:"dashboard-logo",children:[t.jsx("i",{className:"fas fa-shield-alt"}),t.jsx("span",{children:"CRISP Dashboard"})]}),t.jsxs("div",{className:"dashboard-status",children:[t.jsx("span",{className:"status-dot"}),t.jsx("span",{children:"System Online"})]})]}),t.jsxs("div",{className:"dashboard-stats",children:[t.jsxs("div",{className:"stat-card",children:[t.jsx("div",{className:"stat-icon threat-icon",children:t.jsx("i",{className:"fas fa-exclamation-triangle"})}),t.jsxs("div",{className:"stat-info",children:[t.jsx("div",{className:"stat-number",children:"247"}),t.jsx("div",{className:"stat-label",children:"Active Threats"})]})]}),t.jsxs("div",{className:"stat-card",children:[t.jsx("div",{className:"stat-icon institution-icon",children:t.jsx("i",{className:"fas fa-building"})}),t.jsxs("div",{className:"stat-info",children:[t.jsx("div",{className:"stat-number",children:"45"}),t.jsx("div",{className:"stat-label",children:"Institutions"})]})]}),t.jsxs("div",{className:"stat-card",children:[t.jsx("div",{className:"stat-icon sharing-icon",children:t.jsx("i",{className:"fas fa-share-alt"})}),t.jsxs("div",{className:"stat-info",children:[t.jsx("div",{className:"stat-number",children:"1.2K"}),t.jsx("div",{className:"stat-label",children:"Shared IoCs"})]})]})]})]})})]})})}function dS(){return t.jsx("section",{id:"features",className:"features",children:t.jsxs("div",{className:"container",children:[t.jsxs("div",{className:"section-header",children:[t.jsx("h2",{children:"Powerful Features for Educational Cybersecurity"}),t.jsx("p",{children:"Discover how CRISP transforms threat intelligence sharing across educational institutions"})]}),t.jsxs("div",{className:"features-grid",children:[t.jsxs("div",{className:"feature-card",children:[t.jsx("div",{className:"feature-icon",children:t.jsx("i",{className:"fas fa-shield-alt"})}),t.jsx("h3",{className:"feature-title",children:"Secure Intelligence Sharing"}),t.jsx("p",{className:"feature-description",children:"Share threat intelligence securely between institutions while maintaining complete data anonymization and privacy protection."})]}),t.jsxs("div",{className:"feature-card",children:[t.jsx("div",{className:"feature-icon",children:t.jsx("i",{className:"fas fa-users"})}),t.jsx("h3",{className:"feature-title",children:"Trust Management"}),t.jsx("p",{className:"feature-description",children:"Build and manage trust relationships between educational institutions with granular access controls and verification systems."})]}),t.jsxs("div",{className:"feature-card",children:[t.jsx("div",{className:"feature-icon",children:t.jsx("i",{className:"fas fa-chart-line"})}),t.jsx("h3",{className:"feature-title",children:"Advanced Analytics"}),t.jsx("p",{className:"feature-description",children:"Gain insights from shared threat data with powerful analytics tools and real-time monitoring capabilities."})]}),t.jsxs("div",{className:"feature-card",children:[t.jsx("div",{className:"feature-icon",children:t.jsx("i",{className:"fas fa-bell"})}),t.jsx("h3",{className:"feature-title",children:"Real-time Alerts"}),t.jsx("p",{className:"feature-description",children:"Receive instant notifications about emerging threats relevant to your institution's security posture."})]}),t.jsxs("div",{className:"feature-card",children:[t.jsx("div",{className:"feature-icon",children:t.jsx("i",{className:"fas fa-cog"})}),t.jsx("h3",{className:"feature-title",children:"Automated Processing"}),t.jsx("p",{className:"feature-description",children:"Streamline threat intelligence workflows with automated data processing and standardized formats."})]}),t.jsxs("div",{className:"feature-card",children:[t.jsx("div",{className:"feature-icon",children:t.jsx("i",{className:"fas fa-lock"})}),t.jsx("h3",{className:"feature-title",children:"Privacy First"}),t.jsx("p",{className:"feature-description",children:"Built with privacy-by-design principles to protect sensitive educational data while enabling effective collaboration."})]})]})]})})}function uS(){return t.jsx("section",{className:"stats",children:t.jsx("div",{className:"container",children:t.jsxs("div",{className:"stats-grid",children:[t.jsxs("div",{className:"stat-item",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-university"})}),t.jsx("div",{className:"stat-number",children:"150+"}),t.jsx("div",{className:"stat-label",children:"Educational Institutions"})]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-exclamation-triangle"})}),t.jsx("div",{className:"stat-number",children:"10K+"}),t.jsx("div",{className:"stat-label",children:"Threats Detected"})]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-share-alt"})}),t.jsx("div",{className:"stat-number",children:"50K+"}),t.jsx("div",{className:"stat-label",children:"Indicators Shared"})]}),t.jsxs("div",{className:"stat-item",children:[t.jsx("div",{className:"stat-icon",children:t.jsx("i",{className:"fas fa-clock"})}),t.jsx("div",{className:"stat-number",children:"99.9%"}),t.jsx("div",{className:"stat-label",children:"Uptime Reliability"})]})]})})})}function fS(){const n=Jr(),i=()=>{n("/login")};return t.jsx("section",{className:"cta",children:t.jsx("div",{className:"container",children:t.jsxs("div",{className:"cta-content",children:[t.jsx("h2",{children:"Ready to Strengthen Your Institution's Security?"}),t.jsx("p",{children:"Join the growing network of educational institutions sharing threat intelligence to protect students, faculty, and institutional data."}),t.jsxs("div",{className:"cta-actions",children:[t.jsxs("button",{onClick:i,className:"btn btn-primary btn-large",children:[t.jsx("i",{className:"fas fa-rocket"}),"Get Started Today"]}),t.jsxs("a",{href:"#contact",className:"btn btn-outline btn-large",children:[t.jsx("i",{className:"fas fa-phone"}),"Contact Sales"]})]}),t.jsxs("div",{className:"cta-features",children:[t.jsxs("div",{className:"cta-feature",children:[t.jsx("i",{className:"fas fa-check"}),t.jsx("span",{children:"Free 30-day trial"})]}),t.jsxs("div",{className:"cta-feature",children:[t.jsx("i",{className:"fas fa-check"}),t.jsx("span",{children:"No setup fees"})]}),t.jsxs("div",{className:"cta-feature",children:[t.jsx("i",{className:"fas fa-check"}),t.jsx("span",{children:"24/7 support"})]})]})]})})})}function hS(){return t.jsx("footer",{id:"contact",className:"footer",children:t.jsxs("div",{className:"container",children:[t.jsxs("div",{className:"footer-content",children:[t.jsxs("div",{className:"footer-main",children:[t.jsxs("div",{className:"footer-logo",children:[t.jsx("i",{className:"fas fa-shield-alt logo-icon"}),t.jsx("span",{children:"CRISP"})]}),t.jsx("p",{className:"footer-description",children:"Empowering educational institutions with secure, collaborative threat intelligence sharing to build stronger cybersecurity defenses together."}),t.jsxs("div",{className:"footer-social",children:[t.jsx("a",{href:"#","aria-label":"Twitter",children:t.jsx("i",{className:"fab fa-twitter"})}),t.jsx("a",{href:"#","aria-label":"LinkedIn",children:t.jsx("i",{className:"fab fa-linkedin"})}),t.jsx("a",{href:"#","aria-label":"GitHub",children:t.jsx("i",{className:"fab fa-github"})})]})]}),t.jsxs("div",{className:"footer-section",children:[t.jsx("h4",{children:"Product"}),t.jsxs("ul",{children:[t.jsx("li",{children:t.jsx("a",{href:"#features",children:"Features"})}),t.jsx("li",{children:t.jsx("a",{href:"#pricing",children:"Pricing"})}),t.jsx("li",{children:t.jsx("a",{href:"#security",children:"Security"})}),t.jsx("li",{children:t.jsx("a",{href:"#integrations",children:"Integrations"})})]})]}),t.jsxs("div",{className:"footer-section",children:[t.jsx("h4",{children:"Resources"}),t.jsxs("ul",{children:[t.jsx("li",{children:t.jsx("a",{href:"#documentation",children:"Documentation"})}),t.jsx("li",{children:t.jsx("a",{href:"#api",children:"API Reference"})}),t.jsx("li",{children:t.jsx("a",{href:"#guides",children:"User Guides"})}),t.jsx("li",{children:t.jsx("a",{href:"#support",children:"Support Center"})})]})]}),t.jsxs("div",{className:"footer-section",children:[t.jsx("h4",{children:"Company"}),t.jsxs("ul",{children:[t.jsx("li",{children:t.jsx("a",{href:"#about",children:"About Us"})}),t.jsx("li",{children:t.jsx("a",{href:"#careers",children:"Careers"})}),t.jsx("li",{children:t.jsx("a",{href:"#blog",children:"Blog"})}),t.jsx("li",{children:t.jsx("a",{href:"#contact",children:"Contact"})})]})]})]}),t.jsx("div",{className:"footer-bottom",children:t.jsxs("div",{className:"footer-legal",children:[t.jsx("p",{children:"© 2024 CRISP. All rights reserved."}),t.jsxs("div",{className:"footer-links",children:[t.jsx("a",{href:"#privacy",children:"Privacy Policy"}),t.jsx("a",{href:"#terms",children:"Terms of Service"}),t.jsx("a",{href:"#cookies",children:"Cookie Policy"})]})]})})]})})}function mS(){return t.jsxs("div",{className:"landing-page",children:[t.jsx("style",{children:`
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
        `}),t.jsx(oS,{}),t.jsx(cS,{}),t.jsx(uS,{}),t.jsx(dS,{}),t.jsx(fS,{}),t.jsx(hS,{})]})}function pS(){const[n,i]=w.useState(""),[l,o]=w.useState(!1),[u,f]=w.useState(!1),m=async x=>{x.preventDefault(),f(!0),await new Promise(p=>setTimeout(p,1e3)),o(!0),f(!1)};return t.jsx("div",{style:{minHeight:"100vh",display:"flex",justifyContent:"center",alignItems:"center",background:"#f5f7fa"},children:t.jsx("div",{style:{background:"white",padding:"2rem",borderRadius:"8px",maxWidth:"400px",width:"90%",boxShadow:"0 4px 6px rgba(0, 0, 0, 0.1)"},children:l?t.jsxs(t.Fragment,{children:[t.jsx("h2",{children:"Check Your Email"}),t.jsxs("p",{style:{marginBottom:"1.5rem",color:"#666"},children:["We've sent a password reset link to ",n]}),t.jsx("a",{href:"/login",style:{color:"#0056b3"},children:"Back to Login"})]}):t.jsxs(t.Fragment,{children:[t.jsx("h2",{children:"Forgot Password"}),t.jsx("p",{style:{marginBottom:"1.5rem",color:"#666"},children:"Enter your email address and we'll send you a link to reset your password."}),t.jsxs("form",{onSubmit:m,children:[t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{children:"Email Address"}),t.jsx("input",{type:"email",value:n,onChange:x=>i(x.target.value),style:{width:"100%",padding:"0.75rem",marginTop:"0.25rem",border:"1px solid #e2e8f0",borderRadius:"4px"},required:!0})]}),t.jsx("button",{type:"submit",disabled:u,style:{width:"100%",padding:"0.75rem",background:"#0056b3",color:"white",border:"none",borderRadius:"4px",cursor:"pointer"},children:u?"Sending...":"Send Reset Link"})]}),t.jsx("div",{style:{marginTop:"1rem",textAlign:"center"},children:t.jsx("a",{href:"/login",style:{color:"#0056b3"},children:"Back to Login"})})]})})})}function gS(){const[n,i]=w.useState(""),[l,o]=w.useState(""),[u,f]=w.useState(!1),[m,x]=w.useState(!1),[p,h]=w.useState(""),v=async y=>{if(y.preventDefault(),x(!0),h(""),n!==l){h("Passwords do not match"),x(!1);return}await new Promise(N=>setTimeout(N,1e3)),f(!0),x(!1)};return t.jsx("div",{style:{minHeight:"100vh",display:"flex",justifyContent:"center",alignItems:"center",background:"#f5f7fa"},children:t.jsx("div",{style:{background:"white",padding:"2rem",borderRadius:"8px",maxWidth:"400px",width:"90%",boxShadow:"0 4px 6px rgba(0, 0, 0, 0.1)"},children:u?t.jsxs(t.Fragment,{children:[t.jsx("h2",{children:"Password Reset Complete"}),t.jsx("p",{style:{marginBottom:"1.5rem",color:"#666"},children:"Your password has been successfully reset."}),t.jsx("a",{href:"/login",style:{color:"#0056b3"},children:"Go to Login"})]}):t.jsxs(t.Fragment,{children:[t.jsx("h2",{children:"Reset Password"}),t.jsx("p",{style:{marginBottom:"1.5rem",color:"#666"},children:"Enter your new password below."}),p&&t.jsx("div",{style:{color:"red",marginBottom:"1rem"},children:p}),t.jsxs("form",{onSubmit:v,children:[t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{children:"New Password"}),t.jsx("input",{type:"password",value:n,onChange:y=>i(y.target.value),style:{width:"100%",padding:"0.75rem",marginTop:"0.25rem",border:"1px solid #e2e8f0",borderRadius:"4px"},required:!0})]}),t.jsxs("div",{style:{marginBottom:"1rem"},children:[t.jsx("label",{children:"Confirm New Password"}),t.jsx("input",{type:"password",value:l,onChange:y=>o(y.target.value),style:{width:"100%",padding:"0.75rem",marginTop:"0.25rem",border:"1px solid #e2e8f0",borderRadius:"4px"},required:!0})]}),t.jsx("button",{type:"submit",disabled:m,style:{width:"100%",padding:"0.75rem",background:"#0056b3",color:"white",border:"none",borderRadius:"4px",cursor:"pointer"},children:m?"Resetting...":"Reset Password"})]})]})})})}function xS(){var y;const[n,i]=w.useState(!1),[l,o]=w.useState(!0),[u,f]=w.useState(null),m=Jr();w.useEffect(()=>{(()=>{try{const S=localStorage.getItem("crisp_auth_token"),A=localStorage.getItem("crisp_user");if(S&&A){const z=JSON.parse(A);f(z),i(!0),console.log("Session validated for user:",z.username),console.log("User admin fields on session restore:",{is_admin:z.is_admin,is_staff:z.is_staff,role:z.role})}}catch(S){console.error("Error validating session:",S),localStorage.removeItem("crisp_auth_token"),localStorage.removeItem("crisp_user")}finally{o(!1)}})()},[]);const x=N=>{var S;console.log("Login successful for user:",N.user.username),console.log("Full auth data received:",N),console.log("Token received:",(S=N.tokens)!=null&&S.access?N.tokens.access.substring(0,50)+"...":"No token"),console.log("User admin status:",{is_admin:N.user.is_admin,is_staff:N.user.is_staff,role:N.user.role});try{localStorage.setItem("crisp_auth_token",N.tokens.access),localStorage.setItem("crisp_refresh_token",N.tokens.refresh),localStorage.setItem("crisp_user",JSON.stringify(N.user)),f(N.user),i(!0),m("/dashboard",{replace:!0})}catch(A){console.error("Error storing authentication data:",A),alert("Login error: Unable to store session data")}},p=N=>{console.log("Registration successful for user:",N.user.username);try{localStorage.setItem("crisp_auth_token",N.tokens.access),localStorage.setItem("crisp_refresh_token",N.tokens.refresh),localStorage.setItem("crisp_user",JSON.stringify(N.user)),f(N.user),i(!0)}catch(S){console.error("Error storing authentication data:",S),alert("Registration error: Unable to store session data")}},h=()=>{console.log("Logging out user"),localStorage.removeItem("crisp_auth_token"),localStorage.removeItem("crisp_user"),i(!1),f(null),m("/",{replace:!0})};if(l)return t.jsxs("div",{style:{display:"flex",justifyContent:"center",alignItems:"center",height:"100vh",flexDirection:"column",gap:"20px",fontFamily:"Segoe UI, Tahoma, Geneva, Verdana, sans-serif"},children:[t.jsx("div",{style:{width:"40px",height:"40px",border:"4px solid #f3f3f3",borderTop:"4px solid #0056b3",borderRadius:"50%",animation:"spin 1s linear infinite"}}),t.jsx("p",{style:{color:"#718096",fontSize:"16px"},children:"Checking authentication..."}),t.jsx("style",{children:`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `})]});const v=u&&(u.is_admin===!0||u.is_staff===!0||u.role&&["admin","administrator","bluevisionadmin","superuser","super_user"].includes(u.role.toLowerCase())||u.role&&u.role.toLowerCase().includes("admin"));return console.log("Auth state:",{isAuthenticated:n,isAdmin:v,userData:u,adminChecks:u?{is_admin:u.is_admin,is_staff:u.is_staff,role:u.role,roleLower:(y=u.role)==null?void 0:y.toLowerCase(),adminRoleMatch:u.role&&["admin","administrator","bluevisionadmin","superuser","super_user"].includes(u.role.toLowerCase()),legacyAdminMatch:u.role&&u.role.toLowerCase().includes("admin")}:null}),t.jsxs(Dy,{children:[t.jsx(fn,{path:"/",element:t.jsx(mS,{})}),t.jsx(fn,{path:"/construction",element:t.jsx(zx,{})}),t.jsx(fn,{path:"/login",element:n?t.jsx(Nn,{to:"/dashboard",replace:!0}):t.jsx(rS,{onLoginSuccess:x})}),t.jsx(fn,{path:"/forgot-password",element:n?t.jsx(Nn,{to:"/dashboard",replace:!0}):t.jsx(pS,{})}),t.jsx(fn,{path:"/reset-password",element:n?t.jsx(Nn,{to:"/dashboard",replace:!0}):t.jsx(gS,{})}),t.jsx(fn,{path:"/register-user",element:n?v?t.jsx(gg,{onRegisterSuccess:()=>{alert("User registered successfully!"),m("/dashboard")},switchView:()=>m("/dashboard")}):t.jsx(Nn,{to:"/dashboard",replace:!0}):t.jsx(gg,{onRegisterSuccess:p,switchView:()=>m("/login")})}),t.jsx(fn,{path:"/dashboard",element:n?t.jsx(Jd,{user:u,onLogout:h,isAdmin:v}):t.jsx(Nn,{to:"/login",replace:!0})}),t.jsx(fn,{path:"/user-management",element:n?v?t.jsx(Jd,{user:u,onLogout:h,isAdmin:v}):t.jsx(Nn,{to:"/dashboard",replace:!0}):t.jsx(Nn,{to:"/login",replace:!0})}),t.jsx(fn,{path:"/trust-management",element:n?(u==null?void 0:u.role)==="publisher"||(u==null?void 0:u.role)==="BlueVisionAdmin"||v?t.jsx(Jd,{user:u,onLogout:h,isAdmin:v}):t.jsx(Nn,{to:"/dashboard",replace:!0}):t.jsx(Nn,{to:"/login",replace:!0})}),t.jsx(fn,{path:"*",element:t.jsx(Nn,{to:"/",replace:!0})})]})}window.addEventListener("popstate",()=>{localStorage.getItem("crisp_auth_token")||window.location.reload()});function vS(){return t.jsx(Oy,{future:{v7_startTransition:!0,v7_relativeSplatPath:!0},children:t.jsx(xS,{})})}Fv.createRoot(document.getElementById("root")).render(t.jsx(Ui.StrictMode,{children:t.jsx(vS,{})}));
