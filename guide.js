function o(t){if(t.nodeType===Node.TEXT_NODE)return(t.textContent??"").replace(/\s+/g," ");if(!(t instanceof HTMLElement)||t.tagName==="IMG")return"";let e=[...t.childNodes].map(o).join("");return t.tagName==="CODE"?`\`${t.textContent}\``:t.tagName==="STRONG"?`**${e}**`:t.tagName==="BR"?" ":t instanceof HTMLAnchorElement?`[${e.trim()}](${new URL(t.getAttribute("href")??"",location.href)})`:e}function m(t){let e=t.tagName;if(/^H[1-3]$/.test(e))return`${"#".repeat(Number(e[1]))} ${o(t).trim()}`;if(e==="PRE")return`\`\`\`
${t.textContent?.trimEnd()}
\`\`\``;if(e==="UL"||e==="OL")return[...t.children].map((n,r)=>`${e==="OL"?`${r+1}.`:"-"} ${o(n).trim()}`).join(`
`);if(e==="TABLE"){let n=[...t.querySelectorAll("tr")].map(c=>`| ${[...c.children].map(a=>o(a).trim().replace(/\|/g,"\\|")).join(" | ")} |`),r=t.querySelector("tr")?.children.length??0;return n.splice(1,0,`|${" --- |".repeat(r)}`),n.join(`
`)}return e==="P"?o(t).trim():""}var i=document.querySelector("#copy-md");i?.addEventListener("click",async()=>{let t=document.querySelector("main");if(!t)return;let e=[...t.children].filter(r=>r!==i&&!r.contains(i)).map(m).filter(Boolean).join(`

`);await navigator.clipboard.writeText(`${e}
`);let n=i.textContent;i.textContent="\uBCF5\uC0AC\uD588\uC5B4\uC694",setTimeout(()=>{i.textContent=n},1500)});
