clc
clear
close all

% ---------
% Plot Setup
% ---------
% Set Plot Width and FontSize
plot_width = 3.0;
aspect_ratio = 3/1; % 4:3 3:2 1:1
% Titel and Label Font size
font_size = 8.0;
% Legend font size
lfont_size = 6.0;
plot_height = plot_width * (1/aspect_ratio);
% Plot Line Widths
line_width = 1.1;
event_line_width = 0.5;
x_label_height = 0.17;

% load velocity command data which came from the following rosbag:
% ~/Desktop/rosbags/june_27/odroid_bags/t6o_euler_2018-08-29-10-03-00.bag
load('ml_sup3_boat_euler.mat');

% eye-balling the data here based off of video when the drone touched down.
t = euler(1:end,1);
roll = euler(1:end,2);
roll = roll;
pitch = euler(1:end,3);

lever_length = 1.78;  % meters
heave = -lever_length * sin(pitch);

% fix the time
t = t - t(1);

t = t - 40.65;

% Times when events took place starting the bag from t=66.0 seconds
t_wind_cal_start = 5.7;
t_wind_cal_stop = 15.7;
t_heading_cor = 21.7;
t_ibvs_outer = 32.0;
t_ibvs_inner = 59.65;
t_land_mode = 67.1;
t_land = 67.6;

t_end = 70;

figure('Units', 'inches', ...
       'Position', [0 0 plot_width plot_height], ...
       'PaperPositionMode', 'auto')
plot(t, roll, 'LineWidth', line_width)
hold on
plot([t_wind_cal_start; t_wind_cal_start], [-100; 100], '-.k', 'LineWidth', event_line_width)
plot([t_wind_cal_stop; t_wind_cal_stop], [-100; 100], '-.k', 'LineWidth', event_line_width)
plot([t_heading_cor; t_heading_cor], [-100; 100], '-.k', 'LineWidth', event_line_width)
plot([t_ibvs_outer; t_ibvs_outer], [-100; 100], '-.k', 'LineWidth', event_line_width)
plot([t_ibvs_inner; t_ibvs_inner], [-100; 100], '-.k', 'LineWidth', event_line_width)
plot([t_land_mode; t_land_mode], [-100; 100], '-.k', 'LineWidth', event_line_width)
plot([t_land; t_land], [-100; 100], '-.k', 'LineWidth', event_line_width)
% title('Marker Detection Rate vs Distance from Marker',...
%       'Interpreter', 'latex',...
%       'FontUnits', 'points',...
%       'FontSize', font_size,...
%       'FontName', 'Times')
  
% xlabel('Distance (m)',...
%        'Interpreter', 'latex',...
%        'FontUnits', 'points',...
%        'FontSize', font_size,...
%        'FontName', 'Times')
   
ylabel('Roll (rad)',...
       'Interpreter', 'latex',...
       'FontUnits', 'points',...
       'FontSize', font_size,...
       'FontName', 'Times')

% legend([h1], {'Touchdown'},...
%        'Interpreter', 'latex',...
%        'FontUnits', 'points',...
%        'FontSize', lfont_size,...
%        'FontName', 'Times',...
%        'Location', 'NorthEast',...
%        'Orientation', 'vertical',...
%        'Box', 'on')

axis([0, t_end, -0.3, 0.3])
set(gca, ...
    'YTick', -0.3:0.15:0.3,...
    'XTick', 0:10:t_end,...
    'FontSize', font_size,...
    'FontName', 'Times')
grid on



figure('Units', 'inches', ...
       'Position', [0 0 plot_width plot_height], ...
       'PaperPositionMode', 'auto')
