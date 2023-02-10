from flask import Flask, Blueprint, render_template, abort, request, g, redirect, url_for
import random

from ..auth import registration_required
from .utils import QuestionData, QuestionHistory

class QuestionView:
    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        bp = Blueprint('question', __name__, url_prefix="/question")

        question_data = QuestionData(app)
        question_history = QuestionHistory(app)

        @bp.route('/')
        @registration_required
        def all():
            return render_template('multiple-questions.jinja2', question_data_list=question_data.all)

        @bp.route('/<string:level>/<string:topic>/<string:id>')
        @registration_required
        def single(level, topic, id):

            questions = question_data.get_questions(level, topic, id)
            if len(questions) != 1:
                abort(404)

            answered = request.args.get('answered', None) == 'True'
            return render_template('single-question.jinja2', question_data=questions[0], answered=answered)

        @bp.route('/<string:level>/<string:topic>')
        @registration_required
        def by_topic(level, topic):

            questions = question_data.get_questions(level, topic)
            if len(questions) == 1:
                abort(404)

            return render_template('multiple-questions.jinja2', question_data_list=questions)

        @bp.route('/rand/<string:level>/<string:topic>')
        @registration_required
        def rand(level, topic):
            questions = question_data.get_questions(level, topic)
            if len(questions) == 0:
                abort(404)
            
            last_count = request.args.get('nlast', 200, int)
            if last_count < 1:
                last_count = 1
            wrong_count = request.args.get('nwrong', 20, int)
            if wrong_count < 1:
                wrong_count = 1
            wrong_probability = request.args.get('pwrong', 3, int)
            if wrong_probability < 1:
                wrong_probability = 1
                
            wrong_questions_data = []
            if g.registered_user_id:
                wrong_questions_references = question_history.last_n_wrong(g.registered_user_id, n=last_count, m=wrong_count)
                wrong_questions_data = question_data.get_questions(references=wrong_questions_references)
            
            if len(wrong_questions_data) > 0 and random.randint(0, wrong_probability-1) == 0:
                random_question_data = random.choice(wrong_questions_data)
            else:
                random_question_data = random.choice(questions)

            return render_template('single-question.jinja2', question_data=random_question_data)

        @bp.route('/answer', methods=['POST'])
        @registration_required
        def answer():
            data = request.get_json()
            if 'level' not in data or 'topic' not in data or 'id' not in data or 'correct' not in data:
                abort(404)

            question_history.add(g.registered_user_id, data)
            
            return {'received': True}
        
        @bp.route('/clear-history')
        @registration_required
        def clear_history():
            question_history.clear(g.registered_user_id)
            return redirect(url_for('index'))

        @bp.before_app_request
        def load_user_history():
            if g.registered_user_id is None:
                return
            
            g.registered_user_history = question_history.get(g.registered_user_id)
            n = request.args.get('nlast', 100, int)
            if n < 1:
                n = 1
            g.registered_user_statistic = question_history.percentage(g.registered_user_id, n)

        app.register_blueprint(bp)