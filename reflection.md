# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

1. **Add a pet.** The owner registers a pet with basic info like name, species, age, and any special needs, so care tasks can be tied to it.
2. **Schedule a care task.** The owner creates a task for a pet, such as a feeding, walk, medication, or appointment, with a time, duration, priority, and optional recurrence.
3. **View today's plan.** The owner sees a daily schedule of all pets' tasks, sorted and prioritized by the app. Conflicts are flagged and each task can be marked complete.

**a. Initial design**

- Briefly describe your initial UML design.

  My first Mermaid class diagram had four classes and two enums: `Owner`, `Pet`, `Task`, `Scheduler`, `Priority`, and `Frequency`. An Owner has many Pets, each Pet has many Tasks, and the Scheduler plans for one Owner.

- What classes did you include, and what responsibilities did you assign to each?

  `Task` holds one care activity (time, duration, priority, frequency, completion) and knows its end time and whether it overlaps another task. `Pet` stores its details and its tasks, `Owner` manages pets and the daily time budget and returns every pet's tasks together, and `Scheduler` sorts, filters, fits tasks to the time budget, checks conflicts, and explains the plan.

**b. Design changes**

- Did your design change during implementation?

  Yes, but only by small additions; the four classes and their relationships stayed the same. The final diagram is in `diagrams/uml_final.mmd`.

- If yes, describe at least one change and why you made it.

  I added `Task.pet_name`, which `Pet.add_task()` sets. Without it, the Scheduler couldn't filter tasks by pet or name the pet in a conflict warning, because it gets one combined list from `Owner.get_all_tasks()`. I also added `Scheduler.complete_task()`, so `Task.mark_complete()` only returns the next occurrence and never has to know which Pet to add it to.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

  It considers the owner's available minutes, each task's priority, each task's start time and duration (for ordering and conflicts), and the due date and frequency (for which tasks appear today and when they recur). Owner preferences are stored but not used by the scheduler yet.

- How did you decide which constraints mattered most?

  Priority matters most, because skipping a medication is worse than skipping a play session, so the time budget is filled highest priority first. Time comes next: the kept tasks are shown in clock order, and overlaps are flagged as warnings rather than silently moved, so the owner makes the final call.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

  `fit_to_available_time()` fills the owner's time budget greedily, going through tasks from highest priority to lowest. It keeps each task that still fits and skips any that would go over. It doesn't search for the combination that uses the most minutes. For example, with 40 minutes free, it keeps a 35-minute high-priority task and skips two 20-minute medium tasks, even though those two would fill the full 40 minutes.

- Why is that tradeoff reasonable for this scenario?

  For pet care, the most important tasks (meds, feeding) should always come first, even if that leaves a few minutes unused. The greedy approach is also simple, fast, and easy to explain, and the plan lists every skipped task so the owner knows what was dropped.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

  I used Claude Code at every step, one step at a time. It turned my core user actions into a Mermaid UML diagram, created class stubs, and wrote the scheduling logic, the `main.py` demo, the tests, and the docs.

- What kinds of prompts or questions were most helpful?

  Specific prompts that named the file and the exact behavior worked best, such as "Scheduler must read from the Owner method, not a single pet." Asking for one step at a time kept each change small enough to review.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

  While implementing, the AI added things that weren't in my UML (`Task.pet_name`, `Scheduler.complete_task()`, `Scheduler.skipped`). It also kept the name `title` even though my brief said `description`. Before keeping these changes, I checked that each one had a real reason, for example that filtering by pet needs `pet_name`, and I made sure the UML was updated to match the code.

- How did you evaluate or verify what the AI suggested?

  I didn't rely on the AI's explanations alone. I checked that the UML parses with Mermaid, ran `main.py` to see the real schedule, and ran `pytest`. The first `pytest` run failed with `ModuleNotFoundError`, which showed that a `pytest.ini` was needed so plain `pytest` works.

**c. AI strategy**

- Which AI coding assistant features were most effective for building your scheduler?

  The most effective feature was the assistant's ability to edit several files in one change and then run the code itself, using `pytest`, `main.py`, and Streamlit's `AppTest`. For example, the recurrence change touched `pawpal_system.py`, the tests, and the UML together, and it was verified before I reviewed it. Asking it to explain things, such as `st.session_state` and `timedelta`, was useful too.

- Give one example of an AI suggestion you rejected or modified to keep your system design clean.

  The AI's first Streamlit version passed `value=owner.available_minutes` to the minutes input, and clicking + made the number jump back and forth. I reported the glitch and had it changed so the widget uses a fixed `key` and the Owner is set from it each run. That keeps the Owner object as the single source of truth instead of having two copies of the same value fighting each other.

- How did using separate chat sessions for different phases help you stay organized?

  I mostly worked in one continuous Claude Code session, but I gave it one phase at a time (UML, stubs, logic, tests, UI, docs), and each prompt had a clear goal and was checked before moving on. Keeping the context helped the AI stay consistent with earlier decisions. Starting a new session per phase would have made each phase's scope even clearer, at the cost of re-explaining the design.

- Summarize what you learned about being the "lead architect" when collaborating with powerful AI tools.

  The AI is fast at writing code, but I set the design (classes, responsibilities, the Owner → Pet → Task relationships) and decided what "correct" meant. My most important job was reviewing: checking that additions fit the UML, and that docs and code agreed. Giving precise, scoped instructions and verifying the results kept the system clean.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

  The 14 tests in `tests/test_pawpal.py` cover marking a task complete and adding tasks to a pet. They also cover sorting (chronological order, earlier days first, priority on ties, a time-ordered daily plan) and recurrence (next day, next week, nothing for one-time tasks, late tasks coming back tomorrow, no duplicates). Finally, they cover conflict detection (same pet, different pets, back-to-back and different-day tasks not flagged, every overlapping pair reported).

- Why were these tests important?

  Sorting, recurrence, and conflict detection are the parts most likely to break quietly, for example an off-by-one date or a missed overlap. The edge-case tests (late tasks, double completion, touching time slots) check exactly the cases I'd be least likely to try by hand.

**b. Confidence**

- How confident are you that your scheduler works correctly?

  Fairly confident (4/5): all 14 tests pass, and `main.py` and the Streamlit app show the expected plans and warnings. The time-budget skipping in `fit_to_available_time()` and the UI aren't covered by automated tests yet.

- What edge cases would you test next if you had more time?

  I'd test the time budget: exactly filling the minutes, a single task longer than the whole budget, and ties in priority. I'd also test tasks that run past midnight, combined pet and status filters, and the Streamlit flows using Streamlit's `AppTest`.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

  I'm most satisfied with the Scheduler: one plan covers all pets through `Owner.get_all_tasks()`, and it explains itself, showing skipped tasks and labeled conflict warnings instead of failing silently. Recurrence also handles the tricky cases (late or double completion) cleanly.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

  I'd save data to a file or database, because Streamlit's session state is lost on a page reload. I'd also add editing and deleting tasks in the UI. I might replace the greedy time budget with an option that suggests moving a conflicting task to a free slot instead of only warning.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

  Designing the UML first made every later AI prompt easier, because I could point to exact class and method names and check the output against them. The AI writes code quickly, but the design decisions, and checking that the code still matches them, stay my job.
