import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_job_df(job):
    #사람인 데이터
    saramIn = "https://www.saramin.co.kr/zf_user/search/recruit"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    }
    ppp = []

    for i in range(1,100):
        params = {
            "searchType": "search",
            "searchword": job,
            "recruitPage": i,
            "recruitPageCount": 100
        }
        res = requests.get(saramIn, params=params, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        infos = soup.select(".item_recruit")

        if not infos:
            print(f"페이지 {i} 없음  종료")
            break

        for info in infos:
            title = info.select_one(".job_tit a")["title"]
            link = info.select_one(".job_tit a")["href"]

            company = info.select_one(".corp_name a").get_text(strip=True)
            due = info.select_one(".job_date").get_text(strip=True)

            cond_spans = info.select(".job_condition span")
            loc = cond_spans[0].get_text(strip=True)
            requirements = " ".join(
                span.get_text(strip=True) for span in cond_spans[1:]
            )

            ppp.append([title, company, due, link, loc, requirements])

    df1 = pd.DataFrame(
        ppp,
        columns=["title", "company", "due", "link", "loc", "requirements"]
    )

    #잡코리아 데이터

    jobKorea_url = "https://www.jobkorea.co.kr/Search/"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    ppp = []
    for i in range(1,1000):
        params = {
        "stext": job,
        "FeatureCode": "WRK",
        "Page_No": i
        }
        res = requests.get(jobKorea_url, params=params, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        infos = soup.select(".Box_bgColor_white__1wwr54u0.Box_borderColor_default__1wwr54u5.Box_borderSize_1__1wwr54ud.styles_p_space0__dk46ts61.styles_radius_radius16__dk46ts9d.Shadow_root_list__bm2zcc6.dlua7o0")

        if not infos:
            print(f"페이지 {i} 없음  종료")
            break

        for info in infos:
            title = info.select_one("a.Flex_display_flex__i0l0hl2.Flex_gap_space6__i0l0hl1g").text
            link = info.select_one("a.Flex_display_flex__i0l0hl2.Flex_gap_space6__i0l0hl1g")["href"]

            company = info.select_one("a.Flex_display_inline-flex__i0l0hl1").get_text(strip=True)
            due = info.select(".Flex_display_flex__i0l0hl2.Flex_gap_space2__i0l0hl1j.styles_flex-shrink_0__dk46tsa9 span")[2].get_text(strip=True)

            requirements = info.select_one("span.Typography_variant_size13__344nw28.Typography_weight_regular__344nw2e.Typography_color_gray700__344nw2o.styles_flex-shrink_0__dk46tsa9").get_text(strip=True)

            loc = info.select('span.Typography_variant_size14__344nw27.Typography_weight_regular__344nw2e.Typography_color_gray900__344nw2m.Typography_truncate__344nw2y')[0]
            loc = loc.get_text(strip=True)


            ppp.append([title, company, due, link, loc, requirements])

    df2 = pd.DataFrame(
        ppp,
        columns=["title", "company", "due", "link", "loc", "requirements"]
    )


    #병합

    df =pd.concat((df1,df2), axis=0)

    tmp = df.copy()
    tmp['날짜만'] = tmp['due'].str.extract(r'([0-9]+/[0-9]+)')
    tmp = tmp.drop(columns='due')

    tmp['title'] = tmp['title'].str.strip()
    tmp['company'] = tmp['company'].str.strip()
    tmp['link'] = tmp['link'].str.strip()
    tmp['loc'] = tmp['loc'].str.strip()
    tmp['requirements'] = tmp['requirements'].str.strip()
    tmp['날짜만'] = tmp['날짜만'].str.strip()


    tmp.rename(columns={'title':'모집 제목', "company":'회사', 'loc':'위치', 'requirements':'필요 조건', '날짜만':'마감일'},inplace=True)
    tmp = tmp.drop_duplicates(subset=['모집 제목', '마감일'],keep="first")

    new_job = tmp[tmp['필요 조건'].str.contains('신입|경력 무관|경력 무관')]
    return tmp, new_job


from fastapi import FastAPI, Path, Query
from fastapi.responses import StreamingResponse
import io
import zipfile
import urllib.parse

app = FastAPI(title="채용 크롤링 CSV API")

@app.get("/jobs/{job}")
def download_csv_zip(
    job: str = Path(..., description="직종명")
):
    df_all, df_fresher = get_job_df(job)

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        # 전체 채용공고
        all_buffer = io.StringIO()
        df_all.to_csv(all_buffer, index=False, encoding="utf-8-sig")
        zipf.writestr(
            f"{job}_전체_채용공고.csv",
            all_buffer.getvalue().encode('utf-8-sig')
        )

        # 신입 채용공고
        fresher_buffer = io.StringIO()
        df_fresher.to_csv(fresher_buffer, index=False, encoding="utf-8-sig")
        zipf.writestr(
            f"{job}_신입_채용공고.csv",
            fresher_buffer.getvalue().encode('utf-8-sig')
        )

    zip_buffer.seek(0)
    filename = f"{job}_채용공고.zip"
    encoded_filename = urllib.parse.quote(filename)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )
