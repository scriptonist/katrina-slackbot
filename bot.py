import os
import time
from slackclient import SlackClient

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

tasklist = {}

def create_remainder(channel,command,command_name):
    """
        Creates a remainder
        @params
        channel - Channel from which command was posted
        command - Command that user typed
        command_name - Command that system identified
    """
    global tasklist
    command = command.split()
    deadline = ' '.join(command[-3:])
    task =  ' '.join(command[1:len(command)-3])
    deadline_obj = time.strptime(deadline,"%b %d %Y")
    deadline_obj_str = time.strftime('%m/%d/%Y',deadline_obj)
    tasklist[task] = [deadline_obj,deadline_obj_str]
    response = "Task Added : " + task + " on " + deadline_obj_str

    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)

def get_help(channel,command,command_name):
    command = command.split()
    response = COMMAND_HELP[command[1]]
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)
def show_tasks(channel,command,command_name):
    response = ""
    for task in tasklist:
        response += task + "\n"
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)
                          
# Functions which handle the different commands
COMMAND_HANDLERS = {"create":create_remainder,"help":get_help,"show":show_tasks}


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

if __name__ == "__main__":
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
