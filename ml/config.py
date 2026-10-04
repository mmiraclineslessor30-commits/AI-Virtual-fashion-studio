from dataclasses import dataclass
import os


@dataclass
class ModelConfig:
    name: str = "AURA-VTON"
    device: str = "cpu"
    inference_mode: str = "local"
    model_loaded: bool = False


def get_model_config() -> ModelConfig:
    return ModelConfig(
        name=os.getenv("VTON_MODEL", "AURA-VTON"),
        device=os.getenv("VTON_DEVICE", "cpu"),
        inference_mode=os.getenv(
            "VTON_MODE",
            "local",
        ),
        model_loaded=False,
    )