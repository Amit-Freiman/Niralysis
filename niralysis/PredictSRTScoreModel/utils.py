import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
import os
import pandas as pd
import matplotlib.pyplot as plt


def load_and_preprocess_image(image_path, target_size=(64, 64)):
    """
    Load and preprocess an image.

    Args:
    image_path (str): Path to the image.
    target_size (tuple): Target size for the image.

    Returns:
    np.array: Preprocessed image.
    """
    image = tf.keras.utils.load_img(image_path, target_size=target_size)
    image = tf.keras.utils.img_to_array(image)
    image = image / 255.0  # Normalize to [0, 1]
    return image


def prepare_data(image_paths, scores, test_size=0.2, val_size=0.1, target_size=(64, 64)):
    """
    Prepare data by loading and preprocessing images and splitting into train, val, and test sets.

    Args:
    image_paths (list): List of image paths.
    scores (list): List of corresponding scores.
    test_size (float): Fraction of data to be used for the test set.
    val_size (float): Fraction of data to be used for the validation set.
    target_size (tuple): Target size for the images.

    Returns:
    tuple: (X_train, X_val, X_test, y_train, y_val, y_test)
    """
    # Load and preprocess images
    images = np.array([load_and_preprocess_image(path, target_size) for path in image_paths])
    scores = np.array(scores)

    # Split the data into train+val and test sets
    X_train_val, X_test, y_train_val, y_test = train_test_split(images, scores, test_size=test_size, random_state=42)

    # Further split the train+val set into train and val sets
    val_fraction_of_train_val = val_size / (1 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(X_train_val, y_train_val, test_size=val_fraction_of_train_val,
                                                      random_state=42)

    return X_train, X_val, X_test, y_train, y_val, y_test


def create_image_score_arrays(images_folder, excel_file):
    """
    Create arrays of image paths and corresponding scores.

    Args:
    images_folder (str): Path to the folder containing heatmap images.
    excel_file (str): Path to the Excel file containing the scores.

    Returns:
    tuple: (image_paths, scores)
    """
    # Load the Excel file
    df = pd.read_excel(excel_file)

    # Initialize lists to hold image paths and scores
    image_paths = []
    scores = []

    # Iterate over the images in the folder
    for image_name in os.listdir(images_folder):
        # Skip non-image files
        if not image_name.endswith(('.png', '.jpg', '.jpeg')):
            continue

        # Extract time, name, and watch from the image filename
        date, choice, watch = image_name.rsplit('-')
        watch = watch.split('.')[0]  # Remove the file extension from 'watch'

        # Find the corresponding row in the Excel file
        matching_row = df[(df['date'] == date) & (df['choices'] == choice) & (df['watch'] == int(watch))]

        if not matching_row.empty:
            # Get the score for the matching row
            score = matching_row['score'].values[0]

            # Append the image path and score to the lists
            image_paths.append(os.path.join(images_folder, image_name))
            scores.append(score)
        else:
            print(f"No matching entry found for image: {image_name}")

    return image_paths, scores


def plot_model_analysis(history, model, X_test, y_test):
    """
    Analyze and plot the model's performance.

    Args:
    history: History object returned by model.fit() containing training metrics.
    model: Trained Keras model.
    X_test: Test data (features).
    y_test: Test data (labels).
    """

    # 1. Plot training & validation loss values
    plt.figure(figsize=(14, 6))
    plt.subplot(1, 2, 1)
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Model Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss (MSE)')
    plt.legend(loc='upper right')

    # 2. Plot training & validation MAE values
    plt.subplot(1, 2, 2)
    plt.plot(history.history['mae'], label='Train MAE')
    plt.plot(history.history['val_mae'], label='Validation MAE')
    plt.title('Model MAE')
    plt.xlabel('Epoch')
    plt.ylabel('Mean Absolute Error (MAE)')
    plt.legend(loc='upper right')

    plt.tight_layout()
    plt.show()

    # 3. Predicted vs Actual values
    y_pred = model.predict(X_test)

    plt.figure(figsize=(7, 7))
    plt.scatter(y_test, y_pred, alpha=0.5)
    plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], 'r--')  # 45-degree line
    plt.title('Predicted vs Actual')
    plt.xlabel('Actual Scores')
    plt.ylabel('Predicted Scores')
    plt.show()

    # 4. Residuals plot
    residuals = y_test - y_pred.flatten()

    plt.figure(figsize=(10, 6))
    plt.hist(residuals, bins=30, alpha=0.7, color='blue')
    plt.title('Residuals Distribution')
    plt.xlabel('Residual (Actual - Predicted)')
    plt.ylabel('Frequency')
    plt.show()

