from colorama import Fore, Style


def log_info_time(message, time):
    print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + message + Style.RESET_ALL, time)


def log_warning(message):
    print(Fore.LIGHTRED_EX + Style.BRIGHT + message + Style.RESET_ALL)(base)