import pytest
import sys
import re
from pathlib import Path
from unittest.mock import patch, MagicMock, call

# Import the module to test
from scripts.tools.modules.create_new_module import (
  validate_module_name,
  validate_icon_name,
  create_file,
  capitalize,
  generate_django_admin,
  generate_django_models,
  generate_react_view,
  generate_react_components_index,
  update_django_settings,
  update_django_urls,
  update_dashboard_menu,
  create_django_app,
  create_react_module,
  create_react_app_route,
  main
)

class TestValidationFunctions:
  def test_validate_module_name_valid(self):
    assert validate_module_name('quiz') == 'quiz'
    assert validate_module_name('flashcards') == 'flashcards'
    assert validate_module_name('user_profiles') == 'user_profiles'
  
  def test_validate_module_name_invalid(self):
    with pytest.raises(SystemExit):
      validate_module_name('Quiz')  # Uppercase not allowed
    
    with pytest.raises(SystemExit):
      validate_module_name('123quiz')  # Starting with number not allowed
    
    with pytest.raises(SystemExit):
      validate_module_name('quiz-module')  # Hyphens not allowed
  
  def test_validate_icon_name_valid(self):
    assert validate_icon_name('Brain') == 'Brain'
    assert validate_icon_name('BookOpen') == 'BookOpen'
  
  def test_validate_icon_name_invalid(self):
    with pytest.raises(SystemExit):
      validate_icon_name('brain')  # Lowercase first letter not allowed
    
    with pytest.raises(SystemExit):
      validate_icon_name('book-open')  # Hyphens not allowed

class TestHelperFunctions:
  def test_capitalize(self):
    assert capitalize('quiz') == 'Quiz'
    assert capitalize('flashcards') == 'Flashcards'
    assert capitalize('') == ''
    # Test edge case with None
    assert capitalize(None) == None

  @patch('pathlib.Path.mkdir')
  @patch('pathlib.Path.write_text')
  @patch('builtins.print')
  def test_create_file(self, mock_print, mock_write_text, mock_mkdir):
    path = Path('test/path/file.txt')
    content = 'Test content'
    
    create_file(path, content)
    
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    mock_write_text.assert_called_once_with(content)
    mock_print.assert_called_once()

class TestTemplateGenerators:
  def test_generate_django_admin(self):
    result = generate_django_admin('quiz')
    assert 'from django.contrib import admin' in result
    assert 'class QuizAdmin(admin.ModelAdmin):' in result
    assert "list_display = ('id', 'title', 'created_at', 'updated_at')" in result
  
  def test_generate_django_models(self):
    result = generate_django_models('quiz', 'A quiz module')
    assert 'class Quiz(models.Model):' in result
    assert 'A quiz module' in result
    assert "user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizs')" in result
  
  def test_generate_react_view(self):
    result = generate_react_view('quiz', 'Brain', 'Quiz module')
    assert "'use client';" in result
    assert 'import { Brain } from' in result
    assert 'const QuizView: React.FC = () => {' in result
    assert 'Quiz module' in result
  
  def test_generate_react_components_index(self):
    result = generate_react_components_index('quiz')
    assert 'export { default as QuizView } from' in result

@pytest.fixture
def mock_filesystem():
  """Fixture to mock filesystem operations"""
  with patch('pathlib.Path.mkdir'), \
     patch('pathlib.Path.write_text'), \
     patch('pathlib.Path.exists', return_value=False), \
     patch('builtins.print'):
    yield

class TestCreateFunctions:
  @patch('scripts.tools.modules.create_new_module.update_django_settings')
  @patch('scripts.tools.modules.create_new_module.update_django_urls')
  @patch('scripts.tools.modules.create_new_module.create_file')
  @patch('pathlib.Path.exists', return_value=False)
  @patch('pathlib.Path.mkdir')
  def test_create_django_app(self, mock_mkdir, mock_exists, mock_create_file, 
                mock_update_urls, mock_update_settings):
    create_django_app('quiz', 'Quiz module')
    
    # Check if update functions were called
    mock_update_settings.assert_called_once_with('quiz')
    mock_update_urls.assert_called_once_with('quiz')
    
    # Check if files were created
    assert any('__init__.py' in str(call) for call in mock_create_file.call_args_list)
    assert any('models.py' in str(call) for call in mock_create_file.call_args_list)
  
  @patch('scripts.tools.modules.create_new_module.update_dashboard_menu')
  @patch('scripts.tools.modules.create_new_module.create_file')
  @patch('pathlib.Path.exists', return_value=False)
  @patch('pathlib.Path.mkdir')
  def test_create_react_module(self, mock_mkdir, mock_exists, mock_create_file, mock_update_menu):
    create_react_module('quiz', 'Brain', 'Quiz module')
    
    # Check if update function was called
    mock_update_menu.assert_called_once_with('quiz', 'Brain', 'Quiz module')
    
    # Check if files were created
    assert any('index.ts' in str(call) for call in mock_create_file.call_args_list)
  
  @patch('scripts.tools.modules.create_new_module.create_file')
  @patch('pathlib.Path.exists', return_value=False)
  @patch('pathlib.Path.mkdir')
  def test_create_react_app_route(self, mock_mkdir, mock_exists, mock_create_file):
    create_react_app_route('quiz', 'Quiz module')
    
    # Check if files were created
    assert any('page.tsx' in str(call) for call in mock_create_file.call_args_list)
    assert any('layout.tsx' in str(call) for call in mock_create_file.call_args_list)

