class HandManager:
    def __init__(
            self,
            horizontal_span,
            vertical_span,
            initial_sign_counter_threshold,
            confirm_sign_counter_threshold,
            move_sign_counter_threshold,
            back_sign_counter_threshold
        ) -> None:
        self.origin_point = None
        self.origin_point_present = False
        self.horizontal_span = horizontal_span
        self.vertical_span = vertical_span
        self.initial_sign_counter_threshold = initial_sign_counter_threshold
        self.initial_sign_counter = 0
        self.confirm_sign_counter = 0
        self.confirm_sign_counter_threshold = confirm_sign_counter_threshold
        self.move_sign_counter = 0
        self.move_sign_counter_threshold = move_sign_counter_threshold
        self.back_sign_counter = 0
        self.back_sign_counter_threshold = back_sign_counter_threshold
        self.x = None
        self.y = None

    def increase_initial_sign_counter(self):
        self.initial_sign_counter += 1
    
    def get_initial_sign_counter(self):
        return self.initial_sign_counter
    
    def ready_to_add_origin_point(self):
        return self.initial_sign_counter >= self.initial_sign_counter_threshold

    def increase_confirm_sign_counter(self):
        self.confirm_sign_counter += 1
    
    def get_confirm_sign_counter(self):
        return self.confirm_sign_counter
    
    def ready_to_confirm(self):
        return self.confirm_sign_counter >= self.confirm_sign_counter_threshold

    def increase_move_sign_counter(self):
        self.move_sign_counter += 1

    def get_move_sign_counter(self):
        return self.move_sign_counter

    def ready_to_make_move(self):
        return self.move_sign_counter >= self.move_sign_counter_threshold

    def increase_back_sign_counter(self):
        self.back_sign_counter += 1
    
    def get_back_sign_counter(self):
        return self.back_sign_counter
    
    def ready_to_go_back(self):
        return self.back_sign_counter >= self.back_sign_counter_threshold

    def add_origin_point(self, origin_point):
        self.origin_point = origin_point
        self.origin_point_present = True

    def remove_origin_point(self):
        self.origin_point = None
        self.origin_point_present = False
        self.initial_sign_counter = 0

    # def next_move(self, position):
    #     # get the x-coordinate within the boundaries
    #     x = max(position[0], self.origin_point[0] - self.horizontal_span)
    #     x = min(x, self.origin_point[0] + self.horizontal_span)

    #     # get the y-coordinate within the boundaries
    #     y = max(position[1], self.origin_point[1] - self.vertical_span)
    #     y = min(y, self.origin_point[1] + self.vertical_span)

    #     x_transformed = x - (self.origin_point[0] - self.horizontal_span)
    #     y_transformed = y - (self.origin_point[1] - self.vertical_span)

    #     x_percentage = x_transformed/(self.horizontal_span*2)
    #     y_percentage = y_transformed/(self.vertical_span*2)

    #     self.x = x_percentage
    #     self.y = y_percentage

    #     # cell_width = self.horizontal_span*2//self.grid_shape[0]
    #     # cell_idx = x_transformed//cell_width

    #     self.move_sign_counter = 0

    #     return x, y
    
    # def confirm_move(self):
    #     return self.x, self.y
    