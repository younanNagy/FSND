import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from random import seed
from random import randint

from models import setup_db, Question, Category

seed(100)
QUESTIONS_PER_PAGE = 10
def paginateQuestions(request, all_questions):
  page = request.args.get("page", 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  all_questions = [question.format() for question in all_questions]
  questions = all_questions[start:end]
  return questions

def searchQuestion(search_term):
  questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
  formatted_questions=[question.format() for question in questions]
  return formatted_questions

def addNewQuestion(requst_content):
  new_question = requst_content.get('question')
  new_answer = requst_content.get('answer')
  new_difficulty = requst_content.get('difficulty')
  new_category = requst_content.get('category') 
  try:
    question=Question(question=new_question, answer=new_answer,
    difficulty=new_difficulty, category=new_category)
    question.insert()
    return question.id
  except:
    return "Error"
def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  # if test_config is None:
  # # load the instance config, if it exists, when not testing
  # #app.config.from_pyfile('config.py', silent=False)
  # else:
  # # load the test config if passed in
  #   app.config.from_mapping(test_config)
  
  setup_db(app)
  

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  # '''
  # @TODO: Use the after_request decorator to set Access-Control-Allow
  # '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods','GET,PUT,POST,DELETE,OPTIONS')
    # response.headers.add('Access-Control-Allow-Origin', '*')
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def getCategories():
    categories=Category.query.all()
    if len(categories)==0:
      abort(404)
    return jsonify({
    "success": True,
    "categories":{category.id: category.type for category in categories}
    })
    

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions',methods=["GET"])
  def getQuestions():
    all_questions=Question.query.all()
    categories=Category.query.all()
    questions=paginateQuestions(request,all_questions)
    if len(categories)==0 or len(questions)==0:
      abort(404)
    return jsonify({
      "success": True,
      "questions":questions,
      "total_questions":len(all_questions),
      "categories":{category.id: category.type for category in categories},
      "current_category":None
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route("/questions/<int:question_id>", methods=["DELETE"])
  def deleteQuestion(question_id):

    question=Question.query.get(question_id)
    if question is None:
      abort(404)
    question.delete()
    return jsonify({
      'deleted':question_id,
      'success': True
    })
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route("/questions",methods=["POST"])
  def QuestionsEndPoint():
    request_content=request.get_json()
    if "searchTerm" in request_content:
      found_questions=searchQuestion(request_content.get('searchTerm'))
      if len(found_questions)==0:
        abort(404) 
      return jsonify({
        "success":True,
        "questions":found_questions,
        "total_questions":len(found_questions),
        "current_category":None
      })

    elif (('question' in request_content) and('answer' in request_content) and ('difficulty' in request_content) and ('category' in request_content)):
      new_question_id=addNewQuestion(request_content)
      if new_question_id !="Error":
        return jsonify({
      'success': True,
      'created': new_question_id,
      })
    else:
      abort(422)
    

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category>/questions', methods=['GET'])
  def getQuestionByCategories(category):
    questions=Question.query.filter(Question.category==str(category)).all()
    if len(questions) == 0:
      abort(404)
    questions=[question.format() for question in questions]
    return jsonify({
      "success": True,
      "questions":questions,
      "total_questions":len(questions),
      "current_category":category
    })


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes',methods=['POST'])
  def getNextQuestion():
    request_content=request.get_json()
    questions=None
    next_question=None
    
    if not ("previous_questions" in request_content and "quiz_category" in request_content):
      abort(422)
    if request_content.get("quiz_category")["type"]=="click":
      questions=Question.query.filter(Question.id.not_in(request_content.get("previous_questions"))).all()        
    else:
      quiz_category=request_content.get("quiz_category")
      print(quiz_category)
      questions=Question.query.filter(Question.id.not_in(request_content.get("previous_questions")),
      Question.category==str(quiz_category["id"])
      ).all()
      
    if len(questions)==0:
      abort(404)
    else:
      print( len(questions))
      question_number=randint(0, len(questions)-1)
      print(question_number)
      next_question = questions[question_number].format()
    return jsonify({
      "success": True,
      "question":next_question
    })
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "message": "Resource Not Found"
      }),404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "message": "Unprocessable"
      }),422

  @app.errorhandler(400)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "message": "Bad Request"
      }),400
  return app

    