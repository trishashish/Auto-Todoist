# Auto Todoist
Have you ever been overwhelmed with the number of Todoist tasks due today and spent hours manually re-organizing to spread them out more?

Auto Todoist is a Python script that automatically re-prioritizes Todoist tasks. For each day with tasks exceeding the maximum number of working hours per day, the script sorts tasks by priority, and the lowest-priority tasks are moved to the next day until the total duration of tasks falls below the number of working hours. The same adjustments are made for the next day, the day after, and so on.

**Instructions:**
1. Clone the repository
2. Add your Todoist API key to the `.env` file. This can be found in Todoist > Settings > Integrations > Developer
3. `cd` into the Auto-Todoist folder and run `source venv/bin/activate`
4. Run `app.py`. Make any adjustments to the maximum number of working hours constant or the number of days the script adjusts
