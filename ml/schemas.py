from dataclasses import dataclass
from typing import Optional


@dataclass
class TryOnResult:
    status: str
    model: str
    device: str
    output_image: Optional[str] = None
    message: Optional[str] = None

    def to_dict(self):
        return {
            "status": self.status,
            "model": self.model,
            "device": self.device,
            "output_image": self.output_image,
            "message": self.message,
        }