# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.
from django.contrib import admin
from django.utils.html import format_html
from django.db import models


class PairsStatusFilter(admin.SimpleListFilter):
    """Filtre personnalisé pour filtrer les exercices par statut de paires."""
    title = 'Statut des paires'
    parameter_name = 'pairs_status'
    
    def lookups(self, request, model_admin):
        return (
            ('complete', '✅ Complet'),
            ('incomplete', '⚠️ Incomplet'),
            ('excess', '↑ Excès'),
            ('empty', '❌ Vide'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'complete':
            # Exercices où le nombre réel = nombre configuré
            return queryset.filter(
                vocabulary_words__in=queryset.values_list('vocabulary_words', flat=True)
            ).annotate(
                vocab_count=models.Count('vocabulary_words')
            ).filter(vocab_count=models.F('pairs_count'))
        
        elif self.value() == 'incomplete':
            # Exercices où le nombre réel < nombre configuré
            return queryset.annotate(
                vocab_count=models.Count('vocabulary_words')
            ).filter(vocab_count__lt=models.F('pairs_count'))
        
        elif self.value() == 'excess':
            # Exercices où le nombre réel > nombre configuré
            return queryset.annotate(
                vocab_count=models.Count('vocabulary_words')
            ).filter(vocab_count__gt=models.F('pairs_count'))
        
        elif self.value() == 'empty':
            # Exercices sans vocabulaire
            return queryset.annotate(
                vocab_count=models.Count('vocabulary_words')
            ).filter(vocab_count=0)
        
        return queryset


class PairsCountRangeFilter(admin.SimpleListFilter):
    """Filtre personnalisé pour filtrer par plage de nombre de paires."""
    title = 'Nombre de paires'
    parameter_name = 'pairs_range'
    
    def lookups(self, request, model_admin):
        return (
            ('1-5', '1-5 paires'),
            ('6-8', '6-8 paires'),
            ('9-12', '9-12 paires'),
            ('13+', '13+ paires'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == '1-5':
            return queryset.filter(pairs_count__range=(1, 5))
        elif self.value() == '6-8':
            return queryset.filter(pairs_count__range=(6, 8))
        elif self.value() == '9-12':
            return queryset.filter(pairs_count__range=(9, 12))
        elif self.value() == '13+':
            return queryset.filter(pairs_count__gte=13)
        
        return queryset