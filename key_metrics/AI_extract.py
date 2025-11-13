import os
import nltk
import re
import PyPDF2
import openpyxl
from nltk.corpus import stopwords

# 第一次运行时需要下载 nltk 的停用词库
nltk.download('punkt')  # 下载 punkt 资源，用于分词
nltk.download('stopwords')  # 下载停用词

# 从 PDF 中提取文本
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        if reader.is_encrypted:
            try:
                reader.decrypt("")  # 尝试解密（如果有密码可以在此处输入，否则尝试空密码）
            except Exception as e:
                print(f"Failed to decrypt {pdf_path}: {e}. Skipping...")
                return "ERROR"
        try:
            for page in reader.pages:
                if page.extract_text() is not None:  # 确保提取文本不为空
                    text += page.extract_text()
        except PyPDF2.errors.FileNotDecryptedError:
            print(f"File has not been decrypted properly: {pdf_path}. Skipping...")
            return "ERROR"
    return text

# 预处理文本
def preprocess_text(text):
    # 将文本转换为小写
    text = text.lower()
    # 分割文本为单词列表（替代 word_tokenize，避免 punkt 相关错误）
    words = re.findall(r'\b\w+\b', text)  # 使用正则表达式分割文本为单词
    # 去除停用词和标点符号
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word not in stop_words]
    return filtered_words

# 计算关键词频率
def calculate_keyword_frequency(words, keywords):
    # 统计每个关键词的出现次数
    keyword_count = {keyword: 0 for keyword in keywords}
    for i in range(len(words) - 1):
        word_pair = f"{words[i]} {words[i + 1]}"
        if words[i] in keyword_count:
            keyword_count[words[i]] += 1
        if word_pair in keyword_count:
            keyword_count[word_pair] += 1

    # 计算总词数
    total_words = len(words)

    # 计算频率并保留六位小数
    frequency = sum(keyword_count.values()) / total_words * 100 if total_words > 0 else 0
    frequency = round(frequency, 6)

    return keyword_count, total_words, frequency

# 将结果保存到 Excel 表格
def save_to_excel(file_path, data):
    # 如果文件不存在，创建新的工作簿
    if not os.path.exists(file_path):
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "AI Frequency Analysis"
        # 写入表头
        headers = [
            "company", "year", "artificial intelligence_occurrences", "machine learning_occurrences",
            "deep learning_occurrences", "neural network_occurrences", "ai_occurrences", "big data_occurrences",
            "data-driven_occurrences", "data driven_occurrences", "data analytics_occurrences", "data analysis_occurrences",
            "business analytics_occurrences", "intelligent automation_occurrences", "computer vision_occurrences",
            "natural language processing_occurrences", "predictive analytics_occurrences", "predictive analysis_occurrences",
            "robotics_occurrences", "reinforcement learning_occurrences", "cognitive computing_occurrences",
            "cognitive automation_occurrences", "Total words", "ai_frequency"
        ]
        sheet.append(headers)
        workbook.save(file_path)

    # 打开已有的工作簿并追加数据
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook["AI Frequency Analysis"]
    sheet.append(data)
    workbook.save(file_path)

# 主函数：遍历文件夹中的所有 PDF 文件并计算关键词频率
def analyze_reports_in_folder(folder_path, keywords, output_excel):
    for company_name in os.listdir(folder_path):
        company_path = os.path.join(folder_path, company_name)
        if os.path.isdir(company_path):
            for file_name in os.listdir(company_path):
                if file_name.endswith(".pdf"):
                    year = file_name.split('.')[0]  # 假设文件名是年份.pdf 的格式
                    pdf_path = os.path.join(company_path, file_name)
                    # 提取文本
                    text = extract_text_from_pdf(pdf_path)
                    if text == "ERROR":
                        print(f"Failed to process {pdf_path}. Adding to Excel with error status.")
                        data = [
                            company_name, year, "ERROR", "ERROR", "ERROR", "ERROR", "ERROR", "ERROR", "ERROR", "ERROR", "ERROR", "ERROR", "ERROR", "ERROR", "ERROR", "ERROR", "ERROR", "ERROR", "ERROR", "ERROR", "ERROR", "ERROR", "ERROR", "ERROR"
                        ]
                        save_to_excel(output_excel, data)
                        continue
                    if not text:
                        print(f"No text extracted from {pdf_path}. Skipping...")
                        continue
                    # 预处理文本
                    words = preprocess_text(text)
                    # 计算关键词频率
                    keyword_count, total_words, frequency = calculate_keyword_frequency(words, keywords)
                    # 打印结果
                    print(f"AI Frequency in '{pdf_path}': {frequency:.6f}%")
                    print(f"Total words: {total_words}")
                    print("Keyword occurrences:")
                    for keyword, count in keyword_count.items():
                        if count > 0:  # 打印出现次数大于 0 的关键词
                            print(f"  '{keyword}': {count} times")
                    # 保存结果到 Excel
                    data = [
                        company_name, year, keyword_count["artificial intelligence"], keyword_count["machine learning"],
                        keyword_count["deep learning"], keyword_count["neural network"], keyword_count["ai"],
                        keyword_count["big data"], keyword_count["data-driven"], keyword_count["data driven"],
                        keyword_count["data analytics"], keyword_count["data analysis"], keyword_count["business analytics"],
                        keyword_count["intelligent automation"], keyword_count["computer vision"],
                        keyword_count["natural language processing"], keyword_count["predictive analytics"],
                        keyword_count["predictive analysis"], keyword_count["robotics"], keyword_count["reinforcement learning"],
                        keyword_count["cognitive computing"], keyword_count["cognitive automation"], total_words, frequency
                    ]
                    save_to_excel(output_excel, data)

# 定义 AI 关键词列表
ai_keywords = [
    "artificial intelligence", "machine learning", "deep learning", 
    "neural network", "ai", "big data", "data-driven", "data driven",
    "data analytics", "data analysis", "business analytics", "business analysis", "intelligent automation", "computer vision",
    "natural language processing", "predictive analytics", "predictive analysis", "robotics",
    "reinforcement learning", "cognitive computing", "cognitive automation"
]

# 设置需要分析的文件夹路径和输出的 Excel 文件路径
folder_path = r"G:\fy\上市公司年报数据"
output_excel_path = r"G:\fy\AI_Frequency_Analysis.xlsx"

# 运行分析
analyze_reports_in_folder(folder_path, ai_keywords, output_excel_path)
