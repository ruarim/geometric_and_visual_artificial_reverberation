import numpy as np
from utils.file import read_csv
from matplotlib import pyplot as plt
from scipy.stats import t

# Read the test results from the CSV file
test_results = read_csv('_data/listening_test_results.csv')

# Define the sample types
sample_types = ['drums', 'flute', 'clap', 'speech']

# Initialize dictionaries to store the results
model_results = {sample: {} for sample in sample_types}
overall_results = {}

# color mapping for ISMFDN models
color_map = {
    'ISMFDN One-Pole N=16': 'orange',
    'ISMFDN FIR N=16': 'green',
    'ISMFDN One-Pole N=24': 'purple',
    'ISMFDN FIR N=24': 'red'
}

# Process the test results
for key in test_results.keys():
    if key == 'Sample Type':
        continue
    
    result = np.array(test_results[key], dtype=float)
    
    drums = np.array([result[i] for i in range(0, len(result), 4)])
    flute = np.array([result[i] for i in range(1, len(result), 4)])
    clap = np.array([result[i] for i in range(2, len(result), 4)])
    speech = np.array([result[i] for i in range(3, len(result), 4)])
    
    model_results['drums'][key] = drums
    model_results['flute'][key] = flute
    model_results['clap'][key] = clap
    model_results['speech'][key] = speech
    
    overall_scores = np.concatenate([drums, flute, clap, speech])
    overall_results[key] = overall_scores

def calculate_confidence_interval(data, confidence=0.85):
    n = len(data)
    mean = np.mean(data)
    sem = np.std(data, ddof=1) / np.sqrt(n)
    h = sem * t.ppf((1 + confidence) / 2., n-1)
    return mean, h

def stack_text(label):
    return label.replace(' ', '\n')

plt.figure(figsize=(18, 10))

for i, sample in enumerate(sample_types):
    plt.subplot(2, 2, i + 1)
    data_to_plot = [model_results[sample][method] for method in model_results[sample].keys()]
    labels = list(model_results[sample].keys())
    stacked_labels = [stack_text(label) for label in labels]

    means = []
    confidence_intervals = []

    for data in data_to_plot:
        mean, ci = calculate_confidence_interval(data)
        means.append(mean)
        confidence_intervals.append(ci)

    colors = [color_map.get(label, 'gray') for label in labels]
    
    plt.bar(range(1, len(labels) + 1), means, yerr=confidence_intervals, color=colors, capsize=5, width=0.6)

    plt.title(f'{sample.capitalize()} Scores')
    plt.xticks(range(1, len(labels) + 1), stacked_labels, ha='center')
    plt.ylim(1, 9)
    plt.ylabel("Scores")

plt.tight_layout()
plt.show()

plt.figure(figsize=(8, 4))
overall_data_to_plot = [overall_results[method] for method in overall_results.keys()]
overall_labels = list(overall_results.keys())
stacked_overall_labels = [stack_text(label) for label in overall_labels]

overall_means = []
overall_confidence_intervals = []

for data in overall_data_to_plot:
    mean, ci = calculate_confidence_interval(data)
    overall_means.append(mean)
    overall_confidence_intervals.append(ci)

overall_colors = [color_map.get(label, 'gray') for label in overall_labels]

plt.bar(range(1, len(overall_labels) + 1), overall_means, yerr=overall_confidence_intervals, color=overall_colors, capsize=5, width=0.6)

plt.title('Overall Listening Test Scores')
plt.xticks(range(1, len(overall_labels) + 1), stacked_overall_labels, ha='center')
plt.ylim(1, 9)
plt.ylabel("Scores")
plt.tight_layout()
plt.show()
