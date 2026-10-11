# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

1. **Add a pet.** The owner registers a pet with basic info like name, species, age, and any special needs, so care tasks can be tied to it.
2. **Schedule a care task.** The owner creates a task for a pet, such as a feeding, walk, medication, or appointment, with a time, duration, priority, and optional recurrence.
3. **View today's plan.** The owner sees a daily schedule of all pets' tasks, sorted and prioritized by the app. Conflicts are flagged and each task can be marked complete.

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
