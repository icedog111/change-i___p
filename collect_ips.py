import requests
from bs4 import BeautifulSoup
import re
import os
from urllib.parse import urlparse

def fetch_page_content(url):
    """获取网页内容，返回 BeautifulSoup 对象"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 检查请求是否成功
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f'请求失败: {url}, 错误: {e}')
        return None

def extract_ips(soup, url):
    """从网页内容中提取符合要求的 IP 地址，并格式化为 ip#域名-计数"""
    ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    
    if not soup:
        return []
    
    valid_ips = []
    if url == 'https://cf.090227.xyz':
        rows = soup.find_all('tr')
        for row in rows:
            columns = row.find_all('td')
            if len(columns) >= 5:
                ip_address = columns[1].get_text(strip=True)  # 第二列是IP
                speed_text = columns[4].get_text(strip=True)  # 第五列是速度
                speed_match = re.search(r'\d+\.?\d*', speed_text)  # 提取数值部分
                if speed_match:
                    try:
                        speed = float(speed_match.group())
                        if speed > 0 and re.match(ip_pattern, ip_address):
                            valid_ips.append(ip_address)
                    except ValueError:
                        continue
    elif url == 'https://ip.164746.xyz/ipTop10.html':
        valid_ips = re.findall(ip_pattern, soup.text)  # 直接从网页文本中提取 IP 地址
    
    # 格式化 IP 地址为 ip#域名-计数
    formatted_ips = []
    domain = urlparse(url).netloc  # 提取域名部分
    for index, ip in enumerate(valid_ips[:10], start=1):  # 最多提取 10 个 IP
        formatted_ip = f"{ip}#{domain}-{str(index).zfill(2)}"
        formatted_ips.append(formatted_ip)
    
    print(f"从 {url} 提取到 {len(formatted_ips)} 个 IP 地址")  # 调试信息
    return formatted_ips

def save_ips(ip_list, filename='ip.txt'):
    """将 IP 地址列表保存到文件"""
    try:
        with open(filename, 'w') as file:
            file.write('\n'.join(ip_list))
        print(f'IP 地址已保存到 {filename} 文件中。')
    except IOError as e:
        print(f'保存文件失败: {e}')

if __name__ == "__main__":
    urls = [
        'https://ip.164746.xyz/ipTop10.html',
        'https://cf.090227.xyz'
    ]
    
    output_file = 'ip.txt'
    if os.path.exists(output_file):
        os.remove(output_file)
    
    all_ips = []
    for url in urls:
        print(f"正在处理 URL: {url}")
        soup = fetch_page_content(url)
        if soup:
            ips = extract_ips(soup, url)
            all_ips.extend(ips)
    
    save_ips(all_ips, output_file)

    # 适配 GitHub Actions 运行环境
    if os.getenv("GITHUB_ACTIONS"):
        print("在 GitHub Actions 运行环境中执行")
        # 如果需要，可以将文件路径设置为 GitHub Actions 的工作目录
        output_path = os.path.join(os.getenv("GITHUB_WORKSPACE"), output_file)
        save_ips(all_ips, output_path)
