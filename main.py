from time import sleep
from glob import glob
from tqdm import tqdm
import subprocess
import argparse
import shutil
import sys
import os

SIKULI_JAR          = "sikulixapi-2.0.5-win.jar"
SIKULI_DOWNLOAD_URL = "https://github.com/RaiMan/SikuliX1/releases/tag/v2.0.5"
JAVA_DOWNLOAD_URL   = "https://jdk.java.net/"

def check_environment():
    """Check that Java and the SikuliX jar are available before running."""
    ok = True

    if shutil.which("java") is None:
        print("[ERROR] Java is not installed or not found in PATH.")
        print(f"        Please download and install Java from: {JAVA_DOWNLOAD_URL}")
        ok = False

    if not os.path.isfile(SIKULI_JAR):
        print(f"[ERROR] SikuliX jar not found: {SIKULI_JAR}")
        print(f"        Please download it and place the jar in the project directory: {SIKULI_DOWNLOAD_URL}")
        ok = False

    return ok


def run_sikuli(outputpath, resolution='8K', bitrate='recommended', wait=2.5):
    """Invoke SikuliX to automate the export process for a single file.

    Args:
        outputpath:  Absolute path for the exported video file.
        resolution:  Export resolution ('4K', '6K', or '8K').
        bitrate:     Export bitrate ('low', 'high', or 'recommended').
        wait:        Seconds to wait between SikuliX interaction steps.

    Returns:
        True if SikuliX exited successfully, False otherwise.
    """
    sikuli_jar  = SIKULI_JAR
    script_path = "exporter.sikuli"

    outputpath = os.path.abspath(outputpath)

    # wait must be a string; subprocess requires all arguments to be str
    cmd = ["java", "-jar", sikuli_jar, "-r", script_path,
           "--args", outputpath, resolution, bitrate, str(wait)]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"SikuliX: Failed\n{e}")
        return False

    print("SikuliX: Finished")
    return True


if __name__ == '__main__':
    # Abort early if the required environment is not set up
    if not check_environment():
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="Batch-export DJI 360 .OSV files via SikuliX automation."
    )
    parser.add_argument("input_dir",  help="Directory containing .OSV input files (supports glob expressions)")
    parser.add_argument("output_dir", help="Directory where exported video files will be saved")
    parser.add_argument("-r", "--resolution", default="4K", choices=["4K", "6K", "8K"],
                        help="Export resolution (default: 4K)")
    parser.add_argument("-b", "--bitrate", default="recommended", choices=["low", "high", "recommended"],
                        help="Export bitrate (default: recommended)")
    parser.add_argument("-w", "--wait", type=float, default=2.5,
                        help="Wait time in seconds between SikuliX steps (default: 2.5). Modify it to improve performance based on you computer.")
    parser.add_argument("-s", "--skip-before", default=None, metavar="FILENAME",
                        help="Skip all files before this filename (the named file is processed normally)")

    args = parser.parse_args()

    input_dir   = args.input_dir
    output_dir  = args.output_dir
    resolution  = args.resolution
    bitrate     = args.bitrate
    wait        = args.wait
    skip_before = args.skip_before

    os.makedirs(output_dir, exist_ok=True)

    for file in tqdm(sorted(glob(os.path.join(input_dir, "*.OSV")))):
        # Skip files that appear before the requested starting filename.
        # Once the target filename is matched, clear the flag and process it normally.
        if skip_before is not None:
            if skip_before == os.path.basename(file):
                skip_before = None
            else:
                print(f"Skipped: {file}")
                continue

        outputfilename = os.path.basename(file).replace('.OSV', f'.panorama.{resolution}.mp4')
        outputpath     = os.path.join(output_dir, outputfilename)

        # Skip files that have already been exported
        if os.path.exists(outputpath):
            print(f"Already exists, skipped: {outputfilename}")
            continue

        # Open the .OSV file and give the application time to load
        os.startfile(file)
        sleep(4)

        if not run_sikuli(outputpath, resolution=resolution, bitrate=bitrate, wait=wait):
            print(f"Task failed: {outputfilename}")
            break

    print("Done.")