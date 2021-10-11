import configparser
import os

import pandas as pd
import folium

from github import Github
from io import StringIO


env = os.getenv("ENV", "dev")

if env == "dev":
    config = configparser.ConfigParser()
    config.read(".config")
    config = config["GITHUB"]
else:
    config = {
        "TOKEN": os.getenv("GITHUB_TOKEN", "yourTokenFromGitHub"),
        "REPO": os.getenv("GITHUB_REPO", "yourGitHubRepo"),
    }


def load_data():
    """Loads dataset from places.csv using pandas

    Returns:
        df: A Pandas.DataFrame containing all stored data
    """
    github = Github(config["TOKEN"])
    repository = github.get_user().get_repo(config["REPO"])
    file = repository.get_contents('places.csv')
    return pd.read_csv(StringIO(file.decoded_content.decode()))


def save_data(dataset):
    """Saves new data points to dataset in places.csv using pandas

    Args:
        dataset: required, Pandas.DataFrame with locations
    """
    github = Github(config["TOKEN"])
    repository = github.get_user().get_repo(config["REPO"])

    # file info
    filename = 'places.csv'
    sha = repository.get_contents(filename).sha

    s = StringIO()
    dataset.to_csv(s, index=False)
    content = s.getvalue()

    # create with commit message
    commit_message = "Update data via PyGithub"
    repository.update_file(filename, commit_message, content, sha)


def creates_standard_map():
    """Creates a standard map with folium

    Returns:
        map: A folium.Map
    """
    center = (13.133932434766733, 16.103938729508073)
    return folium.Map(location=center, zoom_start=3)


def adds_markers(my_map, dataset):
    """Adds Markers to map from each place in dataset

    Args:
        my_map: required, folium.Map standard map to add markers
        dataset: required, Pandas.DataFrame with locations

    Return:
        my_map: A folium.Map with marker layers
    """

    for _, place in dataset.iterrows():
        folium.Marker(
            location=[place['latitude'], place['longitude']],
            popup=place['name'],
            tooltip=place['name']
        ).add_to(my_map)

    return my_map


def create_map():
    """Adds markers and creates HTML file for the map

    Return:
        created: bool, True if map was successfully saved, False otherwise
    """
    try:
        df = load_data()
        my_map = creates_standard_map()
        marked_map = adds_markers(my_map, df)
        marked_map.save('templates/index.html')
    except:
        return False
    return True


def create_new_place(place_data):
    """Adds new lines to the dataset and then saves the data

    Args:
        place_data: dict, A dictionary containing a new place data

    Return:
        created: bool, True if map was successfully saved, False otherwise
    """
    df = load_data()
    result = df.append(place_data, ignore_index=True)
    result = result.drop_duplicates(keep=False)
    save_data(result)
