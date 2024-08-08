# Author : Michael O'Donnell
# 8/8/2024
# WIP

import ROOT
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import colors

def create_histogram(name, title, x_bins, x_min, x_max, y_bins, y_min, y_max):
    """Create a 2D histogram."""
    return ROOT.TH2F(name, title, x_bins, x_min, x_max, y_bins, y_min, y_max)

def fill_histogram(hist, tree, ch1, ch2, max_events):
    """Fill the histogram with data from the tree."""
    cnt = 0
    for entry in tree:
        if cnt >= max_events:
            break
        cnt += 1
        hist.Fill(entry.FERS_Board1_energyHG[ch1], entry.FERS_Board1_energyHG[ch2])

def extract_points_from_hist(hist):
    """Extract points and values from a histogram."""
    points = []
    for x_bin in range(1, hist.GetNbinsX() + 1):
        for y_bin in range(1, hist.GetNbinsY() + 1):
            x = hist.GetXaxis().GetBinCenter(x_bin)
            y = hist.GetYaxis().GetBinCenter(y_bin)
            z = hist.GetBinContent(x_bin, y_bin)
            if z > 0:  # Only consider non-zero values
                points.append((x, y, z))
    return points

def calculate_correlations(points1, points2):
    """Calculate the correlation between points from two histograms."""
    points1 = np.array(points1)
    points2 = np.array(points2)
    
    dict1 = {(x, y): z for x, y, z in points1}
    dict2 = {(x, y): z for x, y, z in points2}
    
    common_points = set(dict1.keys()).intersection(set(dict2.keys()))
    
    if len(common_points) < 2:
        return np.nan
    
    values1 = np.array([dict1[point] for point in common_points])
    values2 = np.array([dict2[point] for point in common_points])
    
    if np.std(values1) == 0 or np.std(values2) == 0:
        return np.nan
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        correlation = np.corrcoef(values1, values2)[0, 1]
    
    return correlation

def plot_scatter(points1, points2, ch1, ch2, ch3, ch4, pdf_pages):
    """Plot a scatter plot of points from two histograms."""
    x1, y1 = zip(*[(x, y) for x, y, z in points1])
    x2, y2 = zip(*[(x, y) for x, y, z in points2])
    
    plt.figure(figsize=(10, 8))
    plt.scatter(x1, y1, label=f'Channel Pair ({ch1}, {ch2})', alpha=0.5)
    plt.scatter(x2, y2, label=f'Channel Pair ({ch3}, {ch4})', alpha=0.5, marker='x')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title(f'Scatter Plot of Channels ({ch1}, {ch2}) vs ({ch3}, {ch4})')
    plt.legend()
    plt.grid(True)
    
    pdf_pages.savefig()
    plt.close()

