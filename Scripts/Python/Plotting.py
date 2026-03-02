import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm
import numpy as np

def plot(TF):
    
    # T0 = [a.T0 for a in vars(TF.cycle.OUT.T0P0).values()]
    # P0 = [a.P0 for a in vars(TF.cycle.OUT.T0P0).values()]
    # cycle(T0, P0)

    turbine_velocity_triangles(TF.turbine.LP.OUT.multistage_velocity_triangles)

    # compressor_annulus_spans(
    #     TF.compressor.LP.OUT.num_stages,
    #     TF.compressor.LP.OUT.num_stages*2+1,
    #     TF.compressor.LP.OUT.chord_m,
    #     TF.compressor.LP.OUT.r_mean_1,
    #     TF.compressor.LP.OUT.FF
    # )

    # compressor_info(
    #     TF.compressor.LP.OUT.num_stages,
    #     TF.compressor.LP.OUT.num_stages*2+1,
    #     TF.compressor.LP.OUT.chord_m,
    #     TF.compressor.LP.OUT.r_mean_1,
    #     TF.compressor.LP.OUT.FF,
    #     TF.compressor.LP.OUT.Pr_stages,
    #     TF.compressor.LP.OUT.T0_stages,
    #     TF.compressor.LP.OUT.P0_stages,
    #     TF.compressor.LP.OUT.RVT
    # )

    plt.show(block=False)
    input("Press enter to close all plots")
    plt.close('all')

def cycle(T0, P0):
    # Setting up the plot
    fig, axLeft = plt.subplots(num="Cycle P0 and T0 Chart")
    plt.title("Station Total Temperatures and Pressures")
    plt.subplots_adjust(left=0.15, bottom=0.1, right=0.85, top=0.9, wspace=0, hspace=0)

    # Creating x axis
    stations = [0, 1.5, 2, 2.5, 3, 4, 4.5, 5, 6, 7, 8]

    # Plotting the left axis
    axLeft.plot(stations, T0, '-ob', label="Temperatures")
    axLeft.set_ylabel("Total Temperatures")
    axLeft.set_xlabel("Station Number")
    plt.legend(loc="upper left")

    # Plotting the right axis
    axRight = axLeft.twinx()
    axRight.plot(stations, P0, '-or', label="Pressures")
    axRight.set_ylabel("Total Pressure")
    plt.legend(loc="upper right")

def compressor_annulus_spans(num_stages, num_stations, chord_m, r_mean_1, FF):
    fig, axes = plt.subplots(3,1, num="Compressor Annulus")
    axes[0].set_title("Degree of Reaction")
    axes[0].set_ylabel("r (m)")
    axes[0].set_ylabel("z (m)")
    
    axes[1].set_title("C_theta")
    axes[1].set_ylabel("r (m)")
    axes[1].set_ylabel("z (m)")

    axes[2].set_title("C_z")
    axes[2].set_ylabel("r (m)")
    axes[2].set_ylabel("z (m)")

    x_axis, x_axis_long = annulus_base(num_stages, num_stations, chord_m, r_mean_1, FF, axes)
    
    data_min = min([min(span) for span in FF.degR_spans]) 
    data_max = max([max(span) for span in FF.degR_spans])
    norm = colors.Normalize(vmin=data_min, vmax=data_max)
    map = cm.ScalarMappable(norm=norm, cmap='turbo')

    for i in range(num_stages):
        axes[0].scatter([x_axis[i] for _ in range(FF.num_streamlines)], FF.r_spans[i*2], s=None, c=FF.degR_spans[i], cmap='turbo', norm=norm)
    cbar = plt.colorbar(map, ax=axes[0])

    span(FF.r_spans, FF.Ctheta_spans, FF.num_streamlines, num_stations, x_axis_long, axes[1])
    span(FF.r_spans, FF.z_spans,      FF.num_streamlines, num_stations, x_axis_long, axes[2])

    axes[0].axis('equal')
    axes[1].axis('equal')
    axes[2].axis('equal')

