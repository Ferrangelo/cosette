"""
This module contains various utility functions.

The functions in this module provide support for different operations,
including LaTeX conversions and other miscellaneous tasks that are used
across many of my projects.

Functions:
    find_classy(cosmo_directory): Find and import a given installation of classy.
    latex_pnames(pnames): Convert parameter names to LaTeX representations.
    exclude_nuisance(excl_nuis, ...): Exclude parameters from cosmological and nuisance sets.
    delete_burn_in(folder, file, burn_in): Remove burn-in period from data files.

Note: More functions may be added to this module as the project evolves.
"""

import glob
import json
import os
import sys
from pathlib import Path


def find_classy(cosmo_directory):
    """
    Finds and imports the CLASS library.
    """

    for elem in os.listdir(os.path.join(cosmo_directory, "python", "build")):
        if elem.find("lib.") != -1:
            classy_path = os.path.join(cosmo_directory, "python", "build", elem)
            break

    # Inserting the previously found path into the list of folders to
    # search for python modules.
    sys.path.insert(1, classy_path)


def latex_pnames(pnames):
    """
    Convert a list of parameter names to their LaTeX representations.
    The input parameter names are expected to be in the SFX_CLASS format.

    This function takes a list of parameter names and returns a new list with the
    corresponding LaTeX representations. It uses a dictionary to map common parameter
    names to their LaTeX forms, and also handles parameter names in the form 'b{i}'
    and 'm{i}' where 'i' is an integer.

    Args:
        pnames (list): A list of parameter names to be converted to LaTeX.

    Returns:
        list: A new list with the LaTeX representations of the input parameter names.
    """
    latex_dict = {
        "w0": r"w_0",
        "wa": r"w_{\rm a}",
        "ob": r"\Omega_{\rm b}",
        "om": r"\Omega_{\rm m}",
        "sigma8": r"\sigma_8",
        "tau": r"\tau",
        "ns": r"n_{\rm s}",
        "h": r"h",
        "delta_IG": r"\Delta",
        "Delta": r"\Delta",
        "gamma_IG": r"\xi",
        "mnu": r"\sum m_{\nu} \rm [eV]",
        "aIA": r"{\cal A}_{\rm IA}",
        "eIA": r"\eta_{\rm IA}",
        "bIA": r"\beta_{\rm IA}",
    }
    latex_dict.update({f"b{i}": rf"b_{{{i}}}" for i in range(14)})
    latex_dict.update({f"bM{i}": rf"b_{{\rm M, {i}}}" for i in range(14)})
    latex_dict.update({f"m{i}": rf"m_{{{i}}}" for i in range(14)})

    return [latex_dict.get(p, p) for p in pnames]


def exclude_nuisance(
    excl_nuis, tau=True, mnu=False, only_shear_bias=False, nuis_without_shear_bias=False
):
    """
    Exclude parameters from a set of cosmological and nuisance parameters.

    This function takes a list of parameters and determines which ones to exclude based on the provided flags.
    It returns the list of excluded parameters and the type of parameters (cosmological or nuisance) that were excluded.

    Args:
        excl_nuis (bool): if True, exclude the nuisance parameters. If False, exclude the cosmological parameters.
        tau (bool): if True, put tau in the excluded list.
        mnu (bool): if True, put mnu in the excluded list.
        only_shear_bias (bool): if True, exclude all parameters except the shear bias parameters.
        nuis_without_shear_bias:

    Returns:
        list: the list of excluded parameters.
        str: the type of parameters that were excluded ('cosmo' or 'nuisance').
    """

    project_root = Path(__file__).parent.parent.parent
    constants_lists_file_path = project_root / "params_lists.json"
    with open(constants_lists_file_path, "r", encoding="utf-8") as file:
        constants_lists = json.load(file)

    cosmo_list = constants_lists["cosmo"]
    nuisance_list = constants_lists["nuisance"]
    all_but_shear_bias_list = constants_lists["all_but_shear_bias"]
    shear_bias_list = constants_lists["shear_bias"]

    if only_shear_bias:
        exclude = all_but_shear_bias_list
        partype = "nuisance"
    elif excl_nuis is True:
        if mnu is True:
            nuisance_list.insert(0, "mnu")
        if tau is True:
            nuisance_list.insert(0, "tau")
        exclude = nuisance_list
        partype = "cosmo"
    else:
        if nuis_without_shear_bias:
            exclude = cosmo_list + shear_bias_list
        else:
            exclude = cosmo_list
        partype = "nuisance"

    return exclude, partype


def delete_burn_in(folder, file, burn_in):
    """
    Removes the burn-in period from a set of files in a given folder.

    Args:
        folder (str): The folder containing the files to be processed.
        file (str): The base name of the files to be processed.
        burn_in (float): The fraction of the data to be removed as burn-in.

    This function reads the files matching the given pattern in the specified folder,
    keeps the header line, and removes the first `burn_in` fraction of the remaining lines.
    The modified data is then written back to the original files.
    """

    folder = "emg_cc_P18_desi_wideV0"
    file_pattern = os.path.join(folder, file + ".*.txt")
    files = glob.glob(file_pattern)

    for file_path in files:
        # Read the file
        with open(file_path, "r") as f:
            lines = f.readlines()

        # Keep the header (first line)
        header = lines[0]

        # Get remaining lines and calculate middle point
        remaining_lines = lines[1:]
        point_forward = len(remaining_lines) * burn_in

        # Keep only second part of remaining lines
        selected_lines = remaining_lines[point_forward - 1 :]

        # Write back to file
        with open(file_path, "w") as f:
            f.write(header)  # Write header first
            f.writelines(selected_lines)  # Write selected lines