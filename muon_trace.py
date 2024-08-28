import ROOT
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scipy.stats import linregress

file = ROOT.TFile("/home/michaelod/CaloXWork/datafiles/run749_4500.root", "READ")
tree = file.Get("EventTree")

cnt = 0
df = {}

def get_data(ev):
    global df
    # Extract data from the event
    df["hg1"] = np.array(ev.FERS_Board1_energyHG)
    df["run"] = ev.run_n
    df["event"] = ev.event_n

def display_hits(df):
    zval = df["hg1"]

    # Event and hit selection criteria
    smax_event = 1000
    cmax_event = 350
    nhitmin_s = 3
    nhitmin_c = 1
    smin_hit = 350
    cmin_hit = 350

    cfib = np.array([zval[0]-59, zval[1]-59, zval[2]-57, zval[3]-52, zval[8]-56, zval[9]-53, zval[10]-54, zval[11]-53,
                     zval[16]-56, zval[17]-57, zval[18]-57, zval[19]-55, zval[24]-56, zval[25]-54, zval[26]-55, zval[27]-54,
                     zval[32]-56, zval[33]-53, zval[34]-55, zval[35]-51, zval[40]-54, zval[41]-55, zval[42]-51, zval[43]-53,
                     zval[48]-53, zval[49]-52, zval[50]-52, zval[51]-52, zval[56]-51, zval[57]-53, zval[58]-55, zval[59]-53])

    sfib = np.array([zval[4]-54, zval[5]-53, zval[6]-53, zval[7]-51, zval[12]-54, zval[13]-52, zval[14]-52, zval[15]-52,
                     zval[20]-50, zval[21]-53, zval[22]-53, zval[23]-53, zval[28]-51, zval[29]-54, zval[30]-53, zval[31]-48,
                     zval[36]-52, zval[37]-52, zval[38]-52, zval[39]-54, zval[44]-53, zval[45]-50, zval[46]-51, zval[47]-53,
                     zval[52]-52, zval[53]-51, zval[54]-52, zval[55]-49, zval[60]-53, zval[61]-51, zval[62]-52, zval[63]-52])

    cmax = np.max(cfib)
    smax = np.max(sfib)

    xval1 = np.array([24, 22, 23, 21, 23, 21, 24, 22, 24, 22, 23, 21, 23, 21, 24, 22, 24, 22, 23, 21, 23, 21, 24, 22, 24, 22, 23, 21, 23, 21, 24, 22])
    yval1 = np.array([9, 9, 9, 9, 8, 8, 8, 8, 7, 7, 7, 7, 6, 6, 6, 6, 5, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, 3, 2, 2, 2, 2])

    if smax < smax_event or smax > 7999:
        return
    if cmax < cmax_event:
        return

    isfib = sfib > smax_event
    icfib = cfib > cmax_event

    sfiblarge = sfib[isfib]
    cfiblarge = cfib[icfib]

    nsfib = len(sfiblarge)
    ncfib = len(cfiblarge)

    if nsfib < nhitmin_s or ncfib < nhitmin_c:
        return

    print("RUN", df["run"], "EVENT", df["event"])
    print("Cherenkov's border is black")
    print("Scintillator's border is blue")

    # Set up the grid
    pattern = [
        "      ******************      ",
        "      ******************      ",
        "     ********************     ",
        "     ********************     ",
        "   ************************   ",
        "   ************************   ",
        " **************************** ",
        " **************************** ",
        " ************    ************ ",
        " ************    ************ ",
        " ************    ************ ",
        " ************    ************ ",
        " **************************** ",
        " **************************** ",
        "   ************************   ",
        "   ************************   ",
        "     ********************     ",
        "     ********************     ",
        "      ******************      ",
        "      ******************      "
    ]

    height = len(pattern)
    width = len(pattern[0])
    
    # Remove empty rows on the right and left
    left_trim = min(i for i in range(width) if any(pattern[j][i] == '*' for j in range(height)))
    right_trim = max(i for i in range(width) if any(pattern[j][i] == '*' for j in range(height))) + 1
    
    trimmed_pattern = [row[left_trim:right_trim] for row in pattern]
    trimmed_width = right_trim - left_trim

    grid = np.zeros((height, trimmed_width))

    for y, row in enumerate(trimmed_pattern):
        for x, char in enumerate(row):
            if char == '*':
                grid[y, x] = 1

    fig, ax = plt.subplots(figsize=(10, 8))
    cmap = plt.get_cmap('autumn_r')
    norm = mcolors.Normalize(vmin=min(cfib.min(), sfib.min()), vmax=max(cfib.max(), sfib.max()))

    cax = ax.imshow(grid, cmap='gray', interpolation='none')
    plt.xticks(np.arange(trimmed_width))
    plt.yticks(np.arange(height))
    plt.gca().invert_yaxis()
    plt.grid(False)

    # Add rectangles to the grid cells
    for y in range(height):
        for x in range(trimmed_width):
            if grid[y, x] == 1:
                rect = plt.Rectangle((x - 0.5, y - 0.5), 1, 1, linewidth=1, edgecolor='gray', facecolor='none')
                plt.gca().add_patch(rect)

                # Add the first small square inside the big square
                small_square_1 = plt.Rectangle((x - 0.15, y - 0.35), 0.3, 0.3, linewidth=1, edgecolor='blue', facecolor='none')
                plt.gca().add_patch(small_square_1)

                # Add the second small square stacked above the first
                small_square_2 = plt.Rectangle((x - 0.15, y + 0.05), 0.3, 0.3, linewidth=1, edgecolor='gray', facecolor='none')
                plt.gca().add_patch(small_square_2)

    # Plot Cherenkov as rectangles with a color map from yellow to red and semi-transparent
    for (x, y, c) in zip(xval1[icfib] - left_trim, yval1[icfib] - 0.25, cfib[icfib]):
        color = cmap(norm(c))
        rect = plt.Rectangle((x - 0.5, y - 0.25), 0.9, 0.4, color=color, alpha=0.5)  # Semi-transparent
        ax.add_patch(rect)

    # Plot scintillator as rectangles with a color map from yellow to red and semi-transparent
    for (x, y, c) in zip(xval1[isfib] - left_trim, yval1[isfib] + 0.25, sfib[isfib]):
        color = cmap(norm(c))
        rect = plt.Rectangle((x - 0.5, y - 0.25), 0.9, 0.4, color=color, alpha=0.5)  # Semi-transparent
        ax.add_patch(rect)

    # Fit a line to the centroids of the rectangles
    centroids_x = np.concatenate([xval1[icfib] - left_trim, xval1[isfib] - left_trim])
    centroids_y = np.concatenate([yval1[icfib], yval1[isfib]])

    if len(np.unique(centroids_x)) > 1:
        slope, intercept, _, _, _ = linregress(centroids_x, centroids_y)

        # Plot the line of best fit
        line_x = np.array([centroids_x.min() - 5, centroids_x.max() + 5])  # Extend line beyond the data
        line_y = slope * line_x + intercept
        ax.plot(line_x, line_y, color='red', linestyle='-', linewidth=2)
    else:
        print("Cannot calculate a linear regression: all x values are identical.")

    # Add the label on top
    label_text = f"RUN {df['run']} EVENT {df['event']}"
    plt.text(0.5, 1.05, label_text, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=16, weight='bold')

    # Add a colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label('Signal Strength')

    plt.show()


# Loop over the entries in the tree
for entry in tree:
    cnt += 1
    if cnt > 50:  # Change value to loop over a certain amount of entries
        break

    get_data(entry)
    display_hits(df)

#end
