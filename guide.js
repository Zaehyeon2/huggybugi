function i(t){if(t.nodeType===Node.TEXT_NODE)return(t.textContent??"").replace(/\s+/g," ");if(!(t instanceof HTMLElement)||t.tagName==="IMG")return"";let e=[...t.childNodes].map(i).join("");return t.tagName==="CODE"?`\`${t.textContent}\``:t.tagName==="STRONG"?`**${e}**`:t.tagName==="BR"?" ":t instanceof HTMLAnchorElement?`[${e.trim()}](${new URL(t.getAttribute("href")??"",location.href)})`:e}function m(t){let e=t.tagName;if(/^H[1-3]$/.test(e))return`${"#".repeat(Number(e[1]))} ${i(t).trim()}`;if(e==="PRE")return`\`\`\`
${t.textContent?.trimEnd()}
\`\`\``;if(e==="UL"||e==="OL")return[...t.children].map((n,o)=>`${e==="OL"?`${o+1}.`:"-"} ${i(n).trim()}`).join(`
`);if(e==="TABLE"){let n=[...t.querySelectorAll("tr")].map(c=>`| ${[...c.children].map(a=>i(a).trim().replace(/\|/g,"\\|")).join(" | ")} |`),o=t.querySelector("tr")?.children.length??0;return n.splice(1,0,`|${" --- |".repeat(o)}`),n.join(`
`)}return e==="P"?i(t).trim():""}var r=document.querySelector("#copy-md"),u=r?.textContent??"";r?.addEventListener("click",async()=>{let t=document.querySelector("main");if(!t)return;let e=[...t.children].filter(n=>n!==r&&!n.contains(r)).map(m).filter(Boolean).join(`

`);try{await navigator.clipboard.writeText(`${e}
`),r.textContent="\uBCF5\uC0AC\uD588\uC5B4\uC694"}catch{r.textContent="\uBCF5\uC0AC\uD558\uC9C0 \uBABB\uD588\uC5B4\uC694"}setTimeout(()=>{r.textContent=u},1500)});
