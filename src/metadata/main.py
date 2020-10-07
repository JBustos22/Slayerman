import yaml


def get_commands_dict():
    """load the commands yaml file into a python dictionary"""
    try:
        with open('metadata/commands.yaml', 'r') as f:
            commands_dict = yaml.safe_load(f)
            f.close()
        return commands_dict
    except:
        return None


def create_help_message():
    """format a message based on command metadata"""
    commands_dict = get_commands_dict()
    msg = ""
    for command, details in commands_dict.items():
        command_snippet = f"```---- {command}\n" \
            f"Description: {details['description']}\n" \
            f"Usage: {details['usage']}" \
            + (f"\nArguments: {details['arguments']}```" if details['arguments'] != 'None' else "```")  # optional
        msg += command_snippet
    return msg


def get_usage(command: str):
    """get the usage of a specified command"""
    commands_dict = get_commands_dict()
    return commands_dict[command]['usage']