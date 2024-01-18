import re
from flask import Flask, request, jsonify
from requests_html import HTMLSession
from fake_useragent import UserAgent


class Scraper:
    def __init__(self):
        self.session = HTMLSession()
        self.base_url = "https://91md.me"
    
    def getmenu(self):
        response=self.session.get(self.base_url,headers=self.generate_headers())
        menus=response.html.find('a.nav-link')
        menu=[]
        for m in menus:
           link = m.attrs['href']
           name = m.text
           full_link=self.base_url+link
           if full_link=='https://91md.me/':
               continue
           menu.append({
               'link':full_link,
               'name':name
           })
        return menu
        
    def generate_headers(self):
        ua = UserAgent()
        headers = {
            "User-Agent": ua.random,
        }
        return headers
    def getm3u8(self, url):
        response = self.session.get(url, headers=self.generate_headers())
        html_content = response.text

        # Locate the script containing player information
        script_start = html_content.find('var player_aaaa=')
        script_end = html_content.find('</script>', script_start)

        if script_start != -1 and script_end != -1:
            # Extract the script content
            script_content = html_content[script_start:script_end]

            # Use regular expression to extract m3u8 link from the script
            match = re.search(r'"url"\s*:\s*"(.*?)"', script_content)

            if match:
                m3u8 = match.group(1).replace('\\/', '/')
                return m3u8

        return None           
    def scrape_website(self, url):
        try:
            response = self.session.get(url, headers=self.generate_headers())
            response.raise_for_status()  # 检查请求是否成功
        except Exception as e:
            print(f"发生错误: {e}")
            return []

        result_data = []
        data_blocks = response.html.find('p.img')
        for block in data_blocks:
            img_src = block.find('img.lazy', first=True).attrs['src']
            title = block.find('img.lazy', first=True).attrs['title']
            a_href = block.find('a', first=True).attrs['href']
            m3u8=self.getm3u8(self.base_url + a_href)
            result_data.append({
                'image': img_src,
                'title': title,
                'link': self.base_url + a_href,
                'm3u8':m3u8
            })

        return result_data

app = Flask(__name__)

@app.route('/api/scrape', methods=['GET'])
def scrape():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing 'url' parameter."}), 400

    scraper = Scraper()
    scraped_data = scraper.scrape_website(url)

    if scraped_data:
        return jsonify({"data": scraped_data}), 200
    else:
        return jsonify({"error": "No data found."}), 404
    
@app.route('/api/menu', methods=['GET'])
def Mn():
    scraper = Scraper()
    menu_data=scraper.getmenu()
    if menu_data:
        return jsonify({"data": menu_data}), 200
    else:
        return jsonify({"error": "No data found."}), 404

if __name__ == '__main__':
    app.run(debug=True)
