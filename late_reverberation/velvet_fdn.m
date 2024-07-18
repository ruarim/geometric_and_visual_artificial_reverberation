% Velvet FDN where the stucture is inverted such that the output of
% taken from the mixing matrix instead of the delay lines.
function [rir] = velvet_fdn(er_signal_tdl, delay_times, fs)
fs = double(fs);

% input signal
x = transpose_row_2_col(er_signal_tdl);
x = [x(:,1); zeros(2*fs,1)];

% Define FDN
N = 8;
numFDNInput = 1;
numFDNOutput = 1;
inputGain = ones(N,numFDNInput) / sqrt(N);
outputGain = ones(numFDNInput, N);
direct = zeros(numFDNOutput,numFDNInput); % should be replaced with delay line, source -> listener
fdnDelays = [809, 877, 937, 1049, 1151, 1249, 1373, 1499];
% fdnDelays = transpose_row_2_col(delay_times); TODO: allow addition of scattering matrix delay approx
numberOfStages = 2;
sparsity = 2;
maxShift = 30; 

[feedbackMatrix, revFeedbackMatrix] = constructVelvetFeedbackMatrix(N,numberOfStages,sparsity);
[feedbackMatrix, revFeedbackMatrix] = randomMatrixShift(maxShift, feedbackMatrix, revFeedbackMatrix);

% absorption filters including delay of scattering matrix
[approximation, approximationError] = matrixDelayApproximation(feedbackMatrix);

% use filter-bank instead? Early reflections time should be subtracted from rt60
RT_DC = 0.593; % lowest frequnecy decay in seconds - set from sabine eq
RT_NY = 0.593; % highest frequnecy decay in seconds - set from sabine eq

% Use filterbank instead
[absorption.b,absorption.a] = onePoleAbsorption(RT_DC, RT_NY, fdnDelays + approximation, fs);
zAbsorption = zTF(absorption.b, absorption.a,'isDiagonal', true);

% add transposed conditional

output_transposed = processTransposedFDN(x, fdnDelays, feedbackMatrix, inputGain, outputGain, direct, 'absorptionFilters', zAbsorption);
% lossless_output_transposed = processTransposedFDN(x, fdnDelays, feedbackMatrix, inputGain, outputGain, direct);
% output_transposed_norm = output_transposed / max(x);

rir = output_transposed;

%% Test: script finished
assert(1 == 1);
end