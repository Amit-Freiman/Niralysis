import numpy as np
import pandas as pd
import pywt
import matplotlib.pyplot as plt


def plot_wavelet_coherence_heatmaps(data1, data2, scales, wavelet='cmor'):
    """
    Generate wavelet coherence heatmaps for each brain area.

    Parameters:
    - data1: Pandas DataFrame. First set of brain activity measurements.
    - data2: Pandas DataFrame. Second set of brain activity measurements.
    - scales: array_like. Scales to use for the wavelet transform.
    - wavelet: str. The wavelet to use for the CWT (default is 'cmor').

    Returns:
    - None. The function will display the heatmaps.
    """

    # Ensure that both data frames have the same shape and columns
    if data1.shape != data2.shape or list(data1.columns) != list(data2.columns):
        raise ValueError("The two data tables must have the same shape and column names.")

    n_areas = data1.shape[1]
    time_points = data1.shape[0]
    coherences = []
    for i, area in enumerate(data1.columns):
        # Extract the time series for the current brain area
        x = data1[area].values
        y = data2[area].values

        # Compute wavelet coherence
        coeffs_x, _ = pywt.cwt(x, scales, wavelet)
        coeffs_y, _ = pywt.cwt(y, scales, wavelet)

        Sxx = np.abs(coeffs_x) ** 2
        Syy = np.abs(coeffs_y) ** 2
        Sxy = np.conj(coeffs_x) * coeffs_y
        coherences.append(np.abs(Sxy) ** 2 / (Sxx * Syy))

def plot_wavelet_coherence_heatmaps(coherences, areas, time_points, scales):
    n_areas = len(areas)
    # Create a figure with subplots
    fig, axes = plt.subplots(n_areas, 1, figsize=(10, 5 * n_areas))

    # If there's only one brain area, axes won't be a list
    if n_areas == 1:
        axes = [axes]

    for i, area in enumerate(areas):
        ax = axes[i]
        im = ax.imshow(coherences[i], extent=[0, time_points, scales[-1], scales[0]], cmap='jet', aspect='auto', vmax=1,
                       vmin=0)
        ax.set_title(f'Wavelet Coherence - {area}')
        ax.set_xlabel('Time')
        ax.set_ylabel('Frequency (Scale)')
        fig.colorbar(im, ax=ax, orientation='vertical')

    # Adjust layout to prevent overlap
    plt.tight_layout()
    plt.show()