from bs4 import BeautifulSoup
import requests
import re


def get_og_image_meta_contents(url):
    # 获取网页内容
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 查找所有 meta 标签，其中 name 属性为 og:image
    metas = soup.find_all('meta', attrs={'name': 'og:image'})

    # 获取所有 content 属性并去重
    contents = {meta.get('content') for meta in metas if meta.get('content')}  # 使用集合去重

    return list(contents)

# 示例 URL
# url = 'https://example.com'
# print(get_og_image_meta_contents(url))


def extract_url(text):
    regex = r'https?://[^\s，,]+'  # 匹配 http:// 或 https:// 开头，且逗号（中文、英文）为分隔符的 URL
    urls = re.findall(regex, text)
    return urls

text = '15 裴秀智发布了一篇小红书笔记，快来看吧！ 😆 H3HX98ROIiKiNRt 😆 http://xhslink.com/a/O5ZY8gvX2dE0，复制本条信息，打开【小红书】App查看精彩内容！'
url = extract_url(text[0])
print(get_og_image_meta_contents(url))