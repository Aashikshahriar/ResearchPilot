from PIL import Image

from app.services.vision.heuristic_provider import HeuristicVisionProvider


def test_classify_white_background_line_chart(tmp_path):
    img = Image.new("RGB", (400, 300), color=(255, 255, 255))
    pixels = img.load()
    for x in range(50, 350):
        y = 250 - int((x - 50) * 0.5)
        if 0 <= y < 300:
            pixels[x, y] = (0, 0, 0)
    path = tmp_path / "plot.png"
    img.save(path)

    provider = HeuristicVisionProvider()
    result = provider.classify(str(path))

    assert result.label in {"graph_plot", "table", "flowchart", "architecture_diagram"}
    assert 0.0 < result.confidence <= 1.0


def test_classify_returns_description_referencing_label(tmp_path):
    img = Image.new("RGB", (200, 200), color=(255, 255, 255))
    path = tmp_path / "img.png"
    img.save(path)

    provider = HeuristicVisionProvider()
    result = provider.classify(str(path))
    description = provider.describe(str(path), result.label, caption="Figure 1: test")

    assert result.label.replace("_", " ") in description
    assert "Figure 1" in description
