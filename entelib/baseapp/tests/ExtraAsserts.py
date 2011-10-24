
class ExtraAsserts:
    def assertSetEqual(self, iterable1, iterable2):
        for x in iterable1:
            self.assert_(x in iterable2)
        for x in iterable2:
            self.assert_(x in iterable1)

    def assertIn(self, obj, container):
        self.assertTrue(obj in container)

    def assertNotIn(self, obj, container):
        self.assertFalse(obj in container);
