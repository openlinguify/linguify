# **Synthèse : Transition Backend-Frontend avec Django REST Framework et Next.js**

---

## **1. Mise en place du Backend avec Django REST Framework**

### **Étapes principales :**

### **1.1. Création du Modèle :**
Le modèle **`Unit`** représente une unité de cours avec des champs multilingues :
```python
class Unit(models.Model):
    LEVEL_CHOICES = [
        ('A1', 'A1'),
        ('A2', 'A2'),
        ('B1', 'B1'),
        ('B2', 'B2'),
        ('C1', 'C1'),
        ('C2', 'C2'),
    ]
    title_en = models.CharField(max_length=100)
    title_fr = models.CharField(max_length=100)
    description_en = models.TextField(blank=True)
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES)
    order = models.PositiveIntegerField(default=1)
```

### **1.2. Création du Serializer :**
Le **serializer** transforme les objets **Unit** en JSON pour l'API :
```python
from rest_framework import serializers
from .models import Unit

class UnitSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = ['id', 'title', 'description', 'level', 'order']

    def get_title(self, obj):
        lang = self.context.get('request').query_params.get('lang', 'en')
        return getattr(obj, f"title_{lang}", obj.title_en)

    def get_description(self, obj):
        lang = self.context.get('request').query_params.get('lang', 'en')
        return getattr(obj, f"description_{lang}", obj.description_en)
```

### **1.3. Création de la Vue API :**
Vue paginée avec filtres dynamiques :
```python
from rest_framework.generics import ListAPIView
from .models import Unit
from .serializers import UnitSerializer
from rest_framework.permissions import AllowAny

class UnitAPIView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = UnitSerializer

    def get_queryset(self):
        queryset = Unit.objects.all().order_by('order')
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)
        return queryset
```

### **1.4. Routes API :**
```python
from django.urls import path
from .views import UnitAPIView

urlpatterns = [
    path('units/', UnitAPIView.as_view(), name='unit-list'),
]
```

### **1.5. Tests avec Postman ou CURL :**
- **GET** :
```
curl -X GET http://127.0.0.1:8000/api/v1/course/units/?level=A1
```
---

## **2. Mise en place du Frontend avec Next.js et TypeScript**

### **2.1. Installation :**
```bash
npx create-next-app@latest my-app --typescript
cd my-app
npm install axios
npm install @types/axios
```

### **2.2. Création d'un Composant React :**

**TypeScript pour les types de données :**
```typescript
type Unit = {
  id: number;
  title: string;
  description: string;
  level: string;
  order: number;
};

// Réponse paginée
type PaginatedResponse<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};
```

**Composant React :**
```typescript
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';

const UnitsGrid: React.FC = () => {
  const [units, setUnits] = useState<Unit[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchUnits = async () => {
      try {
        const response = await axios.get<PaginatedResponse<Unit>>(
          'http://127.0.0.1:8000/api/v1/course/units/'
        );
        setUnits(response.data.results);
      } catch (err) {
        setError("Erreur lors de la récupération des données.");
      } finally {
        setLoading(false);
      }
    };
    fetchUnits();
  }, []);

  if (loading) return <div>Chargement...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;

  return (
    <div style={{ display: 'grid', gap: '20px', padding: '20px' }}>
      {units.map(unit => (
        <div key={unit.id} onClick={() => router.push(`/units/${unit.id}`)}>
          <h3>{unit.title}</h3>
          <p>{unit.description}</p>
          <p>Niveau : {unit.level}</p>
          <p>Ordre : {unit.order}</p>
        </div>
      ))}
    </div>
  );
};

export default UnitsGrid;
```

### **2.3. Gestion des erreurs et du chargement :**
- **Chargement :** Affiche un message temporaire.
- **Erreurs :** Message clair si l'API échoue.

### **2.4. Tests Frontend :**
Accédez à :
```
http://localhost:3000/course/units
```

---

## **3. Résultat final :**

### **Réponse JSON API :**
```json
{
  "count": 12,
  "next": "http://127.0.0.1:8000/api/v1/course/units/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Greeting",
      "description": "Learn how to greet people.",
      "level": "A1",
      "order": 1
    }
  ]
}
```

### **Affichage :**
| Titre            | Description                         | Niveau | Ordre |
|------------------|-------------------------------------|--------|-------|
| Greeting         | Learn how to greet people.          | A1     | 1     |
| Introduction     | Learn to introduce yourself.        | A1     | 2     |

---

