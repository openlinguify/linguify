from django.core.management.base import BaseCommand
from jobs.models import Department, JobPosition


class Command(BaseCommand):
    help = 'Create sample job positions for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample departments and job positions...')

        # Create departments
        engineering, _ = Department.objects.get_or_create(
            name='Engineering',
            defaults={'description': 'Software development and technical roles'}
        )
        
        product, _ = Department.objects.get_or_create(
            name='Product',
            defaults={'description': 'Product management and design roles'}
        )
        
        marketing, _ = Department.objects.get_or_create(
            name='Marketing',
            defaults={'description': 'Marketing and growth roles'}
        )
        
        sales, _ = Department.objects.get_or_create(
            name='Sales',
            defaults={'description': 'Business development and sales roles'}
        )

        # Create sample job positions
        jobs_data = [
            {
                'title': 'Senior Python Developer',
                'department': engineering,
                'location': 'Paris, France',
                'employment_type': 'full_time',
                'experience_level': 'senior',
                'description': 'We are looking for a Senior Python Developer to join our engineering team and help build the future of language learning. You will work on our core platform, developing new features and improving existing systems.',
                'requirements': '• 5+ years of Python development experience\n• Experience with Django or FastAPI\n• Knowledge of PostgreSQL and Redis\n• Experience with Docker and AWS\n• Strong understanding of RESTful APIs\n• Experience with testing frameworks (pytest)',
                'responsibilities': '• Develop and maintain backend services\n• Design and implement new features\n• Code review and mentoring junior developers\n• Participate in architecture decisions\n• Collaborate with product and design teams\n• Optimize application performance',
                'benefits': 'Competitive salary, health insurance, flexible work hours, remote work options, professional development budget',
                'salary_min': 55000,
                'salary_max': 75000,
                'application_email': 'jobs@linguify.com',
                'is_featured': True,
            },
            {
                'title': 'Frontend Developer (React/Next.js)',
                'department': engineering,
                'location': 'Remote',
                'employment_type': 'full_time',
                'experience_level': 'mid',
                'description': 'Join our frontend team to create beautiful and intuitive user interfaces for our language learning platform. You will work with React, Next.js, and TypeScript to deliver exceptional user experiences.',
                'requirements': '• 3+ years of React development experience\n• Strong knowledge of TypeScript\n• Experience with Next.js\n• Familiarity with state management (Redux, Zustand)\n• Knowledge of CSS frameworks (Tailwind CSS preferred)\n• Experience with testing (Jest, Cypress)',
                'responsibilities': '• Build responsive and accessible user interfaces\n• Implement new features and improve existing ones\n• Collaborate with designers and backend developers\n• Optimize application performance\n• Write unit and integration tests\n• Participate in code reviews',
                'benefits': 'Competitive salary, health insurance, remote work, learning budget, modern equipment',
                'salary_min': 45000,
                'salary_max': 60000,
                'application_email': 'jobs@linguify.com',
                'is_featured': False,
            },
            {
                'title': 'UX/UI Designer',
                'department': product,
                'location': 'Lyon, France',
                'employment_type': 'full_time',
                'experience_level': 'mid',
                'description': 'We are seeking a talented UX/UI Designer to help create intuitive and engaging learning experiences for our users. You will work closely with our product and engineering teams to design user-centered solutions.',
                'requirements': '• 3+ years of UX/UI design experience\n• Proficiency in Figma and Adobe Creative Suite\n• Strong understanding of user-centered design principles\n• Experience with design systems\n• Knowledge of accessibility guidelines\n• Portfolio demonstrating strong design skills',
                'responsibilities': '• Design user interfaces for web and mobile applications\n• Conduct user research and usability testing\n• Create wireframes, prototypes, and design systems\n• Collaborate with product managers and developers\n• Iterate on designs based on user feedback\n• Maintain design consistency across platforms',
                'benefits': 'Competitive salary, health insurance, creative workspace, design tools budget, conference attendance',
                'salary_min': 40000,
                'salary_max': 55000,
                'application_email': 'jobs@linguify.com',
                'is_featured': False,
            },
            {
                'title': 'Product Marketing Manager',
                'department': marketing,
                'location': 'Remote',
                'employment_type': 'full_time',
                'experience_level': 'senior',
                'description': 'Lead our product marketing efforts to drive growth and user acquisition. You will be responsible for positioning our language learning platform in the market and driving user engagement.',
                'requirements': '• 4+ years of product marketing experience\n• Experience in EdTech or SaaS products\n• Strong analytical and data-driven mindset\n• Excellent written and verbal communication skills\n• Experience with marketing automation tools\n• Knowledge of SEO and content marketing',
                'responsibilities': '• Develop go-to-market strategies for new features\n• Create marketing content and campaigns\n• Analyze user behavior and market trends\n• Collaborate with sales and product teams\n• Manage marketing campaigns and budgets\n• Track and report on marketing metrics',
                'benefits': 'Competitive salary, health insurance, remote work, marketing tools budget, conference budget',
                'salary_min': 50000,
                'salary_max': 65000,
                'application_email': 'jobs@linguify.com',
                'is_featured': False,
            },
            {
                'title': 'Business Development Manager',
                'department': sales,
                'location': 'Barcelona, Spain',
                'employment_type': 'full_time',
                'experience_level': 'mid',
                'description': 'Drive business growth by identifying and developing strategic partnerships and new business opportunities. You will work with educational institutions, corporate clients, and other potential partners.',
                'requirements': '• 3+ years of business development experience\n• Experience in EdTech or B2B sales\n• Strong negotiation and communication skills\n• Fluency in English and Spanish\n• Experience with CRM systems\n• Ability to travel occasionally',
                'responsibilities': '• Identify and pursue new business opportunities\n• Build relationships with potential partners\n• Negotiate contracts and agreements\n• Collaborate with product and marketing teams\n• Analyze market trends and competition\n• Represent Linguify at industry events',
                'benefits': 'Competitive salary, health insurance, travel budget, commission structure, professional development',
                'salary_min': 42000,
                'salary_max': 58000,
                'application_email': 'jobs@linguify.com',
                'is_featured': False,
            },
        ]

        created_count = 0
        for job_data in jobs_data:
            job, created = JobPosition.objects.get_or_create(
                title=job_data['title'],
                department=job_data['department'],
                defaults=job_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created job: {job.title}')
            else:
                self.stdout.write(f'Job already exists: {job.title}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} new job positions. '
                f'Total departments: {Department.objects.count()}, '
                f'Total positions: {JobPosition.objects.count()}'
            )
        )