import cv2
import numpy as np
import math
from typing import Dict, Any, Tuple


class CircularMenu:
    def __init__(self, menu_structure: Dict[str, str], radius: int = 200, center: Tuple[int, int] = None, circle_percentage: float = 1.0, arc_points: int = 25, portion_color: Tuple[int, int, int] = (0, 255, 0)):
        """
        Initialize the CircularMenu.
        :param menu_structure: The hierarchical structure of the menu as a dictionary.
        :param radius: Radius of the circular menu.
        :param center: Center of the circular menu.
        :param circle_percentage: The percentage of the circle to show (e.g., 0.5 for half-circle).
        """
        self.menu_structure = menu_structure
        self.radius = radius
        self.center = center
        self.circle_percentage = circle_percentage
        self.current_menu = "Main"
        self.selected_option = None
        self.angles = []
        self.arc_points = arc_points
        self.portion_color = portion_color
        self.menu_ready = False

    def set_center(self, center: Tuple[int, int]):
        """
        Set the center of the circular menu.
        :param center: Center coordinates.
        """
        self.center = center

    def get_selected_item(self, rotation: float):
        """
        Get the selected item based on the rotation angle.
        :param rotation: Rotation angle in degrees.
        :return: The selected item.
        """
        if not self.angles:
            return -1, None

        if self.current_menu not in self.menu_structure:
            return -1, None
        
        rotation *= -1

        options = list(self.menu_structure[self.current_menu].keys())

        for i in range(len(options)):
            angle = self.angles[i]
            if angle <= rotation and rotation < self.angles[i+1]:
                self.selected_option = i
                return i, list(self.menu_structure[self.current_menu].keys())[i]
        return -1, None     

    def instantiate_menu(self) -> bool:
        """
        Draw the circular menu on the given image.
        :param frame: The image to draw on.
        :return: Modified image with the menu drawn.
        """
        if self.center is None:
            return False
        
        if self.current_menu not in self.menu_structure:
            return False
        options = list(self.menu_structure[self.current_menu].keys())
        num_options = len(options)
        self.angles = []

        # Calculate the start and end angles for the visible arc
        max_angle = 2 * math.pi * self.circle_percentage  # Total angle for the visible arc
        start_angle = -math.pi + (-math.pi * (self.circle_percentage - 0.5))
        angle_step = max_angle / num_options if num_options > 0 else 0

        for i, option in enumerate(options):
            angle = start_angle + i * angle_step  # Calculate the angle for each option
            self.angles.append(angle)

        angle = start_angle + len(options) * angle_step
        self.angles.append(angle)
        self.angles = [np.degrees(angle) + 90 for angle in self.angles]

        self.menu_ready = True
        return True
    
    def is_menu_ready(self) -> bool:
        return self.menu_ready

    def select_option(self, option):
        """
        Select an option in the current menu.
        :param option: The index of the option to select.
        """
        if self.current_menu not in self.menu_structure:
            return
        if "data" in self.menu_structure[self.current_menu]:
            return
        if option in self.menu_structure[self.current_menu]:
            self.current_menu = option
            self.selected_option = None
        else:
            print(f"Option {option} not found in the current menu.")

    def go_back(self):
        """Goes one level back in the menu structure."""
        if self.current_menu == "Main":
            return
        for menu, options in self.menu_structure.items():
            if self.current_menu in options:
                self.current_menu = menu
                self.selected_option = self.current_menu
                break

    # def navigate(self, direction):
    #     """
    #     Handle menu navigation.
    #     :param direction: Navigation direction ('next', 'prev', 'select', 'back').
    #     """
    #     options = list(self.menu_structure[self.current_menu].keys())
    #     if not options:
    #         return

    #     current_index = options.index(self.selected_option) if self.selected_option else -1
    #     if direction == "next":
    #         self.selected_option = options[(current_index + 1) % len(options)]
    #     elif direction == "prev":
    #         self.selected_option = options[(current_index - 1) % len(options)]
    #     elif direction == "select":
    #         if self.selected_option in self.menu_structure[self.current_menu]:
    #             self.current_menu = self.selected_option
    #             self.selected_option = None
    #     elif direction == "back":
    #         self.current_menu = "Main"
    #         self.selected_option = None


if __name__ == "__main__":

    # Define menu structure
    menu_structure = {
        "Main": {
            "Pistols": {},
            "Heavy": {},
            "SMGs": {},
            "Rifles": {},
            "Gear": {},
            "Grenades": {},
        },
        "Pistols": {
            "Glock": {},
            "Desert Eagle": {},
        },
        "Rifles": {
            "AK-47": {},
            "M4A1": {},
        },
    }

    # Initialize the menu with 50% of the circle shown
    menu = CircularMenu(menu_structure, circle_percentage=0.8)

    # Create a display window
    cv2.namedWindow("Menu")

    while True:
        # Create a blank image
        img = np.zeros((600, 600, 3), dtype=np.uint8)

        # Draw the menu
        menu.draw_menu(img)

        # Display the image
        cv2.imshow("Menu", img)

        # Handle key input
        key = cv2.waitKey(100)
        if key == ord("q"):
            break
        elif key == ord("d"):  # Navigate to next option
            menu.navigate("next")
        elif key == ord("a"):  # Navigate to previous option
            menu.navigate("prev")
        elif key == ord("s"):  # Select the current option
            menu.navigate("select")
        elif key == ord("b"):  # Go back to the previous menu
            menu.navigate("back")

    cv2.destroyAllWindows()
