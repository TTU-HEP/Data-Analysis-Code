#Michael O'Donnell
#8/8/2024
#WIP

import numpy as np
import ROOT
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr
import seaborn as sns
from itertools import combinations
from sklearn.decomposition import PCA
from collections import defaultdict

# Configuration variables
NUM_CHANNELS = 8  # Number of channels to analyze
MAX_EVENTS_PER_CHANNEL = 10  # Maximum number of events per channel

def load_root_data(root_file, tree_name, num_channels, max_events):
    hist1D_dict = {}
    hist2D_dict = {}

    # Open the ROOT file and get the TTree
    file = ROOT.TFile(root_file, "READ")
    tree = file.Get(tree_name)

    # Check if tree is valid
    if not tree:
        raise ValueError(f"Tree {tree_name} not found in file {root_file}")

    # Create histograms
    for ch in range(num_channels):
        # Create 1D histogram for each channel
        hist1D_dict[ch] = ROOT.TH1F(f"hist1D_{ch}", f"FERS Board 1 Channel {ch};Energy HG;Counts", 100, 0, 1000)
        
        # Create 2D histograms for each pair of channels
        for ch2 in range(ch + 1, num_channels):
            hist2D_dict[(ch, ch2)] = ROOT.TH2F(f"hist2D_{ch}_{ch2}", f"FERS Board 1;Ch{ch};Ch{ch2}", 100, 0, 1000, 100, 0, 1000)

    # Loop through events
    cnt = 0
    for entry in tree:
        if cnt >= max_events:
            break
        cnt += 1
        for ch in range(num_channels):
            hist1D_dict[ch].Fill(entry.FERS_Board1_energyHG[ch])
        
        for ch1 in range(num_channels):
            for ch2 in range(ch1 + 1, num_channels):
                hist2D_dict[(ch1, ch2)].Fill(entry.FERS_Board1_energyHG[ch1], entry.FERS_Board1_energyHG[ch2])
    
    if not hist1D_dict or not hist2D_dict:
        raise ValueError("No data was loaded. Please check branch names and file content.")

    # Convert histograms to data
    data = defaultdict(list)
    for ch in range(num_channels):
        for bin in range(1, hist1D_dict[ch].GetNbinsX() + 1):
            data[ch].append(hist1D_dict[ch].GetBinContent(bin))
    
    histograms = {}
    for (ch1, ch2), hist2D in hist2D_dict.items():
        H = np.array([[hist2D.GetBinContent(x, y) for x in range(1, hist2D.GetNbinsX() + 1)] for y in range(1, hist2D.GetNbinsY() + 1)])
        xedges = [hist2D.GetXaxis().GetBinLowEdge(i) for i in range(1, hist2D.GetNbinsX() + 2)]
        yedges = [hist2D.GetYaxis().GetBinLowEdge(i) for i in range(1, hist2D.GetNbinsY() + 2)]
        histograms[(ch1, ch2)] = (H, xedges, yedges)

    # Close the file
    file.Close()
    
    return data, histograms

def generate_2d_histograms(data, channels, bins=50):
    histograms = {}
    
    # Generate 2D histograms for selected channel pairs
    for i, ch1 in enumerate(channels):
        for j, ch2 in enumerate(channels):
            if i >= j:
                continue
            
            if ch1 not in data or ch2 not in data:
                print(f"Warning: One of the channels {ch1} or {ch2} not found in data")
                continue
            
            # Generate the histogram
            H, xedges, yedges = np.histogram2d(data[ch1], data[ch2], bins=bins)
            histograms[(ch1, ch2)] = (H, xedges, yedges)
    
    return histograms

def plot_2d_histograms(histograms, output_file):
    """Plot 2D histograms and save to a PNG file."""
    
    # Debugging: Print types of histograms and ensure correct type
    for i, hist in enumerate(histograms):
        print(f"Type of histogram {i}: {type(hist)}")
    
    # Ensure histograms contain ROOT.TH2F objects
    histograms = [hist for hist in histograms.values() if isinstance(hist[0], np.ndarray)]
    
    if not histograms:
        print("No valid ROOT.TH2F histograms to plot.")
        return

    num_histograms = len(histograms)
    
    # Calculate the number of rows and columns needed
    num_cols = 4  # Number of columns in the grid
    num_rows = (num_histograms + num_cols - 1) // num_cols  # Calculate rows needed

    # Create a new figure with appropriate size
    plt.figure(figsize=(num_cols * 5, num_rows * 5))  # Adjust size as needed

    for i, (H, xedges, yedges) in enumerate(histograms):
        plt.subplot(num_rows, num_cols, i + 1)  # Create subplot
        
        # Plot using matplotlib
        try:
            plt.imshow(H, origin='lower', cmap='viridis', aspect='auto', extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]])
            plt.title(f"Histogram {i + 1}")
            plt.colorbar()  # Add colorbar
        except Exception as e:
            print(f"Error processing histogram {i}: {e}")
    
    # Adjust layout to make room for labels
    plt.tight_layout()
    
    # Save the figure
    try:
        plt.savefig(output_file)
    except Exception as e:
        print(f"Error saving figure: {e}")
    finally:
        plt.close()

