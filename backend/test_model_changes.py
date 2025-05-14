#!/usr/bin/env python3
"""
Script de test pour simuler les changements apportés au modèle Note
pour s'assurer qu'ils fonctionnent correctement sans accès à la base de données.
"""

from datetime import datetime, timedelta

# Imitation simplifiée du modèle Note pour les tests
class MockNote:
    def __init__(self, last_reviewed_at=None, review_count=0):
        self.last_reviewed_at = last_reviewed_at
        self.review_count = review_count
    
    def _calculate_next_review_date(self, from_date=None):
        if from_date is None:
            from_date = datetime.now()
            
        # Intervalle de révision basé sur le nombre de révisions
        intervals = {
            0: timedelta(days=1),
            1: timedelta(days=3),
            2: timedelta(days=7),
            3: timedelta(days=14),
            4: timedelta(days=30),
            5: timedelta(days=60)
        }
        
        review_level = min(self.review_count, 5)
        return from_date + intervals[review_level]
    
    def mark_reviewed(self):
        now = datetime.now()
        self.last_reviewed_at = now
        self.review_count += 1
    
    @property
    def needs_review(self):
        """Détermine si la note doit être révisée basé sur la dernière révision"""
        if not self.last_reviewed_at:
            return True
            
        next_review = self._calculate_next_review_date(self.last_reviewed_at)
        return datetime.now() >= next_review

# Tests
def run_tests():
    print("Test de la propriété needs_review:")
    
    # Test 1: Note jamais révisée
    note1 = MockNote()
    print(f"Note jamais révisée: needs_review = {note1.needs_review}")
    
    # Test 2: Note révisée récemment (ne devrait pas nécessiter de révision)
    note2 = MockNote(last_reviewed_at=datetime.now(), review_count=1)
    print(f"Note révisée récemment (niveau 1): needs_review = {note2.needs_review}")
    
    # Test 3: Note révisée il y a longtemps (devrait nécessiter une révision)
    old_date = datetime.now() - timedelta(days=10)
    note3 = MockNote(last_reviewed_at=old_date, review_count=1)
    print(f"Note révisée il y a 10 jours (niveau 1): needs_review = {note3.needs_review}")
    
    # Test 4: Test de mark_reviewed
    note4 = MockNote(last_reviewed_at=old_date, review_count=0)
    print(f"Avant mark_reviewed: needs_review = {note4.needs_review}, review_count = {note4.review_count}")
    note4.mark_reviewed()
    print(f"Après mark_reviewed: needs_review = {note4.needs_review}, review_count = {note4.review_count}")
    
    # Test 5: Différents niveaux de révision
    for level in range(6):
        days_ago = 100  # Assez ancien pour déclencher needs_review
        note = MockNote(
            last_reviewed_at=datetime.now() - timedelta(days=days_ago),
            review_count=level
        )
        next_review = note._calculate_next_review_date(note.last_reviewed_at)
        due_in = next_review - (datetime.now() - timedelta(days=days_ago))
        print(f"Niveau {level}: Intervalle avant prochaine révision = {due_in}")

if __name__ == "__main__":
    run_tests()