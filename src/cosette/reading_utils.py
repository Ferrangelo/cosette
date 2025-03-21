import re

import numpy as np


def read_class_file_headers(file_path):
    """
    Read and parse headers from a CLASS output file.

    This function reads a file and extracts column headers from comments starting with '#'.
    It processes the last header line to extract column names by splitting on 'number:' patterns.

    Args:
        file_path (str or Path): Path to the CLASS output file.

    Returns:
        list[str]: List of column headers extracted from the file.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If no headers (lines starting with '#') are found in the file.
    """
    try:
        headers = []

        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if line.startswith("#"):
                    headers.append(
                        line[1:].strip()
                    )  # Remove the # and any leading/trailing whitespace
                else:
                    break  # Stop reading when we encounter a non-header line

        if not headers:
            raise ValueError(f"No headers found in file: {file_path}")

        # Process the last header line to get column names
        # Split the last string by number and colon pattern
        parts = re.split(r"\d+:", headers[-1])

        # Remove empty strings and strip whitespace
        column_headers = [part.strip() for part in parts if part.strip()]

        return column_headers

    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")


def read_sfx_class_cls_file(nbins, cl_filepath):
    """
    Reads the angular power spectra from an sfx_class output file and returns them as a dictionary.

    Args:
        nbins (int): The number of bins.
        cl_filepath (str): The file path to the file.

    Returns:
        dict: A dictionary containing the SHCs for different power spectra, including:
            - 'l': The multipole moments of CMB.
            - 'lls': The multipole of LSS.
            - 'tt', 'ee', 'te', 'pp': The temperature, E-mode, temperature-E-mode, and polarization power spectra.
            - ',
            'dd_auto', 'll_auto', 'ii_auto': The auto power spectra for density, lensing, and cosmic infrared background.
            - 'dd', 'll', 'ii': The cross-correlations between redshift bins for for density, lensing, and intrinsic alignment.
            - td', 'dl', 'di', 'il': The cross-correlation power spectra for density-temperature, density-lensing, density-IA, and lensing-IA.
    """
    all_cl = np.load(cl_filepath, allow_pickle=True)["all_cl"].item()
    all_cl.keys()

    l = all_cl["ell1"]
    lls = all_cl["ell2"]
    tt = all_cl["tt"]
    ee = all_cl["ee"]
    te = all_cl["te"]
    pp = all_cl["pp"]
    tp = all_cl["tp"]
    ep = all_cl["ep"]

    td = {}
    dd_auto = {}
    ll_auto = {}
    ii_auto = {}
    dd = {}
    ll = {}
    ii = {}
    dl = {}
    di = {}
    il = {}

    for bin1 in range(nbins):
        dd[bin1] = {}
        ll[bin1] = {}
        ii[bin1] = {}
        dl[bin1] = {}
        di[bin1] = {}
        il[bin1] = {}

        td[bin1] = all_cl["td" + str(bin1)]
        dd_auto[bin1] = all_cl[("d" + str(bin1)) * 2]
        ll_auto[bin1] = all_cl[("l" + str(bin1)) * 2]
        ii_auto[bin1] = all_cl.get(("i" + str(bin1)) * 2)

        for bin2 in range(bin1, nbins):
            dd[bin1][bin2] = all_cl["d" + str(bin1) + "d" + str(bin2)]
            ll[bin1][bin2] = all_cl["l" + str(bin1) + "l" + str(bin2)]
            ii[bin1][bin2] = all_cl.get("i" + str(bin1) + "i" + str(bin2))

        for bin2 in range(nbins):
            dl[bin1][bin2] = all_cl["d" + str(bin1) + "l" + str(bin2)]
            di[bin1][bin2] = all_cl.get("d" + str(bin1) + "i" + str(bin2))
            il[bin1][bin2] = all_cl.get("i" + str(bin1) + "l" + str(bin2))

    dict_cl = {
        "l": l,
        "lls": lls,
        "tt": tt,
        "ee": ee,
        "te": te,
        "pp": pp,
        "tp": tp,
        "ep": ep,
        "dd": dd,
        "ll": ll,
        "ii": ii,
        "td": td,
        "dd_auto": dd_auto,
        "ll_auto": ll_auto,
        "ii_auto": ii_auto,
        "dl": dl,
        "di": di,
        "il": il,
    }

    return dict_cl
