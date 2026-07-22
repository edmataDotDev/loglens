import argparse
from pydantic import BaseModel, field_validator
from datetime import datetime

parser = argparse.ArgumentParser(prog="loglens")
sub = parser.add_subparsers(dest="cmd", required=True)

comun = argparse.ArgumentParser(add_help=False)
comun.add_argument("file")

# summary
p_summary = sub.add_parser("summary", parents=[comun])

# top
p_top = sub.add_parser("top", parents=[comun])
p_top.add_argument("--by", choices=["ip", "path", "status", "user-agent"])
p_top.add_argument("--limit", type=int, default=10)

# error
p_errors = sub.add_parser("errors", parents=[comun])
p_errors.add_argument("--since", type=str)
p_errors.add_argument("--status", type=int, default=500)

# export
p_export = sub.add_parser("export", parents=[comun])
p_export.add_argument("--format", choices=["json", "csv"])
p_export.add_argument("--out", type=str)

# stats
p_stats = sub.add_parser("stats", parents=[comun])
p_stats.add_argument("--window", type=str)


args = parser.parse_args()

# Validators

class LogEntry(BaseModel):
    ip: str
    identd: str
    user_auth: str
    timestamp: datetime
    request: str
    status: int
    bytes: int
    referer: str
    user_agent: str

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_date(cls, value: str):
        return datetime.strptime(
            value,
            "%d/%m/%Y"
        ).date()

def readLine(file):
    with open(file) as log:
        for logLine in log:
            yield logLine

def main():
    print("hello world")



if __name__ == "__main__":
    main()
