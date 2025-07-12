from rest_framework import serializers


class TextToSpeechSerializer(serializers.Serializer):
    """Serializer pour la synthèse vocale"""
    text = serializers.CharField(max_length=5000)
    language = serializers.CharField(max_length=10, default='en')
    voice = serializers.CharField(max_length=50, required=False)


class SpeechToTextSerializer(serializers.Serializer):
    """Serializer pour la reconnaissance vocale"""
    audio_data = serializers.CharField()  # Base64 encoded audio
    language = serializers.CharField(max_length=10, default='en')


class TranscriptionResultSerializer(serializers.Serializer):
    """Serializer pour les résultats de transcription"""
    text = serializers.CharField()
    confidence = serializers.FloatField(required=False)
    language = serializers.CharField()
    success = serializers.BooleanField(default=True)
    error = serializers.CharField(required=False)