class TestUpdateFunctions:
  def test_update_django_settings_file_not_found(self):
    with patch('pathlib.Path.exists', return_value=False), \
       patch('builtins.print') as mock_print:
      update_django_settings('quiz')
      assert mock_print.call_args_list[0][0][0].startswith("Warning: Could not find")
  
  def test_update_django_settings_success(self):
    mock_content = """
INSTALLED_APPS = [
  # Django built-in apps
  'django.contrib.admin',
  
  # Project django_apps
  'apps.core',
  
  # Django REST framework modules
  'rest_framework',
]
"""
    with patch('pathlib.Path.exists', return_value=True), \
       patch('pathlib.Path.read_text', return_value=mock_content), \
       patch('pathlib.Path.write_text') as mock_write, \
       patch('builtins.print'):
      
      update_django_settings('quiz')
      
      # Check that write_text was called with content containing the new app
      written_content = mock_write.call_args[0][0]
      assert "'apps.quiz'," in written_content
  
  def test_update_django_urls_file_not_found(self):
    with patch('pathlib.Path.exists', return_value=False), \
       patch('builtins.print') as mock_print:
      update_django_urls('quiz')
      assert mock_print.call_args_list[0][0][0].startswith("Warning: Could not find")
  
  def test_update_django_urls_success(self):
    mock_content = """
urlpatterns = [
  path('admin/', admin.site.urls),
  path('api/v1/auth/', include('authentication.urls', namespace='authentication')),
]
"""
    with patch('pathlib.Path.exists', return_value=True), \
       patch('pathlib.Path.read_text', return_value=mock_content), \
       patch('pathlib.Path.write_text') as mock_write, \
       patch('re.search') as mock_search, \
       patch('re.findall') as mock_findall, \
       patch('builtins.print'):
      
      # Mock regex results for urlpatterns
      mock_search.side_effect = lambda pattern, string, flags=0: \
        re.search(pattern, string, flags) if 'urlpatterns' in pattern else None
      mock_findall.return_value = ["    path('api/v1/auth/', include('authentication.urls', namespace='authentication')),\n"]
      
      update_django_urls('quiz')
      
      # Verify that write_text was called
      assert mock_write.called

class TestIntegration:
  @patch('scripts.tools.modules.create_new_module.argparse.ArgumentParser.parse_args')
  @patch('scripts.tools.modules.create_new_module.validate_module_name')
  @patch('scripts.tools.modules.create_new_module.validate_icon_name')
  @patch('scripts.tools.modules.create_new_module.create_django_app')
  @patch('scripts.tools.modules.create_new_module.create_react_module')
  @patch('scripts.tools.modules.create_new_module.create_react_app_route')
  def test_main(self, mock_create_route, mock_create_react, mock_create_django, 
          mock_validate_icon, mock_validate_name, mock_parse_args):
    # Setup mock arguments
    mock_args = MagicMock()
    mock_args.module_name = 'quiz'
    mock_args.module_icon = 'Brain'
    mock_args.description = 'Quiz module'
    mock_parse_args.return_value = mock_args
    
    # Setup validation returns
    mock_validate_name.return_value = 'quiz'
    mock_validate_icon.return_value = 'Brain'
    
    with patch('builtins.print'):
      main()
    
    # Check function calls
    mock_validate_name.assert_called_once_with('quiz')
    mock_validate_icon.assert_called_once_with('Brain')
    mock_create_django.assert_called_once_with('quiz', 'Quiz module')
    mock_create_react.assert_called_once_with('quiz', 'Brain', 'Quiz module')
    mock_create_route.assert_called_once_with('quiz', 'Quiz module')
    
  def test_existing_directories(self):
    with patch('pathlib.Path.exists', return_value=True), \
       patch('builtins.print') as mock_print, \
       patch('scripts.tools.modules.create_new_module.update_django_settings'), \
       patch('scripts.tools.modules.create_new_module.update_django_urls'):
      
      create_django_app('quiz', 'Quiz module')
      
      # Check warning message
      warning_message = mock_print.call_args_list[0][0][0]
      assert "Warning: Directory" in warning_message
      assert "already exists" in warning_message