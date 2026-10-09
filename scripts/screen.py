import sys, glob, os
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE)
from novelkit import prose_scan as PS, continuity as CT, bible as B
WORK=os.path.join(HERE,'..','_work')
draft=sorted(glob.glob(os.path.join(WORK,'draft','ch*.md')))
bibpath=os.path.join(WORK,'what-they-made-me_bible.md')
bib=B.load(bibpath)
# PROSE
ph=0; hard_total=0; worst=[]
for f in draft:
    txt=open(f,encoding='utf-8').read()
    rep=PS.scan(txt)
    hf=rep.get('hard_flags',[])
    hard_total+=len(hf)
    if not rep.get('passed',True): ph+=1
    if hf: worst.append((len(hf),os.path.basename(f),hf))
print(f"PROSE: {len(draft)} ch | prose_scan FAIL: {ph} | total HARD: {hard_total}")
worst.sort(reverse=True)
for hf,name,flags in worst[:12]:
    print(f"  {name}: {hf} HARD -> {flags[:3]}")
# CONTINUITY (full manuscript concatenated)
full="\n\n".join(open(f,encoding='utf-8').read() for f in draft)
try:
    crep=CT.check(full, bib)
    iss=crep.get('issues',crep) if isinstance(crep,dict) else crep
    print("\nCONTINUITY keys:", list(crep.keys()) if isinstance(crep,dict) else type(crep))
    print("CONTINUITY passed:", crep.get('passed') if isinstance(crep,dict) else 'n/a')
    import json
    print(json.dumps(crep.get('issues',{}),indent=1)[:1500] if isinstance(crep,dict) else '')
except Exception as e:
    print("continuity error:",e)
