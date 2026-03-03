function PLOT_Cycle_Graphs(P0s, T0s)
    figure(1)
    % tiledlayout(1,1, TileSpacing='tight', Padding='tight')
    % nexttile

    plot(P0s, T0s)
    drawnow
    % title("Temperature and Pressure at Various Stations")
    % yyaxis left
    % plot([0,1.5,2,2.5,3,4,4.5,5,6,7,8], P0s)
    % ylabel("Pressure")
    % yyaxis right
    % plot([0,1.5,2,2.5,3,4,4.5,5,6,7,8], T0s)
    % ylabel("Temperature")
    % xlabel("Station Number")
    % grid on
end