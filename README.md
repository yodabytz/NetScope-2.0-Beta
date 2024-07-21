# NetScope 2.0

NetScope is a powerful network and process monitoring tool inspired by `htop`. It allows you to view established connections, listening connections, running processes, and interact with the processes, such as killing them. The tool is designed to be user-friendly and efficient, providing detailed information about your system's network and process activity.

## Features

- **Established Connections**: View all established network connections.
- **Listening Connections**: View all listening network connections.
- **Both**: View both established and listening connections side-by-side.
- **Running Processes**: View and interact with running processes. Highlight and kill processes using simple keyboard controls.
- **Smooth Scrolling**: Efficient and smooth scrolling through lists of connections and processes.
- **Interactive Commands**: Navigate and interact with the application using intuitive keyboard commands.

## Installation

### Requirements

- Python 3.x
- `psutil` library
- `curses` library

### Installation Steps

1. **Clone the Repository**:
    ```sh
    git clone https://github.com/yodabytz/netscope.git
    cd netscope
    ```

2. **Install Dependencies**:
    ```sh
    pip install psutil
    ```

3. **Move the Script to /usr/bin**:
    ```sh
    sudo cp netscope.py /usr/bin/netscope
    sudo chmod +x /usr/bin/netscope
    ```

## Usage

Run the tool by typing:
```sh
netscope

## Controls
Menu Navigation:

Up/Down Arrows or k/j: Navigate through the menu options.
Enter or Return: Select a menu option.
q: Quit the application from any screen.
Established and Listening Connections Screens:

Up/Down Arrows or k/j: Scroll through the list of connections.
Left Arrow or Backspace: Return to the main menu.
q: Quit the application.
Both Connections Screen:

Tab: Switch between Established and Listening sections.
Up/Down Arrows or k/j: Scroll through the connections in the active section.
Left Arrow or Backspace: Return to the main menu.
q: Quit the application.
Running Processes Screen:

Up/Down Arrows or k/j: Scroll through the list of processes.
k: Kill the selected process.
Left Arrow or Backspace: Return to the main menu.
q: Quit the application.

##License
This project is licensed under the MIT License. See the LICENSE file for details.

## Author
NetScope 2.0 is developed by Yodabytz. Contributions and feedback are welcome!