"""Demo script: add tasks out of order, then sort, filter, and print today's schedule."""

from datetime import date, time

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task


def print_tasks(heading: str, tasks: list[Task]) -> None:
    """Print a heading followed by one line per task."""
    print(f"\n{heading}")
    print("-" * len(heading))
    if not tasks:
        print("  (none)")
    for task in tasks:
        status = "done" if task.completed else "to do"
        print(f"  {task.due_date:%a} {task.start_time:%H:%M}  "
              f"{task.title} ({task.pet_name}) [{status}]")


def main() -> None:
    owner = Owner(name="Jordan", available_minutes=90)

    mochi = Pet(name="Mochi", species="dog", age=3)
    luna = Pet(name="Luna", species="cat", age=5,
               special_needs=["daily thyroid pill"])
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Added deliberately out of time order.
    luna.add_task(Task("Brushing", "grooming", time(19, 0), 15,
                       Priority.LOW, Frequency.WEEKLY))
    mochi.add_task(Task("Fetch in the yard", "enrichment", time(17, 0), 20,
                        Priority.MEDIUM))
    luna.add_task(Task("Thyroid pill", "medication", time(8, 15), 5,
                       Priority.HIGH, Frequency.DAILY))
    mochi.add_task(Task("Morning walk", "walk", time(7, 30), 30,
                        Priority.HIGH, Frequency.DAILY))
    luna.add_task(Task("Breakfast", "feeding", time(8, 0), 10,
                       Priority.HIGH, Frequency.DAILY))

    scheduler = Scheduler(owner)
    all_tasks = owner.get_all_tasks()

    print_tasks("Tasks as added (unsorted)", all_tasks)
    print_tasks("Sorted by time", scheduler.sort_by_time(all_tasks))

    print_tasks("Filtered: Luna's tasks",
                scheduler.sort_by_time(
                    scheduler.filter_tasks(all_tasks, pet_name="Luna")))

    # Complete two tasks; the daily pill gets a new occurrence for tomorrow.
    scheduler.complete_task(luna.tasks[1])   # Thyroid pill (daily)
    scheduler.complete_task(mochi.tasks[0])  # Fetch in the yard (once)
    all_tasks = owner.get_all_tasks()

    print_tasks("Filtered: completed",
                scheduler.sort_by_time(
                    scheduler.filter_tasks(all_tasks, completed=True)))
    print_tasks("Filtered: still to do",
                scheduler.sort_by_time(
                    scheduler.filter_tasks(all_tasks, completed=False)))
    print_tasks("Filtered: Mochi's tasks still to do",
                scheduler.sort_by_time(
                    scheduler.filter_tasks(all_tasks, pet_name="Mochi",
                                           completed=False)))

    plan = scheduler.build_daily_plan(date.today())
    print(f"\nToday's Schedule ({date.today():%A, %B %d})")
    print("=" * 40)
    print(scheduler.explain_plan(plan))


if __name__ == "__main__":
    main()
