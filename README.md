# dji-osv2mp4

A CLI tool to automate converting panorama videos in raw .OSV format from DJI Osmo 360 into .mp4 panorama videos using SikuliX and ExifTool.

This tool is meant to free users from the god damn DJI proprietary .OSV format. The freaking company DOES NOT provide any API (in contrast, Insta360 provides an SDK for its 360 cameras — see [https://github.com/whmou/insta360-auto-converter](https://github.com/whmou/insta360-auto-converter)) for automation. As a result, exporting and handling metadata for large amounts of video is EXTREMELY frustrating.

This is a small toolchain combines:

* GUI automation (via SikuliX) to batch export `.OSV` files using DJI Studio
* Metadata synchronization to ensure correct timestamps in exported videos

**I am genuinely asking DJI to provide an official CLI tool or SDK for your products beyond drones, for users like me who need to convert hundreds of panorama videos without having to sit in front of a PC all day.**

## Disclaimer

* Read the code before running it.
* Always backup your files before processing.
* This tool invokes external programs (**Java / SikuliX / ExifTool**) and interacts with your system UI.

## Features

### 1. Batch Export DJI `.OSV` Files

Automates exporting `.OSV` files into `.mp4` using SikuliX GUI scripting.

* Supports:

  * `4K`, `6K`, `8K` resolution
  * `low`, `high`, `recommended` bitrate
* Automatically:

  * Opens each `.OSV` file
  * Triggers export via SikuliX
  * Saves output to target directory
* Skips:

  * Already exported files
  * Files before a specified filename (resume support)

### 2. Metadata Synchronization (Post-processing)

Fixes metadata of exported `.mp4` files using `ExifTool`.

* Copies metadata from corresponding `.OSV` file
* Adjusts timezone and timestamps

## Requirements

### Converter (main.py)

The `main.py` and the corresponding `exporter.sikuli/exporter.py` is only test under Windows 10 (and above).

* Windows 10+
* DJI Studio
* Python 3.8+
* OpenJDK
  Download: [https://jdk.java.net/](https://jdk.java.net/)

* SikuliX
  Required file:

  ```
  sikulixapi-2.0.5-win.jar
  ```

  Download: [https://github.com/RaiMan/SikuliX1/releases/tag/v2.0.5](https://github.com/RaiMan/SikuliX1/releases/tag/v2.0.5)

### Utils: Metadata Processing (inject.py)

The utils `inject.py` is only test under debian because my NAS is debian :(.

* Linux
* Python 3.8+
* ExifTool

Install:

```bash
# Debian/Ubuntu
sudo apt install libimage-exiftool-perl
```

## Usage

### 1. Batch Export (`main.py`)

```bash
python main.py <input_dir> <output_dir> [options]
```

| Argument     | Description                          |
| ------------ | ------------------------------------ |
| `input_dir`  | Directory containing `.OSV` files    |
| `output_dir` | Output directory for exported `.mp4` videos |

#### Options

| Option                     | Description                    |
| -------------------------- | ------------------------------ |
| `-r, --resolution`         | `4K`, `6K`, `8K` (default: `4K`) |
| `-b, --bitrate`            | `low`, `high`, `recommended`   (default: `recommended`)|
| `-w, --wait`               | Delay (in second) between automation steps (default: `2.5s`) |
| `-s, --skip-before <file>` | Resume from specific filename  |

#### Example

```bash
python main.py ./input ./output -r 8K -b high
```

#### File Naming

```
CAM_2026XXXXXXXXXX_0001_D.OSV  <->  CAM_2026XXXXXXXXXX_0001_D.panorama.<resolution>.mp4
```

### 2. Metadata Fix (`inject.py`)

```bash
python inject.py "<glob_path>" <timezone> [options]
```

| Argument | Description                                  |
| -------- | -------------------------------------------- |
| `dir`    | Target files (supports glob, e.g. `"*.mp4"`) |

#### Options

| Option             | Description                               |
| ------------------ | ----------------------------------------- |
| `-c, --correct-tz`     | Correct timezone of the footages (e.g. `9` for UTC+9) |
| `-t, --default-tz` | Timezone of the camera timestamp (default: +8) |
| `-f, --overwrite`  | Force overwrite existing metadata         |
| `-d, --debug`      | Print ExifTool command                    |

## Workflow Example

### Step 1: Export `.OSV` files

```bash
python main.py ./osv ./mp4 -r 8K
```

### Step 2: Fix metadata

```bash
python inject.py "./*.mp4" 9
```

The tool assumes:

```
CAM_20251118222532_0001_D.panorama.4K.mp4  <->  CAM_20251118222532_0001_D.OSV
```

Metadata is copied from `.OSV` to `.mp4`. The two files are assumed to be under the same folder.

## License

This script is free to use and modify under the MIT License.
