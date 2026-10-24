#!/usr/bin/env python3
"""
draw.py — true randomness for the idea engine.

Language models are bad at being random: asked for "a random word" they return
the same few words, which quietly collapses idea diversity. Random-entry,
provocation and far-analogy methods only work when the stimulus is genuinely
unrelated to the problem, so this script supplies it.

Usage:
  python draw.py                      # 3 provocation cards, 3 random words, 2 far domains, 1 thinker
  python draw.py --cards 5 --words 4 --domains 3 --thinkers 2
  python draw.py --seed 42            # reproducible draw
  python draw.py --only cards         # just cards (also: words, domains, thinkers, constraints)

No dependencies. Works anywhere Python 3 runs.
"""
import argparse
import random

CARDS = [
    # subtraction / via negativa
    "Delete the feature everyone agrees is essential. What survives?",
    "Remove the main character, product or performer from the frame. Make it work anyway.",
    "Cut it to one-tenth of its size. What is the only part that matters?",
    "What would this look like with no words at all?",
    "Take away the budget entirely. What is the free version?",
    # inversion
    "Make the problem worse on purpose. What did you learn about the cause?",
    "Swap the roles: the audience performs, the brand watches.",
    "Tell it backwards: start with the ending, end with the setup.",
    "Design for the person who hates this category.",
    "What would guarantee this fails? Now do the opposite of each item.",
    "Turn the weakness into the headline.",
    # exaggeration / scale
    "Make it 100x bigger than reasonable. Stadium, city, planet.",
    "Make it microscopic: one second, one pixel, one word.",
    "Push the one quality it has to an absurd extreme.",
    "What if it lasted 10 years instead of 30 seconds?",
    "What if a million people did it at the same moment?",
    # constraint
    "One take. No cuts.",
    "Only one colour, one sound, one location.",
    "It must work with the sound off.",
    "It must be explainable to a seven-year-old in one breath.",
    "Use only things that already exist and are cheap (withered tech).",
    "It has to be finished in one hour with what is in the room.",
    "It must be made by the audience, not by you.",
    # analogy / transfer
    "How does nature already solve this? Name the organism.",
    "How would a casino, a church and a hospital each handle this?",
    "Steal the structure of a game show.",
    "Steal the mechanics of a ritual or holiday.",
    "Steal a rule from a sport and apply it here.",
    "Treat it as a logistics problem. What is the container?",
    "Treat it as a heist. What is being stolen, from whom?",
    # perspective / personal analogy
    "Become the object. What does it feel, want, fear?",
    "Explain it as the villain would.",
    "What would a child invent here? What would a grandmother?",
    "Who is the most extreme user? What hack have they already built?",
    "What is the competitor praying you never do?",
    # reframing / perception
    "Do not fix the thing. Change how the waiting feels.",
    "What is the real job the person is hiring this for?",
    "Who is the hidden second audience?",
    "Make the boring part the entertainment.",
    "The fix is psychological, not mechanical. What is it?",
    # time / context
    "Set it 50 years in the past. Then 50 years in the future.",
    "Move it to the worst possible moment of someone's day.",
    "What happens the day after the story ends?",
    "Make it a ritual people repeat every week.",
    # collision / bisociation
    "Collide it with the most unrelated thing in the room.",
    "Two ideas you already killed: combine them.",
    "Combine the brief with a genre it has never met.",
    "Put two incompatible tones in the same frame.",
    # truth / tension
    "What is the truth everyone in this category is too polite to say?",
    "What is the uncomfortable version?",
    "What would make the client nervous but the audience grateful?",
    "Where is the contradiction people live with every day?",
    # system / leverage
    "Change the rule, not the parameter.",
    "Where is the bottleneck? Ignore everything else.",
    "What feedback loop could make this grow by itself?",
    "Standardise the box: what is the universal adapter?",
    "Solve two problems with one move.",
    # error / accident
    "Keep the mistake. Build the idea around it.",
    "Which failed version of this was secretly better?",
    "Use the side effect as the main effect.",
    # medium
    "It is not an ad, a film or an app. It is an object. What object?",
    "It is a place. What place?",
    "It is a tool people use. What does it do?",
    "Make it a format, not a piece: something that can run forever.",
    "What would the poster be? One image, no copy.",
    # decision / commitment
    "Say it in one sentence. If you cannot, it is not an idea yet.",
    "Write the headline the press would run if it worked.",
    "What would you do if you were not allowed to fail?",
    "What would you do if you were guaranteed to be ignored?",
]

WORDS = [
    "anchor", "ladder", "mirror", "candle", "bridge", "fossil", "compass", "orchard",
    "tide", "ticket", "mask", "lantern", "receipt", "vaccine", "elevator", "umbrella",
    "eclipse", "bakery", "funeral", "lottery", "glacier", "wedding", "satellite", "hive",
    "passport", "rust", "echo", "shadow", "fence", "garden", "skeleton", "parade",
    "magnet", "auction", "subway", "ghost", "spice", "harbour", "pawn", "volcano",
    "library", "recipe", "uniform", "migration", "tattoo", "balloon", "prison", "puzzle",
    "telescope", "laundry", "cathedral", "seed", "thermostat", "drumbeat", "map", "knot",
    "ferry", "nest", "lighthouse", "ticket stub", "pharmacy", "carnival", "graveyard",
    "pulse", "lens", "kite", "border", "museum", "barcode", "choir", "landslide", "dice",
    "costume", "voicemail", "sandcastle", "aquarium", "x-ray", "scarecrow", "jukebox",
    "hourglass", "shipwreck", "billboard", "cocoon", "relay race", "postcard", "fuse",
    "metronome", "sponge", "trophy", "crutch", "firework", "vending machine", "orbit",
    "inheritance", "stopwatch", "quarantine", "translator", "confetti", "fingerprint",
]

