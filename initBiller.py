import xml.etree.ElementTree as ET
from app.models import (
    BillerInfoModel,
    )

def parse_biller_info_response(xml_file):
    tree = ET.parse(xml_file)
    #root = ET.fromstring(xml_response)
  
    # get root element
    root = tree.getroot()

    biller_dict = dict()
    billerId = None
    billerName = None
    for element in root:
        for subelement in element:
            if subelement.tag == 'billerId':
                print("BillerId:", subelement.text)
                billerId = subelement.text
            if subelement.tag == 'billerName':
                print("BillerName:", subelement.text)
                billerName = subelement.text

            if billerId and billerName:
                biller_dict[billerId] = billerName
    print(biller_dict)
    return biller_dict

try:
    biller_dict = parse_biller_info_response(os.path.join(os.getcwd(),"app/billerInfoResponse.xml"))

    if BillerInfoModel.objects.all():
        queryset = BillerInfoModel.objects.filter(biller_id = (list(biller_dict.keys())[0]))
        if not queryset:
            print("biller ID", list(biller_dict.keys())[0])
            print("value", list(biller_dict.values())[0])
            b1 = BillerInfoModel.objects.create(biller_id = (list(biller_dict.keys())[0]), biller_name = list(biller_dict.values())[0])
            b1.save()
            print("Biller saved")
        else:
            print("Biller already exists")
    else:
        biller_obj = BillerInfoModel.objects.create(biller_id = (list(biller_dict.keys())[0]), biller_name = list(biller_dict.values())[0])
        biller_obj.save()
        print("Biller saved")
        
except Exception as e:
    print("Exception:",str(e))
