import csv
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import LabelEncoder

# Define the neural network model
class MyModel(nn.Module):
    def __init__(self, input_size, output_size):
        super(MyModel, self).__init__()
        self.fc1 = nn.Linear(input_size, 64)
        self.fc2 = nn.Linear(64, output_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Define custom dataset
class MyDataset(Dataset):
    def __init__(self, data, labels):
        self.data = data
        self.labels = labels

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        x = self.data[index]
        y = self.labels[index]
        return x, y

# Read data from CSV file and extract channel information
channels = []
hex_codes = []
with open('csv_input.csv', 'r') as file:
    reader = csv.reader(file, delimiter=';')
    next(reader)  # Skip the header row
    for row in reader:
        if not row[1]:  # Skip the line if the 'Frequency' field is empty
            continue

        try:
            frequency = int(float(row[1].replace(',', '.')) * 1e6)
        except ValueError:
            continue  # Skip the line if the 'Frequency' field is not numeric

        channel = {
            'number': int(row[0]),
            'frequency': frequency,
            'duplex': row[2],
            'offset': float(row[3].replace(',', '.')),
            'ts': row[4],
            'mode': row[5],
            'name': row[6],
            'skip': row[7],
            'tone': row[8],
            'repeater_tone': row[9],
            'tsql_frequency': row[10],
            'dtcs_code': row[11],
            'dtcs_polarity': row[12],
            'dv_sql': row[13],
            'dv_csql_code': row[14],
            'your_call_sign': row[15],
            'rpt1_call_sign': row[16],
            'rpt2_call_sign': row[17]
        }
        channels.append(channel)

# Read HEX strings from the "hex_input.txt" file
with open('hex_input.txt', 'r') as file:
    hex_strings = file.readlines()
hex_strings = [hex_string.strip() for hex_string in hex_strings]

# Convert the input features into numerical representation

# Convert the hexadecimal codes into numerical values
numeric_hex_codes = [int(hex_code, 16) for hex_code in hex_strings]

# Convert input features to a list of lists
data = []
for channel in channels:
    channel_data = []
    for key in channel:
        value = channel[key]
        if isinstance(value, str):
            channel_data.append(value)
        else:
            channel_data.append(float(value))
    data.append(channel_data)

# Convert the list of lists into a NumPy array
data = np.array(data)
input_size = data.shape[1]
# Encode categorical variables
label_encoder = LabelEncoder()
for i in range(data.shape[1]):
    if isinstance(data[0][i], str):
        data[:, i] = label_encoder.fit_transform(data[:, i])

# Convert the data to float32
data = data.astype(np.float32)

# Convert labels to a NumPy array
labels = np.array(numeric_hex_codes, dtype=np.float32)

# Create a custom dataset and data loader
dataset = MyDataset(data, labels)
batch_size = 16
dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

# Define the neural network model
input_size = data.shape[1]
output_size = 1
model = MyModel(input_size, output_size)

# Define loss function and optimizer
criterion = nn.MSELoss()
optimizer = optim.SGD(model.parameters(), lr=0.01)

# Train the model
num_epochs = 10
for epoch in range(num_epochs):
    for inputs, labels in dataloader:
        # Forward pass
        outputs = model(inputs)
        loss = criterion(outputs, labels)

        # Backward pass and optimization
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    # Print the loss for each epoch
    print(f"Epoch {epoch+1}/{num_epochs}, Loss: {loss.item()}")

# Save the trained model
#print(model.state_dict())
torch.save(model.state_dict(), 'model.pt')
