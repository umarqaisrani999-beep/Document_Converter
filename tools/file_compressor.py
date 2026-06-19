import os
import zipfile


def compress_files(file_paths: list, output_zip_path: str, progress_cb=None):
    """
    Compress a list of files into a single .zip archive.
    progress_cb(pct: int, msg: str) is called during progress.
    """
    total = len(file_paths)
    if total == 0:
        raise ValueError("No files selected.")

    with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, path in enumerate(file_paths):
            if not os.path.isfile(path):
                continue
            arcname = os.path.basename(path)
            zf.write(path, arcname)
            pct = int(((i + 1) / total) * 100)
            if progress_cb:
                progress_cb(pct, f"Adding: {arcname} ({i+1}/{total})")

    if progress_cb:
        progress_cb(100, "Compression complete.")