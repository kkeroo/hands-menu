# Control a circular menu with your hands

A gesture-controlled interactive menu system using hand tracking and depth sensing with the Luxonis DepthAI camera. This project allows users to navigate through a circular menu interface using simple hand gestures, with real-time feedback through a web interface.

## Features
- Gesture-controlled interface: Navigate and select menu items using hand gestures
- Depth sensing: Detects user presence using depth data
- Circular menu UI: Intuitive radial menu that follows hand position
- Hierarchical menu structure: Navigate through nested menu categories
- Configurable menu system: Define your own menu structure via JSON
- Real-time video streaming: Web interface shows camera feed with menu overlay
- Cross-platform: Works on any device with a web browser

## Requirements
- OAK-D camera
- Python 3.10+
- Web browser

## Installation

1. Clone the repository
```bash
git clone https://github.com/kkeroo/hands-menu.git
cd hands-menu
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Connect the OAK-D camera and run the tracker

## Usage

1. Start the tracker
```bash
cd tracker
python main.py
```

2. Open the index.html file in your web browser

3. Upload the menu structure JSON file

4. Navigate through the menu using hand gestures

## Menu Configuration
The menu structure is defined in a JSON file with a hierarchical format. Example:

```json
{
    "1.letnik": {
        "RI UNI 1.letnik": {"data": "photos/ri-uni-1.png"},
        "RI-VS 1.letnik": { "data": "photos/ri-vs-1.png"},
        "MM 1.letnik": { "data": "photos/mm-uni-1.png"}
    },
    "2.letnik": {
        "RI UNI 2.letnik": {"data": "photos/ri-uni-2.png"},
        "RI-VS 2.letnik": { "data": "photos/ri-vs-2.png"},
        "MM 2.letnik": { "data": "photos/mm-uni-2.png"}
    }
}
```
- Each top-level key represents a menu category
- Nested objects represent subcategories
- Leaf nodes with a "data" property specify content (like images) to display when selected

## Hand Gestures
The menu system recognizes the following hand gestures:
- **PEACE (✌️)** to start the menu system
- **FIVE (🖐️)** to navigate through options
- **ONE (☝️)** to select highlighted option
- **FIST (✊)** to return to previous menu

## System Architecture
- **Backend:** Python Flask server with DepthAI integration
- **Frontend:** HTML/JS web interface
- **Communication:** WebSockets (SocketIO)

