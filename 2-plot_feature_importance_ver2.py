import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# load the data from the text file
data = pd.read_csv('all_sorted_sums_shap.txt', delimiter=':', names=['feature', 'sum'], dtype={'feature': str, 'sum': float})

# extract the feature names and sums as separate arrays
data['feature'] = data['feature'].apply(lambda x: x.replace('Sum of', '').strip().split('[')[0])
data = data.sort_values('sum', ascending=False)[:20]

# create a horizontal bar chart
fig, ax = plt.subplots(figsize=(16, 12))
ax.barh(data['feature'], data['sum'])

# set the title and axis labels
# ax.set_title('Sum of Feature Importance (gini)', size=24)
ax.set_title('Sum of Feature Importance (shap)', size=24)
ax.set_xlabel('Sum', size=16)
for i, (name, value) in enumerate(zip(data['feature'], data['sum'])):
    ax.text(value, i, f'{value:.3f}', ha='right', va='center',
            fontsize=16, color='white', fontweight='bold')

plt.subplots_adjust(left=0.2)
ax.set_xticks(np.arange(0, max(data['sum']) + 0.1, 0.1))
ax.tick_params(labelsize=16)

# put the bar with the highest value on top
ax.invert_yaxis()
plt.show()
