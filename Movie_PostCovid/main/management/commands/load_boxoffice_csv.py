import re
import pandas as pd
from django.core.management.base import BaseCommand
from main.models import Movie, BoxOfficeMonthly
from datetime import datetime

def to_int(x):
    if pd.isna(x): return 0
    s = str(x).strip()
    s = s.replace(",", "")
    if s == "": return 0
    try:
        return int(float(s))
    except Exception:
        return 0

def to_date(x):
    if pd.isna(x): return None
    s = str(x).strip()[:10]
    for fmt in ("%Y-%m-%d", "%Y.%m.%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            pass
    return None

class Command(BaseCommand):
    help = "Load monthly boxoffice data from a sheet-like CSV with repeated blocks (e.g., '2019/01' header + table)."

    def add_arguments(self, parser):
        parser.add_argument("--url", type=str, required=True,
                            help="CSV path (e.g., boxoffice.csv or data/boxoffice.csv) or Google Sheets CSV URL")

    def handle(self, *args, **opts):
        url = opts["url"]

        try:
            # 헤더가 일정하지 않으므로 header=None 로 읽음
            df = pd.read_csv(url, header=None, dtype=str)
            self.stdout.write(self.style.SUCCESS(f"Loaded CSV: {url}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to load CSV: {e}"))
            return

        # 열 인덱스 의미(스샷 기준)
        # 0: 순위, 1: 영화명, 2: 개봉, 3: 매출액, 4: 매출액점유율, 5: 누적매출액,
        # 6: 관객수, 7: 누적관객수, 8: 스크린수, 9: 상영횟수
        # 블록 시작 전에는 A열에 '2019/01' 같은 텍스트가 옴
        ym = None
        inserted = 0
        skipped = 0

        for i in range(len(df)):
            row = df.iloc[i].tolist()

            # 연/월 타이틀 감지 (예: "2019/01")
            head = str(row[0]).strip() if len(row) > 0 else ""
            m = re.match(r"^\s*(20\d{2})\s*[/\-\.]\s*(\d{1,2})\s*$", head)
            if m:
                ym = (int(m.group(1)), int(m.group(2)))
                continue

            # 헤더 줄 감지 (두 번째 컬럼이 '영화명' 이면 표 시작)
            if len(row) > 1 and str(row[1]).strip() == "영화명":
                # 다음 줄부터 실제 데이터
                continue

            # 합계 줄/빈 줄 스킵
            if any(str(x).strip() == "합계" for x in row):
                continue
            if all(pd.isna(x) or str(x).strip() == "" for x in row):
                continue

            # ym(연/월)을 아직 못 찾았으면 스킵
            if ym is None:
                continue

            # 실제 데이터 행 파싱
            try:
                rank = to_int(row[0])
                title = str(row[1]).strip()
                release_date = to_date(row[2])
                sales = to_int(row[3])
                audience = to_int(row[6])
                screens = to_int(row[8])
                show_count = to_int(row[9])

                if title == "" or rank == 0:
                    skipped += 1
                    continue

                movie, _ = Movie.objects.get_or_create(
                    title=title,
                    release_date=release_date
                )

                # 순위를 유니크키 일부로 사용 (월 Top10 구조)
                obj, _created = BoxOfficeMonthly.objects.update_or_create(
                    movie=movie,
                    year=ym[0],
                    month=ym[1],
                    rank=rank,
                    defaults=dict(
                        sales=sales,
                        audience=audience,
                        screens=screens,
                        show_count=show_count,
                    )
                )
                inserted += 1
            except Exception as e:
                skipped += 1
                self.stdout.write(self.style.WARNING(f"skip row {i}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"✅ inserted/updated: {inserted}, skipped: {skipped}"))
