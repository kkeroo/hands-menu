import cv2
import numpy as np
from HandManager import HandManager
from HandTrackerBpfEdge import HandTrackerBpf
from menu import CircularMenu
import base64
from flask import Flask
from flask_socketio import SocketIO
import eventlet

eventlet.monkey_patch()  # For async support

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

class State:
    def __init__(self):
        self.depth_threshold = 30
        self.depth_threshold_exceed_counter = 0
        self.depth_processing_counter = 0  # for evidence if the person is not in the frame
        self.consecutive_exceed_threshold = 5
        
        self.person_infront = False
        self.selected_item = None
        self.selected_item_index = None
        self.image_url = None

def find_cog(hand):
    indexes = [0, 5, 9, 13, 17]
    x = 0
    y = 0
    for i in indexes:
        x += hand.landmarks[i][0]
        y += hand.landmarks[i][1]

    x = int(x/len(indexes))
    y = int(y/len(indexes))
    return x, y

edge=True
pd_model=None
no_lm=False
lm_model=None
use_world_landmarks=False
solo=True
xyz=False
gesture=True
crop=False
internal_fps=None
resolution='full'
internal_frame_height=None
body_pre_focusing='higher'
all_hands=False
single_hand_tolerance_thresh=10
dont_force_same_image=False
lm_nb_threads=2
trace=0

def flatten_dict(d: dict, parent_key='Main'):
    global menu_structure
    sub_dict = {}
    if len(d.keys()) == 0:
        return
    for k, v in d.items():
        sub_dict[k] = {}
        if k == "data":
            sub_dict[k] = v
        if isinstance(v, dict) and v:
            flatten_dict(d[k], k)

    menu_structure[parent_key] = sub_dict

# Initialize the menu with 40% of the circle shown
# menu = CircularMenu(menu_structure, circle_percentage=0.4, radius=200)
# menu.current_menu = "Main"
menu = None

tracker = HandTrackerBpf(
        use_lm=not no_lm,
        use_world_landmarks=use_world_landmarks,
        use_gesture=gesture,
        xyz=xyz,
        solo=solo,
        crop=crop,
        resolution=resolution,
        body_pre_focusing=body_pre_focusing,
        hands_up_only=not all_hands,
        single_hand_tolerance_thresh=single_hand_tolerance_thresh,
        lm_nb_threads=lm_nb_threads,
        stats=True,
        trace=trace,
        )

handManager = HandManager(
    horizontal_span=200,
    vertical_span=100,
    initial_sign_counter_threshold=5,
    confirm_sign_counter_threshold=5,
    move_sign_counter_threshold=10,
    back_sign_counter_threshold=10
)

STATE = State()

@socketio.on('upload_menu_structure')
def handle_menu_structure(json_data):
    global structure, menu_structure, menu
    try:
        # Update the structure with new JSON data
        structure = json_data
        
        # Reset and rebuild menu structure
        menu_structure = {}
        flatten_dict(structure, 'Main')

        print(menu_structure)
        
        # Reinitialize the menu with new structure
        menu = CircularMenu(menu_structure, circle_percentage=0.4, radius=200)
        menu.current_menu = "Main"
        
        print("Menu structure updated successfully")
    except Exception as e:
        print(f"Error updating menu structure: {str(e)}")


def encode_frame(frame):
    """Encode OpenCV frame as Base64 JPEG."""
    frame = cv2.resize(frame, (512, 288))
    _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
    return base64.b64encode(buffer).decode("utf-8")