def plot_correlation_heatmap(correlations, num_channels, pdf_pages, channel_labels="Ch {num_channels}", title_prefix="Correlation Heatmap", cmap='coolwarm', figsize=(10, 8), annot=True, fmt=".2f", vmin=-1, vmax=1, cbar_shrink=0.8):
    """
    Plots and saves correlation heatmaps to a PDF.

    Parameters:
    - correlations (dict): Dictionary of correlation values with keys as tuples of channel pairs.
    - num_channels (int): Number of channels to consider in the heatmap.
    - pdf_pages (PdfPages): PDF file handle for saving heatmaps.
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
        # Prepare an empty matrix for correlation values
        corr_matrix = np.full((num_channels, num_channels), np.nan)

        # Fill the matrix with correlation values
        for (ch1, ch2, ch3, ch4), corr in correlations.items():
            corr_matrix[ch1, ch3] = corr

        # Plot the heatmap
        plt.figure(figsize=figsize)
        sns.heatmap(corr_matrix, cmap=cmap, annot=annot, fmt=fmt, vmin=vmin, vmax=vmax, square=True, cbar_kws={'shrink': cbar_shrink})
        
        # Set plot title, labels, and ticks
        plt.title(title_prefix)
        plt.xlabel(f"Channel X")
        plt.ylabel(f"Channel Y")
        plt.xticks(ticks=np.arange(num_channels) + 0.5, labels=channel_labels if channel_labels else range(num_channels), rotation=90)
        plt.yticks(ticks=np.arange(num_channels) + 0.5, labels=channel_labels if channel_labels else range(num_channels), rotation=0)

        # Save the plot to the PDF
        pdf_pages.savefig()
        plt.close()

        print(f"Heatmap successfully saved to {pdf_pages}")

    except Exception as e:
        print(f"An error occurred while generating the heatmap: {e}")

def save_correlation_results(correlations, output_file):
    """Save correlation results to a text file."""
    with open(output_file, 'w') as f:
        for (ch1, ch2, ch3, ch4), corr in correlations.items():
            f.write(f"Channels ({ch1}, {ch2}) vs ({ch3}, {ch4}): Correlation: {corr:.3f}\n")

def process_root_file(input_file, output_file, output_pdf, max_events, num_channels):
    """Process the ROOT file to create and save 2D histograms and perform correlation analysis."""
    # Open the ROOT file
    file = ROOT.TFile(input_file, "READ")

    # Get the tree from the file
    tree = file.Get("EventTree")

    # Create a new ROOT file to save histograms
    output_root_file = ROOT.TFile(output_file, "RECREATE")

    # Create a canvas to draw histograms
    canvas = ROOT.TCanvas("canvas", "Canvas", 800, 600)

    histograms = []
    points_by_hist = {}

    # Loop over all combinations of channels
    for ch1 in range(num_channels):
        for ch2 in range(ch1 + 1, num_channels):
            hist_name = f"hist2D_ch{ch1}_ch{ch2}"
            hist_title = f"FERS Board 1;Ch{ch1};Ch{ch2}"
            hist2D = create_histogram(hist_name, hist_title, 100, 0, 1000, 100, 0, 1000)
            
            fill_histogram(hist2D, tree, ch1, ch2, max_events)
            
            hist2D.Write()
            histograms.append(hist2D)

            # Extract points from histogram
            points_by_hist[(ch1, ch2)] = extract_points_from_hist(hist2D)

    # Save histograms to PDF
    with PdfPages(output_pdf) as pdf_pages:
        canvas.Print(f"{output_pdf}[")
        canvas.Divide(4, 3)  # Divide canvas into 4x3 grids
        hist_count = 0

        for hist in histograms:
            canvas.cd(hist_count % 12 + 1)
            hist.Draw("COLZ")
            hist_count += 1

            # If we have filled the page, create a new one
            if hist_count % 12 == 0:
                canvas.Print(output_pdf)
                canvas.Clear()
                canvas.Divide(4, 3)

        # Print remaining histograms if any
        if hist_count % 12 != 0:
            canvas.Print(output_pdf)

        # Finalize the PDF
        canvas.Print(f"{output_pdf}]")

        # Perform correlation analysis
        correlations = {}
        for (ch1, ch2), points1 in points_by_hist.items():
            for (ch3, ch4), points2 in points_by_hist.items():
                if (ch1, ch2) != (ch3, ch4):
                    corr = calculate_correlations(points1, points2)
                    correlations[(ch1, ch2, ch3, ch4)] = corr

                    # Plot scatter plots for visual representation
                    plot_scatter(points1, points2, ch1, ch2, ch3, ch4, pdf_pages)

        # Generate and save the heatmap
        plot_correlation_heatmap(correlations, num_channels, pdf_pages)

    # Save correlation results to a text file
    save_correlation_results(correlations, "correlation_results.txt")

    # Close the ROOT file
    output_root_file.Close()

# Parameters
input_file = "/home/michaelod/CaloXWork/datafiles/run742_V22000.root"
output_file = "output_histograms.root"
output_pdf = "output_histograms.pdf"
max_events = 100
num_channels = 64

# Process the ROOT file
process_root_file(input_file, output_file, output_pdf, max_events, num_channels)

#end
