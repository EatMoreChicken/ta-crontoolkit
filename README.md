# Cron Toolkit

Welcome to the Cron Toolkit app.

The purpose of this app to provide a toolkit for visualizing and analyzing cron schedules within Splunk. The app introduces custom commands and easy to use dashboards to make working with cron schedules easier.

## Pre-requisites

**Splunk Timeline - Custom Visualization**

This app requires the Splunk Timeline - Custom Visualization app to be installed. You can download it from [Splunkbase](https://splunkbase.splunk.com/app/3120/).

**Splunk Capability**

Additionally, if you plan to use the dashboards, your account's role will need to have the necessary capabilities to use the `rest` command. This isn't a dealbreaker, but it will limit the functionality of the built-in dashboards.

## Installation

1. Download the app from the latest GitHub release.
2. Install the app on your Splunk instance.
3. Restart Splunk.

## Setup

Currently, the only setup is to configure the app's macros. These macros are used by the app's dashboards. Defaults are provided, but you can modify them to suit your needs.

**crontoolkit_app_allowlist** (Not implemented yet)

Default: `()`

Define a list of apps that are allowed to trigger alerts or appear on dashboards. If you leave this blank, all apps will be included.

**crontoolkit_max_allowed_concurrent_searches** (Not implemented yet)

Default: `16`

Define the maximum number of concurrent searches that should be scheduled at the same time.

**crontoolkit_max_allowed_frequency** (Not implemented yet)

Default: `60`

Define the maximum allowed frequency for schedules within a 1-hour period of time. Any schedule exceeding this frequency would trigger associated alerts or show on related dashboards.

**crontoolkit_saved_search_allowlist** (Not implemented yet)

Default: `()`

Define a list of saved searches that are allowed to trigger alerts or appear on dashboards. If you leave this blank, all saved searches will be included.


## Usage
### Custom Commands
#### `croncountruns`

This command calculates the number of times a cron job is set to trigger within a specified timeframe.

**Syntax**:
```spl
croncountruns schedule=<string> [start=<string>] [end=<string>] [limit=<int>]
```

**Things to note**:
- If you do not specify a `start`, the command will default to the current time.
- If you do not specify an `end`, the command will default to 10 years from the current time.
- The `limit` parameter is used to limit the number of cron triggers to calculate. The default is 43200.

**Examples**:

In this example, we will create a sample cron schedule:

```spl
| makeresults count=1 
| eval schedule = "*/5 * * * *" 
| eval start = "2022-01-01 00:00:00" 
| eval end = "2022-01-02 00:00:00" 
| croncountruns schedule=schedule end=end start=start
| convert ctime(first_trigger_time) ctime(last_trigger_time)
```

This will return the following table:

|_time|schedule|start|end|trigger_count|first_trigger_time|last_trigger_time|
|---|---|---|---|---|---|---|
|2024-07-03 18:56:28|*/5 * * * *|2022-01-01 00:00:00|2022-01-02 00:00:00|288|01/01/2022 00:05:00|01/02/2022 00:00:00|

Here is a real-world example that pulls the cron schedule from saved searches. This example will return the number of times the saved search is set to trigger in the next 10 years (default) from the current time. `43200` is 

```spl
| rest /servicesNS/-/-/saved/searches splunk_server=local search="disabled=0" search="is_scheduled=1" count=10
| fields title cron_schedule
| croncountruns schedule=cron_schedule
| convert ctime(first_trigger_time) ctime(last_trigger_time)
```

#### `cronlistruns`

This command generates a multi-valued list of timestamps in epoch format, indicating when the specified cron schedule will execute.

**Syntax**:
```spl
cronlistruns schedule=<string> [start=<string>] [end=<string>] [limit=<int>]
```

**Things to note**:
- If you do not specify a `start`, the command will default to the current time.
- If you do not specify an `end`, the command will default to 10 years from the current time.
- The `limit` parameter is used to limit the number of cron triggers to calculate. The default is 43200.

**Examples**:

In this example, we will create a sample cron schedule:

```spl
| makeresults count=1 
| eval schedule = "*/5 * * * *" 
| eval start = "2022-01-01 00:00:00" 
| eval end = "2022-01-02 00:00:00" 
| cronlistruns schedule=schedule end=end start=start limit=3
| mvexpand triggers
| convert ctime(triggers)
```

This will return the following table:

|_time|schedule|start|end|triggers|
|---|---|---|---|---|
|2024-07-03 18:59:26|*/5 * * * *|2022-01-01 00:00:00|2022-01-02 00:00:00|01/01/2022 00:05:00|
|2024-07-03 18:59:26|*/5 * * * *|2022-01-01 00:00:00|2022-01-02 00:00:00|01/01/2022 00:10:00|
|2024-07-03 18:59:26|*/5 * * * *|2022-01-01 00:00:00|2022-01-02 00:00:00|01/01/2022 00:15:00|

Here is another real-world example that pulls the cron schedule from saved searches. This example will return the next 10 triggers for the saved search.

```spl
| rest /servicesNS/-/-/saved/searches splunk_server=local search="disabled=0" search="is_scheduled=1" count=10
| fields title cron_schedule
| cronlistruns schedule=cron_schedule limit=10
```

## Dashboards

The dashboards available in this app are meant to provide a starting point to build out your own dashboards. Feel free to clone and modify them to suit your needs.

### Cron Schedule Builder

This dashboard allows you to input a cron schedule to visualize. The panels return various details, such as the number of times the schedule will trigger within the specified timeframe, the next trigger time, and the last trigger time.

![Cron Schedule Builder Image](/appserver/static/images/cron-schedule-builder.png)

### Scheduled Search Timeline

This dashboard allows you to visualize when multiple saved searches are scheduled to trigger. Additionally, this is a quick way to identify concurrent searches that may pose a problem.

![Scheduled Search Timeline](/appserver/static/images/scheduled-search-timeline.png)

### Scheduled Search Analysis

This dashboard provides a list of saved searches and their respective trigger counts. You have several filtering options to help you narrow down the searches you want to analyze. It provides a quick way to find searches that may be running too frequently.

![Scheduled Search Analysis](/appserver/static/images/scheduled-search-analysis.png)

### Scheduled Search Analysis - Detailed

This dashboard visualizes the past and future triggers for a specific saved search. It provides insight into historical triggers, historical runtime, and the expected number of triggers in the future.

![Scheduled Search Analysis - Detailed](/appserver/static/images/scheduled-search-analysis-detailed.png)

--- 

## To-Do
### Custom Commands
 - [ ] `cronnextrun`: This command simply returns the next scheduled trigger time for a specific cron schedule.
 - [ ] `cronlastrun`: This command provides the most recent past trigger time for a specific schedule.

### Saved Searches
- [ ] **Cron Toolkit - Number of Concurrent Searches Exceeded Threshold**: Triggers when a particular time slot is identified as having an excessively high number of saved searches scheduled simultaneously. It's important to note that this search might generate false positives due to the inherent variability in how searches are scheduled, potentially affecting its accuracy. Nevertheless, it can serve as a useful early warning indicator.
- [ ] **Cron Toolkit - Search Schedule Frequency Exceeded Threshold**: Triggers when any of the scheduled searches operate on a cron schedule that surpasses a predetermined frequency limit. This feature is beneficial for identifying instances where users may have set up overly frequent searches or to pinpoint potential misconfigurations in the scheduling process.

### Macros
- [ ] `crontoolkit_max_allowed_frequency`: Defines the maximum allowed frequency for schedules within a 1-hour period of time. Any schedule exceeding this frequency would trigger associated alerts or show on related dashboards.
- [ ] `crontoolkit_max_allowed_concurrent_searches`: Specifies the maximum number of concurrent searches that should be scheduled at the same time.
- [ ] `crontoolkit_saved_search_allowlist`: Lists saved searches that are exempt from triggering alerts or being displayed on dashboards.
- [ ] `crontoolkit_app_allowlist`: Identifies apps that are to be excluded from triggering alerts or appearing on dashboards.

### Random
- [ ] The `cronlistruns.py` has a default limit of `43200`, which might be too high.
- [ ] Update the command limits to use a `limits.conf` if possible.
- [ ] Add support for second repeats?
- [ ] Add check to see if cron schedule is valid and just return an error for that specific item instead of not running the search at all. Currently the search just errors about and doesn't return any results if a cron schedule is invalid.
- [ ] Update `cronlistruns` to return `first_trigger_time` and `last_trigger_time`. (Update dashboards to use this instead of `max()` and `min()`)
- [ ] Base searches for dashboards.
- [ ] Make a macro for the dashboard's time evals.