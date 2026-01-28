
import requests
from bs4 import BeautifulSoup
import pandas as pd
url = "https://www.jobkorea.co.kr/Search/"
headers = {
    "User-Agent": "Mozilla/5.0"
}

#데이터 형식 [title, company, due, link, loc, requirements] 이렇게


ppp = []
for i in range(1,400):
    params = {
    "stext": "개발자",
    "FeatureCode": "WRK",
    "Page_No": i
    }
    res = requests.get(url, params=params, headers=headers)
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

df = pd.DataFrame(
    ppp,
    columns=["title", "company", "due", "link", "loc", "requirements"]
)
df.to_csv("(잡코리아) 개발자 채용 데이터.csv", index=False,encoding='utf-8-sig')
