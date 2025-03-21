import torch_directml
import torch

# Create a DirectML device
dml_device = torch_directml.device()
print("DirectML device:", dml_device)
