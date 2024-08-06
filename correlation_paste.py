import ROOT
import numpy as np

def calculate_correlations(file_path, total_channels):
    # Open the ROOT file
    file = ROOT.TFile(file_path, "READ")
    tree = file.Get("EventTree")

    # Create a multi-page PDF to save all histograms
    pdf_name = "correlation_coefficients_742.pdf"
    canvas = ROOT.TCanvas("canvas", "Correlation Coefficients", 2000, 1000)  # Increased size for better visibility
    canvas.Print(f"{pdf_name}[")

    # Initialize a list to store the correlations above 0.6
    high_correlations = []

    # Initialize counters
    count_above_one = 0
    count_below_neg_one = 0

    # Loop through all channels
    for selected_channel in range(total_channels):
        # Create a histogram to store the correlation coefficients
        correlation_hist = ROOT.TH1D(f"correlation_hist_{selected_channel}", 
                                     f"Correlation Coefficient for Channel {selected_channel};Channel Number;Correlation Coefficient", 
                                     total_channels, 0, total_channels)

        # List to store correlation coefficients for statistics
        correlations = []

        # Loop through all channels except the selected one
        for channel in range(total_channels):
            if channel == selected_channel:
                continue

            print(f"Processing channel {channel} for selected channel {selected_channel}...")

            # Create a 2D histogram for the current channel
            hist2D = ROOT.TH2D(f"hist2D_{selected_channel}_{channel}", 
                               f"FERS Board 1 - Channel {selected_channel} vs Channel {channel};Ch{selected_channel};Ch{channel}", 
                               100, 0, 1000, 100, 0, 1000)

            # Fill the 2D histogram directly from the tree
            expression = f"FERS_Board1_energyHG[{selected_channel}]:FERS_Board1_energyHG[{channel}]>>{hist2D.GetName()}"
            tree.Draw(expression, "", "goff", 22000)  # Process a limited number of entries

            # Check histogram contents
            entries = hist2D.GetEntries()
            print(f"Histogram {hist2D.GetName()} contents: {entries} entries")

            # Calculate and store the correlation coefficient
            correlation_coefficient = hist2D.GetCorrelationFactor()
            print(f"Channel {channel}: Correlation coefficient: {correlation_coefficient}")

            # Ensure correlation coefficient is in the expected range
            if abs(correlation_coefficient) > 1:
                print(f"Warning: Correlation coefficient {correlation_coefficient} is out of range [-1, 1]")

            # Count coefficients above 1 or below -1
            if correlation_coefficient > 1:
                count_above_one += 1
            elif correlation_coefficient < -1:
                count_below_neg_one += 1

            # Fill the correlation histogram
            correlation_hist.Fill(channel, correlation_coefficient)

            # Add the correlation coefficient to the list
            correlations.append(correlation_coefficient)

            # If the correlation coefficient is above 0.6, save it to the high_correlations list
            if correlation_coefficient > 0.6:
                high_correlations.append((selected_channel, channel, correlation_coefficient))

            # Clean up
            del hist2D

        # Calculate mean and standard deviation for the histogram
        mean_correlation = np.mean(correlations)
        std_dev_correlation = np.std(correlations)

        # Draw and save the histogram for the selected channel
        canvas.Clear()
        correlation_hist.Draw()

        # Customize the x-axis labels to show all channel numbers
        xaxis = correlation_hist.GetXaxis()
        xaxis.SetNdivisions(total_channels, ROOT.kTRUE)  # Set number of divisions for all labels
        xaxis.SetLabelSize(0.02)  # Adjust label size for better fit
        xaxis.SetLabelOffset(0.01)  # Increase label offset for better spacing
        xaxis.SetTickLength(0.05)  # Adjust tick length for better visibility
        xaxis.SetRangeUser(0, total_channels)  # Set range for x-axis

        # Add text box with mean and SD to the histogram
        pave_text = ROOT.TPaveText(0.7, 0.8, 0.9, 0.9, "NDC")
        pave_text.AddText(f"Mean: {mean_correlation:.2f}")
        pave_text.AddText(f"SD: {std_dev_correlation:.2f}")
        pave_text.SetBorderSize(1)
        pave_text.SetFillColor(0)
        pave_text.SetTextSize(0.03)
        pave_text.Draw()

        canvas.Print(f"{pdf_name}")

    # Finalize the multi-page PDF
    canvas.Print(f"{pdf_name}]")

    print(f"Number of correlation coefficients above 1: {count_above_one}")
    print(f"Number of correlation coefficients below -1: {count_below_neg_one}")

    # Convert high_correlations list to a NumPy array and save it
    high_correlations_array = np.array(high_correlations, dtype=[('selected_channel', int), ('channel', int), ('correlation_coefficient', float)])
    np.save("high_correlations.npy", high_correlations_array)

    print(f"High correlation coefficients saved to 'high_correlations.npy'.")

    # Close the input file
    file.Close()

# Example usage
calculate_correlations("/home/mileshar/dream/root/run742_V22000.root", total_channels=64)
