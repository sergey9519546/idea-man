# Engine Science — why the workflow is built this way

This reference explains research-motivated working hypotheses, not proof that every
plugin rule is measured or effective. Human/group and model studies have different
tasks and limits. Apply recognition-playbook.md and scoring-calibration.md first;
validate adaptations on the actual task rather than treating citations as mandates.

## Contents
1. The two failure modes this engine exists to beat
2. Generation rules (G1–G9)
3. Selection rules (S1–S8)
4. Failure modes → mitigations table
5. What the evidence does NOT support (honesty notes)
6. Sources

---

## 1. The two failure modes

**Typicality risk.** Studies of preference training, cross-model convergence and
creative summarization motivate checking for homogeneous or conventional output
(Zhang et al. 2025; Jiang et al., NeurIPS 2025 "Artificial Hivemind"; Keon et al. 2025).
This is not evidence that every first answer is a cliché or that a conventional answer
is wrong. Inspect the actual task and result before expanding generation.

**Self-flattery.** Models recognise and prefer their own outputs (Panickssery et al.
2024), can change verdicts when option order changes, and can reward length. Intrinsic
self-correction failed in studied reasoning settings (Huang et al. 2024). These are
reasons to seek task-appropriate external checks, not proof that every self-review fails
or that a second model guarantees correct judgment.

Everything below attacks one of these two.

---

## 2. Generation rules

**G1. Optional warm-up, no automatic exclusion.** Human serial-order findings suggest
trying beyond initial responses during expansive exploration. They do not establish a
fixed three-idea discard rule for LLMs or this plugin. Compare early and later ideas
against the brief; retain any strong candidate regardless of generation order.

**G2. Explore while useful differences emerge.** Human productivity and hybrid-process
studies motivate trying more than the first plausible answer. More draws do not guarantee
a better usable result, particularly when outputs are correlated. These studies do not
establish raw-volume floors for SPARK, FULL or ROOM. Expand only when another pass can
add a distinct mechanism or resolve a specified uncertainty; stop at the requested scope,
repetition or an evidence boundary.

**G3. Independent contexts, then pool.** Pooled solo work produces about twice the ideas of
interacting groups (Diehl & Stroebe 1987), and building on each other's ideas did not
improve quality (Girotra et al.). Ideas already in context anchor the next ones. In ROOM
mode, when authorized and useful, give each separate thinker only its bounded brief and
needed evidence; omit other candidates before pooling. Inspect what was actually shared:
a role label or instruction not to read earlier answers does not erase shared context.
In single-context mode, separate passes can organize work but remain non-independent.

**G4. Task-fit method diversity.** Use zero to three methods as assigned by the
recognition playbook; honor a requested single method. Contrasting families may help
expansive exploration, but cited studies do not validate a mandatory three-method
minimum or this plugin's effectiveness. Report empirical limits.

**G5. Optional experimental tail exploration.** Zhang et al. (2025) reported
creative diversity and rating improvements in the study's verbalized-sampling setting;
those results do not validate this plugin or establish real proposal probabilities.
For expansive exploration, optionally contrast familiar mechanisms with less typical
ones. A five-plus-five or probability-threshold prompt is an experimental exercise,
not a required procedure or output count. The user's requested count prevails.
Do not fabricate probabilities for what a typical team would propose; use qualitative
rarity hypotheses unless probabilities have an empirical basis, and label uncertainty.

**G6. Change the structure, never just say "be different".** Feeding a model
similarity feedback produced the *least* diverse output of 35 strategies tested
(Meincke et al.). When ideas start repeating, switch method, add a constraint, or ban
the mechanisms already used. Do not merely exhort.

**G7. Deduplicate by mechanism, not wording.** Idea-generation studies motivate checking
conceptual repetition, not a universal duplication rate for this plugin. Compare the core
intervention, causal relation and changed experience. Different names or polish can
conceal the same move. Repetition without useful distinction calls for a changed
operation or frame; no fixed percentage is needed.

