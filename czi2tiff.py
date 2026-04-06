# Given path to a CZI file, convert it to TIFF format using the czifile library.
# Usage:
# + With 'uv':
#       uv run czi2tiff.py -i path/to/input.czi -s
#       uv run czi2tiff.py -i path/to/input.czi
#       uv run czi2tiff.py -i path/to/input.czi -o path/to/output.tiff
#       uv run czi2tiff.py -i path/to/input.czi --reshape [1,0,2,3]
# + With 'python' (must activate environment with czifile installed first):
#       python czi2tiff.py -i path/to/input.czi -s
#       python czi2tiff.py -i path/to/input.czi
#       python czi2tiff.py -i path/to/input.czi -o path/to/output.tiff
#       python czi2tiff.py -i path/to/input.czi --reshape [1,0,2,3]

import argparse
from pathlib import Path
import numpy as np
from czifile import CziFile
from tifffile import imwrite, imread


def input_file_exist(path_str: str) -> Path:
    input_path = Path(path_str)
    if not input_path.exists():
        raise argparse.ArgumentTypeError(f"Input file not found: {input_path}")
    if not input_path.is_file():
        raise argparse.ArgumentTypeError(f"Input path is not a file: {input_path}")
    return input_path


def parse_reshape_axes(value: str) -> list[int]:
    cleaned = value.strip()
    if cleaned.startswith("[") and cleaned.endswith("]"):
        cleaned = cleaned[1:-1].strip()

    if not cleaned:
        raise argparse.ArgumentTypeError("--reshape cannot be empty.")

    parts = [part.strip() for part in cleaned.split(",")]
    try:
        axes = [int(part) for part in parts]
    except ValueError as err:
        raise argparse.ArgumentTypeError(
            "--reshape must be a comma-separated list of integers, e.g. [1,0,2,3]."
        ) from err

    if len(axes) != len(set(axes)):
        raise argparse.ArgumentTypeError("--reshape must not contain duplicate axes.")

    if any(axis < 0 for axis in axes):
        raise argparse.ArgumentTypeError("--reshape axes must be non-negative integers.")

    return axes


def apply_axis_permutation(image_data: np.ndarray, axes: list[int] | None) -> np.ndarray:
    if axes is None:
        return image_data

    ndim = image_data.ndim
    if len(axes) != ndim:
        raise ValueError(
            f"--reshape length ({len(axes)}) must match image dimensions ({ndim})."
        )

    expected_axes = set(range(ndim))
    if set(axes) != expected_axes:
        raise ValueError(
            f"--reshape must be a permutation of {list(range(ndim))}. Got {axes}."
        )

    return np.transpose(image_data, axes=axes)


def czi_to_tiff(
    input_path: str | Path, output_path: str | Path, reshape_axes: list[int] | None = None
) -> None:
    input_file = Path(input_path)
    output_file = Path(output_path)

    # Open the CZI file
    with CziFile(str(input_file)) as czi:
        # Read the image data as a NumPy array
        image_data: np.ndarray = czi.asarray()

    image_data = apply_axis_permutation(image_data, reshape_axes)

    # Save the image data as a TIFF file
    imwrite(str(output_file), image_data)
    # Validate the tiff file shape
    data = imread(str(output_file))
    print(f"Converted '{input_file}' to '{output_file}'. TIFF shape: {data.shape}")


def print_czi_shape(input_path: str | Path) -> None:
    input_file = Path(input_path)

    with CziFile(str(input_file)) as czi:
        image_data: np.ndarray = czi.asarray()

    print(f"CZI shape for '{input_file}': {image_data.shape}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert CZI files to TIFF format.")
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        type=input_file_exist,
        help="Path to an existing input CZI file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        help="Path to the output TIFF file. Defaults to input file path with .tiff extension.",
    )
    parser.add_argument(
        "-s",
        "--shape",
        action="store_true",
        help="Display CZI image shape only, without converting or saving a TIFF file.",
    )
    parser.add_argument(
        "--reshape",
        type=parse_reshape_axes,
        required=False,
        help=(
            "Reorder image axes before saving TIFF, e.g. --reshape [1,0,2,3] "
            "or --reshape 1,0,2,3."
        ),
    )
    return parser.parse_args()


def resolve_output_path(input_path: Path, output_path: str | None) -> Path:
    return Path(output_path) if output_path else input_path.with_suffix(".tiff")


def main() -> None:
    args = parse_args()
    if args.shape:
        print_czi_shape(args.input)
        return

    output_path = resolve_output_path(args.input, args.output)
    try:
        czi_to_tiff(args.input, output_path, reshape_axes=args.reshape)
    except ValueError as err:
        raise SystemExit(f"Error: {err}") from err

if __name__ == "__main__":
    main()