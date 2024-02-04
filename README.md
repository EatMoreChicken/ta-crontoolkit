# TA-crontoolkit

This app enhances the Splunk experience by introducing custom commands, dashboards, and saved searches, making it simpler for users to manage, analyze, and visualize cron schedules.

## Usage
- [ ] Build usage based on the `searchbng.conf`. Maybe automate this?

## Custom Commands
 - [ ] `croncountruns`: This command calculates the number of times a cron job is set to trigger within a specified timeframe. A practical application could be to use this command on a list of scheduled search cron schedules to generate a new field indicating how often the cron will trigger. This can help identify searches that run too frequently, potentially due to scheduling errors, or to adjust the schedule as needed for optimization.
 - [ ] `cronlistruns`: This command generates a multi-valued list of timestamps in epoch format, indicating when the specified cron schedule will execute. A use case for this command could be to apply it to a list of scheduled search cron schedules to obtain a new field detailing the specific times a cron schedule will run. This allows for analysis of how often different saved searches are set to run concurrently.
 - [ ] `cronnextrun`: This command simply returns the next scheduled trigger time for a specific cron schedule.
 - [ ] `cronlastrun`: This command provides the most recent past trigger time for a specific schedule.

## Dashboards
- [ ] **Cron Toolkit - Scheduled Search Analysis**: A dashboard with panels designed to assist in the analysis of scheduled searches.
    - [ ] Inputs for toggling enabled searches, setting a cron trigger limit, choosing a relative end date/start date, and a field for entering saved search names with wildcard support.
    - [ ] A timeline panel displaying a visual representation of when the specified saved searches are scheduled to trigger.
    - [ ] Panel will specific times sorted with the highest number of triggers on a timeslot at the top.
- [ ] **Cron Toolkit - Scheduled Search Analysis - Individual**: A dashboard with panels to pull specific infomration from a saved search to see more details.
    - [ ] Input to select a saved search and the cron from the saved search (also allows for custom cron schdule input to test).
    - [ ] Timeline with past triggers and the estimated triggers into the future.
    - [ ] KPIs: Expected triggers in the specified times, how many overlaps with other scheduled searches.
- [ ] **Cron Toolkit - Schedule Builder**: A dashboard aimed at facilitating the creation of cron schedules. It features:
    - [ ] An input field for a cron schedule, which upon submission, provides a timeline indicating when it will trigger, the number of times it will do so between a specified date range.
    - [ ] Other scheduled searches that are set to run concurrently.

## Saved Searches
- [ ] **Cron Toolkit - Number of Concurrent Searches Exceeded Threshold**: Triggers when a particular time slot is identified as having an excessively high number of saved searches scheduled simultaneously. It's important to note that this search might generate false positives due to the inherent variability in how searches are scheduled, potentially affecting its accuracy. Nevertheless, it can serve as a useful early warning indicator.
- [ ] **Cron Toolkit - Search Schedule Frequency Exceeded Threshold**: Triggers when any of the scheduled searches operate on a cron schedule that surpasses a predetermined frequency limit. This feature is beneficial for identifying instances where users may have set up overly frequent searches or to pinpoint potential misconfigurations in the scheduling process.

## Macros
- [x] `crontoolkit_max_allowed_frequency`: Defines the maximum allowed frequency for schedules within a 1-hour period of time. Any schedule exceeding this frequency would trigger associated alerts or show on related dashboards.
- [x] `crontoolkit_max_allowed_concurrent_searches`: Specifies the maximum number of concurrent searches that should be scheduled at the same time.
- [x] `crontoolkit_saved_search_allowlist`: Lists saved searches that are exempt from triggering alerts or being displayed on dashboards.
- [x] `crontoolkit_app_allowlist`: Identifies apps that are to be excluded from triggering alerts or appearing on dashboards.


## Random To-Dos
- [ ] The `cronlistruns.py` has a default limit of `43200`, which might be too high.
- [ ] Update the command limits to use a `limits.conf` if possible.