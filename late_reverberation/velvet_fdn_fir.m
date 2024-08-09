% Velvet FDN where the stucture is inverted such that the output of
% taken from the mixing matrix instead of the delay lines.
function [rir] = velvet_fdn_fir(fs, er_signal, delay_times, rt60s, rt60_bands, matrix_type, filter_order, nyquist_decay_type)
fs = double(fs);

% input signal
x = transpose_row_2_col(er_signal);
x = x(:,1); % TODO: Pass signal length

% Define FDN
N = size(delay_times, 2);
numFDNInput = size(er_signal, 1);
numFDNOutput = 1;
inputGain = ones(N,numFDNInput);
outputGain = ones(numFDNInput, N);
direct = zeros(numFDNOutput,numFDNInput);
delays = double(delay_times);

numberOfStages = 2;
sparsity = 2;
maxShift = 30;

[feedbackMatrix, revFeedbackMatrix] = constructCascadedParaunitaryMatrix( N, numberOfStages, 'sparsity', sparsity, 'matrixType', matrix_type);
[feedbackMatrix, revFeedbackMatrix] = randomMatrixShift(maxShift, feedbackMatrix, revFeedbackMatrix);

% absorption filters including delay of scattering matrix
[approximation, approximationError] = matrixDelayApproximation(feedbackMatrix);

assert(size(rt60_bands, 2) == size(rt60s, 2), 'RT60 bands and times arrays must be equal length.');

rt60_bands = double(transpose_row_2_col(rt60_bands));
T60frequency = [0; rt60_bands; fs/2];
targetT60 = transpose_row_2_col(rt60s) * ones(1,N);

switch nyquist_decay_type
    case 'nyquist_zero'
        nyquist_rt60 = double(0)*ones(1,N);
    case 'nyquist_RT60'
        nyquist_rt60 = targetT60(end,:);
end

% add dc, nyquist and calculated rt60s
targetT60 = [targetT60(1,:); targetT60; nyquist_rt60];

% Using filterbank
filterOrder = double(filter_order);

absorption = absorptionFilters(T60frequency, targetT60, filterOrder, delays + approximation, fs);
absorptionMatrix = polydiag( absorption );
absorptionFeedbackMatrix = zFIR(matrixConvolution(feedbackMatrix, absorptionMatrix));

output_transposed = processTransposedFDN(x, delays, absorptionFeedbackMatrix, inputGain, outputGain, direct);
% lossless_output_transposed = processTransposedFDN(x, delays, feedbackMatrix, inputGain, outputGain, direct);

rir = output_transposed;

end