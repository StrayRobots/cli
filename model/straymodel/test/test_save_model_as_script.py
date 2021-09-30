import pytest
from models.straynet import StrayNet
import torch
import os

def test_save_model_as_script():
    model = StrayNet()

    script_model = torch.jit.script(model)
    torch.jit.save(script_model, "/tmp/script_model.pt")
    os.remove("/tmp/script_model.pt")