**G8. Analogy by relation, not mandatory distance.** Analogy research motivates different
source domains with task-dependent tradeoffs. Use a distant source only if it helps the
bottleneck. Map roles and causal relations, derive a mechanism, then inspect mismatch
and feasibility. No far-probe quota follows.

**G9. Constraints as deliberate experiments.** Constraint studies motivate a focused
restriction that changes the search space, not a universal constraint count for model
ideation. Preserve hard requirements. Vary soft preferences only within scope; check
the function each restriction removes and whether the result still serves the goal.

**Incubation analogue.** Incubation has a real but modest effect, larger for divergent
problems and after solid preparation; rest beats a demanding filler task (Sio & Ormerod
2009). For an LLM the analogue is: finish a thorough framing pass, then start the next
generation pass from a clean restatement (brief + insight + constraints, without the
earlier ideas) plus one unrelated stimulus. This is an analogy, not proven for models.

**Seed from the human.** AI ideas helped less-creative writers but not highly creative
ones, and homogenised group output (Doshi & Hauser 2024); help also failed to transfer
to unaided work (Kumar et al. 2025). With a strong creative user, invite their raw hunches
and enter them into the pool as equals; offer provocations, not only finished concepts.

---

## 3. Selection rules

**S1. The judge is not the author.** Use a separate critic context that sees only the
brief, the insight and the anonymised ideas, never the generation reasoning (rationale:
self-preference, self-correction failure). In Claude Code / Cowork, that is the
`idea-critic` subagent. Without isolated agents, normalize and re-read for a sequential self-review; disclose
that it is not blind and cannot remove shared-context bias. Agent dispatch depends on
host capability, authorization and useful information value.

**S2. Reduce irrelevant presentation bias.** For concept comparison, use equivalent
evidence and concise neutral summaries where useful (idea, experience, mechanism).
Length and polish can bias judges (Zheng et al. 2023). Preserve access to the actual
artifact: voice, detail and form may themselves be criteria, and normalization must not
remove evidence or become an unrequested rewrite of the user's work.

**S3. Absolute scores triage; pairwise comparison ranks.** 1–10 rubric scores are fine for
cutting a long list to a shortlist (coarse agreement with humans is comparable for single
and pairwise grading). For the finalists, compare head-to-head: pairwise ranking agrees
better with humans than direct scoring (Liu et al. 2024), and tournaments were used by Si
et al. and Google's AI co-scientist (Gottweis et al. 2025).

**S4. Check order sensitivity when it could affect a judgment.** For consequential,
subjective or close pairwise judgments, compare neutral A-vs-B and B-vs-A when useful
(Zheng et al.; Wang et al. 2024). A split verdict is inconclusive; inspect evidence or
report the tie. Deterministic calculations and tiny faithful edits need their actual
correctness checks, not an obligatory second preference comparison.

**S5. Novelty, usefulness and feasibility are separate axes.** The standard definition of
creativity is originality *and* effectiveness (Runco & Jaeger 2012; Stein 1953). Novelty
and immediate usability trade off (Franke et al.). Never let a brilliant-but-impossible
idea win on a blended score; feasibility is a gate (can it be made with the real budget,
team, tools and time?).

**S6. Name the closest existing thing.** "Novel" means novel relative to the judge's
knowledge. Every finalist states the nearest existing work; if web search is available,
check it before claiming originality.

**S7. Preserve decision authority.** Judge agreement in particular studies is not a
reliability estimate for this plugin. Present requested options and meaningful tradeoffs,
making unresolved evidence clear. Recommend or select only within delegated authority.
Do not develop or commit an unselected recommendation merely because it ranked first.
No universal finalist count follows from these studies.

