"""Demo script: build an owner with two pets and print today's schedule."""

from datetime import date, time

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task


def main() -> None:
    owner = Owner(name="Jordan", available_minutes=90)

    mochi = Pet(name="Mochi", species="dog", age=3)
    luna = Pet(name="Luna", species="cat", age=5,
               special_needs=["daily thyroid pill"])
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task("Morning walk", "walk", time(
        7, 30), 30, Priority.HIGH, Frequency.DAILY))
    luna.add_task(Task("Breakfast", "feeding", time(
        8, 0), 10, Priority.HIGH, Frequency.DAILY))
    luna.add_task(Task("Thyroid pill", "medication", time(
        8, 15), 5, Priority.HIGH, Frequency.DAILY))
    mochi.add_task(Task("Fetch in the yard", "enrichment",
                   time(17, 0), 20, Priority.MEDIUM))
    luna.add_task(Task("Brushing", "grooming", time(
        19, 0), 15, Priority.LOW, Frequency.WEEKLY))

    scheduler = Scheduler(owner)
    plan = scheduler.build_daily_plan(date.today())

    print(f"Today's Schedule ({date.today():%A, %B %d})")
    print("=" * 40)
    print(scheduler.explain_plan(plan))


if __name__ == "__main__":
    main()
