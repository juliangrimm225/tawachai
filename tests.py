from datetime import datetime, timedelta
import unittest
from app import create_app, db
from app.models import User, Project, Node, Edge
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))

    def test_checks_for_sinks_and_sources(self):
        n0 = Node(name="n0 (root)")
        n1 = Node(name="n1 (level 1)")
        db.session.add(n0)
        db.session.add(n1)
        db.session.commit()
        self.assertEqual(n0.edges_sinks.all(), [])
        self.assertEqual(n1.edges_sinks.all(), [])
        self.assertEqual(n0.edges_sources.all(), [])
        self.assertEqual(n1.edges_sources.all(), [])
        self.assertEqual(n0.sources(), [])
        self.assertEqual(n1.sources(), [])
        self.assertEqual(n0.sinks(), [])
        self.assertEqual(n1.sinks(), [])

        self.assertFalse(n0.is_sink_for(n1))
        self.assertFalse(n0.is_source_for(n1))
        self.assertFalse(n0.is_connected_to(n1))

        e = Edge()
        e.sink = n0
        e.source = n1
        db.session.add(e)
        db.session.commit()
        
        self.assertTrue(n0.is_sink_for(n1))
        self.assertFalse(n0.is_source_for(n1))
        self.assertTrue(n0.is_connected_to(n1))

        self.assertFalse(n1.is_sink_for(n0))
        self.assertTrue(n1.is_source_for(n0))
        self.assertTrue(n1.is_connected_to(n0))
        
        self.assertEqual(n1.edges_sinks.all(), n0.edges_sources.all())

        self.assertEqual(n0.sources(), [n1])
        self.assertEqual(n0.sinks(), [])
        self.assertEqual(n1.sources(), [])
        self.assertEqual(n1.sinks(), [n0])

    def test_addition_and_removal_of_sinks_and_sources(self):
        # create 4 nodes
        n0 = Node(name="n0")
        n1 = Node(name="n1")
        n2 = Node(name="n2")
        n3 = Node(name='n3')
        db.session.add_all([n0, n1, n2, n3])
        db.session.commit()

        # create the following tree:
        # n2 --> n1 --> n0
        # n3 --> n0
        
        n1.add_sink(n0)
        n1.add_source(n2)
        n0.add_source(n3)
        db.session.commit()

        self.assertTrue(n1.is_sink_for(n2))
        self.assertTrue(n1.is_source_for(n0))
        self.assertTrue(n2.is_source_for(n1))
        self.assertTrue(n0.is_sink_for(n1))
        
        self.assertEqual(n0.sinks(), [])
        self.assertEqual(n0.sources(), [n1, n3])
        self.assertEqual(n1.sinks(), [n0])
        self.assertEqual(n1.sources(), [n2])
        self.assertEqual(n2.sinks(), [n1])
        self.assertEqual(n2.sources(), [])
        self.assertEqual(n3.sinks(), [n0])
        self.assertEqual(n3.sources(), [])

        # test if clauses

        e = Edge.query.all()
        n1.add_source(n0)
        n1.add_sink(n2)
        db.session.commit()
        e_test = Edge.query.all()
        self.assertFalse(n2.is_sink_for(n1))
        self.assertEqual(n1.edges_sinks.count(), 1)
        self.assertEqual(n2.edges_sources.count(), 0)
        self.assertEqual(e, e_test)

        # part removal of tree
        n1.remove_sink(n0)
        n1.remove_source(n2)
        db.session.commit()

        self.assertFalse(n1.is_sink_for(n2))
        self.assertFalse(n1.is_source_for(n0))
        self.assertFalse(n2.is_source_for(n1))
        self.assertFalse(n0.is_sink_for(n1))

        self.assertEqual(n0.sinks(), [])
        self.assertEqual(n0.sources(), [n3])
        self.assertEqual(n1.sinks(), [])
        self.assertEqual(n1.sources(), [])
        self.assertEqual(n2.sinks(), [])
        self.assertEqual(n2.sources(), [])
        self.assertEqual(n3.sinks(), [n0])
        self.assertEqual(n3.sources(), [])

        



if __name__ == '__main__':
    unittest.main(verbosity=2)
