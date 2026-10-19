from datetime import date, time, timedelta

from pawpal_system import Frequency, Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    task = Task("Morning walk", "walk", time(7, 30), 30)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog", age=3)
    assert len(pet.tasks) == 0

    pet.add_task(Task("Breakfast", "feeding", time(8, 0), 10))

    assert len(pet.tasks) == 1


def test_completing_daily_task_creates_next_day_occurrence():
    today = date(2026, 10, 18)
    owner = Owner(name="Jordan", available_minutes=90)
    pet = Pet(name="Luna", species="cat", age=5)
    owner.add_pet(pet)
    pill = Task("Thyroid pill", "medication", time(8, 15), 5,
                frequency=Frequency.DAILY, due_date=today)
    pet.add_task(pill)

    next_pill = Scheduler(owner).complete_task(pill, completed_on=today)

    assert pill.completed is True
    assert next_pill.due_date == today + timedelta(days=1)
    assert next_pill.completed is False
    assert next_pill.title == pill.title and next_pill.pet_name == "Luna"
    assert next_pill in pet.tasks and len(pet.tasks) == 2


def test_completing_weekly_task_creates_occurrence_one_week_later():
    today = date(2026, 10, 18)
    brushing = Task("Brushing", "grooming", time(19, 0), 15,
                    frequency=Frequency.WEEKLY, due_date=today)

    next_brushing = brushing.mark_complete(completed_on=today)

    assert next_brushing.due_date == today + timedelta(weeks=1)


def test_completing_one_time_task_creates_nothing():
    task = Task("Vet visit", "appointment", time(10, 0), 60)

    assert task.mark_complete() is None


def test_late_daily_task_next_occurrence_is_tomorrow():
    today = date(2026, 10, 18)
    walk = Task("Morning walk", "walk", time(7, 30), 30,
                frequency=Frequency.DAILY, due_date=today - timedelta(days=3))

    next_walk = walk.mark_complete(completed_on=today)

    assert next_walk.due_date == today + timedelta(days=1)


def test_completing_twice_does_not_duplicate():
    owner = Owner(name="Jordan", available_minutes=90)
    pet = Pet(name="Mochi", species="dog", age=3)
    owner.add_pet(pet)
    walk = Task("Morning walk", "walk", time(7, 30), 30,
                frequency=Frequency.DAILY)
    pet.add_task(walk)
    scheduler = Scheduler(owner)

    scheduler.complete_task(walk)
    assert scheduler.complete_task(walk) is None
    assert len(pet.tasks) == 2
