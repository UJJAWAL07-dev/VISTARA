import numpy as np
from PIL import Image

print("Generating synthetic drone image...")
# 1. Create a dark green background (representing land/grass)
img_array = np.full((1024, 1024, 3), (34, 139, 34), dtype=np.uint8)

# 2. Draw a grey vertical strip (representing a low-saturation road)
img_array[:, 400:600] = (100, 100, 100)

# 3. Draw a bright white square (representing a high-contrast building roof)
img_array[200:350, 700:850] = (240, 240, 240)

# 4. Save the image to our new folder
output_path = "ai/sample_data/synthetic_drone_view.png"
Image.fromarray(img_array).save(output_path)
print(f"Success! Image saved to {output_path}")