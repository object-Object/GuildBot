import traceback
import sys

def print_command_error(command, error):
	print("\nIgnoring exception in command {}:".format(command), file=sys.stderr)
	traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)