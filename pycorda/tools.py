import requests
from xml.etree import ElementTree


class DBTools:
    def __init__(self, db_type=None):
        """
        DBTools to download the required database driver.  Default is H2.

        Parameters
        ----------
        db_type : str
            DB type to retrieve correct driver
        """
        self.db_type = db_type
        url_maven = "https://repo1.maven.org/maven2"

        if db_type == "pg":
            self.maven_path = url_maven + "/org/postgresql/postgresql/"
            self.prefix = "/postgresql-"
        elif db_type is None:
            self.maven_path = url_maven + "/com/h2database/h2/"
            self.prefix = "/h2-"

        self.meta_path = self.maven_path + "maven-metadata.xml"

    def get_latest_version(self):
        """Returns the latest version string for the database driver"""
        r = requests.get(self.meta_path)
        tree = ElementTree.fromstring(r.content)
        return tree.find('versioning').find('latest').text

    def get_jar_url(self, version):
        url = self.maven_path
        url += version + self.prefix + version + ".jar"
        return url

    def download_jar(self, filepath='./db_driver.jar', version=None):
        """Downloads driver jar and copies it to a file in filepath"""
        if version is None:
            version = self.get_latest_version()
        r = requests.get(self.get_jar_url(version))
        with open(filepath, 'wb') as jarfile:
            jarfile.write(r.content)
