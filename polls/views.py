from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Question, Choice
from .services import vote_on_question
from .services import results_on_question

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import QuestionSerializer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle



def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    context = {"latest_question_list": latest_question_list}
    return render(request, "polls/index.html", context)

def prueba(request):
    return HttpResponse("Esto es una prueba")

def detail(request, question_id):
    question = Question.objects.get(id=question_id)
    return render(request, "polls/detail.html", {"question": question})

def results(request, question_id):
    question = Question.objects.get(id=question_id)
    choices = results_on_question(question_id)
    return render(request, "polls/results.html", {
        "question": question,
        "choices": choices
    })


def vote(request, question_id):
    try:
        choice_id = request.POST['choice']
    except KeyError:
        question = Question.objects.get(id=question_id)
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    
    vote_on_question(question_id, choice_id)
    
    
    return HttpResponseRedirect(f'/polls/{question_id}/results/')  


class QuestionDetailAPI(APIView):
    def get(self, request, question_id):
        try:
            question = Question.objects.get(id=question_id)
            serializer = QuestionSerializer(question)
            return Response(serializer.data)
        except Question.DoesNotExist:
            return Response(
                {"error": "Question not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )


@method_decorator(csrf_exempt, name='dispatch')
class VoteAPI(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    
    def post(self, request, question_id):
        try:
            choice_id = request.data.get('choice_id')
            
            if not choice_id:
                return Response(
                    {"error": "choice_id required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                question = Question.objects.get(id=question_id)
            except Question.DoesNotExist:
                return Response(
                    {"error": "Question not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            try:
                choice = question.choice_set.get(id=choice_id)
            except Choice.DoesNotExist:
                return Response(
                    {"error": "Invalid choice for this question"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            vote_on_question(question_id, choice_id)
            
            return Response(
                {"status": "vote recorded", "votes": choice.votes},
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoginAPI(APIView):
    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            
            if not username or not password:
                return Response(
                    {"error": "username and password required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Valida usuario (Django auth)
            from django.contrib.auth import authenticate
            user = authenticate(username=username, password=password)
            
            if not user:
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Genera tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class QuestionListAPI(APIView):
    def get(self, request):
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response({
            "total_questions": len(questions),
            "questions": serializer.data
        })


class QuestionStatsAPI(APIView):
    def get(self, request, question_id):
        from polls.services import get_question_stats
        stats = get_question_stats(question_id)
        
        if not stats:
            return Response(
                {"error": "Question not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(stats)

class QuestionDeleteAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, question_id):
        try:
            return Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            raise "Http404_NOT_FOUND"

    def delete(self, request, question_id):
        question = self.get_object(question_id)
        # Check de owner (acá va lo que tenés que resolver)
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)   