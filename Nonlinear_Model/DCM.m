function Cbn = DCM(phi, theta, psi)
% DCM
% Direction Cosine Matrix for a 3-2-1 (yaw-pitch-roll) rotation.
%
% INPUT:
%   phi   - Roll angle [rad]
%   theta - Pitch angle [rad]
%   psi   - Yaw angle [rad]
%
% OUTPUT:
%   Cbn   - Direction cosine matrix transforming
%           body-frame vectors to NED-frame vectors
%
%   v_NED = Cbn * v_body


%% ================================================================
% TRIGONOMETRIC TERMS
% ================================================================

cphi   = cos(phi);
sphi   = sin(phi);

ctheta = cos(theta);
stheta = sin(theta);

cpsi   = cos(psi);
spsi   = sin(psi);


%% ================================================================
% BODY -> NED DCM
% ================================================================

Cbn = [ ...
    ctheta*cpsi, ...
    sphi*stheta*cpsi - cphi*spsi, ...
    cphi*stheta*cpsi + sphi*spsi;

    ctheta*spsi, ...
    sphi*stheta*spsi + cphi*cpsi, ...
    cphi*stheta*spsi - sphi*cpsi;

    -stheta, ...
    sphi*ctheta, ...
    cphi*ctheta
    ];

end