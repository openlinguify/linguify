"""
HTMX Views for Revision App
Demonstrating Tailwind CSS + HTMX patterns for flashcard interactions
"""

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
import json
import time


def flashcard_examples(request):
    """
    Main demo page showing Tailwind + HTMX flashcard components
    """
    context = {
        'page_title': 'Flashcard Examples',
        'audio_settings': json.dumps({
            'enabled': True,
            'voice_front': 'en-US',
            'voice_back': 'fr-FR',
        })
    }
    return render(request, 'revision/flashcard_examples.html', context)


@require_http_methods(["GET"])
def get_sample_card(request, card_id):
    """
    HTMX endpoint: Load sample card details
    """
    # Simulate some processing delay
    time.sleep(0.5)
    
    sample_cards = {
        1: {
            'title': 'English Vocabulary',
            'description': 'Essential words for daily conversation',
            'cards_count': 24,
            'progress': 60,
            'last_studied': '2 hours ago',
            'color': 'linguify-primary'
        },
        2: {
            'title': 'French Verbs',
            'description': 'Common French verb conjugations',
            'cards_count': 18,
            'progress': 40,
            'last_studied': '1 day ago',
            'color': 'linguify-accent'
        },
        3: {
            'title': 'Spanish Phrases',
            'description': 'Useful phrases for travel',
            'cards_count': 32,
            'progress': 80,
            'last_studied': '3 hours ago',
            'color': 'linguify-secondary'
        }
    }
    
    card_data = sample_cards.get(int(card_id), sample_cards[1])
    
    # Return rendered HTML fragment
    html = f"""
    <div class="bg-white rounded-card p-6 m-4 max-w-md w-full">
        <div class="flex justify-between items-start mb-4">
            <h3 class="text-xl font-semibold text-linguify-primary">{card_data['title']}</h3>
            <button onclick="this.closest('#card-detail-modal').classList.add('hidden')" 
                    class="text-gray-400 hover:text-gray-600">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        </div>
        
        <p class="text-gray-600 mb-4">{card_data['description']}</p>
        
        <div class="space-y-3">
            <div class="flex justify-between">
                <span class="text-sm text-gray-500">Cards:</span>
                <span class="font-medium">{card_data['cards_count']}</span>
            </div>
            <div class="flex justify-between">
                <span class="text-sm text-gray-500">Progress:</span>
                <span class="font-medium">{card_data['progress']}%</span>
            </div>
            <div class="flex justify-between">
                <span class="text-sm text-gray-500">Last studied:</span>
                <span class="font-medium">{card_data['last_studied']}</span>
            </div>
        </div>
        
        <div class="mt-6 flex gap-3">
            <button class="btn-linguify flex-1" 
                    onclick="this.closest('#card-detail-modal').classList.add('hidden')">
                Start Studying
            </button>
            <button class="btn-linguify-outline" 
                    onclick="this.closest('#card-detail-modal').classList.add('hidden')">
                Edit Deck
            </button>
        </div>
    </div>
    """
    
    return HttpResponse(html)


@require_http_methods(["GET"])
def load_study_mode(request, mode):
    """
    HTMX endpoint: Load study mode interface
    """
    # Simulate loading delay
    time.sleep(0.3)
    
    study_modes = {
        'flashcards': {
            'title': 'Flashcard Study',
            'description': 'Review cards with spaced repetition algorithm',
            'icon': '🔄',
            'component': 'flashcard_study'
        },
        'quiz': {
            'title': 'Quiz Mode',
            'description': 'Multiple choice questions for active recall',
            'icon': '🎯',
            'component': 'quiz_study'
        },
        'match': {
            'title': 'Matching Game',
            'description': 'Match terms with their definitions',
            'icon': '🧩',
            'component': 'match_study'
        },
        'write': {
            'title': 'Writing Practice',
            'description': 'Type the correct answers to improve retention',
            'icon': '✍️',
            'component': 'write_study'
        }
    }
    
    mode_data = study_modes.get(mode, study_modes['flashcards'])
    
    if mode == 'flashcards':
        html = render_flashcard_study_interface()
    elif mode == 'quiz':
        html = render_quiz_study_interface()
    elif mode == 'match':
        html = render_match_study_interface()
    elif mode == 'write':
        html = render_write_study_interface()
    else:
        html = f"""
        <div class="text-center py-12">
            <div class="text-6xl mb-4">{mode_data['icon']}</div>
            <h3 class="text-xl font-semibold text-linguify-primary mb-2">{mode_data['title']}</h3>
            <p class="text-gray-600 mb-6">{mode_data['description']}</p>
            <button class="btn-linguify">Start Session</button>
        </div>
        """
    
    return HttpResponse(html)


