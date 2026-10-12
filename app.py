from datetime import date, time

import streamlit as st

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

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
    st.table([
        {"name": pet.name, "species": pet.species, "age": pet.age,
         "special needs": ", ".join(pet.special_needs)}
        for pet in owner.pets
    ])
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

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("Current tasks:")
    st.table([
        {"pet": task.pet_name, "title": task.title, "category": task.category,
         "date": task.due_date.isoformat(), "start": f"{task.start_time:%H:%M}",
         "minutes": task.duration_minutes, "priority": task.priority.name.lower(),
         "repeats": task.frequency.value, "done": task.completed}
        for task in Scheduler(owner).sort_by_time(all_tasks)
    ])
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Builds today's plan from every pet's tasks, highest priority first, "
           "within your available minutes.")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.build_daily_plan(date.today())
    if plan:
        st.table([
            {"time": f"{task.start_time:%H:%M}-{task.end_time():%H:%M}",
             "pet": task.pet_name, "task": task.title,
             "priority": task.priority.name.lower(), "repeats": task.frequency.value}
            for task in plan
        ])
        for warning in scheduler.detect_conflicts(plan):
            st.warning(warning)
    for task in scheduler.skipped:
        st.info(
            f"Skipped '{task.title}' ({task.pet_name}): not enough time left.")
    st.text(scheduler.explain_plan(plan))
