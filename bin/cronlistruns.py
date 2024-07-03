import os
import sys
import datetime
import json
from croniter import croniter
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from splunklib.searchcommands import dispatch, StreamingCommand, Configuration, Option, validators

@Configuration()
class CronListRuns(StreamingCommand):
    """
    The cronlistruns command returns a list of times that a cron schedule will trigger between a start time and end time.

    Example:

    | makeresults count=1 
    | eval schedule = "*/5 * * * *" 
    | eval start = "2022-01-01 00:00:00" 
    | eval end = "2022-01-02 00:00:00" 
    | cronlistruns schedule=schedule end=end start=start

    returns a record with one new field 'triggers' which is a list of times that the cron schedule will trigger between the start time and end time.
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
            triggers = []

            while True:
                next_run = iter.get_next(datetime.datetime)
                next_run_str = int(next_run.timestamp())
                if next_run > end:
                    break
                triggers.append(next_run_str)

                if len(triggers) >= self.limit:
                    break

            record["triggers"] = triggers
            yield record

dispatch(CronListRuns, sys.argv, sys.stdin, sys.stdout, __name__)