import os
import time
from slackclient import SlackClient

# Set Up Mongo Connection
from pymongo import MongoClient
client = MongoClient(os.environ.get("MONGO_CONNECTION_STRING"))
db = client[os.environ.get("COLLECTION_NAME")]
remainders = db.remainders


# The bots enivironment variable
BOT_ID = os.environ.get("BOT_ID")

#instantiante Slack
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

# Constants
AT_BOT = "<@"  + BOT_ID + ">"

# Command help strings

COMMAND_HELP = {"create":"Create new remainder format, format - | create <subject> <deadline> |",\
    "help":"get help for a command, format - | help <command name> |",\
    "show":"shows currently added remainders format | show |"}


def create_remainder(channel,command,command_name):
    """
        Creates a remainder
        @params
        channel - Channel from which command was posted
        command - Command that user typed
        command_name - Command that system identified
    """
    command = command.split()
    deadline = ' '.join(command[-3:])
    task =  ' '.join(command[1:len(command)-3])
    deadline_obj = time.strptime(deadline,"%b %d %Y")
    deadline_obj_str = time.strftime('%m/%d/%Y',deadline_obj)
    rem = {"task name":task,"deadline":deadline_obj}
    remainders.insert_one(rem)
    response = "Task Added : " + task + " on " + deadline_obj_str

    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)

def get_help(channel,command,command_name):
    command = command.split()
    if len(command) == 1:
        response = COMMAND_HELP[command[0]]
    elif len(command) == 2:
        response = COMMAND_HELP[command[1]]
    else:
        response = "Soory! I didn't get that. Is the format correct?? Eg. help <command name>"
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)
def show_tasks(channel,command,command_name):
    response = ""
    tasklist = remainders.find()
    for task in tasklist:
        dline = datetime.strftime(task['deadline'],'%m/%d/%Y')
        response += task["task name"] + " Complete by " + dline + "\n"
    else:
        response = "Task List is Empty"
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)

def show_commands(channel,command,command_name):
    response = "These commands are now avilable ! \n"
    for cmd in COMMAND_HELP.keys():
        response += cmd + "\n"
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)

# Functions which handle the different commands
COMMAND_HANDLERS = {"create":create_remainder,"help":get_help,"show":show_tasks,"commands":show_commands}


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    for command_list_command in COMMAND_HANDLERS.keys():
        if command.startswith(command_list_command):
            COMMAND_HANDLERS[command_list_command](channel,command,command_list_command)
            


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None

def startBot():
    READ_WEBSOCKET_DELAY = 1 # 1 Second delay on reading from firehose
    if slack_client.rtm_connect():
        print("Katrina is Connected and running !")
        while True:
            command,channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command,channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection Failed. Invalid Slack token or Bot ID")

if  __name__ == "__main__":
    startBot()