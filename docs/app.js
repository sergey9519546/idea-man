(() => {
  const examples = {
  "diagnose": {
    "label": "Try an operations challenge",
    "title": "Find the bottleneck behind the missed deadline.",
    "prompt": "Our repair shop keeps missing dates. Help us figure out why before proposing fixes.",
    "outcome": "Map the workflow, separate symptoms from possible causes, and identify the evidence needed to choose a practical improvement."
  },
  "decide": {
    "label": "Try a business challenge",
    "title": "Find the opportunity in what you already have.",
    "prompt": "Find five business models for this unused equipment, using the resources we already have.",
    "outcome": "Explore distinct models, compare assumptions and tradeoffs, then choose a small test before making a bigger commitment."
  },
  "invent": {
    "label": "Try an engineering challenge",
    "title": "Challenge the tradeoff. Keep the requirement.",
    "prompt": "Resolve this engineering contradiction: lower weight without losing impact resistance. Keep the manufacturing constraints fixed.",
    "outcome": "Explore different mechanisms for resolving the contradiction, surface assumptions, and propose tests. Engineering decisions still need domain validation."
  },
  "research": {
    "label": "Try a research challenge",
    "title": "Make the evidence easier to use.",
    "prompt": "Use only these interviews to write a findings memo. Separate supported observations from interpretation and identify gaps.",
    "outcome": "Work from the supplied sources, trace claims to evidence, preserve uncertainty, and develop a clear findings memo."
  },
  "refine": {
    "label": "Try a creative challenge",
    "title": "Go beyond six versions of the same idea.",
    "prompt": "Give me six different concepts for this brief. Use analogy to change the underlying mechanism, while preserving the approved character and colors.",
    "outcome": "Generate distinct directions within your constraints, compare what each makes possible, then develop the option you select."
  },
  "execute": {
    "label": "Try an everyday challenge",
    "title": "Make room for a better routine.",
    "prompt": "Our mornings feel rushed. Help us find the real bottleneck and design one small change to try this week.",
    "outcome": "Examine the sequence, consider everyone involved, and choose a manageable experiment with a simple way to judge whether it helps."
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