FAR_DOMAINS = [
    "evolutionary biology", "military logistics", "restaurant kitchens", "theatre staging",
    "religious ritual", "professional sports", "emergency medicine", "casino design",
    "air traffic control", "beekeeping", "jazz improvisation", "stand-up comedy",
    "urban planning", "magic tricks", "espionage", "fashion runways", "insurance",
    "children's playgrounds", "funeral rites", "prison design", "theme parks",
    "court trials", "deep-sea exploration", "heist films", "board games", "cartography",
    "perfumery", "mountaineering", "circus acrobatics", "monastic life", "auctions",
    "ant colonies", "weather forecasting", "subway systems", "tattoo culture",
    "wrestling storylines", "orchestras", "sourdough fermentation", "chess openings",
    "space missions", "game shows", "border crossings", "street markets",
    "sign language", "beauty pageants", "elections", "cooking competitions",
]

THINKERS = [
    "Edward de Bono (provocation / lateral jump)", "Genrich Altshuller (resolve the contradiction)",
    "Gunpei Yokoi (cheap mature tech, new use)", "Paul MacCready (find the real bottleneck)",
    "Rory Sutherland (psychological fix, not engineering)", "Shigeru Miyamoto (one idea, many problems solved)",
    "Fritz Zwicky (map every combination)", "Clayton Christensen (the job to be done)",
    "Alfred Hitchcock (information asymmetry)", "Sergei Eisenstein (collide two images)",
    "Brian Eno (obey an arbitrary constraint)", "Taiichi Ohno (ask why five times)",
    "Donella Meadows (change the rule, not the number)", "Arthur Koestler (collide two frames)",
    "Gary Klein (it already failed; why?)", "Amazon PR/FAQ (write the launch headline first)",
    "Malcolm McLean (standardise the box)", "Eiji Nakatsu (copy an organism)",
    "Dieter Rams (less, but better)", "Pixar Braintrust (diagnose, don't prescribe)",
    "Trey Parker & Matt Stone (but / therefore)", "Lars von Trier (impose an obstruction)",
    "Roger Martin (what would have to be true?)", "James Webb Young (combine old elements)",
    "Dave Trott (get upstream of the problem)", "Bill Bernbach (flip the flaw)",
    "Leo Burnett (find the inherent drama)", "Nile Rodgers (the deep hidden meaning)",
    "Sid Meier (make every choice interesting)", "Min Basadur (ladder the question)",
    "Jean-Marie Dru (break the category convention)", "Chip & Dan Heath (make it stick)",
    "Raymond Loewy (most advanced, yet acceptable)", "Kenn Adams (but one day...)",
    "Del Close (if this is true, what else is true?)", "Max Martin (hook first, words last)",
]

CONSTRAINTS = [
    "zero budget", "60 seconds", "one location", "no dialogue", "one prop", "sound off",
    "made in a day", "the audience makes part of it", "one colour", "vertical 9:16 only",
    "the main subject never appears on screen", "a single sentence", "must be physical, not digital",
    "must work for a 6-year-old and a 60-year-old", "one continuous shot",
    "only existing footage or assets", "the audience does the work", "the reveal waits until the final moment",
    "every episode ends in the same place", "the lead never speaks", "it repeats, with one change each time",
    "two characters only", "it happens in real time", "the rule is broken exactly once",
]

POOLS = {
    "cards": CARDS,
    "words": WORDS,
    "domains": FAR_DOMAINS,
    "thinkers": THINKERS,
    "constraints": CONSTRAINTS,
}


def main() -> None:
    p = argparse.ArgumentParser(description="Draw random creative stimuli.")
    p.add_argument("--cards", type=int, default=3)
    p.add_argument("--words", type=int, default=3)
    p.add_argument("--domains", type=int, default=2)
    p.add_argument("--thinkers", type=int, default=1)
    p.add_argument("--constraints", type=int, default=1)
    p.add_argument("--only", choices=sorted(POOLS), help="draw from one pool only")
    p.add_argument("--seed", type=int, help="seed for a reproducible draw")
    a = p.parse_args()

    rng = random.Random(a.seed)  # None -> OS entropy
    counts = {
        "cards": a.cards, "words": a.words, "domains": a.domains,
        "thinkers": a.thinkers, "constraints": a.constraints,
    }
    if a.only:
        counts = {k: (v if k == a.only else 0) for k, v in counts.items()}
        if counts[a.only] == 0:
            counts[a.only] = 3

    labels = {
        "cards": "PROVOCATION CARDS", "words": "RANDOM ENTRY WORDS",
        "domains": "FAR DOMAINS (steal a mechanism)", "thinkers": "GUEST THINKER",
        "constraints": "IMPOSED CONSTRAINT",
    }
    for key, n in counts.items():
        if n <= 0:
            continue
        pool = POOLS[key]
        picks = rng.sample(pool, min(n, len(pool)))
        print(f"{labels[key]}:")
        for item in picks:
            print(f"  - {item}")


if __name__ == "__main__":
    main()