plot(t, pitch, 'LineWidth', line_width)
hold on
plot([t_wind_cal_start; t_wind_cal_start], [-100; 100], '-.k', 'LineWidth', event_line_width)
plot([t_wind_cal_stop; t_wind_cal_stop], [-100; 100], '-.k', 'LineWidth', event_line_width)
plot([t_heading_cor; t_heading_cor], [-100; 100], '-.k', 'LineWidth', event_line_width)
plot([t_ibvs_outer; t_ibvs_outer], [-100; 100], '-.k', 'LineWidth', event_line_width)
plot([t_ibvs_inner; t_ibvs_inner], [-100; 100], '-.k', 'LineWidth', event_line_width)
plot([t_land_mode; t_land_mode], [-100; 100], '-.k', 'LineWidth', event_line_width)
plot([t_land; t_land], [-100; 100], '-.k', 'LineWidth', event_line_width)
% title('Marker Detection Rate vs Distance from Marker',...
%       'Interpreter', 'latex',...
%       'FontUnits', 'points',...
%       'FontSize', font_size,...
%       'FontName', 'Times')
  
% xlabel('Time (s)',...
%        'Interpreter', 'latex',...
%        'FontUnits', 'points',...
%        'FontSize', font_size,...
%        'FontName', 'Times')
   
ylabel('Pitch (rad)',...
       'Interpreter', 'latex',...
       'FontUnits', 'points',...
       'FontSize', font_size,...
       'FontName', 'Times')

% legend({'Outer', 'Inner'},...
%        'Interpreter', 'latex',...
%        'FontUnits', 'points',...
%        'FontSize', lfont_size,...
%        'FontName', 'Times',...
%        'Location', 'East',...
%        'Orientation', 'vertical',...
%        'Box', 'on')

axis([0, t_end, -0.2, 0.2])
set(gca, ...
    'YTick', -0.2:0.1:0.2,...
    'XTick', 0:10:t_end,...
    'FontSize', font_size,...
    'FontName', 'Times')
grid on


figure('Units', 'inches', ...
       'Position', [0 0 plot_width plot_height+x_label_height], ...
       'PaperPositionMode', 'auto')
plot(t, heave, 'LineWidth', line_width)
hold on
plot([t_wind_cal_start; t_wind_cal_start], [-100; 100], '-.k', 'LineWidth', event_line_width)
plot([t_wind_cal_stop; t_wind_cal_stop], [-100; 100], '-.k', 'LineWidth', event_line_width)
plot([t_heading_cor; t_heading_cor], [-100; 100], '-.k', 'LineWidth', event_line_width)
plot([t_ibvs_outer; t_ibvs_outer], [-100; 100], '-.k', 'LineWidth', event_line_width)
plot([t_ibvs_inner; t_ibvs_inner], [-100; 100], '-.k', 'LineWidth', event_line_width)
plot([t_land_mode; t_land_mode], [-100; 100], '-.k', 'LineWidth', event_line_width)
plot([t_land; t_land], [-100; 100], '-.k', 'LineWidth', event_line_width)
% title('Marker Detection Rate vs Distance from Marker',...
%       'Interpreter', 'latex',...
%       'FontUnits', 'points',...
%       'FontSize', font_size,...
%       'FontName', 'Times')
  
xlabel('Time (s)',...
       'Interpreter', 'latex',...
       'FontUnits', 'points',...
       'FontSize', font_size,...
       'FontName', 'Times')
   
ylabel('Heave (m)',...
       'Interpreter', 'latex',...
       'FontUnits', 'points',...
       'FontSize', font_size,...
       'FontName', 'Times')

% legend({'Outer', 'Inner'},...
%        'Interpreter', 'latex',...
%        'FontUnits', 'points',...
%        'FontSize', lfont_size,...
%        'FontName', 'Times',...
%        'Location', 'East',...
%        'Orientation', 'vertical',...
%        'Box', 'on')

axis([0, t_end, -0.3, 0.3])
set(gca, ...
    'YTick', -0.3:0.15:0.3,...
    'XTick', 0:10:t_end,...
    'FontSize', font_size,...
    'FontName', 'Times')
grid on

% Get default colors
% get(gca,'colororder')

%EXPORT FIGURE
% -Select the figure window you want to export
% -in command window:
%  print -depsc2 path2plotfile.eps
%