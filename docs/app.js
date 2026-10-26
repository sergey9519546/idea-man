(() => {
  const examples = {
  "diagnose": {
    "label": "Try an operations challenge",
    "title": "Why are Friday repairs always late?",
    "prompt": "Our bike shop promises Friday pickup, then spends Friday calling customers to apologise. We have three mechanics and this month's job log. Find what's going wrong before we hire anyone.",
    "outcome": "Check where jobs wait: approval, parts, or repair. If parts are the delay, try setting pickup dates after they arrive. Use the log to check that explanation first."
  },
  "decide": {
    "label": "Try a business challenge",
    "title": "The studio's empty three days a week.",
    "prompt": "I run a photo studio. Weekends are booked, weekdays are quiet. Should I rent it by the hour or run workshops? I can spare one afternoon a week to manage it.",
    "outcome": "Compare what each option earns after setup and your time. A workshop needs an audience; rentals need turnover and someone on call. Test one paid booking before adding dates."
  },
  "invent": {
    "label": "Try an engineering challenge",
    "title": "Keep the mug safe. Lose the foam.",
    "prompt": "We ship handmade mugs in foam. Help us switch to paper packaging using the same box, without buying custom tooling. The handles still need to survive delivery.",
    "outcome": "Compare a folded-card cradle with a wrap that keeps the handle away from the box wall. Make paper prototypes and define drop tests before changing what customers receive."
  },
  "research": {
    "label": "Try a research challenge",
    "title": "Twelve interviews. What should we fix?",
    "prompt": "I've pasted 12 customer interviews. People abandon checkout, but the team disagrees about why. Write a short findings memo using only these interviews.",
    "outcome": "A memo with the reported sticking points, quotes and interview IDs. It separates what customers said from what the team suspects, and names the unanswered question that matters most."
  },
  "refine": {
    "label": "Try a creative challenge",
    "title": "Two sisters. One kitchen. A slow opening.",
    "prompt": "My short film opens with two sisters explaining their past in a kitchen. It drags. Give me six openings with tension, using the same two actors and location.",
    "outcome": "One sister has a packed bag the other hasn't noticed. Or they're cooking for someone neither wants to see. Explore six different conflicts, then develop the opening you choose."
  },
  "execute": {
    "label": "Try an everyday challenge",
    "title": "Out the door at 7:40. In theory.",
    "prompt": "Two kids, one bathroom, and we're late for school again. We can't wake up earlier. Help us change one thing about our mornings this week.",
    "outcome": "Find out whether you're losing time waiting for the bathroom or hunting for bags. Try a bathroom order or a bags-by-the-door spot, whichever addresses the delay you actually see."
  }
};
  let selected = 'diagnose';
  let timer;
  const status = document.getElementById('copy-status');
  function announce(message) {
    clearTimeout(timer);
    status.textContent = message;
    status.classList.add('visible');
    timer = setTimeout(() => status.classList.remove('visible'), 3500);
  }
  document.querySelectorAll('[data-task]').forEach(button => button.addEventListener('click', event => {
    const item = examples[button.dataset.task];
    if (!item) return;
    selected = button.dataset.task;
    document.querySelectorAll('[data-task]').forEach(control => control.setAttribute('aria-pressed', String(control === button)));
    for (const field of ['label','title','outcome']) document.getElementById('task-' + field).textContent = item[field];
    document.getElementById('task-prompt').textContent = '“' + item.prompt + '”';
    // Reveal a changed example on narrow screens; preserve keyboard focus.
    const panel = document.getElementById('task-panel');
    if (event.detail > 0 && window.matchMedia('(max-width: 760px)').matches) {
      const rect = panel.getBoundingClientRect();
      if (rect.top < 0 || rect.top > window.innerHeight * 0.35) {
        panel.scrollIntoView({block:'start', behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'});
      }
    }


  }));
  async function copy(text, button) {
    let input;
    try {
      if (navigator.clipboard && window.isSecureContext) await navigator.clipboard.writeText(text);
      else {
        input = document.createElement('textarea');
        input.value = text;
        input.style.cssText = 'position:fixed;left:-9999px;top:0';
        document.body.appendChild(input);
        input.select();
        if (!document.execCommand('copy')) throw new Error('Clipboard unavailable');
      }
      announce('Prompt copied. Bring it to Idea-Man in your AI host.');
    } catch {
      announce('Clipboard unavailable. Select the prompt text to copy it.');
    } finally {
      if (input) input.remove();
      button.focus();
    }
  }
  const exampleButton = document.getElementById('copy-example');
  const starterButton = document.getElementById('copy-starter');
  exampleButton.addEventListener('click', () => copy(examples[selected].prompt, exampleButton));
  starterButton.addEventListener('click', () => copy(document.getElementById('starter-prompt').textContent.replace(/^[“”]|[“”]$/g, ''), starterButton));
  document.documentElement.classList.remove('no-js');
})();
