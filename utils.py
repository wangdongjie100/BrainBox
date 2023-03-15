import openai 
from pdf_parser import Paper
import datetime
import os
import re



def chat_summary(api_key, key_word, text):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a researcher in the [" + key_word + "] field, proficient in using concise language to summarize research papers."},
            # ChatGPT role
            {"role": "assistant",
             "content": "This is the title, Abstract, and Introduction of an English literature. I need your help to read it and summarize the following questions: " + text},
            # Background knowledge
            {"role": "user", "content": """
                     1. Mark the title of the literature.
                     2. Mark the keywords of the article.
                     3. Summarize the following four points:
                        - (1): What is the research background of this article?
                        - (2): What are the previous methods? What problems do they have? What is the essential difference between this article and past research?
                        - (3): What is the research method proposed in this article?
                        - (4): What task did the method proposed in this article achieve? What performance was obtained? Does the performance support their goals?
                     Output the corresponding contents in the following format:
                     1. Title: xxx\n\n                
                     2. Keywords: xxx\n\n      
                     3. Summary: xxx\n\n   
                     Use concise and academic language, avoid too much repetitive information, use the original numerical values, 
                     strictly follow the format, and output the corresponding contents to xxx, using \n for line breaks. 
                     When summarizing the paper, please organize all answer into one paragraph instead of listing them separately.
                """},
        ]
    )
    result = ''
    for choice in response.choices:
        result += choice.message.content
    # print("summary_result:\n", result)
    return result

def chat_method(api_key, key_word, text):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a researcher in the [" + key_word + "] field, proficient in using concise language to summarize research papers."},
            # ChatGPT role
            {"role": "assistant",
             "content": "This is the <summary> and <Method> sections of an English literature. You have already summarized the <summary> section, but for the <Method> section, I need your help to read it and summarize the following questions: " + text},
            # Background knowledge
            {"role": "user", "content": """
                         7. Describe the methodology used in this article in detail. For example, its steps are:
                            - (1):...
                            - (2):...
                            - (3):...
                            - .......
                         Output the corresponding contents in the following format:
                         7. The detailed methods can be summarized as follows: \n\n
                            - (1):xxx;\n 
                            - (2):xxx;\n 
                            - (3):xxx;\n  
                            .......\n\n     
                         Use concise and academic language, avoid repeating the content in the previous <summary> section, strictly follow the format, and use \n for line breaks. The "......." represents filling in according to actual needs; if there is none, you do not need to write it.
                    """},
        ]
    )
    result = ''
    for choice in response.choices:
        result += choice.message.content
    # print("method_result:\n", result)
    return result

def chat_conclusion(api_key, key_word, text):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        # prompt需要用英语替换，少占用token。
        messages=[
            {"role": "system",
             "content": "You are a reviewer in the [" + key_word + "] field, and you need to rigorously review this article."},
            # ChatGPT role
            {"role": "assistant",
             "content": "This is the <summary> and <conclusion> sections of an English literature. You have already summarized the <summary> section, but for the <conclusion> section, I need your help to summarize the following questions: " + text},
            # Background knowledge, can refer to the review process of OpenReview
            {"role": "user", "content": """
                         8. Make the following conclusions:
                            - (1): What is the significance of this work?
                            - (2): What are advantages of this article from the three dimensions of innovation, performance, and workload?
                            - (3): What are disadvantages of this article from the three dimensions of innovation, performance, and workload?
                            - (4): If the score range is from 0~10, can you provide a score for this paper and illustrate your justification?
                            - (5): Can you provide several detailed suggestions to improve this paper?
                            .......
                         Output the corresponding contents in the following format:
                         8. Conclusion: \n\n
                            - (1):xxx;\n                     
                            - (2): Strengths: \n 
                                -a. xxx;\n
                                -b. xxx;\n
                                -c. xxx;\n
                                ......
                            - (3): Weaknesses:\n
                                -a. xxx;\n
                                -b. xxx;\n
                                -c. xxx;\n
                                ......
                            - (4): Score: xxx;\n
                                -Justifications: xxx;\n
                            - (5): Detailed Feedback:\n
                                - a. xxx;\n
                                - b. xxx;\n
                                - c. xxx;\n
                                ......                      
                         Use concise and academic language, avoid repeating the content in the previous <summary> section, use the original numerical values, strictly follow the format, and use \n for line breaks. 
                         The "......." represents filling in according to actual needs; 
                         I want to point out really important weaknesses to reject this paper, so try your best to find them.
                          When you score this paper, please as rigorous as possible. if there is none, you do not need to write.
                    """},
        ]
    )
    result = ''
    for choice in response.choices:
        result += choice.message.content
    # print("conclusion_result:\n", result)
    return result

