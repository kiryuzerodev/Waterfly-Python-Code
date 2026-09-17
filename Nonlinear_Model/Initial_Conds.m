%% initial_conditions.m
% Initialize aircraft model parameters, initial conditions and inputs
% and run the Simulink aircraft model.
%
% Model:
%   Aircraft_Model.slx
%
% State vector:
%   X = [x y z u v w phi theta psi p q r]'
  % 1 - x
  % 2 - y
  % 3 - z
  % 4 - u
  % 5 - v
  % 6 - w
  % 7 - phi
  % 8 - theta
  % 9 - psi
  % 10 - p
  % 11 - q
  % 12 - r
%
% Control vector:
%   U = [delta_ail delta_ele delta_rud delta_thr]'


%% ================================================================
% LOAD AIRCRAFT PARAMETERS
% ================================================================

params;


%% ================================================================
% INITIAL CONDITIONS
% ================================================================

% Position in NED frame

x0 = 0;                 % Initial North position [m]
y0 = 0;                 % Initial East position [m]
z0 = -1000;             % Initial Down position [m]
                        % Negative z corresponds to +ve altitude


% Body-axis velocities

u0 = 200;               % Initial forward velocity [m/s]
v0 = 0;                 % Initial lateral velocity [m/s]
w0 = 0;                 % Initial vertical body velocity [m/s]


% Euler angles

phi0   = 0;             % Initial roll angle [rad]
theta0 = 0;             % Initial pitch angle [rad]
psi0   = 0;             % Initial yaw angle [rad]


% Body angular rates

p0 = 0;                 % Initial roll rate [rad/s]
q0 = 0;                 % Initial pitch rate [rad/s]
r0 = 0;                 % Initial yaw rate [rad/s]




%% ==================================================================
%  CALL FOR TRIM CHECK AND IF SUCCESSFUL, USE THOSE AS INITIAL CONDS
%  ==================================================================

% If it becomes not zero, trim was successful
% flagger = 0;

Trim_Check;
flagger = evalin('base','flagger');

if flagger ~= 0
    x0 = evalin('base','xTrim');
else
    % Complete initial state vector
    x0 = [x0;y0;z0;u0;v0;w0;phi0;theta0;psi0;p0;q0;r0];
end




%% ================================================================
% INITIAL CONTROL INPUTS
% ================================================================

delta_ail = 0;          % Initial aileron deflection [rad]
delta_ele = 0;          % Initial elevator deflection [rad]
delta_rud = 0;          % Initial rudder deflection [rad]
delta_thr = 0;          % Initial throttle command [-]



if flagger ~= 0
    U0 = evalin('base','uTrim');
else
    % Complete control vector
    U0 = [delta_ail;delta_ele;delta_rud;delta_thr];
end


%% ================================================================
% SIMULATION SETTINGS
% ================================================================

tStart = 0;             % Simulation start time [s]
tEnd   = 75;             % Simulation end time [s]


%% ================================================================
% RUN SIMULINK MODEL
% ================================================================

sim('Aircraft_Model.slx');