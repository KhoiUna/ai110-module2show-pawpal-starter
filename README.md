# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Implementation Summary

The core logic lives in `pawpal_system.py` (class diagram: `diagrams/uml.mmd`). It has four classes and two enums:

- **`Task`** (dataclass): one care activity on one day, with a title, category, start time, duration, `Priority` (low/medium/high), `Frequency` (once/daily/weekly), due date, and completion status. It can compute its end time, check whether it overlaps another task, and mark itself complete. If it repeats, completing it returns the next occurrence.
- **`Pet`** (dataclass): a pet's details (name, species, age, special needs) and its own list of tasks. `add_task()` tags each task with the pet's name so it can be traced back later.
- **`Owner`** (dataclass): the owner's name, daily time budget (`available_minutes`), preferences, and pets. `get_all_tasks()` returns every pet's tasks as one list.
- **`Scheduler`**: the "brain". It takes an `Owner` and reads tasks only through `owner.get_all_tasks()`, so one plan covers all pets.

**How they work together:** an `Owner` has many `Pet`s, and each `Pet` has many `Task`s. `Scheduler.build_daily_plan(day)` follows four steps:

1. It gathers every task due that day across all pets.
2. It keeps the highest-priority tasks that fit in the owner's available minutes and records the rest in `scheduler.skipped`.
3. It returns the kept tasks sorted by start time.
4. `explain_plan()` turns the plan into readable text that lists time-overlap conflicts and skipped tasks. `complete_task()` marks a task done and adds the next occurrence of a daily or weekly task to the same pet.

Run `python main.py` for a terminal demo and `pytest` for the tests.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Today's Schedule (Sunday, October 11)
========================================
Plan for Jordan: 5 task(s), 80 of 90 available minutes.
  07:30-08:00  Morning walk (Mochi) [high priority, daily, to do]
  08:00-08:10  Breakfast (Luna) [high priority, daily, to do]
  08:15-08:20  Thyroid pill (Luna) [high priority, daily, to do]
  17:00-17:20  Fetch in the yard (Mochi) [medium priority, once, to do]
  19:00-19:15  Brushing (Luna) [low priority, weekly, to do]
```

## 🧪 Testing PawPal+

```bash
python -m pytest
```

The suite (`tests/test_pawpal.py`, 14 tests) covers:

- **Basics:** marking a task complete, adding tasks to a pet.
- **Sorting:** tasks come back in chronological order (earlier days first, higher priority first on time ties), and the daily plan is time-ordered.
- **Recurrence:** completing a daily/weekly task creates the next occurrence (next day / next week) on the same pet; one-time tasks don't recur; late tasks recur from today; completing twice doesn't duplicate.
- **Conflict detection:** same-time tasks are flagged for the same pet and across pets; back-to-back and different-day tasks are not; every overlapping pair is reported.

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/khoi/Desktop/ai110-module2show-pawpal-starter
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collected 14 items

tests/test_pawpal.py ..............                                      [100%]

============================== 14 passed in 0.01s ==============================
```

**Confidence Level:** ★★★★☆ (4/5): all core scheduling behaviors are tested and pass, including edge cases. The Streamlit UI and time-budget skipping (`fit_to_available_time`) aren't directly tested yet.

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature           | Method(s) | Notes                             |
| ----------------- | --------- | --------------------------------- |
| Task sorting      |           | e.g., by priority, duration       |
| Filtering         |           | e.g., skip tasks if time runs out |
| Conflict handling |           | e.g., overlapping time slots      |
| Recurring tasks   |           | e.g., daily vs. weekly            |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** _(optional)_: <!-- Insert a screenshot or link to a demo video here -->