def validateTitle(title):
    # 将论文的乱七八糟的路径格式修正
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title

def export_to_markdown(text, file_name, mode='w'):
    # 使用markdown模块的convert方法，将文本转换为html格式
    # html = markdown.markdown(text)
    # 打开一个文件，以写入模式
    with open(file_name, mode, encoding="utf-8") as f:
        # 将html格式的内容写入文件
        f.write(text)

def review_by_chatgpt(paper_list, api_key, key_word, export_path, file_format, file_names):
    htmls = []
    for paper_index, paper in enumerate(paper_list):
        # 第一步先用title，abs，和introduction进行总结。
        text = ''
        text += 'Title:' + paper.title
        # # text += 'Url:' + paper.url
        # text += 'Abstrat:' + paper.abs
        # intro
        text += list(paper.section_text_dict.values())[0]
        max_token = 2500 * 4
        text = text[:max_token]
        chat_summary_text = chat_summary(api_key=api_key, text=text,key_word=key_word)
        htmls.append('## Paper:' + str(paper_index + 1))
        htmls.append('\n\n\n')
        htmls.append(chat_summary_text)

        # 第二步总结方法：
        # TODO，由于有些文章的方法章节名是算法名，所以简单的通过关键词来筛选，很难获取，后面需要用其他的方案去优化。
        method_key = ''
        for parse_key in paper.section_text_dict.keys():
            if 'method' in parse_key.lower() or 'approach' in parse_key.lower() or 'semantic memory model' in parse_key.lower():
                method_key = parse_key
                break

        if method_key != '':
            text = ''
            method_text = ''
            summary_text = ''
            summary_text += "<summary>" + chat_summary_text
            # methods
            method_text += paper.section_text_dict[method_key]
            # TODO 把这个变成tenacity的自动判别！
            max_token = 2500 * 4
            text = summary_text + "\n\n<Methods>:\n\n" + method_text
            text = text[:max_token]
            chat_method_text = chat_method(api_key=api_key, text=text,key_word=key_word)
            htmls.append(chat_method_text)
        else:
            chat_method_text = ''
        htmls.append("\n" * 4)

        # 第三步总结全文，并打分：
        conclusion_key = ''
        for parse_key in paper.section_text_dict.keys():
            if 'conclu' in parse_key.lower():
                conclusion_key = parse_key
                break

        text = ''
        conclusion_text = ''
        summary_text = ''
        summary_text += "<summary>" + chat_summary_text + "\n <Method summary>:\n" + chat_method_text
        if conclusion_key != '':
            # conclusion
            conclusion_text += paper.section_text_dict[conclusion_key]
            max_token = 2500 * 4
            text = summary_text + "\n\n<Conclusion>:\n\n" + conclusion_text
        else:
            text = summary_text
        text = text[:max_token]
        chat_conclusion_text = chat_conclusion(api_key=api_key, text=text,key_word=key_word)
        htmls.append(chat_conclusion_text)
        htmls.append("\n" * 4)

        # # 整合成一个文件，打包保存下来。
        date_str = str(datetime.datetime.now())[:13].replace(' ', '-')
        try:
            os.makedirs(export_path)
        except:
            pass
        mode = 'w' if paper_index == 0 else 'a'
        file_name = os.path.join(export_path,
                                 date_str + '-' + file_names[paper_index][:25] + "." + file_format)
        export_to_markdown("\n".join(htmls), file_name=file_name, mode=mode)
        htmls.clear()