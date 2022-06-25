import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        #self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres', 'power','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        self.question = {
                "question": "Who is the best programmer in the world?",
                "answer": "Peprah",
                "category": 1,
                "difficulty": 4
            }

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
    def test_get_categories_success(self):
        res=self.client().get("/categories")
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)

    def test_get_questions_success(self):
        res=self.client().get("/questions")
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(1<=len(data['questions'])<=10)
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(len(data["categories"]))
    
    def test_get_paginated_questions_not_found(self):
        res = self.client().get("/questions?page=2000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["error"], 404)
        self.assertEqual(data["success"], False)
    
    def test_delete_question_success(self):
        question=Question(
            question=self.question['question'],
            answer=self.question['answer'],
            category=self.question['category'],
            difficulty=self.question['difficulty']
        )
        question.insert()
        question_id=question.id
        res= self.client().delete('/questions/'+str(question_id))
        data=json.loads(res.data)
        question=Question.query.get(question_id)
        self.assertEqual(res.status_code,200)
        self.assertTrue(data['success'])
        self.assertIsNone(question)
    
    def test_delete_question_not_found(self):
        res=self.client().delete('questions/2000')
        data=json.loads(res.data)
        self.assertEqual(data['success'],False)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['error'],404)

    def test_add_question_success(self):
        res=self.client().post('/questions',json=self.question)
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertTrue(data['questionId']) # to check if type is int

    def test_add_question_server_error(self):
        res=self.client().post('/questions',json={})
        data=json.loads(res.data)
        self.assertEqual(res.status_code,500)
        self.assertEqual(data['error'],500)

    def test_search_questions_success(self):
        res = self.client().post("/questions", json={"searchTerm": "title"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["totalQuestions"])

    def test_search_questions_empty_string(self):
        res = self.client().post("/questions", json={"searchTerm": ""})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["totalQuestions"])
    
    def test_search_questions_not_found(self):
        res = self.client().post("/questions", json={"searchTerm": "i32hdfuu23hgeuigdwq"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(len(data["questions"]))
        self.assertFalse(data["totalQuestions"])

    def test_get_question_for_quiz_success(self):
        res = self.client().post("/quizzes", json={
            "previous_questions": [],
            "quiz_category": 1
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["question"])
    
    def test_get_question_for_quiz_bad_request(self):
        res = self.client().post("/quizzes", json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["error"], 400)

    def test_get_question_for_quiz_no_question_left(self):
        res = self.client().post("/quizzes", json={
            "previous_questions": [13,14,15],
            "quiz_category": 3
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertFalse(data["question"])

    
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()