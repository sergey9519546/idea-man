# Engine Science — why the workflow is built this way

The workflow in SKILL.md is not taste; each rule answers a measured failure of
human brainstorming or of language-model ideation. Read this when you need to
explain a choice, adapt the engine to an unusual situation, or run ROOM mode.

## Contents
1. The two failure modes this engine exists to beat
2. Generation rules (G1–G9)
3. Selection rules (S1–S8)
4. Failure modes → mitigations table
5. What the evidence does NOT support (honesty notes)
6. Sources

---

## 1. The two failure modes

**Typicality.** A language model's first answers are its most probable answers, and
the most probable answer is the cliché. Preference training measurably rewards
"typical" text (Zhang et al. 2025). Different models also converge on strikingly
similar outputs (Jiang et al., NeurIPS 2025 "Artificial Hivemind"). Left alone, an
LLM idea session produces competent, homogeneous, forgettable work. When ads are
compressed or summarised, metaphor and emotion are the first things lost and the
output regresses to clichés (Keon et al. 2025).

**Self-flattery.** Models recognise and prefer their own outputs (Panickssery et al.
2024), flip verdicts when the order of options is swapped, reward length, and cannot
reliably fix their own reasoning without outside feedback (Huang et al. 2024). An idea
engine that grades its own work in the same breath will love everything it makes.

Everything below attacks one of these two.

---

## 2. Generation rules

**G1. The first ideas are warm-up.** Human originality rises over a session and then
plateaus (Beaty & Silvia 2012; Christensen, Guilford & Wilson 1957). An LLM's first
samples are its most typical. Write the first three ideas down, label them WARM-UP, and
treat them as the bar to beat, not as candidates.

**G2. Volume before selection.** The best idea is an extreme value; more draws raise the
maximum. Hybrid (solo-then-group) processes beat team brainstorming mainly by producing
more ideas, and their top ideas were far better (Girotra, Terwiesch & Ulrich 2010). Hits
scale with output (Simonton's equal-odds rule). Floors: SPARK ≥10 raw, FULL ≥20 raw,
ROOM ≥40 raw before dedupe.

**G3. Independent contexts, then pool.** Pooled solo work produces about twice the ideas of
interacting groups (Diehl & Stroebe 1987), and building on each other's ideas did not
improve quality (Girotra et al.). Ideas already in context anchor the next ones. In ROOM
mode, run each thinker as a separate subagent that cannot see the others; merge only at
the end. In single-context mode, generate each method's batch before reading the previous
batch back.

**G4. At least three method families per round.** Chain-of-thought prompting cut idea
similarity close to human-pool levels, while a single persona barely helped
(Meincke, Mollick & Terwiesch 2024). Pooling methods, personas, constraints and models
brought LLM diversity near human level (Terwiesch et al. 2026). One method = one
neighbourhood of ideas.

**G5. Sample the tails (verbalized sampling).** Asking for several candidates with
their probabilities, then asking for candidates below a probability threshold, raised
creative diversity 1.6–2.1× and human ratings ~26% (Zhang et al. 2025). Use: "List 5
directions with how likely a typical creative team is to propose each; now give 5 that a
typical team would propose less than 10% of the time." The numbers are a steering lever,
not calibrated truth.

**G6. Change the structure, never just say "be different".** Feeding a model
similarity feedback produced the *least* diverse output of 35 strategies tested
(Meincke et al.). When ideas start repeating, switch method, add a constraint, or ban
the mechanisms already used. Do not merely exhort.

**G7. Deduplicate by mechanism, not wording.** About 95% of 4,000 LLM seed ideas were
duplicates (Si, Yang & Hashimoto, ICLR 2025). Paraphrases hide shared mechanisms. Give
every raw idea a one-line "mechanism + source of surprise" tag and merge ideas with the
same tag. If more than half of a new batch duplicates earlier ones, the frame is
exhausted: change insight, HMW, method or constraint.

**G8. Analogy distance: mostly near-to-mid, one far probe.** Far-domain solvers produce
more novel ideas, especially in the top tail (Franke, Poetz & Schreier 2014), but far
sources lower average quality and there is a distance sweet spot (Fu et al. 2013; Chan,
Dow & Schunn 2015). Use one far-domain probe per round for variance, and admit it to the
pool only if you can state which *relations* carry over (structure, not surface).

**G9. One or two constraints per pass; fewer for radical briefs.** A required element
made writing measurably more creative, and the boost carried into later unconstrained
work (Haught-Tromp 2016). Constraint effects follow an inverted U, with the peak at fewer
constraints for radical innovation (Acar, Tarakci & van Knippenberg 2019). Rotate
constraints between passes (scripts/draw.py --only constraints).

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
`idea-critic` subagent. In chat, simulate it: restate each idea cold in the normalised
template, then judge as someone who has never seen them.

**S2. Normalise before judging.** Rewrite every surviving idea into the same template and
length (one-sentence idea, what people experience, mechanism). Length and polish bias
judges (Zheng et al. 2023).

**S3. Absolute scores triage; pairwise comparison ranks.** 1–10 rubric scores are fine for
cutting a long list to a shortlist (coarse agreement with humans is comparable for single
and pairwise grading). For the finalists, compare head-to-head: pairwise ranking agrees
better with humans than direct scoring (Liu et al. 2024), and tournaments were used by Si
et al. and Google's AI co-scientist (Gottweis et al. 2025).

**S4. Swap order on every comparison.** Judges flip verdicts when options are swapped
(Zheng et al.; Wang et al. 2024). Compare A-vs-B and B-vs-A; a split verdict is a tie.

**S5. Novelty, usefulness and feasibility are separate axes.** The standard definition of
creativity is originality *and* effectiveness (Runco & Jaeger 2012; Stein 1953). Novelty
and immediate usability trade off (Franke et al.). Never let a brilliant-but-impossible
idea win on a blended score; feasibility is a gate (can it be made with the real budget,
team, tools and time?).

**S6. Name the closest existing thing.** "Novel" means novel relative to the judge's
knowledge. Every finalist states the nearest existing work; if web search is available,
check it before claiming originality.

**S7. The human chooses.** The best LLM judge agreed with expert humans only ~53% on fine
distinctions, about the same as humans agree with each other (Si et al.). Groups picking
their own best ideas barely beat chance (Girotra et al.). Present at most three finalists
with honest trade-offs and the critic's confidence; recommend one, but the user decides.

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
| Typical/cliché output | G1 warm-up ban, G5 tails, cliché registry in anti-pitfalls |
| Homogeneous batch | G3 independent contexts, G4 ≥3 families, G7 mechanism dedupe |
| Frame exhausted (paraphrases) | G7 >50% duplicate trigger → switch frame |
| "Be original" backfiring | G6 structural change, ban list |
| Self-flattering scores | S1 separate critic, S2 normalisation |
| Order/length bias | S2, S4 |
| Judge near chance on close calls | S7 human chooses from ≤3, report confidence |
| Feasibility blindness | S5 gate, S8 pre-mortem |
| Overclaiming novelty | S6 closest-existing-thing |
| Far-analogy noise | G8 one far probe + structure check |
| Over-constraining | G9 one or two constraints, fewer for radical briefs |
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
