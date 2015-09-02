from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import (ascii, bytes, chr, dict, filter, hex, input,
                      int, map, next, oct, open, pow, range, round,
                      str, super, zip)

from io import StringIO

import pandas as pd

from .base import ServerBase, DEFAULT_SCHEMA
from .dataset import Dataset


class Database(ServerBase):

    """Biomart database.

    Represents a specific database on the biomart server.

    Attributes:
        name (str): Name of the database.
        display_name (str): Display name of the database.
        database_name (str): ID of the database on the host.
        datasets (list of Datasets): List of datasets in this database.

    """

    RESULT_COLNAMES = ['type', 'name', 'display_name', 'unknown', 'unknown2',
                       'unknown3', 'unknown4', 'virtual_schema', 'unknown5']

    def __init__(self, name, database_name, display_name,
                 host=None, path=None, port=None, use_cache=True,
                 virtual_schema=DEFAULT_SCHEMA, extra_params=None):
        """Database constructor.

        Args:
            name (str): Name of the database.
            database_name (str): ID of the database on the host.
            display_name (str): Display name of the database.
            host (str): Url of host to connect to.
            path (str): Path on the host to access to the biomart service.
            port (int): Port to use for the connection.
            use_cache (bool): Whether to cache requests.
            virtual_schema (str): The virtual schema of the dataset.

        Examples:
            Getting the database:
                >>> from pybiomart import Server
                >>> server = Server(host='http://www.ensembl.org')
                >>> database = server.databases['ENSEMBL_MART_ENSEMBL']

            Getting a database from the database:
                >>> database.datasets['hsapiens_gene_ensembl']

        """

        super().__init__(host=host, path=path,
                         port=port, use_cache=use_cache)

        self._name = name
        self._database_name = database_name
        self._display_name = display_name

        self._virtual_schema = virtual_schema
        self._extra_params = extra_params

        self._datasets = None

    def __getitem__(self, name):
        return self.datasets[name]

    @property
    def name(self):
        """Name of the database."""
        return self._name

    @property
    def display_name(self):
        """Display name of the database."""
        return self._display_name

    @property
    def database_name(self):
        """ID of the mart on the host."""
        return self._database_name

    @property
    def datasets(self):
        """List of datasets in this database."""
        if self._datasets is None:
            self._datasets = self._fetch_datasets()
        return self._datasets

    def _fetch_datasets(self):
        # Get datasets using biomart.
        response = self.get(type='datasets', mart=self._name)

        # Read result frame from response.
        result = pd.read_csv(StringIO(response.text), sep='\t',
                             header=None, names=self.RESULT_COLNAMES)

        # Convert result to a dict of datasets.
        datasets = (self._dataset_from_row(row)
                    for _, row in result.iterrows())

        return {d.name: d for d in datasets}

    def _dataset_from_row(self, row):
        return Dataset(name=row['name'], display_name=row['display_name'],
                       host=self.host, path=self.path,
                       port=self.port, use_cache=self.use_cache,
                       virtual_schema=row['virtual_schema'])

    def __repr__(self):
        return (('<biomart.Mart name={!r}, database_name={!r},'
                 ' display_name={!r}>')
                .format(self._name, self._display_name,
                        self._database_name, self.host, self.path))