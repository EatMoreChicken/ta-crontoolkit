import os
import sys
import datetime
from croniter import croniter
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from splunklib.searchcommands import dispatch, StreamingCommand, Configuration, Option, validators


@Configuration()
class CronCountRuns(StreamingCommand):
    """
    The croncountruns command returns the number of times a cron schedule will trigger between a start time and end time.

    Example:

    ``| makeresults count=1 | eval schedule = "*/5 * * * *" | eval start = "2022-01-01 00:00:00" | eval end = "2022-01-02 00:00:00" | croncountruns schedule=schedule end=end start=start``

    returns a record with one new field 'trigger_count' which is the number of times the cron schedule will trigger between the start time and end time.
    """

    schedule = Option(
        doc="The cron schedule",
        require=True,
        validate=validators.Fieldname(),
    )
    start = Option(
        doc="The start time",
        require=False,
        validate=validators.Fieldname(),
    )
    end = Option(
        doc="The end time",
        require=False,
        validate=validators.Fieldname(),
    )
    limit = Option(
        doc="The limit of trigger counts",
        require=False,
        validate=validators.Integer(),
        default=43200
    )

    def stream(self, records):
        date_format = "%Y-%m-%d %H:%M:%S"
        for record in records:
            schedule = str(record[self.schedule])
            if self.start in record:
                start = str(record[self.start])
                if start == "":
                    start = datetime.datetime.now()
                    start = start.strftime(date_format)
                if re.match("^\d{10}", start):
                    start = re.match("^\d{10}", start).group()
                if not isinstance(start, datetime.datetime):
                    try:
                        start = datetime.datetime.strptime(start, date_format)
                    except ValueError:
                        try:
                            start = datetime.datetime.fromtimestamp(int(start))
                        except ValueError:
                            raise ValueError(f"Invalid start time format. Expected format: {date_format} or epoch timestamp: {start}")
                else:
                    raise ValueError(f"Invalid start time format. Expected format: {date_format} or epoch timestamp: {start}")
            else:
                start = datetime.datetime.now()
            if self.end in record:
                end = str(record[self.end])
                if end == "":
                    end = datetime.datetime.now() + datetime.timedelta(days=365 * 10)
                    end = end.strftime(date_format)
                elif re.match("^\d{10}", end):
                    end = re.match("^\d{10}", end).group()
                if not isinstance(end, datetime.datetime):
                    try:
                        end = datetime.datetime.strptime(end, date_format)
                    except ValueError:
                        try:
                            end = datetime.datetime.fromtimestamp(int(end))
                        except ValueError:
                            raise ValueError(f"Invalid end time format. Expected format: {date_format} or epoch timestamp: {end}")
                else:
                    raise ValueError(f"Invalid end time format. Expected format: {date_format} or epoch timestamp: {end}")
            else:
                end = datetime.datetime.now() + datetime.timedelta(days=365 * 10)

            iter = croniter(schedule, start)
            trigger_count = 0
            first_trigger_time = None
            last_trigger_time = None

            while True:
                next_run = iter.get_next(datetime.datetime)
                if next_run > end:
                    break
                trigger_count += 1

                if self.limit != 0 and trigger_count > self.limit:
                    trigger_count = str(self.limit)
                    break

                if first_trigger_time is None:
                    first_trigger_time = next_run
                last_trigger_time = next_run

            record["trigger_count"] = trigger_count
            if first_trigger_time is not None:
                record["first_trigger_time"] = int(first_trigger_time.timestamp())
            if last_trigger_time is not None:
                record["last_trigger_time"] = int(last_trigger_time.timestamp())
            yield record

dispatch(CronCountRuns, sys.argv, sys.stdin, sys.stdout, __name__)