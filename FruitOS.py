import sys
import os
import time
import queue
import threading
import subprocess
import socket


alarms = queue.Queue()
prompt_symbol = "FruitOS> "
version = "3.0"
running = True
logged_in_user = None
users = {}  

current_path = os.getcwd()

def setprompt(text):
    global prompt_symbol
    prompt_symbol = text
    print(f"Prompt changed to: {prompt_symbol}")

def alarm_checker():
    while running:
        if not alarms.empty():
            alarm_time = alarms.queue[0]
            current_time = time.strftime("%H:%M")
            if current_time == alarm_time:
                print(f"\n*** ALARM RINGING! Time: {alarm_time} ***")
                alarms.get()
        time.sleep(5)

def calc():
    expr = input("Enter calculation: ")
    try:
        allowed_chars = "0123456789+-*/(). "
        if any(c not in allowed_chars for c in expr):
            raise ValueError("Invalid characters in expression.")
        result = eval(expr)
        print("Result:", result)
    except Exception as e:
        print("Invalid calculation:", e)

def notepad():
    while True:
        print("\nNotepad commands: write, read, exit")
        cmd = input("Notepad> ").strip().lower()
        if cmd == "write":
            note = input("Write your note: ")
            try:
                with open("note.txt", "a", encoding="utf-8") as f:
                    f.write(note + "\n")
                print("Note saved.")
            except Exception as e:
                print("Failed to save note:", e)
        elif cmd == "read":
            try:
                with open("note.txt", "r", encoding="utf-8") as f:
                    content = f.read()
                print("\n--- Notes ---")
                print(content if content else "(No notes yet)")
                print("-------------")
            except FileNotFoundError:
                print("No notes found.")
        elif cmd == "exit":
            print("Exiting notepad.")
            break
        else:
            print("Unknown notepad command.")

def ls():
    try:
        files = os.listdir(current_path)
        for f in files:
            print(f)
    except Exception as e:
        print("Error listing directory:", e)

def cd(path):
    global current_path
    try:
        new_path = os.path.abspath(os.path.join(current_path, path))
        if os.path.isdir(new_path):
            current_path = new_path
            os.chdir(current_path)
        else:
            print("Directory not found:", path)
    except Exception as e:
        print("Error changing directory:", e)

def mkdir(dirname):
    try:
        os.mkdir(os.path.join(current_path, dirname))
        print(f"Directory '{dirname}' created.")
    except Exception as e:
        print("Error creating directory:", e)

def rm(target):
    try:
        full_path = os.path.join(current_path, target)
        if os.path.isfile(full_path):
            os.remove(full_path)
            print(f"File '{target}' removed.")
        elif os.path.isdir(full_path):
            os.rmdir(full_path)
            print(f"Directory '{target}' removed.")
        else:
            print(f"File or directory '{target}' not found.")
    except Exception as e:
        print("Error removing file/directory:", e)

def useradd(username, password):
    if username in users:
        print("User already exists.")
    else:
        users[username] = password
        print(f"User '{username}' added.")

def login(username, password):
    global logged_in_user
    if username in users and users[username] == password:
        logged_in_user = username
        print(f"User '{username}' logged in.")
    else:
        print("Invalid username or password.")

def logout():
    global logged_in_user
    if logged_in_user:
        print(f"User '{logged_in_user}' logged out.")
        logged_in_user = None
    else:
        print("No user is currently logged in.")

def runscript(script_path):
    try:
        full_path = os.path.join(current_path, script_path)
        if not os.path.isfile(full_path):
            print("Script file not found.")
            return
        with open(full_path, "r", encoding="utf-8") as f:
            code = f.read()
        exec(code, globals())
    except Exception as e:
        print("Error running script:", e)

def ping(host):
    try:
        output = subprocess.check_output(["ping", "-c", "4", host], universal_newlines=True)
        print(output)
    except Exception as e:
        print("Ping failed:", e)

def connect(host, port_str):
    try:
        port = int(port_str)
        with socket.create_connection((host, port), timeout=5) as s:
            print(f"Connected to {host} on port {port}")
    except Exception as e:
        print("Connection failed:", e)

def process_command(cmd):
    global prompt_symbol, running

    if not cmd:
        return

    parts = cmd.strip().split()
    base_cmd = parts[0].lower()

    if base_cmd == "help":
        print("Commands: help, about, version, time, calc, notepad, shutdown, exit, setprompt, alarm, ls, cd, mkdir, rm, useradd, login, logout, runscript, ping, connect")

    elif base_cmd == "about":
        print("FruitOS 3.0 - Developed by Cengiz Kara and Other Developers. © 2025")

    elif base_cmd == "version":
        print(f"FruitOS Version {version}")

    elif base_cmd == "time":
        print("Current time:", time.strftime("%Y-%m-%d %H:%M:%S"))

    elif base_cmd == "calc":
        calc()

    elif base_cmd == "notepad":
        notepad()

    elif base_cmd == "shutdown":
        print("Shutting down FruitOS 3.0...")
        running = False
        time.sleep(1)
        print("Goodbye.")
        sys.exit(0)

    elif base_cmd == "exit":
        print("Exiting FruitOS 3.0...")
        running = False
        sys.exit(0)

    elif base_cmd == "setprompt":
        if len(parts) > 1:
            setprompt(" ".join(parts[1:]))
        else:
            print("Usage: setprompt <prompt_text>")

    elif base_cmd == "alarm":
        if len(parts) == 2:
            alarm_time = parts[1]
            if len(alarm_time) == 5 and alarm_time[2] == ":" and alarm_time.replace(":", "").isdigit():
                alarms.put(alarm_time)
                print(f"Alarm set for {alarm_time}")
            else:
                print("Invalid time format. Use HH:MM")
        else:
            print("Usage: alarm <HH:MM>")

    elif base_cmd == "ls":
        ls()

    elif base_cmd == "cd":
        if len(parts) == 2:
            cd(parts[1])
        else:
            print("Usage: cd <directory>")

    elif base_cmd == "mkdir":
        if len(parts) == 2:
            mkdir(parts[1])
        else:
            print("Usage: mkdir <directory>")

    elif base_cmd == "rm":
        if len(parts) == 2:
            rm(parts[1])
        else:
            print("Usage: rm <file_or_directory>")

    elif base_cmd == "useradd":
        if len(parts) == 3:
            useradd(parts[1], parts[2])
        else:
            print("Usage: useradd <username> <password>")

    elif base_cmd == "login":
        if len(parts) == 3:
            login(parts[1], parts[2])
        else:
            print("Usage: login <username> <password>")

    elif base_cmd == "logout":
        logout()

    elif base_cmd == "runscript":
        if len(parts) == 2:
            runscript(parts[1])
        else:
            print("Usage: runscript <script_path>")

    elif base_cmd == "ping":
        if len(parts) == 2:
            ping(parts[1])
        else:
            print("Usage: ping <host>")

    elif base_cmd == "connect":
        if len(parts) == 3:
            connect(parts[1], parts[2])
        else:
            print("Usage: connect <host> <port>")

    else:
        print("Unknown command:", base_cmd)

def main():
    print("Welcome to FruitOS 3.0!")
    alarm_thread = threading.Thread(target=alarm_checker, daemon=True)
    alarm_thread.start()

    while running:
        try:
            cmd = input(prompt_symbol)
            process_command(cmd)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting FruitOS 3.0...")
            break

if __name__ == "__main__":
    main()