def render_flashcard_study_interface():
    """Render the flashcard study interface"""
    return """
    <div class="max-w-md mx-auto">
        <div class="text-center mb-6">
            <h3 class="text-xl font-semibold text-linguify-primary mb-2">Flashcard Study</h3>
            <p class="text-gray-600">Card 1 of 24 • Deck: English Vocabulary</p>
        </div>
        
        <div class="flashcard mx-auto" onclick="this.classList.toggle('flipped')" style="cursor: pointer;">
            <div class="flashcard-inner">
                <div class="flashcard-front">
                    <div class="text-center">
                        <h4 class="text-xl font-semibold mb-4">What does "serendipity" mean?</h4>
                        <p class="text-sm opacity-80">Click to reveal answer</p>
                    </div>
                </div>
                <div class="flashcard-back">
                    <div class="text-center">
                        <h4 class="text-lg font-semibold mb-2">The occurrence of happy or beneficial events by chance</h4>
                        <p class="text-sm opacity-80">How well did you know this?</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="mt-6 grid grid-cols-3 gap-3">
            <button class="py-3 px-4 bg-red-500 hover:bg-red-600 text-white rounded-form font-medium transition-colors"
                    hx-post="/revision/api/study/rate/" hx-vals='{"rating": "again"}' hx-target="#study-area">
                Again
            </button>
            <button class="py-3 px-4 bg-yellow-500 hover:bg-yellow-600 text-white rounded-form font-medium transition-colors"
                    hx-post="/revision/api/study/rate/" hx-vals='{"rating": "hard"}' hx-target="#study-area">
                Hard
            </button>
            <button class="py-3 px-4 bg-green-500 hover:bg-green-600 text-white rounded-form font-medium transition-colors"
                    hx-post="/revision/api/study/rate/" hx-vals='{"rating": "easy"}' hx-target="#study-area">
                Easy
            </button>
        </div>
        
        <div class="mt-4 bg-gray-200 rounded-full h-2">
            <div class="bg-linguify-primary h-2 rounded-full" style="width: 4.17%"></div>
        </div>
        <p class="text-center text-sm text-gray-500 mt-2">Study Progress</p>
    </div>
    """


