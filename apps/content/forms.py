from django import forms

from .models import CuratedContent


class CuratedContentAdminForm(forms.ModelForm):
    """커스텀 Admin 폼

    - JSONField(`tags`)를 쉼표/엔터 구분 문자열로 입력할 수 있게 변환
    - 큐레이터 노트를 기본 4줄 텍스트 영역으로 제공
    """

    tags_text = forms.CharField(
        label='태그 (쉼표 또는 줄바꿈으로 구분)',
        required=False,
        help_text='예: AI, NVDA, 반도체, 초급'
    )

    class Meta:
        model = CuratedContent
        fields = '__all__'
        widgets = {
            'curator_note': forms.Textarea(attrs={'rows': 6}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'tags' in self.fields:
            self.fields['tags'].required = False
            self.fields['tags'].widget = forms.HiddenInput()
        current_tags = self.instance.tags if self.instance and self.instance.tags else []
        if isinstance(current_tags, list):
            # 기본: 콤마 + 공백 포맷으로 노출
            self.fields['tags_text'].initial = ', '.join(current_tags)
        elif isinstance(current_tags, str):
            self.fields['tags_text'].initial = current_tags

    def clean_tags_text(self):
        value = self.cleaned_data.get('tags_text', '')
        if not value:
            return []

        # 줄바꿈/쉼표를 모두 구분자로 처리
        separators = [',', '\n']
        normalized = value
        for separator in separators:
            normalized = normalized.replace(separator, ' ')

        tags = [token.strip() for token in normalized.split(' ') if token.strip()]
        return tags

    def save(self, commit=True):
        tags = self.cleaned_data.get('tags_text', [])
        if not isinstance(tags, list):
            tags = []

        # ModelForm.save()에서 JSONField에 변환한 값 적용
        self.instance.tags = tags
        return super().save(commit=commit)


