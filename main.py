import argparse
from pydantic import BaseModel, field_validator
from datetime import datetime
from rich import print
from rich.console import Console
from rich.table import Table
from rich.columns import Columns
import re
from typing import Literal
import math

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

# {
#     'ip': '66.111.54.249',
#     'date': '22/Jan/2019:04:01:46 +0330',
#     'method': 'GET',
#     'route': '/image/56228/productModel/150x150',
#     'protocols': 'HTTP/1.1',
#     'status': '200',
#     'bytes': '2509',
#     'referer': 
        # 'https://www.zanbil.ir/m/product/34024/64841/%DB%8C%D8%AE%DA%86%D8%A7%D9%84-%D9%81%D8%B1%DB%8C%D8%B2%D8%B1-%D9%81%D8%B1%DB%8C%D8%B2%D8%B1-%D9%BE%D8%A7%DB%8C%DB%8C%D9%86-%
        # D8%AF%D9%88%D9%88-%D9%85%D8%AF%D9%84-Ultimo-D2BF-0028GW',
#     'user_agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900H Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.93 Mobile Safari/537.36'
# }

class LogEntry(BaseModel):
    ip: str
    identd: str
    user_auth: str
    date: datetime
    route: str
    method: Literal['GET', 'POST', 'DELETE', 'PUT', 'PATCH', 'HEAD', 'OPTIONS']
    protocols: str
    status: int
    bytes: int
    referer: str
    user_agent: str

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, value: str):
        return datetime.strptime(
            value,
            "%d/%b/%Y:%H:%M:%S %z"
        )

def readLine(file):
    with open(file) as log:
        for logLine in log:
            yield logLine

LOG_PATTERN = re.compile(
    r'(?P<ip>\S+) '
    r'(?P<identd>\S+) (?P<user_auth>\S+) '     # ahora SÍ con nombre
    r'\[(?P<date>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<route>\S+) (?P<protocols>[^"]+)" '
    r'(?P<status>\d+) (?P<bytes>\S+) '
    r'"(?P<referer>[^"]*)" '
    r'"(?P<user_agent>[^"]*)"'
)


def main():
    lineGenerator = readLine(args.file)
    console = Console()

    match args.cmd:
        case "summary":
            failedCount = 0
            sucessCount = 0
            ips = set()
            statusCounter = {}
            
            firstLog = None
            lastLog = None

            for line in readLine(args.file):
                rawLog = LOG_PATTERN.match(line)
                if rawLog:
                    logData = rawLog.groupdict()
                    try:
                        logEntry = LogEntry(
                            ip=logData['ip'], 
                            identd=logData['identd'], 
                            user_auth=logData['user_auth'],
                            date=logData['date'],
                            method=logData['method'],
                            route=logData['route'],
                            protocols=logData['protocols'],
                            status=logData['status'],
                            bytes=logData['bytes'],
                            referer=logData['referer'],
                            user_agent=logData['user_agent']
                        )
                        ips.add(logEntry.ip)

                        # frist and last log
                        if sucessCount == 0 and failedCount == 0:
                            firstLog = logEntry
                        lastLog = logEntry

                        # status counter
                        generalStatus = logData['status'][0] + "xx"
                        if generalStatus in statusCounter:
                            statusCounter[generalStatus] += 1
                        else:
                            statusCounter[generalStatus] = 1

                        sucessCount += 1
                    except ValueError as exc:
                        failedCount += 1

            summaryTable = Table(title="Summary", show_header=False)
            statusTable = Table(title="Status %", show_header=False)

            summaryTable.add_row("Requests", str(sucessCount))
            summaryTable.add_row("Unique IPs", str(len(ips)))
            summaryTable.add_row("Date Range", firstLog.date.strftime("%Y-%m-%d %H:%M:%S %Z") + " - " + lastLog.date.strftime("%Y-%m-%d %H:%M:%S %Z"))
            summaryTable.add_row("Skipped", str(failedCount))

            for status in sorted(statusCounter.keys()):
                percentage = math.trunc((statusCounter[status] / sucessCount) * 100 * 100) / 100
                statusTable.add_row(status, f"{percentage:.2f}%")
                
            console.print(Columns([summaryTable, statusTable]))

        case "top":
            print("top")
        case "error":
            print("error")
        case "export":
            print("export")
        case "stats":
            print("stats")


if __name__ == "__main__":
    main()
