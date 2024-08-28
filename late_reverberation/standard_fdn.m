function [output] = standard_fdn(fs, input, delay_times, rt60s)
fs = double(fs);

x = transpose_row_2_col(input);
x = x(:,1);


% Define FDN
N = size(delay_times, 2);
numFDNInput = 1;
numFDNOutput = 1;
inputGain = ones(N,numFDNInput);
outputGain = ones(numFDNInput, N);
direct = ones(numFDNOutput,numFDNInput);
delays = double(delay_times);

targetT60 = transpose_row_2_col(rt60s);

[feedbackMatrix, isLossless] = fdnMatrixGallery(N, "Hadamard");

RT_DC = targetT60(1);
RT_NY = targetT60(end);

[absorption.b,absorption.a] = onePoleAbsorption(RT_DC, RT_NY, delays, fs);
zAbsorption = zTF(absorption.b, absorption.a,'isDiagonal', true);

output_transposed = processFDN(x, delays, feedbackMatrix, inputGain, outputGain, direct, 'absorptionFilters', zAbsorption);

output = output_transposed;

end