function [rir] = velvet_fdn(er_signal_tdl, fs)
fs = double(fs);

% get the size of the vector
[rows, cols] = size(er_signal_tdl);

% check if the vector is a column vector (more rows than columns)
if rows < cols
    % if it is a column vector, transpose it
    er_signal_tdl = er_signal_tdl';
end

x = er_signal_tdl;
x = [x(:,1); zeros(2*fs,1)];

% Define FDN
N = 8;
numFDNInput = 1;
numOutput = 2;
inputGain = ones(N,numFDNInput) / sqrt(N);
outputGain = ones(numFDNInput, N);
direct = zeros(numOutput,numFDNInput); % should be replaced with delay line, source -> listener
fdnDelays = [809, 877, 937, 1049, 1151, 1249, 1373, 1499];
numberOfStages = 2;
sparsity = 2;
maxShift = 30;

[feedbackMatrix, revFeedbackMatrix] = constructVelvetFeedbackMatrix(N,numberOfStages,sparsity);
[feedbackMatrix, revFeedbackMatrix] = randomMatrixShift(maxShift, feedbackMatrix, revFeedbackMatrix);

% absorption filters including delay of scattering matrix
[approximation, approximationError] = matrixDelayApproximation(feedbackMatrix);

RT_DC = 0.593; % lowest frequnecy decay in seconds - set from sabine eq
RT_NY = 0.593; % highest frequnecy decay in seconds - set from sabine eq

% Use filterbank instead
[absorption.b,absorption.a] = onePoleAbsorption(RT_DC, RT_NY, fdnDelays + approximation, fs);
zAbsorption = zTF(absorption.b, absorption.a,'isDiagonal', true);

% add transposed conditional

output_transposed = processTransposedFDN(x, fdnDelays, feedbackMatrix, inputGain, outputGain, direct, 'absorptionFilters', zAbsorption);
lossless_output_transposed = processTransposedFDN(x, fdnDelays, feedbackMatrix, inputGain, outputGain, direct);
% output_transposed_norm = output_transposed / max(x);

full_rir = x + output_transposed;

% Delay output by early reflections
% Combine direct signal - (Early reflections) with delayed FDN output.
close all;
% soundsc(x,fs);

% figure
% hold on;
% plot(lossless_output)
% plot(output)
% hold off;

% play output
soundsc(full_rir,fs);

% figure
% hold on;
% plot(lossless_output_transposed)
% plot(output_transposed)
% hold off;

% figure
% hold on;
% plot(output_transposed)
% plot(x)
% hold off;

% figure
% hold on;
% plot(full_rir)
% hold off;

% audiowrite([FULL_RIR_DIR "Velvet_FDN_Unit_ER.wav"], output, fs);
% audiowrite([FULL_RIR_DIR "Velvet_FDN_Lossless.wav_Unit_ER.wav"], lossless_output, fs);

% audiowrite([FULL_RIR_DIR "Velvet_FDN_Transposed_Unit_ER_Full_RIR.wav"], full_rir, fs);
% audiowrite([FULL_RIR_DIR "Velvet_FDN_Transposed_Lossless.wav_Unit_ER.wav"], lossless_output_transposed, fs);

rir = output_transposed;

%% Test: script finished
assert(1 == 1);
end