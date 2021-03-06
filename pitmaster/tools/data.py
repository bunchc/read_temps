#   Copyright 2016 Michael Rice <michael@michaelrice.org>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
from CodernityDB.database_thread_safe import ThreadSafeDatabase as Database
from CodernityDB.database import DatabaseConflict

from pitmaster.exceptions import *


class DBObject(object):

    def __init__(self, filename=None):
        """

        :param filename:
        :return:
        """
        self.db = Database(filename)
        if self.db.exists():
            self._open_db()
            self.db.reindex()
        else:
            self.db.create()

    def _open_db(self):
        try:
            self.db.open()
        except DatabaseConflict:
            pass

    def save(self, info=None):
        """

        :param info:
        :return:
        """
        if info is None:
            raise MissingPropertyException("info must not be None!")
        self._open_db()
        self.db.insert(info)

    def reindex(self):
        """
        Does a reindex of the database.
        :return:
        """
        self._open_db()
        self.db.reindex()

    def list_all(self):
        return self.db.all("id")

