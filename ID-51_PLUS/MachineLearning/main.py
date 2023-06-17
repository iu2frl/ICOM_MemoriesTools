import tensorflow as tf
import numpy as np
import pandas as pd

# Load the training data
csv_data = pd.read_csv('csv_input.csv', delimiter=';', skiprows=1)
hex_data = pd.read_csv('hex_input.txt', delimiter=';', header=None)

# Prepare the input and target data
csv_input = csv_data.iloc[:, 1:].apply(pd.to_numeric, errors='coerce').values.astype(float)  # Exclude the first column (CH No)
hex_target = hex_data.iloc[1:].values.astype(int)
# Define the neural network architecture
model = tf.keras.Sequential([
    tf.keras.layers.Dense(64, activation='relu', input_shape=(17,)),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(16, activation='softmax')
])

# Compile the model
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')

# Train the model
model.fit(csv_input, hex_target, epochs=100)

# Save the trained model
model.save('csv_to_hex_translation_model')

# Load the trained model
model = tf.keras.models.load_model('csv_to_hex_translation_model')

# Generate hex stream for new CSV input
new_csv_data = pd.read_csv('new_input.csv', delimiter=';', skiprows=1)
new_csv_input = new_csv_data.iloc[:, 1:].values
predicted_hex = model.predict(new_csv_input)

# Convert the predicted hex stream to a string
predicted_hex_str = ''.join([format(np.argmax(row), 'x').zfill(2) for row in predicted_hex])

print(predicted_hex_str)
