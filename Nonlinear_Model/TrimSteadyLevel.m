function [xTrim, uTrim] = TrimSteadyLevel(Vtrim, htrim)
% TrimSteadyLevel
% Finds steady, straight, level-flight trim using fminsearch.
%
% INPUTS:
%   Vtrim - Desired airspeed [m/s]
%   htrim - Desired altitude [m]
%
% OUTPUTS:
%   xTrim - Trimmed 12-state vector
%   uTrim - Trimmed 4-input control vector
%
% STATES:
%   X = [x y z u v w phi theta psi p q r]'
%
% INPUTS:
%   U = [delta_ail delta_ele delta_rud delta_thr]'


%% ================================================================
% INITIAL GUESS
% ================================================================

% Optimization vector:
%
% z = [alpha theta delta_ele delta_thr]'

alpha0    = deg2rad(5);
theta0    = deg2rad(5);
deltaEle0 = deg2rad(0);
deltaThr0 = 0.5;

z0 = [ ...
    alpha0;
    theta0;
    deltaEle0;
    deltaThr0
    ];


%% ================================================================
% FMINSEARCH OPTIONS
% ================================================================

options = optimset( ...
    'Display', 'iter', ...
    'MaxIter', 2000, ...
    'MaxFunEvals', 5000, ...
    'TolX', 1e-8, ...
    'TolFun', 1e-8);


%% ================================================================
% RUN FMINSEARCH
% ================================================================

zTrim = fminsearch( ...
    @(z) TrimCostSteadyLevel(z, Vtrim, htrim), ...
    z0, ...
    options);


%% ================================================================
% EXTRACT TRIM VARIABLES
% ================================================================

alpha    = zTrim(1);
theta    = zTrim(2);
deltaEle = zTrim(3);
deltaThr = zTrim(4);


%% ================================================================
% CONSTRUCT TRIMMED STATE
% ================================================================

% Steady level flight:
%
% beta = 0
% phi  = 0
%
% Therefore:
%
% u = V cos(alpha)
% v = 0
% w = V sin(alpha)

u = Vtrim*cos(alpha);
v = 0;
w = Vtrim*sin(alpha);

phi = 0;
psi = 0;

p = 0;
q = 0;
r = 0;


% NED position
%
% z is positive DOWN.
% Therefore altitude htrim corresponds to z = -htrim.

xPos = 0;
yPos = 0;
zPos = -htrim;


% Complete state vector

xTrim = [ ...
    xPos;
    yPos;
    zPos;
    u;
    v;
    w;
    phi;
    theta;
    psi;
    p;
    q;
    r
    ];


%% ================================================================
% CONSTRUCT TRIMMED CONTROL VECTOR
% ================================================================

deltaAil = 0;
deltaRud = 0;

uTrim = [ ...
    deltaAil;
    deltaEle;
    deltaRud;
    deltaThr
    ];


%% ================================================================
% DISPLAY RESULT
% ================================================================

fprintf('\n');
fprintf('================================================\n');
fprintf('             STEADY LEVEL TRIM\n');
fprintf('================================================\n');

fprintf('Requested airspeed : %.3f m/s\n', Vtrim);
fprintf('Requested altitude : %.3f m\n', htrim);

fprintf('\nTrimmed State:\n');

fprintf('u                 : %.6f m/s\n', u);
fprintf('v                 : %.6f m/s\n', v);
fprintf('w                 : %.6f m/s\n', w);

fprintf('alpha             : %.6f deg\n', rad2deg(alpha));
fprintf('theta             : %.6f deg\n', rad2deg(theta));

fprintf('\nTrimmed Controls:\n');

fprintf('Aileron           : %.6f deg\n', rad2deg(deltaAil));
fprintf('Elevator          : %.6f deg\n', rad2deg(deltaEle));
fprintf('Rudder            : %.6f deg\n', rad2deg(deltaRud));
fprintf('Throttle          : %.6f\n', deltaThr);

fprintf('================================================\n');


end