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

    | makeresults count=1 
    | eval schedule = "*/5 * * * *" 
    | eval start = "2022-01-01 00:00:00" 
    | eval end = "2022-01-02 00:00:00" 
    | croncountruns schedule=schedule end=end start=start

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

    DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def parse_datetime(self, value):
        """
        Helper function to parse datetime from various formats.
        """
        try:
            if re.match("^\d{10}$", value):
                return datetime.datetime.fromtimestamp(int(value))
            else:
                return datetime.datetime.strptime(value, self.DEFAULT_DATE_FORMAT)
        except ValueError as e:
            raise ValueError(f"Invalid datetime format: {value}. Expected format: {self.DEFAULT_DATE_FORMAT} or epoch timestamp.")

    def stream(self, records):
        for record in records:
            schedule = str(record[self.schedule])
            start = self.parse_datetime(record.get(self.start, datetime.datetime.now().strftime(self.DEFAULT_DATE_FORMAT)))
            end = self.parse_datetime(record.get(self.end, (datetime.datetime.now() + datetime.timedelta(days=3650)).strftime(self.DEFAULT_DATE_FORMAT)))
            
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
                    trigger_count = self.limit
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