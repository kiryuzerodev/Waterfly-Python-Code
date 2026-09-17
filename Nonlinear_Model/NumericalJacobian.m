function [A,B] = NumericalJacobian(Xtrim,Utrim)

nx = length(Xtrim);
nu = length(Utrim);

A = zeros(nx,nx);
B = zeros(nx,nu);

% Perturbation sizes
dx = 1e-5;
du = 1e-5;


% Jacobian A
for i = 1:nx

    Xplus = Xtrim;
    Xminus = Xtrim;

    Xplus(i)  = Xplus(i)  + dx;
    Xminus(i) = Xminus(i) - dx;

    fplus  = Non_Linear_Model_V1(Xplus,Utrim);
    fminus = Non_Linear_Model_V1(Xminus,Utrim);

    A(:,i) = (fplus - fminus)/(2*dx);

end

% Jacobian B
for i = 1:nu

    Uplus = Utrim;
    Uminus = Utrim;

    Uplus(i)  = Uplus(i)  + du;
    Uminus(i) = Uminus(i) - du;

    fplus  = Non_Linear_Model_V1(Xtrim,Uplus);
    fminus = Non_Linear_Model_V1(Xtrim,Uminus);

    B(:,i) = (fplus - fminus)/(2*du);

end

end