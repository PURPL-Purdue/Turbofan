import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm
import numpy as np

def tree(trunk, branches, root_x, root_y, scale, style, axis):
    for i in range(len(trunk)):
        axis.quiver(root_x, root_y + trunk(i), branches(i), 0, scale, style)

def velocity_triangle(C, W, U, alpha, beta, z, z_offset):
    plt.quiver(z_offset, 0, C*np.cos(alpha), C*np.sin(alpha), angles='xy', scale_units='xy', scale=z*1.1, color='red')
    plt.quiver(z_offset, 0, W*np.cos(beta),  W*np.sin(beta), angles='xy', scale_units='xy', scale=z*1.1, color='cyan')
    plt.quiver(z_offset+(1/1.1), W*np.sin(beta)/(z*1.1), 0, U, angles='xy', scale_units='xy', scale=z*1.1, color='teal')

def annulus_base(num_stages, num_stations, chord_m, r_mean_1, FF, axes):
    x_axis = list(range(1,num_stages+2));
    x_axis = [(i-1)*2*chord_m for i in x_axis]

    x_axis_long = list(range(1,FF.num_stations+1))
    x_axis_long = [(i-1)*chord_m for i in x_axis_long]

    for axis in axes:
        axis.hlines(r_mean_1, 0, (num_stations-1)*chord_m)
        # axis.plot(x_axis, r_hub_vec, '.-r', x_axis, r_tip_vec, '.-r')
        axis.plot(x_axis_long, FF.r_hub_vec_full, '.-k', x_axis_long, FF.r_tip_vec_full, '.-k')
    return([x_axis, x_axis_long])

def span(radii, data, num_streamlines, num_stations, x_axis_long, axis):
    data_min = min([min(span) for span in data]) 
    data_max = max([max(span) for span in data])

    norm = colors.Normalize(vmin=data_min, vmax=data_max)
    map = cm.ScalarMappable(norm=norm, cmap='turbo')

    for i in range(num_stations):
        axis.scatter([x_axis_long[i] for _ in range(num_streamlines)], radii[i], s=None, c=data[i], cmap='turbo', norm=norm)
    cbar = plt.colorbar(map, ax=axis)
