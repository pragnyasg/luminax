import os
import sys
import xml.etree.ElementTree as ET
import xacro

def validate_urdf_tree(xml_string, name="URDF"):
    print(f"\n================ VALIDATING {name} ================")
    root = ET.fromstring(xml_string)
    assert root.tag == "robot", f"Expected <robot>, got <{root.tag}>"
    robot_name = root.attrib.get("name", "unnamed")
    print(f"Robot Name: {robot_name}")

    links = {}
    for link in root.findall("link"):
        lname = link.attrib.get("name")
        visuals = link.findall("visual")
        collisions = link.findall("collision")
        inertials = link.findall("inertial")
        links[lname] = {
            "visuals": len(visuals),
            "collisions": len(collisions),
            "inertials": len(inertials)
        }

    joints = {}
    parent_child = {}
    for joint in root.findall("joint"):
        jname = joint.attrib.get("name")
        jtype = joint.attrib.get("type")
        parent = joint.find("parent").attrib.get("link")
        child = joint.find("child").attrib.get("link")
        origin = joint.find("origin")
        axis = joint.find("axis")
        xyz = origin.attrib.get("xyz", "0 0 0") if origin is not None else "0 0 0"
        rpy = origin.attrib.get("rpy", "0 0 0") if origin is not None else "0 0 0"
        axis_xyz = axis.attrib.get("xyz") if axis is not None else None

        joints[jname] = {
            "type": jtype,
            "parent": parent,
            "child": child,
            "xyz": xyz,
            "rpy": rpy,
            "axis": axis_xyz
        }
        parent_child[child] = (jname, parent)

    print(f"Total Links: {len(links)}")
    print(f"Total Joints: {len(joints)}")

    # Check for missing parent or child link definitions
    for jname, jinfo in joints.items():
        assert jinfo["parent"] in links, f"Joint '{jname}' parent link '{jinfo['parent']}' not defined!"
        assert jinfo["child"] in links, f"Joint '{jname}' child link '{jinfo['child']}' not defined!"

    # Find root links (links that are not children of any joint)
    root_links = [l for l in links if l not in parent_child]
    print(f"Root Link(s): {root_links}")
    assert len(root_links) == 1, f"Expected exactly 1 kinematic root, found {len(root_links)}: {root_links}"

    return root, links, joints, root_links[0]

# 1. Test luminax.urdf.xacro
lum_xacro_path = r"c:\Users\pragn\OneDrive\Desktop\luminax\luminax_ws\src\luminax_description\urdf\luminax.urdf.xacro"
doc1 = xacro.process_file(lum_xacro_path)
xml1 = doc1.toprettyxml(indent="  ")
root1, links1, joints1, root_l1 = validate_urdf_tree(xml1, "luminax.urdf.xacro")

# 2. Test healthcare_robot.urdf.xacro
hc_xacro_path = r"c:\Users\pragn\OneDrive\Desktop\luminax\robot_ws\src\robot_description\urdf\healthcare_robot.urdf.xacro"
doc2 = xacro.process_file(hc_xacro_path)
xml2 = doc2.toprettyxml(indent="  ")
root2, links2, joints2, root_l2 = validate_urdf_tree(xml2, "healthcare_robot.urdf.xacro")

# 3. Test static luminax.urdf
lum_urdf_path = r"c:\Users\pragn\OneDrive\Desktop\luminax\luminax_ws\src\luminax_description\urdf\luminax.urdf"
with open(lum_urdf_path, "r", encoding="utf-8") as f:
    xml3 = f.read()
root3, links3, joints3, root_l3 = validate_urdf_tree(xml3, "static luminax.urdf")

print("\nALL 3 FILES PARSED AND STRUCTURE-VALIDATED SUCCESSFULLY!")
