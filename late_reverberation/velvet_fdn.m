% Velvet FDN where the stucture is inverted such that the output of
% taken from the mixing matrix instead of the delay lines.
function [rir] = velvet_fdn(fs, er_signal_tdl, delay_times, rt60s, rt60_bands)
fs = double(fs);

% input signal
x = transpose_row_2_col(er_signal_tdl);
x = [x(:,1); zeros(2*fs,1)];

% Define FDN
N = size(delay_times, 2);
numFDNInput = 1;
numFDNOutput = 1;
inputGain = ones(N,numFDNInput) / sqrt(N);
outputGain = ones(numFDNInput, N);
direct = zeros(numFDNOutput,numFDNInput); % should be replaced with delay line, source -> listener
delays = double(delay_times);

numberOfStages = 2;
sparsity = 2;
maxShift = 30;

[feedbackMatrix, revFeedbackMatrix] = constructVelvetFeedbackMatrix(N,numberOfStages,sparsity);
[feedbackMatrix, revFeedbackMatrix] = randomMatrixShift(maxShift, feedbackMatrix, revFeedbackMatrix);

% absorption filters including delay of scattering matrix
[approximation, approximationError] = matrixDelayApproximation(feedbackMatrix);

assert(size(rt60_bands, 2) == size(rt60s, 2), 'RT60 bands and times arrays must be equal length.');

% Using filterbank
filterOrder = 32;

% Early reflections time should be subtracted from rt60
T60frequency = transpose_row_2_col(rt60_bands);
targetT60 = transpose_row_2_col(rt60s) * ones(1,N);

% absorption = absorptionFilters(T60frequency, targetT60, filterOrder, delays + approximation, fs);
% absorptionMatrix = polydiag( absorption );

% absorptionFeedbackMatrix = zFIR(matrixConvolution(feedbackMatrix, absorptionMatrix));

% filterCoefficients = absorptionFilters(T60frequency, targetT60, filterOrder, delays, fs).';
% [T60,T60_f] = absorption2T60( filterCoefficients, delays, 2^10, fs );

% % using graphical eq
% zAbsorption = zSOS(absorptionGEQ(rt60s, delays + approximation, fs),'isDiagonal',true);

% Using one-pole filter
[absorption.b,absorption.a] = onePoleAbsorption(targetT60(1), targetT60(end), delays + approximation, fs);
zAbsorption = zTF(absorption.b, absorption.a,'isDiagonal', true);

% TODO: add transposed conditional

% output_transposed = processTransposedFDN(x, delays, absorptionFeedbackMatrix, inputGain, outputGain, direct);
output_transposed = processTransposedFDN(x, delays, feedbackMatrix, inputGain, outputGain, direct, 'absorptionFilters', zAbsorption);
% lossless_output_transposed = processTransposedFDN(x, delays, feedbackMatrix, inputGain, outputGain, direct);
% output_transposed_norm = output_transposed / max(x);

rir = output_transposed;

%% Test: script finished
assert(1 == 1);
end