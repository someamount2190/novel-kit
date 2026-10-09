import sys,os,glob,re
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from novelkit import prose_scan as PS, continuity as CT, bible as B
WORK=os.path.join(HERE,'..','_work')
os.makedirs(os.path.join(WORK,'issues'),exist_ok=True)
bib=B.load(os.path.join(WORK,'what-they-made-me_bible.md'))
EXPR={'dark','pale','light','bright','wide','warm','cold','soft','hard','flat','level','sharp','steady'}
draft=sorted(glob.glob(os.path.join(WORK,'draft','ch*.md')))
nfail=0
for f in draft:
    base=os.path.basename(f); txt=open(f,encoding='utf-8').read()
    pr=PS.scan(txt); hard=pr.get('hard_flags',[])
    cr=CT.check(txt,bib)
    attrs=[]
    for a in cr['findings'].get('attribute',[]):
        found=[x for x in a['found'] if x not in EXPR]
        if found:
            attrs.append(f"{a['character']} {a['attr']} should be '{a['canon']}' but text near line shows {found}: \"{a['text'][:90].strip()}\"")
    lines=[]
    if hard:
        lines.append("PROSE HARD FLAGS (fix every one):")
        for h in hard: lines.append("  - "+str(h))
    if attrs:
        lines.append("CANON COLOUR CONTRADICTIONS (make sure the RIGHT character has the canon colour; some may be the wrong character's colour bleeding in):")
        for a in attrs: lines.append("  - "+a)
    if lines: nfail+=1
    open(os.path.join(WORK,'issues',base.replace('.md','.txt')),'w',encoding='utf-8').write("\n".join(lines) if lines else "NO HARD ISSUES — light polish only.")
print("issue files written for",len(draft),"chapters;",nfail,"have hard issues")
