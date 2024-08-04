% Velvet FDN where the stucture is inverted such that the output of
% taken from the mixing matrix instead of the delay lines.
function [rir] = velvet_fdn_one_pole(fs, er_signal, delay_times, rt60s, rt60_bands, crossover_frequency)
fs = double(fs);

% input signal
x = transpose_row_2_col(er_signal);
x = x(:,1);

% Define FDN
N = size(delay_times, 2);
numFDNInput = 1;
numFDNOutput = 1;
inputGain = ones(N,numFDNInput) / sqrt(N);
outputGain = ones(numFDNInput, N);
direct = zeros(numFDNOutput,numFDNInput);
delays = double(delay_times);

numberOfStages = 2;
sparsity = 2;
maxShift = 30;

[feedbackMatrix, revFeedbackMatrix] = constructCascadedParaunitaryMatrix( N, numberOfStages, 'sparsity', sparsity, 'matrixType', 'random');
[feedbackMatrix, revFeedbackMatrix] = randomMatrixShift(maxShift, feedbackMatrix, revFeedbackMatrix);

% absorption filters including delay of scattering matrix
[approximation, approximationError] = matrixDelayApproximation(feedbackMatrix);

assert(size(rt60_bands, 2) == size(rt60s, 2), 'RT60 bands and times arrays must be equal length.');

targetT60 = transpose_row_2_col(rt60s);

switch 'firstOrder'
    case 'onePole'
        % Using one-pole filter
        [absorption.b,absorption.a] = onePoleAbsorption(targetT60(1), targetT60(end), delays + approximation, fs);
    case 'firstOrder'
        [absorption.b,absorption.a] = firstOrderAbsorption(targetT60(1), targetT60(end), crossover_frequency, delays + approximation, fs);
end


zAbsorption = zTF(absorption.b, absorption.a,'isDiagonal', true);

output_transposed = processTransposedFDN(x, delays, feedbackMatrix, inputGain, outputGain, direct, 'absorptionFilters', zAbsorption);
% lossless_output_transposed = processTransposedFDN(x, delays, feedbackMatrix, inputGain, outputGain, direct);

rir = output_transposed;

end