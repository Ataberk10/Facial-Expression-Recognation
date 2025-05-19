# queries/analysis.py
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification, pipeline
import os
from django.conf import settings  # To build the model path

# --- Configuration ---
# Define the path to your ONNX model relative to the project's BASE_DIR
MODEL_PATH = os.path.join(
    settings.BASE_DIR,
    "ml_models",
)  # Adjust 'emotion_model.onnx' if needed
feature_extractor = AutoImageProcessor.from_pretrained(MODEL_PATH)
model = AutoModelForImageClassification.from_pretrained(MODEL_PATH)
pipe = pipeline(
    task="image-classification", model=model, feature_extractor=feature_extractor
)


def analyze_facial_expression(image_path):
    """
    Analyzes the facial expression in an image using the ONNX model.

    Args:
        image_path (str): The absolute path to the image file.

    Returns:
        tuple: A tuple containing (detected_emotion_label, confidence_score).
               Returns (None, None) if analysis fails.
    """
    if not pipe:
        print("Error: Model is not available.")
        return None, None
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return None, None

    try:
        # --- 1. Preprocessing ---
        # Load the image (using OpenCV here, adapt if using Pillow)
        img = Image.open(image_path).convert("RGB")
        if img is None:
            print(f"Error: Could not read image file {image_path}")
            return None, None

        result = pipe(img)
        # Get the corresponding label and confidence score
        detected_label = result[0]["label"]
        confidence = float(result[0]["score"])  # Ensure it's a standard float

        print(
            f"Analysis result for {os.path.basename(image_path)}: Label={detected_label}, Confidence={confidence:.4f}"
        )
        return detected_label, confidence

    except FileNotFoundError:
        print(f"Error: Image file not found during processing: {image_path}")
        return None, None
    except ImportError:
        print("Error: OpenCV or NumPy might be missing. Please install them.")
        return None, None
    except IndexError:
        print(
            f"Error: Could not map prediction index to label. Check EMOTION_LABELS length ({len(result)}) vs model output."
        )
        return None, None
    except Exception as e:
        # Catch-all for other unexpected errors during processing
        print(f"Error during facial expression analysis for {image_path}: {e}")
        # Consider logging the full traceback here in production
        import traceback

        traceback.print_exc()
        return None, None  # Return None on failure
