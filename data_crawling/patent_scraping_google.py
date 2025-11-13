import os
import csv
import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path

# 从Excel文件中加载专利号
def load_patent_numbers(file_path):
    df = pd.read_excel(file_path)
    return df['Patent Number'].tolist()

# 创建输出目录
def create_output_directory(directory_name):
    Path(directory_name).mkdir(parents=True, exist_ok=True)
    if os.path.exists(directory_name):
        print(f"Directory {directory_name} is ready for saving data.")
    else:
        print(f"Failed to create directory {directory_name}.")

# 爬取单个专利的数据
async def scrape_patent_data(patent_number):
    browser = None
    try:
        # 启动浏览器
        browser = await launch(executablePath='C:/Program Files/Google/Chrome/Application/chrome.exe', headless=True, args=['--no-sandbox'])
        page = await browser.newPage()

        base_url = f"https://patents.google.com/patent/{patent_number}/en"
        print(f"Fetching URL: {base_url}")

        # 设置页面加载超时为 20 秒，减少等待时间
        await page.goto(base_url, {'waitUntil': 'domcontentloaded', 'timeout': 20000})

        # 强制等待时间缩短为 3 秒
        await asyncio.sleep(3)

        # 获取页面 HTML 内容
        page_html = await page.content()
        soup = BeautifulSoup(page_html, 'html.parser')

        # 检查页面内容是否已加载
        if not soup.find('meta', {'name': 'DC.title'}):
            print(f"Failed to load data for patent: {patent_number}")
            await browser.close()
            return [patent_number, 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A']

        # 提取专利名称
        patent_name = soup.find('meta', {'name': 'DC.title'}).get('content') if soup.find('meta', {'name': 'DC.title'}) else 'N/A'

        # 提取发明人和受让人信息
        inventors = []
        assignees = []
        elements = soup.find_all('dl')

        current_label = None
        for dl in elements:
            for dt in dl.find_all('dt'):
                current_label = dt.text.strip()
                if 'Inventor' in current_label:
                    for dd in dt.find_next_siblings('dd'):
                        inventors.append(dd.text.strip())
                elif 'Current Assignee' in current_label:
                    for dd in dt.find_next_siblings('dd'):
                        assignees.append(dd.text.strip())

        inventors = '; '.join(inventors) if inventors else 'N/A'
        assignees = '; '.join(assignees) if assignees else 'N/A'

        # 提取分类信息
        classifications = []
        for state_modifier in soup.find_all('state-modifier', {'class': 'code'}):
            cpc_code = state_modifier['data-cpc'] if state_modifier.has_attr('data-cpc') else None
            description = state_modifier.find_next('span', {'class': 'description'}).text.strip() if state_modifier.find_next('span', {'class': 'description'}) else None

            if cpc_code and description:
                classifications.append(f"{cpc_code} - {description}")

        classifications_output = '; '.join(classifications) if classifications else 'N/A'

        # 提取专利引用和被引用次数
        patent_citations = 'N/A'
        cited_by = 'N/A'
        citation_element = soup.find('a', {'href': '#patentCitations'})
        if citation_element:
            citation_text = citation_element.text.strip()
            if "Patent citations" in citation_text:
                patent_citations = citation_text.split("Patent citations")[-1].strip().strip('()')

        cited_by_element = soup.find('a', {'href': '#citedBy'})
        if cited_by_element:
            cited_by_text = cited_by_element.text.strip()
            if "Cited by" in cited_by_text:
                cited_by = cited_by_text.split("Cited by")[-1].strip().strip('()')

        # 返回专利数据
        return [patent_number, patent_name, inventors, assignees, classifications_output, patent_citations, cited_by]
    
    except Exception as e:
        print(f"Error occurred while fetching {patent_number}: {e}")
        return [patent_number, 'Error', 'Error', 'Error', 'Error', 'Error', 'Error']

    finally:
        if browser:
            await browser.close()

# 保存数据到CSV文件（逐条保存）
def save_to_csv(data, output_dir, batch_number):
    output_file = os.path.join(output_dir, f'patent_data_batch_{batch_number}.csv')
    try:
        with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            if os.path.getsize(output_file) == 0:  # 如果文件为空，则写入表头
                writer.writerow(['Patent Number', 'Name', 'Inventor', 'Current Assignee', 'Classifications', 'Patent citations', 'Cited By'])
            writer.writerow(data)  # 每次爬取完一条数据就保存
        print(f"Saved data for patent {data[0]}")
    except Exception as e:
        print(f"Failed to save data for patent {data[0]}: {e}")

# 爬取所有专利数据
async def run_scraper(patent_file, output_directory, batch_size=500):
    try:
        patent_numbers = load_patent_numbers(patent_file)
        create_output_directory(output_directory)

        for idx, patent_number in enumerate(patent_numbers):
            result = await scrape_patent_data(patent_number)
            save_to_csv(result, output_directory, (idx // batch_size) + 1)

    except Exception as e:
        print(f"An error occurred during scraping: {e}")

if __name__ == "__main__":
    # Excel文件路径
    patent_file = "required_data.xlsx"
    # 输出文件夹
    output_directory = "patent_data_output"

    # 开始爬取数据并保存
    asyncio.run(run_scraper(patent_file, output_directory))

