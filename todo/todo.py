from contextlib import suppress
from string import ascii_uppercase, digits
from time import strftime, strptime

from .exceptions import TDItemException


# TODO: Logging
DATE_FORMAT = "%Y-%m-%d"


class ToDoList:
    """

    """
    def __init__(self, filename=None):
        self.filename = filename
        self._items = []
        pass

    def __enter__(self):
        pass

    def __exit__(self):
        pass

    def open(self):
        # should be load?
        try:
            with open(self.filename) as f:
                for line in f:
                    self._items.append(ToDoItem(line=line))
        except FileNotFoundError:
            # TODO: Do things here, raise own exception or just raise this?
            pass

    def write(self):
        pass


# TODO: date object date setter
class ToDoItem:
    def __init__(self, line=None,
                 description: str=None,
                 creation_date: str=None,
                 completion_date: str=None,
                 due_date: str=None,
                 complete: bool=None,
                 priority: str='',
                 projects: list=None,
                 contexts: str=None,
                 meta: dict=None):
        # TODO: finish doc string
        """
        Provide line, or other data. Line will be used if provided and other
         data will be ignored.

        :param line: line from todo.txt file, will be parsed. if line is given
         all other data will be ignored and only data in line is populated
        :param description: description of the task
        :param creation_date: optional creation date, format: YYYY-MM-DD
        :param completion_date: completion date as str, format: YYYY-MM-DD
         this is required if complete is True
        :param due_date: due date as string, format: YYYY-MM-DD
        :param complete: bool: task is complete
        :param priority: priority as a capital letter
        :param projects: list of tags
        :param contexts: list of contexts
        :param meta: dict of meta data
        """
        self._due_date, self._creation_date, \
            self._completion_date = (None, ) * 3
        if not contexts:
            self.contexts = []
        if not projects:
            self.projects = []
        if not meta:
            self.meta = {}
        if line:
            # build item from line
            self.line = line
            self._parse_line()
        else:
            # build item from parameters
            if complete:
                self.complete = complete
            self._priority = priority
            self.description = description

            try:
                if creation_date:
                    self._creation_date = strptime(creation_date, DATE_FORMAT)
                if completion_date:
                    self._completion_date = strptime(completion_date,
                                                     DATE_FORMAT)
                if due_date:
                    self._due_date = strptime(due_date, DATE_FORMAT)
            except ValueError:
                raise TDItemException("Date was not provided in"
                                      " YYYY-MM-DD format")

    def __repr__(self):
        # TODO: probably need a better repr, including other data
        return self.line

    def __str__(self):
        return self.line

    def _parse_line(self):
        line = self.line
        # complete must start with lowercase x and a space
        if line.startswith('x '):
            self.complete = True
            # trim off the 'x '
            line = line.split(maxsplit=1)[1]

            # completion date is required if complete, will be one of the first
            #  two of the remaining fields, priority may still be present
            items = line.split(maxsplit=2)
            for item in items[:2]:
                if '(' not in item:  # not a priority
                    try:
                        self._completion_date = strptime(item, DATE_FORMAT)
                        # remove the completion date
                        line = line.replace(item, '')
                        break
                    except ValueError:  # malformed date or not date
                        raise TDItemException("Malformed or missing "
                                              "Completion Date")
        else:
            self.complete = False
            self._completion_date = None

        # priority, optional: (X) where X is uppercase letter.
        # Priorities are specified in this format but may also be
        # pri:X  this format is handled later
        # (could use re, but this works)
        piece = line.split(maxsplit=1)[0]
        if '(' in piece and ')' in piece:
            if piece[1] in ascii_uppercase:
                self._priority = line[1]
                line = line.split(maxsplit=1)[1]
            else:
                # raise exception if invalid priority. hopefully user desc
                #  doesn't start with () though
                raise TDItemException("Invalid or missing priority in "
                                      "parenthesis")
        else:
            self._priority = ''

        # creation date (optional)
        if '-' in line.split()[0] and line[0] in digits:
            # attempt date conversion
            try:
                self._creation_date = strptime(line.split()[0], DATE_FORMAT)
                line = line.split(maxsplit=1)[1]
            except ValueError:
                # date could be malformed, or there isn't a date but the
                # description starts with a number and a dash
                # could put in more tests for this, but this should suffice
                self._creation_date = None

        # the rest of the line is the description, which also contains metadata
        self.description = line

        # look for tags, contexts, and other meta data
        pieces = line.strip().split()
        for piece in pieces:
            # contexts
            if len(piece) == 1:
                # nothing relevant could be found here, skip it
                continue
            if piece.startswith('@'):
                self.contexts.append(piece[1:])
                continue
            # projects
            if piece.startswith('+'):
                self.projects.append(piece[1:])
            if ':' in piece \
                    and not piece.startswith(':') \
                    and not piece.endswith(':') \
                    and len(piece.split(':')) == 2:
                k, v = piece.split(':')
                if k == 'pri':
                    self._priority = v
                    continue
                if k == 'due':
                    with suppress(ValueError):
                        self._due_date = strptime(v.strip(), DATE_FORMAT)
                        continue
                # add k:v pair to other metadata
                self.meta[k] = v

    @staticmethod
    def _date_setter(dt):
        if dt == '':
            return ''
        else:
            try:
                return strptime(dt, DATE_FORMAT)
            except ValueError:
                raise TDItemException("Date format must be YYYY-MM-DD")

    @property
    def completion_date(self):
        if self._completion_date:
            return strftime(DATE_FORMAT, self._completion_date)

    @completion_date.setter
    def completion_date(self, dt):
        self._completion_date = self._date_setter(dt)

    @property
    def due_date(self):
        if self._due_date:
            return strftime(DATE_FORMAT, self._due_date)

    @due_date.setter
    def due_date(self, dt):
        self._due_date = self._date_setter(dt)

    @property
    def creation_date(self):
        if self._creation_date:
            return strftime(DATE_FORMAT, self._creation_date)

    @creation_date.setter
    def creation_date(self, dt):
        self._creation_date = self._date_setter(dt)

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, priority):
        if priority in ascii_uppercase or priority == '':
            self._priority = priority
        else:
            raise TDItemException("Priority must be an uppercase letter or"
                                  " empty string")
