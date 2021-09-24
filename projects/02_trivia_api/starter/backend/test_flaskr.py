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
        self.database_name = "trivia"
        self.database_path = "postgresql://{}/{}".format("postgres:2271996@localhost:5432", self.database_name)
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
    
    def test_getCategories(self):
        category=Category(type="new_type")
        category.insert()
        res = self.client().get("/categories")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["categories"]))

        category.delete()

        

    def test_404_getCategories(self):
        res = self.client().get("/categories/2")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_getQuestions(self):
        category=Category(type="new_type")
        category.insert()
        question = Question(question="get question", answer="new answer",
                            difficulty=1, category=1)
        question.insert()
        res = self.client().get("/questions")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(len(data["categories"]))

        category.delete()
        question.delete()
        

    def test_404_getQuestions(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")


    def test_deleteQuestion(self):
        question = Question(question="delete question", answer="new answer",
                            difficulty=1, category=1)
        question.insert()
        question_id = question.id

        res = self.client().delete(f"/questions/{question_id}")
        data = json.loads(res.data)

        question = Question.query.get(question_id)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_404_deleteQuestion(self):
        res = self.client().delete("/questions/a")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_QuestionsEndPoint_add_question(self):
        new_question = {
            "question": "new question",
            "answer": "new answer",
            "difficulty": 1,
            "category": 1
        }
        total_questions_before = len(Question.query.all())
        res = self.client().post("/questions", json=new_question)
        data = json.loads(res.data)
        total_questions_after = len(Question.query.all())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(total_questions_after, total_questions_before + 1)
        question=Question.query.get(data["created"])
        if question is not None:
            question.delete()

    def test_422_QuestionsEndPoint_add_question(self):
        new_question = {
            "question": "new_question",
            "answer": "new_answer",
            "category": 1
        }
        res = self.client().post("/questions", json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable")

    def test_QuestionsEndPoint_search_questions(self):
        question = Question(question="search question", answer="new answer",
                            difficulty=1, category=1)
        question.insert()
        new_search = {"searchTerm": "e"}
        res = self.client().post("/questions", json=new_search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertIsNotNone(data["questions"])
        self.assertIsNotNone(data["total_questions"])
        
        question.delete()

    def test_404_QuestionsEndPoint_search_question(self):
        new_search = {
            "searchTerm": "",
        }
        res = self.client().post("/questions/search", json=new_search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_getQuestionByCategories(self):
        category=Category(type="new_type")
        category.insert()
        question = Question(question="category question", answer="new answer",
                            difficulty=1, category=1)
        question.insert()
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["current_category"])

        category.delete()
        question.delete()

    def test_404_getQuestionByCategories(self):
        res = self.client().get("/categories/a/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_getNextQuestion(self):

        category=Category(type="Entertainment")
        category.insert()
        question = Question(question="next question", answer="new answer",
                            difficulty=1, category=1)
        question.insert()
        new_quiz_round = {"previous_questions": [],
                          "quiz_category": {"type": "Entertainment", "id": 1}}

        res = self.client().post("/quizzes", json=new_quiz_round)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        
        category.delete()
        question.delete()

    def test_422_getNextQuestion(self):
        new_quiz_round = {"previous_questions": []}
        res = self.client().post("/quizzes", json=new_quiz_round)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()