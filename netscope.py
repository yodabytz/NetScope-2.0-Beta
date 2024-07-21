#!/usr/bin/python3

import psutil
import curses
import time
import os

def get_process_name(pid):
    try:
        process = psutil.Process(pid)
        return process.name()
    except psutil.NoSuchProcess:
        return None

def get_process_user(pid):
    try:
        process = psutil.Process(pid)
        return process.username()
    except psutil.NoSuchProcess:
        return None

def format_size(bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024

def get_connections(status_filter):
    connections = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == status_filter:
            laddr = f"{conn.laddr.ip}:{conn.laddr.port}".replace('::ffff:', '').ljust(25)
            raddr = f"{conn.raddr.ip}:{conn.raddr.port}".replace('::ffff:', '').ljust(25) if conn.raddr else "".ljust(25)
            status = conn.status.ljust(12)
            pid = str(conn.pid).ljust(8)
            program = get_process_name(conn.pid).ljust(20) if conn.pid else "".ljust(20)
            user = get_process_user(conn.pid).ljust(15) if conn.pid else "".ljust(15)
            connections.append([laddr, raddr, status, pid, program, user])
    return connections

def get_all_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'nice', 'memory_info', 'memory_percent', 'cpu_percent', 'cpu_times', 'status']):
        pid = str(proc.info['pid']).ljust(8)
        user = proc.info['username'].ljust(15)
        nice = str(proc.info['nice']).ljust(5)
        memory_info = proc.info['memory_info']
        memory_percent = f"{proc.info['memory_percent']:.1f}".ljust(5)
        cpu_percent = f"{proc.info['cpu_percent']:.1f}".ljust(5)
        status = proc.info['status'].ljust(5)
        virt = format_size(memory_info.vms).ljust(8) if memory_info else "N/A".ljust(8)
        res = format_size(memory_info.rss).ljust(8) if memory_info else "N/A".ljust(8)
        shr = format_size(memory_info.shared).ljust(8) if memory_info else "N/A".ljust(8)
        cpu_time = f"{proc.info['cpu_times'].user:.2f}".ljust(8)
        command = proc.info['name'].ljust(20)
        processes.append([pid, user, nice, virt, res, shr, status, cpu_percent, memory_percent, cpu_time, command])
    return processes

def draw_table(window, title, connections, start_y, start_x, width, start_idx, max_lines, active):
    title_color = curses.color_pair(2) | curses.A_BOLD if active else curses.color_pair(2)
    header_color = curses.color_pair(4)
    text_color = curses.color_pair(1)

    window.addstr(start_y, start_x, title, title_color)
    headers = ["Local Address", "Remote Address", "Status", "PID", "Program", "User", "Data Sent", "Data Recv"]
    window.addstr(start_y + 1, start_x, ' '.join(f'{header:25}' if i < 2 else f'{header:12}' if i == 2 else f'{header:8}' if i == 3 else f'{header:20}' if i == 4 else f'{header:15}' if i == 5 else f'{header:10}' for i, header in enumerate(headers)), header_color)

    for i, conn in enumerate(connections[start_idx:start_idx + max_lines]):
        window.addstr(start_y + 2 + i, start_x, ' '.join(f'{str(field):25}' if j < 2 else f'{str(field):12}' if j == 2 else f'{str(field):8}' if j == 3 else f'{str(field):20}' if j == 4 else f'{str(field):15}' if j == 5 else f'{str(field):10}' for j, field in enumerate(conn)), text_color)

def draw_process_table(window, title, processes, start_y, start_x, width, start_idx, max_lines, selected_idx):
    title_color = curses.color_pair(2) | curses.A_BOLD
    header_color = curses.color_pair(4)
    text_color = curses.color_pair(1)
    selected_color = curses.color_pair(2) | curses.A_REVERSE

    window.addstr(start_y, start_x, title, title_color)
    headers = ["PID", "USER", "NI", "VIRT", "RES", "SHR", "S", "CPU%", "MEM%", "TIME+", "Command"]
    window.addstr(start_y + 1, start_x, ' '.join(f'{header:8}' if i == 0 else f'{header:15}' if i == 1 else f'{header:5}' if i == 2 else f'{header:8}' for i, header in enumerate(headers)), header_color)

    for i, proc in enumerate(processes[start_idx:start_idx + max_lines]):
        color = selected_color if i + start_idx == selected_idx else text_color
        window.addstr(start_y + 2 + i, start_x, ' '.join(f'{str(field):8}' if j == 0 else f'{str(field):15}' if j == 1 else f'{str(field):5}' if j == 2 else f'{str(field):8}' for j, field in enumerate(proc)), color)

