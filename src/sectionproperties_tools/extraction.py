from __future__ import annotations
import numpy as np
from typing import Optional
from sectionproperties.analysis.section import Section
from sectionproperties.post.stress_post import StressPost

def extract_properties(
    analysis_section: Section,
    subset_to_extract: Optional[str] = None,
) -> dict[str, float]:
    """
    Extracts the properties from the solved 'analysis_section'.

    'analysis_section': a solved Section from sectionproperties.
    'subset_to_extract': One of {"geometric", "warping", "plastic"}
        The results extracted will be from one of these sets
        of properties. If None, then all results will be extracted.
    'properties_to_extract': If provided, will extract only the 
        properties from the provided list. If None, will extract
        all sectionproperties.


        The following properties can be specified when materials
        are _not_ added to the section (i.e. a geometric analysis):
        [
            'area', 'perimeter', 'mass', 'ea', 'ga', 'nu_eff', 'e_eff', 
            'g_eff', 'qx', 'qy', 'ixx_g', 'iyy_g', 'ixy_g', 'cx', 'cy', 
            'ixx_c', 'iyy_c', 'ixy_c', 'zxx_plus', 'zxx_minus', 'zyy_plus', 
            'zyy_minus', 'rx_c', 'ry_c', 'i11_c', 'i22_c', 'phi', 'z11_plus', 
            'z11_minus', 'z22_plus', 'z22_minus', 'r11_c', 'r22_c', 'j', 
            'my_xx', 'my_yy', 'my_11', 'my_22', 'delta_s', 'x_se', 'y_se', 
            'x11_se', 'y22_se', 'x_st', 'y_st', 'gamma', 'a_sx', 'a_sy', 
            'a_sxy', 'a_s11', 'a_s22', 'beta_x_plus', 'beta_x_minus', 
            'beta_y_plus', 'beta_y_minus', 'beta_11_plus', 'beta_11_minus', 
            'beta_22_plus', 'beta_22_minus', 'x_pc', 'y_pc', 'x11_pc', 
            'y22_pc', 'sxx', 'syy', 'sf_xx_plus', 'sf_xx_minus', 'sf_yy_plus', 
            'sf_yy_minus', 's11', 's22', 'sf_11_plus', 'sf_11_minus', 
            'sf_22_plus', 'sf_22_minus'
        ]

        
        The following properties can be specified when matierals
        ARE added to the section (i.e. a composite analysis). This
        applies even if it is only one material:
        [
            'area', 'perimeter', 'mass', 'ea', 'ga', 'nu_eff', 'e_eff', 
            'g_eff', 'qx', 'qy', 'ixx_g', 'iyy_g', 'ixy_g', 'cx', 'cy', 
            'ixx_c', 'iyy_c', 'ixy_c', 'zxx_plus', 'zxx_minus', 'zyy_plus', 
            'zyy_minus', 'rx_c', 'ry_c', 'i11_c', 'i22_c', 'phi', 'z11_plus', 
            'z11_minus', 'z22_plus', 'z22_minus', 'r11_c', 'r22_c', 'j', 
            'my_xx', 'my_yy', 'my_11', 'my_22', 'omega', 'psi_shear', 
            'phi_shear', 'delta_s', 'x_se', 'y_se', 'x11_se', 'y22_se', 
            'x_st', 'y_st', 'gamma', 'a_sx', 'a_sy', 'a_sxy', 'a_s11', 
            'a_s22', 'beta_x_plus', 'beta_x_minus', 'beta_y_plus', 
            'beta_y_minus', 'beta_11_plus', 'beta_11_minus', 'beta_22_plus', 
            'beta_22_minus', 'x_pc', 'y_pc', 'x11_pc', 'y22_pc', 'sxx', 'syy', 
            'sf_xx_plus', 'sf_xx_minus', 'sf_yy_plus', 'sf_yy_minus', 's11', 
            's22', 'sf_11_plus', 'sf_11_minus', 'sf_22_plus', 'sf_22_minus'
        ]

    """
    props = analysis_section.section_props.asdict()

    # These are arrays of intermediate values and are not 
    # intended to be outputs.
    props.pop("omega")
    props.pop("psi_shear")
    props.pop("phi_shear")

    if subset_to_extract is not None:
        subset = {}
        for prop in subset_to_extract:
            if prop in props:
                subset.update({prop: props[prop]})
        return subset
    else:
        return props
    

def envelope_stress_results(stress_post: StressPost, single_material: bool = False) -> dict[str, dict]:
    """
    Returns the envelope (min/max/absmax) of the stress results.

    The names (keys) of the stress results are modified to match the names
    used in sectionproperties's stress plots. e.g. "sig_zz_mxx" becomes "mxx_zz".

    If 'single_material' is True and the 'stress_post' object represents stresses
    that only occur in a single material, then the results will not be keyed by 
    material name unnecessarily. If either is False, then the returned dict
    will be keyed by material.
    """
    stress_results = stress_post.get_stress()
    stress_envelopes = {}
    nest_by_material = True
    if len(stress_results) == 1 and single_material:
        nest_by_material = False
    for material_stresses in stress_results:
        material_name = material_stresses.pop("material")
        stress_acc = stress_envelopes
        if nest_by_material:
            stress_envelopes.setdefault(material_name, {})
            stress_acc = stress_envelopes[material_name]
        for stress_dir_name, stress_array in material_stresses.items():
            trimmed_stress_name = "_".join(stress_dir_name.replace("sig_", "").split("_")[::-1])
            stress_acc.setdefault(trimmed_stress_name, {})
            max_stress = np.max(stress_array)
            min_stress = np.min(stress_array)
            absmax_stress = np.max(np.abs(stress_array))
            stress_acc[trimmed_stress_name].update({"max": max_stress})
            stress_acc[trimmed_stress_name].update({"min": min_stress})
            stress_acc[trimmed_stress_name].update({"absmax": absmax_stress})
    return stress_envelopes