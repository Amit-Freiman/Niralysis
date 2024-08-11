import tensorflow as tf
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt

from niralysis.PredictSRTScoreModel.utils import create_image_score_arrays, prepare_data


class PredictSRTScoreModal:

    def __init__(self, images_folder_path, excel_file):
        self.base_model = None
        self.model = None
        self.X_train = None
        self.y_train = None
        self.X_val = None
        self.y_val = None
        self.X_test = None
        self.y_test = None
        self.images_folder_path = images_folder_path
        self.excel_file = excel_file

    def set_data(self):
        image_paths, scores = create_image_score_arrays(self.images_folder_path, self.excel_file)
        X_train, X_val, X_test, y_train, y_val, y_test = prepare_data(image_paths, scores)
        self.X_train = X_train
        self.y_train = y_train
        self.X_val = X_val
        self.y_val = y_val
        self.X_test = X_test
        self.y_test = y_test


    def create_model(self):

        # Load the pre-trained ResNet50 model without the top layers
        self.base_model = tf.keras.applications.ResNet50(weights='imagenet', include_top=False, input_shape=(64, 64, 3))

        # Add custom layers on top of the base model
        x = self.base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(128, activation='relu')(x)
        x = Dense(64, activation='relu')(x)
        predictions = Dense(1, activation='linear')(x)  # Output layer for regression

        # Create the full model
        self.model = tf.keras.Model(inputs=self.base_model.input, outputs=predictions)
        # Freeze the layers of the base model
        for layer in self.base_model.layers:
            layer.trainable = False

        # Compile the model
        self.model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])

        # Print the model summary
        self.model.summary()

    def train(self):
        # Train the model
        history = self.model.fit(self.X_train, self.y_train, epochs=20, validation_data=(self.X_val, self.y_val),
                            callbacks=[tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5),
                                       tf.keras.callbacks.ModelCheckpoint('best_model.h5', save_best_only=True)])

        # Fine-tuning: Unfreeze some layers and retrain
        for layer in self.base_model.layers[-10:]:  # Unfreeze the last 10 layers
            layer.trainable = True

        # Recompile the model with a lower learning rate
        self.model.compile(optimizer=Adam(learning_rate=1e-5), loss='mse', metrics=['mae'])

        # Continue training the model
        history_fine = self.model.fit(self.X_train, self.y_train, epochs=20, validation_data=(self.X_val, self.y_val),
                                 callbacks=[tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5),
                                            tf.keras.callbacks.ModelCheckpoint('best_model_fine.h5', save_best_only=True)])

    def evaluate(self):
        # Evaluate the model
        test_loss, test_mae = self.model.evaluate(self.X_test, self.y_test)
        print(f"Test MAE: {test_mae}")

        # Predict the scores on the test set
        y_pred = self.model.predict(self.X_test)

        # Calculate additional evaluation metrics
        mse = mean_squared_error(self.y_test, y_pred)
        mae = mean_absolute_error(self.y_test, y_pred)
        r2 = r2_score(self.y_test, y_pred)

        print(f"Mean Squared Error (MSE): {mse}")
        print(f"Mean Absolute Error (MAE): {mae}")
        print(f"R-squared (R²): {r2}")

        # Plot Actual vs Predicted scores
        plt.figure(figsize=(10, 6))
        plt.scatter(self.y_test, y_pred, alpha=0.5)
        plt.plot([0, 5], [0, 5], color='red', linestyle='--')
        plt.xlabel('Actual Scores')
        plt.ylabel('Predicted Scores')
        plt.title('Actual vs Predicted Heatmap Scores')
        plt.show()
    def run(self):
        self.set_data()
        self.create_model()
        self.train()
        self.evaluate()


