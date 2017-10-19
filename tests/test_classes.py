import unittest

from todo import ToDoItem, ToDoList, TDItemException


class TestToDoItem(unittest.TestCase):
    # example from the documentation: https://github.com/todotxt/todo.txt
    EXAMPLE_LINE = 'x (A) 2016-05-20 2016-05-01 measure space for' \
                   ' +chapelShelving @chapel due:2016-05-30'

    def test_parse_line_example_line(self):
        tdi = ToDoItem(line=self.EXAMPLE_LINE)
        self.assertEqual(tdi.priority, 'A')
        self.assertEqual(tdi.complete, True)
        self.assertEqual(tdi.completion_date, '2016-05-20')
        self.assertEqual(tdi.creation_date, '2016-05-01')
        self.assertEqual(tdi.due_date, '2016-05-30')
        self.assertIn('chapel', tdi.contexts)
        self.assertIn('chapelShelving', tdi.projects)

    def test_parse_line_invalid_data(self):
        # complete but no date
        with self.assertRaises(TDItemException):
            line = self.EXAMPLE_LINE.replace('2016-05-20 2016-05-01', '')
            tdi = ToDoItem(line=line)

        with self.assertRaises(TDItemException):
            line = self.EXAMPLE_LINE.replace('(A)', '()')
            tdi = ToDoItem(line=line)

        # if due date is invalid keep it as other meta data
        line = self.EXAMPLE_LINE.replace('due:2016-05-30', 'due:2016-13-30')
        tdi = ToDoItem(line=line)
        self.assertEqual(tdi.meta['due'], '2016-13-30')

    def test_parse_line_meta_data(self):
        line = 'my description @has @a @firstname and +some +projects val:7 ' \
               'weight:5 amount:9001'
        tdi = ToDoItem(line=line)
        self.assertEqual(tdi.contexts, ['has', 'a', 'firstname'])
        self.assertEqual(tdi.projects, ['some', 'projects'])
        self.assertEqual(tdi.meta['val'], '7')
        self.assertEqual(tdi.meta['weight'], '5')
        self.assertEqual(tdi.meta['amount'], '9001')


if __name__ == '__main__':
    unittest.main()
