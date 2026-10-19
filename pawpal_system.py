"""PawPal+ core system: owners, pets, care tasks, and the daily scheduler."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import Optional


class Priority(Enum):
    """How important a task is."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Frequency(Enum):
    """How often a task repeats."""

    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


# How far ahead the next occurrence of a recurring task is scheduled.
RECURRENCE_STEP = {
    Frequency.DAILY: timedelta(days=1),
    Frequency.WEEKLY: timedelta(weeks=1),
}


@dataclass
class Task:
    """A single pet care task, such as a feeding, walk, medication, or appointment.

    Each Task is one occurrence on one day. Recurring tasks produce their next
    occurrence when marked complete (see mark_complete).
    """

    title: str
    category: str
    start_time: time
    duration_minutes: int
    priority: Priority = Priority.MEDIUM
    frequency: Frequency = Frequency.ONCE
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    pet_name: str = ""  # set by Pet.add_task so tasks can be traced back to their pet

    def __post_init__(self) -> None:
        """Reject tasks with a zero or negative duration."""
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")

    def _start_datetime(self) -> datetime:
        """Return the full date and time this task starts."""
        return datetime.combine(self.due_date, self.start_time)

    def _end_datetime(self) -> datetime:
        """Return the full date and time this task ends."""
        return self._start_datetime() + timedelta(minutes=self.duration_minutes)

    def end_time(self) -> time:
        """Return the time this task finishes (start_time + duration_minutes)."""
        return self._end_datetime().time()

    def overlaps(self, other: Task) -> bool:
        """Return True if this task's time window overlaps with another task's."""
        return (
            self._start_datetime() < other._end_datetime()
            and other._start_datetime() < self._end_datetime()
        )

    def is_due_on(self, day: date) -> bool:
        """Return True if this task should appear on the given day."""
        return self.due_date == day

    def mark_complete(self, completed_on: Optional[date] = None) -> Optional[Task]:
        """Mark this task done; return the next occurrence if it recurs, else None."""
        if self.completed:
            return None  # already done; don't create a duplicate next occurrence
        self.completed = True
        step = RECURRENCE_STEP.get(self.frequency)
        if step is None:
            return None
        # Count from the later of the due date and the completion day, so a late
        # task's next occurrence lands after today and an early one isn't duplicated.
        base = max(self.due_date, completed_on or date.today())
        return replace(self, due_date=base + step, completed=False)


@dataclass
class Pet:
    """A pet owned by the owner, with its own list of care tasks."""

    name: str
    species: str
    age: int
    special_needs: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, title: str) -> bool:
        """Remove a task by title; return True if one was removed."""
        for i, task in enumerate(self.tasks):
            if task.title == title:
                del self.tasks[i]
                return True
        return False

    def get_tasks_for(self, day: date) -> list[Task]:
        """Return this pet's tasks that are due on the given day."""
        return [task for task in self.tasks if task.is_due_on(day)]


@dataclass
class Owner:
    """The pet owner, their daily time budget, preferences, and pets."""

    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a new pet. Pet names must be unique per owner."""
        if self.get_pet(pet.name) is not None:
            raise ValueError(f"{self.name} already has a pet named {pet.name}")
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> bool:
        """Remove a pet by name; return True if one was removed."""
        pet = self.get_pet(pet_name)
        if pet is None:
            return False
        self.pets.remove(pet)
        return True

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        """Return the pet with the given name, or None if not found."""
        for pet in self.pets:
            if pet.name == pet_name:
                return pet
        return None

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Builds and explains a daily care plan for an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler that plans for the given owner's pets."""
        self.owner = owner
        # tasks left out by the last fit_to_available_time call
        self.skipped: list[Task] = []

    def build_daily_plan(self, day: date) -> list[Task]:
        """Return the tasks due on the given day that fit the owner's time, in time order."""
        due_today = [task for task in self.owner.get_all_tasks()
                     if task.is_due_on(day)]
        return self.sort_by_time(self.fit_to_available_time(due_today))

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by start time (higher priority first on ties)."""
        return sorted(tasks, key=lambda t: (t.due_date, t.start_time, -t.priority.value))

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted from highest to lowest priority (earlier first on ties)."""
        return sorted(tasks, key=lambda t: (-t.priority.value, t.due_date, t.start_time))

    def filter_tasks(
        self,
        tasks: list[Task],
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> list[Task]:
        """Return tasks matching the given pet name and completion status (None = any)."""
        return [
            task
            for task in tasks
            if (pet_name is None or task.pet_name == pet_name)
            and (completed is None or task.completed == completed)
        ]

    def fit_to_available_time(self, tasks: list[Task]) -> list[Task]:
        """Keep the highest-priority tasks that fit the owner's minutes; record the rest in self.skipped."""
        budget = self.owner.available_minutes
        used = 0
        kept: list[Task] = []
        self.skipped = []
        for task in self.sort_by_priority(tasks):
            if used + task.duration_minutes <= budget:
                kept.append(task)
                used += task.duration_minutes
            else:
                self.skipped.append(task)
        return kept

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Return a warning message for each pair of overlapping tasks."""
        ordered = self.sort_by_time(tasks)
        warnings = []
        for i, first in enumerate(ordered):
            for second in ordered[i + 1:]:
                if first.overlaps(second):
                    warnings.append(
                        f"Conflict: {_describe(first)} overlaps {_describe(second)}"
                    )
        return warnings

    def complete_task(self, task: Task, completed_on: Optional[date] = None) -> Optional[Task]:
        """Mark a task done and add its next occurrence (if any) to the same pet."""
        next_task = task.mark_complete(completed_on)
        if next_task is not None:
            pet = self.owner.get_pet(task.pet_name)
            if pet is not None:
                pet.add_task(next_task)
        return next_task

    def explain_plan(self, tasks: list[Task]) -> str:
        """Return a human-readable explanation of why the plan looks the way it does."""
        if not tasks:
            return f"No tasks scheduled for {self.owner.name} today."

        total = sum(task.duration_minutes for task in tasks)
        lines = [
            f"Plan for {self.owner.name}: {len(tasks)} task(s), "
            f"{total} of {self.owner.available_minutes} available minutes."
        ]
        for task in self.sort_by_time(tasks):
            status = "done" if task.completed else "to do"
            lines.append(
                f"  {task.start_time:%H:%M}-{task.end_time():%H:%M}  "
                f"{task.title} ({task.pet_name}) "
                f"[{task.priority.name.lower()} priority, {task.frequency.value}, {status}]"
            )
        if self.skipped:
            lines.append(
                "Skipped (not enough time; lower priority tasks dropped first):")
            for task in self.skipped:
                lines.append(
                    f"  {task.title} ({task.pet_name}), {task.duration_minutes} min, "
                    f"{task.priority.name.lower()} priority"
                )
        conflicts = self.detect_conflicts(tasks)
        if conflicts:
            lines.append("Warnings:")
            lines.extend(f"  {warning}" for warning in conflicts)
        return "\n".join(lines)


def _describe(task: Task) -> str:
    """Short label used in conflict messages."""
    return (
        f"'{task.title}' ({task.pet_name}, "
        f"{task.start_time:%H:%M}-{task.end_time():%H:%M})"
    )
