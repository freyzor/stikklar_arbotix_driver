"""
script to generate arbotix_driver compatible yaml config file
"""
# from the urdfdom-py package
from urdf_parser_py.urdf import URDF
import yaml
import math

# make sure we have and up to date version by running
# rosrun xacro xacro.py stikklar.urdf.xacro > stikklar.urdf

urdf_file = "/home/freyr/catkin_ws/src/stikklar_description/urdf/stikklar.urdf"
yaml_file = "stikklar.yaml"

SERVO_ID_MAP = {
    "rf": {"coxa": 1, "femur": 2, "tibia": 3, "wheel": 4},
    "rr": {"coxa": 5, "femur": 6, "tibia": 7, "wheel": 8},
    "lf": {"coxa": 9, "femur": 10, "tibia": 11, "wheel": 12},
    "lr": {"coxa": 13, "femur": 14, "tibia": 15, "wheel": 16},
    "neck": {"pan": 17, "tilt": 18},
}

SERVO_INVERTED_MAP = {
    "rf": {"coxa": False, "femur": False, "tibia": True, "wheel": True},
    "rr": {"coxa": True, "femur": False, "tibia": True, "wheel": False},
    "lf": {"coxa": True, "femur": False, "tibia": True, "wheel": False},
    "lr": {"coxa": False, "femur": False, "tibia": True, "wheel": True},
    "neck": {"pan": False, "tilt": False},
}


def create_default_arbotix_config():
    return {
        "port": "/dev/ttyUSB0",
        "baud": "115200",
        "rate": 20.0,
        "sim": True,
        "sync_read": True,
        "sync_write": True,
        "joints": {},
        "controllers": {},
    }


def get_joint_value(name, value_map):
    for prefix, limb_map in value_map.iteritems():
        if name.startswith(prefix):
            for part, value in limb_map.iteritems():
                if part in name:
                    return value


def get_id(name):
    return get_joint_value(name, SERVO_ID_MAP)


def get_inverted(name):
    return get_joint_value(name, SERVO_INVERTED_MAP)


def get_joint_dict_from_urdf(joint):
    info = {
        "type": "dynamixel",
        "id": get_id(joint.name),
        "max_angle": math.degrees(joint.limit.upper),
        "min_angle": math.degrees(joint.limit.lower),
        # "max_speed": joint.limit.velocity,
        "inverted": get_inverted(joint.name),
        "readable": True,
    }
    return info


def get_continuous_joint_dict_from_urdf(joint):
    info = {
        "type": "dynamixel",
        "id": get_id(joint.name),
        "max_angle": 180,
        "min_angle": -180,
        # "max_speed": 100,
        "inverted": get_inverted(joint.name),
        "readable": False,
    }
    return info


def create_arbotix_joint_config(robot):
    joints = {}
    for joint in robot.joint_map.itervalues():
        if joint.type == "revolute":
            joints[joint.name] = get_joint_dict_from_urdf(joint)
        elif joint.type == "continuous":
            joints[joint.name] = get_continuous_joint_dict_from_urdf(joint)
    return joints


def write_yaml_config_file(data):
    with open(yaml_file, "w") as f:
        f.write(yaml.dump(data, default_flow_style=False))


def generate_yaml():
    robot = URDF.from_xml_file(urdf_file)
    data = create_default_arbotix_config()
    data["joints"] = create_arbotix_joint_config(robot)
    write_yaml_config_file(data)

if __name__ == '__main__':
    generate_yaml()
