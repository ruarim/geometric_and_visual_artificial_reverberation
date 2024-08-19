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
    
    # Convert the results to a numpy array
    result = np.array(test_results[key], dtype=float)
    
    # Extract the results for each sample type (drums, flute, clap, speech)
    drums = np.array([result[i] for i in range(0, len(result), 4)])
    flute = np.array([result[i] for i in range(1, len(result), 4)])
    clap = np.array([result[i] for i in range(2, len(result), 4)])
    speech = np.array([result[i] for i in range(3, len(result), 4)])
    
    # Store the data in the dictionary for each sample type
    model_results['drums'][key] = drums
    model_results['flute'][key] = flute
    model_results['clap'][key] = clap
    model_results['speech'][key] = speech
    
    # Combine all scores into a single array for overall results
    overall_scores = np.concatenate([drums, flute, clap, speech])
    overall_results[key] = overall_scores

# Function to get box plot properties for color coding the Q2 (median) box fill
def get_box_plot_props(model_name):
    boxprops = dict(color='black')
    medianprops = dict(color='black')

    if model_name in color_map:
        boxprops.update(dict(facecolor=color_map[model_name]))  # Set the fill color for Q2
        medianprops.update(dict(color='black'))  # Keep the median line black

    return boxprops, medianprops

# Helper function to split the model names for stacking text
def stack_text(label):
    return label.replace(' ', '\n')

# Plot individual sample type results
plt.figure(figsize=(18, 10))

for i, sample in enumerate(sample_types):
    plt.subplot(2, 2, i + 1)
    data_to_plot = [model_results[sample][method] for method in model_results[sample].keys()]
    labels = list(model_results[sample].keys())
    stacked_labels = [stack_text(label) for label in labels]  # Stack the text for labels

    for j, method in enumerate(labels):
        boxprops, medianprops = get_box_plot_props(method)
        plt.boxplot(
            [data_to_plot[j]],
            positions=[j + 1],
            widths=0.6,
            boxprops=boxprops,
            medianprops=medianprops,
            patch_artist=True,  # Apply the Q2 fill color
            showmeans=True,
            showfliers=True,
        )
    
    plt.title(f'{sample.capitalize()} Scores')
    plt.xticks(range(1, len(labels) + 1), stacked_labels, ha='center')
    plt.ylim(0, 10)  # Assuming scores range from 0 to 10
    plt.ylabel("Scores")

plt.tight_layout()
plt.show()

# Plot overall results in a separate figure
plt.figure(figsize=(10, 6))
overall_data_to_plot = [overall_results[method] for method in overall_results.keys()]
overall_labels = list(overall_results.keys())
stacked_overall_labels = [stack_text(label) for label in overall_labels]  # Stack text for overall labels

for j, method in enumerate(overall_labels):
    boxprops, medianprops = get_box_plot_props(method)
    plt.boxplot(
        [overall_data_to_plot[j]],
        positions=[j + 1],
        widths=0.6,
        boxprops=boxprops,
        medianprops=medianprops,
        patch_artist=True,  # Apply the Q2 fill color
        showmeans=True,
        showfliers=True,
    )

plt.title('Overall Scores')
plt.xticks(range(1, len(overall_labels) + 1), stacked_overall_labels, ha='center')
plt.ylim(0, 10)  # Assuming scores range from 0 to 10
plt.ylabel("Scores")
plt.tight_layout()
plt.show()