def render_quiz_study_interface():
    """Render the quiz study interface"""
    return """
    <div class="max-w-2xl mx-auto">
        <div class="text-center mb-6">
            <h3 class="text-xl font-semibold text-linguify-primary mb-2">Quiz Mode</h3>
            <p class="text-gray-600">Question 1 of 10 • Score: 0/0</p>
        </div>
        
        <div class="bg-white rounded-card shadow-card p-6 mb-6">
            <h4 class="text-lg font-semibold text-gray-800 mb-6">
                Which of the following best describes "serendipity"?
            </h4>
            
            <div class="space-y-3">
                <label class="flex items-center p-4 border border-gray-200 rounded-form hover:border-linguify-primary cursor-pointer transition-colors">
                    <input type="radio" name="quiz-answer" value="a" class="mr-4">
                    <span>A planned and expected discovery</span>
                </label>
                <label class="flex items-center p-4 border border-gray-200 rounded-form hover:border-linguify-primary cursor-pointer transition-colors">
                    <input type="radio" name="quiz-answer" value="b" class="mr-4">
                    <span>The occurrence of happy events by chance</span>
                </label>
                <label class="flex items-center p-4 border border-gray-200 rounded-form hover:border-linguify-primary cursor-pointer transition-colors">
                    <input type="radio" name="quiz-answer" value="c" class="mr-4">
                    <span>A feeling of sadness or regret</span>
                </label>
                <label class="flex items-center p-4 border border-gray-200 rounded-form hover:border-linguify-primary cursor-pointer transition-colors">
                    <input type="radio" name="quiz-answer" value="d" class="mr-4">
                    <span>The fear of making decisions</span>
                </label>
            </div>
        </div>
        
        <div class="text-center">
            <button class="btn-linguify" 
                    hx-post="/revision/api/quiz/submit/" 
                    hx-include="[name='quiz-answer']:checked"
                    hx-target="#study-area">
                Submit Answer
            </button>
        </div>
    </div>
    """


def render_match_study_interface():
    """Render the matching game interface"""
    return """
    <div class="max-w-4xl mx-auto">
        <div class="text-center mb-6">
            <h3 class="text-xl font-semibold text-linguify-primary mb-2">Matching Game</h3>
            <p class="text-gray-600">Match the terms with their definitions • Time: 00:00</p>
        </div>
        
        <div class="grid md:grid-cols-2 gap-8">
            <div>
                <h4 class="font-semibold text-gray-800 mb-4">Terms</h4>
                <div class="space-y-3">
                    <div class="p-4 bg-linguify-primary text-white rounded-form cursor-pointer hover:bg-linguify-primary-dark transition-colors"
                         onclick="selectMatchItem(this, 'serendipity')">
                        Serendipity
                    </div>
                    <div class="p-4 bg-linguify-primary text-white rounded-form cursor-pointer hover:bg-linguify-primary-dark transition-colors"
                         onclick="selectMatchItem(this, 'ubiquitous')">
                        Ubiquitous
                    </div>
                    <div class="p-4 bg-linguify-primary text-white rounded-form cursor-pointer hover:bg-linguify-primary-dark transition-colors"
                         onclick="selectMatchItem(this, 'ephemeral')">
                        Ephemeral
                    </div>
                    <div class="p-4 bg-linguify-primary text-white rounded-form cursor-pointer hover:bg-linguify-primary-dark transition-colors"
                         onclick="selectMatchItem(this, 'mellifluous')">
                        Mellifluous
                    </div>
                </div>
            </div>
            
            <div>
                <h4 class="font-semibold text-gray-800 mb-4">Definitions</h4>
                <div class="space-y-3">
                    <div class="p-4 bg-linguify-accent text-white rounded-form cursor-pointer hover:bg-emerald-500 transition-colors"
                         onclick="selectMatchItem(this, 'pleasant-sounding')">
                        Pleasant-sounding; musical
                    </div>
                    <div class="p-4 bg-linguify-accent text-white rounded-form cursor-pointer hover:bg-emerald-500 transition-colors"
                         onclick="selectMatchItem(this, 'everywhere')">
                        Present everywhere; widespread
                    </div>
                    <div class="p-4 bg-linguify-accent text-white rounded-form cursor-pointer hover:bg-emerald-500 transition-colors"
                         onclick="selectMatchItem(this, 'chance-discovery')">
                        Happy or beneficial discovery by chance
                    </div>
                    <div class="p-4 bg-linguify-accent text-white rounded-form cursor-pointer hover:bg-emerald-500 transition-colors"
                         onclick="selectMatchItem(this, 'short-lived')">
                        Lasting for a very short time
                    </div>
                </div>
            </div>
        </div>
        
        <div class="mt-8 text-center">
            <p class="text-gray-600 mb-4">Matches: 0/4 • Score: 0 points</p>
            <button class="btn-linguify-outline" onclick="resetMatching()">Reset Game</button>
        </div>
    </div>
    
    <script>
    let selectedTerm = null;
    let selectedDefinition = null;
    let matches = 0;
    
    function selectMatchItem(element, value) {
        // Remove previous selections
        document.querySelectorAll('.selected').forEach(el => el.classList.remove('selected'));
        
        // Add selection styling
        element.classList.add('selected');
        element.style.transform = 'scale(0.95)';
        setTimeout(() => element.style.transform = 'scale(1)', 150);
        
        if (element.closest('div').querySelector('h4').textContent.includes('Terms')) {
            selectedTerm = value;
        } else {
            selectedDefinition = value;
        }
        
        // Check for match
        if (selectedTerm && selectedDefinition) {
            checkMatch(selectedTerm, selectedDefinition);
        }
    }
    
    function checkMatch(term, definition) {
        const correctMatches = {
            'serendipity': 'chance-discovery',
            'ubiquitous': 'everywhere',
            'ephemeral': 'short-lived',
            'mellifluous': 'pleasant-sounding'
        };
        
        if (correctMatches[term] === definition) {
            // Correct match
            matches++;
            document.querySelectorAll('.selected').forEach(el => {
                el.style.backgroundColor = '#10b981';
                el.style.pointerEvents = 'none';
                el.classList.remove('selected');
            });
            
            if (matches === 4) {
                setTimeout(() => alert('Congratulations! All matches completed!'), 500);
            }
        } else {
            // Incorrect match
            document.querySelectorAll('.selected').forEach(el => {
                el.style.backgroundColor = '#ef4444';
                setTimeout(() => {
                    el.style.backgroundColor = '';
                    el.classList.remove('selected');
                }, 1000);
            });
        }
        
        selectedTerm = null;
        selectedDefinition = null;
    }
    
    function resetMatching() {
        matches = 0;
        selectedTerm = null;
        selectedDefinition = null;
        document.querySelectorAll('[onclick*="selectMatchItem"]').forEach(el => {
            el.style.backgroundColor = '';
            el.style.pointerEvents = '';
            el.classList.remove('selected');
        });
    }
    </script>
    """


