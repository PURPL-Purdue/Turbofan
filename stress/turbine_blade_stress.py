# slices format: [[slice1, radius1], [slice2, radius2]]
# important: radius from axis of rotation, not from hub edge!!!
# slice format: [(x1, y1), (x2, y2)]
import numpy as np
import matplotlib.pyplot as plt


# finds area of shape from a set of points using shoelace theorem
def contourArea(pts):
    x, y = zip(*pts)
    return 0.5 * np.abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


# returns total centrifugal stress at root for blade geometry that varies with height (slices)
# also takes rpm of blade, density of material
def stress_centrifugal(slices, rpm, rho):
    # need at least tip and base geometry to run stress analysis
    if len(slices) < 2:
        raise ValueError(
            "Aww shucks i need at least 2 bro"
        )
    radii = []
    areas = []
    # separate into radii and areas for each slice
    for slice in slices:
        areas.append(contourArea(slice[0]))
        radii.append(slice[1])
    w = rpm * 2 * np.pi / 60  # rad/s
    a_h = contourArea(slices[0][0])  # area of hub
    integrand = [A * r for A, r in zip(areas, radii)]  # according to farokhi 10.101
    return 1 / a_h * rho * w ** 2 * np.trapezoid(integrand, radii) * 1e-6  # also farokhi 10.101, in MPa


# assumes no tangential bending (ignores swirl, I think)
# assumes constant blade geometry
# error analysis might be useful here - incorporate more accurate airflow pressure distribution
# inputs geometry slice, mass flow rate of air, air velo in, air velo out, number of blades, length of blade
def uniform_stress_gas_bending(slice, mfr, v_in, v_out, n_b, l):
    i_xx, c = blade_slice_properties(slice)
    f = mfr * (v_in - v_out) / n_b  # gas force per blade
    m = f * l / 2  # root moment (uniform load because of constant cross-section)
    return m * c / i_xx * 1e-6  # return bending stress in MPa


# find second moment, distance to outer fibre
def blade_slice_properties(slice):
    pts = np.asarray(slice, dtype=float)
    x, y = pts[:, 0], pts[:, 1]  # separate into pts array
    area = contourArea(slice)  # get area of slice
    x0, y0 = x[:-1], y[:-1]  # first pt
    x1, y1, = x[1:], y[1:]  # last pt
    cross = x0 * y1 - x1 * y0  # cross product
    # calculate centroids
    cx = (1.0 / (6.0 * area)) * np.sum((x0 + x1) * cross)
    cy = (1.0 / (6.0 * area)) * np.sum((y0 + y1) * cross)
    # Second moment about origin of input coords
    i_xx_o = (1.0 / 12.0) * np.sum((y0 ** 2 + y0 * y1 + y1 ** 2) * cross)
    # shift moment to centroid (parallel axis theorem)
    i_xx = i_xx_o - area * cy ** 2
    c = np.max(np.abs(y - cy))  # distance to outer fiber
    return i_xx, c


# lil helper that gets von mises stress, commonly known equation
def von_mises_stress(s1, s2, s3=0.0):
    # return np.sqrt(s1**2-s1*s2+s2**2) 3d for when we calc tangential with swirl (maybe)
    return np.sqrt(((s1 - s2) ** 2 + (s2 - s3) ** 2 + (s3 - s1) ** 2) / 2)


# useful plot function
# stress vs length of constant blade area
def plot_von_mises_stress(slice, rpm, rho, stress_yield, r_b, mfr, v_in, v_out, n_b, start, end, num):
    lengths = []
    stresses = []
    increment = round((end - start) / num, 3)  # distance between each measured point
    current = start
    while current < end:
        lengths.append(current)  # add current blade length to x-axis
        centrifugal = stress_centrifugal([[slice, r_b], [slice, r_b + current]], rpm, rho)
        gas_bending = uniform_stress_gas_bending(slice, mfr, v_in, v_out, n_b, current)
        stresses.append(von_mises_stress(centrifugal, gas_bending))  # add current total stress to y-axis
        current += increment
    # display, duh
    plt.plot(lengths, stresses)
    plt.axhline(y=stress_yield)
    plt.xlabel("length of blade (M)")
    plt.ylabel("Stress (mPa)")
    plt.title("Stress vs length")
    plt.show()


def plot_points(slice):
    x, y = slice[:, 0], slice[:, 1]
    plt.figure(figsize=(10, 4))
    plt.plot(x, y, 'b-', linewidth=1.5)
    plt.axis('equal')  # keep aspect ratio so it looks like a real airfoil shape
    plt.xlabel('x/c')
    plt.ylabel('y/c')
    plt.title('Airfoil Profile')
    plt.grid(True, alpha=0.3)
    plt.show()


if __name__ == "__main__":
    # load points from airfoil into np array
    airfoil_points = np.loadtxt('ExampleBlade_points.txt')

    rpm = 80000
    density = 8190  # inconel, kg/m^3
    yield_stress = 800  # inconel, MPa
    radius_hub = 0.05  # hub radius, m
    mfr = 100  # mass flow rate, kg/s
    v_in = 100  # velo air in, m/s
    v_out = 500  # velo air out, m/s
    n_b = 27  # number of blades
    start = 0.005  # start blade length, m
    end = 0.05  # end blade length, m
    num = 50  # num of test points
    # plot_points(airfoil_points)
    plot_von_mises_stress(airfoil_points, rpm, density, yield_stress, radius_hub, mfr, v_in, v_out, n_b, start, end,
                          num)
