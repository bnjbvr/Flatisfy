# coding : utf-8
"""
This module contains all the code related to building necessary data files from
the source opendata files.
"""
from __future__ import absolute_import, print_function, unicode_literals

import collections
import json
import logging
import os
import shutil

import flatisfy.exceptions


LOGGER = logging.getLogger(__name__)
MODULE_DIR = os.path.dirname(os.path.realpath(__file__))


def _preprocess_ratp(output_dir):
    """
    Build RATP file from the RATP data.

    :param output_dir: Directory in which the output file should reside.
    :return: ``True`` on successful build, ``False`` otherwise.
    """
    ratp_data_raw = []
    # Load opendata file
    try:
        with open(os.path.join(MODULE_DIR, "data_files/ratp.json"), "r") as fh:
            ratp_data_raw = json.load(fh)
    except (IOError, ValueError):
        LOGGER.error("Invalid raw RATP opendata file.")
        return False

    # Process it
    ratp_data = collections.defaultdict(list)
    for item in ratp_data_raw:
        stop_name = item["fields"]["stop_name"].lower()
        ratp_data[stop_name].append(item["fields"]["coord"])

    # Output it
    with open(os.path.join(output_dir, "ratp.json"), "w") as fh:
        json.dump(ratp_data, fh)

    return True


def _preprocess_laposte(output_dir):
    """
    Build JSON files from the postal codes data.

    :param output_dir: Directory in which the output file should reside.
    :return: ``True`` on successful build, ``False`` otherwise.
    """
    raw_laposte_data = []
    # Load opendata file
    try:
        with open(
            os.path.join(MODULE_DIR, "data_files/laposte.json"), "r"
        ) as fh:
            raw_laposte_data = json.load(fh)
    except (IOError, ValueError):
        LOGGER.error("Invalid raw LaPoste opendata file.")
        return False

    # Build postal codes to other infos file
    postal_codes_data = {}
    for item in raw_laposte_data:
        try:
            postal_codes_data[item["fields"]["code_postal"]] = {
                "gps": item["fields"]["coordonnees_gps"],
                "nom": item["fields"]["nom_de_la_commune"].title()
            }
        except KeyError:
            LOGGER.info("Missing data for postal code %s, skipping it.",
                        item["fields"]["code_postal"])
    with open(os.path.join(output_dir, "postal_codes.json"), "w") as fh:
        json.dump(postal_codes_data, fh)

    # Build city name to postal codes and other infos file
    cities_data = {}
    for item in raw_laposte_data:
        try:
            cities_data[item["fields"]["nom_de_la_commune"].title()] = {
                "gps": item["fields"]["coordonnees_gps"],
                "postal_code": item["fields"]["code_postal"]
            }
        except KeyError:
            LOGGER.info("Missing data for city %s, skipping it.",
                        item["fields"]["nom_de_la_commune"])
    with open(os.path.join(output_dir, "cities.json"), "w") as fh:
        json.dump(cities_data, fh)

    return True


def preprocess_data(config, force=False):
    """
    Ensures that all the necessary data files have been built from the raw
    opendata files.

    :params config: A config dictionary.
    :params force: Whether to force rebuild or not.
    """
    LOGGER.debug("Data directory is %s.", config["data_directory"])
    opendata_directory = os.path.join(config["data_directory"], "opendata")
    try:
        LOGGER.info("Ensuring the data directory exists.")
        os.makedirs(opendata_directory)
        LOGGER.debug("Created opendata directory at %s.", opendata_directory)
    except OSError:
        LOGGER.debug("Opendata directory already existed, doing nothing.")

    is_built_ratp = os.path.isfile(
        os.path.join(opendata_directory, "ratp.json")
    )
    if not is_built_ratp or force:
        LOGGER.info("Building from RATP data.")
        if not _preprocess_ratp(opendata_directory):
            raise flatisfy.exceptions.DataBuildError("Error with RATP data.")

    is_built_laposte = (
        os.path.isfile(os.path.join(opendata_directory, "cities.json")) and
        os.path.isfile(os.path.join(opendata_directory, "postal_codes.json"))
    )
    if not is_built_laposte or force:
        LOGGER.info("Building from LaPoste data.")
        if not _preprocess_laposte(opendata_directory):
            raise flatisfy.exceptions.DataBuildError(
                "Error with LaPoste data."
            )


def load_data(data_type, config):
    """
    Load a given built data file.

    :param data_type: A valid data identifier.
    :param config: A config dictionary.
    :return: The loaded data. ``None`` if the query is incorrect.
    """
    if data_type not in ["postal_codes", "cities", "ratp"]:
        LOGGER.error("Invalid request. No %s data file.", data_type)
        return None

    opendata_directory = os.path.join(config["data_directory"], "opendata")
    datafile_path = os.path.join(opendata_directory, "%s.json" % data_type)
    data = {}
    try:
        with open(datafile_path, "r") as fh:
            data = json.load(fh)
    except IOError:
        LOGGER.error("No such data file: %s.", datafile_path)
        return None
    except ValueError:
        LOGGER.error("Invalid JSON data file: %s.", datafile_path)
        return None

    if not data:
        LOGGER.warning("Loading empty data for %s.", data_type)

    return data