def render_write_study_interface():
    """Render the writing practice interface"""
    return """
    <div class="max-w-lg mx-auto">
        <div class="text-center mb-6">
            <h3 class="text-xl font-semibold text-linguify-primary mb-2">Writing Practice</h3>
            <p class="text-gray-600">Type the correct answer • Card 1 of 24</p>
        </div>
        
        <div class="bg-white rounded-card shadow-card p-6 mb-6 text-center">
            <div class="text-6xl mb-4">🇫🇷</div>
            <h4 class="text-xl font-semibold text-gray-800 mb-2">
                "The occurrence of happy events by chance"
            </h4>
            <p class="text-gray-600">What English word matches this definition?</p>
        </div>
        
        <div class="mb-6">
            <input type="text" 
                   class="form-input text-center text-xl font-medium"
                   placeholder="Type your answer..."
                   hx-post="/revision/api/write/check/"
                   hx-trigger="keyup[keyCode==13]"
                   hx-target="#answer-feedback"
                   autocomplete="off"
                   spellcheck="false">
        </div>
        
        <div id="answer-feedback" class="text-center mb-6">
            <p class="text-gray-500">Press Enter to check your answer</p>
        </div>
        
        <div class="text-center">
            <button class="btn-linguify-outline mr-3" 
                    onclick="this.previousElementSibling.previousElementSibling.querySelector('input').value = ''; document.getElementById('answer-feedback').innerHTML = '<p class=&quot;text-gray-500&quot;>Press Enter to check your answer</p>'">
                Clear
            </button>
            <button class="btn-linguify" 
                    hx-post="/revision/api/write/skip/" 
                    hx-target="#study-area">
                Skip Card
            </button>
        </div>
    </div>
    """


