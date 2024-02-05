(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[948],{4440:function(e,t){var r;/*!
	Copyright (c) 2018 Jed Watson.
	Licensed under the MIT License (MIT), see
	http://jedwatson.github.io/classnames
*/!function(){"use strict";var s={}.hasOwnProperty;function classNames(){for(var e=[],t=0;t<arguments.length;t++){var r=arguments[t];if(r){var l=typeof r;if("string"===l||"number"===l)e.push(r);else if(Array.isArray(r)){if(r.length){var n=classNames.apply(null,r);n&&e.push(n)}}else if("object"===l){if(r.toString!==Object.prototype.toString&&!r.toString.toString().includes("[native code]")){e.push(r.toString());continue}for(var o in r)s.call(r,o)&&r[o]&&e.push(o)}}}return e.join(" ")}e.exports?(classNames.default=classNames,e.exports=classNames):void 0!==(r=(function(){return classNames}).apply(t,[]))&&(e.exports=r)}()},8153:function(e,t,r){Promise.resolve().then(r.bind(r,385))},385:function(e,t,r){"use strict";r.r(t),r.d(t,{default:function(){return Home}});var s=r(7437);r(2265);var l=r(2863),n=r.n(l),o=r(4440),a=r.n(o);function Home(){return(0,s.jsxs)("main",{className:"flex min-h-screen flex-col items-stretch gap-0",children:[(0,s.jsx)("div",{id:"aboveFold",className:"flex flex-col justify-center items-center max-w-full w-full min-h-screen  overflow-hidden",children:(0,s.jsxs)("div",{className:"flex flex-col items-center gap-2 md:gap-10 pb-12 md:px-6 lg:px-10 w-full text-center ",children:[(0,s.jsxs)("div",{className:"flex  pt-12 flex-col gap-1 items-center relative z-10",children:[(0,s.jsx)("a",{href:"https://roboflow.com",target:"_blank",children:(0,s.jsx)("img",{src:"/roboflow_full_logo_color.svg",alt:"Roboflow Logo",width:200})}),(0,s.jsx)("h1",{className:"font-bold text-gray-900 text-4xl md:text-6xl",children:"Inference"}),(0,s.jsx)("h2",{className:a()(n().className,"font-bold text-base text-purple-500"),children:"developer-friendly vision inference"})]}),(0,s.jsxs)("div",{className:"flex w-full xl:w-[1000px] max-w-[1000px] bg-white  py-10 bg-opacity-30 border border-white rounded justify-start items-center flex-col px-3 md:px-6 xl:px-12 gap-2 lg:gap-4",children:[(0,s.jsx)("h3",{className:"px-2 lg:px-0 text-xl md:text-3xl text-left  font-semibold  text-gray-900 w-full flex pb-3 ",children:"Jump Into an Inference Enabled Notebook"}),(0,s.jsxs)("div",{className:"flex w-full flex-row gap-3 ",children:[(0,s.jsx)("span",{children:"•"}),(0,s.jsxs)("span",{className:"w-full leading-loose justify-start xl:leading-relaxed text-sm lg:text-base items-baseline gap-0 text-left",children:["To use the built in notebooks in Inference, you need to enable the notebooks feature via the environment variable ",(0,s.jsx)("span",{className:"font-mono text-xs lg:text-sm font-semibold py-1 px-2 border border-gray-400 text-gray-700 rounded",children:"NOTEBOOK_ENABLED"})," ."]})]}),(0,s.jsxs)("div",{className:"flex py-3 flex-row gap-3 ",children:[(0,s.jsx)("span",{children:"•"}),(0,s.jsxs)("span",{className:"w-full leading-loose lg:leading-7 text-sm lg:text-base items-baseline gap-0 text-left",children:["To do this, use the ",(0,s.jsx)("span",{className:"font-mono whitespace-break-spaces break-normal  text-xs lg:text-[13px] bg-black bg-opacity-90 font-normal py-1 px-2 border border-gray-900 mx-1 text-white rounded",children:"--dev"})," flag with the inference-cli: ",(0,s.jsx)("span",{className:"font-mono break-normal whitespace-break-spaces text-xs lg:text-[13px] bg-black bg-opacity-90 font-normal py-1 px-2 border border-gray-900 mx-1 text-white rounded",children:"inference server start --dev"}),". Or, update your docker run command with the argument ",(0,s.jsx)("span",{className:"font-mono whitespace-break-spaces text-xs break-normal lg:text-[13px] bg-black bg-opacity-90 font-normal py-1 px-2 border border-gray-900 mx-1 text-white rounded",children:"-e NOTEBOOK_ENABLED=true"}),"."]})]}),(0,s.jsxs)("a",{href:"notebook/start",className:"mt-6 w-max flex flex-row text-white items-center justify-center text-sm lg:text-base rounded py-3 px-8 hover:bg-purple-600 transition duration-400  bg-purple-500 ",target:"_blank",children:["Launch Notebook ",(0,s.jsx)("div",{className:"pl-2 font-bold",children:"→"})]})]})]})}),(0,s.jsx)("div",{id:"dividerGradient",className:"h-0.5 sm:h-1 w-full",children:" "})]})}},2863:function(e){e.exports={style:{fontFamily:"'__Roboto_Mono_829659', '__Roboto_Mono_Fallback_829659'",fontStyle:"normal"},className:"__className_829659"}},622:function(e,t,r){"use strict";/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var s=r(2265),l=Symbol.for("react.element"),n=(Symbol.for("react.fragment"),Object.prototype.hasOwnProperty),o=s.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner,a={key:!0,ref:!0,__self:!0,__source:!0};function q(e,t,r){var s,i={},c=null,x=null;for(s in void 0!==r&&(c=""+r),void 0!==t.key&&(c=""+t.key),void 0!==t.ref&&(x=t.ref),t)n.call(t,s)&&!a.hasOwnProperty(s)&&(i[s]=t[s]);if(e&&e.defaultProps)for(s in t=e.defaultProps)void 0===i[s]&&(i[s]=t[s]);return{$$typeof:l,type:e,key:c,ref:x,props:i,_owner:o.current}}t.jsx=q,t.jsxs=q},7437:function(e,t,r){"use strict";e.exports=r(622)}},function(e){e.O(0,[971,864,744],function(){return e(e.s=8153)}),_N_E=e.O()}]);