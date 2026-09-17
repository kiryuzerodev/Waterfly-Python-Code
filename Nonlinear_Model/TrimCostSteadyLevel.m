function J = TrimCostSteadyLevel(z, Vtrim, htrim)
% TrimCostSteadyLevel
% Cost function used by fminsearch for steady level flight trim.
%
% z = [alpha theta delta_ele delta_thr]'


%% ================================================================
% EXTRACT OPTIMIZATION VARIABLES
% ================================================================

alpha    = z(1);
theta    = z(2);
deltaEle = z(3);
deltaThr = z(4);


%% ================================================================
% BUILD STATE VECTOR
% ================================================================

% Steady straight level flight:
%
% beta = 0
% phi  = 0
% p = q = r = 0
%
% V = sqrt(u^2 + v^2 + w^2)
%
% alpha = atan2(w,u)

u = Vtrim*cos(alpha);
v = 0;
w = Vtrim*sin(alpha);

phi = 0;
psi = 0;

p = 0;
q = 0;
r = 0;

% NED position
xPos = 0;
yPos = 0;
zPos = -htrim;


X = [ ...
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
% BUILD CONTROL VECTOR
% ================================================================

deltaAil = 0;
deltaRud = 0;

U = [ ...
    deltaAil;
    deltaEle;
    deltaRud;
    deltaThr
    ];


%% ================================================================
% RUN NONLINEAR AIRCRAFT MODEL
% ================================================================

XDOT = Non_Linear_Model_V1(X,U);


%% ================================================================
% EXTRACT DERIVATIVES
% ================================================================

xdot     = XDOT(1);
ydot     = XDOT(2);
zdot     = XDOT(3);

udot     = XDOT(4);
vdot     = XDOT(5);
wdot     = XDOT(6);

phidot   = XDOT(7);
thetadot = XDOT(8);
psidot   = XDOT(9);

pdot     = XDOT(10);
qdot     = XDOT(11);
rdot     = XDOT(12);


%% ================================================================
% TRIM CONDITIONS
% ================================================================

% For steady straight level flight:
%
% Body velocities must remain constant
% Angular rates must remain constant
% Aircraft must not rotate
% Aircraft should not be climbing as well
%
% Since:
%   p = q = r = 0
%
% we require:
%
%   zdot = 0
%   udot = 0
%   vdot = 0
%   wdot = 0
%   pdot = 0
%   qdot = 0
%   rdot = 0

TrimError = [ ...
    zdot;  % added this as we want the steady level flight
    udot;
    vdot;
    wdot;
    pdot;
    qdot;
    rdot
    ];


%% ================================================================
% COST
% ================================================================

J = sum(TrimError.^2);


%% ================================================================
% PENALTIES
% ================================================================

% fminsearch has no built-in constraints.
% Therefore penalize physically unreasonable solutions.

% Angle of attack limits
if alpha < deg2rad(-10)
    J = J + 1e6*(alpha - deg2rad(-10))^2;
end

if alpha > deg2rad(20)
    J = J + 1e6*(alpha - deg2rad(20))^2;
end


% Pitch angle limits
if theta < deg2rad(-20)
    J = J + 1e6*(theta - deg2rad(-20))^2;
end

if theta > deg2rad(20)
    J = J + 1e6*(theta - deg2rad(20))^2;
end


% Elevator limits
if deltaEle < deg2rad(-25)
    J = J + 1e6*(deltaEle - deg2rad(-25))^2;
end

if deltaEle > deg2rad(25)
    J = J + 1e6*(deltaEle - deg2rad(25))^2;
end


% Throttle limits
if deltaThr < 0
    J = J + 1e6*deltaThr^2;
end

if deltaThr > 1
    J = J + 1e6*(deltaThr - 1)^2;
end

end