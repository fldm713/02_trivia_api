import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

# let all testing sorted by the order it defined in the class
unittest.TestLoader.sortTestMethodsUsing = lambda *args: -1  

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # testings for get method on '/categories'
    def test_show_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6) # totally 6categories

    # testings for get method on '/questions'
    def test_show_paginate_questions_page_1(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 10) # 10 questions in page 1
        self.assertEqual(data['totalQuestions'], 19) # totally 10 questions
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6) # totally 6categories
        self.assertFalse(data['currentCategory'])
    
    def test_show_paginate_questions_page_2(self):
        res = self.client().get('/questions?page=2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 9) # 9 questions in page 2 now
        self.assertEqual(data['totalQuestions'], 19) # totally 10 questions
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6) # totally 6categories
        self.assertFalse(data['currentCategory'])

    def test_404_if_show_paginate_questions_get_invalid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    
    # testings for delete method on '/questions/<int:id>'
    def test_delete_question(self):
        res = self.client().delete('/questions/14')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 14).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(question, None)

    def test_422_if_delete_question_not_exist(self):
        res = self.client().delete('/questions/100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    # testings for post method on '/quesitons/create'
    def test_create_question(self):
        new_question = {
            'question': 'Which continent is the United States in?',
            'answer': 'North America',
            'category': 3,
            'difficulty': 1,
        }

        res = self.client().post('/questions/create', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['question'], 'Which continent is the United States in?')
        self.assertEqual(data['answer'], 'North America')
        self.assertEqual(data['category'], 3)
        self.assertEqual(data['difficulty'], 1)

    def test_422_create_question_with_invalid_input(self):
        new_question = {
            'question': 'Which continent is the United States in?',
            'answer': 'North America',
            'category': 3,
            'difficulty': None,
        }

        res = self.client().post('/questions/create', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    # testings for post method on '/quesitons/create'
    def test_search_questions(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'actor'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 1)
        self.assertEqual(data['totalQuestions'], 19)
        self.assertFalse(data['currentCategory'])

    # testings for get method on '/categories/<int:category_id>/questions'
    def test_show_questions_by_category_1(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 3)
        self.assertEqual(data['totalQuestions'], 19)
        self.assertEqual(data['currentCategory'], 'Science')

    def test_show_questions_by_category_2(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 4)
        self.assertEqual(data['totalQuestions'], 19)
        self.assertEqual(data['currentCategory'], 'Art')

    def test_404_show_questions_by_category_with_invalid_input(self):
        res = self.client().get('/categories/7/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # testings for post method on '/quizzes'
    def test_play_quiz_category_1(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': [], 
            'quiz_category': {'id': 1, 'type': 'Science'}
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
    
    def test_play_quiz_category_all(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': [], 
            'quiz_category': {'id': 0, 'type': ''}
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()