import mariadb
import json
from urllib.parse import urlparse
import asyncio
import mesg
import download

print("")
print(mesg.motd)
print("")

print("Reading config file...")

config = json.loads(open("config.json").read())

print("Connecting to database...")

db = mariadb.connect(
    user=config["db_username"],
    password=config["db_passwd"],
    host=config["db_host"],
    port=config["db_port"],
    database=config["db_dbname"]
)

def remove_item_from_queue():
    with db.cursor() as dbc:
        dbc.execute("delete from queue limit 1;");
        db.commit();

def get_item_from_queue() -> (str):
    with db.cursor() as dbc:
        dbc.execute("select full,jobid from queue limit 1;");
        for x in dbc:
            return x
    return None

async def queue_items():
    while True:
        item = get_item_from_queue()
        if item:
            remove_item_from_queue()
            yield item
        else:
            await asyncio.sleep(config["check_iterval"])
        db.commit() # Commit ensure that the transaction is synced with db state.

async def deamon():
    print("Awaiting queue items...")
    async for (url, jobid) in queue_items():
        data = await download.download_url(url,jobid,db, config);

print("Done!")
asyncio.run(deamon());



