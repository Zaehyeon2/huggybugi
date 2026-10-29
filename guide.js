function a(t,i){if(t.nodeType===Node.TEXT_NODE)return(t.textContent??"").replace(/\s+/g," ");if(!(t instanceof HTMLElement)||t.tagName==="IMG")return"";let e=[...t.childNodes].map(n=>a(n,i)).join("");return t.tagName==="CODE"?`\`${t.textContent}\``:t.tagName==="STRONG"?`**${e}**`:t.tagName==="BR"?" ":t instanceof HTMLAnchorElement?`[${e.trim()}](${new URL(t.getAttribute("href")??"",i)})`:e}function s(t,i){let e=t.tagName,n=r=>a(r,i).trim();if(/^H[1-3]$/.test(e))return`${"#".repeat(Number(e[1]))} ${n(t)}`;if(e==="PRE")return`\`\`\`
${t.textContent?.trimEnd()}
\`\`\``;if(e==="UL"||e==="OL")return[...t.children].map((r,c)=>`${e==="OL"?`${c+1}.`:"-"} ${n(r)}`).join(`
`);if(e==="TABLE"){let r=[...t.querySelectorAll("tr")].map(u=>`| ${[...u.children].map(l=>n(l).replace(/\|/g,"\\|")).join(" | ")} |`);if(!r.length)return"";let c=t.querySelector("tr")?.children.length??0;return r.splice(1,0,`|${" --- |".repeat(c)}`),r.join(`
`)}return e==="P"?n(t):""}function m(t,i){return`${[...t.children].filter(n=>!n.matches("#copy-md")&&!n.querySelector("#copy-md")).map(n=>s(n,i)).filter(Boolean).join(`

`)}
`}var o=document.querySelector("#copy-md"),f=o?.textContent??"";o?.addEventListener("click",async()=>{let t=document.querySelector("main");if(t){try{await navigator.clipboard.writeText(m(t,location.href)),o.textContent="\uBCF5\uC0AC\uD588\uC5B4\uC694"}catch{o.textContent="\uBCF5\uC0AC\uD558\uC9C0 \uBABB\uD588\uC5B4\uC694"}setTimeout(()=>{o.textContent=f},1500)}});
