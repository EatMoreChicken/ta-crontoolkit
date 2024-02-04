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

    ``| makeresults count=1 | eval schedule = "*/5 * * * *" | eval start = "2022-01-01 00:00:00" | eval end = "2022-01-02 00:00:00" | cronlistruns schedule=schedule end=end start=start``

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

    def stream(self, records):
        date_format = "%Y-%m-%d %H:%M:%S"
        self.logger.debug('CronListRuns: %s', self)
        for record in records:
            schedule = str(record[self.schedule])
            if self.start in record:
                start = str(record[self.start])
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
                if re.match("^\d{10}", end):
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