def main():
    while True:
        video_frame, disparity_frame = tracker.next_depth()
        if video_frame is None:
            continue

        # Encode the frame
        encoded_frame = encode_frame(video_frame)
        socketio.emit("frame", {"image": encoded_frame})  # Send to WebSocket
        eventlet.sleep(0.03)  # Adjust for real-time speed

        if menu is None:
            continue

        y_offset = 100
        x_offset = 70
        y_center = int(disparity_frame.shape[0]/2)
        x_center = int(disparity_frame.shape[1]/2)

        roi = disparity_frame[y_center-y_offset:y_center+y_offset, x_center-x_offset:x_center+x_offset]
        mean_depth = np.mean(roi, axis=None)

        STATE.depth_processing_counter += 1
        if mean_depth >= STATE.depth_threshold:
            STATE.depth_threshold_exceed_counter += 1
        else:
            STATE.depth_threshold_exceed_counter = 0

        if STATE.depth_threshold_exceed_counter > STATE.consecutive_exceed_threshold:
            STATE.person_infront = True
        
        elif STATE.depth_processing_counter > STATE.consecutive_exceed_threshold:
            STATE.depth_threshold_exceed_counter = 0
            STATE.depth_processing_counter = 0
            STATE.person_infront = False


        # Run hand tracker on next frame
        # 'bag' contains some information related to the frame 
        # and not related to a particular hand like body keypoints in Body Pre Focusing mode
        # Currently 'bag' contains meaningful information only when Body Pre Focusing is used
        frame, hands, bag = tracker.next_frame()

        if STATE.person_infront and len(hands) > 0:
            # print("Person in front and hand detected")
            hand = hands[0]
            gesture = hand.gesture

            # we dont have origin point yet, we need to initialize it
            if not handManager.origin_point_present:
                if gesture == 'PEACE':
                    handManager.increase_initial_sign_counter()
                    
                    if handManager.ready_to_add_origin_point():
                        origin_point = hand.landmarks[0]
                        handManager.add_origin_point(origin_point)
                        print('Origin point added')
                        socketio.emit("origin_point", {
                            "action": "started",
                        })
                        print(handManager.origin_point)
                        center = find_cog(hand)
                        # take mirroring into account
                        center = (frame.shape[1] - center[0], center[1])

                        menu.set_center(center)
                        menu.current_menu = "Main"
                        menu.instantiate_menu()
                else:
                    handManager.initial_sign_counter = 0

            else:
                if gesture == 'FIVE' or gesture == 'FOUR':
                    if not menu.is_menu_ready():
                        continue
                    handManager.increase_move_sign_counter()

                    if handManager.ready_to_make_move():
                        # print(f"Hand rotation in radians: {hand.rotation}, in degrees: {np.degrees(hand.rotation)}")
                        center = find_cog(hand)
                        # take mirroring into account
                        center = (frame.shape[1] - center[0], center[1])
                        print({"x": float(center[0]/frame.shape[1]), "y": float(center[1]/frame.shape[0])})
                        menu.set_center(center)
                        rotation = np.degrees(hand.rotation)
                        STATE.selected_item_index, STATE.selected_item = menu.get_selected_item(rotation)
                        print(f"Selected item: {STATE.selected_item} with index {STATE.selected_item_index}")
                        socketio.emit("hand_center", {
                            "x": float(center[0]/frame.shape[1]),
                            "y": float(center[1]/frame.shape[0]),
                        })
                else:
                    handManager.move_sign_counter = 0
                
                if gesture == 'ONE' or gesture == 'TWO':
                    if not menu.is_menu_ready():
                        continue
                    handManager.increase_confirm_sign_counter()

                    if handManager.ready_to_confirm():                        
                        menu.select_option(STATE.selected_item)
                        STATE.selected_item = None
                        STATE.selected_item_index = None
                else:
                    handManager.confirm_sign_counter = 0
                
                if gesture == "FIST":
                    # go one level back
                    if not menu.is_menu_ready():
                        continue
                    handManager.increase_back_sign_counter()

                    if handManager.ready_to_go_back():
                        STATE.image_url = None
                        menu.go_back()
                        STATE.selected_item = None
                        STATE.selected_item_index = None
                        handManager.back_sign_counter = 0
                else:
                    handManager.back_sign_counter = 0   

        if menu and menu.center:
            if "data" in menu.menu_structure[menu.current_menu]:
                # Its a leaf node, so we need to display the image
                print(f"Leaf node: {menu.current_menu}")
                image_url = menu.menu_structure[menu.current_menu]["data"]
                print(image_url)
                STATE.image_url = image_url
            socketio.emit("menu_update", {
                "center": [menu.center[0]/frame.shape[1], menu.center[1]/frame.shape[0]],  # Normalize coordinates
                "radius": menu.radius,
                "options": list(menu.menu_structure[menu.current_menu].keys()) if not STATE.image_url else [],
                "selectedOption": STATE.selected_item,
                "angles": menu.angles,
                "circlePercentage": menu.circle_percentage,
                "image_url": STATE.image_url
            })

# Run frame generation in background
eventlet.spawn(main)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5432)