**S8. Pre-mortem, then argue the alternative.** Imagining a failure as already having
happened made people generate about 30% more reasons for it (Mitchell, Russo &
Pennington 1989) and reduced overconfidence (Veinott, Klein & Wiggins 2010). Note the 30%
is about the *number* of reasons generated, not their accuracy. For the top two, have a
dissenting voice argue the strongest *alternative plan* (dialectical inquiry), which beat
consensus and beat the best individual in group studies (Schweiger et al. 1986, 1989).
Evolve only the top ideas and re-judge anything you change.

---

## 4. Failure modes → mitigations

| Failure | Mitigation in this skill |
|---|---|
| Typical/cliché output | G1 optional exploration, G5 tails, cliché registry in anti-pitfalls |
| Homogeneous batch | G3 authorized independent contexts, G4 task-fit methods, G7 mechanism dedupe |
| Frame exhausted (paraphrases) | G7 repeated mechanisms without useful difference → change operation/frame |
| "Be original" backfiring | G6 structural change, ban list |
| Self-flattering scores | S1 separate critic, S2 normalisation |
| Order/length bias | S2, S4 |
| Judge near chance on close calls | S7 preserve delegated choice and requested count; state uncertainty |
| Feasibility blindness | S5 gate, S8 pre-mortem |
| Overclaiming novelty | S6 closest-existing-thing |
| Far-analogy noise | G8 optional analogy with relation/mismatch check |
| Over-constraining | G9 deliberate constraint experiment; preserve hard requirements |
| Deskilling a strong human | Seed-from-the-human rule |

---

## 5. Honesty notes — what the evidence does not support

- Named techniques (SCAMPER, TRIZ, Six Thinking Hats, morphological analysis) have
  thin or mixed controlled evidence; SCAMPER had the weakest support in reviews, TRIZ
  improved some metrics and worsened others. Creativity *training* in general works
  (meta-analytic effects around d≈0.5–0.7). Use the named methods as **families that
  force variety**, not as guaranteed quality boosters.
- Incubation-as-default-mode-network is a popular simplification; the meta-analytic
  effect is real but modest and conditional.
- The pre-mortem evidence base is small. It is cheap and directionally supported; do not
  oversell it.

---

## 6. Sources

Beaty & Silvia 2012, *Psych. Aesthetics, Creativity & the Arts* 6(4) · Girotra,
Terwiesch & Ulrich 2010, *Management Science* · Diehl & Stroebe 1987, *JPSP* 53(3) ·
Simonton 1997, *Psych. Review* 104 · Meincke, Mollick & Terwiesch 2024, SSRN (Wharton
Mack Institute) · Terwiesch et al. 2026, arXiv 2607.27553 · Doshi & Hauser 2024, *Science
Advances* · Anderson, Shah & Kreminski 2024, *Creativity & Cognition* · Kumar et al.
2025, *CHI* · Si, Yang & Hashimoto 2025, *ICLR* · Zhang et al. 2025, "Verbalized
Sampling", arXiv 2510.01171 · Jiang et al. 2025, "Artificial Hivemind", *NeurIPS* ·
Keon et al. 2025, arXiv 2509.25767 · Panickssery, Bowman & Feng 2024, *NeurIPS* · Zheng
et al. 2023, *NeurIPS* · Wang et al. 2024, *ACL* · Liu et al. 2024, *COLM* (PairS) ·
Huang et al. 2024, *ICLR* · Gottweis et al. 2025, arXiv 2502.18864 · Runco & Jaeger
2012, *Creativity Research Journal* · Boden 2004, *The Creative Mind* · Franke, Poetz &
Schreier 2014, *Management Science* · Fu et al. 2013, *J. Mech. Design* · Chan, Dow &
Schunn 2015, *Design Studies* · Haught-Tromp 2016, *PACA* · Acar, Tarakci & van
Knippenberg 2019, *J. Management* · Sio & Ormerod 2009, *Psych. Bulletin* · Mitchell,
Russo & Pennington 1989, *J. Behavioral Decision Making* · Veinott, Klein & Wiggins 2010 ·
Schweiger, Sandberg & Ragan 1986, *AMJ*; Schweiger & Sandberg 1989, *SMJ*.
