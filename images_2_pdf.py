from PIL import Image

image_filepath = "screenshots/"

def combine_images_to_pdf(image_list, output_pdf_name):
    """
    Combines a list of image filenames into a single multi-page PDF.
    
    :param image_list: List of strings (e.g., ['img1.png', 'img2.jpg'])
    :param output_pdf_name: String for the output file (e.g., 'output.pdf')
    """
    if not image_list:
        print("The image list is empty.")
        return
        
    opened_images = []
    
    try:
        for file_path in image_list:
            img = Image.open(file_path)
            
            # CRITICAL step: PDF format does not support alpha channels (transparency).
            # If an image is RGBA (like PNG) or Palette with transparency, convert to RGB.
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")
                
            opened_images.append(img)
            
        # Extract the first image to initialize the PDF file mapping
        first_image = opened_images[0]
        remaining_images = opened_images[1:]
        
        # Save the first image as a PDF and append the remaining images as new pages
        first_image.save(
            output_pdf_name, 
            save_all=True, 
            append_images=remaining_images
        )
        print(f"✅ Successfully combined {len(image_list)} images into '{output_pdf_name}'")
        
    except Exception as e:
        print(f"❌ An error occurred while compiling the PDF: {e}")
        
    finally:
        # Always close your image files to free up system memory
        for img in opened_images:
            img.close()

# Example usage:
if __name__ == "__main__":
    image_files = [f"{image_filepath}capture{i}.png" for i in range(1, 3 + 1)]  # Adjust the range as needed, recall end is exclusive
    combine_images_to_pdf(image_files, "output.pdf")