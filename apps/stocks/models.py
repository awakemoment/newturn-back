from django.db import models


class Stock(models.Model):
    """
    종목 기본 정보
    """
    stock_code = models.CharField('종목 코드', max_length=20, unique=True, db_index=True)
    stock_name = models.CharField('종목명', max_length=200)
    stock_name_en = models.CharField('종목명(영문)', max_length=200, blank=True, null=True)
    
    # 국가/거래소
    country = models.CharField(
        '국가',
        max_length=10,
        choices=[('kr', '한국'), ('us', '미국')],
        default='kr'
    )
    exchange = models.CharField('거래소', max_length=50, blank=True, null=True)  # kospi, kosdaq, nasdaq, nyse
    
    # 기업 정보
    corp_code = models.CharField('기업 코드', max_length=50, blank=True, null=True)  # DART, EDGAR
    cik = models.CharField('CIK 번호', max_length=20, blank=True, null=True, db_index=True)  # EDGAR용
    industry = models.CharField('산업', max_length=200, blank=True, null=True)
    sector = models.CharField('섹터', max_length=200, blank=True, null=True)
    
    # 발행 주식 수
    shares_outstanding = models.BigIntegerField('발행 주식 수', null=True, blank=True)
    shares_outstanding_updated_at = models.DateField('주식수 업데이트일', null=True, blank=True)
    
    # 토스 정보 (크롤링)
    toss_code = models.CharField('토스 코드', max_length=50, blank=True, null=True)
    description = models.TextField('기업 설명', blank=True, null=True)
    
    # 메타데이터
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    is_active = models.BooleanField('활성화', default=True)
    
    class Meta:
        db_table = 'stocks'
        verbose_name = '종목'
        verbose_name_plural = '종목'
        indexes = [
            models.Index(fields=['stock_code']),
            models.Index(fields=['country', 'exchange']),
        ]
    
    def __str__(self):
        return f"{self.stock_name} ({self.stock_code})"


class StockFinancialRaw(models.Model):
    """
    재무 원본 데이터 (DART/EDGAR)
    """
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='financials_raw')
    
    # 공시 정보
    disclosure_year = models.IntegerField('공시 연도')
    disclosure_quarter = models.IntegerField('공시 분기')  # 1, 2, 3, 4
    disclosure_date = models.DateField('공시일')
    
    # 재무 데이터
    revenue = models.BigIntegerField('매출액', null=True, blank=True)
    operating_profit = models.BigIntegerField('영업이익', null=True, blank=True)
    net_income = models.BigIntegerField('순이익', null=True, blank=True)
    
    # ⭐ 핵심: 현금흐름
    ocf = models.BigIntegerField('영업활동 현금흐름 (OCF)', null=True, blank=True)
    icf = models.BigIntegerField('투자활동 현금흐름', null=True, blank=True)
    fcf = models.BigIntegerField('잉여현금흐름 (FCF)', null=True, blank=True)
    capex = models.BigIntegerField('설비투자 (CAPEX)', null=True, blank=True)
    
    # 재무상태
    total_assets = models.BigIntegerField('총자산', null=True, blank=True)
    current_assets = models.BigIntegerField('유동자산', null=True, blank=True)
    current_liabilities = models.BigIntegerField('유동부채', null=True, blank=True)
    total_liabilities = models.BigIntegerField('총부채', null=True, blank=True)
    total_equity = models.BigIntegerField('자본총계', null=True, blank=True)
    
    # 배당
    dividend = models.BigIntegerField('배당금', null=True, blank=True)
    
    # 메타데이터
    data_source = models.CharField('데이터 소스', max_length=50)  # DART, EDGAR, GPT4
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        db_table = 'stock_financial_raw'
        verbose_name = '재무 원본 데이터'
        verbose_name_plural = '재무 원본 데이터'
        unique_together = ['stock', 'disclosure_year', 'disclosure_quarter']
        indexes = [
            models.Index(fields=['stock', 'disclosure_date']),
        ]
    
    def __str__(self):
        return f"{self.stock.stock_name} {self.disclosure_year}Q{self.disclosure_quarter}"


class StockPrice(models.Model):
    """
    주가 데이터 (일별)
    """
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='prices')
    
    date = models.DateField('일자', db_index=True)
    open_price = models.DecimalField('시가', max_digits=15, decimal_places=2, null=True)
    high_price = models.DecimalField('고가', max_digits=15, decimal_places=2, null=True)
    low_price = models.DecimalField('저가', max_digits=15, decimal_places=2, null=True)
    close_price = models.DecimalField('종가', max_digits=15, decimal_places=2)
    volume = models.BigIntegerField('거래량', null=True)
    
    # 시가총액
    market_cap = models.BigIntegerField('시가총액', null=True, blank=True)
    shares_outstanding = models.BigIntegerField('발행주식수', null=True, blank=True)
    
    class Meta:
        db_table = 'stock_prices'
        verbose_name = '주가 데이터'
        verbose_name_plural = '주가 데이터'
        unique_together = ['stock', 'date']
        indexes = [
            models.Index(fields=['stock', 'date']),
        ]
    
    def __str__(self):
        return f"{self.stock.stock_name} {self.date} {self.close_price}원"

