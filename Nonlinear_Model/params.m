%% params.m
% Aircraft, atmosphere, propulsion and aerodynamic parameters
% All angles used by the nonlinear model are in radians.

%% ================================================================
% AIRCRAFT MASS AND INERTIA
% ================================================================

m   = 4536;             % Aircraft mass [kg]

Ixx = 35926.5;          % Moment of inertia about body X axis [kg m^2]
Iyy = 33940.7;          % Moment of inertia about body Y axis [kg m^2]
Izz = 67085.5;          % Moment of inertia about body Z axis [kg m^2]
Ixz = 3418.17;          % Product of inertia Ixz [kg m^2]


%% ================================================================
% AIRCRAFT GEOMETRY
% ================================================================

S    = 21.5;            % Wing reference area [m^2]
b    = 10.4;            % Wing span [m]
cBar = 2.14;            % Mean aerodynamic chord [m]

taperw = 0.507;         % Wing taper ratio [-]
ARw    = 5.02;          % Wing aspect ratio [-]
sweepw = 13*pi/180;     % Wing quarter-chord sweep [rad]

ARh    = 4.0;           % Horizontal-tail aspect ratio [-]
sweeph = 25*pi/180;     % Horizontal-tail quarter-chord sweep [rad]

ARv    = 0.64;          % Vertical-tail aspect ratio [-]
sweepv = 40*pi/180;     % Vertical-tail quarter-chord sweep [rad]

lvt    = 4.72;          % Vertical-tail moment arm [m]


%% ================================================================
% ATMOSPHERE
% ================================================================

g       = 9.80665;      % Gravitational acceleration [m/s^2]

rho0    = 1.225;        % Sea-level air density [kg/m^3]
P0      = 101325;       % Sea-level atmospheric pressure [Pa]
T0      = 288.15;      % Sea-level temperature [K]

R       = 287.05287;    % Specific gas constant for air [J/(kg K)]
gamma   = 1.4;          % Ratio of specific heats [-]


%% ================================================================
% PROPULSION
% ================================================================

StaticThrust = 26243.2; % Maximum static thrust at sea level [N]


%% ================================================================
% LONGITUDINAL AERODYNAMICS
% ================================================================

% Lift coefficient:
%
% CL = CL0 + CL_alpha*alpha + CL_qHat*qHat + CL_deltaE*deltaE

CL0       = 0.1101;     % Lift coefficient at alpha = 0 deg [-]

CL_alpha  = 5.8279;     % Lift-curve slope [1/rad]

CL_qHat   = 7.4838;     % Lift coefficient derivative wrt qHat [-]

CL_deltaE = 0.5774;     % Lift coefficient derivative wrt elevator [1/rad]


% Drag coefficient:
%
% CD = CD0 + CD_alpha*alpha + CD_alpha2*alpha^2

CD0       = 0.0254;     % Zero-alpha drag coefficient [-]

CD_alpha  = 0.0;        % Linear drag-alpha coefficient [1/rad]

CD_alpha2 = 0.0;        % Quadratic drag-alpha coefficient [1/rad^2]


% Pitching moment:
%
% Cm = Cm0 + Cm_alpha*alpha + Cm_qHat*qHat + Cm_deltaE*deltaE

Cm0       = 0.0;        % Pitching moment coefficient at alpha = 0 [-]

Cm_alpha  = -1.0671;    % Pitch stiffness derivative [1/rad]

Cm_qHat   = -15.1497;   % Pitch damping derivative wrt qHat [-]

Cm_deltaE = -1.3749;    % Pitching moment derivative wrt elevator [1/rad]


%% ================================================================
% LATERAL-DIRECTIONAL AERODYNAMICS
% ================================================================

% Side force:
%
% CY = CY_beta*beta
%    + CY_pHat*pHat
%    + CY_rHat*rHat
%    + CY_deltaA*deltaA
%    + CY_deltaR*deltaR

CY_beta   = -0.6261;    % Side-force derivative wrt sideslip [1/rad]

CY_pHat   = 0.0;        % Side-force derivative wrt pHat [-]
CY_rHat   = 0.0;        % Side-force derivative wrt rHat [-]

CY_deltaA = -0.00699;   % Side-force derivative wrt aileron [1/rad]
CY_deltaR = 0.1574;     % Side-force derivative wrt rudder [1/rad]


% Rolling moment:
%
% Cl = Cl_beta*beta
%    + Cl_pHat*pHat
%    + Cl_rHat*rHat
%    + Cl_deltaA*deltaA
%    + Cl_deltaR*deltaR

Cl_beta   = -0.1649;    % Rolling-moment derivative wrt sideslip [1/rad]

Cl_pHat   = -1.2000;    % Roll damping derivative wrt pHat [-]
Cl_rHat   = -0.0227;    % Roll-yaw coupling derivative wrt rHat [-]

Cl_deltaA = 0.1377;     % Rolling-moment derivative wrt aileron [1/rad]
Cl_deltaR = 0.0175;     % Rolling-moment derivative wrt rudder [1/rad]


% Yawing moment:
%
% Cn = Cn_beta*beta
%    + Cn_pHat*pHat
%    + Cn_rHat*rHat
%    + Cn_deltaA*deltaA
%    + Cn_deltaR*deltaR

Cn_beta   = 0.1434;     % Yawing-moment derivative wrt sideslip [1/rad]

Cn_pHat   = 0.0227;     % Yawing moment derivative wrt pHat [-]
Cn_rHat   = -0.0649;     % Yaw damping derivative wrt rHat [-]

Cn_deltaA = 0.0014;     % Yawing-moment derivative wrt aileron [1/rad]
Cn_deltaR = -0.0698;    % Yawing-moment derivative wrt rudder [1/rad]


%% ================================================================
% NON-DIMENSIONAL RATE DEFINITIONS
% ================================================================

% These are used in the aerodynamic model:
%
% pHat = p*b/(2*V)
% qHat = q*cBar/(2*V)
% rHat = r*b/(2*V)