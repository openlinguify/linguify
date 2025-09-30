import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.revision.models import CardPerformance, CardMastery

print('=== Card Performances ===')
total = CardPerformance.objects.count()
print(f'Total performances: {total}\n')

if total > 0:
    for p in CardPerformance.objects.order_by('-created_at')[:10]:
        print(f'Card: {p.card.front_text[:30]}...')
        print(f'  Mode: {p.study_mode} | Difficulty: {p.difficulty} | Correct: {p.was_correct}')
        print(f'  Confidence: {p.confidence_before}% -> {p.confidence_after}%')
        print(f'  Time: {p.created_at}')
        print()
else:
    print('No performances recorded yet.\n')

print('=== Card Masteries (updated) ===')
for m in CardMastery.objects.order_by('-updated_at')[:10]:
    print(f'Card: {m.card.front_text[:30]}...')
    print(f'  Confidence: {m.confidence_score}% | Level: {m.mastery_level}')
    print(f'  Attempts: {m.total_attempts} | Success rate: {(m.successful_attempts/m.total_attempts*100) if m.total_attempts > 0 else 0:.1f}%')
    print(f'  Updated: {m.updated_at}')
    print()