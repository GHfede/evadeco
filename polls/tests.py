from django.test import TestCase
from django.utils import timezone
from .models import Question, Choice
from .services import vote_on_question
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User

# ==========================================
# UNIT TESTS — Prueba funciones aisladas
# ==========================================

class VoteOnQuestionTest(TestCase):
    """Prueba que vote_on_question() funciona correctamente"""
    
    def setUp(self):
        """Se ejecuta ANTES de cada test. Prepara datos."""
        
        # Crea una pregunta de prueba en BD temporal
        self.question = Question.objects.create(
            question_text="Test Question",
            pub_date=timezone.now()  # Fecha actual (para test)
        )
        
        # Crea una opción de prueba asociada a la pregunta
        self.choice = Choice.objects.create(
            question=self.question,  # RELACIONA con question
            choice_text="Test Choice",
            votes=0  # Empieza con 0 votos
        )
    
    def test_vote_increments_counter(self):
        """¿Incrementa el contador cuando votamos?"""
        
        # EJECUTA: vota por esta opción
        vote_on_question(self.question.id, self.choice.id)
        
        # RECARGA datos de BD (porque vote_on_question() modificó BD)
        self.choice.refresh_from_db()
        
        # VERIFICA: ¿votes es ahora 1?
        self.assertEqual(self.choice.votes, 1)
        # Si no es 1, el test FALLA ❌
    
    def test_vote_twice(self):
        """¿Funciona si votamos 2 veces?"""
        
        # EJECUTA: primer voto
        vote_on_question(self.question.id, self.choice.id)
        
        # EJECUTA: segundo voto
        vote_on_question(self.question.id, self.choice.id)
        
        # RECARGA de BD
        self.choice.refresh_from_db()
        
        # VERIFICA: ¿votes es ahora 2?
        self.assertEqual(self.choice.votes, 2)


# ==========================================
# INTEGRATION TESTS — Prueba endpoints completos
# ==========================================

class VoteAPITest(TestCase):
    """Prueba que el endpoint /api/vote/ funciona correctamente"""
    
    def setUp(self):
        """Prepara datos y autenticación"""
        
        # Crea pregunta y opción (igual que VoteOnQuestionTest)
        self.question = Question.objects.create(
            question_text="Test Question",
            pub_date=timezone.now()
        )
        self.choice = Choice.objects.create(
            question=self.question,
            choice_text="Test Choice",
            votes=0
        )
        
        # CREA un usuario de prueba (para login)
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass"
        )
        
        # GENERA token JWT para este usuario
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)  # Token válido para requests
        
        # CREA cliente API (para simular requests HTTP)
        self.client = APIClient()
    
    def test_vote_api_with_auth(self):
        """¿Endpoint funciona cuando pasamos token?"""
        
        # AÑADE token al cliente (autenticación)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # HACE un POST al endpoint /api/1/vote/ con opción
        response = self.client.post(
            f'/polls/api/{self.question.id}/vote/',
            {'choice_id': self.choice.id},
            format='json'
        )
        
        # VERIFICA: ¿status code es 201 (Creado)?
        self.assertEqual(response.status_code, 201)
        # 201 = voto guardado exitosamente
    
    def test_vote_api_without_auth(self):
        """¿Endpoint rechaza cuando NO pasamos token?"""
        
        # NO añade token (sin autenticación)
        # self.client sin credentials = sin token
        
        # HACE un POST sin token
        response = self.client.post(
            f'/polls/api/{self.question.id}/vote/',
            {'choice_id': self.choice.id},
            format='json'
        )
        
        # VERIFICA: ¿status code es 401 (No Autorizado)?
        self.assertEqual(response.status_code, 401)
        # 401 = rechazo por falta de autenticación
