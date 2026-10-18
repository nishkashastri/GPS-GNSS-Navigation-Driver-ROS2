% allan_variance.m  -  EECE 5554 Lab 3: Allan variance of VN-100 gyro & accel
% Based on MathWorks "Inertial Sensor Noise Analysis Using Allan Variance".
% Put this script in the same folder as imu_5hr.csv and press Run.

clear; close all; clc;

file = 'imu_5hr_small.csv';
D = readmatrix(file);          % text columns (frame_id) become NaN; ignored

t     = D(:, 1);               % time [s]
gyro  = D(:, 2:4);            % angular velocity x,y,z [rad/s]
accel = D(:, 5:7);           % linear acceleration x,y,z [m/s^2]

Fs = 1 / median(diff(t));      % sample rate from the data (~40 Hz)
fprintf('Samples: %d   Duration: %.2f h   Fs: %.2f Hz\n', ...
        numel(t), (t(end) - t(1)) / 3600, Fs);

g0 = 9.80665;                  % for converting accel to g
sensors = { gyro,  'Gyroscope',     'rad/s';
            accel, 'Accelerometer', 'm/s^2' };
axisNames = {'X', 'Y', 'Z'};
results = {};

for s = 1:size(sensors, 1)
    data = sensors{s, 1};  name = sensors{s, 2};  unit = sensors{s, 3};

    % Cluster sizes (same as the MathWorks example)
    L = size(data, 1);
    maxM = 2.^floor(log2(L / 2));
    m = unique(ceil(logspace(0, log10(maxM), 100)).');

    [avar, tau] = compute_avar(data, m, Fs);
    adev = sqrt(avar);

    figure('Name', name, 'Position', [100 100 1400 420]);
    for k = 1:3
        [N, K, B, lineN, lineK, lineB, tauB] = noise_params(tau, adev(:, k));

        subplot(1, 3, k);
        loglog(tau, adev(:, k), 'b', 'LineWidth', 1.5); hold on;
        loglog(tau, lineN, 'r--', tau, lineK, 'g--', tau, lineB, 'm--');
        loglog(1, N, 'ro', 3, K, 'go', tauB, B * 0.664, 'mo', 'MarkerFaceColor', 'auto');
        text(1, N, '  N'); text(3, K, '  K'); text(tauB, B * 0.664, '  0.664B');
        grid on; axis tight;
        title(sprintf('%s %s - Allan deviation', name, axisNames{k}));
        xlabel('\tau [s]'); ylabel(sprintf('\\sigma(\\tau) [%s]', unit));
        legend('\sigma(\tau)', 'N (slope -1/2)', 'K (slope +1/2)', 'B (slope 0)', ...
               'Location', 'southwest');

        results(end + 1, :) = {name, axisNames{k}, N, B, K, tauB}; %#ok<SAGROW>
    end
    saveas(gcf, sprintf('allan_%s.png', lower(name)));
end

% Results table (SI units)
T = cell2table(results, 'VariableNames', ...
    {'Sensor', 'Axis', 'N_random_walk', 'B_bias_instability', 'K_rate_random_walk', 'tau_at_B_s'});

% Datasheet-friendly units
isG = strcmp(T.Sensor, 'Gyroscope');
T.N_datasheet = T.N_random_walk;  T.B_datasheet = T.B_bias_instability;
T.N_datasheet(isG)  = T.N_random_walk(isG) * 180/pi * 60;       % deg/sqrt(hr)
T.B_datasheet(isG)  = T.B_bias_instability(isG) * 180/pi * 3600; % deg/hr
T.N_datasheet(~isG) = T.N_random_walk(~isG) / g0 * 1e6;         % ug/sqrt(Hz)
T.B_datasheet(~isG) = T.B_bias_instability(~isG) / g0 * 1e6;    % ug

disp(T);
fprintf(['\nSI units: gyro N [rad/s/sqrt(Hz)], B [rad/s], K [rad/s^2/sqrt(Hz)]\n' ...
         '          accel N [m/s^2/sqrt(Hz)], B [m/s^2], K [m/s^3/sqrt(Hz)]\n' ...
         'Datasheet units: gyro N [deg/sqrt(hr)], B [deg/hr];  accel N [ug/sqrt(Hz)], B [ug]\n']);
writetable(T, 'allan_results.csv');


%% ---------- Local functions ----------
function [avar, tau] = compute_avar(omega, m, Fs)
    % Use the toolbox function if available, otherwise the same formula by hand.
    if exist('allanvar', 'file')
        [avar, tau] = allanvar(omega, m, Fs);
        return;
    end
    t0 = 1 / Fs;
    theta = cumsum(omega, 1) * t0;            % integrate rate -> angle
    L = size(theta, 1);
    tau = m * t0;
    avar = zeros(numel(m), size(omega, 2));
    for i = 1:numel(m)
        mi = m(i);
        avar(i, :) = sum((theta(1 + 2*mi:L, :) - 2*theta(1 + mi:L - mi, :) ...
                          + theta(1:L - 2*mi, :)).^2, 1);
    end
    avar = avar ./ (2 * tau.^2 .* (L - 2*m));
end

function [N, K, B, lineN, lineK, lineB, tauB] = noise_params(tau, adev)
    logtau = log10(tau);  logadev = log10(adev);
    dlog = diff(logadev) ./ diff(logtau);     % local slope of the curve

    % Angle/velocity random walk N: slope -1/2, read at tau = 1 s
    [~, i] = min(abs(dlog + 0.5));
    b = logadev(i) + 0.5 * logtau(i);
    N = 10^b;                                 % value of the line at tau = 1
    lineN = N ./ sqrt(tau);

    % Rate random walk K: slope +1/2, read at tau = 3 s
    [~, i] = min(abs(dlog - 0.5));
    b = logadev(i) - 0.5 * logtau(i);
    K = 10^(0.5 * log10(3) + b);
    lineK = K .* sqrt(tau / 3);

    % Bias instability B: slope 0 (flat bottom), scaled by 0.664
    [~, i] = min(abs(dlog));
    scfB = sqrt(2 * log(2) / pi);             % = 0.664
    B = adev(i) / scfB;
    tauB = tau(i);
    lineB = B * scfB * ones(size(tau));
end
