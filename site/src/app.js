(() => {
  const examples = {
    diagnose: {label:'Operations / Find the cause',title:'A delay needs a diagnosis.',prompt:'Our repair shop keeps missing deadlines. We can’t add staff. Help us work out why before suggesting fixes.',intent:'Investigate a recurring process problem within a fixed staffing limit.',route:['Map the handoffs','Compare possible causes','Design a small test'],outcome:'A short list of plausible bottlenecks, the evidence needed to tell them apart, and a pilot the current team can run. No invented cause or promised time saving.'},
    decide: {label:'Business / Make a choice',title:'A choice needs a tradeoff.',prompt:'Should we offer a subscription or a one-time purchase? Use our costs and customer interviews. Show what could change the recommendation.',intent:'Compare two business models using supplied evidence and explicit decision criteria.',route:['Recover the criteria','Compare the tradeoffs','Check decisive assumptions'],outcome:'A recommendation with its supporting evidence, limits and the unknown most likely to change the answer. A recommendation does not commit you to an option.'},
    invent: {label:'Engineering / Explore possibilities',title:'A constraint can open a new angle.',prompt:'Find three ways to make this enclosure lighter without reducing impact resistance. Keep the manufacturing constraints fixed.',intent:'Explore mechanisms for resolving a specific engineering contradiction.',route:['Define the contradiction','Explore different mechanisms','Propose validation tests'],outcome:'Three distinct approaches, their assumptions and practical checks. The requested count stays fixed; technical feasibility still needs validation.'},
    research: {label:'Research / Understand evidence',title:'Sources need synthesis, not a story.',prompt:'Use only these interviews to write a findings memo. Separate what participants said from interpretation, and flag what the sample cannot tell us.',intent:'Synthesize supplied sources into a traceable findings memo.',route:['Read the sources','Separate findings from inference','Write and check the memo'],outcome:'A memo grounded in the interviews, with uncertainty and sample limits visible. No invented participants, quotations or extra research.'},
    refine: {label:'Creative work / Improve what’s here',title:'One change can be exactly enough.',prompt:'Keep the approved round glasses, cape and colors. Change only the bulb silhouette in this image. Do not redesign the character.',intent:'Make a bounded revision to an identified source while protecting approved elements.',route:['Inspect the source','Make the specific edit','Check preserved details'],outcome:'A revised image when suitable editing tools are available, or a precise editing handoff when they are not. No new concept round or changed selection.'},
    execute: {label:'Everyday life / Make it happen',title:'A plan needs something you can use.',prompt:'Turn our agreed weekly study routine into a one-page checklist. Keep the times and subjects fixed. Use only the plan I attached.',intent:'Produce a usable checklist from an approved source, with no new schedule decisions.',route:['Inspect the agreed plan','Make the checklist','Check every time and subject'],outcome:'The checklist itself, in the requested format, checked against the source. A missing attachment needs resolving; it does not justify inventing the schedule.'}
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
  document.querySelectorAll('[data-task]').forEach(button => button.addEventListener('click', () => {
    const item = examples[button.dataset.task];
    if (!item) return;
    selected = button.dataset.task;
    document.querySelectorAll('[data-task]').forEach(control => control.setAttribute('aria-pressed', String(control === button)));
    for (const field of ['label','title','intent','outcome']) document.getElementById('task-' + field).textContent = item[field];
    document.getElementById('task-prompt').textContent = '“' + item.prompt + '”';
    document.getElementById('task-route').replaceChildren(...item.route.map(text => {
      const li = document.createElement('li');
      li.textContent = text;
      return li;
    }));
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