def splash_screen(stdscr, selected=0):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLUE)
    curses.curs_set(0)
    max_y, max_x = stdscr.getmaxyx()

    stdscr.bkgd(curses.color_pair(1))
    stdscr.clear()
    stdscr.refresh()

    title = "NetScope 2.0"
    prompt = "Select an option:"
    options = ["1. Established Connections", "2. Listening Connections", "3. Both", "4. Running Processes", "5. Exit"]
    title_x = max_x // 2 - len(title) // 2
    options_y_start = max_y // 2 - len(options) // 2
    prompt_x = max_x // 2 - len(prompt) // 2
    prompt_y = options_y_start - 2

    stdscr.addstr(1, title_x, title, curses.color_pair(2) | curses.A_BOLD)
    stdscr.addstr(prompt_y, prompt_x, prompt, curses.color_pair(2))

    for idx, option in enumerate(options):
        option_x = max_x // 2 - len(option) // 2
        if idx == selected:
            stdscr.addstr(options_y_start + idx, option_x, option, curses.color_pair(2) | curses.A_BOLD)
        else:
            stdscr.addstr(options_y_start + idx, option_x, option, curses.color_pair(2))

    # Draw border with app name and author
    stdscr.border(0)
    stdscr.addstr(0, 2, "NetScope 2.0", curses.color_pair(2) | curses.A_BOLD)
    stdscr.addstr(1, 2, "Written by Yodabytz", curses.color_pair(2))

    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key in [curses.KEY_ENTER, ord('\n')]:
            return selected + 1
        elif key == curses.KEY_UP:
            selected = (selected - 1) % len(options)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(options)
        elif key in [ord('1'), ord('2'), ord('3'), ord('4'), ord('5')]:
            return int(chr(key))
        elif key == ord('q'):
            return 5  # To quit the program

        for idx, option in enumerate(options):
            option_x = max_x // 2 - len(option) // 2
            if idx == selected:
                stdscr.addstr(options_y_start + idx, option_x, option, curses.color_pair(2) | curses.A_BOLD)
            else:
                stdscr.addstr(options_y_start + idx, option_x, option, curses.color_pair(2))

        stdscr.refresh()

