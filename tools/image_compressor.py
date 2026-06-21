import os
from PIL import Image


def compress_image(input_path: str, output_path: str, quality: int = 70,
                   max_dimension: int = None, progress_cb=None):
    """
    Compress an image by reducing quality and optionally resizing.
    quality: 1-95 (lower = smaller file, more loss)
    max_dimension: if set, scales image so longest side <= this value
    """
   if not os . path . isfile ( input_path ) : 
    raise FileNotFoundError ( f"Input image not found: { input_path } " ) 
if not isinstance ( quality , int ) or not ( 1 <= quality <= 95 ) : 
    raise ValueError ( f"Quality must be an integer between 1 and 95 (got { quality } )." ) 
if max_dimension is not None and max_dimension <= 0 : 
    raise ValueError ( f"max_dimension must be a positive number (got { max_dimension } )." ) 
if progress_cb : 
    progress_cb ( 10 , "Opening image..." ) 
img = Image . open ( input_path )

    # Convert RGBA/P to RGB for JPEG compatibility
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    if progress_cb:
        progress_cb(40, "Resizing...")

    if max_dimension:
        w, h = img.size
        longest = max(w, h)
        if longest > max_dimension:
            scale = max_dimension / longest
            new_w = int(w * scale)
            new_h = int(h * scale)
            img = img.resize((new_w, new_h), Image.LANCZOS)

    if progress_cb:
        progress_cb(70, "Saving compressed image...")

    # Determine format from output extension
    ext = os.path.splitext(output_path)[1].lower()
    fmt = "JPEG" if ext in (".jpg", ".jpeg") else "PNG" if ext == ".png" else "JPEG"

    save_kwargs = {"optimize": True}
    if fmt == "JPEG":
        save_kwargs["quality"] = quality

    img.save(output_path, fmt, **save_kwargs)

    if progress_cb:
        progress_cb(100, "Done.")
