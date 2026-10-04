import numpy as np

class Blade:
    # initializes "private" instance variables for the 11 parameters
    radius = None
    axial_chord = None
    tangential_chord = None
    unguided_turning = None
    inlet_blade_angle = None
    inlet_wedge_angle = None
    leading_edge_radius = None
    exit_blade_angle = None
    trailing_edge_radius = None
    number_of_blades = None
    throat = None

    def get_point_1(self):
        beta_1 = self.exit_blade_angle - (0.5 * self.unguided_turning)
        # convert degree to radians for trig functions to work
        beta_1_rad = np.radians(beta_1)

        x1 = self.axial_chord - self.trailing_edge_radius * (1 + np.sin(beta_1_rad))
        y1 = self.trailing_edge_radius * (np.cos(beta_1_rad))
        m1 = np.tan(beta_1_rad)

        return x1, y1, m1

    def get_point_2(self):
        beta_2 = self.exit_blade_angle - (0.5 * self.unguided_turning) + self.unguided_turning
        # convert degree to radians for trig functions to work
        beta_2_rad = np.radians(beta_2)

        x2 = self.axial_chord - self.trailing_edge_radius + (self.throat + self.trailing_edge_radius) * np.sin(beta_2_rad)
        y2 = (2 * np.pi * self.radius / self.number_of_blades) - (self.throat + self.trailing_edge_radius) * np.cos(beta_2_rad)
        m2 = np.tan(beta_2_rad)

        return x2, y2, m2

    def get_point_3(self):
        beta_3 = self.inlet_blade_angle + 0.5 * self.inlet_wedge_angle
        # convert degree to radians for trig functions to work
        beta_3_rad = np.radians(beta_3)

        x3 = self.leading_edge_radius * (1 - np.sin(beta_3_rad))
        y3 = self.tangential_chord + self.leading_edge_radius * np.cos(beta_3_rad)
        m3 = np.tan(beta_3_rad)

        return x3, y3, m3

    def get_point_4(self):
        beta_4 = self.inlet_blade_angle - (0.5 * self.inlet_wedge_angle)
        # convert degree to radians for trig functions to work
        beta_4_rad = np.radians(beta_4)

        x4 = self.leading_edge_radius * (1 + np.sin(beta_4_rad))
        y4 = self.tangential_chord - (self.leading_edge_radius * np.cos(beta_4_rad))
        m4 = np.tan(beta_4_rad)

        return x4, y4, m4

    def get_point_5(self):
        beta_5 = self.exit_blade_angle + (0.5 * self.unguided_turning)
        # convert degree to radians for trig functions to work
        beta_5_rad = np.radians(beta_5)

        x5 = self.axial_chord - self.trailing_edge_radius * (1 - np.sin(beta_5_rad))
        y5 = -1 * self.trailing_edge_radius * np.cos(beta_5_rad)
        m5 = np.tan(beta_5_rad)

        return x5, y5, m5