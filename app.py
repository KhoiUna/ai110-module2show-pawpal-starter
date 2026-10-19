from datetime import date, time

import pandas as pd
import streamlit as st

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task

PRIORITY_LABELS = {
    Priority.HIGH: "🔴 High",
    Priority.MEDIUM: "🟠 Medium",
    Priority.LOW: "🟢 Low",
}


def task_row(task: Task) -> dict:
    """One display row for a task."""
    return {
        "Date": f"{task.due_date:%a %b %d}",
        "Time": f"{task.start_time:%H:%M}-{task.end_time():%H:%M}",
        "Pet": task.pet_name,
        "Task": task.title,
        "Category": task.category,
        "Priority": PRIORITY_LABELS[task.priority],
        "Repeats": task.frequency.value,
        "Status": "✅ Done" if task.completed else "⏳ To do",
    }


def task_label(task: Task) -> str:
    """Short label for picking a task from a list."""
    return (f"{task.due_date:%a %b %d} {task.start_time:%H:%M} · "
            f"{task.title} ({task.pet_name})")


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' care: add pets and tasks, then get a sorted, "
           "time-budgeted, conflict-checked schedule for today.")

st.divider()

st.subheader("Owner")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Khoi", available_minutes=90)

owner = st.session_state.owner

# Seed the widgets once from the Owner, then let their keys hold the value.
# Passing value=owner.<field> instead would change the widget's identity on
# every edit and make it jump back and forth.
if "owner_name" not in st.session_state:
    st.session_state.owner_name = owner.name
if "available_minutes" not in st.session_state:
    st.session_state.available_minutes = owner.available_minutes

owner.name = st.text_input("Owner name", key="owner_name")
owner.available_minutes = int(
    st.number_input("Minutes available today", min_value=1,
                    max_value=1440, key="available_minutes")
)

st.markdown("### Add a Pet")
with st.form("add_pet", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    age = st.number_input("Age (years)", min_value=0, max_value=50, value=1)
    special_needs = st.text_input(
        "Special needs (comma-separated, optional)")
    if st.form_submit_button("Add pet"):
        if not pet_name.strip():
            st.error("Please enter a pet name.")
        else:
            try:
                owner.add_pet(Pet(
                    name=pet_name.strip(),
                    species=species,
                    age=int(age),
                    special_needs=[need.strip() for need in special_needs.split(",")
                                   if need.strip()],
                ))
                st.success(f"Added {pet_name.strip()}.")
            except ValueError as error:
                st.error(str(error))

if owner.pets:
    st.dataframe(
        [{"Name": pet.name, "Species": pet.species, "Age": pet.age,
          "Special needs": ", ".join(pet.special_needs) or "-"}
         for pet in owner.pets],
        hide_index=True, width="stretch",
    )
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Schedule a Task")
if not owner.pets:
    st.info("Add a pet before scheduling tasks.")
else:
    with st.form("add_task", clear_on_submit=True):
        task_pet = st.selectbox("Pet", [pet.name for pet in owner.pets])
        col1, col2 = st.columns(2)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
            category = st.selectbox(
                "Category", ["walk", "feeding", "medication", "appointment",
                             "grooming", "enrichment", "other"])
            start_time = st.time_input("Start time", value=time(8, 0))
        with col2:
            duration = st.number_input(
                "Duration (minutes)", min_value=1, max_value=240, value=20)
            priority = st.selectbox(
                "Priority", list(Priority), index=2,
                format_func=lambda p: p.name.lower())
            frequency = st.selectbox(
                "Repeats", list(Frequency), format_func=lambda f: f.value)
        if st.form_submit_button("Add task"):
            if not task_title.strip():
                st.error("Please enter a task title.")
            else:
                owner.get_pet(task_pet).add_task(Task(
                    title=task_title.strip(),
                    category=category,
                    start_time=start_time,
                    duration_minutes=int(duration),
                    priority=priority,
                    frequency=frequency,
                ))
                st.success(f"Added '{task_title.strip()}' for {task_pet}.")

scheduler = Scheduler(owner)

st.divider()

st.subheader("✅ Mark a Task Complete")
open_tasks = scheduler.sort_by_time(
    scheduler.filter_tasks(owner.get_all_tasks(), completed=False))
if not open_tasks:
    st.info("No open tasks.")
else:
    with st.form("complete_task"):
        choice = st.selectbox("Task", range(len(open_tasks)),
                              format_func=lambda i: task_label(open_tasks[i]))
        if st.form_submit_button("Mark complete"):
            done = open_tasks[choice]
            next_task = scheduler.complete_task(done)
            if next_task is not None:
                st.success(f"Completed '{done.title}'. Next {done.frequency.value} "
                           f"occurrence added for {next_task.due_date:%A, %b %d}.")
            else:
                st.success(f"Completed '{done.title}'.")

st.subheader("📋 All Tasks")
all_tasks = owner.get_all_tasks()
if not all_tasks:
    st.info("No tasks yet. Add one above.")
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_filter = st.selectbox(
            "Show pet", ["All pets"] + [pet.name for pet in owner.pets],
            key="filter_pet")
    with col2:
        status_filter = st.selectbox(
            "Show status", ["All", "To do", "Done"], key="filter_status")
    with col3:
        sort_choice = st.selectbox(
            "Sort by", ["Time", "Priority"], key="sort_choice")

    filtered = scheduler.filter_tasks(
        all_tasks,
        pet_name=None if pet_filter == "All pets" else pet_filter,
        completed={"All": None, "To do": False, "Done": True}[status_filter],
    )
    ordered = (scheduler.sort_by_time(filtered) if sort_choice == "Time"
               else scheduler.sort_by_priority(filtered))

    if ordered:
        st.caption(f"Showing {len(ordered)} of {len(all_tasks)} tasks, "
                   f"sorted by {sort_choice.lower()}.")
        st.dataframe([task_row(task) for task in ordered],
                     hide_index=True, width="stretch")
    else:
        st.info("No tasks match these filters.")

st.divider()

st.subheader(f"📅 Today's Schedule · {date.today():%A, %B %d}")
plan = scheduler.build_daily_plan(date.today())

if not plan and not scheduler.skipped:
    st.info("No tasks due today.")
else:
    conflicts = scheduler.detect_conflicts(plan)
    used = sum(task.duration_minutes for task in plan)

    col1, col2, col3 = st.columns(3)
    col1.metric("Tasks planned", len(plan))
    col2.metric("Minutes used", f"{used} / {owner.available_minutes}")
    col3.metric("Conflicts", len(conflicts))

    if conflicts:
        for warning in conflicts:
            st.warning(warning, icon="⚠️")
    else:
        st.success("No time conflicts in today's plan.", icon="✅")

    if plan:
        rows = [task_row(task) for task in plan]
        for row in rows:
            del row["Date"]
        st.table(pd.DataFrame(rows).set_index("Time"))

    for task in scheduler.skipped:
        st.info(f"Skipped '{task.title}' ({task.pet_name}, {task.duration_minutes} min, "
                f"{task.priority.name.lower()} priority): not enough time left today.")

    with st.expander("Why this plan?"):
        st.text(scheduler.explain_plan(plan))