def main_screen(stdscr, selected_option):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLUE)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    est_start_idx = 0
    listen_start_idx = 0
    proc_start_idx = 0
    proc_selected_idx = 0
    active_section = "ESTABLISHED"
    stdscr.timeout(500)

    min_width = 100

    established_connections = []
    listening_connections = []
    processes = []

    def update_display():
        nonlocal established_connections, listening_connections, processes

        max_y, max_x = stdscr.getmaxyx()

        if max_x < min_width:
            stdscr.clear()
            stdscr.addstr(0, 0, f"Please resize your window to at least {min_width} columns.", curses.color_pair(2) | curses.A_BOLD)
            stdscr.refresh()
            return

        max_lines = max_y - 8

        buffer = curses.newpad(max_y, max_x)
        buffer.bkgd(curses.color_pair(1))
        buffer.erase()

        if selected_option in [1, 3]:
            established_connections = get_connections('ESTABLISHED')
        if selected_option in [2, 3]:
            listening_connections = get_connections('LISTEN')
        if selected_option == 4:
            processes = get_all_processes()

        io_data = {}
        for conn in established_connections + listening_connections:
            pid = conn[3].strip()
            if pid and pid.isdigit():
                pid = int(pid)
                try:
                    p = psutil.Process(pid)
                    io_counters = p.io_counters()
                    io_data[pid] = {'sent': io_counters.write_bytes, 'recv': io_counters.read_bytes}
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    io_data[pid] = {'sent': 0, 'recv': 0}

        buffer.erase()
        buffer.bkgd(curses.color_pair(1))
        buffer.border(0)

        buffer.addstr(0, 2, "NetScope 2.0", curses.color_pair(2) | curses.A_BOLD)
        buffer.addstr(1, 2, "Written by Yodabytz", curses.color_pair(2))

        if selected_option == 1:
            draw_table(buffer, "Established Connections", [
                conn + [format_size(io_data.get(int(conn[3].strip()), {}).get('sent', 0)), format_size(io_data.get(int(conn[3].strip()), {}).get('recv', 0))]
                for conn in established_connections
            ], 3, 1, max_x - 2, est_start_idx, max_lines, active_section == "ESTABLISHED")
        elif selected_option == 2:
            draw_table(buffer, "Listening Connections", [
                conn + [format_size(io_data.get(int(conn[3].strip()), {}).get('sent', 0)), format_size(io_data.get(int(conn[3].strip()), {}).get('recv', 0))]
                for conn in listening_connections
            ], 3, 1, max_x - 2, listen_start_idx, max_lines, active_section == "LISTEN")
        elif selected_option == 3:
            draw_table(buffer, "Established Connections", [
                conn + [format_size(io_data.get(int(conn[3].strip()), {}).get('sent', 0)), format_size(io_data.get(int(conn[3].strip()), {}).get('recv', 0))]
                for conn in established_connections
            ], 3, 1, max_x - 2, est_start_idx, max_lines // 2, active_section == "ESTABLISHED")
            draw_table(buffer, "Listening Connections", [
                conn + [format_size(io_data.get(int(conn[3].strip()), {}).get('sent', 0)), format_size(io_data.get(int(conn[3].strip()), {}).get('recv', 0))]
                for conn in listening_connections
            ], max_lines // 2 + 6, 1, max_x - 2, listen_start_idx, max_lines // 2, active_section == "LISTEN")
        elif selected_option == 4:
            draw_process_table(buffer, "Running Processes", processes, 3, 1, max_x - 2, proc_start_idx, max_lines, proc_selected_idx)
            buffer.addstr(max_y - 2, 2, "Press 'k' to kill the selected process", curses.color_pair(2) | curses.A_BOLD)

        buffer.refresh(0, 0, 0, 0, max_y - 1, max_x - 1)

    while True:
        try:
            if selected_option == 5:
                break

            update_display()
            stdscr.refresh()

            max_y, max_x = stdscr.getmaxyx()
            max_lines = max_y - 8

            key = stdscr.getch()
            if selected_option == 1:
                if key == curses.KEY_UP:
                    est_start_idx = max(est_start_idx - 1, 0)
                elif key == curses.KEY_DOWN:
                    est_start_idx = min(est_start_idx + 1, len(established_connections) - max_lines)
                elif key == ord('q'):
                    return 5  # To quit the program
                elif key in [curses.KEY_BACKSPACE, curses.KEY_LEFT, 127]:
                    return 0  # Navigate back to the main menu
            elif selected_option == 2:
                if key == curses.KEY_UP:
                    listen_start_idx = max(listen_start_idx - 1, 0)
                elif key == curses.KEY_DOWN:
                    listen_start_idx = min(listen_start_idx + 1, len(listening_connections) - max_lines)
                elif key == ord('q'):
                    return 5  # To quit the program
                elif key in [curses.KEY_BACKSPACE, curses.KEY_LEFT, 127]:
                    return 0  # Navigate back to the main menu
            elif selected_option == 4:
                if key == curses.KEY_UP:
                    proc_selected_idx = max(proc_selected_idx - 1, 0)
                    if proc_selected_idx < proc_start_idx:
                        proc_start_idx = proc_selected_idx
                elif key == curses.KEY_DOWN:
                    proc_selected_idx = min(proc_selected_idx + 1, len(processes) - 1)
                    if proc_selected_idx >= proc_start_idx + max_lines:
                        proc_start_idx = proc_selected_idx - max_lines + 1
                elif key == ord('k'):
                    try:
                        pid = int(processes[proc_selected_idx][0].strip())
                        psutil.Process(pid).terminate()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                elif key == ord('q'):
                    return 5  # To quit the program
                elif key in [curses.KEY_BACKSPACE, curses.KEY_LEFT, 127]:
                    return 0  # Navigate back to the main menu
            elif selected_option == 3:
                if active_section == "ESTABLISHED":
                    if key == curses.KEY_UP:
                        est_start_idx = max(est_start_idx - 1, 0)
                    elif key == curses.KEY_DOWN:
                        est_start_idx = min(est_start_idx + 1, len(established_connections) - max_lines // 2)
                    elif key == ord('q'):
                        return 5  # To quit the program
                    elif key in [curses.KEY_BACKSPACE, curses.KEY_LEFT, 127]:
                        return 0  # Navigate back to the main menu
                    elif key == ord('\t'):
                        active_section = "LISTEN"
                elif active_section == "LISTEN":
                    if key == curses.KEY_UP:
                        listen_start_idx = max(listen_start_idx - 1, 0)
                    elif key == curses.KEY_DOWN:
                        listen_start_idx = min(listen_start_idx + 1, len(listening_connections) - max_lines // 2)
                    elif key == ord('q'):
                        return 5  # To quit the program
                    elif key in [curses.KEY_BACKSPACE, curses.KEY_LEFT, 127]:
                        return 0  # Navigate back to the main menu
                    elif key == ord('\t'):
                        active_section = "ESTABLISHED"
            elif key in [curses.KEY_BACKSPACE, curses.KEY_LEFT, 127]:
                return 0  # Navigate back to the main menu
            elif key == ord('q'):
                return 5  # To quit the program
        except curses.error:
            pass
        except Exception as e:
            stdscr.addstr(0, 0, f"Error: {e}", curses.color_pair(2) | curses.A_BOLD)
            stdscr.refresh()
            time.sleep(1)

def main(stdscr):
    selected_option = 0
    while True:
        selected_option = splash_screen(stdscr, selected_option)
        if selected_option == 5:
            break
        selected_option = main_screen(stdscr, selected_option)
        if selected_option == 5:
            break

if __name__ == "__main__":
    os.environ.setdefault('ESCDELAY', '25')
    curses.wrapper(main)