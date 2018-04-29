from requests_html import HTMLSession
import sqlite3


def crawl_jobs():
    API_URL = ('https://api.github.com/repos/awesome-jobs/vietnam/'
               'issues?per_page=200?page={}')
    page = 1
    lst_jobs = []
    session = HTMLSession()
    get_title_xpath = '//span[@class="js-issue-title"]'
    while True:
        r = session.get(API_URL)
        data = r.json()
        if not data:
            break
        lst_job_urls = list(map(lambda x: x['html_url'], data))
        for job_url in lst_job_urls:
            r1 = session.get(job_url)
            id_ = job_url[job_url.rfind('/') + 1:]
            title = r1.html.xpath(get_title_xpath)[0].full_text
            description = r1.html.xpath('//tr//td')[0].html
            lst_jobs.append((id_, title, description))
        page += 1
    return lst_jobs


def add_job(lst_jobs):
    with sqlite3.connect('jobs.db') as conn:
        c = conn.cursor()
        c.execute('drop table if exists jobs')
        c.execute('CREATE TABLE jobs (id, title, description);')
        for job in lst_jobs:
            c.execute('INSERT INTO jobs VALUES (?,?,?)', job)
        conn.commit()


if __name__ == '__main__':
    add_job(crawl_jobs())
