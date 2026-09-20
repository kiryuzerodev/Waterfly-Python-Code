function [CD, CL, CY, Cl, Cm, Cn] = AeroModel( ...
    alpha, beta, p, q, r, V, delta_ail, delta_ele, delta_rud, Mach)
% AeroModel
% Calculates nonlinear aerodynamic force and moment coefficients.
%
% INPUT:
%   alpha     - Angle of attack [rad]
%   beta      - Sideslip angle [rad]
%   p         - Roll rate [rad/s]
%   q         - Pitch rate [rad/s]
%   r         - Yaw rate [rad/s]
%   V         - Airspeed [m/s]
%   delta_ail - Aileron deflection [rad]
%   delta_ele - Elevator deflection [rad]
%   delta_rud - Rudder deflection [rad]
%   Mach       - Mach number [-]
%
% OUTPUT:
%   CD - Drag coefficient [-]
%   CL - Lift coefficient [-]
%   CY - Side-force coefficient [-]
%   Cl - Rolling-moment coefficient [-]
%   Cm - Pitching-moment coefficient [-]
%   Cn - Yawing-moment coefficient [-]


%% ================================================================
% GET AIRCRAFT PARAMETERS
% ================================================================

b    = evalin('base','b');
cBar = evalin('base','cBar');


%% ================================================================
% GET AERODYNAMIC DERIVATIVES
% ================================================================

% Longitudinal

CL0       = evalin('base','CL0');
CL_alpha  = evalin('base','CL_alpha');
CL_qHat   = evalin('base','CL_qHat');
CL_deltaE = evalin('base','CL_deltaE');

CD0       = evalin('base','CD0');
CD_alpha  = evalin('base','CD_alpha');
CD_alpha2 = evalin('base','CD_alpha2');

Cm0       = evalin('base','Cm0');
Cm_alpha  = evalin('base','Cm_alpha');
Cm_qHat   = evalin('base','Cm_qHat');
Cm_deltaE = evalin('base','Cm_deltaE');


% Lateral-directional

CY_beta   = evalin('base','CY_beta');
CY_pHat   = evalin('base','CY_pHat');
CY_rHat   = evalin('base','CY_rHat');
CY_deltaA = evalin('base','CY_deltaA');
CY_deltaR = evalin('base','CY_deltaR');

Cl_beta   = evalin('base','Cl_beta');
Cl_pHat   = evalin('base','Cl_pHat');
Cl_rHat   = evalin('base','Cl_rHat');
Cl_deltaA = evalin('base','Cl_deltaA');
Cl_deltaR = evalin('base','Cl_deltaR');

Cn_beta   = evalin('base','Cn_beta');
Cn_pHat   = evalin('base','Cn_pHat');
Cn_rHat   = evalin('base','Cn_rHat');
Cn_deltaA = evalin('base','Cn_deltaA');
Cn_deltaR = evalin('base','Cn_deltaR');


%% ================================================================
% NON-DIMENSIONAL ANGULAR RATES
% ================================================================

% Prevent division by zero at zero airspeed.

if V > 1e-6

    pHat = p*b/(2*V);       % Non-dimensional roll rate [-]
    qHat = q*cBar/(2*V);    % Non-dimensional pitch rate [-]
    rHat = r*b/(2*V);       % Non-dimensional yaw rate [-]

else

    pHat = 0;
    qHat = 0;
    rHat = 0;

end


%% ================================================================
% MACH NUMBER
% ================================================================

% Mach is currently not used by the simplified aerodynamic model.
% It is kept as an input so Mach-dependent aerodynamics can be added
% later without changing the function interface.

unused = Mach; %#ok<NASGU>


%% ================================================================
% LONGITUDINAL AERODYNAMIC COEFFICIENTS
% ================================================================

% Lift

CL = CL0 ...
   + CL_alpha*alpha ...
   + CL_qHat*qHat ...
   + CL_deltaE*delta_ele;


% Drag

CD = CD0 ...
   + CD_alpha*alpha ...
   + CD_alpha2*alpha^2;


% Pitching moment

Cm = Cm0 ...
   + Cm_alpha*alpha ...
   + Cm_qHat*qHat ...
   + Cm_deltaE*delta_ele;


%% ================================================================
% LATERAL-DIRECTIONAL AERODYNAMIC COEFFICIENTS
% ================================================================

% Side force

CY = CY_beta*beta ...
   + CY_pHat*pHat ...
   + CY_rHat*rHat ...
   + CY_deltaA*delta_ail ...
   + CY_deltaR*delta_rud;


% Rolling moment

Cl = Cl_beta*beta ...
   + Cl_pHat*pHat ...
   + Cl_rHat*rHat ...
   + Cl_deltaA*delta_ail ...
   + Cl_deltaR*delta_rud;


% Yawing moment

Cn = Cn_beta*beta ...
   + Cn_pHat*pHat ...
   + Cn_rHat*rHat ...
   + Cn_deltaA*delta_ail ...
   + Cn_deltaR*delta_rud;


end