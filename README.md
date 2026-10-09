# novel-kit

A [Claude Code](https://docs.claude.com/en/docs/claude-code) **Agent Skill** for reliable long-form fiction — drafting and editing novels. It wraps a language model's weak spots when writing fiction — *it praises its own prose without reading it cold, defaults to clichéd most-probable phrasing, contradicts its own canon over tens of thousands of words, and writes episodic scenes where nothing escalates* — inside deterministic scanners and a strict **design → draft → inspect → cold-read** loop.

> Stdlib-only Python (3.10+, also runs on 3.14). No API keys, no dependencies.

## Why

There is no objective render of a novel. The two things that come closest, and that this skill is built around:

- **Canon is machine-checkable.** Commit a fact to the story bible once; the continuity checker flags every later contradiction — an eye colour that changes, a name whose spelling drifts, a planted gun that never fires.
- **A cold reader is the proxy for looking.** A fresh subagent that never saw the plan reads the prose blind and reports where it got bored, confused, or felt the words before. The agent praising its own draft is not evidence.

## The mandatory loop

```
GENRE PRE-PROCESS  classify the premise, research the genre's reader promise,
                   conventions and obligatory scenes
DESIGN (plot first) scaffold a plan + story bible: logline, structure beats, a scene
                   ledger where every scene MOVES a character, subplots, chapters,
                   setup/payoff, character baselines incl. physicality, worldbuilding
                   — plan/character/structure/plot/chapters/flags gates must PASS
DRAFT              write a scene against the plan + bible
SCAN               prose_scan (too much: clichés, filter words, adverbs, monotone rhythm)
                   texture   (too little: thin, white-room, under-rendered prose)
INSPECT            report = prose + texture + continuity + character + voice + scene
                   moves + plot + chapters + flags
COLD READ          blind reader subagents, character-fidelity audit, voice blind-tag test
REVISE → REPEAT    until the gates pass AND a cold reader says it works
```

Passing the scanners is **necessary, not sufficient** — a scene can be clean of smells and still be boring. The cold read decides.

## Quick start

Copy the folder into `~/.claude/skills/novel-kit/` and Claude Code picks it up for any fiction task. The toolkit also runs on its own:

```bash
cd scripts
python -m novelkit.prose_scan ../references/samples/bad.md     # see the scanner flag a bad sample
python plan_novel.py "<premise>" --title "..." --protagonist "..."   # scaffold a plan + bible
python -m novelkit.report scene.md _work/slug_bible.md _work/slug_plan.md --genre fantasy
```

Always run modules with `python -m novelkit.<mod>` from `scripts/` (the package reconfigures stdout to UTF-8 so the report glyphs don't crash a Windows console).

## The toolkit (`scripts/novelkit/`)

`prose_scan` (cliché/filter-word/adverb/intensifier densities, impossible dialogue tags, rhythm), `texture` (genre-profiled richness floor), `continuity` (canon contradictions against the bible), `character` (baseline gate), `voice` (dialogue distinctiveness), `structure` (scene moves + escalation), `plot` (arc payoff), `chapters` (long multi-scene chapters, subplots that span), `flags` (typed character-flag lifecycle), `plan` (design gate), `genre` (premise classifier), `critique`, `debug`, `report` (everything at once).

## Layout

```
SKILL.md          the skill contract + routing
scripts/novelkit/ the Python toolkit
scripts/          plan_novel.py (scaffold), screen.py, emit_issues.py
sops/             step-by-step procedures (new novel, edit manuscript, scene, cold read, …)
references/       craft notes, genre profiles, cliché baseline, failure catalog, samples
LEARNINGS.md      lessons recorded from real runs
```

Working files go in `_work/` and scratch in `_tmp/`; both are gitignored.

## Related

[blender-kit](https://github.com/someamount2190/blender-kit) and [godot-kit](https://github.com/someamount2190/godot-kit) apply the same build → inspect → learn pattern to 3D and game work.

## Support

If novel-kit saved you a revision pass, tips are welcome at this EVM address (ETH, USDC, etc. on Ethereum, Base, Arbitrum, Optimism or Polygon):

`0xD3b3d18C871e7dd36489915A6dd83a32eFD7829f`

## License

MIT
