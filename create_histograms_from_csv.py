import pandas as pd
import matplotlib.pyplot as plt
import os

def create_histograms_from_csv(file_path='uicrit_public.csv', output_dir='plot_uicrit/'):
    """
    Reads a CSV file, generates histograms for specified columns, and saves them.

    Args:
        file_path (str): The path to the input CSV file.
        output_dir (str): The directory where the histogram images will be saved.
    """
    # --- 1. Load the data ---
    try:
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
        return

    # --- 2. Define columns for plotting ---
    columns_to_plot = [
        'aesthetics_rating',
        'learnability',
        'efficency',
        'usability_rating',
        'design_quality_rating'
    ]

    # --- 3. Create the output directory if it doesn't exist ---
    try:
        os.makedirs(output_dir, exist_ok=True)
        print(f"Output directory '{output_dir}' is ready.")
    except OSError as e:
        print(f"Error: Could not create directory '{output_dir}'. Reason: {e}")
        return

    # --- 4. Generate and save a histogram for each column ---
    for column in columns_to_plot:
        if column not in df.columns:
            print(f"Warning: Column '{column}' not found in the CSV file. Skipping.")
            continue

        print(f"Generating histogram for '{column}'...")

        plt.figure(figsize=(10, 6)) # Create a new figure for each plot
        
        # Select the data and handle potential non-numeric values
        data = pd.to_numeric(df[column], errors='coerce').dropna()
        
        # Create the histogram
        plt.hist(data, bins=range(int(data.min()), int(data.max()) + 2), edgecolor='black', alpha=0.7, rwidth=0.8)

        plt.title(f'Distribution of {column.replace("_", " ").title()}', fontsize=16)
        plt.xlabel(column.replace("_", " ").title(), fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Set integer ticks for the x-axis since they are ratings
        plt.xticks(range(int(data.min()), int(data.max()) + 1))

        # Define the output file path
        save_path = os.path.join(output_dir, f'{column}_histogram.png')

        # Save the plot to a file
        try:
            plt.savefig(save_path)
            print(f"Histogram saved to '{save_path}'")
        except Exception as e:
            print(f"Could not save the plot for '{column}'. Reason: {e}")
        
        plt.close() # Close the figure to free up memory

    print("\nAll histograms have been generated and saved.")


if __name__ == '__main__':
    # Ensure the script is run from a directory containing 'uicrit_public.csv'
    # or provide the full path to the file.
    create_histograms_from_csv()
