# Author : Michael O'Donnell
# 8/8/2024

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

def plot_correlation_heatmap(correlations, pdf_pages, channel_labels=None, title_prefix="Correlation Heatmap", cmap='coolwarm', figsize=(10, 8), annot=True, fmt=".2f", vmin=-1, vmax=1, cbar_shrink=0.8):
    """
    Plots and saves correlation heatmaps to a PDF.

    Parameters:
    - correlations (list of np.ndarray): List of correlation matrices to plot.
    - pdf_pages (str): Path to the output PDF file where heatmaps will be saved.
    - channel_labels (list of str): Optional list of labels for channels. Defaults to numerical labels.
    - title_prefix (str): Prefix for the titles of the heatmaps.
    - cmap (str): Colormap for the heatmap. Defaults to 'coolwarm'.
    - figsize (tuple): Size of the figure for each heatmap.
    - annot (bool): Whether to annotate each cell with the correlation value.
    - fmt (str): String format for annotating the heatmap.
    - vmin (float): Minimum value for the colormap scale.
    - vmax (float): Maximum value for the colormap scale.
    - cbar_shrink (float): Factor by which to shrink the colorbar.

    Returns:
    - None
    """
    try:
        # Open a PDF file to save the plots
        with PdfPages(pdf_pages) as pdf:
            for i, corr_matrix in enumerate(correlations):
                # Validate correlation matrix dimensions
                if corr_matrix.ndim != 2 or corr_matrix.shape[0] != corr_matrix.shape[1]:
                    raise ValueError(f"Correlation matrix at index {i} is not square.")

                num_channels = corr_matrix.shape[0]

                # Default to numerical labels if none are provided
                if channel_labels is None:
                    channel_labels = range(num_channels)
                elif len(channel_labels) != num_channels:
                    raise ValueError(f"Number of channel labels ({len(channel_labels)}) does not match the size of the correlation matrix ({num_channels}).")

                # Create the figure and plot the heatmap
                plt.figure(figsize=figsize)
                sns.heatmap(corr_matrix, cmap=cmap, annot=annot, fmt=fmt, vmin=vmin, vmax=vmax, square=True, cbar_kws={'shrink': cbar_shrink})
                
                # Set plot title, labels, and ticks
                plt.title(f"{title_prefix} {i+1}")
                plt.xlabel("Channel X")
                plt.ylabel("Channel Y")
                plt.xticks(ticks=np.arange(num_channels) + 0.5, labels=channel_labels, rotation=90)
                plt.yticks(ticks=np.arange(num_channels) + 0.5, labels=channel_labels, rotation=0)

                # Save the current plot to the PDF
                pdf.savefig()
                plt.close()

        print(f"Heatmaps successfully saved to {pdf_pages}")

    except Exception as e:
        print(f"An error occurred while generating heatmaps: {e}")


# Example correlation matrices
corr1 = np.random.rand(10, 10)
corr2 = np.random.rand(10, 10)

# Example usage of the function
plot_correlation_heatmap([corr1, corr2], "correlation_heatmaps.pdf", channel_labels=[f"Ch{i}" for i in range(10)])


#end
