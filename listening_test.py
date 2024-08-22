import numpy as np
from utils.file import read_csv
from matplotlib import pyplot as plt

# Read the test results from the CSV file
test_results = read_csv('_data/listening_test_results.csv')

# Define the sample types
sample_types = ['drums', 'flute', 'clap', 'speech']

# Initialize dictionaries to store the results
model_results = {sample: {} for sample in sample_types}
overall_results = {}

# Define color mapping for ISMFDN models' Q2 (median) box fill (avoiding blue)
color_map = {
    'ISMFDN One-Pole N=16': 'orange',
    'ISMFDN FIR N=16': 'green',
    'ISMFDN One-Pole N=24': 'purple',  # Replacing blue with purple
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
    
    print('Means')
    print(key, 'drums', np.mean(drums))
    print(key, 'flute', np.mean(flute))
    print(key, 'clap', np.mean(clap))
    print(key, 'speech', np.mean(speech))
    
    model_results['drums'][key] = drums
    model_results['flute'][key] = flute
    model_results['clap'][key] = clap
    model_results['speech'][key] = speech
    
    overall_scores = np.concatenate([drums, flute, clap, speech])
    overall_results[key] = overall_scores

def get_box_plot_props(model_name):
    boxprops = dict(color='black')
    medianprops = dict(color='black')

    if model_name in color_map:
        boxprops.update(dict(facecolor=color_map[model_name]))
        medianprops.update(dict(color='black'))  

    return boxprops, medianprops

def stack_text(label):
    return label.replace(' ', '\n')

plt.figure(figsize=(18, 10))

for i, sample in enumerate(sample_types):
    plt.subplot(2, 2, i + 1)
    data_to_plot = [model_results[sample][method] for method in model_results[sample].keys()]
    labels = list(model_results[sample].keys())
    stacked_labels = [stack_text(label) for label in labels]  

    for j, method in enumerate(labels):
        boxprops, medianprops = get_box_plot_props(method)
        plt.boxplot(
            [data_to_plot[j]],
            positions=[j + 1],
            widths=0.6,
            boxprops=boxprops,
            medianprops=medianprops,
            patch_artist=True,
            showmeans=True,
            showfliers=True,
        )
    
    plt.title(f'{sample.capitalize()} Scores')
    plt.xticks(range(1, len(labels) + 1), stacked_labels, ha='center')
    plt.ylim(0, 10)
    plt.ylabel("Scores")

plt.tight_layout()
plt.show()

plt.figure(figsize=(8, 4))
overall_data_to_plot = [overall_results[method] for method in overall_results.keys()]
overall_labels = list(overall_results.keys())
stacked_overall_labels = [stack_text(label) for label in overall_labels]

for j, method in enumerate(overall_labels):
    boxprops, medianprops = get_box_plot_props(method)
    plt.boxplot(
        [overall_data_to_plot[j]],
        positions=[j + 1],
        widths=0.6,
        boxprops=boxprops,
        medianprops=medianprops,
        patch_artist=True,
        showmeans=True,
        showfliers=True,
    )

plt.title('Overall Listening Test Scores')
plt.xticks(range(1, len(overall_labels) + 1), stacked_overall_labels, ha='center')
plt.ylim(0, 10)
plt.ylabel("Scores")
plt.tight_layout()
plt.show()