@require_http_methods(["GET"])
def preview_card(request):
    """
    HTMX endpoint: Live preview of card content
    """
    front = request.GET.get('front', '').strip()
    back = request.GET.get('back', '').strip()
    
    html = f"""
    <div class="flashcard-inner">
        <div class="flashcard-front">
            <div class="text-center">
                <h4 class="text-lg font-semibold mb-2">
                    {front if front else 'Front content will appear here'}
                </h4>
                <p class="text-sm opacity-80">Click to flip</p>
            </div>
        </div>
        <div class="flashcard-back">
            <div class="text-center">
                <h4 class="text-lg font-semibold mb-2">
                    {back if back else 'Back content will appear here'}
                </h4>
                <p class="text-sm opacity-80">Click to flip back</p>
            </div>
        </div>
    </div>
    """
    
    return HttpResponse(html)


@require_http_methods(["POST"])
def create_card(request):
    """
    HTMX endpoint: Create new flashcard
    """
    front = request.POST.get('front', '').strip()
    back = request.POST.get('back', '').strip()
    
    if not front or not back:
        return HttpResponse("""
            <div class="p-4 bg-red-50 border border-red-200 rounded-form">
                <p class="text-red-800">Both front and back content are required.</p>
            </div>
        """, status=400)
    
    # Simulate card creation (in real app, save to database)
    time.sleep(0.5)
    
    return HttpResponse("""
        <div class="p-4 bg-green-50 border border-green-200 rounded-form">
            <p class="text-green-800 font-medium">✅ Card created successfully!</p>
            <p class="text-green-600 text-sm mt-1">Your new flashcard has been added to the deck.</p>
        </div>
    """, status=201)


@require_http_methods(["GET"])
def search_cards(request):
    """
    HTMX endpoint: Search cards with instant results
    """
    query = request.GET.get('q', '').strip().lower()
    category = request.GET.get('category', '')
    
    # Simulate search delay
    time.sleep(0.2)
    
    # Sample cards data
    all_cards = [
        {'id': 1, 'question': 'What is HTML?', 'category': 'web-dev', 'tags': ['Web Development']},
        {'id': 2, 'question': 'Explain CSS flexbox', 'category': 'css', 'tags': ['CSS']},
        {'id': 3, 'question': 'What is JavaScript?', 'category': 'programming', 'tags': ['Programming']},
        {'id': 4, 'question': 'Define responsive design', 'category': 'css', 'tags': ['CSS', 'Design']},
        {'id': 5, 'question': 'What are React hooks?', 'category': 'programming', 'tags': ['React', 'JavaScript']},
        {'id': 6, 'question': 'Explain REST APIs', 'category': 'web-dev', 'tags': ['API', 'Backend']},
    ]
    
    # Filter cards based on search query and category
    filtered_cards = all_cards
    
    if query:
        filtered_cards = [card for card in filtered_cards if query in card['question'].lower()]
    
    if category:
        filtered_cards = [card for card in filtered_cards if card['category'] == category]
    
    if not filtered_cards:
        return HttpResponse("""
            <div class="col-span-full text-center py-8">
                <div class="text-gray-400 text-6xl mb-4">🔍</div>
                <h3 class="text-lg font-medium text-gray-600 mb-2">No cards found</h3>
                <p class="text-gray-500">Try adjusting your search terms or filters</p>
            </div>
        """)
    
    html = ""
    for card in filtered_cards:
        tags_html = " ".join([f'<span class="tag tag-primary">{tag}</span>' for tag in card['tags']])
        html += f"""
        <div class="deck-card">
            <h3 class="font-semibold mb-2">Card #{card['id']}</h3>
            <p class="text-sm text-gray-600 mb-3">{card['question']}</p>
            <div class="flex gap-1 flex-wrap">{tags_html}</div>
        </div>
        """
    
    return HttpResponse(html)