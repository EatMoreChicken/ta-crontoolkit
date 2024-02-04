import os
import sys
import datetime
import json
from croniter import croniter

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
        require=True,
        validate=validators.Fieldname(),
    )
    end = Option(
        doc="The end time",
        require=True,
        validate=validators.Fieldname(),
    )
    limit = Option(
        doc="The limit of trigger counts",
        require=False,
        validate=validators.Integer(),
        default=20
    )

    def stream(self, records):
        self.logger.debug('CronListRuns: %s', self)
        for record in records:
            schedule = record["schedule"]
            start = datetime.datetime.strptime(record["start"], "%Y-%m-%d %H:%M:%S")
            end = datetime.datetime.strptime(record["end"], "%Y-%m-%d %H:%M:%S")

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