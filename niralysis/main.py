from niralysis.niralysis import *
import zipfile


if __name__ == "__main__":
    print("Running STORM and OpenPose analysis on demo data...")

    # The explanation to this code is written in the README file under USAGE
    file = Niralysis('demo_data/60_001.snirf')
    file.storm('demo_data/STORM_demo.txt')
    with zipfile.ZipFile('demo_data/sub59_session2_just_experimenter.zop', 'r') as zip_ref:
        zip_ref.extractall('demo_data/openpose_output')
    file.generate_open_pose('demo_data/openpose_output')