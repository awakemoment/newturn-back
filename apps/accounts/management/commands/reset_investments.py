"""
투자 현황 초기화 관리 명령어

사용법:
    python manage.py reset_investments
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import SavingsReward


class Command(BaseCommand):
    help = '모든 투자 데이터(SavingsReward)를 삭제합니다.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='확인 없이 바로 삭제',
        )

    def handle(self, *args, **options):
        count = SavingsReward.objects.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('삭제할 투자 데이터가 없습니다.')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f'삭제할 투자 데이터: {count}개')
        )
        
        if not options['confirm']:
            confirm = input('정말 모든 투자 데이터를 삭제하시겠습니까? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write(
                    self.style.ERROR('삭제가 취소되었습니다.')
                )
                return
        
        SavingsReward.objects.all().delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ {count}개의 투자 데이터가 삭제되었습니다.')
        )

