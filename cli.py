#!/bin/python3
"""
Interface for a crawler
"""

import mariadb
import json
import uuid
from urllib.parse import urlparse

def print_table(headers, data):
    # Compute column widths
    width = [len(header) for header in headers];
    for row in data:
        assert(len(headers) == len(row)) # All the rows in data should be the same width as the headers
        for (i, point) in enumerate(row):
            width[i] = max(width[i], len(point))
    # Row seperator
    seperator = '+' + "+".join(["-"*(colwidth+2) for colwidth in width]) + "+"
    # Format and print header
    line = []
    for (colidx, col) in enumerate(headers):
        line.append(col.ljust(width[colidx]))
    print(seperator)
    print('| ' + " | ".join(line) + " |")
    print(seperator)
    # Format and print data
    for row in data:
        line = []
        for (colidx, col) in enumerate(row):
            line.append(col.ljust(width[colidx]))
        print("| " + " | ".join(line) + " |");
        print(seperator)


config = json.loads(open("config.json").read())

db = mariadb.connect(
    user=config["db_username"],
    password=config["db_passwd"],
    host=config["db_host"],
    port=config["db_port"],
    database=config["db_dbname"]
)

config = json.loads(open("config.json").read())

def add_job(args):
    url = None
    limit_host = True
    while len(args) > 0:
        match (args[0]):
            case "url":
                url = args[1]
                args = args[2:]
            case "spanhosts":
                args = args[1:]
                limit_host = False
            case a:
                print(f"Unknown keyword {a}.")
                return
    if not url:
        print("No url specifyed")
        return
    host_if_limited = None
    if limit_host:
        host_if_limited = urlparse(url).hostname
    dbc = db.cursor()
    jobid = str(uuid.uuid4())
    print(host_if_limited)
    dbc.execute("insert into jobs (jobid,hostname) values (?, ?)", (jobid, host_if_limited));
    dbc.execute("insert into queue (jobid, method, full) values (?,?,?)", (jobid, "GET", url))
    db.commit()
    print(f"Inserted with id {jobid}");


def jobstat(args):
    dbc = db.cursor()
    dbc.execute("select count(*),jobid from queue group by jobid;")
    stat = [(str(count), ident) for (count,ident) in dbc]
    print_table(['Queue length', 'ID'], stat)

def kill_job(args):
    jobid = None
    while len(args) > 0:
        match (args[0]):
            case "uuid":
                jobid = args[1]
                args = args[2:]
            case a:
                print(f"Unkown keyword {a}.")
                return
    if jobid:
        dbc = db.cursor()
        dbc.execute("delete from queue where jobid=?", (jobid,))
        db.commit()
    else:
        print(f"No id specifyed.")
        return

def help(name):
    print(f"Usage {name} [SUBCOMMAND] [ARGS...]")
    print(f"Subcommands:")
    print(f"\tstat: Print information on running jobs")
    print(f"\tadd_job: Adds a job to the queue ")
    print(f"\t\turl [url]: the inital url")
    print(f"\t\tspanhosts : dont restict job to one host")
    print(f"\tkill_job: Remove a job from queue")
    print(f"\t\tuuid [uuid]: The job to kill")

import sys
args = sys.argv[1:]

if len(args) > 0:
    match (args[0]):
        case "add_job":
            add_job(args[1:])
        case "stat":
            jobstat(args[1:])
        case "kill_job":
            kill_job(args[1:])
        case a:
            print(f"Unkown subcommand {a}.")
else:
    help(sys.argv[0])

