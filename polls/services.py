from .models import Question, Choice
from django.db.models import Sum, Count


def vote_on_question(question_id, choice_id):
    """
    logica de negocio: inclementar votos de una opcion
    """
    question = Question.objects.get(id=question_id)
    choice = question.choice_set.get(id=choice_id)

    choice.votes += 1
    choice.save()

    return choice


def results_on_question(question_id):
    """
    Obtener todos los resultados (todas las choices) de una pregunta
    """
    question = Question.objects.get(id=question_id)
    return question.choice_set.all()

def details_on_question(question_id):
    """
    Obtener una pregunta para mostrar detalles
    """
    question = Question.objects.get(id=question_id)
    return question 

def get_question_stats(question_id):
    """
    Obtén estadísticas de una pregunta:
    - Total de choices
    - Total de votos
    """
    stats = Question.objects.filter(id=question_id).annotate(
        total_choices=Count('choice'),
        total_votes=Sum('choice__votes')
    ).values('question_text', 'total_choices', 'total_votes')
    
    return stats.first()


def get_all_questions_with_stats():
    """
    Por CADA pregunta: cuántas choices tiene Y cuántos votos totales.
    """
    stats = Question.objects.annotate(
        total_choices=Count('choice'),
        total_votes=Sum('choice__votes')
    ).values('id', 'question_text', 'total_choices', 'total_votes')
    
    return list(stats)