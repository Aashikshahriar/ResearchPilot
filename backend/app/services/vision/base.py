from abc import ABC, abstractmethod
from dataclasses import dataclass

FIGURE_LABELS = [
    "architecture_diagram",
    "flowchart",
    "graph_plot",
    "table",
    "microscopy_image",
    "mathematical_figure",
    "other",
]

FIGURE_LABEL_PROMPTS = {
    "architecture_diagram": "a diagram of a neural network or system architecture",
    "flowchart": "a flowchart showing a process or algorithm with arrows between boxes",
    "graph_plot": "a line chart, bar chart, or scatter plot of experimental results",
    "table": "a table of numeric results or data",
    "microscopy_image": "a microscopy or biological/medical image",
    "mathematical_figure": "a mathematical figure with equations or geometric diagrams",
    "other": "a generic photograph or illustration",
}


@dataclass
class ClassificationResult:
    label: str
    confidence: float
    model_name: str


class VisionProvider(ABC):
    name: str = "base"

    @abstractmethod
    def classify(self, image_path: str) -> ClassificationResult: ...

    @abstractmethod
    def describe(self, image_path: str, label: str, caption: str | None = None) -> str: ...
