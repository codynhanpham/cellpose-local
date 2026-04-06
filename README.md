# Local Cellpose
A simple wrapper utility to install and run Cellpose locally on your machine without the need for Docker or Conda. This project uses [uv](https://docs.astral.sh/uv/) as the Python package manager to manage dependencies and run Cellpose.


## Prerequisites
- [uv](https://docs.astral.sh/uv/) installation

## Operating System
This repository should work on any operating system that supports by the upstream Cellpose package (Windows, macOS, Linux).

### GPU Support
For now, the project is configured for NVIDIA GPUs with CUDA 12.8 support on Windows and Linux. It will fallback to CPU-only mode on MacOS and/or no compatible GPU is detected.

If the CUDA Toolkit is not already install in your system, please download and install version 12.8 from the [NVIDIA CUDA Toolkit Archive](https://developer.nvidia.com/cuda-toolkit-archive). Make sure to select the correct version for your operating system and GPU architecture.

> [!Tip]
> If you know your system can run Cellpose with GPU support (even AMD or Intel GPUs) but it is not detected, feel free to update the `pyproject.toml` file to gate the correct PyTorch version for your system and submit a pull request. 

## Installation
1. Clone/Copy this repository to your local machine.
2. Open the terminal and navigate to the repository directory.
3. Run the following command to install the required dependencies:
    ```bash
    uv sync
    ```
4. Run the following command to check if the installation was successful, the installed version of Cellpose, and the installed version of PyTorch (CPU or GPU):
    ```bash
    uv run -m cellpose --version
    ```

## Usage
### Convert CZI to TIFF
Images taken on Airyscan microscopes are often saved in the CZI format, which is not directly supported by Cellpose.

Use the included `czi2tiff.py` script to convert CZI files to TIFF format, which can be read by Cellpose:
1. Check the CZI image stack dimensions and axes order using the `-s` or `--shape` flag:
    ```bash
    uv run czi2tiff.py -i /path/to/input.czi -s
    ```
    This will print the shape and axes order of the CZI image stack. For Cellpose, multi-plane (3D) images should be of shape `nplanes x nchannels x nY x nX` (multi-channel) or as `nplanes x nY x nX` (single-channel) (see [Cellpose documentation](https://cellpose.readthedocs.io/en/latest/do3d.html)).

2. Convert the CZI file to TIFF format:

    Note the axes order of the CZI image stack from the previous step!

    1. **If the CZI image stack is already in the correct shape and axes order** for Cellpose, simply run:
        ```bash
        uv run czi2tiff.py -i /path/to/input.czi
        ```
        By default, the output TIFF file will be saved in the same directory as the input CZI file with the same base name and a `.tiff` extension. You can specify a custom output path using the `-o` or `--output` flag:
        ```bash
        uv run czi2tiff.py -i /path/to/input.czi -o /path/to/output.tiff
        ```
    2. **If the CZI image stack is not in the correct shape and axes order** for Cellpose, you can specify the desired axes order using the `--reshape` flag. For example, if the CZI image stack has axes order `(C x Z x Y x X)`, you can reshape it to `(Z x C x Y x X)` (Cellpose-compatible) using:
        ```bash
        uv run czi2tiff.py -i /path/to/input.czi --reshape [1,0,2,3]
        ```
        The list passed to `--reshape` should contain the new order of axes indices. In this example, `1` corresponds to `Z`, `0` corresponds to `C`, `2` corresponds to `Y`, and `3` corresponds to `X`. Adjust the indices in the list according to the actual axes order of your CZI image stack.

3. Check that a new TIFF file has been created at the specified output path. This TIFF file can now be used as input for Cellpose.

> [!WARNING]
> The `czi2tiff.py` script only convert the image data from CZI to TIFF format. It does not preserve any metadata (e.g., pixel size, channel names, etc.) from the original CZI file. **DO NOT DELETE THE ORIGINAL CZI FILES** after conversion, as you may need to refer back to them for metadata information or if you need to re-convert with different reshape options.

### Use the Cellpose CLI
The general CLI operations for running Cellpose is similar to the official Cellpose package, only replacing `python` calls with `uv run`. This will automatically handle activating the correct Python environment with the necessary dependencies installed.

### Use the Cellpose GUI

To launch the Cellpose GUI for 2D image segmentation, run the following command:
```bash
uv run -m cellpose
```

For 3D image segmentation, run the following command:
```bash
uv run -m cellpose --Zstack
```