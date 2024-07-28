import numpy as np
import pandas as pd
import pywt
import matplotlib.pyplot as plt


class WaveletCoherence:
    def __init__(self, subject_A: pd.DataFrame, subject_B: pd.DataFrame, scales, wavelet_type='cmor'):
        self.average_coherence = None
        self.subject_A = subject_A
        self.subject_B = subject_B
        self.scales = scales
        self.wavelet_type = wavelet_type
        self.n_areas = self.subject_A.shape[1]
        self.coherence_df = None
        self.brain_areas = None
        self.time = None




    def set_wavelet_coherence(self, wavelet='cmor', scales=np.arange(1, 128), sampling_period=1):
        """
        Calculate and plot wavelet coherence heat maps between corresponding brain areas of two brains.

        :param table1: DataFrame with the first brain's measurements (first column is Time, other columns are brain areas)
        :param table2: DataFrame with the second brain's measurements (same structure as table1)
        :param wavelet: Wavelet to use for the wavelet transform (default is 'cmor')
        :param scales: Scales to use for the wavelet transform (default is np.arange(1, 128))
        :param sampling_period: Sampling period of the measurements (default is 1)
        """
        # Ensure both tables have the same structure
        assert self.subject_A.columns.equals(self.subject_B.columns), "Tables must have the same columns"

        # Extract the time column and brain areas (exclude the Time column)
        self.time = self.subject_A.iloc[:, 0].values
        self.brain_areas = self.subject_A.columns[1:]

        # Initialize a dictionary to hold coherence values for each brain area
        coherence_dict = {area: [] for area in self.brain_areas}

        # Calculate wavelet coherence for each brain area
        for area in self.brain_areas:
            signal1 = self.subject_A[area].values
            signal2 = self.subject_B[area].values

            # Compute the continuous wavelet transform for both signals
            coeffs1, freqs1 = pywt.cwt(signal1, scales, wavelet, sampling_period)
            coeffs2, freqs2 = pywt.cwt(signal2, scales, wavelet, sampling_period)

            # Compute the cross wavelet transform
            cross_wavelet = coeffs1 * np.conj(coeffs2)

            # Compute wavelet coherence
            wavelet_coherence = np.abs(cross_wavelet) ** 2 / (np.abs(coeffs1) ** 2 * np.abs(coeffs2) ** 2)

            # Append coherence values (mean over scales) for each time point
            mean_coherence = np.mean(wavelet_coherence, axis=0)
            coherence_dict[area] = mean_coherence

        # Create a DataFrame from the coherence dictionary
        self.coherence_df = pd.DataFrame(coherence_dict, index=self.time)


    def get_coherence_heatmap(self, path=None):
        if not self.coherence_df:
            raise ValueError('No coherence')

        # Plot the heat map
        plt.figure(figsize=(12, 8))
        plt.imshow(self.coherence_df.T, aspect='auto', cmap='viridis', extent=(self.time.min(), self.time.max(), 0,len(self.brain_areas)))
        plt.colorbar(label='Coherence')
        plt.yticks(ticks=np.arange(len(self.brain_areas)), labels=self.brain_areas)
        plt.xlabel('Time')
        plt.ylabel('Brain Areas')
        plt.title('Wavelet Coherence Heat Map')
        if path is not None:
            plt.savefig(path)
        plt.show()
