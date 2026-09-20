function XDOT = Non_Linear_Model_V1(X,U)
% Non_Linear_Model_V1
% 12-state nonlinear 6-DOF aircraft equations of motion.
%
% STATES:
%   X = [x y z u v w phi theta psi p q r]'
%
%   x,y,z       - NED position [m]
%   u,v,w       - Body-axis velocity [m/s]
%   phi         - Roll angle [rad]
%   theta       - Pitch angle [rad]
%   psi         - Yaw angle [rad]
%   p,q,r       - Body angular rates [rad/s]
%
% INPUTS:
%   U = [delta_ail delta_ele delta_rud delta_thr]'
%
%   delta_ail   - Aileron deflection [rad]
%   delta_ele   - Elevator deflection [rad]
%   delta_rud   - Rudder deflection [rad]
%   delta_thr   - Throttle command [-]
%
% OUTPUT:
%   XDOT = derivative of the 12-state vector


%% ================================================================
% GET PARAMETERS FROM BASE WORKSPACE
% ================================================================

m    = evalin('base','m');

Ixx  = evalin('base','Ixx');
Iyy  = evalin('base','Iyy');
Izz  = evalin('base','Izz');
Ixz  = evalin('base','Ixz');

S    = evalin('base','S');
b    = evalin('base','b');
cBar = evalin('base','cBar');

g    = evalin('base','g');

StaticThrust = evalin('base','StaticThrust');


%% ================================================================
% EXTRACT STATES
% ================================================================

x     = X(1);
y     = X(2);
z     = X(3);

u     = X(4);
v     = X(5);
w     = X(6);

phi   = X(7);
theta = X(8);
psi   = X(9);

p     = X(10);
q     = X(11);
r     = X(12);


%% ================================================================
% EXTRACT CONTROL INPUTS
% ================================================================

delta_ail = U(1);
delta_ele = U(2);
delta_rud = U(3);
delta_thr = U(4);


%% ================================================================
% ALTITUDE AND ATMOSPHERE
% ================================================================

% NED convention:
%   z positive downward
%   altitude positive upward

h = -z;

[rho, ~, ~, a] = Atmosphere(h);


%% ================================================================
% AIR DATA
% ================================================================

V = sqrt(u^2 + v^2 + w^2);

% Avoid numerical problems at zero airspeed.

if V > 1e-6

    alpha = atan2(w,u);
    beta  = asin(max(-1,min(1,v/V)));

else

    alpha = 0;
    beta  = 0;

end

Mach = V/a;


%% ================================================================
% DYNAMIC PRESSURE
% ================================================================

qbar = 0.5*rho*V^2;


%% ================================================================
% AERODYNAMIC COEFFICIENTS
% ================================================================

[CD, CL, CY, Cl, Cm, Cn] = AeroModel( ...
    alpha, beta, ...
    p, q, r, V, ...
    delta_ail, delta_ele, delta_rud, ...
    Mach);


%% ================================================================
% AERODYNAMIC FORCES
% ================================================================

% Forces are initially calculated in the wind-axis formulation.
%
% X_wind = -D
% Z_wind = -L
%
% They are then transformed into body axes.

Drag = qbar*S*CD;
Lift = qbar*S*CL;
Side = qbar*S*CY;


% Wind -> body transformation

ca = cos(alpha);
sa = sin(alpha);

cb = cos(beta);
sb = sin(beta);

C_bw = [ ...
     ca*cb,  -ca*sb,  -sa;
     sb,      cb,      0;
     sa*cb,  -sa*sb,   ca
    ];

F_wind = [-Drag;
           Side;
          -Lift];

F_aero_body = C_bw * F_wind;


Xaero = F_aero_body(1);
Yaero = F_aero_body(2);
Zaero = F_aero_body(3);


%% ================================================================
% PROPULSION
% ================================================================

% Simple thrust model.
%
% delta_thr = 0  -> zero thrust
% delta_thr = 1  -> maximum static thrust

T = delta_thr * StaticThrust;

% Assume thrust acts along positive body X axis.

Xprop = T;
Yprop = 0;
Zprop = 0;


%% ================================================================
% TOTAL BODY FORCES
% ================================================================

Xforce = Xaero + Xprop;
Yforce = Yaero + Yprop;
Zforce = Zaero + Zprop;


%% ================================================================
% GRAVITY IN BODY FRAME
% ================================================================

Cbn = DCM(phi,theta,psi);

g_NED = [0;
         0;
         g];

g_body = Cbn' * g_NED;

gx = g_body(1);
gy = g_body(2);
gz = g_body(3);


%% ================================================================
% TRANSLATIONAL EQUATIONS OF MOTION
% ================================================================

udot = Xforce/m + gx + r*v - q*w;

vdot = Yforce/m + gy + p*w - r*u;

wdot = Zforce/m + gz + q*u - p*v;


%% ================================================================
% POSITION KINEMATICS
% ================================================================

V_body = [u;
          v;
          w];

V_NED = Cbn * V_body;

xdot = V_NED(1);
ydot = V_NED(2);
zdot = V_NED(3);


%% ================================================================
% AERODYNAMIC MOMENTS
% ================================================================

Lmoment = qbar*S*b*Cl;
Mmoment = qbar*S*cBar*Cm;
Nmoment = qbar*S*b*Cn;


%% ================================================================
% ROTATIONAL EQUATIONS OF MOTION
% ================================================================

den = Ixx*Izz - Ixz^2;


pdot = ( ...
    Izz*Lmoment ...
    + Ixz*Nmoment ...
    - ( ...
        Ixz*(Iyy-Ixx-Izz)*p ...
        + (Ixz^2 + Izz*(Izz-Iyy))*r ...
      )*q ...
    ) / den;


qdot = ( ...
    Mmoment ...
    - (Ixx-Izz)*p*r ...
    - Ixz*(p^2-r^2) ...
    ) / Iyy;


rdot = ( ...
    Ixz*Lmoment ...
    + Ixx*Nmoment ...
    + ( ...
        Ixz*(Iyy-Ixx-Izz)*r ...
        + (Ixz^2 + Ixx*(Ixx-Iyy))*p ...
      )*q ...
    ) / den;


%% ================================================================
% EULER ANGLE KINEMATICS
% ================================================================

% Avoid singularity at theta = +/- 90 deg.

ctheta = cos(theta);

if abs(ctheta) > 1e-6

    phidot = p ...
        + sin(phi)*tan(theta)*q ...
        + cos(phi)*tan(theta)*r;

    thetadot = cos(phi)*q - sin(phi)*r;

    psidot = ( ...
        sin(phi)*q ...
        + cos(phi)*r ...
        ) / ctheta;

else

    phidot   = p;
    thetadot = q;
    psidot   = 0;

end


%% ================================================================
% OUTPUT STATE DERIVATIVE
% ================================================================

XDOT = [ ...
    xdot;
    ydot;
    zdot;
    udot;
    vdot;
    wdot;
    phidot;
    thetadot;
    psidot;
    pdot;
    qdot;
    rdot
    ];

end