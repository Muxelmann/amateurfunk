from flask import Flask
import random
import os
import json
import hashlib
import csv

class Question:
    def __init__(self, data) -> None:
        self.id: str = data['id'].lower()
        self.level: str = data['level'].lower()
        self.topic: str = data['topic'].lower()
        self.question: list[str] = data['question']
        self._answers: list[tuple[bool, str]] = data['answers']

    @property
    def answers(self) -> str:
        a = self._answers.copy()
        random.shuffle(a)
        return a

    @property
    def level_desc(self) -> str:
        return f'Klasse {self.level.upper()}'

    @property
    def topic_desc(self) -> str:
        if self.topic == 't':
            return 'Technische Kenntnisse'
        if self.topic == 'b':
            return 'Betriebliche Kenntnisse'
        if self.topic == 'v':
            return 'Kenntnisse von Vorschriften'

class QuestionData:

    _question_data_dict: dict[str, dict[str, dict[str, Question]]] = {}
    _question_data_list: list[Question] = None

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        questions_file = os.path.join(app.static_folder, 'fragen.json')
        if not os.path.exists(questions_file):
            return
        
        with open(questions_file, 'r') as f:
            for data in json.load(f):
                level = data['level'] 
                topic = data['topic']
                id = data['id']

                if level not in self._question_data_dict:
                    self._question_data_dict[level] = {}
                if topic not in self._question_data_dict[level]:
                    self._question_data_dict[level][topic] = {}
                
                self._question_data_dict[level][topic][id] = Question(data)

    def get_questions(self, level=None, topic=None, id=None, references=None) -> list[Question]:

        if references is None:
            l = self.all
            if level is not None:
                l = [q for q in l if q.level == level]
            if topic is not None:
                l = [q for q in l if q.topic == topic]
            if id is not None:
                l = [q for q in l if q.id == id]
        else:
            l = []
            for r in references:
                l += self.get_questions(r['level'], r['topic'], r['id'])
        return l

    @property
    def all(self) -> list[Question]:
        if self._question_data_list is None:
            self._question_data_list = []
            for c in self._question_data_dict:
                for t in self._question_data_dict[c]:
                    for id in self._question_data_dict[c][t]:
                        self._question_data_list.append(self._question_data_dict[c][t][id])
            self._question_data_list.sort(key=lambda q: q.level + q.topic + q.id)
        
        return self._question_data_list

class QuestionHistory:

    def __init__(self, app: Flask) -> None:
        self._path = app.instance_path
        self._buffer = dict[str, list]()
    
    def get_path_for(self, name) -> str:
        name = hashlib.sha256(name.encode('utf-8')).hexdigest() + '.csv'
        return os.path.join(self._path, name)

    def add(self, name: str, data: dict):
        if name not in self._buffer:
            self._buffer[name] = []
        self._buffer[name].append(data)

        with open(self.get_path_for(name), 'a+') as f:
            csv_writer = csv.writer(f, delimiter=';')
            csv_writer.writerow([data['level'], data['topic'], data['id'], data['correct']])

    def get(self, name: str) -> list:
        if name in self._buffer:
            return self._buffer[name]
        
        path = self.get_path_for(name)
        if not os.path.exists(path):
            return []
        with open(path, 'r') as f:
            csv_reader = csv.reader(f, delimiter=';')
            data = []
            for row in csv_reader:
                data.append({
                    'level': row[0],
                    'topic': row[1],
                    'id': row[2],
                    'correct': row[3] == 'True'
                })
            self._buffer[name] = data
            return data
        
    def clear(self, name: str):
        if name in self._buffer:
            del self._buffer[name]

        path = self.get_path_for(name)
        if os.path.exists(path):
            os.remove(path)

    def last_n(self, name: str, n: int | None) -> list:
        history = self.get(name)
        if n is None:
            return history
        if len(history) > n:
            return history[-n:]
        return history

    def percentage(self, name: str, n=100) -> float:
        history = [d['correct'] for d in self.last_n(name, n)]
        if len(history) == 0:
            return 0.0
        return history.count(True) / len(history)

    def last_n_wrong(self, name: str, n=100, m=20) -> list[dict]:
        wrong = [json.dumps(d) for d in self.last_n(name, n) if not d['correct']]
        wrong = [json.loads(d) for d in list(dict.fromkeys(wrong))]
        if len(wrong) > m:
            return wrong[-m:]
        return wrong