def compressor_info(num_stages, num_stations, chord_m, r_mean_1, FF, Pr_stages, T0_stages, P0_stages, RVT):
    plt.figure(num="Compressor Pressure Ratios per Stage")
    x_axis = list(range(1,num_stages+1))
    plt.title("Pressure Ratios per Stage")
    plt.xlabel("Stages")
    plt.xticks([_ for _ in range(1, num_stages+2)])
    plt.plot(x_axis, Pr_stages)

    fig, axLeft = plt.subplots(num="Compressor Total Temperatures and Pressures per Station")
    x_axis = list(range(1,num_stages+2));
    axLeft.set_title("Total Temperatures and Pressures per Station")
    axLeft.set_xlabel("Stations")
    axLeft.set_xticks([_ for _ in range(1, num_stations+1)])
    P0_plot, = axLeft.plot(x_axis, P0_stages, color="teal", label="Pressure (P0)")
    axLeft.set_ylabel("P0 (Pa)")

    axRight = axLeft.twinx()
    T0_plot, = axRight.plot(x_axis, T0_stages, color="red", label="Temperature(T0)")
    axRight.set_ylabel("T0 (K)")

    plots = [P0_plot, T0_plot]
    labels = [_.get_label() for _ in plots]

    axLeft.legend(plots, labels, loc='upper left')

    plt.figure(num="Compressor Velocity Triangle")
    x_axis = [(i-1)*2*chord_m for i in x_axis]
    x_axis_long = list(range(1,FF.num_stations+1))
    x_axis_long = [(i-1)*chord_m for i in x_axis_long]
    
    plt.title("Velocity Triangle (Repeating)")
    plt.xlabel("Station Number")
    velocity_triangle(
        RVT.C_1m,
        RVT.W_1m,
        RVT.U_1m,
        RVT.alpha_1m,
        RVT.beta_1m,
        RVT.z_1m,
        1
    )
    plt.xlim([0.5,2.5])
    plt.ylim([-1,1])
    plt.xticks([1,2])
    plt.axis('equal')

    plt.figure(num="Compressor Annulus Geometry")
    plt.title("Compressor Annulus Geometry")
    plt.xlabel("Axial Length (m)")
    plt.ylabel("Radial Direction (m)")
    # Upper Annulus
    plt.hlines(r_mean_1, 0, (num_stations-1)*chord_m)
    # plt.plot(x_axis, r_hub_vec, '.-r', x_axis, r_tip_vec, '.-r')
    plt.plot(x_axis_long, FF.r_hub_vec_full, '.-k', x_axis_long, FF.r_tip_vec_full, '.-k')
    # plt.plot(x_axis, r_hub_vec, '.-r', x_axis, r_tip_vec, '.-r')
    plt.plot(x_axis_long, FF.r_hub_vec_full, '.-k', x_axis_long, FF.r_tip_vec_full, '.-k')
    # Mirrored Lower Annulus
    plt.hlines(-r_mean_1, 0, (num_stations-1)*chord_m)
    # plt.plot(x_axis, [-_ for _ in r_hub_vec], '.-r', x_axis, [-_ for _ in r_tip_vec], '.-r')
    plt.plot(x_axis_long, [-_ for _ in FF.r_hub_vec_full], '.-k', x_axis_long, [-_ for _ in FF.r_tip_vec_full], '.-k')
    # plt.plot(x_axis, [-_ for _ in r_hub_vec], '.-r', x_axis, [-_ for _ in r_tip_vec], '.-r')
    plt.plot(x_axis_long, [-_ for _ in FF.r_hub_vec_full], '.-k', x_axis_long, [-_ for _ in FF.r_tip_vec_full], '.-k')
    plt.axis('equal')

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

def turbine_velocity_triangles(triangles):
    plt.figure("Turbine Velocity Triangles")
    plt.title("Turbine Velocity Triangles")
    plt.xlabel("Station Numbers")
    plt.ylim([-2,2])
    plt.xticks([_ for _ in range(1, len(triangles)*2+3)])
    plt.quiver(1, 0, triangles[0].C_1m*np.cos(triangles[0].alpha_1m), triangles[0].C_1m*np.sin(triangles[0].alpha_1m), angles='xy', scale_units='xy', scale=triangles[0].z_1m*1.1, color='red')
    offset = 2

    for tri in triangles:
        velocity_triangle(tri.C_2m, tri.W_2m, tri.U_2m, tri.alpha_2m, tri.beta_2m, tri.z_2m, offset)
        offset = offset + 1
        velocity_triangle(tri.C_3m, tri.W_3m, tri.U_3m, tri.alpha_3m, tri.beta_3m, tri.z_3m, offset)
        offset = offset + 1

    plt.axis('equal')

def tree(trunk, branches, root_x, root_y, scale, style, axis):
    for i in range(len(trunk)):
        axis.quiver(root_x, root_y + trunk(i), branches(i), 0, scale, style)

def velocity_triangle(C, W, U, alpha, beta, z, z_offset):
    plt.quiver(z_offset, 0, C*np.cos(alpha), C*np.sin(alpha), angles='xy', scale_units='xy', scale=z*1.1, color='red')
    plt.quiver(z_offset, 0, W*np.cos(beta),  W*np.sin(beta), angles='xy', scale_units='xy', scale=z*1.1, color='cyan')
    plt.quiver(z_offset+(1/1.1), W*np.sin(beta)/(z*1.1), 0, U, angles='xy', scale_units='xy', scale=z*1.1, color='teal')