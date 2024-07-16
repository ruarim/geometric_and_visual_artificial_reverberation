% include fndToolbox dependancy
addpath(genpath('fdnToolbox'))

% SAMPLE
% [x, fs] = audioread('synth_dry.m4a');
% x = [x(:,1); zeros(2*fs,1)];

% UNIT
fs = 44100;
x = zeros(2*fs,1);
x(1) = 1.0;

% Define FDN
N = 8;
numInput = 1;
numOutput = 2;
inputGain = ones(N,numInput);
outputGain = ones(numInput, N);
direct = zeros(numOutput,numInput);
delays = [809, 877, 937, 1049, 1151, 1249, 1373, 1499];

% numberOfStages = 2;
% sparsity = 3;
% maxShift = 30;

[feedbackMatrix, isLossless] = fdnMatrixGallery(N, "Hadamard");
% [feedbackMatrix, revFeedbackMatrix] = randomMatrixShift(maxShift, feedbackMatrix, revFeedbackMatrix );

% absorption filters including delay of scattering matrix
% [approximation,approximationError] = matrixDelayApproximation(feedbackMatrix);

RT_DC = 2; % seconds
RT_NY = 0.5; % seconds

[absorption.b,absorption.a] = onePoleAbsorption(RT_DC, RT_NY, delays, fs);
zAbsorption = zTF(absorption.b, absorption.a,'isDiagonal', true);

% compute impulse response and poles/zeros and reverberation time
output = processFDN(x, delays, feedbackMatrix, inputGain, outputGain, direct, 'absorptionFilters', zAbsorption);
lossless_output = processFDN(x, delays, feedbackMatrix, inputGain, outputGain, direct);

output_transposed = processTransposedFDN(x, delays, feedbackMatrix, inputGain, outputGain, direct, 'absorptionFilters', zAbsorption);
lossless_output_transposed = processTransposedFDN(x, delays, feedbackMatrix, inputGain, outputGain, direct);

close all;
% soundsc(x,fs);
% soundsc(output,fs);
figure
hold on;
plot(lossless_output)
plot(output)
hold off;

soundsc(output_transposed,fs);
figure
hold on;
plot(lossless_output_transposed)
plot(output_transposed)
hold off;

audiowrite("Standard_FDN.wav", output, fs);
audiowrite("Standard_FDN_Lossless.wav", lossless_output, fs);

audiowrite("Standard_FDN_Transposed.wav", output_transposed, fs);
audiowrite("Standard_FDN_Transposed_Lossless.wav", lossless_output_transposed, fs);

%% Test: script finished
assert(1 == 1);
