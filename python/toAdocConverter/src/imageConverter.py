from PIL import Image
import os

def convert_images_to_png(media_folder):
    """
    Converts all emf and wmf images in our media folder to png images
    
    Args:
        media_folder (str): Path to the folder
    """
    
    if os.path.exists(f"{media_folder}/media") and os.listdir(f"{media_folder}/media"):
        for filename in os.listdir(f"{media_folder}/media"):
            if 'png' in filename.lower():
                print('png file')
            else:
                file_path = os.path.join(f"{media_folder}/media", filename)
                png_path = os.path.splitext(file_path)[0] + ".png"

                try:
                    with Image.open(file_path) as img:
                        img.save(png_path, "PNG")
                        print(f"Converted: {filename} -> {os.path.basename(png_path)}")
                    os.remove(file_path)  # Remove the original EMF/WMF file
                except Exception as e:
                    print(f"Failed to convert {filename}: {e}")