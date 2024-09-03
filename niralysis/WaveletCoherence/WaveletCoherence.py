import numpy as np
import pandas as pd
import pywt
import matplotlib.pyplot as plt
import os


from niralysis.SharedReality.consts import CandidateChoicesAndScoreXlsx


class WaveletCoherence:
    def __init__(self, subject_A: pd.DataFrame, subject_B: pd.DataFrame, path_to_save_maps=None,
                 path_to_candidate_choices=None, wavelet_type='cmor', scales=np.arange(1, 128)):
        self.average_coherence = None
        self.subject_A = subject_A
        self.subject_B = subject_B
        self.wavelet_type = wavelet_type
        self.n_areas = self.subject_A.shape[1]
        self.coherence_df = []
        self.brain_areas = None
        self.time = None
        self.path_to_save_maps = path_to_save_maps
        self.candidate_choices = pd.read_excel(path_to_candidate_choices) if path_to_candidate_choices else None
        self.plt = None
        self.sampling_rate = 0.02
        self.scales = np.arange(600, 1700)



    """
     creates one heat map, x- time, y - brain area mean value of all scales 
    """
    def set_wavelet_coherence_mean_wavelet(self, wavelet='cmor', sampling_period=0.5):
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
            coeffs1, freqs1 = pywt.cwt(signal1, self.scales, wavelet, sampling_period)
            coeffs2, freqs2 = pywt.cwt(signal2, self.scales, wavelet, sampling_period)

            # Compute the cross wavelet transform
            cross_wavelet = coeffs1 * np.conj(coeffs2)

            # Compute wavelet coherence
            wavelet_coherence = np.abs(cross_wavelet) ** 2 / (np.abs(coeffs1) ** 2 * np.abs(coeffs2) ** 2)

            # Append coherence values (mean over scales) for each time point
            mean_coherence = np.mean(wavelet_coherence, axis=0)
            coherence_dict[area] = mean_coherence

        # Create a DataFrame from the coherence dictionary
        self.coherence_df = pd.DataFrame(coherence_dict, index=self.time)


    def get_coherence_heatmap_x_time_y_areas(self, name=None, show=True):
        if self.coherence_df.empty:
            raise ValueError('No coherence')

        # Plot the heat map
        plt.figure(figsize=(12, 8))
        plt.imshow(self.coherence_df.T, aspect='auto', cmap='viridis',
                   extent=(self.time.min(), self.time.max(), 0, len(self.brain_areas)))
        plt.colorbar(label='Coherence')
        plt.yticks(ticks=np.arange(len(self.brain_areas)), labels=self.brain_areas)
        plt.xlabel('Time')
        plt.ylabel('Brain Areas')
        plt.title('Wavelet Coherence Heat Map')
        if name is not None and self.path_to_save_maps is not None:
            plt.savefig(os.path.join(self.path_to_save_maps, f"{name}.jpg"))
        if show:
            plt.show()

    def get_map_name(self, date: str, event: str, watch: int):
        if self.candidate_choices is None:
            return f"{date}-{event}-{watch}"
        choice = self.candidate_choices.loc[self.candidate_choices[CandidateChoicesAndScoreXlsx.CANDIDATE_NAME] == event, CandidateChoicesAndScoreXlsx.CHOICES].values[0]
        return f"{date}-{choice}-{watch}"

    """
     creates an image with multiple heatmaps, a heat map to each brain area, x time, y freq
    """
    def set_wavelet_coherence_for_each_area(self, wavelet='cmor', scales=None):
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
        if self.subject_A.shape != self.subject_B.shape or list(self.subject_A.columns) != list(self.subject_B.columns):
            raise ValueError("The two data tables must have the same shape and column names.")

        self.brain_areas = self.subject_A.shape[1]
        self.time = self.subject_A.shape[0]
        if scales:
            self.scales = scales
            self.coherence_df = []
        for i, area in enumerate(self.subject_A.columns):
            # Extract the time series for the current brain area
            x = self.subject_A[area].values
            y = self.subject_B[area].values

            # Compute wavelet coherence
            coeffs_x, _ = pywt.cwt(x, self.scales, wavelet)
            coeffs_y, _ = pywt.cwt(y, self.scales, wavelet)

            Sxx = np.abs(coeffs_x) ** 2
            Syy = np.abs(coeffs_y) ** 2
            Sxy = np.conj(coeffs_x) * coeffs_y
            self.coherence_df.append(np.abs(Sxy) ** 2 / (Sxx * Syy))

    def plot_wavelet_coherence_heatmaps(self, name=None, show=True, wavelet='cmor2.5-0.5'):
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
            print(f"starting plot_wavelet_coherence_heatmaps for {name}")
            # Ensure that both data frames have the same shape and columns
            if self.subject_A.shape != self.subject_B.shape or list( self.subject_A.columns) != list( self.subject_B.columns):
                raise ValueError("The two data tables must have the same shape and column names.")

            n_areas = self.subject_A.shape[1] - 1
            time_points = self.subject_A.shape[0]

            # Create a figure with subplots
            # Determine the number of rows and columns for the subplots
            max_maps_per_column = 3
            n_columns = int(np.ceil(n_areas / max_maps_per_column))
            n_rows = min(max_maps_per_column, n_areas)

            # Create a figure with subplots
            fig, axes = plt.subplots(n_rows, n_columns, figsize=(50, 5 * n_columns))
            axes = axes.flatten() if n_columns > 1 else [axes]
            for i, area in enumerate(self.subject_A.columns[1:]):
                print(f"creating {name} {area}, {i} out of {n_areas}")
                # Extract the time series for the current brain area
                try:
                    y1 = self.subject_A[area].values
                    y2 = self.subject_B[area].values
                    if None in y1 or None in y2:
                        continue

                    # Compute wavelet coherence
                    coeffs_x, freqs_1  = pywt.cwt(y1, self.scales, wavelet=wavelet, sampling_period=0.02)
                    print(f"done coeffs_x")
                    coeffs_y, _ = pywt.cwt(y2, self.scales, wavelet=wavelet, sampling_period=0.02)
                    print(f"done coeffs_y")

                    coherence = np.abs(coeffs_x * np.conj(coeffs_y))  # 2D coherence matrix
                    print(f"done coherence")

                    # Plot the coherence heatmap
                    print(f"plotting {area}")
                    ax = axes[i]
                    im = ax.imshow(coherence, extent=[0, time_points, self.scales[-1], self.scales[0]], aspect='auto', cmap='jet')
                    ax.set_title(f'Wavelet Coherence - {area}')
                    ax.set_xlabel('Time')
                    ax.set_ylabel('Frequency (Hz)')
                    fig.colorbar(im, ax=ax, orientation='vertical', label='Coherence')
                except Exception as e:
                    print(f"failed to create heat map for {name} area {area}. Error: {e}")
                    pass
                # Hide unused subplots
            for j in range(len(self.subject_A.columns), len(axes)):
                fig.delaxes(axes[j])

            # Adjust layout to prevent overlap
            plt.tight_layout()
            self.plt = plt

            if name is not None and self.path_to_save_maps is not None:
                plt.savefig(os.path.join(self.path_to_save_maps, f"{name}.jpg"))
                print(f"saved plot fig for {name}")

            if show:
                plt.show()
