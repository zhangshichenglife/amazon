import openpyxl
from openpyxl import Workbook
from openpyxl.drawing.image import Image
import requests
from detail_parser import ParseUrlDetail


class ExcelSaver:

    def __init__(self, filename='new_workbook'):
        """
        初始化excel表格信息，并自动填充第一行 字段名称
        :param filename: str 存储文件名称
        """
        self.filename = filename
        self.workbook = Workbook()
        self.worksheet = self.workbook.create_sheet('index', 0)
        # 设置存储数据的sheet名称 为 test
        self.worksheet.title = 'test'
        # 设定字段名称行的名称变量
        self.worksheet_header = ['main_pic', 'asin', 'pic_id', 'title', 'series_asin_list', 'score', 'comment_num', 'answered_questions_num', 'list_price', 'priceblock_ourprice', 'is_free_shipping', 'is_free_return', 'brand', 'best_sellers_rank', 'date_first_available', 'date']
        self.worksheet.append(self.worksheet_header)
        # 计算列数
        self.ncol = len(self.worksheet_header)

    def insert_data(self, data_json, nrow):
        """
        在excel 中插入数据，按行插入
        :param data_json: dict  本行插入的数据
        :param nrow: int 在多少行插入数据
        :return:
        """
        # 将主图的大小进行扩大
        main_pic_url = data_json.get('main_pic').replace('40_', '150')
        # 主图的id
        pic_id = data_json.get('pic_id')
        # 主图的保存地址
        savepath = './pic/{}.jpg'.format(pic_id)
        # 下载主图并存储到指定位置
        with open(savepath, 'wb+') as f:
            r = requests.get(main_pic_url)
            f.write(r.content)

        # 设定第一列单元格的宽高，用于匹配主图大小，需要手动调整，建议比例23/125
        self.worksheet.column_dimensions['A'].width = 23.0
        self.worksheet.row_dimensions[nrow].height = 125.0
        # 将主图插入到 指定位置
        img = Image(savepath)
        print('准备向 xlsx 写入数据')
        self.worksheet.add_image(img, 'A'+str(nrow))
        # 插入其他各列信息
        self.worksheet['B'+str(nrow)] = data_json.get('asin')
        self.worksheet['C'+str(nrow)] = data_json.get('pic_id')
        self.worksheet['D'+str(nrow)] = data_json.get('title')
        self.worksheet['E'+str(nrow)] = data_json.get('brand')
        self.worksheet['F'+str(nrow)] = ','.join(data_json.get('series_asin_list'))
        self.worksheet['G'+str(nrow)] = data_json.get('score')
        self.worksheet['H'+str(nrow)] = data_json.get('comment_num')
        self.worksheet['I'+str(nrow)] = data_json.get('answered_questions_num')
        self.worksheet['J'+str(nrow)] = data_json.get('list_price')
        self.worksheet['K'+str(nrow)] = data_json.get('priceblock_ourprice')
        self.worksheet['L'+str(nrow)] = data_json.get('is_free_shipping')
        self.worksheet['M'+str(nrow)] = data_json.get('is_free_return')
        self.worksheet['N'+str(nrow)] = data_json.get('best_sellers_rank')
        self.worksheet['O'+str(nrow)] = data_json.get('date_first_available')
        self.worksheet['P'+str(nrow)] = data_json.get('date')
        print('xlsx 写入第', nrow, '行完毕')

    def save_work(self):
        self.workbook.save('./excel/{}.xlsx'.format(self.filename))


if __name__ == '__main__':
    wb = ExcelSaver()

    url_list = ['https://www.amazon.com/dp/product/B083JCXPY1/',  # 用于检测基本字段能否抓取
                'https://www.amazon.com/dp/product/B01KB9WM2S/',  # 用于检测不同的图片展现方式能否抓取
                'https://www.amazon.com/dp/product/B07Y1X24KP/'  # 用于检测不同系列的产品asin 能否抓取
                ]
    nrow = 2
    for url in url_list:
        parse_url_detail = ParseUrlDetail(url)
        response_text = parse_url_detail.download_response()
        # print(response_text)
        if response_text:
            json_data = parse_url_detail.parse_response_text(response_text)
            print(json_data)
            wb.insert_data(json_data, nrow)
            # 增加数据插入行数
            nrow += 1
    wb.save_work()