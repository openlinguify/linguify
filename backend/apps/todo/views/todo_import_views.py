from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import models
import csv
import json
import logging
from datetime import datetime
from django.utils import timezone
from ..models.todo_models import Task, Project, PersonalStageType, Tag

logger = logging.getLogger(__name__)

class TaskImportModalHTMXView(LoginRequiredMixin, TemplateView):
    """HTMX view for task import modal"""
    template_name = 'todo/modals/import_modal.html'
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        html = render_to_string(self.template_name, context, request=request)
        return HttpResponse(html)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user's projects and stages for mapping
        projects = Project.objects.filter(user=user).order_by('name')
        stages = PersonalStageType.objects.filter(user=user).order_by('sequence')
        
        context.update({
            'projects': projects,
            'stages': stages,
        })
        
        return context

@method_decorator(csrf_exempt, name='dispatch')
class TaskImportProcessHTMXView(LoginRequiredMixin, TemplateView):
    """Process the imported file and create tasks"""
    
    def post(self, request, *args, **kwargs):
        try:
            uploaded_file = request.FILES.get('import_file')
            if not uploaded_file:
                return JsonResponse({
                    'success': False,
                    'error': 'No file uploaded'
                })
            
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == 'csv':
                return self.process_csv_file(uploaded_file)
            elif file_extension == 'json':
                return self.process_json_file(uploaded_file)
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Unsupported file format. Please use CSV or JSON files.'
                })
                
        except Exception as e:
            logger.error(f"Import error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Import failed: {str(e)}'
            })
    
    def process_csv_file(self, uploaded_file):
        """Process CSV file import"""
        user = self.request.user
        tasks_created = 0
        errors = []
        
        try:
            # Decode the file content
            file_content = uploaded_file.read().decode('utf-8')
            csv_reader = csv.DictReader(file_content.splitlines())
            
            for row_num, row in enumerate(csv_reader, start=2):
                try:
                    task_data = self.parse_csv_row(row, user)
                    if task_data:
                        task = Task.objects.create(**task_data)
                        tasks_created += 1
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'CSV processing failed: {str(e)}'
            })
        
        return JsonResponse({
            'success': True,
            'tasks_created': tasks_created,
            'errors': errors,
            'message': f'Successfully imported {tasks_created} tasks' + 
                      (f' with {len(errors)} errors' if errors else '')
        })
    
    def process_json_file(self, uploaded_file):
        """Process JSON file import"""
        user = self.request.user
        tasks_created = 0
        errors = []
        
        try:
            file_content = uploaded_file.read().decode('utf-8')
            data = json.loads(file_content)
            
            # Handle different JSON structures
            if isinstance(data, list):
                tasks_data = data
            elif isinstance(data, dict) and 'tasks' in data:
                tasks_data = data['tasks']
            elif isinstance(data, dict) and 'activities' in data:
                tasks_data = data['activities']
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid JSON format. Expected array of tasks or object with tasks/activities key.'
                })
            
            for task_num, task_data in enumerate(tasks_data, start=1):
                try:
                    parsed_data = self.parse_json_task(task_data, user)
                    if parsed_data:
                        task = Task.objects.create(**parsed_data)
                        tasks_created += 1
                except Exception as e:
                    errors.append(f"Task {task_num}: {str(e)}")
                    
        except json.JSONDecodeError as e:
            return JsonResponse({
                'success': False,
                'error': f'Invalid JSON file: {str(e)}'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'JSON processing failed: {str(e)}'
            })
        
        return JsonResponse({
            'success': True,
            'tasks_created': tasks_created,
            'errors': errors,
            'message': f'Successfully imported {tasks_created} tasks' + 
                      (f' with {len(errors)} errors' if errors else '')
        })
    
    def parse_csv_row(self, row, user):
        """Parse a CSV row into task data"""
        title = row.get('title', '').strip()
        if not title:
            return None
        
        # Get or create project
        project = None
        project_name = row.get('project', '').strip()
        if project_name and project_name != 'No Project':
            project, created = Project.objects.get_or_create(
                user=user,
                name=project_name,
                defaults={'description': f'Imported project: {project_name}'}
            )
        
        # Get or create stage
        stage = None
        stage_name = row.get('stage', '').strip()
        if stage_name and stage_name != 'No Stage':
            try:
                stage = PersonalStageType.objects.get(user=user, name=stage_name)
            except PersonalStageType.DoesNotExist:
                # Create new stage if it doesn't exist
                last_sequence = PersonalStageType.objects.filter(user=user).aggregate(
                    models.Max('sequence')
                )['sequence__max'] or 0
                stage = PersonalStageType.objects.create(
                    user=user,
                    name=stage_name,
                    sequence=last_sequence + 10,
                    color='#6B7280'  # Default gray color
                )
        
        # Parse priority
        priority = 0
        priority_str = row.get('priority', '').strip().lower()
        if priority_str == 'high':
            priority = 1
        elif priority_str == 'critical':
            priority = 2
        
        # Parse state
        state = '0_todo'  # default
        state_str = row.get('state', '').strip().lower()
        if 'progress' in state_str:
            state = '1_progress'
        elif 'review' in state_str:
            state = '2_review'
        elif 'done' in state_str:
            state = '1_done'
        
        # Parse dates
        created_at = timezone.now()
        due_date = None
        completed_at = None
        
        if row.get('created_at'):
            try:
                created_at = datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
            except:
                pass
        
        if row.get('due_date'):
            try:
                due_date = datetime.fromisoformat(row['due_date'].replace('Z', '+00:00'))
            except:
                pass
        
        if row.get('completed_at') and state == '1_done':
            try:
                completed_at = datetime.fromisoformat(row['completed_at'].replace('Z', '+00:00'))
            except:
                pass
        
        return {
            'user': user,
            'title': title,
            'description': row.get('description', ''),
            'state': state,
            'priority': priority,
            'project': project,
            'personal_stage_type': stage,
            'due_date': due_date,
            'created_at': created_at,
            'completed_at': completed_at,
            'progress_percentage': int(row.get('progress_percentage', 0)) if row.get('progress_percentage') else 0,
            'active': True,
        }
    
    def parse_json_task(self, task_data, user):
        """Parse JSON task data"""
        title = task_data.get('title', '').strip()
        if not title:
            return None
        
        # Similar parsing logic as CSV but for JSON structure
        project = None
        project_name = task_data.get('project', '').strip()
        if project_name and project_name != 'No Project':
            project, created = Project.objects.get_or_create(
                user=user,
                name=project_name,
                defaults={'description': f'Imported project: {project_name}'}
            )
        
        stage = None
        stage_name = task_data.get('stage', '').strip()
        if stage_name and stage_name != 'No Stage':
            try:
                stage = PersonalStageType.objects.get(user=user, name=stage_name)
            except PersonalStageType.DoesNotExist:
                last_sequence = PersonalStageType.objects.filter(user=user).aggregate(
                    models.Max('sequence')
                )['sequence__max'] or 0
                stage = PersonalStageType.objects.create(
                    user=user,
                    name=stage_name,
                    sequence=last_sequence + 10,
                    color='#6B7280'
                )
        
        # Parse priority and state similar to CSV
        priority = 0
        if isinstance(task_data.get('priority'), int):
            priority = task_data.get('priority', 0)
        else:
            priority_str = str(task_data.get('priority', '')).lower()
            if 'high' in priority_str:
                priority = 1
            elif 'critical' in priority_str:
                priority = 2
        
        state = '0_todo'
        state_str = str(task_data.get('state', '')).lower()
        if 'progress' in state_str:
            state = '1_progress'
        elif 'review' in state_str:
            state = '2_review'
        elif 'done' in state_str:
            state = '1_done'
        
        # Parse dates
        created_at = timezone.now()
        due_date = None
        completed_at = None
        
        if task_data.get('created_at'):
            try:
                created_at = datetime.fromisoformat(str(task_data['created_at']).replace('Z', '+00:00'))
            except:
                pass
        
        if task_data.get('due_date'):
            try:
                due_date = datetime.fromisoformat(str(task_data['due_date']).replace('Z', '+00:00'))
            except:
                pass
        
        if task_data.get('completed_at') and state == '1_done':
            try:
                completed_at = datetime.fromisoformat(str(task_data['completed_at']).replace('Z', '+00:00'))
            except:
                pass
        
        return {
            'user': user,
            'title': title,
            'description': task_data.get('description', ''),
            'state': state,
            'priority': priority,
            'project': project,
            'personal_stage_type': stage,
            'due_date': due_date,
            'created_at': created_at,
            'completed_at': completed_at,
            'progress_percentage': int(task_data.get('progress_percentage', 0)) if task_data.get('progress_percentage') else 0,
            'active': True,
        }