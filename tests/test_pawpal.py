from datetime import date, time, timedelta

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task


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


def _owner_with_two_pets():
    owner = Owner(name="Jordan", available_minutes=120)
    owner.add_pet(Pet(name="Mochi", species="dog", age=3))
    owner.add_pet(Pet(name="Luna", species="cat", age=5))
    return owner


def test_detects_same_time_conflict_between_different_pets():
    owner = _owner_with_two_pets()
    owner.get_pet("Mochi").add_task(Task("Breakfast", "feeding", time(8, 0), 10))
    owner.get_pet("Luna").add_task(Task("Breakfast", "feeding", time(8, 0), 10))

    warnings = Scheduler(owner).detect_conflicts(owner.get_all_tasks())

    assert len(warnings) == 1
    assert "different pets" in warnings[0]


def test_detects_overlap_for_same_pet():
    owner = _owner_with_two_pets()
    luna = owner.get_pet("Luna")
    luna.add_task(Task("Thyroid pill", "medication", time(8, 15), 5))
    luna.add_task(Task("Ear drops", "medication", time(8, 15), 5))

    warnings = Scheduler(owner).detect_conflicts(owner.get_all_tasks())

    assert len(warnings) == 1
    assert "same pet" in warnings[0]


def test_back_to_back_and_different_day_tasks_do_not_conflict():
    owner = _owner_with_two_pets()
    mochi = owner.get_pet("Mochi")
    mochi.add_task(Task("Walk", "walk", time(7, 30), 30))
    mochi.add_task(Task("Feed", "feeding", time(8, 0), 10))  # starts as walk ends
    mochi.add_task(Task("Walk", "walk", time(7, 30), 30,
                        due_date=date.today() + timedelta(days=1)))

    assert Scheduler(owner).detect_conflicts(owner.get_all_tasks()) == []


def test_conflict_check_finds_every_overlapping_pair():
    owner = _owner_with_two_pets()
    mochi = owner.get_pet("Mochi")
    mochi.add_task(Task("Long walk", "walk", time(8, 0), 120))  # 08:00-10:00
    mochi.add_task(Task("Feed", "feeding", time(8, 30), 10))
    mochi.add_task(Task("Pill", "medication", time(9, 30), 5))

    warnings = Scheduler(owner).detect_conflicts(owner.get_all_tasks())

    assert len(warnings) == 2  # long walk overlaps both; feed and pill don't overlap


def test_sort_by_time_returns_chronological_order():
    owner = _owner_with_two_pets()
    mochi = owner.get_pet("Mochi")
    luna = owner.get_pet("Luna")
    mochi.add_task(Task("Evening walk", "walk", time(18, 0), 30))
    luna.add_task(Task("Breakfast", "feeding", time(7, 0), 10))
    mochi.add_task(Task("Lunch", "feeding", time(12, 30), 10))
    luna.add_task(Task("Thyroid pill", "medication", time(8, 15), 5))

    ordered = Scheduler(owner).sort_by_time(owner.get_all_tasks())

    assert [t.start_time for t in ordered] == [
        time(7, 0), time(8, 15), time(12, 30), time(18, 0)]


def test_sort_by_time_puts_earlier_days_first_and_breaks_ties_by_priority():
    today = date(2026, 10, 18)
    tomorrow_early = Task("Walk", "walk", time(6, 0), 30,
                          due_date=today + timedelta(days=1))
    today_low = Task("Brush", "grooming", time(9, 0), 10,
                     priority=Priority.LOW, due_date=today)
    today_high = Task("Pill", "medication", time(9, 0), 5,
                      priority=Priority.HIGH, due_date=today)

    ordered = Scheduler(_owner_with_two_pets()).sort_by_time(
        [tomorrow_early, today_low, today_high])

    assert ordered == [today_high, today_low, tomorrow_early]


def test_daily_plan_is_returned_in_chronological_order():
    today = date(2026, 10, 18)
    owner = _owner_with_two_pets()
    mochi = owner.get_pet("Mochi")
    mochi.add_task(Task("Evening walk", "walk", time(18, 0), 30,
                        priority=Priority.HIGH, due_date=today))
    mochi.add_task(Task("Breakfast", "feeding", time(7, 0), 10,
                        priority=Priority.LOW, due_date=today))
    mochi.add_task(Task("Pill", "medication", time(12, 0), 5,
                        priority=Priority.MEDIUM, due_date=today))

    plan = Scheduler(owner).build_daily_plan(today)

    assert [t.title for t in plan] == ["Breakfast", "Pill", "Evening walk"]