def calculate_correlations(histograms):
    correlations = {}
    for (ch1, ch2), (H, _, _) in histograms.items():
        flattened_H = H.flatten()
        pearson_corr = pearsonr(flattened_H, flattened_H)[0]
        spearman_corr = spearmanr(flattened_H, flattened_H)[0]
        correlations[(ch1, ch2)] = {'pearson': pearson_corr, 'spearman': spearman_corr}
    return correlations

#def perform_pca(histograms, n_components=2):
    all_data = []
    
    for (ch1, ch2), (H, _, _) in histograms.items():
        flattened_H = H.flatten()
        all_data.extend(flattened_H)
    
    all_data = np.array(all_data).reshape(-1, 1)
    
    n_samples = all_data.shape[0]
    n_features = all_data.shape[1]
    
    if n_samples <= n_components or n_features <= n_components:
        raise ValueError(f"Insufficient data: {n_samples} samples and {n_features} features for PCA with {n_components} components.")
    
    pca = PCA(n_components=n_components)
    pca_result = pca.fit_transform(all_data)
    
    return pca_result


#def plot_pca_results(pca_results, output_file):
    plt.figure(figsize=(12, 12))
    plt.plot(pca_results[:, 0], pca_results[:, 1], 'o')
    plt.title('PCA Results')
    plt.xlabel('Principal Component 1')
    plt.ylabel('Principal Component 2')
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def plot_correlation_heatmaps(correlations, output_file):
    pearson_data = np.zeros((NUM_CHANNELS, NUM_CHANNELS))
    spearman_data = np.zeros((NUM_CHANNELS, NUM_CHANNELS))
    
    for (ch1, ch2), corr in correlations.items():
        pearson_data[ch1, ch2] = corr['pearson']
        spearman_data[ch1, ch2] = corr['spearman']
    
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    
    sns.heatmap(pearson_data, ax=ax[0], annot=True, fmt='.2f', cmap='coolwarm', cbar_kws={'label': 'Pearson Correlation'})
    ax[0].set_title('Pearson Correlation')
    sns.heatmap(spearman_data, ax=ax[1], annot=True, fmt='.2f', cmap='coolwarm', cbar_kws={'label': 'Spearman Correlation'})
    ax[1].set_title('Spearman Correlation')
    
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def analyze_data_points(histograms):
    matched_points = []
    for (ch1, ch2), (H, xedges, yedges) in histograms.items():
        for i in range(H.shape[0]):
            for j in range(H.shape[1]):
                if H[i, j] > 10:  # threshold to avoid noise
                    matched_points.append((ch1, ch2, xedges[i], yedges[j], H[i, j]))
    
    return matched_points

def main():
    root_file = "/home/michaelod/CaloXWork/datafiles/run742_V22000.root"
    tree_name = "EventTree"
    
    num_channels = NUM_CHANNELS
    max_events = MAX_EVENTS_PER_CHANNEL
    
    # Load data
    try:
        data, histograms = load_root_data(root_file, tree_name, num_channels, max_events)
    except ValueError as e:
        print(e)
        return
    
    # Print out the data to debug
    print("Loaded data:")
    for ch, values in data.items():
        print(f"Channel {ch}: {len(values)} entries")
    
    # Generate and plot histograms
    plot_2d_histograms(histograms, '2d_histograms.png')
    
    # Calculate correlations
    correlations = calculate_correlations(histograms)
    plot_correlation_heatmaps(correlations, 'correlation_heatmaps.png')
    
    # Perform PCA
    #pca_results = perform_pca(histograms)
    #plot_pca_results(pca_results, 'pca_results.png')
    
    # Analyze data points
    matched_points = analyze_data_points(histograms)
    print(f"Matched points: {matched_points}")

if __name__ == "__main__":
    main()

#end
