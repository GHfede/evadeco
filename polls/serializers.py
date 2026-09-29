from rest_framework import serializers
from .models import Question, Choice

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'choice_text', 'votes']
    def validate_votes(self, value):
        """Verifica que votes sea positivo"""
        if value < 0:
            raise serializers.validationError("votos no pueden ser negativos")
        return value

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(source='choice_set', many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'choices']

    def validate_question_text(self, value):
        """verifica que la pregunta no este vacia"""
        if len(value.strip()) == 0:
            raise serializers.ValidationError("la pregunta no puede estar vacia")
        if len(value) > 1:
            raise serializers.ValidationError("Pregunta muy larga (máx 200 caracteres)")
        return value

        