import os
from dotenv import load_dotenv
from todoist_api_python.api import TodoistAPI
from enum import Enum
from datetime import datetime, timedelta, date

load_dotenv()
todoist_api_key = os.getenv('TODOIST_API_KEY')
api = TodoistAPI(todoist_api_key)

# Set the maximum number of hours you can work per day. Tasks that cause you to exceed this limit will be moved to the next day.
WORKING_HOURS_PER_DAY = 1

class DayEnglish(Enum):
    """Enum for common days in English"""
    TODAY = 'today'
    TOMORROW = 'tomorrow'

def format_date(year: int, month: int, day: int) -> str:
    """Format year, month, and day values as a string in the format YYYY-MM-DD"""
    return f"{year:04d}-{month:02d}-{day:02d}"

def get_next_day(day: DayEnglish | str) -> str:
    """Get the next day as a string in the format YYYY-MM-DD"""
    if isinstance(day, DayEnglish):
        day = get_date_string_from_day_english(day)
    current_date = datetime.strptime(day, "%Y-%m-%d")
    next_day = current_date + timedelta(days=1)
    return next_day.strftime("%Y-%m-%d")

def get_date_string_from_day_english(day: DayEnglish) -> str:
    """Get the YYYY-MM-DD date string for the specified day in English"""
    today = date.today()
    if day == DayEnglish.TODAY:
        return format_date(today.year, today.month, today.day)
    elif day == DayEnglish.TOMORROW:
        tomorrow = today + timedelta(days=1)
        return format_date(tomorrow.year, tomorrow.month, tomorrow.day)

def get_incomplete_tasks(day: DayEnglish | str):
    """Get all incomplete tasks due on the specified day"""
    try:
        all_tasks = api.get_tasks(filter=f"due: {day.value if isinstance(day, DayEnglish) else day}")
        return [task for task in all_tasks if task.is_completed is False]
    except Exception as error:
        print(error)

def move_tasks(tasks: list, day: DayEnglish | str):
    """Move tasks to the specified day"""
    for task in tasks:
        try:
            api.update_task(task_id=task.id, due_string = day.value if isinstance(day, DayEnglish) else day)
        except Exception as error:
            print(error)

def tasks_to_move(tasks: list):
    """
    Get the tasks that need to be moved to the next day.
    The list of tasks needing to be moved is determined by
    the total time of the tasks exceeding the maximum number 
    of working hours per day. The lowest priority tasks
    are prioritized for moving first.
    """
    tasks.sort(key=lambda x: x.priority, reverse=True)
    total_time = 0
    tasks_to_move = []
    for task in tasks:
        if task.duration is None:
            task_duration_hours = 45 / 60
        else:
            if task.duration['unit'] == 'minute':
                task_duration_hours = task.duration['amount'] / 60
            elif task.duration['unit'] == 'day':
                task_duration_hours = task.duration['amount'] * 24

        total_time += task_duration_hours

        if total_time > WORKING_HOURS_PER_DAY:
            tasks_to_move.append(task)

    return tasks_to_move

def day_is_valid(day: DayEnglish | str):
    """
    Check if the specified day is valid. A valid
    day is one where the total time of the tasks
    does not exceed the maximum number of working
    hours per day.
    """
    incomplete_tasks = get_incomplete_tasks(day)
    return len(tasks_to_move(incomplete_tasks)) == 0

def move_deprioritized_tasks_to_next_day(day: DayEnglish | str):
    """
    Move deprioritized tasks to the next day. Deprioritized
    tasks are returned by tasks_to_move(tasks).
    """
    incomplete_tasks = get_incomplete_tasks(day)
    next_day = get_next_day(day)
    tasks_to_move_tomorrow = tasks_to_move(incomplete_tasks)
    move_tasks(tasks_to_move_tomorrow, get_next_day(day))
    return (len(tasks_to_move_tomorrow), day, next_day)

def main():
    """
    Moves the due dates of lower-priority tasks for the next 5 days 
    to ensure that none of the days exceed the maximum number of 
    working hours.
    """
    summary = []
    base_day = DayEnglish.TODAY
    # Loop through the next 5 days and adjust them as needed
    for i in range(5):
        current_day = get_next_day(base_day) if i > 0 else base_day
        if not day_is_valid(current_day):
            num_moved, from_day, to_day = move_deprioritized_tasks_to_next_day(current_day)
            summary.append(f"Moved {num_moved} task{"s" if num_moved > 1 else ""} from {from_day if not isinstance(from_day, DayEnglish) else from_day.value} to {to_day}")
        base_day = current_day
    
    for action in summary:
        print(action)

if __name__ == "__main__":
    main()

